#!/usr/bin/env python3
"""Original procedural march for the Season 1 trailer (no anthem, no borrowed melody): 128 bpm in B-flat major,
snare rolls, bass drum, tuba oom-pah, brass-like stabs and an original 8-bar brass tune, with a rondalla tremolo
(bandurria-like plucks) and a kulintang-like bell ostinato for Philippine colour. Pure numpy, a few seconds of CPU.
The arrangement follows the trailer's lines: build on the hook, groove on the premise, full band on the era flashes,
SILENCE of drums on the Bagumbayan image (a held soft chord, no hit on that cut), sparse bells on the turn with a
snare roll into the theft, a held low chord and no drums on the Huling Tala line, full band again on the title line, a final chord on the end card.
usage: make_march.py out.wav [--timings timings.json] [--video-dir DIR] [--hold 2.5]
  --hold: seconds the end card is held after the built video ends (trailer_post.py adds them); the march covers them.
  without --timings the line times are estimated from sentences.json (syllables at the cloned voice's 5.85 syl/s and
  assemble.py's pauses); after the voice exists, pass its timings.json so the sections land on the real lines.
Level: gated RMS 6 dB under a -17.4 LUFS voice (the pipeline puts music at half the voice level, soundtrack.py);
trailer_post.py re-levels it against the real voice anyway."""
import json, os, re, sys
import numpy as np, soundfile as sf
SR = 44100; BPM = 128; BEAT = 60 / BPM; ROOT = 116.54                     # B-flat 2
HERE = os.path.dirname(os.path.abspath(__file__))
hz = lambda st: ROOT * 2 ** (st / 12)

def estimate(sents):
    t = 0.25; tim = []
    paras = [0] * len(sents)                                             # paragraph index from script.txt
    txt = open(os.path.join(HERE, 'script.txt')).read().strip().split('\n\n'); k = 0
    for p, para in enumerate(txt):
        for _ in re.findall(r'[^.?!]+[.?!]+', para.replace('\n', ' ')): paras[k] = p; k += 1
    for i, s in enumerate(sents):
        d = max(0.6, len(re.findall(r'[aeiou]', s['say'])) / 5.85); tim.append({'text': s['text'], 'start': round(t, 3), 'end': round(t + d, 3)})
        t += d + (0.50 if i + 1 < len(sents) and paras[i + 1] != paras[i] else 0.38)
    return tim

def env(n, a=0.005, d=0.3, hold=0.0):
    t = np.arange(n) / SR; e = np.minimum(1, t / a); return e * np.where(t < hold, 1.0, np.exp(-(t - hold) / d))

def brass(f, dur, amp, bright=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * t) * np.clip((t - 0.15) * 4, 0, 1)
    ph = 2 * np.pi * f * np.cumsum(vib) / SR; open_ = np.clip(t / 0.06, 0, 1) * bright; y = np.zeros(n)
    for k in range(1, 13): y += np.sin(k * ph) / k * np.exp(-k * (1.6 - open_) * 0.35)
    rel = np.clip((dur - t) / 0.05, 0, 1); return (y * np.clip(t / 0.02, 0, 1) * rel * amp * 0.5).astype(np.float32)

def pluck(f, dur, amp):
    n = int(dur * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for k in range(1, 8): y += np.sin(2 * np.pi * f * k * t) * np.exp(-t * (6 + 9 * k)) / k
    return (y * np.clip(t / 0.002, 0, 1) * amp).astype(np.float32)

def bell(f, dur, amp):
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * t) * np.exp(-t * 3.2) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 7) + 0.25 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 12)
    return (y * np.clip(t / 0.002, 0, 1) * amp).astype(np.float32)

