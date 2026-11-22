"""QC every candidate take of a work dir against the real-voice baseline, then pick the best take per chunk (runs in /opt/vc).
usage: qcsel.py <work_dir>   -> <work_dir>/choice.json and one <take>.json per take; prints the chunks that need more takes"""
import os, sys, json, glob, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import vqc, vprofile as VP
work = sys.argv[1]; P = json.load(open(work + '/plan.json')); cen = VP.centroid()
RATE = VP.PROFILE['target_rate_syl_s']
# real Episode 1 sentence-median f0 range per tone (Hz); a take may sit 15% below / 10% above it
F0WIN = VP.PROFILE['f0_window_hz']
MAX_EDITS = VP.PROFILE['max_edits']                                                # real-recording p90 of vqc.edits (32/37 at 0, 5 at 1)
def qc(wav, text):
    a = vqc.load16(wav); W = vqc.words(a, text); conf = [w['conf'] for w in W]; st, en = W[0]['start'], W[-1]['end']; dur = len(a) / 16000
    body = a[int(st * 16000):int(en * 16000)]; b = np.sqrt(np.mean(body ** 2)) + 1e-9; r = lambda x: float(np.sqrt(np.mean(x ** 2)) / b) if len(x) > 160 else 0.0
    h = vqc.asr(a); f0, f0sd = vqc.f0_stats(body)
    return dict(dur=round(dur, 2), first=round(st, 3), last_end=round(en, 3), lead=round(r(a[:max(0, int((st - 0.04) * 16000))]), 3), trail=round(r(a[int((en + 0.10) * 16000):]), 3),
                rate=round(vqc.syllables(text) / max(.2, en - st), 2), match=round(vqc.match(text, h), 3), edits=vqc.edits(text, h), first_ok=vqc.first_ok(text, h), cmatch=round(vqc.cmatch(text, h), 3), conf=round(float(np.mean(conf)), 3), minconf=round(float(min(conf)), 3),
                low=[(w['w'], round(w['conf'], 2)) for w in W if w['conf'] < 0.4], spk=round(float(vqc.spk(a) @ cen), 3), f0=f0, f0sd=f0sd, rms=round(vqc.rms_db(body), 1), heard=h,
                words=[(w['w'], round(w['start'], 3), round(w['end'], 3), round(w['conf'], 3)) for w in W])
def score(m):
    s = 0.40 * m['cmatch'] + 0.25 * m['conf'] + 0.10 * min(m['minconf'], 0.8) / 0.8 + 0.25 * float(np.clip((m['spk'] - 0.90) / 0.08, 0, 1))
    dev = abs(m['rate'] - RATE) / RATE; s -= 0.3 * max(0, dev - 0.15); s -= 0.1 * (m['lead'] > 0.12) + 0.1 * (m['trail'] > 0.12)
    return round(s, 4)
def f0ok(m, style): lo, hi = F0WIN.get(style, F0WIN['narrate']); return m['f0'] is not None and lo * 0.85 <= m['f0'] <= hi * 1.10
def ok(m, style): return m['edits'] <= MAX_EDITS and m['first_ok'] and f0ok(m, style) and m['cmatch'] >= 0.88 and m['conf'] >= 0.84 and m['minconf'] >= 0.30 and m['spk'] >= 0.915 and 4.3 <= m['rate'] <= 7.4 and m['lead'] <= 0.12 and m['trail'] <= 0.12
choice = {}; redo = []
for c in P['chunks']:
    cands = sorted(glob.glob(f"{work}/c{c['id']:03d}_*.wav"))
    if not cands: continue
    best = None
    for w in cands:
        j = w[:-4] + '.json'
        if not os.path.exists(j): json.dump(qc(w, c['text']), open(j, 'w'), ensure_ascii=False)
        m = json.load(open(j)); m['score'] = score(m); m['ok'] = ok(m, c['style']); tag = os.path.basename(w)[5:-4]
        print('c%03d %-3s %s score %.3f | edits %d first %s f0win %s | cmatch %.2f match %.2f conf %.2f min %.2f spk %.3f rate %.2f f0 %3.0f(sd %.1f) rms %.1f dur %.1f lead %.2f trail %.2f | %s' % (c['id'], tag, 'OK ' if m['ok'] else 'BAD', m['score'], m['edits'], 'Y' if m['first_ok'] else 'N', 'Y' if f0ok(m, c['style']) else 'N', m['cmatch'], m['match'], m['conf'], m['minconf'], m['spk'], m['rate'], m['f0'] or 0, m['f0sd'] or 0, m['rms'], m['dur'], m['lead'], m['trail'], m['heard'][:110]), flush=True)
        key = lambda q: (q['ok'], -q['edits'], q['score'])                      # passing first, then fewest edits, then score
        if best is None or key(m) > key(best[1]): best = (w, m)
    choice[str(c['id'])] = dict(wav=best[0], ok=best[1]['ok'], score=best[1]['score'])
    if not best[1]['ok']: redo.append(c['id'])
json.dump(choice, open(work + '/choice.json', 'w'), indent=1)
print('chosen:', {k: os.path.basename(v['wav'])[5:-4] for k, v in choice.items()}); print('need more takes:', redo)
