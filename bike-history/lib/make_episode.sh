#!/usr/bin/env bash
# One episode end to end, from EP_DIR/spec.py: voice -> word check -> 3D render -> compose -> sound -> MP4 -> checks
# -> contact sheet -> cover -> thumbnail. Work files go to WORK (outside the repo: the repo is public).
# usage: bash lib/make_episode.sh EP_DIR WORK KOKORO_DIR        Re-running resumes: rendered frames are kept.
set -euo pipefail
EP=$(cd "$1" && pwd); WORK=$2; KOK=$3; LIB=$(cd "$(dirname "$0")" && pwd); mkdir -p "$WORK"
N=$(basename "$EP"); log() { echo "[$(date +%H:%M)] $N $*" | tee -a "$WORK/status.txt"; }
log start
python3 "$LIB/narration_episode.py" "$EP" "$KOK" "$WORK/vo" > "$WORK/narration.log" 2>&1
grep -i "too long" "$WORK/narration.log" | sed 's/^/  /' | tee -a "$WORK/status.txt" || true
python3 - "$WORK" > "$WORK/heard.txt" 2>/dev/null <<'P' || true
import sys, numpy as np, soundfile as sf
from faster_whisper import WhisperModel
a, sr = sf.read(sys.argv[1] + '/vo/voice.wav'); a16 = np.interp(np.arange(0, len(a), sr / 16000), np.arange(len(a)), a).astype(np.float32)
print(' '.join(s.text for s in WhisperModel('small.en', device='cpu', compute_type='int8').transcribe(a16, beam_size=5)[0]))
P
log "voice done"
python3 "$LIB/render_episode.py" "$EP" "$WORK/frames" > "$WORK/render.log" 2>&1
log "render done ($(grep -c SHOT "$WORK/render.log") shots)"
python3 "$LIB/compose_episode.py" "$EP" "$WORK/frames" "$WORK/silent.mp4" "$WORK/contact" "$WORK/vo/narration.json" 2>&1 | tail -1 | cut -c1-90 | tee -a "$WORK/status.txt"
python3 "$LIB/sound_episode.py" "$EP" "$WORK/sound.wav" "$WORK/vo/voice.wav" | tail -2 | tr '\n' ' ' >> "$WORK/status.txt"; echo >> "$WORK/status.txt"
ffmpeg -y -loglevel error -i "$WORK/silent.mp4" -i "$WORK/sound.wav" -c:v copy -af "loudnorm=I=-16:TP=-1.5:LRA=11" \
  -ar 48000 -c:a aac -b:a 192k -shortest -movflags +faststart "$WORK/$N.mp4"
ffmpeg -v error -i "$WORK/$N.mp4" -f null - && log "every frame decodes"
log "$(ffprobe -v error -show_entries format=duration:stream=nb_frames -of csv=p=0 "$WORK/$N.mp4" | tr '\n' ' ') $(ffmpeg -hide_banner -nostats -i "$WORK/$N.mp4" -af ebur128 -f null - 2>&1 | grep ' I:' | tail -1 | tr -s ' ')"
python3 - "$WORK" <<'P'
from PIL import Image; import glob, sys
fs = sorted(glob.glob(sys.argv[1] + '/contact/*.jpg')); cols = 10; rows = (len(fs) + cols - 1) // cols
sh = Image.new('RGB', (cols * 216, rows * 384), (30, 30, 30))
for i, f in enumerate(fs): sh.paste(Image.open(f).resize((216, 384)), ((i % cols) * 216, (i // cols) * 384))
sh.save(sys.argv[1] + '/contact_sheet.jpg', quality=85)
P
MOD=$(python3 -c "import importlib.util,sys;s=importlib.util.spec_from_file_location('s','$EP/spec.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);print(m.MODEL)")
read_spec() { python3 -c "import importlib.util;s=importlib.util.spec_from_file_location('s','$EP/spec.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);print(getattr(m,'$1'))"; }
python3 "$LIB/cover.py" "$MOD" "$(read_spec COVER_PROMPT)" "$WORK/cover.jpg" -28 2>&1 | grep -E "^cover|no background" | cut -c1-60 | tee -a "$WORK/status.txt" || true
python3 "$LIB/cover.py" "$MOD" "$(read_spec THUMB_PROMPT)" "$WORK/thumb.jpg" -28 v "$(read_spec THUMB_BIG)" "$(read_spec THUMB_NAME)" "BIKE HISTORY · EP $(read_spec EP)" 2>&1 | grep -E "^cover|no background" | cut -c1-60 | tee -a "$WORK/status.txt" || true
log DONE
