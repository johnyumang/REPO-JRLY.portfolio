#!/usr/bin/env python3
"""REAL baybayin for writing inside a picture (the owner, 13 Nov: words nobody can read in a picture should be baybayin, not
machine scribble). An image model cannot write baybayin: it draws false signs. So a picture is drawn with NO writing, and where
a surface needs writing (a sign, a page, a banner, a carved stone, a game-style caption) this tool writes true baybayin on it.

usage (from history-indio/):
  baybayin.py word "<Tagalog words>" [--final virama|pamudpod|drop]      -> the baybayin, and how it reads back sign by sign
  baybayin.py render "<Tagalog words>" <out.png> [--px 160] [--colour 40,26,12] [--final ...]   -> the writing alone, see-through
  baybayin.py paste <in.jpg> <out.jpg> "<Tagalog words>" x1,y1,x2,y2,x3,y3,x4,y4 [--colour r,g,b] [--opacity 0.85] [--rough 1.0] [--carve]
        -> the writing laid on the four-cornered place (corners in pixels: top-left, top-right, bottom-right, bottom-left),
           in perspective, mixed into the paint (multiply), a little worn; a "|" in the words starts a new line;
           --carve = light letters with a dark edge, for stone and metal. LOOK at the result at 3x before you keep it.
  baybayin.py test

How it spells (sound, not letters; Tagalog as written today):
- a sign is a consonant with "a": ba ka da ga ha la ma na nga pa ra sa ta wa ya; a mark above gives e/i, a mark below gives o/u;
  a vowel alone has its own sign (a, e/i, o/u).
- a consonant with NO vowel after it: `virama` (default) writes the sign with the cross mark of 1620 (Fr. Francisco Lopez), the way
  most people who write baybayin today do; `pamudpod` uses the slash mark of the Mangyan; `drop` leaves the consonant out, as the
  old writing before the Spaniards did ("ang" was written "a"): use `drop` for a scene set before about 1600.
- "ng" the word is written na-nga with the mark (nang), "mga" as ma-nga; c/q -> k (c before e,i -> s), f -> p, v -> b, z -> s,
  j -> dy (h in a Spanish name: write it with h yourself), x -> ks, ñ -> ny, ll -> ly, ch -> ts, th -> t, sh -> sy, w and y kept.
- Foreign names come out by sound only. Check the read-back line before you paste.
Honest use: baybayin is right where Filipinos wrote for themselves, and as the series' own mark (titles, the medallion, quest and
skill captions). A Spanish decree, a British order or an American paper was not written in baybayin: leave those as plain ruled
lines with no letters. Font: Noto Sans Tagalog (SIL Open Font License, pipeline/fonts/OFL-NotoSansTagalog.txt)."""
import os, re, sys
FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts', 'NotoSansTagalog-Regular.ttf')
V = {'a': 'ᜀ', 'i': 'ᜁ', 'e': 'ᜁ', 'u': 'ᜂ', 'o': 'ᜂ'}
C = {'k': 'ᜃ', 'g': 'ᜄ', 'ng': 'ᜅ', 't': 'ᜆ', 'd': 'ᜇ', 'n': 'ᜈ', 'p': 'ᜉ', 'b': 'ᜊ', 'm': 'ᜋ',
     'y': 'ᜌ', 'r': 'ᜍ', 'l': 'ᜎ', 'w': 'ᜏ', 's': 'ᜐ', 'h': 'ᜑ'}
KUD = {'a': '', 'i': 'ᜒ', 'e': 'ᜒ', 'u': 'ᜓ', 'o': 'ᜓ'}
END = {'virama': '᜔', 'pamudpod': '᜕', 'drop': None}
NAME = {v: k + 'a' for k, v in C.items()}; NAME.update({'ᜀ': 'a', 'ᜁ': 'e/i', 'ᜂ': 'o/u'})


def _latin(w):
    """Today's Tagalog spelling -> the sounds baybayin has."""
    w = w.lower()
    for a, b in (('ñ', 'ny'), ('ll', 'ly'), ('ch', 'ts'), ('sh', 'sy'), ('th', 't'), ('ph', 'p'), ('qu', 'k'), ('x', 'ks'), ('j', 'dy'), ('f', 'p'), ('v', 'b'), ('z', 's'), ('q', 'k')): w = w.replace(a, b)
    w = re.sub(r'c(?=[ei])', 's', w).replace('c', 'k')
    for a, b in (('á', 'a'), ('à', 'a'), ('â', 'a'), ('é', 'e'), ('è', 'e'), ('ê', 'e'), ('í', 'i'), ('ì', 'i'), ('î', 'i'), ('ó', 'o'), ('ò', 'o'), ('ô', 'o'), ('ú', 'u'), ('ù', 'u'), ('û', 'u')): w = w.replace(a, b)
    return re.sub(r"[^a-z]", '', w)


