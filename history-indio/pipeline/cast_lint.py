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
class CastError(Exception): pass
NEEDED = ('indio_era_template', 'indio_modern', 'indio_modern_2012', 'indio_child_2012', 'indio_s5', 'indio_s5_anting', 'usman',
          'mystery_woman', 'lolo', 'lola_2012', 'guro_ep10', 'classmate_bea', 'classmate_jm')

def load_cast(path=None):
    path = path or os.path.join(ROOT, 'characters', 'series_cast.json')
    try: raw = json.load(open(path))
    except (OSError, ValueError) as e: raise CastError(f'cannot read the cast file {path}: {e}')
    miss = [k for k in NEEDED if not isinstance(raw.get(k), str)]
    if miss: raise CastError(f'the cast file {path} has no string for: {", ".join(miss)}')
    if TEMPLATE_SLOT not in raw['indio_era_template']: raise CastError(f'indio_era_template has no {TEMPLATE_SLOT} slot')
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
    for k in ('indio_modern', 'indio_outfits.modern_rider_from_ep2', 'indio_modern_2012'):
        if k in C['str'] and 'tattoo' not in C['str'][k]:
            C['notes'].append(f'{k} has no tattoos against "tattoos in every era"; prompts that add them beside the string are kept as they are')
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

PLURAL = {'trousers', 'pants', 'jeans', 'sandals', 'clothes', 'shorts', 'robes', 'sleeves', 'boots', 'shoes', 'sneakers'}
def with_article(clothes):
    if re.match(r'(?:a|an|the|his)\b', clothes, re.I): return clothes
    first = CLOTHES_RE.search(clothes)
    if first and first.group(0).lower() in PLURAL: return clothes
    return ('an ' if re.match(r'[aeiou]', clothes, re.I) else 'a ') + clothes

def build_outfit(C, clothes, ep):
    clothes = with_article(clothes)
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
MOD_CLOTHES = re.compile(r"t-shirt|\bjeans\b|\bpolo\b|sneakers|hoodie|windbreaker|(?:rain|denim|leather|hooded|puffer|bomber|track) jacket|\bsuit\b|\bslacks\b|backpack|silk shirt", re.I)
INDIO_V = re.compile(r"topknot|\bhair\b|\bskin\b|\blean\b|young|about twenty|twenty|thirt|forties|forty|grey (?:strands|hairs)|"
                     r"headband|long tails|medallion|necklace|\bneck\b|tattoo|forearm|handkerchief|\bwrist\b|adult face|" + CARRY + "|" + CLOTHES, re.I)
INDIO_ADJ = {'young', 'lean', 'slim', 'thin', 'brown-skinned', 'ten-year-old', 'filipino'}   # "small", "tall" are framing words: kept
INDIO_MARK = re.compile(r'topknot|headband|handkerchief|medallion|tattoo|schoolboy|ten-year-old', re.I)
USMAN_V = re.compile(r"medium-sized|\bblack\b|philippine|street|white|chest|patch|folded|\bears?\b|bright|clever|\beyes\b|kerchief|"
                     r"\bneck\b|aspin|short-haired|\bfur\b|scruffy", re.I)
USMAN_ADJ = {'medium-sized', 'medium', 'black', 'philippine', 'street', 'short-haired', 'small', 'scruffy', 'aspin', 'little', 'slim', 'lean', 'big', 'large'}
USMAN_MARK = re.compile(r'\bblack\b|street|patch|kerchief|folded ear|aspin', re.I)
M_V = re.compile(r"mysterious|\bhair\b|\bcoat\b|umbrella|medallion|\bneck\b|skirt|cloak|\bhood|crescent|filipina|young", re.I)
M_ADJ = {'mysterious', 'young', 'filipina', 'slim', 'tall'}
M_MARK = re.compile(r'mysterious|dark (?:[\w-]+ ){0,2}(?:coat|cloak)|red umbrella', re.I)
GEN_V = re.compile(r"\bhair\b|grey-haired|wrinkled|\bface\b|seventies|sixty|twenties|polo|shirt|medallion|\bcord\b|\bneck\b|engraved|"
                   r"\bbun\b|glasses|dress|blouse|pigtails|uniform|filipin|about ten|\bkind\b|patient|\bthin\b|chubby", re.I)
GEN_ADJ = {'thin', 'grey-haired', 'old', 'kind', 'filipino', 'filipina', 'young', 'public', 'school', 'chubby', 'small', 'elderly'}
OTHER_HEAD = re.compile(r"\b(?:woman|women|girl|girls|boy|boys|dog|dogs|man|men|grandmother|grandfather|teacher|child|children|people|"
                        r"crowd|soldiers?|priest|figure|datu|king|queen|friar|schoolgirl|schoolboy|Filipino|Filipina|Usman|Indio)\b")
ING_OK = (r"wearing|matching|ring|earring|string|sling|clothing|lining|stocking|leggings?|evening|morning|building|king|wing|bring|thing|"
          r"nothing|something|sibling|ceiling|padding|stitching|darling|piping|herring|spring|swing|fling|travelling|traveling|riding|running shoes|hooded|fitting")
STOPW = re.compile(r"\b(?!(?:" + ING_OK + r")\b)\w+ing\b|\b(?:who|which|while|as|then|beside|next|alone|together|stands|sits|holds|looks|"
                   r"walks|runs|kneels|reaches|turns|catches|smiles|raises|points|leans|watches|steps|carries|faces|takes|gives|opens|"
                   r"lies|grins|nods|waves|hugs|pulls|pushes|stares|peers|lifts|drops|eats|reads|says|shouts|whispers|jumps|falls|"
                   r"rises|climbs|rides|bows|squats|crouches|sprints|dives|swims|throws|grabs|touches|places|puts|shows|offers|hands|"
                   r"cries|laughs|is|are|has|have|seen|shot|drawn|framed|silhouetted|both|each|one person|only)\b|"
                   r"\b(?:at|in|on|by|under|beside|behind|inside|near|from|into|onto|toward|towards|across|through|against|between|among|"
                   r"amid|before|after|above|below|beneath|outside|along|past|around|over|up|down|to|for)\s+(?:the|this|that|these|those|"
                   r"its|their)\b|\b(?:outside|inside|beside|behind|near|under|beneath|across|along|through|toward|towards|into|onto|amid|"
                   r"among|in front of)\s+(?:a|an)\b", re.I)
