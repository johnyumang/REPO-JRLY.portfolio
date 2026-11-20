#!/usr/bin/env python3
"""Three original march candidates for the Season 1 trailer, rendered with real sampled instruments.
Each one is composed here note by note (original tunes; NOT Lupang Hinirang and not any existing song), written as MIDI
and rendered with FluidSynth using the FluidR3_GM soundfont (Frank Wen, MIT licence; Debian/Ubuntu package
fluid-soundfont-gm). Arrangement: snare-roll intro with gong, tune (A), counter-melody section (B) with kulintang-like
ostinato, drum break, tune again with counter-melody and glockenspiel, held final chord with roll, last tutti hit.
  1 banda    - brass band march, B-flat, 128 bpm (trumpets, trombones, tuba, horns, clarinet, banjo tremolo)
  2 rondalla - rondalla-led march, C, 132 bpm (bandurria-like tremolo lead, brass stabs, piccolo descant)
  3 bayan    - broad cinematic march, E-flat, 124 bpm (horns + strings, taiko, gongs, kulintang lead in the break)
usage: make_music_candidates.py OUTDIR [--sf2 /usr/share/sounds/sf2/FluidR3_GM.sf2] [--only banda,rondalla,bayan]
needs: apt install fluidsynth fluid-soundfont-gm; pip install mido numpy soundfile pyloudnorm scipy
Output: OUTDIR/<name>.mid, OUTDIR/<name>.wav (44.1 kHz stereo, -14 LUFS integrated, true peak <= -1.5 dBTP)."""
import argparse, os, subprocess, sys
import numpy as np, soundfile as sf, mido, pyloudnorm as pyln
from scipy.signal import resample_poly

TPB = 480
MAJ = [0, 2, 4, 5, 7, 9, 11]

def deg(tok, tonic):
    """'5' -> 5th degree, "3'" an octave up, '5,' an octave down."""
    up = tok.count("'") - tok.count(',')
    d = int(tok.strip("',"))
    return tonic + MAJ[d - 1] + 12 * up

def parse(bar, tonic):
    out = []; t = 0.0
    toks = bar.split()
    for i in range(0, len(toks), 2):
        n, d = toks[i], float(toks[i + 1])
        if n != 'r': out.append((t, d, deg(n, tonic)))
        t += d
    assert abs(t - 4) < 1e-6, (bar, t)
    return out

def triad(root_deg, tonic):
    r = root_deg - 1
    return [tonic + MAJ[(r + k) % 7] + 12 * ((r + k) // 7) for k in (0, 2, 4)]

class Song:
    def __init__(s, bpm, rng):
        s.bpm = bpm; s.ev = []; s.rng = rng; s.progs = {}
    def prog(s, ch, p): s.progs[ch] = p
    def note(s, ch, beat, dur, pitch, vel):
        if pitch is None: return
        vel = int(np.clip(vel + s.rng.integers(-4, 5), 1, 127))
        s.ev.append((beat, 1, ch, int(pitch), vel)); s.ev.append((beat + max(dur, 0.05), 0, ch, int(pitch), 0))
    def cc(s, ch, beat, num, val): s.ev.append((beat, 2, ch, num, val))
    def write(s, path):
        mid = mido.MidiFile(ticks_per_beat=TPB); tr = mido.MidiTrack(); mid.tracks.append(tr)
        tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(s.bpm), time=0))
        for ch, p in s.progs.items():
            tr.append(mido.Message('program_change', channel=ch, program=p, time=0))
            tr.append(mido.Message('control_change', channel=ch, control=91, value=50, time=0))   # reverb send
            tr.append(mido.Message('control_change', channel=ch, control=93, value=0, time=0))    # no chorus
        last = 0
        for b, kind, ch, a, v in sorted(s.ev, key=lambda e: (e[0], e[1])):
            tick = int(round(b * TPB)); dt = tick - last; last = tick
            if kind == 2: tr.append(mido.Message('control_change', channel=ch, control=a, value=v, time=dt))
            else: tr.append(mido.Message('note_on', channel=ch, note=a, velocity=v, time=dt))
        mid.save(path)

