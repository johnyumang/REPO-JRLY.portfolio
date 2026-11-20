#!/usr/bin/env python3
"""Cut the SIIL teaser as ONE continuous take: 1080x1920, 30 fps, our own sound, our own end card, no watermark.

usage: assemble.py REACH.mp4 LOWER.mp4 HOLD.jpg RIFE.onnx OUT.mp4 [--frames 90,105,...]
  REACH.mp4  generated clip (16 fps): the hand comes in from outside the bag and covers the lens
  LOWER.mp4  generated clip (16 fps) that STARTS on HOLD.jpg: the hands lower the pouch down onto the lens.
             It is played BACKWARDS, so the pouch leaves the lens, rises out of the bag and arrives exactly on the
             hold picture: real hand-and-pouch motion, and the last frame is guaranteed to be the good still.
  HOLD.jpg   the photoreal still of the pouch held up (the picture LOWER.mp4 was made from)
  RIFE.onnx  frame interpolator (hzwer/Practical-RIFE 4.25 lite, ONNX export, MIT): true in-between frames, so the
             16 fps clips play at a real 30 fps and can be re-timed without stutter
Env: TAGLINE (default "COMING SOON"; empty = brand only)

How the join is made seamless (no cut, no fade effect):
  * the reach ends with the palm closing on the lens: pushed in, defocused and darkened the way a covered lens goes dark
  * the pull starts from that dark: the pouch is ON the lens, then lifts. The backwards clip plays at its own
    natural pace from the first frame; over its first half second an optical pull-back is laid on top, whose
    distance follows a minimum-jerk path (how an arm really moves: from rest, to rest) with size = 1/distance
    (true perspective), plus the defocus and the light coming back that a lens shows when something leaves it
  * the motion model moves in uneven steps (big, small, big, small: a 16 fps clip that feels like 8). Both clips are
    re-spaced by their measured movement (optical flow) so every step is even, and only then interpolated
  * one slow hand-held drift runs under the whole video, so every part shares the same camera
  * the small word OSTOMY, which the motion model scrambles while it moves, is re-laid on every frame from the still
  * the hold is not a frozen photo: the hands' own small movements at the start of LOWER.mp4 (first 5 frames) are
    measured as optical flow and applied to the full-resolution still, so hands and pouch keep moving a little
"""
import sys, os, math, subprocess, wave
import numpy as np
import cv2
import onnxruntime as ort
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
SW, SH = 768, 1331                 # scene space: the hold still, centre-cropped exactly as the motion Space crops it
CW, CH = 480, 832                  # the motion clips
FONT = "/usr/share/fonts/truetype/freefont/FreeSerif.ttf"
TAG = os.environ.get("TAGLINE", "COMING SOON")
SRC_FPS = 16.0
COVER = 0.42                       # last part of the reach: the palm seals the lens
T1 = 0.60                          # the optical pull-back off the lens, laid over the start of the backwards clip
Z0 = 0.06                          # pouch on the lens, as a fraction of its final distance
AF = 0.40                          # focus settling onto the full-resolution still
HOLD, CARD_IN, CARD = 5.0, 0.5, 2.8
K = max(W / SW, H / SH)
C2S = np.diag([SW / CW, SH / CH, 1.0])


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def sstep(a, b, x):
    u = clamp((x - a) / (b - a))
    return u * u * (3 - 2 * u)


def minjerk(u):
    u = clamp(u)
    return u * u * u * (10 - 15 * u + 6 * u * u)


# ---------------------------------------------------------------- clips, interpolation
def read_clip(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, CH, CW, 3).copy()


