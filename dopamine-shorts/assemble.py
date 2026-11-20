"""Join rendered shots with frame-filling colour dips (invisible portals), build the bump-synced soundtrack, mux to exactly 19.0 s.
usage: assemble.py <out.mp4> shot1.mp4:bed:dipcolor[:slow] ..."""
import sys, json, subprocess, os
out = sys.argv[1]; items = [a.split(':') for a in sys.argv[2:]]; parts, shots, t = [], [], 0.0
for i, it in enumerate(items):
    src, bedk, col = it[0], it[1], it[2]; slow = len(it) > 3
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src], capture_output=True, text=True).stdout)
    p = f"{out}.{i}.mp4"; prev = items[i-1][2] if i else items[-1][2]      # fade in from the previous shot's dip colour (first shot: from the last one's -> loop)
    vf = f"fade=in:st=0:d=0.14:color={prev},fade=out:st={d-0.14}:d=0.14:color={col}"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", vf, "-c:v", "libx264", "-crf", "15", "-preset", "medium", "-pix_fmt", "yuv420p", "-an", p], check=True)
    bumps = json.load(open(src + '.bumps.json')) if os.path.exists(src + '.bumps.json') else []
    shots.append({"t0": round(t, 3), "t1": round(t + d, 3), "bed": bedk, "bumps": bumps, "slow": slow}); t += d; parts.append(p)
open(out + '.list', 'w').write("".join(f"file '{os.path.abspath(p)}'\n" for p in parts)); json.dump({"dur": round(t, 3), "shots": shots}, open(out + '.tl.json', 'w'))
subprocess.run(["python3", "sfx2.py", out + '.wav', out + '.tl.json'], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", out + '.list', "-i", out + '.wav', "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-t", f"{t}", "-movflags", "+faststart", out], check=True)
for p in parts: os.remove(p)
print(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height,r_frame_rate", "-of", "csv=p=0", out], capture_output=True, text=True).stdout)
