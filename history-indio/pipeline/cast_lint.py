#!/usr/bin/env python3
"""Character lint for History Indio key prompts: does every character mention carry the canonical cast string?

usage: cast_lint.py [videos/<slug> ...] [--json] [--all] [--cast characters/series_cast.json] [-v]
  no episode named = every videos/ep*/ ; --json = machine output ; -v = also list EXACT mentions.
Reports, per prompt: every character mention that is not the cast string from characters/series_cast.json (NEAR = other
words, MISSING = a constant is absent, WRONG = contradicts the cast), the cases a person must decide (NOCANON = the cast
file has no string for this age or outfit, UNSURE = cannot tell who it is or which outfit, STORY = the prompt says on purpose
"no tattoos" / "bare neck" where the cast string has them), the "he is alone, no dog, no animals" clause of modern-day
prompts, characters in plates, and every prompt over 800 characters as make_keys.py sends it (after nv_replace).
Exit 0 = clean, 1 = something found (gate a redraw on it). cast_fix.py repairs what can be repaired automatically.
How it decides (the rules cast_fix uses too): see audit/README.md, "Character lint".
"""
import json, os, re, sys, glob, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                                     # history-indio/
LIMIT = 800                                                      # make_keys.py cuts at 800; the free endpoint refuses longer
END = ' Vertical 9:16. No text, no letters, no logos, no watermarks.'   # make_keys.py END
ALONE = 'he is alone, no dog, no animals'
NODOG = 'no dog, no animals'                                     # used instead of ALONE when other people are in the picture
TATTOO_COUNT_UNTIL = 6     # "episode N starts with N-1 tattoos" holds to ep06; the story gives no tattoo in ep06/ep07 (SERIES.md)
NODOG_UNTIL = 30           # from the end of ep30 the story keeps Usman in the present (episode notes)
NUMW = ['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve']
SKIP_TOP = {'_note', 'style', 'white', 'bg', 'end', 'shots', 'nv_replace', 'plates', 'chars', 'full'}

# ------------------------------------------------------------------ cast
def load_cast(path=None):
    path = path or os.path.join(ROOT, 'characters', 'series_cast.json')
    raw = json.load(open(path))
    C = {'_path': path, 'raw': raw, 'str': {}, 'notes': [], 'outfits': {}}
    def clean(name, s):
        m = re.search(r' \(([^()]*)\)$', s)                       # a trailing editorial note is not part of the pasteable string
        if m and name != 'indio_era_template':
            C['notes'].append(f'{name}: ends in an editorial note "({m.group(1)[:70]}...)"; the pasteable string is the text before it')
            s = s[:m.start()]
        return s
    for k, v in raw.items():
        if isinstance(v, str) and not k.startswith('_') and k not in ('style', 'end', 'no_text_clause'): C['str'][k] = clean(k, v)
    for k, v in raw.get('indio_outfits', {}).items():
        C['outfits'][k] = clean('indio_outfits.' + k, v); C['str']['indio_outfits.' + k] = C['outfits'][k]
    for k, s in C['outfits'].items():
        if k.startswith('modern'): continue
        miss = [w for w, rx in (('headband', 'headband'), ('medallion', 'medallion'), ('tattoos', 'tattoo')) if rx not in s]
        if miss: C['notes'].append(f'indio_outfits.{k} lacks {", ".join(miss)} (cast rule: constants in every era); cast_fix builds a template outfit instead')
        n = tattoo_count(s)
        if n is not None: C['notes'].append(f'indio_outfits.{k} names {n} tattoo(s): right only for episode {n + 1}; other episodes get a template outfit with their own count')
    for k, v in C['str'].items():
        if re.search(r'\ba [aeiou]', v): C['notes'].append(f'{k} says "{re.search(r"\ba [aeiou]\w*", v).group(0)}" (grammar); pasted verbatim all the same')
    for k in ('indio_modern_2012',):
        if k in C['str'] and 'medallion' not in C['str'][k]:
            C['notes'].append(f'{k} has no medallion ("bare neck with no necklace") against the rule "medallion in every era"; the string wins for present-day scenes from ep10')
    C['notes'].append('no cast string for Indio from about 25 to his forties (ep32-ep41), nor for Tala, Tubal, Sinag, Albo, Teddy, Lola Ising: those mentions are NOCANON')
    C['notes'].append('rules say Usman is never in the present; the episode notes keep him there from the end of ep30, so the present-day Usman check stops at ep%02d' % NODOG_UNTIL)
    return C

def body(s):                                                    # the canonical string without its leading article
    return re.sub(r'^(?:an?|the) ', '', s)

def numword(n): return NUMW[n] if 0 <= n < len(NUMW) else str(n)

def tattoo_count(s):
    m = re.search(r'\b(no|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|\d+)\b(?: [\w-]+){0,3}? tattoos?\b', s, re.I)
    if not m: return None
    w = m.group(1).lower(); return NUMW.index(w) if w in NUMW else int(w)

TEMPLATE_SLOT = '<ordinary commoner clothes of that place and year>'
def tattoo_phrase(ep):
    n = ep - 1
    if ep <= TATTOO_COUNT_UNTIL:
        return f'one indigo geometric tattoo on his right forearm' if n == 1 else f'{numword(n)} indigo geometric tattoos on his right forearm'
    return 'indigo geometric tattoos on his right forearm'          # the count is not drawable past a handful, and the story skips some

