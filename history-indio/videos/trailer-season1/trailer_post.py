#!/usr/bin/env python3
"""Post-step for the trailer, so build_anime.py stays untouched. It adds what the builder cannot do:
  1. date cards on screen during the era flashes ("cards" in shots_fx.json, one per frame of a "keys" montage);
  2. the fiction label on the end card ("Kathang-isip sina Indio at Usman; totoo ang kasaysayan.");
  3. the trailer's own march instead of the builder's 96 bpm bed: the march is re-made on the real timings
     (make_march.py), mixed under the voice at the pipeline's level (music gated RMS = half the voice's, -6 dB, as
     soundtrack.make), with the builder's whooshes on the cuts EXCEPT into and out of the quiet Bagumbayan shot,
     and no low hits;
  4. a held end card (--hold seconds, default 2.5) so the trailer lands in 35-45 s.
usage (from history-indio/): python videos/trailer-season1/trailer_post.py <built.mp4> <voice.mp3> <out.mp4> [--hold 2.5]
Light: one ffmpeg re-encode of a ~40 s 1080x1920 video (the CPU worker runs it after the build)."""
import json, os, subprocess, sys, tempfile
import numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..', 'pipeline')); sys.path.insert(0, HERE)
import soundtrack, make_march
LABEL = 'Kathang-isip sina Indio at Usman; totoo ang kasaysayan.'
a = sys.argv[1:]; built, voice, out = [os.path.abspath(x) for x in a[:3]]; hold = float(a[a.index('--hold') + 1]) if '--hold' in a else 2.5
tim = json.load(open(os.path.join(HERE, 'timings.json'))); FX = json.load(open(os.path.join(HERE, 'shots_fx.json')))

# the builder's shot list (same rules as build_anime.py), with the line each shot belongs to
total = tim[-1]['end'] + 0.8; shots = []
for i, s in enumerate(tim):
    st = 0.0 if i == 0 else s['start']; en = tim[i + 1]['start'] if i + 1 < len(tim) else total; cfg = FX.get(str(i), {})
    if cfg.get('keys'):
        step = (en - st) / len(cfg['keys']); shots += [(i, j, st + j * step, st + (j + 1) * step) for j in range(len(cfg['keys']))]
    elif en - st > 6.2: mid = st + (en - st) * 0.52; shots += [(i, 0, st, mid), (i, 1, mid, en)]
    else: shots.append((i, 0, st, en))
quiet = {i for i, s in enumerate(tim) if FX.get(str(i), {}).get('quiet')}

# audio: voice + march + whooshes
SR = soundtrack.SR; tmp = tempfile.mkdtemp()
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', voice, '-ac', '1', '-ar', str(SR), f'{tmp}/v.wav'], check=True)
v, _ = sf.read(f'{tmp}/v.wav', dtype='float32'); dur = total + hold; n = int(dur * SR); v = np.pad(v, (0, max(0, n - len(v))))[:n]
make_march.make(tim, f'{tmp}/m.wav', hold); mu, _ = sf.read(f'{tmp}/m.wav', dtype='float32'); mu = np.pad(mu, (0, max(0, n - len(mu))))[:n]
cuts = [sh[2] for k, sh in enumerate(shots[1:], 1) if sh[0] not in quiet and shots[k - 1][0] not in quiet]
fx = soundtrack.sfx(dur, cuts, [])[:n]
rv = soundtrack.gated_rms(v); mu *= 0.5 * rv / soundtrack.gated_rms(mu); fx *= 0.5 * rv / soundtrack.gated_rms(fx)
pk = 0.7 * np.abs(v).max(); fx = np.clip(fx, -pk, pk); mix = v + mu + fx; mix *= 0.89 / np.abs(mix).max()
sf.write(f'{tmp}/mix.wav', mix, SR)
db = lambda x: round(20 * np.log10(x), 1)
print('mix: music vs voice %s dB, sfx vs voice %s dB, %.1f s' % (db(soundtrack.gated_rms(mu) / rv), db(soundtrack.gated_rms(fx) / rv), dur))

# on-screen text: date cards and the fiction label
ts = lambda t: '%d:%02d:%05.2f' % (t // 3600, t % 3600 // 60, t % 60)
ev = []
for i, j, st, en in shots:
    cards = FX.get(str(i), {}).get('cards')
    if cards and j < len(cards): ev.append(f'Dialogue: 1,{ts(st + 0.08)},{ts(en - 0.04)},Card,,0,0,0,,{{\\fad(60,80)}}{cards[j]}')
ev.append(f'Dialogue: 1,{ts(total - 2.4)},{ts(dur)},Label,,0,0,0,,{{\\fad(300,0)}}{LABEL}')
open(f'{tmp}/cards.ass', 'w', encoding='utf-8').write("""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Card,DejaVu Sans,68,&H004DD3FF,&H004DD3FF,&H001F121F,&H00000000,1,0,0,0,100,100,2,0,3,18,0,8,60,60,330,1
Style: Label,DejaVu Sans,40,&H00DCF6FF,&H00DCF6FF,&H001F121F,&H96000000,1,0,0,0,100,100,0,0,1,4,2,8,90,90,880,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + '\n'.join(ev) + '\n')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', built, '-i', f'{tmp}/mix.wav', '-map', '0:v', '-map', '1:a',
                '-vf', f'tpad=stop_mode=clone:stop_duration={hold},ass=cards.ass', '-c:v', 'libx264', '-crf', '21', '-maxrate', '5000k',
                '-bufsize', '10000k', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], check=True, cwd=tmp)
print('wrote', out, '%.1f s;' % dur, len(ev) - 1, 'date cards + fiction label')
