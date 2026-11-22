#!/usr/bin/env python3
"""Instrumental arrangement of "Bayan Ko" for the Season 1 trailer (himig: Constancio de Guzman; the words by
Jose Corazon de Jesus are NOT used). The channel owner states that permission has been obtained; credit the composer
and lyricist on screen and in captions. The melody below was read by the central session from two independent
sources (Smithsonian Folkways lesson worksheet SFLN080_WS02 and a piano letter-notes page) and checked bar by bar;
it was written in A (verse A minor, refrain A major) and is transposed here up a semitone to B-flat. 3/4 throughout.
All performance data (tempo, voicing, accompaniment, drums, dynamics) is written here; no recording or downloaded MIDI
is used. Rendered with FluidSynth + FluidR3_GM (Frank Wen, MIT licence).
Form at 138 bpm (bar = 1.304 s): roll intro 3 bars | verse bars 13-16 softly (build) | 1 lift bar on the dominant |
refrain 17-28 full | 29-32 THIN (melody alone, soft) for narration | refrain 25-31 tutti | bar 32 final chord + ring.
usage: make_bayanko.py OUTDIR [--only banda,rondalla] [--sf2 PATH]
Output: OUTDIR/bayanko_<name>.wav, 48 kHz stereo, -15.5 LUFS integrated, true peak <= -1.5 dBTP."""
import argparse, os, re, subprocess, sys
import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy.signal import resample_poly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_music_candidates import Song, DR, KICK, SNARE, CRASH, CRASH2, CHINA, SPLASH

SR = 48000; BPM = 138; TRANSPOSE = 1          # A -> B-flat
PC = dict(C=0, D=2, E=4, F=5, G=7, A=9, B=11)

def midi(n):
    m = re.fullmatch(r'([A-G])([#b]?)(-?\d)', n); p = PC[m[1]] + {'#': 1, 'b': -1, '': 0}[m[2]]
    return 12 * (int(m[3]) + 1) + p + TRANSPOSE

def bar(s):
    out = []; t = 0.0
    for tok in s.split():
        n, d = tok.split(':'); d = float(d); out.append((t, d, midi(n))); t += d
    assert abs(t - 3) < 1e-6, (s, t); return out

# ---- melody as sent by the central session (in A), bar number -> notes
MEL = {
 13: "F4:0.5 E4:0.5 D4:1.5 F4:0.5", 14: "E4:0.5 D4:0.5 C4:1.5 E4:0.5", 15: "D4:0.5 C4:0.5 B3:1 C4:1", 16: "A3:3",
 17: "C#5:0.5 C#5:0.5 B4:0.5 B4:0.5 A4:0.5 A4:0.5", 18: "G#4:0.75 A4:0.25 G#4:2",
 19: "A4:0.5 A4:0.5 G#4:0.5 G#4:0.5 F#4:0.5 F#4:0.5", 20: "E4:0.75 F#4:0.25 E4:2",
 21: "E4:0.5 D#4:0.5 E4:0.5 D#4:0.5 E4:0.5 G#4:0.5", 22: "F#4:0.75 E4:0.25 D4:2",
 23: "D4:0.5 C#4:0.5 D4:0.5 C#4:0.5 D4:0.5 F#4:0.5", 24: "E4:0.5 D4:0.5 C#4:2",
 29: "F#4:1.5 F#4:0.5 E4:0.5 D4:0.5", 30: "E4:1.5 A4:0.5 G#4:0.5 A4:0.5", 31: "C#5:0.5 B4:0.5 A4:1 G#4:1", 32: "A4:3"}
for k in range(25, 29): MEL[k] = MEL[k - 8]
HARM = {17: "E4:0.5 E4:0.5 D4:0.5 D4:0.5 C#4:0.5 C#4:0.5", 18: "E4:0.75 F#4:0.25 E4:2",
        19: "F#4:0.5 F#4:0.5 E4:0.5 E4:0.5 D4:0.5 D4:0.5", 20: "C#4:0.75 D4:0.25 C#4:2",
        21: "C#4:0.5 C4:0.5 C#4:0.5 C4:0.5 C#4:0.5 E4:0.5", 22: "D4:0.75 C#4:0.25 B3:2",
        23: "G#4:0.5 G4:0.5 G#4:0.5 G4:0.5 G#4:0.5 B4:0.5", 24: "A4:0.5 F#4:0.5 E4:2"}
