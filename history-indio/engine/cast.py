"""History Indio cast: flat 2D bean-head caricatures drawn with cairo.

Every character is defined ONLY by the parameters in CAST, and drawn by one
function (draw_char).  Same params in -> same face out, in every shot.
These are clearly cartoons (bean heads, dot eyes, name tags), not likenesses.
"""
import math
import cairo

INK = (0.23, 0.12, 0.23)          # plum outline
LW = 9                             # outline width in design units


def hexc(h):
    if not isinstance(h, str):
        return tuple(h)
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


CAST = {
    # real public figures (caricature = hair silhouette + outfit + name tag)
    'sara': dict(name='VP SARA', skin='#c98e66', hair='#1d1716', hstyle='pixie',
                 outfit='#2f6b3a', collar='#f2efe6', pants='#2a2a33', tag='#ffd34d',
                 cheek=0.35, headw=1.0),
    'castro': dict(name='PALACE', skin='#d9a27a', hair='#2b1d18', hstyle='bob',
                   outfit='#24375e', collar='#ffffff', pants='#1f2433', tag='#ffffff',
                   cheek=0.3, headw=0.96),
    'jing': dict(name='AMB. JING', skin='#e2b48c', hair='#151515', hstyle='neat',
                 outfit='#3a3a40', collar='#ffffff', pants='#2a2a30', tag='#e84a3c',
                 tie='#a3282b', cheek=0.15, headw=1.04),
    'wang': dict(name='WANG YI', skin='#e6bb93', hair='#c9c9cf', hstyle='silver',
                 outfit='#2c2c34', collar='#ffffff', pants='#24242a', tag='#e84a3c',
                 tie='#5a2a6e', cheek=0.1, headw=1.0),
    # generic / original characters (not real individuals)
    'afp': dict(name='AFP', skin='#b9825c', hair='#1a1410', hstyle='cap',
                outfit='#56663a', collar='#56663a', pants='#4a5732', tag='#f5d142',
                camo=True, cheek=0.2, headw=1.02),
    'indio': dict(name='INDIO', skin='#c58b5e', hair='#24160f', hstyle='curly',
                  outfit='#f4eedb', collar='#f4eedb', pants='#3b5f8c', tag=None,
                  barong=True, cheek=0.4, headw=1.0),
    'ofw1': dict(name=None, skin='#c4875f', hair='#1c1414', hstyle='pony', outfit='#e0574f',
                 collar='#e0574f', pants='#33334a', tag=None, cheek=0.3, headw=0.95),
    'ofw2': dict(name=None, skin='#b77a52', hair='#151010', hstyle='bob', outfit='#3f9ad6',
                 collar='#3f9ad6', pants='#2b2b3d', tag=None, cheek=0.3, headw=0.95),
    'ofw3': dict(name=None, skin='#d1966b', hair='#2a1a12', hstyle='neat', outfit='#f2b33d',
                 collar='#f2b33d', pants='#3a3a3a', tag=None, cheek=0.25, headw=1.0),
}

EXPRS = ['neutral', 'happy', 'talk', 'angry', 'surprised', 'smug']


# ---------------------------------------------------------------- helpers
def fill_stroke(ctx, col, lw=LW):
    ctx.set_source_rgb(*hexc(col) if isinstance(col, str) else col)
    ctx.fill_preserve()
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(lw)
    ctx.stroke()


def ellipse(ctx, x, y, rx, ry):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(rx, ry)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()


def rrect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


def limb(ctx, pts, col, w):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    for lw, c in ((w + 2 * LW, INK), (w, hexc(col))):
        ctx.move_to(*pts[0])
        if len(pts) == 3:
            ctx.curve_to(pts[1][0], pts[1][1], pts[1][0], pts[1][1], pts[2][0], pts[2][1])
        else:
            for p in pts[1:]:
                ctx.line_to(*p)
        ctx.set_source_rgb(*c)
        ctx.set_line_width(lw)
        ctx.stroke()


# ---------------------------------------------------------------- arms
ARM_POSES = {
    #        (elbow, hand) for the arm on the +x side; mirrored for -x side
    'down': ((150, -430), (165, -320)),
    'hip': ((215, -430), (130, -370)),
    'point': ((230, -560), (330, -600)),
    'up': ((210, -640), (230, -790)),
    'pinky': ((215, -600), (200, -760)),
    'fist': ((230, -620), (230, -790)),
    'podium': ((190, -450), (150, -420)),
    'phone': ((200, -560), (150, -700)),
    'wave': ((230, -600), (280, -760)),
    'shrug': ((230, -470), (300, -540)),
}