def make(tim, out, hold=2.5):
    rng = np.random.default_rng(1898); dur = tim[-1]['end'] + 0.8 + hold; n = int(dur * SR); mix = np.zeros(n, np.float32)
    def add(sig, t0):
        i = int(t0 * SR)
        if 0 <= i < n: mix[i:i + len(sig)] += sig[:n - i]
    S = lambda i: tim[i]['start']
    L = lambda key: next(i for i, s in enumerate(tim) if s['text'].startswith(key))      # lines found by their words, not by index
    flash, quiet0, quiet1, sig, theft, tala, title = (S(L(k)) for k in ('Anim na talon', 'Saksi', 'May sikreto', 'Pirma', 'Tapos may kumuha', 'At may hinahanap', "Ako 'to"))
    def kick(t0, a=0.9):
        m = int(.3 * SR); tt = np.arange(m) / SR; add((np.sin(2 * np.pi * (46 + 60 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 9) * a).astype(np.float32), t0)
    def snare(t0, a=0.5):
        m = int(.18 * SR); tt = np.arange(m) / SR; x = rng.normal(0, 1, m); x = np.diff(x, prepend=0) * 0.6 + x * 0.4
        add(((x * np.exp(-tt * 28) + 0.6 * np.sin(2 * np.pi * 196 * tt) * np.exp(-tt * 40)) * a).astype(np.float32), t0)
    def roll(t0, t1, a0=0.08, a1=0.45):
        k = 0; step = BEAT / 8
        while t0 + k * step < t1: p = k * step / max(1e-3, t1 - t0); snare(t0 + k * step, a0 + (a1 - a0) * p ** 1.5); k += 1
    def crash(t0, a=0.35):
        m = int(1.6 * SR); tt = np.arange(m) / SR; x = np.diff(rng.normal(0, 1, m + 1)); add((x * np.exp(-tt * 2.2) * a).astype(np.float32), t0)
    def stab(t0, chord, a=0.16):
        for st in chord: add(brass(hz(st + 12), 0.17, a, 1.2), t0)
    # original tune (semitones above B-flat 2, one note per beat, 0 = rest/hold) and its chords, 8 bars of 4 beats
    TUNE = [19, 24, 28, 31, 29, 28, 26, 24, 26, 26, 28, 29, 31, 0, 0, 0, 33, 31, 29, 28, 26, 28, 29, 26, 24, 28, 26, 23, 24, 0, 0, 0]
    CH = {'I': [0, 4, 7], 'IV': [5, 9, 12], 'V': [7, 11, 14], 'vi': [9, 12, 16]}
    BARS = ['I', 'IV', 'V', 'V', 'IV', 'V', 'I', 'I']
    end = max(tim[-1]['end'] + 0.8, dur - 1.4)                             # final chord under the end card, rings out
    b = 0
    while b * BEAT < end - 0.1:
        t0 = b * BEAT; bar = (b // 4) % 8; beat = b % 4; ch = CH[BARS[bar]]; root = ch[0] - 12
        if t0 < S(1) - 0.05:                                               # hook: roll and drum build, stab at the end
            if beat == 0: kick(t0, 0.6)
            if b == 0: roll(0.0, S(1) - 0.05, 0.03, 0.4)
        elif quiet0 - 0.55 <= t0 < quiet1 - 0.1: pass                      # Bagumbayan: no drums, no stabs, no melody
        elif tala - 0.6 <= t0 < title - 0.05: pass                         # the Huling Tala line: no drums, only a held low chord
        elif quiet1 - 0.1 <= t0 < tala - 0.6:                              # the turn and the theft: bells and a heartbeat
            if beat == 0: kick(t0, 0.45)
            for h in range(2):
                st = [12, 14, 19, 21, 24, 19, 14, 16][(b * 2 + h) % 8] + 12; add(bell(hz(st) * 2, 0.9, 0.12), t0 + h * BEAT / 2)
            if sig - BEAT <= t0 < theft: roll(t0, t0 + BEAT, 0.12, 0.35)       # snare roll into the theft only
        else:                                                              # the band
            full = t0 >= flash
            if beat in (0, 2):
                kick(t0, 0.85); add(brass(hz(root + (0 if beat == 0 else 7)), BEAT * 0.55, 0.32, 0.6), t0)   # oom: bass drum + tuba root/fifth
            else: snare(t0, 0.42)
            if beat in (1, 3) and rng.random() < 0.5: snare(t0 + BEAT * 0.75, 0.12)   # ghost note
            stab(t0 + BEAT / 2, ch, 0.12 if not full else 0.16)
            note = TUNE[(b % 32)]
            if full and note:                                              # brass tune
                ln = 1 + sum(1 for k in range(1, 4) if (b % 32) + k < 32 and TUNE[(b % 32) + k] == 0 and (b % 32) % 4 + k < 4)
                add(brass(hz(note), BEAT * ln * 0.92, 0.22, 1.0), t0)
            if note:                                                       # rondalla tremolo, an octave up, always
                for k in range(4): add(pluck(hz(note + 12), 0.2, 0.05 + 0.02 * (k == 0)), t0 + k * BEAT / 4)
        b += 1
    for t_ in (flash, title): crash(t_, 0.4)                               # crashes only on the big entrances, never on Bagumbayan
    stab(theft, CH['vi'], 0.22)                                            # the theft: a brass stab, no cymbal
    # Huling Tala: a G-minor chord that swells in after the cut and holds until the title's crash
    m = int((title - tala + 0.5) * SR); tt = np.arange(m) / SR; pad = np.zeros(m)
    for st in (9 - 24, 9 - 12, 12 - 12, 16 - 12, 9):
        for det in (-0.1, 0.1): pad += np.sin(2 * np.pi * hz(st + det) * tt + rng.random() * 6)
    pad *= np.clip(tt / 0.7, 0, 1) * np.clip((m / SR - tt) / 0.5, 0, 1) * 0.045; add(pad.astype(np.float32), tala + 0.05)
    # Bagumbayan: a soft E-flat major chord that swells in AFTER the cut and dies away (strings-like, no attack)
    m = int((quiet1 - quiet0 + 0.4) * SR); tt = np.arange(m) / SR; pad = np.zeros(m)
    for st in (5 - 12, 5, 9, 12, 17):
        for det in (-0.12, 0.12): pad += np.sin(2 * np.pi * hz(st + det / 1) * tt + rng.random() * 6)
    pad *= np.clip(tt / 0.6, 0, 1) * np.clip((m / SR - tt) / 0.4, 0, 1) * 0.05; add(pad.astype(np.float32), quiet0 + 0.05)
    for st in (0, 4, 7, 12): add(brass(hz(st + 12), 0.9, 0.2, 1.0), end)
    kick(end, 0.9); crash(end, 0.3)
    fade = int(0.5 * SR); mix[-fade:] *= np.linspace(1, 0, fade)
    # level: gated RMS (soundtrack.py's measure) 6 dB under a -17.4 LUFS voice, about -24 dBFS gated RMS
    sys.path.insert(0, os.path.join(HERE, '..', '..', 'pipeline')); import soundtrack
    mix *= 10 ** (-24 / 20) / soundtrack.gated_rms(mix); mix = np.clip(mix, -0.98, 0.98)
    sf.write(out, mix, SR, subtype='PCM_16'); return dur, {k: round(v, 2) for k, v in dict(flash=flash, bagumbayan=quiet0, turn=quiet1, theft=theft, huling_tala=tala, title=title, end=dur).items()}

if __name__ == '__main__':
    a = sys.argv[1:]; vdir = a[a.index('--video-dir') + 1] if '--video-dir' in a else HERE
    tim = json.load(open(a[a.index('--timings') + 1])) if '--timings' in a else estimate(json.load(open(os.path.join(vdir, 'sentences.json'))))
    d, sec = make(tim, a[0], float(a[a.index('--hold') + 1]) if '--hold' in a else 2.5); print('march %.1fs' % d, sec, '(timings: %s)' % ('real' if '--timings' in a else 'estimated'))
