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
X1, X3 = 0.4, 0.5                           # cross-over lengths
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


def hold_clip(still, path):
    """The held shot from one still: pulled back from the lens in the first second, then a slow hand-held drift."""
    im = Image.open(still).convert("RGB")
    k = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(3, 60, 2))
    cx, cy = im.width / 2, im.height / 2
    rng = np.random.default_rng(3)
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "fast", "-crf", "14", "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for i in range(int(HOLD * FPS)):
        t = i / FPS
        u = 1 - (1 - min(1, t / 1.1)) ** 3
        sc = 1.60 + (1.05 - 1.60) * u + 0.006 * math.sin(t * 0.9)
        th = math.radians((1 - u) * 5 + 0.40 * math.sin(t * 0.8) + 0.18 * math.sin(t * 1.9 + 1))
        tx = W / 2 + 9 * math.sin(t * 0.7) + 4 * math.sin(t * 1.6 + 2) + (1 - u) * 40
        ty = H / 2 + 8 * math.sin(t * 0.55 + 1) + 3 * math.sin(t * 1.3) + (1 - u) * 260
        c, sn = math.cos(th), math.sin(th)
        a, b, d, e = c / sc, sn / sc, -sn / sc, c / sc
        fr = im.transform((W, H), Image.AFFINE, (a, b, cx - (a * tx + b * ty), d, e, cy - (d * tx + e * ty)), resample=Image.BICUBIC)
        if u < 0.98:
            fr = fr.filter(ImageFilter.GaussianBlur((1 - u) * 14))
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
        f"[0:v]fps={FPS},{up},trim=0:{REACH},setpts=PTS-STARTPTS[a];"
        f"[1:v]fps={FPS},format=yuv420p,setsar=1,trim=0:{HOLD},setpts=PTS-STARTPTS[c];"
        f"[2:v]fps={FPS},format=yuv420p,setsar=1,trim=0:{CARD},setpts=PTS-STARTPTS[d];"
        f"[a][c]xfade=transition=fadeblack:duration={X1}:offset={T_HOLD}[ac];"
        f"[ac][d]xfade=transition=slideleft:duration={X3}:offset={T_CARD},fade=t=in:d=0.3[v]"
    )
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", reach, "-i", hold_mp4, "-loop", "1", "-t", str(CARD), "-i", card_png, "-i", wav,
           "-filter_complex", fc, "-map", "[v]", "-map", "3:a", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{DUR:.2f}", out]
    subprocess.run(cmd, check=True)
    print("done", out, f"{DUR:.2f}s")


if __name__ == "__main__":
    main()
