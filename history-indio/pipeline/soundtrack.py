"""Synthesised music bed + SFX, mixed under the voice at half level (-6 dB).
make(voice_path, cuts, hits, out_path): cuts = cut times (whoosh), hits = twist times (low hit)."""
import numpy as np, soundfile as sf, subprocess, tempfile, os
SR = 44100


def _env(n, a=0.005, d=0.25):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)


def music(dur, bpm=96, seed=3):
    rng = np.random.default_rng(seed); n = int(dur * SR); out = np.zeros(n, np.float32); beat = 60 / bpm
    scale = [0, 3, 5, 7, 10]; root = 110.0   # A minor pentatonic
    prog = [0, 0, 5, 7]
    def add(sig, t0):
        i = int(t0 * SR)
        if i < n: out[i:i + len(sig)] += sig[:n - i]
    b = 0
    while b * beat < dur:
        t0 = b * beat; bar = (b // 4) % 4
        # kick on 1 and 3, rim on 2 and 4 (light, kulintang-ish feel)
        if b % 2 == 0:
            m = int(.22 * SR); tt = np.arange(m) / SR
            add((np.sin(2 * np.pi * (55 + 70 * np.exp(-tt * 28)) * tt) * np.exp(-tt * 14) * .8).astype(np.float32), t0)
        else:
            m = int(.08 * SR); add((rng.normal(0, 1, m) * np.exp(-np.arange(m) / SR * 55) * .22).astype(np.float32), t0)
        # bass
        f = root * 2 ** (prog[bar] / 12) / 2; m = int(beat * .9 * SR); tt = np.arange(m) / SR
        add((np.sign(np.sin(2 * np.pi * f * tt)) * .0 + np.sin(2 * np.pi * f * tt) * _env(m, .01, .35) * .5).astype(np.float32), t0)
        # plucked melody on 8th notes (gong/kulintang-like bell tone)
        for h in range(2):
            if rng.random() < .72:
                st = scale[rng.integers(0, 5)] + prog[bar] + 12 * rng.integers(1, 3); f2 = root * 2 ** (st / 12)
                m = int(.5 * SR); tt = np.arange(m) / SR
                add(((np.sin(2 * np.pi * f2 * tt) + .4 * np.sin(2 * np.pi * f2 * 2.76 * tt) * np.exp(-tt * 9)) * _env(m, .003, .16) * .23).astype(np.float32), t0 + h * beat / 2)
        b += 1
    fade = int(1.5 * SR); out[-fade:] *= np.linspace(1, 0, fade); return out


def sfx(dur, cuts, hits):
    rng = np.random.default_rng(9); n = int(dur * SR); out = np.zeros(n, np.float32)
    for c in cuts:                                   # whoosh into each cut
        m = int(.28 * SR); x = rng.normal(0, 1, m); k = np.linspace(0, 1, m)
        y = np.zeros(m); a = 0.0
        for i in range(m):                           # swept one-pole low-pass
            al = .02 + .5 * k[i] ** 2; a += al * (x[i] - a); y[i] = a
        y *= np.sin(np.pi * k) ** 2 * .7; i0 = max(0, int(c * SR) - m // 2)
        out[i0:i0 + m] += y[:n - i0].astype(np.float32)
    for h in hits:                                   # low sting on the twist
        m = int(1.2 * SR); tt = np.arange(m) / SR
        y = (np.sin(2 * np.pi * 48 * tt) + .5 * np.sin(2 * np.pi * 72 * tt)) * np.exp(-tt * 2.6) + rng.normal(0, 1, m) * np.exp(-tt * 30) * .5
        i0 = int(h * SR); out[i0:i0 + m] += y[:n - i0].astype(np.float32)
    return out


def gated_rms(x, win=0.4):
    w = int(win * SR); r = np.array([np.sqrt(np.mean(x[i:i + w] ** 2)) for i in range(0, max(1, len(x) - w), w)])
    r = r[r > r.max() * 0.1]; return float(np.sqrt(np.mean(r ** 2)))


LUFS, TP = -16.0, -1.5                     # final mix target: integrated loudness, true-peak ceiling (dBTP)


AAC = ('-c:a', 'aac', '-b:a', '192k')     # the encode build_anime.py uses: the true peak is checked after it


def true_peak(path, encode=False):
    """True peak (dBTP) of path's audio; encode=True measures it after an AAC encode like the final MP4's."""
    return ebur(path, encode)[1]


LUFS_TOL = 0.5                               # an output is accepted at LUFS +/- LUFS_TOL and true peak <= TP
TRIES = 6


def ebur(path, encode=False):
    """(integrated LUFS, true peak dBTP) of path's audio at full precision; encode=True measures after an AAC encode like the
    final MP4's. Read from ebur128's per-frame metadata (last lavfi.r128.I, largest lavfi.r128.true_peak), not its Summary:
    the Summary prints 0.1 dB, so a file at -1.46 dBTP or -15.46 LUFS read -1.5 / -15.5 and passed (review, 2026-11-13).
    Every pass/fail decision on loudness (loudnorm2, build_anime.py's final check, trivia_break.py) goes through here."""
    src = path
    if encode:
        src = tempfile.mktemp(suffix='.m4a'); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', path, '-vn'] + list(AAC) + [src], check=True)
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', src, '-vn', '-af', 'ebur128=peak=true:metadata=1,ametadata=mode=print:file=-',
                        '-f', 'null', '-'], capture_output=True, text=True)
    if encode: os.remove(src)
    I = [float(l.split('=', 1)[1]) for l in r.stdout.splitlines() if l.startswith('lavfi.r128.I=')]
    P = [float(l.split('=', 1)[1]) for l in r.stdout.splitlines() if l.startswith('lavfi.r128.true_peak=')]
    if not I or not P:                                                               # under 0.1 s: no frame out, only the Summary
        e = r.stderr.split('Summary')[-1]; g = lambda k: float([l.split(':')[1].split()[0] for l in e.splitlines() if l.strip().startswith(k)][-1])
        return g('I:'), g('Peak:')
    return I[-1], float(20 * np.log10(max(max(P), 1e-10)))


