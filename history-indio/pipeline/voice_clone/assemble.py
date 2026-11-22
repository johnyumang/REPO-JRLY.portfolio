"""Join the chosen takes into one read that follows the real recording's level, pauses and tone balance; write timings (runs in /opt/vc).
usage: assemble.py <work_dir> <episode_dir> <out_prefix> [--upto N_chunks] [--no-eq]   -> <out_prefix>.mp3/.wav and <out_prefix>_timings.json"""
import os, sys, json, subprocess, tempfile, numpy as np, soundfile as sf, librosa, scipy.signal as sg
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import vqc, vprofile as VP
work, ep, outp = sys.argv[1:4]; a = sys.argv[4:]; upto = int(a[a.index('--upto') + 1]) if '--upto' in a else 10 ** 6
P = json.load(open(work + '/plan.json')); CH = json.load(open(work + '/choice.json')); D = json.load(open(ep + '/sentences.json'))
REC = VP.rec()
# speech level of the real recording per tone (dB RMS), measured on Episode 1 (voice_profile.json)
LEVEL = VP.PROFILE['level_db']; LEVEL_DEFAULT = VP.PROFILE['level_default_db']
RATE_MAX, RATE_TO = 6.9, 6.3
TARGET_LUFS, TP_MAX = VP.PROFILE['target_lufs'], -1.2                            # real Episode 1 integrated loudness; true peak kept under -1 dBFS
TMP = tempfile.mkdtemp(prefix='hi_asm_'); FI, FO, TI, TO = (os.path.join(TMP, n) for n in ('_fi.wav', '_fo.wav', '_in.wav', '_out.wav'))
def ff(x, sr, af):                                                                  # run one ffmpeg audio filter on a float array
    sf.write(FI, x, sr, subtype='FLOAT'); subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', FI, '-af', af, '-c:a', 'pcm_f32le', FO], check=True)
    z, _ = sf.read(FO, dtype='float32'); return z
