#!/usr/bin/env python3
"""Rewrite drifting character mentions in ONE episode's key_prompts.json to the canonical cast strings.

usage: cast_fix.py --ep videos/<slug> [--dry-run | --write] [--only NAME] [--save-outfit] [--wear-medallion] [--cast PATH] [--json]
  --dry-run (default) shows every change and every prompt left for a person; --write changes the file.
  --only NAME   one prompt (its key in chars/full, or the number of an ep01 flat prompt); nv_replace is then left alone.
  --save-outfit also saves the era outfits built from indio_era_template into characters/series_cast.json
                (indio_outfits.epNN). That file is shared by every machine: it is written first, atomically, after a fresh
                re-read; if it changed meanwhile the whole run is redone. Without the flag the built string is used and
                cast_lint lists it as UNSAVED_OUTFIT, so a person can save it in a separate, reviewed step.
  --wear-medallion  a person has decided that Indio wears the medallion in this episode's past scenes (see "bare neck").
Exit: 0 = dry run done or written with nothing left, 1 = written but some prompts were left for a person, 2 = could not run
(bad arguments, unreadable cast or episode file, the file kept changing).
Rules (the same decisions as cast_lint.py, through cast_lint.analyse):
  * the cast string replaces the article, the cast adjectives and the head noun ("a lean young Filipino man"). After the
    head the tail is cut into small phrases (at commas, "and", prepositions, verbs and adverbs). A phrase is dropped only
    if EVERY content word in it is a description word the cast string now covers (hair, skin, the episode's clothes,
    headband, medallion, tattoos, handkerchief, chest patch, ears, kerchief, M's coat). An appearance phrase the string does
    not cover ("with long black hair", "clean-shaven") stays where it is; the first phrase with any other word (a place,
    action, expression or prop: "on a yacht deck", "grips his hand", "with eyes closed") ends the description, and it and
    everything after it stay as written. Later in the same clause a comma segment that only repeats a constant is dropped.
    A final check compares the words before and after: if any word that is not a description word would be lost, the
    prompt is left alone. If the old description still goes on after the scene words, the prompt is left alone too.
  * one string per character per prompt: a later bare name ("Indio pointing") or "the dog" is a back-reference and stays
    as written; a second "a ..." description of the same character (or another dog) is left for a person.
  * Indio's string: the era outfit of this episode (saved under indio_outfits, or built from the template with the clothes
    the episode already names and N-1 tattoos up to ep06), the modern string of the episode for present-day scenes,
    indio_s5 from ep42, the schoolboy in Episode 10. Undecidable -> the whole prompt is left alone and reported: no cast
    string for that age or outfit, cannot tell who or which outfit, a deliberate "no tattoos" / "bare neck", an episode
    that draws Indio with a bare neck elsewhere (M took the medallion in ep06; nv_replace short forms say "bare neck"),
    clothes in this shot that the episode outfit does not have.
  * Usman: the cast string; "ears up / pricked / flying" and "the other ear standing up" next to him are removed.
    M: the cast string, unless the shot gives her something else in her hands, describes her umbrella separately, or
    dresses her in era clothes (a person decides).
  * modern-day prompts without Usman get "he is alone, no dog, no animals"; "no dog, no animals" when other people are in
    the picture ("he is alone" would erase them); only "no dog" when the shot shows another animal or a creature.
  * nv_replace: character entries that no prompt uses, or that only shorten a cast string, are removed (unless removing
    one would push a prompt over 800); entries that send Indio with a bare neck or M with another medallion are kept and
    reported (NV_STORY).
  * over 800 characters as make_keys sends it after the cast strings go in -> shorten the SCENE wording only: anti-text
    words END already says ("no text", "no letters": not for the ep01 flat layout, whose own line is its END), decorative
    adjectives, "detailed background", mild adjectives, the long single-image line; style lines are never touched. Still
    over -> prompt left alone (LENGTH).
  * plates are never changed. Every candidate is linted again before it is kept: anything not EXACT -> left alone.
  * the file is edited by exact replacement of the changed JSON strings only, re-read right before writing and written
    atomically (temp file + rename); if it changed meanwhile the whole computation is redone.
"""
import json, os, re, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cast_lint as L

def arg(a, f, d=None):
    return a[a.index(f) + 1] if f in a else d

