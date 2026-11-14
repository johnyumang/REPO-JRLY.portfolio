#!/usr/bin/env python3
"""REAL Latin-letter writing on a sign, marker, plaque, page or label inside a picture (the owner, 14 Nov: a sign that the story
says carries writing is never empty, and never machine scribble). The picture is drawn with a PLAIN surface; this tool writes the
words on it afterwards, in perspective, mixed into the paint, the same way baybayin.py does for baybayin.

usage (from history-indio/):
  latin_sign.py paste <in.jpg> <out.jpg> "<words>" x1,y1,x2,y2,x3,y3,x4,y4 [--font serif|sans|caps|hand|<file.ttf>]
        [--colour r,g,b] [--opacity 0.85] [--rough 0.6] [--carve] [--fill 0.9]
  corners in pixels: top-left, top-right, bottom-right, bottom-left of the place the words go; a "|" starts a new line;
  --carve = light letters with a dark edge (stone, bronze); --fill = how much of the place's width a line may take.
Only words that are certainly true (the script or facts.md gives them, or they are plain labels such as a place name).
A Spanish, British or American paper of the past stays plain ruled lines. LOOK at the result at 3x before you keep it."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = {'serif': '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', 'sans': '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
         'caps': os.path.join(HERE, 'fonts', 'BebasNeue-Regular.ttf'), 'hand': '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf'}


def render(text, px, font):
    from PIL import Image, ImageDraw, ImageFont
    f = ImageFont.truetype(FONTS.get(font, font), px); d = ImageDraw.Draw(Image.new('L', (8, 8))); x0, y0, x1, y1 = d.textbbox((0, 0), text, font=f); p = px // 5
    im = Image.new('L', (x1 - x0 + 2 * p, y1 - y0 + 2 * p), 0); ImageDraw.Draw(im).text((p - x0, p - y0), text, font=f, fill=255); return im


def paste(src, dst, text, quad, font='serif', colour=None, opacity=0.85, rough=0.6, carve=False, fill=0.9):
    import cv2, numpy as np
    im = cv2.imread(src); H, W = im.shape[:2]; q = np.float32(quad).reshape(4, 2); lines = [x.strip() for x in text.split('|') if x.strip()]
    colour = colour or ((236, 208, 150) if carve else (40, 26, 12))
    wq = int(max(np.linalg.norm(q[1] - q[0]), np.linalg.norm(q[2] - q[3]))); hq = int(max(np.linalg.norm(q[3] - q[0]), np.linalg.norm(q[2] - q[1])))
    SS = 3; bw, bh = wq * SS, hq * SS; box = np.zeros((bh, bw), np.float32); lh = bh // len(lines)
    for k, ln in enumerate(lines):
        a = np.array(render(ln, max(24, int(lh * 0.7)), font)).astype(np.float32) / 255
        ys, xs = np.where(a > 0.05); a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        s = min(bw * fill / a.shape[1], lh * 0.72 / a.shape[0]); a = cv2.resize(a, (max(1, int(a.shape[1] * s)), max(1, int(a.shape[0] * s))), interpolation=cv2.INTER_AREA)
        y = k * lh + (lh - a.shape[0]) // 2; x = (bw - a.shape[1]) // 2; box[y:y + a.shape[0], x:x + a.shape[1]] = a
    if rough > 0:                                                           # paint, not print: uneven ink and a soft edge
        rng = np.random.default_rng(len(text) * 7919 + wq); n = cv2.GaussianBlur(rng.random((bh, bw)).astype(np.float32), (0, 0), max(1.0, bh / 40))
        n = (n - n.min()) / (n.max() - n.min() + 1e-6); box = cv2.GaussianBlur(box, (0, 0), SS * (0.4 + 0.3 * rough)) * (1 - 0.35 * rough * n)
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [bw, 0], [bw, bh], [0, bh]]), q); m = cv2.warpPerspective(box, M, (W, H), flags=cv2.INTER_AREA)[..., None]
    f = im.astype(np.float32); c = np.float32(colour[::-1])
    if carve:
        d = max(1, int(round(hq / len(lines) / 28))); sh = np.clip(np.roll(np.roll(m, d, 0), d, 1) - m, 0, 1)
        f = f * (1 - 0.75 * opacity * sh); f = f * (1 - opacity * m) + c * (opacity * m)
    elif sum(colour) > 380: f = f * (1 - opacity * m) + c * (opacity * m)   # light paint on a dark board: laid over
    else: f = f * (1 - opacity * m) + f * (c / 255) * (opacity * m)        # dark ink: multiplied, the paint under it still shows
    cv2.imwrite(dst, np.clip(f, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 95])


if __name__ == '__main__':
    a = sys.argv[1:]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    if len(a) < 5 or a[0] != 'paste': sys.exit(__doc__)
    q = [float(v) for v in a[4].split(',')]; assert len(q) == 8, 'eight numbers: four corners'
    rgb = tuple(int(v) for v in opt('--colour', '').split(',')) if '--colour' in a else None
    paste(a[1], a[2], a[3], q, opt('--font', 'serif'), rgb, float(opt('--opacity', 0.85)), float(opt('--rough', 0.6)), '--carve' in a, float(opt('--fill', 0.9)))
    print('written on', a[2], ':', a[3])
