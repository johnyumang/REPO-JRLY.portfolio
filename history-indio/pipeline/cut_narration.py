#!/usr/bin/env python3
"""Cut the sentences named in videos/<slug>/narration_cuts.json out of a FINISHED narration file, at the quiet points
around them, and write the timings that go with the shorter file. For the episodes whose narration is one finished file
(Season 1 layout) and for a cut sentence that shares a recorded chunk with a kept one. Where every cut sentence has its
own chunk(s), `voice_clone/ms.py assemble <W> <W>/voice --cut i,j` does the same from the takes and is the first choice.

usage: cut_narration.py videos/<slug> <voice in> <voice out> [--timings <timings of the voice in>] [--write] [--pause S]
  <voice in>   the full narration (wav is best; mp3 is decoded with ffmpeg), the one timings.json was made from
  <voice out>  wav, mp3 or flac by its ending; <voice out minus ending>_timings.json is always written beside it
  --timings    default videos/<slug>/timings.json; when that one is already cut, videos/<slug>/timings_full.json
  --write      also put the new timings in videos/<slug>/timings.json (the full one is kept as timings_full.json)
  --pause S    pause left where a sentence was (default: the longer of the two pauses around it, 0.35 to 0.80 s)

Nothing is renumbered: sentences.json, key_prompts.json, shots_fx.json and the keys keep the original numbers
(pipeline/narration_cuts.py maps them at build time). A sentence that a "revoice" line replaces is NOT cut here.
The tool stops instead of cutting when the join would not be quiet (less than 8 dB under the speech around it).
After it: listen to each join (the times are printed), then build with the new voice.
self-test: cut_narration.py --self-test"""
import json, os, sys, subprocess, tempfile, shutil
import numpy as np, soundfile as sf

WIN, HOP, XF = 0.040, 0.005, 0.020                              # level window, search step, crossfade (seconds)


def read_audio(p):
    if p.lower().endswith(('.wav', '.flac')): y, sr = sf.read(p, dtype='float32', always_2d=True); return y, sr
    d = tempfile.mkdtemp(); w = os.path.join(d, 'in.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', p, '-c:a', 'pcm_f32le', w], check=True)
    y, sr = sf.read(w, dtype='float32', always_2d=True); shutil.rmtree(d); return y, sr


def write_audio(p, y, sr):
    if p.lower().endswith('.wav'): sf.write(p, y, sr, subtype='PCM_24'); return
    if p.lower().endswith('.flac'): sf.write(p, y, sr); return
    d = tempfile.mkdtemp(); w = os.path.join(d, 'out.wav'); sf.write(w, y, sr, subtype='PCM_24')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', w] + (['-c:a', 'libmp3lame', '-b:a', '192k'] if p.lower().endswith('.mp3') else []) + [p], check=True); shutil.rmtree(d)


def _rms(m, a, b): a, b = max(0, a), min(len(m), b); return float(np.sqrt(np.mean(m[a:b] ** 2) + 1e-12)) if b > a else 1.0


def quiet_points(m, sr, t0, t1):
    """-> [(seconds, level)] for every window centre between t0 and t1 (widened to 0.30 s when the pause is shorter)."""
    if t1 - t0 < 0.30: c = (t0 + t1) / 2; t0, t1 = c - 0.15, c + 0.15
    t0, t1 = max(WIN / 2, t0), min(len(m) / sr - WIN / 2, t1); out = []; t = t0
    while t <= t1 + 1e-9: c = int(t * sr); h = int(WIN * sr / 2); out.append((t, _rms(m, c - h, c + h))); t += HOP
    return out


def plan_cuts(m, sr, tim, gone, pause=None):
    """-> [(q1, q2, first, last, margins)] in seconds of the full file: remove q1..q2 for the run of cut sentences first..last."""
    n = len(tim); dur = len(m) / sr; runs = []; g = sorted(gone)
    for i in g:
        if runs and runs[-1][1] == i - 1: runs[-1][1] = i
        else: runs.append([i, i])
    cuts = []
    for a, b in runs:
        if a == 0 and b == n - 1: raise SystemExit('every sentence is cut')
        around = [k for k in (a - 2, a - 1, b + 1, b + 2) if 0 <= k < n and k not in gone]
        speech = float(np.sqrt(np.mean([_rms(m, int(tim[k]['start'] * sr), int(tim[k]['end'] * sr)) ** 2 for k in around])))
        L = quiet_points(m, sr, tim[a - 1]['end'], tim[a]['start']) if a > 0 else None
        R = quiet_points(m, sr, tim[b]['end'], tim[b + 1]['start']) if b < n - 1 else None
        if L is None: q2 = min(R, key=lambda x: x[1]); q1 = (0.0, q2[1]); q2 = (max(q2[0] - 0.04, 0.0), q2[1])       # the file now starts 40 ms before the next line's quiet point
        elif R is None: q1 = min(L, key=lambda x: x[1]); q2 = (dur, q1[1]); q1 = (min(q1[0] + 0.25, dur), q1[1])      # the file now ends 0.25 s after the last line's quiet point
        else:
            g1, g2 = tim[a]['start'] - tim[a - 1]['end'], tim[b + 1]['start'] - tim[b]['end']
            want = pause if pause else min(0.80, max(0.35, g1, g2))
            lo1, lo2 = min(x[1] for x in L), min(x[1] for x in R)
            Lq = [x for x in L if x[1] <= lo1 * 1.6]; Rq = [x for x in R if x[1] <= lo2 * 1.6]      # only points about as quiet as the quietest (4 dB)
            q1, q2 = min(((x, y) for x in Lq for y in Rq), key=lambda p: (abs((p[0][0] - tim[a - 1]['end']) + (tim[b + 1]['start'] - p[1][0]) - want), p[0][1] + p[1][1]))
        m1 = 20 * np.log10(speech / max(q1[1], 1e-9)); m2 = 20 * np.log10(speech / max(q2[1], 1e-9))
        cuts.append((q1[0], q2[0], a, b, (m1, m2)))
    return cuts


