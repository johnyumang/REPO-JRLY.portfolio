#!/usr/bin/env python3
"""An ACCURATE glowing map of the Philippines with points of light, drawn from real coastline data instead of an image model
(image models mangle the archipelago and cannot count lights). Made for Episode 43 (full/map_five.jpg).
usage: ph_map.py <out.jpg> [Name:lon:lat ...]        default: the five places of Episode 43
needs (once, outside the pipeline venv is fine):  pip install --target <dir> basemap basemap-data ; PYTHONPATH=<dir> python ph_map.py ...
Land cut by the frame (Borneo) and Malaysian or Indonesian islands are left out. 768x1344, the look of the series' night maps."""
import sys, math, numpy as np
import matplotlib; matplotlib.use('Agg')
from mpl_toolkits.basemap import Basemap
from PIL import Image, ImageDraw, ImageFilter
import cv2
out = sys.argv[1]; W, H, SS = 768, 1344, 3
m = Basemap(projection='merc', llcrnrlon=116.2, llcrnrlat=4.0, urcrnrlon=127.3, urcrnrlat=21.3, resolution='i', area_thresh=25)
mw, mh = m.xmax, m.ymax; bw = 700.0; sc = bw / mw; bh = mh * sc; ox = (W - bw) / 2; oy = 70.0
def XY(lon, lat): x, y = m(lon, lat); return (ox + x * sc, oy + (mh - y) * sc)
land = Image.new('L', (W * SS, H * SS), 0); d = ImageDraw.Draw(land); polys = []
for p in m.landpolygons:
    c = np.asarray(p.get_coords())
    if len(c) < 3: continue
    if c[:, 0].min() < 2000 or c[:, 1].min() < 2000 or c[:, 0].max() > mw - 2000 or c[:, 1].max() > mh - 2000: continue      # land cut by the frame (Borneo): not the Philippines
    lon, lat = m(c[:, 0].mean(), c[:, 1].mean(), inverse=True)
    if (lon < 118.0 and lat < 7.6) or (lon < 119.2 and lat < 6.6) or (lon > 125.9 and lat < 5.0): continue                   # Malaysian and Indonesian islands
    pts = [((ox + x * sc) * SS, (oy + (mh - y) * sc) * SS) for x, y in c]
    d.polygon(pts, fill=255); polys.append(pts)
ink = Image.new('L', (W * SS, H * SS), 0); di = ImageDraw.Draw(ink)
for pts in polys: di.line(pts + [pts[0]], fill=255, width=int(1.7 * SS), joint='curve')
land = np.asarray(land.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255; ink = np.asarray(ink.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
rng = np.random.default_rng(43); Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
# the dark, with a faint blue lift behind the islands
bg = np.zeros((H, W, 3), np.float32); bg[...] = (3, 9, 22)
lift = cv2.GaussianBlur(land, (0, 0), 90); bg += lift[..., None] * np.array((4, 40, 78), np.float32) * 1.6
glow = cv2.GaussianBlur(land, (0, 0), 26); rim = cv2.GaussianBlur(land, (0, 0), 7)
img = bg + glow[..., None] * np.array((10, 120, 205), np.float32) * 1.15 + rim[..., None] * np.array((40, 150, 230), np.float32) * 0.75
# land: two-tone cel fill in old gold, light from the upper left, a few painted patches
n1 = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 16); n1 /= np.abs(n1).max()
n2 = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 3); n2 /= np.abs(n2).max()
edge = cv2.GaussianBlur(land, (0, 0), 5); gx = cv2.Sobel(edge, cv2.CV_32F, 1, 0, ksize=5); gy = cv2.Sobel(edge, cv2.CV_32F, 0, 1, ksize=5)
lit = np.clip((gx + gy) * 1.4, -1, 1)                                   # + on shores facing the upper left
tone = (n1 > 0.18).astype(np.float32); tone = cv2.GaussianBlur(tone, (0, 0), 1.2)
light, dark, hi = np.array((218, 200, 112), np.float32), np.array((150, 148, 92), np.float32), np.array((238, 226, 150), np.float32)
fill = light[None, None] * (1 - tone[..., None]) + dark[None, None] * tone[..., None]
fill = fill * (1 + 0.05 * n2[..., None]) + np.clip(lit, 0, 1)[..., None] * (hi - light)[None, None] * 0.9 - np.clip(-lit, 0, 1)[..., None] * 38
img = img * (1 - land[..., None]) + fill * land[..., None]
img = img * (1 - 0.92 * ink[..., None]) + np.array((18, 16, 8), np.float32) * 0.92 * ink[..., None]
# five lights
P = [('Manila Bay', 120.93, 14.58), ('Mactan', 123.98, 10.31), ('Bohol', 124.17, 9.83), ('Lake Lanao', 124.25, 7.90), ('Sulu', 121.02, 6.03)]
if len(sys.argv) > 2: P = [(n, float(lo), float(la)) for n, lo, la in (x.split(':') for x in sys.argv[2:])]
for name, lon, lat in P:
    x, y = XY(lon, lat); D = np.hypot(X - x, Y - y)
    halo = np.exp(-(D / 12.0) ** 2) * 1.0 + np.exp(-(D / 34.0) ** 2) * 0.2; core = np.clip(1 - (D - 4.2) / 2.0, 0, 1)
    ring = np.exp(-((D - 13.5) / 1.3) ** 2) * 0.85
    fl = np.exp(-(np.abs(Y - y) / 1.1) ** 2) * np.exp(-(np.abs(X - x) / 20.0) ** 2) + np.exp(-(np.abs(X - x) / 1.1) ** 2) * np.exp(-(np.abs(Y - y) / 20.0) ** 2)
    shade = np.exp(-(D / 20.0) ** 2) * 0.45; img = img * (1 - shade[..., None])                       # the land dims a little under each light so the light reads on the gold
    img += halo[..., None] * np.array((255, 150, 40), np.float32) * 1.05 + fl[..., None] * np.array((255, 225, 160), np.float32) * 0.8 + ring[..., None] * np.array((255, 215, 140), np.float32)
    img = img * (1 - core[..., None]) + np.array((255, 250, 228), np.float32) * core[..., None]
    print('%-11s at %.0f, %.0f' % (name, x, y))
# vignette and a little grain, like the painted stills
v = 1 - 0.35 * np.clip((np.hypot((X - W / 2) / (W * 0.75), (Y - H * 0.42) / (H * 0.62)) - 0.55), 0, 1)
img = img * v[..., None] + rng.normal(0, 1.6, (H, W, 1)).astype(np.float32)
Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(out, quality=94); print('saved', out)
