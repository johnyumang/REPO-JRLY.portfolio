#!/usr/bin/env python3
"""Proves that no still is shown twice (consistency check 8). usage: check_unique_stills.py videos/<slug>
Walks the sentences the way build_anime.py does (shots_fx "key", "keys", "_": {"hold_same_key": true}) and checks:
1. every key is shown in ONE unbroken run of the video (a held key across its lines counts once; a jump back into it fails),
2. every key points at its own still (no two keys share a 'full' / plate+char), 3. no two still files are the same picture
(identical bytes, or nearly identical at 16x16), 4. every still in full/ is used. Exit 1 on any failure."""
import hashlib, json, os, sys
from PIL import Image
v = sys.argv[1].rstrip('/'); K = json.load(open(v + '/key_prompts.json')); FX = json.load(open(v + '/shots_fx.json')) if os.path.exists(v + '/shots_fx.json') else {}
n = len(json.load(open(v + '/sentences.json'))); hold = bool(FX.get('_', {}).get('hold_same_key')); bad = []
seq = []                                                                   # (key, sentence) in the order shown
for i in range(n):
    c = FX.get(str(i), {})
    for k in (c['keys'] if c.get('keys') else [c.get('key', i)]): seq.append((int(k), i))
runs = []
for k, i in seq:
    if runs and runs[-1][0] == k and hold: runs[-1][2].append(i)
    else: runs.append([k, i, [i]])
seen = {}
for k, i, lines in runs:
    if k in seen: bad.append(f'key k{k:02d} is shown again at sentence {i} (first at sentence {seen[k]})')
    else: seen[k] = i
    if str(k) not in K['shots']: bad.append(f'key k{k:02d} (sentence {i}) has no entry in key_prompts shots')
still = {}
for k, s in K['shots'].items():
    nm = s.get('full') or (s.get('plate'), s.get('char')); still.setdefault(str(nm), []).append(k)
    if int(k) not in seen: bad.append(f'key k{int(k):02d} ({nm}) is never shown')
for nm, ks in still.items():
    if len(ks) > 1: bad.append(f'still {nm} is used by keys {ks}')
fd = v + '/full'; files = sorted(f for f in os.listdir(fd) if f.endswith(('.jpg', '.png'))) if os.path.isdir(fd) else []
used = {s.get('full') for s in K['shots'].values()}
for f in files:
    if f.rsplit('.', 1)[0] not in used: bad.append(f'full/{f} is not used by any key')
hs, sm = {}, {}
for f in files:
    b = open(os.path.join(fd, f), 'rb').read(); h = hashlib.sha1(b).hexdigest(); hs.setdefault(h, []).append(f)
    t = tuple(Image.open(os.path.join(fd, f)).convert('L').resize((16, 16)).tobytes()); sm[f] = t
for h, fs in hs.items():
    if len(fs) > 1: bad.append(f'identical files: {fs}')
fl = list(sm)
for a in range(len(fl)):
    for b in range(a + 1, len(fl)):
        d = sum(abs(x - y) for x, y in zip(sm[fl[a]], sm[fl[b]])) / 256
        if d < 6: bad.append(f'nearly the same picture: {fl[a]} and {fl[b]} (mean difference {d:.1f})')
print(f'{n} sentences, {len(runs)} shown runs, {len(seen)} keys, {len(still)} stills, {len(files)} files in full/')
for k, i, lines in runs:
    print(f'  k{k:02d} {K["shots"].get(str(k), {}).get("full", "?"):7s} sentences {lines[0]}-{lines[-1]}' if len(lines) > 1 else f'  k{k:02d} {K["shots"].get(str(k), {}).get("full", "?"):7s} sentence {lines[0]}')
if bad: print('FAIL'); [print(' -', b) for b in bad]; sys.exit(1)
print('PASS: every still is shown in exactly one place')
