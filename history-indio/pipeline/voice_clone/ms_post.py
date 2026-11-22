"""Sound rules of 15 Nov for a finished multi-voice read: level every line to its speaker's median and set the gaps.
usage: ms_post.py <work dir (ms.py assemble output)> <episode dir> <out dir>
Reads <work>/voice.mp3 + <work>/voice_timings.json and <episode>/script_multispeaker.txt (scenes = '# ---' headers),
optional <episode>/voice_post.json {"hush_before": [sentence, ...], "hush": 0.6, "balance": {"to": "TAGAPAGSALAYSAY", "max": 2.0, "allow": {"MGA KAKLASE": 3.5}}}
(balance: no speaker's median sits more than max LU from the named speaker's; allow = a larger margin above for one voice).
Each sentence is cut at the quiet between it and its neighbours (never inside a word), gained so its loudness (K-weighted,
gated, BS.1770 style) sits on its speaker's median, then joined again with:
  0.30-0.45 s between sentences of a scene (a natural pause inside that range is kept, others become 0.38 / 0.42 at a turn),
  0.80 s at a scene change, and the 'hush' before each listed sentence (the hero's line).
No time-stretching: the words are never resampled, only moved and gained.
Writes <out>/voice.wav, <out>/voice.mp3, <out>/timings.json (same entries, new times) and <out>/post_report.json."""
import json, os, re, sys, subprocess
import numpy as np, soundfile as sf
from scipy.signal import lfilter

W, EP, OUT = sys.argv[1:4]
os.makedirs(OUT, exist_ok=True)
tim = json.load(open(os.path.join(W, 'voice_timings.json')))
cfg = json.load(open(os.path.join(EP, 'voice_post.json'))) if os.path.exists(os.path.join(EP, 'voice_post.json')) else {}
HUSH_AT = set(cfg.get('hush_before', [])); HUSH = float(cfg.get('hush', 0.6))
tmp = os.path.join(OUT, '_in.wav'); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(W, 'voice.mp3'), '-ac', '1', tmp], check=True)
y, SR = sf.read(tmp, dtype='float64'); os.remove(tmp)


def kweight(x, sr):
    """BS.1770 pre-filter (shelf + high-pass), coefficients for the actual rate via the bilinear-transform formulas."""
    import math
    f0, G, Q = 1681.974450955533, 3.999843853973347, 0.7071752369554196
    K = math.tan(math.pi * f0 / sr); Vh = 10 ** (G / 20); Vb = Vh ** 0.4996667741545416
    a0 = 1 + K / Q + K * K
    b = [(Vh + Vb * K / Q + K * K) / a0, 2 * (K * K - Vh) / a0, (Vh - Vb * K / Q + K * K) / a0]; a = [1, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0]
    x = lfilter(b, a, x)
    f0, Q = 38.13547087602444, 0.5003270373238773; K = math.tan(math.pi * f0 / sr)
    a0 = 1 + K / Q + K * K
    return lfilter([1, -2, 1], [1, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0], x)


def loud(x, sr):
    """Loudness of a short line: 100 ms blocks, absolute gate -70, relative gate -10 LU (integrated-loudness rule on short blocks)."""
    z = kweight(x, sr) ** 2; n = int(0.1 * sr); m = len(z) // n
    if m < 2: return -70.0
    bl = z[:m * n].reshape(m, n).mean(1); lk = -0.691 + 10 * np.log10(bl + 1e-12)
    g = bl[lk > -70]
    if not len(g): return -70.0
    rel = -0.691 + 10 * np.log10(g.mean()) - 10; g = bl[(lk > -70) & (lk > rel)]
    return float(-0.691 + 10 * np.log10(g.mean()))


def env_db(x, sr, w=0.01):
    n = int(w * sr); m = len(x) // n
    return 20 * np.log10(np.sqrt((x[:m * n].reshape(m, n) ** 2).mean(1)) + 1e-9), n


# scenes from the script headers, matched to sentences in order
scene_of = []; sc = -1; lines = []
for L in open(os.path.join(EP, 'script_multispeaker.txt'), encoding='utf-8'):
    L = L.strip()
    if L.startswith('# ---'): sc += 1; continue
    if not L or L.startswith('#') or L.startswith('('): continue
    mm = re.match(r'^([A-ZÑ][A-ZÑ .\'-]*?)(?:\s*\([^)]*\))?:\s*(?:\[[^\]]*\]\s*)?(.*)$', L)
    if mm: lines.append((max(sc, 0), re.sub(r'\W+', '', mm.group(2).lower())))
li = 0; rest = lines[0][1] if lines else ''
for s_ in tim:
    t = re.sub(r'\W+', '', s_['text'].lower())
    while not rest.startswith(t) and li + 1 < len(lines): li += 1; rest = lines[li][1]
    if not rest.startswith(t): sys.exit('ms_post: sentence %r not found in the script lines' % s_['text'])
    scene_of.append(lines[li][0]); rest = rest[len(t):]