NEG_STORY = [('tattoo', re.compile(r'no tattoos?|without (?:any )?tattoos|bare (?:clean )?forearms', re.I)),
             ('medallion', re.compile(r'bare neck|no necklace|no medallion|without (?:the |any |a )?(?:medallion|necklace)', re.I)),
             ('headband', re.compile(r'no headband|without (?:a |the |his )?headband', re.I)),
             ('topknot', re.compile(r'no topknot|short hair|shaved head', re.I))]
EARS_WRONG = re.compile(r"(?:,\s*|\s+)(?:with\s+|his\s+|its\s+)?(?:both\s+)?ears\s+(?:up|flying|pricked|perked|raised|upright)\b"
                        r"|(?:,\s*|\s+)(?:two upright ears|pricked ears|perked ears|floppy ears)\b", re.I)
EARS_BAD_BREED = re.compile(r'floppy-eared|labrador|golden retriever|\bpuppy\b', re.I)

# ------------------------------------------------------------------ what a replacement may drop
# The cast string replaces the article, the head noun and the words right after it that only describe the character
# (hair, skin, clothes, headband, medallion, tattoos, kerchief...). The tail is cut into small phrases (at commas, "and"
# and before prepositions); a phrase is dropped only if EVERY content word in it is a description word that the cast
# string now covers. The first phrase with any other word (place, action, expression, prop: "on a yacht deck",
# "grips his hand", "with eyes closed", "with a low growl") ends the replacement, and it and everything after it stay.
FUNC = set('a an the his her its their of with and in on at around wearing over under'.split())
COMMON_D = set('black white red grey gray blue navy brown dark light beige cream off-white khaki green orange yellow maroon '
               'faded plain simple worn old loose rough cotton linen wool woolen woven homespun abaca collarless short-sleeved '
               'long-sleeved rolled rolled-up patched striped checkered neat'.split())
DROP = {
    'indio': set('hair topknot tied knotted bun tousled messy short long spiky headband band cloth tails tail medallion bronze '
                 'round cord necklace pendant neck indigo geometric tattoo tattoos tattooed forearm forearms arm arms right left '
                 'skin skinned brown-skinned tan tanned lean slim thin wiry young twenty about twenties handkerchief bandana '
                 'wrist clothes outfit dressed sleeves sleeve collar'.split()),
    'usman': set('black philippine street aspin medium medium-sized small slim lean scruffy short-haired fur furred glossy '
                 'shiny white chest patch ear ears folded floppy down upright other one bright clever eyes kerchief bandana '
                 'neckerchief red tied around neck'.split()),
    'm': set('mysterious young filipina long dark black coat holding red umbrella round bronze medallion neck'.split()),
    'gen': set('hair grey grey-haired gray-haired bun glasses round neat short long kind patient wrinkled face thin chubby '
               'elderly old young about ten sixty seventies twenties late filipino filipina cord neck medallion engraved '
               'clothes outfit dressed sleeves'.split()),
}
ACCESS = re.compile(r"helmet|\bhat\b|\bcap\b|sunglasses|goggles|gloves|scarf|\bwatch(?:es)?\b|salakot|\bbag\b|backpack|mask|"
                    r"greave|sword|bolo|spear|shield|kalasag|bow\b|arrows?|lens|phone|umbrella|torch|lantern|book|letter|map", re.I)
HEADW = set('man woman dog boy schoolboy schoolgirl girl filipino filipina indio usman aspin teacher grandfather '
            'grandmother'.split())
EARW = set('ears ear up pricked flying perked raised upright both floppy two'.split())
SPLIT_BEFORE = set('with wearing in on at by around over under beside behind near from into onto toward towards across through '
                   'against between among amid before after above below beneath outside inside along past up down to for '
                   'holding while who which as'.split())
def words(s): return re.findall(r"[a-z0-9][a-z0-9'-]*", s.lower())

def droppable_word(w, char, cw):
    """may this word disappear when the cast string `cw` (its word set) replaces the description of `char`?"""
    c = char if char in DROP else 'gen'
    if w in FUNC or w in cw or w in DROP[c] or w in COMMON_D: return True
    if c in ('indio', 'gen'):
        if re.fullmatch(r"\d{3,4}s?|\d{1,2}(?:st|nd|rd|th)-century", w) or w in NUMW: return True
        if c == 'gen' and CLOTHES_RE.search(w) and not ACCESS.search(w): return True
    return False       # an Indio garment that is not in the cast string stays: the shot may show other clothes (a person decides)

def _phrases(p, i):
    """yield (sep_start, phrase_start, phrase_end, text) from position i; stops at . ; : ! ? ( ) and at the end."""
    while i < len(p):
        sep = re.match(r"\s*,\s*|\s+and\s+|\s+", p[i:])
        j = i + (sep.end() if sep else 0)
        if j >= len(p) or p[j] in '.;:!?()"': return
        toks, k = [], j
        for t in re.finditer(r"[^\s,.;:!?()\"]+", p[j:]):
            if p[k:j + t.start()].strip(): break                                    # punctuation in between
            w = t.group(0).lower()
            if toks and (w == 'and' or w in SPLIT_BEFORE): break
            toks.append(w); k = j + t.end()
        if not toks: return
        yield i, j, k, p[j:k]
        i = k

