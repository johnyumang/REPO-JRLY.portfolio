import subprocess
from edl2 import EDL
SRC="/root/.claude/uploads/ee52e1aa-2485-56aa-89c7-ac031a1ae968/7a589f4b-copy_05059AA4-92B2-4266-8573-8943049F3456.mov"
G={"before":"eq=saturation=0.18:contrast=1.06:brightness=-0.02,colorbalance=bs=0.06:bm=0.04:rh=-0.03",
   "warm":"eq=contrast=1.10:saturation=1.08:gamma=0.96,colorbalance=rs=0.05:gs=0.01:bs=-0.04:rh=0.04:bh=-0.05",
   "hero":"eq=contrast=1.14:saturation=1.15:gamma=0.95,colorbalance=rs=0.06:bs=-0.04:rh=0.05:bh=-0.05",
   "end":"eq=contrast=1.12:saturation=1.0:brightness=-0.10:gamma=0.92,colorbalance=rs=0.05:bs=-0.03"}
LOOK="vignette=PI/4.5,noise=alls=5:allf=t,format=yuv420p"
DEFL="deflicker=size=7:mode=pm"
def push(w,h,n,rate=0.0010):  # sub-pixel-smooth push-in: zoompan at 3x then downscale
    return (f"scale={w*3}:{h*3}:flags=bicubic,zoompan=z='1+{rate}*on':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={w*3}x{h*3}:fps=30,"
            f"scale={w}:{h}:flags=lanczos")
def run(a): subprocess.run(["ffmpeg","-v","error","-y"]+a,check=True)
lst=open("list2.txt","w"); t0=0
for i,(n,src,sp,g,_) in enumerate(EDL):
    d=n/30; out=f"r{i:02d}.mov"
    afx=f"aresample=44100,apad,atrim=0:{d},afade=t=in:d=0.012,afade=t=out:st={d-0.015}:d=0.015"
    if g=="split":
        run(["-ss","0.30","-i",SRC,"-ss","32.80","-i",SRC,"-ss","20.0","-t",str(d+0.1),"-i",SRC,"-filter_complex",
          f"[0:v]trim=end_frame=1,scale=720:1280,crop=720:640:0:200,{G['before']},loop={n}:1:0,setpts=N/30/TB,{push(720,640,n,0.0008)}[a];"
          f"[1:v]trim=end_frame=1,scale=720:1280,crop=720:640:0:520,{G['hero']},loop={n}:1:0,setpts=N/30/TB,{push(720,640,n,0.0008)}[b];"
          f"[a][b]vstack,drawbox=x=0:y=637:w=720:h=6:color=0xC9A45C:t=fill,{LOOK}[v];[2:a]{afx}[a2]",
          "-map","[v]","-map","[a2]","-frames:v",str(n),"-ac","1","-c:v","libx264","-preset","fast","-crf","14","-c:a","pcm_s16le",out])
    else:
        v=f"setpts=(PTS-STARTPTS)/{sp},fps=30,scale=720:1280,{DEFL},{G[g]}"
        if g in("hero","end"): v+=","+push(720,1280,n,0.0012)
        v+=","+LOOK
        if i==0: v+=",fade=t=in:st=0:d=0.6"
        fc=f"[0:v]{v}[v0]"
        if g=="hero":  # soft white bloom instead of hard white flash
            fc+=(";[v0]split[x][y];[y]lutyuv=y=255:u=128:v=128[wh];"
                 "[x][wh]blend=all_expr='A*(1-max(0\\,0.45-T*1.5))+B*max(0\\,0.45-T*1.5)'[v0b]")
            vout="[v0b]"
        else: vout="[v0]"
        # real-time source audio (never time-stretched) so slow-mo has natural room tone
        run(["-ss",f"{src:.3f}","-i",SRC,"-filter_complex",fc+f";[0:a]{afx}[a0]","-map",vout,"-map","[a0]",
             "-frames:v",str(n),"-ac","1","-c:v","libx264","-preset","fast","-crf","14","-c:a","pcm_s16le",out])
    lst.write(f"file '{out}'\n"); print(f"{i:02d} {t0/30:6.3f}-{(t0+n)/30:6.3f}s {_}"); t0+=n
lst.close()
run(["-f","concat","-safe","0","-i","list2.txt","-c:v","libx264","-preset","fast","-crf","14","-c:a","pcm_s16le","cut2.mov"])
