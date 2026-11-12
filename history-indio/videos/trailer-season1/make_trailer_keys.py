#!/usr/bin/env python3
"""Fill videos/trailer-season1/keys/ (git-ignored) with frames that already exist in Episodes 1-6. No generation.
usage (from history-indio/): python videos/trailer-season1/make_trailer_keys.py [--theft-ep6]
Episode keys/ folders are rebuilt with pipeline/make_keys.py; Episode 5 has none on this machine, so its frames are
made here the same way make_keys.py makes them (a full frame, or a character composited on its plate, from the
committed plates/ chars/ full/). --theft-ep6 uses Episode 6 k35 (empty chest) for the theft line instead of a
medallion close-up from Episode 4 (see facts.md: the rule allows one quiet Episode 6 image; k35 is not an execution
image, but it is a second Episode 6 frame, so it is off by default)."""
import json, os, sys, cv2
HERE = os.path.dirname(os.path.abspath(__file__)); V = os.path.dirname(HERE); sys.path.insert(0, os.path.join(V, '..', 'pipeline'))
import composite_shot
E = {1: 'ep01-ang-unang-talon', 2: 'ep02-british-sa-maynila', 3: 'ep03-ang-sabi-ni-lola', 4: 'ep04-ang-aso-ni-pepe',
     5: 'ep05-dalawampung-milyon', 6: 'ep06-ang-huling-umaga'}
# trailer key: (episode, source key, what it is)
MAP = {0: (1, 14, 'marker in the rain (Pugad Lawin shrine)'), 1: (1, 16, 'rain stops in the air'),
       2: (1, 8, 'the medallion in his hand'), 3: (2, 10, 'the medallion glows'), 4: (1, 19, 'falling through the portal'),
       5: (1, 18, 'Usman leaps out of the light'), 6: (2, 11, 'Usman, deadpan'),
       7: (1, 24, '1896: Katipuneros tear their cedulas'), 8: (2, 18, '1762: the wall of Manila falls'),
       9: (3, 15, '1898: the crowd at the Aguinaldo house, Kawit'), 10: (4, 26, '1869: the carromata leaves Calamba'),
       11: (5, 13, '1898: Paris in December'), 12: (6, 1, '1896: Rizal seen from behind at sunrise (the one quiet Ep 6 image)'),
       13: (3, 38, 'Lola: shh'), 14: (5, 46, 'the woman with the red umbrella'), 15: (5, 7, 'the twenty-peso note signed M'),
       16: (4, 11, 'a hand closes on the medallion'), 17: (1, 1, 'Indio and Usman before the portal'),
       18: (1, 41, 'Indio and Usman jump'), 19: (1, 20, 'Indio and Usman in 1896')}
if '--theft-ep6' in sys.argv: MAP[16] = (6, 35, 'his chest, the medallion gone')

def green_cutout(im):                                           # copied from make_keys.py (importing it would run it)
    import numpy as np
    f = im.astype(np.float32); bl, g, r = f[..., 0], f[..., 1], f[..., 2]
    m = ((g > 90) & (g > r * 1.25) & (g > bl * 1.25)).astype(np.uint8) * 255
    m = cv2.dilate(m, np.ones((5, 5), np.uint8)); a = (255 - cv2.GaussianBlur(m, (5, 5), 0)).astype(np.float32) / 255
    im[..., 1] = np.minimum(g, np.maximum(r, bl) * 1.05).astype(np.uint8)
    return a

def ep5(k):                                                     # same recipe as make_keys.py, from committed files only
    d = os.path.join(V, E[5]); K = json.load(open(os.path.join(d, 'key_prompts.json'))); s = K['shots'][str(k)]
    find = lambda kind, n: next((p for p in (f'{d}/{kind}/{n}.png', f'{d}/{kind}/{n}.jpg') if os.path.exists(p)), None)
    if 'char' in s:
        if K.get('bg') == 'green': composite_shot.cutout = green_cutout
        im = composite_shot.composite(cv2.imread(find('chars', s['char'])), cv2.imread(find('plates', s['plate'])), s.get('x', .5), s.get('y', .5),
                                      s.get('s', .7), s.get('blur', 5), tuple(s.get('tint', (1.0, 0.97, 0.94))), s.get('gain', 0.97))
    else: im = cv2.imread(find('full', s['full']) if 'full' in s else find('plates', s['plate']))
    return cv2.resize(im, (1152, 2048), interpolation=cv2.INTER_LANCZOS4)

out = os.path.join(HERE, 'keys'); os.makedirs(out, exist_ok=True); bad = []
for t, (e, k, what) in MAP.items():
    src = os.path.join(V, E[e], 'keys', f'k{k:02d}.png'); dst = os.path.join(out, f'k{t:02d}.png')
    if os.path.exists(src): im = cv2.imread(src)
    elif e == 5: im = ep5(k)
    else: bad.append(f'k{t:02d} <- Ep{e} k{k:02d}: run pipeline/make_keys.py videos/{E[e]}'); continue
    if im is None: bad.append(f'k{t:02d} <- Ep{e} k{k:02d}: unreadable'); continue
    if im.shape[:2] != (2048, 1152): im = cv2.resize(im, (1152, 2048), interpolation=cv2.INTER_LANCZOS4)
    cv2.imwrite(dst, im); print(f'k{t:02d} <- Ep{e} k{k:02d}  {what}')
for p in [os.path.join(out, 'depth', f) for f in os.listdir(os.path.join(out, 'depth'))] if os.path.isdir(os.path.join(out, 'depth')) else []: os.remove(p)   # stale depth cache
print('MISSING:\n' + '\n'.join(bad) if bad else f'{len(MAP)} keys written to {out}'); sys.exit(1 if bad else 0)
