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


def make(voice_path, cuts, hits, out_path):
    tmp = tempfile.mktemp(suffix='.wav'); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', voice_path, '-ac', '1', '-ar', str(SR), tmp], check=True)
    v, _ = sf.read(tmp, dtype='float32'); os.remove(tmp); dur = len(v) / SR + 0.8
    v = np.pad(v, (0, int(dur * SR) - len(v))); mu = music(dur)[:len(v)]; fx = sfx(dur, cuts, hits)[:len(v)]
    rv = gated_rms(v); mu *= 0.5 * rv / gated_rms(mu); fx *= 0.5 * rv / gated_rms(fx)
    pk = 0.7 * np.abs(v).max(); fx = np.clip(fx, -pk, pk)
    mix = v + mu + fx; mix *= 0.89 / np.abs(mix).max()
    sf.write(out_path, mix, SR)
    db = lambda a: 20 * np.log10(a)
    return {'voice_rms_db': round(db(rv), 1), 'music_vs_voice_db': round(db(gated_rms(mu) / rv), 1), 'sfx_vs_voice_db': round(db(gated_rms(fx) / rv), 1), 'duration': round(dur, 2)}
