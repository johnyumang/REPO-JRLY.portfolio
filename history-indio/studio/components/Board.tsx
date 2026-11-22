'use client';
import {useCallback, useEffect, useRef, useState} from 'react';
import {Manifest, ProviderId, Shot, Take, emptyManifest, exportManifest, newShot, parseManifest} from '@/lib/manifest';
import {WAN_MAX_SECONDS, runWanFree} from '@/lib/providers/wan-free';

const STORE = 'indio-studio-manifest-v1';
const POLL_MS = 6000;
type Providers = Record<ProviderId, {ready: boolean; free: boolean; note: string}>;

function load(): Manifest {
  try {
    const t = window.localStorage.getItem(STORE);
    if (t) return parseManifest(t);
  } catch { /* storage blocked or bad data: start empty */ }
  return emptyManifest();
}

/** Shrinks an uploaded picture so it fits in browser storage and in a request body. */
async function fileToDataUrl(file: File, maxW = 1344): Promise<string> {
  const bmp = await createImageBitmap(file);
  const scale = Math.min(1, maxW / bmp.width);
  const c = document.createElement('canvas');
  c.width = Math.round(bmp.width * scale);
  c.height = Math.round(bmp.height * scale);
  c.getContext('2d')!.drawImage(bmp, 0, 0, c.width, c.height);
  return c.toDataURL('image/jpeg', 0.86);
}

function download(name: string, text: string) {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([text], {type: 'application/json'}));
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 2000);
}

const uid = () => Math.random().toString(36).slice(2, 9);

