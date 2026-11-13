"""Tests for soundtrack.loudnorm2 (the loudness guard). Inputs are made here; no audio files in the repo.
Run: /opt/vc/bin/python -m unittest history-indio/pipeline/tests/test_loudness_guard.py   (needs ffmpeg; about 1 minute)
Each hard input must come out at -16.0 +/- 0.5 LUFS with the true peak at or under -1.5 dBTP after an AAC encode.
The guard can only fail on an input where no answer exists: with a limiter, any input with real loudness has one (gain up,
limit the peaks), so the failing case is silence, or an input that needs more than the guard's gain cap."""
import os, sys, tempfile, shutil, unittest, contextlib, io
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import soundtrack as st

SR = st.SR


def speechlike(sec, seed=0):
    """Syllable-rate bursts of a voiced harmonic tone with noise: a peaky, speech-like signal."""
    rng = np.random.default_rng(seed); t = np.arange(int(sec * SR)) / SR
    f0 = 120 + 30 * np.sin(2 * np.pi * 0.3 * t)
    x = sum(np.sin(2 * np.pi * k * np.cumsum(f0) / SR) / k for k in range(1, 12)) + 0.2 * rng.normal(0, 1, len(t))
    env = np.clip(np.sin(2 * np.pi * 4.0 * t + rng.normal(0, 0.3)), 0, 1) ** 2 * (np.sin(2 * np.pi * 0.25 * t) > -0.6)
    return x * env / np.abs(x * env).max()


def inputs():
    rng = np.random.default_rng(1); t = np.arange(20 * SR) / SR
    sp = speechlike(20)
    k = np.log(16000 / 50); sweep = np.sin(2 * np.pi * 50 * 20 / k * (np.exp(k * t / 20) - 1))
    click = sp * 10 ** (-26 / 20); click[10 * SR:10 * SR + 3] = [2.0, -2.0, 1.4]     # one +6 dBFS click in quiet speech
    return {
        'noise_bursts': rng.normal(0, 0.35, len(t)) * (np.sin(2 * np.pi * 1.3 * t) > 0.2),
        'sweep_full_scale': sweep,
        'clipped_speech': np.clip(sp * 8, -1, 1),
        'speech_plus12dB': sp * 4.0,                                                     # over full scale, kept as float
        'click_plus6dBFS': click,
        'quiet_minus40': sp * 10 ** (-24 / 20),
        'short_2s': sp[5 * SR:7 * SR],
    }


class LoudnessGuard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = tempfile.mkdtemp(prefix='loudguard_')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d, ignore_errors=True)

    def guard(self, x, name):
        src, dst = os.path.join(self.d, name + '_in.wav'), os.path.join(self.d, name + '_out.wav')
        sf.write(src, np.asarray(x, np.float32), SR, subtype='FLOAT')
        log = io.StringIO()
        with contextlib.redirect_stdout(log): st.loudnorm2(src, dst)
        return dst, log.getvalue()

    def test_converges_on_hard_inputs(self):
        for name, x in inputs().items():
            with self.subTest(name):
                dst, log = self.guard(x, name)
                self.assertTrue(log.startswith(st.GUARD), log)
                i, tp = st.ebur(dst, encode=True)
                self.assertLessEqual(abs(i - st.LUFS), st.LUFS_TOL, f'{name}: {i} LUFS\n{log}')
                self.assertLessEqual(tp, st.TP, f'{name}: {tp} dBTP\n{log}')

    def test_limiter_ceiling_holds_however_hard_driven(self):
        from scipy.signal import resample_poly
        rng = np.random.default_rng(2)
        for drive in (0, 12, 30):
            x = (rng.normal(0, 0.3, (3 * SR, 1)) * 10 ** (drive / 20)).astype(np.float32); x[SR] = 100.0
            y = st._limit(x, -3.0, SR)
            p = 20 * np.log10(np.abs(resample_poly(y, 4, 1, axis=0)).max())
            self.assertLessEqual(p, -3.0 + 1e-3, f'drive +{drive} dB: 4x peak {p:.3f} dBFS')

    def test_fails_loudly_when_no_answer_exists(self):
        for name, x in {'silence': np.zeros(5 * SR), 'minus80': speechlike(10) * 10 ** (-64 / 20)}.items():
            with self.subTest(name), self.assertRaises(SystemExit) as e:
                self.guard(x, 'fail_' + name)
            self.assertIn('LOUDNESS GUARD FAILED', str(e.exception))

    def test_encoder_that_adds_more_peak(self):
        """An encode that adds 1.5 dB of true peak (more than the limiter's 0.5 dB room): the guard must lower the limiter,
        not raise the gain in that round, and still land inside the targets as that encode measures them."""
        real = st.ebur
        st.ebur = lambda p, encode=False: (lambda r: (r[0], r[1] + 1.5))(real(p, encode))
        try:
            dst, log = self.guard(speechlike(20, seed=5) * 2, 'bad_encoder')
            i, tp = st.ebur(dst, encode=True)
        finally:
            st.ebur = real
        rounds = [l for l in log.splitlines() if l.startswith('loudness round')]
        self.assertGreater(len(rounds), 1, log)
        self.assertLessEqual(abs(i - st.LUFS), st.LUFS_TOL, log)
        self.assertLessEqual(tp, st.TP, log)

    def test_idempotent(self):
        dst, _ = self.guard(np.clip(speechlike(20, seed=3) * 3, -1.5, 1.5), 'idem')
        i1, _ = st.ebur(dst, encode=True)
        dst2, log = self.guard(sf.read(dst, dtype='float32')[0], 'idem2')
        i2, tp2 = st.ebur(dst2, encode=True)
        self.assertLess(abs(i2 - i1), 0.2, log)
        self.assertLessEqual(tp2, st.TP, log)


if __name__ == '__main__':
    unittest.main()