def hand(ctx, x, y, skin, kind='open', s=1.0):
    if kind == 'fist':
        rrect(ctx, x - 52 * s, y - 50 * s, 104 * s, 100 * s, 38 * s)
        fill_stroke(ctx, skin)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(6)
        for i in (-1, 0, 1):
            ctx.move_to(x + i * 26 * s - 10, y - 46 * s)
            ctx.line_to(x + i * 26 * s - 10, y - 10 * s)
        ctx.stroke()
        return
    if kind == 'pinky':
        # tiny little finger up from a closed hand
        rrect(ctx, x - 13, y - 92, 26, 70, 13)
        fill_stroke(ctx, skin, 7)
        ellipse(ctx, x, y, 34, 32)
        fill_stroke(ctx, skin)
        return
    if kind == 'point':
        rrect(ctx, x, y - 12, 70, 24, 12)
        fill_stroke(ctx, skin, 7)
    ellipse(ctx, x, y, 32, 30)
    fill_stroke(ctx, skin)


def draw_arm(ctx, ch, side, pose, outfit_col):
    sx = side
    elbow, hnd = ARM_POSES.get(pose, ARM_POSES['down'])
    sh = (sx * 95, -520)
    el = (sx * elbow[0], elbow[1])
    hd = (sx * hnd[0], hnd[1])
    limb(ctx, [sh, el, hd], outfit_col, 30)
    kind = 'open'
    if pose == 'fist':
        kind = 'fist'
    elif pose == 'pinky':
        kind = 'pinky'
    elif pose == 'point':
        kind = 'point'
    hand(ctx, hd[0], hd[1], ch['skin'], kind, 1.4 if kind == 'fist' else 1.0)


# ---------------------------------------------------------------- hair
def hair_back(ctx, ch, view, hx):
    st = ch['hstyle']
    if st == 'bob':
        ctx.move_to(hx - 178, -760)
        ctx.curve_to(hx - 215, -560, hx - 190, -520, hx - 140, -520)
        ctx.line_to(hx + 140, -520)
        ctx.curve_to(hx + 190, -520, hx + 215, -560, hx + 178, -760)
        ctx.curve_to(hx + 170, -960, hx - 170, -960, hx - 178, -760)
        ctx.close_path()
        fill_stroke(ctx, ch['hair'])
    elif st == 'pony':
        ellipse(ctx, hx - 150 if view != 'side' else hx - 170, -790, 55, 70)
        fill_stroke(ctx, ch['hair'])


def hair_front(ctx, ch, view, hx, hw):
    st, col = ch['hstyle'], ch['hair']
    off = {'front': 0, 'q': 40, 'side': 85}[view]
    HY, R = -735, 168
    if st == 'curly':
        for dx, dy in [(-130, -830), (-70, -890), (0, -910), (70, -890), (130, -830), (-160, -760), (160, -760)]:
            ellipse(ctx, hx + dx * hw, dy, 62, 55)
            fill_stroke(ctx, col)
        return
    if st == 'cap':
        ctx.save(); ellipse(ctx, hx, HY, R * hw, R); ctx.clip()
        ctx.rectangle(hx - 300, -1000, 600, 215); ctx.set_source_rgb(*hexc(ch['outfit'])); ctx.fill()
        ctx.restore()
        ctx.move_to(hx - R * hw - 6, -785); ctx.curve_to(hx - 150, -985, hx + 150, -985, hx + R * hw + 6, -785)
        ctx.close_path(); fill_stroke(ctx, ch['outfit'])
        rrect(ctx, hx - 150 + off * 0.6, -800, 300 + off * 0.5, 34, 16); fill_stroke(ctx, '#3d4a2a')
        ellipse(ctx, hx + off, -870, 24, 20); fill_stroke(ctx, '#f5d142', 6)
        return
    # fringe line (y of hairline) as function of x, per style
    if st == 'pixie':      # short crop, side-swept fringe falling to the left
        pts = [(-R, -700), (-120, -760), (-40 + off, -800), (60 + off, -790), (R, -760)]
    elif st in ('bob', 'pony'):   # centre-ish part, fuller fringe
        pts = [(-R, -650), (-110, -770), (-10 + off, -800), (20 + off, -820), (110, -780), (R, -650)]
    else:                  # neat / silver: high side part
        pts = [(-R, -720), (-110, -800), (-30 + off, -830), (90 + off, -825), (R, -730)]
    ctx.save()
    ellipse(ctx, hx, HY, R * hw, R)
    ctx.clip()
    ctx.move_to(hx + pts[0][0] * hw - 40, -1000)
    for x, y in pts:
        ctx.line_to(hx + x * hw, y)
    ctx.line_to(hx + pts[-1][0] * hw + 40, -1000)
    ctx.close_path()
    ctx.set_source_rgb(*hexc(col))
    ctx.fill_preserve()
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(LW)
    ctx.stroke()
    ctx.restore()
    # re-ink head outline on top
    ellipse(ctx, hx, HY, R * hw, R)
    ctx.set_source_rgb(*INK); ctx.set_line_width(LW); ctx.stroke()
    if st in ('neat', 'silver'):
        ctx.move_to(hx - 30 + off, -830); ctx.line_to(hx - 10 + off, -895); ctx.set_line_width(6); ctx.stroke()