def build_outfit(C, clothes, ep):
    t = C['raw']['indio_era_template']
    t = re.sub(r'indigo geometric tattoos on his forearms \([^()]*\)', tattoo_phrase(ep), t)
    return t.replace(TEMPLATE_SLOT, clothes)

def outfit_clothes(s):
    m = re.search(r'wearing (.+?), a round bronze medallion', s); return m.group(1) if m else None

# ------------------------------------------------------------------ vocabulary
CLOTHES = (r"t-shirt|shirt|\btee\b|polo|jeans|slacks|trousers|pants|shorts|sneakers|shoes|sandals|boots|windbreaker|jacket|"
           r"\bcoat\b|\bsuit\b|\btie\b|vest|tunic|sash|cloak|camisa|\bbaro\b|barong|backpack|loincloth|bahag|\brobe\b|uniform|hoodie|"
           r"sweater|\bcap\b|\bhat\b|salakot|sunglasses|watch(?:es)?\b|apron|scarf|belt|armou?r|\bcape\b|sleeves|collar|\bwrap\b|kimono|"
           r"poncho|raincoat|gloves|helmet|jersey|clothes|outfit|dressed|barefoot|skirt")
CLOTHES_RE = re.compile(CLOTHES, re.I)
CARRY = r"\bno (?:logos?|patch(?:es)?|badges?|lettering|letters|text|writing|print|brand)\b(?: anywhere)?"   # anti-text notes kept beside the cast string
CARRY_RE = re.compile(CARRY, re.I)
NONCASUAL = re.compile(r"silk|\bsuit\b|\btie\b|jacket|hoodie|\bcoat\b|uniform|sunglasses|watch|barong|apron|sweater|raincoat|poncho|"
                       r"tuxedo|vest|helmet|\bcap\b|\bhat\b|armou?r|\brobe\b|\bcape\b|towel|sando|tank top|shorts|shirtless|bare-chested|"
                       r"windbreaker|rider|backpack", re.I)
ERA_CLOTHES = re.compile(r"tunic|sash|camisa|\bbaro\b|cloak|bahag|loincloth|\brobe\b|sandals|barefoot|collarless|wool|linen|homespun|"
                         r"trousers|kimono|\bwrap\b", re.I)
MOD_CLOTHES = re.compile(r"t-shirt|\bjeans\b|\bpolo\b|sneakers|hoodie|windbreaker|jacket|\bsuit\b|\bslacks\b|backpack|silk shirt", re.I)
INDIO_V = re.compile(r"topknot|\bhair\b|\bskin\b|\blean\b|\bslim\b|\bsmall\b|\bthin\b|young|about twenty|twenty|thirt|forties|forty|grey (?:strands|hairs)|"
                     r"headband|long tails|medallion|necklace|\bneck\b|tattoo|forearm|handkerchief|\bwrist\b|adult face|" + CARRY + "|" + CLOTHES, re.I)
INDIO_ADJ = {'young', 'lean', 'slim', 'thin', 'small', 'tall', 'brown-skinned', 'ten-year-old', 'filipino'}
INDIO_MARK = re.compile(r'topknot|headband|handkerchief|medallion|tattoo|schoolboy|ten-year-old', re.I)
USMAN_V = re.compile(r"medium-sized|\bblack\b|philippine|street|white|chest|patch|folded|\bears?\b|bright|clever|\beyes\b|kerchief|"
                     r"\bneck\b|aspin|short-haired|\bfur\b|scruffy", re.I)
USMAN_ADJ = {'medium-sized', 'black', 'philippine', 'street', 'short-haired', 'small', 'scruffy', 'aspin', 'little', 'slim'}
USMAN_MARK = re.compile(r'\bblack\b|street|patch|kerchief|folded ear|aspin', re.I)
M_V = re.compile(r"mysterious|\bhair\b|\bcoat\b|umbrella|medallion|\bneck\b|skirt|cloak|\bhood|crescent|filipina|young", re.I)
M_ADJ = {'mysterious', 'young', 'filipina', 'slim', 'tall'}
M_MARK = re.compile(r'mysterious|dark (?:[\w-]+ )?coat|red umbrella|dark (?:hooded )?cloak', re.I)
GEN_V = re.compile(r"\bhair\b|grey-haired|wrinkled|\bface\b|seventies|sixty|twenties|polo|shirt|medallion|\bcord\b|\bneck\b|engraved|"
                   r"\bbun\b|glasses|dress|blouse|pigtails|uniform|filipin|about ten|\bkind\b|patient|\bthin\b|chubby", re.I)
GEN_ADJ = {'thin', 'grey-haired', 'old', 'kind', 'filipino', 'filipina', 'young', 'public', 'school', 'chubby', 'small', 'elderly'}
OTHER_HEAD = re.compile(r"\b(?:woman|women|girl|girls|boy|boys|dog|dogs|man|men|grandmother|grandfather|teacher|child|children|people|"
                        r"crowd|soldiers?|priest|figure|datu|king|queen|friar|schoolgirl|schoolboy|Filipino|Filipina|Usman|Indio)\b")
ING_OK = (r"wearing|matching|ring|earring|string|sling|clothing|lining|stocking|leggings?|evening|morning|building|king|wing|bring|thing|"
          r"nothing|something|sibling|ceiling|padding|stitching|darling|piping|herring|spring|swing|fling")
