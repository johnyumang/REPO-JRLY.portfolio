import numpy as np, wave
SR=44100; N=SR*30; rng=np.random.default_rng(11)
def t(d): return np.arange(int(SR*d))/SR
def add(buf,s,at,g=1.0):
    i=int(at*SR); j=min(len(buf),i+len(s)); 
    if j>i: buf[i:j]+=g*s[:j-i]
def hz(n): return 440*2**((n-69)/12)
def reverb(x,dec=2.2,mix=0.35):
    L=int(SR*dec); ir=rng.standard_normal(L)*np.exp(-np.arange(L)/SR*6.9/dec); ir[:int(SR*0.02)]=0
    n=1<<int(np.ceil(np.log2(len(x)+L))); y=np.fft.irfft(np.fft.rfft(x,n)*np.fft.rfft(ir,n),n)[:len(x)]
    y/= (np.max(np.abs(y))+1e-9); y*=np.max(np.abs(x))
    return x*(1-mix)+y*mix
def pad(notes,d,amp=0.12):
    x=t(d); s=np.zeros_like(x)
    for n in notes:
        for det in (-0.08,0,0.08):
            f=hz(n+det)
            for h,a in ((1,1),(2,.35),(3,.18),(4,.08)): s+=a*np.sin(2*np.pi*f*h*x+rng.uniform(0,6))
    env=np.minimum(1,np.minimum(x/0.8,(d-x)/0.8)).clip(0); return s*env*amp/len(notes)
def bell(n,d=2.5,amp=.25):
    x=t(d); f=hz(n); return amp*np.exp(-x*2.2)*(np.sin(2*np.pi*f*x)+.4*np.sin(2*np.pi*f*2.76*x)*np.exp(-x*4)+.2*np.sin(2*np.pi*f*5.4*x)*np.exp(-x*7))
def kick(g=1): x=t(.5); f=45+110*np.exp(-x*30); return g*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x*6)
def snare():
    x=t(.35); n=rng.standard_normal(len(x)); n=np.diff(np.concatenate([[0],n]))
    return (n*np.exp(-x*14)*.45+np.sin(2*np.pi*190*x)*np.exp(-x*25)*.4)
def hat(g=.12): x=t(.04); n=np.diff(np.concatenate([[0],rng.standard_normal(len(x))])); return n*np.exp(-x*110)*g
def tick(): x=t(.03); return np.sin(2*np.pi*3200*x)*np.exp(-x*220)*.25+np.sin(2*np.pi*1800*x)*np.exp(-x*300)*.15
def boom(g=1): x=t(3); f=32+55*np.exp(-x*5); return g*(np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x*1.3))
def drone(d): x=t(d); s=np.sin(2*np.pi*hz(40)*x)*.5+np.sin(2*np.pi*hz(47)*x)*.25; return s*(0.8+0.2*np.sin(2*np.pi*0.25*x))*np.minimum(1,x/1.5)*np.minimum(1,(d-x)/0.3)*.35
def riser(d):
    x=t(d); p=x/d; n=rng.standard_normal(len(x)); k=np.maximum(1,(40*(1-p)).astype(int))
    s=np.sin(2*np.pi*np.cumsum(150+1500*p**2)/SR)
    return (n*0.18+s*0.25)*p**2.2
def whoosh(d=.6):
    x=t(d); n=rng.standard_normal(len(x)); k=int(SR*.003); n=np.convolve(n,np.ones(k)/k,'same')*5; return n*np.sin(np.pi*x/d)**3*.8
def snip():  # scissor: two metallic clicks + shear
    x=t(.12); n=rng.standard_normal(len(x)); s=np.diff(np.concatenate([[0],n]))*np.exp(-x*60)*.35
    s+=np.sin(2*np.pi*5200*x)*np.exp(-x*90)*.3; return s
def clipper(d):
    x=t(d); saw=2*((x*120)%1)-1; s=np.tanh(3*saw)*.22+.12*np.sin(2*np.pi*240*x)+rng.standard_normal(len(x))*.06*(0.6+.4*np.sin(2*np.pi*13*x))
    return s*np.minimum(1,np.minimum(x/.05,(d-x)/.1))
def shutter(): x=t(.08); n=rng.standard_normal(len(x)); return np.diff(np.concatenate([[0],n]))*(np.exp(-x*120)+0.6*np.exp(-np.clip(x-.04,0,None)*150)*(x>.04))*.5
M=np.zeros(N); D=np.zeros(N); S=np.zeros(N)
# --- intro 0-4.5: drone + clock ticks
add(M,drone(4.6),0)
for k in range(9): add(S,tick(),0.5+k*0.5,0.9)
add(M,pad([52,55,59],4.6,0.06),0)              # Em, very soft
# --- 4.5-12.25 craft: pulse + Em -> C pads
add(M,boom(0.5),4.5)
for st,ch in ((4.5,[52,55,59,64]),(6.5,[48,52,55,59]),(8.5,[50,54,57,62]),(10.5,[52,55,59,64])):
    add(M,pad(ch,2.4,0.11),st)
b=4.5
while b<12.24:
    add(D,kick(.75),b); add(D,hat(.08),b+.25)
    b+=0.5
for b in np.arange(5.5,10.5,0.5): add(S,snip(),b+0.02,0.9)
add(S,clipper(1.25),10.5,0.8)
add(S,whoosh(.6),11.6)
# --- build 12.25-14.75
add(M,pad([48,52,55,59],1.6,0.12),12.25); add(M,pad([50,54,57,62],1.6,0.13),13.6)
for b in np.arange(12.25,14.75,0.5): add(D,kick(.85),b)
for b in np.arange(13.25,14.75,0.25): add(D,snare()*0.35,b)
for b in np.arange(12.25,14.75,0.125): add(D,hat(.07),b)
add(S,riser(2.5),12.25,0.9)
# 14.75-15.25 silence (breath), only a reversed bell swell
rb=bell(76,0.5,0.25)[::-1]; add(S,rb,14.75)
# --- 15.25 hero: G major lift
add(S,boom(1.1),15.25)
add(M,pad([43,55,59,62,67],6.8,0.14),15.25)
for k,n in enumerate([79,74,71,74,79,83]): add(M,bell(n,2.2,.16),15.25+k*0.5)
add(M,pad([48,55,60,64,67],3.4,0.12),22.0)
b=15.25
while b<25.2:
    bar=(b-15.25)%2
    if bar in (0,0.75): add(D,kick(.9),b)
    if abs(bar-1.0)<1e-6: add(D,snare(),b)
    add(D,hat(.10 if (b*4)%2==0 else .06),b)
    b+=0.25
add(S,shutter(),17.75,1.0); add(S,whoosh(.5),17.55); add(S,boom(0.45),17.75)
add(S,whoosh(.7),21.75)
# --- 25.25 end: final hit + resolve
add(S,boom(1.0),25.25); add(M,pad([43,50,55,59,62],4.75,0.16),25.25)
for k,n in enumerate([67,71,74,79]): add(M,bell(n,3.0,.14),25.25+k*0.35)
mix=reverb(M,2.8,0.45)+reverb(D,1.0,0.15)+reverb(S,1.4,0.2)*0.9
def wr(nm,x):
    x=x/np.max(np.abs(x))*0.9; w=wave.open(nm,'w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x*32767).astype('<i2').tobytes()); w.close()
fade=np.ones(N); i=int(28.6*SR); fade[i:]=np.linspace(1,0,N-i)**1.5
wr("score.wav",mix*fade)
