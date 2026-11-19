#!/usr/bin/env python3
"""SIIL Ostomy teaser, drawn, animated and scored entirely in code.

numpy + Pillow + ffmpeg only. No photos, no footage, no AI generators, no samples.
Every shape (sky, bag, hands, belt), every move and every sound is computed here.

    python3 build.py OUT_DIR                 # full video  -> OUT_DIR/siil_teaser.mp4
    python3 build.py OUT_DIR --frames 30,150 # preview stills + contact sheet only
Env: CAPTION (default "COMING SOON")
"""
import sys, os, math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

W, H, FPS, DUR = 1080, 1920, 30, 18.0
N = int(DUR * FPS)
CAPTION = os.environ.get("CAPTION", "COMING SOON")
BRAND = "SIIL OSTOMY"
FONT = "/usr/share/fonts/truetype/freefont/FreeSerif.ttf"
A = {}


# ---------------------------------------------------------------- helpers
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def sstep(a, b, t):
    u = clamp((t - a) / (b - a))
    return u * u * (3 - 2 * u)


def lerp(a, b, u):
    return a + (b - a) * u


def lerp2(p, q, u):
    return (lerp(p[0], q[0], u), lerp(p[1], q[1], u))


def ease_out(u):
    return 1 - (1 - clamp(u)) ** 3


def catmull(pts, n=14):
    P = np.array(pts, float)
    P = np.vstack([P[0], P, P[-1]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-2])
    return np.array(out)


def arc(c, r, p_start, toward, n=24):
    a0 = math.atan2(p_start[1] - c[1], p_start[0] - c[0])
    best = None
    for sgn in (1, -1):
        am = a0 + sgn * math.pi / 2
        mid = (c[0] + r * math.cos(am), c[1] + r * math.sin(am))
        d = (mid[0] - c[0]) * toward[0] + (mid[1] - c[1]) * toward[1]
        if best is None or d > best[0]:
            best = (d, sgn)
    sgn = best[1]
    return [(c[0] + r * math.cos(a0 + sgn * math.pi * k / n), c[1] + r * math.sin(a0 + sgn * math.pi * k / n))
            for k in range(1, n)]


def capsule(d, p0, p1, w, fill):
    d.line([tuple(p0), tuple(p1)], fill=fill, width=max(1, int(round(w))))
    r = w / 2
    for p in (p0, p1):
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=fill)


def blur_arr(a, r):
    im = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r)), np.float32) / 255


def place(spr, piv, T, s, th, sy=1.0):
    """Affine-place a sprite: sprite point piv lands on frame point T, scale s, rotation th, y-squash sy."""
    c, sn = math.cos(th), math.sin(th)
    a, b = c / s, sn / s
    d, e = -sn / (s * sy), c / (s * sy)
    cc = piv[0] - (a * T[0] + b * T[1])
    f = piv[1] - (d * T[0] + e * T[1])
    return spr.transform((W, H), Image.AFFINE, (a, b, cc, d, e, f), resample=Image.BICUBIC)


def fwd(q, piv, T, s, th, sy=1.0):
    dx, dy = q[0] - piv[0], (q[1] - piv[1]) * sy
    c, sn = math.cos(th), math.sin(th)
    return (T[0] + s * (c * dx - sn * dy), T[1] + s * (sn * dx + c * dy))


# ---------------------------------------------------------------- the belt (from the owner's two photos)
# Front view, units of the belt's length (y down 0..1). Long strap at the top, a body that bulges to
# the right, a round opening with a bound edge, seams where the straps meet the body, a hook patch on
# the front of the lower strap, a small zip pull at the top of the bulge. Black fabric.
RIGHT = [(0.029, 0.035), (0.026, 0.13), (0.024, 0.25), (0.030, 0.29), (0.060, 0.35), (0.088, 0.40),
         (0.100, 0.456), (0.092, 0.51), (0.060, 0.566), (0.004, 0.62), (-0.058, 0.675), (-0.092, 0.73),
         (-0.128, 0.84), (-0.160, 0.955)]
