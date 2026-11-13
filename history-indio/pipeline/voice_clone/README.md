# voice_clone: Indio's narration from the user's own voice

Makes an episode's narration in the Indio voice, cloned locally from the user's OWN Episode 1 recording, so episodes
do not wait for a new recording (user decision, 2026-11-12). No ElevenLabs, no paid API. The recording is the user's
file: it, the baseline files and every generated audio file stay OUT of the repo (`/opt/work/voice` by default).

- Engine: VoxCPM2 (`openbmb/VoxCPM2`, Apache-2.0, official Tagalog, 48 kHz) on CPU, float32 config copy
  (`/opt/vx_model32`), in venv `/opt/vx` layered on `/opt/vc`. About 65-110 s per sentence on 4 cores, about 11 GB RAM.
- Rejected: OmniVoice (the user found its Tagalog unnatural; weights are non-commercial).

## Setup (once per machine)
```
bash history-indio/pipeline/setup.sh                 # the normal pipeline venv /opt/vc
bash history-indio/pipeline/voice_clone/setup_vox.sh # optional: faster-whisper in /opt/vc, /opt/vx, /opt/vx_model32
export HI_VOICE_REC=/path/to/episode_1_recording.mp3 # the user's file, never committed
export HI_VOICE_WORK=/opt/work/voice                 # default
cd history-indio
/opt/vc/bin/python pipeline/voice_clone/baseline.py videos/ep01-ang-unang-talon   # once per recording: baseline/real_ep1.json, real_centroid.npy
```
Slow network: plain pip can take over an hour on torch's CUDA wheels. Instead list the URLs (`pip install --dry-run --report r.json ...`), fetch them with `curl` 12 at a time and `pip install --no-index --find-links <dir>`: about 5 minutes.
The VoxCPM2 weights (4.6 GB) also come fastest as 16 parallel `curl -r` byte ranges (about 1 minute), then the float32 config copy as in `setup_vox.sh`.

## The sequence (one episode)
```
bash pipeline/voice_clone/run_episode.sh videos/<slug> [max_seed=3]
```
It runs, into `$HI_VOICE_WORK/<slug>/`:
1. `plan.py <ep> <work>`: `script_elevenlabs.txt` -> sentences (must equal `sentences.json`) -> chunks = runs of up to 3
   sentences / 170 characters in one paragraph that share a tone tag. `plan.json`.
2. `gen.py <work> --modes U,R --seeds 1` (in `/opt/vx`): two takes per chunk. **U** = continuation from a prompt cut
   from the real recording in the same tone + timbre reference; **R** = timbre reference only.
3. `qcsel.py <work>`: checks every take against the real recording and picks the best per chunk (`choice.json`).
4. Retry: chunks with no passing take get new takes with seed 2, then 3, re-checked each time.
5. `assemble.py <work> <ep> <work>/voice`: joins the chosen takes with per-tone levels, real-like pauses (0.38 s in a
   paragraph, 0.50 s between paragraphs), a match EQ to the real recording's spectrum, a compressor only if the clone is
   peakier, -17.4 LUFS. Writes `voice.mp3` and `voice_timings.json` (sentence times from the alignment, same format as
   `timings.json`).
6. `verify.py voice.mp3 voice_timings.json plan.json`: re-hears the finished file per sentence and per chunk.

Re-runs are resumable (existing takes and checks are kept). One run at a time per machine (`cpu.lock`).
After the user approves the voice: copy `voice_timings.json` to `videos/<slug>/timings.json` and build with
`build_anime.py ... $HI_VOICE_WORK/<slug>/voice.mp3 ...` (no `align_audio.py` needed).

## What the numbers mean (real Episode 1 recording = the yardstick)
| Check | What it is | Real recording | A take passes if |
|---|---|---|---|
| `edits` | spelling-insensitive edit distance between the script and what Whisper large-v3-turbo (forced Tagalog) hears | p90 = 1 | <= 1, and the first word is right |
| `cmatch` / `match` | same comparison as a 0-1 ratio (sound-based / word-based) | match mean 0.90 | cmatch >= 0.88 |
| `conf` / `minconf` | forced-alignment confidence per word (MMS aligner): is each word there and clear | mean 0.905 | mean >= 0.84, worst word >= 0.30 |
| `spk` | speaker similarity (WavLM x-vector) to the real voice's centroid | mean 0.972, min 0.917 | >= 0.915 |
| `rate` | syllables per second | 5.85 (sd 0.78) | 4.3-7.4 (assembly slows a take above 6.9 to 6.3) |
| `f0` | median pitch, against the real voice's window for that tone | per tone, `voice_profile.json` | inside the window -15% / +10% |
| `lead` / `trail` | sound before the first word / after the last, relative to speech level (breaths, clicks, babble) | ~0 | <= 0.12 |
Selection order: passing first, then fewest edits, then a score (0.40 cmatch + 0.25 conf + 0.10 minconf + 0.25 spk,
minus penalties for rate and artifacts).

