#!/usr/bin/env bash
# Build one video. usage: pipeline/make_video.sh <slug>
# Needs videos/<slug>/script.txt and videos/<slug>/shots.mjs. Output: /opt/work/<slug>/final.mp4 + qa_sheet.jpg
# Voice: the indio-voice skill reads the tagged script expressively. With $HI_VOICE_REF (clean 15-25 s narrator wav)
# it speaks in the narrator's voice; without it, it uses a neutral male Tagalog voice (say so when delivering).
set -e
SLUG="$1"; HI="$(cd "$(dirname "$0")/.." && pwd)"; V="$HI/videos/$SLUG"; W="/opt/work/$SLUG"; mkdir -p "$W"
export HF_HUB_CACHE=/opt/models/hf
/opt/vc/bin/python "$HI/pipeline/make_sentences.py" "$V/script.txt" "$V/sentences.json"
/opt/vc/bin/python "$HI/pipeline/tts_mms.py" "$V/sentences.json" "$W/base.wav" "$V/timings.json"
REF="${HI_VOICE_REF:-$HI/voice/default_ref.wav}"     # narrator sample; falls back to a neutral sample made from the TTS voice
if [ ! -f "$REF" ]; then mkdir -p "$HI/voice"; ffmpeg -v error -y -i "$W/base.wav" -t 20 -ar 24000 "$REF"; fi
VOICE="$W/voice.wav"
/opt/vc/bin/python "$HI/skills/indio-voice/scripts/voice.py" "$V/sentences.json" "$REF" "$VOICE" "$V/timings.json"
cd "$HI/engine3d"; (python3 -m http.server 8765 >/dev/null 2>&1 &) ; sleep 1
node render_stills.mjs "$V/shots.mjs" "$W/stills"
pkill -f "http.server 8765" || true
/opt/vc/bin/python "$HI/pipeline/build_video.py" "$V" "$W/stills" "$VOICE" "$W/final.mp4"
ffmpeg -v error -y -i "$W/final.mp4" -vf "fps=1/7,scale=216:-1,tile=8x4" -frames:v 1 "$W/qa_sheet.jpg"
ffmpeg -v error -i "$W/final.mp4" -vf "blackdetect=d=0.3,freezedetect=n=0.003:d=1.5" -an -f null - 2>&1 | grep -E "black_start|freeze_start" | head -5 || true
echo "voice used: $VOICE"; ls -la "$W/final.mp4"
