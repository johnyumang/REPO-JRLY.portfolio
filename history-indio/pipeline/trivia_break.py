#!/usr/bin/env python3
"""Chibi trivia break ("PATALASTAS NI USMAN"): a 18-23 s joke-commercial interruption with one true, surprising fact
about the Philippines, told by chibi Indio and chibi Usman, cut into an episode at its best-retention point.
numpy + Pillow + soundfile + ffmpeg only; no network.

  trivia_break.py cutout --in art.png --out sprite.png [--bg auto|green|magenta|white] [--tol 70] [--outline 14]
  trivia_break.py render --spec spec.json --out break.mp4 [--size 720x1280] [--fps 30] [--sheet sheet.jpg]
                         [--stills 2.5,9,16] [--guides]
  trivia_break.py splice --video episode.mp4 --brk break.mp4 --at SECONDS --out out.mp4 [--force]

cutout: one subject on a flat green / magenta / white background -> RGBA cut-out (flood fill from the borders, so green
or white parts INSIDE the subject stay), soft edges, colour spill removed, cropped, thick white sticker outline and a
soft drop shadow.

render: spec.json (paths are relative to the spec file)
  {"title": "PATALASTAS NI USMAN", "subtitle": "trivia lang, walang bayad", "palette": "sun"|"sea"|"leaf",
   "sprites": {"INDIO": "indio.png", "USMAN": "usman.png"},
   "subjects": [{"image": "subject.png", "label": "KAGWANG", "from_line": 1}],
   "lines": [{"speaker": "USMAN", "text": "Teka, patalastas muna!", "wav": "l0.wav", "emphasis": ["patalastas"]}, ...],
   "source": "Pinagmulan: ...", "countdown_text": "babalik ang kuwento"}
  Timeline: 0.30 s lead, the line wavs in order with 0.16 s between them (or the spec's "gap"), 0.35 s tail. Sound: synthesised two-note
  sting, quiet rhythmic bed (at least 14 dB under the voice), synthesised whoosh at the end; mastered to -16 LUFS,
  true peak -1.5 dBTP; 48 kHz stereo AAC. Picture layout: see BOXES. THE FIRST RULE: nothing covers a face or the
  subject: the drawn extents of every element are computed before rendering (and tracked while rendering) and the
  command exits with code 3 naming the overlap if any two meet or anything important leaves the phone safe area.

splice: puts the break into the episode at --at (rounded to a frame), 0.20 s audio fades either side, one re-encode,
then the loudness guard and the full-decode check. Refuses (exit 2) if --at falls inside speech: the 120 ms around the
cut should be at least 12 dB under the episode's average level (warning, with the quietest frame nearby) and the 40 ms at
the cut itself must be (else refused; --force to override): music under the narration keeps whole pauses only ~10 dB down."""
import argparse, json, math, os, re, subprocess, sys, tempfile
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import soundtrack                                                  # loudnorm2 (two-pass, true-peak guard) and the targets
SR = 48000
LUFS, TP = soundtrack.LUFS, soundtrack.TP
FONTS = {'anton': 'Anton-Regular.ttf', 'archivo': 'ArchivoBlack-Regular.ttf', 'bebas': 'BebasNeue-Regular.ttf'}
INK = (24, 16, 30)
LEAD, GAP, TAIL = 0.30, 0.16, 0.35

# Layout, fractions of the frame (x0, y0, x1, y1). Phone safe area: nothing important above 9 %, below 82 % or right of 88 %.
SAFE = (0.0, 0.09, 0.88, 0.82)
BOXES = {
    'title':    (0.05, 0.093, 0.87, 0.168),
    'bar':      (0.09, 0.176, 0.83, 0.204),
    'subject':  (0.14, 0.212, 0.78, 0.384),
    'label':    (0.22, 0.389, 0.70, 0.424),
    'captions': (0.04, 0.430, 0.88, 0.534),
    'INDIO':    (0.02, 0.541, 0.44, 0.790),
    'USMAN':    (0.46, 0.541, 0.88, 0.790),
    'source':   (0.04, 0.796, 0.88, 0.818),
}
PALETTES = {   # a, b: the two sunburst tones; dot: halftone; accent: emphasis words; sticker/ribbon/bar fills
    'sun':  dict(a=(255, 208, 58), b=(255, 180, 40), dot=(255, 150, 34), accent=(255, 56, 80), sticker=(214, 20, 30),
                 title=(255, 226, 0), bar=(255, 92, 40), ribbon=(214, 20, 30), src=(70, 34, 8)),
    'sea':  dict(a=(76, 214, 222), b=(40, 172, 212), dot=(22, 140, 192), accent=(255, 226, 0), sticker=(18, 58, 140),
                 title=(255, 226, 0), bar=(255, 200, 0), ribbon=(18, 58, 140), src=(6, 40, 70)),
    'leaf': dict(a=(150, 222, 96), b=(104, 192, 74), dot=(74, 160, 62), accent=(255, 226, 0), sticker=(22, 104, 48),
                 title=(255, 240, 110), bar=(255, 140, 20), ribbon=(22, 104, 48), src=(18, 60, 20)),
}
# animation limits (the extents below are computed from these, so the layout check is exact)
GROW, SHRINK, BREATH, STRETCH, BOUNCE = 1.08, 0.94, 0.02, 0.05, 0.06   # chibi: speaking size, quiet size, idle, loudness
POP, WOB = 1.12, 5.0                                                     # subject / title / label pop overshoot, wobble deg
WPOP = 1.08                                                              # caption word pop overshoot
TILT = -3.0                                                              # title sticker tilt, deg
ENTRY = 0.42                                                             # chibi slide-in time (not checked: off-screen entry)


def font(name, size): return ImageFont.truetype(os.path.join(HERE, 'fonts', FONTS[name]), max(6, int(size)))
def ease_out_back(x, k=1.70158): x = min(max(x, 0.0), 1.0) - 1; return 1 + (k + 1) * x ** 3 + k * x ** 2
def ease_out(x): x = min(max(x, 0.0), 1.0); return 1 - (1 - x) ** 3
def px(box, W, H): return (box[0] * W, box[1] * H, box[2] * W, box[3] * H)
def inter(r, s): w = min(r[2], s[2]) - max(r[0], s[0]); h = min(r[3], s[3]) - max(r[1], s[1]); return (w, h) if w > 0 and h > 0 else None
def union(r, s): return s if r is None else (min(r[0], s[0]), min(r[1], s[1]), max(r[2], s[2]), max(r[3], s[3]))
def die(msg, code=3): print(msg, file=sys.stderr, flush=True); sys.exit(code)


# ---------------------------------------------------------------------------------------------------------- cutout
def _shift(m, dy, dx):
    o = np.zeros_like(m); H, W = m.shape
    o[max(0, dy):H + min(0, dy), max(0, dx):W + min(0, dx)] = m[max(0, -dy):H + min(0, -dy), max(0, -dx):W + min(0, -dx)]
    return o


