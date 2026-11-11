#!/usr/bin/env python3
"""Transcribe each sentence of a generated read with Whisper and report the word match (clarity check only).
usage: check_voice.py out.wav timings.json"""
import json, re, sys, difflib, librosa
from transformers import pipeline
asr = pipeline('automatic-speech-recognition', model='openai/whisper-small', device='cpu')
y, sr = librosa.load(sys.argv[1], sr=16000); tim = json.load(open(sys.argv[2])); norm = lambda s: re.sub(r'[^a-zñ0-9 ]', '', s.lower().replace('-', ' ')).split()
tot = 0; low = []
for i, t in enumerate(tim):
    seg = y[int(t['start'] * sr):int(t['end'] * sr)]
    hyp = asr({'raw': seg, 'sampling_rate': sr}, generate_kwargs={'language': 'tagalog', 'task': 'transcribe'})['text']
    r = difflib.SequenceMatcher(None, norm(t['text']), norm(hyp)).ratio(); tot += r
    if r < .7: low.append(i); print(f'LOW {i} {r:.0%} | want: {t["text"]} | heard: {hyp.strip()}')
print(f'average match {tot / len(tim):.0%}; low sentences: {low}')
