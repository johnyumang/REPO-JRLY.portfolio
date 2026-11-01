import subprocess
SRC="/root/.claude/uploads/ee52e1aa-2485-56aa-89c7-ac031a1ae968/7a589f4b-copy_05059AA4-92B2-4266-8573-8943049F3456.mov"
VIVID="eq=saturation=1.65:contrast=1.12:brightness=0.06:gamma=1.12,colorbalance=rs=0.04:bs=0.02:rh=0.03,unsharp=5:5:0.8"
BEFORE="eq=saturation=0.0:contrast=1.25:brightness=0.08:gamma=1.15"   # bright xerox b/w, not dark
# hit = RGB split + shake decaying over first frames of every shot
def hit(n):
    return (f"scale=780:1386,crop=720:1280:x='(iw-ow)/2+14*exp(-n/3)*sin(n*9)':y='(ih-oh)/2+10*exp(-n/3)*cos(n*7)',"
            f"rgbashift=rh=-10:bh=10:enable='lt(n\\,3)'")
# (frames, kind, src, speed, extra, note)
EDL=[
 (30,"live",0.30,1.0,"before","HOOK: BEFORE, stop-motion 8fps xerox b/w"),
 (10,"ai","clippers","", "","AI B-roll: clippers paint explosion (Canva AI)"),
 (30,"live",3.00,1.0,"","Barber pole"),
 (10,"ai","razor","","","AI B-roll: razor + scissors on hot pink (Canva AI)"),
 (20,"live",4.40,1.0,"","Scissors up"),
 (20,"live",6.20,1.0,"","Comb + shears"),
 (10,"ai","hair","","","AI B-roll: flying hair clippings (Canva AI)"),
 (20,"live",14.00,1.0,"","Clipper at nape"),
 (10,"live",32.00,1.0,"punch","Push toward client, zoom punch"),
 (90,"live",32.62,0.28,"reveal","AFTER reveal, half speed, vivid"),
 (90,"split",None,None,"","Split BEFORE/AFTER, torn divider"),
 (10,"ai","pole","","","AI B-roll: graffiti barber pole (Canva AI)"),
 (100,"end",18.00,0.5,"","End card: duotone storefront, ransom-note type"),
]
assert sum(e[0] for e in EDL)==450
def run(a): subprocess.run(["ffmpeg","-v","error","-y"]+a,check=True)
ENC=["-c:v","libx264","-preset","fast","-crf","14","-pix_fmt","yuv420p","-an"]
lst=open("list.txt","w"); t0=0
for i,(n,kind,src,sp,extra,note) in enumerate(EDL):
    out=f"p{i:02d}.mov"
    if kind=="ai":   # xerox/halftone flash insert from the AI still; slow push + shake
        vf=(f"loop={n}:1:0,setpts=N/30/TB,scale=720:1280:flags=bicubic,"
            f"lutrgb=r='val/48*48':g='val/48*48':b='val/48*48',eq=saturation=1.4:contrast=1.1,"
            f"scale=w='trunc(760+6*n)/2*2':h=-2:eval=frame,crop=720:1280,{hit(n)},noise=alls=14:allf=t+u,fps=30")
        run(["-i",f"ai/{src}.png","-vf",vf,"-frames:v",str(n)]+ENC+[out])
    elif kind=="split":
        run(["-ss","0.30","-i",SRC,"-ss","32.80","-i",SRC,"-filter_complex",
          f"[0:v]trim=end_frame=1,scale=720:1280,crop=720:640:0:240,{BEFORE},loop={n}:1:0,setpts=N/30/TB[a];"
          f"[1:v]trim=end_frame=1,scale=720:1280,crop=720:640:0:300,{VIVID},loop={n}:1:0,setpts=N/30/TB[b];"
          f"[a][b]vstack,"
          # torn-paper divider: white band + jagged yellow edge made of small offset boxes
          + ",".join(f"drawbox=x={k*40}:y={622+((k*37)%13)}:w=40:h={22+((k*23)%11)}:color=white:t=fill" for k in range(18))
          + ",drawbox=x=0:y=636:w=720:h=8:color=0xFFE100:t=fill,"
          f"scale=760:1352,crop=720:1280:x='(iw-ow)/2+12*exp(-n/3)*sin(n*9)':y='(ih-oh)/2',format=yuv420p[v]",
          "-map","[v]","-frames:v",str(n)]+ENC+[out])
    else:
        v=f"setpts=(PTS-STARTPTS)/{sp},fps=30,scale=720:1280,deflicker=size=7:mode=pm,"
        if extra=="before": v+=f"{BEFORE},fps=8,fps=30,"
        elif kind=="end":
            # bright duotone: shadows hot pink -> highlights acid yellow (no dark end card)
            v+="format=gray,eq=brightness=0.10:contrast=1.2,format=rgb24,lutrgb=r=255:g='45+val*0.82':b='150-val*0.55',"
        else: v+=VIVID+","
        if extra=="punch":
            v+="scale=w='trunc(720*(1+0.05*n))/2*2':h=-2:eval=frame,crop=720:1280,avgblur=sizeX=6:enable='gte(n\\,6)',"
        v+=hit(0) if kind=="end" else hit(0)
        if extra=="reveal":   # stamp-in: 2 frames pink flash then 2 yellow (bright, max 2 flashes)
            v+=",drawbox=x=0:y=0:w=iw:h=ih:color=0xFF2D8C@0.55:t=fill:enable='lt(n\\,2)',drawbox=x=0:y=0:w=iw:h=ih:color=0xFFE100@0.45:t=fill:enable='between(n\\,2\\,3)'"
        v+=",noise=alls=6:allf=t,format=yuv420p"
        run(["-ss",f"{src:.3f}","-i",SRC,"-vf",v,"-frames:v",str(n)]+ENC+[out])
    lst.write(f"file '{out}'\n"); print(f"{i:02d} {t0/30:6.3f}-{(t0+n)/30:6.3f} {note}"); t0+=n
lst.close()
run(["-f","concat","-safe","0","-i","list.txt","-c:v","libx264","-preset","fast","-crf","14","punkcut.mov"])
