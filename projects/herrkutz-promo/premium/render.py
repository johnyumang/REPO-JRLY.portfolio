import subprocess
from edl import EDL
SRC="/root/.claude/uploads/ee52e1aa-2485-56aa-89c7-ac031a1ae968/7a589f4b-copy_05059AA4-92B2-4266-8573-8943049F3456.mov"
G={"before":"eq=saturation=0.18:contrast=1.06:brightness=-0.02,colorbalance=bs=0.06:bm=0.04:rh=-0.03",
   "warm":"eq=contrast=1.10:saturation=1.08:gamma=0.96,colorbalance=rs=0.05:gs=0.01:bs=-0.04:rh=0.04:bh=-0.05",
   "hero":"eq=contrast=1.14:saturation=1.15:gamma=0.95,colorbalance=rs=0.06:bs=-0.04:rh=0.05:bh=-0.05",
   "end":"eq=contrast=1.12:saturation=1.0:brightness=-0.10:gamma=0.92,colorbalance=rs=0.05:bs=-0.03"}
LOOK="vignette=PI/4.5,noise=alls=5:allf=t,format=yuv420p"
def run(a): subprocess.run(["ffmpeg","-v","error","-y"]+a,check=True)
lst=open("list.txt","w")
for i,(st,d,src,sp,g,_) in enumerate(EDL):
    out=f"s{i:02d}.mov"; n=round(d*30)
    if g=="split":
        # two freeze frames, slow push-in each, stacked; gold divider
        run(["-ss","0.30","-i",SRC,"-ss","32.80","-i",SRC,"-f","lavfi","-t",str(d),"-i","anullsrc=r=44100:cl=mono",
          "-filter_complex",
          f"[0:v]trim=end_frame=1,scale=720:1280,crop=720:640:0:200,{G['before']},loop={n}:1:0,setpts=N/30/TB,"
          f"zoompan=z='1+0.0009*on':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=720x640:fps=30[a];"
          f"[1:v]trim=end_frame=1,scale=720:1280,crop=720:640:0:520,{G['hero']},loop={n}:1:0,setpts=N/30/TB,"
          f"zoompan=z='1+0.0009*on':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=720x640:fps=30[b];"
          f"[a][b]vstack,drawbox=x=0:y=637:w=720:h=6:color=0xC9A45C:t=fill,{LOOK}[v]",
          "-map","[v]","-map","2:a","-frames:v",str(n),"-c:v","libx264","-preset","fast","-crf","16","-c:a","pcm_s16le",out])
    else:
        v=f"setpts=(PTS-STARTPTS)/{sp},fps=30,scale=720:1280,{G[g]}"
        if g in("hero","end"):  # slow push-in
            v+=f",scale=820:1458,zoompan=z='1+0.0012*on':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=720x1280:fps=30"
        v+=","+LOOK
        if i==0: v+=",fade=t=in:st=0:d=0.6"
        if i==13: v+=",fade=t=in:st=0:d=0.25:color=white"
        a="asetpts=PTS-STARTPTS"+(f",atempo={max(sp,0.5)}" if sp!=1 else "")+f",aresample=44100,apad,atrim=0:{d}"
        run(["-ss",str(src),"-t",str(d*sp+0.1),"-i",SRC,"-vf",v,"-af",a,"-frames:v",str(n),"-ac","1",
             "-c:v","libx264","-preset","fast","-crf","16","-c:a","pcm_s16le",out])
    lst.write(f"file '{out}'\n")
lst.close()
run(["-f","concat","-safe","0","-i","list.txt","-c","copy","cut.mov"])
