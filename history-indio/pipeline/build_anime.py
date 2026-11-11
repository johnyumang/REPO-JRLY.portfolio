#!/usr/bin/env python3
"""Animate still keyframes into a moving short: depth-based parallax camera, water shimmer, glow pulse,
particles (embers / sparkles / bubbles), impact shake, punch-in, cut-ins on long lines, subtitles, soundtrack.
usage: build_anime.py <video_dir> <keys_dir> <voice.wav> <out.mp4> [--only 0,1,2] [--fps 30]
video_dir: timings.json (+ shots_fx.json optional: {"<i>": {"fx": ["water","embers"], "move": "push_in"}})
keys_dir: k00.png ... one keyframe per sentence. Depth comes from Depth-Anything-V2-Small (Hugging Face)."""
import json, os, subprocess, sys
import numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import soundtrack, subtitles, branding
from PIL import Image as _I
W, H = 1080, 1920
a = sys.argv[1:]; vdir, kdir, voice, out = [os.path.abspath(x) for x in a[:4]]
fps = int(a[a.index('--fps') + 1]) if '--fps' in a else 30
only = [int(x) for x in a[a.index('--only') + 1].split(',')] if '--only' in a else None
tim = json.load(open(os.path.join(vdir, 'timings.json')))
fxp = os.path.join(vdir, 'shots_fx.json'); FX = json.load(open(fxp)) if os.path.exists(fxp) else {}
ease = lambda x: x * x * x * (x * (x * 6 - 15) + 10)
MOVES = ['push_in', 'pan_right', 'tilt_up', 'pull_out', 'pan_left', 'push_in', 'tilt_down']

def depth_maps(paths):
    cache = os.path.join(kdir, 'depth'); os.makedirs(cache, exist_ok=True); pipe = None; res = {}
    for p in paths:
        c = os.path.join(cache, os.path.basename(p) + '.npy')
        if not os.path.exists(c):
            if pipe is None:
                from transformers import pipeline; from PIL import Image
                pipe = pipeline('depth-estimation', model='depth-anything/Depth-Anything-V2-Small-hf', device='cpu')
            d = np.asarray(pipe(Image.open(p).convert('RGB'))['depth'], dtype=np.float32)
            d = (d - d.min()) / max(1e-6, d.max() - d.min()); np.save(c, d)
        res[p] = np.load(c)
    return res

def prep(img, dep, head=1.22):
    """cover-fit the keyframe with headroom for camera moves; depth resized to match (1 = near)."""
    k = max(W * head / img.shape[1], H * head / img.shape[0])
    im = cv2.resize(img, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4)
    d = cv2.GaussianBlur(cv2.resize(dep, (im.shape[1], im.shape[0]), interpolation=cv2.INTER_LINEAR), (0, 0), 6)
    hl = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    glow = cv2.GaussianBlur(np.clip(hl - 0.72, 0, 1)[..., None] * im.astype(np.float32), (0, 0), 28)      # bloom of the bright parts
    return im, d, glow

YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)