STOPW = re.compile(r"\b(?!(?:" + ING_OK + r")\b)\w+ing\b|\b(?:who|which|while|as|then|beside|next|alone|together|stands|sits|holds|looks|"
                   r"walks|runs|kneels|reaches|turns|catches|smiles|raises|points|leans|watches|steps|carries|faces|takes|gives|opens|"
                   r"lies|grins|nods|waves|hugs|pulls|pushes|stares|peers|lifts|drops|eats|reads|says|shouts|whispers|jumps|falls|"
                   r"rises|climbs|rides|bows|squats|crouches|sprints|dives|swims|throws|grabs|touches|places|puts|shows|offers|hands|"
                   r"cries|laughs|is|are|has|have|seen|shot|drawn|framed|silhouetted|both|each|one person|only)\b|"
                   r"\b(?:at|in|on|by|under|beside|behind|inside|near|from|into|onto|toward|towards|across|through|against|between|among|"
                   r"amid|before|after|above|below|beneath|outside|along|past|around|over|up|down|to|for)\s+(?:the|this|that|these|those|"
                   r"its|their|her|them|him)\b", re.I)
NEG_STORY = [('tattoo', re.compile(r'no tattoos?|without (?:any )?tattoos|bare (?:clean )?forearms', re.I)),
             ('medallion', re.compile(r'bare neck|no necklace|no medallion|without (?:the |any |a )?(?:medallion|necklace)', re.I)),
             ('headband', re.compile(r'no headband|without (?:a |the |his )?headband', re.I)),
             ('topknot', re.compile(r'no topknot|short hair|shaved head', re.I))]
EARS_WRONG = re.compile(r"(?:,\s*|\s+)(?:with\s+|his\s+|its\s+)?(?:both\s+)?ears\s+(?:up|flying|pricked|perked|raised|upright)\b"
                        r"|(?:,\s*|\s+)(?:two upright ears|pricked ears|perked ears|floppy ears)\b", re.I)
EARS_BAD_BREED = re.compile(r'floppy-eared|labrador|golden retriever|\bpuppy\b', re.I)

PRESENT = re.compile(r'\b(?:present[- ]day|today|modern(?! Japanese| TV| anime)|smartphones?|phones?|laptops?|jeepneys?|motorcycles?|'
                     r'sidecar|cars?|offices?|elevators?|hotel|yacht|billboards?|TV|video call|condo|apartment|parking|senat\w*|campaign|'
                     r'airport|taxi|delivery|fluorescent|tricycles?|mall|vlogger|20[0-2]\d)\b', re.I)
NOTMOD = re.compile(r'nothing modern', re.I)
PAST = re.compile(r'\b(?:1[0-8]\d\d|19[0-4]\d|[2-9]\d\d)s?\b|pre-?colonial|colonial|ancient|galleon|Victorian|Katipunan|medieval|'
                  r'biblical|primeval|\bAD\b|\bBC\b', re.I)
VIEW = re.compile(r'through the (?:brass |golden-rimmed )?lens|hologram|sepia|old[- ]print|photograph|memory|painting|screen|vision', re.I)
JUMP = re.compile(r'time portal|portal|\bjump|lagusan|swirl of golden light|golden light|clock gears|dissolv|fading into|sparks|'
                  r'translucen|ghostly', re.I)
PERSON = re.compile(r"\b(?:woman|women|girls?|boys?|man|men|people|crowd|children|kids|child|grandmother|grandfather|teacher|vendors?|"
                    r"friends?|stranger|pupils|students|soldiers|guards|workers|family|couple|mother|father|baby|toddler|passengers|"
                    r"tourists|customers|someone|figures?|officials?|politicians?|reporters?|nurse|doctor|driver|lola|lolo)\b", re.I)
PERSON_NEG = re.compile(r"\b(?:no|nobody|no other|without|empty of|not a|no one)\s+(?:[\w-]+\s+){0,2}?"
                        r"(?:woman|women|girls?|boys?|man|men|people|crowd|children|kids|child|person|persons|figures?|one)\b", re.I)

# ------------------------------------------------------------------ episode files
def ep_num(slug):
    m = re.match(r'ep(\d+)', os.path.basename(slug.rstrip('/'))); return int(m.group(1)) if m else 0

def prompts(K):
    """(kind, key, text) for every prompt that make_keys draws; ep01 keeps flat top-level prompts."""
    if 'chars' in K or 'full' in K:
        for kind in ('chars', 'full'):
            for k, v in K.get(kind, {}).items():
                if isinstance(v, str): yield kind, k, v
    else:
        for k, v in K.items():
            if k not in SKIP_TOP and isinstance(v, str) and len(v) > 60: yield 'flat', k, v

def assemble(K, kind, p, nv=None):
    if kind == 'flat': y = p
    elif kind == 'chars': y = K['white'] + p + ' ' + K['style'] + END
    elif kind == 'plates': y = K['style'] + 'Background art only, no people, no animals: ' + p + END
    else: y = K['style'] + p + END
    for a, b in (K.get('nv_replace', {}) if nv is None else nv).items(): y = y.replace(a, b)
    return y

CHAR_NV = re.compile(r'Filipino man|Filipina woman|street dog|topknot|grandfather|grandmother|schoolboy|schoolgirl|teacher', re.I)
def char_nv_entries(K):
    return [k for k in K.get('nv_replace', {}) if CHAR_NV.search(k) and k not in (K.get('style'), K.get('white'))]

# ------------------------------------------------------------------ scene
def scene_era(p):
    pres = bool(PRESENT.search(p)) and not NOTMOD.search(p)
    past = bool(PAST.search(p))
    if past and not pres: return 'past'
    if pres and not past: return 'present'
    if pres and past: return 'present' if VIEW.search(p) else 'mixed'
    return 'unknown'

