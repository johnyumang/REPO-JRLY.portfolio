#!/usr/bin/env python3
"""Apply videos/<slug>/narration_cuts.json to a finished narration, for the one rebuild (ruling of 13 November 2026).
usage: apply_cuts.py videos/<slug> <voice.mp3> <voice_timings.json> <out_dir>
Writes into out_dir (outside the repository): voice.mp3 without the cut sentences, timings.json (cut entries dropped,
later ones shifted), shots_fx.json renumbered, keys/kNN.png (links to the episode's keys, renumbered), endcard.txt.
Each cut removes from the middle of the pause before the cut sentence to the middle of the pause after it, so the join
sits in silence and the new pause is half of each old one (10 ms fades, no click). Every cut text must equal timings[index].text exactly.
Then: build_anime.py <out_dir> <out_dir>/keys <out_dir>/voice.mp3 <out>.mp4 --size 720, and copy <out_dir>/timings.json
to videos/<slug>/timings.json (commit it); sentences.json, key_prompts.json and the stills keep the full numbering."""
import json, os, shutil, subprocess, sys
import numpy as np, soundfile as sf

ep, voice, vtim, out = sys.argv[1:5]
C = json.load(open(os.path.join(ep, 'narration_cuts.json')))
T = json.load(open(vtim))
cuts = sorted({int(c['index']) for c in C.get('cut', [])})
for c in C.get('cut', []):
    i = int(c['index'])
    if not 0 <= i < len(T) or T[i]['text'].strip() != c['text'].strip():
        sys.exit(f'cut {i}: text does not match {vtim} (got {T[i]["text"][:60] if 0 <= i < len(T) else "out of range"!r}); stop')
if C.get('revoice'): sys.exit('this cut file asks for a re-voiced line: record it first (not handled here)')
os.makedirs(out, exist_ok=True)
tmp = os.path.join(out, 'voice_full.wav')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', voice, '-c:a', 'pcm_f32le', tmp], check=True)
y, sr = sf.read(tmp, always_2d=True)
spans = []
for i in cuts:
    a = (T[i - 1]['end'] + T[i]['start']) / 2 if i else 0.0                          # both edges in the middle of a silence: the join
    b = (T[i]['end'] + T[i + 1]['start']) / 2 if i + 1 < len(T) else len(y) / sr     # lands in a pause, never on a word's attack
    if i + 1 >= len(T): a = T[i - 1]['end'] + 0.5 if i else 0.0                     # a cut at the very end keeps 0.5 s after the last line
    spans.append((a, b))
keep, pos, F = [], 0, int(0.010 * sr)                                                # 10 ms fades at every join: no click
for a, b in spans:
    seg = y[pos:int(round(a * sr))].copy()
    if len(seg) > F: seg[-F:] *= np.linspace(1, 0, F)[:, None]
    keep.append(seg); pos = int(round(b * sr))
seg = y[pos:].copy()
if spans and len(seg) > F: seg[:F] *= np.linspace(0, 1, F)[:, None]
keep.append(seg)
z = np.concatenate(keep)
sf.write(os.path.join(out, 'voice_cut.wav'), z, sr, subtype='FLOAT')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(out, 'voice_cut.wav'), '-c:a', 'libmp3lame', '-b:a', '256k',
                os.path.join(out, 'voice.mp3')], check=True)
os.remove(tmp)
removed = lambda t: sum(min(b, t) - a for a, b in spans if t > a)                    # seconds removed before time t
NT, old2new = [], {}
for i, s in enumerate(T):
    if i in cuts: continue
    old2new[i] = len(NT); d = removed(s['start'])
    NT.append({**s, 'start': round(s['start'] - d, 3), 'end': round(s['end'] - d, 3)})
json.dump(NT, open(os.path.join(out, 'timings.json'), 'w'), ensure_ascii=False, indent=1)
fxp = os.path.join(ep, 'shots_fx.json')
if os.path.exists(fxp):
    FX = json.load(open(fxp))
    json.dump({str(old2new[int(k)]): v for k, v in FX.items() if k.isdigit() and int(k) in old2new} |
              {k: v for k, v in FX.items() if not k.isdigit()}, open(os.path.join(out, 'shots_fx.json'), 'w'), ensure_ascii=False, indent=1)
kd = os.path.join(out, 'keys'); os.makedirs(kd, exist_ok=True)
for o, n in old2new.items():
    src = os.path.abspath(os.path.join(ep, 'keys', f'k{o:02d}.png')); dst = os.path.join(kd, f'k{n:02d}.png')
    if os.path.lexists(dst): os.remove(dst)
    os.symlink(src, dst)
for f in ('endcard.txt',):
    if os.path.exists(os.path.join(ep, f)): shutil.copy(os.path.join(ep, f), out)
if os.path.isdir(os.path.join(ep, 'rigs')): sys.exit('this episode has puppet rigs: renumber rigs/ too before building')
print(f'cut sentences {cuts}: removed {sum(b - a for a, b in spans):.2f} s; {len(T)} -> {len(NT)} sentences; '
      f'voice {len(y) / sr:.2f} -> {len(z) / sr:.2f} s; joins: ' +
      ' | '.join(f'"{T[i - 1]["text"][-40:]}" / "{T[i + 1]["text"][:40]}"' for i in cuts if 0 < i < len(T) - 1))
print(f'next: build_anime.py {out} {out}/keys {out}/voice.mp3 <out>.mp4 --size 720; then cp {out}/timings.json {ep}/timings.json')