class Rife:
    def __init__(self, path):
        so = ort.SessionOptions()
        so.intra_op_num_threads = os.cpu_count()
        self.s = ort.InferenceSession(path, so, providers=["CPUExecutionProvider"])
        self.cache = {}

    def __call__(self, clip, p):
        """Frame at real-valued position p of a clip."""
        p = clamp(p, 0, len(clip) - 1)
        i = min(int(p), len(clip) - 2)
        t = round(p - i, 3)
        if t <= 0.002:
            return clip[i]
        if t >= 0.998:
            return clip[i + 1]
        key = (id(clip), i, t)
        if key not in self.cache:
            pw = (-CW) % 64
            f = lambda a: np.pad(a.astype(np.float32) / 255, ((0, (-CH) % 64), (0, pw), (0, 0)), mode="edge").transpose(2, 0, 1)[None]
            o = self.s.run(None, {"img0": f(clip[i]), "img1": f(clip[i + 1]), "timestep": np.full((1, 1, 1, 1), t, np.float32)})[0]
            self.cache[key] = (np.clip(o[0].transpose(1, 2, 0)[:CH, :CW], 0, 1) * 255).astype(np.uint8)
        return self.cache[key]


# ---------------------------------------------------------------- even steps
def motion(clip):
    """Movement between neighbouring frames, in pixels: the mean of the fastest 15 % of the optical flow."""
    g = [cv2.cvtColor(f, cv2.COLOR_RGB2GRAY) for f in clip]
    out = []
    for k in range(len(g) - 1):
        fl = cv2.calcOpticalFlowFarneback(g[k], g[k + 1], None, 0.5, 4, 25, 3, 7, 1.5, 0)
        mag = np.hypot(fl[..., 0], fl[..., 1]).ravel()
        out.append(float(mag[mag >= np.percentile(mag, 85)].mean()))
    return np.array(out) + 0.05


def even_time(clip, m=None):
    """x -> p: the source position to show at nominal position x so that the movement per frame comes out even.
    m[k] is the movement from source frame k to k+1 (optical flow unless given); c[k] is the movement up to frame k;
    C is the same total movement with the big-small steps smoothed away."""
    m = motion(clip) if m is None else m
    c = np.concatenate([[0], np.cumsum(m)])
    ms = np.convolve(np.pad(m, 3, mode="edge"), np.array([1, 2, 3, 4, 3, 2, 1]) / 16.0, mode="valid")
    C = np.concatenate([[0], np.cumsum(ms * m.sum() / ms.sum())])
    idx = np.arange(len(c), dtype=np.float64)
    return (lambda x: float(np.interp(np.interp(clamp(x, 0, len(c) - 1), idx, C), c, idx))), c, C


# ---------------------------------------------------------------- lettering
def text_bands(rgb, k):
    """Bright lettering on the black pouch -> list of (y0, y1, x0, x1) bands, top to bottom."""
    L = rgb.astype(np.float32).mean(2)
    inside = cv2.blur((L < 70).astype(np.float32), (k, k)) > 0.62
    if inside.sum() < 50:
        return []
    lo, hi = np.median(L[inside]), np.percentile(L[inside], 99.6)       # letters blurred by motion are dimmer: threshold follows
    thr = max(lo + 0.30 * (hi - lo), lo + 22)
    m = cv2.morphologyEx(((L > thr) & inside).astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8)) > 0
    rows = m.sum(1)
    bands, y = [], 0
    while y < len(rows):
        if rows[y] >= 2:
            y0, gap = y, 0
            while y < len(rows) and gap <= 2:
                gap = 0 if rows[y] >= 2 else gap + 1
                y += 1
            y1 = y - gap
            xs = np.nonzero(m[y0:y1].any(0))[0]
            if len(xs) and y1 - y0 >= 3:
                bands.append((y0, y1, int(xs.min()), int(xs.max()) + 1))
        else:
            y += 1
    return bands