def word(w, final='virama'):
    s = _latin(w)
    if s == 'ng': s = 'nang'
    if s == 'mga': s = 'manga'
    out, i, end = [], 0, END[final]
    while i < len(s):
        c = 'ng' if s.startswith('ng', i) else s[i]
        if c in V: out.append(V[c]); i += 1; continue
        if c not in C: i += len(c); continue
        j = i + len(c)
        if j < len(s) and s[j] in KUD: out.append(C[c] + KUD[s[j]]); i = j + 1
        else:
            if end: out.append(C[c] + end)
            i = j
    return ''.join(out)


def to_baybayin(text, final='virama'):
    """Words -> baybayin; a comma becomes the single bar, a full stop (and ! ?) the double bar; other marks are left out."""
    out = []
    for tok in re.findall(r"[^\s,.!?;:]+|[,.!?;:]", text):
        if tok in ',;:': out.append('᜵')
        elif tok in '.!?': out.append('᜶')
        else:
            b = word(tok, final)
            if b: out.append(b)
    return ' '.join(out)


def read_back(b):
    """The signs as syllables, so a person who cannot read baybayin can check the spelling."""
    r = []
    for ch in b:
        if ch in NAME: r.append(NAME[ch])
        elif ch == 'ᜒ' and r: r[-1] = r[-1][:-1] + 'i'
        elif ch == 'ᜓ' and r: r[-1] = r[-1][:-1] + 'u'
        elif ch in ('᜔', '᜕') and r: r[-1] = r[-1][:-1]
        elif ch == ' ': r.append('|')
        elif ch == '᜵': r.append(',')
        elif ch == '᜶': r.append('.')
    return ' '.join(r).replace(' | ', '   ')


def render(text, px=160, colour=(40, 26, 12), final='virama', pad=0.18):
    """-> RGBA picture of the writing (see-through around it). Needs Pillow with raqm for the marks to sit right."""
    from PIL import Image, ImageDraw, ImageFont, features
    b = to_baybayin(text, final); f = ImageFont.truetype(FONT, px, layout_engine=ImageFont.Layout.RAQM if features.check('raqm') else ImageFont.Layout.BASIC)
    d = ImageDraw.Draw(Image.new('L', (8, 8))); x0, y0, x1, y1 = d.textbbox((0, 0), b, font=f); p = int(px * pad)
    im = Image.new('RGBA', (x1 - x0 + 2 * p, y1 - y0 + 2 * p), (0, 0, 0, 0)); ImageDraw.Draw(im).text((p - x0, p - y0), b, font=f, fill=tuple(colour) + (255,))
    return im


