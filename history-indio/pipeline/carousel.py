#!/usr/bin/env python3
"""Photo carousel from an episode's own keys: one key per slide, a text band in the reel's caption look, the logo bug.
usage: carousel.py spec.json out_dir
spec: {"keys_dir": "...", "slides": [{"key": "k01", "y": 0.05, "text": "...", "sub": "...", "swipe": true}, ...]}
  y = where the 4:5 window sits in the key (0 = top, 1 = bottom); the 9:16 version shows the whole key.
Writes out_dir/4x5/NN.jpg (1080x1350) and out_dir/9x16/NN.jpg (1080x1920), JPG quality 95. Never stretches; LANCZOS only."""
import json, os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from branding import logo, FB, PLUM, CREAM

YELLOW = '#ffe400'                       # the burned captions' colour (subtitles.py, &H0000E4FF)

def _fit(d, text, size, maxw):
    """Biggest font <= size that fits text in at most two lines of maxw; returns (font, lines)."""
    while size > 40:
        f = ImageFont.truetype(FB, size); words = text.split(); lines = [words[0]]
        for w in words[1:]:
            t = lines[-1] + ' ' + w
            if d.textlength(t, font=f) <= maxw: lines[-1] = t
            else: lines.append(w)
        if len(lines) <= 2 and all(d.textlength(l, font=f) <= maxw for l in lines): return f, lines
        size -= 4
    return f, lines

def _band(im, top, bottom):
    """Soft dark gradient from top to bottom of the frame (behind the words)."""
    W, H = im.size; g = Image.new('L', (1, H), 0)
    for y in range(H):
        a = 0 if y < top else min(1, (y - top) / max(1, bottom - top)) ** 1.2
        g.putpixel((0, y), int(205 * a))
    sh = Image.new('RGBA', (W, H), (12, 6, 14, 255)); sh.putalpha(g.resize((W, H)))
    im.alpha_composite(sh)

def _swipe(im, cx, cy, r=38):
    """Small round mark with a right chevron at the right edge (no words)."""
    d = ImageDraw.Draw(im)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=PLUM + 'd0', outline=YELLOW, width=4)
    for dx in (-10, 10):
        d.line([(cx - 8 + dx, cy - 16), (cx + 8 + dx, cy), (cx - 8 + dx, cy + 16)], fill=YELLOW, width=7, joint='curve')

def render(key_path, slide, size, text_top):
    W, H = size; src = Image.open(key_path).convert('RGB')
    s = W / src.width; big = src.resize((W, round(src.height * s)), Image.LANCZOS)      # upscale, aspect kept
    y0 = round((big.height - H) * slide.get('y', 0.5)) if big.height > H else 0
    im = big.crop((0, y0, W, y0 + H)).convert('RGBA')
    d = ImageDraw.Draw(im)
    f, lines = _fit(d, slide['text'], 92, W - 120)
    if slide.get('break'): lines = [slide['text'][:slide['break']].strip(), slide['text'][slide['break']:].strip()]   # chosen line break
    lh = f.size * 1.18; sub = slide.get('sub')
    fs = ImageFont.truetype(FB, 50) if sub else None
    y = text_top
    _band(im, int(y - 260), int(y + 40))
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        w = d.textlength(l, font=f); x = (W - w) / 2; yy = y + i * lh
        # soft shadow, then plum outline, then yellow fill (the burned-caption look)
        sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).text((x + 4, yy + 6), l, font=f, fill=(0, 0, 0, 200), stroke_width=9, stroke_fill=(0, 0, 0, 200))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6))); d = ImageDraw.Draw(im)
        d.text((x, yy), l, font=f, fill=YELLOW, stroke_width=8, stroke_fill=PLUM)
    if sub:
        yy = y + lh * len(lines) + fs.size * 0.45; w = d.textlength(sub, font=fs)
        d.text(((W - w) / 2, yy), sub, font=fs, fill=CREAM, stroke_width=6, stroke_fill=PLUM)
    lg = logo(280); lg.putalpha(lg.split()[3].point(lambda v: int(v * .92)))
    im.alpha_composite(lg, (40, 40 if H < 1500 else 96))
    if slide.get('swipe'): _swipe(im, W - 58, int(y + lh * len(lines) / 2))
    return im.convert('RGB')

def main(spec_path, out):
    spec = json.load(open(spec_path))
    for fmt, size, top in (('4x5', (1080, 1350), 1010), ('9x16', (1080, 1920), 1440)):
        os.makedirs(os.path.join(out, fmt), exist_ok=True)
        for n, sl in enumerate(spec['slides'], 1):
            p = os.path.join(out, fmt, f'{n:02d}.jpg')
            render(os.path.join(spec['keys_dir'], sl['key'] + '.png'), sl, size, sl.get('top_' + fmt, top)).save(p, quality=95, subsampling=0)
            print(p)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
