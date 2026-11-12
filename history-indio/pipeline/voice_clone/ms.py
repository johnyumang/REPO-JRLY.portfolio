"""Season 2 multi-speaker read: plan, check and select, assemble, verify (runs in /opt/vc). The single-voice path is untouched.
usage: ms.py plan <script_multispeaker.txt | episode_dir> <work_dir>
       ms.py qc <work_dir> [--full]        -> choice.json; prints the chunks that need another take
       ms.py assemble <work_dir> <out_prefix>   -> <out_prefix>.mp3/.wav + <out_prefix>_timings.json
       ms.py verify <work_dir> <out_prefix>     -> re-hears every line of the finished file, <out_prefix>_verify.json
Script: one line per speaker turn, `NAME: [tone] text` (a turn may hold several sentences and tone tags; a blank line = new scene).
Speed mode (default): a chunk gets a second take only when its WORDS are wrong; --full also retries any other failed check."""
import os, sys, re, json, glob, subprocess, tempfile, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import vprofile as VP
TAGMAP = {'whisper': 'whispers', 'suspense': 'suspenseful', 'somber': 'sad'}
SPK_CAST = 0.85          # a designed-voice line must be at least this similar (WavLM x-vector) to ITS OWN reference clip
F0_CAST_ST = 4.0         # ... and its median pitch within this many semitones of the reference clip's
GAP_SENT, GAP_TURN, GAP_SCENE = 0.38, 0.45, 0.65
def parse_script(script):
    S = []; scene = 0; turn = -1
    for line in open(script, encoding='utf-8').read().split('\n'):
        line = line.strip()
        if not line: scene += 1 if S else 0; continue
        if line.startswith('#'): continue
        m = re.match(r'^([A-Za-z\u00d1\u00f1 .\'-]+?)\s*:\s*(.+)$', line)
        assert m, 'not `NAME: [tone] text`: %r' % line
        spk = m.group(1).strip().upper(); turn += 1; cur = 'narrate'
        for s in re.findall(r'[^.?!]+[.?!]+["\u201d]?', m.group(2) + ('' if re.search(r'[.?!]["\u201d]?\s*$', m.group(2)) else '.')):
            tags = re.findall(r'\[([^\]]+)\]', s); txt = re.sub(r'\[[^\]]+\]\s*', '', s).strip()
            if not txt: continue
            if tags: cur = TAGMAP.get(tags[-1].lower(), tags[-1].lower())
            S.append(dict(i=len(S), speaker=spk, turn=turn, para=scene, style=cur, tagged=bool(tags), text=txt, say=txt))
    return S
def plan(src, work):
    """src = a script_multispeaker.txt, or an episode folder with script_multispeaker.txt and/or sentences.json (with a speaker per
    sentence). With both, the script gives turns and scenes, sentences.json the spoken form ('say') and pauses; they must agree."""
    d = src if os.path.isdir(src) else os.path.dirname(src); script = src if not os.path.isdir(src) else os.path.join(d, 'script_multispeaker.txt')
    sj = os.path.join(d, 'sentences.json'); J = json.load(open(sj)) if os.path.exists(sj) and 'speaker' in (json.load(open(sj)) or [{}])[0] else None
    if os.path.exists(script):
        S = parse_script(script)
        if J:
            assert len(J) == len(S), ('script and sentences.json differ in sentence count', len(S), len(J))
            for s, j in zip(S, J):
                assert j['speaker'].upper() == s['speaker'], (s['i'], s['speaker'], j['speaker'])
                s['text'] = j['text']; s['say'] = j.get('say') or j['text']; s['pause'] = j.get('pause')
    else:
        assert J, 'need script_multispeaker.txt or sentences.json with a speaker field in ' + d
        S = []; turn = -1
        for k, j in enumerate(J):
            if not S or j['speaker'].upper() != S[-1]['speaker']: turn += 1
            st = TAGMAP.get((j.get('style') or 'narrate').lower(), (j.get('style') or 'narrate').lower())
            S.append(dict(i=k, speaker=j['speaker'].upper(), turn=turn, para=turn, style=st, tagged=True, text=j['text'], say=j.get('say') or j['text'], pause=j.get('pause')))
    C = []
    for s in S:
        c = C[-1] if C else None
        if c and c['turn'] == s['turn'] and not s['tagged'] and len(c['sent_ids']) < 3 and len(c['text']) + len(s['say']) + 1 <= 170: c['sent_ids'].append(s['i']); c['text'] += ' ' + s['say']
        else: C.append(dict(id=len(C), speaker=s['speaker'], turn=s['turn'], para=s['para'], style=s['style'], prompt=s['style'], sent_ids=[s['i']], text=s['say']))
    for sp in sorted({c['speaker'] for c in C} - {VP.NARRATOR}): VP.cast_ref(sp)      # fail early on a missing reference
    os.makedirs(work, exist_ok=True); json.dump(dict(multispeaker=True, sentences=S, chunks=C), open(work + '/plan.json', 'w'), ensure_ascii=False, indent=1)
    print(len(S), 'sentences ->', len(C), 'chunks, speakers:', sorted({c['speaker'] for c in C}))
    for c in C: print(c['id'], c['speaker'], c['style'], c['sent_ids'], '|', c['text'])
