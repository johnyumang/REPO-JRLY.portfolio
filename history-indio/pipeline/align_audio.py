#!/usr/bin/env python3
"""Time a script to a finished voice recording. Whisper gives word timestamps; the script's sentences are
matched to those words, so every shot and subtitle follows the recording.
usage: align_audio.py voice.(mp3|wav) sentences.json timings.json"""
import json, re, sys, difflib, librosa
from transformers import pipeline
voice, sent_path, out = sys.argv[1:4]
norm = lambda w: re.sub(r'[^a-zñ0-9]', '', w.lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u'))
y, sr = librosa.load(voice, sr=16000, mono=True); dur = len(y) / sr
asr = pipeline('automatic-speech-recognition', model='openai/whisper-small', device='cpu', chunk_length_s=28, stride_length_s=4)
res = asr({'raw': y, 'sampling_rate': sr}, return_timestamps='word', generate_kwargs={'language': 'tagalog', 'task': 'transcribe'})
words = [(norm(c['text']), c['timestamp'][0], c['timestamp'][1] if c['timestamp'][1] is not None else c['timestamp'][0] + 0.3) for c in res['chunks'] if norm(c['text'])]
print('heard', len(words), 'words in %.1fs:' % dur, res['text'][:200])
sents = json.load(open(sent_path)); toks = []; owner = []
for i, s in enumerate(sents):
    for w in s['text'].split():
        if norm(w): toks.append(norm(w)); owner.append(i)
sm = difflib.SequenceMatcher(None, toks, [w[0] for w in words], autojunk=False); t_of = {}
for a, b, n in sm.get_matching_blocks():
    for k in range(n): t_of[a + k] = (words[b + k][1], words[b + k][2])
matched = len(t_of) / len(toks); print('matched %.0f%% of script words' % (matched * 100))
idx = sorted(t_of); first = {}; last = {}
for j in idx:
    first.setdefault(owner[j], t_of[j][0]); last[owner[j]] = t_of[j][1]
tim = []
for i, s in enumerate(sents):                      # sentences with no matched word are placed between their neighbours
    st = first.get(i); en = last.get(i)
    tim.append({'text': s['text'], 'start': st, 'end': en, 'style': s.get('style') or 'narrate'})
for i, t in enumerate(tim):
    if t['start'] is None:
        prev = tim[i - 1]['end'] if i else 0.0; nxt = next((x['start'] for x in tim[i + 1:] if x['start'] is not None), dur)
        t['start'] = prev + 0.05; t['end'] = max(t['start'] + 0.3, min(nxt - 0.05, t['start'] + 3))
for i in range(len(tim) - 1):                      # keep order and no overlaps
    if tim[i]['end'] > tim[i + 1]['start']: tim[i]['end'] = tim[i + 1]['start'] - 0.02
    if tim[i]['end'] <= tim[i]['start']: tim[i]['end'] = tim[i]['start'] + 0.2
for t in tim: t['start'] = round(float(t['start']), 3); t['end'] = round(float(t['end']), 3)
json.dump(tim, open(out, 'w'), ensure_ascii=False, indent=1)
miss = [i for i in range(len(sents)) if i not in first]; print('sentences with no direct match:', miss); print('last sentence ends %.1fs of %.1fs' % (tim[-1]['end'], dur))
