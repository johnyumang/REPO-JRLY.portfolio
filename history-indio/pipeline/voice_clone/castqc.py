"""Check every designed-voice candidate, keep one reference clip per character, report how different the voices are (runs in /opt/vc).
usage: castqc.py            -> castwork/qc.json, cast/<NAME>.wav + .txt (+ cast/emb.json), similarity table
       castqc.py --samples  -> checks castwork/<NAME>/sample_s*.wav against the kept reference (words, speaker, pitch drift)
A candidate is kept only if the words are right (same check as Indio's takes) and nothing measurable is wrong:
clipping, long silences, speed outside about 5 to 6.5 syllables/s, pitch outside the character's range, noise before/after."""
import os, sys, json, glob, numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import vqc, vprofile as VP
D = json.load(open(os.path.join(VP.HERE, 'cast_design.json'))); a = sys.argv[1:]
MAXSIM = 0.90            # two kept voices at or above this speaker similarity (Indio included) must differ by at least 4 semitones of pitch
                         # (WavLM x-vector; the real Indio recording scores 0.917-0.99 against itself, Indio clone takes must reach 0.915)
GAP_MAX, GAP_TO = 0.55, 0.45   # pauses between words longer than GAP_MAX are shortened to GAP_TO in the kept reference
REF_LEVEL_DB = -20.0     # speech RMS of a kept reference clip
def measure(wav, text): return vqc.take_metrics(wav, text)
def build_ref(wav, text, out):
    """The clip a character keeps: cut to the sound around its words, long pauses shortened, speech level set, 0.10 s / 0.25 s of silence added."""
    y, sr = sf.read(wav, dtype='float32'); y16 = vqc.load16(wav); W = vqc.words(y16, text); e0, e1 = vqc.speech_edges(y16, 16000, W[0]['start'], W[-1]['end'])
    keep = []; t0 = max(0.0, e0 - 0.05)
    for a, b in zip(W[:-1], W[1:]):
        if b['start'] - a['end'] > GAP_MAX:
            keep.append((t0, a['end'] + GAP_TO / 2)); t0 = b['start'] - GAP_TO / 2
    keep.append((t0, min(len(y) / sr, e1 + 0.15))); parts = []
    for a, b in keep:
        z = y[int(a * sr):int(b * sr)].copy(); n = int(0.012 * sr); z[:n] *= np.linspace(0, 1, n); z[-n:] *= np.linspace(1, 0, n); parts.append(z)
    y = np.concatenate(parts); y *= 10 ** ((REF_LEVEL_DB - vqc.rms_db(y)) / 20); y = np.clip(y, -0.97, 0.97)
    y = np.concatenate([np.zeros(int(0.10 * sr), np.float32), y, np.zeros(int(0.25 * sr), np.float32)])   # VoxCPM starts speaking at sample 0: give the clip clean silent edges
    sf.write(out, y, sr, subtype='PCM_16'); return len(keep) - 1
def problems(m, c, ref=True):
    p = []
    if m['edits'] > VP.PROFILE['max_edits'] or not m['first_ok'] or m['cmatch'] < 0.88: p.append('words')
    if m['conf'] < 0.82 or m['minconf'] < 0.30: p.append('unclear word')
    if m['clip'] > 1e-4: p.append('clipping')
    if m['maxgap'] > 0.8: p.append('long silence')
    if not (4.8 <= m['rate'] <= 6.8): p.append('speed %.1f' % m['rate'])
    lo, hi = c['f0_hz']
    if m['f0'] is None or not (lo <= m['f0'] <= hi): p.append('pitch %s' % (m['f0'] and round(m['f0'])))
    if ref:                                                         # a kept clip must start and end in near-silence (clip edges, 30 / 60 ms)
        if m['edge_db'] > -30: p.append('edge %.0f dB' % m['edge_db'])
    elif m['pre_s'] > 0.35 or m['post_s'] > 0.45: p.append('sound outside the words')
    if ref and not (8.5 <= m['last_end'] - m['first'] <= 16.5): p.append('length')
    return p
def score(m): return 0.40 * m['cmatch'] + 0.25 * m['conf'] + 0.10 * min(m['minconf'], 0.8) / 0.8 - 0.3 * max(0, abs(m['rate'] - 5.75) / 5.75 - 0.08)
def cached(wav, text):
    j = wav[:-4] + '.qc.json'
    if not os.path.exists(j) or os.path.getmtime(j) < os.path.getmtime(wav):
        m = measure(wav, text); y = vqc.load16(wav); b = vqc.rms_db(y[int(m['first'] * 16000):int(m['last_end'] * 16000)])
        m['edge_db'] = round(max(vqc.rms_db(y[:480]), vqc.rms_db(y[-960:])) - b, 1); json.dump(m, open(j, 'w'), ensure_ascii=False)
    return json.load(open(j))
indio = VP.centroid()
def row(name, m, extra=''):
    print('%-13s %-12s %s edits %d cm %.2f conf %.2f min %.2f rate %.2f f0 %3.0f sd %.1f clip %.4f gap %.2f edge %.0f pre %.2f indio %.3f %s| %s' % (
        name, extra, 'OK ' if not m['problems'] else 'BAD', m['edits'], m['cmatch'], m['conf'], m['minconf'], m['rate'], m['f0'] or 0, m['f0sd'] or 0, m['clip'], m['maxgap'],
        m.get('edge_db', 0), m['pre_s'], float(np.array(m['emb']) @ indio), ','.join(m['problems']) + ' ' if m['problems'] else '', m['heard'][:90]), flush=True)
