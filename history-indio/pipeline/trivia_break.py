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
   "source": "Pinagmulan: ...", "countdown_text": "babalik ang kuwento",
   optional: "layout": "bold" (default: BOLD) | "classic" (version 1: BOXES), "joke_line": index of the joke (default: the
   one before the last; the listener cracks up on it), subjects[].pulse: words that make the subject pulse (default: the label)}
  Timeline: 0.30 s lead, the line wavs in order with 0.16 s between them (or the spec's "gap"), 0.35 s tail. Sound: synthesised two-note
  sting, quiet rhythmic bed (mixed 18 dB under the voice; refused if less than 14 dB), synthesised whoosh at the end; mastered to -16 LUFS,
  true peak -1.5 dBTP; 48 kHz stereo AAC. Picture layout: see BOLD (or BOXES for classic). THE FIRST RULE: nothing covers a face or the
  subject: the drawn extents of every element are computed before rendering (and tracked while rendering) and the
  command exits with code 3 naming the overlap if any two meet or anything important leaves the phone safe area.

splice: puts the break into the episode at --at (rounded to a frame), 0.06 s audio fades either side, one re-encode,
then the loudness guard and the full-decode check. Refuses (exit 2) if --at falls inside speech: the 120 ms around the
cut should be at least 12 dB under the episode's average level (warning, with the quietest frame nearby) and the 40 ms at
the cut itself must be (else refused; --force to override): music under the narration keeps whole pauses only ~10 dB down."""
import argparse, json, math, os, re, subprocess, sys, tempfile
import numpy as np, soundfile as sf
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageFilter

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
    'INDIO':    (0.02, 0.541, 0.44, 0.774),
    'USMAN':    (0.46, 0.541, 0.88, 0.774),
    'source':   (0.04, 0.778, 0.88, 0.8165),
}
SRC_X1 = 0.875                                                       # the source line stays left of 87.5 % (x = 630 of 720)
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
BOB, BOBT = 4 / 1280, 1.5                                                # subject idle bob: +-amplitude (fraction of H), period s
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
def word_img(txt, size, fill, fname='anton', stroke_k=0.10, shadow=True, plain=(255, 255, 255)):
    """one word, thick dark stroke, soft shadow; returns (RGBA image, baseline y inside the image, stroke px).
    fill colours the word; leading / trailing punctuation (quotes, comma, period...) is drawn in `plain`."""
    f = font(fname, size); sw = max(2, round(size * stroke_k)) if stroke_k > 0 else 0; off = max(1, round(size * 0.06)) if shadow else 0
    m = re.match(r"^(\W*)(.*?)(\W*)$", txt); segs = [(s_, c_) for s_, c_ in ((m.group(1), plain), (m.group(2), fill), (m.group(3), plain)) if s_]
    l, t, r, b = f.getbbox(txt, anchor='ls', stroke_width=sw)
    im = Image.new('RGBA', (r - l + off + 4, b - t + off + 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    org = (2 - l, 2 - t)
    if shadow:
        s = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(s).text((org[0] + off, org[1] + off), txt, font=f, anchor='ls', fill=INK + (190,), stroke_width=sw, stroke_fill=INK + (190,))
        im = Image.alpha_composite(im, s.filter(ImageFilter.GaussianBlur(max(1, off * 0.6)))); d = ImageDraw.Draw(im)
    if len(segs) == 1 or tuple(fill) == tuple(plain):
        d.text(org, txt, font=f, anchor='ls', fill=tuple(fill) + (255,), stroke_width=sw, stroke_fill=INK + (255,))
    else:                                                       # strokes of every piece first, then the fills on top
        xs = [org[0] + f.getlength(''.join(s_ for s_, _ in segs[:k])) for k in range(len(segs))]
        for x, (s_, _) in zip(xs, segs): d.text((x, org[1]), s_, font=f, anchor='ls', fill=INK + (255,), stroke_width=sw, stroke_fill=INK + (255,))
        for x, (s_, c_) in zip(xs, segs): d.text((x, org[1]), s_, font=f, anchor='ls', fill=tuple(c_) + (255,))
    return im, org[1], sw


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
            imgs = []; ink = []; sw = 2
            for w in self.words:
                e = norm(w) in emph; im, base, sw = word_img(w, size * (1.18 if e else 1.0), pal['accent'] if e else (255, 255, 255)); imgs.append((im, base, e))
                bb = im.getchannel('A').point(lambda v: 255 if v > 40 else 0).getbbox() or (0, 0, im.width, im.height); ink.append((bb[0], bb[2]))
            # fixed word spacing, centred lines, no justification: about 0.3 em between the white letters of two words
            # (the dark strokes are measured, so the gap between the strokes is 0.3 em less both strokes, at least 0.14 em)
            space = max(size * 0.30 - 2 * sw, size * 0.14); widths = [x1 - x0 for x0, x1 in ink]
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
                    im, b_, e = imgs[i]; self.place[i] = (im, round(x - ink[i][0]), round(base - b_)); x += widths[i] + space
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
    """the title sticker; the subtitle is 0.62 of the title size (about 17 px on a 1280 px frame, readable on a phone)."""
    u = H * 0.05; f1 = font('anton', u); f2 = font('archivo', u * 0.62); sw = max(3, round(u * 0.08))
    w1 = f1.getlength(title); w2 = f2.getlength(subtitle) if subtitle else 0
    pw, ph = round(max(w1, w2) + u * 0.9), round(u * (1.42 + (0.66 if subtitle else 0)))
    bd = max(4, round(u * 0.12)); sh = max(4, round(u * 0.12))
    im = Image.new('RGBA', (pw + 2 * bd + sh + 4, ph + 2 * bd + sh + 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    R = round(u * 0.28)
    d.rounded_rectangle((2 + sh, 2 + sh, 2 + pw + 2 * bd + sh, 2 + ph + 2 * bd + sh), radius=R, fill=INK + (255,))
    d.rounded_rectangle((2, 2, 2 + pw + 2 * bd, 2 + ph + 2 * bd), radius=R, fill=(255, 255, 255, 255), outline=INK + (255,), width=max(2, bd // 3))
    d.rounded_rectangle((2 + bd, 2 + bd, 2 + pw + bd, 2 + ph + bd), radius=round(R * 0.7), fill=tuple(pal['sticker']) + (255,))
    cx = 2 + bd + pw / 2
    d.text((cx, 2 + bd + u * 0.74), title, font=f1, anchor='mm', fill=tuple(pal['title']) + (255,), stroke_width=sw, stroke_fill=INK + (255,))
    if subtitle: d.text((cx, 2 + bd + u * 1.60), subtitle, font=f2, anchor='mm', fill=(255, 255, 255, 255), stroke_width=max(1, sw // 2), stroke_fill=INK + (255,))
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
def load_spec(a):
    spec = json.load(open(a.spec)); base = os.path.dirname(os.path.abspath(a.spec))
    return spec, (lambda p: p if os.path.isabs(p) else os.path.join(base, p))


def make_sound(spec, P, fps):
    """the line wavs on the timeline, sting, bed and whoosh, mastered; returns (voices, starts, T, N, mastered wav, gap)."""
    lines = spec['lines']
    if not lines: die('spec has no lines', 2)
    # format rules (warnings: the sample can still be looked at)
    if norm(lines[0]['text']) != norm('Teka, patalastas muna!') or lines[0]['speaker'] != 'USMAN': print('WARNING: line 1 should be USMAN: "Teka, patalastas muna!"')
    if norm(lines[-1]['text']) != norm('Balik sa kuwento, par!') or lines[-1]['speaker'] != 'INDIO': print('WARNING: the last line should be INDIO: "Balik sa kuwento, par!"')
    mid_words = sum(len(l['text'].split()) for l in lines[1:-1])
    if mid_words > 40 or not 2 <= len(lines) - 2 <= 4: print(f'WARNING: the middle should be 2 to 4 lines and at most 40 words (now {len(lines) - 2} lines, {mid_words} words)')
    if not spec.get('source'): print('WARNING: no "source" line: every fact needs its sources on screen')
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
    return voices, starts, T, N, wav, gap


def render(a):
    spec, P = load_spec(a); lay = spec.get('layout', 'bold')
    if lay not in ('bold', 'classic'): die(f'unknown "layout": {lay!r} (bold or classic)', 2)
    print(f'layout: {lay}', flush=True)
    (render_classic if lay == 'classic' else render_bold)(a, spec, P)


def render_classic(a, spec, P):
    """the version-1 frame ("layout": "classic"): BOXES and the animation limits above."""
    W, H = (int(v) for v in a.size.lower().split('x')); fps = a.fps
    pal = PALETTES[spec.get('palette', 'sun')]; lines = spec['lines']
    voices, starts, T, N, wav, gap = make_sound(spec, P, fps)

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
        im = Image.open(P(s['image'])).convert('RGBA'); im = im.crop(im.getchannel('A').getbbox()); box = BX['subject']; bob = BOB * H
        k = fit_scale(im.width, im.height, (box[0], box[1] + bob, box[2], box[3] - bob), POP, WOB); im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2; rw, rh = rot_size(im.width, im.height, WOB)
        sub = dict(im=im, cx=cx, cy=cy, t0=starts[min(int(s.get('from_line', 1)), len(starts) - 1)], rib=None)
        ext['subject'] = union(ext.get('subject'), (cx - rw * POP / 2, cy - rh * POP / 2 - bob, cx + rw * POP / 2, cy + rh * POP / 2 + bob))
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
    if src:                                     # light text, dark outline, ~20 px; two centred lines if one would pass x = 87.5 %
        maxw = min(sb[2] - sb[0], 2 * (SRC_X1 * W - W / 2)); words = src.split()
        for size in range(round(H * 20 / 1280), 11, -1):
            f = font('archivo', size); sw = max(2, round(size * 0.1)); lh = size * 1.12
            opts = [[src]] + [[' '.join(words[:k]), ' '.join(words[k:])] for k in range(1, len(words))]
            fit = [o for o in opts if max(f.getlength(x) for x in o) + 2 * sw <= maxw and len(o) * lh + 2 * sw <= sb[3] - sb[1]]
            if fit:                             # one line if it fits, else the most even split (a break after ';' or ':' wins ties)
                ln = fit[0] if len(fit[0]) == 1 else min(fit, key=lambda o: (max(f.getlength(x) for x in o) - (0.15 * maxw if o[0][-1] in ';:' else 0)))
                break
        else: die(f'LAYOUT: the source line does not fit two lines even at 12 px: shorten it ("{src}")')
        srcim = Image.new('RGBA', (round(max(f.getlength(x) for x in ln) + 2 * sw + 4), round(len(ln) * lh + 2 * sw + 4)), (0, 0, 0, 0)); d_ = ImageDraw.Draw(srcim)
        for j, x in enumerate(ln):
            d_.text((srcim.width / 2, 2 + sw + lh * (j + 0.5)), x, font=f, anchor='mm', fill=(255, 255, 255, 255), stroke_width=sw, stroke_fill=INK + (255,))
        srcim = srcim.crop(srcim.getchannel('A').getbbox())
        sx, sy = (sb[0] + sb[2]) / 2 - srcim.width / 2, (sb[1] + sb[3]) / 2 - srcim.height / 2
        ext['source'] = (sx, sy, sx + srcim.width, sy + srcim.height)
        print(f'source line: {size} px, {len(ln)} line(s), x {sx:.0f}-{sx + srcim.width:.0f}, y {sy:.0f}-{sy + srcim.height:.0f}', flush=True)
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
        d.text((bx1 - hb * 0.7, (by0 + by1) / 2), f'{max(0, math.floor(T - t + 1e-6))}s', font=fbar, anchor='rm', fill=(255, 255, 255), stroke_width=2, stroke_fill=INK)
        # subject cut-out and its ribbon
        cur = [s_ for s_ in subs if s_['t0'] <= t]
        if cur:
            s_ = cur[-1]; q = t - s_['t0']; p = q / 0.45
            sc = ease_out_back(p, 2.0) if p < 1 else 1.0 + 0.012 * math.sin(q * 2.2)
            rot = WOB * math.exp(-q * 4.5) * math.sin(q * 16) + 1.2 * math.sin(q * 1.4)
            if sc > 0.02:
                by = BOB * H * math.sin(2 * math.pi * max(0.0, q - 0.45) / BOBT)          # gentle idle bob once it has popped in
                sc = min(sc, POP); r = paste(fr, s_['im'], s_['cx'], s_['cy'] + by, sc, rot); note(track, 'subject', s_['im'], r, sc, rot, t)
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


# ---------------------------------------------------------------------------------------------------------- render: bold
# The default frame since version 2 ("layout": "bold"): stars 1.5x bigger standing on a stage floor, the subject about
# 1.5x with its label and sources as a card beside it, captions in short pages on a speech plate whose tail points at
# the speaker, a cold open (the title slams in big, then flies to its slot as the subject pops), hops, sway, a laughing
# listener on the joke line, a countdown that heats up, and a whip-pan exit. "layout": "classic" keeps version 1.
BOLD = {
    'title':     (0.06, 0.092, 0.86, 0.146),
    'bar':       (0.07, 0.150, 0.85, 0.172),
    'subject':   (0.03, 0.178, 0.60, 0.403),
    'label':     (0.615, 0.200, 0.875, 0.252),
    'source':    (0.615, 0.262, 0.875, 0.395),
    'captions':  (0.03, 0.408, 0.875, 0.512),
    'INDIO':     (0.02, 0.515, 0.44, 0.875),
    'USMAN':     (0.46, 0.515, 0.88, 0.875),
    'title_big': (0.03, 0.182, 0.86, 0.400),   # the cold-open title, before the subject and its card are there
}
FEET = 0.875      # the chibis only: their feet may stand in the bottom app margin (down to here) ...
FACE = 0.55       # ... but the top 55 % of their drawn extent (the face zone) must stay above SAFE[3]
FLOOR = 0.846     # stage floor (background) from here down
B_GROW, B_SHRINK, B_BREATH, B_STRETCH, B_SQX = 1.05, 0.94, 0.025, 0.03, 1.06   # speaking / listening size, idle, loudness, max x squash
B_HOP, B_BOUNCE, B_TILT = 0.030, 0.025, 3.0       # max lift (fraction of H), loudness lift (fraction of sprite h), sway deg
B_POP, B_WOB, B_BOB = 1.06, 2.0, 3 / 1280          # subject pop and pulse cap, wobble deg, idle bob
B_WPOP, B_EPOP, B_EMPH = 1.08, 1.14, 1.0           # word pop, emphasis-word pop, emphasis-word size
PAGE_WORDS, PAGE_CHARS, PAGE_MIN = 3, 14, 0.35     # caption pages: at most 3 words / 14 letters, at least 0.35 s each
SLAM, SLAM_T, FLY_T, WHIP = 1.3, 0.22, 0.30, 7     # cold-open slam overshoot and time, fly to the header, whip-pan frames
CHIBI = ('INDIO', 'USMAN')


def pivot_ext(w, h, deg):
    """bbox (dx0, dy0, dx1, dy1) of a w x h sprite standing on its bottom centre, rotated by anything up to +-deg about it."""
    xs, ys = [], []
    for a_ in (-deg, 0.0, deg):
        c, s = math.cos(math.radians(a_)), math.sin(math.radians(a_))
        for x, y in ((-w / 2, 0), (w / 2, 0), (-w / 2, -h), (w / 2, -h)): xs.append(x * c + y * s); ys.append(-x * s + y * c)
    return min(xs), min(ys), max(xs), max(ys)


def draw_pivot(fr, im, cx, by, deg):
    """paste im with its bottom centre at (cx, by), rotated deg about that point; returns the visible drawn rect."""
    if abs(deg) < 0.05:
        x, y = round(cx - im.width / 2), round(by - im.height); fr.paste(im, (x, y), im); return opaque_rect(im, (x, y))
    C = math.ceil(math.hypot(im.width / 2, im.height)) + 2
    cv = Image.new('RGBA', (2 * C, 2 * C), (0, 0, 0, 0)); cv.paste(im, (round(C - im.width / 2), C - im.height))
    cv = cv.rotate(deg, resample=Image.BICUBIC, center=(C, C)); bb = cv.getbbox()
    if not bb: return None
    cv = cv.crop(bb); x, y = round(cx - C) + bb[0], round(by - C) + bb[1]; fr.paste(cv, (x, y), cv)
    return opaque_rect(cv, (x, y))


def paginate(words):
    """1 to 3 words / at most 14 letters a page; a page ends after punctuation; quoted and hyphenated words stay whole."""
    pages, cur, n = [], [], 0
    for i, w in enumerate(words):
        L = len(norm(w))
        if cur and (len(cur) >= PAGE_WORDS or n + L > PAGE_CHARS): pages.append(cur); cur, n = [], 0
        cur.append(i); n += L
        if re.search(r'[,.!?;:]\W*$', w): pages.append(cur); cur, n = [], 0
    if cur: pages.append(cur)
    return pages


class Pages:
    """one spoken line as caption pages on a white speech plate (dark words, emphasis in the accent colour, the word
    being spoken on a yellow pill). Every page of the break uses one font size (the biggest that fits them all)."""
    PAD, SHADOW, PLATE_POP, MIN_W = 9, 6, 1.05, 240
    GREY = (205, 202, 210)                                     # words still to come, emphasis or not

    def __init__(self, text, emphasis, pal, H):
        self.words = text.upper().split(); em = {norm(e) for x in emphasis for e in x.split()}
        self.emph = [norm(w) in em for w in self.words]; self.pal = pal; self.pages = paginate(self.words)

    def layout(self, size, area):
        """place every page centred in area (x0, y0, x1, y1); None if one does not fit."""
        out = []
        for pg in self.pages:
            imgs = []
            for i in pg:
                e = self.emph[i]
                im, base, sw = word_img(self.words[i], size * (B_EMPH if e else 1.0), self.pal['accent'] if e else INK, stroke_k=0,
                                        shadow=False, plain=INK)
                # on the pill: emphasis words in the accent colour on an ink pill (quotes in white), others as drawn
                act = word_img(self.words[i], size * (B_EMPH if e else 1.0), self.pal['accent'], stroke_k=0, shadow=False,
                               plain=(255, 255, 255))[0] if e else im
                grey = Image.new('RGBA', im.size, self.GREY + (255,)); grey.putalpha(im.getchannel('A'))
                bb = im.getchannel('A').point(lambda v: 255 if v > 40 else 0).getbbox() or (0, 0, im.width, im.height); imgs.append((im, base, bb, e, act, grey))
            space = size * 0.24; widths = [x_[2][2] - x_[2][0] for x_ in imgs]
            opts = [[list(range(len(imgs)))]] + [[list(range(k)), list(range(k, len(imgs)))] for k in range(1, len(imgs))]
            done = None
            for rows in opts:
                lw = [sum(widths[j] for j in r) + space * (len(r) - 1) for r in rows]
                asc = [max(imgs[j][1] - imgs[j][2][1] for j in r) for r in rows]; desc = [max(imgs[j][2][3] - imgs[j][1] for j in r) for r in rows]
                gap = size * 0.10; tot = sum(asc) + sum(desc) + gap * (len(rows) - 1)
                cx, y = (area[0] + area[2]) / 2, (area[1] + area[3]) / 2 - tot / 2; place = [None] * len(imgs); pr = None
                for r, w_, a_, d_ in zip(rows, lw, asc, desc):
                    x = cx - w_ / 2; base = y + a_
                    for j in r:
                        im, b_, bb, e, act, grey = imgs[j]; px_, py_ = round(x - bb[0]), round(base - b_)
                        ink = (px_ + bb[0], py_ + bb[1], px_ + bb[2], py_ + bb[3]); k = B_EPOP if e else B_WPOP
                        icx, icy = (ink[0] + ink[2]) / 2, (ink[1] + ink[3]) / 2
                        pr = union(pr, (icx - (ink[2] - ink[0]) * k / 2, icy - (ink[3] - ink[1]) * k / 2, icx + (ink[2] - ink[0]) * k / 2, icy + (ink[3] - ink[1]) * k / 2))
                        place[j] = (im, px_, py_, e, ink, act, grey); x += widths[j] + space
                    y = base + d_ + gap
                plate = [pr[0] - self.PAD, pr[1] - self.PAD, pr[2] + self.PAD, pr[3] + self.PAD]
                if plate[2] - plate[0] < self.MIN_W:                    # a short page keeps a plate wide enough for a short tail
                    m_ = (plate[0] + plate[2]) / 2; plate[0], plate[2] = m_ - self.MIN_W / 2, m_ + self.MIN_W / 2
                plate = tuple(plate)
                pcx, pcy = (plate[0] + plate[2]) / 2, (plate[1] + plate[3]) / 2; pw, ph = (plate[2] - plate[0]) * self.PLATE_POP / 2, (plate[3] - plate[1]) * self.PLATE_POP / 2
                big = (pcx - pw, pcy - ph, pcx + pw + self.SHADOW, pcy + ph + self.SHADOW)
                if big[0] >= area[0] and big[1] >= area[1] and big[2] <= area[2] and big[3] <= area[3]: done = (place, plate, big); break
            if done is None: return None
            out.append(done)
        return out

    def times(self, start, s0, s1, end):
        syl = np.array([syllables(w) for w in self.words], float); c = np.concatenate([[0], np.cumsum(syl)[:-1]]) / syl.sum()
        t = start + s0 + c * (s1 - s0) * 0.94; t[0] = start
        self.pt = []
        for k, pg in enumerate(self.pages):                    # each page on screen at least PAGE_MIN
            p0 = t[pg[0]] if k else start
            if k and p0 < self.pt[-1] + PAGE_MIN: p0 = min(self.pt[-1] + PAGE_MIN, end - 0.15)
            for i in pg: t[i] = max(t[i], p0)
            self.pt.append(p0)
        self.t = t


def pop_curve(p, peak):
    """0.6 -> peak -> 1.0 with an alpha ramp; p in 0..1 over the pop."""
    if p >= 1: return 1.0, 1.0
    p = max(p, 0.0); s = 0.6 + (peak - 0.6) * (p / 0.6) if p < 0.6 else peak - (peak - 1) * ((p - 0.6) / 0.4)
    return s, min(1.0, p / 0.4 + 0.15)


def wrap_source(src, f, maxw, maxlines):
    """break after ':' and ';' first, then greedy word wrap; None if more than maxlines are needed."""
    out = []
    for part in re.split(r'(?<=[:;])\s+', src):
        cur = ''
        for w in part.split():
            if cur and f.getlength(cur + ' ' + w) > maxw: out.append(cur); cur = w
            else: cur = (cur + ' ' + w).strip()
        if cur: out.append(cur)
    return out if len(out) <= maxlines and max(f.getlength(x) for x in out) <= maxw else None


def check_layout_bold(ext, win, allow, W, H):
    """every element inside the safe area (the chibis' feet may go down to FEET, their face zone may not leave it);
    no two elements that are on screen at the same time may meet, except the allowed pairs (drawn under, by design)."""
    sa = (SAFE[0] * W, SAFE[1] * H, SAFE[2] * W, SAFE[3] * H); errs = []
    for k, r in ext.items():
        bot = FEET * H if k in CHIBI else sa[3]
        if r[0] < sa[0] - 0.5 or r[1] < sa[1] - 0.5 or r[2] > sa[2] + 0.5 or r[3] > bot + 0.5:
            errs.append(f'{k} leaves the phone safe area: {tuple(round(v) for v in r)} vs {tuple(round(v) for v in (sa[0], sa[1], sa[2], bot))}')
        if k in CHIBI and r[1] + FACE * (r[3] - r[1]) > sa[3] + 0.5:
            errs.append(f'{k}: the face zone reaches y {r[1] + FACE * (r[3] - r[1]):.0f}, below the safe area ({sa[3]:.0f})')
    ks = list(ext)
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            a_, b_ = ks[i], ks[j]; wa, wb = win[a_], win[b_]
            if not (wa[0] < wb[1] and wb[0] < wa[1]) or frozenset((a_, b_)) in allow: continue
            o = inter(ext[a_], ext[b_])
            if o: errs.append(f'{a_} would cover {b_} ({o[0]:.0f} x {o[1]:.0f} px, both on screen {max(wa[0], wb[0]):.2f}-{min(wa[1], wb[1]):.2f} s)')
    for e in errs: print('OVERLAP:', e, file=sys.stderr)
    if errs: die(f'LAYOUT CHECK FAILED ({len(errs)}): nothing may cover a face or the subject; shorten text or change BOLD')
    print('layout check: ' + ', '.join(f'{k} {tuple(round(v / (W if n % 2 == 0 else H), 3) for n, v in enumerate(r))} [{win[k][0]:.2f}-{win[k][1]:.2f} s]'
                                       for k, r in ext.items()), flush=True)


def render_bold(a, spec, P):
    W, H = (int(v) for v in a.size.lower().split('x')); fps = a.fps
    pal = PALETTES[spec.get('palette', 'sun')]; lines = spec['lines']
    voices, starts, T, N, wav, gap = make_sound(spec, P, fps)
    BX = {k: px(v, W, H) for k, v in BOLD.items()}; ext, win = {}, {}; allow = set()
    ends = [s + len(v) / SR for s, v in zip(starts, voices)]

    # ---- captions: pages, one font size for the whole break, word times
    tail = round(H * 0.016); cb = BX['captions']; area = (cb[0], cb[1], cb[2], cb[3] - tail)
    caps = [Pages(l['text'], l.get('emphasis', []), pal, H) for l in lines]
    for size in range(round(H * 0.058), round(H * 0.024) - 1, -1):
        lay = [c.layout(size, area) for c in caps]
        if all(lay): break
    else: die('LAYOUT: a caption page does not fit the caption box even at the smallest size: shorten the words')
    print(f'captions: {size} px ({size / H:.3f} H), pages: ' + ' | '.join(' / '.join(' '.join(c.words[i] for i in pg) for pg in c.pages) for c in caps), flush=True)
    for li, (c, l_) in enumerate(zip(caps, lay)):
        c.lay = l_; env = envelope(voices[li], fps, int(len(voices[li]) / SR * fps) + 2)
        on = np.nonzero(env > 0.15)[0]; s0, s1 = (on[0] / fps, (on[-1] + 1) / fps) if len(on) else (0, len(voices[li]) / SR)
        c.times(starts[li], s0, s1, ends[li]); c.env = env; c.start = starts[li]; c.end = ends[li]
        for place, plate, big in l_:
            ext['captions'] = union(ext.get('captions'), big)
            for im, x_, y_, e_, ink, *_ in place:                          # the popped word must stay on its plate
                k_ = B_EPOP if e_ else B_WPOP; cx_, cy_, hw_, hh_ = (ink[0] + ink[2]) / 2, (ink[1] + ink[3]) / 2, (ink[2] - ink[0]) * k_ / 2 + 6 * k_, (ink[3] - ink[1]) * k_ / 2 + 5 * k_
                if cx_ - hw_ < plate[0] or cy_ - hh_ < plate[1] or cx_ + hw_ > plate[2] or cy_ + hh_ > plate[3]:
                    die(f'LAYOUT: a popped caption word or its pill in line {li + 1} leaves its plate')
    ext['captions'] = union(ext['captions'], (cb[0], cb[3] - tail - 2, cb[2], cb[3])); win['captions'] = (starts[0], T)   # the tail's row

    # ---- chibis: as big as the box allows with every hop, squash, sway and the loudness lift inside it
    sprites = {}; hop_px = B_HOP * H
    first = lines[0]['speaker']
    for name in CHIBI:
        p = spec.get('sprites', {}).get(name)
        if not p or not os.path.exists(P(p)): print(f'note: no sprite for {name}: skipped'); continue
        im = Image.open(P(p)).convert('RGBA'); im = im.crop(im.getchannel('A').getbbox()); box = BX[name]
        GW, GH = B_GROW * B_SQX, B_GROW * (1 + B_BREATH + B_STRETCH)
        e1 = pivot_ext(im.width * GW, im.height * GH, B_TILT)
        k = min((box[2] - box[0]) / (e1[2] - e1[0]), (box[3] - box[1] - hop_px) / (e1[3] - e1[1]))
        im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
        dim = Image.eval(im.convert('RGB'), lambda v: int(v * 0.85)).convert('RGBA'); dim.putalpha(im.getchannel('A'))
        e = pivot_ext(im.width * GW, im.height * GH, B_TILT); cx = (box[0] + box[2]) / 2; bot = box[3] - e[3]
        ext[name] = (cx + e[0], bot + e[1] - hop_px, cx + e[2], bot + e[3])
        rise = name == first
        sprites[name] = dict(im=im, dim=dim, cx=cx, bot=bot, ph=0.0 if name == 'INDIO' else 1.7, side=-1 if name == 'INDIO' else 1,
                             rise=rise, enter=0.0 if rise else 0.25, dur=0.30 if rise else 0.42, hops=[], nods=[], laugh=None)
        win[name] = (sprites[name]['enter'] + sprites[name]['dur'] + 0.1, T)
        print(f'{name}: sprite {im.width} x {im.height} px ({im.height / H:.3f} H), feet at {bot / H:.3f} H', flush=True)
    for li, (c, l) in enumerate(zip(caps, lines)):                         # hop at each line start; nods; the joke; the exit jump
        if l['speaker'] in sprites: sprites[l['speaker']]['hops'].append((c.start, hop_px))
        for k2, sp in sprites.items():
            if k2 == l['speaker']: continue
            for i, e_ in enumerate(c.emph):
                if e_: sp['nods'].append(c.t[i])
    joke = int(spec.get('joke_line', len(lines) - 2))
    if 1 <= joke < len(lines) - 1:
        c = caps[joke]; te = [c.t[i] for i, e_ in enumerate(c.emph) if e_]; tl = te[-1] if te else (c.start + c.end) / 2
        for k2, sp in sprites.items():
            if k2 != lines[joke]['speaker']: sp['laugh'] = tl; sp['nods'] = [n_ for n_ in sp['nods'] if not tl - 0.1 <= n_ <= tl + 1.0]
    cl = caps[-1]; te = [cl.t[i] for i, e_ in enumerate(cl.emph) if e_]
    if te:
        for sp in sprites.values(): sp['hops'].append((te[0], hop_px))
    for sp in sprites.values(): sp['hops'].sort()

    # ---- subject, label, source card
    subs = []; t_s = None
    for s in spec.get('subjects', []):
        im = Image.open(P(s['image'])).convert('RGBA'); im = im.crop(im.getchannel('A').getbbox()); box = BX['subject']; bob = B_BOB * H
        k = fit_scale(im.width, im.height, (box[0], box[1] + bob, box[2], box[3] - bob), B_POP, B_WOB); im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2; rw, rh = rot_size(im.width, im.height, B_WOB)
        t0 = starts[min(int(s.get('from_line', 1)), len(starts) - 1)]; t_s = t0 if t_s is None else min(t_s, t0)
        pulse_on = {norm(w) for w in s.get('pulse', [])} or {norm(s.get('label', '')) or '\0'}
        pulses = [c.t[i] for c in caps for i, w in enumerate(c.words) if c.emph[i] and c.t[i] > t0 and any(pw in norm(w) for pw in pulse_on)]
        sub = dict(im=im, cx=cx, cy=cy, t0=t0, rib=None, pulses=pulses)
        ext['subject'] = union(ext.get('subject'), (cx - rw * B_POP / 2, cy - rh * B_POP / 2 - bob, cx + rw * B_POP / 2, cy + rh * B_POP / 2 + bob))
        print(f'subject: {im.width} x {im.height} px, pulses at ' + ', '.join(f'{x:.2f}' for x in pulses), flush=True)
        if s.get('label'):
            rb = ribbon(s['label'].upper(), pal, H, (255, 255, 255)); lb = BX['label']; k = min(1.0, fit_scale(rb.width, rb.height, lb, POP))
            if k < 1: rb = rb.resize((round(rb.width * k), round(rb.height * k)), Image.LANCZOS)
            sub['rib'] = (rb, (lb[0] + lb[2]) / 2, (lb[1] + lb[3]) / 2)
            ext['label'] = union(ext.get('label'), (sub['rib'][1] - rb.width * POP / 2, sub['rib'][2] - rb.height * POP / 2, sub['rib'][1] + rb.width * POP / 2, sub['rib'][2] + rb.height * POP / 2))
        subs.append(sub)
    subs.sort(key=lambda s: s['t0'])
    if t_s is None: t_s = starts[min(1, len(starts) - 1)]
    if subs: win['subject'] = (t_s, T)
    if 'label' in ext: win['label'] = (t_s, T)
    src = spec.get('source', ''); sb = BX['source']; card = None
    if src:                                     # white words on a dark rounded card, up to 4 lines, 18 px down to 13 px
        for fs in range(round(H * 18 / 1280), 12, -1):
            f = font('archivo', fs); ln = wrap_source(src, f, sb[2] - sb[0] - 20, 4); lh = fs * 1.22
            if ln and len(ln) * lh + 16 <= sb[3] - sb[1]: break
        else: die(f'LAYOUT: the source line does not fit its card even at 13 px: shorten it ("{src}")')
        cw = round(max(f.getlength(x) for x in ln) + 20); ch = round(len(ln) * lh + 14)
        card = Image.new('RGBA', (cw, ch), (0, 0, 0, 0)); d_ = ImageDraw.Draw(card)
        d_.rounded_rectangle((0, 0, cw - 1, ch - 1), radius=10, fill=INK + (200,), outline=(255, 255, 255, 230), width=2)
        for j, x in enumerate(ln): d_.text((cw / 2, 7 + lh * (j + 0.5)), x, font=f, anchor='mm', fill=(255, 255, 255, 255))
        sx, sy = (sb[0] + sb[2]) / 2 - cw / 2, sb[1]; card = (card, round(sx), round(sy))
        ext['source'] = (sx, sy, sx + cw, sy + ch); win['source'] = (t_s, T)
        print(f'source card: {fs} px, {len(ln)} line(s): ' + ' / '.join(ln), flush=True)

    # ---- title: slam in big (cold open), fly to the header slot as the subject pops, then stay
    ts = title_sticker(spec.get('title', 'PATALASTAS NI USMAN').upper(), spec.get('subtitle', ''), pal, H)
    tb, gb = BX['title'], BX['title_big']
    s_h = fit_scale(ts.width, ts.height, tb, B_POP, abs(TILT)); s_b = fit_scale(ts.width, ts.height, gb, SLAM, 14)
    hc, gc = ((tb[0] + tb[2]) / 2, (tb[1] + tb[3]) / 2), ((gb[0] + gb[2]) / 2, (gb[1] + gb[3]) / 2)
    fly0 = max(SLAM_T + 0.2, t_s - FLY_T); fly1 = fly0 + FLY_T

    def title_at(t):
        if t < SLAM_T:
            p = t / SLAM_T; return gc[0], gc[1], s_b * (1 + (SLAM - 1) * (1 - ease_out(p))), -14 + 11 * ease_out(p), min(1.0, 0.4 + p * 1.5), 'title (cold open)'
        if t < fly0: return gc[0], gc[1], s_b * (1 + 0.025 * math.sin(2 * math.pi * (t - SLAM_T) / 0.8)), TILT, 1.0, 'title (cold open)'
        if t < fly1:
            p = ease_out((t - fly0) / FLY_T); return gc[0] + (hc[0] - gc[0]) * p, gc[1] + (hc[1] - gc[1]) * p, s_b + (s_h - s_b) * p, TILT, 1.0, 'title (fly)'
        q = t - fly1; return hc[0], hc[1], s_h * (1 + (B_POP - 1) * math.exp(-q * 7) * math.sin(q * 22)), TILT, 1.0, 'title'
    for fi in range(N):
        x, y, s, r, _, k = title_at(fi / fps); rw, rh = rot_size(ts.width * s, ts.height * s, r)
        ext[k] = union(ext.get(k), (x - rw / 2 - 1, y - rh / 2 - 1, x + rw / 2 + 1, y + rh / 2 + 1))
    win['title (cold open)'], win['title (fly)'], win['title'] = (0, fly0), (fly0, fly1), (fly1, T)
    allow.add(frozenset(('title (fly)', 'bar')))                       # the flying sticker passes under the countdown bar
    ext['bar'] = BX['bar']; win['bar'] = (0, T)
    print(f'title: header {s_h:.3f}, cold open {s_b:.3f} ({s_b / s_h:.2f}x), flies {fly0:.2f}-{fly1:.2f} s; subject at {t_s:.2f} s', flush=True)
    check_layout_bold(ext, win, allow, W, H)

    # ---- per-frame state of the two chibis: who speaks, how loud
    act = {k: np.zeros(N, np.float32) for k in sprites}; loud = {k: np.zeros(N, np.float32) for k in sprites}
    for c, l in zip(caps, lines):
        f0, f1 = int(round(c.start * fps)), int(round(c.end * fps))
        for k in sprites:
            act[k][f0:min(N, f1 + int(gap * fps) + 1)] = 1.0 if l['speaker'] == k else -1.0
            if l['speaker'] == k: e = c.env[:max(0, min(N, f1) - f0)]; loud[k][f0:f0 + len(e)] = e
    for k in sprites:
        v = 0.0; a_ = act[k]
        for i in range(N): v += (a_[i] - v) * 0.25; a_[i] = v

    # ---- background: sunburst from the subject, halftone, and a stage floor
    ang, BG_A, BG_B = background(W, H, pal, ((BX['subject'][0] + BX['subject'][2]) / 2, (BX['subject'][1] + BX['subject'][3]) / 2))
    fy = round(FLOOR * H); yy, xx = np.mgrid[fy:H, 0:W].astype(np.float32); cell = max(8, round(W / 30))
    dots = (np.hypot((xx % cell) - cell / 2, (yy % cell) - cell / 2) < cell * (0.16 + 0.30 * (yy - fy) / (H - fy))).astype(np.float32)[..., None]
    floor = np.clip(np.array(pal['b'], np.float32) * 0.80 * (1 - dots) + np.array(pal['dot'], np.float32) * 0.70 * dots, 0, 255).astype(np.uint8)
    BG_A[fy:], BG_B[fy:] = floor, floor; BG_A[fy - 1:fy + 2] = BG_B[fy - 1:fy + 2] = INK
    shadows = {}
    for k, sp in sprites.items():
        sw_, sh_ = round(sp['im'].width * 0.85), round(H * 0.035); m = Image.new('L', (sw_ + 40, sh_ + 40), 0)
        ImageDraw.Draw(m).ellipse((20, 20, 20 + sw_, 20 + sh_), fill=90); m = m.filter(ImageFilter.GaussianBlur(6))
        shadows[k] = Image.merge('RGBA', [Image.new('L', m.size, c_) for c_ in INK] + [m])
    emph_t = [c.t[i] for c in caps for i, e_ in enumerate(c.emph) if e_]
    bursts = [(SLAM_T, gc[0], gc[1], ts.width * s_b / 2, 12), (fly1, hc[0], hc[1], ts.width * s_h / 2, 9)]
    bursts += [(s['t0'], s['cx'], s['cy'], max(s['im'].size) / 2, 12) for s in subs] + [(tp, s['cx'], s['cy'], max(s['im'].size) / 2, 8) for s in subs for tp in s['pulses']]
    rng = np.random.default_rng(11); star_seed = [rng.random((14, 3)) for _ in bursts]
    stills = [float(x) for x in a.stills.split(',')] if a.stills else []
    track = {}; thumbs = []; spin = 0.0; prev_tip = None; spill = []
    LR = tuple(round(v) for v in (ext['captions'][0] - 4, ext['captions'][1] - 4, ext['captions'][2] + 4, ext['captions'][3] + 4))   # caption layer
    keep_out = [(r[0] - 8, r[1] - 8, r[2] + 8, r[3] + 8) for k_ in ('label', 'source') if k_ in ext for r in (ext[k_],)]   # no sparkles there
    hb = BX['bar'][3] - BX['bar'][1]; fbar = font('archivo', hb * 0.60); fnum = {}
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-', '-i', wav,
                           '-map', '0:v', '-map', '1:a', '-t', f'{T:.4f}', '-c:v', 'libx264', '-profile:v', 'high', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
                           '-c:a', 'aac', '-b:a', '192k', '-ar', str(SR), '-ac', '2', '-movflags', '+faststart', a.out], stdin=subprocess.PIPE)
    for fi in range(N):
        t = fi / fps
        spin += (0.10 + sum(0.9 * (1 - (t - x) / 0.6) for x in emph_t if 0 <= t - x < 0.6)) / fps     # the rays kick on each emphasis word
        stripe = (((ang + spin) * (16 / (2 * np.pi))) % 1.0) < 0.5
        bg_now = np.where(stripe[..., None], BG_A, BG_B); fr = Image.fromarray(bg_now); d = ImageDraw.Draw(fr)
        if t < 0.6:                                                       # cold open: a ray burst behind the title
            ov = Image.new('RGBA', fr.size, (0, 0, 0, 0)); do = ImageDraw.Draw(ov); R = H * 0.30 * ease_out(t / 0.6); al = round(200 * (1 - t / 0.6))
            for j in range(16):
                a0, a1 = j / 16 * 2 * math.pi + t, (j + 0.5) / 16 * 2 * math.pi + t
                do.polygon([gc, (gc[0] + R * math.cos(a0), gc[1] + R * math.sin(a0)), (gc[0] + R * math.cos(a1), gc[1] + R * math.sin(a1))],
                           fill=((255, 255, 255) if j % 2 else tuple(pal['accent'])) + (al,))
            fr = Image.alpha_composite(fr.convert('RGBA'), ov).convert('RGB'); d = ImageDraw.Draw(fr)
        for (t0, cx, cy, r0, cnt), sd in zip(bursts, star_seed):         # sparkles at each pop, behind everything
            p = (t - t0) / 0.7
            if 0 <= p < 1:
                for j in range(cnt):
                    an = j / cnt * 2 * np.pi + sd[j, 0] * 0.5; dist = r0 * 0.7 + (r0 * 0.6 + H * 0.05) * ease_out(p) * (0.7 + 0.6 * sd[j, 1])
                    rr = H * (0.011 + 0.011 * sd[j, 2]) * (1 - p) ** 0.7; sx_, sy_ = cx + math.cos(an) * dist, cy + math.sin(an) * dist * 0.8
                    if any(inter((sx_ - rr, sy_ - rr, sx_ + rr, sy_ + rr), ko) for ko in keep_out): continue
                    if rr > 1: star(d, cx + math.cos(an) * dist, cy + math.sin(an) * dist * 0.8, rr, p * 3 + j, (255, 255, 255) if j % 2 else tuple(pal['title']))
        # subject, its ribbon and the source card
        cur = [s_ for s_ in subs if s_['t0'] <= t]
        if cur:
            s_ = cur[-1]; q = t - s_['t0']; p = q / 0.45
            sc = ease_out_back(p, 2.0) if p < 1 else 1.0 + 0.012 * math.sin(q * 2.2)
            for tp in s_['pulses']:
                if 0 <= t - tp < 0.3: sc *= 1 + 0.06 * math.sin(math.pi * (t - tp) / 0.3)
            rot = (B_WOB - 0.8) * math.exp(-q * 4.5) * math.sin(q * 16) + 0.8 * math.sin(q * 1.4)
            if sc > 0.02:
                by = B_BOB * H * math.sin(2 * math.pi * max(0.0, q - 0.45) / BOBT)
                sc = min(sc, B_POP); r = paste(fr, s_['im'], s_['cx'], s_['cy'] + by, sc, rot); note(track, 'subject', s_['im'], r, sc, rot, t)
            if s_['rib']:
                p2 = (q - 0.12) / 0.4; sc2 = 0.0 if p2 <= 0 else (min(POP, ease_out_back(p2, 2.0)) if p2 < 1 else 1.0)
                if sc2 > 0.02: rb, rx, ry = s_['rib']; r = paste(fr, rb, rx, ry, sc2); note(track, 'label', rb, r, sc2, 0, t)
        if card and t >= t_s + 0.2:
            al = min(1.0, (t - t_s - 0.2) / 0.25); im_ = card[0] if al >= 1 else Image.fromarray((np.asarray(card[0]) * np.array([1, 1, 1, al])).astype(np.uint8))
            fr.paste(im_, (card[1], card[2]), im_); note(track, 'source', card[0], (card[1], card[2], card[1] + card[0].width, card[2] + card[0].height), 1, 0, t)
        # title (drawn before the bar: on its way up it passes under it)
        x, y, s, r, al, k = title_at(t)
        if s > 0.02: rr = paste(fr, ts, x, y, s, r, al); note(track, k, ts, rr, s, r, t)
        draw_bar(fr, BX['bar'], t, T, fps, pal, fbar, fnum, spec.get('countdown_text', 'babalik ang kuwento').upper())
        # caption plate and words: drawn on one layer, and the page pop scales that whole layer about the tail tip
        li = max([i for i, c in enumerate(caps) if c.start <= t + 1e-6], default=None)
        if li is not None:
            c = caps[li]; pg = max(k_ for k_, p0 in enumerate(c.pt) if p0 <= t + 1e-6); place, plate, _ = c.lay[pg]
            spk = sprites.get(lines[li]['speaker']); tip_x = spk['cx'] if spk else (cb[0] + cb[2]) / 2
            prev_tip = tip_x if prev_tip is None else prev_tip + (tip_x - prev_tip) * 0.45
            q = t - c.pt[pg]; dur_ = 0.15 if pg == 0 else 0.10
            ls = 1.0 if q >= dur_ else (0.55 if pg == 0 else 0.86) + (0.45 if pg == 0 else 0.14) * ease_out(q / dur_)
            lay_ = Image.new('RGBA', (LR[2] - LR[0], LR[3] - LR[1]), (0, 0, 0, 0)); o_ = (LR[0], LR[1])
            loc = lambda r_: (r_[0] - o_[0], r_[1] - o_[1], r_[2] - o_[0], r_[3] - o_[1])
            tip = draw_plate(lay_, loc(plate), prev_tip - o_[0], cb[3] - 1 - o_[1], Pages.SHADOW)
            dl = ImageDraw.Draw(lay_); boxes = []
            cur_w = max([i for i in c.pages[pg] if c.t[i] <= t + 1e-6], default=None)
            for i, (im, x_, y_, e_, ink, act_im, grey) in zip(c.pages[pg], place):
                if t < c.t[i]:                                                  # words still to come: light grey, so the page reads ahead
                    paste(lay_, grey, x_ + im.width / 2 - o_[0], y_ + im.height / 2 - o_[1]); boxes.append(('word', ink, 1.0)); continue
                s, _ = pop_curve((t - c.t[i]) / (0.18 if e_ else 0.14), B_EPOP if e_ else B_WPOP)   # full colour from its first frame
                icx, icy = (ink[0] + ink[2]) / 2 - o_[0], (ink[1] + ink[3]) / 2 - o_[1]
                if i == cur_w:                                                  # the word being spoken sits on a pill (scaled with it)
                    hw_, hh_ = ((ink[2] - ink[0]) / 2 + 6) * s, ((ink[3] - ink[1]) / 2 + 5) * s; pill = (icx - hw_, icy - hh_, icx + hw_, icy + hh_)
                    dl.rounded_rectangle(pill, radius=8, fill=INK if e_ else tuple(pal['title'])); boxes.append(('pill', tuple(v + o for v, o in zip(pill, o_ * 2)), 1.0))
                paste(lay_, act_im if i == cur_w else im, x_ + im.width / 2 - o_[0], y_ + im.height / 2 - o_[1], s)
                boxes.append(('word', ink, s))
            if ls < 1.0:
                ax, ay = tip; lay_ = lay_.resize((max(1, round(lay_.width * ls)), max(1, round(lay_.height * ls))), Image.BICUBIC)
                px0, py0 = round(o_[0] + ax - ax * ls), round(o_[1] + ay - ay * ls)
            else: ax = ay = 0.0; px0, py0 = o_
            fr.paste(lay_, (px0, py0), lay_); d = ImageDraw.Draw(fr)
            X = lambda v: o_[0] + ax + (v - o_[0] - ax) * ls; Y = lambda v: o_[1] + ay + (v - o_[1] - ay) * ls
            pr_ = (X(plate[0]), Y(plate[1]), X(plate[2]), Y(plate[3])); track['captions'] = union(track.get('captions'), (px0, py0, px0 + lay_.width, py0 + lay_.height))
            for kind, r_, s in boxes:                                          # every word and the pill stay on the plate, every frame
                if kind == 'word':
                    cx_, cy_, hw_, hh_ = (r_[0] + r_[2]) / 2, (r_[1] + r_[3]) / 2, (r_[2] - r_[0]) * s / 2, (r_[3] - r_[1]) * s / 2; r_ = (cx_ - hw_, cy_ - hh_, cx_ + hw_, cy_ + hh_)
                rr_ = (X(r_[0]), Y(r_[1]), X(r_[2]), Y(r_[3]))
                if rr_[0] < pr_[0] - 0.5 or rr_[1] < pr_[1] - 0.5 or rr_[2] > pr_[2] + 0.5 or rr_[3] > pr_[3] + 0.5:
                    spill.append(f'frame {fi}: a caption {kind} at {tuple(round(v) for v in rr_)} leaves its plate {tuple(round(v) for v in pr_)}')
        # chibis: contact shadows first, then the sprites
        draws = []
        for k, sp in sprites.items():
            te = (t - sp['enter']) / sp['dur']
            if te <= 0: continue
            a_ = float(act[k][fi]); e = float(loud[k][fi]) * max(0.0, a_)
            size = 1 + (B_GROW - 1) * max(0, a_) - (1 - B_SHRINK) * max(0, -a_)
            br = math.sin(2 * math.pi * t / 1.3 + sp['ph'])
            sy = size * (1 + B_BREATH * br + B_STRETCH * e); sx = size * (1 - B_BREATH * br * 0.5 - 0.03 * e)
            up = 0.0; qx = qy = 1.0
            for h0, amp in sp['hops']:
                q = t - h0
                if -2 / fps <= q < 0: qy *= 0.92; qx *= 1.05
                elif 0 <= q < 0.28: up = max(up, amp * math.sin(math.pi * q / 0.28))
                elif 0.28 <= q < 0.28 + 2 / fps: qy *= 0.94; qx *= 1.04
            for n0 in sp['nods']:
                q = t - n0
                if 0 <= q < 0.25: qy *= 1 - 0.04 * math.sin(math.pi * q / 0.25)
            deg = B_TILT * math.sin(2 * math.pi * t / 0.55) * e * sp['side'] * -1
            bright = a_
            if sp['laugh'] is not None and 0 <= t - sp['laugh'] < 1.0:          # the listener cracks up at the joke
                q = t - sp['laugh']; fade = 1 - q / 1.0
                deg = B_TILT * math.sin(2 * math.pi * 6 * q) * fade; up = max(up, H * 0.014 * abs(math.sin(2 * math.pi * 3 * q)) * fade); bright = 1.0
            up = min(hop_px, up + B_BOUNCE * sp['im'].height * e)
            sx = min(sx * qx, B_GROW * B_SQX); sy = min(sy * qy, B_GROW * (1 + B_BREATH + B_STRETCH))
            dx = dy = 0.0
            if te < 1:
                if sp['rise']: dy = H * 0.35 * (1 - ease_out_back(te, 1.6))
                else: ee = ease_out_back(te, 1.4); dx = sp['side'] * (1 - ee) * (W * 0.62); up += math.sin(math.pi * te) * 0.10 * sp['im'].height
            elif sp['rise'] and te < 1 + 3 / (sp['dur'] * fps): sy *= 0.88; sx *= 1.08    # landing squash after rising in
            src_im = sp['im'] if bright >= 0 else Image.blend(sp['im'], sp['dim'], min(1.0, -bright))
            w_, h_ = max(1, round(sp['im'].width * sx)), max(1, round(sp['im'].height * sy))
            draws.append((k, src_im.resize((w_, h_), Image.BICUBIC), sp['cx'] + dx, sp['bot'] - up + dy, deg, up, te))
        for k, im, x_, y_, deg, up, te in draws:
            sh = shadows[k]; f_ = max(0.5, 1 - 0.3 * up / hop_px)
            if te >= 0.5: s2 = sh.resize((max(1, round(sh.width * f_)), max(1, round(sh.height * f_)))); fr.paste(s2, (round(x_ - s2.width / 2), round(sprites[k]['bot'] - s2.height / 2)), s2)
        for k, im, x_, y_, deg, up, te in draws:
            r = draw_pivot(fr, im, x_, y_, deg)
            if te >= 1 + 0.1 / sprites[k]['dur'] and r: track[k] = union(track.get(k), r)
        if a.guides: guides(fr, W, H, ext)
        arr = np.asarray(fr)
        if fi == 0: arr = (arr * 0.65 + np.array(pal['accent']) * 0.35).astype(np.uint8)           # one accent flash frame
        q = t - SLAM_T
        if 0 <= q < 0.2:                                                                      # the slam shakes the frame
            k_ = 6 * (1 - q / 0.2); arr = np.roll(np.roll(arr, round(k_ * math.sin(q * 95)), 1), round(k_ * math.cos(q * 80)), 0)
        if fi >= N - WHIP: arr = whip(arr, (fi - (N - WHIP) + 1) / WHIP, bg_now, fi)
        fr = Image.fromarray(arr)
        if fi % fps == fps // 2: thumbs.append((t, fr.resize((W // 4, H // 4), Image.LANCZOS)))
        for st_ in stills:
            if fi == round(st_ * fps): p_ = f'{os.path.splitext(a.out)[0]}_t{st_:05.2f}.png'; fr.save(p_); print('still', p_)
        ff.stdin.write(arr.tobytes())
    ff.stdin.close(); rc = ff.wait(); os.remove(wav)
    if rc: die('ffmpeg failed', rc)
    bad = [f'{k}: drawn at {tuple(round(v) for v in r)}, outside its checked area {tuple(round(v) for v in ext[k])}' for k, r in track.items()
           if k in ext and (r[0] < ext[k][0] - 2 or r[1] < ext[k][1] - 2 or r[2] > ext[k][2] + 2 or r[3] > ext[k][3] + 2)]
    bad += spill[:20] + ([f'... {len(spill) - 20} more caption spills'] if len(spill) > 20 else [])
    if a.sheet: sheet(thumbs, a.sheet, T)
    ok = guard(a.out)
    for b_ in bad: print('LAYOUT DRIFT:', b_)
    print('layout: nothing covers the faces or the subject; every caption word stays on its plate' if not bad else 'layout: see LAYOUT DRIFT above')
    sys.exit(0 if ok and not bad else 4)


def draw_plate(fr, r, tip_x, tip_y, shadow):
    """the white speech plate r (rounded, dark outline, hard drop shadow) with a tail down towards (tip_x, tip_y): the
    tip leans at most 0.6 x the plate half-width from its centre and the base is 36 px wide, so a short page keeps a
    short, solid tail. Returns the tail tip (the anchor of the page pop)."""
    d = ImageDraw.Draw(fr); hw, hh = (r[2] - r[0]) / 2, (r[3] - r[1]) / 2; cx = (r[0] + r[2]) / 2; R = min(18, hh * 0.6)
    tx = min(max(tip_x, cx - 0.6 * hw), cx + 0.6 * hw)
    bx = min(max(cx + (tx - cx) * 0.75, r[0] + R + 20), r[2] - R - 20); tl = [(bx - 18, r[3] - 3), (bx + 18, r[3] - 3), (tx, tip_y)]
    o = shadow; d.rounded_rectangle((r[0] + o, r[1] + o, r[2] + o, r[3] + o), radius=R, fill=INK)
    if tip_y > r[3] + 4: d.polygon([(x + o * 0.6, y) for x, y in tl], fill=INK)
    d.rounded_rectangle(r, radius=R, fill=(255, 255, 255), outline=INK, width=4)
    if tip_y > r[3] + 4:
        d.polygon(tl, fill=(255, 255, 255)); d.line([tl[0], tl[2]], fill=INK, width=4); d.line([tl[1], tl[2]], fill=INK, width=4)
    return tx, tip_y


def draw_bar(fr, box, t, T, fps, pal, fbar, fnum, text):
    """the countdown: the fill runs down and warms to the accent colour; a shine sweeps it; the last 3 seconds pop."""
    bx0, by0, bx1, by1 = (round(v) for v in box); hb = by1 - by0; left = max(0.0, 1 - t / T); rem = T - t; n = max(0, math.ceil(rem - 1e-6))
    since = n - rem; hot = n <= 3                                        # the number shown changes when rem passes an integer
    d = ImageDraw.Draw(fr); flash = hot and since < 2 / fps
    d.rounded_rectangle((bx0, by0, bx1, by1), radius=hb / 2, fill=INK, outline=tuple(pal['title']) if flash else (255, 255, 255), width=max(2, round(hb * 0.10)))
    ins = max(3, round(hb * 0.16)); w = (t / T - 0.7) / 0.3
    col = tuple(int(a_ + (b_ - a_) * min(1, max(0, w))) for a_, b_ in zip(pal['bar'], pal['accent']))
    fx1 = bx0 + ins + (bx1 - bx0 - 2 * ins) * left
    if left > 0.01:
        d.rounded_rectangle((bx0 + ins, by0 + ins, fx1, by1 - ins), radius=(hb - 2 * ins) / 2, fill=col)
        ph = (t % 1.5) / 0.7
        if ph < 1:                                                           # a shine sweeps across the fill every 1.5 s
            mw, mh = round(fx1 - bx0), hb; m = Image.new('L', (mw, mh), 0)
            ImageDraw.Draw(m).rounded_rectangle((ins, ins, mw - 1, mh - ins), radius=(hb - 2 * ins) / 2, fill=255)
            sh = Image.new('L', (mw, mh), 0); x = -hb * 2 + ph * (mw + hb * 3); sw = (bx1 - bx0) * 0.08
            ImageDraw.Draw(sh).polygon([(x + hb * 0.5, 0), (x + hb * 0.5 + sw, 0), (x + sw, mh), (x, mh)], fill=90)
            fr.paste((255, 255, 255), (bx0, by0), ImageChops.multiply(m, sh))
    d.text((bx0 + hb * 0.7, (by0 + by1) / 2), text, font=fbar, anchor='lm', fill=(255, 255, 255), stroke_width=2, stroke_fill=INK)
    if rem < 0.5: return                                                 # no '0s' while the break still plays
    s = 1 + 0.35 * max(0.0, 1 - since / 0.2) if hot else 1.0; fs = round(fbar.size * s)
    if fs not in fnum: fnum[fs] = font('archivo', fs)
    d.text((bx1 - hb * 0.6, (by0 + by1) / 2), f'{n}s', font=fnum[fs], anchor='rm', fill=tuple(pal['title']) if hot else (255, 255, 255), stroke_width=2, stroke_fill=INK)


def whip(arr, p, bg, seed):
    """whip-pan out: the frame slides left, faster and faster, with a horizontal smear and speed lines; the empty
    background (rays, halftone, floor) shows where the content has slid away, never a flat fill."""
    Hh, Ww = arr.shape[:2]; sft = round(Ww * p ** 2); acc = np.zeros(arr.shape, np.float32)
    for j in range(4):
        s = min(Ww, sft + round(12 * j * p)); o = bg.astype(np.float32).copy()
        if s < Ww: o[:, :Ww - s] = arr[:, s:]
        acc += o
    im = Image.fromarray((acc / 4).astype(np.uint8)); d = ImageDraw.Draw(im); rng = np.random.default_rng(seed)
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); do = ImageDraw.Draw(ov)
    for _ in range(10):
        y = rng.uniform(0.1, 0.9) * Hh; x0 = rng.uniform(0, 0.6) * Ww; do.line([(x0, y), (x0 + rng.uniform(0.25, 0.6) * Ww, y)], fill=(255, 255, 255, 180), width=4)
    return np.asarray(Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB'))


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
