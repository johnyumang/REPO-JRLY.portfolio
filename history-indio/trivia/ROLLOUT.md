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

## Grave episodes (the quiet look)

Pull, then run the same episode command again; the tool picks the quiet look by itself. Nothing else changes.
Episodes: 6, 20, 26, 28, 29, 31, 38, 40, 41, 42, 44, 45, 46, 48.

Report one line per episode: break length, cut time, loudness, peak, level difference, warnings, and what you saw on
the sheet.

## State on 13 November, 08:20 UTC (what changed after the first rollout)
- **The quiet look is in** (commit 57525be). Grave episodes get it by themselves: dark blue ground, no sunburst, a fade in and out, a low hum in place of the jingle.
- **Insert points moved in 19 episodes** after a second reader checked all 48: 3, 10, 11, 14, 15, 20, 21, 26, 29, 31, 33, 35, 38, 40, 41, 42, 44, 46, 50. The tool reads the index from `trivia_break.json`, so a pull and the same episode command are enough. A break spliced before the pull is spliced again; the voice lines stay.
- **Stickers are final** as of commit 508f20f. These were redrawn after the first versions went out: 4, 5, 6, 10, 11, 15, 18, 19, 20, 22 to 29, 31, 32, 35, 37, 39, 40, 42, 43, 44, 48, 49. A break rendered with an older sticker is rendered again.
- **Episode 45:** line 1 changed ("…kada dalawang taon."); record that one line again.
- **The caption check** no longer flags o/u and e/i spellings of one word, and the length warning fires only when a break is outside 12 to 24 s.
- **Still to come:** fixed recordings of "Teka, patalastas muna!" and "Balik sa kuwento, par!" (after the upload reset), and the older chibi Indio for Season 5.

