#!/usr/bin/env python3
"""Sound design for an animated short: ambience beds, foley, spot effects, simple instruments, whispers and walla, all
SYNTHESISED HERE in numpy/scipy (no samples, nothing downloaded, nothing copyrighted), laid on the timeline by a per-episode
sound plan and mixed under the voice. See SOUND.md for why the layers and levels are what they are.

THE PLAN: videos/<slug>/sound.json, keyed by ORIGINAL sentence number (the same numbers as shots_fx.json):
  {"<line>": {"amb": "rain_heavy" | ["crowd", "wind:-6"],          ambience bed(s); "name:-6" = that bed 6 dB lower; "none" = no bed
              "music": "none|guitar|flute|gongs|band|drone|heartbeat",
              "level": -3,                                          optional dB offset for this line's beds and music
              "foley": [{"what": "steps_earth", "at": 0.4, "pace": "walk|run|sneak", "count": 6, "gain": -3}],
              "spot":  [{"what": "thunder", "at": 0.0, "hush": 0.4}]}, ...,
   "_": {"whoosh_cuts": true}}                                      optional: a soft whoosh on every shot cut
  "at" is seconds from the start of the line (a riser's "at" is where it PEAKS, so it starts before). "hush": the beds dip
  for that many seconds just before the hit (silence before a hit). "dur" sets the length where a sound has one.
  A line without an entry keeps the bed (amb, music, level) of the line before; an entry that leaves out amb, music or
  level keeps the previous value too. foley and spot belong only to the line that lists them.
mix(episode_dir, timings, voice, out) lays the plan, ducks it under the voice and hands it to soundtrack.loudnorm2.
An episode WITHOUT sound.json goes to soundtrack.make exactly as before (soundtrack_for() decides).
usage:  sound_design.py --report [dir]     level and spectrum centroid of every generator (and a WAV of each in dir)"""
import json, os, subprocess, sys, tempfile
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, lfilter, fftconvolve
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import soundtrack

SR = soundtrack.SR
NYQ = SR / 2 - 200


# ---------------------------------------------------------------- building blocks
def _n(sec): return max(1, int(round(sec * SR)))
def _t(n): return np.arange(n) / SR
def _rng(seed): return np.random.default_rng(seed)


def _f(x, kind, f, order=2):
    """Butterworth filter: kind 'low'|'high'|'band' (f = (lo, hi) for band)."""
    f = (max(20.0, min(NYQ, f[0])), max(30.0, min(NYQ, f[1]))) if kind == 'band' else max(20.0, min(NYQ, f))
    return sosfilt(butter(order, f, btype=kind, fs=SR, output='sos'), x)


def _pink(n, rng):
    return lfilter([0.049922035, -0.095993537, 0.050612699, -0.004408786], [1, -2.494956002, 2.017265875, -0.522189400], rng.normal(0, 1, n)) * 8


def _brown(n, rng):
    y = lfilter([1.0], [1, -0.997], rng.normal(0, 1, n)); y = _f(y, 'high', 25); return y / (np.std(y) + 1e-9)


def _smooth_rand(n, rate, rng, lo=0.0, hi=1.0):
    """A slowly wandering control signal in [lo, hi] (about `rate` changes per second)."""
    k = max(2, int(n / SR * rate) + 3); pts = rng.random(k)
    y = np.interp(np.linspace(0, k - 1, n), np.arange(k), pts)
    y = np.interp(y, [0, 1], [lo, hi]); return y


def _dec(n, tau, att=0.002):
    t = _t(n); return np.minimum(1.0, t / max(att, 1e-4)) * np.exp(-t / tau)


def _add(out, sig, t0):
    i = int(round(t0 * SR)); j0 = max(0, -i); i = max(0, i)
    m = min(len(sig) - j0, len(out) - i)
    if m > 0: out[i:i + m] += sig[j0:j0 + m]


def _impulses(n, rate, rng, amp_sd=0.6):
    """A sparse train of random-height impulses (rate per second, may be an array over time)."""
    rate = np.broadcast_to(np.asarray(rate, float), (n,))
    hit = rng.random(n) < rate / SR; x = np.zeros(n); k = hit.sum()
    x[hit] = np.exp(rng.normal(0, amp_sd, k)) * rng.choice([-1, 1], k); return x


def _rms_db(x):
    return float(20 * np.log10(np.sqrt(np.mean(np.square(x))) + 1e-12))


def _active_rms(x, win=0.05):
    """RMS over the windows where the sound is actually sounding (within 20 dB of its loudest window)."""
    w = max(1, int(win * SR)); m = len(x) // w
    if m < 1: return float(np.sqrt(np.mean(x ** 2)) + 1e-12)
    r = np.sqrt(np.mean(x[:m * w].reshape(m, w) ** 2, axis=1)); r = r[r > r.max() * 0.1]
    return float(np.sqrt(np.mean(r ** 2)) + 1e-12)


def _out(x, rms_db=-24.0):
    """float32, finite, scaled so its sounding part sits at rms_db dBFS."""
    x = np.nan_to_num(np.asarray(x, np.float64)); a = _active_rms(x)
    return (x * (10 ** (rms_db / 20) / a)).astype(np.float32) if a > 1e-9 else x.astype(np.float32)


def _sweep(x, f0, f1, q=2.0, blk=256):
    """Band-pass whose centre glides from f0 to f1 (arrays allowed): block-wise biquad with carried state."""
    n = len(x); fc = np.interp(np.arange(0, n, blk), [0, n], [f0, f1]) if np.isscalar(f0) else np.asarray(f0)[::blk]
    y = np.empty(n); zi = np.zeros(2)
    for k, c in enumerate(fc):
        w = 2 * np.pi * min(c, NYQ) / SR; al = np.sin(w) / (2 * q)
        b = np.array([al, 0, -al]); a = np.array([1 + al, -2 * np.cos(w), 1 - al])
        s = slice(k * blk, min(n, (k + 1) * blk)); y[s], zi = lfilter(b / a[0], a / a[0], x[s], zi=zi)
    return y


VOWELS = {'a': (800, 1200, 2500), 'e': (500, 1800, 2550), 'i': (320, 2250, 3000), 'o': (520, 900, 2450), 'u': (360, 800, 2300)}


def _formant(x, fs, bw=(90, 110, 160)):
    return sum(_f(x, 'band', (f - b, f + b)) * g for f, b, g in zip(fs, bw, (1.0, 0.6, 0.3)))


def _syllables(n, rng, rate=5.0, phrase=(4, 9), gap=(0.2, 0.6), vowels='aeiou'):
    """Speech-like timing with no words: per vowel a weight track (0..1) and an onset list (sample, kind)."""
    W = {v: np.zeros(n) for v in vowels}; onsets = []; i = int(rng.uniform(0, 0.3) * SR)
    while i < n:
        for _ in range(rng.integers(*phrase)):
            L = int(rng.uniform(0.7, 1.4) / rate * SR); v = vowels[rng.integers(len(vowels))]
            e = np.sin(np.pi * np.linspace(0, 1, L)) ** 0.6 * rng.uniform(0.6, 1.0)
            m = min(L, n - i)
            if m <= 0: break
            W[v][i:i + m] += e[:m]; onsets.append((i, rng.choice(['s', 'sh', 't', 'k', 'h', 'p', '-', '-'])))
            i += L
        i += int(rng.uniform(*gap) * SR)
    return W, onsets


