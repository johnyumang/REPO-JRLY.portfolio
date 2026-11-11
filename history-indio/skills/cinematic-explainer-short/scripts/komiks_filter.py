#!/usr/bin/env python3
"""Pinoy Komiks look: turn any rendered or generated frame into halftone ink on newsprint.

usage: komiks_filter.py in.png out.png [--caption "TEXT" ...] [--bottom "TEXT"]
Posterises colour, adds angled halftone dots in the shadows, inks the edges, tints to newsprint,
adds grain and a panel border. Captions are optional yellow/white komiks boxes.
"""
import math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def komiks(im, dot=13, seed=5, border=True):
    im = im.convert('RGB')
    W, H = im.size
    a = np.asarray(im).astype(np.float32) / 255
    lum = a @ np.array([0.3, 0.59, 0.11])
    lq = np.maximum(np.round(lum * 6) / 6, 0.12)                 # posterise brightness only, so hues stay clean
    post = np.clip(a * (lq / np.maximum(lum, 1e-3))[..., None], 0, 1)
    yy, xx = np.mgrid[0:H, 0:W]
    ang = math.radians(35)
    u = xx * math.cos(ang) + yy * math.sin(ang)
    v = -xx * math.sin(ang) + yy * math.cos(ang)
    d = np.sqrt(((u % dot) - dot / 2) ** 2 + ((v % dot) - dot / 2) ** 2)
    dots = (d < np.clip(0.78 - lum, 0, 1) * dot * 0.85).astype(np.float32)
    post = post * (1 - 0.42 * dots[..., None])
    edges = np.asarray(im.convert('L').filter(ImageFilter.GaussianBlur(1.2)).filter(ImageFilter.FIND_EDGES)
                       .filter(ImageFilter.MaxFilter(5))).astype(np.float32) / 255
    ink = np.clip(edges * 4 - 0.25, 0, 1)[..., None]
    post = post * (1 - ink) + np.array([0.12, 0.07, 0.12]) * ink
    post = post * np.array([1.0, 0.95, 0.82])
    n = np.random.default_rng(seed).normal(0, 9, (H // 2, W // 2)).astype(np.float32)
    n = np.asarray(Image.fromarray(n).resize((W, H), Image.BILINEAR))
    out = Image.fromarray(np.clip(post * 255 + n[..., None], 0, 255).astype(np.uint8))
    if border:
        ImageDraw.Draw(out).rectangle([14, 14, W - 14, H - 14], outline='#1f121f', width=14)
    return out


def caption(im, text, x, y, size=58, bg='#ffe45c'):
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, size)
    while d.textlength(text, font=f) > im.width - 2 * x - 60 and size > 24:
        size -= 2
        f = ImageFont.truetype(FONT, size)
    w = d.textlength(text, font=f)
    d.rectangle([x - 8, y - 8, x + w + 44, y + size + 36], fill='#1f121f')
    d.rectangle([x - 18, y - 18, x + w + 32, y + size + 24], fill=bg, outline='#1f121f', width=7)
    d.text((x + 6, y), text, font=f, fill='#1f121f')


def overlay(size, top=None, bottom=None):
    """Transparent layer with the panel border and caption boxes, kept inside the phone-safe area."""
    W, H = size
    ov = Image.new('RGBA', size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).rectangle([14, 14, W - 14, H - 14], outline='#1f121f', width=14)
    if top:
        caption(ov, top, 70, int(H * 0.105), 56)
    if bottom:
        caption(ov, bottom, 70, int(H * 0.735), 52, '#ffffff')
    return ov


if __name__ == '__main__':
    a = sys.argv[1:]
    out = komiks(Image.open(a[0]))
    if '--caption' in a:
        caption(out, a[a.index('--caption') + 1], 60, 70)
    if '--bottom' in a:
        caption(out, a[a.index('--bottom') + 1], 80, out.height - 190, 50, '#ffffff')
    out.save(a[1])