`voice_profile.json` holds everything that is specific to the Episode 1 recording (prompt and reference sentence ids,
per-tone level and pitch window, target rate, loudness, centroid sentences) with a note on how each was measured.
A different reference recording needs a new baseline and a new profile.

## Season 2: several voices (`script_multispeaker.txt`)
Indio stays the clone of the user's own recording, exactly as above. Every other character is a **designed** voice
(VoxCPM2 voice design: a text description, never a clone of or an imitation of a real person), kept from one private
reference clip per character: `$HI_VOICE_WORK/cast/<NAME>.wav` + `<NAME>.txt` (its exact words; NAME in capitals,
spaces as underscores, e.g. `BATANG_INDIO`). Never in the repo.
```
# once: design the cast (descriptions, reference texts, sample lines in cast_design.json)
/opt/vx/bin/python pipeline/voice_clone/castdesign.py            # candidates: description x seed -> castwork/<NAME>/d<k>s<seed>.wav
/opt/vc/bin/python pipeline/voice_clone/castqc.py                # checks every candidate, keeps one per character in cast/, similarity table
/opt/vx/bin/python pipeline/voice_clone/castdesign.py --samples  # one extra line per character FROM the kept reference
/opt/vc/bin/python pipeline/voice_clone/castqc.py --samples      # does the voice hold (words, own-reference similarity, pitch drift)
# per episode (speed mode: one take per chunk, a second only where the words are wrong; --full retries every failed check)
bash pipeline/voice_clone/run_multispeaker.sh videos/<slug>/script_multispeaker.txt <slug> [--full]
```
- Script: one line per speaker turn, `NAME: [tone] text`; a blank line starts a new scene. Chunks never cross a turn.
- Generation (`gen_ms.py`): INDIO lines = mode U of `gen.py` (tone prompt from the real recording + timbre reference);
  other lines = continuation from the character's reference clip with its transcript (same clip as timbre reference).
- Checks (`ms.py qc`, via `vqc.take_metrics`): the word check is the same for every line (edits <= 1, first word right,
  cmatch >= 0.88). Speaker: INDIO against the real-recording centroid (>= 0.915, as `qcsel.py`); anyone else against
  ITS OWN reference clip (>= 0.85), pitch within 4 semitones of that clip. Speed, edge noise, clipping, pauses as above.
