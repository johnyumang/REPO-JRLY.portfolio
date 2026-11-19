#!/usr/bin/env python3
"""Cut the three motion clips into the finished SIIL teaser: 1080x1920, 30 fps, our own sound, our own end card, no watermark.
usage: assemble.py CLIPS_DIR OUT.mp4      (CLIPS_DIR holds reach.mp4, pull.mp4, hold.mp4 from the motion Space)
Env: TAGLINE (default "COMING SOON"; empty string = brand only)"""
import sys, os, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont
W, H, FPS = 1080, 1920, 30
FONT = "/usr/share/fonts/truetype/freefont/FreeSerif.ttf"
TAG = os.environ.get("TAGLINE", "COMING SOON")
REACH, PULL_IN, PULL_SLOW, HOLD, CARD = 3.56, 1.65, 1.2, 7.12, 3.3     # seconds; the pull clip is only good for its first 1.65 s
X1, X2, X3 = 0.4, 0.3, 0.5                                             # cross-over lengths
PULL = PULL_IN * PULL_SLOW
T_PULL = REACH - X1
T_HOLD = T_PULL + PULL - X2
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
    mix += 0.60 * paper * env(T_PULL, T_PULL + 0.3, T_HOLD, T_HOLD + 0.8)
    mix += 0.20 * norm(band(rng.normal(size=n), 200, 1600)) * env(T_PULL, T_PULL + 0.4, T_HOLD - 0.2, T_HOLD + 0.5)   # plastic sliding out
    mix += 0.07 * paper * env(T_HOLD + 0.8, T_HOLD + 1.3, T_CARD - 1, T_CARD) * (handle > 0.55)
    m = t >= REACH - 0.25                                                                                   # soft thump as the palm covers the lens
    dt = t[m] - (REACH - 0.25)
    mix[m] += 0.35 * np.sin(2 * np.pi * 70 * dt) * np.exp(-dt / 0.12)
    pad = np.zeros(n)
    for f0 in (220.0, 277.18, 329.63, 493.88):
        for det in (-0.6, 0.6):
            pad += np.sin(2 * np.pi * (f0 + det) * t + rng.uniform(0, 6))
    mix += 0.10 * norm(pad) * env(T_PULL, T_HOLD + 1.0, T_CARD + 0.5, DUR - 0.4) * (0.85 + 0.15 * np.sin(2 * np.pi * 0.25 * t))
    notes = [659.25, 554.37, 440.0, 493.88, 659.25, 554.37, 739.99, 659.25]
    for j, tt in enumerate(np.arange(T_HOLD + 0.2, T_CARD - 0.2, 0.7)):
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


def main():
    clips, out = sys.argv[1], sys.argv[2]
    tmp = os.path.dirname(os.path.abspath(out))
    card_png, wav = os.path.join(tmp, "card.png"), os.path.join(tmp, "sound.wav")
    card(card_png)
    soundtrack(wav)
    up = f"scale=1108:1920:flags=lanczos,crop={W}:{H},unsharp=5:5:0.7,noise=alls=5:allf=t,format=yuv420p,setsar=1"
    fc = (
        f"[0:v]fps={FPS},{up},trim=0:{REACH},setpts=PTS-STARTPTS[a];"
        f"[1:v]trim=0:{PULL_IN},setpts={PULL_SLOW}*(PTS-STARTPTS),minterpolate=fps={FPS}:mi_mode=blend,{up},trim=0:{PULL},setpts=PTS-STARTPTS[b];"
        f"[2:v]split[h1][h2];[h2]reverse[hr];[h1][hr]concat=n=2:v=1,minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc,{up},trim=0:{HOLD},setpts=PTS-STARTPTS[c];"
        f"[3:v]fps={FPS},format=yuv420p,setsar=1,trim=0:{CARD},setpts=PTS-STARTPTS[d];"
        f"[a][b]xfade=transition=fadeblack:duration={X1}:offset={T_PULL}[ab];"
        f"[ab][c]xfade=transition=fade:duration={X2}:offset={T_HOLD}[abc];"
        f"[abc][d]xfade=transition=slideleft:duration={X3}:offset={T_CARD},fade=t=in:d=0.3[v]"
    )
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", f"{clips}/reach.mp4", "-i", f"{clips}/pull.mp4", "-i", f"{clips}/hold.mp4",
           "-loop", "1", "-t", str(CARD), "-i", card_png, "-i", wav, "-filter_complex", fc, "-map", "[v]", "-map", "4:a",
           "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
           "-t", f"{DUR:.2f}", out]
    subprocess.run(cmd, check=True)
    print("done", out, f"{DUR:.2f}s")


if __name__ == "__main__":
    main()