def paste(src, dst, text, quad, colour=None, opacity=0.85, rough=1.0, carve=False, final='virama'):
    """Lay the writing on the four-cornered place of a picture: in perspective, worn at the edges, mixed into the paint.
    A "|" in the text starts a new line. colour: the ink (default dark brown), or with carve the light of the cut letters (default pale bronze)."""
    import cv2, numpy as np
    im = cv2.imread(src); H, W = im.shape[:2]; q = np.float32(quad).reshape(4, 2); lines = [x.strip() for x in text.split('|') if x.strip()]
    colour = colour or ((236, 208, 150) if carve else (40, 26, 12))
    wq = int(max(np.linalg.norm(q[1] - q[0]), np.linalg.norm(q[2] - q[3]))); hq = int(max(np.linalg.norm(q[3] - q[0]), np.linalg.norm(q[2] - q[1])))
    SS = 3; bw, bh = wq * SS, hq * SS; box = np.zeros((bh, bw), np.float32); lh = bh // len(lines)      # drawn three times larger, then warped down: clean edges
    for k, ln in enumerate(lines):
        a = np.array(render(ln, px=max(24, int(lh * 0.6)), colour=(255, 255, 255), final=final))[..., 3].astype(np.float32) / 255
        ys, xs = np.where(a > 0.05); a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]            # the ink alone, so the line fills its band
        s = min(bw * 0.9 / a.shape[1], lh * 0.72 / a.shape[0]); a = cv2.resize(a, (max(1, int(a.shape[1] * s)), max(1, int(a.shape[0] * s))), interpolation=cv2.INTER_AREA)
        y = k * lh + (lh - a.shape[0]) // 2; x = (bw - a.shape[1]) // 2; box[y:y + a.shape[0], x:x + a.shape[1]] = a
    if rough > 0:                                                           # a hand, not a printer: uneven ink and a soft edge
        rng = np.random.default_rng(len(text) * 7919 + wq); n = cv2.GaussianBlur(rng.random((bh, bw)).astype(np.float32), (0, 0), max(1.0, bh / 40))
        n = (n - n.min()) / (n.max() - n.min() + 1e-6); box = cv2.GaussianBlur(box, (0, 0), SS * (0.5 + 0.3 * rough)) * (1 - 0.4 * rough * n)
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [bw, 0], [bw, bh], [0, bh]]), q); m = cv2.warpPerspective(box, M, (W, H), flags=cv2.INTER_AREA)[..., None]
    f = im.astype(np.float32); c = np.float32(colour[::-1])
    if carve:                                                               # cut letters: a dark edge below and to the right, light inside
        d = max(1, int(round(hq / len(lines) / 28))); sh = np.clip(np.roll(np.roll(m, d, 0), d, 1) - m, 0, 1)
        f = f * (1 - 0.75 * opacity * sh); f = f * (1 - opacity * m) + c * (opacity * m)
    else: f = f * (1 - opacity * m) + f * (c / 255) * (opacity * m)        # multiply: the paint under the ink still shows
    cv2.imwrite(dst, np.clip(f, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 95])
    return ' | '.join(to_baybayin(ln, final) for ln in lines)


def _test():
    t = [('ba', 'ᜊ'), ('mabuhay', 'ᜋᜊᜓᜑᜌ᜔'), ('Pilipinas', 'ᜉᜒᜎᜒᜉᜒᜈᜐ᜔'),
         ('ng', 'ᜈᜅ᜔'), ('mga', 'ᜋᜅ'), ('Indio', 'ᜁᜈ᜔ᜇᜒᜂ'), ('kalayaan', 'ᜃᜎᜌᜀᜈ᜔'),
         ('ang', 'ᜀᜅ᜔'), ('Usman', 'ᜂᜐ᜔ᜋᜈ᜔'), ('saksi', 'ᜐᜃ᜔ᜐᜒ')]
    for w, want in t: assert word(w) == want, (w, word(w), want)
    assert word('ang', 'drop') == 'ᜀ' and word('bundok', 'drop') == 'ᜊᜓᜇᜓ'
    assert to_baybayin('Mabuhay, Indio.') == word('mabuhay') + ' ᜵ ' + word('indio') + ' ᜶'
    assert read_back(word('mabuhay')) == 'ma bu ha y', read_back(word('mabuhay'))
    print('baybayin: %d words spelled as expected' % (len(t) + 2))


if __name__ == '__main__':
    a = sys.argv[1:]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    rgb = lambda s: tuple(int(x) for x in s.split(','))
    if a[:1] == ['test']: _test()
    elif a[:1] == ['word'] and len(a) >= 2: b = to_baybayin(a[1], opt('--final', 'virama')); print(b); print('reads:', read_back(b))
    elif a[:1] == ['render'] and len(a) >= 3: render(a[1], int(opt('--px', 160)), rgb(opt('--colour', '40,26,12')), opt('--final', 'virama')).save(a[2]); print(a[2], '|', read_back(to_baybayin(a[1], opt('--final', 'virama'))))
    elif a[:1] == ['paste'] and len(a) >= 5:
        q = [float(x) for x in a[4].split(',')]; assert len(q) == 8, 'four corners: x1,y1,x2,y2,x3,y3,x4,y4'
        b = paste(a[1], a[2], a[3], q, rgb(opt('--colour', '')) if '--colour' in a else None, float(opt('--opacity', 0.85)), float(opt('--rough', 1.0)), '--carve' in a, opt('--final', 'virama')); print(a[2], '|', b, '| reads:', ' / '.join(read_back(x) for x in b.split(' | ')))
    else: sys.exit(__doc__)
