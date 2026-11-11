"""Expressive Tagalog read in the narrator's own voice with Chatterbox Multilingual (ResembleAI, Hugging Face).
Tagalog is not an official language of the model; Malay mode ('ms') reads Tagalog spelling clearly.
usage: tts_chatterbox.py sentences.json narrator_ref.wav out.wav timings.json"""
import json, re, sys, numpy as np, soundfile as sf, torch, librosa
torch.set_num_threads(4)
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
sents = json.load(open(sys.argv[1])); ref = sys.argv[2]
m = ChatterboxMultilingualTTS.from_pretrained(device='cpu'); sr = m.sr; out = []; t = 0.0; tim = []
def say(s):
    s = re.sub(r'\bng\b', 'nang', s['say']).replace('aniceto', 'aniseto').replace('luzuriaga', 'lusuryaga').replace('cinco', 'singko')
    return s[0].upper() + s[1:]
for i, s in enumerate(sents):
    txt = say(s); limit = len(txt.split()) * 0.8 + 2.5
    for seed in (11, 23, 37):
        torch.manual_seed(seed + i)
        w = m.generate(txt, language_id='ms', audio_prompt_path=ref, exaggeration=0.6, cfg_weight=0.4).squeeze().numpy()
        w, _ = librosa.effects.trim(w, top_db=40)
        if len(w) / sr <= limit: break               # retry if the model rambled
    w = w / max(1e-6, np.abs(w).max()) * 0.9
    tim.append({'text': s['text'], 'start': round(t, 3), 'end': round(t + len(w) / sr, 3)})
    pause = np.zeros(int(sr * s.get('pause', 0.32)), np.float32); out += [w.astype(np.float32), pause]; t += (len(w) + len(pause)) / sr
    print(i + 1, '/', len(sents), '%.1fs' % (len(w) / sr), flush=True)
sf.write(sys.argv[3], np.concatenate(out), sr); json.dump(tim, open(sys.argv[4], 'w'), ensure_ascii=False, indent=1); print('dur', round(t, 1))
