# Original punk-rock track, 180 BPM, E: E5-C5-G5-D5. Synthesized here.
import numpy as np, wave
SR=44100; N=SR*15; B=60/180; rng=np.random.default_rng(5)
def t(d): return np.arange(int(SR*d))/SR
def add(b,s,at,g=1):
    i=int(at*SR); j=min(len(b),i+len(s))
    if j>i: b[i:j]+=g*s[:j-i]
def hz(m): return 440*2**((m-69)/12)
def gtr(root,d,mute):
    x=t(d); s=0
    for iv,a in ((0,1),(7,.8),(12,.6)):
        for det in (-.06,.06): ph=hz(root+iv+det)*x; s=s+a*(2*(ph%1)-1)
    env=np.exp(-x*(18 if mute else 1.2))*np.minimum(1,x/.004)
    y=np.tanh(6*s*env)*0.5
    y=np.convolve(y,np.ones(6)/6,'same')  # tame fizz
    return y*(0.6 if mute else 1.0)
def bass(root,d): x=t(d); ph=hz(root-24)*x; return np.tanh(2.5*(2*(ph%1)-1))*np.exp(-x*6)*.5
def kick(): x=t(.3); f=50+130*np.exp(-x*40); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x*9)
def snare(): x=t(.25); n=np.diff(np.concatenate([[0],rng.standard_normal(len(x))])); return n*np.exp(-x*16)*.5+np.sin(2*np.pi*200*x)*np.exp(-x*30)*.4
def hat(): x=t(.05); return np.diff(np.concatenate([[0],rng.standard_normal(len(x))]))*np.exp(-x*80)*.15
def crash(): x=t(1.6); return np.diff(np.concatenate([[0],rng.standard_normal(len(x))]))*np.exp(-x*2.5)*.35
def buzz(d): x=t(d); saw=2*((x*120)%1)-1; return (np.tanh(3*saw)*.25+rng.standard_normal(len(x))*.05)*np.minimum(1,np.minimum(x/.03,(d-x)/.05))
def spray(d=.3): x=t(d); return np.diff(np.concatenate([[0],rng.standard_normal(len(x))]))*np.sin(np.pi*x/d)*.35
def thump(): x=t(.25); f=60+80*np.exp(-x*30); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x*14)*.9
G=np.zeros(N); D=np.zeros(N); S=np.zeros(N)
prog=[40,36,43,38]  # E C G D (low E = 40)
beat=0
while beat*B<14.0:
    at=beat*B; bar=beat//4; r=prog[bar%4]
    chorus = at>=5.333 and at<11.6
    stop = 5.0<=at<5.333 or 11.33<=at<11.67
    if not stop and at<11.67:
        for e in (0,.5): add(G,gtr(r,B/2*0.95,not chorus),at+e*B,.55); add(G,bass(r,B/2),at+e*B,.7)
        add(D,kick(),at) if beat%2==0 or chorus else None
        if beat%4 in (1,3): add(D,snare(),at)
        for e in (0,.5): add(D,hat(),at+e*B)
    beat+=1
# breaks: stop-time hits + crashes
for at in (5.333,11.667): add(D,crash(),at); add(D,kick(),at,1.2)
# outro: 11.67-15 big open E chord ring + drum fill then final hit at 13.333
add(G,gtr(40,3.3,False),11.667,.75); add(G,bass(40,1.5),11.667,.8)
for k in range(8): add(D,snare(),12.0+k*B/2,0.6+0.05*k)
add(D,crash(),13.333,1.1); add(D,kick(),13.333,1.3); add(G,gtr(40,1.6,False),13.333,.8)
# SFX
add(S,buzz(.66),4.333,.8)
for at in (1.0,2.333,4.0,11.333): add(S,spray(),at,1)
for at in (5.4,8.4,8.5): add(S,thump(),at,1)
mix=G*0.9+D*1.0+S*0.8
f=np.ones(N); i=int(14.5*SR); f[i:]=np.linspace(1,0,N-i); mix*=f; mix/=np.max(np.abs(mix))/0.9
w=wave.open("punk.wav","w"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype('<i2').tobytes()); w.close()
