import sys, math, numpy as np, cairo
sys.path.insert(0, '/home/user/REPO-JRLY.portfolio/history-indio/engine')
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageChops, ImageOps
import cast, scenes
W, H = 1080, 1920
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def layer(fn):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s); fn(c); 
    a = np.frombuffer(s.get_data(), np.uint8).reshape(H, W, 4).astype(np.float32)
    al = a[..., 3:4] / 255; rgb = np.where(al > 0, a[..., [2, 1, 0]] / np.maximum(al, 1e-6), 0)
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), al * 255]).astype(np.uint8), 'RGBA')

def grain(img, amt=14, seed=3):
    rng = np.random.default_rng(seed); n = rng.normal(0, amt, (H // 2, W // 2)).astype(np.float32)
    n = np.array(Image.fromarray(n).resize((W, H), Image.BILINEAR))
    a = np.asarray(img.convert('RGB')).astype(np.float32) + n[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

# ---------------- paper cutout
def paper():
    base = Image.new('RGBA', (W, H), '#f3e2c2')
    def put(fn, border=10, sh=(14, 20), blur=14, tint=None):
        nonlocal base
        L = layer(fn); al = L.split()[3]
        if border:
            fat = al.filter(ImageFilter.MaxFilter(border * 2 + 1))
            white = Image.new('RGBA', (W, H), tint or '#fffaf0'); white.putalpha(fat)
            white.alpha_composite(L); L = white; al = fat
        shadow = Image.new('RGBA', (W, H), (40, 20, 30, 0)); shadow.putalpha(al.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * 0.45)))
        base.alpha_composite(ImageChops.offset(shadow, *sh)); base.alpha_composite(L)
    def bgsheet(col, pts):
        def f(c):
            c.move_to(*pts[0]); [c.line_to(*p) for p in pts[1:]]; c.close_path(); c.set_source_rgb(*cast.hexc(col)); c.fill()
        return f
    put(bgsheet('#f6a55c', [(0, 0), (W, 0), (W, 1150), (0, 1250)]), border=0)
    def sun(c): cast.ellipse(c, 250, 380, 190, 190); c.set_source_rgb(*cast.hexc('#ffd86b')); c.fill()
    put(sun, border=0)
    def hill1(c): cast.ellipse(c, 150, 1500, 800, 420); c.set_source_rgb(*cast.hexc('#5fae57')); c.fill()
    def hill2(c): cast.ellipse(c, 950, 1560, 760, 430); c.set_source_rgb(*cast.hexc('#3f8f52')); c.fill()
    put(hill2, border=0); put(hill1, border=0)
    put(bgsheet('#e7c58f', [(0, 1560), (W, 1500), (W, H), (0, H)]), border=0)
    def fist(c):
        c.rectangle(560, 760, 330, 900); c.set_source_rgb(*cast.hexc('#33333c')); c.fill()
        c.rectangle(545, 1010, 360, 90); c.set_source_rgb(*cast.hexc('#d8362e')); c.fill()
        c.rectangle(550, 760, 350, 80); c.set_source_rgb(1, 1, 1); c.fill()
        scenes.fist_icon(c, 725, 590, 2.3, '#e7b98f')
    put(fist, border=12, sh=(20, 28), blur=20)
    put(lambda c: cast.draw_char(c, 'sara', 330, 1700, 1.0, view='q', expr='smug', arms=('pinky', 'down')), border=12)
    put(lambda c: cast.draw_char(c, 'indio', 800, 1820, 0.82, view='q', facing=-1, expr='surprised', arms=('up', 'up')), border=12)
    out = grain(base, 10)
    # fibre texture
    return out

# ---------------- komiks (from the cel-shaded 3D render)
def komiks():
    im = Image.open('out_toon.png').convert('RGB')
    a = np.asarray(im).astype(np.float32) / 255
    lum = a @ np.array([0.3, 0.59, 0.11])
    post = np.round(a * 4) / 4                                   # posterise
    yy, xx = np.mgrid[0:H, 0:W]
    ang = math.radians(35); u = xx * math.cos(ang) + yy * math.sin(ang); v = -xx * math.sin(ang) + yy * math.cos(ang)
    P = 13; d = np.sqrt(((u % P) - P / 2) ** 2 + ((v % P) - P / 2) ** 2)
    r = np.clip((0.78 - lum), 0, 1) * P * 0.85                    # darker = bigger dot
    dots = (d < r).astype(np.float32)
    post = post * (1 - 0.42 * dots[..., None])
    edges = np.asarray(im.convert('L').filter(ImageFilter.GaussianBlur(1.2)).filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(5))).astype(np.float32) / 255
    ink = np.clip(edges * 4 - 0.25, 0, 1)[..., None]
    post = post * (1 - ink) + np.array([0.12, 0.07, 0.12]) * ink
    post = post * np.array([1.0, 0.95, 0.82])                     # newsprint tint
    out = grain(Image.fromarray((np.clip(post, 0, 1) * 255).astype(np.uint8)), 9, 5)
    d = ImageDraw.Draw(out)
    def cap(txt, x, y, size, bg='#ffe45c', rot=0):
        f = ImageFont.truetype(FB, size); w = d.textlength(txt, font=f)
        d.rectangle([x - 8, y - 8, x + w + 44, y + size + 36], fill='#1f121f')
        d.rectangle([x - 18, y - 18, x + w + 32, y + size + 24], fill=bg, outline='#1f121f', width=7)
        d.text((x + 6, y), txt, font=f, fill='#1f121f')
    cap('ISANG HINLILIIT LANG...', 60, 70, 62)
    cap('PERO INABOT NG PALASYO!', 150, 1730, 50, bg='#ffffff')
    d.rectangle([14, 14, W - 14, H - 14], outline='#1f121f', width=14)
    return out

paper().save('out_paper.png'); komiks().save('out_komiks.png'); print('ok')