# ------------------------------------------------------------------ scene shortening
SHORTEN = [
    ('END already says it', re.compile(r"(?:,\s*|\s+)\bno (?:readable |visible )?(?:text|letters|logos?|watermarks?)\b(?=\s*[,.;]|\s*$)", re.I), ''),
    ('decorative words', re.compile(r"\b(?:very|really|extremely|incredibly|highly|beautiful|beautifully|stunning|gorgeous|breathtaking|"
                                    r"majestic|epic|magical|lush|vibrant|glorious|delicate|intricate|softly|gently|slightly|subtle|subtly|"
                                    r"dramatic|dramatically|cinematic|brilliant|dazzling|elegant|lovely|richly|vivid)\s+(?=[a-z])"), ''),
    ('detailed background', re.compile(r"(?:,\s*)?\b(?:highly )?detailed (?:full )?background\b", re.I), ''),
    ('mild adjectives', re.compile(r"\b(?:warm|soft|faint|faintly|gentle)\s+(?=[a-z])"), ''),
    ('single-image line', re.compile(r"Single image, no panels, no border, no black bars, the picture fills the whole vertical frame\.?"), 'Single image, no panels, no border.'),
]
def _tidy(t):
    t = re.sub(r"\s+,", ',', t); t = re.sub(r",\s*,", ',', t); t = re.sub(r",\s*\.", '.', t); t = re.sub(r":\s*,", ':', t)
    t = re.sub(r"\.\s*\.", '.', t); t = re.sub(r" {2,}", ' ', t); return t.strip()

def shorten(text, protected, fits, kind='full'):
    """apply the steps one by one outside the protected strings until fits(text); -> (text, steps used) or (None, steps).
    The END step is skipped for the flat layout (ep01): make_keys appends no END there, the prompt's own anti-text line is it."""
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
        if kind == 'flat' and name == 'END already says it': continue
        n = _tidy(unmask(rx.sub(rep, mask(t))))
        if n != t: used.append(name); t = n
    return (t, used) if fits(t) else (None, used)

# ------------------------------------------------------------------ one prompt
def replacement(p, mm, canon, aside=None):
    """the text that replaces p[mm.start:end]: the cast string, keeping an article/expression word before the head
    ("a tired ...") and an aside in brackets right after it."""
    cb = L.body(canon); cart = canon[:len(canon) - len(cb)].strip()
    cw = set(L.words(canon))
    kept = [w for w in (mm.kept or []) if w.lower() not in cw and not any(c.startswith(w.lower()) for c in cw)]
    if mm.bare:
        new = canon
    elif kept:
        new = (mm.art + ' ' if mm.art else '') + ' '.join(kept) + ' ' + cb
    elif mm.art and mm.art.lower() == 'the':
        new = mm.art + ' ' + cb
    elif mm.art:
        new = (cart.capitalize() if mm.art[0].isupper() else cart) + ' ' + cb
    else:
        new = cb
    before = p[:mm.start].rstrip()
    if (not mm.bare and p[mm.start:mm.start + 1].isupper()) or (mm.bare and (before == '' or before.endswith(('.', '!', '?', ':')))):
        new = new[0].upper() + new[1:]
    if aside: new += ' ' + p[aside[0]:aside[1]]
    return new

def blank_ears(p, ms):
    """ears words next to Usman that the cast string replaces: "ears up / pricked / flying" (they contradict one folded ear)
    and "the other (ear) standing up" (the cast says only "one folded ear") -> (spans to delete, p with them blanked so
    the tail scanner reads past them)"""
    spans = []
    for mm in ms:
        if mm.char != 'usman': continue
        for rx in (L.EARS_WRONG, L.OTHER_EAR):
            for w in rx.finditer(p, mm.start, min(len(p), mm.end + 160)):
                if not any(a <= w.start() < b for a, b in spans): spans.append((w.start(), w.end()))
    pm = p
    for a, b in spans: pm = pm[:a] + ' ' * (b - a) + pm[b:]
    return sorted(spans), pm

def clothes_left(reg, canon):
    cw = set(L.words(canon))
    return [w for w in L.words(reg) if L.CLOTHES_RE.search(w) and not L.ACCESS.search(w) and w not in cw
            and w not in ('clothes', 'outfit', 'dressed', 'sleeves', 'sleeve', 'collar', 'barefoot')]