def dilate(m, n, diag=True):
    for i in range(int(n)):
        o = m | _shift(m, 1, 0) | _shift(m, -1, 0) | _shift(m, 0, 1) | _shift(m, 0, -1)
        if diag and i % 2: o = o | _shift(m, 1, 1) | _shift(m, -1, -1) | _shift(m, 1, -1) | _shift(m, -1, 1)   # octagon ~ round
        m = o
    return m


def flood_from_border(cand):
    """the part of cand (bool) connected to the image border: the background, not same-coloured holes inside the subject."""
    seed = np.zeros_like(cand); seed[0, :] = seed[-1, :] = True; seed[:, 0] = seed[:, -1] = True
    bg = seed & cand; n = 0
    while True:
        nb = (bg | _shift(bg, 1, 0) | _shift(bg, -1, 0) | _shift(bg, 0, 1) | _shift(bg, 0, -1)) & cand
        n += 1
        if n % 8 == 0 or n < 8:
            if np.array_equal(nb, bg): return bg
        bg = nb


def blur(a, r): return np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255


def cutout(a):
    im = Image.open(a.inp).convert('RGBA')
    if max(im.size) > 1400: k = 1400 / max(im.size); im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    arr = np.asarray(im).astype(np.float32); rgb = arr[..., :3]; al0 = arr[..., 3] / 255
    border = np.concatenate([rgb[:3].reshape(-1, 3), rgb[-3:].reshape(-1, 3), rgb[:, :3].reshape(-1, 3), rgb[:, -3:].reshape(-1, 3)])
    bgc = np.median(border, 0); r, g, b = bgc; kind = a.bg
    if kind == 'auto':
        kind = 'green' if g > r + 40 and g > b + 40 else 'magenta' if min(r, b) > g + 40 else 'white' if bgc.min() > 200 else 'flat'
    if (al0 < 0.5).mean() > 0.05:                               # already transparent: keep its alpha
        alpha = al0; print('cutout: picture already has transparency; keeping its alpha')
    else:
        dist = np.sqrt(((rgb - bgc) ** 2).sum(-1)); tol = a.tol
        bg = flood_from_border(dist < tol)
        near = dilate(bg, 2, False) & dilate(~bg, 2, False)     # within 2 px of the edge, either side
        soft = np.clip((dist - tol * 0.6) / (tol * 1.2), 0, 1)
        alpha = np.where(near, soft, np.where(bg, 0.0, 1.0)).astype(np.float32)
        alpha = np.where(near, blur(alpha, 0.8), alpha)
        edge = dilate(bg, 4) & ~bg                                # decontaminate and despill only along the edge
        aa = np.clip(alpha, 0.25, 1)[..., None]
        dec = np.clip((rgb - (1 - aa) * bgc) / aa, 0, 255)
        rgb = np.where((edge & (alpha < 0.999))[..., None], dec, rgb)
        R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
        if kind == 'green':
            G = np.where(edge, np.minimum(G, np.maximum(R, B) * 1.04), G)
        elif kind == 'magenta':
            m = np.clip(np.minimum(R, B) - G, 0, None) * 0.7; R = np.where(edge, R - m, R); B = np.where(edge, B - m, B)
        rgb = np.stack([R, G, B], -1)
        print(f'cutout: background {kind} {tuple(int(v) for v in bgc)}, {bg.mean():.0%} of the picture removed')
    ys, xs = np.nonzero(alpha > 0.03)
    if not len(ys): die('cutout: nothing left after removing the background (raise --tol or check --bg)', 2)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    rgb, alpha = rgb[y0:y1, x0:x1], alpha[y0:y1, x0:x1]
    o = int(a.outline); sb = max(2, o * 0.6); sd = (round(o * 0.35), round(o * 0.55)); pad = o + int(sb * 3) + max(sd) + 2
    rgb = np.pad(rgb, ((pad, pad), (pad, pad), (0, 0)), constant_values=255); alpha = np.pad(alpha, pad)
    ring = blur(dilate(alpha > 0.5, o).astype(np.float32), 1.1) if o else alpha
    ring = np.clip((ring - 0.5) * 3 + 0.5, 0, 1)                    # crisp but anti-aliased sticker edge
    outa = np.maximum(alpha, ring)
    col = rgb * alpha[..., None] + 255 * (1 - alpha[..., None])      # the subject on its white sticker
    sh = blur(np.roll(np.roll(outa, sd[1], 0), sd[0], 1), sb) * 0.45
    fa = outa + sh * (1 - outa)
    col = (col * outa[..., None]) / np.maximum(fa, 1e-4)[..., None]  # black shadow under the sticker
    out = np.dstack([np.clip(col, 0, 255), fa * 255]).astype(np.uint8)
    Image.fromarray(out, 'RGBA').save(a.out); print('cutout:', a.out, out.shape[1], 'x', out.shape[0])


# ---------------------------------------------------------------------------------------------------------- audio
def read_audio(path, ch=1):
    tmp = tempfile.mktemp(suffix='.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', path, '-vn', '-ac', str(ch), '-ar', str(SR), '-c:a', 'pcm_f32le', tmp], check=True)
    x, _ = sf.read(tmp, dtype='float32', always_2d=True); os.remove(tmp)
    return x[:, 0] if ch == 1 else x


def gated_rms(x, win=0.4):
    w = int(win * SR); r = np.array([np.sqrt(np.mean(x[i:i + w] ** 2)) for i in range(0, max(1, len(x) - w), w)])
    r = r[r > r.max() * 0.1] if r.max() > 0 else r; return float(np.sqrt(np.mean(r ** 2))) if len(r) else 0.0


def sting():
    out = np.zeros(int(0.45 * SR), np.float32)
    for t0, f, d in ((0.0, 1046.5, 0.13), (0.10, 1568.0, 0.32)):
        n = int(d * SR); t = np.arange(n) / SR
        tone = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.18 * np.sin(6 * np.pi * f * t) + 0.12 * np.sin(2 * np.pi * f * 2.76 * t)
        env = np.minimum(1, t / 0.004) * np.exp(-t / (0.06 if d < 0.2 else 0.11))
        i = int(t0 * SR); out[i:i + n] += (tone * env).astype(np.float32)
    return out


