"""List sentences whose text is new compared with a git revision (default HEAD): index and text."""
import json, subprocess, sys
d = sys.argv[1].rstrip('/'); rev = sys.argv[2] if len(sys.argv) > 2 else 'HEAD'
old = {x['text'] for x in json.loads(subprocess.check_output(['git', 'show', f'{rev}:history-indio/{d}/sentences.json']))}
new = json.load(open(f'{d}/sentences.json'))
gone = old - {x['text'] for x in new}
print(f"{d}: {len(new)} sentences, {sum(len(x['text'].split()) for x in new)} words")
for i, x in enumerate(new):
    if x['text'] not in old: print(f"  s{i} {x['speaker']}: {x['text']}")
for g in sorted(gone): print(f"  GONE: {g}")
