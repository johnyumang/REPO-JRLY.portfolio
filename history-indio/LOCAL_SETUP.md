# Running this exact setup on your own computer (free)

This file is written so you can hand it, with the repository, to a local model or agent and say: "make the next
episode the same way as `videos/ep01v2-ang-unang-talon`". Everything it needs is in this repository except three
things that are yours and are never committed: your Episode 1 voice recording, the finished audio/video, and keys.

## What is free and what you must bring
| Part | Tool | Cost | Runs where |
|---|---|---|---|
| Story and script | any local model, following `story/` | free | your computer |
| Voices (Indio clone + designed cast) | VoxCPM2, `pipeline/voice_clone/` | free | your computer, CPU is enough (about 1-2 min per sentence) |
| Pictures | `pipeline/flux_hq.py` on NVIDIA's free endpoint | free tier, rate-limited | NVIDIA's servers; needs your own free key |
| Writing on signs, baybayin | `pipeline/sign_text.py`, `pipeline/baybayin.py` | free | your computer |
| Sound effects and music bed | `pipeline/sound_design.py` (made in code) | free | your computer |
| Subtitles, camera moves, final MP4 | `pipeline/build_anime.py`, ffmpeg | free | your computer |

- The picture key: make a free account at build.nvidia.com, create an API key, and set it only as an environment
  variable: `export NVIDIA_API_KEY=...`. Never write it into a file in this repository.
- Your voice recording: set `export HI_VOICE_REC=/path/to/your_episode1_recording.mp3`.

## Machine
Linux, or Windows with WSL2 (the scripts use `/opt/vc`, `/opt/vx`, `/opt/work`). 16 GB RAM, about 20 GB of disk,
python 3.10+, ffmpeg, node 22+. No graphics card is needed.

## One-time setup
```
git clone https://github.com/johnyumang/REPO-JRLY.portfolio && cd REPO-JRLY.portfolio/history-indio
bash pipeline/setup.sh
bash pipeline/voice_clone/setup_vox.sh
/opt/vc/bin/python pipeline/voice_clone/baseline.py videos/ep01-ang-unang-talon   # measures your recording once
```

## What the local model must read first, in this order
1. `story/CONSISTENCY.md` — the rules that never change (looks, names, the villains' sign, hero quotes, tender moments).
2. `story/BIBLE.md` and `story/REWRITE_PLAN.md` — the whole story and what each episode must do.
3. `story/ep01_v2/` and `videos/ep01v2-ang-unang-talon/` — the finished model episode: `script_multispeaker.txt`,
   `shots.md`, `key_prompts.json`, `shots_fx.json`, `sound.json`, `facts.md`, `trivia_break.json`, `endcard.txt`.
4. `audit/README.md` — how the pictures are drawn and checked (the Bakunawa look, many draws, Usman's ears,
   writing inside a picture, the two rules that are not negotiable).
5. `pipeline/voice_clone/README.md` and `pipeline/SOUND.md`.

## One episode, step by step
1. **Script.** Write `videos/<slug>/script_multispeaker.txt` in the same form as Episode 1 v2: `NAME: [tone] line`,
   stage lines in (parentheses), `INDIO (sa atin):` for asides, trivia lines at the very end. Write `facts.md`
   saying what is true and what is invented.
2. **Shots.** Write `shots.md` (one still per line or group of lines, no still used twice) and `key_prompts.json`
   (`subject`, `setting`, `light` per shot, with the character descriptions copied word for word).
3. **Voices.** New characters get a designed voice: add a description to `pipeline/voice_clone/cast_design.json`, then
   `castdesign.py` and `castqc.py`. Then:
   `HI_VOICE_REC=... bash pipeline/voice_clone/run_multispeaker.sh videos/<slug> <slug>`
   Copy the resulting `voice_timings.json` to `videos/<slug>/timings.json`.
4. **Pictures.** For each shot: `python pipeline/draw_pick.py <dir> <prompt.json> <seeds> "<negative>"`, three draws,
   choose the best at 3x zoom, redraw on any fault. One request at a time; wait and retry on 429 or 502.
5. **Writing.** Put real words on signs with `sign_text.py` / `baybayin.py`. Nothing blank, no scribble.
6. **Sound.** Write `videos/<slug>/sound.json` as in Episode 1 v2 (footsteps, crowd, rips, hush before a shout).
7. **Build.** `python pipeline/build_anime.py videos/<slug> videos/<slug>/keys <voice file> out.mp4 --size 720`
   (`endcard.txt` containing `NONE` = no follow card).
8. **Check before anyone sees it.** Every frame decodes; loudness -16 LUFS +/-0.5, true peak <= -1.5 dBTP; cut the
   video at 2.5 frames a second and look at every sheet; run the eight consistency checks below; listen to the
   whole thing once.

## The eight consistency checks (a fault means redraw or re-voice, not a note)
1. Indio: same face, hair, skin tone and medallion; the right clothes for the time he is in; no change inside a scene.
2. Usman: same black dog, same ears, red neckerchief; never in the present day before Episode 30.
3. Every named or speaking character: same face, age and clothes in every shot.
4. Place and time: light and weather continue across a scene.
5. Props: the same object looks the same each time; the villains' sign is always three slanted strokes.
6. Voices: one voice per character from first line to last; subtitle name tags match the speaker.
7. Words: names and spellings identical throughout.
8. No still used twice; a long line gets a second still, not a cut back into the same one.

## Honest limits
- A small local model writes weaker Tagalog and judges pictures poorly. The scripts and the rules carry over; the
  judgement does not. Keep a person on step 8.
- The free picture endpoint is slow and sometimes refuses a prompt (for example a child holding a blade); reword it.
- Real motion clips (the Wan test) used a free Hugging Face quota of about 6 clips a day; they are not part of this
  build and need a graphics card to run locally.
- Only clone your own voice. Every other voice is designed from a written description.
