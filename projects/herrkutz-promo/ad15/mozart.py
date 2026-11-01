# Original synthesized performance of Mozart, Eine kleine Nachtmusik K.525, I. Allegro, opening (public domain).
import numpy as np, wave
SR=44100; T=15.0; N=int(SR*T); rng=np.random.default_rng(3)
Q=0.375  # quarter = 160 bpm -> 4 bars = 6.0 s
def hz(m): return 440*2**((m-69)/12)
def t(d): return np.arange(int(SR*d))/SR
def add(b,s,at,g=1):
    i=int(at*SR); j=min(len(b),i+len(s))
    if j>i: b[i:j]+=g*s[:j-i]
def string(m,d,amp=.2,vib=True,att=.03):
    x=t(d+.25); f=hz(m)*(1+(0.004*np.sin(2*np.pi*5.6*x)*np.clip((x-.12)/.2,0,1) if vib else np.zeros_like(x)))
    ph=2*np.pi*np.cumsum(f)/SR; s=sum(np.sin(k*ph)/k**1.15*(1 if k<6 else .6) for k in range(1,13))
    s+=0.02*rng.standard_normal(len(x))  # bow noise
    env=np.clip(x/att,0,1)*np.where(x<d,1,np.exp(-(x-d)*14)); return s*env*amp
# melody, (midi or None for rest, beats)
G4,D4,B4,D5,C5,A4,Fs4,G3,D3=67,62,71,74,72,69,66,55,50
bars=[(G4,1),(None,.5),(D4,.5),(G4,1),(None,.5),(D4,.5),
      (G4,.5),(D4,.5),(G4,.5),(B4,.5),(D5,2),
      (C5,1),(None,.5),(A4,.5),(C5,1),(None,.5),(A4,.5),
      (C5,.5),(A4,.5),(Fs4,.5),(A4,.5),(D4,2)]
mel=np.zeros(N); low=np.zeros(N); pad=np.zeros(N)
def play(at,octs,gain):
    p=at
    for m,b in bars:
        d=b*Q*0.92
        if m: 
            for o,g in octs: add(mel if o>=0 else low,string(m+12*o,d,.16*g,vib=b>=1,att=.02 if b<1 else .04),p)
        p+=b*Q
    return p
# phrase 1 (0-6s): unison strings, violins + violas, mf
play(0.0,[(0,1),(-1,.55)],0.8)
# phrase 2 (6-12s): tutti forte at the reveal: violins 8va + cellos 8vb + sustained harmony
play(6.0,[(1,.75),(0,1),(-1,.7),(-2,.5)],1.0)
def chord(ms,at,d,g=.06):
    for m in ms: add(pad,string(m,d,g,att=.35),at)
chord([G3,59,62,67],6.0,3.0); chord([D3,57,60,66],9.0,3.0)   # G  | D7
# final cadence (12-15s): G major, held, tremolo feel
for m,g in ((43,.10),(55,.08),(59,.07),(62,.07),(67,.08),(71,.06),(79,.05)):
    x=t(3.0); trem=0.75+0.25*np.sin(2*np.pi*7*x)
    s=string(m,2.8,g,att=.08)[:len(x)]*trem; add(pad,s,12.0)
def reverb(x,dec=1.8,mix=.32):
    L=int(SR*dec); ir=rng.standard_normal(L)*np.exp(-np.arange(L)/SR*6.9/dec); ir[:int(SR*.015)]=0
    n=1<<int(np.ceil(np.log2(len(x)+L))); y=np.fft.irfft(np.fft.rfft(x,n)*np.fft.rfft(ir,n),n)[:len(x)]
    y*=np.max(np.abs(x))/(np.max(np.abs(y))+1e-9); return x*(1-mix)+y*mix
mus=reverb(mel+low*0.9+pad,2.0,0.33)
# SFX layer (kept light under the strings)
S=np.zeros(N)
def snip(): x=t(.12); n=rng.standard_normal(len(x)); return np.diff(np.concatenate([[0],n]))*np.exp(-x*60)*.3+np.sin(2*np.pi*5200*x)*np.exp(-x*90)*.25
def whoosh(d=.45): x=t(d); n=rng.standard_normal(len(x)); k=int(SR*.003); n=np.convolve(n,np.ones(k)/k,'same')*5; return n*np.sin(np.pi*x/d)**3*.7
def clip(d): x=t(d); saw=2*((x*120)%1)-1; return (np.tanh(3*saw)*.18+.1*np.sin(2*np.pi*240*x)+rng.standard_normal(len(x))*.05)*np.minimum(1,np.minimum(x/.05,(d-x)/.1))
def boom(g): x=t(2.5); f=34+50*np.exp(-x*5); return g*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x*1.6)
def shine(): x=t(.9); return sum(np.sin(2*np.pi*hz(m)*x)*np.exp(-x*3.5) for m in (91,95,98))*.08
for b in (2.5,2.875,3.25,3.625,4.0,4.375): add(S,snip(),b,.8)
add(S,clip(1.0),4.5,.7)
for at in (1.28,5.78,11.8): add(S,whoosh(),at,.9)
add(S,boom(.7),6.0); add(S,boom(.45),12.0); add(S,shine(),12.6)
mix=mus/np.max(np.abs(mus))*0.85+reverb(S,1.2,.2)*0.55
f=np.ones(N); i=int(14.2*SR); f[i:]=np.linspace(1,0,N-i)**1.4; f[:int(.02*SR)]=np.linspace(0,1,int(.02*SR))
mix*=f; mix/=np.max(np.abs(mix))/0.9
w=wave.open("music15.wav","w"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype('<i2').tobytes()); w.close()