def desc_tail(p, pos, char, canon):
    """-> (del_end, aside): the description after the head noun that the cast string replaces ends at del_end; an aside in
    brackets right after the head that is not pure description ("(not a bulldog, not muscular)") is kept (its span)."""
    cw = set(words(canon)); i = del_end = pos; aside = None
    m = re.match(r"\s*\(([^()]{1,200})\)", p[pos:])
    if m:
        ws = [w for w in words(m.group(1)) if w not in FUNC]
        if ws and all(droppable_word(w, char, cw) for w in ws): del_end = i = pos + m.end()
        else: aside = (pos + m.start() + len(m.group(0)) - len(m.group(0).lstrip()), pos + m.end()); del_end = i = pos + m.end()
    for s0, a, b, text in _phrases(p, i):
        ws = [w for w in words(text) if w not in FUNC]
        if not ws or any(w in HEADW for w in ws) or not all(droppable_word(w, char, cw) for w in ws): break
        del_end = b
    return del_end, aside

def dropped_words(old, new, chars, canons):
    """content words of `old` that are gone from `new` and are not description words of an edited character."""
    from collections import Counter
    lost = Counter(words(old)) - Counter(words(new))
    cws = [set(words(c)) for c in canons]
    bad = []
    for w in lost:
        if w in HEADW or w in EARW or w in FUNC: continue
        if any(droppable_word(w, ch, cw) for ch in chars for cw in (cws or [set()])): continue
        if any(w in a for a in (INDIO_ADJ, USMAN_ADJ, M_ADJ, GEN_ADJ)): continue
        bad.append(w)
    return bad

# after a cast string: words that show the old description is still there (the string was pasted beside it, not instead)
AFTER_MARK = {'indio': re.compile(r"topknot|headband|tattoo|handkerchief|medallion (?:on a cord|necklace|around his neck|at his neck)", re.I),
              'usman': re.compile(r"chest patch|kerchief|folded ear|ear folded|ears? (?:folded|upright)", re.I),
              'm': re.compile(r"umbrella|long dark coat|medallion at her neck", re.I)}
M_BUSY = re.compile(r"\b(?:holding|holds|carrying|carries|clutching|clutches|cradling|cradles|lifting|lifts|raising|raises|"
                    r"offering|offers|hands? (?:him|her|over))\b", re.I)
M_CLOTHES = re.compile(r"\b(?:coat|cloak|skirt|dress|kimono|robe|gown|blouse|uniform|baro|saya|shawl|veil|hood)\b", re.I)
def region_after(p, at):
    """text after position `at` up to the end of the clause about this character (next . ; or another character)."""
    seg = p[at:at + 220]
    m = re.search(r"[.;]|\b(?:woman|women|man|men|dog|dogs|boy|girl|Usman|Indio|M)\b", seg)
    return seg[:m.start()] if m else seg

PRESENT = re.compile(r'\b(?:present[- ]day|today|modern(?! Japanese| TV| anime)|smartphones?|phones?|laptops?|jeepneys?|motorcycles?|'
                     r'sidecar|cars?|offices?|elevators?|hotel|yacht|billboards?|TV|video call|condo|apartment|parking|senat\w*|campaign|'
                     r'airport|taxi|delivery|fluorescent|tricycles?|mall|vlogger)\b', re.I)
NOTMOD = re.compile(r'nothing modern', re.I)
PAST = re.compile(r'\b(?:1[0-8]\d\d|19[0-4]\d|[2-9]\d\d)s?\b|pre-?colonial|colonial|ancient|galleon|Victorian|Katipunan|medieval|'
                  r'biblical|primeval|\bAD\b|\bBC\b', re.I)
VIEW = re.compile(r'through the (?:brass |golden-rimmed )?lens|hologram|sepia|old[- ]print|photograph|memory|painting|screen|vision', re.I)
JUMP = re.compile(r'time portal|portal|\bjump|lagusan|swirl of golden light|golden light|clock gears|dissolv|fading into|sparks|'
                  r'translucen|ghostly', re.I)
PERSON = re.compile(r"\b(?:woman|women|girls?|boys?|man|men|people|crowd|children|kids|child|grandmother|grandfather|teacher|vendors?|"
                    r"friends?|stranger|pupils|students|soldiers|guards|workers|family|couple|mother|father|baby|toddler|passengers|"
                    r"tourists|customers|someone|figures?|officials?|politicians?|reporters?|nurse|doctor|driver|lola|lolo|"
                    r"applicants?|commuters?|shoppers?|villagers?|sailors?|fishermen|fisherman|merchants?|traders?|monks?|priests?|"
                    r"nuns?|warriors?|crew|audience|spectators?|onlookers?|pedestrians?|residents?|neighbou?rs?|classmates?|players?|"
                    r"guests?|staff|employees?|clerks?|officers?|police(?:men|man)?|guard|waiters?|waitress|cashiers?|vendor|"
                    r"queue|everyone|ladies|lady|gentlemen|gentleman|elders?|youths?|teens?|teenagers?|protesters?|"
                    r"marchers?|rebels?|revolutionaries|troops|army|delegates?|senators?|congressm[ae]n|journalists?|"
                    r"photographers?|cameram[ae]n|staffers?|aides?|bodyguards?|boatm[ae]n|rowers?|farmers?|"
                    r"labou?rers?|porters?|slaves?|captives?|prisoners?|captains?|soldier|datus?|rajahs?|chiefs?|chieftains?|"
                    r"kings?|queens?|princes?|princess|friars?|missionar(?:y|ies)|conquistadors?|spaniards?|"
                    r"natives?|islanders?|tribesm[ae]n|warlords?|"
                    r"strangers?|silhouettes?|someone's|grandparents?|parents?|sisters?|brothers?|sons?|daughters?|"
                    r"wife|husband|kid|girl|boy|persons?)\b", re.I)
