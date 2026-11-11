"""Convert a narration wav to a target speaker's timbre with Chatterbox VC (ResembleAI, Hugging Face weights).
usage: vc_chatterbox.py source.wav target_voice.wav out.wav   -- converts in ~25 s chunks cut at pauses, keeps timing."""
import sys, numpy as np, soundfile as sf, librosa, torch, tempfile, os
from chatterbox.vc import ChatterboxVC
src, ref, out = sys.argv[1:4]
torch.set_num_threads(4)
vc = ChatterboxVC.from_pretrained('cpu'); vc.set_target_voice(ref); SR = vc.sr
y, sr = librosa.load(src, sr=16000, mono=True)
# split at silences so every chunk is <= 25 s
iv = librosa.effects.split(y, top_db=38, frame_length=1024, hop_length=256)
cuts = [0]; last = 0
for a, b in zip(iv[:-1], iv[1:]):
    mid = (a[1] + b[0]) // 2
    if (b[1] - last) / sr > 24 and mid > last: cuts.append(mid); last = mid
cuts.append(len(y)); res = []
for i, (a, b) in enumerate(zip(cuts[:-1], cuts[1:])):
    tmp = tempfile.mktemp(suffix='.wav'); sf.write(tmp, y[a:b], sr)
    w = vc.generate(tmp).squeeze().cpu().numpy(); os.remove(tmp)
    want = int((b - a) / sr * SR)                    # keep exact timing
    w = w[:want] if len(w) >= want else np.pad(w, (0, want - len(w)))
    res.append(w); print('chunk', i + 1, '/', len(cuts) - 1, flush=True)
o = np.concatenate(res); sf.write(out, o / max(1e-6, np.abs(o).max()) * 0.9, SR); print('done', len(o) / SR)
