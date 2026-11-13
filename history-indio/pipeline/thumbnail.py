#!/usr/bin/env python3
"""Thumbnail / cover maker: big stacked words, thick outline, season and episode badge, brand tab, on one key picture.
The picture carries the idea (one face, one feeling, one object); this script only frames it and sets the type,
because image models cannot spell. Fonts are open-licence (pipeline/fonts, SIL OFL).

  thumbnail.py make --art art.png --out ep01_thumb.jpg --line "NASA 1896" --line "NA AKO?!" \
      --accent 1896 --season 1 --episode 1 [--pos top|bottom] [--color yellow|red|cyan|white] [--tilt -4]
      [--zoom 1.0 --dx 0 --dy 0] [--size 1080x1920|1280x720] [--font anton|archivo|bebas] [--box 2] [--guides]
      [--brand-pos bl|br|tl|tr|none] --keep face:0.20,0.30,0.80,0.62 --keep medallion:0.40,0.80,0.62,0.93
  thumbnail.py sheet --out sheet.jpg a.jpg b.jpg c.jpg [--labels A B C]

THE FIRST RULE (the owner's): nothing may cover a face or a thing that matters in the story (the medallion, the dog,
the paper, a hand that holds something). Give every such area with --keep name:x0,y0,x1,y1 (fractions of the finished
frame, after zoom and shift). The script measures how much the words, the badge and the brand tab cover each area,
prints BLOCKED lines and exits with code 3 when anything is covered; move the words (--pos, --top), shrink them
(fewer words), move the brand (--brand-pos) or reframe (--zoom, --dx, --dy) until it passes. --guides draws the areas.

Rules the layout follows (vertical covers): everything that matters sits inside the middle 4:5 of the frame (feeds and
profile grids crop to it); at most two lines and four words; the words never repeat the title; one word in the accent
colour; the badge is always top left, the brand always bottom left. `make` also writes <out>_small.jpg (the size a
phone shows in a feed): if the words cannot be read there, use fewer words."""
import argparse, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = {'anton': 'Anton-Regular.ttf', 'archivo': 'ArchivoBlack-Regular.ttf', 'bebas': 'BebasNeue-Regular.ttf'}
COLORS = {'yellow': (255, 226, 0), 'red': (255, 48, 48), 'cyan': (0, 229, 255), 'white': (255, 255, 255), 'orange': (255, 140, 0)}


def font(name, size):
    return ImageFont.truetype(os.path.join(HERE, 'fonts', FONTS[name]), int(size))


def cover(im, W, H, zoom=1.0, dx=0.0, dy=0.0):
    """Fill WxH with the picture (centre crop), zoom >= 1, dx/dy shift the crop by a fraction of the spare room (-1..1)."""
    s = max(W / im.width, H / im.height) * max(1.0, zoom)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = round((im.width - W) / 2 * (1 + dx)); y = round((im.height - H) / 2 * (1 + dy))
    x = min(max(x, 0), im.width - W); y = min(max(y, 0), im.height - H)
    return im.crop((x, y, x + W, y + H))


def grade(im):
    im = ImageEnhance.Contrast(im).enhance(1.12); im = ImageEnhance.Color(im).enhance(1.22)
    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    W, H = im.size                                            # soft vignette: the eye goes to the middle
    v = Image.new('L', (W, H), 0); d = ImageDraw.Draw(v)
    d.ellipse((-W * 0.25, -H * 0.12, W * 1.25, H * 1.12), fill=255)
    v = v.filter(ImageFilter.GaussianBlur(W * 0.18))
    dark = ImageEnhance.Brightness(im).enhance(0.55)
    return Image.composite(im, dark, v)


def scrim(im, pos, strength):
    """Dark gradient behind the words so they read on any picture."""
    W, H = im.size; g = Image.new('L', (1, H), 0)
    for y in range(H):
        t = y / H
        a = max(0.0, 1 - t / 0.46) if pos == 'top' else max(0.0, (t - 0.54) / 0.46)
        g.putpixel((0, y), int(255 * strength * a ** 1.4))
    return Image.composite(Image.new('RGB', (W, H), (0, 0, 0)), im, g.resize((W, H)))


