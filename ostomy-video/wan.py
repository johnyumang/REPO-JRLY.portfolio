#!/usr/bin/env python3
"""One image-to-video clip on the free Wan 2.2 Space (github.com/Wan-Video/Wan2.2), with the Space's real error text.
usage: wan.py STILL OUT.mp4 "PROMPT" [--seconds 3.5] [--steps 6] [--seed 7] [--end LAST_STILL]
Env WAN_SPACE: another Space with the same interface, e.g. https://upsampler-wan-2-2-14b-image-to-video.hf.space
(same model; also takes --end, a last frame; called without an account it runs on the visitor quota of this machine).

Free ZeroGPU quota is counted in GPU seconds. The Space asks for 1.5 x (10 + steps * 15 * (frames*480*832 / (81*832*624))**1.5)
seconds, frames = 1 + 16 * seconds: 68 s for the default 3.5 s / 6 steps, 31 s for 2.0 s / 4 steps. When the quota is
used up the Space says how long until it refills; this script prints that. A tall still is centre-cropped to 480:832
and resized to 480x832; the clip is 16 fps."""
import json, os, subprocess, sys, uuid
H = os.environ.get('WAN_SPACE', 'https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space')
def hdr(): return ['-H', 'Authorization: Bearer ' + os.environ['HF_TOKEN']] if os.environ.get('HF_TOKEN') else []
def curl(*a, t=900): return subprocess.run(['curl', '-sS', *hdr(), *a], capture_output=True, text=True, timeout=t)
def main():
    a = sys.argv[1:]
    if len(a) < 3: sys.exit(__doc__)
    g = lambda f, d: type(d)(a[a.index(f) + 1]) if f in a else d
    img, out, prompt = a[0], a[1], a[2]
    secs, steps, seed = g('--seconds', 3.5), g('--steps', 6), g('--seed', 7)
    frames = 1 + round(secs * 16)
    print('asks for about %.0f GPU seconds' % (1.5 * (10 + steps * 15 * (frames * 480 * 832 / (81 * 832 * 624)) ** 1.5)), flush=True)
    path = json.loads(curl('-F', 'files=@' + img, H + '/gradio_api/upload').stdout)[0]
    info = json.loads(curl(H + '/gradio_api/info').stdout)['named_endpoints']['/generate_video']['parameters']
    extra = []
    if any(q.get('parameter_name') == 'end_image' for q in info):
        end = g('--end', '')
        extra = [{"path": json.loads(curl('-F', 'files=@' + end, H + '/gradio_api/upload').stdout)[0], "meta": {"_type": "gradio.FileData"}} if end else None]
    cfg = json.loads(curl(H + '/config').stdout)
    fn = [d for d in cfg['dependencies'] if d.get('api_name') == 'generate_video'][0]['id']
    sh = uuid.uuid4().hex[:10]
    body = {"data": [{"path": path, "meta": {"_type": "gradio.FileData"}}, prompt, steps, "", secs, 1, 1, seed, False, *extra],
            "fn_index": fn, "session_hash": sh, "event_data": None, "trigger_id": None}
    curl('-H', 'Content-Type: application/json', '-d', json.dumps(body), H + '/gradio_api/queue/join')
    r = curl('-N', H + '/gradio_api/queue/data?session_hash=' + sh)
    for line in r.stdout.splitlines():
        if not line.startswith('data:'): continue
        d = json.loads(line[5:])
        if d.get('msg') != 'process_completed': continue
        if not d.get('success'): sys.exit('refused: ' + str((d.get('output') or {}).get('error')))
        v = d['output']['data'][0]; v = v.get('video', v)
        url = v.get('url') or H + '/gradio_api/file=' + v['path']
        subprocess.run(['curl', '-sS', '-L', *hdr(), '-o', out, url], check=True, timeout=600)
        print('ok', out); return
    sys.exit('no answer: ' + r.stdout[-300:])
if __name__ == '__main__': main()
