#!/usr/bin/env python3
"""Book trailer and animated cover from existing episode frames (no new pictures, no voice).
usage: python3 make_trailer.py <out_dir> [--size 720] [--cover <cover.jpg>]
Writes trailer_9x16.mp4, trailer_1x1.mp4 and (with --cover) cover_loop.mp4. Music: the synthesized bed of
pipeline/soundtrack.py (made by our own code, so its rights are clear). Moves: slow push/pan with a two-plane
parallax (the lower part of the frame drifts faster than the top), crossfades, title cards in the house font."""
import os, sys, subprocess, json, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HI = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(HI, 'pipeline'))
import soundtrack
a = sys.argv[1:]; out = os.path.abspath(a[0]); os.makedirs(out, exist_ok=True)
SW = int(a[a.index('--size') + 1]) if '--size' in a else 720
FPS = 30
V = lambda p: os.path.join(HI, 'videos', p)
SHOTS = [  # frame, caption (Tagalog), seconds, move
    ('ep01-ang-unang-talon/keys/k13.png', 'Isang lumang medalyong tanso.\nIsang marker, binasa nang malakas.', 3.0, 'push_in'),
    ('ep01-ang-unang-talon/keys/k18.png', 'At isang asong\ngaling sa liwanag.', 2.6, 'pull_out'),
    ('ep01-ang-unang-talon/keys/k24.png', 'Pugad Lawin, 1896.', 2.4, 'pan_right'),
    ('ep02-british-sa-maynila/full/wallfall.jpg', 'Maynila, 1762.', 2.2, 'push_in'),
    ('ep03-ang-sabi-ni-lola/full/flag.jpg', 'Kawit, 1898.', 2.2, 'tilt_up'),
    ('ep06-ang-huling-umaga/full/m_back.jpg', 'Sino si M?', 2.4, 'push_in'),
    ('ep06-ang-huling-umaga/full/chest_empty.jpg', 'Nawala ang medalyon.', 2.4, 'pan_left'),
    ('ep07-ang-sulat-ni-lolo/full/lens.jpg', 'Saksi lang siya.\nHindi niya mababago ang nakaraan.', 3.0, 'push_in'),
    ('ep08-ang-huling-tala/full/star_medallion.jpg', 'Ang Huling Tala.', 2.6, 'pull_out'),
]
END = 6.2   # cover card
XF = 0.45   # crossfade

def font(stem, size):
    for root, _, fs in os.walk('/usr/share/fonts'):
        for f in fs:
            if os.path.splitext(f)[0] == stem: return ImageFont.truetype(os.path.join(root, f), size)
    return ImageFont.load_default()

def fit(im, W, H, head=1.18):
    k = max(W * head / im.width, H * head / im.height)
    return im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)

def move_xy(move, e):
    z = {'push_in': 1 + .10 * e, 'pull_out': 1.10 - .10 * e}.get(move, 1.05)
    dx = {'pan_right': -.5 + e, 'pan_left': .5 - e}.get(move, 0) * .6
    dy = {'tilt_up': .5 - e, 'tilt_down': -.5 + e}.get(move, 0) * .6
    return z, dx, dy

def render_shot(big, W, H, move, e):
    z, dx, dy = move_xy(move, e)
    arr = np.asarray(big, np.float32); h, w = arr.shape[:2]
    out = np.zeros((H, W, 3), np.float32)
    for band, (y0, y1), par in (('far', (0, .55), 0.6), ('near', (.45, 1), 1.4)):   # two planes: top slower, bottom faster
        cw, ch = W / z, H / z
        cx = w / 2 + dx * (w - cw) / 2 * par; cy = h / 2 + dy * (h - ch) / 2 * par
        x0 = int(np.clip(cx - cw / 2, 0, w - cw)); yy0 = int(np.clip(cy - ch / 2, 0, h - ch))
        crop = Image.fromarray(arr[yy0:yy0 + int(ch), x0:x0 + int(cw)].astype(np.uint8)).resize((W, H), Image.BILINEAR)
        c = np.asarray(crop, np.float32)
        m = np.zeros((H, 1, 1), np.float32); ys = np.linspace(0, 1, H)[:, None, None]
        m[:] = np.clip((ys - y0) / .1, 0, 1) * np.clip((y1 - ys) / .1, 0, 1) if band == 'near' else np.clip((y1 - ys) / .1, 0, 1)
        if band == 'far': out = c
        else: out = out * (1 - m) + c * m
    return out

