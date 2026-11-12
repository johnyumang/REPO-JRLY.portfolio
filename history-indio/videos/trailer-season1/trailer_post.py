#!/usr/bin/env python3
"""Post-step for the trailer, so build_anime.py stays untouched. It adds what the builder cannot do:
  1. date cards on screen during the era flashes ("cards" in shots_fx.json, one per frame of a "keys" montage);
  2. the fiction label on the end card ("Kathang-isip sina Indio at Usman; totoo ang kasaysayan.");
  3. the music instead of the builder's 96 bpm bed: by default the trailer's own march, re-made on the real timings
     (make_march.py); with --music, that file instead. Either way: music gated RMS 6 dB under the voice's (as
     soundtrack.make), a further 8 dB down under the two "quiet" lines of shots_fx.json (Bagumbayan, Huling Tala) with
     0.4 s ramps on their real timings, the builder's whooshes on the cuts EXCEPT into and out of the quiet Bagumbayan
     shot, no low hits;
  4. a held end card (--hold seconds, default 2.5) so the trailer lands in 35-45 s;
  5. --credit "<text>": a small credit line near the bottom of the end card (e.g. the music credit).
With --music, the file is placed so its FINAL HIT lands where the held end card starts (the end of the built video,
after the last line), and its ring-out covers the hold: the start is shifted, the intro trimmed with a short fade-in,
or the track padded with silence, as needed. The hit is found automatically (the strongest onset in the last 8 s of
the file) or given with --hit <seconds from the start of the file>.
The final mix is mastered to -16 LUFS integrated, true peak under -1 dBTP (4x oversampled limiter), stereo.
usage (from history-indio/): python videos/trailer-season1/trailer_post.py <built.mp4> <voice.mp3> <out.mp4>
          [--timings voice_timings.json] [--hold 2.5] [--music file] [--hit 40.43] [--credit "text"]
  --timings: sentence timings of the voice (default timings.json beside this script; keep a cloned voice's timings
  OUT of the repo and pass them here).
Light: one ffmpeg re-encode of a ~40 s 1080x1920 video (the CPU worker runs it after the build)."""
import json, os, subprocess, sys, tempfile
import numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..', 'pipeline')); sys.path.insert(0, HERE)
import soundtrack, make_march
LABEL = 'Kathang-isip sina Indio at Usman; totoo ang kasaysayan.'
a = sys.argv[1:]; built, voice, out = [os.path.abspath(x) for x in a[:3]]
opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
hold = float(opt('--hold', 2.5)); music = opt('--music'); credit = opt('--credit'); hit_arg = opt('--hit')
TARGET_LUFS, TP_MAX, DUCK_DB, RAMP = -16.0, -1.0, 8.0, 0.4
tim = json.load(open(os.path.abspath(opt('--timings', os.path.join(HERE, 'timings.json'))))); FX = json.load(open(os.path.join(HERE, 'shots_fx.json')))

# the builder's shot list (same rules as build_anime.py), with the line each shot belongs to
total = tim[-1]['end'] + 0.8; shots = []
for i, s in enumerate(tim):
    st = 0.0 if i == 0 else s['start']; en = tim[i + 1]['start'] if i + 1 < len(tim) else total; cfg = FX.get(str(i), {})
    if cfg.get('keys'):
        step = (en - st) / len(cfg['keys']); shots += [(i, j, st + j * step, st + (j + 1) * step) for j in range(len(cfg['keys']))]
    elif en - st > 6.2: mid = st + (en - st) * 0.52; shots += [(i, 0, st, mid), (i, 1, mid, en)]
    else: shots.append((i, 0, st, en))
quiet = {i for i, s in enumerate(tim) if FX.get(str(i), {}).get('quiet')}

