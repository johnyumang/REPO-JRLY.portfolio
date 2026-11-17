#!/usr/bin/env bash
# One command for an episode: manifest -> 16:9 stills -> clips -> render -> loudness (-16 LUFS, true peak <= -1.5 dBTP).
# usage: bash pipeline/animate/run.sh <episode> --voice <voice.wav> [--shots 0-3] [--provider wan-free|comfy|minimax]
#                                     [--work DIR] [--manifest FILE] [--no-draw] [--fresh]
#   <episode>   name under videos/ (e.g. ep01b-1min) or a path to the episode folder
#   --manifest  start from a manifest exported by the studio instead of writing one (its picked takes are downloaded)
# Everything made goes to the work dir (default /opt/work/animate/<episode>), never into the repo.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$HERE/../.." && pwd)"
EP="${1:?usage: run.sh <episode> --voice <voice.wav> [options]}"; shift
VOICE=""; SHOTS=""; PROVIDER=""; WORK=""; MAN_IN=""; NODRAW=""; FRESH=""
while [ $# -gt 0 ]; do case "$1" in
  --voice) VOICE="$2"; shift 2;; --shots) SHOTS="$2"; shift 2;; --provider) PROVIDER="$2"; shift 2;;
  --work) WORK="$2"; shift 2;; --manifest) MAN_IN="$2"; shift 2;; --no-draw) NODRAW=1; shift;; --fresh) FRESH=1; shift;;
  *) echo "unknown option $1"; exit 2;; esac; done
[ -d "$EP" ] && EPDIR="$(cd "$EP" && pwd)" || EPDIR="$ROOT/videos/$EP"
NAME="$(basename "$EPDIR")"; WORK="${WORK:-/opt/work/animate/$NAME}"; mkdir -p "$WORK"; WORK="$(cd "$WORK" && pwd)"
MAN="$WORK/manifest.json"
CHROME="${CHROME:-/opt/pw-browsers/chromium}"

# python with the gradio client (for the free provider)
PY="${PY:-}"
if [ -z "$PY" ]; then
  for c in "$WORK/../venv/bin/python" /opt/work/anim/venv/bin/python python3; do
    if "$c" -c "import gradio_client" 2>/dev/null; then PY="$c"; break; fi; done
fi
if [ -z "$PY" ]; then
  python3 -m venv "$WORK/../venv" && "$WORK/../venv/bin/pip" -q install gradio_client pillow && PY="$WORK/../venv/bin/python"
fi

echo "== 1. manifest"
if [ -n "$MAN_IN" ]; then cp "$MAN_IN" "$MAN"
elif [ ! -f "$MAN" ] || [ -n "$FRESH" ]; then
  python3 "$HERE/motion.py" "$EPDIR" "$MAN" ${SHOTS:+--shots "$SHOTS"} --audio voice.wav
fi
if [ -z "$MAN_IN" ]; then
  echo "== 2. 16:9 stills"
  python3 "$HERE/stills.py" "$EPDIR" "$MAN" "$WORK/stills16x9" ${NODRAW:+--no-draw}
fi
echo "== 3. clips (studio takes are downloaded, missing ones generated)"
"$PY" "$HERE/i2v.py" "$MAN" "$WORK" ${PROVIDER:+--provider "$PROVIDER"}

echo "== 4. render"
PUB="$WORK/public"; rm -rf "$PUB"; mkdir -p "$PUB/fonts" "$PUB/clips"
cp "$ROOT/pipeline/fonts/Anton-Regular.ttf" "$ROOT/pipeline/fonts/BebasNeue-Regular.ttf" "$PUB/fonts/"
[ -d "$WORK/clips" ] && cp "$WORK"/clips/*.mp4 "$PUB/clips/" 2>/dev/null || true
if [ -n "$VOICE" ]; then cp "$VOICE" "$PUB/voice.wav"; fi
"$PY" - "$MAN" "$WORK/props.json" "$PUB" <<'P'
import json, os, sys
m = json.load(open(sys.argv[1], encoding="utf-8"))
if not os.path.exists(os.path.join(sys.argv[3], "voice.wav")): m["audio"] = None
json.dump({"manifest": m}, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False)
P
cd "$HERE/remotion"
[ -d node_modules ] || npm install --no-audit --no-fund
RAW="$WORK/render_raw.mp4"; OUT="$WORK/${NAME}_animated.mp4"
npx remotion render src/index.ts Episode "$RAW" --props="$WORK/props.json" --public-dir="$PUB" \
  --browser-executable="$CHROME" --codec=h264 --crf=18 --log=warn
echo "== 5. loudness"
if ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$RAW" | grep -q .; then
  bash "$ROOT/pipeline/renorm.sh" "$RAW" "$OUT"
else cp "$RAW" "$OUT"; echo "no voice track: loudness step skipped"; fi
echo "done: $OUT"
