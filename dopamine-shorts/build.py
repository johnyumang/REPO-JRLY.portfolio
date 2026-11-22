"""Assemble one 19.0 s 1080x1920 short from clips/stills + flash transitions. usage: build.py <spec.json> <out.mp4>
spec: {"segs":[{"src":"clips/x.mp4","start":0.0,"dur":2.5} | {"still":"stills/x.jpg","dur":2.6}], "flash":"#c9a0ff"}"""
import json, sys, subprocess, os
spec = json.load(open(sys.argv[1])); out = sys.argv[2]; tmp = out + '.parts'; os.makedirs(tmp, exist_ok=True)
FPS = 32; VF = "scale=1080:1920:flags=lanczos,unsharp=5:5:0.6,setsar=1"
parts = []
for i, s in enumerate(spec['segs']):
    p = f"{tmp}/{i:02d}.mp4"; d = s['dur']; fl = spec.get('flash')
    fade = f",fade=in:st=0:d=0.16:color={fl}" if fl and i > 0 else ""
    if 'src' in s:
        sp = s.get('speed', 1.0)
        vf = f"trim=start={s.get('start',0)},setpts=(PTS-STARTPTS)/{sp},minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:vsbmc=1,{VF},trim=duration={d}{fade},format=yuv420p"
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", s['src'], "-vf", vf]
    else:   # still: accelerating push-in with a slight handheld shake
        n = int(round(d * FPS))
        vf = (f"scale=2160:3780:flags=lanczos,zoompan=z='1+0.45*pow(on/{n},1.6)':x='iw/2-(iw/zoom/2)+6*sin(on*1.7)':y='ih/2-(ih/zoom/2)+6*cos(on*1.3)':d={n}:s=1080x1920:fps={FPS},"
              f"tmix=frames=3,unsharp=5:5:0.5,setsar=1{fade},format=yuv420p")
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", s['still'], "-vf", vf, "-frames:v", str(n)]
    subprocess.run(cmd + ["-r", str(FPS), "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-an", p], check=True)
    parts.append(p)
open(f"{tmp}/list.txt", "w").write("".join(f"file '{os.path.abspath(p)}'\n" for p in parts))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{tmp}/list.txt", "-c", "copy", out + '.silent.mp4'], check=True)
print(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out + '.silent.mp4'], capture_output=True, text=True).stdout)
