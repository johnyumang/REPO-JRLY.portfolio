#!/usr/bin/env python3
"""SIIL Ostomy teaser: the belt is pulled up out of a paper bag, seen from inside the bag.

Pure code (numpy + Pillow + ffmpeg): the kraft-paper bag, its lighting, the sky, the camera,
the motion and the sound are all computed here. The only picture used is the owner's own
photo of the product, cut out by cut.py (kept OUTSIDE this public repository).

    python3 build.py BELT_PNG OUT_DIR                  # full video -> OUT_DIR/siil_teaser.mp4
    python3 build.py BELT_PNG OUT_DIR --frames 30,150  # preview stills + contact sheet
Env: CAPTION (default "COMING SOON")
"""
import sys, os, math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS, DUR = 1080, 1920, 30, 18.0
N = int(DUR * FPS)
CAPTION = os.environ.get("CAPTION", "COMING SOON")
BRAND = "SIIL OSTOMY"
FONT = "/usr/share/fonts/truetype/freefont/FreeSerif.ttf"
CX, CY, HW, HH = 540, 880, 335, 560        # the bag's opening, seen from below
S_END = 0.44                                # belt scale when it hangs outside the bag
PIV = (339, 0)                              # top-strap centre in the cut-out (photo's top edge)
A = {}


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def sstep(a, b, t):
    u = clamp((t - a) / (b - a))
    return u * u * (3 - 2 * u)


def lerp(a, b, u):
    return a + (b - a) * u


def ease_out(u):
    return 1 - (1 - clamp(u)) ** 3


def blur(a, r):
    im = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r)), np.float32) / 255


def noise(rng, gw, gh, w=W, h=H):
    """Smooth value noise 0..1 at a given grid density."""
    g = rng.random((gh, gw)).astype(np.float32)
    return np.asarray(Image.fromarray(g).resize((w, h), Image.BICUBIC), np.float32).clip(0, 1)


def affine(img, piv, T, s, th):
    c, sn = math.cos(th), math.sin(th)
    a, b, d, e = c / s, sn / s, -sn / s, c / s
    return img.transform((W, H), Image.AFFINE,
                         (a, b, piv[0] - (a * T[0] + b * T[1]), d, e, piv[1] - (d * T[0] + e * T[1])),
                         resample=Image.BICUBIC)


