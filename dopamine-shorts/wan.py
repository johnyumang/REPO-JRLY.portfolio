"""Image-to-video on the Wan 2.2 Space. usage: wan.py <still.jpg> <out.mp4> "<motion prompt>" [seed] [seconds] [steps]"""
import json, sys, subprocess, time, re
H = "https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space/gradio_api"
NEG = ("text, letters, logo, watermark, subtitles, static, still image, frozen, blurry, low quality, jpeg artifacts, morphing, melting, warping, "
       "distorted, deformed, extra limbs, extra fingers, bad hands, bad face, flicker, cartoon, cgi, slow motion stutter, walking backwards")
def sh(*a): return subprocess.run(a, capture_output=True, text=True, timeout=900).stdout
def run(img, out, prompt, seed=42, secs=4.0, steps=6):
    up = json.loads(sh("curl", "-s", "-F", f"files=@{img}", H + "/upload"))[0]
    body = {"data": [{"path": up, "meta": {"_type": "gradio.FileData"}}, prompt, steps, NEG, secs, 1, 1, seed, False]}
    ev = json.loads(sh("curl", "-s", "-H", "Content-Type: application/json", "-d", json.dumps(body), H + "/call/generate_video"))["event_id"]
    t = time.time(); txt = sh("curl", "-sN", f"{H}/call/generate_video/{ev}")
    if "event: complete" not in txt: print("FAIL %.0fs" % (time.time() - t), txt[-600:]); return False
    data = txt.split("event: complete")[1].split("data:", 1)[1].strip().splitlines()[0]
    url = re.search(r'"url":\s*"([^"]+)"', data).group(1)
    sh("curl", "-s", "-o", out, url); print("ok %.0fs" % (time.time() - t), out, flush=True); return True
if __name__ == '__main__':
    a = sys.argv; run(a[1], a[2], a[3], int(a[4]) if len(a) > 4 else 42, float(a[5]) if len(a) > 5 else 4.0, int(a[6]) if len(a) > 6 else 6)