- Numbers (`numwords.py`): the word check compares numbers by VALUE, so "mil nuwebe syentos sais", "1906" and "nineteen oh six"
  are equal (Tagalog incl. "labing-anim na raan at siyam", Spanish-derived, English year pairs, milyon/libo, alas-, chapter and
  verse, digits, and a heard split a listener hears as one number: "1900, 60" = 1960; `python3 numwords.py` runs the tests), and a different number ("1909" for 1906) counts as a wrong
  word that forces the second take; among takes, one with every number right ranks first. `qc` re-judges old take files from
  their stored transcript, so a re-run picks takes by this rule with no new generation. Audit an episode already narrated:
  `/opt/vc/bin/python pipeline/voice_clone/ms.py numbers $HI_VOICE_WORK/<slug>` lists each chunk with a year, age, date or
  amount (expected vs heard in the chosen take, `DIFF` where they differ with the heard words, other takes' numbers); exit 1 if
  any differ. Works on Season 1 (`run_episode.sh`) work folders too. A DIFF chunk is heard once
  more with a prompt asking for numbers as words (`vqc.num_prompt`, whose examples never contain the line's own numbers: an
  example equal to the expected year steered a take that says 1909 into "1906"); if the numbers then match it prints
  "ok (on second listen)" with both transcripts. Last line: real DIFF / ok on second listen. The qc pass keeps its own prompt. To fix:
  `ms.py qc <work>`, then `ms.py assemble <work> <work>/voice`, then rebuild the video.
- Stray sound before the first word (`leadtrim.py`, called by `ms.py assemble`): when the recogniser hears an extra token
  before the script's first word ("O", "Do") and the take has a voiced burst (>= 60 ms) then a dip (>= 30 ms) before that
  word, the line is cut at the dip with a 40 ms pre-roll and fade-in, kept only if a second listen hears the first word and
  no drop in match; the same after the last word. Prints `trim cNNN ...` and a total. A stray syllable glued to the first
  word (no dip) cannot be trimmed: it needs another take. Episode 35: 1 trim, stray-start lines 4 -> 3, no line worse.
- Assembly (`ms.py assemble`): same per-tone level, slow-down of rushed takes, -17.4 LUFS master and true-peak limit as
  `assemble.py`; the match EQ to the real recording is applied to Indio's lines only. Pauses 0.38 s in a turn, 0.45 s
  between turns, 0.65 s between scenes. `voice_timings.json` = one entry per sentence in script order, the same format
  as `timings.json` plus a `speaker` field. `ms.py verify` re-hears every line of the finished file (`voice_verify.json`).
- Cast candidates are kept only if the words are right and nothing measurable is wrong (clipping, a pause > 0.8 s,
  speed outside 4.8-6.8 syl/s, pitch outside the character's range) and the voice is below 0.88 speaker similarity to
  Indio and to every voice already kept. The numbers measure clarity and consistency, not naturalness: the user's ear decides.

## Final pass (a finished episode, before its last publish)
From `history-indio/`, with `W=$HI_VOICE_WORK/<slug>` (default `/opt/work/voice/<slug>`), `HI_VOICE_REC` set, one heavy job per machine:
```
git pull --rebase origin <branch>                                                  # the code below, and the episode's frames
/opt/vc/bin/python pipeline/voice_clone/ms.py qc $W                                # re-judge every take (numbers by value), re-pick
/opt/vc/bin/python pipeline/voice_clone/ms.py fixstarts $W --max 3                 # new takes for stray syllables glued to the first word
/opt/vc/bin/python pipeline/voice_clone/ms.py numbers $W                           # must end "0 real DIFF"; listen to any DIFF line
/opt/vc/bin/python pipeline/voice_clone/ms.py assemble $W $W/voice                 # with the stray-sound trim; prints the trims
/opt/vc/bin/python pipeline/voice_clone/ms.py verify $W $W/voice                   # optional: re-hears the finished file line by line
cp $W/voice_timings.json videos/<slug>/timings.json                                # commit this file only
/opt/vc/bin/python pipeline/make_keys.py videos/<slug>                             # keys/ from full/ (never committed)
/opt/vc/bin/python pipeline/build_anime.py videos/<slug> videos/<slug>/keys $W/voice.mp3 <out>.mp4 --size 720
```
Then the trivia break (Episode 3 on; see the main README, "Chibi trivia break", and `videos/<slug>/trivia_break.json`):
```
/opt/vc/bin/python pipeline/trivia_voice.py videos/<slug> --out $W/trivia                     # the break's lines: Indio clone + Usman's designed voice, takes.json
/opt/vc/bin/python pipeline/trivia_break.py episode videos/<slug> --voice $W/trivia --video <out>.mp4 --out <final>.mp4   # spec, cut, render, splice, checks; look at the sheet and 4 frames it prints
```
The same by hand:
`pipeline/trivia_break.py render --spec ... --out break.mp4 --sheet sheet.jpg` (look at the sheet), then
`pipeline/trivia_break.py splice --video <out>.mp4 --brk break.mp4 --at <t> --out <final>.mp4`, where `<t>` is the end of
sentence `insert_after_sentence` in the NEW `timings.json` plus its pause (re-assembly moves times; do not reuse an old
`insert_time`). Check: duration, both streams, loudness about -16 LUFS / true peak under -1.5 dBTP, the break within 1.5 LU of the 10 s of
story either side (splice re-levels the break to the story and prints `level check`), the sheet and four frames.
Last, the page: `pipeline/episode_page/make_page.py videos/<slug> <final>.mp4 <scratchpad>/page` and ONE private publish
(4 files). Audio, video and keys never go into the repository.

## Limits
- It measures clarity and similarity, NOT naturalness: a take can pass every check and still sound flat, oddly
  stressed or not like Indio's attitude. **The user's ear is the final check**; send the user a short test before a full
  episode and never call a voice final without their verdict.
- Whisper and the aligner are not perfect in Tagalog/Taglish (the real recording itself only reaches match 0.90).
- Tone comes from the prompt clip; a tone the real recording never uses has no good prompt (falls back to `narrate`).
- Slow on CPU: a 50-sentence episode with retries is several hours. Do not run two heavy jobs on one machine.
