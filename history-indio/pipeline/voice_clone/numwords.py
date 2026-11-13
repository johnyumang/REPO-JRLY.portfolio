"""Numbers in a script line and in what the recogniser heard, as integers, so "mil nuwebe syentos sais", "1906" and
"nineteen oh six" compare equal and 1906 vs 1909 is a wrong word. No dependencies; `python3 numwords.py` runs the tests.
Reads: digits (1,906 / 72% / Genesis 3:24 -> 3, 24); Tagalog (isa ... siyam, sampu, labing-, -pu, "labing-anim na raan at
siyam" = 1609, "dalawampung milyon"); Spanish-derived Tagalog (uno ... nuwebe, onse ... disinuwebe, bente ... nobenta,
-syentos, "mil seis siyentos nuwebe" = 1609, milyones); English (one ... ninety, hundred, thousand, million, year pairs
"eighteen ninety-six" = 1896, "nineteen oh-six" = 1906); the linkers -ng / -'t / -'y / na / at / y; clock words
("alas-sais" = "alasais" = alas 6). A heard split that a listener hears as one number ("1900, 60" = nineteen hundred sixty
= 1960; "600 at 89" = 689) is read as that one number.
  numbers(text) -> [int, ...] in order;  strip(text) -> text with every number removed (for the letter comparison);
  starts_with_number(text) -> bool;  diff(want, heard) -> [(expected or None, heard or None), ...] for each mismatch."""
import re, difflib

UNIT = {}
for v, ws in {1: ('isa', 'uno', 'one'), 2: ('dalawa', 'dos', 'two'), 3: ('tatlo', 'tres', 'three'), 4: ('apat', 'kuwatro', 'kwatro', 'kuatro', 'cuatro', 'four'),
              5: ('lima', 'singko', 'sinko', 'cinco', 'five'), 6: ('anim', 'sais', 'seis', 'six'), 7: ('pito', 'siyete', 'syete', 'siete', 'seven'),
              8: ('walo', 'otso', 'ocho', 'eight'), 9: ('siyam', 'nuwebe', 'nueve', 'nwebe', 'nine'),
              10: ('sampu', 'diyes', 'dyes', 'dies', 'ten'), 11: ('onse', 'eleven', 'labingisa'), 12: ('dose', 'doce', 'twelve', 'labindalawa'),
              13: ('trese', 'trece', 'thirteen', 'labintatlo'), 14: ('katorse', 'catorce', 'fourteen', 'labingapat'), 15: ('kinse', 'quince', 'fifteen', 'labinlima'),
              16: ('disisais', 'diesiseis', 'sixteen', 'labinganim'), 17: ('disisiyete', 'disisyete', 'diesisiete', 'seventeen', 'labimpito', 'labinpito'),
              18: ('disiotso', 'diesiocho', 'eighteen', 'labingwalo'), 19: ('disinuwebe', 'diesinueve', 'nineteen', 'labinsiyam'), 0: ('zero', 'sero')}.items():
    for w in ws: UNIT[w] = v
TENS = {}
for v, ws in {20: ('bente', 'beinte', 'veinte', 'twenty', 'dalawampu'), 30: ('trenta', 'treinta', 'treynta', 'thirty', 'tatlumpu'),
              40: ('kuwarenta', 'kwarenta', 'cuarenta', 'forty', 'apatnapu'), 50: ('singkuwenta', 'singkwenta', 'sinkuwenta', 'sinkwenta', 'cincuenta', 'fifty', 'limampu'),
              60: ('sesenta', 'sisenta', 'sixty', 'animnapu'), 70: ('setenta', 'sitenta', 'seventy', 'pitumpu'), 80: ('otsenta', 'ochenta', 'eighty', 'walumpu'),
              90: ('nobenta', 'nubenta', 'noventa', 'ninety', 'siyamnapu')}.items():
    for w in ws: TENS[w] = v
HUND = {}
for v, ws in {100: ('siyento', 'syento', 'siento', 'ciento'), 200: ('dosyentos', 'dosientos', 'doscientos'), 300: ('tresyentos', 'tresientos', 'trescientos'),
              400: ('kuwatrosyentos', 'kwatrosyentos', 'cuatrocientos'), 500: ('kinyentos', 'quinientos'),
              600: ('saisyentos', 'seisyentos', 'sesyentos', 'sisyentos', 'seiscientos'), 700: ('siyetesyentos', 'syetesyentos', 'setesyentos', 'setecientos'),
              800: ('otsosyentos', 'otsosientos', 'ochocientos'), 900: ('nobesyentos', 'nobesientos', 'novecientos', 'nobyentos', 'nuwebesyentos')}.items():
    for w in ws: HUND[w] = v
