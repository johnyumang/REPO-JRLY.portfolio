# Trivia break: what every render machine does (13 November)

The owner said to proceed, in the version 2 look. For EACH of your episodes from 3 to 50, once its rebuilt MP4 exists
(Season 1: the rebuild with fixed stills; the others: the final-pass rebuild), from `history-indio/`:

1. `git pull`, then record the break lines (Indio's clone and Usman's designed voice; needs `USMAN.wav` and `USMAN.txt`
   in your cast folder; nothing else heavy may run beside it; about 15 minutes):
   `/opt/vc/bin/python pipeline/trivia_voice.py videos/<slug> --out $HI_VOICE_WORK/<slug>/trivia`
2. `git pull` again (the stickers in `trivia/stickers/` are still being improved), then render and splice:
   `/opt/vc/bin/python pipeline/trivia_break.py episode videos/<slug> --voice $HI_VOICE_WORK/<slug>/trivia --video <rebuilt>.mp4 --out <rebuilt>_trivia.mp4`
   It renders the break (the calm variant by itself when the episode's file says `"grave": true`), finds the cut in the
   silent gap after the right sentence in the CURRENT `timings.json`, matches the break's level to the story around it,
   splices, and checks the result.
3. LOOK at the sheet and the four frames it prints: the sticker is the right subject and whole; nothing covers a face;
   every word is whole. Read its summary line: duration = episode + break, about -16 LUFS, true peak at or under
   -1.5 dBTP, level difference within 1.5 LU.
4. If it prints `CAPTION MISMATCH`, `INTONATION`, `LEVEL MISMATCH`, or refuses the cut: fix that (more takes with
   `--takes 5`; a per-line `"say"` or `"tone"` in the json only when needed, and tell the conductor) instead of passing
   it on. For a grave episode, judge honestly whether the break is fitting where it sits; if it is not, say what you see.
5. Keep BOTH files on disk (with and without the break). Publish nothing until the conductor says so.
6. Episodes that still wait for other voice work (cast kit 4 for the adult Bea and JM): record the trivia lines now and
   splice after the final rebuild.

Report one line per episode: break length, cut time, loudness, peak, level difference, warnings, and what you saw on
the sheet.
