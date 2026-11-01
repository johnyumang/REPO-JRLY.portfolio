import subprocess
SRC="/root/.claude/uploads/ee52e1aa-2485-56aa-89c7-ac031a1ae968/7a589f4b-copy_05059AA4-92B2-4266-8573-8943049F3456.mov"
CLEAN="eq=saturation=1.25:contrast=1.06:brightness=0.04:gamma=1.06,colorbalance=rs=0.02:bs=-0.01,unsharp=5:5:0.6"
BEF="eq=saturation=0.35:contrast=1.04:brightness=0.03"
def zin(k=5,a=0.18):  # smooth incoming zoom settle + 2-frame blur
    return (f"scale=w='trunc(720*(1+{a}*pow(max(0\\,1-n/{k})\\,2)))/2*2':h=-2:eval=frame,crop=720:1280,"
            f"avgblur=sizeX=7:sizeY=7:enable='lt(n\\,2)'")
# (frames, src, speed, grade, extra, note)
EDL=[(30,32.62,0.5,"clean","hook","HOOK: the result first (tight on hair)"),
     (15,31.50,-2.0,"clean","rewind","Rewind: walk-through reversed at 2x"),
     (45,0.00,1.0,"before","","BEFORE: long hair, caped"),
     (15,3.00,1,"clean","","Barber pole"),(15,4.40,1,"clean","","Scissors up"),
     (15,6.20,1,"clean","","Comb + shears"),(15,8.00,1,"clean","","Shaping"),
     (15,9.00,1,"clean","","Over-shoulder"),(15,13.00,1,"clean","","Wide cut"),
     (15,14.30,1,"clean","","Clipper"),(15,31.00,1,"clean","","Barber smiles"),
     (60,32.62,0.28,"clean","reveal","AFTER reveal, slow motion"),
     (75,None,None,"split","","BEFORE/AFTER split, AFTER slides in"),
     (105,18.00,0.5,"cta","","CTA card over bright blurred storefront")]
assert sum(e[0] for e in EDL)==450
def run(a): subprocess.run(["ffmpeg","-v","error","-y"]+a,check=True)
ENC=["-c:v","libx264","-preset","fast","-crf","14","-pix_fmt","yuv420p","-an"]
lst=open("list.txt","w"); t0=0
for i,(n,src,sp,g,ex,note) in enumerate(EDL):
    out=f"m{i:02d}.mov"
    if g=="split":
        run(["-ss","0.30","-i",SRC,"-ss","32.80","-i",SRC,"-f","lavfi","-i","color=c=white:s=720x1280:r=30","-filter_complex",
          f"[0:v]trim=end_frame=1,scale=720:1280,crop=720:640:0:240,{BEF},loop={n}:1:0,setpts=N/30/TB[a];"
          f"[1:v]trim=end_frame=1,scale=720:1280,crop=720:640:0:300,{CLEAN},loop={n}:1:0,setpts=N/30/TB[b];"
          f"[2:v][a]overlay=0:0:shortest=1[t];[t][b]overlay=x='max(0\\,720-720*min(1\\,t/0.35)*(2-min(1\\,t/0.35)))':y=640:shortest=1,"
          f"drawbox=x=0:y=636:w=720:h=8:color=white:t=fill,format=yuv420p[v]","-map","[v]","-frames:v",str(n)]+ENC+[out])
    elif g=="cta":
        run(["-ss",str(src),"-i",SRC,"-filter_complex",
          f"[0:v]setpts=(PTS-STARTPTS)/{sp},fps=30,scale=720:1280,{CLEAN},eq=brightness=0.30:saturation=1.3:gamma=1.5,gblur=sigma=18,drawbox=x=0:y=0:w=iw:h=ih:color=0xFFF4C2@0.45:t=fill,"
          f"drawbox=x=50:y=302:w=640:h=700:color=black@0.12:t=fill,drawbox=x=40:y=290:w=640:h=700:color=white@0.97:t=fill,"
          f"{zin(8,0.12)},format=yuv420p[v]","-map","[v]","-frames:v",str(n)]+ENC+[out])
    else:
        rev = sp<0
        v=f"setpts=(PTS-STARTPTS)/{abs(sp)},fps=30,scale=720:1280,deflicker=size=7:mode=pm,{CLEAN if g=='clean' else BEF}"
        if ex=="hook": v+=",scale=1008:1792,crop=720:1280:144:420"       # tight on the haircut (zoom 1.4)
        if rev: v="reverse,"+v+",rgbashift=rh=-6:bh=6,tmix=frames=3"
        if ex in("","reveal"): v+=","+zin()
        if ex=="reveal": v+=",drawbox=x=0:y=0:w=iw:h=ih:color=white@0.5:t=fill:enable='lt(n\\,2)'"
        v+=",format=yuv420p"
        dur=n/30*abs(sp)
        run(["-ss",f"{src:.3f}","-t",f"{dur+0.05:.3f}","-i",SRC,"-vf",v,"-frames:v",str(n)]+ENC+[out])
    lst.write(f"file '{out}'\n"); print(f"{i:02d} {t0/30:6.3f}-{(t0+n)/30:6.3f} {note}"); t0+=n
lst.close()
run(["-f","concat","-safe","0","-i","list.txt","-c:v","libx264","-preset","fast","-crf","14","moderncut.mov"])
