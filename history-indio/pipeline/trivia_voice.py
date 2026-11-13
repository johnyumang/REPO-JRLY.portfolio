#!/usr/bin/env python3
"""Record the lines of an episode's trivia break ("PATALASTAS NI USMAN") in the show's own voices (run with /opt/vc/bin/python).

  trivia_voice.py videos/<slug> --out DIR [--takes 3] [--cast DIR] [--work DIR]

Reads videos/<slug>/trivia_break.json. INDIO lines: the local clone of the user's OWN Episode 1 recording, made exactly as the
multi-speaker pipeline makes Indio lines (voice_clone/gen_ms.py: tone prompt cut from the real recording + the same timbre
reference, same VoxCPM2 settings). USMAN lines: Usman's DESIGNED voice from the cast kit (USMAN.wav + USMAN.txt), found in
--cast, else $HI_VOICE_WORK/cast, else /opt/work/voice/cast. No other voice, no stand-in.
Tones (lively, as the Episode 3 break): line 1 excited, a question curious, the other middle lines playful, the last excited;
a line's "tone" field overrides; "grave": true makes Indio's playful/excited lines warm. Tones steer Indio's prompt clip and
pitch window; Usman always continues from his own reference clip.
Per line: up to --takes takes (seeds 1, 2, ...; default 4). A line stops early only on a take that passes every check below
with 0 word edits (a dropped or changed word is a mismatch with the caption), statement intonation on a statement line and
speaker similarity comfortably above the floor (Usman >= 0.89, Indio >= 0.935); otherwise it keeps taking while takes remain.
Each take is judged by the
project's own checks (voice_clone/vqc.take_metrics + ms.checks): ACCEPTABLE = first word right, no stray token before the first
word or after the last, words match (edits <= 1, cmatch >= 0.88), speaker similarity (Indio >= 0.915 to the real-recording
centroid, Usman >= 0.85 to his own clip), numbers right by value. The best acceptable take is kept: 0 edits first, then the right intonation (a statement line, ending
in '.', may not end on a rise of more than 2 semitones or be heard as a question; a '!' line may not be heard as a question),
then fewest failed other checks, clean edges, fewest edits, score + speaker similarity + liveliness. A kept take with edits
prints a CAPTION MISMATCH warning (listen; more --takes, or a "say" field). A line's "say" field is what the voice reads and is judged against; "text"
stays the caption. Before every generation round the listener models are unloaded and the tool waits (60 s steps, up to
20 min) until 12 GB of memory are available: the voice model needs about 11 GB.
Output in --out: l{i}_{SPEAKER}.wav (trimmed to 60 ms of silence at both ends, 48 kHz mono 16-bit, about -18 LUFS, true peak
under -1 dBTP, no clipping) and takes.json (per line: file, duration, heard in the finished file, checks, the other takes;
total speech time). Takes and checks stay in --work (default DIR/work): a re-run judges what is there and only generates
what is missing. Exit 1 naming the line if a line has no acceptable take after --takes; a warning if the total speech time is
outside 12-20 s. Needs: HI_VOICE_REC (the user's recording), $HI_VOICE_WORK/baseline (baseline.py), /opt/vx, /opt/vx_model32."""
import argparse, glob, json, os, re, subprocess, sys, time
import numpy as np, soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__)); VC = os.path.join(HERE, 'voice_clone'); sys.path.insert(0, VC)
import vprofile as VP                                                  # noqa: E402  (paths and the voice profile)
SR, PAD, TARGET, TP_MAX = 48000, 0.06, -18.0, -1.0
SPK_COMFORT = {'USMAN': 0.89, 'INDIO': 0.935}                          # floors 0.85 / 0.915 (ms.checks); stop early only above these
RISE_MAX = 2.0                                                         # semitones: a statement that ends higher sounds like a question
VX = os.environ.get('HI_VX_PYTHON', '/opt/vx/bin/python')
MEM_GB, MEM_WAIT_S = 12.0, 20 * 60


def die(msg, code=1): print('trivia_voice: ' + msg, file=sys.stderr, flush=True); sys.exit(code)


