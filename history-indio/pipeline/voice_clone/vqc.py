"""Voice QC: objective checks of a synthetic read against the script and against the real narrator recording.
 - words(): CTC forced alignment (MMS aligner) -> per-word time span and pronunciation confidence (0-1)
 - asr(): Whisper large-v3-turbo forced to Tagalog -> what a listener model hears
 - spk(): speaker embedding (WavLM x-vector) -> cosine similarity to the real voice
 - rate / f0 helpers"""
import re, os, json, numpy as np, torch, librosa, difflib
torch.set_num_threads(os.cpu_count() or 4)
_m = {}
def norm_words(t):
    t = t.lower().replace('ñ', 'n').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('â', 'a').replace('î', 'i').replace('ô', 'o')
    t = t.replace('-', ' ').replace('’', '').replace("'", '')
    return [w for w in re.sub(r"[^a-z' ]", ' ', t).split() if re.sub("'", '', w)]
def syllables(t): return sum(len(re.findall(r'[aeiou]+', w)) or 1 for w in norm_words(t))
def load16(path_or_wav, sr=None):
    if isinstance(path_or_wav, str): y, _ = librosa.load(path_or_wav, sr=16000, mono=True); return y
    y = np.asarray(path_or_wav, dtype=np.float32); return librosa.resample(y, orig_sr=sr, target_sr=16000) if sr != 16000 else y
def _aligner():
    if 'al' not in _m:
        from transformers import AutoModelForCTC, AutoTokenizer
        n = 'MahmoudAshraf/mms-300m-1130-forced-aligner'
        _m['al'] = (AutoModelForCTC.from_pretrained(n).eval(), AutoTokenizer.from_pretrained(n))
    return _m['al']
def emissions(y16):
    model, tok = _aligner(); out = []; W = 16000 * 30; ctx = 16000 * 2            # 30 s windows with 2 s context on both sides
    with torch.inference_mode():
        i = 0
        while i < len(y16):
            a, b = max(0, i - ctx), min(len(y16), i + W + ctx); seg = torch.from_numpy(y16[a:b])[None]
            lp = torch.log_softmax(model(seg).logits[0], -1); fps = lp.shape[0] / ((b - a) / 16000)
            s = int(round((i - a) / 16000 * fps)); e = s + int(round((min(len(y16), i + W) - i) / 16000 * fps)); out.append(lp[s:e]); i += W
    return torch.cat(out)
def words(y16, text, em=None):
    """-> [{'w','start','end','conf'}], conf = mean aligned-frame posterior of the word's letters."""
    import torchaudio.functional as AF
    model, tok = _aligner(); vocab = tok.get_vocab(); ws = norm_words(text)
    em = emissions(y16) if em is None else em; ids = []; owner = []
    for k, w in enumerate(ws):
        for ch in w:
            if ch in vocab: ids.append(vocab[ch]); owner.append(k)
    blank = vocab.get('<blank>', 0)
    ali, sc = AF.forced_align(em[None], torch.tensor([ids]), blank=blank); ali, sc = ali[0], sc[0].exp()
    spf = (len(y16) / 16000) / em.shape[0]; res = [dict(w=w, start=None, end=None, p=[]) for w in ws]; j = -1; prev = blank
    for f, (a, s) in enumerate(zip(ali.tolist(), sc.tolist())):
        if a != blank and (a != prev or prev == blank and False): j += 1 if (a != prev) else 0
        if a != blank:
            if a != prev: pass
            k = owner[min(j, len(owner) - 1)]; r = res[k]; r['p'].append(s); r['start'] = f * spf if r['start'] is None else r['start']; r['end'] = (f + 1) * spf
        prev = a
    for r in res: r['conf'] = float(np.mean(r['p'])) if r['p'] else 0.0; del r['p']
    return res
def asr(y16):
    """What a strong listener model hears (Whisper large-v3-turbo, CTranslate2 int8, forced Tagalog)."""
    if 'asr' not in _m:
        from faster_whisper import WhisperModel
        _m['asr'] = WhisperModel('deepdml/faster-whisper-large-v3-turbo-ct2', device='cpu', compute_type='int8', cpu_threads=os.cpu_count() or 4)
    segs, _ = _m['asr'].transcribe(np.asarray(y16, dtype=np.float32), language='tl', task='transcribe', beam_size=3, condition_on_previous_text=False, vad_filter=False,
                                   initial_prompt="Ako 'to si Indio. Samahan mo akong mag-time travel, at tuklasin ang history natin.")
    return ' '.join(x.text.strip() for x in segs).strip()
def match(want, heard):
    return difflib.SequenceMatcher(None, norm_words(want), norm_words(heard), autojunk=False).ratio()
def spk(y16):
    if 'sv' not in _m:
        from transformers import AutoFeatureExtractor, WavLMForXVector
        n = 'microsoft/wavlm-base-plus-sv'; _m['sv'] = (AutoFeatureExtractor.from_pretrained(n), WavLMForXVector.from_pretrained(n).eval())
    fe, sv = _m['sv']
    with torch.inference_mode():
        e = sv(**fe([y16], sampling_rate=16000, return_tensors='pt', padding=True)).embeddings[0]
    return torch.nn.functional.normalize(e, dim=-1).numpy()
def f0_stats(y16):
    f0 = librosa.yin(y16, fmin=70, fmax=350, sr=16000, frame_length=1024); rms = librosa.feature.rms(y=y16, frame_length=1024, hop_length=256)[0]
    n = min(len(f0), len(rms)); f0 = f0[:n][rms[:n] > 0.3 * np.median(rms[:n][rms[:n] > 1e-4])] if n else f0
    f0 = f0[(f0 > 75) & (f0 < 340)]
    if len(f0) < 5: return None, None
    st = 12 * np.log2(f0 / np.median(f0)); return float(np.median(f0)), float(np.std(st))
_NUM = set('zero oh one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety hundred thousand'.split())
def phon(t):
    """Spelling-insensitive, word-boundary-insensitive form: 'kanyon ang' and 'kanyo ng' are the same sounds."""
    t = t.lower().replace('ñ', 'ny'); t = re.sub(r'\d+', ' ', t)
    ws = [w for w in norm_words(t) if w not in _NUM]; ws = ['nang' if w == 'ng' else 'manga' if w == 'mga' else w for w in ws]; s = ''.join(ws)
    s = re.sub(r'c(?=[ei])', 's', s).replace('ch', 'ts').replace('c', 'k').replace('qu', 'k').replace('q', 'k').replace('z', 's').replace('x', 'ks').replace('ph', 'p').replace('f', 'p').replace('v', 'b')
    s = s.replace('uw', 'w').replace('iy', 'y').replace('ou', 'u').replace('ee', 'i').replace('oo', 'u')
    return re.sub(r'(.)\1+', r'\1', s)
def cmatch(want, heard):
    return difflib.SequenceMatcher(None, phon(want), phon(heard), autojunk=False).ratio()
def lev(a, b):
    d = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        p, d[0] = d[0], i
        for j, z in enumerate(b, 1): p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (x != z))
    return d[-1]
def edits(want, heard): return lev(phon(want), phon(heard))
def first_ok(want, heard):
    """First word heard right: same-length prefix of phon(text) and phon(heard) (phon merges across word boundaries, so compare both in context)."""
    ws = [w for w in norm_words(want) if phon(w)]; n = len(phon(ws[0])) if ws else 0; return n > 0 and phon(want)[:n] == phon(heard)[:n]
def rms_db(y): return float(20 * np.log10(np.sqrt(np.mean(np.square(y))) + 1e-9)) if len(y) else -99.0
