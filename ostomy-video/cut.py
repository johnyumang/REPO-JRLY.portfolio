# Cut the belt out of the owner's photo (dark object on light tiles) and cover the sewn-in label.
import sys
from PIL import Image, ImageOps, ImageDraw, ImageFilter
import numpy as np
src, dst = sys.argv[1], sys.argv[2]
im = ImageOps.exif_transpose(Image.open(src)).convert('RGB')
a = np.asarray(im).astype(np.float32).copy(); L = a.mean(2)
reg = (slice(1930, 2140), slice(890, 1090))
ys, xs = np.nonzero(L[reg] > 68)
lx0, lx1, ly0, ly1 = xs.min() + 890 - 12, xs.max() + 890 + 12, ys.min() + 1930 - 12, ys.max() + 1930 + 12
print('label', lx0, lx1, ly0, ly1)
rng = np.random.default_rng(1); patch = np.zeros((ly1 - ly0, lx1 - lx0, 3), np.float32)
for y in range(ly0, ly1):
    l = a[y, lx0 - 18:lx0 - 4].mean(0); r = a[y, lx1 + 4:lx1 + 18].mean(0)
    t = np.linspace(0, 1, lx1 - lx0)[:, None]; patch[y - ly0] = l * (1 - t) + r * t
patch += rng.normal(0, 1.6, patch.shape)
w = Image.new('L', (lx1 - lx0, ly1 - ly0), 0); ImageDraw.Draw(w).rectangle([8, 8, lx1 - lx0 - 9, ly1 - ly0 - 9], fill=255)
w = np.asarray(w.filter(ImageFilter.GaussianBlur(4)), np.float32)[..., None] / 255
a[ly0:ly1, lx0:lx1] = a[ly0:ly1, lx0:lx1] * (1 - w) + patch * w
m = Image.fromarray(((a.mean(2) < 100) * 255).astype(np.uint8)).copy(); ImageDraw.floodfill(m, (1417, 1159), 128)
mm = np.array(m) == 128
mi = Image.fromarray((mm * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.MinFilter(9)).filter(ImageFilter.GaussianBlur(1.5))
al = np.asarray(mi); ys, xs = np.nonzero(al > 128); x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
top = np.nonzero(al[y0 + 2] > 128)[0]; print('bbox', x0, x1, y0, y1, 'top strap centre x rel', (top.min() + top.max()) // 2 - x0)
rgba = np.dstack([np.clip(a, 0, 255).astype(np.uint8), al])[y0:y1 + 1, x0:x1 + 1]
Image.fromarray(rgba).save(dst); print('size', rgba.shape)