# ---------------------------------------------------------------- face
def face(ctx, ch, view, expr, talk, blink, hx):
    off = {'front': 0, 'q': 45, 'side': 95}[view]
    if view == 'front':
        eyes = [(-58, 1.0), (58, 1.0)]
    elif view == 'q':
        eyes = [(-20 + off, 0.82), (75 + off, 1.0)]
    else:
        eyes = [(off, 1.0)]
    ey = -720
    ctx.set_source_rgb(*INK)
    # cheeks
    if ch.get('cheek'):
        ctx.set_source_rgba(0.95, 0.45, 0.45, ch['cheek'])
        for ex, sc in eyes:
            ellipse(ctx, hx + ex + (12 if ex > off - 1 else -12), -655, 30 * sc, 18)
            ctx.fill()
    ctx.set_source_rgb(*INK)
    for ex, sc in eyes:
        x = hx + ex
        if expr == 'happy':
            ctx.set_line_width(10)
            ctx.arc(x, ey + 10, 24 * sc, math.pi * 1.1, math.pi * 1.9)
            ctx.stroke()
        elif blink > 0.5:
            ctx.set_line_width(9)
            ctx.move_to(x - 22 * sc, ey)
            ctx.line_to(x + 22 * sc, ey)
            ctx.stroke()
        elif expr == 'surprised':
            ellipse(ctx, x, ey, 26 * sc, 32)
            ctx.set_source_rgb(1, 1, 1)
            ctx.fill_preserve()
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(7)
            ctx.stroke()
            ellipse(ctx, x, ey + 4, 11 * sc, 13)
            ctx.fill()
        else:
            ellipse(ctx, x, ey, 15 * sc, 21)
            ctx.fill()
            ctx.set_source_rgb(1, 1, 1)
            ellipse(ctx, x + 5, ey - 7, 5, 6)
            ctx.fill()
            ctx.set_source_rgb(*INK)
        # brows
        ctx.set_line_width(10)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        bx0, bx1 = x - 26 * sc, x + 26 * sc
        inner_left = ex < off  # brow's inner end is toward face centre
        by = ey - 52
        if expr == 'angry':
            a, b = (by - 14, by + 10) if inner_left else (by + 10, by - 14)
        elif expr == 'surprised':
            a = b = by - 24
        elif expr == 'smug':
            a, b = (by + 4, by + 4) if inner_left else (by - 22, by - 6)
        else:
            a = b = by
        if view == 'side':
            a, b = (by - 24, by - 24) if expr == 'surprised' else ((by + 8, by - 10) if expr == 'angry' else (by, by))
        ctx.move_to(bx0, a)
        ctx.line_to(bx1, b)
        ctx.stroke()
    # nose
    ctx.set_line_width(7)
    if view == 'side':
        ctx.move_to(hx + 150, -700)
        ctx.curve_to(hx + 185, -680, hx + 180, -655, hx + 150, -650)
        ctx.stroke()
    else:
        nx = hx + off * 0.9 + 8
        ctx.move_to(nx, -690)
        ctx.curve_to(nx + 14, -665, nx + 4, -655, nx - 8, -657)
        ctx.stroke()
    # mouth
    mx, my = hx + off * 0.85, -605
    mw = 46 if view != 'side' else 30
    ctx.set_line_width(9)
    if expr == 'talk' or talk > 0.05:
        o = 10 + 34 * (talk if talk > 0.05 else 0.6)
        ellipse(ctx, mx, my + o * 0.3, mw * 0.75, o)
        ctx.set_source_rgb(0.45, 0.12, 0.18)
        ctx.fill_preserve()
        ctx.set_source_rgb(*INK)
        ctx.stroke()
    elif expr == 'happy':
        ctx.move_to(mx - mw, my - 8)
        ctx.curve_to(mx - mw * 0.5, my + 38, mx + mw * 0.5, my + 38, mx + mw, my - 8)
        ctx.close_path()
        ctx.set_source_rgb(0.45, 0.12, 0.18)
        ctx.fill_preserve()
        ctx.set_source_rgb(*INK)
        ctx.stroke()
    elif expr == 'angry':
        ctx.move_to(mx - mw * 0.8, my + 14)
        ctx.curve_to(mx - 10, my - 16, mx + 10, my - 16, mx + mw * 0.8, my + 14)
        ctx.stroke()
    elif expr == 'surprised':
        ellipse(ctx, mx, my + 8, 20, 26)
        ctx.set_source_rgb(0.45, 0.12, 0.18)
        ctx.fill_preserve()
        ctx.set_source_rgb(*INK)
        ctx.stroke()
    elif expr == 'smug':
        ctx.move_to(mx - mw * 0.7, my + 4)
        ctx.curve_to(mx, my + 10, mx + mw * 0.5, my + 4, mx + mw * 0.9, my - 16)
        ctx.stroke()
    else:
        ctx.move_to(mx - mw * 0.6, my)
        ctx.curve_to(mx - 10, my + 14, mx + 10, my + 14, mx + mw * 0.6, my)
        ctx.stroke()