# ------------------------------------------------------------------ mentions
def _walk_back(p, head_start, adjv):
    """from the head noun go back over adjectives to the article; returns (start, article, kept_adjs, vocab_start)."""
    toks = list(re.finditer(r"[^\s]+", p[max(0, head_start - 90):head_start]))
    off = max(0, head_start - 90)
    vocab_start, kept, start, art = head_start, [], head_start, ''
    for t in reversed(toks):
        w = t.group(0)
        if re.search(r'[,.;:!?()"]$', w) or re.search(r'^[(\"]', w): break
        lw = w.lower()
        if lw in ('a', 'an', 'the'):
            art = w; start = off + t.start(); break
        if lw in adjv:
            if not kept: vocab_start = off + t.start(); start = vocab_start
            continue
        if len(kept) < 2 and re.fullmatch(r"[a-z][\w'-]*", lw):
            kept.insert(0, (off + t.start(), w)); continue
        break
    if not art and kept:                         # non-vocab words without an article are scene words, not adjectives
        kept = []; start = vocab_start
    return start, art, [w for _, w in kept], vocab_start

def _consume(p, pos, vocab, first_with=True):
    """take descriptor segments after the head noun; returns the end of the character description."""
    end, i, first = pos, pos, True
    while True:
        if first:
            c = re.match(r"(?:,\s*|\s+)(?:wearing\s+|with\s+|in\s+)?", p[i:]) if first_with else re.match(r",\s*(?:wearing\s+)?", p[i:])
        else:
            c = re.match(r",\s*(?:wearing\s+|with\s+)?|\s+and\s+(?:wearing\s+|with\s+)?|\s+wearing\s+", p[i:])
        if not c or not c.group(0): break
        s0 = i + c.end()
        b = re.search(r",|\s+and\s+|[.;:!?()]|$", p[s0:])
        seg = p[s0:s0 + b.start()]
        cut = STOPW.search(seg)
        if cut: seg = seg[:cut.start()]
        seg = seg.rstrip()
        if not seg or not vocab.search(seg) or OTHER_HEAD.search(seg): break
        end = s0 + len(seg); first = False
        if cut: break
        i = end
    return end

class Mention(dict):
    __getattr__ = dict.get

def find_mentions(p, ep, key=''):
    out, taken = [], []
    def free(a, b): return not any(a < y and x < b for x, y in taken)
    # ep10 extra cast (their strings are the 2012 / Episode 10 versions)
    if ep == 10:
        for name, head in (('classmate_jm', r'chubby Filipino schoolboy'), ('lolo', r'grandfather'), ('lola_2012', r'grandmother'),
                           ('guro_ep10', r'(?:Filipina|public school) teacher'), ('classmate_bea', r'schoolgirl')):
            for m in re.finditer(head, p):
                if p[m.end():m.end() + 2] == "'s": continue
                hs = m.start() if name != 'classmate_jm' else m.start() + len('chubby ')
                st, art, kept, vs = _walk_back(p, hs, GEN_ADJ)
                e = _consume(p, m.end(), GEN_V)
                if free(st, e): taken.append((st, e)); out.append(Mention(char=name, start=st, end=e, art=art, kept=kept, vstart=vs, head=m.group(0)))
    # Indio
    for m in re.finditer(r"\bFilipino (?:man|schoolboy|boy)\b|\byoung man\b|\bIndio\b", p):
        if p[m.end():m.end() + 2] == "'s" or not free(m.start(), m.end()): continue
        if m.group(0) == 'Indio':
            taken.append((m.start(), m.end())); out.append(Mention(char='indio', start=m.start(), end=m.end(), art='', kept=[], vstart=m.start(), head='Indio', bare=True)); continue
        hs = m.start() + (0 if m.group(0) == 'young man' else 0)
        st, art, kept, vs = _walk_back(p, hs, INDIO_ADJ)
        e = _consume(p, m.end(), INDIO_V)
        span = p[st:e]
        if not INDIO_MARK.search(span):
            if art.lower() == 'the' and any(x.char == 'indio' for x in out): continue      # "the young man": back-reference
            if re.search(r'\bold\b|grandfather|sixties|seventies|fifties|heavyset|teenage', span, re.I): continue
            if m.group(0) == 'young man' and not key.lower().startswith('indio'): continue
            taken.append((st, e)); out.append(Mention(char='indio', start=st, end=e, art=art, kept=kept, vstart=vs, head=m.group(0), unsure='no Indio marker (topknot, headband, handkerchief, medallion, tattoo): another man, or Indio with every constant missing'))
            continue
        taken.append((st, e)); out.append(Mention(char='indio', start=st, end=e, art=art, kept=kept, vstart=vs, head=m.group(0)))
    # Usman (negated "no dog" is not a mention)
    t0 = re.sub(r"\b(?:[Nn]o|NO|not a|without (?:a |the |any )?|[Oo]nly one|ONE|[Ee]xactly one|One|[Ee]xactly ONE|other) (?:[\w-]+ )?(?:dogs?|animals?)\b",
                lambda x: '#' * len(x.group(0)), p)
    for m in re.finditer(r"\bdog\b|\baspin\b|\bUsman\b", t0):
        if p[m.end():m.end() + 2] == "'s" or re.match(r"-(?:like|shaped)", p[m.end():]) or not free(m.start(), m.end()): continue
        if m.group(0) == 'Usman':
            if re.match(r",\s*(?:a|the)\s+(?:[\w-]+\s+){0,5}dog\b", p[m.end():]): continue      # "Usman, a black ... dog" (the dog phrase is the mention)
            taken.append((m.start(), m.end())); out.append(Mention(char='usman', start=m.start(), end=m.end(), art='', kept=[], vstart=m.start(), head='Usman', bare=True)); continue
        st, art, kept, vs = _walk_back(p, m.start(), USMAN_ADJ)
        e = _consume(p, m.end(), USMAN_V)
        span = p[st:e]
        if re.search(r'collar|bears and a dog|drawn as glowing', span, re.I) and not USMAN_MARK.search(span): continue
        if not USMAN_MARK.search(span):
            if any(x.char == 'usman' for x in out): continue                       # "the dog": back-reference to a described Usman
            if ep == 4: continue                                                   # Pepe's dog (1869) is not Usman
            taken.append((st, e)); out.append(Mention(char='usman', start=st, end=e, art=art, kept=kept, vstart=vs, head=m.group(0), unsure='a dog with no Usman marker (black, street, patch, kerchief): Usman or another dog?'))
            continue
        taken.append((st, e)); out.append(Mention(char='usman', start=st, end=e, art=art, kept=kept, vstart=vs, head=m.group(0)))
    # M
    for m in re.finditer(r"\bwoman\b", p):
        if p[m.end():m.end() + 2] == "'s" or not free(m.start(), m.end()): continue
        st, art, kept, vs = _walk_back(p, m.start(), M_ADJ)
        e = _consume(p, m.end(), M_V)
        span = p[st:e]
        if not M_MARK.search(span) or re.search(r'snow-white|white hair|grandmother|white dress|in white|fox|\bold\b', span, re.I): continue
        taken.append((st, e)); out.append(Mention(char='m', start=st, end=e, art=art, kept=kept, vstart=vs, head='woman'))
    return sorted(out, key=lambda x: x.start)

