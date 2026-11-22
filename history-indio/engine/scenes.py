"""Scenes for "Isang Hinliliit Lang" (History Indio).  Pure functions of
(ctx, t, f, talk) where t = 0..1 progress inside the shot, f = global frame,
talk = narrator voice envelope 0..1 (drives the on-screen speaker's mouth)."""
import math
import cairo
from cast import draw_char, hexc, ellipse, rrect, fill_stroke, INK, LW

W, H = 1080, 1920
FONT = 'DejaVu Sans'


# ------------------------------------------------------------ easing
def ss(x):
    x = max(0.0, min(1.0, x))
    return x * x * x * (x * (x * 6 - 15) + 10)


def back(x, k=1.7):
    x = max(0.0, min(1.0, x)) - 1
    return 1 + x * x * ((k + 1) * x + k)


def blink(f, seed):
    return 1.0 if (f + seed * 41) % 113 < 3 else 0.0


def bob(f, seed, amp=8):
    return amp * (0.5 + 0.5 * math.sin((f + seed * 17) * 0.16))


# ------------------------------------------------------------ painting helpers
def vgrad(ctx, y0, y1, c0, c1, x0=-2000, x1=4000):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *hexc(c0))
    g.add_color_stop_rgb(1, *hexc(c1))
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.set_source(g)
    ctx.fill()


def sky_day(ctx, f):
    vgrad(ctx, -800, 1300, '#6fb6e8', '#cfe9f7')
    clouds(ctx, f)


def sky_night(ctx, f):
    vgrad(ctx, -800, 1300, '#0e1838', '#2b3d72')
    ctx.set_source_rgb(1, 1, 0.85)
    for i in range(40):
        x = (i * 263) % 1400 - 160
        y = (i * 151) % 900 - 300
        r = 2 + (i % 3)
        a = 0.5 + 0.5 * math.sin(f * 0.1 + i)
        ctx.set_source_rgba(1, 1, 0.85, 0.4 + 0.6 * a)
        ellipse(ctx, x, y, r, r)
        ctx.fill()
    ellipse(ctx, 820, 180, 70, 70)
    ctx.set_source_rgb(*hexc('#f7f3d8'))
    ctx.fill()


def clouds(ctx, f, n=4, y=180):
    for i in range(n):
        x = ((i * 420 + f * (0.6 + 0.2 * i)) % 1700) - 300
        yy = y + (i % 2) * 140
        ctx.set_source_rgba(1, 1, 1, 0.95)
        for dx, dy, r in ((0, 0, 60), (55, -25, 70), (115, 0, 55), (55, 15, 60)):
            ellipse(ctx, x + dx, yy + dy, r * 1.2, r)
            ctx.fill()


def hills(ctx, y=1150, c1='#7cc35a', c2='#5aa543'):
    ctx.set_source_rgb(*hexc(c1))
    ellipse(ctx, 200, y + 120, 700, 260)
    ctx.fill()
    ctx.set_source_rgb(*hexc(c2))
    ellipse(ctx, 950, y + 160, 760, 280)
    ctx.fill()


def ground(ctx, y, col, col2=None):
    ctx.rectangle(-2000, y, 6000, 3000)
    ctx.set_source_rgb(*hexc(col))
    ctx.fill()
    if col2:
        ctx.set_source_rgba(*hexc(col2), 0.5)
        for i in range(-10, 30):
            ctx.rectangle(i * 120, y, 4, 3000)
            ctx.fill()


def room(ctx, wall='#8a5a5a', floor='#c9a77a', wy=1350):
    vgrad(ctx, -800, wy, wall, _mix(wall, '#000000', 0.25))
    ground(ctx, wy, floor, '#a8875c')
    ctx.rectangle(-2000, wy - 14, 6000, 14)
    ctx.set_source_rgb(*hexc('#5b3a3a'))
    ctx.fill()


def _mix(a, b, k):
    a, b = hexc(a), hexc(b)
    return tuple(a[i] * (1 - k) + b[i] * k for i in range(3))


