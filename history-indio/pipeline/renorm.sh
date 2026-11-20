#!/usr/bin/env bash
# Re-normalise a finished episode MP4's audio to the channel's level (-16 LUFS integrated, true peak <= -1.5 dBTP,
# two-pass loudnorm, same as soundtrack.py), video stream copied untouched. Prints loudness before and after.
# usage: bash pipeline/renorm.sh <in.mp4> <out.mp4>
set -euo pipefail
IN="${1:?usage: renorm.sh <in.mp4> <out.mp4>}"; OUT="${2:?out.mp4}"
HERE="$(cd "$(dirname "$0")" && pwd)"; PY=/opt/vc/bin/python; [ -x "$PY" ] || PY=python3
"$PY" - "$IN" "$OUT" "$HERE" <<'P'
import sys, subprocess; sys.path.insert(0, sys.argv[3]); import soundtrack as s
b, a = s.loudnorm2(sys.argv[1], sys.argv[2], ('-map', '0:v:0', '-map', '0:a:0', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart'))
tp = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', sys.argv[2], '-vn', '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
tp = [l.split(':')[1].strip() for l in tp.split('Summary')[-1].splitlines() if l.strip().startswith('Peak:')]
print(f'loudness before {b:.1f} LUFS -> after {a:.1f} LUFS (target {s.LUFS}), true peak after {tp[-1] if tp else "?"} (ceiling {s.TP} dBTP): {sys.argv[2]}')
P