HUND.update({'isandaan': 100, 'sandaan': 100, 'isanlibo': 1000, 'sanlibo': 1000})                  # one-word "one hundred" / "one thousand"
for w in list(HUND):                                                                      # script spelling "kuwatrosiyentos", "nobesiyentos"
    if 'syentos' in w: HUND[w.replace('syentos', 'siyentos')] = HUND[w]
MULT = {**{w: 'x100' for w in ('syentos', 'siyentos', 'sientos', 'cientos', 'hundred', 'daan', 'raan')},   # after a number: x 100
        **{w: 'x1000' for w in ('mil', 'thousand', 'libo')}, **{w: 'x1M' for w in ('milyon', 'milyones', 'million')}}
NEED_BEFORE = {'daan', 'raan', 'libo', 'hundred', 'syentos', 'siyentos', 'sientos', 'cientos'}   # ordinary words ("daan" = road) unless a number comes first
LINK = {'na', 'at', 'y', 'and', ','}

def _val(w):
    """-> (kind, value) for a number word, its linker forms included ("limang", "dalawamput", "trentay"), else None."""
    if not w or not w.isalpha(): return None
    for x in (w, w[:-2] if w.endswith('ng') else None, w[:-1] if w[-1:] in 'gty' else None):
        if not x: continue
        if x.endswith('po') and x[:-1] + 'u' in TENS: x = x[:-1] + 'u'                  # "siyamnapo" heard for siyamnapu
        if x in UNIT: return 'u', UNIT[x]
        if x in TENS: return 't', TENS[x]
        if x in HUND: return 'h', HUND[x]
        if x in MULT: return MULT[x], None
        if x in ('labing', 'labin', 'labim'): return 'u', 10
    return None

def _words(t):
    t = t.lower().replace('ñ', 'n')
    for a, b in (('á', 'a'), ('é', 'e'), ('í', 'i'), ('ó', 'o'), ('ú', 'u')): t = t.replace(a, b)
    t = re.sub(r'(?<=\d)[,.](?=\d{3}\b)', '', t)                                       # 1,906 -> 1906
    t = t.replace('%', ' porsyento ').replace('-', ' ').replace('’', '').replace("'", '')
    t = re.sub(r'\b(apat|anim|siyam)\s+na\s*p([uo])', r'\1nap\2', t)                  # recogniser splits: "siyam napot" -> siyamnapot
    t = re.sub(r'\b(dalawa|tatlu|tatlo|lima|pitu|pito|walu|walo)m?\s+m?p([uo])', lambda m: {'tatlo': 'tatlu', 'pito': 'pitu', 'walo': 'walu'}.get(m[1], m[1]) + 'mp' + m[2], t)
    out = []
    for w in re.findall(r'\d+|[a-z]+|[^\sa-z\d]', t):                                  # punctuation kept as its own token: it ends a number
        if w.startswith('alas') and len(w) > 4:                                        # clock: "alasais" = alas + sais, "alassiyete"
            r = w[4:]; r = r if _val(r) else 's' + r if _val('s' + r) else None
            if r: out += ['alas', r]; continue
        out.append(w)
    return out

def _kind(w):
    if w.isdigit(): return 'd', int(w)
    return _val(w)

