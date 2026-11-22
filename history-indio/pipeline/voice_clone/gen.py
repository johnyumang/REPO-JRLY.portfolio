"""Generate cloned-voice candidates for the chunks of a plan with VoxCPM2 (runs in /opt/vx).
usage: gen.py <work_dir> [--only 0,1,2] [--modes U,R] [--seeds 1]
U = continuation from a tone-matched prompt cut from the real recording + timbre reference; R = timbre reference only."""
import os, sys, json, time, numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import voxgen as V, vprofile as VP
work = sys.argv[1]; a = sys.argv[2:]; arg = lambda f, d: a[a.index(f) + 1] if f in a else d
P = json.load(open(work + '/plan.json')); only = [int(x) for x in arg('--only', '').split(',') if x]; modes = arg('--modes', 'U').split(','); seeds = [int(x) for x in arg('--seeds', '1').split(',')]
# tone -> real Episode 1 sentences used as the continuation prompt (the last one sets the tone); timbre reference ids (voice_profile.json)
PROMPTS = VP.PROFILE['prompts']
REFS = VP.PROFILE['refs']
import librosa
def clip(ids, out, gap=0.38, tail=0.30):
    if os.path.exists(out): return out
    parts = []
    for k, i in enumerate(ids):
        r = V.REAL[i]; y, sr = librosa.load(V.REC, sr=44100, mono=True, offset=max(0, r['start'] - 0.05), duration=r['end'] - r['start'] + 0.13)
        n = int(0.015 * sr); y[:n] *= np.linspace(0, 1, n); y[-n:] *= np.linspace(1, 0, n); parts.append(y)
        parts.append(np.zeros(int((tail if k == len(ids) - 1 else gap) * sr), np.float32))
    sf.write(out, np.concatenate(parts), 44100); return out
os.makedirs(work + '/refs', exist_ok=True); ref = clip(REFS, work + '/refs/ref.wav', tail=0.2)
for c in P['chunks']:
    if only and c['id'] not in only: continue
    ids = PROMPTS.get(c['prompt'], PROMPTS['narrate']); pw = clip(ids, f"{work}/refs/p_{c['prompt']}.wav"); pt = ' '.join(V.REAL[i]['text'] for i in ids)
    for mode in modes:
        for seed in seeds:
            out = f"{work}/c{c['id']:03d}_{mode}{seed}.wav"
            if os.path.exists(out): continue
            t0 = time.time()
            w, sr = V.gen(c['text'], prompt=pw if mode == 'U' else None, prompt_text=pt if mode == 'U' else None, ref=ref, seed=seed)
            sf.write(out, w, sr); print('chunk %d %s%d [%s] %.1fs audio in %.0fs | %s' % (c['id'], mode, seed, c['prompt'], len(w) / sr, time.time() - t0, c['text'][:70]), flush=True)
print('gen done', flush=True)