def ref_emb(work, speaker):
    """Speaker check target: Indio = centroid of the user's real recording; anyone else = their own reference clip (cached)."""
    import vqc
    if speaker == VP.NARRATOR: return VP.centroid(), None
    p = f"{work}/refs/{VP.fname(speaker)}.emb.json"
    if not os.path.exists(p):
        w, t = VP.cast_ref(speaker); y = vqc.load16(w); f0, _ = vqc.f0_stats(y); os.makedirs(work + '/refs', exist_ok=True)
        json.dump(dict(emb=vqc.spk(y).tolist(), f0=f0), open(p, 'w'))
    d = json.load(open(p)); return np.array(d['emb']), d['f0']
def words_ok(m): return m['edits'] <= VP.PROFILE['max_edits'] and m['first_ok'] and m['cmatch'] >= 0.88
def checks(m, c, rf0):
    """-> list of failed checks (empty = pass). Indio keeps exactly the thresholds of qcsel.py."""
    p = [] if words_ok(m) else ['words']
    if c['speaker'] == VP.NARRATOR:
        lo, hi = VP.PROFILE['f0_window_hz'].get(c['style'], VP.PROFILE['f0_window_hz']['narrate'])
        if m['f0'] is None or not (lo * 0.85 <= m['f0'] <= hi * 1.10): p.append('pitch')
        if m['conf'] < 0.84 or m['minconf'] < 0.30: p.append('unclear')
        if m['spk'] < 0.915: p.append('speaker')
    else:
        if m['f0'] is None or abs(12 * np.log2(m['f0'] / rf0)) > F0_CAST_ST: p.append('pitch')
        if m['conf'] < 0.82 or m['minconf'] < 0.30: p.append('unclear')
        if m['spk'] < SPK_CAST: p.append('speaker')
    if not (4.3 <= m['rate'] <= 7.4): p.append('speed')
    if c['speaker'] == VP.NARRATOR and (m['lead'] > 0.12 or m['trail'] > 0.12): p.append('edge noise')
    if c['speaker'] != VP.NARRATOR and (m['pre_s'] > 0.35 or m['post_s'] > 0.45): p.append('sound outside the words')
    if m['clip'] > 1e-4: p.append('clipping')
    if m['maxgap'] > 0.8: p.append('long silence')
    return p
def destray(w, m, text):
    """Take whose words fail only because of extra sound before the first word: cut at the first pause (>= 50 ms, 30 dB under the speech)
    before the second aligned word, keep it as take <name>t.wav when the cut take passes the word check. -> (wav, metrics) or None."""
    import vqc, soundfile as sf
    W = m['words']
    if len(W) < 2 or w.endswith('t.wav') or vqc.edits(text, m['heard']) == 0: return None
    y, sr = sf.read(w, dtype='float32'); hop = int(0.01 * sr); n = len(y) // hop
    db = np.array([vqc.rms_db(y[i * hop:(i + 1) * hop]) for i in range(n)]); lvl = np.percentile(db, 90); lim = int(min(W[1][1], 1.6) / 0.01)
    lo = np.where(db[:lim] < lvl - 30)[0]; runs = []; i0 = None
    for a, b in zip(np.r_[-9, lo], np.r_[lo, 10 ** 9]):
        if b != a + 1:
            if i0 is not None and a - i0 >= 4 and i0 > int((m.get('onset', 0) + 0.06) / 0.01): runs.append((i0, a))
            i0 = b
    if not runs: return None
    cut = max(0, (runs[0][1] - 2) * hop); out = w[:-4] + 't.wav'
    sf.write(out, np.r_[np.zeros(int(0.05 * sr), np.float32), y[cut:]], sr)
    t = vqc.take_metrics(out, text); json.dump(t, open(out[:-4] + '.json', 'w'), ensure_ascii=False); return out, t
