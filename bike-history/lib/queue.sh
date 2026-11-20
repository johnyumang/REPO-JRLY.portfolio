#!/usr/bin/env bash
# Build episodes one after another (one render at a time on this CPU). Skips any episode whose MP4 already exists.
# usage: bash lib/queue.sh WORK_ROOT KOKORO_DIR ep06 ep07 ...      (run from bike-history/)
ROOT=$1; KOK=$2; shift 2
for e in "$@"; do
  [ -f "$ROOT/$e/$e.mp4" ] && continue
  [ -f "$e/spec.py" ] || { echo "[$(date +%H:%M)] $e has no spec.py yet, stopping" >> "$ROOT/queue.txt"; exit 0; }
  bash lib/make_episode.sh "$e" "$ROOT/$e" "$KOK" >> "$ROOT/queue.txt" 2>&1 || echo "[$(date +%H:%M)] $e FAILED" >> "$ROOT/queue.txt"
done
echo "[$(date +%H:%M)] queue empty" >> "$ROOT/queue.txt"