def text(ctx, s, x, y, size, col='#3b1f3a', center=True, bold=True, rot=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    e = ctx.text_extents(s)
    ctx.move_to(-e.width / 2 - e.x_bearing if center else 0, e.height / 2)
    ctx.set_source_rgb(*hexc(col))
    ctx.show_text(s)
    ctx.restore()


def sign(ctx, s, x, y, w, h, bg='#fff6dc', fg='#3b1f3a', size=56, rot=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    rrect(ctx, -w / 2, -h / 2, w, h, 18)
    fill_stroke(ctx, bg)
    text(ctx, s, 0, 0, size, fg)
    ctx.restore()


def calendar(ctx, x, y, month, day, s=1.0, rot=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    rrect(ctx, -130, -150, 260, 300, 20)
    fill_stroke(ctx, '#ffffff')
    ctx.rectangle(-130, -150, 260, 80)
    ctx.set_source_rgb(*hexc('#d8433b'))
    ctx.fill()
    rrect(ctx, -130, -150, 260, 300, 20)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(LW)
    ctx.stroke()
    text(ctx, month, 0, -110, 46, '#ffffff')
    text(ctx, str(day), 0, 30, 130)
    ctx.restore()


def podium(ctx, x, y, col='#6b3f2a', label=None):
    ctx.move_to(x - 150, y - 330)
    ctx.line_to(x + 150, y - 330)
    ctx.line_to(x + 120, y)
    ctx.line_to(x - 120, y)
    ctx.close_path()
    fill_stroke(ctx, col)
    rrect(ctx, x - 170, y - 360, 340, 50, 12)
    fill_stroke(ctx, _hex(_mix(col, '#000000', 0.2)))
    if label:
        ellipse(ctx, x, y - 200, 70, 70)
        fill_stroke(ctx, '#e9c46a')
        text(ctx, label, x, y - 200, 34)
    # mic
    ctx.set_line_width(8)
    ctx.set_source_rgb(*INK)
    ctx.move_to(x + 40, y - 360)
    ctx.line_to(x + 70, y - 430)
    ctx.stroke()
    ellipse(ctx, x + 72, y - 440, 16, 20)
    fill_stroke(ctx, '#333333', 6)


def _hex(c):
    return '#%02x%02x%02x' % tuple(int(v * 255) for v in c)


def phone(ctx, x, y, w, h, rot=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    rrect(ctx, -w / 2, -h / 2, w, h, 50)
    fill_stroke(ctx, '#22222b')
    rrect(ctx, -w / 2 + 22, -h / 2 + 60, w - 44, h - 120, 20)
    ctx.set_source_rgb(*hexc('#f4f6fb'))
    ctx.fill()
    ctx.restore()


def bubble(ctx, x, y, w, h, tail=(0, 120), col='#ffffff'):
    rrect(ctx, x - w / 2, y - h / 2, w, h, 40)
    ctx.move_to(x - 30, y + h / 2 - 4)
    ctx.line_to(x + tail[0], y + h / 2 + tail[1])
    ctx.line_to(x + 30, y + h / 2 - 4)
    fill_stroke(ctx, col)


def fist_icon(ctx, x, y, s, col='#e2b48c'):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -60, -10, 120, 160, 30)  # wrist
    fill_stroke(ctx, '#3a3a40')
    rrect(ctx, -90, -120, 180, 150, 50)
    fill_stroke(ctx, col)
    ctx.set_line_width(7)
    ctx.set_source_rgb(*INK)
    for i in (-1, 0, 1):
        ctx.move_to(-20 + i * 45, -118)
        ctx.line_to(-20 + i * 45, -60)
    ctx.stroke()
    rrect(ctx, -100, -70, 70, 50, 24)
    fill_stroke(ctx, col, 7)
    ctx.restore()


def pinky_icon(ctx, x, y, s, col='#c98e66'):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -60, 20, 120, 140, 30)
    fill_stroke(ctx, '#2f6b3a')
    rrect(ctx, 30, -200, 44, 160, 22)  # the pinky
    fill_stroke(ctx, col)
    rrect(ctx, -85, -70, 170, 120, 45)
    fill_stroke(ctx, col)
    ctx.set_line_width(7)
    ctx.set_source_rgb(*INK)
    for i in (0, 1, 2):
        ctx.move_to(-55 + i * 35, -68)
        ctx.line_to(-55 + i * 35, -20)
    ctx.stroke()
    ctx.restore()


def flag_ph(ctx, x, y, w, h):
    ctx.rectangle(x, y, w, h / 2)
    ctx.set_source_rgb(*hexc('#0038a8'))
    ctx.fill()
    ctx.rectangle(x, y + h / 2, w, h / 2)
    ctx.set_source_rgb(*hexc('#ce1126'))
    ctx.fill()
    ctx.move_to(x, y)
    ctx.line_to(x + h * 0.86, y + h / 2)
    ctx.line_to(x, y + h)
    ctx.close_path()
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()
    ellipse(ctx, x + h * 0.3, y + h / 2, h * 0.1, h * 0.1)
    ctx.set_source_rgb(*hexc('#fcd116'))
    ctx.fill()
    ctx.rectangle(x, y, w, h)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(6)
    ctx.stroke()


def sea(ctx, f, y=1100, col='#2f7fc1'):
    vgrad(ctx, y, 2600, col, '#173f6b')
    ctx.set_source_rgba(1, 1, 1, 0.5)
    ctx.set_line_width(6)
    for row in range(8):
        yy = y + 40 + row * 110
        for i in range(-2, 12):
            x = i * 140 + ((f * (1.5 + row * 0.3)) % 140) - (row % 2) * 70
            ctx.move_to(x, yy)
            ctx.curve_to(x + 25, yy - 18, x + 45, yy - 18, x + 70, yy)
        ctx.stroke()


def ship(ctx, x, y, s, hull='#8d99a6', big=True, flag=None, f=0):
    ctx.save()
    ctx.translate(x, y + 6 * math.sin(f * 0.08 + x))
    ctx.scale(s, s)
    ctx.move_to(-300, -80)
    ctx.line_to(300, -80)
    ctx.line_to(240, 40)
    ctx.line_to(-240, 40)
    ctx.close_path()
    fill_stroke(ctx, hull)
    rrect(ctx, -150, -190, 260, 115, 14)
    fill_stroke(ctx, '#e8eef2')
    for i in range(4):
        rrect(ctx, -125 + i * 60, -165, 36, 30, 8)
        fill_stroke(ctx, '#7fc4e8', 5)
    if big:
        rrect(ctx, -60, -290, 110, 105, 12)
        fill_stroke(ctx, '#e8eef2')
    ctx.set_line_width(8)
    ctx.move_to(170, -80)
    ctx.line_to(170, -300)
    ctx.set_source_rgb(*INK)
    ctx.stroke()
    if flag == 'ph':
        flag_ph(ctx, 172, -300, 110, 66)
    ctx.restore()


def stamp(ctx, s, x, y, t, col='#d8433b', size=86, rot=-0.18):
    if t <= 0:
        return
    k = back(min(1, t * 3))
    sc = 2.2 - 1.2 * k
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(sc, sc)
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    e = ctx.text_extents(s)
    w, h = e.width + 70, e.height + 60
    rrect(ctx, -w / 2, -h / 2, w, h, 14)
    ctx.set_source_rgba(*hexc(col), min(1, t * 3))
    ctx.set_line_width(12)
    ctx.stroke()
    ctx.move_to(-e.width / 2 - e.x_bearing, e.height / 2)
    ctx.show_text(s)
    ctx.restore()


def check(ctx, x, y, s, col='#2e9e5b'):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_width(22)
    ctx.set_source_rgb(*hexc(col))
    ctx.move_to(-40, 0)
    ctx.line_to(-10, 32)
    ctx.line_to(48, -36)
    ctx.stroke()
    ctx.restore()


def qmark(ctx, x, y, s, col='#f2b33d'):
    text(ctx, '?', x, y, 140 * s, col)


def crowd(ctx, f, y, n=7, s=0.42, x0=60, dx=150, cheer=0.0):
    keys = ['ofw1', 'ofw2', 'ofw3']
    for i in range(n):
        k = keys[i % 3]
        x = x0 + i * dx + (i % 2) * 20
        yy = y + (i % 2) * 40
        arm = 'wave' if cheer > 0 and (i + f // 8) % 3 == 0 else 'down'
        draw_char(ctx, k, x, yy, s, view='q' if i % 2 else 'front', facing=-1 if i > n / 2 else 1,
                  expr='happy' if cheer else 'neutral', blink=blink(f, i), bob=bob(f, i, 6),
                  arms=(arm, 'down'))


def skyline(ctx, f, y, night=True):
    cols = ['#24305a', '#2d3a6b', '#1c264a'] if night else ['#9fb4c9', '#b6c7d8', '#8aa1b8']
    xs = [(-40, 380, 120), (80, 520, 140), (230, 300, 110), (340, 640, 150), (500, 420, 120),
          (610, 560, 130), (740, 360, 120), (860, 700, 140), (990, 450, 130)]
    for i, (x, h, w) in enumerate(xs):
        ctx.rectangle(x, y - h, w, h)
        ctx.set_source_rgb(*hexc(cols[i % 3]))
        ctx.fill()
        if night:
            for r in range(int(h / 50)):
                for c in range(int(w / 40)):
                    if (r * 7 + c * 3 + i) % 4 == 0:
                        ctx.rectangle(x + 12 + c * 38, y - h + 20 + r * 50, 16, 22)
                        ctx.set_source_rgba(1, 0.86, 0.45, 0.85)
                        ctx.fill()


# ------------------------------------------------------------ the scenes
def sc_hook(ctx, t, f, talk, P):
    vgrad(ctx, -800, 2600, '#26334f', '#0f1526')
    # spotlight
    g = cairo.RadialGradient(540, 900, 50, 540, 900, 700)
    g.add_color_stop_rgba(0, 1, 0.95, 0.7, 0.5)
    g.add_color_stop_rgba(1, 1, 0.95, 0.7, 0)
    ctx.set_source(g)
    ctx.paint()
    k = back(min(1, t * 2.2))
    pinky_icon(ctx, 540, 1150 - 120 * k, 2.6 * k + 0.01)
    for i in range(6):  # sparkle lines
        a = i / 6 * math.pi * 2 + f * 0.02
        r0, r1 = 520, 600 + 30 * math.sin(f * 0.3 + i)
        ctx.move_to(540 + r0 * math.cos(a), 900 + r0 * math.sin(a))
        ctx.line_to(540 + r1 * math.cos(a), 900 + r1 * math.sin(a))
    ctx.set_source_rgba(1, 0.9, 0.5, 0.8)
    ctx.set_line_width(10)
    ctx.stroke()


def sc_reactions(ctx, t, f, talk, P):
    vgrad(ctx, -800, 2600, '#fbf3e4', '#f1dfc2')
    panels = [(0.0, 'palace'), (0.33, 'afp'), (0.66, 'net')]
    for i, (t0, kind) in enumerate(panels):
        k = back(min(1, max(0, (t - t0) * 3.5)))
        if k <= 0:
            continue
        y = 330 + i * 600
        ctx.save()
        ctx.translate(540, y)
        ctx.scale(k, k)
        rrect(ctx, -460, -260, 920, 520, 30)
        fill_stroke(ctx, ['#f7e7c6', '#dfe8cf', '#dfe6f5'][i])
        if kind == 'palace':
            draw_char(ctx, 'castro', -250, 230, 0.42, expr='surprised', blink=blink(f, 2), arms=('up', 'up'))
            palace_bldg(ctx, 150, 200, 0.55)
        elif kind == 'afp':
            draw_char(ctx, 'afp', -250, 230, 0.42, expr='surprised', blink=blink(f, 3), arms=('hip', 'hip'))
            ship(ctx, 180, 120, 0.5, hull='#dfe6ea', big=False, flag='ph', f=f)
        else:
            phone(ctx, -230, 0, 220, 430)
            for j in range(4):
                bubble(ctx, 150 + (j % 2) * 120, -150 + j * 90, 200, 60, tail=(0, 0), col=['#ffd34d', '#ff8a80', '#a5d6a7', '#90caf9'][j])
        ctx.restore()


def palace_bldg(ctx, x, y, s):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.rectangle(-300, -300, 600, 300)
    fill_stroke(ctx, '#f4efe3')
    ctx.move_to(-340, -300)
    ctx.line_to(0, -440)
    ctx.line_to(340, -300)
    ctx.close_path()
    fill_stroke(ctx, '#e9e1cf')
    for i in range(6):
        ctx.rectangle(-260 + i * 100, -270, 40, 270)
        fill_stroke(ctx, '#ffffff', 6)
    rrect(ctx, -60, -150, 120, 150, 50)
    fill_stroke(ctx, '#6b3f2a')
    ctx.restore()


def sc_host(ctx, t, f, talk, P):
    sky_day(ctx, f)
    hills(ctx, 1150)
    ground(ctx, 1350, '#d8b98a', '#b89a6a')
    # sari-sari table + tea
    rrect(ctx, 520, 1180, 460, 60, 10)
    fill_stroke(ctx, '#8a5a3a')
    for lx in (560, 940):
        ctx.rectangle(lx, 1240, 22, 200)
        fill_stroke(ctx, '#6b3f2a', 6)
    for i in range(3):
        cx = 620 + i * 130
        ellipse(ctx, cx, 1150, 45, 18)
        fill_stroke(ctx, '#ffffff', 6)
        rrect(ctx, cx - 45, 1080, 90, 75, 20)
        fill_stroke(ctx, '#ffffff', 6)
        # steam
        ctx.set_source_rgba(1, 1, 1, 0.8)
        ctx.set_line_width(6)
        for s_ in range(2):
            yy = 1060 - ((f * 2 + s_ * 30 + i * 11) % 60)
            ctx.move_to(cx - 10 + s_ * 20, yy)
            ctx.curve_to(cx + 10, yy - 20, cx - 20, yy - 30, cx + s_ * 10, yy - 50)
        ctx.stroke()
    draw_char(ctx, 'indio', 300, 1500, 0.95, view='q', expr='happy' if t > 0.6 else 'talk',
              talk=talk, blink=blink(f, 5), bob=bob(f, 5), arms=('wave', 'down'))


def sc_hk_wide(ctx, t, f, talk, P):
    sky_night(ctx, f)
    skyline(ctx, f, 1150, True)
    sea(ctx, f, 1150, '#1d3d74')
    calendar(ctx, 780, 1500, 'NOV', 8, 1.0 * back(min(1, t * 2.5)), rot=0.08)
    sign(ctx, 'HONG KONG', 330, 1480, 460, 110, '#ffd34d', size=58, rot=-0.04)


def sc_hk_stage(ctx, t, f, talk, P):
    room(ctx, '#5b3f6e', '#8a6a4a', 1250)
    # banner
    rrect(ctx, 120, 160, 840, 170, 20)
    fill_stroke(ctx, '#2f6b3a')
    text(ctx, 'OFW FORUM · HONG KONG', 540, 245, 52, '#fff6dc')
    # stage
    rrect(ctx, 60, 1180, 960, 90, 10)
    fill_stroke(ctx, '#a0522d')
    podium(ctx, 640, 1185, '#5a3a2a')
    draw_char(ctx, 'sara', 430, 1185, 0.82, view='q', expr='talk', talk=talk, blink=blink(f, 1),
              bob=bob(f, 1, 4), arms=('point' if P.get('point') and t > 0.4 else 'down', 'down'))
    if P.get('thought') and t > 0.35:
        k = back(min(1, (t - 0.35) * 3))
        ctx.save()
        ctx.translate(760, 560)
        ctx.scale(k, k)
        ellipse(ctx, 0, 0, 230, 160)
        fill_stroke(ctx, '#ffffff')
        ctx.save()
        ellipse(ctx, 0, 0, 220, 150)
        ctx.clip()
        sea(ctx, f, -60)
        ship(ctx, 0, 40, 0.35, flag='ph', big=False, f=f)
        ctx.restore()
        ctx.restore()
    crowd(ctx, f, 1650, n=7, s=0.4, cheer=0.0)
    crowd(ctx, f + 30, 1900, n=6, s=0.45, x0=120, dx=170)


def sc_newspaper(ctx, t, f, talk, P):
    vgrad(ctx, -800, 2600, '#e9dcc4', '#d4c2a2')
    ctx.save()
    ctx.translate(540, 960)
    ctx.rotate(-0.06 + 0.04 * ss(t))
    sc = 0.9 + 0.12 * ss(t)
    ctx.scale(sc, sc)
    rrect(ctx, -420, -620, 840, 1240, 8)
    fill_stroke(ctx, '#fbf8f0')
    text(ctx, P.get('mast', 'ULAT NG DIYARYO'), 0, -540, 64)
    ctx.rectangle(-380, -490, 760, 6)
    ctx.set_source_rgb(*INK)
    ctx.fill()
    text(ctx, P.get('head', 'VP SA HONG KONG'), 0, -410, 70, '#a3282b')
    # photo box with mini sara
    rrect(ctx, -360, -330, 720, 520, 10)
    fill_stroke(ctx, '#dfe6ee', 6)
    ctx.save()
    rrect(ctx, -360, -330, 720, 520, 10)
    ctx.clip()
    draw_char(ctx, 'sara', 0, 380, 0.7, expr='talk', talk=talk, blink=blink(f, 1), arms=(P.get('arm', 'down'), 'down'))
    ctx.restore()
    ctx.set_source_rgba(*INK, 0.35)
    for i in range(7):
        ctx.rectangle(-360, 240 + i * 50, 720 - (i % 3) * 120, 18)
        ctx.fill()
    ctx.restore()
    # magnifier
    mx = 760 - 200 * ss(t)
    ellipse(ctx, mx, 1300, 120, 120)
    ctx.set_source_rgba(0.8, 0.9, 1, 0.35)
    ctx.fill_preserve()
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(16)
    ctx.stroke()
    ctx.move_to(mx + 85, 1385)
    ctx.line_to(mx + 200, 1500)
    ctx.set_line_width(30)
    ctx.stroke()


def sc_sara_close(ctx, t, f, talk, P):
    room(ctx, '#5b3f6e', '#8a6a4a', 1700)
    rrect(ctx, 120, 160, 840, 170, 20)
    fill_stroke(ctx, '#2f6b3a')
    text(ctx, 'OFW FORUM · HONG KONG', 540, 245, 52, '#fff6dc')
    arm = P.get('arm', 'down')
    k = back(min(1, t * 3)) if arm in ('pinky', 'fist') else 1
    draw_char(ctx, 'sara', 540, 2250, 1.7, view='front', expr=P.get('expr', 'talk'), talk=talk,
              blink=blink(f, 1), bob=bob(f, 1, 5), arms=(arm if k > 0.3 else 'down', 'down'),
              tilt=0.04 * math.sin(f * 0.08))
    if arm == 'pinky':
        flag_ph(ctx, 80, 420, 220 * k, 132 * k)
        text(ctx, 'PILIPINAS', 190, 600, 44)
    if arm == 'fist':
        ctx.set_source_rgba(0.85, 0.15, 0.15, 0.25 * k)
        ctx.paint()
        text(ctx, 'CHINA', 860, 520, 64, '#a3282b')


def sc_no_fight(ctx, t, f, talk, P):
    vgrad(ctx, -800, 2600, '#e7f0f7', '#cfe0ee')
    # phone with angry comments
    phone(ctx, 300, 650, 420, 760, -0.06)
    for j in range(4):
        bubble(ctx, 300, 430 + j * 140, 300, 90, tail=(0, 0), col='#ff8a80')
        text(ctx, '>:(', 300, 430 + j * 140, 50)
    # sea clash
    ctx.save()
    rrect(ctx, 560, 300, 460, 700, 30)
    ctx.clip()
    vgrad(ctx, 300, 700, '#9ed0f2', '#d8eefc', 560, 1020)
    sea(ctx, f, 700)
    ship(ctx, 700, 760, 0.3, big=False, flag='ph', f=f)
    ship(ctx, 900, 720, 0.45, hull='#c7ced6', f=f)
    ctx.restore()
    rrect(ctx, 560, 300, 460, 700, 30)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(LW)
    ctx.stroke()
    # X marks
    for cx, cy, t0 in ((300, 650, 0.25), (790, 650, 0.5)):
        k = back(min(1, max(0, (t - t0) * 4)))
        if k > 0:
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.set_line_width(40 * k)
            ctx.set_source_rgba(0.85, 0.2, 0.2, 0.9)
            r = 230 * k
            ctx.move_to(cx - r, cy - r)
            ctx.line_to(cx + r, cy + r)
            ctx.move_to(cx + r, cy - r)
            ctx.line_to(cx - r, cy + r)
            ctx.stroke()
    draw_char(ctx, 'sara', 540, 1850, 0.75, view='front', expr='talk', talk=talk, blink=blink(f, 1),
              bob=bob(f, 1), arms=('shrug', 'shrug'))


def sc_negotiate(ctx, t, f, talk, P):
    room(ctx, '#3f5b7a', '#b59a74', 1150)
    # long table
    rrect(ctx, 60, 1250, 960, 90, 14)
    fill_stroke(ctx, '#7a4a2e')
    for i, k in enumerate(['ofw3', 'ofw2', 'ofw1']):
        draw_char(ctx, k, 170 + i * 130, 1300, 0.55, view='q', facing=1, expr='neutral',
                  blink=blink(f, i), bob=bob(f, i, 4), arms=('podium', 'podium'), show_tag=False)
    draw_char(ctx, 'jing', 870, 1300, 0.6, view='q', facing=-1, expr='neutral', blink=blink(f, 9),
              bob=bob(f, 9, 4), arms=('podium', 'podium'))
    # papers + handshake sparkle
    rrect(ctx, 420, 1200, 200, 60, 6)
    fill_stroke(ctx, '#ffffff', 6)
    sign(ctx, 'DIPLOMASYA', 540, 380, 640, 150, '#ffd34d', size=80, rot=-0.03)
    k = back(min(1, t * 2))
    ellipse(ctx, 540, 760, 160 * k, 160 * k)
    fill_stroke(ctx, '#fff6dc')
    text(ctx, '🤝' if False else 'USAP', 540, 760, 70 * max(k, 0.01))


def sc_livelihood(ctx, t, f, talk, P):
    sky_day(ctx, f)
    hills(ctx, 1100, '#8fcf6b', '#6ab64e')
    ground(ctx, 1300, '#d8b98a')
    # balikbayan boxes
    for i in range(3):
        rrect(ctx, 100 + i * 120, 1320 - i * 10, 160, 120, 6)
        fill_stroke(ctx, '#c8a26b')
        text(ctx, 'BALIKBAYAN', 180 + i * 120, 1380 - i * 10, 20)
    crowd(ctx, f, 1650, n=5, s=0.6, x0=180, dx=190)
    # crack across the sky (relationship)
    k = ss(min(1, t * 1.6))
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(14)
    pts = [(80, 520), (260, 600), (380, 520), (540, 640), (700, 540), (860, 620), (1000, 560)]
    n = max(1, int(len(pts) * k))
    ctx.move_to(*pts[0])
    for p in pts[1:n]:
        ctx.line_to(*p)
    ctx.stroke()
    sign(ctx, 'KABUHAYAN', 540, 300, 560, 130, '#fff6dc', size=70)


def sc_thermo(ctx, t, f, talk, P):
    vgrad(ctx, -800, 2600, '#ffd3a1', '#ff8d6b')
    k = ss(t)
    rrect(ctx, 720, 300, 120, 1000, 60)
    fill_stroke(ctx, '#ffffff')
    ellipse(ctx, 780, 1330, 120, 120)
    fill_stroke(ctx, '#e53935')
    rrect(ctx, 745, 1300 - 900 * k, 70, 900 * k + 20, 35)
    ctx.set_source_rgb(*hexc('#e53935'))
    ctx.fill()
    draw_char(ctx, 'indio', 340, 1650, 0.95, view='q', expr='surprised', talk=talk, blink=blink(f, 5),
              bob=bob(f, 5), arms=('hip', 'down'))
    # sweat drops
    for i in range(3):
        y = 760 + ((f * 6 + i * 40) % 120)
        ellipse(ctx, 200 + i * 90, y, 14, 22)
        fill_stroke(ctx, '#8fd3ff', 5)


def sc_clock(ctx, t, f, talk, P):
    vgrad(ctx, -800, 2600, '#fbf3e4', '#f1dfc2')
    ellipse(ctx, 540, 700, 330, 330)
    fill_stroke(ctx, '#ffffff')
    ctx.set_source_rgb(*INK)
    for i in range(12):
        a = i / 12 * 2 * math.pi
        ctx.move_to(540 + 270 * math.cos(a), 700 + 270 * math.sin(a))
        ctx.line_to(540 + 300 * math.cos(a), 700 + 300 * math.sin(a))
    ctx.set_line_width(12)
    ctx.stroke()
    for L, sp, w in ((180, 0.04, 22), (250, 0.5, 12)):
        a = f * sp
        ctx.move_to(540, 700)
        ctx.line_to(540 + L * math.sin(a), 700 - L * math.cos(a))
        ctx.set_line_width(w)
        ctx.stroke()
    draw_char(ctx, 'indio', 540, 1800, 0.9, view='front', expr='smug', talk=talk, blink=blink(f, 5),
              bob=bob(f, 5), arms=('point', 'hip'))


def sc_jing(ctx, t, f, talk, P):
    room(ctx, '#7a2e2e', '#b59a74', 1350)
    podium(ctx, 640, 1500, '#5a2a2a', 'PRESS')
    draw_char(ctx, 'jing', 420, 1500, 0.95, view='q', expr='smug' if P.get('part', 0) else 'talk',
              talk=talk, blink=blink(f, 9), bob=bob(f, 9, 4), arms=('fist' if P.get('part', 0) else 'point', 'down'))
    calendar(ctx, 820, 420, 'OCT', 15, back(min(1, t * 3)), rot=0.07)
    if P.get('part', 0):
        k = back(min(1, t * 2.5))
        bubble(ctx, 420, 520, 360 * k + 1, 260 * k + 1, tail=(-20, 150))
        fist_icon(ctx, 420, 560, 0.9 * k + 0.01)


def sc_dfa(ctx, t, f, talk, P):
    room(ctx, '#3f6e5b', '#c9a77a', 1300)
    sign(ctx, 'DFA', 540, 260, 360, 140, '#fff6dc', size=90)
    rrect(ctx, 520, 1260, 480, 70, 10)
    fill_stroke(ctx, '#7a4a2e')
    draw_char(ctx, 'jing', 300, 1550, 0.9, view='q', expr='surprised', blink=blink(f, 9),
              bob=bob(f, 9, 4), arms=('down', 'down'))
    # flying envelope
    k = ss(min(1, t * 1.8))
    ex = 1150 - 700 * k
    ey = 900 - 300 * math.sin(k * math.pi)
    ctx.save()
    ctx.translate(ex, ey)
    ctx.rotate(0.6 * (1 - k))
    rrect(ctx, -140, -90, 280, 180, 10)
    fill_stroke(ctx, '#ffffff')
    ctx.move_to(-140, -90)
    ctx.line_to(0, 10)
    ctx.line_to(140, -90)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(7)
    ctx.stroke()
    ellipse(ctx, 0, 30, 30, 30)
    fill_stroke(ctx, '#d8433b', 6)
    ctx.restore()
    if t > 0.6:
        text(ctx, 'IPINATAWAG', 540, 520, 76, '#a3282b', rot=-0.05)


def sc_wang(ctx, t, f, talk, P):
    if P.get('part', 0) == 0:
        # split screen phone call
        vgrad(ctx, -800, 960, '#7a2e2e', '#5a1f1f')
        vgrad(ctx, 960, 2600, '#2e4f7a', '#1f3557')
        draw_char(ctx, 'wang', 380, 900, 0.75, view='q', expr='talk', talk=talk, blink=blink(f, 7),
                  bob=bob(f, 7, 4), arms=('phone', 'down'))
        calendar(ctx, 820, 330, 'NOV', 3, back(min(1, t * 3)), rot=0.06)
        sign(ctx, 'DFA · MANILA', 700, 1180, 420, 100, '#fff6dc', size=46)
        # phone handset on Manila side
        ctx.save()
        ctx.translate(380, 1650)
        rrect(ctx, -160, -60, 320, 120, 50)
        fill_stroke(ctx, '#22222b')
        ctx.restore()
        ctx.set_source_rgba(1, 1, 1, 0.7)
        ctx.set_line_width(8)
        for i in range(3):
            r = 60 + i * 50 + (f * 3) % 50
            ctx.arc(380, 1650, r, -2.4, -0.7)
            ctx.stroke()
        ctx.rectangle(-100, 952, 1400, 16)
        ctx.set_source_rgb(*INK)
        ctx.fill()
    else:
        # red line on the ground, faceless politicians tiptoe over it
        sky_day(ctx, f)
        ground(ctx, 900, '#e9dcc4')
        ctx.set_source_rgb(*hexc('#d8433b'))
        ctx.rectangle(-100, 1260, 1400, 46)
        ctx.fill()
        text(ctx, 'RED LINE', 540, 1360, 50, '#d8433b')
        for i in range(3):
            x = 220 + i * 320
            ctx.save()
            ctx.translate(x, 1240 - (0 if i != 1 else 30 * abs(math.sin(f * 0.15))))
            # anonymous silhouette (no one named)
            ellipse(ctx, 0, -330, 90, 90)
            fill_stroke(ctx, '#4b4b58')
            ctx.move_to(-80, -230)
            ctx.curve_to(-100, -60, 100, -60, 80, -230)
            ctx.close_path()
            fill_stroke(ctx, '#4b4b58')
            text(ctx, '?', 0, -330, 90, '#ffffff')
            ctx.restore()
        k = back(min(1, t * 2))
        bubble(ctx, 540, 450, 640 * k + 1, 220 * k + 1, tail=(0, 120))
        text(ctx, 'PIGILAN!', 540, 450, 90 * k + 1, '#a3282b')


def sc_echo(ctx, t, f, talk, P):
    vgrad(ctx, -800, 2600, '#1c2440', '#38295a')
    draw_char(ctx, 'sara', 280, 1500, 0.75, view='q', expr='neutral', blink=blink(f, 1),
              bob=bob(f, 1, 4), arms=('fist', 'down'))
    draw_char(ctx, 'jing', 820, 1500, 0.75, view='q', facing=-1, expr='smug', blink=blink(f, 9),
              bob=bob(f, 9, 4), arms=('fist', 'down'))
    ctx.set_line_width(10)
    for i in range(5):
        ph = ((f * 0.02 + i / 5) % 1)
        ctx.set_source_rgba(1, 0.85, 0.4, 1 - ph)
        ctx.arc(820, 820, 80 + ph * 520, math.pi * 0.75, math.pi * 1.25)
        ctx.stroke()
    text(ctx, 'ECHO?', 540, 400, 120, '#ffd34d')


def sc_comments(ctx, t, f, talk, P):
    vgrad(ctx, -800, 2600, '#ffe7a3', '#ffb86b')
    phone(ctx, 540, 1000, 640, 1200)
    cols = ['#ff8a80', '#a5d6a7', '#90caf9', '#ffd34d', '#ce93d8', '#ffab91']
    faces = ['!!', '??', ':O', '>:(', 'LOL', '...']
    for j in range(12):
        t0 = j * 0.06
        k = back(min(1, max(0, (t - t0) * 6)))
        if k <= 0:
            continue
        ang = j * 2.4
        r = 120 + 360 * k
        x = 540 + r * math.cos(ang)
        y = 1000 + r * math.sin(ang) * 1.3
        bubble(ctx, x, y, 200 * k + 1, 90 * k + 1, tail=(0, 0), col=cols[j % 6])
        text(ctx, faces[j % 6], x, y, 46 * k + 1)
    # boom
    if t < 0.25:
        k = t / 0.25
        ctx.set_source_rgba(1, 1, 1, 0.8 * (1 - k))
        ellipse(ctx, 540, 1000, 900 * k + 1, 900 * k + 1)
        ctx.fill()


def sc_palace_ext(ctx, t, f, talk, P):
    sky_day(ctx, f)
    ground(ctx, 1300, '#9ccc65')
    palace_bldg(ctx, 540, 1330, 1.35)
    calendar(ctx, 840, 1650, 'NOV', 10, back(min(1, t * 3)), rot=0.07)
    for i in range(3):  # trees
        x = [90, 990, 160][i]
        ellipse(ctx, x, 1180, 90, 120)
        fill_stroke(ctx, '#4f9b3c')


def sc_castro(ctx, t, f, talk, P):
    room(ctx, '#2f3f63', '#b59a74', 1350)
    rrect(ctx, 140, 200, 800, 300, 20)
    fill_stroke(ctx, '#e9e1cf')
    palace_bldg(ctx, 540, 470, 0.55)
    podium(ctx, 610, 1550, '#4a3020', 'PCO')
    part = P.get('part', 0)
    draw_char(ctx, 'castro', 400, 1550, 0.95, view='q', expr='angry' if part else 'talk', talk=talk,
              blink=blink(f, 2), bob=bob(f, 2, 4), arms=('point', 'down'))
    if part:
        k = back(min(1, t * 2.5))
        ctx.save()
        ctx.translate(860, 820)
        ctx.scale(0.5 * k + 0.01, 0.5 * k + 0.01)
        pinky_icon(ctx, 0, 0, 1.0)
        ctx.restore()
        text(ctx, '"MINAMALIIT"', 700, 620, 56, '#a3282b')


def sc_manchurian(ctx, t, f, talk, P):
    vgrad(ctx, -800, 2600, '#2c2c3a', '#1b1b25')
    # spotlight on row of anonymous silhouettes
    for i in range(4):
        x = 170 + i * 250
        g = cairo.RadialGradient(x, 1100, 20, x, 1100, 260)
        g.add_color_stop_rgba(0, 1, 1, 0.8, 0.35)
        g.add_color_stop_rgba(1, 1, 1, 0.8, 0)
        ctx.set_source(g)
        ctx.paint()
        ellipse(ctx, x, 950, 90, 90)
        fill_stroke(ctx, '#4b4b58')
        ctx.move_to(x - 90, 1060)
        ctx.curve_to(x - 110, 1300, x + 110, 1300, x + 90, 1060)
        ctx.close_path()
        fill_stroke(ctx, '#4b4b58')
        qmark(ctx, x, 950 - 10 * math.sin(f * 0.2 + i), 0.7, '#ffd34d')
    sign(ctx, '"MANCHURIAN CANDIDATE"?', 540, 420, 960, 140, '#fff6dc', size=54)
    draw_char(ctx, 'castro', 540, 1850, 0.6, view='front', expr='talk', talk=talk, blink=blink(f, 2),
              bob=bob(f, 2, 4), arms=('point', 'down'))


def sc_noname(ctx, t, f, talk, P):
    vgrad(ctx, -800, 2600, '#fbf3e4', '#f1dfc2')
    draw_char(ctx, 'castro', 540, 1450, 0.95, view='front', expr='neutral', talk=talk,
              blink=blink(f, 2), bob=bob(f, 2, 4), arms=('shrug', 'shrug'))
    for i in range(3):
        sign(ctx, '_____', 220 + i * 320, 1700, 240, 90, '#ffffff', size=50)
    stamp(ctx, 'WALANG PINANGALANAN', 540, 450, max(0, t - 0.2), size=64)


def sc_fakepost(ctx, t, f, talk, P):
    vgrad(ctx, -800, 2600, '#dfe6f5', '#b9c6e6')
    phone(ctx, 540, 960, 760, 1400)
    rrect(ctx, 200, 420, 680, 520, 20)
    fill_stroke(ctx, '#ffffff', 6)
    ellipse(ctx, 270, 490, 40, 40)
    fill_stroke(ctx, '#bbbbbb', 5)
    ctx.set_source_rgba(*INK, 0.4)
    for i in range(5):
        ctx.rectangle(230, 570 + i * 60, 600 - (i % 2) * 140, 22)
        ctx.fill()
    if P.get('part', 0):
        stamp(ctx, 'WALA SA ULAT', 540, 700, t, size=90)
    else:
        text(ctx, 'SHARE?', 540, 1100, 70, '#2e5aa8')


def sc_afp(ctx, t, f, talk, P):
    if P.get('part', 0) == 0:
        room(ctx, '#56663a', '#b59a74', 1350)
        sign(ctx, 'AFP', 540, 300, 300, 140, '#f5d142', size=90)
        podium(ctx, 640, 1550, '#3d4a2a')
        draw_char(ctx, 'afp', 420, 1550, 0.95, view='q', expr='talk', talk=talk, blink=blink(f, 3),
                  bob=bob(f, 3, 4), arms=('down', 'down'), tilt=0.06 * math.sin(f * 0.25))
        check(ctx, 820, 760, 2.2 * back(min(1, t * 2)) + 0.01)
    else:
        sky_day(ctx, f)
        sea(ctx, f, 1000)
        ship(ctx, 540, 1300, 0.9, hull='#f2f4f6', big=False, flag='ph', f=f)
        # shield
        k = back(min(1, t * 2))
        ctx.save()
        ctx.translate(540, 600)
        ctx.scale(k + 0.01, k + 0.01)
        ctx.move_to(0, -200)
        ctx.curve_to(150, -170, 180, -150, 180, -150)
        ctx.curve_to(180, 50, 100, 160, 0, 220)
        ctx.curve_to(-100, 160, -180, 50, -180, -150)
        ctx.curve_to(-180, -150, -150, -170, 0, -200)
        ctx.close_path()
        fill_stroke(ctx, '#2e5aa8')
        text(ctx, 'KARAPATAN', 0, 0, 44, '#ffffff')
        ctx.restore()


def sc_board(ctx, t, f, talk, P):
    room(ctx, '#6e5a4a', '#b59a74', 1500)
    rrect(ctx, 70, 180, 940, 1100, 20)
    fill_stroke(ctx, '#2f4f3a')
    ctx.rectangle(540, 220, 6, 1020)
    ctx.set_source_rgba(1, 1, 1, 0.5)
    ctx.fill()
    text(ctx, 'PROVEN', 300, 290, 64, '#ffffff')
    text(ctx, 'OPINYON', 780, 290, 64, '#ffffff')
    stage = P.get('stage', 0)
    if stage >= 1:
        items = ['NAGSALITA SA HK', 'SUMAGOT PALASYO', 'SUMAGOT AFP']
        for i, s in enumerate(items):
            k = min(1, max(0, (t if stage == 1 else 1) * 3 - i * 0.6))
            if k > 0:
                check(ctx, 140, 470 + i * 160, 0.7 * k)
                text(ctx, s, 330, 470 + i * 160, 34, '#ffffff')
    if stage >= 2:
        for i in range(3):
            k = min(1, max(0, (t if stage == 2 else 1) * 3 - i * 0.6))
            if k > 0:
                qmark(ctx, 700 + (i % 2) * 140, 520 + i * 200, 0.7 * k)
    draw_char(ctx, 'indio', 900, 1900, 0.7, view='q', facing=-1, expr='talk', talk=talk,
              blink=blink(f, 5), bob=bob(f, 5), arms=('point', 'down'))


def sc_scale(ctx, t, f, talk, P):
    vgrad(ctx, -800, 2600, '#fbf3e4', '#f1dfc2')
    a = 0.18 * math.sin(f * 0.07)
    ctx.set_source_rgb(*INK)
    ctx.rectangle(530, 600, 20, 900)
    ctx.fill()
    ctx.save()
    ctx.translate(540, 620)
    ctx.rotate(a)
    ctx.rectangle(-380, -12, 760, 24)
    ctx.fill()
    for sx, lab in ((-1, 'REALISTIC?'), (1, 'MINAMALIIT?')):
        ctx.save()
        ctx.translate(sx * 360, 0)
        ctx.rotate(-a)
        ctx.move_to(0, 0)
        ctx.line_to(-120, 260)
        ctx.move_to(0, 0)
        ctx.line_to(120, 260)
        ctx.set_line_width(6)
        ctx.stroke()
        ellipse(ctx, 0, 270, 150, 40)
        fill_stroke(ctx, '#e9c46a')
        text(ctx, lab, 0, 380, 44)
        ctx.restore()
    ctx.restore()
    rrect(ctx, 400, 1480, 280, 60, 20)
    fill_stroke(ctx, '#6b3f2a')
    if P.get('host'):
        draw_char(ctx, 'indio', 540, 1900, 0.65, view='front', expr='smug', talk=talk, blink=blink(f, 5),
                  bob=bob(f, 5), arms=('shrug', 'shrug'))


def sc_senate(ctx, t, f, talk, P):
    room(ctx, '#5a4a6e', '#8a6a4a', 1250)
    rrect(ctx, 100, 220, 880, 160, 20)
    fill_stroke(ctx, '#e9e1cf')
    text(ctx, 'SENADO · IMPEACHMENT COURT', 540, 300, 40)
    rrect(ctx, 140, 1000, 800, 160, 14)
    fill_stroke(ctx, '#6b3f2a')
    for i in range(5):  # anonymous senator-judges
        x = 220 + i * 160
        ellipse(ctx, x, 940, 60, 60)
        fill_stroke(ctx, '#8d7b6a')
    # gavel
    k = abs(math.sin(f * 0.18))
    ctx.save()
    ctx.translate(540, 900)
    ctx.rotate(-0.6 * k)
    rrect(ctx, -10, -10, 160, 24, 8)
    fill_stroke(ctx, '#7a4a2e')
    rrect(ctx, 130, -45, 60, 90, 14)
    fill_stroke(ctx, '#7a4a2e')
    ctx.restore()
    draw_char(ctx, 'sara', 540, 1800, 0.8, view='front', expr='neutral', blink=blink(f, 1),
              bob=bob(f, 1, 4), arms=('down', 'down'))
    if P.get('stamp'):
        stamp(ctx, 'ALEGASYON PA LANG', 540, 640, t, col='#e07b00', size=64)
        if t > 0.5:
            stamp(ctx, 'WALA PANG HATOL', 540, 1300, (t - 0.5) * 2, col='#2e5aa8', size=60, rot=0.12)


def sc_outro(ctx, t, f, talk, P):
    vgrad(ctx, -800, 2600, '#2f4f7a', '#16253f')
    pinky_icon(ctx, 260, 640, 1.2 + 0.05 * math.sin(f * 0.2))
    fist_icon(ctx, 820, 640, 1.2 + 0.05 * math.cos(f * 0.2))
    text(ctx, 'O', 540, 600, 120, '#ffd34d')
    draw_char(ctx, 'indio', 540, 1750, 0.95, view='front', expr='talk', talk=talk, blink=blink(f, 5),
              bob=bob(f, 5), arms=(P.get('arm', 'point'), 'hip'))
    if P.get('books'):
        for i in range(4):
            rrect(ctx, 760, 1550 - i * 70, 240, 64, 8)
            fill_stroke(ctx, ['#d8433b', '#2e5aa8', '#2e9e5b', '#f2b33d'][i], 6)
        text(ctx, 'SOURCES', 880, 1210, 44, '#ffffff')
        k = back(min(1, t * 2))
        bubble(ctx, 540, 1020, 520 * k + 1, 140 * k + 1, tail=(0, 80))
        text(ctx, 'COMMENT ⬇' if False else 'COMMENT!', 540, 1020, 64 * k + 1)


SCENES = {k[3:]: v for k, v in globals().items() if k.startswith('sc_')}
