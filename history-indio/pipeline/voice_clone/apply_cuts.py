"""Leave the sentences named in videos/<slug>/narration_cuts.json out of a multi-voice narration (ruling of 13 Nov:
the video no longer says the story is fiction; the caption does), without recording anything.
usage: apply_cuts.py videos/<slug> <work_dir>      then: ms.py assemble <work> <work>/voice ; ms.py verify <work> <work>/voice
- <work>/plan.json loses the chunks whose sentences are all cut (the full plan stays in plan_full.json; a chunk that is only
  partly cut stops the run: that needs a new take);
- videos/<slug>/shots_fx.json is renumbered to the sentences that remain, each moved shot keeping its own picture through
  "key" (build_anime.py reads it), so no picture sits over silence and no key file is renamed (the old file stays as
  shots_fx_full.json). Run once; a second run finds nothing to do."""
import json, os, sys, shutil
v, work = sys.argv[1].rstrip('/'), sys.argv[2].rstrip('/')
C = json.load(open(v + '/narration_cuts.json')); cut = sorted(c['index'] for c in C['cut'])
pf = work + '/plan_full.json'
if not os.path.exists(pf): shutil.copy(work + '/plan.json', pf)
P = json.load(open(pf)); S = json.load(open(v + '/sentences.json'))
for c in C['cut']:
    t = S[c['index']]['text']
    if t.strip() != c['text'].strip(): sys.exit('sentence %d is not the one the cut file names:\n  file: %s\n  cut:  %s' % (c['index'], t, c['text']))
keep = []
for ch in P['chunks']:
    inside = [i for i in ch['sent_ids'] if i in cut]
    if inside and len(inside) != len(ch['sent_ids']): sys.exit('chunk %d holds sentences %s but only %s are cut: it needs a new take' % (ch['id'], ch['sent_ids'], inside))
    if not inside: keep.append(ch)
P2 = dict(P, chunks=keep); json.dump(P2, open(work + '/plan.json', 'w'), ensure_ascii=False, indent=1)
print('plan: %d chunks -> %d (sentences cut: %s)' % (len(P['chunks']), len(keep), cut))
fx, full = v + '/shots_fx.json', v + '/shots_fx_full.json'
if not os.path.exists(full): shutil.copy(fx, full)
F = json.load(open(full)); n = len(S); new = {}; j = 0
for o in range(n):
    if o in cut: continue
    e = dict(F.get(str(o), {}))
    if j != o and 'key' not in e: e['key'] = o                       # the shot keeps its own picture
    if e: new[str(j)] = e
    j += 1
for k, e in F.items():                                               # entries past the sentences (extra keys) stay as they are
    if int(k) >= n: new[k] = e
json.dump(new, open(fx, 'w'), ensure_ascii=False, indent=0); print('shots_fx: %d sentences -> %d shots' % (n, j))