GUARD = 'loudness guard v3'                 # printed first by loudnorm2, so a log shows which guard ran
GAIN_CAP = 36.0                              # dB: the most gain the guard applies to reach LUFS (more means the input is broken or silent)


def _limit(x, lim_db, sr, attack=0.0015, release=0.06, blk=32):
    """Look-ahead peak limiter done here at 4x oversampling, so its ceiling holds by construction: returns y (same shape as x,
    rate sr) whose 4x-oversampled peak is at or under lim_db dBFS however hard x drives it. The gain is the per-block need
    (min over the block and its neighbour), a look-ahead min over the attack, an exponential release, then a box smoothing over
    the attack: every step can only lower the gain under what each sample needs, so no sample passes the ceiling. Material under
    the ceiling comes back untouched. Up to 3 passes catch the small overshoot of the downsampling; a last plain scaling
    (exact) covers whatever remains."""
    from scipy.signal import resample_poly
    L = 10 ** (lim_db / 20); y = x
    for _ in range(3):
        u = resample_poly(y, 4, 1, axis=0); a = np.abs(u).max(axis=1)
        if a.max() <= L: return y
        q = np.minimum(1.0, L / np.maximum(a, 1e-12)); nb = -(-len(q) // blk)
        qb = np.pad(q, (0, nb * blk - len(q)), constant_values=1.0).reshape(nb, blk).min(axis=1)
        pb = np.minimum(qb, np.r_[1.0, qb[:-1]])                                     # block j's gain also bounds the ramp into block j+1
        na = max(1, int(round(attack * 4 * sr / blk)))
        m = np.lib.stride_tricks.sliding_window_view(np.r_[pb, np.ones(na - 1)], na).min(axis=1)    # look-ahead: down before the peak
        c = float(np.exp(-blk / (4 * sr * release))); d = 1.0 - m; r = np.empty(nb); h = 0.0
        for j, dj in enumerate(d.tolist()):                                          # release: recover towards 1, never above the need
            h = h * c
            if dj > h: h = dj
            r[j] = 1.0 - h
        cs = np.cumsum(np.r_[np.full(na, r[0]), r]); s = (cs[na:] - cs[:-na]) / na          # attack smoothing (causal box over the look-ahead)
        g = np.interp(np.arange(len(q)), np.arange(nb) * blk, s).astype(u.dtype)
        y = resample_poly(u * g[:, None], 1, 4, axis=0)[:len(x)].astype(x.dtype)
    p = np.abs(resample_poly(y, 4, 1, axis=0)).max()
    return y * (L / p) if p > L else y


def _read(src, af=''):
    """src's audio as float32 (samples, channels) at SR, through the ffmpeg filter af if given."""
    tmp = tempfile.mktemp(suffix='.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vn'] + (['-af', af] if af else []) + ['-ar', str(SR), '-c:a', 'pcm_f32le', tmp], check=True)
    x, _ = sf.read(tmp, dtype='float32', always_2d=True); os.remove(tmp); return x