def frame(im, d, glow, e, t, move, fx, zoom_extra=1.0, focus=(0.5, 0.5), seed=0):
    ih, iw = im.shape[:2]; fit = min(iw / W, ih / H)
    z0, z1, px, py, sx, sy = 1.06, 1.06, 0.0, 0.0, 1.0, 0.0
    if move == 'push_in': z0, z1 = 1.0, 1.16
    elif move == 'pull_out': z0, z1 = 1.16, 1.0
    elif move == 'pan_left': px, sx = 0.5 - e, -1.0
    elif move == 'pan_right': px = e - 0.5
    elif move == 'tilt_up': py, sx, sy = 0.5 - e, 0.0, -1.0
    elif move == 'tilt_down': py, sx, sy = e - 0.5, 0.0, 1.0
    z = (z0 + (z1 - z0) * e) * zoom_extra
    if 'punch' in fx and t < 0.2: z *= 1 + 0.10 * (1 - t / 0.2) ** 2                    # punch-in on the cut
    s = fit / z; w, h = W * s, H * s
    x0 = (iw - w) * (focus[0] + px * 0.9) ; y0 = (ih - h) * (focus[1] + py * 0.9)
    x0 = np.clip(x0, 0, iw - w); y0 = np.clip(y0, 0, ih - h)
    if 'shake' in fx and t < 0.6:
        rng = np.random.default_rng(seed + int(t * fps)); k = (1 - t / 0.6) ** 2 * 16
        x0 += rng.normal() * k; y0 += rng.normal() * k
    mx = (x0 + XX * s).astype(np.float32); my = (y0 + YY * s).astype(np.float32)
    dd = cv2.remap(d, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT) - 0.45        # near > 0, far < 0
    par = 30.0 * s                                                                           # parallax strength in source px
    mx = mx + dd * par * sx * (e - 0.5) * 2 + (XX - W / 2) * dd * 0.035 * (z - 1.0) * s * 4  # near things slide and grow more
    my = my + dd * par * sy * (e - 0.5) * 2 + (YY - H / 2) * dd * 0.035 * (z - 1.0) * s * 4 - dd * 5 * s * np.sin(t * 1.1)   # slow breathing drift
    if 'water' in fx:                                                                        # shimmer on the far lower part (the sea)
        wmask = np.clip((YY / H - 0.45) * 3, 0, 1) * np.clip(0.75 - dd - 0.45, 0, 1) * 1.6
        mx = mx + wmask * 3.2 * s * np.sin(YY * 0.045 + t * 2.6); my = my + wmask * 2.2 * s * np.sin(XX * 0.02 + YY * 0.06 + t * 3.1)
    mx = mx.astype(np.float32); my = my.astype(np.float32)
    fr = cv2.remap(im, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    g = cv2.remap(glow, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    fr += g * (0.30 + 0.22 * np.sin(t * 2.3))                                                # moons and fires pulse
    rng = np.random.default_rng(seed); ov = np.zeros((H // 2, W // 2, 3), np.float32)        # particles at half res
    def dots(n, col, vy, size, sway, twinkle=0.0, region=(0, 1)):
        bx = rng.random(n) * W / 2; by = rng.random(n) * H / 2; ph = rng.random(n) * 6.28; sp = 0.5 + rng.random(n)
        for i in range(n):
            y = (by[i] + vy * sp[i] * t * 30) % (H / 2); x = bx[i] + np.sin(t * 1.7 + ph[i]) * sway
            if not (region[0] * H / 2 <= y <= region[1] * H / 2): continue
            a_ = 1.0 if not twinkle else max(0.0, np.sin(t * twinkle * sp[i] + ph[i]))
            cv2.circle(ov, (int(x), int(y)), size, [c * a_ for c in col], -1, cv2.LINE_AA)
    if 'embers' in fx: dots(46, (40, 150, 255), -1.6, 2, 14)
    if 'sparkle' in fx: dots(60, (255, 245, 225), 0.0, 1, 0, twinkle=3.2, region=(0, 0.55))
    if 'bubbles' in fx: dots(40, (255, 230, 200), -1.0, 3, 9)
    if 'spray' in fx: dots(70, (255, 255, 255), 2.4, 1, 6, region=(0.2, 1))
    if ov.any(): fr += cv2.resize(cv2.GaussianBlur(ov, (0, 0), 1.6), (W, H)) * 0.9
    if 'flash' in fx and t < 0.12: fr = fr * (t / 0.12) + 255 * (1 - t / 0.12)
    vig = 1 - 0.28 * (((XX - W / 2) / (W / 2)) ** 2 + ((YY - H / 2) / (H / 2)) ** 2) ** 1.2 ; fr *= vig[..., None]
    return np.clip(fr, 0, 255).astype(np.uint8)

paths = [os.path.join(kdir, f'k{i:02d}.png') for i in range(len(tim))]; deps = depth_maps(paths if not only else [paths[i] for i in only])
total = tim[-1]['end'] + 0.8; shots = []
for i, s in enumerate(tim):
    start = 0.0 if i == 0 else s['start']; end = tim[i + 1]['start'] if i + 1 < len(tim) else total
    cfg = FX.get(str(i), {}); mv = cfg.get('move', MOVES[i % len(MOVES)]); fx = cfg.get('fx', [])
    if cfg.get('keys'):                                                                      # montage: several keyframes inside one line (cold open)
        ks = cfg['keys']; step = (end - start) / len(ks)
        for j, kk in enumerate(ks): shots.append((kk, start + j * step, start + (j + 1) * step, ['push_in', 'pull_out'][j % 2], fx, 1.0, (0.5, 0.5)))
        continue
    if end - start > 6.2:                                                                    # cut-in on long lines
        mid = start + (end - start) * 0.52
        shots.append((i, start, mid, mv, fx, 1.0, (0.5, 0.5))); shots.append((i, mid, end, 'push_in' if mv != 'push_in' else 'pan_right', [f for f in fx if f not in ('punch', 'shake', 'flash')] + ['punch'], 1.42, tuple(cfg.get('focus', (0.5, 0.36)))))
    else: shots.append((i, start, end, mv, fx, 1.0, (0.5, 0.5)))
if only: shots = [s for s in shots if s[0] in only]; t0 = shots[0][1]; shots = [(i, a_ - t0, b - t0, m, f, z, fo) for i, a_, b, m, f, z, fo in shots]
lens = [b - a_ for _, a_, b, *_ in shots]; print('shots', len(shots), 'min %.1f max %.1f avg %.1f' % (min(lens), max(lens), sum(lens) / len(lens)), flush=True)
work = os.path.join(kdir, 'build'); os.makedirs(work, exist_ok=True); cmd_a = []
if not only:
    mix = os.path.join(work, 'mix.wav'); print(soundtrack.make(voice, [s[1] for s in shots[1:]], [s[1] for s in shots if 'flash' in s[4]], mix), flush=True)
    print(subtitles.make(tim, os.path.join(work, 'subs.ass')), 'subtitle lines'); cmd_a = ['-i', mix, '-vf', 'subtitles=subs.ass', '-c:a', 'aac', '-b:a', '192k', '-shortest']
ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-'] + cmd_a +
                      ['-c:v', 'libx264', '-crf', '21', '-maxrate', '5000k', '-bufsize', '10000k', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], stdin=subprocess.PIPE, cwd=work)
def _layer(im): r = np.asarray(im.convert('RGBA')).astype(np.float32); return r[..., [2, 1, 0]], r[..., 3:4] / 255      # BGR + alpha
BUG_RGB, BUG_A = _layer(branding.bug((W, H))); bb = np.argwhere(BUG_A[..., 0] > 0); by0, bx0 = bb.min(0); by1, bx1 = bb.max(0) + 1
END_RGB, END_A = _layer(branding.endcard((W, H))); END_T = 2.6; total_f = round(shots[-1][2] * fps)
def brand(fr, fi):
    reg = fr[by0:by1, bx0:bx1].astype(np.float32); al = BUG_A[by0:by1, bx0:bx1]; fr[by0:by1, bx0:bx1] = (reg * (1 - al) + BUG_RGB[by0:by1, bx0:bx1] * al).astype(np.uint8)
    left = (total_f - fi) / fps
    if left < END_T and not only:                                             # end card fades in over the last seconds
        k = min(1.0, (END_T - left) / 0.5); fr = (fr.astype(np.float32) * (1 - END_A * k) + END_RGB * END_A * k).astype(np.uint8)
    return fr
f = 0; cur = None
for n, (i, a_, b, mv, fx, zx, fo) in enumerate(shots):
    if cur != i: im, d, glow = prep(cv2.imread(paths[i]), deps[paths[i]]); cur = i
    f1 = round(b * fps); cnt = max(1, f1 - f)
    for k in range(cnt):
        ff.stdin.write(brand(frame(im, d, glow, ease(k / max(1, cnt - 1)), k / fps, mv, fx, zx, fo, seed=n * 97), f + k).tobytes())
    f = f1; print('shot', n + 1, '/', len(shots), flush=True)
ff.stdin.close(); sys.exit(ff.wait())
