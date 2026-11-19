"""Episode 3 compositor: drawn 2D backgrounds, labels and captions over the 3D bike frames.
usage: python3 compose.py FRAMES_DIR OUT_SILENT.mp4 [CONTACT_DIR]
Reads the transparent PNG frames and anchors.json written by render.py; pipes 720x1280 frames to ffmpeg."""
import sys, os, json, math, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FR, OUTV = sys.argv[1], sys.argv[2]
CONTACT = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != '-' else None
_N = json.load(open(sys.argv[4])) if len(sys.argv) > 4 else {}
NARR = _N.get('lines'); RIDE_TITLE = _N.get('ride_title', '1884')   # from narration.py: subtitles follow the voice
W, H, FPS = 720, 1280, 24
HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, '..', '..', 'history-indio', 'pipeline', 'fonts')
def F(name, size): return ImageFont.truetype(os.path.join(FONTS, name), size)
ANTON = lambda s: F('Anton-Regular.ttf', s)
BODY = lambda s: F('ArchivoBlack-Regular.ttf', s)
PAPER, INK, RED, SOFT = (236, 226, 206), (40, 30, 22), (176, 48, 34), (150, 132, 104)

# timeline: (segment, source shot, frames, source-frame function)
SEGS = [('hook', 'hook', 72, lambda i: i), ('turn', 'turn', 168, lambda i: i),
        ('wheel', 'wheel', 144, lambda i: i), ('spokes', 'spokes', 144, lambda i: i),
        ('step', 'step', 144, lambda i: i), ('brake', 'brake', 144, lambda i: i),
        ('explode', 'explode', 192, lambda i: i), ('ride', 'ride', 288, lambda i: i % 16),
        ('outro', 'turn', 144, lambda i: i + 12)]
assert sum(s[2] for s in SEGS) == 60 * FPS
ANCH = {s: {int(k): v for k, v in json.load(open(os.path.join(FR, s, 'anchors.json'))).items()}
        for s in {x[1] for x in SEGS}}

def paper():
    im = Image.new('RGB', (W, H), PAPER); d = ImageDraw.Draw(im)
    for x in range(0, W, 40): d.line([(x, 0), (x, H)], fill=(228, 217, 195), width=1)
    for y in range(0, H, 40): d.line([(0, y), (W, y)], fill=(228, 217, 195), width=1)
    for x in range(0, W, 200): d.line([(x, 0), (x, H)], fill=(219, 207, 183), width=2)
    for y in range(0, H, 200): d.line([(0, y), (W, y)], fill=(219, 207, 183), width=2)
    v = Image.new('L', (W, H), 0); ImageDraw.Draw(v).ellipse([-200, -150, W + 200, H + 150], fill=255)
    v = v.filter(ImageFilter.GaussianBlur(160))
    return Image.composite(im, Image.new('RGB', (W, H), (205, 190, 160)), v)
BG = paper()

def wrap(d, text, font, maxw):
    lines = []
    for para in text.split('\n'):
        cur = ''
        for w_ in para.split():
            t = (cur + ' ' + w_).strip()
            if d.textlength(t, font=font) <= maxw or not cur: cur = t
            else: lines.append(cur); cur = w_
        lines.append(cur)
    return lines

class Layer:
    """A cached RGBA overlay of static text for one segment."""
    def __init__(self): self.im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); self.d = ImageDraw.Draw(self.im)
    def text(self, xy, s, font, fill=INK, anchor='ma'): self.d.text(xy, s, font=font, fill=fill, anchor=anchor)
    def caption(self, s, y=820, size=38, panel=True):
        f = BODY(size); lines = wrap(self.d, s, f, 610); lh = int(size * 1.28); h = lh * len(lines)
        if panel: self.d.rounded_rectangle([40, y - 22, W - 40, y + h + 18], 22, fill=(246, 239, 224, 240), outline=INK, width=3)
        for k, ln in enumerate(lines): self.d.text((W // 2, y + k * lh), ln, font=f, fill=INK, anchor='ma')
        return y + h
    def pill(self, xy, s, size=50, fill=RED):
        f = ANTON(size); w_ = self.d.textlength(s, font=f); x, y = xy
        box = [x - w_ / 2 - 20, y - size * 0.72, x + w_ / 2 + 20, y + size * 0.72]
        self.d.rounded_rectangle(box, 14, fill=fill); self.d.text((x, y), s, font=f, fill=(255, 250, 240), anchor='mm')
        return box

def leader(d, frm, to):
    d.line([frm, to], fill=INK, width=4)
    x, y = to; d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=RED, outline=(255, 250, 240), width=3)

def put(base, layer, a):
    if a <= 0: return
    im = layer.im
    if a < 1: im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * a)))
    base.paste(im, (0, 0), im)

