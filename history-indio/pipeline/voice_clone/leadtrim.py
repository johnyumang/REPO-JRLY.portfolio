"""Stray sound before the first word (or after the last) of a generated take: find it, cut it, keep the cut only if the
listener still hears the script. Measured on Episode 35 (ms.py assemble): the voice model often starts a line with a real
syllable of about 0.1-0.26 s at speech level ("O", "Do", "Lo"), then a short dip (10-30 dB down, 30-50 ms), then the first
word; the aligner puts the first word on that syllable, so a cut at the aligned start leaves half of it. Here the cut goes
at the dip. No model inside: the listener is passed in, so `python3 leadtrim.py` runs the tests.
  frames_db(y, sr)                       -> 10 ms frame levels (dB) and the speech level (90th percentile)
  lead_cuts(db, lvl, t0, t1)             -> candidate cut times (s) in [t0, t1]: dips after a voiced burst >= 60 ms
  tail_cuts(db, lvl, t0, t1)             -> the same mirrored: a dip before a voiced burst >= 60 ms at the end
  trim(y, sr, st, en, words, text, listen, ok, stray) -> (st, en, note): new edges, or the old ones when no cut is heard clean
Lead cuts are tried only when stray(text, heard) says the untrimmed line is heard with an extra leading token: on Episode 35
a dip inside "Hin-di" / "Pag-balik" passed the listener (it filled the lost syllable back in from context) and cut the word."""
import numpy as np

HOP = 0.01; PRE = 0.04; FADE = 0.015; BURST = 0.06; DIP_DB = 9.0; DIP_MIN = 0.03; LOUD_DB = 25.0

