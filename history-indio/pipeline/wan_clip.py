#!/usr/bin/env python3
"""Real motion for one still: image-to-video on a free Hugging Face Space (Wan 2.2), about 3.5 s, 480x832, 16 fps.
usage: wan_clip.py <still.jpg|png> <out.mp4> "<what moves, in plain words>" [--seed N] [--neg "<what must not appear>"]
Free: it runs on the Space's shared graphics card under your Hugging Face account's free daily quota (about 6 clips a
day; when it is used up the Space refuses until the next day, so wait, do not pay). Needs a free Hugging Face token
with read access in the environment: export HF_TOKEN=...   (never in a file).
Play the clip in an episode with "clip": "<file>" on that shot in shots_fx.json (build_anime.py)."""
import json, os, sys, subprocess, urllib.request
H = os.environ.get('WAN_SPACE', 'https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space') + '/gradio_api'
NEG = 'text, letters, watermark, extra limbs, extra fingers, deformed hands, face change, morphing, flicker, blur, low quality'
def hdr(): return ['-H', 'Authorization: Bearer ' + os.environ['HF_TOKEN']] if os.environ.get('HF_TOKEN') else []
def curl(*a): return subprocess.run(['curl', '-sS', '--fail-with-body', *hdr(), *a], capture_output=True, text=True, timeout=900)
def main():
    a = sys.argv[1:]
    if len(a) < 3: sys.exit(__doc__)
    img, out, prompt = a[0], a[1], a[2]
    seed = int(a[a.index('--seed') + 1]) if '--seed' in a else 7
    neg = a[a.index('--neg') + 1] if '--neg' in a else NEG
    r = curl('-F', 'files=@' + img, H + '/upload')
    if r.returncode: sys.exit('upload failed: ' + (r.stdout or r.stderr)[:300])
    path = json.loads(r.stdout)[0]
    body = {"data": [{"path": path, "meta": {"_type": "gradio.FileData"}}, prompt, 6, neg, 3.5, 1, 1, seed, False]}   # steps 6, 3.5 s, guidance 1 / 1, fixed seed
    r = curl('-H', 'Content-Type: application/json', '-d', json.dumps(body), H + '/call/generate_video')
    if r.returncode: sys.exit('start failed: ' + (r.stdout or r.stderr)[:300])
    ev = json.loads(r.stdout)['event_id']
    r = curl('-N', H + '/call/generate_video/' + ev)
    url = None; last = ''
    for line in r.stdout.splitlines():
        if line.startswith('event:'): last = line[6:].strip()
        if line.startswith('data:') and last == 'complete':
            d = json.loads(line[5:]); v = d[0].get('video', d[0]) if isinstance(d[0], dict) else {}
            url = v.get('url') or (H + '/file=' + v['path'] if v.get('path') else None)
        if line.startswith('data:') and last == 'error': sys.exit('the Space refused (quota used up for today, or busy): ' + line[5:][:300])
    if not url: sys.exit('no video came back: ' + r.stdout[-300:])
    r = subprocess.run(['curl', '-sS', '-L', *hdr(), '-o', out, url], capture_output=True, text=True, timeout=600)
    print('ok', out) if not r.returncode and os.path.getsize(out) > 10000 else sys.exit('download failed')
if __name__ == '__main__': main()
