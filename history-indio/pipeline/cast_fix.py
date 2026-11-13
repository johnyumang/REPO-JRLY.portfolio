#!/usr/bin/env python3
"""Rewrite drifting character mentions in ONE episode's key_prompts.json to the canonical cast strings.

usage: cast_fix.py --ep videos/<slug> [--dry-run | --write] [--only NAME] [--save-outfit] [--cast PATH] [--json]
  --dry-run (default) shows every change and every prompt left for a person; --write changes the file.
  --only NAME   one prompt (its key in chars/full); nv_replace is then left alone.
  --save-outfit also saves the era outfits built from indio_era_template into the cast file (indio_outfits.epNN),
                as the cast file's _how_to_use asks; without it the built string is used and cast_lint reports it unsaved.
Rules (the same decisions as cast_lint.py):
  * only the span that describes the character is replaced (article, the cast adjectives, the head noun and the comma /
    "and" / "with" / "wearing" segments that describe hair, skin, clothes, headband, medallion, tattoos, handkerchief);
    everything else in the prompt stays as written. Expression words before the head ("a tired young Filipino man") stay.
  * Indio's string: the era outfit of this episode (saved under indio_outfits, or built from the template with the clothes
    the episode already names and the episode's tattoos), the modern string of the episode for present-day scenes,
    indio_s5 from ep42, the schoolboy in Episode 10. Undecidable (no cast string for that age or outfit, cannot tell who or
    which outfit, a deliberate "no tattoos" / "bare neck") -> the whole prompt is left alone and reported.
  * Usman: the cast string; "ears up / pricked / flying" next to him is removed. M: the cast string.
  * modern-day prompts without Usman get "he is alone, no dog, no animals" ("no dog, no animals" when other people are
    in the picture: "he is alone" would erase them).
  * nv_replace entries that rewrite character strings are removed, unless removing one would push a prompt over 800.
  * over 800 characters as make_keys sends it -> shorten the SCENE wording only (END duplicates such as "no text", then
    decorative adjectives, then "detailed background", then the long single-image line); still over -> prompt left alone.
  * plates are never changed. Every candidate is linted again before it is kept: anything not EXACT -> left alone.
  * the file is edited by exact replacement of the changed JSON strings only, re-read right before writing; if it changed
    meanwhile the whole computation is redone.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cast_lint as L

def arg(a, f, d=None):
    return a[a.index(f) + 1] if f in a else d

# ------------------------------------------------------------------ scene shortening
SHORTEN = [
    ('END already says it', re.compile(r"(?:,\s*|\s+)\bno (?:readable |visible )?(?:text|letters|logos?|watermarks?)\b(?=\s*[,.;]|\s*$)", re.I), ''),
    ('decorative words', re.compile(r"\b(?:very|really|extremely|incredibly|highly|beautiful|beautifully|stunning|gorgeous|breathtaking|"
                                    r"majestic|epic|magical|lush|vibrant|glorious|delicate|intricate|softly|gently|slightly|subtle|subtly|"
                                    r"dramatic|dramatically|cinematic|brilliant|dazzling|elegant|lovely|richly|vivid|quiet|calm)\s+(?=[a-z])"), ''),
    ('detailed background', re.compile(r"(?:,\s*)?\b(?:highly )?detailed background\b", re.I), ''),
    ('mild adjectives', re.compile(r"\b(?:warm|soft|faint|faintly|gentle|deep|tiny|huge|massive|giant|little)\s+(?=[a-z])"), ''),
    ('single-image line', re.compile(r"Single image, no panels, no border, no black bars, the picture fills the whole vertical frame\.?"), 'Single image, no panels, no border.'),
]
def _tidy(t):
    t = re.sub(r"\s+,", ',', t); t = re.sub(r",\s*,", ',', t); t = re.sub(r",\s*\.", '.', t); t = re.sub(r":\s*,", ':', t)
    t = re.sub(r"\.\s*\.", '.', t); t = re.sub(r" {2,}", ' ', t); return t.strip()

def shorten(text, protected, fits):
    """apply the steps one by one outside the protected strings until fits(text); -> (text, steps used) or (None, steps)."""
    keep = sorted({x for x in protected if x}, key=len, reverse=True)
    def mask(t):
        for i, x in enumerate(keep): t = t.replace(x, f'\x00{i}\x00')
        return t
    def unmask(t):
        for i, x in enumerate(keep): t = t.replace(f'\x00{i}\x00', x)
        return t
    used, t = [], text
    for name, rx, rep in SHORTEN:
        if fits(t): break
        n = _tidy(unmask(rx.sub(rep, mask(t))))
        if n != t: used.append(name); t = n
    return (t, used) if fits(t) else (None, used)

# ------------------------------------------------------------------ one prompt
def replacement(p, mm, canon):
    cb = L.body(canon); cart = canon[:len(canon) - len(cb)].strip()
    if mm.bare:
        new = canon
    elif mm.kept:
        new = (mm.art + ' ' if mm.art else '') + ' '.join(mm.kept) + ' ' + cb
    elif mm.art and mm.art.lower() == 'the':
        new = mm.art + ' ' + cb
    elif mm.art:
        new = (cart.capitalize() if mm.art[0].isupper() else cart) + ' ' + cb
    else:
        new = cb
    before = p[:mm.start].rstrip()
    if p[mm.start:mm.start + 1].isupper() or (mm.bare and before.endswith(('.', '!', '?'))):
        new = new[0].upper() + new[1:]
    carry = []
    span = p[mm.start:mm.end]
    for seg in re.split(r",\s*|\s+and\s+", span):            # props worn for this scene (a helmet, sunglasses) stay beside the string
        a = ACCESSORY.search(seg)
        if a and a.group(0).lower() not in canon.lower():
            seg = seg.strip()
            seg = re.sub(r'^.*?\b(?:man|boy|dog|woman)\s+(?=wearing|with|in)', '', seg)
            if not seg.startswith(('wearing', 'with', 'in ')): seg = 'wearing ' + re.sub(r'^(?:with|in)\s+', '', seg)
            carry.append(seg)
    for c in L.CARRY_RE.findall(span):
        c = c.lower()
        if c not in canon.lower() and c not in carry and not any(c in x for x in carry): carry.append(c)
    return new + (', ' + ', '.join(carry) if carry else '')

ACCESSORY = re.compile(r"helmet|\bhat\b|\bcap\b|sunglasses|goggles|gloves|scarf|\bwatch(?:es)?\b|salakot|backpack|bag\b|mask", re.I)

def check_candidate(K, kind, key, p, ep, canon, need):
    era = L.scene_era(p); bad = []
    for mm in L.find_mentions(p, ep, key):
        if mm.unsure: bad.append(f'{mm.char}: {mm.unsure}'); continue
        name, s, why = canon.pick(mm, p, era)
        if not name: bad.append(f'{mm.char}: {why}'); continue
        mm['end'] = L.extend(p, mm, s)
        cls, det = L.classify(mm, p, name, s, ep, era)
        if cls != 'EXACT': bad.append(f'{mm.char} {cls}: {det}')
    st, msg = L.clause_state(p, need)
    if st != 'OK': bad.append(msg)
    return bad

def fix_prompt(K, kind, key, p, ep, canon, nv):
    """-> dict(status=changed|clean|left, new, reasons, notes, used)"""
    era = L.scene_era(p)
    ms = L.find_mentions(p, ep, key)
    edits, used, reasons, resolved = [], [], [], []
    for mm in ms:
        if mm.unsure: reasons.append(f'{mm.char}: {mm.unsure} ("{p[mm.start:mm.end][:80]}")'); resolved.append(None); continue
        name, s, why = canon.pick(mm, p, era)
        if not name: reasons.append(f'{mm.char}: {why} ("{p[mm.start:mm.end][:80]}")'); resolved.append(None); continue
        resolved.append((name, s))
        mm['end'] = L.extend(p, mm, s)
        cls, det = L.classify(mm, p, name, s, ep, era)
        if cls == 'STORY': reasons.append(f'{mm.char}: {det}'); continue
        used.append((name, s))
        if cls != 'EXACT':
            if not (cls == 'WRONG' and p.startswith(L.body(s), mm.vstart)):
                edits.append((mm.start, mm.end, replacement(p, mm, s)))
        if mm.char == 'usman':                                  # "ears up" etc. next to Usman
            zone_end = min(len(p), mm.end + 160)
            for w in L.EARS_WRONG.finditer(p, mm.start, zone_end):
                if not any(a <= w.start() < b for a, b, _ in edits): edits.append((w.start(), w.end(), ''))
    if reasons: return dict(status='left', new=p, reasons=reasons)
    need = L.clause_need(p, ep, ms, era, resolved, canon.omp)
    new = p
    for a, b, r in sorted(edits, reverse=True):
        new = new[:a] + r + new[b:]
    if need:
        st, _ = L.clause_state(new, need)
        if st == 'NEAR':
            m = L.NODOG_RX.search(new); rep = need[0].upper() + need[1:] if new[m.start()].isupper() else need
            new = new[:m.start()] + rep + new[m.end():]
        elif st == 'MISSING':
            s0 = new.rstrip()
            new = (s0 + ' ' + need[0].upper() + need[1:] + '.') if s0.endswith('.') else (s0 + ', ' + need + '.')
    notes = []
    fits = lambda t: len(L.assemble(K, kind, t, nv)) <= L.LIMIT
    if not fits(new):
        before = len(L.assemble(K, kind, new, nv))
        short, steps = shorten(new, [s for _, s in used] + [L.body(s) for _, s in used] + [need], fits)
        if short is None:
            return dict(status='left', new=p, reasons=[f'over {L.LIMIT} even after shortening the scene ({before} sent with the cast strings; tried: {", ".join(steps) or "nothing to drop"}): needs a shorter scene by hand or a short cast form'])
        notes.append(f'scene shortened ({before} -> {len(L.assemble(K, kind, short, nv))} sent): ' + ', '.join(steps)); new = short
    bad = check_candidate(K, kind, key, new, ep, canon, need)
    if bad: return dict(status='left', new=p, reasons=['the rewrite did not lint clean: ' + '; '.join(bad)])
    return dict(status='changed' if new != p else 'clean', new=new, reasons=[], notes=notes, used=used)

# ------------------------------------------------------------------ minimal file edits
def _dump(x, asc): return json.dumps(x, ensure_ascii=asc)

def replace_value(T, section, key, old, new):
    for asc in (False, True):
        frag = _dump(key, asc) + ': ' + _dump(old, asc)
        if T.count(frag) == 1: return T.replace(frag, _dump(key, asc) + ': ' + _dump(new, asc))
        if T.count(frag) > 1 and section:
            st = T.find(_dump(section, asc) + ': {')
            i = T.find(frag, st)
            if st >= 0 and i >= 0: return T[:i] + _dump(key, asc) + ': ' + _dump(new, asc) + T[i + len(frag):]
    raise ValueError(f'cannot find {section}/{key} exactly in the file')

def remove_pair(T, key, val):
    for asc in (False, True):
        frag = re.escape(_dump(key, asc) + ': ' + _dump(val, asc))
        for rx in (r',\s*' + frag, frag + r'\s*,\s*', r'\s*' + frag + r'\s*'):
            m = list(re.finditer(rx, T))
            if len(m) == 1:
                rep = '' if rx.startswith(',') else ('\n  ' if rx.endswith(',\\s*') else '')
                cand = T[:m[0].start()] + rep + T[m[0].end():]
                try: json.loads(cand); return cand
                except ValueError: continue
    raise ValueError('cannot remove nv_replace entry exactly: ' + key[:60])

def add_outfits(T, items):
    """insert "epNN": "..." pairs at the end of indio_outfits (indent 1 file); returns new text."""
    m = re.search(r'"indio_outfits": \{(.*?)\n \}', T, re.S)
    if not m: raise ValueError('indio_outfits not found in the cast file')
    ins = ''.join(',\n  ' + json.dumps(k, ensure_ascii=False) + ': ' + json.dumps(v, ensure_ascii=False) for k, v in items)
    return T[:m.end(1)] + ins + T[m.end(1):]

# ------------------------------------------------------------------ episode
def plan(epdir, C, only=None):
    path = os.path.join(epdir, 'key_prompts.json')
    T = open(path).read(); K = json.loads(T)
    ep = L.ep_num(epdir)
    items = [(k, n, p) for k, n, p in L.prompts(K) if not p.startswith('(copied')]
    canon = L.EpisodeCanon(C, ep, items); canon.omp = L.outfit_means_present(canon, items, ep)
    nv_all = dict(K.get('nv_replace', {}))
    cnv = [] if only else L.char_nv_entries(K)
    nv_new = {k: v for k, v in nv_all.items() if k not in cnv}
    results = {}
    for kind, key, p in items:
        if only and key != only: continue
        results[(kind, key)] = fix_prompt(K, kind, key, p, ep, canon, nv_new)
    kept_nv = []
    if cnv:                                                     # does dropping the character nv entries push any prompt over?
        prot = [s for s in C['str'].values()] + [L.body(s) for s in C['str'].values()] + [L.ALONE, L.NODOG]
        for kind, key, p in items:
            r = results.get((kind, key))
            cur = r['new'] if r else p
            fits_new = lambda t: len(L.assemble(K, kind, t, nv_new)) <= L.LIMIT
            if fits_new(cur) or len(L.assemble(K, kind, cur, nv_all)) > L.LIMIT: continue
            if r and r['status'] != 'left':
                short, steps = shorten(cur, prot, fits_new)
                if short is not None and not check_candidate(K, kind, key, short, ep, canon, None):
                    results[(kind, key)] = dict(status='changed' if short != p else 'clean', new=short, reasons=[], used=r.get('used', []),
                                                notes=r.get('notes', []) + [f'scene shortened so the cast strings fit without nv_replace: {", ".join(steps)}'])
                    continue
            for k in cnv:
                if k in L.assemble(K, kind, cur, {}) and k not in kept_nv: kept_nv.append(k)
            if r and r['status'] != 'left':
                r.setdefault('notes', []).append('needs the nv_replace short form to fit 800: entry kept')
        nv_final = {k: v for k, v in nv_all.items() if k not in cnv or k in kept_nv}
    else:
        nv_final = nv_all
    used_names = {n for r in results.values() if r['status'] in ('changed', 'clean') for n, _ in r.get('used', [])}
    new_outfits = [(n.split('.', 1)[1], s) for n, s in canon.unsaved() if n in used_names]
    return dict(path=path, T=T, K=K, ep=ep, results=results, nv_removed=[k for k in cnv if k not in kept_nv], nv_kept=kept_nv,
                nv_final=nv_final, outfits=new_outfits)

def apply(P, only):
    T, K = P['T'], json.loads(P['T'])
    for (kind, key), r in P['results'].items():
        if r['status'] != 'changed': continue
        sec = None if kind == 'flat' else kind
        T = replace_value(T, sec, key, (K[kind][key] if sec else K[key]), r['new'])
        if sec: K[kind][key] = r['new']
        else: K[key] = r['new']
    for k in P['nv_removed']:
        T = remove_pair(T, k, K['nv_replace'][k]); del K['nv_replace'][k]
    if json.loads(T) != K: raise ValueError('edited text does not parse to the expected prompts: nothing written')
    return T

def report(P, epdir, js=False):
    out = {'episode': os.path.basename(epdir.rstrip('/')), 'changed': [], 'left_for_a_person': [], 'nv_removed': P['nv_removed'],
           'nv_kept': P['nv_kept'], 'outfits_built': P['outfits']}
    K = P['K']
    for (kind, key), r in P['results'].items():
        old = K[kind][key] if kind != 'flat' else K[key]
        if r['status'] == 'changed': out['changed'].append({'kind': kind, 'key': key, 'before': old, 'after': r['new'], 'notes': r.get('notes', [])})
        elif r['status'] == 'left': out['left_for_a_person'].append({'kind': kind, 'key': key, 'reasons': r['reasons']})
    if js: return json.dumps(out, ensure_ascii=False, indent=1)
    Lr = [f"== {out['episode']}: {len(out['changed'])} prompts rewritten, {len(out['left_for_a_person'])} left for a person"]
    for c in out['changed']:
        Lr.append(f"\n{c['kind']}/{c['key']}")
        Lr.append('  before: ' + c['before']); Lr.append('  after:  ' + c['after'])
        for n in c['notes']: Lr.append('  note:   ' + n)
    if out['left_for_a_person']:
        Lr.append('\nLEFT ALONE (a person decides):')
        for x in out['left_for_a_person']:
            Lr.append(f"  {x['kind']}/{x['key']}: " + ' | '.join(x['reasons']))
    if out['nv_removed']: Lr.append(f"\nnv_replace: {len(out['nv_removed'])} character entries removed (they rewrote the cast strings before sending)")
    if out['nv_kept']: Lr.append(f"nv_replace: {len(out['nv_kept'])} character entries KEPT because a prompt would not fit 800 without them")
    for n, s in out['outfits_built']: Lr.append(f'era outfit built from the template: indio_outfits.{n} = "{s}"')
    return '\n'.join(Lr)

def main(a):
    if '--ep' not in a: print(__doc__); return 2
    epdir = arg(a, '--ep'); epdir = epdir if os.path.isdir(epdir) else os.path.join(L.ROOT, epdir)
    write, only, js = '--write' in a, arg(a, '--only'), '--json' in a
    C = L.load_cast(arg(a, '--cast'))
    for attempt in range(4):
        P = plan(epdir, C, only)
        print(report(P, epdir, js))
        if not write: print('\n(dry run: nothing written; add --write)'); return 0
        newT = apply(P, only)
        if open(P['path']).read() != P['T']:                     # changed under us (another machine's commit): redo this file
            print('key_prompts.json changed while planning; redoing'); continue
        if newT != P['T']:
            open(P['path'], 'w').write(newT)
        if '--save-outfit' in a and P['outfits']:
            cp = C['_path']; CT = open(cp).read(); exp = json.loads(CT)
            add = [(k, v) for k, v in P['outfits'] if k not in exp.get('indio_outfits', {})]
            if add:
                NT = add_outfits(CT, add)
                for k, v in add: exp['indio_outfits'][k] = v
                if json.loads(NT) != exp: raise ValueError('cast file edit does not parse as expected')
                if open(cp).read() != CT: print('cast file changed meanwhile; outfits NOT saved, run again'); return 1
                open(cp, 'w').write(NT); print('saved to', cp, ':', ', '.join('indio_outfits.' + k for k, _ in add))
        print('written', P['path']); return 0
    print('gave up: the file kept changing'); return 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
