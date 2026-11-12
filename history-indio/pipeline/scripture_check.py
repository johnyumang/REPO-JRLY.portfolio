#!/usr/bin/env python3
"""Mechanical check of scripture quotations in episode scripts against Ang Dating Biblia (1905).
usage: scripture_check.py <abtag_dir> <videos_dir> [min_words]
For every sentence in every sentences.json, find the verse sharing the longest run of consecutive words.
A run of >= min_words words means the sentence quotes or closely follows that verse. EXACT: the whole sentence
is the verse's words. PART: the sentence carries an exact piece of the verse plus its own words (an attribution,
or narration). DIFFER: words inside the quoted span are not the verse's words; read these by eye (narration that
retells a verse in its own words is fine, a line presented as a quotation is not).
Text: the public-domain abtag files of github.com/nehemiaharchives/bbl (see KAIZEN.md for the small clone)."""
import sys, re, json, glob, os, difflib, collections
A, V = sys.argv[1], sys.argv[2]; MINW = int(sys.argv[3]) if len(sys.argv) > 3 else 6
BOOK = {1:'Genesis',2:'Exodo',19:'Awit',20:'Kawikaan',23:'Isaias',27:'Daniel',40:'Mateo',41:'Marcos',42:'Lucas',43:'Juan',44:'Gawa',45:'Roma',58:'Hebreo',60:'1 Pedro',65:'Judas',66:'Pahayag'}
def norm(s): return re.sub(r"[^a-zñ0-9' ]+", ' ', s.lower().replace('’', "'")).split()
verses = []; idx = collections.defaultdict(set); N = 4
for f in glob.glob(os.path.join(A, 'abtag.*.txt')):
    b, c = map(int, os.path.basename(f).split('.')[1:3])
    for line in open(f, encoding='utf-8'):
        m = re.match(r'(\d+)\s+(.*)', line.strip())
        if not m: continue
        w = norm(m.group(2)); vid = len(verses); verses.append((b, c, int(m.group(1)), w, m.group(2)))
        for i in range(len(w) - N + 1): idx[tuple(w[i:i+N])].add(vid)
out = []
for sj in sorted(glob.glob(os.path.join(V, 'ep*', 'sentences.json'))):
    ep = os.path.basename(os.path.dirname(sj))
    try: Sx = json.load(open(sj, encoding='utf-8'))
    except Exception as e: print(ep, 'bad json', e); continue
    for i, s in enumerate(Sx):
        t = s.get('text') if isinstance(s, dict) else str(s)
        w = norm(re.sub(r'\[[^\]]*\]', ' ', t or ''))
        cand = collections.Counter()
        for k in range(len(w) - N + 1):
            for vid in idx.get(tuple(w[k:k+N]), ()): cand[vid] += 1
        best = None
        for vid, _ in cand.most_common(8):
            vw = verses[vid][3]
            m = difflib.SequenceMatcher(None, w, vw, autojunk=False)
            blk = m.find_longest_match(0, len(w), 0, len(vw))
            if best is None or blk.size > best[0]: best = (blk.size, vid, blk, m)
        if not best or best[0] < MINW: continue
        size, vid, blk, m = best; b, c, vn, vw, vraw = verses[vid]
        # the "quoted span": the stretch of the sentence aligned to the verse, extended over small gaps
        ops = [o for o in m.get_opcodes()]
        eq = [o for o in ops if o[0] == 'equal' and o[2]-o[1] >= 2]
        a0, a1, b0, b1 = eq[0][1], eq[-1][2], eq[0][3], eq[-1][4]
        # differences strictly inside the quoted span; what comes before it (an attribution) or after it (the rest of the verse) is not a misquote
        diffs = [(tag, ' '.join(w[i1:i2]), ' '.join(vw[j1:j2])) for tag, i1, i2, j1, j2 in ops if tag != 'equal' and i1 >= a0 and i2 <= a1 and j1 >= b0 and j2 <= b1 and not (i1 == i2 == a1) and not (i1 == i2 == a0)]
        cover = sum(o[2]-o[1] for o in eq) / max(1, len(w))
        out.append(dict(ep=ep, i=i, speaker=(s.get('speaker') if isinstance(s, dict) else ''), ref=f"{BOOK.get(b, 'aklat '+str(b))} {c}:{vn}", run=size, cover=round(cover, 2),
                        exact=(not diffs), diffs=diffs, text=t, verse=vraw))
for o in out:
    flag = 'DIFFER' if not o['exact'] else ('EXACT ' if o['cover'] >= 0.95 else 'PART  ')
    print(f"{flag} {o['ep'][:4]} [{o['i']}] {o['speaker']} ~ {o['ref']} (run {o['run']}, {int(o['cover']*100)}% of sentence)")
    if not o['exact']:
        print('   script:', o['text']); print('   verse :', o['verse'])
        for tag, a, b in o['diffs']: print(f"   {tag}: script '{a}' vs verse '{b}'")
print(len(out), 'sentences follow a verse;', sum(1 for o in out if not o['exact']), 'differ')
