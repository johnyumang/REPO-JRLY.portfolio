"""Numbers in a script line and in what the recogniser heard, as integers, so "mil nuwebe syentos sais", "1906" and
"nineteen oh six" compare equal and 1906 vs 1909 is a wrong word.
Reads digits (1,906 / 72% / 3.5 -> 3 and 5), Tagalog (isa ... siyam, sampu, labing-, -pu, daan, libo), Spanish-derived
Tagalog (uno ... nuwebe, diyes ... disinuwebe, bente ... nobenta, -syentos, mil) and English (one ... ninety, hundred,
thousand), with the linkers -ng / -'t / -'y. No dependencies.
  numbers(text) -> [int, ...] in order;  strip(text) -> text with every number removed (for the letter comparison);
  starts_with_number(text) -> bool;  diff(want, heard) -> [(expected or None, heard or None), ...] for each mismatch."""
import re, difflib

def _forms(base, *alts): return (base,) + alts
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
for v, ws in {20: ('bente', 'beinte', 'veinte', 'twenty', 'dalawampu'), 30: ('trenta', 'treinta', 'thirty', 'tatlumpu'),
              40: ('kuwarenta', 'kwarenta', 'cuarenta', 'forty', 'apatnapu'), 50: ('singkuwenta', 'singkwenta', 'sinkuwenta', 'sinkwenta', 'cincuenta', 'fifty', 'limampu'),
              60: ('sesenta', 'sisenta', 'sixty', 'animnapu'), 70: ('setenta', 'sitenta', 'seventy', 'pitumpu'), 80: ('otsenta', 'ochenta', 'eighty', 'walumpu'),
              90: ('nobenta', 'nubenta', 'noventa', 'ninety', 'siyamnapu')}.items():
    for w in ws: TENS[w] = v
HUND = {}
for v, ws in {100: ('siyento', 'syento', 'siento', 'ciento'), 200: ('dosyentos', 'dosientos', 'doscientos'), 300: ('tresyentos', 'tresientos', 'trescientos'),
              400: ('kuwatrosyentos', 'kwatrosyentos', 'cuatrocientos'), 500: ('kinyentos', 'quinientos'), 600: ('saisyentos', 'seiscientos'),
              700: ('siyetesyentos', 'syetesyentos', 'setecientos'), 800: ('otsosyentos', 'otsosientos', 'ochocientos'),
              900: ('nobesyentos', 'nobesientos', 'novecientos', 'nobyentos')}.items():
    for w in ws: HUND[w] = v
TIMES100 = {'syentos', 'siyentos', 'sientos', 'cientos', 'hundred', 'daan', 'raan'}      # after a number: x 100 ("nuwebe syentos", "limang daan")
TIMES1000 = {'mil', 'thousand', 'libo'}                                                    # "mil" alone = 1000; "libo" only after a number
TIMES1M = {'milyon', 'million'}
NEED_BEFORE = {'daan', 'raan', 'libo', 'hundred'}                                          # ordinary words ("daan" = road) unless a number comes first
NOT_NUM = {'una', 'isang'}                                                                 # handled below; "una" = first

def _words(t):
    t = t.lower().replace('ñ', 'n')
    for a, b in (('á', 'a'), ('é', 'e'), ('í', 'i'), ('ó', 'o'), ('ú', 'u')): t = t.replace(a, b)
    t = re.sub(r'(?<=\d)[,.](?=\d{3}\b)', '', t)                  # 1,906 -> 1906
    t = t.replace('%', ' porsyento ').replace('-', ' ').replace('’', '').replace("'", '')
    t = re.sub(r'\b(apat|anim|siyam)\s+na\s*p([uo])', r'\1nap\2', t)          # recogniser splits: "siyam napot" -> siyamnapot
    t = re.sub(r'\b(dalawa|tatlu|tatlo|lima|pitu|pito|walu|walo)m?\s+m?p([uo])', lambda m: {'tatlo': 'tatlu', 'pito': 'pitu', 'walo': 'walu'}.get(m[1], m[1]) + 'mp' + m[2], t)
    return re.findall(r'\d+|[a-z]+|[^\sa-z\d]', t)               # punctuation kept as its own token: it ends a number

def _val(w):
    """-> (kind, value) for a number word, its linker forms included ("limang", "dalawamput", "trentay"), else None."""
    for x in (w, w[:-2] if w.endswith('ng') else None, w[:-1] if w[-1:] in 'gty' else None):
        if not x: continue
        if x.endswith('po') and x[:-1] + 'u' in TENS: x = x[:-1] + 'u'                  # "siyamnapo" heard for siyamnapu
        if x in UNIT: return 'u', UNIT[x]
        if x in TENS: return 't', TENS[x]
        if x in HUND: return 'h', HUND[x]
        if x in TIMES100: return 'x100', 100
        if x in TIMES1000: return 'x1000', 1000
        if x in TIMES1M: return 'x1M', 10 ** 6
        if x in ('labing', 'labin', 'labim'): return 'u', 10
    return None