def loudnorm2(src, dst, extra=('-c:a', 'pcm_s16le'), check_encoded=True):
    """Bring src's audio to LUFS (+/- LUFS_TOL) with the true peak at or under TP, both measured as delivered (after the AAC
    encode for a WAV dst; dst's own audio for an MP4). Each round: one linear gain, then the look-ahead limiter of _limit at
    4x oversampling (its ceiling holds by construction), then dst is written and measured. The control is monotone: the limiter
    only ever goes down (by the measured encode overshoot + 0.3 dB when the peak is over), the gain is never raised in a round
    whose peak was over, gain steps use the measured loudness-per-dB slope, and the total gain is capped at GAIN_CAP. Up to
    TRIES rounds; dst keeps the best round under the ceiling. A file that still misses stops the run (SystemExit with a
    LOUDNESS GUARD FAILED line). (v1 used loudnorm, which turns dynamic when the peaks forbid the gain (Episode 11: -17.0 LUFS),
    then ffmpeg's alimiter without delay compensation: its 2 ms shift alone moved the AAC overshoot by up to 1 dB, and lowering
    it only clipped harder (Episode 22: -1.0 -> +0.1 -> +0.8 dBTP). v2 (24b37df) kept alimiter, whose hard clip at the limit
    rebounds after the band-limit: set at -2.5 and driven 18 dB it delivered -0.1 dBTP.)
    Returns (before, after) LUFS."""
    print(GUARD, flush=True)
    i0, tp0 = ebur(src)
    if i0 <= -69.0 or LUFS - i0 > GAIN_CAP:
        raise SystemExit(f'LOUDNESS GUARD FAILED: {dst}: input is {i0:.2f} LUFS, it needs more than the {GAIN_CAP:.0f} dB gain cap to reach '
                         f'{LUFS} (silent, broken or too short to measure). Do not publish this file.')
    x = _read(src)                                                                   # no low-pass: v2's 16 kHz IIR one changed the mix by -22 dB (phase)
    enc = check_encoded and dst.lower().endswith('.wav'); tmp = tempfile.mktemp(suffix='.wav')
    ex = list(extra); maps = ['1:a:0' if (k and ex[k - 1] == '-map' and e.startswith('0:a')) else e for k, e in enumerate(ex)]
    if '-map' not in ex: maps = ['-map', '1:a:0'] + maps                             # input 0 = src (video, if any), input 1 = the limited audio
    gain, lim, over = LUFS - i0, TP - 0.5, 0.0                                       # limiter 0.5 dB under the ceiling, as v1; over: largest encode overshoot (dB)
    rounds, best, slope = [], None, 1.0                                              # slope: LUFS per dB of gain (limiting eats some)
    def render(g, l):
        sf.write(tmp, _limit(x * np.float32(10 ** (g / 20)), l, SR), SR, subtype='FLOAT')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-i', tmp] + maps + [dst], check=True)
        return ebur(dst, encode=enc)
    for k in range(TRIES):
        i, tp = render(gain, lim); rounds.append((gain, lim, i, tp))
        print(f'loudness round {k + 1}: gain {gain:+.2f} dB, limiter {lim:.2f} dBTP -> {i:.2f} LUFS, true peak {tp:.2f} dBTP', flush=True)
        ok = abs(i - LUFS) <= LUFS_TOL and tp <= TP
        if tp <= TP and (best is None or abs(i - LUFS) < abs(best[2] - LUFS)): best = rounds[-1]
        if ok and abs(i - LUFS) <= 0.2: break
        over = max(over, tp - lim)
        if tp > TP:                                                                  # peak over: lower the limiter, never raise the gain
            lim = min(lim - 0.3, TP - over - 0.3)
            if i > LUFS: gain -= i - LUFS
            continue
        same = [r for r in rounds[:-1] if r[1] == lim and abs(r[0] - gain) > 0.05]
        if same: slope = min(1.0, max(0.15, (i - same[-1][2]) / (gain - same[-1][0])))  # measured at this limiter; kept after it moves
        step = max(-12.0, min(12.0, (LUFS - i) / slope))
        if abs(step) < 0.02: break
        gain = max(-GAIN_CAP, min(GAIN_CAP, gain + step))
    if best is not None and best is not rounds[-1]:
        i, tp = render(best[0], best[1])                                             # keep the best round under the ceiling
    os.remove(tmp)
    if abs(i - LUFS) <= LUFS_TOL and tp <= TP: return i0, i
    why = (f'loudness cannot reach {LUFS - LUFS_TOL} without the true peak going over the ceiling; kept the peak under it'
           if tp <= TP and i < LUFS else f'loudness did not settle in {TRIES} rounds' if tp <= TP else 'the true peak stays over the ceiling')
    raise SystemExit(f'LOUDNESS GUARD FAILED: {dst}: {i:.2f} LUFS (target {LUFS} +/- {LUFS_TOL}), true peak {tp:.2f} dBTP (ceiling {TP}) '
                     f'after {len(rounds)} rounds; input was {i0:.2f} LUFS / {tp0:.2f} dBTP; {why}. Do not publish this file.')


