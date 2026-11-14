"""Paste one keyed bike cockpit onto a world plate so the bike is identical in all shots, relit per world.
usage: comp.py <cockpit_green.jpg> <plate.jpg> <out.jpg>"""
import sys, numpy as np
from PIL import Image, ImageFilter
def blur(a, r): return np.asarray(Image.fromarray((np.clip(a, 0, 1)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))).astype(np.float32)/255
c = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(np.float32)/255
p = np.asarray(Image.open(sys.argv[2]).convert('RGB').resize((768, 1344), Image.LANCZOS)).astype(np.float32)/255
r, g, b = c[..., 0], c[..., 1], c[..., 2]; green = g - np.maximum(r, b)
a = 1 - np.clip((green - 0.05)/0.12, 0, 1)
a = np.where(c.max(axis=2) < 0.32, 1.0, a)                                             # dark parts (fork, gloves) are always bike, even with green bounce
a = np.asarray(Image.fromarray((a*255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.0))).astype(np.float32)/255
fg = c.copy(); fg[..., 1] = np.minimum(fg[..., 1], np.maximum(r, b)*1.02)                 # despill
dark = np.clip((0.45 - c.max(axis=2))/0.2, 0, 1)[..., None]; fg = fg*(1 - dark) + fg.mean(axis=2, keepdims=True)*dark   # no green cast on black parts
env = blur(p, 60)                                                                        # low-frequency scene light at each pixel
envn = env/(env.mean(axis=2, keepdims=True) + 1e-6)                                      # its colour
expo = 0.35 + 1.5*env.mean(axis=2, keepdims=True)                                        # its brightness
fg = fg*expo*(0.45 + 0.55*envn)                                                          # relight: exposure and tint follow the world
edge = blur(a, 5); rim = np.clip(a - edge, 0, 1)[..., None]*0.6                            # inner edge band
fg = fg + env*rim*0.5 + blur(p, 20)*(1 - blur(a, 3))[..., None]*0.15                     # rim light + light wrap
sh = np.roll(blur(a, 22), 14, axis=0)                                                    # soft shadow thrown down onto the ground
p2 = p*(1 - 0.45*sh[..., None]*(1 - a[..., None]))
out = fg*a[..., None] + p2*(1 - a[..., None])
Image.fromarray((np.clip(out, 0, 1)*255).astype(np.uint8)).save(sys.argv[3], quality=95)