def find_cast(arg):
    places = []
    for d in ([arg] if arg else []) + [VP.CAST, '/opt/work/voice/cast']:
        if d and os.path.abspath(d) not in [os.path.abspath(x) for x in places]: places.append(d)
    for d in places:
        if d and os.path.exists(os.path.join(d, 'USMAN.wav')) and os.path.exists(os.path.join(d, 'USMAN.txt')): return os.path.abspath(d)
    die('no designed USMAN voice found (looked in: %s). Put the cast kit\'s USMAN.wav and USMAN.txt (its exact words) in '
        '$HI_VOICE_WORK/cast/ (default /opt/work/voice/cast/) or pass --cast DIR. Never a stand-in voice.' % ', '.join(p for p in places if p), 2)


def tone(i, n, line, grave):
    if line.get('tone'): t = line['tone'].lower()
    elif i == 0 or i == n - 1: t = 'excited'
    elif '?' in line.get('say', line['text']): t = 'curious'
    else: t = 'playful'
    if grave and line['speaker'] == VP.NARRATOR and t in ('playful', 'excited'): t = 'warm'
    return t


def end_rise(wav, W):
    """pitch at the end of the last word against the line's median pitch, in semitones (None if too little voicing)."""
    import librosa, vqc
    y = vqc.load16(wav); st, en, lw0 = W[0][1], W[-1][2], W[-1][1]; seg = y[int(st * 16000):int(en * 16000)]
    if len(seg) < 4000: return None
    f0 = librosa.yin(seg, fmin=70, fmax=350, sr=16000, frame_length=1024); r = librosa.feature.rms(y=seg, frame_length=1024, hop_length=256)[0]
    n = min(len(f0), len(r)); f0, r = f0[:n], r[:n]; tt = st + np.arange(n) * 256 / 16000
    ok = (r > 0.3 * np.median(r[r > 1e-4])) & (f0 > 75) & (f0 < 340)
    if ok.sum() < 5: return None
    tail = f0[ok & (tt >= max(lw0, en - 0.35))]
    if len(tail) < 3: return None
    return round(float(12 * np.log2(np.median(tail[len(tail) // 2:]) / np.median(f0[ok]))), 2)


def intonation_ok(text, heard, rise):
    t = text.strip().rstrip('"\'”) ')
    if t.endswith('?'): return True                                      # a question may rise
    asked = heard.strip().endswith('?')
    if t.endswith('!'): return not asked
    return not asked and (rise is None or rise <= RISE_MAX)              # a statement: no question ending


def mem_avail_gb():
    for l in open('/proc/meminfo'):
        if l.startswith('MemAvailable:'): return int(l.split()[1]) / 1024 / 1024
    return 99.0


def wait_memory():
    t0 = time.time()
    while mem_avail_gb() < MEM_GB:
        if time.time() - t0 > MEM_WAIT_S: die('only %.1f GB of memory available after %d min (the voice model needs %.0f GB): stop the other heavy job' % (mem_avail_gb(), MEM_WAIT_S // 60, MEM_GB), 3)
        print('waiting for memory: %.1f GB available, need %.0f GB' % (mem_avail_gb(), MEM_GB), flush=True); time.sleep(60)


def ebu(path):
    o = subprocess.run(['ffmpeg', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    o = o[o.rindex('Summary:'):]; g = lambda k: float(o.split(k)[1].split()[0]); return g('I:'), g('Peak:')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('episode'); ap.add_argument('--out', required=True); ap.add_argument('--takes', type=int, default=4)
    ap.add_argument('--cast'); ap.add_argument('--work')
    a = ap.parse_args()
    tb_path = os.path.join(a.episode, 'trivia_break.json')
    if not os.path.exists(tb_path): die('no %s' % tb_path, 2)
    TB = json.load(open(tb_path)); lines = TB['lines']; grave = bool(TB.get('grave'))
    out = os.path.abspath(a.out); work = os.path.abspath(a.work or os.path.join(out, 'work')); os.makedirs(work, exist_ok=True)
    VP.rec(); [VP.need(p) for p in (VP.REAL_JSON, VP.CENTROID)]                     # fail early: the user's recording and its baseline
    if not os.path.exists(VX): die('missing %s (the voice venv, voice_clone/setup_vox.sh)' % VX, 2)
    speakers = {l['speaker'].upper() for l in lines}
    bad = speakers - {VP.NARRATOR, 'USMAN'}
    if bad: die('unknown speaker(s) %s: a trivia break has INDIO and USMAN only' % sorted(bad), 2)
    cast = find_cast(a.cast) if 'USMAN' in speakers else None
    if cast: VP.CAST = cast                                                          # this process (ms.ref_emb, VP.cast_ref)
    vroot = os.path.join(work, 'vroot'); os.makedirs(vroot, exist_ok=True)           # the generator's HI_VOICE_WORK: same baseline, this cast
    for name, tgt in (('baseline', VP.BASE), ('cast', cast)):
        p = os.path.join(vroot, name)
        if tgt and os.path.realpath(p) != os.path.realpath(tgt):
            if os.path.islink(p): os.remove(p)
            os.symlink(tgt, p)
    import ms, vqc, numwords                                                         # after VP.CAST is set
    n = len(lines); S, C = [], []
    for i, l in enumerate(lines):
        spk = l['speaker'].upper(); say = (l.get('say') or l['text']).strip(); st = tone(i, n, l, grave)
        S.append(dict(i=i, speaker=spk, turn=i, para=0, style=st, tagged=True, text=say, say=say))
        C.append(dict(id=i, speaker=spk, turn=i, para=0, style=st, prompt=st, sent_ids=[i], text=say))
    plan = dict(multispeaker=True, trivia=True, sentences=S, chunks=C)
    old = json.load(open(work + '/plan.json')) if os.path.exists(work + '/plan.json') else None
    if old and [c['text'] for c in old['chunks']] != [c['text'] for c in C]:          # the lines changed: old takes say other words
        for i, (c0, c1) in enumerate(zip(old['chunks'] + [None] * n, C)):
            if not c0 or c0['text'] != c1['text'] or c0['speaker'] != c1['speaker']:
                for f in glob.glob(f'{work}/c{i:03d}_*'): os.remove(f)
    json.dump(plan, open(work + '/plan.json', 'w'), ensure_ascii=False, indent=1)
    print('%s: %d lines, Usman voice from %s' % (os.path.basename(os.path.abspath(a.episode)), n, cast))
    for c in C: print('  l%d %-5s [%s] %s' % (c['id'], c['speaker'], c['style'], c['text']))

    judged = {}                                                                      # wav -> metrics

    def judge(c, w):
        if w in judged: return judged[w]
        j = w[:-4] + '.json'
        if not os.path.exists(j): json.dump(vqc.take_metrics(w, c['text']), open(j, 'w'), ensure_ascii=False)
        m = json.load(open(j))
        if 'end_rise' not in m: m['end_rise'] = end_rise(w, m['words']); json.dump(m, open(j, 'w'), ensure_ascii=False)
        ms.renum(m, c['text']); e, rf0 = ms.ref_emb(work, c['speaker'])
        m['spk'] = round(float(np.array(m['emb']) @ e), 3); m['fail'] = ms.checks(m, c, rf0); h = m.get('heard', '')
        why = [x for x, b in (('first word', not m['first_ok']), ('stray start %r' % vqc.extra_lead(c['text'], h), vqc.extra_lead(c['text'], h)),
                              ('stray end %r' % vqc.extra_trail(c['text'], h), vqc.extra_trail(c['text'], h)),
                              ('words (edits %d, cmatch %.2f)' % (m['edits'], m['cmatch']), not ms.words_ok(m)),
                              ('speaker %.3f' % m['spk'], 'speaker' in m['fail']), ('numbers', numwords.numbers(c['text']) and not m['num_ok'])) if b]
        m['acceptable'] = not why; m['why'] = why
        m['clean_edges'] = m['pre_s'] <= 0.25 and m['post_s'] <= 0.35 and m['lead'] <= 0.12 and m['trail'] <= 0.12
        m['energy'] = (m['f0sd'] or 0) / max(1, m['f0'] or 1)                        # pitch movement relative to pitch: a livelier read
        m['tone_ok'] = intonation_ok(c['text'], h, m['end_rise'])
        m['key'] = (m['acceptable'], m['edits'] == 0, m['tone_ok'], not m['fail'], m['clean_edges'], -m['edits'],
                    round(ms.score(m) + 0.5 * m['spk'] + 0.3 * m['energy'], 4))
        m['done'] = m['acceptable'] and not m['fail'] and m['clean_edges'] and m['edits'] == 0 and m['tone_ok'] and m['spk'] >= SPK_COMFORT.get(c['speaker'], 0)
        print('  l%d %-5s %-4s %s edits %d cm %.2f spk %.3f rate %.2f%s%s | %s' % (c['id'], c['speaker'], os.path.basename(w)[-6:-4], 'OK ' if m['acceptable'] else 'NO ',
              m['edits'], m['cmatch'], m['spk'], m['rate'], (' not: ' + '; '.join(why)) if why else '', (' other: ' + ','.join(m['fail'])) if m['fail'] else '', h)
              + ('' if m['tone_ok'] else '  (intonation: end %+.1f st%s)' % (m['end_rise'] or 0, ', heard as a question' if h.strip().endswith('?') else '')), flush=True)
        judged[w] = m; return m

    def takes(c): return sorted(glob.glob(f"{work}/c{c['id']:03d}_{VP.fname(c['speaker'])}_s*.wav"))
    t_gen = 0.0
    for seed in range(1, a.takes + 1):
        need = []
        for c in C:
            ms_ = [judge(c, w) for w in takes(c)]
            done = any(m['done'] for m in ms_)                                         # 0 edits, right intonation, clear similarity: enough
            if not done and not os.path.exists(f"{work}/c{c['id']:03d}_{VP.fname(c['speaker'])}_s{seed}.wav"): need.append(c['id'])
        if not need: continue
        print('== round %d: new takes (seed %d) for line(s) %s' % (seed, seed, ','.join(map(str, need))), flush=True)
        ms.free_models(); wait_memory()                                              # the voice model needs ~11 GB: listeners out first
        env = dict(os.environ, HI_VOICE_WORK=vroot); t0 = time.time()
        with open(work + '/gen.log', 'a') as lg:
            r = subprocess.run([VX, '-u', os.path.join(VC, 'gen_ms.py'), work, '--only', ','.join(map(str, need)), '--seeds', str(seed)], env=env, stdout=lg, stderr=subprocess.STDOUT)
        t_gen += time.time() - t0
        if r.returncode: die('the voice generator failed (exit %d): see %s/gen.log' % (r.returncode, work), 3)
        print('   generated in %.0f s' % (time.time() - t0), flush=True)
    os.makedirs(out, exist_ok=True); rows = []; total = 0.0; failed = []
    for c, l in zip(C, lines):
        cands = [(w, judge(c, w)) for w in takes(c)]
        if not cands: failed.append('line %d (%s: %s): no take' % (c['id'] + 1, c['speaker'], l['text'])); continue
        w, m = max(cands, key=lambda x: x[1]['key'])
        if not m['acceptable']: failed.append('line %d (%s: %s): best take %s fails %s' % (c['id'] + 1, c['speaker'], l['text'], os.path.basename(w), '; '.join(m['why'])))
        y, sr = sf.read(w, dtype='float32'); y = y if y.ndim == 1 else y.mean(1)
        if sr != SR: die('take %s is %d Hz, expected %d' % (w, sr, SR), 3)
        Wd = m['words']; st = min(Wd[0][1] - 0.03, m['onset']); en = max(Wd[-1][2] + 0.08, m['offset'])
        i0 = max(0, int((st - PAD) * sr)); i1 = min(len(y), int((en + PAD) * sr)); seg = y[i0:i1].copy()
        seg = np.r_[np.zeros(max(0, int(PAD * sr) - int(st * sr)), np.float32), seg, np.zeros(max(0, int((en + PAD) * sr) - len(y)), np.float32)]
        k = int(0.01 * sr); seg[:k] *= np.linspace(0, 1, k); seg[-k:] *= np.linspace(1, 0, k)
        name = 'l%d_%s.wav' % (c['id'], c['speaker']); dst = os.path.join(out, name); tmp = dst + '.f.wav'; lim = dst + '.l.wav'
        sf.write(tmp, seg, sr, subtype='FLOAT'); I, pk = ebu(tmp); g = TARGET - I; seg2 = seg * 10 ** (g / 20)
        if pk + g > TP_MAX or np.abs(seg2).max() >= 0.98:                            # keep the true peak under -1 dBTP: a limiter, never a clip
            sf.write(tmp, seg2, sr, subtype='FLOAT')
            subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', tmp, '-af', 'alimiter=limit=0.85:attack=2:release=40:level=false', '-c:a', 'pcm_f32le', lim], check=True)
            seg2 = sf.read(lim, dtype='float32')[0][:len(seg)]
        sf.write(dst, np.clip(seg2, -0.999, 0.999), sr, subtype='PCM_16')
        for f in (tmp, lim):
            if os.path.exists(f): os.remove(f)
        I2, pk2 = ebu(dst); h = vqc.asr(vqc.load16(dst)); dur = round(len(seg2) / sr, 3); total += dur
        fin = dict(first_word=vqc.first_ok(c['text'], h), stray_start=vqc.extra_lead(c['text'], h), stray_end=vqc.extra_trail(c['text'], h),
                   edits=vqc.edits(c['text'], h), cmatch=round(vqc.cmatch(c['text'], h), 3), numbers_ok=not numwords.diff(c['text'], h))
        rows.append(dict(line=c['id'], speaker=c['speaker'], tone=c['style'], text=l['text'], say=c['text'], file=dst, take=os.path.basename(w), duration=dur, heard=h,
                         checks=dict(acceptable=m['acceptable'], not_acceptable=m['why'], other_failed=m['fail'], speaker_similarity=m['spk'], edits=m['edits'],
                                     cmatch=m['cmatch'], rate=m['rate'], clean_edges=m['clean_edges'], end_rise_st=m['end_rise'], intonation_ok=m['tone_ok'],
                                     finished_file=fin, lufs=I2, true_peak_db=pk2),
                         other_takes=[dict(take=os.path.basename(x), heard=q['heard'], acceptable=q['acceptable'], why=q['why'], fail=q['fail']) for x, q in cands if x != w]))
        if m['edits'] or fin['edits']:
            print('CAPTION MISMATCH l%d: the caption says "%s", the kept take is heard as "%s" (%d edit(s)): listen; if a word is really dropped or '
                  'changed, record again with more --takes or give the line a "say"' % (c['id'], c['text'], h, max(m['edits'], fin['edits'])), flush=True)
        if not m['tone_ok']: print('INTONATION l%d: no take ends as a statement (end %+.1f st): listen, or give the line a "tone"' % (c['id'], m['end_rise'] or 0), flush=True)
        print('==> %s %s %.2f s %.1f LUFS tp %.1f | heard: %s%s' % (name, os.path.basename(w), dur, I2, pk2, h, '' if fin['first_word'] and not fin['stray_start'] and not fin['stray_end'] else '  (finished file: check by ear)'), flush=True)
    json.dump(dict(episode=os.path.basename(os.path.abspath(a.episode)), lines=rows, total=round(total, 3), target_lufs=TARGET, generation_s=round(t_gen),
                   format='48 kHz mono 16-bit, 60 ms silence at each end', cast=cast), open(os.path.join(out, 'takes.json'), 'w'), ensure_ascii=False, indent=1)
    print('total speech %.2f s%s' % (total, '' if 12 <= total <= 20 else '  WARNING: outside 12-20 s (the break is 18-23 s with the pauses)'))
    if failed:
        for f in failed: print('NO ACCEPTABLE TAKE: ' + f, file=sys.stderr)
        sys.exit(1)
    print('takes.json ->', os.path.join(out, 'takes.json'))


if __name__ == '__main__':
    main()