def track_and_fix(clip, still):
    """Follow the word SIIL through the clip (it stays correct) and re-lay the small word OSTOMY from the still.
    Returns the fixed clip and SIIL's measured box per frame: centre x, centre y, width, height."""
    fb = sorted(text_bands(still, 65), key=lambda q: -(q[3] - q[2]) * (q[1] - q[0]))
    sy0, sy1, sx0, sx1 = fb[0]
    oy0, oy1, ox0, ox1 = min((q for q in fb[1:] if q[0] >= sy1), key=lambda q: q[0])
    sw, sh = sx1 - sx0, sy1 - sy0
    dx, dy = (ox0 + ox1) / 2 - (sx0 + sx1) / 2, (oy0 + oy1) / 2 - (sy0 + sy1) / 2
    py0, py1, px0, px1 = oy0 - 7, oy1 + 7, ox0 - 9, ox1 + 9
    Lp = still[py0:py1, px0:px1].astype(np.float32).mean(2)
    lo, hi = np.percentile(Lp, 10), np.percentile(Lp, 99.7)
    alpha = np.clip((Lp - lo - 12) / (hi - lo - 12), 0, 1)
    pcx, pcy = (px1 - px0) / 2, (py1 - py0) / 2
    boxes, prev = [], ((sx0 + sx1) / 2 * CW / SW, (sy0 + sy1) / 2 * CH / SH)
    for f in clip:
        cand = [q for q in text_bands(f, 41) if q[3] - q[2] >= 40
                and math.hypot((q[2] + q[3]) / 2 - prev[0], (q[0] + q[1]) / 2 - prev[1]) < 110]
        q = max(cand, key=lambda q: (q[3] - q[2]) * (q[1] - q[0])) if cand else None
        if q:
            boxes.append(((q[2] + q[3]) / 2, (q[0] + q[1]) / 2, q[3] - q[2], q[1] - q[0]))
            prev = boxes[-1][:2]
        else:
            boxes.append(boxes[-1])
    b = np.array(boxes, np.float32)
    bs = b.copy()
    bs[1:-1] = 0.25 * b[:-2] + 0.5 * b[1:-1] + 0.25 * b[2:]
    out = clip.copy()
    for n, (cx, cy, w, h) in enumerate(bs):
        f = out[n]
        L = f.astype(np.float32).mean(2)
        x0, x1 = int(cx - 0.62 * w), int(cx + 0.62 * w)
        y0, y1 = int(cy + h / 2 + 0.10 * h), int(cy + h / 2 + 0.95 * h)
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(CW, x1), min(CH, y1)
        if x1 - x0 < 6 or y1 - y0 < 3:
            continue
        box = L[y0:y1, x0:x1]
        m = np.zeros((CH, CW), np.uint8)
        m[y0:y1, x0:x1] = (box > np.median(box) + 26).astype(np.uint8)
        m = cv2.dilate(m, np.ones((3, 3), np.uint8), iterations=2)
        f = cv2.inpaint(f, m, 3, cv2.INPAINT_TELEA)
        ax, ay = w / sw, h / sh
        M = np.array([[ax, 0, cx + dx * ax - ax * pcx], [0, ay, cy + dy * ay - ay * pcy]], np.float32)
        a = cv2.warpAffine(alpha, M, (CW, CH), flags=cv2.INTER_AREA if ax < 1 else cv2.INTER_CUBIC)
        if ax > 1.2:
            a = cv2.GaussianBlur(a, (0, 0), 0.35 * ax)
        sm = L[int(cy - h / 2):int(cy + h / 2), int(cx - w / 2):int(cx + w / 2)]
        sel = clip[n][int(cy - h / 2):int(cy + h / 2), int(cx - w / 2):int(cx + w / 2)][sm >= np.percentile(sm, 93)]
        col = sel.mean(0) if len(sel) else np.array([215, 212, 208.0])
        a = np.clip(a, 0, 1)[..., None]
        out[n] = np.clip(f * (1 - a) + col * a, 0, 255).astype(np.uint8)
    return out, b


# ---------------------------------------------------------------- camera
def m_out(t):
    """Scene -> output, with one slow hand-held drift for the whole video."""
    sc = K * (1.03 + 0.005 * math.sin(0.9 * t))
    th = math.radians(0.40 * math.sin(0.8 * t) + 0.18 * math.sin(1.9 * t + 1))
    tx = W / 2 + 9 * math.sin(0.7 * t) + 4 * math.sin(1.6 * t + 2)
    ty = H / 2 + 8 * math.sin(0.55 * t + 1) + 3 * math.sin(1.3 * t)
    c, s = math.cos(th) * sc, math.sin(th) * sc
    return np.array([[c, -s, tx - (c * SW / 2 - s * SH / 2)], [s, c, ty - (s * SW / 2 + c * SH / 2)], [0, 0, 1.0]])


