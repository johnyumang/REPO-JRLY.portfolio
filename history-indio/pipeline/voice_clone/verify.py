"""Re-check the finished read: level, timings order, what Whisper hears, speaker similarity per sentence and per chunk (runs in /opt/vc).
usage: verify.py <voice.mp3> <voice_timings.json> [plan.json]"""
import os, sys, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import vqc, vprofile as VP
f = sys.argv[1]; T = json.load(open(sys.argv[2])); cen = VP.centroid()
import soundfile as sf, librosa
y, sr = librosa.load(f, sr=None, mono=True); print('peak %.3f sr %d dur %.2f' % (np.abs(y).max(), sr, len(y) / sr))
st = [t['start'] for t in T]; print('timings n', len(T), 'increasing', all(T[i]['start'] < T[i]['end'] <= T[i + 1]['start'] for i in range(len(T) - 1)) and T[-1]['start'] < T[-1]['end'] <= len(y) / sr)
a = vqc.load16(f); h = vqc.asr(a); want = ' '.join(t['text'] for t in T)
print('HEARD:', h); print('cmatch %.3f match %.3f' % (vqc.cmatch(want, h), vqc.match(want, h)))
print('spk whole clip %.3f' % float(vqc.spk(a) @ cen))
for t in T:
    seg = a[int(t['start'] * 16000):int(t['end'] * 16000)]; print('  spk %.3f | %s' % (float(vqc.spk(seg) @ cen), t['text'][:50]))
print('whole clip edits %d first_ok %s' % (vqc.edits(want, h), vqc.first_ok(want, h)))
if len(sys.argv) > 3:                                                              # per chunk, cut from the assembled clip and re-heard
    P = json.load(open(sys.argv[3]))
    for c in P['chunks']:
        ids = [i for i in c['sent_ids'] if i < len(T)]
        if not ids: continue
        s0, s1 = max(0.0, T[ids[0]]['start'] - 0.05), T[ids[-1]]['end'] + 0.1; seg = a[int(s0 * 16000):int(s1 * 16000)]; hh = vqc.asr(seg)
        print('  c%03d edits %d first_ok %s spk %.3f | %s' % (c['id'], vqc.edits(c['text'], hh), vqc.first_ok(c['text'], hh), float(vqc.spk(seg) @ cen), hh))
