import subprocess
SRC="/root/.claude/uploads/ee52e1aa-2485-56aa-89c7-ac031a1ae968/7a589f4b-copy_05059AA4-92B2-4266-8573-8943049F3456.mov"
SUN="eq=saturation=1.45:contrast=1.08:brightness=0.06:gamma=1.10,colorbalance=rs=0.10:gs=-0.02:bs=0.14:rm=0.06:bm=0.05:rh=0.14:gh=0.04:bh=-0.10"
BLOOM="format=gbrp,split[q1][q2];[q2]gblur=sigma=14[q3];[q1][q3]blend=all_mode=screen:all_opacity=0.32,format=yuv420p"
PAINT=("smartblur=lr=5:ls=1.0:lt=0,eq=saturation=1.5:contrast=1.1,format=gbrp,split[p1][p2];[p2]edgedetect=low=0.04:high=0.12,negate,erosion,format=gbrp[pe];"
       "[p1]lutrgb=r='val/56*56+20':g='val/56*56+10':b='val/56*56+20'[pp];[pp][pe]blend=all_mode=multiply,format=yuv420p")
def run(a): subprocess.run(["ffmpeg","-v","error","-y"]+a,check=True)
ENC=["-c:v","libx264","-preset","fast","-crf","14","-pix_fmt","yuv420p","-an"]
def live(out,src,n,sp=1.0,extra=""):
    zin=("scale=w='trunc(720*(1+0.15*pow(max(0\\,1-n/6)\\,2)))/2*2':h=-2:eval=frame,crop=720:1280")
    run(["-ss",f"{src:.3f}","-t",f"{n/30*sp+0.05:.3f}","-i",SRC,"-filter_complex",
         f"[0:v]setpts=(PTS-STARTPTS)/{sp},fps=30,scale=720:1280,deflicker=size=7:mode=pm,{SUN},{zin}{extra},{BLOOM}[v]",
         "-map","[v]","-frames:v",str(n)]+ENC+[out])
def freeze(out,src,n,crop=None):
    c=f",crop=720:640:0:{crop}" if crop is not None else ""
    run(["-ss",f"{src:.3f}","-i",SRC,"-filter_complex",
         f"[0:v]trim=end_frame=1,scale=720:1280{c},{SUN},{PAINT},loop={n}:1:0,setpts=N/30/TB,"
         f"scale=w='trunc(720*(1+0.0015*n))/2*2':h=-2:eval=frame,crop=720:ih,{BLOOM}[v]" if crop is None else
         f"[0:v]trim=end_frame=1,scale=720:1280{c},{SUN},{PAINT},loop={n}:1:0,setpts=N/30/TB[v]",
         "-map","[v]","-frames:v",str(n)]+ENC+[out])
parts=[]
def P(name,note): parts.append((name,note))
live("g00.mov",18.00,45,0.5); P("g00.mov","Opener: storefront, sunset grade + bloom (location title)")
live("g01a.mov",0.00,21); P("g01a.mov","THE CLIENT: live")
freeze("g01b.mov",0.70,39); P("g01b.mov","THE CLIENT: painted freeze-frame + name card")
for k,s in enumerate((3.00,4.40,6.20,8.00,14.30)): live(f"g02{k}.mov",s,15); P(f"g02{k}.mov",f"Montage {k+1} (HUD on)")
live("g03a.mov",31.00,15); P("g03a.mov","THE BARBER: live")
freeze("g03b.mov",31.50,45); P("g03b.mov","THE BARBER: painted freeze-frame + name card")
live("g04.mov",32.62,75,0.28); P("g04.mov","AFTER reveal, slow motion, five stars")
# loading-screen diptych: painted BEFORE / AFTER panels on the sunset background
freeze("pb.mov",0.30,45,240); freeze("pa.mov",32.80,45,300)
run(["-loop","1","-t","1.5","-i","sunset_bg.png","-i","pb.mov","-i","pa.mov","-filter_complex",
     "[0:v]fps=30,format=yuv420p[bg];[1:v]scale=640:568,pad=652:580:6:6:white[b];[2:v]scale=640:568,pad=652:580:6:6:white[a];"
     "[bg][b]overlay=34:50:shortest=1[t];[t][a]overlay=34:650:shortest=1,format=yuv420p[v]","-map","[v]","-frames:v","45"]+ENC+["g05.mov"])
P("g05.mov","Loading-screen diptych BEFORE/AFTER (painted)")
# end card: sunset gradient + retro striped sun
run(["-loop","1","-t","3","-i","sunset_bg.png","-loop","1","-t","3","-i","sun_mask.png","-f","lavfi","-i","color=c=0xFFF2A8:s=720x1280:d=3:r=30","-filter_complex",
     "[1:v]format=gray[m];[2:v][m]alphamerge[sun];[0:v]fps=30[bg];[bg][sun]overlay=0:0:shortest=1,"
     "scale=w='trunc(720*(1+0.10*pow(max(0\\,1-n/20)\\,2)))/2*2':h=-2:eval=frame,crop=720:1280,format=yuv420p[v]","-map","[v]","-frames:v","90"]+ENC+["g06.mov"])
P("g06.mov","End card: sunset + retro sun")
with open("list.txt","w") as f:
    for n,_ in parts: f.write(f"file '{n}'\n")
run(["-f","concat","-safe","0","-i","list.txt","-c:v","libx264","-preset","fast","-crf","14","gtacut.mov"])
for n,note in parts: print(n,note)