CREATURE = re.compile(r"\b(?:serpents?|bakunawa|dragons?|snakes?|fish(?:es)?|birds?|eagles?|hawks?|horses?|carabaos?|crocodiles?|"
                      r"monkeys?|kappa|foxe?s?|tikbalang|creatures?|monsters?|whales?|sharks?|turtles?|siyokoy|cats?|kittens?|"
                      r"chickens?|roosters?|hens?|goats?|pigs?|deer|butterfl(?:y|ies)|bees?|insects?|fireflies|firefly|crabs?|"
                      r"octopus|squid|dolphins?|bats?|owls?|crows?|ravens?|parrots?|lizards?|geckos?|frogs?|cattle|cows?|"
                      r"oxen|buffalo|tigers?|lions?|elephants?|bears?|wolves|wolf|sheep|camels?|mules?|donkeys?|animals?|"
                      r"beasts?|giants?|spirits? of|naga|garuda|manaul|sarimanok|aswang|kapre|duwende|engkanto|diwata)\b", re.I)
CREATURE_NEG = re.compile(r"\b(?:no|nobody|no other|without|empty of|not a|not an)\s+(?:[\w-]+\s+){0,2}?(?:[\w-]+)\b", re.I)
def has_creature(p):
    """an animal or creature the shot shows (not negated): "no animals" would contradict it, so the clause is "no dog"."""
    t = NODOG_RX.sub(lambda x: ' ' * len(x.group(0)), p)
    t = CREATURE_NEG.sub(lambda x: ' ' * len(x.group(0)), t)
    return bool(CREATURE.search(t))
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
    m = re.match(r"\s*\(([^()]{3,200})\)", p[pos:])               # "a lean young Filipino man (black topknot, red headband, ...)"
    if m and vocab.search(m.group(1)) and not OTHER_HEAD.search(m.group(1)):
        end = i = pos + m.end(); first = False
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
                if free(st, e): taken.append((st, e)); out.append(Mention(char=name, start=st, end=e, art=art, kept=kept, vstart=vs, head=m.group(0), hend=m.end()))
    # Indio
    for m in re.finditer(r"\bFilipino (?:man|schoolboy|boy)\b|\byoung man\b|\bIndio\b", p):
        if p[m.end():m.end() + 2] == "'s" or not free(m.start(), m.end()): continue
        if m.group(0) == 'Indio':
            taken.append((m.start(), m.end())); out.append(Mention(char='indio', start=m.start(), end=m.end(), art='', kept=[], vstart=m.start(), head='Indio', hend=m.end(), bare=True)); continue
        hs = m.start() + (0 if m.group(0) == 'young man' else 0)
        st, art, kept, vs = _walk_back(p, hs, INDIO_ADJ)
        e = _consume(p, m.end(), INDIO_V)
        span = p[st:e]
        if not INDIO_MARK.search(span):
            if art.lower() == 'the' and any(x.char == 'indio' for x in out): continue      # "the young man": back-reference
            if re.search(r'\bold\b|grandfather|sixties|seventies|fifties|heavyset|teenage', span, re.I): continue
            taken.append((st, e)); out.append(Mention(char='indio', start=st, end=e, art=art, kept=kept, vstart=vs, head=m.group(0), hend=m.end(), weak=True,
                                                      unsure='no Indio marker (topknot, headband, handkerchief, medallion, tattoo): another man, or Indio with every constant missing'))
            continue
        taken.append((st, e)); out.append(Mention(char='indio', start=st, end=e, art=art, kept=kept, vstart=vs, head=m.group(0), hend=m.end()))
    # Usman (negated "no dog" is not a mention)
    t0 = re.sub(r"\b(?:[Nn]o|NO|not a|without (?:a |the |any )?|[Oo]nly one|ONE|[Ee]xactly one|One|[Ee]xactly ONE|other) (?:[\w-]+ )?(?:dogs?|animals?)\b",
                lambda x: '#' * len(x.group(0)), p)
    for m in re.finditer(r"\bdog\b|\baspin\b|\bUsman\b", t0):
        if p[m.end():m.end() + 2] == "'s" or re.match(r"-(?:like|shaped)", p[m.end():]) or not free(m.start(), m.end()): continue
        if m.group(0) == 'Usman':
            if re.match(r",\s*(?:a|the)\s+(?:[\w-]+\s+){0,5}dog\b", p[m.end():]): continue      # "Usman, a black ... dog" (the dog phrase is the mention)
            taken.append((m.start(), m.end())); out.append(Mention(char='usman', start=m.start(), end=m.end(), art='', kept=[], vstart=m.start(), head='Usman', hend=m.end(), bare=True)); continue
        st, art, kept, vs = _walk_back(p, m.start(), USMAN_ADJ)
        e = _consume(p, m.end(), USMAN_V)
        span = p[st:e]
        if re.search(r'collar|bears and a dog', span, re.I) and not USMAN_MARK.search(span): continue
        if re.match(r'\s*(?:drawn|sketched|outlined) as|-like|-shaped', p[e:]) and not USMAN_MARK.search(span): continue
        if not USMAN_MARK.search(span):
            if any(x.char == 'usman' for x in out): continue                       # "the dog": back-reference to a described Usman
            if ep == 4: continue                                                   # Pepe's dog (1869) is not Usman
            taken.append((st, e)); out.append(Mention(char='usman', start=st, end=e, art=art, kept=kept, vstart=vs, head=m.group(0), hend=m.end(), unsure='a dog with no Usman marker (black, street, patch, kerchief): Usman or another dog?'))
            continue
        taken.append((st, e)); out.append(Mention(char='usman', start=st, end=e, art=art, kept=kept, vstart=vs, head=m.group(0), hend=m.end()))
    # M
    for m in re.finditer(r"\bwoman\b", p):
        if p[m.end():m.end() + 2] == "'s" or not free(m.start(), m.end()): continue
        st, art, kept, vs = _walk_back(p, m.start(), M_ADJ)
        e = _consume(p, m.end(), M_V)
        span = p[st:e]
        if not M_MARK.search(span) or re.search(r'snow-white|white hair|grandmother|white dress|in white|fox|\bold\b', span, re.I): continue
        taken.append((st, e)); out.append(Mention(char='m', start=st, end=e, art=art, kept=kept, vstart=vs, head='woman', hend=m.end()))
    if any(x.char in ('usman', 'm') and not x.unsure for x in out):     # beside Usman or M a plain "young man" is Indio
        for x in out:
            if x.weak: x['unsure'] = None
    out = [x for x in out if not (x.weak and x.unsure and x.head == 'young man' and not key.lower().startswith('indio'))]
    out = sorted(out, key=lambda x: x.start)
    # one character, several mentions in one prompt: the first described one carries the cast string. A later bare name
    # ("Indio pointing") or "the ..." is a back-reference (ref: left as written); a dog without a marker beside a marked
    # Usman is a label ("a real dog: a medium-sized black ...") or a reference; a second "a ..." description is either
    # the same character twice or someone else (second: a person decides unless it already is the cast string).
    for ch in ('indio', 'usman', 'm'):
        ms = [x for x in out if x.char == ch]
        desc = [x for x in ms if not x.bare and not x.unsure]
        if ch == 'usman' and desc:
            out = [x for x in out if not (x.char == 'usman' and x.unsure)]; ms = [x for x in ms if not x.unsure]
        prim = desc[0] if desc else (ms[0] if ms else None)
        for x in ms:
            if x is prim or x.unsure: continue
            if x.bare or (x.art or '').lower() == 'the': x['ref'] = True
            else: x['second'] = True
    return out

