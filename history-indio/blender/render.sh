#!/usr/bin/env bash
# Render the proof shot and encode it. Output: $W/out/host_shot.mp4 (never commit MP4s; the repo is public).
set -euo pipefail
W=${1:-/opt/bl}
HERE=$(cd "$(dirname "$0")" && pwd)
"$W/v/bin/python" "$HERE/host_shot.py" --model "$W/model/host.glb" --out "$W/out/frames" "${@:2}" 2>&1 | grep -E "FRAME|TIMING|Error|Traceback"
ffmpeg -y -loglevel error -framerate 24 -i "$W/out/frames/f%04d.png" -c:v libx264 -crf 17 -preset slow -pix_fmt yuv420p -movflags +faststart "$W/out/host_shot.mp4"
echo "$W/out/host_shot.mp4"