for k in range(25, 29): HARM[k] = HARM[k - 8]
# ---- my harmonisation (worksheet chords: verse Am/E/Dm, refrain A/E/D), (beat, chord) per bar
CH = {13: [(0, 'Dm')], 14: [(0, 'Am')], 15: [(0, 'Dm'), (1, 'E')], 16: [(0, 'Am')], 'lift': [(0, 'E7')],
      17: [(0, 'A')], 18: [(0, 'E')], 19: [(0, 'D')], 20: [(0, 'A')], 21: [(0, 'A')], 22: [(0, 'D')], 23: [(0, 'E7')], 24: [(0, 'A')],
      29: [(0, 'D')], 30: [(0, 'A')], 31: [(0, 'A'), (1, 'E')], 32: [(0, 'A')]}
for k in range(25, 29): CH[k] = CH[k - 8]
CHORD = {'A': ('A', [0, 4, 7]), 'Am': ('A', [0, 3, 7]), 'D': ('D', [0, 4, 7]), 'Dm': ('D', [0, 3, 7]),
         'E': ('E', [0, 4, 7]), 'E7': ('E', [0, 4, 7, 10])}
LIFT = "E4:0.5 G#4:0.5 B4:0.5 D5:0.5 E5:1"       # my own one-bar dominant lift into the refrain

def chord_notes(name, octave=3):
    r, iv = CHORD[name]; root = midi(f'{r}{octave}'); return root, [root + i for i in iv]

def plan():
    """list of (section, bar label) in playing order."""
    p = [('intro', None)] * 3 + [('verse', b) for b in (13, 14, 15, 16)] + [('lift', 'lift')]
    p += [('full', b) for b in range(17, 29)] + [('thin', b) for b in (29, 30, 31, 32)]
    p += [('tutti', b) for b in range(25, 32)] + [('final', 32)]
    return p