DR = 9; KICK, SNARE, CRASH, CRASH2, CHINA, SPLASH = 36, 38, 49, 57, 52, 55

TUNES = {
 'banda': dict(bpm=128, tonic=58, prog=dict(lead=56, lead2=71, counter=60, stab=57, bass=58, trem=105, kul=114, timp=47, glock=9, str=48, gong=14, taiko=116),
  A=["1 0.5 3 0.5 5 1 5 0.75 6 0.25 5 1", "3' 1.5 2' 0.5 1' 1 5 1", "6 0.75 6 0.25 1' 1 6 1 4 1", "5 2 3 1 1 1",
     "2 0.75 3 0.25 4 1 6 1 4 1", "5 0.75 6 0.25 7 1 2' 1 7 1", "1' 1.5 7 0.5 1' 1 3' 1", "2' 3 r 1"],
  Ach=[1, 1, 4, 1, 2, 5, 1, 5],
  Aend=["3' 1 2' 1 7 1 2' 1", "1' 3 r 1"], Aendch=[5, 1],
  B=["3' 0.5 2' 0.5 1' 0.5 7 0.5 6 2", "1' 0.5 7 0.5 6 0.5 5 0.5 4 2", "6 0.5 5 0.5 4 0.5 3 0.5 2 1 4 1", "5 1 7 1 2' 1 5' 1"],
  Bch=[6, 4, 2, 5], lead_vel=100, trem_lead=False, drums=1.0),
 'rondalla': dict(bpm=132, tonic=60, prog=dict(lead=105, lead2=25, counter=60, stab=61, bass=58, trem=24, kul=114, timp=47, glock=72, str=48, gong=14, taiko=116),
  A=["5 0.5 5 0.5 1' 1 7 0.5 6 0.5 5 1", "4 0.5 5 0.5 7 1 2' 1 5 1", "6 0.5 7 0.5 1' 1 3' 1 1' 1", "6 1.5 4 0.5 6 1 1' 1",
     "5 0.5 3' 0.5 3' 1 2' 0.5 1' 0.5 5 1", "6 0.5 1' 0.5 2' 1 4' 1 2' 1", "3' 1.5 2' 0.5 1' 1 3' 1", "2' 3 r 1"],
  Ach=[1, 5, 6, 4, 1, 2, 1, 5],
  Aend=["5' 1.5 4' 0.5 2' 1 7 1", "1' 3 r 1"], Aendch=[5, 1],
  B=["4' 1 3' 0.5 2' 0.5 1' 1 6 1", "5 1 1' 0.5 3' 0.5 5' 2", "4' 1 2' 1 6 1 4 1", "5 1 6 0.5 7 0.5 2' 1 5 1"],
  Bch=[4, 1, 2, 5], lead_vel=108, trem_lead=True, drums=0.85),
 'bayan': dict(bpm=124, tonic=51, prog=dict(lead=60, lead2=56, counter=57, stab=61, bass=58, trem=105, kul=114, timp=47, glock=9, str=48, gong=14, taiko=116),
  A=["1 1.5 2 0.5 3 1 5 1", "5 1.5 3 0.5 7 1 5 1", "6 1.5 5 0.5 4 1 1' 1", "5 3 5 0.5 6 0.5",
     "1' 1.5 7 0.5 6 1 3 1", "4 1.5 6 0.5 2' 1 1' 1", "7 1.5 1' 0.5 2' 1 4' 1", "2' 3 r 1"],
  Ach=[1, 3, 4, 1, 6, 2, 5, 5],
  Aend=["2' 1.5 1' 0.5 7 1 2' 1", "1' 3 r 1"], Aendch=[5, 1],
  B=["1' 1 6 1 4 1 6 1", "2' 1 7 1 5 1 7 1", "3' 1 1' 1 6 1 3' 1", "2' 2 5 1 7 1"],
  Bch=[4, 5, 6, 5], lead_vel=104, trem_lead=False, drums=0.9, strings=True),
}

