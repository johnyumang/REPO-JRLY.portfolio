#!/usr/bin/env python3
"""REAL Latin letters inside a picture, for things of today (the owner, 14 Nov: a sign, placard, screen or note that the story
says carries writing is never empty). The image model draws the surface plain; this tool writes the words on it in code.
Only short words that are certainly true (the story's own words, a percent the narration says). Old Spanish, British or
American papers stay plain ruled lines; Filipino writing of the past is baybayin (pipeline/baybayin.py).

usage (from history-indio/):
  latin_text.py paste <in.jpg> <out.jpg> "<words>" x1,y1,x2,y2,x3,y3,x4,y4 [--font anton|archivo|bebas|serif|hand|sans]
        [--colour r,g,b] [--opacity 0.9] [--mode ink|paint|glow] [--rough 0.6]
     corners in pixels: top-left, top-right, bottom-right, bottom-left; "|" starts a new line.
     ink   = multiplied into the paint (marker on cardboard, ink on paper)
     paint = laid on top (a printed banner, a sticker)
     glow  = added light with a soft halo (a screen, a hologram)
  LOOK at the result at 3x before you keep it."""
import os, sys
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
FONTS = {'anton': D + '/Anton-Regular.ttf', 'archivo': D + '/ArchivoBlack-Regular.ttf', 'bebas': D + '/BebasNeue-Regular.ttf',
         'serif': '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', 'sans': '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
         'hand': '/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf'}


def _line(text, font, px):
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
    f = ImageFont.truetype(font, px); l, t, r, b = f.getbbox(text)
    im = Image.new('L', (r - l + px, b - t + px), 0); ImageDraw.Draw(im).text((px // 2 - l, px // 2 - t), text, font=f, fill=255)
    a = np.array(im).astype(np.float32) / 255; ys, xs = np.where(a > 0.05)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def paste(src, dst, text, quad, font='anton', colour=(20, 16, 12), opacity=0.9, mode='ink', rough=0.6):
    import cv2, numpy as np
    font = FONTS.get(font, font); im = cv2.imread(src); H, W = im.shape[:2]; q = np.float32(quad).reshape(4, 2)
    lines = [x.strip() for x in text.split('|') if x.strip()]
    wq = int(max(np.linalg.norm(q[1] - q[0]), np.linalg.norm(q[2] - q[3]))); hq = int(max(np.linalg.norm(q[3] - q[0]), np.linalg.norm(q[2] - q[1])))
    SS = 3; bw, bh = wq * SS, hq * SS; box = np.zeros((bh, bw), np.float32); lh = bh // len(lines)
    scales = []
    for ln in lines:
        a = _line(ln, font, max(24, int(lh * 0.8))); scales.append(min(bw * 0.92 / a.shape[1], lh * 0.78 / a.shape[0]))
    s0 = min(scales)                                                         # one letter size for every line
    for k, ln in enumerate(lines):
        a = _line(ln, font, max(24, int(lh * 0.8))); a = cv2.resize(a, (max(1, int(a.shape[1] * s0)), max(1, int(a.shape[0] * s0))), interpolation=cv2.INTER_AREA)
        y = k * lh + (lh - a.shape[0]) // 2; x = (bw - a.shape[1]) // 2; box[y:y + a.shape[0], x:x + a.shape[1]] = np.maximum(box[y:y + a.shape[0], x:x + a.shape[1]], a)
    if rough > 0:
        rng = np.random.default_rng(len(text) * 7919 + wq); n = cv2.GaussianBlur(rng.random((bh, bw)).astype(np.float32), (0, 0), max(1.0, bh / 40))
        n = (n - n.min()) / (n.max() - n.min() + 1e-6); box = box * (1 - 0.35 * rough * n)
    box = cv2.GaussianBlur(box, (0, 0), SS * 0.45)
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [bw, 0], [bw, bh], [0, bh]]), q); m = cv2.warpPerspective(box, M, (W, H), flags=cv2.INTER_AREA)[..., None]
    f = im.astype(np.float32); c = np.float32(colour[::-1])
    if mode == 'ink': f = f * (1 - opacity * m) + f * (c / 255) * (opacity * m)
    elif mode == 'paint': f = f * (1 - opacity * m) + c * (opacity * m)
    else:
        halo = cv2.GaussianBlur(m[..., 0], (0, 0), max(2, hq / len(lines) / 6))[..., None]
        f = f + c * (opacity * m) + c * (0.6 * opacity * halo)
    cv2.imwrite(dst, np.clip(f, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 95])


if __name__ == '__main__':
    a = sys.argv[1:]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    rgb = lambda s: tuple(int(x) for x in s.split(','))
    if a[:1] == ['paste'] and len(a) >= 5:
        q = [float(x) for x in a[4].split(',')]; assert len(q) == 8, 'four corners: x1,y1,x2,y2,x3,y3,x4,y4'
        paste(a[1], a[2], a[3], q, opt('--font', 'anton'), rgb(opt('--colour', '20,16,12')), float(opt('--opacity', 0.9)), opt('--mode', 'ink'), float(opt('--rough', 0.6)))
        print(a[2], '|', a[3])
    else: sys.exit(__doc__)
