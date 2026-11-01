import subprocess
SRC="/root/.claude/uploads/ee52e1aa-2485-56aa-89c7-ac031a1ae968/7a589f4b-copy_05059AA4-92B2-4266-8573-8943049F3456.mov"
G={"before":"eq=saturation=0.18:contrast=1.06:brightness=-0.02,colorbalance=bs=0.06:bm=0.04:rh=-0.03",
   "warm":"eq=contrast=1.10:saturation=1.08:gamma=0.96,colorbalance=rs=0.05:gs=0.01:bs=-0.04:rh=0.04:bh=-0.05",
   "hero":"eq=contrast=1.14:saturation=1.15:gamma=0.95,colorbalance=rs=0.06:bs=-0.04:rh=0.05:bh=-0.05",
   "end":"eq=contrast=1.12:saturation=1.0:brightness=-0.10:gamma=0.92,colorbalance=rs=0.05:bs=-0.03"}
LOOK="vignette=PI/4.5,noise=alls=5:allf=t,format=yuv420p"
# (frames, src, speed, grade, push_rate, zoom_out_in(K,A) or None, punch_out(bool), note)
EDL=[
 (45, 0.00,0.80,"before",0.0015,None,   True, "HOOK - BEFORE: long hair, caped; zoom-through out"),
 (30, 3.00,1.0, "warm",  0.0,   (6,.35),False,"Barber pole; zoom-out settle in"),
 (30, 4.40,1.0, "warm",  0.0008,None,   False,"Scissors up, HERRKUTZ chair"),
 (30, 6.20,1.0, "warm",  0.0008,None,   False,"Comb + shears at crown"),
 (30,14.00,1.0, "warm",  0.0008,None,   False,"Clipper at the nape"),
 (15,32.00,1.0, "warm",  0.004, None,   True, "Push toward client; zoom-through out"),
 (75,32.62,0.30,"hero",  0.0006,(22,.30),False,"AFTER reveal, slow motion, zoom-out reveal"),
 (105,None,None,"split", 0,     None,   False,"Split BEFORE / AFTER"),
 (90,18.00,0.50,"end",   0.0008,(30,.25),False,"Storefront end card, zoom-out reveal + address"),
]
assert sum(e[0] for e in EDL)==450
def run(a): subprocess.run(["ffmpeg","-v","error","-y"]+a,check=True)
def zexpr(n,rate,zo,punch):
    z=f"1+{rate}*on"
    if zo: K,A=zo; z+=f"+if(lt(on\\,{K})\\,{A}*pow(1-on/{K}\\,2)\\,0)"
    if punch: z+=f"+if(gte(on\\,{n-6})\\,0.40*pow((on-{n-6})/5\\,2)\\,0)"
    return z
def zp(w,h,z): return (f"scale={w*2}:{h*2}:flags=bicubic,zoompan=z='{z}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={w*2}x{h*2}:fps=30,"
                       f"scale={w}:{h}:flags=lanczos")
lst=open("list.txt","w"); t0=0
for i,(n,src,sp,g,rate,zo,punch,note) in enumerate(EDL):
    d=n/30; out=f"c{i:02d}.mov"
    blur=[]
    if zo: blur.append(f"lt(n\\,4)")
    if punch: blur.append(f"gte(n\\,{n-4})")
    bl=f",avgblur=sizeX=9:sizeY=9:enable='{'+'.join(blur)}'" if blur else ""
    if g=="split":
        run(["-ss","0.30","-i",SRC,"-ss","32.80","-i",SRC,"-filter_complex",
          f"[0:v]trim=end_frame=1,scale=720:1280,crop=720:640:0:200,{G['before']},loop={n}:1:0,setpts=N/30/TB,{zp(720,640,'1+0.001*on')}[a];"
          f"[1:v]trim=end_frame=1,scale=720:1280,crop=720:640:0:520,{G['hero']},loop={n}:1:0,setpts=N/30/TB,{zp(720,640,'1+0.001*on')}[b];"
          f"[a][b]vstack,drawbox=x=0:y=637:w=720:h=6:color=0xC9A45C:t=fill,{LOOK}[v]",
          "-map","[v]","-frames:v",str(n),"-an","-c:v","libx264","-preset","fast","-crf","14",out])
    else:
        v=f"setpts=(PTS-STARTPTS)/{sp},fps=30,scale=720:1280,deflicker=size=7:mode=pm,{G[g]},{zp(720,1280,zexpr(n,rate,zo,punch))}{bl},{LOOK}"
        if g=="hero":
            v+=(",split[x][y];[y]lutyuv=y=255:u=128:v=128[wh];[x][wh]blend=all_expr='A*(1-max(0\\,0.40-T*1.4))+B*max(0\\,0.40-T*1.4)'")
        run(["-ss",f"{src:.3f}","-i",SRC,"-filter_complex",f"[0:v]{v}[v]","-map","[v]","-frames:v",str(n),"-an",
             "-c:v","libx264","-preset","fast","-crf","14",out])
    lst.write(f"file '{out}'\n"); print(f"{i} {t0/30:6.3f}-{(t0+n)/30:6.3f} {note}"); t0+=n
lst.close()
run(["-f","concat","-safe","0","-i","list.txt","-c:v","libx264","-preset","fast","-crf","14","cut15.mov"])
# procedural light layers (generated here, no stock assets)
run(["-f","lavfi","-i","color=c=black:s=90x160:r=30:d=1.4","-vf",
  "format=gbrp,geq=r='255*exp(-(pow(X-W*(0.1+0.7*T),2)+pow(Y-H*(0.25+0.25*T),2))/(W*W*0.10))*sin(PI*min(1\\,T/1.4))':"
  "g='150*exp(-(pow(X-W*(0.1+0.7*T),2)+pow(Y-H*(0.25+0.25*T),2))/(W*W*0.10))*sin(PI*min(1\\,T/1.4))':"
  "b='40*exp(-(pow(X-W*(0.1+0.7*T),2)+pow(Y-H*(0.25+0.25*T),2))/(W*W*0.10))*sin(PI*min(1\\,T/1.4))',scale=720:1280,gblur=sigma=20",
  "-c:v","libx264rgb","-crf","10","leak.mkv"])
run(["-f","lavfi","-i","color=c=black:s=180x320:r=30:d=0.9","-vf",
  "format=gbrp,geq=r='230*exp(-pow(X+0.45*Y-(W*2.0)*(T/0.9)+W*0.3\\,2)/(W*W*0.006))':"
  "g='195*exp(-pow(X+0.45*Y-(W*2.0)*(T/0.9)+W*0.3\\,2)/(W*W*0.006))':"
  "b='120*exp(-pow(X+0.45*Y-(W*2.0)*(T/0.9)+W*0.3\\,2)/(W*W*0.006))',scale=720:1280,gblur=sigma=6",
  "-c:v","libx264rgb","-crf","10","sweep.mkv"])