# ------------------------------------------------------------------ choosing the canonical string
def mention_variant(span, era, p):
    low = span.lower()
    if re.search(r'schoolboy|\bboy\b|ten-year-old|about ten', low): return 'child'
    if 'headband' in low: return 'era'
    if 'handkerchief' in low and 'pocket' not in low: return 'modern'
    if MOD_CLOTHES.search(low): return 'modern'
    if ERA_CLOTHES.search(low): return 'era'
    if era == 'past': return 'era'
    if era == 'present': return 'modern'
    return None

def clothes_of(span):
    segs = [s.strip() for s in re.split(r",\s*|\s+and\s+", span)]
    keep = []
    for s in segs:
        s = re.sub(r'^(?:wearing|with|in)\s+', '', s)
        s = re.sub(r'^.*?\b(?:man|boy)\s+(?:wearing|with|in)\s+', '', s)
        if CLOTHES_RE.search(s) and not re.search(r'headband|medallion|tattoo|handkerchief|topknot|\bhair\b|\bskin\b|necklace|\bneck\b|forearm', s, re.I):
            keep.append(s)
    return ', '.join(keep)

def noun_key(clothes):
    return frozenset(x.lower().replace('t-shirt', 'tshirt') for x in CLOTHES_RE.findall(clothes or ''))