def whoosh(d=0.55, seed=7):
    n = int(d * SR); x = np.random.default_rng(seed).normal(size=n).astype(np.float32); y = np.zeros(n, np.float32)
    p = np.arange(n) / n; fc = 300 + 5200 * np.sin(np.pi * np.clip(p / 0.8, 0, 1)) ** 2       # rising then falling filter
    k = 1 - np.exp(-2 * np.pi * fc / SR); s1 = s2 = 0.0
    for i in range(n):                                                                    # two one-pole low-passes
        s1 += k[i] * (x[i] - s1); s2 += k[i] * (s1 - s2); y[i] = s1 - 0.6 * s2           # minus some lows: airy band
    env = np.sin(np.pi * np.clip(p / 0.85, 0, 1)) ** 2
    m = y * env; pan = np.clip(p, 0, 1)
    return np.stack([m * np.cos(pan * np.pi / 2), m * np.sin(pan * np.pi / 2)], 1)          # sweeps left to right


def bed(dur, bpm=104, seed=3):
    n = int(round(dur * SR)); out = np.zeros(n, np.float32); rng = np.random.default_rng(seed); beat = 60 / bpm
    kn = int(0.16 * SR); kt = np.arange(kn) / SR
    kick = np.sin(2 * np.pi * (55 * kt + 60 * (1 - np.exp(-kt / 0.03)) * 0.03)) * np.exp(-kt / 0.07)
    hn = int(0.035 * SR); hat = np.diff(rng.normal(size=hn + 1)).astype(np.float32) * np.exp(-np.arange(hn) / SR / 0.012)
    pn = int(beat * 0.9 * SR); pt = np.arange(pn) / SR
    notes = [196.0, 246.9, 293.7, 246.9]                                                   # soft marimba-ish plucks
    k = 0; t = 0.0
    while t < dur:
        i = int(t * SR)
        if k % 2 == 0:
            seg = kick[:max(0, min(kn, n - i))]; out[i:i + len(seg)] += 0.9 * seg
            f = notes[(k // 2) % 4]; pl = (np.sin(2 * np.pi * f * pt) + 0.3 * np.sin(4 * np.pi * f * pt)) * np.exp(-pt / 0.12)
            seg = pl[:max(0, min(pn, n - i))]; out[i:i + len(seg)] += 0.35 * seg
        seg = hat[:max(0, min(hn, n - i))]; out[i:i + len(seg)] += (0.30 if k % 2 else 0.16) * seg
        k += 1; t += beat / 2
    f = np.minimum(1, np.minimum(np.arange(n) / (0.3 * SR), (n - np.arange(n)) / (0.4 * SR)))
    return out * f


def envelope(x, fps, n_frames):
    """loudness per video frame of one line's wav, 0..1, smoothed with a fast attack and a slower release (PNGtuber)."""
    hop = SR / fps; e = np.zeros(n_frames, np.float32)
    for i in range(n_frames):
        a, b = int(i * hop - hop / 2), int(i * hop + hop * 1.5); s = x[max(0, a):max(0, b)]
        e[i] = np.sqrt(np.mean(s ** 2)) if len(s) else 0
    ref = np.percentile(e[e > 0], 95) if (e > 0).any() else 1
    e = np.clip((e / max(ref, 1e-6) - 0.08) / 0.92, 0, 1)
    o = np.zeros_like(e); v = 0.0
    for i, x_ in enumerate(e): v += (x_ - v) * (0.6 if x_ > v else 0.22); o[i] = v
    return o


def ebur(path):
    e = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-vn', '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr.split('Summary')[-1]
    val = lambda k: float(next(l.split(':')[1].split()[0] for l in e.splitlines() if l.strip().startswith(k)))
    return val('I:'), val('Peak:')


def guard(path):
    """the two checks of build_anime.py on the finished file: loudness as delivered, and every video frame decodes."""
    i, tp = ebur(path); ok = abs(i - LUFS) <= 0.5 and tp <= TP
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path], capture_output=True, text=True).stdout.strip())
    print(f'final MP4: {dur:.3f} s, {i:.1f} LUFS (target {LUFS}, +-0.5), true peak {tp:.1f} dBTP (ceiling {TP})' + ('' if ok else '  -> LOUDNESS OUT OF RANGE'), flush=True)
    d = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-an', '-f', 'null', '-'], capture_output=True, text=True).stderr.strip().splitlines()
    if d: print(f'VIDEO STREAM DAMAGED: {len(d)} decode errors, first: {d[0][:160]}  -> do not publish this file', flush=True); return False
    print('video stream: every frame decodes', flush=True)
    return ok


def master(mix, out_wav):
    raw = tempfile.mktemp(suffix='.wav'); sf.write(raw, mix, SR, subtype='FLOAT')
    soundtrack.SR = SR                                            # loudnorm2 resamples to soundtrack.SR: keep 48 kHz
    b, a_ = soundtrack.loudnorm2(raw, out_wav); os.remove(raw); return b, a_