def score(m): return 0.40 * m['cmatch'] + 0.25 * m['conf'] + 0.10 * min(m['minconf'], 0.8) / 0.8 + 0.25 * float(np.clip((m['spk'] - 0.80) / 0.15, 0, 1)) - 0.3 * max(0, abs(m['rate'] - 5.85) / 5.85 - 0.15)
def qc(work, full=False):
    import vqc
    P = json.load(open(work + '/plan.json')); choice = {}; redo = []
    for c in P['chunks']:
        cands = sorted(glob.glob(f"{work}/c{c['id']:03d}_{VP.fname(c['speaker'])}_s*.wav"))
        if not cands: continue
        e, rf0 = ref_emb(work, c['speaker']); best = None
        for w in cands:
            j = w[:-4] + '.json'
            if not os.path.exists(j): json.dump(vqc.take_metrics(w, c['text']), open(j, 'w'), ensure_ascii=False)
            m = json.load(open(j)); m['spk'] = round(float(np.array(m['emb']) @ e), 3); m['fail'] = checks(m, c, rf0); m['score'] = round(score(m), 4)
            print('c%03d %-12s %-4s %s edits %d cm %.2f conf %.2f min %.2f spk %.3f rate %.2f f0 %3.0f %s| %s' % (c['id'], c['speaker'][:12], w[-6:-4], 'OK ' if not m['fail'] else 'BAD', m['edits'], m['cmatch'],
                  m['conf'], m['minconf'], m['spk'], m['rate'], m['f0'] or 0, ','.join(m['fail']) + ' ' if m['fail'] else '', m['heard'][:90]), flush=True)
            key = lambda q: (words_ok(q), not q['fail'], -q['edits'], q['score'])
            if best is None or key(m) > key(best[1]): best = (w, m)
        if not words_ok(best[1]):   # a stray syllable carried over from the continuation prompt ("But", "Dot"): cut it off at the pause before the line and hear it again
            t = destray(best[0], best[1], c['text'])
            if t:
                m = t[1]; m['spk'] = round(float(np.array(m['emb']) @ e), 3); m['fail'] = checks(m, c, rf0); m['score'] = round(score(m), 4)
                print('c%03d %-12s %-4s %s stray start cut | %s' % (c['id'], c['speaker'][:12], t[0][-7:-4], 'OK ' if not m['fail'] else 'BAD', m['heard'][:90]), flush=True)
                if words_ok(m): best = t
        w, m = best; choice[str(c['id'])] = dict(wav=w, ok=not m['fail'], words_ok=words_ok(m), fail=m['fail'], spk=m['spk'], score=m['score'])
        if not words_ok(m) or (full and m['fail']): redo.append(c['id'])
    json.dump(choice, open(work + '/choice.json', 'w'), indent=1); print('need another take:', ','.join(map(str, redo)))
TMP = tempfile.mkdtemp(prefix='hi_ms_'); FI, FO = os.path.join(TMP, '_fi.wav'), os.path.join(TMP, '_fo.wav')
def ff(x, sr, af):
    import soundfile as sf
    sf.write(FI, x, sr, subtype='FLOAT'); subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', FI, '-af', af, '-c:a', 'pcm_f32le', FO], check=True)
    z, _ = sf.read(FO, dtype='float32'); return z
