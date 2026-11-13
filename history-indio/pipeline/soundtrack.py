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
    src = path
    if encode:
        src = tempfile.mktemp(suffix='.m4a'); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', path, '-vn'] + list(AAC) + [src], check=True)
    e = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', src, '-vn', '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    if encode: os.remove(src)
    return float([l.split(':')[1].split()[0] for l in e.split('Summary')[-1].splitlines() if l.strip().startswith('Peak:')][-1])


LUFS_TOL = 0.5                               # an output is accepted at LUFS +/- LUFS_TOL and true peak <= TP
TRIES = 4


def ebur(path, encode=False):
    """(integrated LUFS, true peak dBTP) of path's audio; encode=True measures after an AAC encode like the final MP4's."""
    src = path
    if encode:
        src = tempfile.mktemp(suffix='.m4a'); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', path, '-vn'] + list(AAC) + [src], check=True)
    e = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', src, '-vn', '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    if encode: os.remove(src)
    e = e.split('Summary')[-1]; g = lambda k: float([l.split(':')[1].split()[0] for l in e.splitlines() if l.strip().startswith(k)][-1])
    return g('I:'), g('Peak:')


def loudnorm2(src, dst, extra=('-c:a', 'pcm_s16le'), check_encoded=True):
    """Bring src's audio to LUFS (+/- LUFS_TOL) with the true peak at or under TP, measured as delivered (after the AAC encode
    for a WAV dst). Each round: one linear gain plus an oversampled true-peak limiter (4x, 176.4 kHz), then measure the result
    and correct both: the gain by the loudness error, the limiter by any true-peak overshoot + 0.5 dB. Up to TRIES rounds;
    a file that still misses stops the run (SystemExit with a LOUDNESS GUARD FAILED line), so a file that is off is never kept.
    (The old version used loudnorm's linear mode, which silently turns dynamic when the peaks forbid the gain and could land
    1 dB low (Episode 11: -17.0 LUFS), and its retries checked only the peak, giving up at -0.5 dBTP (Episode 4).)
    Returns (before, after) LUFS."""
    i0, tp0 = ebur(src)
    gain, lim = LUFS - i0, TP - 1.0          # dB; the limiter starts 1 dB under the ceiling for the AAC encode's overshoot
    for k in range(TRIES):
        af = (f'volume={gain:.3f}dB,lowpass=f=16000:poles=2,aresample=176400:resampler=soxr,'          # 16 kHz: the AAC encode drops it anyway, and
              f'alimiter=limit={10 ** (lim / 20):.5f}:attack=0.5:release=60:level=false:latency=true,aresample={SR}:resampler=soxr')   # full-band hits overshoot after it
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-af', af] + list(extra) + [dst], check=True)
        i, _ = ebur(dst); _, tp = ebur(dst, encode=check_encoded and dst.lower().endswith('.wav'))
        print(f'loudness round {k + 1}: gain {gain:+.2f} dB, limiter {lim:.2f} dBTP -> {i:.2f} LUFS, true peak {tp:.2f} dBTP', flush=True)
        if abs(i - LUFS) <= LUFS_TOL and tp <= TP and (abs(i - LUFS) <= 0.2 or k == TRIES - 1): return i0, i
        gain += LUFS - i                                                               # loudness error (limiting the peaks costs a little level)
        if tp > TP: lim -= (tp - TP) + 0.5                                             # peak leaked through the encode: lower the ceiling with room
    if abs(i - LUFS) <= LUFS_TOL and tp <= TP: return i0, i
    raise SystemExit(f'LOUDNESS GUARD FAILED: {dst}: {i:.2f} LUFS (target {LUFS} +/- {LUFS_TOL}), true peak {tp:.2f} dBTP (ceiling {TP}) '
                     f'after {TRIES} rounds; input was {i0:.2f} LUFS / {tp0:.2f} dBTP. Do not publish this file.')


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
