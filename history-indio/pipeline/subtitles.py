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

TAG_COLOURS = ['&H0000E4FF', '&H00FFD27A', '&H008CF08C', '&H00B49BFF', '&H0060B4FF', '&H00F0A0F0', '&H00D0D0D0', '&H0080FFFF', '&H00FF9A9A', '&H0090C8FF']

def make(timings, path):
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,DejaVu Sans,74,&H0000E4FF,&H0000E4FF,&H001F121F,&H961F121F,1,0,0,0,100,100,0,0,1,7,3,2,60,60,650,1
Style: Shout,DejaVu Sans,100,&H0000E4FF,&H0000E4FF,&H001F121F,&H961F121F,1,0,0,0,100,100,1,0,1,9,4,2,40,40,640,1
Style: Who,DejaVu Sans,40,&H00FFFFFF,&H00FFFFFF,&H001F121F,&H961F121F,1,0,0,0,100,100,2,0,1,5,2,2,60,60,742,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    who = [s.get('speaker') for s in timings]; tag = len({w for w in who if w}) > 1          # several voices: a small name tag over each line
    order = list(dict.fromkeys(w for w in who if w))
    for s in timings:
        if tag and s.get('speaker'):                                                         # colour per speaker (ASS colours are &HBBGGRR)
            col = TAG_COLOURS[order.index(s['speaker']) % len(TAG_COLOURS)]; name = s['speaker'] + (' (SA ATIN)' if s.get('aside') else '')
            lines.append(f"Dialogue: 1,{ts(s['start'])},{ts(s['end'] + 0.12)},Who,,0,0,{790 if s.get('style') == 'shout' else 0},,{{\\c{col}}}{name}")
        shout = tag and s.get('style') == 'shout'                                            # big type: shorter chunks so a shout stays inside the frame
        cs = chunks(s['text'].replace('\n', ' ').split(), *((15, 3) if shout else ())); total = sum(len(' '.join(c)) for c in cs); t = s['start']
        for i, c in enumerate(cs):
            txt = ' '.join(c); d = (s['end'] - s['start']) * len(txt) / total; end = s['end'] if i == len(cs) - 1 else t + d
            st = 'Shout' if shout else 'Sub'                   # a shouted line of a multi-voice episode: big, centred
            lines.append(f"Dialogue: 0,{ts(t)},{ts(end + (0.12 if i == len(cs) - 1 else 0))},{st},,0,0,0,,{txt.upper()}")
            t = end
    # no fade-in: a 40 ms fade left one half-transparent frame per page, seen as a ghost subtitle on a pause (owner, Ep17, 14 Nov)
    open(path, 'w', encoding='utf-8').write(head + '\n'.join(lines) + '\n'); return len(lines)

if __name__ == '__main__':
    print(make(json.load(open(sys.argv[1])), sys.argv[2]), 'subtitle lines')
