"""Soundtrack v2: beds per shot, fork thuds at the simulated bump times, transition whooshes, hit on frame 0, loopable tail.
usage: sfx2.py <out.wav> <timeline.json>   timeline: {"dur":19.0,"shots":[{"t0","t1","bed","bumps":[[t,a],...],"slow":bool}]}"""
import sys, json, numpy as np, scipy.signal as ss, pyloudnorm as pyln, soundfile as sf
from sfx import SR, rng, t_, bp, lp, hp, env, kick, whoosh, riser, impact, bed, add
def thud(a):   # fork bottoming: low knock + tyre slap + chain rattle
    t = t_(0.28); k = np.sin(2*np.pi*np.cumsum(70 + 90*np.exp(-t*40))/SR)*np.exp(-t*16)
    slap = bp(rng.standard_normal(len(t)), 300, 1800)*np.exp(-t*35)*0.6
    rattle = hp(rng.standard_normal(len(t)), 3500)*np.exp(-t*22)*(np.sin(2*np.pi*38*t) > 0)*0.25
    return (k + slap + rattle)*min(1.0, 0.35 + 0.25*a)
def water(d):  # slow-motion splash: filtered noise swell with bubbles
    t = t_(d); w = rng.standard_normal(len(t)); return (0.6*bp(w, 250, 2500) + 0.3*lp(w, 200)*3)*np.sin(np.linspace(0, np.pi, len(t)))**1.5
TL = json.load(open(sys.argv[2])); D = TL['dur']; N = int(D*SR); mix = np.zeros(N); bass = np.zeros(N)
for s in TL['shots']:
    d = s['t1'] - s['t0']; add(mix, bed(s['bed'], d)*env(int(d*SR), 0.04, 0.06), s['t0'], 0.5)
    for t, a in s.get('bumps', []): add(mix, thud(a), s['t0'] + t, 1.0)
    if s.get('slow'): add(mix, water(d), s['t0'], 0.8); add(mix, lp(riser(d*0.9)[::-1].copy(), 900), s['t0'], 0.35)   # downshift feel
    if s['t0'] > 0: add(mix, riser(0.6), s['t0'] - 0.6, 0.45); add(mix, impact(), s['t0'], 0.85); add(mix, whoosh(0.4, 5000, 400), s['t0'], 0.5)
beat = 0.5
for i, bt in enumerate(np.arange(0, D, beat)):
    slow = any(s.get('slow') and s['t0'] <= bt < s['t1'] for s in TL['shots']); g = 0.45 if slow else 1.0   # beat ducks in slow motion
    add(mix, kick(), bt, 0.85*g); t = t_(beat)
    add(bass, np.sin(2*np.pi*(55 if (i//8) % 2 == 0 else 49)*t)*np.exp(-t*4)*(1 - np.exp(-t*200)), bt, g)
    if i % 2: add(mix, hp(rng.standard_normal(int(0.05*SR)), 7000)*np.exp(-np.linspace(0, 6, int(0.05*SR))), bt, 0.14*g)
mix += 0.7*lp(np.tanh(bass*1.5), 300)
add(mix, impact(), 0.0, 1.0); add(mix, whoosh(0.5, 300, 6000), 0.0, 0.7)           # hook: hit on frame 0
add(mix, riser(0.9), D - 0.9, 0.5)                                                  # riser into the loop point
mix[-int(0.02*SR):] *= np.linspace(1, 0, int(0.02*SR))
st = np.stack([mix, np.roll(mix, 240)*0.97], 1); m = pyln.Meter(SR); lim = 10**(-1.3/20)
for _ in range(8):
    st = pyln.normalize.loudness(st, m.integrated_loudness(st), -14.0)
    if np.abs(ss.resample_poly(st, 4, 1, axis=0)).max() <= lim: break
    st = np.tanh(st/lim*0.9)*lim/np.tanh(0.9)*0.97
st = np.clip(st, -lim, lim); sf.write(sys.argv[1], st, SR, subtype='PCM_24')
print('LUFS %.1f TP %.2f' % (m.integrated_loudness(st), 20*np.log10(np.abs(ss.resample_poly(st, 4, 1, axis=0)).max())))