def ebu(x, sr):                                                                     # (integrated LUFS, LRA LU, true peak dBFS)
    sf.write(FI, x, sr, subtype='FLOAT'); o = subprocess.run(['ffmpeg', '-nostats', '-i', FI, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    o = o[o.rindex('Summary:'):]; g = lambda k: float(o.split(k)[1].split()[0]); return g('I:'), g('LRA:'), g('Peak:')
def dyn(x, sr):                                                                     # 99.9th-percentile |sample| over speech RMS (dB); speech = 20 ms frames within 25 dB of the p95 frame
    f = librosa.util.frame(x, frame_length=int(.02 * sr), hop_length=int(.02 * sr)); r = 20 * np.log10(np.sqrt((f ** 2).mean(0)) + 1e-9)
    sp = f[:, r > np.percentile(r, 95) - 25]; return float(20 * np.log10(np.percentile(np.abs(x), 99.9) / np.sqrt((sp ** 2).mean()))), float(20 * np.log10(np.sqrt((sp ** 2).mean())))
SR = 48000; parts = []; t = 0.0; tim = {}; rows = []
for c in P['chunks'][:upto]:
    ch = CH.get(str(c['id']))
    if not ch: break
    m = json.load(open(ch['wav'][:-4] + '.json')); y, sr = sf.read(ch['wav'], dtype='float32'); assert sr == SR
    W = m['words']; st = max(0.0, W[0][1] - 0.04); en = min(len(y) / sr, W[-1][2] + 0.12); seg = y[int(st * sr):int(en * sr)].copy(); k = 1.0
    if m['rate'] > RATE_MAX:                                                      # rushed take: slow it to the real voice's pace, pitch unchanged
        k = RATE_TO / m['rate']; sf.write(TI, seg, sr)
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', TI, '-af', f'rubberband=tempo={k:.4f}:pitchq=quality:formant=preserved', TO], check=True); seg, _ = sf.read(TO, dtype='float32')
    body = seg[int(0.04 * sr):len(seg) - int(0.12 * sr)]; g = float(np.clip(LEVEL.get(c['style'], LEVEL_DEFAULT) - vqc.rms_db(body), -12, 12)); seg *= 10 ** (g / 20)
    n1, n2 = int(0.008 * sr), int(0.04 * sr); seg[:n1] *= np.linspace(0, 1, n1); seg[-n2:] *= np.linspace(1, 0, n2)
    seg = ff(seg, sr, 'alimiter=limit=0.89:attack=5:release=50:level=false:latency=true')[:len(seg)]   # one loud syllable no longer pulls the whole read down
    j = 0
    for si in c['sent_ids']:
        n = len(vqc.norm_words(P['sentences'][si]['text'])); ws = W[j:j + n]; j += n
        tim[si] = (t + (ws[0][1] - st) / k, t + (ws[-1][2] - st) / k)
    parts.append(seg); t += len(seg) / sr
    nxt = P['chunks'][c['id'] + 1] if c['id'] + 1 < len(P['chunks']) else None
    gap = 0.0 if nxt is None else (0.56 if c['id'] == 0 else 0.50 if nxt['para'] != c['para'] else 0.38) + 0.03 * (((c['id'] * 37) % 5) - 2) / 2
    parts.append(np.zeros(int(gap * sr), np.float32)); t += gap
    rows.append((c['id'], c['style'], os.path.basename(ch['wav'])[5:-4], m['rate'], round(k, 3), round(g, 1)))
y = np.concatenate(parts); y = librosa.resample(y, orig_sr=SR, target_sr=44100, res_type='soxr_hq'); sr = 44100
if '--no-eq' not in a:                                                             # tone balance: follow the long-term spectrum of the real recording
    r, _ = librosa.load(REC, sr=sr, mono=True)
    def ltas(x):
        x = x[np.abs(x) > 1e-4]; f, p = sg.welch(x, sr, nperseg=4096); return f, 10 * np.log10(p + 1e-20)
    f, a_ = ltas(r); _, b_ = ltas(y); d = a_ - b_
    lf = np.log2(np.maximum(f, 20)); sm = np.array([d[np.abs(lf - x) < 1 / 6].mean() for x in lf])           # 1/3-octave smoothing
    ref = sm[(f > 200) & (f < 4000)].mean(); sm = np.clip(sm - ref, -6, 6); sm[f > 15000] = 0; sm[f < 60] = 0; sm[np.abs(sm) < 1.0] = 0
    for fc in (100, 200, 400, 800, 1600, 3200, 6400, 10000, 14000): print('eq %5d Hz %+.1f dB' % (fc, sm[np.argmin(abs(f - fc))]), end=' | ')
    print(); h = sg.firwin2(2049, f / (sr / 2), 10 ** (sm / 20)); y = sg.fftconvolve(y, h, mode='same').astype(np.float32)
r, _ = librosa.load(REC, sr=sr, mono=True); cr, _ = dyn(r, sr); cy, sy = dyn(y, sr); _, lr, _ = ebu(r, sr); _, ly, _ = ebu(y, sr)
print('dynamics: p99.9/speechRMS real %.2f dB clone %.2f dB | LRA real %.1f clone %.1f' % (cr, cy, lr, ly))
if cy - cr > 2.0:                                                                  # clone peakier than the real voice: one gentle compressor, threshold 6 dB above the clone's speech RMS
    th = sy + 6; print('compressor: acompressor threshold %.1f dBFS ratio 2 attack 10 ms release 150 ms knee 4' % th)
    y = ff(y, sr, 'acompressor=threshold=%.5f:ratio=2:attack=10:release=150:knee=4:makeup=1' % (10 ** (th / 20)))[:len(y)]
else: print('compressor: not needed')
def master(x, gain_db):                                                            # gain, then a true-peak limiter (4x oversampled)
    return ff(x * 10 ** (gain_db / 20), sr, 'aresample=176400:resampler=soxr,alimiter=limit=%.5f:attack=2:release=80:level=false:latency=true,aresample=44100:resampler=soxr' % (10 ** ((TP_MAX - 0.1) / 20)))[:len(x)]
i0, _, _ = ebu(y, sr); gdb = TARGET_LUFS - i0
for _ in range(3):
    z = master(y, gdb); I, L, TP = ebu(z, sr)
    if abs(I - TARGET_LUFS) <= 0.1: break
    gdb += TARGET_LUFS - I
y0, y = y, z; print('master: gain %+.2f dB -> %.2f LUFS, LRA %.1f LU, true peak %.2f dBFS' % (gdb, I, L, TP))
for _ in range(2):                                                                 # the MP3 is what ships: measure it and correct the encoder's level loss once
    sf.write(outp + '.wav', y, sr, subtype='PCM_16'); subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', outp + '.wav', '-codec:a', 'libmp3lame', '-b:a', '192k', outp + '.mp3'], check=True)
    I, L, TP = ebu(librosa.load(outp + '.mp3', sr=sr, mono=True)[0], sr); print('mp3: %.2f LUFS, LRA %.1f LU, true peak %.2f dBFS' % (I, L, TP))
    if abs(I - TARGET_LUFS) <= 0.1: break
    gdb += TARGET_LUFS - I; y = master(y0, gdb)
T = [{'text': D[i]['text'], 'start': round(tim[i][0], 3), 'end': round(tim[i][1], 3), 'style': D[i].get('style') or 'narrate'} for i in sorted(tim)]
json.dump(T, open(outp + '_timings.json', 'w'), ensure_ascii=False, indent=1)
print('chunks:', rows); print('assembled %d chunks, %d sentences, %.1f s -> %s.mp3' % (len(rows), len(T), len(y) / sr, outp))
