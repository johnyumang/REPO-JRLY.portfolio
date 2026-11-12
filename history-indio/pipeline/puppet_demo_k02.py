"""Puppet-warp demo: make one painted key still move, locally, on CPU (no AI video, no GPU).

    python puppet_demo_k02.py videos/limahong-1574/keys/k02.png out.mp4

The still is cut into soft regions (head, cup arm, chest, hair, cloth, fire, steam, water) and each region
is bent with its own small motion; blinks are painted over the eyes. Regions are hand-placed for k02
(coordinates are in a 720x1280 frame), so every new still needs its own region list.
"""
import math, subprocess, sys
import cv2
import numpy as np

SRC, OUT = sys.argv[1], sys.argv[2]
W, H, FPS, SECS = 720, 1280, 30, 10.0
N = int(FPS * SECS)
rng = np.random.default_rng(3)
img = cv2.resize(cv2.imread(SRC), (W, H), interpolation=cv2.INTER_AREA).astype(np.float32)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)


def ell(cx, cy, rx, ry, ang=0.0, soft=25):
    """Soft elliptical mask, 0..1."""
    m = np.zeros((H, W), np.uint8)
    cv2.ellipse(m, (int(cx), int(cy)), (int(rx), int(ry)), ang, 0, 360, 255, -1)
    k = soft * 2 + 1
    return cv2.GaussianBlur(m, (k, k), soft / 2).astype(np.float32) / 255


def poly(pts, soft=25):
    m = np.zeros((H, W), np.uint8)
    cv2.fillPoly(m, [np.array(pts, np.int32)], 255)
    k = soft * 2 + 1
    return cv2.GaussianBlur(m, (k, k), soft / 2).astype(np.float32) / 255


def rot(mask, px, py, deg):
    """Displacement that turns the masked region about a pivot (inverse map)."""
    a = np.radians(-deg) * mask
    c, s = np.cos(a), np.sin(a)
    dx, dy = xx - px, yy - py
    return (px + c * dx - s * dy) - xx, (py + s * dx + c * dy) - yy


ease = lambda t: t * t * (3 - 2 * t)


def bump(t, a, b, c, d):
    """0 before a, eases to 1 by b, holds to c, eases back to 0 by d."""
    if t <= a or t >= d:
        return 0.0
    if t < b:
        return ease((t - a) / (b - a))
    if t <= c:
        return 1.0
    return 1 - ease((t - c) / (d - c))


# ---- regions (hand-placed for k02)
M_HEAD = ell(385, 215, 185, 175, 0, 45)
M_NECKUP = np.clip(M_HEAD + ell(350, 380, 110, 70, 0, 35), 0, 1)
M_ARM = poly([(60, 300), (270, 300), (275, 420), (215, 470), (170, 560), (120, 700), (0, 760), (0, 420)], 30)
M_CUPTOP = ell(200, 240, 70, 90, 0, 30)
M_CHEST = ell(345, 600, 190, 200, 0, 60)
M_HAIR = np.clip(ell(380, 150, 190, 85, 0, 30) - ell(385, 265, 95, 95, 0, 25), 0, 1)
M_TAIL = np.clip(ell(250, 285, 40, 60, 0, 20) + ell(455, 395, 35, 55, 0, 18), 0, 1)
M_EAR1, M_EAR2 = ell(280, 300, 26, 30, 0, 8), ell(428, 350, 24, 28, 0, 8)
M_FIRE = poly([(0, 830), (120, 820), (300, 950), (340, 1080), (300, 1280), (0, 1280)], 40)
M_FLAG = poly([(60, 0), (190, 0), (150, 250), (60, 300)], 30)
M_WATER = poly([(470, 365), (620, 365), (640, 480), (470, 470)], 18)
M_SASH = ell(400, 880, 60, 130, 0, 30)
M_TORCH = np.clip(ell(20, 275, 26, 40, 0, 12) + ell(708, 470, 20, 32, 0, 10), 0, 1)
M_WARM = np.clip(poly([(0, 560), (720, 700), (720, 1280), (0, 1280)], 120), 0, 1)
EYES = [((362, 222), (25, 11), 20), ((432, 258), (22, 11), 22)]  # centre, radii, tilt
skin = img[250:262, 372:384].reshape(-1, 3).mean(0)
lid = img.copy()
for (cx, cy), (rx, ry), ang in EYES:
    cv2.ellipse(lid, (cx, cy), (rx + 3, ry + 3), ang, 0, 360, tuple(float(v) for v in skin), -1)
    cv2.ellipse(lid, (cx, cy + 3), (rx, ry - 4), ang, 15, 165, (20, 14, 18), 3, cv2.LINE_AA)  # closed-lash curve
LID_M = np.zeros((H, W), np.float32)
for (cx, cy), (rx, ry), ang in EYES:
    LID_M = np.maximum(LID_M, ell(cx, cy, rx + 5, ry + 5, ang, 3))
BLINKS = [1.1, 4.4, 4.75, 7.6]

sparks = [dict(x=rng.uniform(20, 300), ph=rng.uniform(0, 1), sp=rng.uniform(0.35, 0.7), sway=rng.uniform(8, 30),
               r=rng.integers(2, 5)) for _ in range(26)]
puffs = [dict(ph=i / 7, dx=rng.uniform(-14, 14)) for i in range(7)]

ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", "%dx%d" % (W, H),
                       "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-crf", "17", "-preset", "slow",
                       "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
