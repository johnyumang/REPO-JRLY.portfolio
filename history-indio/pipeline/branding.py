"""History Indio branding: a small logo bug shown on every frame, and an end card for the last seconds."""
import math
from PIL import Image, ImageDraw, ImageFont
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
PLUM, GOLD, CREAM, RED = '#1f121f', '#ffd34d', '#fff6dc', '#c62828'

def _sun(d, cx, cy, r, col=GOLD):
    for i in range(8):
        a = i * math.pi / 4; d.polygon([(cx + math.cos(a - .16) * r * 1.05, cy + math.sin(a - .16) * r * 1.05), (cx + math.cos(a) * r * 1.75, cy + math.sin(a) * r * 1.75),
                                        (cx + math.cos(a + .16) * r * 1.05, cy + math.sin(a + .16) * r * 1.05)], fill=col)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)

def logo(width=330):
    """Badge: sun + HISTORY / INDIO on a dark plum plate with a gold rule."""
    s = width / 330; im = Image.new('RGBA', (width, int(118 * s)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, width - 1, im.height - 1], radius=int(22 * s), fill=PLUM + 'e6', outline=GOLD, width=max(2, int(4 * s)))
    _sun(d, int(58 * s), int(59 * s), int(21 * s))
    d.text((int(108 * s), int(14 * s)), 'HISTORY', font=ImageFont.truetype(FB, int(30 * s)), fill=CREAM)
    d.text((int(106 * s), int(46 * s)), 'INDIO', font=ImageFont.truetype(FB, int(56 * s)), fill=GOLD)
    return im

def bug(size=(1080, 1920)):
    """Full-frame transparent layer with the logo in the top-left safe area."""
    ov = Image.new('RGBA', size, (0, 0, 0, 0)); lg = logo(300); lg.putalpha(lg.split()[3].point(lambda v: int(v * .92))); ov.alpha_composite(lg, (44, 96)); return ov

import os as _os
def endcard(size=(1080, 1920), line=None):
    line = line or _os.environ.get('HI_ENDCARD', 'FOLLOW = DAGDAG LAKAS LABAN SA PEKENG KASAYSAYAN!')      # set HI_ENDCARD per video to change the line
    W, H = size; ov = Image.new('RGBA', size, (20, 10, 22, 150)); d = ImageDraw.Draw(ov)
    lg = logo(820); ov.alpha_composite(lg, ((W - lg.width) // 2, int(H * .2)))
    size = 46; f = ImageFont.truetype(FB, size)
    while d.textlength(line, font=f) > W - 140 and size > 24: size -= 2; f = ImageFont.truetype(FB, size)
    w = d.textlength(line, font=f); x = (W - w) // 2; y = int(H * .2) + lg.height + 46
    d.rounded_rectangle([x - 30, y - 18, x + w + 30, y + 74], radius=18, fill=RED); d.text((x, y), line, font=f, fill='#ffffff')
    return ov

if __name__ == '__main__':
    import sys; logo(660).save(sys.argv[1] if len(sys.argv) > 1 else 'history_indio_logo.png')
