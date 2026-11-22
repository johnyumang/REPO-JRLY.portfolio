"""Measure the real narrator recording once: per-sentence alignment, what Whisper hears, pitch, speaker embeddings (runs in /opt/vc).
usage: HI_VOICE_REC=<real ep1 recording> baseline.py <episode1_dir>
reads <episode1_dir>/script_elevenlabs.txt and timings.json; writes $HI_VOICE_WORK/baseline/real_ep1.json and real_centroid.npy"""
import sys, json, re, os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import vqc, vprofile as VP
ep = sys.argv[1]; rec = VP.rec(); script = os.path.join(ep, 'script_elevenlabs.txt'); os.makedirs(VP.BASE, exist_ok=True); out = VP.REAL_JSON
y = vqc.load16(rec); el = open(script).read(); sents = []
for para in el.strip().split('\n\n'):
    for s in re.findall(r'[^.?!]+[.?!]+', para.replace('\n', ' ')):
        s = re.sub(r'\[[^\]]+\]\s*', '', s).strip()
        if s: sents.append(s)
full = ' '.join(sents); em = vqc.emissions(y); W = vqc.words(y, full, em)
# sentence spans from the word alignment
k = 0; rows = []
for i, s in enumerate(sents):
    n = len(vqc.norm_words(s)); ws = W[k:k + n]; k += n
    st, en = ws[0]['start'], ws[-1]['end']; seg = y[int(max(0, st - .08) * 16000):int((en + .12) * 16000)]
    heard = vqc.asr(seg); f0, f0sd = vqc.f0_stats(seg)
    rows.append(dict(i=i, text=s, start=round(st, 3), end=round(en, 3), dur=round(en - st, 3), syl=vqc.syllables(s), words=[(w['w'], round(w['start'], 3), round(w['end'], 3), round(w['conf'], 3)) for w in ws],
                     heard=heard, match=round(vqc.match(s, heard), 3), f0=f0, f0sd=f0sd, emb=vqc.spk(seg).tolist() if en - st > 1.5 else None))
    print(i, 'dur %.2f' % (en - st), 'match %.2f' % rows[-1]['match'], 'minconf %.2f' % min(w['conf'] for w in ws), '|', heard[:100], flush=True)
json.dump(rows, open(out, 'w'), ensure_ascii=False)
conf = np.array([w[3] for r in rows for w in r['words']]); m = np.array([r['match'] for r in rows])
E_ = np.array([r['emb'] for r in rows if r['emb']]); C = E_ @ E_.T; iu = np.triu_indices(len(E_), 1)
cen = E_.mean(0); cen /= np.linalg.norm(cen)
rate = [r['syl'] / r['dur'] for r in rows if r['dur'] > 1.2]
gaps = [(rows[i + 1]['start'] - rows[i]['end'], rows[i]['text'][-1]) for i in range(len(rows) - 1)]
print('\nREAL RECORDING BASELINE')
print('ASR match: mean %.3f  p10 %.3f  min %.3f' % (m.mean(), np.percentile(m, 10), m.min()))
print('word conf: mean %.3f  median %.3f  p5 %.3f  p1 %.3f' % (conf.mean(), np.median(conf), np.percentile(conf, 5), np.percentile(conf, 1)))
print('speaker sim real-vs-real (pairs): mean %.3f  p10 %.3f ; to centroid: mean %.3f  min %.3f' % (C[iu].mean(), np.percentile(C[iu], 10), (E_ @ cen).mean(), (E_ @ cen).min()))
print('rate syl/s: mean %.2f  sd %.2f' % (np.mean(rate), np.std(rate)))
print('f0 median Hz: %.0f ; within-sentence f0 sd (semitones): mean %.2f' % (np.median([r['f0'] for r in rows if r['f0']]), np.mean([r['f0sd'] for r in rows if r['f0sd']])))
for p in '.?!':
    g = [x for x, c in gaps if c == p]
    if g: print('pause after %s: n=%d median %.2f  p25 %.2f  p75 %.2f' % (p, len(g), np.median(g), np.percentile(g, 25), np.percentile(g, 75)))
# the speaker centroid every take is compared with: 10 longer sentences, spans from the episode's timings.json
T = json.load(open(os.path.join(ep, 'timings.json'))); E = np.array([vqc.spk(y[int(T[i]['start'] * 16000):int(T[i]['end'] * 16000)]) for i in VP.PROFILE['centroid_sentence_ids']])
cen = E.mean(0); cen /= np.linalg.norm(cen); C = E @ E.T; iu = np.triu_indices(len(E), 1); np.save(VP.CENTROID, cen)
print('centroid: real-vs-real pair sim mean %.3f min %.3f | real-to-centroid mean %.3f min %.3f -> %s' % (C[iu].mean(), C[iu].min(), (E @ cen).mean(), (E @ cen).min(), VP.CENTROID))