# audio: voice + music + whooshes
SR = soundtrack.SR; tmp = tempfile.mkdtemp(); dur = total + hold; n = int(round(dur * SR))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', voice, '-ac', '1', '-ar', str(SR), f'{tmp}/v.wav'], check=True)
v, _ = sf.read(f'{tmp}/v.wav', dtype='float32'); v = np.pad(v, (0, max(0, n - len(v))))[:n]
place = ''
if music:
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.abspath(music), '-ac', '2', '-ar', str(SR), f'{tmp}/m.wav'], check=True)
    m, _ = sf.read(f'{tmp}/m.wav', dtype='float32', always_2d=True)
    if hit_arg is not None: hit = float(hit_arg)
    else:                                                                  # final hit = strongest onset in the last 8 s (onset strength, 10 ms hop)
        import librosa
        mm = m.mean(1); hop = 441; o = librosa.onset.onset_strength(y=mm, sr=SR, hop_length=hop)
        t_o = np.arange(len(o)) * hop / SR; w = t_o > len(mm) / SR - 8; k = int(np.argmax(np.where(w, o, 0))); hit = float(t_o[k])
        # refine to the sample where the hit's envelope rises (within 60 ms before the onset frame)
        seg = np.abs(mm[max(0, int((hit - .06) * SR)):int((hit + .03) * SR)]); thr = 0.5 * seg.max(); hit = max(0, hit - .06) + int(np.argmax(seg > thr)) / SR
    shift = total - hit                                                    # music time 0 sits at video time `shift`
    if shift < 0:                                                          # trim the intro, short fade-in
        m = m[int(round(-shift * SR)):].copy(); f = int(0.25 * SR); m[:f] *= np.linspace(0, 1, f)[:, None]
        place = 'trimmed the first %.2f s of the music (0.25 s fade-in)' % -shift
    else:
        m = np.concatenate([np.zeros((int(round(shift * SR)), 2), np.float32), m]); place = 'music starts %.2f s into the video' % shift
    ring = len(m) / SR - total                                             # music left after the hit
    if len(m) < n: m = np.concatenate([m, np.zeros((n - len(m), 2), np.float32)]); place += '; padded %.2f s of silence after the ring-out' % (dur - total - ring)
    else: f = int(min(0.6, hold) * SR); m = m[:n].copy(); m[-f:] *= np.linspace(1, 0, f)[:, None]
    place = 'final hit at %.2f s of the file -> %.2f s of the video (end-card hold starts); ring-out %.2f s over a %.2f s hold; ' % (hit, total, ring, hold) + place
    mu = m
else:
    make_march.make(tim, f'{tmp}/m.wav', hold); mo, _ = sf.read(f'{tmp}/m.wav', dtype='float32'); mo = np.pad(mo, (0, max(0, n - len(mo))))[:n]
    mu = np.stack([mo, mo], 1); place = 'built-in march (make_march.py) on the real timings'
cuts = [sh[2] for k, sh in enumerate(shots[1:], 1) if sh[0] not in quiet and shots[k - 1][0] not in quiet]
fx = soundtrack.sfx(dur, cuts, [])[:n]; fx = np.pad(fx, (0, n - len(fx)))
rv = soundtrack.gated_rms(v); mu *= 0.5 * rv / soundtrack.gated_rms(mu.mean(1)); fx *= 0.5 * rv / soundtrack.gated_rms(fx)
# duck the music a further 8 dB under the quiet lines (0.4 s ramps, fully down from the first word to the last)
g = np.zeros(n, np.float32); tt = np.arange(n) / SR
for i in sorted(quiet):
    s0, s1 = tim[i]['start'], tim[i]['end']
    g = np.maximum(g, np.clip(np.minimum((tt - (s0 - RAMP)) / RAMP, ((s1 + RAMP) - tt) / RAMP), 0, 1).astype(np.float32))
duck = 10 ** (-DUCK_DB * g / 20); mu *= duck[:, None]
pk = 0.7 * np.abs(v).max(); fx = np.clip(fx, -pk, pk)
mix = v[:, None] + mu + fx[:, None]

