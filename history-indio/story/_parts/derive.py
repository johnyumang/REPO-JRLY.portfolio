#!/usr/bin/env python3
"""Derive script.txt and sentences.json from a v2 master script (script_multispeaker.txt).
Usage: python3 story/_parts/derive.py story/epNN_v2
Master format: '# --- title' starts a scene; '(...)' lines are pictures, not spoken; 'NAME: [tone] text' is spoken;
'NAME (sa atin): [tone] text' is Indio's aside; '# SAY: word=respelling' lines give the voice's spelling
(stress in capitals); everything after '# --- TRIVIA' is the end clip and is not part of sentences.json."""
import re, json, sys, collections
d = sys.argv[1].rstrip('/')
lines = [l.rstrip('\n') for l in open(f'{d}/script_multispeaker.txt')]
say_map = [("Indio", "indio")]
for l in lines:
    m = re.match(r'^# SAY: (.+?)=(.+)$', l)
    if m: say_map.append((m.group(1), m.group(2)))
say_map.sort(key=lambda p: -len(p[0]))
sent, paras, cur = [], [], []
for l in lines:
    if l.startswith('# --- TRIVIA'): break
    if l.startswith('# ---'):
        if cur: paras.append(cur); cur = []
        continue
    if not l or l.startswith('#') or l.startswith('('): continue
    m = re.match(r'^([^:]+): \[([\w ]+)\] (.*)$', l)
    assert m, l
    name, tone, text = m.groups()
    aside = '(sa atin)' in name
    spk = name.replace(' (sa atin)', '')
    parts = re.findall(r"[^.!?]+[.!?]+[\"']?", text)
    assert ''.join(parts).replace(' ', '') == text.replace(' ', ''), text
    for i, p in enumerate(parts):
        p = p.strip(); say = p.lower().replace("'", '').replace('"', '')
        for a, b in say_map:
            say = re.sub(r'\b' + re.escape(a.lower()) + r'\b', b, say)
        e = {"text": p, "say": say, "style": tone if i == 0 else "", "pre": 0,
             "pause": 0.4 if i < len(parts) - 1 else 0.5, "speaker": spk}
        if aside: e["aside"] = True
        sent.append(e); cur.append(f"[{tone}] {p}" if i == 0 else p)
if cur: paras.append(cur)
json.dump(sent, open(f'{d}/sentences.json', 'w'), ensure_ascii=False, indent=1)
open(f'{d}/script.txt', 'w').write('\n\n'.join(' '.join(p) for p in paras) + '\n')
c = collections.Counter()
for s in sent: c[s['speaker']] += len(s['text'].split())
print(len(sent), 'sentences;', sum(c.values()), 'words;', dict(c))
if '-v' in sys.argv:
    for i, s in enumerate(sent): print(i, s['speaker'][:6], '|', s['text'][:56])