# ---------------------------------------------------------------- body
def draw_char(ctx, key, x, y, scale, view='front', expr='neutral', talk=0.0, blink=0.0,
              arms=('down', 'down'), facing=1, bob=0.0, tilt=0.0, squash=1.0, show_tag=True):
    """Draw character `key` with feet at (x, y). scale = px per design unit
    (figure is ~1000 units tall)."""
    ch = CAST[key]
    hw = ch['headw']
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(scale * facing, scale * squash)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    # contact shadow
    ctx.save()
    ctx.set_source_rgba(0, 0, 0, 0.18)
    ellipse(ctx, 0, 0, 190, 34)
    ctx.fill()
    ctx.restore()
    ctx.translate(0, -bob)
    # legs
    for lx in (-48, 48):
        limb(ctx, [(lx, -200), (lx, -20)], ch['pants'], 22)
        ellipse(ctx, lx + (18 if view != 'front' else 0), -12, 44, 20)
        fill_stroke(ctx, '#2b2020')
    ra, la = arms
    # far arm (behind body) in side / q views
    if view != 'front':
        draw_arm(ctx, ch, -1, la, _darken(ch['outfit']))
    # torso
    egg(ctx)
    fill_stroke(ctx, ch['outfit'])
    if ch.get('camo'):
        ctx.save()
        egg(ctx)
        ctx.clip()
        for i, (bx, by, r) in enumerate([(-70, -480, 40), (40, -420, 50), (-30, -300, 45), (80, -250, 38), (-90, -220, 36), (60, -520, 30)]):
            ellipse(ctx, bx, by, r, r * 0.7)
            ctx.set_source_rgb(*hexc('#3e4b29' if i % 2 else '#7b7f4a'))
            ctx.fill()
        ctx.restore()
    if ch.get('barong'):
        ctx.set_source_rgba(0.55, 0.45, 0.3, 0.6)
        ctx.set_line_width(5)
        for k in range(5):
            ctx.move_to(-60 + k * 30, -540)
            ctx.line_to(-60 + k * 30, -300)
        ctx.stroke()
    # collar / shirt V
    if ch['collar'] != ch['outfit']:
        ctx.move_to(-55, -575)
        ctx.line_to(0, -470)
        ctx.line_to(55, -575)
        ctx.close_path()
        fill_stroke(ctx, ch['collar'], 6)
        if ch.get('tie'):
            ctx.move_to(-14, -540)
            ctx.line_to(14, -540)
            ctx.line_to(20, -420)
            ctx.line_to(0, -395)
            ctx.line_to(-20, -420)
            ctx.close_path()
            fill_stroke(ctx, ch['tie'], 5)
    # name tag
    if show_tag and ch.get('tag') and ch.get('name'):
        tx = 0 if view == 'front' else 40
        rrect(ctx, tx - 85, -380, 170, 66, 12)
        fill_stroke(ctx, ch['tag'], 6)
        ctx.save()
        if facing < 0:  # keep text readable when mirrored
            ctx.translate(tx * 2, 0)
            ctx.scale(-1, 1)
        ctx.set_source_rgb(*INK)
        ctx.select_font_face('DejaVu Sans', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        name = ch['name']
        fs = 34
        ctx.set_font_size(fs)
        ext = ctx.text_extents(name)
        while ext.width > 148 and fs > 14:
            fs -= 2
            ctx.set_font_size(fs)
            ext = ctx.text_extents(name)
        ctx.move_to(tx - ext.width / 2 - ext.x_bearing, -347 + ext.height / 2)
        ctx.show_text(name)
        ctx.restore()
    # head
    hx = {'front': 0, 'q': 10, 'side': 25}[view]
    ctx.save()
    ctx.translate(0, -560)
    ctx.rotate(tilt)
    ctx.translate(0, 560)
    rrect(ctx, -38, -610, 76, 70, 20)            # neck
    fill_stroke(ctx, ch['skin'], 7)
    hair_back(ctx, ch, view, hx)
    ellipse(ctx, hx, -735, 168 * hw, 168)
    fill_stroke(ctx, ch['skin'])
    # ear
    if view != 'front':
        ellipse(ctx, hx - 40 if view == 'side' else hx - 135, -705, 26, 34)
        fill_stroke(ctx, ch['skin'], 7)
    else:
        for exs in (-1, 1):
            ellipse(ctx, exs * 170 * hw, -705, 22, 32)
            fill_stroke(ctx, ch['skin'], 7)
        ellipse(ctx, hx, -735, 168 * hw, 168)
        fill_stroke(ctx, ch['skin'])
    hair_front(ctx, ch, view, hx, hw)
    face(ctx, ch, view, expr, talk, blink, hx)
    ctx.restore()
    # near arm(s)
    if view == 'front':
        draw_arm(ctx, ch, -1, la, ch['outfit'])
    draw_arm(ctx, ch, 1, ra, ch['outfit'])
    ctx.restore()


def egg(ctx):
    ctx.move_to(0, -585)
    ctx.curve_to(110, -585, 145, -420, 140, -300)
    ctx.curve_to(135, -200, 80, -175, 0, -175)
    ctx.curve_to(-80, -175, -135, -200, -140, -300)
    ctx.curve_to(-145, -420, -110, -585, 0, -585)
    ctx.close_path()


def _darken(h, k=0.78):
    r, g, b = hexc(h)
    return (r * k, g * k, b * k)


# ---------------------------------------------------------------- sheet
def character_sheet(key, path):
    W, H = 2400, 1500
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    ctx.set_source_rgb(*hexc('#fbf3e4'))
    ctx.paint()
    ctx.set_source_rgb(*INK)
    ctx.select_font_face('DejaVu Sans', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(54)
    ctx.move_to(60, 90)
    nm = CAST[key]['name'] or key.upper()
    ctx.show_text(f'HISTORY INDIO  ·  character sheet  ·  {nm}')
    ctx.set_font_size(30)
    ctx.move_to(60, 135)
    ctx.show_text('Cartoon caricature (not a likeness). Same parameters are used in every shot.')
    for i, (v, lab) in enumerate([('front', 'FRONT'), ('q', '3/4'), ('side', 'SIDE')]):
        x = 260 + i * 420
        draw_char(ctx, key, x, 1350, 1.0, view=v)
        ctx.set_source_rgb(*INK)
        ctx.set_font_size(36)
        ctx.move_to(x - 50, 1430)
        ctx.show_text(lab)
    for i, e in enumerate(EXPRS):
        cx = 1540 + (i % 3) * 290
        cy = 250 + (i // 3) * 600
        # head-and-shoulders crop
        ctx.save()
        rrect(ctx, cx - 135, cy, 270, 520, 20)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill_preserve()
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(4)
        ctx.stroke()
        rrect(ctx, cx - 135, cy, 270, 520, 20)
        ctx.clip()
        draw_char(ctx, key, cx, cy + 840, 0.78, view='front', expr=e, show_tag=False)
        ctx.restore()
        ctx.set_source_rgb(*INK)
        ctx.set_font_size(30)
        ext = ctx.text_extents(e)
        ctx.move_to(cx - ext.width / 2, cy + 560)
        ctx.show_text(e)
    surf.write_to_png(path)


if __name__ == '__main__':
    import os, sys
    out = sys.argv[1] if len(sys.argv) > 1 else 'sheets'
    os.makedirs(out, exist_ok=True)
    for k in ['sara', 'castro', 'jing', 'wang', 'afp', 'indio']:
        character_sheet(k, os.path.join(out, f'{k}.png'))
        print('sheet', k)
