"""VoxCPM2 runner on CPU (float32 copy of the config, $HI_VOX_MODEL, default /opt/vx_model32). gen() returns a 48 kHz waveform."""
import os, sys, time, json, numpy as np, soundfile as sf, torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import vprofile as VP
torch.set_num_threads(os.cpu_count() or 4)
REC = VP.rec()
REAL = VP.real()
_m = {}
def model(path=os.environ.get('HI_VOX_MODEL', '/opt/vx_model32')):
    if 'm' not in _m:
        from voxcpm import VoxCPM
        t = time.time(); _m['m'] = VoxCPM.from_pretrained(path, load_denoiser=False, optimize=False); print('model loaded %.0fs' % (time.time() - t), file=sys.stderr, flush=True)
    return _m['m']
def cutref(i0, i1, out, tail=0.30, head=0.06):
    """Cut sentences i0..i1 of the real recording at word-aligned boundaries; pad the end with silence so a continuation starts clean."""
    import librosa
    y, sr = librosa.load(REC, sr=44100, mono=True, offset=max(0, REAL[i0]['start'] - head), duration=REAL[i1]['end'] - REAL[i0]['start'] + head + 0.05)
    n = int(0.02 * sr); y[:n] *= np.linspace(0, 1, n); y[-n:] *= np.linspace(1, 0, n)
    y = np.concatenate([y, np.zeros(int(tail * sr), np.float32)]); sf.write(out, y, sr)
    return out, ' '.join(REAL[i]['text'] for i in range(i0, i1 + 1))
def gen(text, prompt=None, prompt_text=None, ref=None, cfg=2.0, steps=10, seed=0):
    m = model(); torch.manual_seed(seed); np.random.seed(seed)
    w = m.generate(text=text, prompt_wav_path=prompt, prompt_text=prompt_text, reference_wav_path=ref, cfg_value=cfg, inference_timesteps=steps, normalize=False, denoise=False)
    return np.asarray(w, dtype=np.float32), m.tts_model.sample_rate