def extend(p, mm, canon, vocab=None):
    """after the canonical string is known: take further segments that are part of it (", in a white school uniform
    shirt"), also across up to two other character segments ("small and thin") when a canonical segment follows."""
    if mm.bare: return mm.end
    vocab = vocab or {'indio': INDIO_V, 'usman': USMAN_V, 'm': M_V}.get(mm.char, GEN_V)
    cl = canon.lower(); end = i = mm.end; skipped = 0
    while True:
        words = list(re.finditer(r"[ ,]+[^ ,]+", p[i:i + 200]))       # words that continue the canonical text ("holding a red umbrella")
        k = 0
        for j, w in enumerate(words):
            if p[i:i + w.end()].lower() in cl: k = j + 1
            else: break
        if k >= 2 and not skipped:
            end = i = i + words[k - 1].end(); continue
        c = re.match(r",\s*|\s+and\s+|\s+in\s+|\s+with\s+", p[i:])
        if not c: break
        s0 = i + c.end()
        b = re.search(r",|\s+and\s+|[.;:!?()]|$", p[s0:]); seg = p[s0:s0 + b.start()]
        cut = STOPW.search(seg)
        if cut: seg = seg[:cut.start()]
        seg = seg.rstrip()
        if not seg or OTHER_HEAD.search(seg): break
        core = re.sub(r'^(?:a|an)\s+', '', re.sub(r'^(?:wearing|in|with)\s+', '', seg.lower()))
        if core and len(core) > 3 and core in cl or (not skipped and vocab.search(seg)):
            end = i = s0 + len(seg); skipped = 0
            if cut: break
            continue
        if cut or skipped >= 3 or not re.search(r'\b(?:skin|small|thin|slim|lean|tall|eyes|face|build)\b', seg): break
        skipped += 1; i = s0 + len(seg)
    return end

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
        # one jump = one outfit described in several ways: merge clothes that share a garment ("labourer jacket over a shirt" /
        # "work jacket, loose trousers, straw sandals"); different garments (a cloak vs a camisa) stay apart
        GEN = {'shirt', 'sleeves', 'collar', 'clothes', 'outfit', 'dressed', 'barefoot'}
        merged = []                                           # [set of noun keys, Counter]
        for nk, cnt in self.groups.items():
            hit = [g for g in merged if any((set(k) & set(nk)) - GEN for k in g[0])]
            if hit:
                g = hit[0]
                for o in hit[1:]: g[0] |= o[0]; g[1].update(o[1]); merged.remove(o)
                g[0].add(nk); g[1].update(cnt)
            else: merged.append([{nk}, collections.Counter(cnt)])
        self.alias = {}
        n = 0
        for keys, cnt in merged:
            nk = frozenset().union(*keys)
            for k in keys: self.alias[k] = nk
            phrase = sorted(cnt.items(), key=lambda x: (-x[1], -len(x[0])))[0][0]
            match = None
            for k, s in saved.items():
                if noun_key(outfit_clothes(s) or '') in keys: match = (k, s); break
            if match and self._valid(match[1]): self.era[nk] = ('indio_outfits.' + match[0], match[1], True); continue
            if match: phrase = outfit_clothes(match[1]) or phrase          # keep the saved wording of the clothes
            built = build_outfit(C, phrase, ep)
            same = [k for k, s in saved.items() if s == built]
            if same: self.era[nk] = ('indio_outfits.' + same[0], built, True); continue
            n += 1; name = f'ep{ep:02d}' + ('' if n == 1 else f'_{n}')
            self.era[nk] = ('indio_outfits.' + name, built, False)
        for k, nk in self.alias.items(): self.era.setdefault(k, self.era[nk])

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
        if cl:
            for k, v in self.era.items():
                if (set(k) & set(noun_key(cl))) - {'shirt', 'sleeves', 'collar'}: return v[0], v[1], None
        outs = self.outfits()
        if not cl or True:
            if len(outs) == 1: n, s, _ = outs[0]; return n, s, None
            if not outs: return None, None, 'past-era Indio with no clothes named anywhere in this episode: write the outfit once'
            return None, None, 'past-era Indio with %s and the episode has %d era outfits' % ('no clothes named' if not cl else 'clothes "%s"' % cl, len(outs))
        return None, None, 'era clothes not grouped'

    def _s5(self, low):
        if re.search(r'armou?r|anting', low): return 'indio_s5_anting', self.C['str']['indio_s5_anting'], None
        cl = [c for c in CLOTHES_RE.findall(low) if c not in ('coat',)]
        if cl and not re.search(r'long dark grey coat', low):
            return None, None, 'Season 5 Indio in an outfit the cast does not have (%s)' % ', '.join(sorted(set(cl)))
        return 'indio_s5', self.C['str']['indio_s5'], None

    def outfits(self):
        return list(dict.fromkeys(self.era.values()))

    def unsaved(self):
        return [(n, s) for n, s, saved in self.outfits() if not saved]