def make(voice_path, cuts, hits, out_path):
    tmp = tempfile.mktemp(suffix='.wav'); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', voice_path, '-ac', '1', '-ar', str(SR), tmp], check=True)
    v, _ = sf.read(tmp, dtype='float32'); os.remove(tmp); dur = len(v) / SR + 0.8
    v = np.pad(v, (0, int(dur * SR) - len(v))); mu = music(dur)[:len(v)]; fx = sfx(dur, cuts, hits)[:len(v)]
    rv = gated_rms(v); mu *= 0.5 * rv / gated_rms(mu); fx *= 0.5 * rv / gated_rms(fx)
    pk = 0.7 * np.abs(v).max(); fx = np.clip(fx, -pk, pk)
    mix = v + mu + fx                       # no peak normalisation here: scaling to a fixed peak dropped the mix to about -21 LUFS
    raw = tempfile.mktemp(suffix='.wav'); sf.write(raw, mix, SR, subtype='FLOAT')
    loudnorm2(raw, out_path); os.remove(raw)
    db = lambda a: 20 * np.log10(a)
    return {'voice_rms_db': round(db(rv), 1), 'music_vs_voice_db': round(db(gated_rms(mu) / rv), 1), 'sfx_vs_voice_db': round(db(gated_rms(fx) / rv), 1), 'duration': round(dur, 2)}