def _scan(t):
    """-> (list of (start_token, end_token, value) for each number, tokens)."""
    tok = _words(t); out = []; i = 0
    while i < len(tok):
        k0 = _kind(tok[i])
        if not k0 or k0[0] in ('x100',) or tok[i] in NEED_BEFORE or (k0[0] == 'x1000' and tok[i] != 'mil'):
            i += 1; continue
        total, cur, last, lastd, j = 0, 0, None, None, i
        while j < len(tok):
            w = tok[j]
            if w in LINK and last:                                                     # a linker continues only into a fitting number
                nk = _kind(tok[j + 1]) if j + 1 < len(tok) else None
                if not nk: break
                if w == 'na' and nk[0] in ('x100', 'x1000', 'x1M') and last in ('u', 't', 'd'): j += 1; continue            # "anim na raan"
                if w in ('at', 'y', 'and') and nk[0] in ('u', 't') and last in ('t', 'h', 'x100', 'x1000', 'x1M'): j += 1; continue   # "daan at siyam"
                if w in (',', 'at', 'and') and nk[0] == 'd' and last == 'd' and lastd % 100 == 0 and lastd >= 100 and nk[1] < 100:
                    j += 1; continue                                                   # heard "1900, 60" / "600 at 89": one number to a listener
                break
            k = _kind(w)
            if not k: break
            kind, x = k
            if kind == 'd':
                if last is None: cur = x
                elif last == 'd' and lastd % 100 == 0 and lastd >= 100 and x < 100: cur += x
                else: break
                lastd = x
            elif kind == 'u':
                if last == 'd' or (last == 'u' and not (cur % 100 == 10 and tok[j - 1].startswith('labi'))): break   # "isa, dalawa": two numbers
                cur += x
            elif kind == 't':
                if last == 'd': break
                if last in ('u', 't') and cur % 100:
                    if total == 0 and 10 <= cur <= 99: cur = cur * 100 + x                # English year pair: "eighteen ninety" -> 1890
                    else: break
                else: cur += x
            elif kind == 'h':
                if cur % 1000 or last == 'd': break
                cur += x
            elif kind == 'x100': cur = (cur or 1) * 100
            elif kind == 'x1000': total += (cur or 1) * 1000; cur = 0
            elif kind == 'x1M': total = (total + (cur or 1)) * 10 ** 6; cur = 0
            last = kind; j += 1
        if j < len(tok) and tok[j] in ('oh', 'o') and last == 'u' and total == 0 and 10 <= cur <= 99 and j + 1 < len(tok) and (_kind(tok[j + 1]) or ('',))[0] == 'u':
            cur = cur * 100 + _kind(tok[j + 1])[1]; j += 2                             # "nineteen oh six" -> 1906
        if j == i: i += 1; continue
        out.append((i, j, total + cur)); i = j
    return out, tok

def _real(spans, tok): return [(s, e, v) for s, e, v in spans if not (e - s == 1 and tok[s] == 'isang')]   # "isang" alone = the article "a"

def numbers(t):
    """Every number in the text, in order (digits and words alike)."""
    spans, tok = _scan(t); return [v for s, e, v in _real(spans, tok)]

def strip(t):
    """The text with every number removed (digits and number words), for the letter-by-letter comparison."""
    spans, tok = _scan(t); drop = set()
    for s, e, v in _real(spans, tok): drop.update(range(s, e))
    return ' '.join(w for k, w in enumerate(tok) if k not in drop and w.isalnum())

def starts_with_number(t):
    spans, tok = _scan(t); first = next((k for k, w in enumerate(tok) if w.isalnum()), None)
    return any(s == first for s, e, v in _real(spans, tok))

def diff(want, heard):
    """-> [(expected, heard), ...] for numbers that differ (None where one side has no number)."""
    a, b = numbers(want), numbers(heard); out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == 'equal': continue
        for k in range(max(i2 - i1, j2 - j1)):
            out.append((a[i1 + k] if i1 + k < i2 else None, b[j1 + k] if j1 + k < j2 else None))
    return out