def shadow(base, A):
    (x0, y0), (x1, y1) = A['ground_r'], A['ground_f']
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; hw = abs(x1 - x0) / 2 + 70
    hh = min(46, abs(y1 - y0) / 2 + 16)
    s = 4; m = Image.new('L', (W // s, H // s), 0)
    ImageDraw.Draw(m).ellipse([(cx - hw) / s, (cy - hh) / s, (cx + hw) / s, (cy + hh) / s], fill=90)
    m = m.filter(ImageFilter.GaussianBlur(5)).resize((W, H), Image.BILINEAR)
    base.paste(Image.new('RGB', (W, H), (70, 55, 40)), (0, 0), m)

def fade(i, start=0, n=8): return max(0.0, min(1.0, (i - start) / n))
TAG = 'BIKE HISTORY  ·  EP 3'
def tag(L): L.text((W // 2, 84), TAG, ANTON(30), SOFT)

# ---- static layers -------------------------------------------------------------------------------
L = {}
x = L['hook'] = Layer(); tag(x); x.text((W // 2, 700), '1870s', ANTON(220), RED)
x = L['hook2'] = Layer(); x.caption('Bigger wheel,\nmore speed.', 985, 42, panel=False)
x = L['turn'] = Layer(); tag(x); x.text((W // 2, 730), 'THE PENNY-FARTHING', ANTON(86), INK)
x = L['turn2'] = Layer(); x.caption('Built by Karl Drais\nin Mannheim, Germany.', 875, 38, panel=False)
x = L['turn3'] = Layer(); x.caption('He called it the Laufmaschine:\nthe “running machine”.', 985, 34, panel=False)
CLOSE = {  # segment: (label, anchor, pill position, caption used only without narration)
    'wheel': ('BIG FRONT WHEEL', 'front_wheel', (250, 190), 'Direct drive: a bigger wheel goes further each turn.'),
    'spokes': ('WIRE SPOKES', 'spokes', (230, 190), 'Thin wire spokes, pulled tight.'),
    'step': ('MOUNTING STEP', 'step', (280, 190), 'Step up here to climb on.'),
    'brake': ('SPOON BRAKE', 'brake', (480, 190), 'A spoon presses on the front tyre.'),
}
PILLBOX = {}
for k, (lab, an, pos, cap) in CLOSE.items():
    x = L[k] = Layer(); tag(x); PILLBOX[k] = x.pill(pos, lab)
    x = L[k + '2'] = Layer(); x.caption(cap, 830, 36)
EXL = [('front_wheel', 'FRONT WHEEL'), ('fork', 'FORK'), ('handlebar', 'HANDLEBAR'), ('pedals', 'PEDALS'),
       ('saddle', 'SADDLE'), ('frame', 'FRAME'), ('rear_wheel', 'REAR WHEEL'), ('brake', 'BRAKE')]
def explode_layout():
    A = ANCH['explode'][191]; top = [k for k in EXL if A[k[0]][1] < 520]; bot = [k for k in EXL if k not in top]
    out = {}; x = Layer(); tag(x)
    for group, ys in ((top, (170, 240)), (bot, (790, 860))):
        n = len(group)                                       # spread evenly so pills never touch
        for j, (an, lab) in enumerate(sorted(group, key=lambda k: A[k[0]][0])):
            px = 30 + (W - 60) * (j + 0.5) / n; py = ys[j % 2] if n > 3 else ys[0]
            out[an] = x.pill((px, py), lab, 32, INK)
    return x, out
L['explode'], EXBOX = explode_layout()
x = L['explode2'] = Layer(); x.caption('Eight main parts. Mostly wood, with iron fittings. No pedals, no chain, no gears.', 930, 32, panel=False)
x = L['ride'] = Layer(); tag(x); x.text((W // 2, 975), RIDE_TITLE, ANTON(84), RED)
x = L['ride2'] = Layer(); x.caption('Karl Drais rides out of Mannheim: about 7 km to a coaching inn on the Schwetzingen road, then back.', 800, 34)
x = L['ride3'] = Layer(); x.caption('The round trip takes a little over an hour. Roughly 13 km/h, and no horse.', 800, 34)
x = L['outro'] = Layer(); tag(x); x.caption('Riders used the smooth pavements. Cities banned the machine, and the craze faded.', 740, 34, panel=False)
x = L['outro2'] = Layer(); x.text((W // 2, 900), 'NEXT: AN ENGINE', ANTON(56), RED)
x.text((W // 2, 978), 'EP 4  ·  THE FIRST HARLEY-DAVIDSON', ANTON(40), INK)

# ---- subtitles that follow the voice (replace the fixed captions) -------------------------------
SUBS = []
if NARR:
    for k_ in ('hook2', 'turn2', 'turn3', 'explode2', 'ride2', 'ride3', 'outro') + tuple(c_ + '2' for c_ in CLOSE): L[k_] = Layer()
    SEG0, acc = {}, 0
    for sname, _, n_, _ in SEGS: SEG0[sname] = (acc, acc + n_); acc += n_
    SUBY = dict(hook=(985, 42, False), turn=(875, 36, False), explode=(930, 32, False), ride=(800, 34, True), outro=(740, 34, False))
    shown = [l_ for l_ in NARR if l_['sub']]
    for j_, l_ in enumerate(shown):
        y_, sz, pan = SUBY.get(l_['seg'], (830, 36, True))
        lay = Layer(); lay.caption(l_['sub'], y_, sz, pan)
        g0 = max(SEG0[l_['seg']][0], int(l_['start'] * FPS) - 3)
        nxt = shown[j_ + 1] if j_ + 1 < len(shown) else None
        g1 = SEG0[l_['seg']][1] if not nxt or nxt['seg'] != l_['seg'] else int(nxt['start'] * FPS) - 3
        SUBS.append((lay, g0, g1))

# ---- the drawn ride scene ------------------------------------------------------------------------
def ik(a, b, l1, l2, bend):
    dx, dy = b[0] - a[0], b[1] - a[1]; d = max(1e-6, min(l1 + l2 - 1e-3, math.hypot(dx, dy)))
    ca = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d); t = math.atan2(dy, dx) + bend * math.acos(max(-1, min(1, ca)))
    return (a[0] + l1 * math.cos(t), a[1] + l1 * math.sin(t))
def ride_bg(i, gy):
    im = BG.copy(); d = ImageDraw.Draw(im)
    hz = gy - 190
    pts = [(xx, hz - 26 * math.sin((xx + i * 0.6) / 170.0) - 14 * math.sin((xx + i * 0.6) / 61.0)) for xx in range(-10, W + 20, 10)]
    d.polygon(pts + [(W, gy), (0, gy)], fill=(214, 204, 176)); d.line(pts, fill=SOFT, width=3)
    for k in range(-1, 6):                                   # poplars along the road
        tx = (k * 190 - i * 9) % (190 * 6) - 150; ty = gy - 70
        d.line([(tx, ty), (tx, ty + 60)], fill=INK, width=4)
        d.ellipse([tx - 24, ty - 170, tx + 24, ty + 10], fill=(168, 170, 120), outline=INK, width=3)
    d.rectangle([0, gy - 12, W, gy + 150], fill=(206, 190, 158)); d.line([(0, gy - 12), (W, gy - 12)], fill=INK, width=3)
    for k in range(12):                                      # road marks rush past
        rx = (k * 97 - i * 40) % (97 * 12) - 100; d.line([(rx, gy + 34 + (k % 3) * 22), (rx + 46, gy + 34 + (k % 3) * 22)], fill=SOFT, width=4)
    return im
def rider(d, A, i, near):
    s = abs(A['front_wheel'][0] - A['rear_wheel'][0]) / 0.97; gy = A['ground_r'][1]   # 0.97 m: penny-farthing wheelbase
    hip = (A['seat'][0], A['seat'][1] - 0.05 * s); sh = (hip[0] + 0.20 * s, hip[1] - 0.50 * s)
    foot = tuple(A['foot_l'] if near else A['foot_r'])            # feet on the pedals
    knee = ik(hip, foot, 0.50 * s, 0.50 * s, -1); col = INK if near else (104, 88, 70); w_ = int(0.10 * s)
    d.line([hip, knee, foot], fill=col, width=w_, joint='curve')
    d.line([(foot[0] - 0.05 * s, foot[1]), (foot[0] + 0.11 * s, foot[1])], fill=col, width=int(0.07 * s))
    for p in (hip, knee): d.ellipse([p[0] - w_ / 2, p[1] - w_ / 2, p[0] + w_ / 2, p[1] + w_ / 2], fill=col)
    if not near: return
    d.polygon([(hip[0] - 0.14 * s, hip[1] + 0.26 * s), (hip[0] - 0.10 * s, hip[1] - 0.05 * s), sh, (hip[0] + 0.10 * s, hip[1] + 0.03 * s)], fill=(60, 74, 96), outline=INK)
    d.line([hip, sh], fill=(60, 74, 96), width=int(0.20 * s))
    hand = A['hands']; el = ik(sh, hand, 0.30 * s, 0.30 * s, 1)
    d.line([sh, el, hand], fill=(60, 74, 96), width=int(0.085 * s), joint='curve')
    hd = (sh[0] + 0.07 * s, sh[1] - 0.17 * s); r_ = 0.105 * s
    d.ellipse([hd[0] - r_, hd[1] - r_, hd[0] + r_, hd[1] + r_], fill=(226, 190, 150), outline=INK, width=3)
    d.rectangle([hd[0] - 0.10 * s, hd[1] - 0.36 * s, hd[0] + 0.10 * s, hd[1] - 0.07 * s], fill=INK)
    d.line([(hd[0] - 0.17 * s, hd[1] - 0.07 * s), (hd[0] + 0.17 * s, hd[1] - 0.07 * s)], fill=INK, width=int(0.035 * s))

# ---- frame loop ----------------------------------------------------------------------------------
ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                       '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', OUTV], stdin=subprocess.PIPE)
g = 0; warn = []
for seg, shot, n, fmap in SEGS:
    for i in range(n):
        j = fmap(i); A = ANCH[shot][j]
        bike = Image.open(os.path.join(FR, shot, f'{j:04d}.png')).convert('RGBA')
        if seg == 'ride':
            bob = 3 * math.sin(2 * math.pi * i / 8.0); A = {k: [v[0], v[1] + bob] for k, v in A.items()}
            A['ground_r'][1] -= bob; A['ground_f'][1] -= bob
            im = ride_bg(i, A['ground_r'][1]); d = ImageDraw.Draw(im); shadow(im, A)
            rider(d, A, i, False); im.paste(bike, (0, int(round(bob))), bike); rider(d, A, i, True)
            put(im, L['ride'], fade(i)); put(im, L['ride2'], fade(i, 6) * (1 - fade(i, 138)))
            put(im, L['ride3'], fade(i, 146))
        else:
            im = BG.copy()
            if seg not in CLOSE: shadow(im, A)               # close-ups have no ground in view
            im.paste(bike, (0, 0), bike); d = ImageDraw.Draw(im)
            if seg == 'hook':
                put(im, L['hook'], fade(i, 2, 6)); put(im, L['hook2'], fade(i, 20))
            elif seg == 'turn':
                put(im, L['turn'], fade(i)); put(im, L['turn2'], fade(i, 14)); put(im, L['turn3'], fade(i, 72))
            elif seg in CLOSE:
                lab, an, pos, cap = CLOSE[seg]; b = PILLBOX[seg]
                if i >= 8:
                    leader(d, ((b[0] + b[2]) / 2, b[3] - 2), tuple(A[an]))
                    if not (b[3] + 20 < A[an][1] < 790): warn.append((seg, i, A[an]))
                put(im, L[seg], fade(i, 4)); put(im, L[seg + '2'], fade(i, 16))
            elif seg == 'explode':
                a = fade(i, 62, 10)
                if a > 0:
                    for an, b in EXBOX.items():
                        up = b[1] < 500
                        leader(d, ((b[0] + b[2]) / 2, b[3] - 2 if up else b[1] + 2), tuple(A[an]))
                put(im, L['explode'], a); put(im, L['explode2'], fade(i, 80))
            elif seg == 'outro':
                put(im, L['outro'], fade(i)); put(im, L['outro2'], fade(i, 48))
        for lay, g0, g1 in SUBS:
            if g0 <= g < g1: put(im, lay, min(fade(g, g0, 4), 1 - fade(g, g1 - 3, 3)))
        ff.stdin.write(im.tobytes())
        if CONTACT and g % 36 == 18:
            os.makedirs(CONTACT, exist_ok=True); im.resize((270, 480), Image.LANCZOS).save(os.path.join(CONTACT, f'{g:04d}_{seg}.jpg'), quality=85)
        g += 1
ff.stdin.close(); ff.wait()
print('frames', g, 'label_warnings', len(warn), warn[:3])