def ebu(path):
    o = subprocess.run(['ffmpeg', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    o = o[o.rindex('Summary:'):]; gg = lambda k: float(o.split(k)[1].split()[0]); return gg('I:'), gg('Peak:')
def master(x, gain_db):                                                    # gain, then a 4x-oversampled true-peak limiter
    sf.write(f'{tmp}/pre.wav', x * 10 ** (gain_db / 20), SR, subtype='FLOAT')
    lim = 10 ** ((TP_MAX - 0.5) / 20)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{tmp}/pre.wav', '-af', f'aresample=176400:resampler=soxr,alimiter=limit={lim:.5f}:attack=2:release=80:level=false:latency=true,aresample={SR}:resampler=soxr',
                    '-c:a', 'pcm_f32le', f'{tmp}/mix.wav'], check=True)
    return ebu(f'{tmp}/mix.wav')
sf.write(f'{tmp}/pre.wav', mix, SR, subtype='FLOAT'); I0, _ = ebu(f'{tmp}/pre.wav'); gdb = TARGET_LUFS - I0
for _ in range(4):
    I, TP = master(mix, gdb)
    if abs(I - TARGET_LUFS) <= 0.1: break
    gdb += TARGET_LUFS - I
db = lambda x: round(20 * np.log10(x), 1)
print('music:', place)
print('mix: music vs voice %s dB (gated RMS, before the duck), sfx vs voice %s dB, duck -%.0f dB under lines %s, master gain %+.2f dB -> %.2f LUFS, true peak %.2f dBFS, %.2f s' % (
      db(soundtrack.gated_rms(mu.mean(1) / duck) / rv), db(soundtrack.gated_rms(fx) / rv), DUCK_DB, sorted(quiet), gdb, I, TP, dur))

# on-screen text: date cards, the fiction label, the credit
ts = lambda t: '%d:%02d:%05.2f' % (t // 3600, t % 3600 // 60, t % 60)
ev = []
for i, j, st, en in shots:
    cards = FX.get(str(i), {}).get('cards')
    if cards and j < len(cards): ev.append(f'Dialogue: 1,{ts(st + 0.08)},{ts(en - 0.04)},Card,,0,0,0,,{{\\fad(60,80)}}{cards[j]}')
ncards = len(ev)
ev.append(f'Dialogue: 1,{ts(total - 2.4)},{ts(dur)},Label,,0,0,0,,{{\\fad(300,0)}}{LABEL}')
if credit: ev.append(f'Dialogue: 1,{ts(tim[-1]["end"] + 0.1)},{ts(dur)},Credit,,0,0,0,,{{\\fad(300,0)}}{credit}')   # after the last line, so it never sits on its subtitle
open(f'{tmp}/cards.ass', 'w', encoding='utf-8').write("""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Card,DejaVu Sans,68,&H004DD3FF,&H004DD3FF,&H001F121F,&H00000000,1,0,0,0,100,100,2,0,3,18,0,8,60,60,330,1
Style: Label,DejaVu Sans,40,&H00DCF6FF,&H00DCF6FF,&H001F121F,&H96000000,1,0,0,0,100,100,0,0,1,4,2,8,90,90,880,1
Style: Credit,DejaVu Sans,30,&H00F0F0F0,&H00F0F0F0,&H001F121F,&H96000000,0,0,0,0,100,100,0,0,1,3,1,2,110,110,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + '\n'.join(ev) + '\n')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', built, '-i', f'{tmp}/mix.wav', '-map', '0:v', '-map', '1:a',
                '-vf', f'tpad=stop_mode=clone:stop_duration={hold},ass=cards.ass', '-c:v', 'libx264', '-crf', '21', '-maxrate', '5000k',
                '-bufsize', '10000k', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], check=True, cwd=tmp)
print('wrote', out, '%.1f s;' % dur, ncards, 'date cards + fiction label' + (' + credit' if credit else ''))