def frames_db(y, sr):
    h = int(HOP * sr); n = max(1, len(y) // h)
    db = np.array([20 * np.log10(np.sqrt(np.mean(np.square(y[i * h:(i + 1) * h]))) + 1e-9) for i in range(n)])
    return db, float(np.percentile(db, 90))

def _runs(mask):
    out = []; i = 0
    while i < len(mask):
        if mask[i]:
            j = i
            while j < len(mask) and mask[j]: j += 1
            out.append((i, j)); i = j
        else: i += 1
    return out

def lead_cuts(db, lvl, t0, t1):
    """Dips (>= 30 ms, >= DIP_DB under the speech level) in [t0, t1] that follow a voiced burst (>= 60 ms within LOUD_DB of the
    speech level) and come before more voiced sound: the cut point is the quietest frame of the dip. Earliest first."""
    a, b = max(0, int(t0 / HOP)), min(len(db), int(t1 / HOP) + 1); seg = db[a:b]; cuts = []
    loud = seg > lvl - LOUD_DB
    for i, j in _runs(seg < lvl - DIP_DB):
        if j - i < round(DIP_MIN / HOP) or i == 0 or j >= len(seg): continue
        before = max((q - p for p, q in _runs(loud[:i])), default=0)
        after = loud[j:].any()
        if before * HOP >= BURST - 1e-9 and after: cuts.append((a + i + int(np.argmin(seg[i:j]))) * HOP)
    return cuts

def tail_cuts(db, lvl, t0, t1):
    """lead_cuts mirrored: dips before a voiced burst >= 60 ms at the very end of [t0, t1]. Latest first."""
    a, b = max(0, int(t0 / HOP)), min(len(db), int(t1 / HOP) + 1); r = db[a:b][::-1]
    return [round((a + len(r) - 1) * HOP - c, 3) for c in lead_cuts(r, lvl, 0, len(r) * HOP)]

def onset_after(db, lvl, t):
    """First frame after t within LOUD_DB of the speech level (the next word's start)."""
    i = int(t / HOP)
    while i < len(db) and db[i] <= lvl - LOUD_DB: i += 1
    return i * HOP

def trim(y, sr, st, en, words, text, listen, ok, stray=lambda t, h: True, stray_end=lambda t, h: True):
    """words: aligned [[w, start, end, conf], ...]; listen(clip) -> heard text; ok(text, heard_trimmed, heard_before) -> bool
    (first word right and no drop in match). Lead: candidate cuts at dips before the second aligned word, earliest first; the
    clip starts PRE before the next voiced frame after the dip (never before the dip). Tail: the same mirrored after the
    last-but-one word's end. A cut is kept only if listen() of the cut clip passes ok(). -> (st, en, note or '')."""
    db, lvl = frames_db(y, sr); notes = []
    lim = words[1][1] if len(words) > 1 else words[0][2]
    cand = [c for c in lead_cuts(db, lvl, st, min(lim, st + 1.2)) if c > st + 0.02]
    if cand:
        h0 = listen(y[int(st * sr):int(en * sr)])
        if not stray(text, h0): cand = []                                                # cut only a sound the listener hears as an extra token
        for c in cand:
            s2 = max(c, onset_after(db, lvl, c) - PRE)
            if s2 >= words[0][2]: break                                                  # past the first word: never cut into it
            h2 = listen(y[int(s2 * sr):int(en * sr)])
            if ok(text, h2, h0): notes.append('lead %.2f->%.2f' % (st, s2)); st = s2; break
    if len(words) > 1:
        cand = [c for c in tail_cuts(db, lvl, max(words[-2][2], en - 1.2), en) if c < en - 0.02 and c >= words[-1][2] - 0.05]                    # only after the last word's aligned end
        if cand:
            h0 = listen(y[int(st * sr):int(en * sr)])
            if not stray_end(text, h0): cand = []                                        # likewise only a token heard after the last word
            for c in cand:
                h2 = listen(y[int(st * sr):int((c + PRE) * sr)])
                if ok(text, h2, h0): notes.append('tail %.2f->%.2f' % (en, c + PRE)); en = c + PRE; break
    return st, en, ' '.join(notes)

def fade_in(seg, sr):
    n = int(FADE * sr); seg[:n] *= np.linspace(0, 1, n); return seg

if __name__ == '__main__':
    sr = 16000; rng = np.random.default_rng(1)
    def tone(d, a=0.3, f=180): t = np.arange(int(d * sr)) / sr; return (a * np.sin(2 * np.pi * f * t) * (1 + 0.2 * np.sin(2 * np.pi * 5 * t))).astype(np.float32)
    def sil(d, a=0.001): return (a * rng.standard_normal(int(d * sr))).astype(np.float32)
    bad = 0
    def check(name, cond):
        global bad; bad += not cond; print('%s %s' % ('ok  ' if cond else 'FAIL', name))
    # 1 stray syllable (0.2 s) + dip 40 ms (-20 dB) + word: one cut, inside the dip
    y = np.concatenate([sil(0.03), tone(0.2), tone(0.04, 0.02), tone(0.6), sil(0.1)]); db, lvl = frames_db(y, sr)
    c = lead_cuts(db, lvl, 0, 0.6); check('stray + dip: one cut in the dip (%s)' % c, len(c) == 1 and 0.22 <= c[0] <= 0.28)
    # 2 continuous word from the start: no cut
    y = np.concatenate([sil(0.03), tone(0.8), sil(0.1)]); db, lvl = frames_db(y, sr); check('continuous: no cut', lead_cuts(db, lvl, 0, 0.6) == [])
    # 3 burst shorter than 60 ms (a click): no cut
    y = np.concatenate([sil(0.03), tone(0.03), sil(0.05), tone(0.6)]); db, lvl = frames_db(y, sr); check('30 ms click: no cut', lead_cuts(db, lvl, 0, 0.6) == [])
    # 4 dip shorter than 30 ms (a consonant closure inside the word): no cut
    y = np.concatenate([sil(0.03), tone(0.2), tone(0.02, 0.01), tone(0.6)]); db, lvl = frames_db(y, sr); check('20 ms closure: no cut', lead_cuts(db, lvl, 0, 0.6) == [])
    # 5 trim(): listener accepts the cut -> start moves to just before the word, never into it
    y = np.concatenate([sil(0.03), tone(0.2), sil(0.05), tone(0.5), sil(0.05), tone(0.4), sil(0.1)])
    W = [['sa', 0.20, 0.40, .9], ['bahay', 0.83, 1.2, .9]]
    st, en, note = trim(y, sr, 0.0, len(y) / sr, W, 'sa bahay', lambda clip: 'sa bahay' if len(clip) < len(y) - int(0.2 * sr) else 'o sa bahay', lambda t, h, h0: h == t)
    check('trim lead accepted (%s)' % note, 0.23 <= st <= 0.28 and note.startswith('lead'))
    # 6 trim(): listener rejects every cut (first word lost) -> edges unchanged
    st, en, note = trim(y, sr, 0.0, len(y) / sr, W, 'sa bahay', lambda clip: 'bahay', lambda t, h, h0: h == t)
    check('trim rejected keeps edges', st == 0.0 and note == '')
    # 6b no extra token heard before the first word -> no lead cut even with a burst and a dip ("Hin-di")
    y = np.concatenate([sil(0.03), tone(0.2), sil(0.05), tone(0.5), sil(0.05), tone(0.4), sil(0.1)]); W = [['hindi', 0.03, 0.40, .9], ['ko', 0.83, 1.2, .9]]
    st, en, note = trim(y, sr, 0.0, len(y) / sr, W, 'hindi ko', lambda clip: 'hindi ko', lambda t, h, h0: True, lambda t, h: h.split()[0] != t.split()[0])
    check('no extra token heard: no lead cut', st == 0.0 and not note.startswith('lead'))
    # 7 tail: word + dip + stray syllable at the end -> cut kept when the listener agrees
    y = np.concatenate([sil(0.03), tone(0.5), sil(0.05), tone(0.5), tone(0.05, 0.01), tone(0.15), sil(0.05)])
    W = [['sa', 0.03, 0.53, .9], ['bahay', 0.58, 1.08, .9]]
    st, en, note = trim(y, sr, 0.0, len(y) / sr, W, 'sa bahay', lambda clip: 'sa bahay' if len(clip) < len(y) - int(0.12 * sr) else 'sa bahay o', lambda t, h, h0: h == t)
    check('trim tail accepted (%s)' % note, note.startswith('tail') and 1.08 <= en <= 1.18)
    print('%d of 8 tests fail' % bad); raise SystemExit(1 if bad else 0)