def _consonants(n, onsets, rng, level=0.5):
    out = np.zeros(n)
    for i, c in onsets:
        if c == '-': continue
        L = {'s': 0.07, 'sh': 0.08, 'h': 0.05}.get(c, 0.018); m = _n(L); z = rng.normal(0, 1, m)
        band = {'s': ('high', 4500), 'sh': ('band', (1800, 4200)), 'h': ('band', (500, 2500)), 't': ('high', 3000),
                'k': ('band', (1200, 3000)), 'p': ('low', 1200)}[c]
        z = _f(z, *band) * np.sin(np.pi * np.linspace(0, 1, m)) * level * (1.6 if c in ('t', 'k', 'p') else 1.0)
        _add(out, z, (i - m * 0.6) / SR)
    return out


# ---------------------------------------------------------------- (a) ambience beds: f(dur, seed) -> mono float32
def night_insects(dur, seed=1):
    rng = _rng(seed); n = _n(dur); t = _t(n)
    out = _f(_pink(n, rng), 'low', 1500) * 0.08                                           # night air
    for k in range(7):                                                                    # crickets: chirps of 3-4 pulses
        fc = rng.uniform(3900, 5400); rate = rng.uniform(1.4, 3.2); ph = rng.random()
        pulses = (np.sin(2 * np.pi * rng.uniform(26, 34) * t) > 0.2).astype(float)
        chirp = (((t * rate + ph) % 1.0) < rng.uniform(0.08, 0.14)).astype(float)
        g = _f(pulses * chirp, 'low', 250) * _smooth_rand(n, 0.2, rng, 0.2, 1.0) * rng.uniform(0.25, 1.0) / (1 + k * 0.3)
        out += np.sin(2 * np.pi * fc * t + 0.3 * np.sin(2 * np.pi * 2 * fc * t)) * g * 0.35
    out += _f(rng.normal(0, 1, n), 'band', (6500, 8500)) * (0.5 + 0.5 * np.sin(2 * np.pi * 48 * t)) ** 4 * 0.06   # a katydid buzz
    return _out(out)


def _rain(dur, seed, rate, hiss, rumble):
    rng = _rng(seed); n = _n(dur)
    out = _f(_pink(n, rng), 'band', (1200, 9000)) * hiss * _smooth_rand(n, 0.3, rng, 0.8, 1.0)
    out += _f(_brown(n, rng), 'low', 350) * rumble
    for k, fc in enumerate((1800, 2600, 3600, 5200)):                                    # drops on leaves, ground and roofs
        m = _n(0.025); z = _f(rng.normal(0, 1, m), 'band', (fc * 0.7, fc * 1.4)) * _dec(m, 0.004, 0.0003)
        out += fftconvolve(_impulses(n, rate / 4, rng), z)[:n] * 0.35
    return _out(out)


def rain_light(dur, seed=2): return _rain(dur, seed, 120, 0.5, 0.05)
def rain_heavy(dur, seed=3): return _rain(dur, seed, 900, 1.0, 0.35)


def wind(dur, seed=4):
    rng = _rng(seed); n = _n(dur); g = _smooth_rand(n, 0.25, rng, 0.25, 1.0) ** 1.5
    b = _brown(n, rng); w = _f(b, 'low', 500) * g + _f(rng.normal(0, 1, n), 'band', (700, 1400)) * 0.15 * g ** 2
    w += _sweep(rng.normal(0, 1, n), 600 + 500 * g, None, q=14) * 0.12 * g ** 3            # whistle in the gusts
    return _out(w)


def sea(dur, seed=5):
    rng = _rng(seed); n = _n(dur); env = np.zeros(n); t0 = -rng.uniform(0, 4)
    while t0 < dur:                                                                       # one wave every 6-9 s: rise, crash, wash back
        m = _n(7.0); tt = _t(m); e = np.where(tt < 2.4, (tt / 2.4) ** 2, np.exp(-(tt - 2.4) / 1.6)) * rng.uniform(0.6, 1.0)
        _add(env, e, t0); t0 += rng.uniform(6, 9)
    p = _pink(n, rng)
    out = _f(p, 'low', 600) * env + _f(p, 'band', (1500, 7000)) * np.roll(env, _n(0.4)) ** 2 * 0.5 + _f(_brown(n, rng), 'low', 180) * 0.4
    return _out(out)


def forest(dur, seed=6):
    rng = _rng(seed); n = _n(dur)
    out = wind(dur, seed + 10).astype(float) * 0.35 + _f(rng.normal(0, 1, n), 'band', (2000, 6000)) * _smooth_rand(n, 0.5, rng, 0, 1) ** 3 * 0.02
    out += night_insects(dur, seed + 11).astype(float) * 0.15
    t0 = rng.uniform(0.3, 1.5)
    while t0 < dur:                                                                       # birds: short phrases of FM chirps
        f = rng.uniform(2200, 4200)
        for j in range(rng.integers(2, 6)):
            m = _n(rng.uniform(0.05, 0.12)); tt = _t(m); fs = f * (1 + rng.uniform(-0.3, 0.3) * tt / tt[-1])
            c = np.sin(2 * np.pi * np.cumsum(fs) / SR + 2 * np.sin(2 * np.pi * 40 * tt)) * np.sin(np.pi * tt / tt[-1]) * 0.012 * rng.uniform(0.3, 1)
            _add(out, c, t0 + j * rng.uniform(0.09, 0.16))
        t0 += rng.uniform(1.0, 4.0)
    return _out(out)


def city(dur, seed=7):
    rng = _rng(seed); n = _n(dur); t = _t(n)
    out = _f(_brown(n, rng), 'low', 160) * 0.8 + _f(_pink(n, rng), 'band', (300, 2500)) * 0.15            # far traffic
    t0 = rng.uniform(0, 3)
    while t0 < dur:                                                                       # cars and jeepneys passing
        m = _n(rng.uniform(3, 6)); tt = np.linspace(-1, 1, m)
        car = _f(_brown(m, rng), 'band', (90, 900)) * np.exp(-tt ** 2 * 5) * rng.uniform(0.4, 1.2)
        _add(out, car, t0); t0 += rng.uniform(1.5, 5)
    t0 = rng.uniform(3, 9)
    while t0 < dur:                                                                       # a far horn now and then
        m = _n(rng.uniform(0.15, 0.4)); tt = _t(m); f = rng.choice([370, 415, 466])
        h = np.sign(np.sin(2 * np.pi * f * tt)) + np.sign(np.sin(2 * np.pi * f * 1.26 * tt))
        _add(out, _f(h, 'low', 1800) * np.minimum(1, tt / 0.01) * np.minimum(1, (tt[-1] - tt) / 0.03) * 0.06, t0); t0 += rng.uniform(6, 15)
    out += walla(dur, voices=10, seed=seed + 5, far=True).astype(float) * 0.004
    return _out(out)