class EpisodeCanon:
    """per episode: which Indio string each mention gets (era outfits saved or built from the template, modern, child, Season 5)."""
    def __init__(self, C, ep, items):
        self.C, self.ep = C, ep
        self.groups = collections.OrderedDict()               # noun key -> Counter of clothes phrases (past-era Indio)
        self.modern_votes = collections.Counter()
        for kind, key, p in items:
            era = scene_era(p)
            for mm in find_mentions(p, ep, key):
                if mm.char != 'indio' or mm.bare or mm.unsure: continue
                sp = p[mm.start:mm.end]; v = mention_variant(sp, era, p)
                if v == 'era':
                    cl = clothes_of(sp)
                    if cl: self.groups.setdefault(noun_key(cl), collections.Counter())[cl] += 1
                elif v == 'modern':
                    r = self._modern(sp)
                    if r[0]: self.modern_votes[r[0]] += 1
        self.era = {}                                         # noun key -> (name, string, saved?)
        saved = {k: v for k, v in C['outfits'].items() if not k.startswith('modern')}
        n = 0
        for nk, cnt in self.groups.items():
            phrase = sorted(cnt.items(), key=lambda x: (-x[1], -len(x[0])))[0][0]
            match = None
            for k, s in saved.items():
                if noun_key(outfit_clothes(s) or '') == nk: match = (k, s); break
            if match and self._valid(match[1]): self.era[nk] = ('indio_outfits.' + match[0], match[1], True); continue
            if match: phrase = outfit_clothes(match[1]) or phrase          # keep the saved wording of the clothes
            built = build_outfit(C, phrase, ep)
            same = [k for k, s in saved.items() if s == built]
            if same: self.era[nk] = ('indio_outfits.' + same[0], built, True); continue
            n += 1; name = f'ep{ep:02d}' + ('' if n == 1 else f'_{n}')
            self.era[nk] = ('indio_outfits.' + name, built, False)

    def _valid(self, s):
        if not ('headband' in s and 'medallion' in s and 'tattoo' in s): return False
        c = tattoo_count(s)
        if c is None: return True
        return self.ep <= TATTOO_COUNT_UNTIL and c == self.ep - 1

    def _modern(self, sp):
        ep, low = self.ep, sp.lower()
        if 10 <= ep <= 31:
            if NONCASUAL.search(low): return None, 'story outfit not in the cast file (' + NONCASUAL.search(low).group(0) + '): add it to indio_outfits or reword by hand'
            return 'indio_modern_2012', None
        if ep == 1: return 'indio_modern', None
        if 2 <= ep <= 9:
            if re.search(r'windbreaker|rider|orange jacket|orange', low): return 'indio_outfits.modern_rider_from_ep2', None
            if 'polo' in low: return 'indio_modern', None
            if NONCASUAL.search(low): return None, 'story outfit not in the cast file (' + NONCASUAL.search(low).group(0) + ')'
            return '?', None
        return None, 'no cast string for this episode'

    def pick(self, mm, p, era):
        """-> (name, string, None) or (None, None, reason a person must decide)"""
        C, ep = self.C, self.ep
        sp = p[mm.start:mm.end]; low = sp.lower()
        if mm.char != 'indio':
            name = {'usman': 'usman', 'm': 'mystery_woman'}.get(mm.char, mm.char)
            return name, C['str'][name], None
        if re.search(r'thirt|forties|forty|fifties|mid-twenties|twenty-five|late twenties|grey strands|grey hairs|streaked with grey|older', low) or 32 <= ep <= 41:
            if ep >= 42 or (re.search(r'forties|forty', low) and ep >= 41):
                return self._s5(low)
            return None, None, 'no cast string for Indio at this age (about 25 to 41, ep32-ep41): add one to series_cast.json'
        if ep >= 42: return self._s5(low)
        if mm.bare:
            v = 'child' if ep == 10 and re.search(r'\bboy\b|schoolboy|child', p) else mention_variant('', era, p)
        else:
            v = mention_variant(sp, era, p)
        if v == 'child':
            if ep == 10: return 'indio_child_2012', C['str']['indio_child_2012'], None
            return None, None, 'Indio as a child outside Episode 10: the cast has only the 2012 schoolboy'
        if v is None:
            if self.modern_votes and not self.era: v = 'modern'
            elif self.era and not self.modern_votes: v = 'era'
            else: return None, None, 'cannot tell past or present-day outfit from this prompt'
        if v == 'modern':
            name, why = self._modern(low)
            if name == '?':
                name = self.modern_votes.most_common(1)[0][0] if self.modern_votes else None
                if not name: return None, None, 'present-day outfit not named and the episode has no other present-day Indio'
            if not name: return None, None, why
            return name, C['str'][name], None
        cl = clothes_of(sp)
        if cl and noun_key(cl) in self.era:
            n, s, _ = self.era[noun_key(cl)]; return n, s, None
        if not cl:
            if len(self.era) == 1: n, s, _ = list(self.era.values())[0]; return n, s, None
            if not self.era: return None, None, 'past-era Indio with no clothes named anywhere in this episode: write the outfit once'
            return None, None, 'past-era Indio with no clothes named and the episode has %d era outfits' % len(self.era)
        return None, None, 'era clothes not grouped'

    def _s5(self, low):
        if re.search(r'armou?r|anting', low): return 'indio_s5_anting', self.C['str']['indio_s5_anting'], None
        cl = [c for c in CLOTHES_RE.findall(low) if c not in ('coat',)]
        if cl and not re.search(r'long dark grey coat', low):
            return None, None, 'Season 5 Indio in an outfit the cast does not have (%s)' % ', '.join(sorted(set(cl)))
        return 'indio_s5', self.C['str']['indio_s5'], None

    def unsaved(self):
        return [(n, s) for n, s, saved in self.era.values() if not saved]

# ------------------------------------------------------------------ classification
INDIO_CONST = [('topknot', r'topknot'), ('headband', r'headband'), ('medallion', r'medallion'), ('tattoos', r'tattoo'),
               ('wrist handkerchief', r'handkerchief')]
USMAN_CONST = [('white chest patch', r'chest patch'), ('one folded ear', r'folded ear|ear folded'), ('red kerchief', r'kerchief')]
M_CONST = [('long dark coat', r'long dark coat'), ('red umbrella', r'red umbrella'), ('medallion', r'medallion')]

