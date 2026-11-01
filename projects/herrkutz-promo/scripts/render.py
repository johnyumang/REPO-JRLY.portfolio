import subprocess,os
from edl import EDL
SRC="/root/.claude/uploads/ee52e1aa-2485-56aa-89c7-ac031a1ae968/7a589f4b-copy_05059AA4-92B2-4266-8573-8943049F3456.mov"
PUNCH={0,4,6,13,22,27}  # punch-in zoom on these segment indices
lst=open("list.txt","w")
for i,(st,d,src,sp,lab) in enumerate(EDL):
    srcdur=d*sp; out=f"seg{i:02d}.mp4"
    v=f"setpts=(PTS-STARTPTS)/{sp},scale=720:1280,fps=30"
    if i in PUNCH: v+=",scale=iw*1.12:ih*1.12,crop=720:1280"
    if i==27: v+=",eq=contrast=1.08:saturation=1.15"
    a=f"asetpts=PTS-STARTPTS"+(f",atempo={sp}" if sp!=1 else "")+f",aresample=44100,apad,atrim=0:{d}"
    subprocess.run(["ffmpeg","-v","error","-y","-ss",str(src),"-t",str(srcdur),"-i",SRC,
      "-vf",v+f",trim=0:{d},setpts=PTS-STARTPTS","-af",a,"-frames:v",str(round(d*30)),
      "-c:v","libx264","-preset","fast","-crf","18","-c:a","pcm_s16le","-ac","1",out.replace(".mp4",".mov")],check=True)
    lst.write(f"file '{out.replace('.mp4','.mov')}'\n")
lst.close()
subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i","list.txt","-c","copy","cut.mov"],check=True)