# ---------------------------------------------------------------------------------------------------------- text
def word_img(txt, size, fill, fname='anton', stroke_k=0.10, shadow=True):
    """one word, thick dark stroke, soft shadow; returns (RGBA image, baseline y inside the image)."""
    f = font(fname, size); sw = max(2, round(size * stroke_k)); off = max(1, round(size * 0.06)) if shadow else 0
    l, t, r, b = f.getbbox(txt, anchor='ls', stroke_width=sw)
    im = Image.new('RGBA', (r - l + off + 4, b - t + off + 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    org = (2 - l, 2 - t)
    if shadow:
        s = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(s).text((org[0] + off, org[1] + off), txt, font=f, anchor='ls', fill=INK + (190,), stroke_width=sw, stroke_fill=INK + (190,))
        im = Image.alpha_composite(im, s.filter(ImageFilter.GaussianBlur(max(1, off * 0.6)))); d = ImageDraw.Draw(im)
    d.text(org, txt, font=f, anchor='ls', fill=tuple(fill) + (255,), stroke_width=sw, stroke_fill=INK + (255,))
    return im, org[1]


def norm(w): return re.sub(r"[^\w']", '', w.lower())


def syllables(w):
    w = norm(w); v = len(re.findall(r'[aeiou]+', w))
    return v if v else max(1, len(re.sub(r'\D', '', w)) * 2 if re.search(r'\d', w) else len(w) // 2)


class Caption:
    """one spoken line laid out in the caption box: at most two lines, centred, words pop in on time."""
    def __init__(self, text, emphasis, box, pal, H):
        self.words = text.upper().split(); emph = {norm(e) for x in emphasis for e in x.split()}
        bw, bh = box[2] - box[0], box[3] - box[1]; self.box = box
        for size in range(int(H * 0.052), int(H * 0.023) - 1, -1):
            imgs = []
            for w in self.words:
                e = norm(w) in emph; im, base = word_img(w, size * (1.18 if e else 1.0), pal['accent'] if e else (255, 255, 255)); imgs.append((im, base, e))
            space = size * 0.22; widths = [im.width for im, _, _ in imgs]
            splits = [[list(range(len(imgs)))]] + [[list(range(k)), list(range(k, len(imgs)))] for k in range(1, len(imgs))]
            best = None
            for sp in splits:
                lw = [sum(widths[i] for i in ln) + space * (len(ln) - 1) for ln in sp]
                if max(lw) * WPOP <= bw and (best is None or max(lw) < best[0] - 1): best = (max(lw), sp, lw)
                if len(sp) == 1 and best: break                     # one line fits: prefer it
            if best is None: continue
            _, sp, lw = best
            asc = [max(imgs[i][1] for i in ln) for ln in sp]; desc = [max(imgs[i][0].height - imgs[i][1] for i in ln) for ln in sp]
            gap = size * 0.02; total = sum(asc) + sum(desc) + gap * (len(sp) - 1)
            if total * WPOP > bh: continue
            self.size = size; self.place = [None] * len(imgs); y = box[1] + (bh - total) / 2
            cx = (box[0] + box[2]) / 2
            for ln, w_, a_, d_ in zip(sp, lw, asc, desc):
                x = cx - w_ / 2; base = y + a_
                for i in ln:
                    im, b_, e = imgs[i]; self.place[i] = (im, round(x), round(base - b_)); x += im.width + space
                y = base + d_ + gap
            self.lines = len(sp); return
        die(f'LAYOUT: the caption "{text}" does not fit two lines in the caption box even at the smallest size: shorten it or split it into two spoken lines')

    def extent(self):
        r = None
        for im, x, y in self.place:
            cx, cy = x + im.width / 2, y + im.height / 2; r = union(r, (cx - im.width * WPOP / 2, cy - im.height * WPOP / 2, cx + im.width * WPOP / 2, cy + im.height * WPOP / 2))
        return r

    def times(self, start, s0, s1):
        """word appearance times: spread over the speech span [s0, s1] of the wav by syllable count."""
        syl = np.array([syllables(w) for w in self.words], float); c = np.concatenate([[0], np.cumsum(syl)[:-1]]) / syl.sum()
        self.t = start + s0 + c * (s1 - s0) * 0.94; self.t[0] = start   # the first word comes with the cut to the line


def wpop(p):
    if p >= 1: return 1.0, 1.0
    s = 0.6 + (WPOP - 0.6) * (p / 0.6) if p < 0.6 else WPOP - (WPOP - 1) * ((p - 0.6) / 0.4)
    return s, min(1.0, p / 0.4)


def paste(fr, im, cx, cy, s=1.0, rot=0.0, alpha=1.0):
    """paste RGBA im centred at (cx, cy), scaled and rotated; returns the drawn rectangle."""
    if s != 1.0: im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.BICUBIC)
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1.0: a = im.getchannel('A').point(lambda v: int(v * alpha)); im = im.copy(); im.putalpha(a)
    x, y = round(cx - im.width / 2), round(cy - im.height / 2); fr.paste(im, (x, y), im)
    return (x, y, x + im.width, y + im.height)


def opaque_rect(im, r):
    """the rectangle of the visible (alpha > 40) part of an image pasted at r: the soft shadow edge does not count."""
    bb = im.getchannel('A').point(lambda v: 255 if v > 40 else 0).getbbox()
    return (r[0] + bb[0], r[1] + bb[1], r[0] + bb[2], r[1] + bb[3]) if bb else None


def rot_size(w, h, deg):
    c, s = abs(math.cos(math.radians(deg))), abs(math.sin(math.radians(deg))); return w * c + h * s, w * s + h * c


def fit_scale(w, h, box, pop=1.0, deg=0.0):
    rw, rh = rot_size(w, h, deg); return min((box[2] - box[0]) / (rw * pop), (box[3] - box[1]) / (rh * pop))


def title_sticker(title, subtitle, pal, H):
    u = H * 0.05; f1 = font('anton', u); f2 = font('archivo', u * 0.36); sw = max(3, round(u * 0.08))
    w1 = f1.getlength(title); w2 = f2.getlength(subtitle) if subtitle else 0
    pw, ph = round(max(w1, w2) + u * 0.9), round(u * (1.42 + (0.5 if subtitle else 0)))
    bd = max(4, round(u * 0.12)); sh = max(4, round(u * 0.12))
    im = Image.new('RGBA', (pw + 2 * bd + sh + 4, ph + 2 * bd + sh + 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    R = round(u * 0.28)
    d.rounded_rectangle((2 + sh, 2 + sh, 2 + pw + 2 * bd + sh, 2 + ph + 2 * bd + sh), radius=R, fill=INK + (255,))
    d.rounded_rectangle((2, 2, 2 + pw + 2 * bd, 2 + ph + 2 * bd), radius=R, fill=(255, 255, 255, 255), outline=INK + (255,), width=max(2, bd // 3))
    d.rounded_rectangle((2 + bd, 2 + bd, 2 + pw + bd, 2 + ph + bd), radius=round(R * 0.7), fill=tuple(pal['sticker']) + (255,))
    cx = 2 + bd + pw / 2
    d.text((cx, 2 + bd + u * 0.74), title, font=f1, anchor='mm', fill=tuple(pal['title']) + (255,), stroke_width=sw, stroke_fill=INK + (255,))
    if subtitle: d.text((cx, 2 + bd + u * 1.52), subtitle, font=f2, anchor='mm', fill=(255, 255, 255, 255), stroke_width=max(1, sw // 2), stroke_fill=INK + (255,))
    return im


def ribbon(label, pal, H, accent):
    u = H * 0.03; f = font('archivo', u); w = f.getlength(label) + u * 1.4; h = u * 1.55; t = u * 0.9; sh = max(3, round(u * 0.1))
    im = Image.new('RGBA', (round(w + 2 * t + sh + 4), round(h + u * 0.4 + sh + 4)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x0, y0 = 2 + t, 2; dark = tuple(int(c * 0.6) for c in pal['ribbon']) + (255,)
    for sx in (-1, 1):                                              # folded tails with a notch, behind the band
        xa = x0 if sx < 0 else x0 + w; xb = xa + sx * t
        d.polygon([(xa, y0 + u * 0.4), (xb, y0 + u * 0.4), (xb - sx * t * 0.45, y0 + u * 0.4 + h / 2), (xb, y0 + u * 0.4 + h), (xa, y0 + u * 0.4 + h)], fill=dark, outline=INK + (255,))
    d.rectangle((x0 + sh, y0 + sh, x0 + w + sh, y0 + h + sh), fill=INK + (255,))
    d.rectangle((x0, y0, x0 + w, y0 + h), fill=tuple(pal['ribbon']) + (255,), outline=INK + (255,), width=max(2, round(u * 0.08)))
    d.text((x0 + w / 2, y0 + h / 2), label, font=f, anchor='mm', fill=tuple(accent) + (255,), stroke_width=max(2, round(u * 0.08)), stroke_fill=INK + (255,))
    return im


def star(d, cx, cy, r, rot, fill):
    pts = [(cx + math.cos(rot + k * math.pi / 4) * (r if k % 2 == 0 else r * 0.38), cy + math.sin(rot + k * math.pi / 4) * (r if k % 2 == 0 else r * 0.38)) for k in range(8)]
    d.polygon(pts, fill=fill, outline=INK); return pts


def background(W, H, pal, center):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    ang = np.arctan2(yy - center[1], xx - center[0]); rad = np.hypot(xx - center[0], yy - center[1]) / H
    gain = 1 + 0.16 * np.exp(-(rad / 0.32) ** 2) - 0.10 * np.clip(rad - 0.45, 0, 1)
    cell = max(8, round(W / 30)); cxg = (xx % cell) - cell / 2; cyg = (yy % cell) - cell / 2
    dr = cell * 0.46 * np.clip((rad - 0.25) / 0.5, 0, 1) ** 1.2                                  # halftone: bigger dots outward
    dots = (np.hypot(cxg, cyg) < dr).astype(np.float32)[..., None]
    mk = lambda c: np.clip((np.array(c, np.float32) * (1 - dots) + np.array(pal['dot'], np.float32) * dots) * gain[..., None], 0, 255)
    return ang, mk(pal['a']).astype(np.uint8), mk(pal['b']).astype(np.uint8)


# ---------------------------------------------------------------------------------------------------------- render
def render(a):
    W, H = (int(v) for v in a.size.lower().split('x')); fps = a.fps
    spec = json.load(open(a.spec)); base = os.path.dirname(os.path.abspath(a.spec)); P = lambda p: p if os.path.isabs(p) else os.path.join(base, p)
    pal = PALETTES[spec.get('palette', 'sun')]; lines = spec['lines']
    if not lines: die('spec has no lines', 2)
    # format rules (warnings: the sample can still be looked at)
    if norm(lines[0]['text']) != norm('Teka, patalastas muna!') or lines[0]['speaker'] != 'USMAN': print('WARNING: line 1 should be USMAN: "Teka, patalastas muna!"')
    if norm(lines[-1]['text']) != norm('Balik sa kuwento, par!') or lines[-1]['speaker'] != 'INDIO': print('WARNING: the last line should be INDIO: "Balik sa kuwento, par!"')
    mid_words = sum(len(l['text'].split()) for l in lines[1:-1])
    if mid_words > 40 or not 2 <= len(lines) - 2 <= 4: print(f'WARNING: the middle should be 2 to 4 lines and at most 40 words (now {len(lines) - 2} lines, {mid_words} words)')
    if not spec.get('source'): print('WARNING: no "source" line: every fact needs its sources on screen')

    # ---- sound and timeline
    gap = float(spec.get('gap', GAP))                                                     # optional: pause between lines, s
    voices = [read_audio(P(l['wav'])) for l in lines]; starts = []; t = LEAD
    for i, v in enumerate(voices): starts.append(t); t += len(v) / SR + (gap if i + 1 < len(voices) else 0)
    T = t + TAIL; N = round(T * fps); T = N / fps; n = int(round(T * SR))
    print(f'break: {T:.2f} s, {N} frames, {len(lines)} lines' + ('' if 18 <= T <= 23 else '  (WARNING: the format is 18 to 23 s)'), flush=True)
    vo = np.zeros(n, np.float32)
    for s, v in zip(starts, voices): i = int(s * SR); vo[i:i + len(v)] += v[:n - i]
    rv = gated_rms(vo); db = lambda x: 20 * np.log10(max(x, 1e-9))
    st = sting(); st *= rv * 10 ** (-3 / 20) / gated_rms(st)
    wh = whoosh(); wh *= rv * 10 ** (-6 / 20) / gated_rms(wh.mean(1))
    bd = bed(T); bd *= rv * 10 ** (-18 / 20) / gated_rms(bd)
    mix = np.repeat(vo[:, None], 2, 1) + np.repeat(bd[:, None], 2, 1)
    mix[:len(st)] += st[:, None]; i = n - len(wh); mix[i:] += wh[:n - i]
    print(f'mix vs voice: bed {db(gated_rms(bd)) - db(rv):.1f} dB, sting {db(gated_rms(st)) - db(rv):+.1f} dB, whoosh {db(gated_rms(wh.mean(1))) - db(rv):+.1f} dB', flush=True)
    if db(gated_rms(bd)) - db(rv) > -14: die('the bed is not 14 dB under the voice', 4)
    wav = tempfile.mktemp(suffix='.wav'); b4, af = master(mix, wav); print(f'mastered: {b4:.1f} -> {af:.1f} LUFS', flush=True)

    # ---- layout and drawn extents
    BX = {k: px(v, W, H) for k, v in BOXES.items()}; ext = {}
    sprites = {}
    for name in ('INDIO', 'USMAN'):
        p = spec.get('sprites', {}).get(name)
        if not p or not os.path.exists(P(p)): print(f'note: no sprite for {name}: skipped'); continue
        im = Image.open(P(p)).convert('RGBA'); im = im.crop(im.getchannel('A').getbbox()); box = BX[name]
        k = min((box[3] - box[1]) / (im.height * (GROW * (1 + BREATH + STRETCH) + BOUNCE)), (box[2] - box[0]) / (im.width * GROW * (1 + BREATH)))
        im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
        dim = Image.eval(im.convert('RGB'), lambda v: int(v * 0.80)).convert('RGBA'); dim.putalpha(im.getchannel('A'))
        cx = (box[0] + box[2]) / 2; bot = box[3]
        sprites[name] = dict(im=im, dim=dim, cx=cx, bot=bot, ph=0.0 if name == 'INDIO' else 1.7, delay=0.0 if name == 'INDIO' else 0.08,
                             side=-1 if name == 'INDIO' else 1)
        hw = im.width * GROW * (1 + BREATH) / 2
        ext[name] = (cx - hw, bot - im.height * (GROW * (1 + BREATH + STRETCH) + BOUNCE), cx + hw, bot)
    subs = []
    for s in spec.get('subjects', []):
        im = Image.open(P(s['image'])).convert('RGBA'); im = im.crop(im.getchannel('A').getbbox()); box = BX['subject']
        k = fit_scale(im.width, im.height, box, POP, WOB); im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2; rw, rh = rot_size(im.width, im.height, WOB)
        sub = dict(im=im, cx=cx, cy=cy, t0=starts[min(int(s.get('from_line', 1)), len(starts) - 1)], rib=None)
        ext['subject'] = union(ext.get('subject'), (cx - rw * POP / 2, cy - rh * POP / 2, cx + rw * POP / 2, cy + rh * POP / 2))
        if s.get('label'):
            rb = ribbon(s['label'].upper(), pal, H, (255, 255, 255)); lb = BX['label']; k = min(1.0, fit_scale(rb.width, rb.height, lb, POP))
            if k < 1: rb = rb.resize((round(rb.width * k), round(rb.height * k)), Image.LANCZOS)
            sub['rib'] = (rb, (lb[0] + lb[2]) / 2, (lb[1] + lb[3]) / 2)
            ext['label'] = union(ext.get('label'), (sub['rib'][1] - rb.width * POP / 2, sub['rib'][2] - rb.height * POP / 2, sub['rib'][1] + rb.width * POP / 2, sub['rib'][2] + rb.height * POP / 2))
        subs.append(sub)
    subs.sort(key=lambda s: s['t0'])
    ts = title_sticker(spec.get('title', 'PATALASTAS NI USMAN').upper(), spec.get('subtitle', ''), pal, H); tb = BX['title']
    k = fit_scale(ts.width, ts.height, tb, POP, abs(TILT)); ts = ts.resize((round(ts.width * k), round(ts.height * k)), Image.LANCZOS)
    tcx, tcy = (tb[0] + tb[2]) / 2, (tb[1] + tb[3]) / 2; rw, rh = rot_size(ts.width, ts.height, TILT)
    ext['title'] = (tcx - rw * POP / 2, tcy - rh * POP / 2, tcx + rw * POP / 2, tcy + rh * POP / 2)
    ext['bar'] = BX['bar']
    caps = []
    for li, (l, s) in enumerate(zip(lines, starts)):
        c = Caption(l['text'], l.get('emphasis', []), BX['captions'], pal, H); env = envelope(voices[li], fps, int(len(voices[li]) / SR * fps) + 2)
        on = np.nonzero(env > 0.15)[0]; s0, s1 = (on[0] / fps, (on[-1] + 1) / fps) if len(on) else (0, len(voices[li]) / SR)
        c.times(s, s0, s1); c.env = env; c.start = s; c.end = s + len(voices[li]) / SR; caps.append(c)
        ext[f'captions (line {li + 1})'] = c.extent()
    src = spec.get('source', ''); sb = BX['source']; srcim = None
    if src:
        for size in range(int((sb[3] - sb[1]) * 0.95), 11, -1):
            f = font('archivo', size)
            if f.getlength(src) + size * 0.3 <= sb[2] - sb[0]: break
        else: die(f'LAYOUT: the source line is too long for one line even at 12 px: shorten it ("{src}")')
        sw = max(1, round(size * 0.14)); l_, t_, r_, b_ = f.getbbox(src, stroke_width=sw)
        srcim = Image.new('RGBA', (r_ - l_ + 2, b_ - t_ + 2), (0, 0, 0, 0))
        ImageDraw.Draw(srcim).text((1 - l_, 1 - t_), src, font=f, fill=tuple(pal['src']) + (255,), stroke_width=sw, stroke_fill=(255, 255, 255, 235))
        sx, sy = (sb[0] + sb[2]) / 2 - srcim.width / 2, (sb[1] + sb[3]) / 2 - srcim.height / 2
        ext['source'] = (sx, sy, sx + srcim.width, sy + srcim.height)
    check_layout(ext, W, H)

    # ---- per-frame state of the two chibis: who speaks, how loud
    act = {k: np.zeros(N, np.float32) for k in sprites}; loud = {k: np.zeros(N, np.float32) for k in sprites}
    for c, l in zip(caps, lines):
        f0, f1 = int(round(c.start * fps)), int(round(c.end * fps))
        for k in sprites:
            tgt = 1.0 if l['speaker'] == k else -1.0
            act[k][f0:min(N, f1 + int(gap * fps) + 1)] = tgt
            if l['speaker'] == k: e = c.env[:max(0, min(N, f1) - f0)]; loud[k][f0:f0 + len(e)] = e
    for k in sprites:                                                       # smooth the speaking state (no pops)
        v = 0.0; a_ = act[k]
        for i in range(N): v += (a_[i] - v) * 0.25; a_[i] = v

    # ---- frames
    ang, BG_A, BG_B = background(W, H, pal, ((BX['subject'][0] + BX['subject'][2]) / 2, (BX['subject'][1] + BX['subject'][3]) / 2))
    bursts = [(0.04, tcx, tcy, rw / 2, 9)] + [(s['t0'], s['cx'], s['cy'], max(s['im'].size) / 2, 11) for s in subs]
    stills = [float(x) for x in a.stills.split(',')] if a.stills else []
    track = {}; thumbs = []
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-', '-i', wav,
                           '-map', '0:v', '-map', '1:a', '-t', f'{T:.4f}', '-c:v', 'libx264', '-profile:v', 'high', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
                           '-c:a', 'aac', '-b:a', '192k', '-ar', str(SR), '-ac', '2', '-movflags', '+faststart', a.out], stdin=subprocess.PIPE)
    fbar = font('archivo', (BX['bar'][3] - BX['bar'][1]) * 0.52); rng = np.random.default_rng(11)
    star_seed = [rng.random((14, 3)) for _ in bursts]
    for fi in range(N):
        t = fi / fps
        stripe = (((ang + t * 0.10) * (16 / (2 * np.pi))) % 1.0) < 0.5
        fr = Image.fromarray(np.where(stripe[..., None], BG_A, BG_B)); d = ImageDraw.Draw(fr)
        for (t0, cx, cy, r0, cnt), sd in zip(bursts, star_seed):           # sparkles burst at each pop, behind everything
            p = (t - t0) / 0.7
            if 0 <= p < 1:
                for j in range(cnt):
                    an = j / cnt * 2 * np.pi + sd[j, 0] * 0.5; dist = r0 * 0.7 + (r0 * 0.6 + H * 0.05) * ease_out(p) * (0.7 + 0.6 * sd[j, 1])
                    rr = H * (0.010 + 0.010 * sd[j, 2]) * (1 - p) ** 0.7
                    if rr > 1: star(d, cx + math.cos(an) * dist, cy + math.sin(an) * dist * 0.8, rr, p * 3 + j, (255, 255, 255) if j % 2 else tuple(pal['title']))
        # title sticker: pops in with an overshoot in the first 0.4 s
        p = t / 0.4; s = 0.0 if p <= 0 else (ease_out_back(p, 2.2) if p < 1 else 1.0)
        if s > 0.02: r = paste(fr, ts, tcx, tcy, min(s, POP), TILT); note(track, 'title', ts, r, s, TILT, t)
        # countdown bar
        bx0, by0, bx1, by1 = BX['bar']; left = max(0.0, 1 - t / T); hb = by1 - by0
        d.rounded_rectangle((bx0, by0, bx1, by1), radius=hb / 2, fill=INK, outline=(255, 255, 255), width=max(2, round(hb * 0.10)))
        ins = max(3, round(hb * 0.18))
        if left > 0.01: d.rounded_rectangle((bx0 + ins, by0 + ins, bx0 + ins + (bx1 - bx0 - 2 * ins) * left, by1 - ins), radius=(hb - 2 * ins) / 2, fill=tuple(pal['bar']))
        d.text((bx0 + hb * 0.7, (by0 + by1) / 2), spec.get('countdown_text', 'babalik ang kuwento').upper(), font=fbar, anchor='lm', fill=(255, 255, 255), stroke_width=2, stroke_fill=INK)
        d.text((bx1 - hb * 0.7, (by0 + by1) / 2), f'{math.ceil(T - t - 1e-6)}s', font=fbar, anchor='rm', fill=(255, 255, 255), stroke_width=2, stroke_fill=INK)
        # subject cut-out and its ribbon
        cur = [s_ for s_ in subs if s_['t0'] <= t]
        if cur:
            s_ = cur[-1]; q = t - s_['t0']; p = q / 0.45
            sc = ease_out_back(p, 2.0) if p < 1 else 1.0 + 0.012 * math.sin(q * 2.2)
            rot = WOB * math.exp(-q * 4.5) * math.sin(q * 16) + 1.2 * math.sin(q * 1.4)
            if sc > 0.02:
                sc = min(sc, POP); r = paste(fr, s_['im'], s_['cx'], s_['cy'], sc, rot); note(track, 'subject', s_['im'], r, sc, rot, t)
            if s_['rib']:
                p2 = (q - 0.12) / 0.4; sc2 = 0.0 if p2 <= 0 else (min(POP, ease_out_back(p2, 2.0)) if p2 < 1 else 1.0)
                if sc2 > 0.02: rb, rx, ry = s_['rib']; r = paste(fr, rb, rx, ry, sc2); note(track, 'label', rb, r, sc2, 0, t)
        # captions of the current line (until the next line starts; the last one stays through the tail)
        li = max([i for i, c in enumerate(caps) if c.start <= t + 1e-6], default=None)
        if li is not None:
            c = caps[li]
            for (im, x, y), tw in zip(c.place, c.t):
                if t < tw: continue
                s, al = wpop((t - tw) / 0.14)
                r = paste(fr, im, x + im.width / 2, y + im.height / 2, s, 0, al); note(track, f'captions (line {li + 1})', im, r, s, 0, t)
        # chibis
        for k, sp in sprites.items():
            te = (t - sp['delay']) / ENTRY
            if te <= 0: continue
            a_ = float(act[k][fi]); e = float(loud[k][fi]) * max(0.0, a_)
            size = 1 + (GROW - 1) * max(0, a_) - (1 - SHRINK) * max(0, -a_)
            br = math.sin(2 * math.pi * t / 1.7 + sp['ph'])
            sy = size * (1 + BREATH * br + STRETCH * e); sx = size * (1 - BREATH * br * 0.5 - 0.03 * e)
            up = BOUNCE * sp['im'].height * e
            dx = 0.0
            if te < 1:
                ee = ease_out_back(te, 1.4); dx = sp['side'] * (1 - ee) * (W * 0.62); up += math.sin(math.pi * te) * 0.12 * sp['im'].height
            src_im = sp['im'] if a_ >= 0 else Image.blend(sp['im'], sp['dim'], min(1.0, -a_))
            w_, h_ = max(1, round(sp['im'].width * sx)), max(1, round(sp['im'].height * sy))
            im = src_im.resize((w_, h_), Image.BICUBIC); x = round(sp['cx'] + dx - w_ / 2); y = round(sp['bot'] - up - h_)
            fr.paste(im, (x, y), im)
            if te >= 1: note(track, k, im, (x, y, x + w_, y + h_), 1, 0, t)
        if srcim is not None: fr.paste(srcim, (round(ext['source'][0]), round(ext['source'][1])), srcim)
        if a.guides: guides(fr, W, H, ext)
        # 3-frame white flash on the first and last frames
        wf = {0: 0.9, 1: 0.6, 2: 0.3, N - 3: 0.3, N - 2: 0.6, N - 1: 0.9}.get(fi)
        if wf: fr = Image.blend(fr, Image.new('RGB', fr.size, (255, 255, 255)), wf)
        if fi % fps == fps // 2: thumbs.append((t, fr.resize((W // 4, H // 4), Image.LANCZOS)))
        for st_ in stills:
            if fi == round(st_ * fps): p_ = f'{os.path.splitext(a.out)[0]}_t{st_:05.2f}.png'; fr.save(p_); print('still', p_)
        ff.stdin.write(fr.tobytes())
    ff.stdin.close(); rc = ff.wait(); os.remove(wav)
    if rc: die('ffmpeg failed', rc)
    bad = [f'{k}: drawn at {tuple(round(v) for v in r)}, outside its checked area {tuple(round(v) for v in ext[k])}' for k, r in track.items()
           if k in ext and (r[0] < ext[k][0] - 2 or r[1] < ext[k][1] - 2 or r[2] > ext[k][2] + 2 or r[3] > ext[k][3] + 2)]
    if a.sheet: sheet(thumbs, a.sheet, T)
    ok = guard(a.out)
    for b_ in bad: print('LAYOUT DRIFT:', b_)
    print('layout: nothing covers the faces or the subject' if not bad else 'layout: see LAYOUT DRIFT above')
    sys.exit(0 if ok and not bad else 4)


def note(track, k, im, r, s, rot, t):
    """keep the union of the visible part of what was really drawn (to confirm the pre-render layout check held)."""
    if t < ENTRY + 0.1 and k in ('INDIO', 'USMAN'): return
    o = opaque_rect(im.resize((max(1, round(im.width * s)), max(1, round(im.height * s)))) if s != 1 else im, (0, 0)) if not rot else None
    rr = (r[0] + o[0], r[1] + o[1], r[0] + o[2], r[1] + o[3]) if o else r
    track[k] = union(track.get(k), rr)


def check_layout(ext, W, H):
    sa = (SAFE[0] * W, SAFE[1] * H, SAFE[2] * W, SAFE[3] * H); errs = []
    for k, r in ext.items():
        if r[0] < sa[0] - 0.5 or r[1] < sa[1] - 0.5 or r[2] > sa[2] + 0.5 or r[3] > sa[3] + 0.5:
            errs.append(f'{k} leaves the phone safe area: {tuple(round(v) for v in r)} vs {tuple(round(v) for v in sa)}')
    ks = list(ext)
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            a_, b_ = ks[i], ks[j]
            if a_.startswith('captions') and b_.startswith('captions'): continue   # only one caption line shows at a time
            o = inter(ext[a_], ext[b_])
            if o: errs.append(f'{a_} would cover {b_} ({o[0]:.0f} x {o[1]:.0f} px)')
    for e in errs: print('OVERLAP:', e, file=sys.stderr)
    if errs: die(f'LAYOUT CHECK FAILED ({len(errs)}): nothing may cover a face or the subject; shorten text or change BOXES')
    print('layout check: ' + ', '.join(f'{k} {tuple(round(v / (W if n % 2 == 0 else H), 3) for n, v in enumerate(r))}' for k, r in ext.items() if not k.startswith('captions (line ') or k.endswith('(line 1)')), flush=True)


def guides(fr, W, H, ext):
    d = ImageDraw.Draw(fr); s = SAFE
    d.rectangle((s[0] * W, s[1] * H, s[2] * W - 1, s[3] * H), outline=(0, 255, 0), width=2)
    for k, r in ext.items(): d.rectangle(r, outline=(0, 200, 255), width=1)


def sheet(thumbs, out, T):
    if not thumbs: return
    tw, th = thumbs[0][1].size; cols = min(6, len(thumbs)); rows = math.ceil(len(thumbs) / cols); pad = 10; top = 46
    S = Image.new('RGB', (cols * (tw + pad) + pad, top + rows * (th + pad + 22) + pad), (18, 18, 20)); d = ImageDraw.Draw(S)
    d.text((pad, 12), f'PATALASTAS NI USMAN: one frame per second, {T:.1f} s', font=font('archivo', 20), fill=(255, 226, 0))
    f = font('archivo', 15)
    for i, (t, im) in enumerate(thumbs):
        x = pad + (i % cols) * (tw + pad); y = top + (i // cols) * (th + pad + 22)
        S.paste(im, (x, y + 20)); d.text((x, y + 2), f'{t:.1f} s', font=f, fill=(220, 220, 220))
    S.save(out, quality=90); print('sheet', out, S.size)


# ---------------------------------------------------------------------------------------------------------- splice
def probe(path):
    j = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', path], capture_output=True, text=True, check=True).stdout)
    v = next(s for s in j['streams'] if s['codec_type'] == 'video'); n, dn = v['r_frame_rate'].split('/')
    return int(v['width']), int(v['height']), int(n) / int(dn), float(j['format']['duration'])


def splice(a):
    W, H, fps, dur = probe(a.video); bw, bh, bfps, bdur = probe(a.brk)
    nf = round(a.at * fps); at = nf / fps
    if not 0 < at < dur: die(f'--at {a.at} is outside the episode (0..{dur:.2f} s)', 2)
    ep = read_audio(a.video, 2); br = read_audio(a.brk, 2)
    mono = ep.mean(1); c = int(at * SR)
    lv = lambda c_, h: 20 * np.log10(max(1e-9, float(np.sqrt(np.mean(mono[max(0, c_ - h):c_ + h] ** 2)))))
    avg = 20 * np.log10(max(1e-9, gated_rms(mono))); lvl = lv(c, int(0.060 * SR)); core = lv(c, int(0.020 * SR))
    print(f'cut at {at:.3f} s (frame {nf}): 120 ms around it {lvl:.1f} dBFS ({avg - lvl:.1f} dB under the episode average {avg:.1f}), '
          f'40 ms at the cut {core:.1f} dBFS ({avg - core:.1f} dB under)', flush=True)
    if avg - lvl < 12:                                       # the music bed and nearby SFX keep pauses only ~6-12 dB down
        q = min(range(-15, 16), key=lambda k: lv(c + int(k * SR / fps), int(0.060 * SR)))
        print(f'WARNING: the 120 ms around the cut is only {avg - lvl:.1f} dB under the average (want 12); '
              f'quietest nearby: {at + q / fps:.3f} s ({avg - lv(c + int(q * SR / fps), int(0.060 * SR)):.1f} dB under)', flush=True)
    if avg - core < 12 and not a.force:                      # the cut itself is in speech: refuse
        die(f'refused: --at {at:.3f} falls inside speech ({avg - core:.1f} dB under the average at the cut); '
            'pick a pause between sentences (timings.json), or --force', 2)
    nb = round(bdur * fps); bt = nb / fps
    fade = int(0.06 * SR); A = ep[:c].copy(); Bq = ep[c:].copy()     # short fade: a pause can be ~0.35 s; longer dims the words
    A[-fade:] *= np.linspace(1, 0, fade, dtype=np.float32)[:, None]; Bq[:fade] *= np.linspace(0, 1, fade, dtype=np.float32)[:, None]
    br = br[:int(round(bt * SR))]; br = np.pad(br, ((0, int(round(bt * SR)) - len(br)), (0, 0)))
    mix = np.concatenate([A, br, Bq]); n_all = int(round((round(dur * fps) + nb) / fps * SR))      # audio as long as the picture
    mix = np.pad(mix[:n_all], ((0, max(0, n_all - len(mix))), (0, 0))); wav = tempfile.mktemp(suffix='.wav')
    b4, af = master(mix, wav); print(f'spliced audio mastered: {b4:.1f} -> {af:.1f} LUFS', flush=True)
    vf = (f'[0:v]split[e0][e1];[e0]trim=end_frame={nf},setpts=PTS-STARTPTS,fps={fps},setsar=1,format=yuv420p[v0];'
          f'[1:v]scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,fps={fps},setsar=1,format=yuv420p,trim=end_frame={nb},setpts=PTS-STARTPTS[v1];'
          f'[e1]trim=start_frame={nf},setpts=PTS-STARTPTS,fps={fps},setsar=1,format=yuv420p[v2];[v0][v1][v2]concat=n=3:v=1:a=0[v]')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', a.video, '-i', a.brk, '-i', wav, '-filter_complex', vf, '-map', '[v]', '-map', '2:a',
                    '-c:v', 'libx264', '-profile:v', 'high', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', str(fps),
                    '-c:a', 'aac', '-b:a', '192k', '-ar', str(SR), '-ac', '2', '-shortest', '-movflags', '+faststart', a.out], check=True)
    os.remove(wav)
    print(f'episode {dur:.3f} s + break {bt:.3f} s at {at:.3f} s', flush=True)
    sys.exit(0 if guard(a.out) else 4)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0]); sub = p.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('cutout'); c.add_argument('--in', dest='inp', required=True); c.add_argument('--out', required=True)
    c.add_argument('--bg', default='auto', choices=['auto', 'green', 'magenta', 'white', 'flat']); c.add_argument('--tol', type=float, default=70)
    c.add_argument('--outline', type=int, default=14)
    r = sub.add_parser('render'); r.add_argument('--spec', required=True); r.add_argument('--out', required=True)
    r.add_argument('--size', default='720x1280'); r.add_argument('--fps', type=int, default=30); r.add_argument('--sheet')
    r.add_argument('--stills', help='comma-separated times: also save these frames as PNG next to --out'); r.add_argument('--guides', action='store_true')
    s = sub.add_parser('splice'); s.add_argument('--video', required=True); s.add_argument('--brk', required=True)
    s.add_argument('--at', type=float, required=True); s.add_argument('--out', required=True); s.add_argument('--force', action='store_true')
    a = p.parse_args(); {'cutout': cutout, 'render': render, 'splice': splice}[a.cmd](a)
