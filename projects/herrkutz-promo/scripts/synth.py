import numpy as np, wave
SR=44100; T=30.0; N=int(SR*T); BPM=120; B=60/BPM
rng=np.random.default_rng(7)
def t(d): return np.arange(int(SR*d))/SR
def add(buf,sig,at,g=1.0):
    i=int(at*SR); j=min(N,i+len(sig)); buf[i:j]+=g*sig[:j-i]
def kick(): x=t(.45); f=50+120*np.exp(-x*35); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x*7)
def sub808(f0,d): x=t(d); return np.tanh(2*np.sin(2*np.pi*f0*x))*np.exp(-x*1.6)*0.6
def clap():
    x=t(.25); n=rng.standard_normal(len(x)); env=np.exp(-x*25)
    for o in (0.0,0.012,0.024): env+=np.exp(-np.clip(x-o,0,None)*120)*(x>=o)*0.6
    return np.diff(np.concatenate([[0],n]))*env*0.5
def hat(d=.05): x=t(d); n=np.diff(np.concatenate([[0],rng.standard_normal(len(x))])); return n*np.exp(-x*90)*0.25
def boom(): x=t(2.5); f=38+40*np.exp(-x*6); return (np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x*1.8)+0.3*rng.standard_normal(len(x))*np.exp(-x*10)*0.3)
def riser(d):
    x=t(d); n=rng.standard_normal(len(x)); out=np.zeros_like(n); a=0
    # crude sweeping one-pole highpass-ish brightening + pitch rise
    s=np.sin(2*np.pi*np.cumsum(200+1800*(x/d)**2)/SR)*0.3
    return (n*0.25*(x/d)**2+s*(x/d))
def whoosh(d=.5):
    x=t(d); n=rng.standard_normal(len(x)); k=int(SR*0.002); n=np.convolve(n,np.ones(k)/k,'same')*4
    return n*np.sin(np.pi*x/d)**2*0.9
def clipper(d):
    x=t(d); f=120  # mains-type motor buzz with blade chatter
    saw=2*((x*f)%1)-1; buzz=np.tanh(3*saw)*0.25+0.15*np.sin(2*np.pi*240*x)
    chatter=rng.standard_normal(len(x))*0.08*(0.6+0.4*np.sin(2*np.pi*13*x))
    env=np.minimum(1,np.minimum(x/0.05,(d-x)/0.08)); return (buzz+chatter)*env
def scrape(d=.35):
    x=t(d); n=rng.standard_normal(len(x)); n=np.diff(np.concatenate([[0],n]))
    am=0.5+0.5*np.sign(np.sin(2*np.pi*55*x))  # stubble grain
    return n*am*np.sin(np.pi*x/d)*0.35
L=np.zeros(N)  # music
S=np.zeros(N)  # sfx
bass=[41.2,41.2,49.0,36.7]  # E1 E1 G1 D1 per bar
for bar in range(15):
    b0=bar*4*B
    if 24.0<=b0<25.5: continue
    drop = 12<=bar*4*B<24 or b0>=25.5
    for k in (0,1.5,2.5): add(L,kick(),b0+k*B,0.9)
    for k in (1,3): add(L,clap(),b0+k*B,0.8)
    step=B/4 if drop else B/2
    for i in range(int(4*B/step)): add(L,hat(),b0+i*step,1.0 if i%2==0 else 0.6)
    add(L,sub808(bass[bar%4],4*B),b0,0.8)
# breakdown before reveal: mute 23.0-24.0 drums except riser
cut=slice(int(23.0*SR),int(24.0*SR)); L[cut]*=0.25
add(S,boom(),0.0,1.0); add(S,boom(),24.0,1.1); add(S,boom(),25.5,0.8)
add(S,riser(2.0),22.0,0.9)
for at in (0.45,9.45,19.95,25.4): add(S,whoosh(),at,1.0)
for st,d in ((4.5,5.0),(10.0,2.0),(16.0,2.0)): add(S,clipper(d),st,0.9)
for at in (2.5,3.5,6.5,8.5,11.0,13.0): add(S,scrape(),at,1.0)
def wr(name,x):
    x=x/np.max(np.abs(x))*0.89; w=wave.open(name,'w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x*32767).astype('<i2').tobytes()); w.close()
wr('beat.wav',L); wr('sfx.wav',S)
