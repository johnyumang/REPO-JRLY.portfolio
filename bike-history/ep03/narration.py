"""Episode 3 narration: English, a stock Kokoro-82M voice (Apache-2.0 weights, run with kokoro-onnx, MIT). No cloning.
Writes the voice track and narration.json (when each line starts and ends, and the subtitle shown with it).
usage: python3 narration.py MODEL_DIR OUT_DIR [voice]
MODEL_DIR holds kokoro-v1.0.onnx and voices-v1.0.bin (github.com/thewh1teagle/kokoro-onnx, release model-files-v1.0)."""
import sys, os, json, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
MD, OUT = sys.argv[1], sys.argv[2]; VOICE = sys.argv[3] if len(sys.argv) > 3 else 'am_michael'
SR_OUT, DUR = 44100, 60.0
SEG = dict(hook=0, turn=3, wheel=10, spokes=16, step=22, brake=28, explode=34, ride=42, outro=54, end=60)
RIDE_TITLE = '1884 – 1886'
ORDER = list(SEG)
# (segment, subtitle on screen or None, words spoken). Facts: facts.md. Numbers are spelled out for the voice;
# names are respelled so the voice says them right: Draisine = Dry-zeen, Drais = Drice (checked with a speech recogniser).
LINES = [
    ('hook', 'Bigger wheel, more speed.', 'The eighteen seventies. Bigger wheel, more speed.'),
    ('turn', 'This is the high-wheeler. Today we call it the penny-farthing, after a big penny and a tiny farthing coin.', 'This is the high-wheeler. Today we call it the penny-farthing, after a big penny and a tiny farthing coin.'),
    ('wheel', 'No chain: the pedals turn the front wheel, so a bigger wheel goes further with every turn.', 'No chain. The pedals turn the front wheel, so a bigger wheel goes further with every turn.'),
    ('spokes', 'Thin wire spokes, pulled tight, and solid rubber tyres.', 'Thin wire spokes, pulled tight, and solid rubber tyres.'),
    ('step', 'To get on, step on this peg above the rear wheel, then climb up to the saddle.', 'To get on, step on this peg above the rear wheel, then climb up to the saddle.'),
    ('brake', 'A spoon brake presses the front tyre. Stop too hard, and you fly over the bars.', 'A spoon brake presses the front tyre. Stop too hard, and you fly over the bars.'),
    ('explode', 'A big wheel, a small wheel, a steel tube frame, pedals, a saddle, a brake.', 'Take it apart. A big wheel, a small wheel, a steel tube frame, pedals, a saddle, a brake.'),
    ('ride', 'April 1884: Thomas Stevens sets off from San Francisco on a 50-inch Columbia.', 'In April eighteen eighty-four, Thomas Stevens set off from San Francisco on a fifty-inch Columbia.'),
    ('ride', 'December 1886, Yokohama: the first ride around the world.', 'December eighteen eighty-six, Yokohama. The first ride around the world.'),
    ('outro', 'Then came the chain.', 'Then came the chain.'),
    ('outro', None, 'Next: an engine. The first Harley-Davidson.'),
]
LINES = [l for l in LINES if l[2]]
k = Kokoro(os.path.join(MD, 'kokoro-v1.0.onnx'), os.path.join(MD, 'voices-v1.0.bin'))
def say(text, speed):
    a, sr = k.create(text, voice=VOICE, speed=speed, lang='en-us')
    a = np.asarray(a, dtype=np.float64)
    nz = np.flatnonzero(np.abs(a) > 0.01 * np.abs(a).max())          # trim the silence at both ends
    a = a[max(0, nz[0] - int(0.02 * sr)): nz[-1] + int(0.06 * sr)]
    n = int(round(len(a) * SR_OUT / sr))
    return np.interp(np.linspace(0, len(a) - 1, n), np.arange(len(a)), a)
track = np.zeros(int(DUR * SR_OUT)); meta = []; t_prev = 0.0
for i, (seg, sub, text) in enumerate(LINES):
    seg_end = SEG[ORDER[ORDER.index(seg) + 1]]
    last_in_seg = i + 1 == len(LINES) or LINES[i + 1][0] != seg
    start = max(SEG[seg] + 0.25, t_prev + 0.30)
    room = (seg_end + {'hook': 0.9, 'turn': 0.9, 'outro': -0.6}.get(seg, 0.4) - start) if last_in_seg else 99
    for speed in (0.95, 1.0, 1.08, 1.15, 1.22):
        a = say(text, speed)
        if len(a) / SR_OUT <= room: break
    dur = len(a) / SR_OUT
    if dur > room: print('WARNING too long', seg, round(dur, 2), 'room', round(room, 2))
    s0 = int(start * SR_OUT); track[s0:s0 + len(a)] += a[:len(track) - s0]
    meta.append(dict(seg=seg, start=round(start, 3), end=round(start + dur, 3), sub=sub, text=text, speed=speed))
    t_prev = start + dur
act = track[np.abs(track) > 1e-4]; track *= 10 ** (-18 / 20) / np.sqrt(np.mean(act ** 2))   # -18 dBFS while speaking
os.makedirs(OUT, exist_ok=True)
sf.write(os.path.join(OUT, 'voice.wav'), track.astype(np.float32), SR_OUT)
json.dump(dict(voice=VOICE, lines=meta, ride_title=RIDE_TITLE), open(os.path.join(OUT, 'narration.json'), 'w'), indent=1)
for m in meta: print(m['seg'], m['start'], m['end'], m['speed'])