def crowd(dur, seed=8):
    """Hundreds of people at a distance: far walla, low and wide, with a slow swell."""
    w = walla(dur, voices=48, seed=seed, far=True).astype(float); rng = _rng(seed + 1)
    return _out(w * _smooth_rand(len(w), 0.15, rng, 0.7, 1.0) + _f(_brown(len(w), rng), 'low', 200) * 0.002)


def fire(dur, seed=9):
    rng = _rng(seed); n = _n(dur)
    out = _f(_brown(n, rng), 'low', 500) * _smooth_rand(n, 1.5, rng, 0.5, 1.0) * 0.5           # the roar
    for fc, rate, g in ((2500, 6, 0.5), (4000, 12, 0.35), (900, 0.8, 1.0)):                  # crackles and pops
        m = _n(0.012); z = _f(rng.normal(0, 1, m), 'band', (fc * 0.5, fc * 1.6)) * _dec(m, 0.002, 0.0002)
        out += fftconvolve(_impulses(n, rate, rng, 0.8), z)[:n] * g
    return _out(out)


def indoor(dur, seed=10):
    rng = _rng(seed); n = _n(dur); t = _t(n)
    out = _f(_pink(n, rng), 'low', 400) * 0.5 + _f(rng.normal(0, 1, n), 'high', 3000) * 0.004
    out += (np.sin(2 * np.pi * 60 * t) * 0.02 + np.sin(2 * np.pi * 120 * t) * 0.012)        # 60 Hz mains hum (the Philippines)
    return _out(out)


def office(dur, seed=11):
    rng = _rng(seed); n = _n(dur); t = _t(n)
    out = indoor(dur, seed).astype(float) + _out(_f(_pink(n, rng), 'band', (150, 1400)), -26).astype(float)   # air-con
    out += np.sin(2 * np.pi * 120 * t) * 0.0015
    m = _n(0.01); click = _f(rng.normal(0, 1, m), 'band', (2000, 6000)) * _dec(m, 0.002, 0.0002)
    keys = _impulses(n, 7 * (_smooth_rand(n, 0.3, rng) > 0.55), rng, 0.3)                  # a keyboard in the next desk
    return _out(out + fftconvolve(keys, click)[:n] * 0.004)


AMBIENCES = {k: globals()[k] for k in ('night_insects', 'rain_light', 'rain_heavy', 'wind', 'sea', 'forest', 'city', 'crowd', 'fire', 'indoor', 'office')}


# ---------------------------------------------------------------- (b) foley
PACE = {'walk': (0.52, 1.0, 0.055), 'run': (0.31, 1.3, 0.0), 'sneak': (0.9, 0.45, 0.09)}     # step interval s, strength, heel-to-toe s


def _step(surface, s, rng):
    m = _n(0.35); z = rng.normal(0, 1, m); tt = _t(m); f0 = rng.uniform(60, 95)
    thud = np.sin(2 * np.pi * f0 * tt) * _dec(m, 0.022, 0.001)
    if surface == 'earth':
        y = thud * 0.7 + _f(z, 'low', 900) * _dec(m, 0.035, 0.002) * 0.8 + _f(z, 'band', (2000, 5000)) * _dec(m, 0.012) * 0.15
    elif surface == 'grass':
        grain = _f(z, 'band', (1800, 6000)) * _f((rng.random(m) < 0.004) * 1.0, 'low', 300) * 40
        y = thud * 0.35 + _f(z, 'low', 700) * _dec(m, 0.03) * 0.4 + grain * _dec(m, 0.11, 0.01)
    elif surface == 'stone':
        y = thud * 0.25 + _f(z, 'band', (1500, 5500)) * _dec(m, 0.008, 0.0004) * 1.4 + np.sin(2 * np.pi * rng.uniform(1700, 2300) * tt) * _dec(m, 0.015, 0.0005) * 0.25
        y += _f(z, 'band', (800, 4000)) * _dec(m, 0.05, 0.02) * 0.12                              # scuff of the sole
    elif surface == 'wood':
        y = sum(np.sin(2 * np.pi * f * tt) * _dec(m, d, 0.001) * a for f, d, a in ((rng.uniform(100, 130), 0.07, 0.9), (rng.uniform(230, 260), 0.05, 0.5), (rng.uniform(450, 520), 0.03, 0.3)))
        y += _f(z, 'band', (600, 3000)) * _dec(m, 0.01) * 0.3
    elif surface == 'wet':
        grain = _f(z, 'band', (900, 4500)) * _f((rng.random(m) < 0.003) * 1.0, 'low', 250) * 45
        y = thud * 0.4 + grain * _dec(m, 0.09, 0.006) + _f(z, 'band', (300, 900)) * _dec(m, 0.05, 0.004) * 0.6
    else: raise ValueError(f'unknown surface {surface!r} (earth, grass, stone, wood, wet)')
    return y * s * rng.uniform(0.75, 1.1)


def footsteps(surface='earth', pace='walk', count=6, seed=12):
    """count steps on surface at a walking, running or sneaking pace."""
    rng = _rng(seed); iv, s, toe = PACE[pace]; out = np.zeros(_n(iv * count + 0.5))
    for k in range(int(count)):
        t0 = k * iv * rng.uniform(0.93, 1.07)
        st = _step(surface, s, rng)
        if pace == 'sneak': st = st * np.minimum(1, _t(len(st)) / 0.02)                      # rolled softly onto the foot
        _add(out, st, t0)
        if toe: _add(out, _step(surface, s * 0.45, rng), t0 + toe * rng.uniform(0.8, 1.2))
    return _out(out)


def cloth(dur=0.7, seed=13):
    rng = _rng(seed); n = _n(dur); env = np.zeros(n)
    for _ in range(rng.integers(3, 6)):
        m = _n(rng.uniform(0.08, 0.3)); _add(env, np.sin(np.pi * np.linspace(0, 1, m)) * rng.uniform(0.4, 1), rng.uniform(0, max(0.01, dur - 0.2)))
    grain = _f(rng.normal(0, 1, n), 'low', 60) ** 2
    return _out(_f(rng.normal(0, 1, n), 'band', (1200, 6500)) * env * (0.4 + grain))


