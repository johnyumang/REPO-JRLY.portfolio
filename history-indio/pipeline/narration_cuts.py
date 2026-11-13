#!/usr/bin/env python3
"""Sentences cut from a narration (videos/<slug>/narration_cuts.json): which picture belongs to which line afterwards.

THE RULE (13 Nov): nobody renumbers anything. sentences.json, key_prompts.json, shots_fx.json and the key files keep the
ORIGINAL sentence numbers for ever. Only the narration and timings.json lose the cut sentences. The builder asks this
module which original number each line of timings.json has, and takes that number's key and shots_fx entry.

narration_cuts.json: {"cut": [{"index": N, "text": "..."}], "revoice": [{"after_index": N, "new_text": "..."}], ...}
- a cut sentence is simply gone: timings.json has one line fewer;
- a "revoice" line that follows the sentence just before a cut one REPLACES that cut sentence: same number, same picture,
  new words (Episodes 31 and 49). The count does not change for it.

usage (check an episode by hand):  narration_cuts.py videos/<slug>
"""
import json, os, sys


def _txt(s): return (s['text'] if isinstance(s, dict) else s).strip()


def source_index(vdir, tim):
    """-> (src, note): src[i] = the original sentence number of timings line i; note = None when the episode has no cuts,
    else a short text for the log. Stops the run (SystemExit) when timings.json fits neither the uncut nor the cut narration,
    or when a line's words are not the words of the sentence it is mapped to: a wrong map puts the wrong picture under
    every later line, so it is never guessed."""
    n_t = len(tim); src = list(range(n_t))
    cp, sp = os.path.join(vdir, 'narration_cuts.json'), os.path.join(vdir, 'sentences.json')
    if not (os.path.exists(cp) and os.path.exists(sp)): return src, None
    C = json.load(open(cp)); S = json.load(open(sp)); S = S if isinstance(S, list) else S.get('sentences', [])
    n = len(S); cut = {int(c['index']) for c in C.get('cut', [])}
    if not cut: return src, None
    new = {int(r['after_index']) + 1: r.get('new_text', '').strip() for r in C.get('revoice', []) if int(r['after_index']) + 1 in cut}
    gone = cut - set(new)                                              # really removed; the others are replaced in place
    if n_t == n - len(gone): src = [k for k in range(n) if k not in gone]; state = 'applied'
    elif n_t == n: state = 'NOT applied yet'
    else: raise SystemExit(f'narration cuts: timings.json has {n_t} lines; sentences.json has {n} and the cut file removes {len(gone)} '
                           f'(want {n} before the cut or {n - len(gone)} after it). Is timings.json the one for this narration?')
    bad = []
    for i, k in enumerate(src):
        want = _txt(S[k])
        if state == 'applied' and k in new: want = new[k] or want       # the replaced sentence carries the new words
        if _txt(tim[i]) != want and not (k in new and _txt(tim[i]) in (new[k], _txt(S[k]))): bad.append((i, k, _txt(tim[i])[:50], want[:50]))
    if bad:
        i, k, a, b = bad[0]
        raise SystemExit(f'narration cuts: {len(bad)} line(s) of timings.json do not hold the words of their sentence; the first: line {i} '
                         f'"{a}" against sentence {k} "{b}". Nothing was built: check that nothing renumbered sentences.json or timings.json.')
    pos = {k: i for i, k in enumerate(src)}
    old = sorted(k for k in new if new[k] and _txt(tim[pos[k]]) != new[k])     # replaced sentences that still carry the old words
    if old: state = 'NOT applied yet' if state != 'applied' or not gone else 'applied in part'
    note = f'narration cuts {state}:' + (f' sentences {sorted(gone)} left out' if gone else '')
    if new: note += (',' if gone else '') + f' {sorted(new)} replaced by a new line' + (f' ({old} NOT recorded yet: the old words are still said)' if old else '')
    if state == 'NOT applied yet' and gone: note += ' (this build still SAYS them: apply the cut to the narration first)'
    return src, note


if __name__ == '__main__':
    v = sys.argv[1].rstrip('/'); tim = json.load(open(v + '/timings.json'))
    src, note = source_index(v, tim); print(note or 'no cuts for this episode')
    moved = [(i, k) for i, k in enumerate(src) if i != k]
    if moved: print(f'{len(moved)} line(s) take the picture of an earlier number: line {moved[0][0]} -> key k{moved[0][1]:02d} ... line {moved[-1][0]} -> key k{moved[-1][1]:02d}')
