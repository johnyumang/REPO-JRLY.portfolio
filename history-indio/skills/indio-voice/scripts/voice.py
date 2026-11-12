#!/usr/bin/env python3
"""Directed Filipino/Taglish read in the narrator's voice with OmniVoice (k2-fsa/OmniVoice, Apache-2.0, Hugging Face).
usage: voice.py sentences.json narrator_ref.wav out.wav timings.json [--only 3,7] [--ref-text "what the sample says"]
sentences.json: [{"text": shown text, "say": spoken spelling (may hold reaction tags), "style": "excited+slow", "pause": 0.3, "pre": 0}]
Sentences are cached in <out.wav>.parts so an interrupted run resumes; delete a part (or use --only) to redo it."""
import json, os, sys, numpy as np, soundfile as sf, torch, librosa
torch.set_num_threads(os.cpu_count() or 4)
from omnivoice import OmniVoice

# tone -> (speed, loudness). OmniVoice has no emotion dial; tone tags shape pace and level,
# and the reaction tags below are real sounds the model performs.
STYLES = {'narrate': (1.00, 1.00), 'excited': (1.07, 1.06), 'playful': (1.04, 1.00), 'serious': (.97, 1.00), 'dramatic': (.94, 1.06), 'suspense': (.90, .84),
          'whisper': (.88, .62), 'somber': (.92, .90), 'triumphant': (1.03, 1.10), 'curious': (1.00, 1.00), 'warm': (.97, .95)}
REACTIONS = ['[laughter]', '[sigh]', '[confirmation-en]', '[question-en]', '[question-ah]', '[question-oh]', '[question-ei]', '[question-yi]',
             '[surprise-ah]', '[surprise-oh]', '[surprise-wa]', '[surprise-yo]', '[dissatisfaction-hnn]']

def params(style):
    speed, gain = STYLES['narrate']
    for t in (style or '').split('+'):
        if t in STYLES: speed, gain = STYLES[t]
    if 'slow' in (style or ''): speed *= .92
    if 'fast' in (style or ''): speed *= 1.08
    speed *= float(os.environ.get('HI_VOICE_SPEED', 1))                      # overall pace, e.g. HI_VOICE_SPEED=1.15 when the read feels slow
    return speed, gain

def main():
    a = sys.argv[1:]; only = set(int(x) for x in a[a.index('--only') + 1].split(',')) if '--only' in a else None
    sents = json.load(open(a[0])); ref, out_wav, out_tim = a[1], a[2], a[3]
    ref_text = a[a.index('--ref-text') + 1] if '--ref-text' in a else (open(os.path.splitext(ref)[0] + '.txt').read().strip() if os.path.exists(os.path.splitext(ref)[0] + '.txt') else None)
    cache = out_wav + '.parts'; os.makedirs(cache, exist_ok=True); m = None
    for i, s in enumerate(sents):
        p = os.path.join(cache, f'{i:03d}.wav')
        if os.path.exists(p) and not (only and i in only): continue
        if m is None:
            m = OmniVoice.from_pretrained('k2-fsa/OmniVoice', device_map='cpu', dtype=torch.float32)
            if ref_text is None: m.load_asr_model()                      # transcribes the sample itself
            prompt = m.create_voice_clone_prompt(ref_audio=ref, ref_text=ref_text)
        speed, gain = params(s.get('style')); txt = s['say'][0].upper() + s['say'][1:]
        w = np.asarray(m.generate(text=txt, language='fil', voice_clone_prompt=prompt, speed=speed, seed=7 + i)[0], dtype=np.float32)
        w, _ = librosa.effects.trim(w, top_db=40)
        w = np.clip(w / max(1e-6, np.sqrt(np.mean(w ** 2))) * 0.11 * gain, -.98, .98)
        sf.write(p, w, m.sampling_rate); print(i + 1, '/', len(sents), s.get('style') or 'narrate', '%.1fs' % (len(w) / m.sampling_rate), flush=True)
    parts = []; tim = []; t = 0.0; sr = None
    for i, s in enumerate(sents):
        w, sr = sf.read(os.path.join(cache, f'{i:03d}.wav'), dtype='float32')
        pre = s.get('pre', 0) or 0; t += pre; parts.append(np.zeros(int(sr * pre), np.float32))
        tim.append({'text': s['text'], 'start': round(t, 3), 'end': round(t + len(w) / sr, 3), 'style': s.get('style') or 'narrate'})
        pause = np.zeros(int(sr * s.get('pause', .32)), np.float32); parts += [w, pause]; t += (len(w) + len(pause)) / sr
    sf.write(out_wav, np.concatenate(parts), sr); json.dump(tim, open(out_tim, 'w'), ensure_ascii=False, indent=1); print('dur', round(t, 1), flush=True)

if __name__ == '__main__':
    main()