# ------------------------------------------------------------------ classification
INDIO_CONST = [('topknot', r'topknot'), ('headband', r'headband'), ('medallion', r'medallion'), ('tattoos', r'tattoo'),
               ('wrist handkerchief', r'handkerchief')]
USMAN_CONST = [('white chest patch', r'chest patch'), ('one folded ear', r'folded ear|ear folded'), ('red kerchief', r'kerchief')]
M_CONST = [('long dark coat', r'long dark coat'), ('red umbrella', r'red umbrella'), ('medallion', r'medallion')]

NECK_RX = re.compile(r'bare neck|no necklace|no medallion|without (?:the |any |a |his )?(?:medallion|necklace)', re.I)
M_ERA = re.compile(r"\b(?:skirt|dress|kimono|robe|gown|blouse|uniform|baro|saya|shawl|veil|hood|cloak|\d{3,4}s)\b", re.I)

def classify(mm, p, canon_name, canon, ep, era, ecanon=None):
    """-> (cls, detail). cls: EXACT NEAR MISSING WRONG STORY DOUBLE"""
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
    if (mm.char == 'indio' and not exact and ecanon is not None and getattr(ecanon, 'neck_story', None) and 'medallion' in canon
            and 'headband' in canon):
        return 'STORY', (f'this episode draws Indio with a bare neck elsewhere ({ecanon.neck_story}); {canon_name} has the medallion: '
                         'medallion or not is a story decision (cast_fix --wear-medallion once a person has decided)')
    if mm.char == 'm' and not exact:
        reg = p[mm.hend:mm.hend + 200]; reg = reg[:re.search(r'[.;]|$', reg).start()]
        outside = p[:mm.start] + p[mm.end:]
        busy = M_BUSY.search(reg)
        if busy and 'umbrella' not in reg[busy.end():busy.end() + 30].lower():
            return 'STORY', f'M\'s cast string holds a red umbrella; in this shot she is "{reg[busy.start():busy.end() + 25].strip()}": a person decides'
        if re.search(r'umbrella', outside, re.I) and 'umbrella' not in low:
            return 'STORY', "the shot describes M's umbrella separately; the cast string adds a second one: a person merges them"
        me = M_ERA.search(reg)
        if me: return 'STORY', f'M in clothes the cast string does not have ("{me.group(0)}"; the string has only the long dark coat): a person decides'
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
    if exact and not wrong:
        mk = AFTER_MARK.get(mm.char)
        reg = region_after(p, mm.vstart + len(b))
        if mk and mk.search(reg):
            return 'DOUBLE', f'{canon_name} is there, but the old description follows it ("{reg.strip()[:90]}"): the engine gets the character twice; a person merges them'
        return 'EXACT', canon_name
    miss = [n for n, rx in consts if re.search(rx, canon) and not re.search(rx, low)]
    if wrong: return 'WRONG', '; '.join(wrong + (['missing ' + ', '.join(miss)] if miss else []))
    if mm.bare: return 'MISSING', f'name only ("{sp}"): the image engine gets no description'
    if miss: return 'MISSING', 'missing ' + ', '.join(miss) + f' (vs {canon_name})'
    cw = [w for w in dict.fromkeys(re.findall(r"[\w'-]+", b.lower())) if w not in low and w not in ('a', 'an', 'the', 'of', 'on', 'his', 'her', 'with', 'in', 'and', 'tied', 'around', 'wearing', 'about')]
    return 'NEAR', f'other words than {canon_name}' + (' (lacks: ' + ' '.join(cw[:10]) + ')' if cw else '')

def other_people(p, mentions, indio_spans):
    if any(x.char not in ('indio', 'usman') for x in mentions): return True
    if sum(1 for x in mentions if x.char == 'indio' and not x.ref) > 1: return True
    t = p
    for a, b in sorted(indio_spans, reverse=True): t = t[:a] + ' ' * (b - a) + t[b:]
    t = PERSON_NEG.sub(lambda x: ' ' * len(x.group(0)), t)
    t = re.sub(r"\b(?:man|woman|boy|girl)'s\b", '', t)
    return bool(PERSON.search(t))

NODOG_ONLY = 'no dog'          # a shot with another animal or creature (the bakunawa, fish, the kappa): "no animals" would erase it
def clause_need(p, ep, mentions, era, resolved, outfit_means_present=True):
    """modern-day prompt without Usman: which clause it needs, or None."""
    if ep > NODOG_UNTIL or any(x.char == 'usman' for x in mentions): return None
    modern = era == 'present' or outfit_means_present and any(x.char == 'indio' and r and 'headband' not in r[1] and r[0] != 'indio_child_2012' for x, r in zip(mentions, resolved))
    if era == 'past' or not modern or JUMP.search(p): return None
    if has_creature(p): return NODOG_ONLY
    has_indio = any(x.char == 'indio' for x in mentions)
    return ALONE if has_indio and not other_people(p, mentions, [(x.start, x.end) for x in mentions if x.char == 'indio']) else NODOG

NODOG_RX = re.compile(r"\b(?:he is alone,\s*)?no dogs?\b(?:,?\s*(?:and\s+)?no (?:other )?animals?\b)?", re.I)
NOANIMALS_RX = re.compile(r",?\s*(?:and\s+)?\bno (?:other )?animals?\b", re.I)
def clause_state(p, need):
    if need is None: return 'OK', ''
    if need == NODOG_ONLY:
        if NOANIMALS_RX.search(p): return 'NEAR', 'says "no animals" but the shot shows an animal or creature: the clause must be only "no dog"'
        return ('OK', '') if re.search(r'\bno dogs?\b', p, re.I) else ('MISSING', 'modern-day prompt without "no dog"')
    if need.lower() in p.lower(): return 'OK', ''
    if need == NODOG and ALONE in p.lower(): return 'OK', ''
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

