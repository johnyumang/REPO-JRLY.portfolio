#!/usr/bin/env python3
"""Apply videos/<slug>/narration_cuts.json to an assembled narration (13 Nov ruling: the fiction label lives in the captions).
usage: apply_cuts.py videos/<slug> <work>/voice [--write-fx]
Reads <work>/voice.wav and <work>/voice_timings.json (ms.py assemble), removes each cut sentence together with the pause
after it (so the sentence before a cut meets the one after with the pause that preceded the cut line), 15 ms crossfade at
every join, and writes <work>/voice_cut.wav, voice_cut.mp3 and voice_cut_timings.json (cut sentences gone, later ones
shifted). The shot of every later line moves down one index; --write-fx rewrites videos/<slug>/shots_fx.json so line i
keeps its old picture and moves through "key" (build_anime reuses that keyframe), so keys/ need no renumbering.
Checks each cut entry's text against the timings before cutting and refuses a mismatch."""
import json, os, subprocess, sys
import numpy as np, soundfile as sf

ep, vb = sys.argv[1], sys.argv[2]; work = os.path.dirname(vb)
C = json.load(open(os.path.join(ep, 'narration_cuts.json'))); T = json.load(open(vb + '_timings.json'))
y, sr = sf.read(vb + '.wav', dtype='float32')
norm = lambda s: ' '.join(s.lower().split())
cut = sorted(c['index'] for c in C.get('cut', []))
for c in C.get('cut', []):
    if norm(T[c['index']]['text']) != norm(c['text']): sys.exit('cut %d: text does not match the timings: %r' % (c['index'], T[c['index']]['text'][:60]))
if C.get('revoice'): print('NOTE: revoice entries present; record them before this step:', C['revoice'])
# spans to remove: [start of cut line, start of the next kept line); the last line cut -> to the end of the line + 0.05 s
spans = []
for i in cut:
    a = T[i]['start']; j = i + 1
    while j in cut: j += 1
    b = T[j]['start'] if j < len(T) else T[i]['end'] + 0.05
    if spans and abs(spans[-1][1] - a) < 1e-6: spans[-1] = (spans[-1][0], b)
    else: spans.append((a, b))
mono = y if y.ndim == 1 else y.mean(1); W20 = int(0.02 * sr)
def quiet(i): return i >= W20 and 20 * np.log10(np.sqrt(np.mean(mono[i - W20:i] ** 2)) + 1e-9) < -55
def back_to_silence(i, lo):                     # a line's audio can start before its timing (breath, lead-in): move the cut point
    while i > lo and not quiet(i): i -= int(0.005 * sr)   # back into the pause, so no syllable of the cut line is left over
    return i
X = int(0.015 * sr); out = []; pos = 0; shift = []
for k, (a, b) in enumerate(spans):
    prev_end = max([s['end'] for s in T if s['end'] <= a + 1e-6] or [0.0])
    ia, ib = back_to_silence(int(a * sr), int(prev_end * sr)), back_to_silence(int(b * sr), int(a * sr))
    if not quiet(ia): sys.exit('no silence found before the cut at %.2f s' % a)
    a, b = ia / sr, ib / sr; spans[k] = (a, b)
    out.append(y[pos:ia]); pos = ib; shift.append((a, b - a))
out.append(y[pos:])
# crossfade each join (end of one piece into the start of the next)
res = out[0]
for seg in out[1:]:
    n = min(X, len(res), len(seg))
    if n:
        w = np.linspace(0, 1, n); w = w[:, None] if y.ndim > 1 else w
        res = np.concatenate([res[:-n], res[-n:] * (1 - w) + seg[:n] * w, seg[n:]])
    else: res = np.concatenate([res, seg])
def moved(t):
    d = 0.0
    for a, L in shift:
        if t >= a + L - 1e-6: d += L
    return round(t - d, 3)
NT = []
for i, s in enumerate(T):
    if i in cut: continue
    s = dict(s); s['start'], s['end'] = moved(s['start']), moved(s['end']); NT.append(s)
sf.write(work + '/voice_cut.wav', res, sr); json.dump(NT, open(work + '/voice_cut_timings.json', 'w'), ensure_ascii=False, indent=1)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', work + '/voice_cut.wav', '-c:a', 'libmp3lame', '-b:a', '192k', work + '/voice_cut.mp3'], check=True)
print('cut sentences %s: %.2f s removed, %d -> %d lines, %.2f s -> %.2f s' % (cut, sum(L for _, L in shift), len(T), len(NT), len(y) / sr, len(res) / sr))
for i in cut:
    k = i - sum(1 for c in cut if c < i)
    if 0 < k < len(NT): print('join: [%d] %s / [%d] %s' % (k - 1, NT[k - 1]['text'][-50:], k, NT[k]['text'][:50]))
if '--write-fx' in sys.argv:
    p = os.path.join(ep, 'shots_fx.json'); FX = json.load(open(p)) if os.path.exists(p) else {}
    if FX.get('_cuts_applied'): sys.exit('shots_fx.json already has cuts applied: %s' % FX['_cuts_applied'])
    keep = [i for i in range(len(T)) if i not in cut]; N = {}
    for k, old in enumerate(keep):
        cfg = dict(FX.get(str(old), {}))
        if k != old: cfg.setdefault('key', cfg.get('key', old))
        if cfg: N[str(k)] = cfg
    N.update({k: v for k, v in FX.items() if not k.isdigit() or int(k) >= len(T)})          # cut-ins and notes beyond the lines stay
    N['_cuts_applied'] = cut
    json.dump(N, open(p, 'w'), ensure_ascii=False, indent=1); print('shots_fx.json: lines after each cut keep their pictures via "key"')