def compose(name):
    rng = np.random.default_rng(11); s = Song(BPM, rng); band = name == 'banda'
    C = dict(lead=0, lead2=1, harm=2, stab=3, bass=4, trem=5, pad=6, timp=7, glock=8, gtr=10, gong=11, taiko=12)
    progs = dict(lead=56, lead2=71, harm=60, stab=57, bass=58, trem=105, pad=61, timp=47, glock=9, gtr=24, gong=14, taiko=116) if band else \
            dict(lead=105, lead2=25, harm=25, stab=24, bass=32, trem=105, pad=48, timp=47, glock=72, gtr=24, gong=14, taiko=116)
    for k, ch in C.items(): s.prog(ch, progs[k])
    dk = 1.0 if band else 0.7                       # lighter drums for the rondalla
    P = plan(); tl = {}
    for i, (sec, lab) in enumerate(P):
        b0 = 3 * i; tl.setdefault(sec, [b0, b0 + 3]); tl[sec][1] = b0 + 3
        chords = CH.get(lab, [(0, 'E7')]) if sec != 'intro' else [(0, 'E')]
        def tremolo(ch, t, d, p, v, step=0.125):
            k = 0.0
            while k < d - 1e-6: s.note(ch, b0 + t + k, step * 0.9, p, v - (0 if k == 0 else 12)); k += step
        # ---------------- melody
        notes = bar(MEL[lab]) if lab in MEL else bar(LIFT) if sec == 'lift' else []
        for t, d, p in notes:
            if sec == 'verse':
                v = 62 + 6 * (lab - 13)
                if band: s.note(C['harm'], b0 + t, d * 0.97, p, v + 6)          # french horn, soft, swelling
                else: tremolo(C['lead'], t, d, p, v + 6)
            elif sec == 'thin':
                if band: s.note(C['harm'], b0 + t, d * 0.97, p, 70)              # horn alone carries the tune
                else: tremolo(C['lead'], t, d, p, 72)
            else:
                v = 108 if sec in ('full', 'tutti', 'final') else 100
                art = d * (0.85 if d <= 0.5 else 0.95)
                if band:
                    s.note(C['lead'], b0 + t, art, p, v); s.note(C['lead2'], b0 + t, art, p + 12, v - 18)
                    if sec == 'tutti' or lab in (17, 18, 19, 20): s.note(C['glock'], b0 + t, min(d, 0.5), p + 24, 72)
                else:
                    tremolo(C['lead'], t, d, p, v); tremolo(C['lead2'], t, d, p - 12, v - 20, 0.25)
                    if sec == 'tutti': s.note(C['glock'], b0 + t, art, p + 12, 74)   # piccolo descant on the return
        # ---------------- worksheet Part 1 harmony under the tune (bars 17-28), soft
        if lab in HARM and sec in ('full', 'tutti'):
            for t, d, p in bar(HARM[lab]): s.note(C['harm'], b0 + t, d * 0.95, p, 70 if band else 64)
        # ---------------- accompaniment
        for j, (cb, cn) in enumerate(chords):
            ce = chords[j + 1][0] if j + 1 < len(chords) else 3
            root, tri = chord_notes(cn)
            if sec == 'verse' or sec == 'thin':
                for p in tri: s.note(C['pad'], b0 + cb, ce - cb - 0.05, p, 52 if sec == 'thin' else 50 + 5 * (lab - 13 if sec == 'verse' else 0))
                if cb == 0: s.note(C['bass'], b0, 2.5, root - 12, 62 if sec == 'thin' else 70)
            elif sec in ('full', 'tutti', 'lift'):
                for bt in range(int(cb), int(ce)):                               # oom-pah-pah
                    if bt == 0 or (bt == cb and cb > 0):
                        s.note(C['bass'], b0 + bt, 0.8, (root - 12) + (7 if (i % 2 and sec != 'lift' and cb == 0) else 0), 102)
                    else:
                        for p in tri[:3]: s.note(C['stab'], b0 + bt, 0.3, p + (0 if band else 12), 78 if band else 72)
                if not band:                                                     # octavina/guitar tremolo on chord tones
                    k = cb
                    while k < ce - 1e-6:
                        for p in tri[1:3]: s.note(C['trem'], b0 + k, 0.11, p + 12, 52 if k % 1 == 0 else 42)
                        k += 0.25
                if sec == 'tutti':
                    for p in tri: s.note(C['pad'], b0 + cb, ce - cb - 0.05, p + 12, 66)
        # ---------------- percussion
        if sec == 'intro':
            if i == 0: s.note(C['gong'], b0, 6, midi('E2'), 100); s.note(C['taiko'], b0, 1, midi('E1'), 118); s.note(DR, b0, 1, CHINA, 70)
            k = 0.0
            while k < 3 - 1e-6:
                g = (i * 3 + k) / 9
                if not (i == 2 and k >= 2.0):
                    s.note(DR, b0 + k, 0.1, SNARE, int((35 + 75 * g) * dk))
                    if k % 0.25 == 0: s.note(C['timp'], b0 + k, 0.2, midi('E2'), int(45 + 50 * g))
                k += 0.125
            if i == 2: s.note(DR, b0 + 2, 0.5, KICK, 110); s.note(C['timp'], b0 + 2, 0.6, midi('E2'), 105); s.note(DR, b0 + 2, 1, CRASH, int(80 * dk))
        elif sec == 'verse':
            s.note(C['timp'], b0, 0.8, midi('A2') if lab in (14, 16) else midi('D2') if lab == 13 else midi('E2'), 60 + 6 * (lab - 13))
            if lab == 16:                                                        # build: snare roll crescendo into the lift
                k = 0.0
                while k < 3 - 1e-6: s.note(DR, b0 + k, 0.1, SNARE, int((40 + 60 * k / 3) * dk)); k += 0.125
        elif sec == 'lift':
            for bt in range(3): s.note(DR, b0 + bt, 0.3, KICK, 100 + 8 * bt); s.note(C['timp'], b0 + bt, 0.4, midi('E2'), 95 + 10 * bt)
            k = 0.0
            while k < 3 - 1e-6: s.note(DR, b0 + k, 0.1, SNARE, int((70 + 45 * k / 3) * dk)); k += 0.125
        elif sec in ('full', 'tutti'):
            first = (sec == 'full' and lab == 17) or (sec == 'tutti' and lab == 25)
            if first:
                s.note(DR, b0, 1.5, CRASH, int(118 * dk)); s.note(C['gong'], b0, 4, midi('A2'), 95); s.note(C['taiko'], b0, 1, midi('A1'), 115)
            s.note(DR, b0, 0.3, KICK, 112); s.note(DR, b0 + 2, 0.3, KICK, 78)
            for t, v in [(0, 100), (1, 92), (1.5, 62), (2, 96), (2.5, 66), (2.75, 74)]:
                s.note(DR, b0 + t, 0.1, SNARE, int(v * dk))
            for t in (1, 2): s.note(DR, b0 + t, 0.4, SPLASH, int(60 * dk))
            if sec == 'full' and lab == 28:                                       # fill out of the full block
                for k in range(8): s.note(DR, b0 + 2 + k * 0.125, 0.1, SNARE, int((60 + 6 * k) * dk))
        elif sec == 'thin':
            if lab == 29: s.note(C['gong'], b0, 4, midi('D2'), 55)
            if lab == 32:                                                         # pickup roll back into the tutti
                k = 1.5
                while k < 3 - 1e-6: s.note(DR, b0 + k, 0.1, SNARE, int((35 + 70 * (k - 1.5) / 1.5) * dk)); k += 0.125
                s.note(C['timp'], b0 + 2.5, 0.4, midi('E2'), 90)
        elif sec == 'final':
            root, tri = chord_notes('A')
            for ch in ('lead', 'lead2', 'harm', 'stab', 'pad', 'gtr'):
                for p in tri + [root + 12]: s.note(C[ch], b0, 1.6, p + 12 if ch in ('lead', 'lead2') else p, 118)
            s.note(C['bass'], b0, 1.6, root - 12, 120); s.note(C['timp'], b0, 1.0, midi('A2'), 127)
            s.note(C['gong'], b0, 6, midi('A2'), 110); s.note(C['taiko'], b0, 1, midi('A1'), 127); s.note(C['glock'], b0, 1, root + 24, 90)
            if not band:
                for p in tri: tremolo(C['trem'], 0, 1.5, p + 12, 90)
            s.note(DR, b0, 0.5, KICK, 127); s.note(DR, b0, 0.5, SNARE, int(122 * dk)); s.note(DR, b0, 2, CRASH, int(122 * dk)); s.note(DR, b0, 2, CRASH2, int(110 * dk))
    return s, P, tl

