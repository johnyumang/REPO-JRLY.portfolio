"""Puppet warp: make a painted key still move, locally, on CPU (no AI video, no GPU).

A "rig" is a small JSON file that lists soft regions of the still and how each one moves. Coordinates are
always in a 720x1280 frame, whatever the render size. See pipeline/PUPPET.md for the rig format.

    python puppet_still.py rig.json still.png out.mp4 [--seconds 4] [--size 720] [--fps 30]
    python puppet_still.py --grid still.png grid.jpg        # numbered grid to read coordinates from

build_anime.py uses a rig automatically when videos/<slug>/rigs/kNN.json exists for a line's keyframe.
"""
import json, math, subprocess, sys
import cv2
import numpy as np

RW, RH = 720, 1280  # rig coordinate space
ease = lambda t: t * t * (3 - 2 * t)


def bump(t, a, b, c, d):
    """0 before a, eases to 1 by b, holds to c, eases back to 0 by d."""
    if t <= a or t >= d:
        return 0.0
    if t < b:
        return ease((t - a) / max(b - a, 1e-6))
    if t <= c:
        return 1.0
    return 1 - ease((t - c) / max(d - c, 1e-6))


class Puppet:
    def __init__(self, rig, img, W=720, H=1280, fps=30, seed=3):
        self.W, self.H, self.fps, self.s = W, H, fps, W / RW
        self.rig = rig
        self.img = cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32)
        self.yy, self.xx = np.mgrid[0:H, 0:W].astype(np.float32)
        self.rng = np.random.default_rng(seed)
        self.fx = []
        for e in rig.get("effects", []):
            e = dict(e)
            if "mask" in e:
                e["_m"] = self.mask(e["mask"], e.get("soft", 25))
            if e["fx"] == "sparks":
                x0, x1, yb, yt = e["box"]
                e["_p"] = [dict(x=self.rng.uniform(x0, x1), ph=self.rng.uniform(0, 1), sp=self.rng.uniform(0.35, 0.7),
                                sway=self.rng.uniform(8, 30), r=int(self.rng.integers(2, 5))) for _ in range(e.get("n", 24))]
            if e["fx"] == "steam":
                e["_p"] = [dict(ph=i / 7, dx=self.rng.uniform(-14, 14)) for i in range(7)]
            self.fx.append(e)
        b = rig.get("blink")
        self.lid = None
        if b:
            s = self.s
            x, y = [int(v * s) for v in b["skin"]]
            skin = self.img[max(0, y - 5):y + 6, max(0, x - 5):x + 6].reshape(-1, 3).mean(0)
            lid, m = self.img.copy(), np.zeros((H, W), np.float32)
            for eye in b["eyes"]:
                c = (int(eye["c"][0] * s), int(eye["c"][1] * s))
                rx, ry, ang = eye["r"][0] * s, eye["r"][1] * s, eye.get("tilt", 0)
                cv2.ellipse(lid, c, (int(rx + 3 * s), int(ry + 3 * s)), ang, 0, 360, tuple(float(v) for v in skin), -1)
                cv2.ellipse(lid, (c[0], int(c[1] + 3 * s)), (int(rx), max(1, int(ry - 4 * s))), ang, 15, 165, (20, 14, 18),
                            max(1, int(3 * s)), cv2.LINE_AA)
                em = np.zeros((H, W), np.uint8)
                cv2.ellipse(em, c, (int(rx + 5 * s), int(ry + 5 * s)), ang, 0, 360, 255, -1)
                m = np.maximum(m, cv2.GaussianBlur(em, (0, 0), max(1.0, 1.5 * s)).astype(np.float32) / 255)
            self.lid, self.lid_m, self.blinks = lid, m[..., None], b.get("times")

    # ---- masks
    def _shape(self, spec):
        m = np.zeros((self.H, self.W), np.uint8)
        s = self.s
        if "ellipse" in spec:
            cx, cy, rx, ry, *rest = spec["ellipse"]
            cv2.ellipse(m, (int(cx * s), int(cy * s)), (max(1, int(rx * s)), max(1, int(ry * s))), rest[0] if rest else 0, 0, 360, 255, -1)
        else:
            cv2.fillPoly(m, [np.array([[x * s, y * s] for x, y in spec["poly"]], np.int32)], 255)
        return m

    def mask(self, spec, soft=25):
        specs = spec if isinstance(spec, list) else [spec]
        m = np.zeros((self.H, self.W), np.float32)
        for sp in specs:
            k = max(1.0, sp.get("soft", soft) * self.s / 2)
            part = cv2.GaussianBlur(self._shape(sp), (0, 0), k).astype(np.float32) / 255
            m = np.clip(m - part, 0, 1) if sp.get("minus") else np.clip(m + part, 0, 1)
        return m

    def _rot(self, m, pivot, deg):
        px, py = pivot[0] * self.s, pivot[1] * self.s
        a = np.radians(-deg) * m
        c, s = np.cos(a), np.sin(a)
        dx, dy = self.xx - px, self.yy - py
        return (px + c * dx - s * dy) - self.xx, (py + s * dx + c * dy) - self.yy

    # ---- one frame
    def frame(self, t, dur, zoom_extra=1.0, focus=None):
        W, H, s, xx, yy = self.W, self.H, self.s, self.xx, self.yy
        u = t / max(dur, 1e-6)
        src = self.img
        if self.lid is not None:
            times = self.blinks if self.blinks is not None else [0.9 + 2.9 * i for i in range(int(dur / 2.9) + 1)]
            b = max([1 - abs(t - bt) / 0.09 for bt in times] + [0])
            if b > 0:
                k = min(1.0, b * 1.6)
                src = self.img * (1 - self.lid_m * k) + self.lid * (self.lid_m * k)
        dx = np.zeros((H, W), np.float32)
        dy = np.zeros((H, W), np.float32)
        gain = None
        add = []
        for e in self.fx:
            k, m = e["fx"], e.get("_m")
            g = 0.0
            if "at" in e:
                a, b_, c, d = e["at"]
                g = bump(u, a, b_, c, d)
                if u > b_:  # small overshoot wobble after the move lands
                    g += 0.22 * math.sin((u - b_) * dur * 9) * math.exp(-(u - b_) * dur * 3) * (1 if u < c else 0)
            if k == "turn":
                deg = e.get("sway", 0) * math.sin(t * e.get("speed", 1.3) + e.get("phase", 0)) + e.get("gesture", 0) * g
                rx, ry = self._rot(m, e["pivot"], deg)
                dx += rx
                dy += ry
                if "lift" in e:
                    dx -= m * e["lift"][0] * s * g
                    dy -= m * e["lift"][1] * s * g
            elif k == "bob":
                w = math.sin(t * e.get("speed", 1.5) + e.get("phase", 0))
                dx -= m * e.get("dx", 0) * s * w
                dy -= m * e.get("dy", 0) * s * w
            elif k == "breath":
                cx, cy, rx, ry = [v * s for v in e["ellipse"][:4]]
                if m is None:
                    m = e["_m"] = self.mask({"ellipse": e["ellipse"]}, e.get("soft", 60))
                w = math.sin(t * 2 * math.pi / e.get("period", 3.3)) * e.get("amp", 2.6) * s
                dy += m * w * ((yy - cy) / ry)
                dx += m * 0.45 * w * ((xx - cx) / rx)
            elif k == "wind":
                amp, wl, sp = e.get("amp", 4) * s, e.get("wave", 100) * s, e.get("speed", 4.0)
                gust = math.sin(t * 2.3 + e.get("phase", 0)) + 0.5 * math.sin(t * 5.1 + 1)
                if e.get("axis", "x") == "x":
                    dx += m * (amp * np.sin(yy * (2 * math.pi / wl) - t * sp) + 0.6 * amp * gust)
                else:
                    dy += m * (amp * np.sin(xx * (2 * math.pi / wl) - t * sp) + 0.6 * amp * gust)
            elif k == "flame":
                amp = e.get("amp", 7) * s
                dx += m * (amp * np.sin(yy * (0.045 / s) + t * 10 + 2.0 * np.sin(xx * (0.03 / s))))
                dy += m * (0.85 * amp * (0.5 + 0.5 * np.sin(xx * (0.05 / s) - t * 8)))
                fl = 0.12 * math.sin(t * 11) + 0.08 * math.sin(t * 23 + 1) + 0.06 * self.rng.uniform(-1, 1)
                gain = (1 if gain is None else gain) + fl * m
            elif k == "shimmer":
                dx += m * (e.get("amp", 2.5) * s * np.sin(yy * (0.6 / s) + t * e.get("speed", 4.0)))
            elif k == "glow":
                fl = e.get("amount", 0.06) * (math.sin(t * 11) + 0.6 * math.sin(t * 23 + 1) + 0.5 * self.rng.uniform(-1, 1))
                gain = (1 if gain is None else gain) + fl * m
            elif k == "sparks":
                x0, x1, yb, yt = e["box"]
                col = e.get("color", [60, 170, 255])
                lay = np.zeros((H, W, 3), np.float32)
                for p_ in e["_p"]:
                    p = (t * p_["sp"] + p_["ph"]) % 1
                    x = p_["x"] + p_["sway"] * math.sin(p * 9 + p_["ph"] * 20) + e.get("drift", 60) * p
                    cv2.circle(lay, (int(x * s), int((yb + (yt - yb) * p) * s)), max(1, int(p_["r"] * s)),
                               tuple(float(c * (1 - p)) for c in col), -1, cv2.LINE_AA)
                add.append(cv2.GaussianBlur(lay, (0, 0), 1.6 * s) * 1.3)
            elif k == "steam":
                fx_, fy = e["from"]
                st = np.zeros((H, W), np.float32)
                for p_ in e["_p"]:
                    p = (t * e.get("speed", 0.22) + p_["ph"]) % 1
                    cv2.circle(st, (int((fx_ + p_["dx"] + e.get("spread", 22) * math.sin(p * 6 + p_["ph"] * 9)) * s),
                                    int((fy - e.get("rise", 190) * p) * s)), int((12 + 26 * p) * s * e.get("size", 1.0)),
                               float(0.5 * math.sin(math.pi * p)), -1, cv2.LINE_AA)
                st = cv2.GaussianBlur(st, (0, 0), 14 * s * e.get("size", 1.0))
                add.append(st[..., None] * np.array(e.get("color", [150, 140, 130]), np.float32) * e.get("strength", 1.0))
        out = cv2.remap(src, xx + dx, yy + dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        if gain is not None:
            out = out * gain[..., None]
        for a in add:
            out = out + a
        cam = self.rig.get("camera", {})
        z0, z1 = cam.get("zoom", [1.0, 1.06])
        fo = cam.get("focus", [360, 560])
        z = (z0 + (z1 - z0) * ease(u)) * zoom_extra
        cx, cy = (360 + (fo[0] - 360) * ease(u)) * s, (640 + (fo[1] - 640) * ease(u)) * s
        if focus is not None and zoom_extra != 1.0:
            cx, cy = focus[0] * W, focus[1] * H
        sh = cam.get("shake")
        if sh and u >= sh["at"]:
            k = max(0.0, 1 - (u - sh["at"]) * dur / sh.get("len", 0.5))
            cx += self.rng.uniform(-1, 1) * sh.get("amp", 14) * s * k
            cy += self.rng.uniform(-1, 1) * sh.get("amp", 14) * s * k
        if abs(z - 1) > 1e-4 or sh:
            out = cv2.warpAffine(out, np.float32([[z, 0, cx - z * cx], [0, z, cy - z * cy]]), (W, H), flags=cv2.INTER_LINEAR,
                                 borderMode=cv2.BORDER_REFLECT)
        return np.clip(out, 0, 255).astype(np.uint8)


def grid(src, dst):
    im = cv2.resize(cv2.imread(src), (RW, RH), interpolation=cv2.INTER_AREA)
    for x in range(0, RW, 60):
        cv2.line(im, (x, 0), (x, RH), (255, 255, 255) if x % 120 == 0 else (0, 255, 255), 1)
        cv2.putText(im, str(x), (x + 2, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)
    for y in range(0, RH, 60):
        cv2.line(im, (0, y), (RW, y), (255, 255, 255) if y % 120 == 0 else (0, 255, 255), 1)
        cv2.putText(im, str(y), (2, y + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)
    cv2.imwrite(dst, im)


def zoom_grid(src, dst, x0, y0, size=300):
    """3x enlargement of a square crop with a 30 px grid, for placing eyes."""
    im = cv2.resize(cv2.imread(src), (RW, RH), interpolation=cv2.INTER_AREA)[y0:y0 + size, x0:x0 + size]
    im = cv2.resize(im, (size * 3, size * 3), interpolation=cv2.INTER_CUBIC)
    for i in range(0, size * 3, 90):
        cv2.line(im, (i, 0), (i, size * 3), (0, 255, 255), 1)
        cv2.putText(im, str(x0 + i // 3), (i + 2, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        cv2.line(im, (0, i), (size * 3, i), (0, 255, 255), 1)
        cv2.putText(im, str(y0 + i // 3), (2, i + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
    cv2.imwrite(dst, im)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "--grid":
        grid(a[1], a[2])
        sys.exit()
    if a[0] == "--zoom":
        zoom_grid(a[1], a[2], int(a[3]), int(a[4]))
        sys.exit()
    opt = lambda n, d: type(d)(a[a.index(n) + 1]) if n in a else d
    secs, W, fps = opt("--seconds", 4.0), opt("--size", 720), opt("--fps", 30)
    H = W * 16 // 9
    pup = Puppet(json.load(open(a[0])), cv2.imread(a[1]), W, H, fps)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", "%dx%d" % (W, H),
                           "-r", str(fps), "-i", "-", "-an", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                           "-movflags", "+faststart", a[2]], stdin=subprocess.PIPE)
    n = int(secs * fps)
    for f in range(n):
        ff.stdin.write(pup.frame(f / fps, secs).tobytes())
    ff.stdin.close()
    ff.wait()
    print("wrote", a[2], n, "frames")
