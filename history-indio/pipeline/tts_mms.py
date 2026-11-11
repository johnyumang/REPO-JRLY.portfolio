"""Base Tagalog read with facebook/mms-tts-tgl (Hugging Face). One wav per sentence + timings json.
usage: tts_mms.py sentences.json out.wav timings.json"""
import json, sys, numpy as np, torch, soundfile as sf
from transformers import VitsModel, AutoTokenizer
tok = AutoTokenizer.from_pretrained('facebook/mms-tts-tgl'); model = VitsModel.from_pretrained('facebook/mms-tts-tgl')
model.speaking_rate = 1.08; model.noise_scale = 0.75
sents = json.load(open(sys.argv[1])); sr = model.config.sampling_rate; out = []; t = 0.0; tim = []
torch.manual_seed(7)
for s in sents:
    ids = tok(s['say'], return_tensors='pt')
    with torch.no_grad(): w = model(**ids).waveform[0].numpy()
    w = w / max(1e-6, np.abs(w).max()) * 0.9
    tim.append({'text': s['text'], 'start': round(t, 3), 'end': round(t + len(w) / sr, 3)})
    pause = np.zeros(int(sr * s.get('pause', 0.32)), np.float32); out += [w.astype(np.float32), pause]; t += (len(w) + len(pause)) / sr
sf.write(sys.argv[2], np.concatenate(out), sr); json.dump(tim, open(sys.argv[3], 'w'), ensure_ascii=False, indent=1); print('dur', round(t, 1), 'sr', sr)