export default function Board() {
  const [m, setM] = useState<Manifest | null>(null);
  const [providers, setProviders] = useState<Providers | null>(null);
  const [paste, setPaste] = useState<string | null>(null);
  const [msg, setMsg] = useState('');
  const mRef = useRef<Manifest | null>(null);
  mRef.current = m;

  useEffect(() => { setM(load()); }, []);
  useEffect(() => {
    fetch('/api/providers').then((r) => (r.ok ? r.json() : null)).then(setProviders).catch(() => setProviders(null));
  }, []);
  useEffect(() => {
    if (!m) return;
    try {
      window.localStorage.setItem(STORE, JSON.stringify(m));
    } catch {
      setMsg('Browser storage is full (uploaded pictures are large). Use image URLs, or export often.');
    }
  }, [m]);

  const updShot = useCallback((id: string, f: (s: Shot) => Shot) => {
    setM((cur) => (cur ? {...cur, shots: cur.shots.map((s) => (s.id === id ? f(s) : s))} : cur));
  }, []);
  const updTake = useCallback((shotId: string, takeId: string, patch: Partial<Take>) => {
    updShot(shotId, (s) => ({...s, takes: s.takes.map((t) => (t.id === takeId ? {...t, ...patch} : t))}));
  }, [updShot]);

  // MiniMax takes: ask the status route every few seconds (each call is short).
  useEffect(() => {
    const timer = setInterval(async () => {
      const cur = mRef.current;
      if (!cur) return;
      for (const s of cur.shots) {
        for (const t of s.takes) {
          if (t.provider !== 'minimax' || !t.taskId || (t.status !== 'queued' && t.status !== 'running')) continue;
          try {
            const r = await fetch(`/api/minimax/status?taskId=${encodeURIComponent(t.taskId)}`);
            const j = await r.json();
            if (r.status === 401) { setMsg('Session ended: log in again.'); return; }
            if (j.error && j.status === 'running') {
              const errors = (t.errors || 0) + 1;
              updTake(s.id, t.id, errors > 10 ? {status: 'failed', error: j.error, errors} : {errors, note: j.error});
            } else {
              updTake(s.id, t.id, {status: j.status, url: j.videoUrl, error: j.error, note: j.raw, errors: 0});
              if (j.status === 'done') updShot(s.id, (x) => ({...x, chosen: x.chosen || t.id}));
            }
          } catch { /* network blip: next round */ }
        }
      }
    }, POLL_MS);
    return () => clearInterval(timer);
  }, [updShot, updTake]);

  async function generate(shot: Shot) {
    if (!shot.image) { setMsg(`${shot.id}: add a picture first.`); return; }
    if (!shot.prompt.trim()) { setMsg(`${shot.id}: write a motion prompt first.`); return; }
    const take: Take = {id: uid(), provider: shot.provider, status: 'queued', startedAt: Date.now()};
    updShot(shot.id, (s) => ({...s, takes: [...s.takes, take]}));
    if (shot.provider === 'minimax') {
      if (!window.confirm('This take spends MiniMax credits. Go?')) {
        updTake(shot.id, take.id, {status: 'failed', error: 'cancelled'});
        return;
      }
      try {
        const r = await fetch('/api/minimax/create', {
          method: 'POST', headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({image: shot.image, prompt: shot.prompt, duration: shot.duration}),
        });
        const j = await r.json();
        if (!r.ok) throw new Error(j.error || `HTTP ${r.status}`);
        updTake(shot.id, take.id, {taskId: j.taskId, status: 'queued'});
      } catch (e) {
        updTake(shot.id, take.id, {status: 'failed', error: (e as Error).message});
      }
      return;
    }
    try {
      const out = await runWanFree({image: shot.image, prompt: shot.prompt, negative: shot.negative, duration: shot.duration},
        (u) => updTake(shot.id, take.id, u));
      updTake(shot.id, take.id, {status: 'done', url: out.url, note: out.seed != null ? `seed ${out.seed}` : undefined});
      updShot(shot.id, (s) => ({...s, chosen: s.chosen || take.id}));
    } catch (e) {
      const err = (e as Error).message;
      const hint = /quota/i.test(err) ? ' The free GPU limit for this connection is used up: try again later, run the local pipeline, or use minimax.' : '';
      updTake(shot.id, take.id, {status: 'failed', error: err + hint});
    }
  }

  function importText(text: string) {
    try {
      setM(parseManifest(text));
      setPaste(null);
      setMsg('Manifest loaded.');
    } catch (e) {
      setMsg('Could not read that manifest: ' + (e as Error).message);
    }
  }

  if (!m) return <div className="wrap muted">Loading…</div>;
  const doneCount = m.shots.filter((s) => s.takes.some((t) => t.id === s.chosen && t.status === 'done')).length;

  return (
    <>
      <header className="top">
        <span className="brand"><i />INDIO <b>STUDIO</b></span>
        <input aria-label="Episode" value={m.episode} onChange={(e) => setM({...m, episode: e.target.value})} style={{width: 180}} />
        <label className="row">
          <span className="muted small">Import</span>
          <input type="file" accept="application/json,.json" onChange={async (e) => {
            const f = e.target.files?.[0];
            if (f) importText(await f.text());
            e.target.value = '';
          }} />
        </label>
        <button onClick={() => setPaste(paste === null ? '' : null)}>Paste JSON</button>
        <button onClick={() => setM({...m, shots: [...m.shots, newShot(m.shots.length)]})}>+ Shot</button>
        <button className="primary" onClick={() => download(`${m.episode}_manifest.json`, JSON.stringify(exportManifest(m), null, 1))}>
          Export manifest ({doneCount}/{m.shots.length})
        </button>
        <button onClick={() => { if (window.confirm('Clear the board? Export first if you need it.')) setM(emptyManifest()); }}>Clear</button>
        <span style={{flex: 1}} />
        <button onClick={async () => { await fetch('/api/logout', {method: 'POST'}); window.location.href = '/login'; }}>Lock</button>
      </header>
      <main className="wrap">
        {msg ? <div className="panel warn" onClick={() => setMsg('')}>{msg} <span className="muted small">(click to hide)</span></div> : null}
        {paste !== null ? (
          <div className="panel">
            <textarea rows={8} placeholder='{"episode": "...", "shots": [{"image": "https://...", "prompt": "...", "duration": 3}]}'
              value={paste} onChange={(e) => setPaste(e.target.value)} />
            <div className="row"><button className="primary" onClick={() => importText(paste)}>Load</button></div>
          </div>
        ) : null}
        <div className="panel small muted">
          <b>wan-free</b>: free, runs from this browser, up to {WAN_MAX_SECONDS}s per take; keep the tab open while it works.{' '}
          <b>minimax</b>: {providers?.minimax?.ready ? 'ready, spends credits on every take.' : 'not set up on this deployment.'}{' '}
          Take links expire (about an hour for MiniMax): export, then run the local pipeline to keep copies.
        </div>
        {m.shots.length === 0 ? <p className="muted">No shots yet. Import a manifest from <code>pipeline/animate/motion.py</code> or add a shot.</p> : null}
        <div className="grid">
          {m.shots.map((s) => (
            <ShotCard key={s.id} shot={s} providers={providers} line={m.lines}
              onChange={(f) => updShot(s.id, f)} onGenerate={() => generate(s)}
              onDuration={(takeId, d) => updTake(s.id, takeId, {duration: d})}
              onRemove={() => setM({...m, shots: m.shots.filter((x) => x.id !== s.id)})} />
          ))}
        </div>
      </main>
    </>
  );
}

