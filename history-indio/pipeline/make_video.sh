#!/usr/bin/env bash
# Build one video. usage: pipeline/make_video.sh <slug>
# Needs videos/<slug>/script.txt and videos/<slug>/shots.mjs. Output: /opt/work/<slug>/final.mp4 + qa_sheet.jpg
# Voice: if $HI_VOICE_REF points at a clean 15-25 s wav of the narrator, the read is converted to that voice;
# otherwise the plain Tagalog TTS voice is used (say so when delivering).
set -e
SLUG="$1"; HI="$(cd "$(dirname "$0")/.." && pwd)"; V="$HI/videos/$SLUG"; W="/opt/work/$SLUG"; mkdir -p "$W"
export HF_HUB_CACHE=/opt/models/hf
/opt/vc/bin/python "$HI/pipeline/make_sentences.py" "$V/script.txt" "$V/sentences.json"
/opt/vc/bin/python "$HI/pipeline/tts_mms.py" "$V/sentences.json" "$W/base.wav" "$V/timings.json"
VOICE="$W/base.wav"
if [ -n "$HI_VOICE_REF" ] && [ -f "$HI_VOICE_REF" ]; then
  /opt/cb/bin/python "$HI/pipeline/vc_chatterbox.py" "$W/base.wav" "$HI_VOICE_REF" "$W/voice.wav" && VOICE="$W/voice.wav"
fi
cd "$HI/engine3d"; (python3 -m http.server 8765 >/dev/null 2>&1 &) ; sleep 1
node render_stills.mjs "$V/shots.mjs" "$W/stills"
pkill -f "http.server 8765" || true
/opt/vc/bin/python "$HI/pipeline/build_video.py" "$V" "$W/stills" "$VOICE" "$W/final.mp4"
ffmpeg -v error -y -i "$W/final.mp4" -vf "fps=1/7,scale=216:-1,tile=8x4" -frames:v 1 "$W/qa_sheet.jpg"
ffmpeg -v error -i "$W/final.mp4" -vf "blackdetect=d=0.3,freezedetect=n=0.003:d=1.5" -an -f null - 2>&1 | grep -E "black_start|freeze_start" | head -5 || true
echo "voice used: $VOICE"; ls -la "$W/final.mp4"