def fit(name, text, width, max_size, stroke_k):
    lo, hi = 20, int(max_size)
    while lo < hi:
        m = (lo + hi + 1) // 2; f = font(name, m)
        if f.getlength(text) + 2 * m * stroke_k <= width: lo = m
        else: hi = m - 1
    return lo


def words_layer(W, H, lines, accent, color, fname, pos, tilt, box, top_frac=None, scale=1.0):
    """The stacked words on a transparent layer: each line as wide as the safe width allows, black outline, shadow."""
    vertical = H > W
    safe_w = W * (0.90 if vertical else 0.62) * scale; stroke_k = 0.085
    max_size = H * (0.150 if vertical else 0.30) if len(lines) > 1 else H * (0.19 if vertical else 0.34)
    sizes = [fit(fname, ln.upper(), safe_w, max_size, stroke_k) for ln in lines]
    gap = lambda s: int(s * 0.04)
    heights = [int(s * 1.02) for s in sizes]; total = sum(heights) + sum(gap(s) for s in sizes[:-1])
    if top_frac is None:
        safe_top = H * (0.165 if vertical else 0.07); safe_bot = H * (0.835 if vertical else 0.93)
        top = safe_top if pos == 'top' else safe_bot - total
    else: top = H * top_frac
    pad = int(max(sizes) * 0.5)
    L = Image.new('RGBA', (W + 2 * pad, H + 2 * pad), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    acc = {a.upper().strip('?!.,') for a in accent}; y = top + pad
    x0 = pad + (W * 0.05 if vertical else W * 0.04)
    for i, (ln, s) in enumerate(zip(lines, sizes)):
        f = font(fname, s); sw = max(3, int(s * stroke_k)); text = ln.upper()
        asc, desc = f.getmetrics(); x = x0 + sw if not vertical else pad + (W - f.getlength(text)) / 2
        if box and i + 1 == box:                              # one line on a solid block, the "label" look
            bx = (x - s * 0.10, y + s * 0.10, x + f.getlength(text) + s * 0.10, y + s * 1.10)
            d.rounded_rectangle(bx, radius=int(s * 0.08), fill=COLORS['red'] + (255,), outline=(0, 0, 0, 255), width=sw // 2)
        for w in text.split(' '):
            fill = color if w.strip('?!.,') in acc else COLORS['white']
            if box and i + 1 == box: fill = COLORS['white']
            d.text((x, y), w, font=f, fill=fill + (255,), stroke_width=0 if (box and i + 1 == box) else sw, stroke_fill=(0, 0, 0, 255))
            x += f.getlength(w + ' ')
        y += heights[i] + gap(s)
    sh = Image.new('RGBA', L.size, (0, 0, 0, 0)); a = L.split()[3]
    off = int(max(sizes) * 0.055)
    sh.paste((0, 0, 0, 215), (off, off), a); sh = sh.filter(ImageFilter.GaussianBlur(max(2, off // 2)))
    L = Image.alpha_composite(sh, L)
    if tilt: L = L.rotate(tilt, resample=Image.BICUBIC, center=(pad + W / 2, pad + top + total / 2))
    return L.crop((pad, pad, pad + W, pad + H)), (top, top + total)


def badge(im, season, episode, tag=None):
    """Top left, always the same place: SEASON n on yellow, EPISODE n on red."""
    W, H = im.size; vertical = H > W; d = ImageDraw.Draw(im)
    u = H * (0.030 if vertical else 0.062); x = W * 0.05; y = H * (0.075 if vertical else 0.06)
    f1 = font('archivo', u * 0.80); f2 = font('anton', u * 1.75); sw = max(3, int(u * 0.10))
    t1 = f'SEASON {season}'; t2 = tag or f'EPISODE {episode}'
    w1 = f1.getlength(t1) + u * 0.9; h1 = u * 1.25; w2 = f2.getlength(t2) + u * 1.0; h2 = u * 2.35
    d.rounded_rectangle((x + u * 0.12, y + u * 0.12, x + max(w1, w2) + u * 0.12, y + h1 + h2 + u * 0.12), radius=int(u * 0.25), fill=(0, 0, 0))
    d.rounded_rectangle((x, y, x + w1, y + h1), radius=int(u * 0.22), fill=COLORS['yellow'], outline=(0, 0, 0), width=sw)
    d.text((x + u * 0.45, y + h1 / 2), t1, font=f1, fill=(0, 0, 0), anchor='lm')
    d.rounded_rectangle((x, y + h1 - sw, x + w2, y + h1 + h2), radius=int(u * 0.25), fill=(214, 20, 30), outline=(0, 0, 0), width=sw)
    d.text((x + u * 0.5, y + h1 + h2 / 2 - sw / 2), t2, font=f2, fill=(255, 255, 255), anchor='lm')
    return im, (x, y, x + max(w1, w2) + u * 0.12, y + h1 + h2 + u * 0.12)


def brand(im, name='HISTORY INDIO', pos='bl'):
    W, H = im.size; vertical = H > W; d = ImageDraw.Draw(im)
    u = H * (0.024 if vertical else 0.05); f = font('archivo', u)
    w = f.getlength(name) + u * 1.2
    x = W * 0.05 if pos[1] == 'l' else W * 0.95 - w
    y = H * (0.872 if vertical else 0.90) if pos[0] == 'b' else H * (0.082 if vertical else 0.07)
    d.rounded_rectangle((x, y, x + w, y + u * 1.7), radius=int(u * 0.3), fill=(0, 0, 0), outline=COLORS['yellow'], width=max(2, int(u * 0.10)))
    d.text((x + u * 0.6, y + u * 0.85), name, font=f, fill=COLORS['yellow'], anchor='lm')
    return im, (x, y, x + w, y + u * 1.7)


def overlap(r, k):
    w = min(r[2], k[2]) - max(r[0], k[0]); h = min(r[3], k[3]) - max(r[1], k[1])
    return max(0.0, w) * max(0.0, h) / max(1e-9, (k[2] - k[0]) * (k[3] - k[1]))


def make(a):
    W, H = (int(v) for v in a.size.lower().split('x'))
    im = Image.open(a.art).convert('RGB'); im = cover(im, W, H, a.zoom, a.dx, a.dy); im = grade(im)
    rects = {}
    if a.line:
        im = scrim(im, a.pos, a.scrim)
        layer, _ = words_layer(W, H, a.line, a.accent or [], COLORS[a.color], a.font, a.pos, a.tilt, a.box, a.top, a.scale)
        solid = layer.split()[3].point(lambda v: 255 if v > 200 else 0)        # the letters and outline, not the soft shadow
        if solid.getbbox(): rects['words'] = solid.getbbox()
        im = Image.alpha_composite(im.convert('RGBA'), layer).convert('RGB')
    if a.season: im, rects['badge'] = badge(im, a.season, a.episode, a.tag)
    if a.brand_pos != 'none': im, rects['brand tab'] = brand(im, pos=a.brand_pos)
    keeps = []
    for k in a.keep or []:
        name, box = k.split(':'); x0, y0, x1, y1 = (float(v) for v in box.split(','))
        keeps.append((name, (x0 * W, y0 * H, x1 * W, y1 * H)))
    blocked = [(n, e, overlap(r, kb)) for n, kb in keeps for e, r in rects.items() if overlap(r, kb) > 0.01]
    if 'words' in rects:                                      # the words must not sit on the badge or the brand tab either
        blocked += [('the ' + e, 'words', overlap(rects['words'], r)) for e, r in rects.items() if e != 'words' and overlap(rects['words'], r) > 0.01]
    if a.guides:                                              # the middle 4:5 (green) and the keep-clear areas (cyan)
        d = ImageDraw.Draw(im); h45 = W * 5 / 4; y0 = (H - h45) / 2
        d.rectangle((2, y0, W - 3, y0 + h45), outline=(0, 255, 0), width=3)
        for n, kb in keeps: d.rectangle(kb, outline=(0, 229, 255), width=4)
    im.save(a.out, quality=93, subsampling=0)
    small = im.resize((270, round(270 * H / W)), Image.LANCZOS); small.save(os.path.splitext(a.out)[0] + '_small.jpg', quality=88)
    print(a.out, im.size)
    if not keeps: print('NOTE: no --keep areas given: nothing checked that faces and story objects are clear')
    for n, e, f in blocked: print(f'BLOCKED: the {e} covers {f:.0%} of {n}')
    if blocked and not a.allow_overlap: sys.exit(3)
    if keeps and not blocked: print('clear: nothing covers ' + ', '.join(n for n, _ in keeps))


def sheet(a):
    ims = [Image.open(p).convert('RGB') for p in a.images]; labels = a.labels or [chr(65 + i) for i in range(len(ims))]
    h = 960; big = [i.resize((round(i.width * h / i.height), h), Image.LANCZOS) for i in ims]
    sm = [i.resize((round(i.width * 240 / i.height), 240), Image.LANCZOS) for i in ims]
    pad = 28; top = 76; W = sum(b.width for b in big) + pad * (len(big) + 1); H = top + h + pad + 60 + 240 + pad
    S = Image.new('RGB', (W, H), (18, 18, 20)); d = ImageDraw.Draw(S); f = font('archivo', 40); fs = font('archivo', 24); x = pad
    for b, s, l in zip(big, sm, labels):
        d.text((x, 18), l, font=f, fill=COLORS['yellow']); S.paste(b, (x, top))
        S.paste(s, (x, top + h + pad + 44)); x += b.width + pad
    d.text((pad, top + h + pad + 6), 'Kasinlaki sa feed ng phone:', font=fs, fill=(200, 200, 200))
    S.save(a.out, quality=92); print(a.out, S.size)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest='cmd', required=True)
    m = sub.add_parser('make'); m.add_argument('--art', required=True); m.add_argument('--out', required=True)
    m.add_argument('--line', action='append', default=[]); m.add_argument('--accent', action='append')
    m.add_argument('--color', default='yellow', choices=list(COLORS)); m.add_argument('--pos', default='bottom', choices=['top', 'bottom'])
    m.add_argument('--top', type=float, help='top of the words as a fraction of the height (overrides --pos placement)')
    m.add_argument('--scale', type=float, default=1.0, help='make the words smaller (0.7 to 1.0) when they would cover something')
    m.add_argument('--tilt', type=float, default=-3.0); m.add_argument('--font', default='anton', choices=list(FONTS))
    m.add_argument('--box', type=int, default=0, help='put line N on a red block'); m.add_argument('--scrim', type=float, default=0.72)
    m.add_argument('--season', type=int); m.add_argument('--episode', type=int); m.add_argument('--tag')
    m.add_argument('--size', default='1080x1920'); m.add_argument('--zoom', type=float, default=1.0)
    m.add_argument('--dx', type=float, default=0.0); m.add_argument('--dy', type=float, default=0.0)
    m.add_argument('--brand-pos', default='bl', choices=['bl', 'br', 'tl', 'tr', 'none']); m.add_argument('--guides', action='store_true')
    m.add_argument('--keep', action='append', help='name:x0,y0,x1,y1 (fractions): an area nothing may cover; repeatable')
    m.add_argument('--allow-overlap', action='store_true', help='save anyway and exit 0 (for looking only, never for a final)')
    s = sub.add_parser('sheet'); s.add_argument('--out', required=True); s.add_argument('images', nargs='+'); s.add_argument('--labels', nargs='*')
    a = p.parse_args(); (make if a.cmd == 'make' else sheet)(a)