def _scan(t):
    """-> list of (start_token, end_token, value) for each number, and the tokens."""
    tok = _words(t); out = []; i = 0
    while i < len(tok):
        w = tok[i]
        if w.isdigit():
            out.append((i, i + 1, int(w))); i += 1; continue
        v = _val(w) if w.isalpha() else None
        if not v or (w in NEED_BEFORE) or (v[0] == 'x1000' and w.startswith('libo')) or (v[0] == 'x100' and v[1] == 100 and w in ('daan', 'raan', 'daang', 'raang')):
            i += 1; continue
        total, cur, j, last = 0, 0, i, None
        while j < len(tok):
            w = tok[j]; v = _val(w) if w.isalpha() else None
            if w in ('at', 'y', 'and') and last in ('t', 'h', 'x1000', 'x100') and j + 1 < len(tok) and _val(tok[j + 1]) and _val(tok[j + 1])[0] == 'u':
                j += 1; continue                                                     # "dalawampu at isa", "treinta y uno"
            if not v: break
            k, x = v
            if k == 'u':
                if last == 'u' and not (cur == 10 and tok[j - 1].startswith('labi')): break   # "isa, dalawa": two numbers
                cur += x
            elif k == 't':
                if last in ('u', 't') and cur % 100: break
                cur += x
            elif k == 'h':
                if cur: break
                cur += x
            elif k == 'x100': cur = (cur or 1) * 100
            elif k == 'x1000': total += (cur or 1) * 1000; cur = 0
            elif k == 'x1M': total += (cur or 1) * 10 ** 6; cur = 0
            last = k; j += 1
        if j == i: i += 1; continue
        out.append((i, j, total + cur)); i = j
    return out, tok

def numbers(t):
    """Every number in the text, in order (digits and words alike). "isang" (the article "a/one") is not counted."""
    return [v for s, e, v in _scan(t)[0] if not (e - s == 1 and _scan_word(t, s) in NOT_NUM)]

def _scan_word(t, i): return _words(t)[i]

def strip(t):
    """The text with every number removed (digits and number words), for the letter-by-letter comparison."""
    spans, tok = _scan(t); drop = set()
    for s, e, v in spans:
        if not (e - s == 1 and tok[s] in NOT_NUM): drop.update(range(s, e))
    return ' '.join(w for k, w in enumerate(tok) if k not in drop and (w.isalpha() or w.isdigit()))

def starts_with_number(t):
    spans, tok = _scan(t); first = next((k for k, w in enumerate(tok) if w.isalnum()), None)
    return any(s == first and not (e - s == 1 and tok[s] in NOT_NUM) for s, e, v in spans)

def diff(want, heard):
    """-> [(expected, heard), ...] for numbers that differ (None where one side has no number)."""
    a, b = numbers(want), numbers(heard); out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == 'equal': continue
        for k in range(max(i2 - i1, j2 - j1)):
            out.append((a[i1 + k] if i1 + k < i2 else None, b[j1 + k] if j1 + k < j2 else None))
    return out

if __name__ == '__main__':
    for w, h in [("sumuko siya noong mil nuwebe syentos sais, umaasa", "Sumuko siya noong 1906, umaasa"),
                 ("sumuko siya noong mil nuwebe syentos sais, umaasa", "Sumuko siya noong 1909, umaasa"),
                 ("trenta'y singko na ako", "35 na ako"), ("trenta'y singko na ako", "Tanat-ray-sinko na ako"),
                 ("dos mil bente singko", "2025"), ("noong ikalabintatlo ng setyembre", "noong ikalabintatlo ng Setyembre"),
                 ("limampung sasakyan", "50 sasakyan"), ("dalawampu't isang taon", "21 taon"), ("sa daan papunta", "sa daan papunta"),
                 ("setenta'y dos porsyento", "72%"), ("kabanata bente dos, talata uno", "Kabanata 22, Talata 1"), ("isang video", "Isang video"),
                 ("mil otsosyentos nobentay otso", "1898"), ("limang trak", "5 truck"),
                 ("siyamnapu't dalawang porsiyento", "siyam napot dalawang porsyento"), ("siyamnapu't dalawang porsiyento", "72% pa rin"),
                 ("limampu", "lima pu"), ("dalawampung taon", "dalawam pung taon")]:
        print('%-50s | %-35s want %s heard %s diff %s | %s' % (w, h, numbers(w), numbers(h), diff(w, h), strip(w)))
