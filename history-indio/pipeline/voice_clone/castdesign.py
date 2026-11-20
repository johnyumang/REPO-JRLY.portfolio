"""Designed voices for the Season 2 cast with VoxCPM2 voice design (runs in /opt/vx). Never a clone of a real person.
usage: castdesign.py [--only USMAN,M] [--desc 0,1] [--seeds 1,2]   -> $HI_VOICE_WORK/castwork/<NAME>/d<k>s<seed>.wav (candidate reference clips)
       castdesign.py --samples [--only ...] [--seeds 1]             -> castwork/<NAME>/sample_s<seed>.wav, generated FROM the kept cast/<NAME>.wav
Voice design = '(description)text' with no reference audio. A kept voice is reused as prompt + reference with its exact
transcript (cast/<NAME>.txt), the same way Indio's own recording is used."""
import os, sys, json, time, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import voxgen as V, vprofile as VP
a = sys.argv[1:]; arg = lambda f, d: a[a.index(f) + 1] if f in a else d
D = json.load(open(os.path.join(VP.HERE, 'cast_design.json')))
only = [x for x in arg('--only', '').split(',') if x]; seeds = [int(x) for x in arg('--seeds', ','.join(map(str, D['seeds']))).split(',')]
descs = [int(x) for x in arg('--desc', '0,1').split(',')]
for name, c in D['cast'].items():
    if only and name not in only: continue
    d = os.path.join(VP.CASTWORK, VP.fname(name)); os.makedirs(d, exist_ok=True)
    jobs = []
    if '--samples' in a:
        ref, txt = VP.cast_ref(name)
        jobs = [(f'{d}/sample_s{s}.wav', dict(text=c['sample'], prompt=ref, prompt_text=txt, ref=ref, seed=s), c['sample']) for s in seeds]
    else:
        jobs = [(f'{d}/d{k}s{s}.wav', dict(text='(%s)%s' % (c['descriptions'][k], c['ref_text']), seed=s), c['ref_text']) for k in descs if k < len(c['descriptions']) for s in seeds]
    for out, kw, text in jobs:
        if os.path.exists(out): continue
        t0 = time.time(); w, sr = V.gen(**kw); sf.write(out, w, sr)
        json.dump(dict(text=text, **{k: v for k, v in kw.items() if k != 'text'}), open(out[:-4] + '.gen.json', 'w'), ensure_ascii=False)
        print('%s %s %.1fs audio in %.0fs' % (name, os.path.basename(out), len(w) / sr, time.time() - t0), flush=True)
print('castdesign done', flush=True)
