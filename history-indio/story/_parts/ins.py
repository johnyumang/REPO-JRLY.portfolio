"""Small helper for rule-9 revisions: edit a master script by line prefix.
ops: ('after', prefix, text) insert text after the first line starting with prefix;
     ('before', prefix, text); ('cut', prefix) delete that line; ('sub', prefix, text) replace that line."""
import sys
def apply(path, ops):
    L = open(path).read().split('\n')
    for op in ops:
        kind, pre = op[0], op[1]
        hits = [i for i, l in enumerate(L) if l.startswith(pre)]
        assert hits, ('NOT FOUND', pre)
        i = hits[0]
        if kind == 'after': L[i + 1:i + 1] = op[2].split('\n')
        elif kind == 'before': L[i:i] = op[2].split('\n')
        elif kind == 'cut': del L[i]
        elif kind == 'sub': L[i:i + 1] = op[2].split('\n')
    open(path, 'w').write('\n'.join(L))
