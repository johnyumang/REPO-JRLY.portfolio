"""Chunk plan for a cloned-voice read: script_elevenlabs.txt -> chunks (runs of sentences that share one tone tag)."""
import re, json, sys, os
TAGMAP = {'whisper': 'whispers', 'suspense': 'suspenseful', 'somber': 'sad'}
def sentences(script_path):
    out = []
    for pi, para in enumerate(open(script_path).read().strip().split('\n\n')):
        cur = 'narrate'
        for s in re.findall(r'[^.?!]+[.?!]+', para.replace('\n', ' ')):
            tags = re.findall(r'\[([^\]]+)\]', s); txt = re.sub(r'\[[^\]]+\]\s*', '', s).strip()
            if not txt: continue
            tagged = bool(tags)
            if tags: cur = TAGMAP.get(tags[-1], tags[-1])
            out.append(dict(i=len(out), para=pi, style=cur, tagged=tagged, text=txt))
    return out
def chunks(sents, max_chars=170, max_sents=3):
    ch = []
    for s in sents:
        c = ch[-1] if ch else None
        if c and not s['tagged'] and c['para'] == s['para'] and len(c['sent_ids']) < max_sents and len(c['text']) + len(s['text']) + 1 <= max_chars:
            c['sent_ids'].append(s['i']); c['text'] += ' ' + s['text']
        else: ch.append(dict(id=len(ch), para=s['para'], style=s['style'], sent_ids=[s['i']], text=s['text']))
    for c in ch:
        c['prompt'] = 'follow' if c['text'].lower().startswith('at mag-follow') else c['style']
    return ch
if __name__ == '__main__':
    ep, work = sys.argv[1:3]; S = sentences(os.path.join(ep, 'script_elevenlabs.txt')); D = json.load(open(os.path.join(ep, 'sentences.json')))
    assert len(S) == len(D), (len(S), len(D))
    C = chunks(S); os.makedirs(work, exist_ok=True); json.dump(dict(sentences=S, chunks=C), open(os.path.join(work, 'plan.json'), 'w'), ensure_ascii=False, indent=1)
    print(len(S), 'sentences ->', len(C), 'chunks')
    for c in C[:12]: print(c['id'], c['prompt'], c['sent_ids'], '|', c['text'])
