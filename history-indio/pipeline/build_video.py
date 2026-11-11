#!/usr/bin/env python3
"""Build a History Indio komiks short from rendered stills + narration.
usage: build_video.py <video_dir> <stills_dir> <voice.wav> <out.mp4>
video_dir holds timings.json (sentence start/end) ; stills_dir holds sXX.png + shots_meta.json."""
import json, os, subprocess, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'skills', 'cinematic-explainer-short', 'scripts')); sys.path.insert(0, HERE)
import komiks_filter as kf, soundtrack

vdir, sdir, voice, out = sys.argv[1:5]
tim = json.load(open(os.path.join(vdir, 'timings.json'))); meta = json.load(open(os.path.join(sdir, 'shots_meta.json')))
def t_at(a):
    i = int(a); fr = a - i; s = tim[i]; return s['start'] + fr * (s['end'] - s['start'])
work = os.path.join(sdir, 'komiks'); os.makedirs(work, exist_ok=True)
total = tim[-1]['end'] + 0.8; shots = []
for k, m in enumerate(meta):
    start = 0.0 if k == 0 else t_at(m['at']); end = t_at(meta[k + 1]['at']) if k + 1 < len(meta) else total
    kf.komiks(Image.open(os.path.join(sdir, m['id'] + '.png')), border=False).save(os.path.join(work, m['id'] + '.png'))
    kf.overlay((1080, 1920), m.get('caption'), m.get('bottom')).save(os.path.join(work, m['id'] + '_ov.png'))
    shots.append({'id': m['id'], 'image': m['id'] + '.png', 'overlay': m['id'] + '_ov.png', 'start': round(start, 3), 'end': round(end, 3), 'camera': m.get('camera', 'hold'), 'flash': m['id'] in ('s31',)})
json.dump(shots, open(os.path.join(work, 'shots.json'), 'w'), indent=1)
lens = [s['end'] - s['start'] for s in shots]
print('shots', len(shots), 'min %.1f max %.1f avg %.1f s' % (min(lens), max(lens), sum(lens) / len(lens)))
mix = os.path.join(work, 'mix.wav')
print(soundtrack.make(voice, [s['start'] for s in shots[1:]], [s['start'] for s in shots if s['flash']], mix))
subprocess.run([sys.executable, os.path.join(HERE, '..', 'skills', 'cinematic-explainer-short', 'scripts', 'motion_comic.py'), os.path.join(work, 'shots.json'), mix, out], check=True)
json.dump(shots, open(os.path.join(vdir, 'shots_timed.json'), 'w'), indent=1)
