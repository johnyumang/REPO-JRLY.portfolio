"""Generate one take per chunk of a multi-speaker plan, each in its speaker's voice (runs in /opt/vx).
usage: gen_ms.py <work_dir> [--only 0,3] [--seeds 1] [--leadin 'Sige.'|@echo --tag x]   -> <work_dir>/c<id>_<speaker>_s<seed>.wav (lead-in: _lead<seed><tag>.wav)
INDIO: exactly as gen.py mode U (continuation from a tone-matched prompt cut from the user's own recording + timbre reference).
Any other speaker: continuation from its private designed-voice reference $HI_VOICE_WORK/cast/<NAME>.wav with its exact
transcript <NAME>.txt, the same clip also as timbre reference."""
import os, sys, json, time, numpy as np, soundfile as sf, librosa
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import voxgen as V, vprofile as VP
work = sys.argv[1]; a = sys.argv[2:]; arg = lambda f, d: a[a.index(f) + 1] if f in a else d
P = json.load(open(work + '/plan.json')); only = [int(x) for x in arg('--only', '').split(',') if x]; seeds = [int(x) for x in arg('--seeds', '1').split(',')]
LEAD = arg('--leadin', ''); TAG = arg('--tag', 'L')   # throwaway lead-in before the line (ms.py fixstarts --leadin cuts it off): out c<id>_<SPK>_lead<seed><tag>.wav
import leadtrim; SAY = {x['i']: x.get('say', x['text']) for x in P['sentences']}
PROMPTS, REFS = VP.PROFILE['prompts'], VP.PROFILE['refs']
TAIL = 0.80   # silence after the continuation prompt: with 0.30 s the model often voices a stray syllable before the line (Ep 10: 0/8 -> 5/8 takes right)
def clip(ids, out, gap=0.38, tail=TAIL):                                          # same cut as gen.py, longer tail
    if os.path.exists(out): return out
    parts = []
    for k, i in enumerate(ids):
        r = V.REAL[i]; y, sr = librosa.load(V.REC, sr=44100, mono=True, offset=max(0, r['start'] - 0.05), duration=r['end'] - r['start'] + 0.13)
        n = int(0.015 * sr); y[:n] *= np.linspace(0, 1, n); y[-n:] *= np.linspace(1, 0, n); parts.append(y)
        parts.append(np.zeros(int((tail if k == len(ids) - 1 else gap) * sr), np.float32))
    sf.write(out, np.concatenate(parts), 44100); return out
os.makedirs(work + '/refs', exist_ok=True)
def voice(c):
    if c['speaker'] == VP.NARRATOR:
        ids = PROMPTS.get(c['prompt'], PROMPTS['narrate'])
        return dict(prompt=clip(ids, f"{work}/refs/p_{c['prompt']}_t80.wav"), prompt_text=' '.join(V.REAL[i]['text'] for i in ids), ref=clip(REFS, work + '/refs/ref.wav', tail=0.2))
    w, t = VP.cast_ref(c['speaker']); pw = f"{work}/refs/{VP.fname(c['speaker'])}_t80.wav"
    if not os.path.exists(pw):                                                  # cast clips end in 0.25 s silence: pad to TAIL
        y, sr = sf.read(w, dtype='float32'); sf.write(pw, np.r_[y, np.zeros(int((TAIL - 0.25) * sr), np.float32)], sr)
    return dict(prompt=pw, prompt_text=t, ref=w)
for c in P['chunks']:
    if only and c['id'] not in only: continue
    for seed in seeds:
        out = f"{work}/c{c['id']:03d}_{VP.fname(c['speaker'])}_s{seed}.wav"
        text = c['text']
        if LEAD:
            out = f"{work}/c{c['id']:03d}_{VP.fname(c['speaker'])}_lead{seed}{TAG}.wav"
            text = leadtrim.leadin_text(LEAD, SAY.get(c['sent_ids'][0] - 1, '')) + ' ' + c['text']
        if os.path.exists(out): continue
        t0 = time.time(); w, sr = V.gen(text, seed=seed, **voice(c)); sf.write(out, w, sr)
        print('chunk %d %s s%d [%s] %.1fs audio in %.0fs | %s' % (c['id'], c['speaker'], seed, c['style'], len(w) / sr, time.time() - t0, c['text'][:70]), flush=True)
print('gen done', flush=True)
