#!/usr/bin/env python3
"""script.txt -> sentences.json for the Tagalog TTS. Each sentence keeps its display text and gets a
`say` version respelled the way Tagalog reads it (the TTS model reads letters phonetically, so English
words, years and Spanish names need respelling). Add words to respell.json as you meet them.
usage: make_sentences.py script.txt sentences.json"""
import json, os, re, sys
rep = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'respell.json')))
txt = open(sys.argv[1]).read().strip(); out = []
for para in txt.split('\n\n'):
    ss = re.findall(r'[^.?!]+[.?!]+', para.replace('\n', ' '))
    for i, s in enumerate(ss):
        s = s.strip(); say = s
        for a, b in rep.items(): say = say.replace(a, b)
        if re.search(r'\d', say): print('WARNING digits left, respell them:', say)
        out.append({'text': s, 'say': say.lower(), 'pause': 0.62 if i == len(ss) - 1 else (0.42 if s.endswith('?') else 0.3)})
json.dump(out, open(sys.argv[2], 'w'), ensure_ascii=False, indent=1); print(len(out), 'sentences')
