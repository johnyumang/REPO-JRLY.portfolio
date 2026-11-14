"""Leave the sentences named in videos/<slug>/narration_cuts.json out of a multi-voice narration (ruling of 13 Nov:
the video no longer says the story is fiction; the caption does), without recording anything.
usage: apply_cuts.py videos/<slug> <work_dir>      then: ms.py assemble <work> <work>/voice ; ms.py verify <work> <work>/voice
(the same as `ms.py assemble <work> <work>/voice --cut i,j` with the numbers read from the cut file)
- <work>/plan.json loses the chunks whose sentences are all cut (the full plan stays in plan_full.json; a chunk that is only
  partly cut stops the run: use pipeline/cut_narration.py on the finished voice instead, or make a new take);
- a sentence that a "revoice" line REPLACES (Episodes 31, 49) is not cut here: record the new words as that sentence's chunk.
NOTHING ELSE CHANGES: sentences.json, key_prompts.json, shots_fx.json and the key files keep the original numbers;
build_anime.py finds each line's picture through pipeline/narration_cuts.py. An earlier version of this tool renumbered
shots_fx.json: if videos/<slug>/shots_fx_full.json exists, this run puts it back as shots_fx.json and removes the copy.
Run once; a second run finds nothing to do."""
import json, os, sys, shutil
v, work = sys.argv[1].rstrip('/'), sys.argv[2].rstrip('/')
C = json.load(open(v + '/narration_cuts.json')); S = json.load(open(v + '/sentences.json'))
new = {int(r['after_index']) + 1 for r in C.get('revoice', [])}
cut = sorted(c['index'] for c in C['cut'] if c['index'] not in new)
fx, full = v + '/shots_fx.json', v + '/shots_fx_full.json'
if os.path.exists(full): shutil.move(full, fx); print('shots_fx.json: the renumbered copy is gone, the original numbering is back')
pf = work + '/plan_full.json'
if not os.path.exists(pf): shutil.copy(work + '/plan.json', pf)
P = json.load(open(pf))
for c in C['cut']:
    t = S[c['index']]['text']
    if t.strip() != c['text'].strip(): sys.exit('sentence %d is not the one the cut file names:\n  file: %s\n  cut:  %s' % (c['index'], t, c['text']))
keep = []
for ch in P['chunks']:
    inside = [i for i in ch['sent_ids'] if i in cut]
    if inside and len(inside) != len(ch['sent_ids']): sys.exit('chunk %d holds sentences %s but only %s are cut: cut the finished voice with pipeline/cut_narration.py, or make a new take' % (ch['id'], ch['sent_ids'], inside))
    if not inside: keep.append(ch)
P2 = dict(P, chunks=keep); json.dump(P2, open(work + '/plan.json', 'w'), ensure_ascii=False, indent=1)
print('plan: %d chunks -> %d (sentences cut: %s%s)' % (len(P['chunks']), len(keep), cut, '; replaced by a new line, not cut: %s' % sorted(new) if new else ''))