assert len(scene_of) == len(tim)

# cut points: the quietest 10 ms in the gap between two sentences (gap = previous end .. next start)
db, hop = env_db(y, SR)
def quiet_between(a, b):
    i0, i1 = int(a * SR / hop), max(int(a * SR / hop) + 1, int(b * SR / hop))
    seg = db[i0:i1]
    return (i0 + int(np.argmin(seg))) * hop / SR if len(seg) else a
bounds = [0.0]
for i in range(len(tim) - 1):
    bounds.append(quiet_between(tim[i]['end'], tim[i + 1]['start']) if tim[i + 1]['start'] > tim[i]['end'] else tim[i]['end'])
bounds.append(len(y) / SR)
pieces = []
for i, s in enumerate(tim):
    a, b = bounds[i], bounds[i + 1]
    x = y[int(a * SR):int(b * SR)].copy()
    # the speech inside the piece: its energy edges (35 dB under the piece's peak), so a gap is measured word to word
    d, h = env_db(x, SR); thr = d.max() - 35; on = np.where(d > thr)[0]
    s0, s1 = (on[0] * h, (on[-1] + 1) * h) if len(on) else (0, len(x))
    s0 = max(0, s0 - int(0.015 * SR)); s1 = min(len(x), s1 + int(0.03 * SR))
    pieces.append(dict(i=i, spk=s['speaker'], x=x[s0:s1], L=loud(x[s0:s1], SR), nat_gap=None))
for i in range(1, len(pieces)):
    pieces[i]['nat_gap'] = round((tim[i]['start'] - tim[i - 1]['end']), 3)

med = {}
for p in pieces: med.setdefault(p['spk'], []).append(p['L'])
med = {k: float(np.median(v)) for k, v in med.items()}
tgt = dict(med)                                             # optional balance between speakers (voice_post.json "balance": {"to": speaker, "max": 2.0, "allow": {speaker: LU}})
if cfg.get('balance'):
    b = cfg['balance']; ref = med[b['to']]
    for k in tgt: mx = float(b.get('allow', {}).get(k, b.get('max', 2.0))); tgt[k] = float(np.clip(med[k], ref - float(b.get('max', 2.0)), ref + mx))
out = []; T = 0.0; rep = []; new_tim = []
for k, p in enumerate(pieces):
    g = float(np.clip(tgt[p['spk']] - p['L'], -10, 10)); x = p['x'] * 10 ** (g / 20)
    f = int(0.006 * SR); x[:f] *= np.linspace(0, 1, f); x[-int(0.02 * SR):] *= np.linspace(1, 0, int(0.02 * SR))
    if k:
        same_scene = scene_of[k] == scene_of[k - 1]; turn = tim[k]['speaker'] != tim[k - 1]['speaker']
        ng = p['nat_gap'] if p['nat_gap'] is not None else 0.38
        gap = (ng if 0.30 <= ng <= 0.45 else (0.42 if turn else 0.38)) if same_scene else 0.80
        if k in HUSH_AT: gap = max(gap, HUSH)
        out.append(np.zeros(int(gap * SR))); T += int(gap * SR) / SR
    else: gap = 0.0
    st = T; out.append(x); T += len(x) / SR
    e = dict(tim[k])
    e['start'] = round(st + 0.015, 3); e['end'] = round(T - 0.03, 3); new_tim.append(e)
    rep.append(dict(i=k, speaker=p['spk'], scene=scene_of[k], loud_before=round(p['L'], 2), gain_db=round(g, 2), gap_before=round(gap, 3), natural_gap=p['nat_gap']))
yo = np.concatenate(out + [np.zeros(int(0.3 * SR))])
pk = np.abs(yo).max()
if pk > 0.89: yo *= 0.89 / pk
sf.write(os.path.join(OUT, 'voice.wav'), yo.astype(np.float32), SR, subtype='PCM_24')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(OUT, 'voice.wav'), '-c:a', 'libmp3lame', '-b:a', '256k', os.path.join(OUT, 'voice.mp3')], check=True)
json.dump(new_tim, open(os.path.join(OUT, 'timings.json'), 'w'), indent=1, ensure_ascii=False)
json.dump(dict(medians=med, lines=rep), open(os.path.join(OUT, 'post_report.json'), 'w'), indent=1, ensure_ascii=False)
print('speaker medians (LUFS-like):', {k: round(v, 1) for k, v in med.items()})
print('lines %d, scenes %d, length %.2f s (was %.2f s), largest gain %+.1f dB' % (len(rep), max(scene_of) + 1, len(yo) / SR, len(y) / SR, max(abs(r['gain_db']) for r in rep)))
