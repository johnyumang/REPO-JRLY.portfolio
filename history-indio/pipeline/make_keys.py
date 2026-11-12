#!/usr/bin/env python3
"""Make an episode's keyframes from key_prompts.json with the shot rules (one plate per location, character on
white, composite). Free NVIDIA FLUX.2 klein only. Existing files are kept, so Figma-made plates/characters dropped
into plates/ chars/ full/ win. usage: make_keys.py videos/<slug> [--only name,name] [--redo name,name]
key_prompts.json: {"style","white","plates":{n:prompt},"chars":{n:prompt},"full":{n:prompt},
 "shots":{"NN":{"char":n,"plate":n,"x":0-1,"y":0-1,"s":crop scale,"blur":px} | {"full":n} | {"plate":n}}}"""
import json, os, sys, time, zlib, cv2, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nvidia_still, composite_shot
v = sys.argv[1]; K = json.load(open(f'{v}/key_prompts.json'))
arg = lambda f: sys.argv[sys.argv.index(f) + 1].split(',') if f in sys.argv else []
only, redo = arg('--only'), arg('--redo'); END = ' Vertical 9:16. No text, no letters, no logos, no watermarks.'
def green_cutout(im):
    f = im.astype(np.float32); bl, g, r = f[..., 0], f[..., 1], f[..., 2]
    m = ((g > 90) & (g > r * 1.25) & (g > bl * 1.25)).astype(np.uint8) * 255
    m = cv2.dilate(m, np.ones((5, 5), np.uint8)); a = (255 - cv2.GaussianBlur(m, (5, 5), 0)).astype(np.float32) / 255
    im[..., 1] = np.minimum(g, np.maximum(r, bl) * 1.05).astype(np.uint8)                    # remove green spill (in place)
    return a
def find(kind, n):
    for e in ('png', 'jpg'):
        if os.path.exists(f'{v}/{kind}/{n}.{e}'): return f'{v}/{kind}/{n}.{e}'
def gen(kind, n):
    p = find(kind, n)
    if p and n not in redo: return p
    if only and n not in only: return p
    os.makedirs(f'{v}/{kind}', exist_ok=True); out = f'{v}/{kind}/{n}.jpg'
    if kind == 'chars': prompt = K['white'] + K[kind][n] + ' ' + K['style'] + END          # subject first: the free model follows the start of the prompt best
    else: prompt = K['style'] + ('Background art only, no people, no animals: ' if kind == 'plates' else '') + K[kind][n] + END
    seed = zlib.crc32(n.encode()) % 9999 + (len(redo) and n in redo) * int.from_bytes(os.urandom(2), 'big')
    for t in range(6):                                                    # the free endpoint sometimes answers 504 or with no image
        try:
            if nvidia_still.call('black-forest-labs/flux.2-klein-4b', {'prompt': prompt, 'width': 768, 'height': 1344, 'seed': seed + t, 'steps': 4}, out) and cv2.imread(out) is not None: return out
        except Exception as e: print(n, 'failed:', str(e)[:120])
        if os.path.exists(out) and cv2.imread(out) is None: os.remove(out)
        time.sleep(4 * (t + 1))
for kind in ('plates', 'chars', 'full'):
    for n in K.get(kind, {}): gen(kind, n)
os.makedirs(f'{v}/keys', exist_ok=True)
for i, s in K['shots'].items():
    out = f'{v}/keys/k{int(i):02d}.png'
    if 'char' in s:
        c, p = find('chars', s['char']), find('plates', s['plate'])
        if not (c and p): print('missing', i, s); continue
        ci = cv2.imread(c)
        if ci is None: print('unreadable', c); continue
        if K.get('bg') == 'green': composite_shot.cutout = green_cutout                     # white clothes survive a green key
        im = composite_shot.composite(ci, cv2.imread(p), s.get('x', 0.5), s.get('y', 0.5), s.get('s', 0.7), s.get('blur', 5), tuple(s.get('tint', (1.0, 0.97, 0.94))), s.get('gain', 0.97))
    else:
        p = find('full', s['full']) if 'full' in s else find('plates', s['plate'])
        if not p: print('missing', i, s); continue
        im = cv2.imread(p)
    cv2.imwrite(out, cv2.resize(im, (1152, 2048), interpolation=cv2.INTER_LANCZOS4))
print('keys written')