def paper_tear(dur=0.9, seed=14, sheets=1):
    """One sheet torn (sheets > 1: many people tearing at once, each a little apart)."""
    rng = _rng(seed); n = _n(dur + 0.4 * (sheets > 1)); out = np.zeros(n)
    m = _n(0.004); click = _f(rng.normal(0, 1, m), 'band', (1500, 8000)) * _dec(m, 0.0008, 0.0001)
    for k in range(sheets):
        L = _n(dur * rng.uniform(0.7, 1.0)); r = np.linspace(250, 1600, L) * rng.uniform(0.7, 1.3)
        fib = _f(rng.normal(0, 1, L), 'band', (2000, 5500)) * np.linspace(0.3, 1, L) * 0.08
        x = (fftconvolve(_impulses(L, r, rng, 0.9), click)[:L] + fib) * np.minimum(1, np.linspace(0, 12, L)) * np.minimum(1, np.linspace(6, 0, L))
        _add(out, x * (1.0 if sheets == 1 else rng.uniform(0.3, 1.0)), 0 if sheets == 1 else rng.uniform(0, 0.4))
    return _out(out)


def paper_tear_many(dur=1.1, seed=15): return paper_tear(dur, seed, sheets=40)


def door(seed=16):
    """A wooden door: creak (stick-slip friction), then the slam and the latch."""
    rng = _rng(seed); m = _n(0.9); tt = _t(m)
    rate = 45 + 40 * np.sin(np.pi * tt / tt[-1]) + 8 * _smooth_rand(m, 8, rng)
    ph = np.cumsum(rate) / SR; pulses = np.diff(np.floor(ph), prepend=0) * np.exp(rng.normal(0, 0.3, m))
    creak = sum(_f(pulses, 'band', (f * 0.92, f * 1.08)) * g for f, g in ((620, 1.0), (1240, 0.6), (2150, 0.35))) * np.sin(np.pi * tt / tt[-1]) ** 0.5
    s = _n(0.5); st = _t(s); z = rng.normal(0, 1, s)
    slam = np.sin(2 * np.pi * 85 * st) * _dec(s, 0.06) + _f(z, 'low', 700) * _dec(s, 0.05) * 0.8 + _f(z, 'band', (2500, 6000)) * _dec(s, 0.004) * 0.4
    out = np.zeros(_n(1.6)); _add(out, creak * 4, 0); _add(out, slam * 1.4, 0.95)
    _add(out, _f(rng.normal(0, 1, _n(0.02)), 'band', (2500, 7000)) * _dec(_n(0.02), 0.003) * 0.6, 1.05)       # latch click
    return _out(out)


def dog_paws(count=12, seed=17):
    """A dog trotting: four soft pad taps per stride, each with a nail click."""
    rng = _rng(seed); stride = 0.42; out = np.zeros(_n(stride * count / 4 + 0.4)); m = _n(0.06)
    for k in range(int(count)):
        t0 = (k // 4) * stride + (k % 4) * stride / 4 * rng.uniform(0.8, 1.2); z = rng.normal(0, 1, m)
        tap = _f(z, 'low', 600) * _dec(m, 0.012) * 0.8 + _f(z, 'band', (3000, 7000)) * _dec(m, 0.0015, 0.0002) * 0.5
        _add(out, tap * rng.uniform(0.6, 1.0), t0)
    return _out(out)


def dog_pant(dur=2.0, seed=18):
    rng = _rng(seed); n = _n(dur); t = _t(n); rate = 3.3
    ph = (t * rate) % 1.0; out_b = np.sin(np.pi * np.clip(ph / 0.45, 0, 1)) ** 2; in_b = np.sin(np.pi * np.clip((ph - 0.5) / 0.4, 0, 1)) ** 2
    z = rng.normal(0, 1, n); f0 = 290 * (1 + 0.05 * np.sin(2 * np.pi * 0.7 * t))
    voiced = _f(((np.cumsum(f0) / SR) % 1.0) - 0.5, 'low', 1500) * 0.15
    out = _formant(z, (650, 1500, 2600)) * out_b + _formant(z, (450, 1800, 3000)) * in_b * 0.5 + voiced * out_b
    return _out(out * np.minimum(1, t / 0.1) * np.minimum(1, (dur - t) / 0.15))


def growl(dur=1.8, seed=19):
    rng = _rng(seed); n = _n(dur); t = _t(n)
    f0 = 82 * (1 + 0.08 * _smooth_rand(n, 6, rng, -1, 1)); saw = ((np.cumsum(f0) / SR) % 1.0) - 0.5
    rough = (0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(28 + 6 * _smooth_rand(n, 4, rng)) / SR)) ** 2         # the rattle of a growl
    src = saw * rough + rng.normal(0, 1, n) * 0.08 * rough
    env = np.minimum(1, t / 0.45) * np.minimum(1, (dur - t) / 0.35) * (0.8 + 0.2 * _smooth_rand(n, 3, rng))
    y = (_f(src, 'band', (250, 700)) + _f(src, 'band', (850, 1500)) * 0.5 + _f(src, 'low', 200) * 0.6) * env
    return _out(y)


# ---------------------------------------------------------------- (c) spot effects
def cannon(seed=20):
    rng = _rng(seed); m = _n(4.0); tt = _t(m); z = rng.normal(0, 1, m)
    boom = np.sin(2 * np.pi * np.cumsum(42 + 60 * np.exp(-tt * 18)) / SR) * _dec(m, 0.45, 0.002)
    y = boom + _f(z, 'low', 450) * _dec(m, 0.35, 0.002) * 0.8 + _f(z, 'high', 1500) * _dec(m, 0.01, 0.0003) * 0.9
    y += _f(_brown(m, rng), 'low', 180) * _dec(m, 1.4, 0.2) * 0.5                              # the roll over the field
    return _out(y)


def thunder(dur=4.5, seed=21):
    rng = _rng(seed); m = _n(dur); tt = _t(m); env = np.zeros(m)
    for _ in range(6): k = _n(rng.uniform(0.4, 1.4)); _add(env, np.sin(np.pi * np.linspace(0, 1, k)) * rng.uniform(0.3, 1), rng.uniform(0.05, dur * 0.6))
    env *= np.exp(-tt / (dur * 0.45))
    crack = _f(rng.normal(0, 1, m), 'high', 900) * _dec(m, 0.12, 0.003) * (0.5 + (rng.random(m) < 0.1) * 2)
    return _out(_f(_brown(m, rng), 'low', 260) * env * 1.4 + crack * 0.6)


def bell(seed=22, f=330.0):
    """A church bell: hum, prime, minor third, fifth, nominal ... (inharmonic partials), long decay."""
    rng = _rng(seed); m = _n(5.0); tt = _t(m); y = np.zeros(m)
    for r, a, d in ((0.5, 0.6, 3.5), (1.0, 0.8, 2.5), (1.19, 0.5, 2.0), (1.5, 0.35, 1.6), (2.0, 0.6, 1.4), (2.52, 0.25, 1.0), (2.66, 0.2, 0.9), (3.01, 0.18, 0.7), (4.0, 0.12, 0.5)):
        y += np.sin(2 * np.pi * f * r * tt * (1 + rng.normal(0, 0.0005)) + rng.random() * 6) * a * _dec(m, d, 0.001)
    y += _f(rng.normal(0, 1, m), 'band', (1500, 6000)) * _dec(m, 0.01) * 0.3
    return _out(y)


