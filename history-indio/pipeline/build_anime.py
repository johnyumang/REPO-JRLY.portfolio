#!/usr/bin/env python3
"""Animate still keyframes into a moving short: depth-based parallax camera, water shimmer, glow pulse,
particles (embers / sparkles / bubbles), impact shake, punch-in, cut-ins on long lines, subtitles, soundtrack.
usage: build_anime.py <video_dir> <keys_dir> <voice.wav> <out.mp4> [--only 0,1,2] [--fps 30]
video_dir: timings.json (+ shots_fx.json optional: {"<i>": {"fx": ["water","embers"], "move": "push_in"}})
3D perspective (opt-in per shot): "move": dolly_in/out, orbit_left/right, crane_up/down, rack_focus, or "depth": "strong";
optional "dof": "far"|"near", "focus_to": "far" (see depth3d.py and README).
keys_dir: k00.png ... one keyframe per sentence. Depth comes from Depth-Anything-V2-Small (Hugging Face)."""
import json, os, subprocess, sys
import numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import soundtrack, subtitles, branding, puppet_still, depth3d
from PIL import Image as _I
W, H = 1080, 1920
if '--size' in sys.argv: W = int(sys.argv[sys.argv.index('--size') + 1]); H = W * 16 // 9          # e.g. --size 720 renders 720x1280, about twice as fast
a = sys.argv[1:]; vdir, kdir, voice, out = [os.path.abspath(x) for x in a[:4]]
fps = int(a[a.index('--fps') + 1]) if '--fps' in a else 30
only = [int(x) for x in a[a.index('--only') + 1].split(',')] if '--only' in a else None
until = float(a[a.index('--until') + 1]) if '--until' in a else None                      # render only the first N seconds (preview)
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
    near = np.clip((d - 0.5) * 6, 0, 1); kk = max(15, int(im.shape[1] * 0.05)) | 1
    ring = cv2.GaussianBlur(cv2.dilate(near, np.ones((kk, kk), np.uint8)), (0, 0), kk * 0.4) * (1 - near * 0.8)        # energy-aura zone hugging the foreground figure
    return im, d, glow, ring.astype(np.float32)

YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)

_n = cv2.GaussianBlur(np.random.default_rng(4).random((256, 256)).astype(np.float32), (0, 0), 5); NOISE = np.clip((_n - _n.min()) / (_n.max() - _n.min()) * 2.2 - 0.6, 0, 1)
AURA = {'aura_gold': (40, 190, 255), 'aura_blue': (255, 180, 70), 'aura_red': (60, 70, 255), 'aura_green': (110, 255, 120)}          # BGR