def ebu(x, sr):
    import soundfile as sf
    sf.write(FI, x, sr, subtype='FLOAT'); o = subprocess.run(['ffmpeg', '-nostats', '-i', FI, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    o = o[o.rindex('Summary:'):]; g = lambda k: float(o.split(k)[1].split()[0]); return g('I:'), g('LRA:'), g('Peak:')
def assemble(work, outp):
    """Same master as assemble.py (per-tone level, slow-down of rushed takes, -17.4 LUFS, true peak under -1.2 dBFS). The match EQ
    to the user's recording is applied to Indio's lines only, so the designed voices keep their own colour."""
    import soundfile as sf, librosa, scipy.signal as sg, vqc
    P = json.load(open(work + '/plan.json')); CH = json.load(open(work + '/choice.json')); S = P['sentences']
    LEVEL, LDEF = VP.PROFILE['level_db'], VP.PROFILE['level_default_db']; TARGET, TP_MAX = VP.PROFILE['target_lufs'], -1.2; SR = 48000
    segs = []; tim = {}; rows = []
    for c in P['chunks']:
        ch = CH.get(str(c['id']))
        if not ch: sys.exit('chunk %d has no take: run gen_ms.py and ms.py qc first' % c['id'])
        m = json.load(open(ch['wav'][:-4] + '.json')); y, sr = sf.read(ch['wav'], dtype='float32'); assert sr == SR
        W = m['words']; st = max(0.0, min(W[0][1] - 0.04, m.get('onset', 9) - 0.03)); en = min(len(y) / sr, max(W[-1][2] + 0.12, m.get('offset', 0) + 0.08))   # energy edges: the aligner starts exclamations late
        if W[0][1] - st > 0.04:   # stray syllable glued to the first word (continuation prompt): trim to just before the first aligned word, kept only if the recogniser then hears the script's first word
            st2 = max(0.0, W[0][1] - 0.03); h2 = vqc.asr(vqc.load16(y[int(st2 * sr):int(en * sr)], sr))
            if vqc.first_ok(c['text'], h2): print('trim lead c%03d %.2f -> %.2f | %s' % (c['id'], st, st2, h2[:40])); st = st2
        seg = y[int(st * sr):int(en * sr)].copy(); k = 1.0
        if m['rate'] > 6.9:
            k = 6.3 / m['rate']; seg = ff(seg, sr, f'rubberband=tempo={k:.4f}:pitchq=quality:formant=preserved')
        body = seg[int(0.04 * sr):len(seg) - int(0.12 * sr)]; g = float(np.clip(LEVEL.get(c['style'], LDEF) - vqc.rms_db(body), -12, 12)); seg *= 10 ** (g / 20)
        n1, n2 = int(0.008 * sr), int(0.04 * sr); seg[:n1] *= np.linspace(0, 1, n1); seg[-n2:] *= np.linspace(1, 0, n2)
        seg = ff(seg, sr, 'alimiter=limit=0.89:attack=5:release=50:level=false:latency=true')[:len(seg)]
        j = 0; offs = []
        for si in c['sent_ids']:
            n = len(vqc.norm_words(S[si]['say'])); ws = W[j:j + n]; j += n; offs.append((si, (ws[0][1] - st) / k, (ws[-1][2] - st) / k))
        nxt = P['chunks'][c['id'] + 1] if c['id'] + 1 < len(P['chunks']) else None
        gap = 0.0 if nxt is None else (GAP_SCENE if nxt['para'] != c['para'] else GAP_TURN if nxt['turn'] != c['turn'] else GAP_SENT) + 0.03 * (((c['id'] * 37) % 5) - 2) / 2
        if nxt is not None: gap = max(gap, S[c['sent_ids'][-1]].get('pause') or 0)
        segs.append(dict(c=c, y=seg, offs=offs, gap=gap)); rows.append((c['id'], c['speaker'], os.path.basename(ch['wav'])[-6:-4], m['rate'], round(k, 3), round(g, 1)))
    ind = [s['y'] for s in segs if s['c']['speaker'] == VP.NARRATOR]
    if ind:                                                                         # match EQ for Indio's lines (as assemble.py, at 48 kHz)
        r, _ = librosa.load(VP.rec(), sr=SR, mono=True)
        def ltas(x):
            x = x[np.abs(x) > 1e-4]; f, p = sg.welch(x, SR, nperseg=4096); return f, 10 * np.log10(p + 1e-20)
        f, a_ = ltas(r); _, b_ = ltas(np.concatenate(ind)); d = a_ - b_; lf = np.log2(np.maximum(f, 20)); sm = np.array([d[np.abs(lf - x) < 1 / 6].mean() for x in lf])
        ref = sm[(f > 200) & (f < 4000)].mean(); sm = np.clip(sm - ref, -6, 6); sm[f > 15000] = 0; sm[f < 60] = 0; sm[np.abs(sm) < 1.0] = 0
        h = sg.firwin2(2049, f / (SR / 2), 10 ** (sm / 20))
        for s in segs:
            if s['c']['speaker'] == VP.NARRATOR: s['y'] = sg.fftconvolve(s['y'], h, mode='same').astype(np.float32)
    parts = []; t = 0.0
    for s in segs:
        for si, a0, a1 in s['offs']: tim[si] = (t + a0, t + a1)
        parts += [s['y'], np.zeros(int(s['gap'] * SR), np.float32)]; t += (len(s['y']) + int(s['gap'] * SR)) / SR
    y = librosa.resample(np.concatenate(parts), orig_sr=SR, target_sr=44100, res_type='soxr_hq'); sr = 44100
    # (all times above are in seconds, so the resample does not move them)
    def master(x, gdb): return ff(x * 10 ** (gdb / 20), sr, 'aresample=176400:resampler=soxr,alimiter=limit=%.5f:attack=2:release=80:level=false:latency=true,aresample=44100:resampler=soxr' % (10 ** ((TP_MAX - 0.1) / 20)))[:len(x)]
    i0, _, _ = ebu(y, sr); gdb = TARGET - i0
    for _ in range(3):
        z = master(y, gdb); I, L, TP = ebu(z, sr)
        if abs(I - TARGET) <= 0.1: break
        gdb += TARGET - I
    y0, y = y, z
    for _ in range(2):
        sf.write(outp + '.wav', y, sr, subtype='PCM_16'); subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', outp + '.wav', '-codec:a', 'libmp3lame', '-b:a', '192k', outp + '.mp3'], check=True)
        I, L, TP = ebu(librosa.load(outp + '.mp3', sr=sr, mono=True)[0], sr); print('mp3: %.2f LUFS, LRA %.1f LU, true peak %.2f dBFS' % (I, L, TP))
        if abs(I - TARGET) <= 0.1: break
        gdb += TARGET - I; y = master(y0, gdb)
    T = [{'text': S[i]['text'], 'start': round(tim[i][0], 3), 'end': round(tim[i][1], 3), 'style': S[i]['style'], 'speaker': S[i]['speaker']} for i in sorted(tim)]
    json.dump(T, open(outp + '_timings.json', 'w'), ensure_ascii=False, indent=1)
    print('chunks:', rows); print('assembled %d chunks, %d sentences, %.1f s -> %s.mp3' % (len(rows), len(T), len(y) / sr, outp))
def verify(work, outp):
    import librosa, vqc
    P = json.load(open(work + '/plan.json')); T = json.load(open(outp + '_timings.json')); y, sr = librosa.load(outp + '.mp3', sr=44100, mono=True); a = vqc.load16(outp + '.mp3')
    ok_t = all(T[i]['start'] < T[i]['end'] <= T[i + 1]['start'] for i in range(len(T) - 1)) and T[-1]['end'] <= len(y) / sr
    I, L, TP = ebu(y, sr); print('file %.1f s, %.2f LUFS, LRA %.1f, true peak %.2f dBFS | timings: %d sentences, in order %s' % (len(y) / sr, I, L, TP, len(T), ok_t))
    out = []
    for c in P['chunks']:
        ids = c['sent_ids']; s0, s1 = max(0.0, T[ids[0]]['start'] - 0.05), T[ids[-1]]['end'] + 0.10
        seg = a[int(s0 * 16000):int(s1 * 16000)]; hh = vqc.asr(seg); e, _ = ref_emb(work, c['speaker'])
        li = ebu(y[int(s0 * sr):int(s1 * sr)], sr)[0] if s1 - s0 > 0.45 else None
        r = dict(id=c['id'], speaker=c['speaker'], text=c['text'], heard=hh, edits=vqc.edits(c['text'], hh), first_ok=vqc.first_ok(c['text'], hh), spk=round(float(vqc.spk(seg) @ e), 3),
                 rate=round(vqc.syllables(c['text']) / max(.2, T[ids[-1]]['end'] - T[ids[0]]['start']), 2), lufs=li, start=T[ids[0]]['start'], end=T[ids[-1]]['end'])
        r['words_ok'] = r['edits'] <= VP.PROFILE['max_edits'] and r['first_ok']; out.append(r)
        print('  c%03d %-12s words %s edits %d spk %.3f rate %.2f lufs %s | %s' % (c['id'], c['speaker'][:12], 'OK ' if r['words_ok'] else 'BAD', r['edits'], r['spk'], r['rate'], li and round(li, 1), hh))
    json.dump(dict(lufs=I, lra=L, true_peak=TP, timings_in_order=ok_t, lines=out), open(outp + '_verify.json', 'w'), ensure_ascii=False, indent=1)
    print('all words right:', all(r['words_ok'] for r in out))
if __name__ == '__main__':
    cmd = sys.argv[1]; x = sys.argv[2:]
    if cmd == 'plan': plan(x[0], x[1])
    elif cmd == 'qc': qc(x[0], '--full' in x)
    elif cmd == 'assemble': assemble(x[0], x[1])
    elif cmd == 'verify': verify(x[0], x[1])
    else: sys.exit(__doc__)