LEAVE = ('UNSURE', 'NOCANON', 'STORY', 'DOUBLE', 'SECOND')
def fix_prompt(K, kind, key, p, ep, canon, nv, story_nv=()):
    """-> dict(status=changed|clean|left, new, reasons, notes, used)"""
    era, ms, recs, need = L.analyse(p, ep, key, canon)
    reasons, used, edits = [], [], []                      # edits: (start, end, text, char, canon or None)
    ears, pm = blank_ears(p, ms)
    for r in recs:
        mm, cls = r['mm'], r['cls']
        if cls in LEAVE: reasons.append(f'{mm.char} {cls}: {r["detail"]} ("{p[mm.start:mm.end][:80]}")'); continue
        if mm.ref: continue                                   # back-reference: as written (its "ears up" goes below)
        s = r['string']; used.append((r['name'], s))
        for k in story_nv:
            if k.rstrip(', ') in s or L.body(s) in k:
                reasons.append(f'{mm.char}: nv_replace sends {r["name"]} as a short form without the medallion (NV_STORY): a person decides')
        if cls == 'EXACT' or (cls == 'WRONG' and (p.startswith(L.body(s), mm.vstart) or p.startswith(re.sub(r'\ba ([aeiou])', r'an \1', L.body(s)), mm.vstart))): continue
        if mm.bare:
            edits.append((mm.start, mm.end, replacement(p, mm, s), mm.char, s)); continue
        dels, aside, stop = L.desc_tail(pm, mm.hend, mm.char, s)
        if mm.char == 'indio' and clothes_left(stop, s):
            reasons.append(f'indio: this shot names clothes the episode outfit does not have ("{stop.strip()[:60]}"): a person decides'); continue
        edits.append((mm.start, mm.hend, replacement(p, mm, s), mm.char, s))
        for a, b in dels: edits.append((a, b, '', mm.char, None))
    if reasons: return dict(status='left', new=p, reasons=reasons)
    for a, b in ears:
        if not any(x <= a < y for x, y, *_ in edits): edits.append((a, b, '', 'usman', None))
    edits.sort(key=lambda e: e[0])
    for (a1, b1, *_), (a2, b2, *_) in zip(edits, edits[1:]):
        if a2 < b1: return dict(status='left', new=p, reasons=['two character descriptions overlap in this prompt: a person rewrites it'])
    new, off, placed = p, 0, []
    for a, b, txt, ch, s in edits:
        new = new[:a + off] + txt + new[b + off:]
        if s: placed.append((a + off + len(txt), ch, s))
        off += len(txt) - (b - a)
    for at, ch, s in placed:                                  # the old description must not go on after the cast string
        at = new.find(L.body(s)) + len(L.body(s)) if L.body(s) in new else at
        reg = L.marks_only(L.region_after(new, at), s)
        mk = L.AFTER_MARK.get(ch)
        if mk and mk.search(reg):
            return dict(status='left', new=p, reasons=[f'{ch}: the description goes on after the scene words ("{reg.strip()[:80]}", {mk.search(reg).group(0)}): pasting the cast string would leave it twice; a person rewrites it'])
    for at, ch, s in reversed(placed):                        # "...at her neck with long black hair" -> "...at her neck, with ..."
        if re.match(r" (?:with|wearing)\b", new[at:at + 9]): new = new[:at] + ',' + new[at:]
    if need:
        st, _ = L.clause_state(new, need)
        if st == 'NEAR' and need == L.NODOG_ONLY:
            new = L.NOANIMALS_RX.sub('', new, count=1)
        elif st == 'NEAR':
            m = L.NODOG_RX.search(new); rep = need[0].upper() + need[1:] if new[m.start()].isupper() else need
            new = new[:m.start()] + rep + new[m.end():]
        elif st == 'MISSING':
            s0 = new.rstrip()
            new = (s0 + ' ' + need[0].upper() + need[1:] + '.') if s0.endswith('.') else (s0 + ', ' + need + '.')
    lost = L.dropped_words(p, new, sorted({e[3] for e in edits}), [e[4] for e in edits if e[4]])
    if lost:
        return dict(status='left', new=p, reasons=['the rewrite would drop scene words (' + ', '.join(sorted(set(lost))) + '): a person rewrites it'])
    notes = []
    fits = lambda t: len(L.assemble(K, kind, t, nv)) <= L.LIMIT
    if not fits(new):
        before = len(L.assemble(K, kind, new, nv))
        style = [K.get('style', ''), K.get('white', ''), canon.C['raw'].get('style', ''), canon.C['raw'].get('end', '')]
        short, steps = shorten(new, [s for _, s in used] + [L.body(s) for _, s in used] + [need] + style, fits, kind)
        if short is None:
            return dict(status='left', new=p, reasons=[f'LENGTH: over {L.LIMIT} even after shortening the scene ({before} sent with the cast strings; tried: {", ".join(steps) or "nothing to drop"}): needs a shorter scene by hand or a short cast form'])
        notes.append(f'scene shortened ({before} -> {len(L.assemble(K, kind, short, nv))} sent): ' + ', '.join(steps)); new = short
    bad = check_candidate(K, kind, key, new, ep, canon, need)
    if bad: return dict(status='left', new=p, reasons=['the rewrite did not lint clean: ' + '; '.join(bad)])
    return dict(status='changed' if new != p else 'clean', new=new, reasons=[], notes=notes, used=used)

