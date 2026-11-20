#!/usr/bin/env python3
"""Cut the finished SIIL teaser: 1080x1920, 30 fps, our own sound, our own end card, no watermark.
usage: assemble.py REACH.mp4 HOLD.jpg OUT.mp4
  REACH.mp4  the one generated motion clip: the hand reaches into the bag and covers the lens
  HOLD.jpg   the photoreal still of the pouch held up; it is moved by code only (hand-held drift, pull-back
             from the lens), so nothing in that shot can bend or melt
Env: TAGLINE (default "COMING SOON"; empty string = brand only)"""
import sys, os, math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H, FPS = 1080, 1920, 30
FONT = "/usr/share/fonts/truetype/freefont/FreeSerif.ttf"
TAG = os.environ.get("TAGLINE", "COMING SOON")
REACH, HOLD, CARD = 3.56, 7.0, 3.3          # seconds
X1, X3 = 0.0, 0.5                           # no cross-over into the pull: the dark frame IS the pouch on the lens
T_HOLD = REACH - X1
T_CARD = T_HOLD + HOLD - X3
DUR = T_CARD + CARD


def card(path):
    im = Image.new("RGB", (W, H), (250, 249, 246))
    d = ImageDraw.Draw(im)

    def spaced(cy, text, size, track, fill):
        f = ImageFont.truetype(FONT, size)
        ws = [d.textlength(c, font=f) for c in text]
        x = W / 2 - (sum(ws) + track * (len(text) - 1)) / 2
        for c, w in zip(text, ws):
            d.text((x, cy), c, font=f, fill=fill, anchor="lm")
            x += w + track
    spaced(880, "SIIL", 230, 36, (30, 32, 40))
    spaced(1045, "OSTOMY", 74, 30, (30, 32, 40))
    if TAG:
        d.line([(W / 2 - 120, 1140), (W / 2 + 120, 1140)], fill=(150, 150, 150), width=2)
        spaced(1215, TAG, 46, 16, (90, 92, 100))
    im.save(path)


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

    mix = 0.045 * norm(band(rng.normal(size=n), 60, 500)) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.13 * t))      # open air
    clicks = (rng.random(n) < 0.004) * rng.normal(size=n)
    crack = norm(band(np.convolve(clicks, np.exp(-np.arange(400) / 60.0), "same") * rng.normal(size=n), 1200, 9000))
    handle = norm(np.abs(band(rng.normal(size=n), 1.5, 9))) ** 1.5
    paper = crack * (0.35 + 0.65 * handle)                                                                 # paper bag crackle
    mix += 0.40 * paper * env(0.3, 0.9, REACH - 0.5, REACH)
    mix += 0.60 * paper * env(T_HOLD - 0.2, T_HOLD + 0.1, T_HOLD + 0.7, T_HOLD + 1.4)
    mix += 0.22 * norm(band(rng.normal(size=n), 200, 1600)) * env(T_HOLD - 0.1, T_HOLD + 0.3, T_HOLD + 0.5, T_HOLD + 1.1)   # plastic sliding out
    mix += 0.07 * paper * env(T_HOLD + 0.8, T_HOLD + 1.3, T_CARD - 1, T_CARD) * (handle > 0.55)
    m = t >= REACH - 0.25                                                                                   # soft thump as the palm covers the lens
    dt = t[m] - (REACH - 0.25)
    mix[m] += 0.35 * np.sin(2 * np.pi * 70 * dt) * np.exp(-dt / 0.12)
    pad = np.zeros(n)
    for f0 in (220.0, 277.18, 329.63, 493.88):
        for det in (-0.6, 0.6):
            pad += np.sin(2 * np.pi * (f0 + det) * t + rng.uniform(0, 6))
    mix += 0.10 * norm(pad) * env(T_HOLD, T_HOLD + 1.5, T_CARD + 0.5, DUR - 0.4) * (0.85 + 0.15 * np.sin(2 * np.pi * 0.25 * t))
    notes = [659.25, 554.37, 440.0, 493.88, 659.25, 554.37, 739.99, 659.25]
    for j, tt in enumerate(np.arange(T_HOLD + 0.9, T_CARD - 0.2, 0.7)):
        f0 = notes[j % len(notes)]
        m = t >= tt
        dt = t[m] - tt
        mix[m] += 0.065 * (np.sin(2 * np.pi * f0 * dt) + 0.3 * np.sin(4 * np.pi * f0 * dt)) * np.exp(-dt / 0.55)
    mix += 0.16 * norm(band(rng.normal(size=n), 400, 3500)) * env(T_CARD - 0.2, T_CARD + 0.25, T_CARD + 0.3, T_CARD + 0.7) ** 2
    m = t >= T_CARD + 0.5
    dt = t[m] - (T_CARD + 0.5)
    for f0, a in ((880.0, 1.0), (1320.0, 0.5), (1778.0, 0.3)):
        mix[m] += 0.09 * a * np.sin(2 * np.pi * f0 * dt) * np.exp(-dt / 1.6)
    mix *= np.clip(t / 0.2, 0, 1) * np.clip((DUR - t) / 0.8, 0, 1)
    pcm = (0.89 * mix / np.abs(mix).max() * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(np.stack([pcm, pcm], 1).tobytes())


def sstep(a, b, x):
    u = min(1.0, max(0.0, (x - a) / (b - a)))
    return u * u * (3 - 2 * u)


PULL = 1.5        # seconds: the pouch leaves the lens and rises out through the opening


def layers(im):
    """Split the still into what is outside the bag (hands + pouch, keyed off the blue sky) and the bag with a clean sky."""
    a = np.asarray(im, np.float32)
    h, w = a.shape[:2]
    sky = ((a[..., 2] - a[..., 0] > 45) & (a[..., 2] > 120)).astype(np.uint8) * 255
    sky = np.asarray(Image.fromarray(sky).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(5))) > 0
    ys, xs = np.nonzero(sky)                                                  # the opening = convex hull of the visible sky
    pts = sorted(set(zip(xs[::7].tolist(), ys[::7].tolist())))
    def half(points):
        out = []
        for q in points:
            while len(out) >= 2 and (out[-1][0] - out[-2][0]) * (q[1] - out[-2][1]) - (out[-1][1] - out[-2][1]) * (q[0] - out[-2][0]) <= 0:
                out.pop()
            out.append(q)
        return out
    poly = half(pts)[:-1] + half(pts[::-1])[:-1]
    hm_img = Image.new("L", (w, h), 0)
    ImageDraw.Draw(hm_img).polygon(poly, fill=255)
    hull = np.asarray(hm_img) > 0
    # arms that come over the rim hide the sky in their corners: complete the opening with its own mirror image
    xm = int(xs.min()) + int(xs.max())
    mir = np.zeros_like(hull)
    cols_ = np.arange(w)
    ok = (xm - cols_ >= 0) & (xm - cols_ < w)
    mir[:, cols_[ok]] = hull[:, (xm - cols_)[ok]]
    hull = hull | mir
    hull_in = np.asarray(Image.fromarray((hull * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(13))) > 0
    obj = hull_in & ~sky
    thick = np.asarray(Image.fromarray((obj * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(19)).filter(ImageFilter.MaxFilter(21))) > 0
    obj = obj & thick                                                          # drop thin slivers of paper left along the rim
    alpha = np.asarray(Image.fromarray((obj * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)), np.float32) / 255
    ys, xs = np.nonzero(sky)
    A = np.stack([xs, ys, np.ones_like(xs)], 1).astype(np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    fill = np.stack([(np.linalg.lstsq(A, a[ys, xs, c], rcond=None)[0] * np.stack([xx, yy, np.ones_like(xx)], -1)).sum(-1) for c in range(3)], -1)
    m = (np.asarray(Image.fromarray((obj * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(17))) > 0) & hull
    m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2)), np.float32)[..., None] / 255
    bg = a * (1 - m) + fill * m
    hm = np.asarray(Image.fromarray((hull * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1)), np.float32)[..., None] / 255
    oy, ox = np.nonzero(obj)
    piv = (float(ox.mean()), float(oy.mean()))
    return a, bg, Image.fromarray(np.dstack([a, alpha * 255]).astype(np.uint8), "RGBA"), hm, piv


def hold_clip(still, path):
    """One continuous move from one still: out of the dark the pouch leaves the lens, rises through the opening of the
    bag (the bag itself stays put), then is held with a slow hand-held drift. Nothing is generated here, so nothing bends."""
    im = Image.open(still).convert("RGB")
    orig, bg, obj, hm, piv = layers(im)
    k = max(W / im.width, H / im.height)
    cx, cy = im.width / 2, im.height / 2
    rng = np.random.default_rng(3)
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "fast", "-crf", "14", "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for i in range(int(HOLD * FPS)):
        t = i / FPS
        if t < PULL:
            u = 1 - (1 - t / PULL) ** 3
            s = 4.2 + (1 - 4.2) * u
            th = math.radians(7 * (1 - u))
            T = (piv[0] + 25 * (1 - u), piv[1] + 130 * (1 - u))
            c, sn = math.cos(th), math.sin(th)
            a, b, d, e = c / s, sn / s, -sn / s, c / s
            o = obj.transform(obj.size, Image.AFFINE, (a, b, piv[0] - (a * T[0] + b * T[1]), d, e, piv[1] - (d * T[0] + e * T[1])), resample=Image.BICUBIC)
            if s > 1.05:
                o = o.filter(ImageFilter.GaussianBlur((s - 1) * 3.2))
            o = np.asarray(o, np.float32)
            pa = o[..., 3:4] / 255
            prgb = o[..., :3] * (1 - 0.5 * sstep(1.3, 2.6, s))               # shaded while still down inside the bag
            behind = bg * (1 - pa * hm) + prgb * pa * hm                       # above the bag: the rim hides it
            front = bg * (1 - pa) + prgb * pa                                  # inside the bag: in front of the paper
            wf = sstep(1.35, 1.8, s)
            comp = behind * (1 - wf) + front * wf
            wo = sstep(0.992, 1.0, u)                                       # hand over to the untouched still only once it lines up
            comp = (comp * (1 - wo) + orig * wo) * sstep(0.0, 0.35, t)
            base = Image.fromarray(np.clip(comp, 0, 255).astype(np.uint8))
        else:
            base = im
        sc = k * (1.035 + 0.006 * math.sin(t * 0.9))
        th = math.radians(0.40 * math.sin(t * 0.8) + 0.18 * math.sin(t * 1.9 + 1))
        tx = W / 2 + 9 * math.sin(t * 0.7) + 4 * math.sin(t * 1.6 + 2)
        ty = H / 2 + 8 * math.sin(t * 0.55 + 1) + 3 * math.sin(t * 1.3)
        c, sn = math.cos(th), math.sin(th)
        a, b, d, e = c / sc, sn / sc, -sn / sc, c / sc
        fr = base.transform((W, H), Image.AFFINE, (a, b, cx - (a * tx + b * ty), d, e, cy - (d * tx + e * ty)), resample=Image.BICUBIC)
        fr = fr.filter(ImageFilter.UnsharpMask(3, 50, 2))
        arr = np.asarray(fr, np.float32) + rng.normal(0, 2.2, (H, W, 1)).astype(np.float32)
        ff.stdin.write(np.clip(arr, 0, 255).astype(np.uint8).tobytes())
    ff.stdin.close()
    ff.wait()


def main():
    reach, still, out = sys.argv[1], sys.argv[2], sys.argv[3]
    tmp = os.path.dirname(os.path.abspath(out))
    card_png, wav, hold_mp4 = os.path.join(tmp, "card.png"), os.path.join(tmp, "sound.wav"), os.path.join(tmp, "hold.mp4")
    card(card_png)
    soundtrack(wav)
    hold_clip(still, hold_mp4)
    up = f"scale=1108:1920:flags=lanczos,crop={W}:{H},unsharp=5:5:0.7,noise=alls=5:allf=t,format=yuv420p,setsar=1"
    fc = (
        f"[0:v]fps={FPS},{up},trim=0:{REACH},setpts=PTS-STARTPTS,fade=t=out:st={REACH - 0.3}:d=0.3[a];"
        f"[1:v]fps={FPS},format=yuv420p,setsar=1,trim=0:{HOLD},setpts=PTS-STARTPTS[c];"
        f"[2:v]fps={FPS},format=yuv420p,setsar=1,trim=0:{CARD},setpts=PTS-STARTPTS,settb=AVTB[d];"
        f"[a][c]concat=n=2:v=1,fps={FPS},settb=AVTB[ac];"
        f"[ac][d]xfade=transition=slideleft:duration={X3}:offset={T_CARD},fade=t=in:d=0.3[v]"
    )
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", reach, "-i", hold_mp4, "-loop", "1", "-t", str(CARD), "-i", card_png, "-i", wav,
           "-filter_complex", fc, "-map", "[v]", "-map", "3:a", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{DUR:.2f}", out]
    subprocess.run(cmd, check=True)
    print("done", out, f"{DUR:.2f}s")


if __name__ == "__main__":
    main()
