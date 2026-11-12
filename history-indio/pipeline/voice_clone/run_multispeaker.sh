#!/usr/bin/env bash
# Season 2 multi-voice read: plan -> one take per chunk -> check -> second take only where the words are wrong -> assemble -> verify.
# usage: HI_VOICE_REC=<real ep1 recording> bash run_multispeaker.sh <script_multispeaker.txt> <work_name> [--full]
#   --full: also retry chunks that fail a non-word check (pitch, speaker, speed...), up to seed 3.
# needs: the Indio baseline (as run_episode.sh) and $HI_VOICE_WORK/cast/<NAME>.wav + <NAME>.txt for every other speaker.
# Resumable; one heavy run per machine (cpu.lock).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$(realpath "${1:?usage: run_multispeaker.sh <script_multispeaker.txt> <work_name> [--full]}")"; NAME="${2:?work name}"; FULL="${3:-}"
VC=/opt/vc/bin/python; VX=/opt/vx/bin/python
export HI_VOICE_WORK="${HI_VOICE_WORK:-/opt/work/voice}"
[ -f "${HI_VOICE_REC:-}" ] || { echo "set HI_VOICE_REC to the real Episode 1 recording"; exit 1; }
for f in real_ep1.json real_centroid.npy; do [ -f "$HI_VOICE_WORK/baseline/$f" ] || { echo "missing baseline/$f: run baseline.py (README.md)"; exit 1; }; done
W="$HI_VOICE_WORK/$NAME"; mkdir -p "$W"
exec 9>"$HI_VOICE_WORK/cpu.lock"; flock -n 9 || { echo "another voice run holds the CPU ($HI_VOICE_WORK/cpu.lock)"; exit 1; }
redo() { $VC "$HERE/ms.py" qc "$W" $FULL 2>&1 | tee -a "$W/qc.log" | sed -n 's/^need another take: //p'; }
echo "== 1 plan";                 $VC "$HERE/ms.py" plan "$SCRIPT" "$W" | tee "$W/plan.log"
echo "== 2 generate (seed 1)";    $VX -u "$HERE/gen_ms.py" "$W" --seeds 1 2>&1 | tee -a "$W/gen.log"
echo "== 3 check and select";     R="$(redo)"
MAX=2; [ "$FULL" = "--full" ] && MAX=3
for s in $(seq 2 $MAX); do
  [ -z "$R" ] && break
  echo "== 4 take $s for chunks $R"; $VX -u "$HERE/gen_ms.py" "$W" --only "$R" --seeds "$s" 2>&1 | tee -a "$W/gen.log"; R="$(redo)"
done
[ -n "$R" ] && echo "WARNING: chunks $R still fail (best take used; listen to these first)"
echo "== 5 assemble";             $VC -u "$HERE/ms.py" assemble "$W" "$W/voice" 2>&1 | tee "$W/assemble.log"
echo "== 6 verify";               $VC -u "$HERE/ms.py" verify "$W" "$W/voice" 2>&1 | tee "$W/verify.log"
echo "done: $W/voice.mp3, $W/voice_timings.json (one entry per sentence, with speaker), $W/voice_verify.json"