def classify(mm, p, canon_name, canon, ep, era):
    """-> (cls, detail). cls: EXACT NEAR MISSING WRONG STORY"""
    sp = p[mm.start:mm.end]; low = sp.lower(); b = body(canon)
    exact = not mm.bare and p.startswith(b, mm.vstart)
    consts = {'indio': INDIO_CONST, 'usman': USMAN_CONST, 'm': M_CONST}.get(mm.char, [])
    tail_end = _consume(p, mm.vstart + len(b), INDIO_V if mm.char == 'indio' else USMAN_V if mm.char == 'usman' else M_V, first_with=False) if exact else mm.end
    whole = p[mm.start:tail_end].lower()
    if mm.char == 'm' and 'crescent' in whole:
        return 'STORY', "M's crescent-moon medallion (an episode note) against the cast's round bronze medallion: a person decides"
    for what, rx in NEG_STORY:                                 # the prompt says on purpose that a constant is absent
        if what in canon and rx.search(whole) and not rx.search(canon):
            return 'STORY', f'says "{rx.search(whole).group(0)}" but {canon_name} has the {what}: a story choice (e.g. M took the medallion) or drift? a person decides'
    wrong = []
    if mm.char == 'indio':
        if 'headband' in low and 'headband' not in canon: wrong.append('headband in a present-day scene')
        mc = MOD_CLOTHES.search(low)
        if mc and 'headband' in canon and era in ('past', 'mixed') and not JUMP.search(p): wrong.append(f'modern clothes in a past scene ({mc.group(0)})')
        tc = tattoo_count(low)
        if tc is not None and 'headband' in canon and ep <= TATTOO_COUNT_UNTIL and tc != ep - 1: wrong.append(f'{tc} tattoo(s); episode {ep} starts with {ep - 1}')
    if mm.char == 'usman':
        w = EARS_WRONG.search(p[mm.start:min(len(p), tail_end + 120)]) or EARS_BAD_BREED.search(whole)
        if w: wrong.append(f'"{w.group(0).strip(", ")}" contradicts one folded ear')
        if era == 'present' and not JUMP.search(p) and ep < NODOG_UNTIL: wrong.append('Usman in a present-day scene (he exists only in a jump and in the past)')
    if exact and not wrong: return 'EXACT', canon_name
    miss = [n for n, rx in consts if re.search(rx, canon) and not re.search(rx, low)]
    if wrong: return 'WRONG', '; '.join(wrong + (['missing ' + ', '.join(miss)] if miss else []))
    if mm.bare: return 'MISSING', f'name only ("{sp}"): the image engine gets no description'
    if miss: return 'MISSING', 'missing ' + ', '.join(miss) + f' (vs {canon_name})'
    cw = [w for w in dict.fromkeys(re.findall(r"[\w'-]+", b.lower())) if w not in low and w not in ('a', 'an', 'the', 'of', 'on', 'his', 'her', 'with', 'in', 'and', 'tied', 'around', 'wearing', 'about')]
    return 'NEAR', f'other words than {canon_name}' + (' (lacks: ' + ' '.join(cw[:10]) + ')' if cw else '')

def other_people(p, mentions, indio_spans):
    if any(x.char not in ('indio', 'usman') for x in mentions): return True
    if sum(1 for x in mentions if x.char == 'indio') > 1: return True
    t = p
    for a, b in sorted(indio_spans, reverse=True): t = t[:a] + ' ' * (b - a) + t[b:]
    t = PERSON_NEG.sub(lambda x: ' ' * len(x.group(0)), t)
    t = re.sub(r"\b(?:man|woman|boy|girl)'s\b", '', t)
    return bool(PERSON.search(t))

def clause_need(p, ep, mentions, era, resolved, outfit_means_present=True):
    """modern-day prompt without Usman: which clause it needs, or None."""
    if ep > NODOG_UNTIL or any(x.char == 'usman' for x in mentions): return None
    modern = era == 'present' or outfit_means_present and any(x.char == 'indio' and r and 'headband' not in r[1] and r[0] != 'indio_child_2012' for x, r in zip(mentions, resolved))
    if era == 'past' or not modern or JUMP.search(p): return None
    has_indio = any(x.char == 'indio' for x in mentions)
    return ALONE if has_indio and not other_people(p, mentions, [(x.start, x.end) for x in mentions if x.char == 'indio']) else NODOG

NODOG_RX = re.compile(r"\b(?:he is alone,\s*)?no dogs?\b(?:,?\s*(?:and\s+)?no (?:other )?animals?\b)?", re.I)
def clause_state(p, need):
    if need is None: return 'OK', ''
    if need in p: return 'OK', ''
    if need == NODOG and ALONE in p: return 'OK', ''
    if NODOG_RX.search(p): return 'NEAR', f'modern-day prompt says "{NODOG_RX.search(p).group(0)}", not "{need}"'
    return 'MISSING', f'modern-day prompt without "{need}"'

PLATE_CHAR = re.compile(r"\bFilipino man\b|\bFilipina woman\b|\byoung man\b|\byoung woman\b|\bdog\b|\bUsman\b|\bIndio\b|topknot|headband|red umbrella", re.I)
PLATE_NEG = re.compile(r"\b(?:no|nobody|without|empty of|no one|not a)\s+(?:[\w-]+\s+){0,3}?(?:man|men|woman|women|dogs?|people|person|persons|figures?|boy|girl|crowd|animals?|one)\b|nobody|no one", re.I)

def outfit_means_present(canon, items, ep):
    for kind, key, p in items:
        ms = find_mentions(p, ep, key)
        if JUMP.search(p) or not any(x.char == 'usman' and not x.unsure for x in ms): continue
        for x in ms:
            if x.char == 'indio' and not x.unsure and not x.bare and mention_variant(p[x.start:x.end], 'unknown', p) == 'modern': return False
    return True