def splash(seed=23):
    rng = _rng(seed); m = _n(1.2); z = rng.normal(0, 1, m)
    y = _f(z, 'band', (300, 3000)) * _dec(m, 0.12, 0.004) + _f(z, 'band', (1500, 5000)) * _f((rng.random(m) < 0.002) * 1.0, 'low', 200) * _dec(m, 0.35, 0.05) * 60
    return _out(y)


def gong(seed=24, f=98.0):
    """A large hanging boss gong (agung-like): strong fundamental with a slow beat, a soft padded beater."""
    rng = _rng(seed); m = _n(4.5); tt = _t(m)
    fs = f * (1 + 0.012 * np.exp(-tt * 3))                                                    # the pitch settles after the hit
    y = (np.sin(2 * np.pi * np.cumsum(fs) / SR) + np.sin(2 * np.pi * np.cumsum(fs * 1.006) / SR)) * _dec(m, 2.2, 0.004) * 0.5
    y += np.sin(2 * np.pi * f * 2.02 * tt) * _dec(m, 0.9, 0.004) * 0.3 + np.sin(2 * np.pi * f * 3.3 * tt) * _dec(m, 0.25, 0.003) * 0.12
    y += _f(rng.normal(0, 1, m), 'low', 300) * _dec(m, 0.02) * 0.4
    return _out(y)


def impact(seed=25):
    rng = _rng(seed); m = _n(1.4); tt = _t(m); z = rng.normal(0, 1, m)
    sub = np.sin(2 * np.pi * np.cumsum(40 + 90 * np.exp(-tt * 14)) / SR) * _dec(m, 0.35, 0.001)
    y = sub + _f(z, 'band', (180, 900)) * _dec(m, 0.08, 0.001) * 0.7 + _f(z, 'high', 2000) * _dec(m, 0.015, 0.0003) * 0.6
    return _out(y)


def whoosh(dur=0.6, seed=26):
    rng = _rng(seed); n = _n(dur); k = np.linspace(0, 1, n)
    fc = 300 + 2700 * np.sin(np.pi * k) ** 2
    return _out(_sweep(rng.normal(0, 1, n), fc, None, q=1.4) * np.sin(np.pi * k) ** 2)


def riser(dur=2.0, seed=27):
    """Builds to its end: noise sweeping up and a rising tone, loudest at the last sample (placed so it PEAKS at "at")."""
    rng = _rng(seed); n = _n(dur); k = np.linspace(0, 1, n)
    nz = _sweep(rng.normal(0, 1, n), 250 * 24 ** k, None, q=1.0)
    f0 = 110 * 4 ** k; tone = sum(np.sin(2 * np.pi * np.cumsum(f0 * h) / SR) / h for h in (1, 2, 3, 1.5))
    return _out((nz + tone * 0.2) * k ** 2.2 * np.minimum(1, (1 - k) * n / _n(0.02) + 0.0))


def shimmer(dur=2.5, seed=28):
    """Magic: a cloud of small bright bell grains and a soft high wash (the medallion)."""
    rng = _rng(seed); n = _n(dur); out = np.zeros(n); scale = [0, 2, 4, 7, 9]
    for _ in range(int(dur * 14)):
        f = 1046.5 * 2 ** ((scale[rng.integers(5)] + 12 * rng.integers(0, 3)) / 12); m = _n(rng.uniform(0.25, 0.8)); tt = _t(m)
        g = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt * 8)) * _dec(m, 0.18, 0.002) * rng.uniform(0.2, 1)
        _add(out, g, rng.uniform(0, dur * 0.85) * rng.uniform(0.4, 1.0) ** 0.5)
    k = np.linspace(0, 1, n); wash = _f(rng.normal(0, 1, n), 'band', (5000, 12000)) * np.sin(np.pi * k) * 0.08
    return _out((out + wash) * np.minimum(1, k / 0.15) * np.minimum(1, (1 - k) / 0.25))


def drone(dur=6.0, seed=29):
    """Dread: low beating sines and a dark filtered noise that swells slowly."""
    rng = _rng(seed); n = _n(dur); t = _t(n)
    y = sum(np.sin(2 * np.pi * f * t + rng.random() * 6) * a for f, a in ((55, 1), (55.35, 0.8), (82.6, 0.5), (110.4, 0.3), (116.5, 0.12)))
    y += _f(_brown(n, rng), 'band', (60, 400)) * 0.25 * _smooth_rand(n, 0.2, rng, 0.4, 1)
    return _out(y * (0.75 + 0.25 * np.sin(2 * np.pi * 0.11 * t)))


def cheer(dur=2.8, seed=30):
    """A crowd's shout and cheer swelling up and dying away (walla pitched up, open vowels, long syllables)."""
    w = walla(dur, voices=60, seed=seed, f0=(170, 330), vowels='aao', rate=2.2).astype(float)
    k = np.linspace(0, 1, len(w)); env = np.minimum(1, k / 0.18) * np.exp(-np.maximum(0, k - 0.45) * 3.5)
    return _out(w * env + _f(_pink(len(w), _rng(seed)), 'band', (500, 4000)) * env * 0.08)


# ---------------------------------------------------------------- (d) instruments: f(dur, seed) -> a loopable music bed
def _pluck(f, sec, rng, t60=1.6, bright=0.6):
    """Karplus-Strong plucked string, computed a period at a time."""
    N = max(2, int(round(SR / f))); g = 10 ** (-3 / (t60 * f))
    buf = _f(rng.normal(0, 1, N * 6), 'low', min(5000.0, f * (4 + 10 * bright)))[-N:]; buf /= np.abs(buf).max() + 1e-9      # the pluck: a soft finger, not a pick
    P = int(sec * SR / N) + 1; out = np.empty(P * N)
    for k in range(P): out[k * N:(k + 1) * N] = buf; buf = g * 0.5 * (buf + np.roll(buf, 1))
    return out[:_n(sec)]


