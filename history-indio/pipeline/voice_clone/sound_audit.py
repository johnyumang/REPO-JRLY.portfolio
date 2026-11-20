"""SOUND_AUDIT.md for a built multi-voice episode: one row per spoken line, then what a listener would notice, worst first.
usage: sound_audit.py <work dir> <post dir (ms_post.py out)> <stems.npz (HI_MIX_STEMS) or -> <out.md> [--offset S]
--offset: seconds the story's voice starts into the final film (0 for the new form).
Per line: loudness against the speaker's median (LU), speaker similarity (Indio: centroid of the real recording; others: their
own reference clip), median pitch, speed (syllables a second), gap before, clipped start or end, bed level against the voice
during the line, effect level on the words, the words the recogniser hears against the script.
Limits it flags (central, 15 Nov): loudness off the median by more than 1 LU; Indio under 0.93; narrator speed outside
5.0-5.5; gaps outside 0.30-0.45 inside a scene (0.7-0.9 at a scene change); bed or effects less than 14 dB under the voice;
a clipped edge; a wrong word."""
import json, os, sys
import numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import vqc, vprofile as VP
from ms import ref_emb

W, P, STEMS, OUT = sys.argv[1:5]
tim = json.load(open(os.path.join(P, 'timings.json'))); rep = json.load(open(os.path.join(P, 'post_report.json')))
plan = json.load(open(os.path.join(W, 'plan.json'))); S = {s['i']: s for s in plan['sentences']}
y, SR = sf.read(os.path.join(P, 'voice.wav'), dtype='float64')
sys.argv = sys.argv[:1]
_src = open(os.path.join(HERE, 'ms_post.py')).read(); from scipy.signal import lfilter
exec(_src[_src.index('def kweight'):_src.index('# scenes from the script headers')])   # kweight(), loud(), env_db() of ms_post.py
st = np.load(STEMS) if STEMS != '-' else None


def rms(x): return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)


rows = []; refs = {}
L = {r['i']: r for r in rep['lines']}
for k, s in enumerate(tim):
    a, b = s['start'], s['end']; x = y[int(max(0, a - 0.015) * SR):int((b + 0.03) * SR)]
    spk = s['speaker']; lo = loud(x, SR)
    if spk not in refs: refs[spk] = ref_emb(W, spk)
    e, rf0 = refs[spk]; x16 = vqc.load16(x.astype(np.float32), SR)
    sim = float(np.dot(vqc.spk(x16), e)) if len(x16) > 8000 else None
    f0, _ = vqc.f0_stats(x16); syl = vqc.syllables(S[k]['say']); rate = syl / max(0.2, b - a)
    heard = vqc.asr(x16); ed = vqc.edits(S[k]['say'], heard)
    d, h = env_db(x, SR); pk = d.max()
    clip0 = d[0] > pk - 20; clip1 = d[-1] > pk - 20
    bed = fxl = None
    if st is not None:
        sv = st['voice']; ss = int(st['sr']); i0, i1 = int(a * ss), int(b * ss)
        vr = rms(sv[i0:i1]); bed = rms(st['bed'][i0:i1]) - vr; fxl = rms(st['fx'][i0:i1]) - vr
    rows.append(dict(i=k, spk=spk, text=s['text'], t=a, lo=lo, sim=sim, f0=f0, rate=rate, gap=L[k]['gap_before'], scene=L[k]['scene'],
                     clip0=clip0, clip1=clip1, bed=bed, fx=fxl, heard=heard, edits=ed))
    print(k, spk, round(lo, 1), sim and round(sim, 3), round(rate, 2), ed, heard[:50], flush=True)

