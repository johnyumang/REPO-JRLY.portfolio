#!/usr/bin/env bash
# Render the four host action clips for limahong-1574 (30 fps, 720x1280, no audio).
# Durations = line length in timings.json (start to next start) + 0.4 s.
set -euo pipefail
W=${1:-/opt/bl}
OUT=${2:-$W/out/clips}
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$OUT"
while read -r id shot secs; do
  "$W/v/bin/python" "$HERE/host_shot.py" --model "$W/model/host.glb" --out "$OUT/$id" --shot "$shot" --seconds "$secs" --fps 30 2>&1 | grep -E "TIMING|Error|Traceback"
  ffmpeg -y -loglevel error -framerate 30 -i "$OUT/$id/f%04d.png" -an -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p -movflags +faststart "$OUT/$id.mp4"
  echo "done $OUT/$id.mp4"
done <<'L'
c02 greet 2.76
c31 twist 2.36
c39 point 3.04
c41 powerup 4.68
L
