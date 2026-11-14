"""Tests for sound_design.py. Every input is made here; no audio files in the repo.
Run: /opt/vc/bin/python -m unittest history-indio/pipeline/tests/test_sound_design.py   (needs ffmpeg; about 1 minute)
- every generator returns finite audio of the asked length and is not silent;
- the mix of a small plan meets the loudness guard (-16 LUFS +/- 0.5, true peak at or under -1.5 dBTP after AAC);
- an episode without sound.json gets soundtrack.make's mix exactly (bit for bit)."""
import os, sys, json, tempfile, shutil, unittest, contextlib, io
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import soundtrack as st, sound_design as sd
from test_loudness_guard import speechlike

SR = sd.SR


class Generators(unittest.TestCase):
    def check(self, name, x, n=None):
        self.assertEqual(x.ndim, 1, name)
        self.assertTrue(np.all(np.isfinite(x)), f'{name}: not finite')
        if n is not None: self.assertEqual(len(x), n, f'{name}: {len(x)} samples, asked {n}')
        self.assertGreater(np.sqrt(np.mean(x.astype(float) ** 2)), 1e-4, f'{name}: silent')

    def test_beds_and_music_have_the_asked_length(self):
        for d in (0.5, 3.3):
            for k, f in sd.AMBIENCES.items(): self.check(k, f(d), sd._n(d))
            for k, f in sd.MUSIC.items():
                if f: self.check(k, f(d), sd._n(d))

    def test_events(self):
        for k, f in sd.EVENTS.items(): self.check(k, f({}, 3))
        for k, d in (('whisper', 2.0), ('cloth', 0.5), ('dog_pant', 1.5), ('growl', 1.2), ('whoosh', 0.4), ('riser', 1.5), ('shimmer', 1.0)):
            self.check(k, sd.EVENTS[k]({'dur': d}, 1), sd._n(d))
        for p in sd.PACE: self.check('steps ' + p, sd.footsteps('earth', p, 4))


class Mix(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = tempfile.mkdtemp(); cls.voice = os.path.join(cls.d, 'voice.wav')
        sf.write(cls.voice, (speechlike(12) * 0.3).astype(np.float32), SR)
        cls.tim = [{'start': 0.0, 'end': 3.8, 'text': 'a'}, {'start': 4.0, 'end': 7.8, 'text': 'b'}, {'start': 8.0, 'end': 12.0, 'text': 'c'}]

    @classmethod
    def tearDownClass(cls): shutil.rmtree(cls.d)

    def test_small_plan_meets_the_loudness_guard(self):
        ep = os.path.join(self.d, 'ep'); os.makedirs(ep, exist_ok=True)
        plan = {'0': {'amb': ['city', 'wind:-6'], 'music': 'guitar', 'foley': [{'what': 'steps_stone', 'at': 0.5, 'count': 4}]},
                   '1': {'amb': 'rain_heavy', 'music': 'drone', 'spot': [{'what': 'thunder', 'at': 0.1, 'hush': 0.4}, {'what': 'riser', 'at': 3.9}]},
                   '2': {'amb': 'crowd', 'music': 'none', 'spot': [{'what': 'cheer', 'at': 1.0}], 'foley': [{'what': 'paper_tear_many', 'at': 0.2}]},
                '_': {'whoosh_cuts': True}}
        with open(os.path.join(ep, 'sound.json'), 'w') as fh: json.dump(plan, fh)
        out = os.path.join(self.d, 'mix.wav')
        with contextlib.redirect_stdout(io.StringIO()):
            r = sd.soundtrack_for(ep, self.tim, self.voice, out, [4.0, 8.0], [], src=[0, 1, 2])
        self.assertIn('sound_design', r)
        i, tp = st.ebur(out, encode=True)
        self.assertLessEqual(abs(i - st.LUFS), st.LUFS_TOL, f'{i:.2f} LUFS')
        self.assertLessEqual(tp, st.TP, f'{tp:.2f} dBTP')
        self.assertLess(r['bed_vs_voice_in_speech_db'], -6, r)               # the voice stays on top

    def test_missing_plan_changes_nothing(self):
        ep = os.path.join(self.d, 'ep_plain'); os.makedirs(ep, exist_ok=True)
        a, b = os.path.join(self.d, 'a.wav'), os.path.join(self.d, 'b.wav')
        with contextlib.redirect_stdout(io.StringIO()):
            ra = sd.soundtrack_for(ep, self.tim, self.voice, a, [4.0, 8.0], [8.0])
            rb = st.make(self.voice, [4.0, 8.0], [8.0], b)
        self.assertEqual(ra, rb)
        with open(a, 'rb') as fa, open(b, 'rb') as fb: self.assertEqual(fa.read(), fb.read())


if __name__ == '__main__': unittest.main()