# ------------------------------------------------------------------ episode lint
def lint_episode(epdir, C, K=None):
    slug = os.path.basename(epdir.rstrip('/')); ep = ep_num(slug)
    K = K if K is not None else json.load(open(os.path.join(epdir, 'key_prompts.json')))
    items = [(k, n, p) for k, n, p in prompts(K) if not p.startswith('(copied')]
    canon = EpisodeCanon(C, ep, items)
    res = {'slug': slug, 'episode': ep, 'episode_issues': [], 'prompts': []}
    cnv = char_nv_entries(K)
    if cnv:
        res['episode_issues'].append({'type': 'NV_REPLACE', 'msg': f'nv_replace rewrites {len(cnv)} character string(s) after the prompt is built, so the cast strings never reach the engine', 'entries': cnv})
    for n, s in canon.unsaved():
        res['episode_issues'].append({'type': 'UNSAVED_OUTFIT', 'msg': f'era outfit built from indio_era_template is not saved in series_cast.json as {n} (cast_fix --save-outfit)', 'name': n, 'string': s})
    for n, p in K.get('plates', {}).items():
        if not isinstance(p, str): continue
        t = PLATE_NEG.sub(lambda x: ' ' * len(x.group(0)), p)
        m = PLATE_CHAR.search(t)
        if m: res['prompts'].append({'kind': 'plates', 'key': n, 'era': scene_era(p), 'sent_len': len(assemble(K, 'plates', p)), 'mentions': [],
                                     'issues': [{'type': 'PLATE_PERSON', 'msg': f'plate (background) mentions "{m.group(0)}": plates must have no characters; a person decides'}]})
    omp = outfit_means_present(canon, items, ep)
    if not omp: res['episode_issues'].append({'type': 'INFO', 'msg': 'the present-day outfit also appears beside Usman outside a jump (e.g. Episode 10 in 2012): only scene words decide the no-dog clause here'})
    for kind, key, p in items:
        era = scene_era(p)
        ms = find_mentions(p, ep, key)
        resolved, out = [], []
        for mm in ms:
            if mm.unsure: resolved.append(None); out.append({'char': mm.char, 'cls': 'UNSURE', 'detail': mm.unsure, 'span': p[mm.start:mm.end], 'start': mm.start, 'end': mm.end}); continue
            name, s, why = canon.pick(mm, p, era)
            if not name:
                resolved.append(None); out.append({'char': mm.char, 'cls': 'NOCANON', 'detail': why, 'span': p[mm.start:mm.end], 'start': mm.start, 'end': mm.end}); continue
            cls, det = classify(mm, p, name, s, ep, era)
            resolved.append((name, s))
            out.append({'char': mm.char, 'cls': cls, 'detail': det, 'canon': name, 'span': p[mm.start:mm.end], 'start': mm.start, 'end': mm.end})
        issues = []
        need = clause_need(p, ep, ms, era, resolved, omp)
        st, msg = clause_state(p, need)
        if st != 'OK': issues.append({'type': 'NO_DOG_' + st, 'msg': msg, 'need': need})
        L = len(assemble(K, kind, p))
        if L > LIMIT: issues.append({'type': 'LENGTH', 'msg': f'{L} characters sent > {LIMIT}: make_keys cuts the end off', 'len': L})
        res['prompts'].append({'kind': kind, 'key': key, 'era': era, 'sent_len': L, 'mentions': out, 'issues': issues})
    return res

def count(res):
    c = collections.Counter()
    for e in res:
        for i in e['episode_issues']:
            if i['type'] != 'INFO': c[i['type']] += 1
        for p in e['prompts']:
            for m in p['mentions']: c[m['cls']] += 1
            for i in p['issues']: c[i['type']] += 1
    return c

BAD = ('NEAR', 'MISSING', 'WRONG', 'STORY', 'NOCANON', 'UNSURE')
def found(res):
    c = count(res); return sum(v for k, v in c.items() if k != 'EXACT')

def text_report(res, C, verbose=False):
    L = []
    L.append('cast file notes (contradictions inside characters/series_cast.json; not counted per prompt):')
    L += ['  - ' + n for n in C['notes']]
    for e in res:
        bad = [p for p in e['prompts'] if p['issues'] or any(m['cls'] != 'EXACT' for m in p['mentions'])]
        L.append('')
        L.append(f"== {e['slug']} (episode {e['episode']}): {len(bad)} of {len(e['prompts'])} prompts need attention")
        for i in e['episode_issues']:
            L.append(f"  [episode] {i['type']}: {i['msg']}")
            if i['type'] == 'UNSAVED_OUTFIT': L.append(f"            \"{i['string']}\"")
        for p in e['prompts']:
            ms = p['mentions'] if verbose else [m for m in p['mentions'] if m['cls'] != 'EXACT']
            if not ms and not p['issues']: continue
            L.append(f"  {p['kind']}/{p['key']}  [{p['era']}, {p['sent_len']} chars sent]")
            for m in ms:
                L.append(f"    {m['cls']:8} {m['char']:14} {m['detail']}")
                if m['cls'] != 'EXACT': L.append(f"             as written: \"{m['span'][:160]}\"")
            for i in p['issues']: L.append(f"    {i['type']:8} {i['msg']}")
    c = count(res)
    L.append('')
    L.append('TOTAL: ' + ', '.join(f'{k} {v}' for k, v in sorted(c.items())) + ('  -> clean' if not found(res) else '  -> exit 1'))
    L.append('NEAR/MISSING/WRONG/NO_DOG/NV_REPLACE/UNSAVED_OUTFIT: cast_fix.py repairs them. NOCANON/UNSURE/STORY/PLATE_PERSON/LENGTH it cannot: a person decides.')
    return '\n'.join(L)

def episode_dirs(args):
    if args: return [a if os.path.isdir(a) else os.path.join(ROOT, a) for a in args]
    return sorted(d for d in glob.glob(os.path.join(ROOT, 'videos', 'ep*')) if os.path.exists(os.path.join(d, 'key_prompts.json')))

def main(argv):
    a = list(argv); js = '--json' in a; verbose = '-v' in a
    cast = a[a.index('--cast') + 1] if '--cast' in a else None
    if cast: i = a.index('--cast'); del a[i:i + 2]
    eps = [x for x in a if not x.startswith('-')]
    C = load_cast(cast)
    res = [lint_episode(d, C) for d in episode_dirs(eps)]
    if js:
        json.dump({'cast_notes': C['notes'], 'totals': count(res), 'episodes': res}, sys.stdout, ensure_ascii=False, indent=1); print()
    else:
        print(text_report(res, C, verbose))
    return 1 if found(res) else 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