function ShotCard({shot, providers, line, onChange, onGenerate, onDuration, onRemove}: {
  shot: Shot; providers: Providers | null; line: Manifest['lines'];
  onChange: (f: (s: Shot) => Shot) => void; onGenerate: () => void;
  onDuration: (takeId: string, d: number) => void; onRemove: () => void;
}) {
  const busy = shot.takes.some((t) => t.status === 'queued' || t.status === 'running');
  const said = (shot.lines || []).map((i) => line.find((l) => l.i === i)).filter(Boolean);
  const mmReady = providers?.minimax?.ready;
  return (
    <section className="card">
      <div className="row">
        <b>{shot.id}</b>
        {shot.still ? <span className="muted small">{shot.still}</span> : null}
        {shot.start != null && shot.end != null ? <span className="muted small">{shot.start.toFixed(2)}–{shot.end.toFixed(2)}s</span> : null}
        <span style={{flex: 1}} />
        <button className="small" onClick={() => { if (window.confirm(`Remove ${shot.id}?`)) onRemove(); }}>Remove</button>
      </div>
      {said.length ? <div className="small">{said.map((l) => <div key={l!.i}><b>{l!.speaker}</b> {l!.text}</div>)}</div> : null}
      {shot.warning ? <div className="warn small">{shot.warning}</div> : null}
      {shot.image ? <img className="still" src={shot.image} alt={shot.id} /> : <div className="still muted small" style={{display: 'grid', placeItems: 'center'}}>no picture</div>}
      <div className="row">
        <input style={{flex: 1, minWidth: 0}} placeholder="Image URL (https://…)" value={shot.image.startsWith('data:') ? '' : shot.image}
          onChange={(e) => onChange((s) => ({...s, image: e.target.value.trim()}))} />
        <label className="small muted">or upload <input type="file" accept="image/*" style={{width: 110}} onChange={async (e) => {
          const f = e.target.files?.[0];
          if (f) { const d = await fileToDataUrl(f); onChange((s) => ({...s, image: d})); }
        }} /></label>
      </div>
      <textarea rows={4} placeholder="Motion prompt: only the motion the line needs; one continuous shot." value={shot.prompt}
        onChange={(e) => onChange((s) => ({...s, prompt: e.target.value}))} />
      <div className="row">
        <label className="small">Seconds <input type="number" min={0.5} max={10} step={0.1} style={{width: 72}} value={shot.duration}
          onChange={(e) => onChange((s) => ({...s, duration: Number(e.target.value)}))} /></label>
        <select value={shot.provider} onChange={(e) => onChange((s) => ({...s, provider: e.target.value as ProviderId}))}>
          <option value="wan-free">wan-free (free)</option>
          <option value="minimax" disabled={!mmReady}>minimax (credits){mmReady ? '' : ' – not set up'}</option>
        </select>
        <button className="primary" disabled={busy} onClick={onGenerate}>{busy ? 'Working…' : 'Generate'}</button>
      </div>
      {shot.takes.length ? (
        <div className="takes">
          {shot.takes.map((t) => (
            <div key={t.id} className={'take' + (shot.chosen === t.id ? ' chosen' : '')}>
              <div className="row small">
                <span className={'badge ' + t.status}>{t.status}</span>
                <span className="muted">{t.provider}</span>
              </div>
              {t.url ? (
                <video src={t.url} controls muted loop playsInline preload="metadata"
                  onLoadedMetadata={(e) => { const d = (e.target as HTMLVideoElement).duration; if (d && !t.duration) onDuration(t.id, Math.round(d * 1000) / 1000); }} />
              ) : null}
              {t.note ? <div className="muted small">{t.note}</div> : null}
              {t.error ? <div className="warn small">{t.error}</div> : null}
              <div className="row small">
                {t.status === 'done' ? (
                  <label><input type="radio" name={'pick-' + shot.id} checked={shot.chosen === t.id}
                    onChange={() => onChange((s) => ({...s, chosen: t.id}))} /> use this</label>
                ) : null}
                {t.url ? <a href={t.url} target="_blank" rel="noreferrer">open</a> : null}
                <span style={{flex: 1}} />
                <button className="small" onClick={() => onChange((s) => ({...s, takes: s.takes.filter((x) => x.id !== t.id),
                  chosen: s.chosen === t.id ? null : s.chosen}))}>×</button>
              </div>
            </div>
          ))}
        </div>
      ) : null}
    </section>
  );
}