def caption(W, H, text, alpha):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f = font('InterDisplay-ExtraBold', int(W * .05)); lines = text.split('\n')
    lh = int(W * .066); y = int(H * .74) - lh * len(lines) // 2
    for i in range(H // 3):     # soft dark band behind the text
        d.line([(0, H - i), (W, H - i)], fill=(0, 0, 0, int(160 * (1 - i / (H / 3)) * alpha)))
    for ln in lines:
        tw = d.textlength(ln, font=f); x = (W - tw) / 2
        d.text((x + 3, y + 3), ln, font=f, fill=(0, 0, 0, int(200 * alpha)))
        d.text((x, y), ln, font=f, fill=(250, 236, 205, int(255 * alpha))); y += lh
    return lay

def end_card(W, H, cover):
    bg = fit(Image.open(cover).convert('RGB'), W, H, 1.0).filter(ImageFilter.GaussianBlur(18))
    bg = Image.blend(bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width + W) // 2, (bg.height + H) // 2)), Image.new('RGB', (W, H)), .55)
    c = Image.open(cover).convert('RGB'); ch = int(H * (.62 if H > W else .70)); c = c.resize((int(c.width * ch / c.height), ch), Image.LANCZOS)
    bg.paste(c, ((W - c.width) // 2, int(H * .05))); d = ImageDraw.Draw(bg)
    f1 = font('InterDisplay-Bold', int(min(W, H) * .052)); f2 = font('Inter-Medium', int(min(W, H) * .034))
    for t, f, y, col in (('Ang nobela ng History Indio', f1, .05 + ch / H + .03, (240, 190, 90)),
                         ('Unang Aklat: Ang Unang Talon', f2, .05 + ch / H + .095, (250, 240, 220)),
                         ('Kathang-isip sina Indio at Usman; totoo ang kasaysayan.', f2, .05 + ch / H + .15, (210, 200, 180))):
        tw = d.textlength(t, font=f); d.text(((W - tw) / 2, int(H * y)), t, font=f, fill=col)
    return np.asarray(bg, np.float32)

def encode(frames_fn, n, W, H, path, audio=None):
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-']
    if audio: cmd += ['-i', audio, '-c:a', 'aac', '-b:a', '160k', '-shortest']
    cmd += ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'medium', '-movflags', '+faststart', path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n): p.stdin.write(np.clip(frames_fn(i), 0, 255).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait(); print(path, os.path.getsize(path) // 1024, 'KB')

def trailer(W, H, path, cover, music):
    bigs = [fit(Image.open(V(s[0])).convert('RGB'), W, H) for s in SHOTS]
    starts = np.cumsum([0] + [s[2] for s in SHOTS]); total = starts[-1] + END
    endc = end_card(W, H, cover); caps = {}
    def shot_frame(i, t):
        s = SHOTS[i]; e = np.clip(t / s[2], 0, 1); e = e * e * (3 - 2 * e)
        fr = render_shot(bigs[i], W, H, s[3], e)
        al = float(np.clip(min(t / .35, (s[2] - t) / .35), 0, 1))
        key = (i, round(al, 2))
        if key not in caps: caps[key] = caption(W, H, s[1], al)
        lay = caps[key]; A = np.asarray(lay, np.float32)[..., 3:] / 255
        return fr * (1 - A) + np.asarray(lay, np.float32)[..., :3] * A
    def f(n):
        t = n / FPS; i = int(np.searchsorted(starts, t, 'right') - 1)
        if i >= len(SHOTS):
            te = t - starts[-1]; z = 1 + .03 * te / END
            img = Image.fromarray(endc.astype(np.uint8)); cw, ch = int(W / z), int(H / z)
            fr = np.asarray(img.crop(((W - cw) // 2, (H - ch) // 2, (W + cw) // 2, (H + ch) // 2)).resize((W, H)), np.float32)
            if te < XF: fr = fr * (te / XF) + shot_frame(len(SHOTS) - 1, t - starts[-2]) * (1 - te / XF)
            return fr * min(1, (total - t) / .6)
        fr = shot_frame(i, t - starts[i])
        if i > 0 and t - starts[i] < XF:
            k = (t - starts[i]) / XF; fr = fr * k + shot_frame(i - 1, t - starts[i - 1]) * (1 - k)
        return fr * min(1, t / .5)
    encode(f, int(total * FPS), W, H, path, music)
    return total

def music_wav(dur, path):
    x = soundtrack.music(dur, bpm=84, seed=7); x = x / max(1e-6, np.abs(x).max()) * .5
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(soundtrack.SR); w.writeframes((x * 32767).astype(np.int16).tobytes())
    return path

cover = a[a.index('--cover') + 1] if '--cover' in a else os.path.join(HI, 'videos/ep01-ang-unang-talon/keys/k01.png')
dur = sum(s[2] for s in SHOTS) + END
mus = music_wav(dur + .5, os.path.join(out, 'music.wav'))
print('trailer seconds', round(trailer(SW, SW * 16 // 9, os.path.join(out, 'trailer_9x16.mp4'), cover, mus), 1))
trailer(SW, SW, os.path.join(out, 'trailer_1x1.mp4'), cover, mus)
if '--cover' in a:   # 6-second seamless cover loop: slow breathe + light sweep, no sound
    c = np.asarray(Image.open(cover).convert('RGB').resize((SW, int(SW * 1.6))), np.float32); H2 = c.shape[0]
    xs = np.arange(SW)[None, :, None]; ys = np.arange(H2)[:, None, None]
    def g(n):
        t = n / (6 * FPS); z = 1 + .025 * (1 - np.cos(2 * np.pi * t)) / 2
        img = Image.fromarray(c.astype(np.uint8)); cw, ch = int(SW / z), int(H2 / z)
        fr = np.asarray(img.crop(((SW - cw) // 2, (H2 - ch) // 2, (SW + cw) // 2, (H2 + ch) // 2)).resize((SW, H2)), np.float32)
        band = np.exp(-(((xs + ys * .5) - (t * 2.2 - .6) * (SW + H2 * .5)) / (SW * .12)) ** 2)    # gold light sweep
        return fr + band * np.array([60, 40, 10], np.float32)
    encode(g, 6 * FPS, SW, H2 - H2 % 2, os.path.join(out, 'cover_loop.mp4'))