def glow3d(fr):
    """bloom of the bright parts, computed on the finished 3D frame at quarter size (cheap, follows both layers)."""
    sm = cv2.resize(fr, (W // 4, H // 4), interpolation=cv2.INTER_AREA); hl = sm.mean(2, keepdims=True) / 255
    return cv2.resize(cv2.GaussianBlur(np.clip(hl - 0.72, 0, 1) * sm, (0, 0), 6.0 * W / 1080), (W, H), interpolation=cv2.INTER_LINEAR)

def frame(im, d, glow, e, t, move, fx, zoom_extra=1.0, focus=(0.5, 0.5), seed=0, aura=None, L3=None):
    if L3 is not None: return frame_tail(*frame_3d(L3, e, t, move, fx, zoom_extra, focus, seed), t, fx, seed, aura)
    if '3d' in fx: move = depth3d.FALLBACK.get(move, move)                                  # flat depth map: the normal parallax
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
    near = np.clip(dd * 3.0, 0, 1)                                                           # the foreground figure sways and breathes
    mx = mx + near * 3.4 * s * np.sin(t * 2.4 + YY * 0.011); my = my + near * 2.4 * s * np.sin(t * 1.9 + XX * 0.004)
    if 'water' in fx:                                                                        # shimmer on the far lower part (the sea)
        wmask = np.clip((YY / H - 0.45) * 3, 0, 1) * np.clip(0.75 - dd - 0.45, 0, 1) * 1.6
        mx = mx + wmask * 3.2 * s * np.sin(YY * 0.045 + t * 2.6); my = my + wmask * 2.2 * s * np.sin(XX * 0.02 + YY * 0.06 + t * 3.1)
    mx = mx.astype(np.float32); my = my.astype(np.float32)
    fr = cv2.remap(im, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    g = cv2.remap(glow, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    fr += g * (0.30 + 0.22 * np.sin(t * 2.3))                                                # moons and fires pulse
    return frame_tail(fr, mx, my, s, t, fx, seed, aura)

def frame_3d(L3, e, t, move, fx, zoom_extra, focus, seed):
    sh = (0.0, 0.0)
    if 'shake' in fx and t < 0.6: rng = np.random.default_rng(seed + int(t * fps)); k = (1 - t / 0.6) ** 2 * 16; sh = (rng.normal() * k, rng.normal() * k)
    dof = next((f[4:] for f in fx if f.startswith('dof:')), None); to = 'far' if 'rack:far' in fx else 'near'
    fr, mx, my, s = depth3d.frame3d(L3, e, t, move, fx, W, H, zoom_extra, focus, dof, to, sh)
    fr += glow3d(fr) * (0.30 + 0.22 * np.sin(t * 2.3))
    return fr, mx, my, s

def frame_tail(fr, mx, my, s, t, fx, seed, aura):
    ak = next((f for f in fx if f in AURA), None)
    if ak and aura is not None:                                                              # flame-like energy aura rising around the figure
        am = cv2.remap(aura, mx, (my + 26 * s).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        n = NOISE[((YY * 0.33 + t * 250).astype(np.int32)) % 256, ((XX * 0.33 + 26 * np.sin(t * 3.1 + YY * 0.012)).astype(np.int32)) % 256]
        fr += (am * (0.30 + 1.15 * n) * (0.85 + 0.15 * np.sin(t * 11)))[..., None] * np.array(AURA[ak], np.float32) * 0.95
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
    if 'speedlines' in fx:                                                                   # radial speed lines, redrawn every 2 frames
        r2 = np.random.default_rng(seed + int(t * fps) // 2); sl = np.zeros((H // 2, W // 2), np.float32); cx, cy = W / 4, H / 4 * 0.9
        for _ in range(54):
            an = r2.random() * 6.283; r0 = (0.30 + 0.22 * r2.random()) * H / 2; wd = 0.006 + 0.014 * r2.random()
            pts = np.array([[cx + np.cos(an) * r0, cy + np.sin(an) * r0], [cx + np.cos(an - wd) * H, cy + np.sin(an - wd) * H], [cx + np.cos(an + wd) * H, cy + np.sin(an + wd) * H]], np.int32)
            cv2.fillPoly(sl, [pts], 1.0, cv2.LINE_AA)
        sl = cv2.resize(sl, (W, H))[..., None] * 0.8; fr = fr * (1 - sl) + 255 * sl
    if 'impact' in fx and t < 0.36:                                                          # impact frame, then colour-split shake-off
        k = 1 - t / 0.36; sh = int(16 * k * W / 1080)
        if sh: fr[..., 2] = np.roll(fr[..., 2], sh, axis=1); fr[..., 0] = np.roll(fr[..., 0], -sh, axis=1)
        if t < 2.0 / fps - 1e-6 and seed: g = fr.mean(2, keepdims=True)      # not on the very first shot, which becomes the thumbnail; fr = np.where(g > 105, 250.0, 12.0) * np.ones(3, np.float32)
    vig = 1 - 0.28 * (((XX - W / 2) / (W / 2)) ** 2 + ((YY - H / 2) / (H / 2)) ** 2) ** 1.2 ; fr *= vig[..., None]
    return np.clip(fr, 0, 255).astype(np.uint8)

paths = [os.path.join(kdir, f'k{i:02d}.png') for i in range(max(len(tim), 200))]
total = tim[-1]['end'] + 0.8; shots = []
for i, s in enumerate(tim):
    start = 0.0 if i == 0 else s['start']; end = tim[i + 1]['start'] if i + 1 < len(tim) else total
    cfg = FX.get(str(i), {}); mv = cfg.get('move', MOVES[i % len(MOVES)]); fx = list(cfg.get('fx', []))
    if 'punch' in fx or 'shake' in fx: fx += [f for f in ('speedlines', 'impact') if f not in fx]      # action beats get the full anime treatment
    if cfg.get('depth') == 'strong' or mv in depth3d.MOVES3D:                                # 3D perspective (opt-in): layered depth camera, see depth3d.py
        fx += ['3d'] + (['dof:' + cfg['dof']] if cfg.get('dof') in ('far', 'near') else []) + (['rack:far'] if cfg.get('focus_to') == 'far' else [])
    i = cfg.get('key', i)                                                                    # reuse another line's keyframe
    if cfg.get('clip'):                                                                      # a ready-made moving clip (e.g. a Blender action shot) plays for this line
        shots.append((i, start, end, 'hold', fx, 1.0, (0.5, 0.5), os.path.join(vdir, cfg['clip']))); continue
    if cfg.get('keys'):                                                                      # montage: several keyframes inside one line (cold open)
        ks = cfg['keys']; step = (end - start) / len(ks)
        for j, kk in enumerate(ks): shots.append((kk, start + j * step, start + (j + 1) * step, ['push_in', 'pull_out'][j % 2], fx, 1.0, (0.5, 0.5)))
        continue
    if end - start > 6.2:                                                                    # cut-in on long lines
        mid = start + (end - start) * 0.52
        shots.append((i, start, mid, mv, fx, 1.0, (0.5, 0.5))); shots.append((i, mid, end, 'push_in' if mv != 'push_in' else 'pan_right', [f for f in fx if f not in ('punch', 'shake', 'flash')] + ['punch'], 1.42, tuple(cfg.get('focus', (0.5, 0.36)))))
    else: shots.append((i, start, end, mv, fx, 1.0, (0.5, 0.5)))
if only: shots = [s for s in shots if s[0] in only]; t0 = shots[0][1]; shots = [(s_[0], s_[1] - t0, s_[2] - t0) + tuple(s_[3:]) for s_ in shots]
if until: shots = [s_ for s_ in shots if s_[1] < until]
def rig_for(i): p = os.path.join(vdir, 'rigs', f'k{i:02d}.json'); return p if os.path.exists(p) else None      # a puppet rig makes the still itself move (see PUPPET.md)
deps = depth_maps(sorted({paths[s_[0]] for s_ in shots if len(s_) < 8 and not rig_for(s_[0])}))
lens = [b - a_ for _, a_, b, *_ in shots]; print('shots', len(shots), 'min %.1f max %.1f avg %.1f' % (min(lens), max(lens), sum(lens) / len(lens)), flush=True)
work = os.path.join(kdir, 'build'); os.makedirs(work, exist_ok=True); cmd_a = []
if not only:
    mix = os.path.join(work, 'mix.wav'); print(soundtrack.make(voice, [s[1] for s in shots[1:]], [s[1] for s in shots if 'flash' in s[4]], mix), flush=True)
    print(subtitles.make(tim, os.path.join(work, 'subs.ass')), 'subtitle lines'); cmd_a = ['-i', mix, '-vf', 'subtitles=subs.ass', '-c:a', 'aac', '-b:a', '192k', '-shortest']
ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-'] + cmd_a +
                      ['-c:v', 'libx264', '-crf', '21', '-maxrate', '5000k', '-bufsize', '10000k', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], stdin=subprocess.PIPE, cwd=work)
def _layer(im): r = np.asarray(im.convert('RGBA')).astype(np.float32); return r[..., [2, 1, 0]], r[..., 3:4] / 255      # BGR + alpha
BUG_RGB, BUG_A = _layer(branding.bug((1080, 1920)).resize((W, H))); bb = np.argwhere(BUG_A[..., 0] > 0); by0, bx0 = bb.min(0); by1, bx1 = bb.max(0) + 1
_ec = os.path.join(vdir, 'endcard.txt'); _kw = {'line': open(_ec).read().strip()} if os.path.exists(_ec) else {}      # per-video end-card line
END_RGB, END_A = _layer(branding.endcard((1080, 1920), **_kw).resize((W, H))); END_T = 2.6; total_f = round(shots[-1][2] * fps)
def brand(fr, fi):
    reg = fr[by0:by1, bx0:bx1].astype(np.float32); al = BUG_A[by0:by1, bx0:bx1]; fr[by0:by1, bx0:bx1] = (reg * (1 - al) + BUG_RGB[by0:by1, bx0:bx1] * al).astype(np.uint8)
    left = (total_f - fi) / fps
    if left < END_T and not only and not until:                                             # end card fades in over the last seconds
        k = min(1.0, (END_T - left) / 0.5); fr = (fr.astype(np.float32) * (1 - END_A * k) + END_RGB * END_A * k).astype(np.uint8)
    return fr
TRANS = ['whip', 'slash', 'dissolve', 'zoom', 'whip', 'flash']; TN = 7                    # transition types, cycled; each lasts TN frames
def _zoom(img, z): return cv2.warpAffine(img, cv2.getRotationMatrix2D((W / 2, H / 2), 0, z), (W, H), borderMode=cv2.BORDER_REFLECT)
def transition(a_, b_, p, kind):
    pe = ease(p)
    if kind == 'whip':                                                                       # whip-pan with motion blur
        dx = int(W * pe); cv = np.concatenate([a_, b_], axis=1)[:, dx:dx + W]; k = int(1 + 140 * np.sin(np.pi * p) * W / 1080)
        return cv2.blur(cv, (k, 1)) if k > 1 else cv
    if kind == 'slash':                                                                      # diagonal blade wipe with a bright edge
        pos = pe * (W + H * 0.5) * 1.06; dgn = XX + YY * 0.5; o = np.where((dgn < pos)[..., None], b_, a_).astype(np.float32)
        o += (np.clip(1 - np.abs(dgn - pos) / (26 * W / 1080), 0, 1) ** 2)[..., None] * 255; return np.clip(o, 0, 255).astype(np.uint8)
    if kind == 'zoom': return cv2.addWeighted(_zoom(a_, 1 + 0.55 * pe), 1 - pe, _zoom(b_, 1.5 - 0.5 * pe), pe, 0)      # zoom-through
    if kind == 'flash': w = np.sin(np.pi * p); return cv2.addWeighted(a_ if p < 0.5 else b_, 1 - w, np.full_like(b_, 255), w, 0)
    return cv2.addWeighted(a_, 1 - pe, b_, pe, 0)                                             # dissolve
f = 0; cur = None; last = None; pup = None; L3s = {}
for n, sh in enumerate(shots):
    i, a_, b, mv, fx, zx, fo = sh[:7]; clip = sh[7] if len(sh) > 7 else None; cap = cv2.VideoCapture(clip) if clip else None; held = None
    if cur != i and not clip:
        rp = rig_for(i); cur = i
        if rp: pup = puppet_still.Puppet(json.load(open(rp)), cv2.imread(paths[i]), W, H, fps, seed=n)
        else: pup = None; im, d, glow, ring = prep(cv2.imread(paths[i]), deps[paths[i]])
    L3 = None
    if '3d' in fx and not clip and pup is None:                                              # layers are made once per keyframe; None = flat depth
        if i not in L3s: L3s[i] = depth3d.prep3d(im, deps[paths[i]], im.shape[1] * 0.008); print('3d layers k%02d:' % i, 'flat, normal parallax' if L3s[i] is None else 'ok', flush=True)
        L3 = L3s[i]
    kind = FX.get('trans', {}).get(str(n), TRANS[n % len(TRANS)])
    f1 = round(b * fps); cnt = max(1, f1 - f)
    for k in range(cnt):
        if cap is not None:
            ok, cf = cap.read(); held = cv2.resize(cf, (W, H), interpolation=cv2.INTER_LANCZOS4) if ok else held; fr = held.copy()      # hold the last frame if the clip is short
        elif pup is not None: fr = pup.frame(k / fps, cnt / fps, zx, fo)
        else: fr = frame(im, d, glow, ease(k / max(1, cnt - 1)), k / fps, mv, fx, zx, fo, seed=n * 97, aura=ring, L3=L3)
        raw = fr
        if last is not None and k < TN and cnt > TN * 2: fr = transition(last, fr, (k + 1) / (TN + 1), kind)
        ff.stdin.write(brand(fr, f + k).tobytes())
    last = raw
    f = f1; print('shot', n + 1, '/', len(shots), flush=True)
ff.stdin.close(); sys.exit(ff.wait())