if '--samples' in a:
    E = json.load(open(os.path.join(VP.CAST, 'emb.json'))); out = {}
    for name, c in D['cast'].items():
        for w in sorted(glob.glob(os.path.join(VP.CASTWORK, VP.fname(name), 'sample_s*.wav'))):
            m = cached(w, c['sample']); m['problems'] = problems(m, c, ref=False); m['spk_own'] = round(float(np.array(m['emb']) @ np.array(E[name]['emb'])), 3)
            m['f0_drift_st'] = round(12 * np.log2(m['f0'] / E[name]['f0']), 2) if m['f0'] else None
            out[name] = {k: v for k, v in m.items() if k != 'emb'}; row(name, m, os.path.basename(w)[:-4]); print('   own-ref similarity %.3f, pitch drift vs reference %+.2f semitones' % (m['spk_own'], m['f0_drift_st'] or 0))
    json.dump(out, open(os.path.join(VP.CASTWORK, 'samples_qc.json'), 'w'), ensure_ascii=False, indent=1); sys.exit()
allm = {}
for name, c in D['cast'].items():
    for w0 in sorted(glob.glob(os.path.join(VP.CASTWORK, VP.fname(name), 'd[0-9]s[0-9].wav'))):
        w = w0[:-4] + '.ref.wav'
        if not os.path.exists(w) or os.path.getmtime(w) < os.path.getmtime(w0): build_ref(w0, c['ref_text'], w)
        m = cached(w, c['ref_text']); m['problems'] = problems(m, c); m['score'] = round(score(m), 4); m['wav'] = w; allm.setdefault(name, []).append(m); row(name, m, os.path.basename(w)[:-4])
# keep: the combination of passing candidates (one per character) with the fewest and least close pairs of voices, Indio included
# (closeness = speaker similarity minus 0.02 per semitone of pitch gap, up to 6); ties go to the higher summed score. Greedy picking runs out of room: on this speaker model women's and children's voices sit
# at 0.86-0.89 to each other even an octave apart, so closeness is judged over the whole cast at once.
import itertools
pas = {n: sorted([m for m in ms if not m['problems']], key=lambda m: -m['score'])[:4] for n, ms in allm.items()}
F0I = float(np.median([r['f0'] for r in VP.real() if r['f0']]))
def closeness(e1, f1, e2, f2): return float(np.dot(e1, e2)) - 0.02 * min(abs(12 * np.log2(f1 / f2)), 6.0)   # a pitch gap counts, up to 6 semitones
missing = [n for n in allm if not pas[n]]; names_ = [n for n in allm if pas[n]]; best = None
for combo in itertools.product(*[pas[n] for n in names_]):
    pts = [(indio, F0I)] + [(np.array(m['emb']), m['f0']) for m in combo]
    cl = [closeness(*pts[a], *pts[b]) for a in range(len(pts)) for b in range(a + 1, len(pts))]
    key = (-sum(max(0.0, c - 0.84) ** 2 for c in cl), sum(m['score'] for m in combo))   # every close pair costs, the closest most
    if best is None or key > best[0]: best = (key, combo)
chosen = dict(zip(names_, best[1])) if best else {}
os.makedirs(VP.CAST, exist_ok=True); emb = {}
for name, m in chosen.items():
    p = os.path.join(VP.CAST, VP.fname(name)); y, sr = sf.read(m['wav'], dtype='float32'); sf.write(p + '.wav', y, sr, subtype='PCM_16'); open(p + '.txt', 'w').write(D['cast'][name]['ref_text'] + '\n')
    e = vqc.spk(vqc.load16(p + '.wav')); emb[name] = dict(emb=e.tolist(), f0=m['f0'], rate=m['rate'], source=os.path.basename(m['wav']),
                                                         description=D['cast'][name]['descriptions'][int(os.path.basename(m['wav'])[1])])
json.dump(emb, open(os.path.join(VP.CAST, 'emb.json'), 'w'), indent=1)
json.dump({n: [{k: v for k, v in m.items() if k != 'emb'} for m in ms] for n, ms in allm.items()}, open(os.path.join(VP.CASTWORK, 'qc.json'), 'w'), ensure_ascii=False, indent=1)
names = [VP.NARRATOR] + [n for n in D['cast'] if n in emb]; V = {VP.NARRATOR: indio, **{n: np.array(emb[n]['emb']) for n in emb}}
print('\nkept:', {n: emb[n]['source'] for n in emb}, '| no passing distinct candidate:', missing)
print('speaker similarity (INDIO = centroid of the real recording; 1.0 = same voice):'); print('%-13s' % '' + ''.join('%13s' % n[:12] for n in names))
for x in names: print('%-13s' % x[:12] + ''.join('%13.3f' % float(V[x] @ V[y]) for y in names))
F = {VP.NARRATOR: float(np.median([r['f0'] for r in VP.real() if r['f0']])), **{n: emb[n]['f0'] for n in emb}}
close = [(x, y, float(V[x] @ V[y]), 12 * np.log2(F[x] / F[y])) for k, x in enumerate(names) for y in names[k + 1:] if float(V[x] @ V[y]) >= 0.88]
print('closest pair %.3f (MAXSIM %.2f); pairs >= 0.88 with their pitch gap:' % (max(float(V[x] @ V[y]) for k, x in enumerate(names) for y in names[k + 1:]), MAXSIM))
for x, y, c, st in close: print('  %s / %s  sim %.3f  pitch gap %+.1f semitones %s' % (x, y, c, st, '' if c < MAXSIM or abs(st) >= 4 else '<- too close: change one of them'))
