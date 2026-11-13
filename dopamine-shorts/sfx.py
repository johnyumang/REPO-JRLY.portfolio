"""Synthesized soundtrack (no samples, no music licences): 120 BPM bass pulse + kicks, wind/tyre bed,
portal risers and impacts at each cut. usage: sfx.py <out.wav> <dur> <cut1,cut2,...> [bed: dirt|air|lava|space|city ... per segment]"""
import sys, numpy as np, scipy.signal as ss, pyloudnorm as pyln, soundfile as sf
SR = 48000; rng = np.random.default_rng(7)
def t_(d): return np.arange(int(d * SR)) / SR
def bp(x, lo, hi, o=2): return ss.sosfilt(ss.butter(o, [lo, hi], 'band', fs=SR, output='sos'), x)
def lp(x, f, o=2): return ss.sosfilt(ss.butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return ss.sosfilt(ss.butter(o, f, 'high', fs=SR, output='sos'), x)
def env(n, a, r): e = np.ones(n); a = int(a*SR); r = int(r*SR); e[:a] = np.linspace(0,1,a); e[-r:] *= np.linspace(1,0,r); return e
def kick(d=0.45):
    t = t_(d); f = 45 + 110*np.exp(-t*28); return np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t*7)
def whoosh(d=0.5, lo=300, hi=6000):
    n = int(d*SR); x = rng.standard_normal(n); f = np.geomspace(lo, hi, n)
    y = np.zeros(n); blk = 1024
    for i in range(0, n, blk): y[i:i+blk] = bp(x[i:i+blk], max(40, f[i]*0.6), min(20000, f[i]*1.4))
    return y * np.sin(np.linspace(0, np.pi, n))**2
def riser(d=0.8):
    t = t_(d); f = np.geomspace(150, 2400, len(t)); return 0.5*np.sin(2*np.pi*np.cumsum(f)/SR)*(t/d)**2 + 0.6*whoosh(d, 200, 9000)
def impact(d=1.2):
    t = t_(d); boom = np.sin(2*np.pi*np.cumsum(38+60*np.exp(-t*10))/SR)*np.exp(-t*3.5)
    crack = hp(rng.standard_normal(len(t)), 1500)*np.exp(-t*25)*0.5
    shimmer = sum(np.sin(2*np.pi*f*t+rng.random()*6) for f in (880, 1320, 1975, 2637))*np.exp(-t*4)*0.06
    return boom + crack + shimmer
def bed(kind, d):
    n = int(d*SR); w = rng.standard_normal(n); t = t_(d)
    if kind == 'dirt':  # tyre on dirt: low rumble + gravel crackle + wind
        crack = (rng.random(n) < 0.004) * rng.standard_normal(n); return 0.5*lp(w,180)*4 + 0.25*bp(crack,800,5000) + 0.2*bp(w,300,2000)*(1+0.5*np.sin(2*np.pi*0.7*t))
    if kind == 'air':   # high wind
        return 0.45*bp(w, 200, 1800)*(1+0.6*np.sin(2*np.pi*0.4*t)) + 0.15*hp(w, 3000)
    if kind == 'lava':  # roar + bubbles
        bub = np.zeros(n); 
        for s in rng.integers(0, n-6000, 40): bub[s:s+6000] += np.sin(2*np.pi*np.linspace(120,260,6000)*t[:6000])*np.exp(-np.linspace(0,8,6000))
        return 0.8*lp(w, 120)*4 + 0.25*bub + 0.15*bp(w, 400, 1500)
    if kind == 'space': # deep drone + shimmer
        return 0.4*np.sin(2*np.pi*55*t)*(0.6+0.4*np.sin(2*np.pi*0.3*t)) + 0.2*np.sin(2*np.pi*82.5*t) + 0.08*bp(w, 3000, 9000)
    if kind == 'city':  # wind + distant traffic hum + glass squeal
        return 0.35*bp(w, 150, 1200) + 0.12*np.sin(2*np.pi*(2200+300*np.sin(2*np.pi*3*t))*t)*np.abs(np.sin(2*np.pi*1.1*t)) + 0.3*lp(w, 100)*3
    return 0.3*bp(w, 200, 2000)
def add(buf, x, at, g=1.0):
    i = int(at*SR); x = x[:max(0, len(buf)-i)]; buf[i:i+len(x)] += g*x
if __name__ == '__main__':
    out, D = sys.argv[1], float(sys.argv[2]); cuts = [float(c) for c in sys.argv[3].split(',')]; beds = sys.argv[4].split(',')
    N = int(D*SR); mix = np.zeros(N); edges = [0.0] + cuts + [D]
    for k, (a, b) in enumerate(zip(edges[:-1], edges[1:])):
        x = bed(beds[k], b-a) * env(int((b-a)*SR), 0.03, 0.05); add(mix, x, a, 0.5)
    bass = np.zeros(N); beat = 0.5
    for i, bt in enumerate(np.arange(0, D, beat)):
        g = 0.35 if bt < cuts[0] else 1.0       # hook is quieter, the beat drops in when the portal opens
        add(mix, kick(), bt, 0.9*g)
        t = t_(beat); add(bass, np.sin(2*np.pi*(55 if (i//8) % 2 == 0 else 49)*t)*np.exp(-t*4)*(1-np.exp(-t*200)), bt, g)
        if i % 2: add(mix, hp(rng.standard_normal(int(0.05*SR)), 7000)*np.exp(-np.linspace(0, 6, int(0.05*SR))), bt, 0.15*g)
    mix += 0.7*lp(np.tanh(bass*1.5), 300)
    for c in cuts: add(mix, riser(0.8), c-0.8, 0.5); add(mix, impact(), c, 0.9); add(mix, whoosh(0.45, 4000, 400), c, 0.5)
    add(mix, whoosh(0.4, 300, 5000), 0, 0.6)   # opening whoosh so second one is not silent
    mix[-int(0.04*SR):] *= np.linspace(1, 0, int(0.04*SR))
    st = np.stack([mix, np.roll(mix, 240)*0.97], 1)          # light width
    m = pyln.Meter(SR); st = pyln.normalize.loudness(st, m.integrated_loudness(st), -14.0)
    tp = np.abs(ss.resample_poly(st, 4, 1, axis=0)).max(); lim = 10**(-1.2/20)
    if tp > lim:   # soft-clip peaks above the ceiling, then renormalize to -14
        for _ in range(6):
            st = np.tanh(st/lim*0.9)*lim/np.tanh(0.9)*0.98; st = pyln.normalize.loudness(st, m.integrated_loudness(st), -14.0)
            if np.abs(ss.resample_poly(st, 4, 1, axis=0)).max() <= lim: break
        st = np.clip(st, -lim, lim)
    sf.write(out, st, SR, subtype='PCM_24'); print('LUFS %.1f  TP %.2f dB' % (m.integrated_loudness(st), 20*np.log10(np.abs(ss.resample_poly(st,4,1,axis=0)).max())))
