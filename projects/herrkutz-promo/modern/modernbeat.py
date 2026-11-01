# Original modern bounce/house track, 120 BPM (1 beat = 15 frames), Am-F-C-G. Synthesized here.
import numpy as np, wave
SR=44100; N=SR*15; B=0.5; rng=np.random.default_rng(9)
def t(d): return np.arange(int(SR*d))/SR
def add(b,s,at,g=1):
    i=int(at*SR); j=min(len(b),i+len(s))
    if j>i: b[i:j]+=g*s[:j-i]
def hz(m): return 440*2**((m-69)/12)
def kick(): x=t(.35); f=48+140*np.exp(-x*45); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x*8)
def clap():
    x=t(.3); n=np.diff(np.concatenate([[0],rng.standard_normal(len(x))])); e=np.exp(-x*20)
    for o in (0,.01,.02): e+=0.5*np.exp(-np.clip(x-o,0,None)*150)*(x>=o)
    return n*e*.35
def ohat(): x=t(.15); return np.diff(np.concatenate([[0],rng.standard_normal(len(x))]))*np.exp(-x*25)*.18
def pluck(ms,d=.22):
    x=t(d); s=sum(np.sign(np.sin(2*np.pi*hz(m)*x))*.5+np.sin(2*np.pi*hz(m)*x) for m in ms)
    s=np.convolve(s,np.ones(8)/8,'same'); return s*np.exp(-x*14)*.12
def sub(m,d): x=t(d); return np.sin(2*np.pi*hz(m-24)*x)*np.minimum(1,x/.01)*np.exp(-x*1.5)*.6
def riser(d): x=t(d); p=x/d; return (rng.standard_normal(len(x))*.15+np.sin(2*np.pi*np.cumsum(300+2500*p**2)/SR)*.2)*p**2
def rewind(d=.5): x=t(d); f=1800*np.exp(-x*5)+80; return (np.sin(2*np.pi*np.cumsum(f)/SR)*.25+rng.standard_normal(len(x))*.1)*np.sin(np.pi*x/d)
def pop(): x=t(.08); return np.sin(2*np.pi*np.cumsum(900+1400*np.exp(-x*60))/SR)*np.exp(-x*45)*.35
def whoosh(d=.35): x=t(d); n=rng.standard_normal(len(x)); n=np.convolve(n,np.ones(120)/120,'same')*6; return n*np.sin(np.pi*x/d)**2*.6
def ching():
    x=t(1.0); s=sum(np.sin(2*np.pi*hz(m)*x)*np.exp(-x*k) for m,k in ((88,4),(95,5),(100,6)))*.12
    return s+np.diff(np.concatenate([[0],rng.standard_normal(len(x))]))*np.exp(-x*40)*.3
def boom(): x=t(1.5); f=36+60*np.exp(-x*6); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x*2.2)
M=np.zeros(N); S=np.zeros(N)
chords=[([57,60,64],57),([53,57,60],53),([60,64,67],48),([55,59,62],55)]  # Am F C G
for beat in range(30):
    at=beat*B; ch,root=chords[(beat//4)%4]
    drop = at>=7.0 or at<1.0
    if 1.0<=at<1.5 or 6.5<=at<7.0: continue           # rewind gap + pre-drop gap
    add(M,kick(),at, 1.0 if (drop or at>=3.0) else .7)
    add(M,ohat(),at+.25)
    if beat%2==1: add(M,clap(),at)
    for e in (0,.75) if drop else (0,): add(M,pluck(ch),at+e*B)
    if beat%4==0 and (drop or at>=3.0): add(M,sub(root,2.0),at)
add(S,rewind(.5),1.0,1.0); add(S,riser(1.0),6.0,.9); add(S,boom(),7.0,1.0)
for at in (0.1,1.55,3.0,4.0,5.0,6.0,7.05,9.05,9.15): add(S,pop(),at)
for at in (3.0,4.0,5.0,6.0,8.95,11.45): add(S,whoosh(),at-.15,.8)
add(S,ching(),12.1,1.0)
mix=M+S*0.8; f=np.ones(N); i=int(14.4*SR); f[i:]=np.linspace(1,0,N-i); mix*=f; mix/=np.max(np.abs(mix))/0.9
w=wave.open("modern.wav","w"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype('<i2').tobytes()); w.close()
