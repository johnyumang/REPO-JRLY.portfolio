#!/usr/bin/env bash
# Episode 4 end to end. Work files (frames, audio, video) go to $WORK, outside the repo: the repo is public.
# usage: bash build.sh [WORK_DIR]
set -euo pipefail
cd "$(dirname "$0")"; WORK=${1:-/tmp/bike-history/ep04}; KOKORO_DIR=${KOKORO_DIR:-/opt/kokoro}; mkdir -p "$WORK"
python3 render.py "$WORK/frames" > "$WORK/render.log" 2>&1          # 3D bike frames + label anchors (about 1 hour on 4 CPU cores)
python3 narration.py "$KOKORO_DIR" "$WORK/vo"                       # English voice + timing (KOKORO_DIR: kokoro-v1.0.onnx, voices-v1.0.bin)
python3 compose.py "$WORK/frames" "$WORK/silent.mp4" "$WORK/contact" "$WORK/vo/narration.json"  # backgrounds, labels, subtitles
python3 sound.py "$WORK/sound.wav" "$WORK/vo/voice.wav"
ffmpeg -y -loglevel error -i "$WORK/silent.mp4" -i "$WORK/sound.wav" -c:v copy \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11" -ar 48000 -c:a aac -b:a 192k -shortest -movflags +faststart "$WORK/ep04_first_harley.mp4"
ffmpeg -v error -i "$WORK/ep04_first_harley.mp4" -f null - && echo "every frame decodes"
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,nb_frames -of compact "$WORK/ep04_first_harley.mp4"