LEFT = [(-0.029, 0.035), (-0.031, 0.13), (-0.030, 0.25), (-0.048, 0.35), (-0.087, 0.456),
        (-0.124, 0.566), (-0.146, 0.65), (-0.182, 0.73), (-0.218, 0.84), (-0.250, 0.955)]
XS_ = 1.35                    # the photos show a fuller body than the raw trace: widen
RIGHT = [(x * XS_, y) for x, y in RIGHT]
LEFT = [(x * XS_, y) for x, y in LEFT]
PH = 1700                     # sprite px per belt length (1x)
OX, OY = 0.40, 0.02           # sprite origin offset in belt units
RC = catmull(RIGHT)
LC = catmull(LEFT)


def edge_x(curve, yn):
    return float(np.interp(yn, curve[:, 1], curve[:, 0]))


def strap_c(yn):
    return 0.5 * (edge_x(RC, yn) + edge_x(LC, yn))


def bpx(x, y, k=1.0):
    return ((x + OX) * PH * k, (y + OY) * PH * k)


def build_belt():
    k = 2.0
    cw, ch = int(0.60 * PH * k), int(1.04 * PH * k)
    im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    top_c = ((RC[0] + LC[0]) / 2)
    bot_c = ((RC[-1] + LC[-1]) / 2)
    r_top = float(np.hypot(*(RC[0] - LC[0]))) / 2
    r_bot = float(np.hypot(*(RC[-1] - LC[-1]))) / 2
    ax_b = (bot_c - (RC[-8] + LC[-8]) / 2)
    ax_b = ax_b / np.hypot(*ax_b)
    outline = [tuple(p) for p in RC]
    outline += arc(bot_c, r_bot, RC[-1], ax_b)
    outline += [tuple(p) for p in LC[::-1]]
    outline += arc(top_c, r_top, LC[0], (0, -1))
    poly = [bpx(x, y, k) for x, y in outline]
    FAB, BIND = (24, 24, 28), (11, 11, 13)
    d.polygon(poly, fill=FAB + (255,))
    d.line(poly + [poly[0]], fill=BIND + (255,), width=int(0.0045 * PH * k), joint="curve")
    # seams across the straps
    for yn in (0.25, 0.675):
        p0, p1 = bpx(edge_x(LC, yn), yn, k), bpx(edge_x(RC, yn), yn, k)
        d.line([p0, p1], fill=BIND + (255,), width=7)
        d.line([(p0[0], p0[1] + 8), (p1[0], p1[1] + 8)], fill=(44, 44, 50, 255), width=3)
    # hook patch on the lower strap (front)
    ys = np.linspace(0.862, 0.945, 12)
    pl = [bpx(edge_x(LC, y) + 0.014, y, k) for y in ys]
    pr = [bpx(edge_x(RC, y) - 0.014, y, k) for y in ys]
    patch = pr + pl[::-1]
    d.polygon(patch, fill=(17, 17, 20, 255), outline=(36, 36, 41, 255), width=5)
    rng = np.random.default_rng(3)
    xs0, ys0 = min(p[0] for p in patch), min(p[1] for p in patch)
    xs1, ys1 = max(p[0] for p in patch), max(p[1] for p in patch)
    pm = Image.new("L", im.size, 0)
    ImageDraw.Draw(pm).polygon(patch, fill=255)
    pma = np.asarray(pm)
    for _ in range(2600):
        x, y = rng.uniform(xs0, xs1), rng.uniform(ys0, ys1)
        if pma[int(y), int(x)] and not (abs(x - xs0) < 12 or abs(x - xs1) < 12):
            d.point((x, y), fill=(30, 30, 35, 255))
    # round opening with bound edge, slight gathers to its right
    rx, ry, rr = -0.046, 0.43, 0.038
    c = bpx(rx, ry, k)
    R = rr * PH * k
    for j in range(9):
        a = -0.9 + j * 0.22 + rng.uniform(-0.05, 0.05)
        p0 = (c[0] + 1.25 * R * math.cos(a), c[1] + 1.25 * R * math.sin(a))
        p1 = (c[0] + (1.55 + rng.uniform(0, 0.3)) * R * math.cos(a), c[1] + (1.55 + rng.uniform(0, 0.3)) * R * math.sin(a))
        d.line([p0, p1], fill=(16, 16, 19, 255), width=6)
    d.ellipse([c[0] - 1.17 * R, c[1] - 1.17 * R, c[0] + 1.17 * R, c[1] + 1.17 * R], fill=(13, 13, 15, 255))
    d.ellipse([c[0] - R, c[1] - R, c[0] + R, c[1] + R], fill=(7, 7, 8, 255))
    d.arc([c[0] - 1.10 * R, c[1] - 1.10 * R, c[0] + 1.10 * R, c[1] + 1.10 * R], 190, 300, fill=(58, 58, 66, 255), width=5)
    # zip pull at the top of the bulge
    zx, zy = edge_x(RC, 0.30), 0.30
    p = bpx(zx, zy, k)
    d.rounded_rectangle([p[0] - 10, p[1] - 6, p[0] + 34, p[1] + 10], 6, fill=(34, 34, 40, 255))
    d.ellipse([p[0] + 22, p[1] - 3, p[0] + 30, p[1] + 5], fill=(150, 150, 160, 255))
    im = im.resize((cw // 2, ch // 2), Image.LANCZOS)
    arr = np.asarray(im, np.float32).copy()
    a = arr[..., 3] / 255
    rim = np.clip((a - blur_arr(a, 5)) * 2.6, 0, 1)
    hh, ww = a.shape
    yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
    bx, by = bpx(0.06, 0.46)
    sheen = np.exp(-(((xx - bx) / (0.07 * PH)) ** 2 + ((yy - by) / (0.10 * PH)) ** 2))
    noise = np.random.default_rng(5).normal(0, 1.6, a.shape)
    for ch_, rimc in zip(range(3), (62, 72, 96)):
        arr[..., ch_] += (rimc * rim + 20 * sheen + noise) * a
    A["belt"] = arr
    A["belt_rows"] = (np.arange(hh, dtype=np.float32) / PH - OY)[:, None]
    A["g_top"] = bpx(strap_c(0.10), 0.10)
    A["g_bot"] = bpx(strap_c(0.93), 0.93)
    A["b_piv"] = lerp2(A["g_top"], A["g_bot"], 0.5)


def belt_sprite(fold):
    """fold 0 = folded bundle (shaded creases), 1 = flat."""
    arr = A["belt"]
    if fold >= 0.999:
        return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    yn = A["belt_rows"]
    k = 1 - fold
    ph = 2 * math.pi * 4.5 * yn + 0.8
    shade = 1 - k * 0.42 * (0.5 + 0.5 * np.sin(ph)) ** 2
    hi = k * 22 * np.maximum(0, np.sin(ph + 1.9)) ** 10
    out = arr.copy()
    out[..., :3] = out[..., :3] * shade[..., None] + hi[..., None] * (out[..., 3:4] / 255)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


# ---------------------------------------------------------------- the hand (original, drawn from shapes)
U = 450                         # sprite px per hand length (wrist to middle fingertip), 1x
HX0, HY0 = 0.5, 2.3             # sprite origin offset in hand units
SKIN, SKIN_D, CREASE = (224, 172, 142), (168, 112, 88), (196, 140, 114)
GOLD, GOLD_H = (205, 160, 70), (250, 226, 150)
FINGERS = [  # name, base x, length, width, spread angle (rad)
    ("index", -0.150, 0.44, 0.088, -0.10),
    ("middle", -0.048, 0.52, 0.091, -0.02),
    ("ring", 0.055, 0.48, 0.086, 0.05),
    ("pinky", 0.150, 0.37, 0.075, 0.13),
]
assert len(FINGERS) == 4  # + one thumb = five digits per hand


def hpx(x, y, k=1.0):
    return ((x + HX0) * U * k, (y + HY0) * U * k)


def build_hand():
    k = 2.0
    cw, ch = int(1.0 * U * k), int(3.4 * U * k)
    hand = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    thumb = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(hand)
    o = 0.012 * U * k
    for name, bx, ln, w, ang in FINGERS[::-1]:
        p0 = np.array(hpx(bx, 0.40, k))
        p1 = p0 + np.array([math.sin(ang), math.cos(ang)]) * ln * U * k
        capsule(d, p0, p1, w * U * k + o, SKIN_D + (255,))
        capsule(d, p0, p1, w * U * k, SKIN + (255,))
        dirv = (p1 - p0) / np.linalg.norm(p1 - p0)
        nrm = np.array([-dirv[1], dirv[0]])
        for fr in (0.36, 0.68):
            q = p0 + (p1 - p0) * (0.25 + 0.75 * fr)
            hw = 0.3 * w * U * k
            d.line([tuple(q - nrm * hw), tuple(q + nrm * hw)], fill=CREASE + (255,), width=3)
        if name in ("ring", "index"):
            q = p0 + (p1 - p0) * (0.40 if name == "ring" else 0.42)
            hw = 0.5 * w * U * k + 3
            bw = (0.026 if name == "ring" else 0.014) * U * k
            d.line([tuple(q - nrm * hw), tuple(q + nrm * hw)], fill=GOLD + (255,), width=int(bw))
            d.line([tuple(q - nrm * hw * 0.7 - dirv * bw * 0.2), tuple(q + nrm * hw * 0.2 - dirv * bw * 0.2)],
                   fill=GOLD_H + (255,), width=max(2, int(bw * 0.35)))
    palm = catmull([(-0.20, -0.02), (0.18, -0.02), (0.215, 0.20), (0.21, 0.42), (0.12, 0.49), (-0.02, 0.50),
                    (-0.15, 0.48), (-0.215, 0.40), (-0.23, 0.20), (-0.20, -0.02)], 10)
    pp = [hpx(x, y, k) for x, y in palm]
    d.polygon(pp, fill=SKIN + (255,), outline=SKIN_D + (255,), width=int(o / 2))
    for line in ([(-0.18, 0.37), (0.0, 0.40), (0.18, 0.35)], [(-0.20, 0.25), (-0.05, 0.27), (0.08, 0.33)],
                 [(-0.13, 0.08), (-0.10, 0.25), (-0.04, 0.44)]):
        d.line([hpx(x, y, k) for x, y in catmull(line, 8)], fill=CREASE + (255,), width=4)
    sl = [(-0.26, 0.07), (0.24, 0.07), (0.34, -2.28), (-0.36, -2.28)]
    d.polygon([hpx(x, y, k) for x, y in sl], fill=(28, 30, 39, 255))
    for x0, x1 in ((-0.18, -0.08), (0.02, 0.10), (-0.24, -0.26), (0.12, 0.24)):
        d.line([hpx(x0, -0.2, k), hpx(x1, -1.6, k)], fill=(17, 18, 24, 255), width=10)
    d.line([hpx(-0.26, 0.06, k), hpx(0.24, 0.06, k)], fill=(46, 49, 62, 255), width=8)
    # thumb, on its own layer so it can sit in front of what the hand grips
    t = ImageDraw.Draw(thumb)
    base = np.array(hpx(-0.17, 0.15, k))
    dirv = np.array([math.sin(-0.55), math.cos(-0.55)])
    mid = base + dirv * 0.21 * U * k
    tip = mid + np.array([math.sin(-0.40), math.cos(-0.40)]) * 0.19 * U * k
    t.ellipse([*hpx(-0.24, 0.08, k), *hpx(-0.08, 0.34, k)], fill=SKIN_D + (255,))
    capsule(t, base, mid, 0.115 * U * k + o, SKIN_D + (255,))
    capsule(t, mid, tip, 0.098 * U * k + o, SKIN_D + (255,))
    t.ellipse([*hpx(-0.235, 0.085, k), *hpx(-0.085, 0.335, k)], fill=SKIN + (255,))
    capsule(t, base, mid, 0.115 * U * k, SKIN + (255,))
    capsule(t, mid, tip, 0.098 * U * k, SKIN + (255,))
    nrm = np.array([-dirv[1], dirv[0]])
    t.line([tuple(mid - nrm * 18), tuple(mid + nrm * 18)], fill=CREASE + (255,), width=3)

    def finish(im):
        im = im.resize((cw // 2, ch // 2), Image.LANCZOS)
        arr = np.asarray(im, np.float32).copy()
        a = arr[..., 3] / 255
        vol = blur_arr(a, 9)
        arr[..., :3] *= (0.70 + 0.30 * vol)[..., None]
        return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    A["hand"], A["thumb"] = finish(hand), finish(thumb)
    A["hand_m"], A["thumb_m"] = ImageOps.mirror(A["hand"]), ImageOps.mirror(A["thumb"])
    A["h_w"] = A["hand"].size[0]
    A["h_grip"] = hpx(-0.02, 0.58)
    A["h_palm"] = hpx(0.0, 0.30)


def put_hand(layers, T, hl, th, piv_key="h_grip", mirror=False, blur=0.0):
    piv = A[piv_key]
    if mirror:
        piv = (A["h_w"] - piv[0], piv[1])
    s = hl / U
    h = place(A["hand_m" if mirror else "hand"], piv, T, s, th)
    tb = place(A["thumb_m" if mirror else "thumb"], piv, T, s, th)
    if blur > 0.3:
        h, tb = h.filter(ImageFilter.GaussianBlur(blur)), tb.filter(ImageFilter.GaussianBlur(blur))
    layers[0].append(h)
    layers[1].append(tb)


# ---------------------------------------------------------------- sky, text, cards
def build_static():
    rng = np.random.default_rng(11)
    hh, ww = H + 80, W + 80
    y = np.linspace(0, 1, hh)[:, None]
    top, bot = np.array([30, 104, 206.0]), np.array([150, 202, 242.0])
    sky = top * (1 - y[..., None] ** 1.2) + bot * (y[..., None] ** 1.2)
    sky = np.broadcast_to(sky, (hh, ww, 3)).copy()
    yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
    glow = np.exp(-(((xx - 820) / 520) ** 2 + ((yy - 1650) / 700) ** 2))
    sky += glow[..., None] * np.array([40, 30, 10.0])
    n = np.zeros((hh, ww), np.float32)
    for g, amp in ((7, 1.0), (15, 0.5), (31, 0.25)):
        small = rng.random((g * 2, g)).astype(np.float32)
        n += amp * np.asarray(Image.fromarray(small).resize((ww, hh), Image.BICUBIC))
    cloud = np.clip((n / 1.75 - 0.58) * 3.0, 0, 1) * 0.35
    sky = sky * (1 - cloud[..., None]) + 255 * cloud[..., None]
    sky += rng.normal(0, 0.8, sky.shape)
    A["sky"] = np.clip(sky, 0, 255).astype(np.uint8)

    def spaced(draw, cx, cy, text, font, track, fill):
        widths = [draw.textlength(ch, font=font) for ch in text]
        total = sum(widths) + track * (len(text) - 1)
        x = cx - total / 2
        for ch, wd in zip(text, widths):
            draw.text((x, cy), ch, font=font, fill=fill, anchor="lm")
            x += wd + track
        return total

    cap = Image.new("L", (W, H), 0)
    dc = ImageDraw.Draw(cap)
    f_big = ImageFont.truetype(FONT, 124)
    while spaced(ImageDraw.Draw(Image.new("L", (1, 1))), 0, 0, CAPTION, f_big, 8, 0) > W - 140:
        f_big = ImageFont.truetype(FONT, f_big.size - 6)
    spaced(dc, W / 2, 1690, CAPTION, f_big, 8, 255)
    spaced(dc, W / 2, 1572, BRAND, ImageFont.truetype(FONT, 50), 14, 255)
    capa = np.asarray(cap, np.float32) / 255
    A["cap_a"] = capa
    A["cap_sh"] = blur_arr(capa, 10) * 0.55

    card = np.full((H, W, 3), (250, 249, 246), np.float32)
    txt = Image.new("L", (W, H), 0)
    dt = ImageDraw.Draw(txt)
    spaced(dt, W / 2, 900, "SIIL", ImageFont.truetype(FONT, 230), 36, 255)
    spaced(dt, W / 2, 1065, "OSTOMY", ImageFont.truetype(FONT, 74), 30, 255)
    dt.line([(W / 2 - 120, 1150), (W / 2 + 120, 1150)], fill=150, width=2)
    A["card"] = card
    A["card_txt"] = np.asarray(txt, np.float32) / 255


XS = np.arange(W, dtype=np.float32)[None, :]
YS = np.arange(H, dtype=np.float32)


def bag_edges(out, t):
    op = sstep(0.5, 2.6, t)
    bL, bR = lerp(300, 95, op), lerp(290, 95, op)
    corner = 170 * np.exp(-(YS / 300) ** 2) + 170 * np.exp(-((H - YS) / 300) ** 2)
    eL = bL + 18 * np.sin(2 * np.pi * YS / 700 + 0.6 * t) + 9 * np.sin(2 * np.pi * YS / 230 + 1.3 + 0.9 * t) + corner
    eR = W - (bR + 20 * np.sin(2 * np.pi * YS / 760 + 2 + 0.5 * t) + 8 * np.sin(2 * np.pi * YS / 190 + 0.4 + 1.1 * t) + corner)
    for e, sgn in ((eL, 1), (eR, -1)):
        dd = sgn * (e[:, None] - XS)
        occ = np.where(dd < 0, 1 - 0.30 * np.exp(np.minimum(dd, 0) / 70), 1.0)
        a = np.clip(dd + 0.5, 0, 1)[..., None]
        rim = np.exp(-np.clip(dd, 0, None) / 12)
        fold = 7 * np.sin(XS * 0.021 * sgn + YS[:, None] * 0.013 + t * 0.3)
        stitch = ((np.abs(dd - 28) < 1.6) & ((YS[:, None] // 18) % 2 == 0)) * 36.0
        base = fold + stitch
        fab = np.stack([16 + 66 * rim + base, 17 + 76 * rim + base, 22 + 98 * rim + base], -1)
        out *= occ[..., None] * (1 - a)
        out += fab * a
    return eL


# ---------------------------------------------------------------- one frame
def frame(i):
    t = i / FPS
    shx = 10 * math.sin(t * 0.9) + 4 * math.sin(t * 2.3 + 1)
    shy = 8 * math.sin(t * 0.7 + 2) + 3 * math.sin(t * 1.9)
    ox, oy = int(round(40 + shx)), int(round(40 + shy))
    img = Image.fromarray(A["sky"][oy:oy + H, ox:ox + W]).convert("RGBA")

    # belt + the two hands that hold it (outside the bag, behind its rim)
    if t >= 6.15:
        S = 1300 / PH
        if t < 8.0:
            u = ease_out((t - 6.15) / 1.85)
            kz = lerp(5.0, 1.0, u)
            T = lerp2((540, 1250), (560, 760), u)
            th, sy, fold, hth = math.radians(-30), 0.30, 0.0, 0.0
        else:
            v = sstep(8.0, 9.3, t)
            kz = 1.0
            T = lerp2((560, 760), (545, 830), v)
            th = math.radians(lerp(-30, -9, v))
            sy, fold = lerp(0.30, 1.0, v), v
            hth = v
        th += math.radians(1.2 * math.sin(2 * math.pi * t / 3.7)) * sstep(9.0, 10.0, t)
        T = (T[0] + shx * 0.6 + 6 * math.sin(t * 1.3), T[1] + shy * 0.6 + 5 * math.sin(t * 1.7))
        s = S * kz
        bl = max(0.0, (kz - 1.4) * 5)
        layers = ([], [])
        gt = fwd(A["g_top"], A["b_piv"], T, s, th, sy)
        put_hand(layers, gt, 360 * kz, lerp(0.0, th + math.pi / 2, hth), blur=bl)
        if t >= 8.3:
            e = ease_out((t - 8.3) / 0.8)
            gb = fwd(A["g_bot"], A["b_piv"], T, s, th, sy)
            put_hand(layers, (gb[0] - 700 * (1 - e), gb[1] + 220 * (1 - e)), 360, th - math.pi / 2, mirror=True)
        belt = place(belt_sprite(fold), A["b_piv"], T, s, th, sy)
        if bl > 0.3:
            belt = belt.filter(ImageFilter.GaussianBlur(bl))
        for h in layers[0]:
            img.alpha_composite(h)
        img.alpha_composite(belt)
        for h in layers[1]:
            img.alpha_composite(h)

    out = np.asarray(img.convert("RGB"), np.float32).copy()
    eL = bag_edges(out, t)
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert("RGBA")

    # hand on the bag's rim, opening it
    if t < 3.3:
        ex = ease_out((t - 2.6) / 0.7) if t > 2.6 else 0.0
        yg = 430
        T = (float(eL[yg]) + 12 - 300 * ex, yg - 520 * ex)
        layers = ([], [])
        put_hand(layers, T, 280, math.radians(-60))
        for h in layers[0] + layers[1]:
            img.alpha_composite(h)
    # hand reaching in towards the lens
    if 3.0 <= t < 5.95:
        u = clamp((t - 3.0) / 2.8)
        hl = 300 / (1 - 0.89 * u ** 1.6)
        T = (540 + 30 * math.sin(t * 2.0), lerp(-80, 980, ease_out(u)))
        layers = ([], [])
        put_hand(layers, T, hl, math.radians(4 * math.sin(t * 1.5)), piv_key="h_palm",
                 blur=max(0.0, (hl - 900) / 110))
        for h in layers[0] + layers[1]:
            img.alpha_composite(h)

    out = np.asarray(img.convert("RGB"), np.float32).copy()
    ca = A["cap_a"] * sstep(10.0, 10.7, t)
    if ca.max() > 0:
        sh = A["cap_sh"] * sstep(10.0, 10.7, t)
        out *= (1 - sh[..., None] * 0.6)
        out = out * (1 - ca[..., None]) + 255 * ca[..., None]
    dark = 0.0
    if t < 0.5:
        dark = 1 - sstep(0.0, 0.5, t)
    elif t < 6.9:
        dark = 0.94 * sstep(4.9, 5.8, t) * (1 - sstep(6.15, 6.9, t))
    out *= (1 - dark)
    if t >= 15.0:
        x0 = int(round(W * (1 - ease_out((t - 15.0) / 0.6))))
        if x0 < W:
            card = A["card"].copy()
            ta = A["card_txt"] * sstep(15.5, 16.2, t)
            card = card * (1 - ta[..., None]) + np.array([30, 32, 40.0]) * ta[..., None]
            out[:, x0:] = card[:, :W - x0]
            if x0 > 0:
                sh = np.exp(-np.arange(min(x0, 60))[::-1] / 18.0)[None, :, None]
                out[:, x0 - sh.shape[1]:x0] *= (1 - 0.25 * sh)
    return np.clip(out, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- sound (all synthesised)
def soundtrack(path):
    SR = 44100
    n = int(SR * DUR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(7)

    def band(x, lo, hi):
        X = np.fft.rfft(x)
        f = np.fft.rfftfreq(len(x), 1 / SR)
        X[(f < lo) | (f > hi)] = 0
        return np.fft.irfft(X, len(x))

    def env(a, b, c, d):
        return np.clip((t - a) / (b - a), 0, 1) * np.clip((d - t) / (d - c), 0, 1)

    def norm(x):
        return x / (np.abs(x).max() + 1e-9)

    mix = np.zeros(n)
    mix += 0.05 * norm(band(rng.normal(size=n), 60, 500)) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.13 * t))
    pad = np.zeros(n)
    for f0 in (220.0, 277.18, 329.63, 493.88):
        for det in (-0.6, 0.6):
            pad += np.sin(2 * np.pi * (f0 + det) * t + rng.uniform(0, 6))
    mix += 0.10 * norm(pad) * env(0.5, 3.5, 15.2, 17.6) * (0.85 + 0.15 * np.sin(2 * np.pi * 0.25 * t))
    notes = [659.25, 554.37, 440.0, 493.88, 659.25, 554.37, 739.99, 659.25]
    for j, tt in enumerate(np.arange(9.4, 15.0, 0.7)):
        f0 = notes[j % len(notes)]
        m = t >= tt
        dt = t[m] - tt
        mix[m] += 0.07 * (np.sin(2 * np.pi * f0 * dt) + 0.3 * np.sin(4 * np.pi * f0 * dt)) * np.exp(-dt / 0.55)
    crackle = np.abs(band(rng.normal(size=n), 3, 30))
    rust = norm(band(rng.normal(size=n), 1400, 7500)) * norm(crackle)
    mix += 0.32 * rust * env(3.6, 4.1, 5.3, 5.9)
    mix += 0.36 * rust * env(6.0, 6.3, 7.3, 7.9)
    mix += 0.40 * rust * env(8.0, 8.25, 8.9, 9.3)
    mix += 0.18 * norm(band(rng.normal(size=n), 250, 1800)) * env(8.1, 8.6, 8.8, 9.3)
    mix += 0.16 * norm(band(rng.normal(size=n), 400, 3500)) * env(14.8, 15.25, 15.3, 15.7) ** 2
    m = t >= 15.55
    dt = t[m] - 15.55
    for f0, a in ((880.0, 1.0), (1320.0, 0.5), (1778.0, 0.3)):
        mix[m] += 0.09 * a * np.sin(2 * np.pi * f0 * dt) * np.exp(-dt / 1.6)
    mix *= np.clip((t - 0.5) / 0.15, 0, 1) * np.clip((DUR - t) / 0.8, 0, 1)
    mix = 0.89 * mix / np.abs(mix).max()
    pcm = (mix * 32767).astype(np.int16)
    st = np.stack([pcm, pcm], 1).tobytes()
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(st)


# ---------------------------------------------------------------- main
def main():
    out_dir = sys.argv[1]
    os.makedirs(out_dir, exist_ok=True)
    build_static()
    build_belt()
    build_hand()
    if "--frames" in sys.argv:
        idx = [int(x) for x in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        thumbs = []
        for i in idx:
            im = Image.fromarray(frame(i))
            im.save(os.path.join(out_dir, f"f{i:04d}.png"))
            thumbs.append(im.resize((270, 480)))
        cols = 6
        rows = (len(thumbs) + cols - 1) // cols
        sheet = Image.new("RGB", (270 * cols, 480 * rows), "black")
        for k, im in enumerate(thumbs):
            sheet.paste(im, ((k % cols) * 270, (k // cols) * 480))
        sheet.save(os.path.join(out_dir, "sheet.jpg"), quality=88)
        return
    wav = os.path.join(out_dir, "sound.wav")
    soundtrack(wav)
    mp4 = os.path.join(out_dir, "siil_teaser.mp4")
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                           "-shortest", mp4], stdin=subprocess.PIPE)
    from multiprocessing import Pool
    with Pool(os.cpu_count()) as pool:
        for k, fr in enumerate(pool.imap(frame, range(N), chunksize=4)):
            ff.stdin.write(fr.tobytes())
            if k % 60 == 0:
                print(f"frame {k}/{N}", flush=True)
    ff.stdin.close()
    ff.wait()
    print("done", mp4)


if __name__ == "__main__":
    main()