def limit(y, sr, ceil, look=0.005, rel=0.08):
    """Look-ahead peak limiter: gain = min(1, ceil / peak over the next 5 ms), instant attack, 80 ms release."""
    from scipy.ndimage import maximum_filter1d
    n = int(look * sr); pk = maximum_filter1d(np.abs(y).max(1), size=2 * n + 1)
    g = np.minimum(1.0, ceil / np.maximum(pk, 1e-9))
    a = np.exp(-1 / (rel * sr)); out = np.empty_like(g); cur = 1.0
    for i, gi in enumerate(g):                       # min-hold with exponential release
        cur = gi if gi < cur else a * cur + (1 - a) * gi; out[i] = cur
    return y * out[:, None]

def render(name, outdir, sf2):
    s, P, tl = compose(name)
    mid = os.path.join(outdir, f'bayanko_{name}.mid'); raw = mid[:-4] + '.raw.wav'; out = mid[:-4] + '.wav'
    s.write(mid)
    subprocess.run(['fluidsynth', '-ni', '-q', '-g', '0.5', '-r', str(SR), '-F', raw, sf2, mid], check=True, stdout=subprocess.DEVNULL)
    y, sr = sf.read(raw, always_2d=True); os.remove(raw); assert sr == SR
    spb = 60 / BPM; hit = tl['final'][0] * spb
    lead = int(np.argmax(np.abs(y).max(1) > 1e-4)); y = y[lead:]; off = lead / sr
    y = y[: int((hit - off + 1.6 * spb + 2.0) * sr)]                     # chord held 1.6 beats, then 2 s ring-out
    tail = int(1.0 * sr); y[-tail:] *= np.linspace(1, 0, tail)[:, None] ** 2
    tp = lambda z: 20 * np.log10(np.abs(resample_poly(z, 4, 1, axis=0)).max() + 1e-12)
    meter = pyln.Meter(sr)
    for _ in range(4):                                # normalise, limit, re-normalise until both targets hold
        y = pyln.normalize.loudness(y, meter.integrated_loudness(y), -15.5)
        y = limit(y, sr, 10 ** (-2.0 / 20))
    if tp(y) > -1.5: y *= 10 ** ((-1.5 - tp(y)) / 20)
    sf.write(out, y.astype(np.float32), sr, subtype='PCM_16')
    marks = {k: (round(v[0] * spb - off, 2), round(v[1] * spb - off, 2)) for k, v in tl.items()}
    return out, marks

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('outdir'); ap.add_argument('--sf2', default='/usr/share/sounds/sf2/FluidR3_GM.sf2')
    ap.add_argument('--only', default='banda,rondalla'); a = ap.parse_args(); os.makedirs(a.outdir, exist_ok=True)
    for n in a.only.split(','): print(*render(n, a.outdir, a.sf2))
