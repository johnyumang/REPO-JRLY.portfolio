"""Voice QC: objective checks of a synthetic read against the script and against the real narrator recording.
 - words(): CTC forced alignment (MMS aligner) -> per-word time span and pronunciation confidence (0-1)
 - asr(): Whisper large-v3-turbo forced to Tagalog -> what a listener model hears
 - spk(): speaker embedding (WavLM x-vector) -> cosine similarity to the real voice
 - rate / f0 helpers"""
import re, os, json, numpy as np, torch, librosa, difflib
import numwords
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
    t = numwords.strip(t)                                       # numbers are compared as values in edits(), not as letters
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
NUM_MISS = 2   # one wrong number (1909 said for 1906, "35" garbled) is more than max_edits: always a wrong word that forces another take
def edits(want, heard):
    """letter edits between script and heard with numbers taken out, plus NUM_MISS per number that differs in value
    ("mil nuwebe syentos sais" = "1906"; "1909" for it is wrong). See numwords.py."""
    return lev(phon(want), phon(heard)) + NUM_MISS * len(numwords.diff(want, heard))
def first_ok(want, heard):
    """First word heard right: same-length prefix of phon(text) and phon(heard) (phon merges across word boundaries, so compare both in context)."""
    if numwords.starts_with_number(want):                       # "Trenta'y singko na ako" / "35 na ako": the first number must match in value
        a, b = numwords.numbers(want), numwords.numbers(heard); return numwords.starts_with_number(heard) and bool(b) and a[0] == b[0]
    ws = [w for w in norm_words(want) if phon(w)]; n = len(phon(ws[0])) if ws else 0; return n > 0 and phon(want)[:n] == phon(heard)[:n]
def rms_db(y): return float(20 * np.log10(np.sqrt(np.mean(np.square(y))) + 1e-9)) if len(y) else -99.0
def speech_edges(y, sr, st, en, back=0.5, fwd=0.6, rel=-35.0):
    """Where the sound really starts and ends around the aligned words [st, en] (s): walk out from them while 10 ms frames stay
    within `rel` dB of the speech level (the aligner often starts an exclamation like 'Uy!' late)."""
    h = int(0.01 * sr); f = np.array([np.sqrt(np.mean(y[i:i + h] ** 2)) + 1e-9 for i in range(0, len(y) - h, h)]); db = 20 * np.log10(f)
    lvl = np.percentile(db[int(st / 0.01):max(int(st / 0.01) + 1, int(en / 0.01))], 75); thr = lvl + rel
    a = int(st / 0.01); lo = max(0, a - int(back / 0.01))
    while a > lo and db[a - 1] > thr: a -= 1
    b = min(len(db) - 1, int(en / 0.01)); hi = min(len(db) - 1, int(en / 0.01) + int(fwd / 0.01))
    while b < hi and db[b + 1] > thr: b += 1
    return a * 0.01, (b + 1) * 0.01
def take_metrics(wav, text, emb=True):
    """All checks of one generated take (used by the Season 2 cast and multi-speaker path; qcsel.py keeps its own).
    words, clarity, speed, pitch, clipping, longest pause between words, noise before/after, speaker embedding."""
    import soundfile as sf
    yo, _ = sf.read(wav, dtype='float32'); yo = yo if yo.ndim == 1 else yo.mean(1)
    y = load16(wav); W = words(y, text); conf = [w['conf'] for w in W]; st, en = W[0]['start'], W[-1]['end']
    body = y[int(st * 16000):int(en * 16000)]; b = np.sqrt(np.mean(body ** 2)) + 1e-9
    r = lambda x: float(np.sqrt(np.mean(x ** 2)) / b) if len(x) > 160 else 0.0
    gaps = [W[i + 1]['start'] - W[i]['end'] for i in range(len(W) - 1) if W[i + 1]['start'] is not None and W[i]['end'] is not None]
    h = asr(y); f0, f0sd = f0_stats(body)
    e0, e1 = speech_edges(y, 16000, st, en); conf2 = [w['conf'] for w in W if len(w['w']) > 1] or conf   # one-letter interjections ('E', said 'Eh') align to 2-3 frames: no usable confidence
    m = dict(dur=round(len(y) / 16000, 2), rate=round(syllables(text) / max(.2, en - st), 2), edits=edits(text, h), first_ok=first_ok(text, h),
             cmatch=round(cmatch(text, h), 3), match=round(match(text, h), 3), conf=round(float(np.mean(conf)), 3), minconf=round(float(min(conf2)), 3),
             onset=round(e0, 3), offset=round(e1, 3), pre_s=round(st - e0, 3), post_s=round(e1 - en, 3),
             low=[(w['w'], round(w['conf'], 2)) for w in W if w['conf'] < 0.4], clip=round(float(np.mean(np.abs(yo) >= 0.99)), 5), peak=round(float(np.abs(yo).max()), 3),
             maxgap=round(max(gaps) if gaps else 0.0, 2), lead=round(r(y[:max(0, int((st - 0.04) * 16000))]), 3), trail=round(r(y[int((en + 0.10) * 16000):]), 3),
             f0=f0, f0sd=f0sd, rms=round(rms_db(body), 1), heard=h, first=round(st, 3), last_end=round(en, 3),
             words=[(w['w'], round(w['start'], 3), round(w['end'], 3), round(w['conf'], 3)) for w in W])
    if emb: m['emb'] = spk(y).tolist()
    return m
