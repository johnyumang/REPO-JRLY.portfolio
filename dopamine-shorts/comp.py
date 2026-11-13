"""Paste one keyed bike cockpit onto every world plate so the bike is identical in all shots.
usage: comp.py <cockpit_green.jpg> <plate.jpg> <out.jpg>"""
import sys, numpy as np
from PIL import Image, ImageFilter
c = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(np.float32)/255; p = np.asarray(Image.open(sys.argv[2]).convert('RGB').resize((768, 1344))).astype(np.float32)/255
r, g, b = c[..., 0], c[..., 1], c[..., 2]
green = g - np.maximum(r, b)                                   # green dominance
a = 1 - np.clip((green - 0.06)/0.14, 0, 1)                     # alpha: 1 = bike
a = np.asarray(Image.fromarray((a*255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32)/255
fg = c.copy(); spill = np.clip(g - np.maximum(r, b), 0, 1); fg[..., 1] -= spill          # despill
amb = p[900:].reshape(-1, 3).mean(0); key = p.reshape(-1, 3).mean(0)                      # scene ambient colour
lum = p.mean()
fg = fg*(0.55 + 0.9*lum) * (0.6 + 0.4*amb/ (amb.mean()+1e-6))                             # match exposure and tint
wrap = np.asarray(Image.fromarray((p*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(25))).astype(np.float32)/255
edge = np.clip(np.asarray(Image.fromarray((a*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))).astype(np.float32)/255, 0, 1)
fg = fg + wrap*(1-edge)[..., None]*0.5                                                   # light wrap at the edges
sh = np.asarray(Image.fromarray((a*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(18))).astype(np.float32)/255
p = p*(1 - 0.25*sh[..., None])                                                           # soft contact shadow
out = fg*a[..., None] + p*(1-a[..., None])
Image.fromarray((np.clip(out, 0, 1)*255).astype(np.uint8)).save(sys.argv[3], quality=95)