def compose(name, seed=7):
    T = TUNES[name]; rng = np.random.default_rng(seed); s = Song(T['bpm'], rng); tn = T['tonic']; P = T['prog']
    CH = dict(lead=0, lead2=1, counter=2, stab=3, bass=4, trem=5, kul=6, timp=7, glock=8, str=10, gong=11, taiko=12)
    for k, ch in CH.items(): s.prog(ch, P[k])
    dk = T['drums']
    # ---- form: intro 2 | A 8 | B 4 | break 2 | A' 6 (A1-4 + ending 2) | final hit
    bars = []                                    # (section, melody bar, chord degree)
    bars += [('intro', None, 5)] * 2
    bars += [('A', m, c) for m, c in zip(T['A'], T['Ach'])]
    bars += [('B', m, c) for m, c in zip(T['B'], T['Bch'])]
    bars += [('break', None, 1), ('break', None, 5)]
    bars += [('A2', m, c) for m, c in zip(T['A'][:4] + T['Aend'], T['Ach'][:4] + T['Aendch'])]
    nb = len(bars)
    for i, (sec, mel, ch) in enumerate(bars):
        b0 = 4 * i; tri = triad(ch, tn); root = tri[0]
        bass_root = root - 24 if root - 24 >= 34 else root - 12
        last = i == nb - 1; first_of = i == 0 or bars[i - 1][0] != sec
        # ----- melody
        if mel:
            notes = parse(mel, tn)
            for t, d, p in notes:
                v = T['lead_vel'] + (8 if t % 2 == 0 else 0) - (6 if sec == 'B' else 0)
                art = d * (0.92 if d < 1 else 0.97)
                if sec == 'B':                       # B: tune on the second voice, a little softer
                    s.note(CH['lead2'], b0 + t, art, p, v - 6)
                    if name == 'rondalla': s.note(CH['lead'], b0 + t, art, p, v - 10)
                elif T['trem_lead']:                 # rondalla: bandurria tremolo on every tune note
                    k = 0.0
                    while k < d - 1e-6:
                        s.note(CH['lead'], b0 + t + k, 0.11, p, v - (0 if k == 0 else 14)); k += 0.125
                    s.note(CH['lead2'], b0 + t, art, p, v - 30)
                else:
                    s.note(CH['lead'], b0 + t, art, p, v)
                    if sec == 'A2': s.note(CH['lead2'], b0 + t, art, p - (12 if name == 'banda' else -12 if name == 'bayan' else 0), v - 12)
                if sec == 'A2':                      # glockenspiel / piccolo doubling on the return
                    s.note(CH['glock'], b0 + t, min(d, 0.5), p + 12 if name != 'rondalla' else p + 12, 78)
        # ----- counter-melody (horns / trombones): long chord tones moving by step, in A2 and B
        if sec in ('A2', 'B') and not last:
            hi = sorted([x + 12 if x < tn else x for x in tri])
            s.note(CH['counter'], b0, 1.9, hi[1] - 12, 82); s.note(CH['counter'], b0 + 2, 1.9, hi[2] - 12, 80)
        # ----- bass: oom on 1 and 3 (root / fifth)
        if sec != 'intro' and sec != 'break':
            s.note(CH['bass'], b0, 0.8, bass_root, 100); s.note(CH['bass'], b0 + 2, 0.8, bass_root + 7, 92)
            if last: s.note(CH['bass'], b0, 3.0, bass_root, 105)
        # ----- pah: short brass chord stabs on 2 and 4
        if sec in ('A', 'A2', 'B') and not last:
            for bt in (1, 3):
                for p in tri: s.note(CH['stab'], b0 + bt, 0.35, p - 12, 78 if sec != 'B' else 70)
        # ----- strings pad (bayan always, others in A2)
        if T.get('strings') or sec == 'A2':
            if sec != 'intro' and sec != 'break':
                for p in tri + [root - 12]: s.note(CH['str'], b0, 3.95 if not last else 3.0, p, 70 if T.get('strings') else 58)
        # ----- tremolo strings (rondalla accompaniment)
        if sec in ('A', 'A2', 'B') and not last:
            k = 0.0
            while k < 4 - 1e-6:
                for p in tri[1:]: s.note(CH['trem'], b0 + k, 0.12, p, (64 if k % 1 == 0 else 50) + (8 if name == 'rondalla' else 0))
                k += 0.25
        # ----- kulintang-like ostinato (8ths on chord + pentatonic tones)
        if sec in ('B', 'break', 'A2') and not last:
            pat = [0, 7, 12, 7, 16, 7, 12, 14] if sec != 'break' else [12, 7, 12, 16, 19, 16, 12, 7]
            kroot = root + 12 if root + 12 < tn + 20 else root
            for j, off in enumerate(pat):
                s.note(CH['kul'], b0 + j * 0.5, 0.45, kroot + off, (84 if sec == 'break' else 66) + (10 if j % 2 == 0 else 0))
        # ----- gong accents (low tubular bell + taiko + china) at section starts
        if first_of and sec in ('A', 'B', 'A2'):
            s.note(CH['gong'], b0, 3, tn - 12, 90); s.note(CH['taiko'], b0, 1, tn - 24, 110)
            s.note(DR, b0, 1, CRASH, int(110 * dk)); s.note(DR, b0, 1, CHINA, 60)
        # ----- drums
        if sec == 'intro':
            if i == 0:
                s.note(CH['gong'], b0, 4, tn - 12, 100); s.note(CH['taiko'], b0, 1, tn - 24, 118)
            k = 0.0
            while k < 4 - 1e-6:                      # snare roll, crescendo over 2 bars, stops before the downbeat
                if not (i == 1 and k >= 3.0):
                    s.note(DR, b0 + k, 0.1, SNARE, int((40 + 70 * ((i * 4 + k) / 7)) * dk))
                k += 0.125
            k = 0.0
            while k < 4 - 1e-6:                      # timpani roll on V
                s.note(CH['timp'], b0 + k, 0.2, tn - 24 + 7, int(50 + 50 * ((i * 4 + k) / 8))); k += 0.25
            if i == 1:
                for bt in (3.0, 3.5):
                    s.note(DR, b0 + bt, 0.3, KICK, 115); s.note(DR, b0 + bt, 0.3, SNARE, int(118 * dk))
                    s.note(CH['timp'], b0 + bt, 0.4, tn - 24, 115)
                    for p in triad(5, tn): s.note(CH['stab'], b0 + bt, 0.3, p - 12, 100)
        elif sec == 'break':
            pat = [(0, 120), (0.75, 70), (1, 105), (1.5, 90), (1.75, 70), (2, 115), (2.5, 85), (3, 105), (3.25, 75), (3.5, 95), (3.75, 80)] if i == bars.index(('break', None, 1)) else \
                  [(0, 118), (0.5, 85), (1, 108), (1.5, 88), (2, 112)] + [(2 + k * 0.125, 60 + k * 8) for k in range(8)] + [(3.25, 0)]
            for t, v in pat:
                if v: s.note(DR, b0 + t, 0.1, SNARE, int(v * dk))
            for t in (0, 1, 2, 3): s.note(DR, b0 + t, 0.3, KICK, 108 if t in (0, 2) else 92)
            s.note(CH['taiko'], b0, 0.8, tn - 24, 110); s.note(CH['taiko'], b0 + 2, 0.8, tn - 24 + 7, 100)
            if i == len(bars) - 7:                    # pickup into A': timpani + kick + stab on 4-and
                for bt in (3.5,): s.note(CH['timp'], b0 + bt, 0.4, tn - 24 + 7, 112); s.note(DR, b0 + bt, 0.3, KICK, 118)
        elif last:
            k = 0.0
            while k < 3.0 - 1e-6:                    # held tonic with snare roll + timpani roll
                s.note(DR, b0 + k, 0.1, SNARE, int((60 + 50 * k / 3) * dk)); s.note(CH['timp'], b0 + k, 0.2, tn - 24, int(70 + 35 * k / 3)); k += 0.125
            s.note(DR, b0, 1, KICK, 118); s.note(DR, b0, 2, CRASH2, int(118 * dk))
        else:
            # march pattern: kick 1 & 3, snare backbeat with 16th ruffs, light cymbal on 2 & 4
            for t in (0, 2): s.note(DR, b0 + t, 0.3, KICK, 110)
            for t in (1, 3): s.note(DR, b0 + t, 0.3, KICK, 80)
            for t, v in [(0, 72), (0.5, 60), (1, 108), (1.75, 62), (2, 74), (2.5, 66), (2.75, 70), (3, 112), (3.5, 64), (3.75, 80)]:
                s.note(DR, b0 + t, 0.1, SNARE, int(v * dk * (0.85 if sec == 'B' else 1)))
            for t in (1, 3): s.note(DR, b0 + t, 0.4, SPLASH, int(58 * dk))
    # ----- final tutti hit on the downbeat after the held chord, then ring
    fb = 4 * nb
    for ch_ in ('lead', 'lead2', 'counter', 'stab', 'str'):
        for p in triad(1, tn) + [tn + 12]: s.note(CH[ch_], fb, 0.45, p - (12 if ch_ == 'stab' else 0), 120)
    s.note(CH['bass'], fb, 0.6, tn - 24 if tn - 24 >= 34 else tn - 12, 120); s.note(CH['timp'], fb, 0.8, tn - 24, 127)
    s.note(CH['gong'], fb, 4, tn - 12, 110); s.note(CH['taiko'], fb, 1, tn - 24, 127)
    s.note(DR, fb, 0.5, KICK, 127); s.note(DR, fb, 0.5, SNARE, int(120 * dk)); s.note(DR, fb, 1, CRASH, int(120 * dk)); s.note(DR, fb, 1, CRASH2, int(110 * dk))
    end_beat = fb + 1
    return s, end_beat

