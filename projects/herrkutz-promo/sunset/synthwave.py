# Original 80s synthwave score, 120 BPM, Am-F-C-G. Synthesized here.
import numpy as np, wave
SR=44100; N=SR*15; B=0.5; rng=np.random.default_rng(21)
def t(d): return np.arange(int(SR*d))/SR
def add(b,s,at,g=1):
    i=int(at*SR); j=min(len(b),i+len(s))
    if j>i: b[i:j]+=g*s[:j-i]
def hz(m): return 440*2**((m-69)/12)
def saw(f,x): ph=f*x; return 2*(ph%1)-1
def lp(s,k): return np.convolve(s,np.ones(k)/k,'same')
def arp(m,d): x=t(d); s=lp(saw(hz(m),x)+saw(hz(m)*1.005,x),10); return s*np.exp(-x*9)*.18
def pad(ms,d):
    x=t(d); s=sum(lp(saw(hz(m)*(1+dt),x),30) for m in ms for dt in (-.004,.004))
    return s*np.minimum(1,x/.6)*np.minimum(1,(d-x)/.4).clip(0)*.05
def lead(m,d): x=t(d); f=hz(m)*(1+.006*np.sin(2*np.pi*5*x)); s=lp(np.sign(np.sin(2*np.pi*np.cumsum(f)/SR)),6); return s*np.minimum(1,x/.02)*np.exp(-x*1.2)*.10
def kick(): x=t(.4); f=45+120*np.exp(-x*35); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x*7)
def gsnare():  # gated reverb snare
    x=t(.32); n=rng.standard_normal(len(x)); n=lp(n,3); return n*(x<.26)*np.exp(-x*3)*.38+np.sin(2*np.pi*190*x)*np.exp(-x*25)*.35
def hat(): x=t(.04); return np.diff(np.concatenate([[0],rng.standard_normal(len(x))]))*np.exp(-x*90)*.10
def hit(): x=t(2.0); f=40+70*np.exp(-x*6); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x*2)+lp(rng.standard_normal(len(x)),4)*np.exp(-x*4)*.3
def whoosh(d=.4): x=t(d); n=lp(rng.standard_normal(len(x)),150)*6; return n*np.sin(np.pi*x/d)**2*.6
def tick(): x=t(.06); return np.sin(2*np.pi*2400*x)*np.exp(-x*80)*.25
M=np.zeros(N); S=np.zeros(N)
ch=[([57,60,64],45),([53,57,60],41),([48,52,55],36),([55,59,62],43)]  # Am F C G
mel=[(76,1),(74,.5),(72,.5),(69,2),(72,1),(74,.5),(76,.5),(79,2)]
for bar in range(8):
    at=bar*2.0; ms,r=ch[bar%4]
    add(M,pad([m+12 for m in ms],2.05),at)
    full = at>=3.5
    for k in range(16):  # 16th-note arp bass
        if at+k*.125<15: add(M,arp(r+(12 if k%4==2 else 0),.12),at+k*.125, .9 if full else .5)
    for b in range(4):
        tt=at+b*B
        if full or tt>=1.5:
            add(M,kick(),tt) if b in (0,2) or tt>=8.0 else None
            if b in (1,3): add(M,gsnare(),tt)
        for e in (0,.5): add(M,hat(),tt+e*B)
# lead melody from the reveal
p=8.0
for m,d in mel:
    if p<12: add(M,lead(m,d*B*1.6),p)
    p+=d*B*1.6
# end: big Am chord swell
add(M,pad([57,60,64,69,72],3.0)*2.2,12.0)
# SFX: freeze-frame hits, HUD ticks, reveal impact
for at in (2.4,7.0): add(S,hit(),at,.7); add(S,whoosh(),at-.2,.8)
for at in (1.5,3.5,6.0,8.0,10.5,12.0): add(S,whoosh(.35),at-.15,.6)
for k in range(12): add(S,tick(),3.5+k*0.45,.6)
add(S,hit(),8.0,1.0); add(S,hit(),12.0,.6)
mix=M+S*.7; f=np.ones(N); i=int(14.3*SR); f[i:]=np.linspace(1,0,N-i); mix*=f; mix/=np.max(np.abs(mix))/0.9
w=wave.open("synthwave.wav","w"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype('<i2').tobytes()); w.close()