# ------------------------------------------------------------------ nv_replace and the medallion
def nv_status(K, items):
    """character entries of nv_replace -> {key: ('dead' | 'plain' | 'story', why)}. dead: no prompt contains the key (copied
    boilerplate; removing it changes no picture, and it would start rewriting cast strings cast_fix puts in). plain: a
    short form of the cast string (removed, so the engine gets the cast string). story: the short form drops the medallion
    ("bare neck") or changes M's medallion: a person decides; kept."""
    raw = [assemble(K, kind, p, {}) for kind, key, p in items]
    out = {}
    for k in char_nv_entries(K):
        v = K['nv_replace'][k]
        if not any(k in r for r in raw): out[k] = ('dead', 'no prompt contains it'); continue
        if (NECK_RX.search(v) and not NECK_RX.search(k)) or 'crescent' in v or ('Filipina woman' in k and 'medallion' in k and 'medallion' not in v):
            out[k] = ('story', 'the short form drops or changes the medallion'); continue
        out[k] = ('plain', 'short form of a cast string')
    return out

def neck_story(C, K, items):
    """does this episode draw Indio with a bare neck on purpose somewhere (M took the medallion in ep06)? -> where, or None.
    Looks at the prompts and at nv_replace (live or copied), not at cast strings that themselves say "bare neck"."""
    own = [s for s in C['str'].values() if NECK_RX.search(s)]
    def clean(t):
        for s in own: t = t.replace(body(s), '')
        return t
    for kind, key, p in items:
        if re.search(r'\b(?:man|Indio|topknot|headband)\b', p) and NECK_RX.search(clean(p)): return f'{kind}/{key} says "{NECK_RX.search(clean(p)).group(0)}"'
    for k, v in K.get('nv_replace', {}).items():
        if NECK_RX.search(clean(k)) or (NECK_RX.search(clean(v)) and CHAR_NV.search(k)): return 'nv_replace has a "bare neck" short form'
    return None

def setup_canon(C, K, ep, wear_medallion=False):
    items = [(k, n, p) for k, n, p in prompts(K) if not p.startswith('(copied')]
    canon = EpisodeCanon(C, ep, items)
    canon.omp = outfit_means_present(canon, items, ep)
    canon.neck_story = None if wear_medallion else neck_story(C, K, items)
    return items, canon

def analyse(p, ep, key, canon):
    """one prompt -> (era, mentions, records, need). Each record: cls, detail, name, string (cast_lint and cast_fix share it)."""
    era = scene_era(p); ms = find_mentions(p, ep, key); recs, resolved = [], []
    for mm in ms:
        if mm.unsure:
            recs.append(dict(mm=mm, cls='UNSURE', detail=mm.unsure)); resolved.append(None); continue
        if mm.ref:
            w = EARS_WRONG.search(p, mm.start, min(len(p), mm.end + 80))
            recs.append(dict(mm=mm, cls='WRONG' if w and mm.char == 'usman' else 'REF',
                             detail=(f'"{w.group(0).strip(", ")}" contradicts one folded ear' if w and mm.char == 'usman' else 'refers back to the character described earlier in the prompt')))
            resolved.append(None); continue
        name, s, why = canon.pick(mm, p, era)
        if not name:
            recs.append(dict(mm=mm, cls='NOCANON', detail=why)); resolved.append(None); continue
        mm['end'] = extend(p, mm, s)
        cls, det = classify(mm, p, name, s, canon.ep, era, canon)
        if mm.second and cls not in ('EXACT', 'STORY', 'DOUBLE'):
            cls, det = 'SECOND', f'a second description of {mm.char} in one prompt ({det}): the same character twice, or someone else? a person decides'
        recs.append(dict(mm=mm, cls=cls, detail=det, name=name, string=s)); resolved.append((name, s))
    need = clause_need(p, ep, ms, era, resolved, canon.omp)
    return era, ms, recs, need

# ------------------------------------------------------------------ episode lint
def lint_episode(epdir, C, K=None, wear_medallion=False):
    slug = os.path.basename(epdir.rstrip('/')); ep = ep_num(slug)
    K = K if K is not None else json.load(open(os.path.join(epdir, 'key_prompts.json')))
    items, canon = setup_canon(C, K, ep, wear_medallion)
    res = {'slug': slug, 'episode': ep, 'episode_issues': [], 'prompts': []}
    nvs = nv_status(K, items)
    rm = [k for k, (st, _) in nvs.items() if st != 'story']
    if rm:
        dead = sum(1 for k in rm if nvs[k][0] == 'dead')
        res['episode_issues'].append({'type': 'NV_REPLACE', 'msg': f'nv_replace has {len(rm)} entr{"y" if len(rm) == 1 else "ies"} that rewrite cast strings after the prompt is built ({dead} used by no prompt)', 'entries': rm})
    st_ = [k for k, (st, _) in nvs.items() if st == 'story']
    if st_:
        res['episode_issues'].append({'type': 'NV_STORY', 'msg': f'nv_replace sends {len(st_)} cast string(s) as a short form without the medallion ("bare neck") or with another medallion: a story decision, a person decides', 'entries': st_})
    if canon.neck_story:
        res['episode_issues'].append({'type': 'INFO', 'msg': f'medallion: {canon.neck_story}; era-Indio mentions that lack the medallion are left as STORY'})
    for n, s in canon.unsaved():
        res['episode_issues'].append({'type': 'UNSAVED_OUTFIT', 'msg': f'era outfit built from indio_era_template is not saved in series_cast.json as {n} (cast_fix --save-outfit)', 'name': n, 'string': s})
    for n, p in K.get('plates', {}).items():
        if not isinstance(p, str): continue
        t = PLATE_NEG.sub(lambda x: ' ' * len(x.group(0)), p)
        m = PLATE_CHAR.search(t)
        if m: res['prompts'].append({'kind': 'plates', 'key': n, 'era': scene_era(p), 'sent_len': len(assemble(K, 'plates', p)), 'mentions': [],
                                     'issues': [{'type': 'PLATE_PERSON', 'msg': f'plate (background) mentions "{m.group(0)}": plates must have no characters; a person decides'}]})
    if not canon.omp: res['episode_issues'].append({'type': 'INFO', 'msg': 'the present-day outfit also appears beside Usman outside a jump (e.g. Episode 10 in 2012): only scene words decide the no-dog clause here'})
    for kind, key, p in items:
        era, ms, recs, need = analyse(p, ep, key, canon)
        out = []
        for r in recs:
            mm = r['mm']
            out.append({'char': mm.char, 'cls': r['cls'], 'detail': r['detail'], 'canon': r.get('name'), 'span': p[mm.start:mm.end], 'start': mm.start, 'end': mm.end})
        issues = []
        st, msg = clause_state(p, need)
        if st != 'OK': issues.append({'type': 'NO_DOG_' + st, 'msg': msg, 'need': need})
        L = len(assemble(K, kind, p))
        if L > LIMIT: issues.append({'type': 'LENGTH', 'msg': f'{L} characters sent > {LIMIT}: make_keys cuts the end off', 'len': L})
        res['prompts'].append({'kind': kind, 'key': key, 'era': era, 'sent_len': L, 'mentions': out, 'issues': issues})
    return res