def check_candidate(K, kind, key, p, ep, canon, need):
    era, ms, recs, need2 = L.analyse(p, ep, key, canon)
    bad = [f'{r["mm"].char} {r["cls"]}: {r["detail"]}' for r in recs if r['cls'] not in L.OKCLS]
    st, msg = L.clause_state(p, need if need is not None else need2)
    if st != 'OK': bad.append(msg)
    return bad

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
def plan(epdir, C, only=None, wear_medallion=False):
    path = os.path.join(epdir, 'key_prompts.json')
    T = open(path).read(); K = json.loads(T)
    ep = L.ep_num(epdir)
    items, canon = L.setup_canon(C, K, ep, wear_medallion)
    nv_all = dict(K.get('nv_replace', {}))
    nvs = L.nv_status(K, items)
    story_nv = [k for k, (st, _) in nvs.items() if st == 'story']
    cnv = [] if only else [k for k, (st, _) in nvs.items() if st != 'story']
    nv_new = {k: v for k, v in nv_all.items() if k not in cnv}
    results = {}
    for kind, key, p in items:
        if only and key != only: continue
        results[(kind, key)] = fix_prompt(K, kind, key, p, ep, canon, nv_new, story_nv)
    kept_nv = []
    if cnv:                                                     # does dropping the character nv entries push any prompt over?
        prot = [s for s in C['str'].values()] + [L.body(s) for s in C['str'].values()] + [L.ALONE, L.NODOG]
        for kind, key, p in items:
            r = results.get((kind, key))
            cur = r['new'] if r else p
            fits_new = lambda t: len(L.assemble(K, kind, t, nv_new)) <= L.LIMIT
            if fits_new(cur) or len(L.assemble(K, kind, cur, nv_all)) > L.LIMIT: continue
            if r and r['status'] != 'left':
                short, steps = shorten(cur, prot, fits_new, kind)
                if short is not None and not check_candidate(K, kind, key, short, ep, canon, None):
                    results[(kind, key)] = dict(status='changed' if short != p else 'clean', new=short, reasons=[], used=r.get('used', []),
                                                notes=r.get('notes', []) + [f'scene shortened so the cast strings fit without nv_replace: {", ".join(steps)}'])
                    continue
            for k in cnv:
                if k in L.assemble(K, kind, cur, {}) and k not in kept_nv: kept_nv.append(k)
            if r and r['status'] != 'left':
                r.setdefault('notes', []).append('needs the nv_replace short form to fit 800: entry kept')
    nv_final = {k: v for k, v in nv_all.items() if k not in cnv or k in kept_nv}
    used_names = {n for r in results.values() if r['status'] in ('changed', 'clean') for n, _ in r.get('used', [])}
    new_outfits = [(n.split('.', 1)[1], s) for n, s in canon.unsaved() if n in used_names]
    return dict(path=path, T=T, K=K, ep=ep, results=results, nv_removed=[k for k in cnv if k not in kept_nv], nv_kept=kept_nv,
                nv_story=story_nv, nv_final=nv_final, outfits=new_outfits)

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
           'nv_kept': P['nv_kept'], 'nv_story': P['nv_story'], 'outfits_built': P['outfits']}
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
    if out['nv_removed']: Lr.append(f"\nnv_replace: {len(out['nv_removed'])} character entries removed (they rewrote the cast strings before sending, or no prompt used them)")
    if out['nv_kept']: Lr.append(f"nv_replace: {len(out['nv_kept'])} character entries KEPT because a prompt would not fit 800 without them")
    if out['nv_story']: Lr.append(f"nv_replace: {len(out['nv_story'])} entries KEPT that send Indio without the medallion (bare neck) or M with another medallion: a person decides")
    for n, s in out['outfits_built']: Lr.append(f'era outfit built from the template: indio_outfits.{n} = "{s}"')
    return '\n'.join(Lr)

