#!/usr/bin/env python3
"""REAL Latin writing on a sign, plaque, marker or label inside a picture (the owner, 14 Nov: a sign the story says carries
writing is never empty; an image model cannot write, so the picture is drawn with no writing and the words are added here).
Same placing as baybayin.py (perspective onto four corners, worn a little, mixed into the paint), with a Latin font.
Use it only for things of TODAY or of a period that wrote in Latin letters, with short words that are certainly true (a
street name, a place name, a date on a marker that the script states); never an invented inscription. Filipinos writing for
themselves before about 1600 -> baybayin.py instead; a Spanish, British or American paper -> plain ruled lines, no words.

usage (from history-indio/):
  sign_text.py paste <in.jpg> <out.jpg> "<WORDS|SECOND LINE>" x1,y1,x2,y2,x3,y3,x4,y4 [--font sans|serif|bold] [--colour r,g,b]
               [--opacity 0.9] [--rough 0.5] [--carve]
      corners in pixels: top-left, top-right, bottom-right, bottom-left; "|" starts a new line; --carve = light letters with a
      dark edge (stone, bronze). LOOK at the result at 3x before you keep it.
  sign_text.py test"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import baybayin
FONTS = {'sans': '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 'serif': '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',
         'bold': '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'}


def render_latin(font_path):
    def render(text, px=160, colour=(40, 26, 12), final=None, pad=0.18):
        from PIL import Image, ImageDraw, ImageFont
        f = ImageFont.truetype(font_path, px); d = ImageDraw.Draw(Image.new('L', (8, 8))); x0, y0, x1, y1 = d.textbbox((0, 0), text, font=f)
        p = int(px * pad); im = Image.new('RGBA', (x1 - x0 + 2 * p, y1 - y0 + 2 * p), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((p - x0, p - y0), text, font=f, fill=tuple(colour) + (255,)); return im
    return render


def paste(src, dst, text, quad, font='sans', colour=None, opacity=0.9, rough=0.5, carve=False):
    """Latin words laid on the four-cornered place, with baybayin.paste's warp and blending."""
    old = baybayin.render, baybayin.to_baybayin
    baybayin.render = render_latin(FONTS.get(font, font)); baybayin.to_baybayin = lambda t, final=None: t
    try: return baybayin.paste(src, dst, text, quad, colour=colour, opacity=opacity, rough=rough, carve=carve)
    finally: baybayin.render, baybayin.to_baybayin = old


def _test():
    import numpy as np, cv2, tempfile
    d = tempfile.mkdtemp(); a = os.path.join(d, 'a.jpg'); b = os.path.join(d, 'b.jpg')
    cv2.imwrite(a, np.full((400, 600, 3), 200, np.uint8))
    paste(a, b, 'DEZHOU|1417', [100, 100, 500, 120, 490, 300, 110, 280]); im = cv2.imread(b)
    assert im is not None and im[150:250, 150:450].min() < 150, 'no ink was laid'
    assert abs(int(im[10, 10].mean()) - 200) <= 2, 'ink outside the place'
    print('sign_text test PASSED')


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    if a[0] == 'test': _test()
    elif a[0] == 'paste' and len(a) >= 5:
        opt = lambda k, d: a[a.index(k) + 1] if k in a else d
        col = opt('--colour', None); col = tuple(int(v) for v in col.split(',')) if col else None
        q = [float(v) for v in a[4].split(',')]; assert len(q) == 8, 'four corners: x1,y1,...,x4,y4'
        paste(a[1], a[2], a[3], q, font=opt('--font', 'sans'), colour=col, opacity=float(opt('--opacity', 0.9)), rough=float(opt('--rough', 0.5)), carve='--carve' in a)
        print('written', a[2], '| words:', a[3])
    else: sys.exit(__doc__)
