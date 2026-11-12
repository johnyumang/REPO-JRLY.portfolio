#!/usr/bin/env bash
# Narration for one episode in the cloned Indio voice: plan -> generate -> check and select -> retry seeds -> assemble -> verify.
# usage: HI_VOICE_REC=<real ep1 recording> bash run_episode.sh videos/<slug> [max_seed]
# env:   HI_VOICE_WORK (default /opt/work/voice; baseline in $HI_VOICE_WORK/baseline, takes in $HI_VOICE_WORK/<slug>)
# Resumable: existing takes and their checks are kept, so a re-run only does what is missing.
# Heavy: about 65-110 s per sentence on 4 CPU cores and about 11 GB RAM. One run at a time per machine (CPU lock below).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
EP="$(cd "${1:?usage: run_episode.sh videos/<slug> [max_seed]}" && pwd)"; MAX_SEED="${2:-3}"
VC=/opt/vc/bin/python; VX=/opt/vx/bin/python
export HI_VOICE_WORK="${HI_VOICE_WORK:-/opt/work/voice}"
[ -f "${HI_VOICE_REC:-}" ] || { echo "set HI_VOICE_REC to the real Episode 1 recording"; exit 1; }
for f in real_ep1.json real_centroid.npy; do [ -f "$HI_VOICE_WORK/baseline/$f" ] || { echo "missing baseline/$f: run baseline.py (README.md)"; exit 1; }; done
[ -x "$VX" ] || { echo "run setup_vox.sh first"; exit 1; }
W="$HI_VOICE_WORK/$(basename "$EP")"; mkdir -p "$W"
exec 9>"$HI_VOICE_WORK/cpu.lock"; flock -n 9 || { echo "another voice run holds the CPU ($HI_VOICE_WORK/cpu.lock)"; exit 1; }
redo() { $VC -c "import json,sys; c=json.load(open(sys.argv[1])); print(','.join(k for k,v in c.items() if not v['ok']))" "$W/choice.json"; }

echo "== 1 plan";            $VC "$HERE/plan.py" "$EP" "$W" | tee "$W/plan.log"
echo "== 2 generate (U,R seed 1)"; $VX -u "$HERE/gen.py" "$W" --modes U,R --seeds 1 2>&1 | tee -a "$W/gen.log"
echo "== 3 check and select"; $VC -u "$HERE/qcsel.py" "$W" 2>&1 | tee -a "$W/qc.log"
for s in $(seq 2 "$MAX_SEED"); do
  R="$(redo)"; [ -z "$R" ] && break
  echo "== 4 retry seed $s for chunks $R"
  $VX -u "$HERE/gen.py" "$W" --only "$R" --modes U,R --seeds "$s" 2>&1 | tee -a "$W/gen.log"
  $VC -u "$HERE/qcsel.py" "$W" 2>&1 | tee -a "$W/qc.log"
done
R="$(redo)"; [ -n "$R" ] && echo "WARNING: no passing take for chunks $R (best take used; listen to these first)"
echo "== 5 assemble";        $VC -u "$HERE/assemble.py" "$W" "$EP" "$W/voice" 2>&1 | tee "$W/assemble.log"
echo "== 6 verify";          $VC -u "$HERE/verify.py" "$W/voice.mp3" "$W/voice_timings.json" "$W/plan.json" 2>&1 | tee "$W/verify.log"
echo "done: $W/voice.mp3 and $W/voice_timings.json (copy the timings to $EP/timings.json after the user approves the voice)"