def atomic_write(path, text):
    """write to a temp file in the same folder and rename it over the old one: a reader never sees half a file."""
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix='.' + os.path.basename(path) + '.', suffix='.tmp')
    try:
        with os.fdopen(fd, 'w') as f: f.write(text)
        try: os.chmod(tmp, os.stat(path).st_mode & 0o777)
        except OSError: pass
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp): os.unlink(tmp)
        raise

def save_outfits(C, outfits):
    """add the built outfits to the cast file (shared by every machine): re-read it, add only missing names, check, atomic."""
    cp = C['_path']; CT = open(cp).read(); exp = json.loads(CT)
    add = [(k, v) for k, v in outfits if k not in exp.get('indio_outfits', {})]
    if not add: return []
    NT = add_outfits(CT, add)
    for k, v in add: exp['indio_outfits'][k] = v
    if json.loads(NT) != exp: raise ValueError('cast file edit does not parse as expected: cast file not written')
    if open(cp).read() != CT: return None
    atomic_write(cp, NT); return [k for k, _ in add]

USAGE = 'usage: cast_fix.py --ep videos/<slug> [--dry-run | --write] [--only NAME] [--save-outfit] [--wear-medallion] [--cast PATH] [--json]'
def main(a):
    """exit 0 = done (dry run or written), 1 = written but something was left for a person / not saved, 2 = could not run."""
    try:
        flags = {'--write', '--dry-run', '--save-outfit', '--json', '--wear-medallion'}
        withval = {'--ep', '--only', '--cast'}
        i, opt = 0, {}
        while i < len(a):
            x = a[i]
            if x in withval:
                if i + 1 >= len(a) or a[i + 1].startswith('--'): raise L.UsageError(f'{x} needs a value')
                opt[x] = a[i + 1]; i += 2; continue
            if x in flags: opt[x] = True; i += 1; continue
            raise L.UsageError(f'unknown argument {x}')
        if '--ep' not in opt: raise L.UsageError('--ep is required')
        epdir = opt['--ep'] if os.path.isdir(opt['--ep']) else os.path.join(L.ROOT, opt['--ep'])
        if not os.path.isfile(os.path.join(epdir, 'key_prompts.json')): raise L.UsageError(f'{opt["--ep"]}: no key_prompts.json there')
        write, only, js, wm = '--write' in opt, opt.get('--only'), '--json' in opt, '--wear-medallion' in opt
        C = L.load_cast(opt.get('--cast'))
        if only:
            K0 = json.load(open(os.path.join(epdir, 'key_prompts.json')))
            if only not in {k for _, k, _ in L.prompts(K0)}: raise L.UsageError(f'--only {only}: no such prompt in chars/full of this episode')
    except (L.UsageError, L.CastError) as e:
        print(f'cast_fix: {e}\n{USAGE}', file=sys.stderr); return 2
    except ValueError as e:
        print(f'cast_fix: cannot read {opt.get("--ep")}: {e}', file=sys.stderr); return 2
    try:
        for attempt in range(4):
            P = plan(epdir, C, only, wm)
            print(report(P, epdir, js))
            left = sum(1 for r in P['results'].values() if r['status'] == 'left')
            if not write: print('\n(dry run: nothing written; add --write)'); return 0
            newT = apply(P, only)
            if '--save-outfit' in opt and P['outfits']:          # the shared cast file first: if it cannot be saved, nothing is written
                saved = save_outfits(C, P['outfits'])
                if saved is None: print('cast file changed meanwhile; redoing'); C = L.load_cast(opt.get('--cast')); continue
                if saved: print('saved to', C['_path'], ':', ', '.join('indio_outfits.' + k for k in saved)); C = L.load_cast(opt.get('--cast'))
            if open(P['path']).read() != P['T']:                 # changed under us (another machine): redo this file
                print('key_prompts.json changed while planning; redoing'); continue
            if newT != P['T']: atomic_write(P['path'], newT); print('written', P['path'])
            else: print('nothing to change in', P['path'])
            return 1 if left else 0
        print('gave up: the file kept changing', file=sys.stderr); return 2
    except Exception as e:
        print(f'cast_fix: failed on {epdir}: {type(e).__name__}: {e} (nothing written for this step)', file=sys.stderr); return 2

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