TESTS = [  # (script as spoken, heard, expected numbers, numbers must match?)
    ("sumuko siya noong mil nuwebe syentos sais, umaasa", "Sumuko siya noong 1906, umaasa", [1906], True),
    ("sumuko siya noong mil nuwebe syentos sais, umaasa", "Sumuko siya noong 1909, umaasa", [1906], False),
    ("trenta'y singko na ako", "35 na ako", [35], True), ("trenta'y singko na ako", "Tanat-ray-sinko na ako", [35], False),
    ("dos mil bente singko", "2025", [2025], True), ("noong ikalabintatlo ng setyembre", "noong ikalabintatlo ng Setyembre", [], True),
    ("limampung sasakyan", "50 sasakyan", [50], True), ("dalawampu't isang taon", "21 taon", [21], True), ("sa daan papunta", "sa daan papunta", [], True),
    ("setenta'y dos porsyento", "72%", [72], True), ("kabanata bente dos, talata uno", "Kabanata 22, Talata 1", [22, 1], True), ("isang video", "Isang video", [], True),
    ("mil otsosyentos nobentay otso", "1898", [1898], True), ("limang trak", "5 truck", [5], True),
    ("siyamnapu't dalawang porsiyento", "siyam napot dalawang porsyento", [92], True), ("siyamnapu't dalawang porsiyento", "72% pa rin", [92], False),
    ("limampu", "lima pu", [50], True), ("dalawampung taon", "dalawam pung taon", [20], True),
    # second round: false alarms reported by the render machines, and the cases they must still catch
    ("labing-anim na raan at siyam", "1609", [1609], True), ("labingwalong daan at tatlumpu't pito", "1837", [1837], True),
    ("dalawang daan at apatnapu't tatlong kasapi", "243 kasapi", [243], True), ("mil seis siyentos nuwebe", "1609", [1609], True),
    ("mil sesyentos nuwebe", "1609", [1609], True), ("mil kinyentos sisenta'y singko", "1565", [1565], True),
    ("mil kinyentos sisenta'y singko", "1500, season 5", [1565], False),
    ("aklat ng mil sesyentos nuwebe, na ilalathala niya sa paris noong mil otsosyentos nobenta", "aklat ng 1609, na ilalathala niya sa Paris noong 1890", [1609, 1890], True),
    ("unang iniulat noong mil otsosyentos treyntay siyete", "unang iniulat noong 1837", [1837], True),
    ("oktubre mil otsosyentos kuwarenta, dalawang daan at apatnapu't tatlong kasapi", "Oktubre 1840, 243 kasapi", [1840, 243], True),
    ("eighteen ninety-six", "1896", [1896], True), ("eighteen sixty-nine", "1869", [1869], True), ("nineteen oh-six", "1906", [1906], True),
    ("eighteen ninety-nine", "1899", [1899], True), ("mil otso syentos sisentay nuwebe", "1869", [1869], True),
    ("mil nuwebe syentos sais lang ito unang nalathala", "1906 lang ito unang nalathala", [1906], True),
    ("mil otsosyentos nobentay nuwebe, sumiklab", "1899, sumiklab", [1899], True),
    ("alas-siyete ng umaga, ikatatlumpu ng disyembre, mil otsosyentos nobentay sais", "Alas 7 ng umaga, ikatatlumpu ng Disyembre, 1896", [7, 1896], True),
    ("dalawampung milyong dolyar ang nakasulat", "20 milyong dolyar ang nakasulat", [20000000], True),
    ("dalawampung milyong dolyar ang nakasulat", "20 million dollars ang nakasulat", [20000000], True),
    ("bente milyones", "20 milyones", [20000000], True), ("ang dalawampung milyon, at walang pilipino", "ang 20 milyon at walang Pilipino", [20000000], True),
    ("humingi ang mga britis ng apat na milyong piso", "humingi ang mga British ng 4 na milyong piso", [4000000], True),
    ("alas-sais ng umaga, sa risal park", "Alasais ng umaga sa Rizal Park", [6], True), ("alas-sais ng umaga", "Alas sais ng umaga", [6], True),
    ("noong mil nuwebe syentos sisenta", "noong 1900, 60", [1960], True), ("mil nuwebe syentos sisenta", "1916", [1960], False),
    ("noong anim na raan at walumpu't siyam hanggang siyam na raan at walumpu't walo", "noong 600 at 89 hanggang 188", [689, 988], False),
    ("noong anim na raan at walumpu't siyam hanggang siyam na raan at walumpu't walo", "noong 689 hanggang 988", [689, 988], True),
    ("henesis tres, bente kuwatro", "Genesis 3:24", [3, 24], True), ("henesis tres, bente kuwatro", "Genesis 3", [3, 24], False),
    ("genesis siyam, talata labing-isa", "Genesis 9, talata 11", [9, 11], True), ("genesis siyam, talata labing-isa", "Genesis siyam, talata labing isa", [9, 11], True),
    ("isa, dalawa, tatlo", "1, 2, 3", [1, 2, 3], True), ("mula sa isang libong metro", "mula sa 1,000 metro", [1000], True),
    ("isandaang taon", "100 taon", [100], True), ("mil kuwatrosiyentos nobentay dos", "1492", [1492], True),
    ("tatlong daan at apatnapu", "300 at 40", [340], True), ("mil nobesiyentos", "1900", [1900], True),
    ("mahigit dalawang libong metro ang taas", "mahigit 2000 metro ang taas", [2000], True), ("libu-libo na sila", "libu-libo na sila", [], True),
]

if __name__ == '__main__':
    bad = 0
    for w, h, exp, same in TESTS:
        got, d = numbers(w), diff(w, h); ok = got == exp and (not d) == same; bad += not ok
        print('%s %-60s | %-40s want %s heard %s diff %s' % ('ok  ' if ok else 'FAIL', w[:60], h[:40], got, numbers(h), d))
    print('%d of %d tests fail' % (bad, len(TESTS))); raise SystemExit(1 if bad else 0)
