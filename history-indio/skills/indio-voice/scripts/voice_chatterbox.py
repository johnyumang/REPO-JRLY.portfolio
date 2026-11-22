#!/usr/bin/env python3
"""Directed Tagalog/Taglish read in the narrator's voice (Chatterbox Multilingual, Hugging Face weights).
usage: voice.py sentences.json narrator_ref.wav out.wav timings.json [--only 3,7]
sentences.json: [{"text": shown text, "say": phonetic spelling, "style": "excited+slow", "pause": 0.3}, ...]"""
import json, os, re, sys, numpy as np, soundfile as sf, torch, librosa
torch.set_num_threads(os.cpu_count() or 4)
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

# tone -> (exaggeration, cfg_weight, tempo, loudness). exaggeration = emotional intensity, cfg lower = freer pacing.
STYLES = {'narrate': (.55, .40, 1.00, 1.00), 'excited': (.85, .30, 1.05, 1.05), 'playful': (.75, .35, 1.03, 1.00), 'serious': (.40, .50, .97, 1.00),
          'dramatic': (.90, .30, .95, 1.05), 'suspense': (.45, .50, .91, .82), 'whisper': (.30, .60, .90, .62), 'somber': (.35, .55, .93, .90),
          'triumphant': (.95, .30, 1.02, 1.08), 'curious': (.68, .35, 1.00, 1.00), 'warm': (.60, .45, .98, .95)}

def params(style):
    ex, cfg, tempo, gain = STYLES['narrate']
    for t in (style or '').split('+'):
        if t in STYLES: ex, cfg, tempo, gain = STYLES[t]
    if 'slow' in (style or ''): tempo *= .92
    if 'fast' in (style or ''): tempo *= 1.08
    return ex, cfg, tempo, gain

def main():
    a = sys.argv[1:]; only = set(int(x) for x in a[a.index('--only') + 1].split(',')) if '--only' in a else None
    sents = json.load(open(a[0])); ref, out_wav, out_tim = a[1], a[2], a[3]
    m = ChatterboxMultilingualTTS.from_pretrained(device='cpu'); sr = m.sr
    cache = out_wav + '.parts'; os.makedirs(cache, exist_ok=True); parts = []; tim = []; t = 0.0
    for i, s in enumerate(sents):
        p = os.path.join(cache, f'{i:03d}.wav')
        if not os.path.exists(p) or (only and i in only):
            ex, cfg, tempo, gain = params(s.get('style')); txt = re.sub(r'\bng\b', 'nang', s['say']); txt = txt[0].upper() + txt[1:]
            limit = len(txt.split()) * 0.85 + 2.5
            for seed in (11, 23, 37, 51):
                torch.manual_seed(seed + i)
                w = m.generate(txt, language_id='ms', audio_prompt_path=ref, exaggeration=ex, cfg_weight=cfg).squeeze().numpy()
                w, _ = librosa.effects.trim(w, top_db=40)
                if 0.25 * len(txt.split()) <= len(w) / sr <= limit: break      # retry if it rambled or cut off
            if abs(tempo - 1) > .01: w = librosa.effects.time_stretch(w, rate=tempo)
            w = w / max(1e-6, np.sqrt(np.mean(w ** 2))) * 0.11 * gain; w = np.clip(w, -.98, .98)
            sf.write(p, w, sr); print(i + 1, '/', len(sents), s.get('style') or 'narrate', '%.1fs' % (len(w) / sr), flush=True)
        w, _ = sf.read(p, dtype='float32')
        t += s.get('pre', 0); parts.append(np.zeros(int(sr * s.get('pre', 0)), np.float32))
        tim.append({'text': s['text'], 'start': round(t, 3), 'end': round(t + len(w) / sr, 3), 'style': s.get('style') or 'narrate'})
        pause = np.zeros(int(sr * s.get('pause', .32)), np.float32); parts += [w, pause]; t += (len(w) + len(pause)) / sr
    sf.write(out_wav, np.concatenate(parts), sr); json.dump(tim, open(out_tim, 'w'), ensure_ascii=False, indent=1); print('dur', round(t, 1))

if __name__ == '__main__':
    main()