OKCLS = ('EXACT', 'REF')
def count(res):
    c = collections.Counter()
    for e in res:
        for i in e['episode_issues']:
            if i['type'] != 'INFO': c[i['type']] += 1
        for p in e['prompts']:
            for m in p['mentions']: c[m['cls']] += 1
            for i in p['issues']: c[i['type']] += 1
    return c

PERSON_DECIDES = ('NOCANON', 'UNSURE', 'STORY', 'DOUBLE', 'SECOND', 'PLATE_PERSON', 'NV_STORY', 'ERROR')
def found(res):
    c = count(res); return sum(v for k, v in c.items() if k not in OKCLS)

def text_report(res, C, verbose=False):
    L = []
    L.append('cast file notes (contradictions inside characters/series_cast.json; not counted per prompt):')
    L += ['  - ' + n for n in C['notes']]
    for e in res:
        bad = [p for p in e['prompts'] if p['issues'] or any(m['cls'] not in OKCLS for m in p['mentions'])]
        L.append('')
        L.append(f"== {e['slug']} (episode {e['episode']}): {len(bad)} of {len(e['prompts'])} prompts need attention")
        for i in e['episode_issues']:
            L.append(f"  [episode] {i['type']}: {i['msg']}")
            if i['type'] == 'UNSAVED_OUTFIT': L.append(f"            \"{i['string']}\"")
        for p in e['prompts']:
            ms = p['mentions'] if verbose else [m for m in p['mentions'] if m['cls'] not in OKCLS]
            if not ms and not p['issues']: continue
            L.append(f"  {p['kind']}/{p['key']}  [{p['era']}, {p['sent_len']} chars sent]")
            for m in ms:
                L.append(f"    {m['cls']:8} {m['char']:14} {m['detail']}")
                if m['cls'] not in OKCLS: L.append(f"             as written: \"{m['span'][:160]}\"")
            for i in p['issues']: L.append(f"    {i['type']:8} {i['msg']}")
    c = count(res)
    L.append('')
    L.append('TOTAL: ' + ', '.join(f'{k} {v}' for k, v in sorted(c.items())) + ('  -> clean' if not found(res) else '  -> exit 1'))
    L.append('NEAR/MISSING/WRONG/NO_DOG/NV_REPLACE/UNSAVED_OUTFIT: cast_fix.py repairs them. ' + '/'.join(PERSON_DECIDES) + '/LENGTH it cannot: a person decides.')
    return '\n'.join(L)

class UsageError(Exception): pass

def episode_dirs(args):
    if args:
        out = []
        for a in args:
            d = a if os.path.isdir(a) else os.path.join(ROOT, a)
            if not os.path.isfile(os.path.join(d, 'key_prompts.json')): raise UsageError(f'{a}: no key_prompts.json there')
            out.append(d)
        return out
    return sorted(d for d in glob.glob(os.path.join(ROOT, 'videos', 'ep*')) if os.path.exists(os.path.join(d, 'key_prompts.json')))

USAGE = 'usage: cast_lint.py [videos/<slug> ...] [--json] [-v] [--wear-medallion] [--cast characters/series_cast.json]'
def main(argv):
    """exit 0 = clean, 1 = something found, 2 = the lint could not run (bad arguments, broken cast file, unreadable episode)."""
    try:
        a = list(argv); js = '--json' in a; verbose = '-v' in a; wm = '--wear-medallion' in a
        cast = None
        if '--cast' in a:
            i = a.index('--cast')
            if i + 1 >= len(a) or a[i + 1].startswith('-'): raise UsageError('--cast needs a path')
            cast = a[i + 1]; del a[i:i + 2]
        bad = [x for x in a if x.startswith('-') and x not in ('--json', '-v', '--wear-medallion')]
        if bad: raise UsageError('unknown option ' + ' '.join(bad))
        eps = [x for x in a if not x.startswith('-')]
        C = load_cast(cast)
        dirs = episode_dirs(eps)
    except (UsageError, CastError) as e:
        print(f'cast_lint: {e}\n{USAGE}', file=sys.stderr); return 2
    res, errors = [], 0
    for d in dirs:
        try: res.append(lint_episode(d, C, wear_medallion=wm))
        except Exception as e:                                  # one half-written file must not stop the other 49
            errors += 1
            res.append({'slug': os.path.basename(d.rstrip('/')), 'episode': ep_num(d), 'prompts': [],
                        'episode_issues': [{'type': 'ERROR', 'msg': f'could not lint: {type(e).__name__}: {e}'}]})
    if js:
        json.dump({'cast_notes': C['notes'], 'totals': count(res), 'errors': errors, 'episodes': res}, sys.stdout, ensure_ascii=False, indent=1); print()
    else:
        print(text_report(res, C, verbose))
    if errors: print(f'cast_lint: {errors} episode(s) could not be read (see ERROR above)', file=sys.stderr); return 2
    return 1 if found(res) else 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