def apply(y, sr, tim, gone, cuts):
    """-> (new audio, new timings, [join time in the new file]). The new file is exactly as much shorter as the cuts are long."""
    xf = int(XF * sr); n = len(tim); keep = []; pos = 0; removed = []           # keep: sample ranges of the full file; removed: (last cut sentence, seconds)
    for q1, q2, a, b, _ in cuts:
        s1, s2 = int(round(q1 * sr)), int(round(q2 * sr)); keep.append((pos, s1)); removed.append((b, (s2 - s1) / sr)); pos = s2
    keep.append((pos, len(y))); out = y[keep[0][0]:keep[0][1]].copy(); joins = []
    for (p0, p1), (r0, r1) in zip(keep, keep[1:]):
        joins.append(len(out) / sr); seg = y[r0:r1].copy(); k = min(xf, len(out), r0)
        if k > 0 and len(seg):                                                   # crossfade over the last k samples before the join: what was there fades out, what led up to the next part fades in
            w = np.linspace(0, 1, k, dtype=np.float32)[:, None]; out[-k:] = out[-k:] * (1 - w) + y[r0 - k:r0] * w
        out = np.concatenate([out, seg])
    if cuts and cuts[0][2] == 0: f = min(int(0.03 * sr), len(out)); out[:f] *= np.linspace(0, 1, f, dtype=np.float32)[:, None]
    if cuts and cuts[-1][3] == n - 1: f = min(int(0.12 * sr), len(out)); out[-f:] *= np.linspace(1, 0, f, dtype=np.float32)[:, None]
    new = []
    for i, s in enumerate(tim):
        if i in gone: continue
        sh = sum(d for b, d in removed if i > b); e = dict(s); e['start'] = round(max(0.0, s['start'] - sh), 3); e['end'] = round(s['end'] - sh, 3); new.append(e)
    return out, new, joins


def run(v, vin, vout, tpath=None, write=False, pause=None):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import narration_cuts
    C = json.load(open(v + '/narration_cuts.json')); S = json.load(open(v + '/sentences.json')); n = len(S)
    new = {int(r['after_index']) + 1 for r in C.get('revoice', [])}; gone = {int(c['index']) for c in C.get('cut', [])} - new
    if not gone: print('nothing to cut here' + (' (the cut sentence is replaced by a new line: record it)' if new else '')); return 0
    tp = tpath or v + '/timings.json'; tim = json.load(open(tp))
    if not tpath and len(tim) == n - len(gone):
        if not os.path.exists(v + '/timings_full.json'): raise SystemExit('timings.json is already cut and there is no timings_full.json: give the full timings with --timings')
        tp = v + '/timings_full.json'; tim = json.load(open(tp)); print('timings.json is already cut: reading timings_full.json')
    if len(tim) != n: raise SystemExit(f'{tp} has {len(tim)} lines, sentences.json has {n}: the timings must be the ones of the FULL narration')
    for c in C['cut']:
        if tim[c['index']]['text'].strip() != c['text'].strip(): raise SystemExit('sentence %d of the timings is not the one the cut file names: "%s" / "%s"' % (c['index'], tim[c['index']]['text'][:60], c['text'][:60]))
    y, sr = read_audio(vin); dur = len(y) / sr; m = y.mean(axis=1)
    if not (tim[-1]['end'] - 0.3 <= dur <= tim[-1]['end'] + 6.0): raise SystemExit(f'{vin} lasts {dur:.1f} s but the timings end at {tim[-1]["end"]:.1f} s: is this the full narration these timings were made from?')
    cuts = plan_cuts(m, sr, tim, gone, pause)
    for q1, q2, a, b, (m1, m2) in cuts:
        print('cut sentences %s: %.2f to %.2f s (%.2f s out); the join is %.0f / %.0f dB under the speech around it' % (list(range(a, b + 1)), q1, q2, q2 - q1, m1, m2))
        if min(m1, m2) < 8: raise SystemExit('this join is not quiet enough to cut (under 8 dB): the sentence runs into its neighbour. Make a new take of the neighbour, or re-plan.')
        if min(m1, m2) < 12: print('  CAREFUL: under 12 dB. Listen to this join before the build.')
    out, newt, joins = apply(y, sr, tim, gone, cuts); write_audio(vout, out, sr)
    tout = os.path.splitext(vout)[0] + '_timings.json'; json.dump(newt, open(tout, 'w'), ensure_ascii=False, indent=1)
    print('%s: %.1f s -> %.1f s, %d lines -> %d; timings: %s' % (vout, dur, len(out) / sr, n, len(newt), tout))
    for j, (q1, q2, a, b, _) in zip(joins, cuts): print('  listen at %.1f s of the new file (where sentence%s %s %s)' % (j, 's' if b > a else '', ' to '.join(str(k) for k in sorted({a, b})), 'were' if b > a else 'was'))
    src, note = narration_cuts.source_index(v, newt); print(' ', note)
    if write:
        if not os.path.exists(v + '/timings_full.json'): shutil.copy(tp, v + '/timings_full.json')
        json.dump(newt, open(v + '/timings.json', 'w'), ensure_ascii=False, indent=1); print('  written: %s/timings.json (the full one: timings_full.json)' % v)
    return 0


