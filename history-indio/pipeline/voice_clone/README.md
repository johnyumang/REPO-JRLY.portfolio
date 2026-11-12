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

## Limits
- It measures clarity and similarity, NOT naturalness: a take can pass every check and still sound flat, oddly
  stressed or not like Indio's attitude. **The user's ear is the final check**; send the user a short test before a full
  episode and never call a voice final without their verdict.
- Whisper and the aligner are not perfect in Tagalog/Taglish (the real recording itself only reaches match 0.90).
- Tone comes from the prompt clip; a tone the real recording never uses has no good prompt (falls back to `narrate`).
- Slow on CPU: a 50-sentence episode with retries is several hours. Do not run two heavy jobs on one machine.