for f in range(N):
    t = f / FPS
    toast = bump(t, 2.0, 2.9, 4.6, 5.8) + 0.55 * bump(t, 6.6, 7.3, 8.4, 9.6)
    over = 0.25 * math.sin(max(0.0, t - 2.9) * 9) * math.exp(-max(0.0, t - 2.9) * 3) if t > 2.9 else 0.0
    breath = math.sin(t * 2 * math.pi / 3.3)

    # painted blink on the source, so it rides along with the head
    b = max((1 - abs(t - bt) / 0.09) for bt in BLINKS)
    src = img if b <= 0 else img * (1 - LID_M[..., None] * min(1, b * 1.6)) + lid * (LID_M[..., None] * min(1, b * 1.6))

    dx = np.zeros((H, W), np.float32)
    dy = np.zeros((H, W), np.float32)

    def add(d):
        global dx, dy
        dx += d[0]
        dy += d[1]

    # head: slow sway, a nod and tilt into the toast
    add(rot(M_NECKUP, 350, 380, 1.4 * math.sin(t * 1.25) + 4.2 * (toast + over)))
    dy += M_HEAD * (-3.0 * (toast + over) + 1.2 * breath)
    # cup arm swings up from the elbow; steam above the cup follows
    arm = 6.5 * (toast + over) + 0.5 * math.sin(t * 1.9)
    add(rot(np.clip(M_ARM + M_CUPTOP * 0.9, 0, 1), -40, 700, arm))
    # breathing
    dy += M_CHEST * (2.6 * breath) * ((yy - 600) / 200)
    dx += M_CHEST * (1.2 * breath) * ((xx - 345) / 190)
    # hair, headband tails, flag, sash: wind
    wind = math.sin(t * 2.3) + 0.5 * math.sin(t * 5.1 + 1)
    dx += M_HAIR * (2.2 * wind + 1.5 * np.sin(xx * 0.05 + t * 6))
    dx += M_TAIL * (5.0 * np.sin(yy * 0.06 - t * 5.0) + 3 * wind)
    dx += M_FLAG * (4.0 * np.sin(yy * 0.03 - t * 2.6))
    dx += M_SASH * (2.0 * np.sin(yy * 0.03 - t * 2.2)) * ((yy - 760) / 240).clip(0, 1)
    add(rot(M_EAR1, 280, 272, 7 * math.sin(t * 3.1 + 0.4) + 10 * over))
    add(rot(M_EAR2, 428, 324, 7 * math.sin(t * 3.1) + 10 * over))
    # fire and torches: flames lick upward
    dx += M_FIRE * (7.0 * np.sin(yy * 0.045 + t * 10 + 2.0 * np.sin(xx * 0.03)))
    dy += M_FIRE * (6.0 * (0.5 + 0.5 * np.sin(xx * 0.05 - t * 8)))
    dx += M_TORCH * (3.0 * np.sin(yy * 0.2 + t * 14))
    dy += M_TORCH * (2.5 * math.sin(t * 17))
    # painted steam wavers; water glints shimmer
    dx += M_CUPTOP * (4.0 * np.sin(yy * 0.05 + t * 3.0))
    dx += M_WATER * (2.5 * np.sin(yy * 0.6 + t * 4.0))

    out = cv2.remap(src, xx + dx, yy + dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

    # firelight flicker on the lower half
    fl = 1 + 0.06 * math.sin(t * 11) + 0.04 * math.sin(t * 23 + 1) + 0.03 * rng.uniform(-1, 1)
    out *= 1 + (fl - 1) * (M_WARM[..., None] + 2.0 * M_FIRE[..., None])
    # sparks and steam puffs (additive)
    lay = np.zeros((H, W, 3), np.float32)
    for s in sparks:
        p = (t * s["sp"] + s["ph"]) % 1
        x = s["x"] + s["sway"] * math.sin(p * 9 + s["ph"] * 20) + 60 * p
        y = 1150 - 620 * p
        cv2.circle(lay, (int(x), int(y)), int(s["r"]), (60 * (1 - p), 170 * (1 - p), 255 * (1 - p)), -1, cv2.LINE_AA)
    lay = cv2.GaussianBlur(lay, (0, 0), 1.6) * 1.3
    st = np.zeros((H, W), np.float32)
    cupx, cupy = 195 + 2.2 * arm, 300 - 5.5 * arm
    for pf in puffs:
        p = (t * 0.22 + pf["ph"]) % 1
        cv2.circle(st, (int(cupx + pf["dx"] + 22 * math.sin(p * 6 + pf["ph"] * 9)), int(cupy - 190 * p)), int(12 + 26 * p),
                   float(0.5 * math.sin(math.pi * p)), -1, cv2.LINE_AA)
    st = cv2.GaussianBlur(st, (0, 0), 14)
    out = out + lay + st[..., None] * np.array([150, 140, 130], np.float32)

    # slow push-in toward the face
    z = 1.0 + 0.07 * ease(t / SECS) + 0.012 * (toast + over)
    cx, cy = 360 + 25 * ease(t / SECS), 560 - 150 * ease(t / SECS)
    Mz = np.float32([[z, 0, cx - z * cx], [0, z, cy - z * cy]])
    out = cv2.warpAffine(out, Mz, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    ff.stdin.write(np.clip(out, 0, 255).astype(np.uint8).tobytes())
ff.stdin.close()
ff.wait()
print("wrote", OUT, N, "frames")
