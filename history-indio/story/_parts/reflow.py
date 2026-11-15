#!/usr/bin/env python3
"""After a master script is revised: re-derive, count what changed against the committed version, and move the
sentence numbers in shots.md and facts.md to the new numbering.
Usage: python3 story/_parts/reflow.py story/epNN_v2      (run from history-indio/, before committing)
Old numbering = sentences.json at git HEAD. A new sentence between two shots goes to a "(silent)" shot lying
between them if there is one (that shot now carries a storyteller line), else to the shot that follows."""
import json, re, subprocess, sys, difflib
d = sys.argv[1].rstrip('/')
old = json.loads(subprocess.check_output(['git', 'show', f'{sys.argv[2] if len(sys.argv)>2 else "HEAD"}:history-indio/{d}/sentences.json']))
subprocess.check_call([sys.executable, 'story/_parts/derive.py', d])
new = json.load(open(f'{d}/sentences.json'))
ot = [(s['speaker'], s['text']) for s in old]; nt = [(s['speaker'], s['text']) for s in new]
m = {}; added = cut = changed = 0
for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ot, nt, autojunk=False).get_opcodes():
    if tag == 'equal':
        for k in range(i2 - i1): m[i1 + k] = j1 + k
    elif tag == 'replace':
        c = min(i2 - i1, j2 - j1); changed += c; cut += (i2 - i1) - c; added += (j2 - j1) - c
        for k in range(c): m[i1 + k] = j1 + k
    elif tag == 'delete': cut += i2 - i1
    else: added += j2 - j1
words = sum(len(s['text'].split()) for s in new)
# shots.md
lines = open(f'{d}/shots.md').read().split('\n')
rows = []  # (line index, kind, old indices)
for li, l in enumerate(lines):
    mm = re.match(r'^\| (\d+) \| ([^|]*) \|', l)
    if not mm: continue
    cell = mm.group(2).strip()
    nums = re.match(r'^(\d+)(?:-(\d+))?', cell)
    if nums:
        a = int(nums.group(1)); b = int(nums.group(2) or a); rows.append([li, 'num', list(range(a, b + 1)), cell])
    elif cell.startswith('(silent') : rows.append([li, 'silent', [], cell])
    else: rows.append([li, 'other', [], cell])
owner = {}
for ri, r in enumerate(rows):
    for o in r[2]:
        if o in m: owner[m[o]] = ri
for j in range(len(new)):
    if j in owner: continue
    p = max([owner[k] for k in owner if k < j], default=-1)
    nxt = [owner[k] for k in sorted(owner) if k > j]
    n = nxt[0] if nxt else None
    sil = [ri for ri in range(p + 1, n if n is not None else len(rows)) if rows[ri][1] == 'silent']
    owner[j] = sil[0] if sil else (n if n is not None else max(p, 0))
for ri, r in enumerate(rows):
    mine = sorted(j for j in owner if owner[j] == ri)
    if r[1] == 'other': continue
    if not mine: cell = '(silent)' if r[1] == 'silent' else '(cut)'
    else: cell = str(mine[0]) if mine[0] == mine[-1] else f'{mine[0]}-{mine[-1]}'
    lines[r[0]] = re.sub(r'^(\| \d+ \| )([^|]*)( \|)', lambda k: k.group(1) + cell + k.group(3), lines[r[0]], count=1)
txt = '\n'.join(lines)
txt = re.sub(r'\((\d+) sentences\)', f'({len(new)} sentences)', txt, count=1)
note = 'Revised for rule 9 (the storyteller tells every action in a full sentence): shots that were silent now carry a storyteller line; the pictures themselves do not change.'
if note not in txt: txt = txt.replace('\n\n', '\n\n' + note + '\n\n', 1)
open(f'{d}/shots.md', 'w').write(txt)
# facts.md: first column sentence references
fl = open(f'{d}/facts.md').read().split('\n')
for i, l in enumerate(fl):
    mm = re.match(r'^(\| )([^|]*)(\|.*)$', l)
    if mm and re.search(r'\bs\d+', mm.group(2)):
        cell = re.sub(r'\bs(\d+)', lambda k: 's' + (str(m[int(k.group(1))]) if int(k.group(1)) in m else k.group(1) + '(cut)'), mm.group(2))
        fl[i] = mm.group(1) + cell + mm.group(3)
open(f'{d}/facts.md', 'w').write('\n'.join(fl))
tg = sum(len(s['text'].split()) for s in new if s['speaker'] == 'TAGAPAGSALAYSAY')
print(f'{d}: {len(new)} sentences, {words} words (storyteller {tg}); added {added}, changed {changed}, cut {cut}')