def guitar(dur, seed=31, bpm=84):
    """Fingerpicked guitar in 3/4, in A minor (bass on 1, chord tones on 2 and 3): the kundiman accompaniment feel."""
    rng = _rng(seed); n = _n(dur); out = np.zeros(n); beat = 60 / bpm
    prog = [(110.0, (220.0, 261.6, 329.6)), (146.8, (220.0, 293.7, 349.2)), (82.4, (207.7, 246.9, 293.7)), (110.0, (220.0, 261.6, 329.6)),
            (130.8, (261.6, 329.6, 392.0)), (98.0, (246.9, 293.7, 392.0)), (82.4, (207.7, 246.9, 329.6)), (110.0, (220.0, 261.6, 329.6))]
    b = 0
    while b * beat < dur:
        bar = (b // 3) % len(prog); bass, ch = prog[bar]; t0 = b * beat + rng.normal(0, 0.008)
        if b % 3 == 0: _add(out, _pluck(bass, 2.2, rng, 2.0, 0.5) * 0.9, t0)
        else:
            for j, f in enumerate(ch if b % 3 == 1 else ch[1:]): _add(out, _pluck(f, 1.6, rng, 1.4, 0.7) * 0.45, t0 + j * 0.012)
        if b % 3 == 2 and rng.random() < 0.5: _add(out, _pluck(ch[-1] * 2, 1.0, rng, 1.0, 0.75) * 0.3, t0 + beat / 2)
        b += 1
    out = out + _f(out, 'band', (90, 260)) * 0.4                                               # the wooden body
    return _out(out)


def flute(dur, seed=32):
    """A breathy bamboo transverse flute: short phrases in a minor pentatonic, vibrato, breath noise and a chiff on each note."""
    rng = _rng(seed); n = _n(dur); out = np.zeros(n); scale = [0, 3, 5, 7, 10, 12, 15]; t0 = 0.3
    while t0 < dur:
        notes = [scale[rng.integers(2, 7)] for _ in range(rng.integers(3, 7))]; notes[-1] = rng.choice([0, 7, 12])
        for st in notes:
            L = rng.choice([0.4, 0.6, 0.9, 1.3]); m = _n(L); tt = _t(m); f = 587.3 * 2 ** (st / 12)
            vib = 1 + 0.006 * np.sin(2 * np.pi * 5.2 * tt) * np.minimum(1, tt / 0.35)
            ph = 2 * np.pi * np.cumsum(f * vib) / SR; env = np.minimum(1, tt / 0.06) * np.minimum(1, (L - tt) / 0.12) ** 1.5
            tone = np.sin(ph) + 0.22 * np.sin(2 * ph) + 0.06 * np.sin(3 * ph)
            br = _f(rng.normal(0, 1, m), 'band', (f * 0.9, f * 2.6)) * 0.35 + _f(rng.normal(0, 1, m), 'band', (2000, 6000)) * _dec(m, 0.04, 0.005) * 0.5
            _add(out, (tone * env + br * env) * 0.5, t0); t0 += L
            if t0 >= dur: break
        t0 += rng.uniform(1.2, 2.5)
    return _out(out)


def _gongtone(f, sec, rng, knob=True):
    m = _n(sec); tt = _t(m)
    y = np.sin(2 * np.pi * f * tt) * _dec(m, 0.9 if knob else 2.0, 0.002) + np.sin(2 * np.pi * f * 2.92 * tt) * _dec(m, 0.08, 0.001) * 0.25
    return y + _f(rng.normal(0, 1, m), 'low', 1500) * _dec(m, 0.006) * 0.15


def gongs(dur, seed=33, bpm=120):
    """Kulintang ensemble pattern (MINDANAO: Maguindanao, Maranao, Tausug, among others; see SOUND.md before using it):
    a row of knobbed gongs in a fast ostinato, agung on the low beat, dabakan drum."""
    rng = _rng(seed); n = _n(dur); out = np.zeros(n); s16 = 60 / bpm / 4
    row = [262, 294, 330, 392, 440, 494, 523, 587]
    cell = [0, 2, 4, 2, 5, 4, 2, 0, 3, 2, 4, 5, 7, 5, 4, 2]; k = 0
    while k * s16 < dur:
        t0 = k * s16
        if rng.random() < 0.88: _add(out, _gongtone(row[cell[k % 16]], 1.0, rng) * 0.4, t0)
        if k % 8 == 0: _add(out, gong(seed + k, 82.0).astype(float) * 10, t0)
        if k % 8 == 6: _add(out, gong(seed + k, 110.0).astype(float) * 6, t0)
        if k % 4 == 2:
            m = _n(0.1); _add(out, _f(rng.normal(0, 1, m), 'band', (150, 900)) * _dec(m, 0.03) * 0.5, t0)
        k += 1
    return _out(out)


def _brass(f, sec, rng):
    m = _n(sec); tt = _t(m); env = np.minimum(1, tt / 0.04) * np.minimum(1, (sec - tt) / 0.06)
    ph = np.cumsum(f * (1 + 0.003 * np.sin(2 * np.pi * 5.5 * tt))) / SR; saw = (ph % 1.0) - 0.5
    return _sweep(saw, 600 + 2400 * env, None, q=0.7) * env


def band(dur, seed=34, bpm=112):
    """A town brass band (banda) march in 2/4: bass drum and snare, a tuba on the beats, a cornet fanfare."""
    rng = _rng(seed); n = _n(dur); out = np.zeros(n); beat = 60 / bpm
    fan = [(0, 1), (4, 0.5), (7, 0.5), (12, 1), (11, 0.5), (7, 0.5), (9, 1), (7, 1), (4, 0.5), (5, 0.5), (7, 1), (2, 1), (0, 2)]
    b = 0
    while b * beat < dur:
        t0 = b * beat; m = _n(0.3); z = rng.normal(0, 1, m); tt = _t(m)
        if b % 2 == 0: _add(out, np.sin(2 * np.pi * 60 * tt) * _dec(m, 0.12) * 0.9, t0)                  # bass drum
        else: _add(out, (_f(z, 'band', (180, 6000)) * _dec(m, 0.08) + np.sin(2 * np.pi * 190 * tt) * _dec(m, 0.03)) * 0.45, t0)   # snare
        if b % 8 == 7:
            for r in range(6): _add(out, _f(rng.normal(0, 1, _n(0.06)), 'band', (200, 6000)) * _dec(_n(0.06), 0.02) * 0.2 * (r + 1) / 6, t0 + r * beat / 6)
        _add(out, _brass(58.3 * (1.5 if b % 2 else 1.0), beat * 0.6, rng) * 0.5, t0)                  # tuba, root and fifth
        b += 1
    t0 = 0.0
    while t0 < dur:
        for st, L in fan:
            _add(out, _brass(233.1 * 2 ** (st / 12), L * beat * 0.95, rng) * 0.35, t0); t0 += L * beat
        t0 += 4 * beat
    return _out(out)


def heartbeat(dur, seed=35, bpm=68):
    rng = _rng(seed); n = _n(dur); out = np.zeros(n); iv = 60 / bpm; m = _n(0.25); tt = _t(m); t0 = 0.1
    while t0 < dur:
        for dt, f, a in ((0, 52, 1.0), (0.28, 62, 0.65)):
            _add(out, (np.sin(2 * np.pi * f * tt) * _dec(m, 0.05, 0.004) + _f(rng.normal(0, 1, m), 'low', 150) * _dec(m, 0.03) * 0.3) * a, t0 + dt)
        t0 += iv * rng.uniform(0.98, 1.02)
    return _out(out)


MUSIC = {'none': None, 'guitar': guitar, 'flute': flute, 'gongs': gongs, 'band': band, 'drone': drone, 'heartbeat': heartbeat}


# ---------------------------------------------------------------- (e) whispers and walla
def whisper(dur=1.6, seed=36):
    """Breathy whisper with the timing and vowel colours of speech, and no words: formant-filtered noise, fricatives."""
    rng = _rng(seed); n = _n(dur); W, ons = _syllables(n, rng, rate=5.5, phrase=(3, 7), gap=(0.15, 0.4))
    out = sum(_formant(rng.normal(0, 1, n), VOWELS[v]) * _f(w, 'low', 30) for v, w in W.items())
    return _out(out + _consonants(n, ons, rng, 0.3))


def walla(dur=4.0, voices=12, seed=37, far=False, f0=(95, 230), vowels='aeiou', rate=4.5):
    """Many people talking at once with no words (the loop group's 'walla'). Each voice: a pulsed source at its own pitch and
    intonation, syllable timing, vowel colours. Linear trick: all voices' share of each vowel are summed first, then each
    vowel's formant filter runs once, so 60 voices cost what 1 does."""
    rng = _rng(seed); n = _n(dur); src = {v: np.zeros(n) for v in vowels}; cons = np.zeros(n)
    for k in range(voices):
        f = rng.uniform(*f0) * (1 + 0.12 * _smooth_rand(n, 1.5, rng, -1, 1)); pulse = ((np.cumsum(f) / SR) % 1.0) - 0.5
        W, ons = _syllables(n, rng, rate=rate * rng.uniform(0.8, 1.2), vowels=vowels); g = rng.uniform(0.3, 1.0)
        for v, w in W.items(): src[v] += pulse * _f(w, 'low', 25) * g
        if not far: cons += _consonants(n, ons, rng, 0.03) * g
    out = sum(_formant(_f(s, 'low', 3500), VOWELS[v]) for v, s in src.items()) + cons
    if far:                                                                                    # distance: darker and smeared
        out = _f(out, 'low', 2200); out = out + np.roll(out, _n(0.045)) * 0.5 + np.roll(out, _n(0.11)) * 0.3
    return _out(out)


# ---------------------------------------------------------------- the registry
EVENTS = {
    'steps_earth': lambda e, s: footsteps('earth', e.get('pace', 'walk'), e.get('count', 6), s),
    'steps_grass': lambda e, s: footsteps('grass', e.get('pace', 'walk'), e.get('count', 6), s),
    'steps_stone': lambda e, s: footsteps('stone', e.get('pace', 'walk'), e.get('count', 6), s),
    'steps_wood': lambda e, s: footsteps('wood', e.get('pace', 'walk'), e.get('count', 6), s),
    'steps_wet': lambda e, s: footsteps('wet', e.get('pace', 'walk'), e.get('count', 6), s),
    'cloth': lambda e, s: cloth(e.get('dur', 0.7), s), 'paper_tear': lambda e, s: paper_tear(e.get('dur', 0.9), s),
    'paper_tear_many': lambda e, s: paper_tear_many(e.get('dur', 1.1), s), 'door': lambda e, s: door(s),
    'dog_paws': lambda e, s: dog_paws(e.get('count', 12), s), 'dog_pant': lambda e, s: dog_pant(e.get('dur', 2.0), s),
    'growl': lambda e, s: growl(e.get('dur', 1.8), s),
    'cannon': lambda e, s: cannon(s), 'thunder': lambda e, s: thunder(e.get('dur', 4.5), s), 'bell': lambda e, s: bell(s),
    'splash': lambda e, s: splash(s), 'gong': lambda e, s: gong(s), 'impact': lambda e, s: impact(s),
    'whoosh': lambda e, s: whoosh(e.get('dur', 0.6), s), 'riser': lambda e, s: riser(e.get('dur', 2.0), s),
    'shimmer': lambda e, s: shimmer(e.get('dur', 2.5), s), 'drone': lambda e, s: drone(e.get('dur', 6.0), s),
    'heartbeat': lambda e, s: heartbeat(e.get('dur', 4.0), s), 'cheer': lambda e, s: cheer(e.get('dur', 2.8), s),
    'whisper': lambda e, s: whisper(e.get('dur', 1.6), s),
    'walla': lambda e, s: walla(e.get('dur', 4.0), e.get('voices', 12), s),
}


# ---------------------------------------------------------------- the mix
# Levels, in dB against the voice's gated RMS (SOUND.md says why). Beds and music are written at their level between words and
# DUCK dB lower under speech; effects duck only FX_DUCK so a hit can still be heard between words.
AMB_DB, MUSIC_DB, FOLEY_DB, SPOT_DB = -6.0, -5.0, -8.0, -4.0
DUCK, FX_DUCK, XF = 5.0, 3.0, 0.6                       # dB, dB, cross-fade between beds (s)


def _bed(spec, dur, seed):
    names = [] if spec in (None, 'none') else ([spec] if isinstance(spec, str) else list(spec))
    out = np.zeros(_n(dur))
    for k, nm in enumerate(names):
        nm, _, off = nm.partition(':')
        if nm == 'none': continue
        if nm not in AMBIENCES: raise SystemExit(f'sound.json: unknown ambience {nm!r}; known: {", ".join(AMBIENCES)}')
        out += AMBIENCES[nm](dur, seed + 101 * k).astype(float)[:len(out)] * 10 ** ((float(off) if off else 0.0) / 20)
    return out


def _voice_activity(v, rv):
    """0..1 per sample: 1 while the voice speaks (fast attack, slow release), for the ducking."""
    w = _n(0.02); m = len(v) // w + 1; vp = np.pad(v, (0, m * w - len(v)))
    db = 20 * np.log10(np.sqrt(np.mean(vp.reshape(m, w) ** 2, axis=1)) + 1e-9)
    act = (db > 20 * np.log10(rv) - 22).astype(float); out = np.empty(m); h = 0.0; hold = 0
    for i, a in enumerate(act):                                                                # attack 40 ms, hold 120 ms, release 350 ms
        if a: hold = 6
        tgt = 1.0 if (a or hold > 0) else 0.0; hold -= 1
        h += (tgt - h) * (0.5 if tgt > h else 0.055); out[i] = h
    return np.interp(np.arange(len(v)), np.arange(m) * w + w / 2, out)


def lines(tim, total):
    return [(0.0 if i == 0 else s['start'], tim[i + 1]['start'] if i + 1 < len(tim) else total) for i, s in enumerate(tim)]


def mix(episode_dir, tim, voice, out, src=None, cuts=(), plan=None):
    """Lay videos/<slug>/sound.json on the timeline, duck it under the voice, loudness-guard it into out (a WAV). -> stats."""
    if plan is None:
        with open(os.path.join(episode_dir, 'sound.json')) as fh: plan = json.load(fh)
    src = list(src) if src is not None else list(range(len(tim)))
    tmp = tempfile.mktemp(suffix='.wav'); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', voice, '-ac', '1', '-ar', str(SR), tmp], check=True)
    v, _ = sf.read(tmp, dtype='float32'); os.remove(tmp); dur = len(v) / SR + 0.8
    v = np.pad(v, (0, int(dur * SR) - len(v))).astype(np.float64); n = len(v); total = n / SR
    rv = soundtrack.gated_rms(v); act = _voice_activity(v, rv)
    LN = lines(tim, total); state = {'amb': None, 'music': 'none', 'level': 0.0}; per = []
    beds = np.zeros(n); mus = np.zeros(n); fol = np.zeros(n); spt = np.zeros(n); hush = np.zeros(n); events = 0
    for i, (a, b) in enumerate(LN):
        e = plan.get(str(src[i]), {})
        for k in ('amb', 'music', 'level'):
            if k in e: state[k] = e[k]
        per.append((a, b, json.dumps(state['amb']), state['music'], float(state['level'])))
        for lst, dest, base in ((e.get('foley', []), fol, FOLEY_DB), (e.get('spot', []), spt, SPOT_DB)):
            for ev in lst:
                w = ev['what']
                if w not in EVENTS: raise SystemExit(f'sound.json line {src[i]}: unknown sound {w!r}; known: {", ".join(EVENTS)}')
                x = EVENTS[w](ev, 1000 + 37 * i + events).astype(float); t0 = a + float(ev.get('at', 0.0))
                if w == 'riser': t0 -= len(x) / SR
                _add(dest, x * rv * 10 ** ((base + float(ev.get('gain', 0.0))) / 20) / _active_rms(x), t0); events += 1
                if ev.get('hush'): h0 = a + float(ev.get('at', 0.0)); _add(hush, np.ones(_n(float(ev['hush']))), h0 - float(ev['hush']))
    if plan.get('_', {}).get('whoosh_cuts'):
        for c in cuts:
            x = whoosh(0.45, int(c * 100)).astype(float); _add(spt, x * rv * 10 ** ((SPOT_DB - 9) / 20) / _active_rms(x), c - 0.3); events += 1
    # runs: consecutive lines with the same bed (or the same music) become one sound, cross-faded into the next run
    def runs(col):
        r = []
        for a, b, *k in per:
            key = k[col]
            if r and r[-1][2] == key: r[-1][1] = b
            else: r.append([a, b, key])
        return r
    for col, dest, base in ((0, beds, AMB_DB), (1, mus, MUSIC_DB)):
        for j, (a, b, spec) in enumerate(runs(col)):
            if col == 0: spec = json.loads(spec)
            if spec in (None, 'none', []): continue
            pre = XF / 2 if a > 0 else 0.0; L = b - a + pre + XF / 2
            if col == 1 and spec not in MUSIC: raise SystemExit(f'sound.json: unknown music {spec!r}; known: {", ".join(MUSIC)}')
            x = _bed(spec, L, 300 + j) if col == 0 else MUSIC[spec](L, 500 + j).astype(float) if MUSIC[spec] else None
            if x is None or not np.any(x): continue
            m = len(x); fi = _n(XF if a > 0 else 0.3); fo = _n(XF); g = np.ones(m)
            g[:fi] = np.sin(np.linspace(0, np.pi / 2, fi)) ** 2; g[-fo:] = np.minimum(g[-fo:], np.cos(np.linspace(0, np.pi / 2, fo)) ** 2)
            _add(dest, x * g * rv * 10 ** (base / 20) / _active_rms(x), a - pre)
    lvl = np.zeros(n)                                                                          # "level": a gain curve over the beds, ramped, so a level change never restarts a bed
    for a, b, *_k in per: lvl[_n(a) - 1 if a > 0 else 0:_n(b)] = _k[2]
    lvl = lfilter([1 - np.exp(-1 / (0.25 * SR))], [1, -np.exp(-1 / (0.25 * SR))], lvl, zi=[lvl[0] * np.exp(-1 / (0.25 * SR))])[0]
    hush = np.clip(_f(np.clip(hush, 0, 1), 'low', 8), 0, 1)
    duck = 10 ** (-(DUCK * act + 14 * hush) / 20); fduck = 10 ** (-FX_DUCK * act / 20)
    bed = (beds + mus) * duck * 10 ** (lvl / 20); fx = (fol + spt) * fduck
    pk = 0.9 * np.abs(v).max(); fx = pk * np.tanh(fx / pk)                                    # effects never pass the voice's peak (soft)
    mixd = v + bed + fx
    raw = tempfile.mktemp(suffix='.wav'); sf.write(raw, mixd.astype(np.float32), SR, subtype='FLOAT')
    soundtrack.loudnorm2(raw, out); os.remove(raw)
    sp = act > 0.9; gp = act < 0.1
    db = lambda x, m: round(float(20 * np.log10(np.sqrt(np.mean(x[m] ** 2)) + 1e-12)), 1) if m.any() else None
    vs = db(v, sp)
    return {'sound_design': os.path.join(os.path.basename(os.path.abspath(episode_dir)), 'sound.json'), 'voice_rms_db': vs,
            'bed_vs_voice_in_speech_db': round(db(bed, sp) - vs, 1) if db(bed, sp) is not None else None,
            'bed_vs_voice_between_words_db': round(db(bed, gp) - vs, 1) if db(bed, gp) is not None else None,
            'fx_peak_vs_voice_peak_db': round(float(20 * np.log10((np.abs(fx).max() + 1e-12) / np.abs(v).max())), 1),
            'events': events, 'duration': round(dur, 2)}


def soundtrack_for(episode_dir, tim, voice, out, cuts, hits, src=None):
    """The one switch build_anime.py calls: an episode with sound.json gets the designed mix, one without gets soundtrack.make
    exactly as before."""
    if os.path.exists(os.path.join(episode_dir, 'sound.json')): return mix(episode_dir, tim, voice, out, src=src, cuts=cuts)
    return soundtrack.make(voice, cuts, hits, out)


# ---------------------------------------------------------------- listening with numbers
def generators(dur=4.0):
    g = {f'amb:{k}': (lambda f=f: f(dur)) for k, f in AMBIENCES.items()}
    g.update({f'fx:{k}': (lambda f=f: f({}, 7)) for k, f in EVENTS.items()})
    g.update({f'music:{k}': (lambda f=f: f(dur * 2)) for k, f in MUSIC.items() if f})
    return g


def centroid(x):
    X = np.abs(np.fft.rfft(x * np.hanning(len(x)))); fr = np.fft.rfftfreq(len(x), 1 / SR)
    return float((X * fr).sum() / (X.sum() + 1e-12))


if __name__ == '__main__':
    if '--report' in sys.argv:
        d = sys.argv[sys.argv.index('--report') + 1] if len(sys.argv) > sys.argv.index('--report') + 1 else None
        if d: os.makedirs(d, exist_ok=True)
        print(f'{"sound":24s} {"len s":>6s} {"RMS dBFS":>9s} {"peak dBFS":>9s} {"crest dB":>8s} {"centroid Hz":>11s}')
        for k, f in generators().items():
            x = f().astype(np.float64)
            pk = 20 * np.log10(np.abs(x).max() + 1e-12); r = _rms_db(x)
            print(f'{k:24s} {len(x) / SR:6.2f} {r:9.1f} {pk:9.1f} {pk - r:8.1f} {centroid(x):11.0f}', flush=True)
            if d: sf.write(os.path.join(d, k.replace(':', '_') + '.wav'), (x / max(1.0, np.abs(x).max() / 0.9)).astype(np.float32), SR, subtype='PCM_16')
    else: print(__doc__)
