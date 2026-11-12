"""Check every designed-voice candidate, keep one reference clip per character, report how different the voices are (runs in /opt/vc).
usage: castqc.py            -> castwork/qc.json, cast/<NAME>.wav + .txt (+ cast/emb.json), similarity table
       castqc.py --samples  -> checks castwork/<NAME>/sample_s*.wav against the kept reference (words, speaker, pitch drift)
A candidate is kept only if the words are right (same check as Indio's takes) and nothing measurable is wrong:
clipping, long silences, speed outside about 5 to 6.5 syllables/s, pitch outside the character's range, noise before/after."""
import os, sys, json, glob, numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import vqc, vprofile as VP
D = json.load(open(os.path.join(VP.HERE, 'cast_design.json'))); a = sys.argv[1:]
MAXSIM = 0.88            # a kept voice must be below this speaker similarity to Indio and to every other kept voice
REF_LEVEL_DB = -20.0     # speech RMS of a kept reference clip
def measure(wav, text): return vqc.take_metrics(wav, text)
def problems(m, c, ref=True):
    p = []
    if m['edits'] > VP.PROFILE['max_edits'] or not m['first_ok'] or m['cmatch'] < 0.88: p.append('words')
    if m['conf'] < 0.82 or m['minconf'] < 0.30: p.append('unclear word')
    if m['clip'] > 1e-4: p.append('clipping')
    if m['maxgap'] > 0.8: p.append('long silence')
    if not (4.8 <= m['rate'] <= 6.8): p.append('speed %.1f' % m['rate'])
    lo, hi = c['f0_hz']
    if m['f0'] is None or not (lo <= m['f0'] <= hi): p.append('pitch %s' % (m['f0'] and round(m['f0'])))
    if m['lead'] > 0.12 or m['trail'] > 0.12: p.append('noise at edge')
    if ref and not (8.5 <= m['last_end'] - m['first'] <= 16.5): p.append('length')
    return p
def score(m): return 0.40 * m['cmatch'] + 0.25 * m['conf'] + 0.10 * min(m['minconf'], 0.8) / 0.8 - 0.3 * max(0, abs(m['rate'] - 5.75) / 5.75 - 0.08)
def cached(wav, text):
    j = wav[:-4] + '.qc.json'
    if not os.path.exists(j): json.dump(measure(wav, text), open(j, 'w'), ensure_ascii=False)
    return json.load(open(j))
indio = VP.centroid()
def row(name, m, extra=''):
    print('%-13s %-12s %s edits %d cm %.2f conf %.2f min %.2f rate %.2f f0 %3.0f sd %.1f clip %.4f gap %.2f lead %.2f trail %.2f indio %.3f %s| %s' % (
        name, extra, 'OK ' if not m['problems'] else 'BAD', m['edits'], m['cmatch'], m['conf'], m['minconf'], m['rate'], m['f0'] or 0, m['f0sd'] or 0, m['clip'], m['maxgap'],
        m['lead'], m['trail'], float(np.array(m['emb']) @ indio), ','.join(m['problems']) + ' ' if m['problems'] else '', m['heard'][:90]), flush=True)
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
    for w in sorted(glob.glob(os.path.join(VP.CASTWORK, VP.fname(name), 'd*s*.wav'))):
        m = cached(w, c['ref_text']); m['problems'] = problems(m, c); m['score'] = round(score(m), 4); m['wav'] = w; allm.setdefault(name, []).append(m); row(name, m, os.path.basename(w)[:-4])
# keep: best passing candidate per character that is clearly different from Indio and from the voices already kept
chosen = {}; missing = []
for name in sorted(allm, key=lambda n: sum(not m['problems'] for m in allm[n])):   # fewest passing candidates choose first
    for m in sorted([m for m in allm[name] if not m['problems']], key=lambda m: -m['score']):
        e = np.array(m['emb']); sims = [float(e @ indio)] + [float(e @ np.array(o['emb'])) for o in chosen.values()]
        if max(sims) < MAXSIM: chosen[name] = m; break
    else: missing.append(name)
os.makedirs(VP.CAST, exist_ok=True); emb = {}
for name, m in chosen.items():
    y, sr = sf.read(m['wav'], dtype='float32'); s0, s1 = max(0, int((m['first'] - 0.06) * sr)), min(len(y), int((m['last_end'] + 0.25) * sr)); y = y[s0:s1].copy()
    body = y[int(0.06 * sr):len(y) - int(0.25 * sr)]; y *= 10 ** ((REF_LEVEL_DB - vqc.rms_db(body)) / 20); y = np.clip(y, -0.97, 0.97)
    n1, n2 = int(0.01 * sr), int(0.05 * sr); y[:n1] *= np.linspace(0, 1, n1); y[-n2:] *= np.linspace(1, 0, n2)
    p = os.path.join(VP.CAST, VP.fname(name)); sf.write(p + '.wav', y, sr, subtype='PCM_16'); open(p + '.txt', 'w').write(D['cast'][name]['ref_text'] + '\n')
    e = vqc.spk(vqc.load16(p + '.wav')); emb[name] = dict(emb=e.tolist(), f0=m['f0'], rate=m['rate'], source=os.path.basename(m['wav']),
                                                         description=D['cast'][name]['descriptions'][int(os.path.basename(m['wav'])[1])])
json.dump(emb, open(os.path.join(VP.CAST, 'emb.json'), 'w'), indent=1)
json.dump({n: [{k: v for k, v in m.items() if k != 'emb'} for m in ms] for n, ms in allm.items()}, open(os.path.join(VP.CASTWORK, 'qc.json'), 'w'), ensure_ascii=False, indent=1)
names = [VP.NARRATOR] + [n for n in D['cast'] if n in emb]; V = {VP.NARRATOR: indio, **{n: np.array(emb[n]['emb']) for n in emb}}
print('\nkept:', {n: emb[n]['source'] for n in emb}, '| no passing distinct candidate:', missing)
print('speaker similarity (INDIO = centroid of the real recording; 1.0 = same voice):'); print('%-13s' % '' + ''.join('%13s' % n[:12] for n in names))
for x in names: print('%-13s' % x[:12] + ''.join('%13.3f' % float(V[x] @ V[y]) for y in names))