def zoom(z, cx, cy):
    return np.array([[z, 0, cx * (1 - z)], [0, z, cy * (1 - z)], [0, 0, 1.0]])


def warp(img, M):
    return cv2.warpAffine(img.astype(np.float32), M[:2].astype(np.float32), (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT_101)


def crisp(x, amt=0.8, sig=2.2):
    return x + amt * (x - cv2.GaussianBlur(x, (0, 0), sig)) if amt > 0.01 else x


# ---------------------------------------------------------------- end card, sound
def card_image():
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
    return np.asarray(im, np.float32)


def soundtrack(path, TR, T_HELD, TC, DUR):
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
    mix += 0.40 * paper * env(0.3, 0.9, TR - 0.3, TR + 0.1)
    mix += 0.55 * paper * env(TR, TR + 0.25, T_HELD - 0.4, T_HELD + 0.5)
    mix += 0.24 * norm(band(rng.normal(size=n), 200, 1600)) * env(TR + 0.05, TR + 0.45, TR + 0.8, T_HELD)   # plastic sliding up
    mix += 0.07 * paper * env(T_HELD + 0.6, T_HELD + 1.1, TC - 1, TC) * (handle > 0.55)
    m = t >= TR - 0.12                                                                                     # palm lands on the lens
    dt = t[m] - (TR - 0.12)
    mix[m] += 0.35 * np.sin(2 * np.pi * 70 * dt) * np.exp(-dt / 0.12)
    mix *= 1 - 0.75 * env(TR - 0.1, TR, TR + 0.15, TR + 0.5)                                               # covered lens: muffled
    pad = np.zeros(n)
    for f0 in (220.0, 277.18, 329.63, 493.88):
        for det in (-0.6, 0.6):
            pad += np.sin(2 * np.pi * (f0 + det) * t + rng.uniform(0, 6))
    mix += 0.10 * norm(pad) * env(TR + 0.4, T_HELD + 0.8, TC + 0.5, DUR - 0.4) * (0.85 + 0.15 * np.sin(2 * np.pi * 0.25 * t))
    notes = [659.25, 554.37, 440.0, 493.88, 659.25, 554.37, 739.99, 659.25]
    for j, tt in enumerate(np.arange(T_HELD + 0.3, TC - 0.2, 0.7)):
        f0 = notes[j % len(notes)]
        m = t >= tt
        dt = t[m] - tt
        mix[m] += 0.065 * (np.sin(2 * np.pi * f0 * dt) + 0.3 * np.sin(4 * np.pi * f0 * dt)) * np.exp(-dt / 0.55)
    mix += 0.16 * norm(band(rng.normal(size=n), 400, 3500)) * env(TC - 0.2, TC + 0.25, TC + 0.3, TC + 0.7) ** 2
    m = t >= TC + 0.5
    dt = t[m] - (TC + 0.5)
    for f0, a in ((880.0, 1.0), (1320.0, 0.5), (1778.0, 0.3)):
        mix[m] += 0.09 * a * np.sin(2 * np.pi * f0 * dt) * np.exp(-dt / 1.6)
    mix *= np.clip(t / 0.2, 0, 1) * np.clip((DUR - t) / 0.8, 0, 1)
    pcm = (0.89 * mix / np.abs(mix).max() * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(np.stack([pcm, pcm], 1).tobytes())


# ---------------------------------------------------------------- main
def main():
    reach_p, lower_p, still_p, rife_p, out = sys.argv[1:6]
    rife = Rife(rife_p)
    A = read_clip(reach_p)
    B = read_clip(lower_p)
    im = Image.open(still_p).convert("RGB")
    assert im.size == (768, 1344), "hold still must be 768x1344 (the size the stills are made at)"
    F = np.asarray(im)[6:6 + SH].copy()                       # the Space's own centre crop: rows 6..1337
    B, box = track_and_fix(B, F)
    width = box[:, 2]

    # colour: bring the clip onto the still (first clip frame == the still)
    f0 = cv2.resize(F, (CW, CH), interpolation=cv2.INTER_AREA).astype(np.float32)
    b0 = B[0].astype(np.float32)
    gain = [np.polyfit(b0[::4, ::4, c].ravel(), f0[::4, ::4, c].ravel(), 1) for c in range(3)]
    B = np.clip(np.stack([B[..., c] * gain[c][0] + gain[c][1] for c in range(3)], -1), 0, 255).astype(np.uint8)

    # even steps for the reach
    pos_A = even_time(A)[0]

    # the pull: the backwards clip at its own pace, steps evened; it starts where the pouch has stopped near the lens
    # its steps are measured on the pouch itself: how far the word SIIL moved and grew (1.9 x the change in its width
    # is how far the pouch's edges moved), with a little optical flow for the frames where the word barely changes
    step = np.sqrt(np.diff(box[:, 0]) ** 2 + np.diff(box[:, 1]) ** 2 + (1.9 * np.diff(box[:, 2])) ** 2)
    pos_B, _, CB = even_time(B, 0.85 * step + 0.15 * motion(B))
    X0 = float(np.interp(0.92 * CB[-1], CB, np.arange(len(CB), dtype=np.float64)))   # skip its long, nearly still approach to the lens
    SMAX = float(np.median(width[-4:]) / np.median(width[:3]))         # the pouch there, against its held size
    ZC0 = (1 / Z0) / SMAX                                               # how much nearer still "on the lens" is
    print(f"pouch stops near the lens at position {X0:.1f} of {len(B) - 1}, {SMAX:.2f}x its held size; optical pull-back starts at {ZC0:.1f}x", flush=True)

    TR = (len(A) - 1) / SRC_FPS
    T_HELD = TR + X0 / SRC_FPS                         # the backwards clip has run out: exactly the still
    TC = T_HELD + HOLD
    DUR = TC + CARD_IN + CARD
    N = int(round(DUR * FPS))
    PALM = (0.45 * SW, 0.42 * SH)
    CEN = (SW / 2, SH / 2)
    card = card_image()

    # a living hold: how every pixel moves over the clip's first frames (the hands' own small movements), smoothed and
    # scaled up to the still; the still is then bent by that much, back and forth, never repeating exactly
    LIVE = 5
    g0 = cv2.cvtColor(B[0], cv2.COLOR_RGB2GRAY)
    flows = [np.zeros((SH, SW, 2), np.float32)]
    for k in range(1, LIVE + 1):
        fl = cv2.calcOpticalFlowFarneback(g0, cv2.cvtColor(B[k], cv2.COLOR_RGB2GRAY), None, 0.5, 4, 25, 3, 7, 1.5, 0)
        fl = cv2.GaussianBlur(fl, (0, 0), 6)
        flows.append(cv2.resize(fl, (SW, SH), interpolation=cv2.INTER_LINEAR) * np.array([SW / CW, SH / CH], np.float32))
    gx, gy = np.meshgrid(np.arange(SW, dtype=np.float32), np.arange(SH, dtype=np.float32))

    def living_still(t):
        u = t - T_HELD
        q = sstep(0, 1.2, u) * (2.4 + 1.5 * math.sin(2 * math.pi * u / 3.1 + 0.4) + 0.6 * math.sin(2 * math.pi * u / 1.9 + 2.0))
        k = min(int(q), LIVE - 1)
        fl = flows[k] * (1 - (q - k)) + flows[k + 1] * (q - k)
        return cv2.remap(Ff, gx - fl[..., 0], gy - fl[..., 1], cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT_101)
    grain = np.random.default_rng(3).normal(0, 2.2, (H + 64, W + 64)).astype(np.float32)
    Ff = F.astype(np.float32)

    def frame(t):
        if t < TR:                                                       # ---- the hand comes in and covers the lens
            f = rife(A, pos_A(t * SRC_FPS))
            g = clamp((t - (TR - COVER)) / COVER)
            if g <= 0:
                return crisp(warp(f, m_out(t) @ C2S))
            acc = 0
            for k in range(6):                                           # the push-in smears like a real fast move
                gg = clamp(g + k / 5 * (0.5 / FPS) / COVER)
                acc = acc + warp(f, m_out(t) @ zoom(1 + 1.9 * gg ** 2.2, *PALM) @ C2S)
            x = acc / 6
            sig = 18 * g * g
            if sig > 0.4:
                x = cv2.GaussianBlur(x, (0, 0), sig)
            d = sstep(0.45, 1.0, g)                                      # the palm shuts the light out; skin glows warm
            return crisp(x, 0.8 * (1 - clamp(sig / 3))) * (1 - d) * np.array([1.0, 1 - 0.25 * d, 1 - 0.38 * d], np.float32)
        if t < T_HELD:                                                   # ---- the pouch leaves the lens and rises
            u = t - TR
            f = rife(B, pos_B(X0 - u * SRC_FPS))

            def zc_at(uu):                                               # optical pull-back: distance on a minimum-jerk path
                return 1 / (1 / ZC0 + (1 - 1 / ZC0) * minjerk(uu / T1))
            zc = zc_at(u)
            if zc < 1.002:
                return crisp(warp(f, m_out(t) @ C2S))
            acc = 0
            for k in range(6):                                           # smear across the shutter, like any fast move
                acc = acc + warp(f, m_out(t) @ zoom(zc_at(u + k / 5 * 0.5 / FPS), *CEN) @ C2S)
            x = acc / 6
            sig = 7 * (zc - 1)                                           # out of focus while it is this near
            if sig > 0.4:
                x = cv2.GaussianBlur(x, (0, 0), sig)
            return crisp(x, 0.8 * (1 - clamp(sig / 3))) * sstep(Z0, 0.15, 1 / (zc * SMAX))   # light returns as it lifts
        hi = warp(living_still(t), m_out(t))                             # ---- held: the full-resolution still, alive
        w = sstep(0, AF, t - T_HELD)                                     # focus settles
        if w < 1:
            hi = crisp(warp(B[0], m_out(t) @ C2S)) * (1 - w) + hi * w
        if t >= TC:
            x0 = int(round(W * (1 - (1 - (1 - clamp((t - TC) / CARD_IN)) ** 3))))
            if x0 < W:
                hi[:, x0:] = card[:, :W - x0]
                if x0 > 0:
                    sh = np.exp(-np.arange(min(x0, 60))[::-1] / 18.0)[None, :, None]
                    hi[:, x0 - sh.shape[1]:x0] *= (1 - 0.25 * sh)
        return hi

    def finish(x, i):
        rng = np.random.default_rng(i)
        gx, gy = int(rng.integers(0, 64)), int(rng.integers(0, 64))
        x = x + grain[gy:gy + H, gx:gx + W, None]
        if i < 9:
            x = x * (i / 9.0)
        return np.clip(x, 0, 255).astype(np.uint8)

    if "--frames" in sys.argv:
        idx = [int(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        tiles = [cv2.resize(finish(frame(i / FPS), i), (216, 384), interpolation=cv2.INTER_AREA) for i in idx]
        cols = 10
        rows = (len(tiles) + cols - 1) // cols
        sheet = np.zeros((384 * rows, 216 * cols, 3), np.uint8)
        for k, tl in enumerate(tiles):
            sheet[(k // cols) * 384:(k // cols + 1) * 384, (k % cols) * 216:(k % cols + 1) * 216] = tl
        Image.fromarray(sheet).save(out, quality=88)
        print("sheet", out, "TR=%.2f T_HELD=%.2f TC=%.2f DUR=%.2f" % (TR, T_HELD, TC, DUR))
        return
    wav = os.path.join(os.path.dirname(os.path.abspath(out)), "sound.wav")
    soundtrack(wav, TR, T_HELD, TC, DUR)
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", out], stdin=subprocess.PIPE)
    for i in range(N):
        ff.stdin.write(finish(frame(i / FPS), i).tobytes())
        if i % 60 == 0:
            print(f"frame {i}/{N}", flush=True)
    ff.stdin.close()
    ff.wait()
    print("done", out, "%.2fs" % DUR, "TR=%.2f T_HELD=%.2f TC=%.2f" % (TR, T_HELD, TC))


if __name__ == "__main__":
    main()
