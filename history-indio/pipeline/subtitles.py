#!/usr/bin/env python3
"""timings.json -> burned-in style subtitles (.ass): short upper-case chunks, timed inside each sentence.
usage: subtitles.py timings.json out.ass
Sits at about two-thirds height: above the bottom komiks caption and clear of the Facebook/Reels buttons."""
import json, sys

def ts(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f'{h}:{m:02d}:{s:05.2f}'

def chunks(words, max_chars=20, max_words=4):
    out, cur = [], []
    for w in words:
        if cur and (len(' '.join(cur + [w])) > max_chars or len(cur) >= max_words): out.append(cur); cur = []
        cur.append(w)
    if cur:
        if out and len(cur) == 1 and len(' '.join(out[-1] + cur)) <= max_chars + 2: out[-1] += cur     # no orphan word, but never wider than the frame
        else: out.append(cur)
    return out

def make(timings, path):
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,DejaVu Sans,74,&H0000E4FF,&H0000E4FF,&H001F121F,&H961F121F,1,0,0,0,100,100,0,0,1,7,3,2,60,60,650,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for s in timings:
        cs = chunks(s['text'].replace('\n', ' ').split()); total = sum(len(' '.join(c)) for c in cs); t = s['start']
        for i, c in enumerate(cs):
            txt = ' '.join(c); d = (s['end'] - s['start']) * len(txt) / total; end = s['end'] if i == len(cs) - 1 else t + d
            lines.append(f"Dialogue: 0,{ts(t)},{ts(end + (0.12 if i == len(cs) - 1 else 0))},Sub,,0,0,0,,{{\\fad(40,0)}}{txt.upper()}")
            t = end
    open(path, 'w', encoding='utf-8').write(head + '\n'.join(lines) + '\n'); return len(lines)

if __name__ == '__main__':
    print(make(json.load(open(sys.argv[1])), sys.argv[2]), 'subtitle lines')