# ---------------------------------------------------------------- the bag, sky, text (computed once)
def build_static(belt_png):
    rng = np.random.default_rng(11)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

    # opening: rounded rectangle with a wavy, serrated paper edge
    pts = []
    ph = rng.uniform(0, 6.28, 6)
    for a in np.linspace(0, 2 * np.pi, 1600, endpoint=False):
        c, s = math.cos(a), math.sin(a)
        f = (1 + 0.020 * math.sin(3 * a + ph[0]) + 0.014 * math.sin(7 * a + ph[1]) + 0.008 * math.sin(17 * a + ph[2])
             + 0.006 * math.sin(41 * a + ph[3]) + 0.0045 * abs(((a * 150 / np.pi) % 2) - 1))
        pts.append(((CX + HW * f * math.copysign(abs(c) ** (2 / 7), c)) * 2,
                    (CY + HH * f * math.copysign(abs(s) ** (2 / 7), s)) * 2))
    m = Image.new("L", (W * 2, H * 2), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    O = np.asarray(m.resize((W, H), Image.LANCZOS), np.float32) / 255

    # kraft paper walls: four planes running from the rim towards the lens, lit through the opening
    g1 = blur(O, 30)
    u, v = (xx - CX) / HW, (yy - CY) / HH
    q = np.maximum(np.abs(u), np.abs(v))                       # 1 at the rim, grows towards the lens
    depth = np.clip((q - 1) / 0.85, 0, 1)
    tone = 0.88 + 0.24 * (0.6 * noise(rng, 5, 9) + 0.4 * noise(rng, 24, 42))
    fib = (noise(rng, 200, 1900) - 0.5) * 0.09 + (noise(rng, 1000, 320) - 0.5) * 0.05 + rng.normal(0, 0.012, (H, W))
    cr = Image.new("L", (W, H), 0)                              # a few long, straight handling creases
    dcr = ImageDraw.Draw(cr)
    for _ in range(26):
        x0, y0, ang, ln = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0, np.pi), rng.uniform(250, 900)
        dcr.line([(x0, y0), (x0 + ln * math.cos(ang), y0 + ln * math.sin(ang))], fill=int(rng.uniform(90, 255)), width=2)
    hgt = blur(np.asarray(cr, np.float32) / 255, 1.6) + 0.5 * noise(rng, 6, 10)
    gy, gx = np.gradient(hgt)
    dist = np.hypot(CX - xx, CY - yy) + 1
    shade = (gx * (CX - xx) + gy * (CY - yy)) / dist * 5
    side = np.where(np.abs(u) > np.abs(v), np.where(u < 0, 0.86, 1.10), np.where(v < 0, 0.78, 1.0))
    side = blur(side / 1.2, 2.5) * 1.2
    seam = np.exp(-(((np.abs(u) - np.abs(v)) * 360) / 3.0) ** 2)
    folds = sum(np.exp(-((q - qq) * 360 / 2.2) ** 2) for qq in (1.27, 1.58))       # flat-pack folds, parallel to the rim
    folds_hi = sum(np.exp(-((q - qq - 0.012) * 360 / 3.0) ** 2) for qq in (1.27, 1.58))
    gus = np.exp(-((yy - CY - 30) / 2.4) ** 2) * (np.abs(u) > np.abs(v))           # gusset fold on each side wall
    light = lerp(1.18, 0.42, depth ** 0.8) * side * (1 + shade) * (1 - 0.38 * seam) * (1 - 0.30 * folds + 0.10 * folds_hi) * (1 - 0.28 * gus)
    kraft = np.array([203, 150, 97], np.float32)
    wall = kraft * ((tone + fib) * light)[..., None]
    wall += np.array([255, 170, 80], np.float32) * (0.22 * g1 ** 1.6 * (1 - O))[..., None]   # sun glowing through thin paper
    edge = blur(O, 2.2) * (1 - O)
    wall += np.array([255, 232, 190], np.float32) * (0.45 * edge)[..., None]                 # the cut edge catches the sky
    far = depth ** 1.5                                                                        # nearer the lens: softer
    soft = np.asarray(Image.fromarray(np.clip(wall, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(11)), np.float32)
    wall = wall * (1 - far[..., None]) + soft * far[..., None]
    wall *= (1 - 0.35 * np.clip(dist / 1150, 0, 1) ** 3)[..., None]
    rgba = np.dstack([np.clip(wall, 0, 255), (1 - O) * 255]).astype(np.uint8)
    A["bag"] = Image.fromarray(rgba, "RGBA")

    # sky
    hh, ww = H + 120, W + 120
    y2, x2 = np.mgrid[0:hh, 0:ww].astype(np.float32)
    d = (y2 / hh) * 0.75 + (1 - x2 / ww) * 0.25
    sky = np.array([44, 112, 204], np.float32) * (1 - d[..., None]) + np.array([118, 176, 236], np.float32) * d[..., None]
    sun = np.exp(-(((x2 - 900) / 380) ** 2 + ((y2 - 520) / 420) ** 2))
    sky += sun[..., None] * np.array([70, 60, 36], np.float32)
    n = sum(amp * noise(rng, gw, gh, ww, hh) for gw, gh, amp in ((4, 7, 1.0), (9, 16, 0.5), (19, 34, 0.25), (40, 70, 0.12)))
    cloud = np.clip((n / 1.87 - 0.56) * 3.2, 0, 1) ** 1.3 * 0.55
    sky = sky * (1 - cloud[..., None]) + np.array([250, 250, 252], np.float32) * cloud[..., None]
    A["sky"] = np.clip(sky, 0, 255).astype(np.float32)

    # the belt: owner's photo, graded for a backlit object under open sky
    b = np.asarray(Image.open(belt_png).convert("RGBA"), np.float32).copy()
    al = b[..., 3] / 255
    rgb = (b[..., :3] - 12) * 1.55 * np.array([0.96, 0.99, 1.05], np.float32)
    rim = np.clip((al - blur(al, 7)) * 2.4, 0, 1)
    rgb += rim[..., None] * np.array([95, 125, 170], np.float32) * 0.35
    bi = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).filter(ImageFilter.UnsharpMask(6, 90, 2))
    A["belt"] = Image.merge("RGBA", (*bi.split(), Image.fromarray(b[..., 3].astype(np.uint8))))

    # text
    def spaced(draw, cx, cy, text, font, track, fill):
        ws = [draw.textlength(ch, font=font) for ch in text]
        x = cx - (sum(ws) + track * (len(text) - 1)) / 2
        for ch, wd in zip(text, ws):
            draw.text((x, cy), ch, font=font, fill=fill, anchor="lm")
            x += wd + track

    cap = Image.new("L", (W, H), 0)
    dc = ImageDraw.Draw(cap)
    size = 116
    while sum(dc.textlength(ch, font=ImageFont.truetype(FONT, size)) + 8 for ch in CAPTION) > W - 170:
        size -= 4
    spaced(dc, CX, 1722, CAPTION, ImageFont.truetype(FONT, size), 8, 255)
    spaced(dc, CX, 1622, BRAND, ImageFont.truetype(FONT, 46), 14, 255)
    A["cap_a"] = np.asarray(cap, np.float32) / 255
    A["cap_sh"] = blur(A["cap_a"], 12) * 0.6
    txt = Image.new("L", (W, H), 0)
    dt = ImageDraw.Draw(txt)
    spaced(dt, W / 2, 900, "SIIL", ImageFont.truetype(FONT, 230), 36, 255)
    spaced(dt, W / 2, 1065, "OSTOMY", ImageFont.truetype(FONT, 74), 30, 255)
    dt.line([(W / 2 - 120, 1150), (W / 2 + 120, 1150)], fill=150, width=2)
    A["card_txt"] = np.asarray(txt, np.float32) / 255
    A["grain"] = np.random.default_rng(5).normal(0, 2.2, (H + 64, W + 64)).astype(np.float32)


