"""Episode 1 sound, all synthesised in code: a light 3/4 music bed, a whoosh on every cut, a tick when a label
lands, wooden clacks for the exploded view, footfalls for the ride. No voice yet (the owner chooses it).
usage: python3 sound.py OUT.wav [VOICE.wav]   (with a voice: music and effects duck under it)
Levels follow history-indio/pipeline/SOUND.md: effects sit under the lead layer and the final mix is normalised
to -16 LUFS / -1.5 dBTP in build.sh. With no narration the music is the lead; when a voice is added, drop
MUSIC_DB by about 12 dB so the bed sits 11 to 12 dB under speech."""
import sys, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt
SR = 44100; DUR = 60.0; N = int(SR * DUR); rng = np.random.default_rng(7)
MUSIC_DB, FX_DB = -20.0, -24.0
CUTS = [3, 10, 16, 22, 28, 34, 42, 54]                       # seconds, same as compose.py SEGS
def db(x): return 10 ** (x / 20)
def rms(x): return float(np.sqrt(np.mean(x ** 2)) + 1e-12)
def filt(x, kind, f): return sosfilt(butter(2, f, kind, fs=SR, output='sos'), x)
def add(buf, sig, t, g=1.0):
    a = int(t * SR); b = min(len(buf), a + len(sig))
    if a < len(buf): buf[a:b] += sig[:b - a] * g
def pluck(f, dur=1.6, bright=1.0):
    t = np.arange(int(dur * SR)) / SR; y = sum(np.sin(2 * np.pi * f * k * t) * np.exp(-t * (2.2 + 1.3 * k)) / k ** (2.0 / bright) for k in range(1, 7))
    return y * np.minimum(1, t / 0.004)
def note(n): return 440.0 * 2 ** ((n - 69) / 12)
def music():
    out = np.zeros(N); beat = 60 / 108.0
    chords = [(50, [62, 66, 69]), (55, [62, 67, 71]), (57, [61, 64, 69]), (50, [62, 66, 69]),
              (47, [62, 66, 71]), (55, [62, 67, 71]), (57, [64, 67, 73]), (50, [62, 66, 69])]
    t = 0.0; bar = 0
    while t < DUR - 2:
        root, tri = chords[bar % 8]
        add(out, pluck(note(root), 2.2, 0.8), t, 0.9)
        add(out, pluck(note(tri[bar % 3]), 1.2), t + beat, 0.5); add(out, pluck(note(tri[(bar + 1) % 3]), 1.2), t + 2 * beat, 0.5)
        if bar % 2 == 1: add(out, pluck(note(tri[2] + 12), 1.0, 1.3), t + 2.5 * beat, 0.28)
        t += 3 * beat; bar += 1
    env = np.ones(N); f = int(1.5 * SR); env[-f:] = np.linspace(1, 0, f); return out * env
def whoosh(dur=0.45):
    n = int(dur * SR); x = rng.standard_normal(n); t = np.linspace(0, 1, n)
    y = np.zeros(n); blk = 512
    for a in range(0, n, blk):
        fc = 400 + 3600 * np.sin(np.pi * t[a]) ** 2; y[a:a + blk] = sosfilt(butter(2, [fc * 0.7, fc * 1.4], 'bandpass', fs=SR, output='sos'), x[a:a + blk])
    return y * np.sin(np.pi * t) ** 2
def tick():
    t = np.arange(int(0.06 * SR)) / SR; return np.sin(2 * np.pi * 1900 * t) * np.exp(-t * 90)
def clack(f=520):
    t = np.arange(int(0.12 * SR)) / SR; return (np.sin(2 * np.pi * f * t) + 0.6 * np.sin(2 * np.pi * f * 2.7 * t)) * np.exp(-t * 55) + 0.3 * filt(rng.standard_normal(len(t)), 'highpass', 2000) * np.exp(-t * 120)
def thud():
    t = np.arange(int(0.16 * SR)) / SR; return np.sin(2 * np.pi * 90 * t * (1 - 1.5 * t)) * np.exp(-t * 28) + 0.25 * filt(rng.standard_normal(len(t)), 'lowpass', 900) * np.exp(-t * 60)
def hit():
    t = np.arange(int(1.4 * SR)) / SR; return np.sin(2 * np.pi * 55 * t) * np.exp(-t * 4) + 0.5 * pluck(note(74), 1.4, 1.4)
def fx():
    out = np.zeros(N)
    add(out, hit(), 0.05, 1.6)
    for c in CUTS: add(out, whoosh(), c - 0.22, 1.0)
    for c in (10, 16, 22, 28): add(out, tick(), c + 8 / 24, 0.9)                 # close-up label lands
    for k in range(8): add(out, clack(430 + 45 * k), 34.2 + 0.11 * k, 0.8)        # parts pull apart
    for k in range(8): add(out, tick(), 34 + 62 / 24 + 0.03 * k, 0.5)             # exploded labels
    for k in range(36): add(out, thud(), 42.2 + k * (8 / 24), 0.7 if k % 2 else 0.55)   # footfalls, one per half stride
    rat = filt(rng.standard_normal(int(12 * SR)), 'bandpass', [180, 700]) * (0.6 + 0.4 * np.sin(2 * np.pi * 6 * np.arange(int(12 * SR)) / SR))
    e = np.ones(len(rat)); k = int(0.4 * SR); e[:k] = np.linspace(0, 1, k); e[-k:] = np.linspace(1, 0, k); add(out, rat * e, 42, 0.12)
    add(out, pluck(note(86), 2.0, 1.5), 56.0, 1.2)
    return out
VOICE = sf.read(sys.argv[2])[0] if len(sys.argv) > 2 else None
if VOICE is not None:
    if VOICE.ndim > 1: VOICE = VOICE.mean(1)
    VOICE = np.pad(VOICE, (0, max(0, N - len(VOICE))))[:N]
    MUSIC_DB, FX_DB = -25.0, -26.0                         # voice sits at -18 dBFS while speaking
m = music(); m *= db(MUSIC_DB) / rms(m)
x = fx(); act = x[np.abs(x) > 1e-4]; x *= db(FX_DB) / rms(act)
if VOICE is not None:                                       # duck: music -5 dB, effects -3 dB while the voice speaks
    hop = 441; e = np.sqrt(np.convolve(VOICE ** 2, np.ones(hop) / hop, 'same')); on = (e > db(-40)).astype(float)
    k_ = int(0.25 * SR); on = np.convolve(on, np.ones(k_) / k_, 'same').clip(0, 1)
    m *= db(-5 * on); x *= db(-3 * on)
    sp = on > 0.5
    print('bed_vs_voice_in_speech_db', round(20 * np.log10(rms(m[sp]) / rms(VOICE[sp])), 1))
mix = m + x + (VOICE if VOICE is not None else 0); mix = np.tanh(mix * 1.0)
st = np.stack([mix, mix], 1); st[:, 0] *= 0.98
sf.write(sys.argv[1], st.astype(np.float32), SR)
print('music_rms_db', round(20 * np.log10(rms(m)), 1), 'fx_active_rms_db', round(20 * np.log10(rms(x[np.abs(x) > 1e-4])), 1), 'peak', round(float(np.abs(mix).max()), 3))