def render(name, outdir, sf2):
    s, end_beat = compose(name)
    mid = os.path.join(outdir, name + '.mid'); raw = os.path.join(outdir, name + '.raw.wav'); out = os.path.join(outdir, name + '.wav')
    s.write(mid)
    subprocess.run(['fluidsynth', '-ni', '-q', '-g', '0.5', '-r', '44100', '-F', raw, sf2, mid], check=True, stdout=subprocess.DEVNULL)
    y, sr = sf.read(raw, always_2d=True); os.remove(raw)
    hit = end_beat * 60 / s.bpm - 60 / s.bpm      # time of the final hit
    y = y[: int((hit + 2.4) * sr)]                 # keep 2.4 s of ring after the last hit
    tail = int(1.2 * sr); y[-tail:] *= np.linspace(1, 0, tail)[:, None] ** 2
    lead = np.argmax(np.abs(y).max(1) > 1e-4); y = y[max(0, lead - int(0.02 * sr)):]
    meter = pyln.Meter(sr); y = pyln.normalize.loudness(y, meter.integrated_loudness(y), -14.0)
    tp = 20 * np.log10(np.abs(resample_poly(y, 4, 1, axis=0)).max() + 1e-12)
    if tp > -1.5:                                  # soft-knee peak control instead of clipping: tanh on the excess only
        thr = 10 ** (-3 / 20); a = np.abs(y); over = a > thr
        y[over] = np.sign(y[over]) * (thr + (1 - thr) * np.tanh((a[over] - thr) / (1 - thr)))
        tp = 20 * np.log10(np.abs(resample_poly(y, 4, 1, axis=0)).max() + 1e-12)
        if tp > -1.5: y *= 10 ** ((-1.5 - tp) / 20)
    sf.write(out, y.astype(np.float32), sr, subtype='PCM_16')
    return out

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('outdir'); ap.add_argument('--sf2', default='/usr/share/sounds/sf2/FluidR3_GM.sf2')
    ap.add_argument('--only', default='banda,rondalla,bayan'); a = ap.parse_args(); os.makedirs(a.outdir, exist_ok=True)
    for n in a.only.split(','): print(render(n, a.outdir, a.sf2))