# ---------------------------------------------------------------- one frame
T0, T1 = 2.6, 5.8        # the pull: belt leaves the lens and rises out of the bag


def frame(i):
    t = i / FPS
    rng = np.random.default_rng(i)
    # hand-held drift of the world outside the bag
    shx = 14 * math.sin(t * 0.8) + 5 * math.sin(t * 2.1 + 1)
    shy = 11 * math.sin(t * 0.6 + 2) + 4 * math.sin(t * 1.7)
    cx_, cy_ = 60 + shx + t * 1.5, 60 + shy
    ox, oy = int(cx_), int(cy_)
    sky = A["sky"][oy:oy + H, ox:ox + W].copy()

    # the bag rustles: more while the belt is pulled through it
    rust = 0.35 * sstep(0.4, 0.9, t) * (1 - sstep(2.0, 2.5, t)) + 1.0 * sstep(2.3, 2.8, t) * (1 - sstep(5.0, 6.2, t)) + 0.10
    wob = math.sin(t * 9.1) * 0.6 + math.sin(t * 15.7 + 1) * 0.4
    bag = affine(A["bag"], (CX, CY), (CX + 3.0 * rust * math.sin(t * 6.3), CY + 3.0 * rust * math.sin(t * 7.9 + 2)),
                 1.012 + 0.006 * rust * wob, math.radians(0.35 * rust * math.sin(t * 5.2 + 0.5)))
    bag = np.asarray(bag, np.float32)
    wall, O = bag[..., :3], (1 - bag[..., 3:4] / 255)

    out = sky * O + wall * (1 - O)
    if t >= T0:
        e = ease_out((t - T0) / (T1 - T0))
        k = 1 + 3.8 * (1 - e) ** 2.2                       # how much nearer than its final distance
        s = S_END * k
        th = math.radians(13 * math.exp(-(t - T0) / 2.0) * math.sin(2 * math.pi * (t - T0) / 1.9)
                          + 1.5 * math.sin(2 * math.pi * t / 4.3))
        T = (lerp(560, 455, e) + shx * 0.5, lerp(-620, 275, e) + shy * 0.5)
        belt = affine(A["belt"], PIV, T, s, th)
        br = (k - 1) * 7
        if br > 0.4:
            belt = belt.filter(ImageFilter.GaussianBlur(br))
        belt = np.asarray(belt, np.float32)
        pa = belt[..., 3:4] / 255
        prgb = belt[..., :3] * (1 - 0.6 * sstep(1.0, 2.6, k))      # dimmer while still inside the bag
        behind = (sky * (1 - pa) + prgb * pa) * O + wall * (1 - O)       # outside the bag: the rim hides it
        w = sstep(1.75, 2.05, k)
        if w > 0:
            front = out * (1 - pa) + prgb * pa                           # still inside the bag: in front of the walls
            out = behind * (1 - w) + front * w
        else:
            out = behind

    ca = A["cap_a"] * sstep(9.2, 9.9, t)
    if ca.max() > 0:
        out *= (1 - (A["cap_sh"] * sstep(9.2, 9.9, t))[..., None] * 0.6)
        out = out * (1 - ca[..., None]) + 255 * ca[..., None]

    gx, gy = int(rng.integers(0, 64)), int(rng.integers(0, 64))
    out += A["grain"][gy:gy + H, gx:gx + W, None]
    dark = 0.0
    if t < 0.5:
        dark = 1 - sstep(0.0, 0.5, t)
    elif t < 3.6:
        dark = 0.93 * sstep(2.15, 2.6, t) * (1 - sstep(2.75, 3.6, t))
    out *= (1 - dark)
    if t >= 15.0:
        x0 = int(round(W * (1 - ease_out((t - 15.0) / 0.6))))
        if x0 < W:
            ta = (A["card_txt"] * sstep(15.5, 16.2, t))[..., None]
            card = np.array([250, 249, 246], np.float32) * (1 - ta) + np.array([30, 32, 40], np.float32) * ta
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

    mix = 0.045 * norm(band(rng.normal(size=n), 60, 500)) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.13 * t))   # open air
    # paper: sparse sharp crackles shaped by a slow random "handling" curve
    clicks = (rng.random(n) < 0.004) * rng.normal(size=n)
    crack = norm(band(np.convolve(clicks, np.exp(-np.arange(400) / 60.0), "same") * rng.normal(size=n), 1200, 9000))
    handle = norm(np.abs(band(rng.normal(size=n), 1.5, 9))) ** 1.5
    paper = crack * (0.35 + 0.65 * handle)
    mix += 0.30 * paper * env(0.6, 0.9, 2.0, 2.5)
    mix += 0.62 * paper * env(2.3, 2.7, 4.9, 6.0)
    mix += 0.22 * norm(band(rng.normal(size=n), 150, 1400)) * env(2.4, 2.9, 3.4, 4.6)                   # cloth sliding out
    mix += 0.08 * paper * env(6.0, 6.5, 14.0, 15.0) * (handle > 0.55)
    pad = np.zeros(n)
    for f0 in (220.0, 277.18, 329.63, 493.88):
        for det in (-0.6, 0.6):
            pad += np.sin(2 * np.pi * (f0 + det) * t + rng.uniform(0, 6))
    mix += 0.10 * norm(pad) * env(3.6, 6.5, 15.2, 17.6) * (0.85 + 0.15 * np.sin(2 * np.pi * 0.25 * t))
    notes = [659.25, 554.37, 440.0, 493.88, 659.25, 554.37, 739.99, 659.25]
    for j, tt in enumerate(np.arange(6.2, 15.0, 0.7)):
        f0 = notes[j % len(notes)]
        m = t >= tt
        dt = t[m] - tt
        mix[m] += 0.065 * (np.sin(2 * np.pi * f0 * dt) + 0.3 * np.sin(4 * np.pi * f0 * dt)) * np.exp(-dt / 0.55)
    mix += 0.16 * norm(band(rng.normal(size=n), 400, 3500)) * env(14.8, 15.25, 15.3, 15.7) ** 2
    m = t >= 15.55
    dt = t[m] - 15.55
    for f0, a in ((880.0, 1.0), (1320.0, 0.5), (1778.0, 0.3)):
        mix[m] += 0.09 * a * np.sin(2 * np.pi * f0 * dt) * np.exp(-dt / 1.6)
    mix *= np.clip((t - 0.5) / 0.15, 0, 1) * np.clip((DUR - t) / 0.8, 0, 1)
    pcm = (0.89 * mix / np.abs(mix).max() * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(np.stack([pcm, pcm], 1).tobytes())


# ---------------------------------------------------------------- main
def main():
    belt_png, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    build_static(belt_png)
    if "--frames" in sys.argv:
        idx = [int(x) for x in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        thumbs = []
        for i in idx:
            im = Image.fromarray(frame(i))
            im.save(os.path.join(out_dir, f"f{i:04d}.png"))
            thumbs.append(im.resize((270, 480)))
        cols = 6
        sheet = Image.new("RGB", (270 * cols, 480 * ((len(thumbs) + cols - 1) // cols)), "black")
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
            if k % 90 == 0:
                print(f"frame {k}/{N}", flush=True)
    ff.stdin.close()
    ff.wait()
    print("done", mp4)


if __name__ == "__main__":
    main()