def self_test():
    """A made voice: tone bursts as sentences with room noise between; cut one in the middle, a run of two, the first and the last."""
    sr = 24000; rng = np.random.default_rng(3); tim = []; y = [rng.normal(0, 0.0008, int(0.2 * sr))]; t = 0.2
    for i in range(8):
        d = 1.0 + 0.2 * (i % 3); tt = np.arange(int(d * sr)) / sr; env = np.minimum(1, np.minimum(tt, d - tt) / 0.05)
        y.append((0.2 * np.sin(2 * np.pi * (200 + 40 * i) * tt) * env).astype(np.float64)); tim.append({'text': 'pangungusap %d' % i, 'start': round(t, 3), 'end': round(t + d, 3), 'style': 'x'}); t += d
        g = 0.3 + 0.1 * (i % 4); y.append(rng.normal(0, 0.0008, int(g * sr))); t += g
    y = np.concatenate(y).astype(np.float32)[:, None]; m = y[:, 0]; ok = True
    def freq(seg): f = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))); return np.argmax(f) * sr / len(seg)
    for gone in ({3}, {2, 3}, {0}, {7}, {1, 4, 5}):
        cuts = plan_cuts(m, sr, tim, gone); out, newt, joins = apply(y, sr, tim, gone, cuts); kept = [i for i in range(8) if i not in gone]; bad = []
        if abs(len(out) / sr - (len(y) / sr - sum(q2 - q1 for q1, q2, *_ in cuts))) > 0.002: bad.append('length')
        if len(newt) != len(kept): bad.append('count')
        for e, i in zip(newt, kept):                                             # each kept sentence must sit where the new timings say: its own tone, loud
            a, b = int((e['start'] + 0.1) * sr), int((e['end'] - 0.1) * sr); seg = out[a:b, 0]
            if abs(freq(seg) - (200 + 40 * i)) > 6 or _rms(out[:, 0], a, b) < 0.1: bad.append('sentence %d misplaced' % i)
        for (q1, q2, a, b, mm) in cuts:
            if min(mm) < 30: bad.append('join not quiet')
        for k in range(len(newt) - 1):
            gap = newt[k + 1]['start'] - newt[k]['end']
            if not 0.2 <= gap <= 0.85: bad.append('pause %.2f after line %d' % (gap, k))
        for i in gone:                                                           # the cut tone must be gone from the whole file
            f = np.abs(np.fft.rfft(out[:, 0])); fr = np.fft.rfftfreq(len(out), 1 / sr); pk = f[np.abs(fr - (200 + 40 * i)) < 3].max(); ref = f[np.abs(fr - (200 + 40 * kept[0])) < 3].max()
            if pk > ref * 0.02: bad.append('sentence %d still heard' % i)
        print('cut', sorted(gone), '->', 'ok' if not bad else 'FAIL: ' + ', '.join(bad)); ok = ok and not bad
    # a sentence that runs into its neighbour (no pause, no quiet point) must be refused
    y2 = y.copy(); a, b = int(tim[3]['end'] * sr) - int(0.2 * sr), int(tim[4]['start'] * sr) + int(0.2 * sr); y2[a:b, 0] = 0.2 * np.sin(2 * np.pi * 300 * np.arange(b - a) / sr)
    c = plan_cuts(y2[:, 0], sr, tim, {4}); refused = min(c[0][4]) < 8; print('no pause before the cut sentence ->', 'refused, ok' if refused else 'FAIL: would cut'); ok = ok and refused
    print('self-test', 'PASSED' if ok else 'FAILED'); return 0 if ok else 1


if __name__ == '__main__':
    A = sys.argv[1:]
    if A[:1] == ['--self-test']: sys.exit(self_test())
    opt = lambda k: A[A.index(k) + 1] if k in A else None
    pos = [a for i, a in enumerate(A) if not a.startswith('--') and (i == 0 or A[i - 1] not in ('--timings', '--pause'))]
    if len(pos) != 3: sys.exit(__doc__)
    sys.exit(run(pos[0].rstrip('/'), pos[1], pos[2], opt('--timings'), '--write' in A, float(opt('--pause')) if opt('--pause') else None))