med = {}
for r in rows: med.setdefault(r['spk'], []).append(r['lo'])
med = {k: float(np.median(v)) for k, v in med.items()}
nar = [r for r in rows if r['spk'] == 'TAGAPAGSALAYSAY']
issues = []
for r in rows:
    r['dl'] = r['lo'] - med[r['spk']]; f = []
    if abs(r['dl']) > 1.0: f.append((abs(r['dl']) * 2, 'loudness %+.1f LU off %s median' % (r['dl'], r['spk'])))
    if r['spk'] == 'INDIO' and r['sim'] is not None and r['sim'] < 0.93: f.append(((0.93 - r['sim']) * 100, 'Indio similarity %.3f (< 0.93)' % r['sim']))
    if r['spk'] == 'TAGAPAGSALAYSAY' and not (5.0 <= r['rate'] <= 5.5): f.append((abs(r['rate'] - 5.25) * 3, 'narrator speed %.2f syl/s (5.0-5.5)' % r['rate']))
    if r['i']:
        lo_, hi_ = (0.30, 0.45) if r['scene'] == rows[r['i'] - 1]['scene'] else (0.70, 0.90)
        if not (lo_ - 1e-3 <= r['gap'] <= hi_ + 1e-3) and r['gap'] < 0.55 or r['gap'] > hi_ + 0.25: f.append((1, 'gap %.2f s' % r['gap']))
    if r['clip0'] or r['clip1']: f.append((4, 'clipped ' + ('start' if r['clip0'] else '') + (' end' if r['clip1'] else '')))
    if r['bed'] is not None and r['bed'] > -14: f.append((r['bed'] + 14 + 2, 'bed %.1f dB under the voice (< 14)' % -r['bed']))
    if r['fx'] is not None and r['fx'] > -14: f.append((r['fx'] + 14 + 2, 'effects %.1f dB under the voice on the words' % -r['fx']))
    if r['edits'] > VP.PROFILE['max_edits']: f.append((5 + r['edits'], 'heard "%s"' % r['heard']))
    r['flags'] = f
    for sc, msg in f: issues.append((sc, r, msg))
with open(OUT, 'w') as fh:
    fh.write('# Sound audit\n\nOne row per spoken line of the story (trivia not included). Times are seconds into the story voice.\n')
    fh.write('Loudness is K-weighted and gated (LUFS-like) against the speaker\'s median; similarity is to the speaker\'s reference '
             '(Indio: his real recording). Bed and effects are measured during the line against the voice, before the final loudness guard.\n\n')
    fh.write('Speaker medians: ' + ', '.join('%s %.1f' % kv for kv in med.items()) + '\n\n')
    fh.write('| # | s | speaker | LU vs median | similarity | pitch Hz | syl/s | gap before | clipped | bed dB | fx dB | wrong words | line |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|\n')
    for r in rows:
        fh.write('| %d | %.2f | %s | %+.1f | %s | %s | %.2f | %.2f | %s | %s | %s | %s | %s |\n' % (
            r['i'], r['t'], r['spk'], r['dl'], '%.3f' % r['sim'] if r['sim'] is not None else 'short', '%.0f' % r['f0'] if r['f0'] else '-', r['rate'], r['gap'],
            ('start ' if r['clip0'] else '') + ('end' if r['clip1'] else '') or 'no', '%.1f' % r['bed'] if r['bed'] is not None else '-',
            '%.1f' % r['fx'] if r['fx'] is not None else '-', ('heard: ' + r['heard']) if r['edits'] > VP.PROFILE['max_edits'] else 'none', r['text']))
    fh.write('\n## What a listener would notice, worst first\n\n')
    if not issues: fh.write('Nothing over the limits.\n')
    for sc, r, msg in sorted(issues, key=lambda z: -z[0]): fh.write('- %.2f s, line %d (%s, "%s"): %s\n' % (r['t'], r['i'], r['spk'], r['text'][:50], msg))
    if nar:
        rr = [r['rate'] for r in nar]; fh.write('\nNarrator: %d lines, speed %.2f to %.2f syl/s, loudness spread %.1f LU.\n' % (len(nar), min(rr), max(rr), max(r['dl'] for r in nar) - min(r['dl'] for r in nar)))
print('wrote', OUT, '|', len(issues), 'flags')
