---
name: indio
description: History Indio episode workflow in one page, run on two principles to save time and tokens - the Neocortex principle (one repeating unit, hierarchy, remember and predict) and the Elon Musk principle (the five-step algorithm - question, delete, simplify, accelerate, automate). Use for any History Indio task - writing an episode, building a video from an uploaded MP3, upgrading frames, or giving status. This is the FATHER skill: one bundle holding the principles, the episode workflow and Kaizen. Invoke as /indio [episode or task], or /indio kaizen.
---

# Indio: the History Indio workflow, the short way

Channel: History Indio. Tagalog/Taglish vertical shorts (1080x1920, 30 fps, about 3 minutes), anime look, time-travel
series with Indio and Usman. Work in `history-indio/` on branch `claude/eager-davinci-9qu2gg`. Repo is PUBLIC.

## What is in this bundle (everything lives under this one skill)
| Part | Where | Use |
|---|---|---|
| Neocortex principle | this file | how the work is organised |
| Elon Musk principle | this file | the order of attack on every task |
| Indio workflow | this file | rules, file set, commands, story shape |
| Kaizen | `kaizen.md` beside this file | one small improvement after every finished unit or user correction; log in `history-indio/KAIZEN.md` |
| Older helper skills | `history-indio/skills/cinematic-explainer-short`, `history-indio/skills/indio-voice`, `.claude/skills/anime-style` | read only when the task needs them (komiks look, fallback voice, Blender look) |
Do not create a separate skill for History Indio work: add a file or a section here.

## Principle 1: Neocortex (how the work is organised)
From Mountcastle's idea, popularised by Jeff Hawkins: the neocortex repeats ONE unit (the cortical column) everywhere,
stacks units in a hierarchy, and works by remembering patterns and predicting from them instead of computing from zero.
- **One repeating unit.** Every episode is the same unit: same ten files, same 8 beats, same commands. A new episode
  is a copy of the last one with the content changed. Never invent a new structure.
- **Hierarchy.** Series -> chapter (8 episodes) -> episode (8 beats) -> beat (about 6 shots) -> shot (plate +
  character). Decide at the highest level that settles the question; do not reopen a higher level from a lower one.
- **Memory before thinking.** The answer is usually already stored: `HANDOFF.md` (newest section wins), `SERIES.md`,
  `facts.md`, `characters/series_cast.json`, the previous episode. Read, reuse, then predict the next step from the
  pattern. Only what is surprising (a new decision, a failed step) needs fresh thought.
- **Learn from the error.** When the result differs from what was expected (user correction, bad frame, failed
  build), write the correction into memory at once (HANDOFF.md or this skill) so it is never paid for twice.
  Kaizen (below) does this.

## Principle 2: Elon Musk (the five-step algorithm, in this order on every task)
1. **Question the requirement.** Read only what the task needs: the last sections of `history-indio/HANDOFF.md`
   (newest wins), the "Chapter structure" in `SERIES.md`, and the previous episode's folder. Never re-derive what is
   written there. Ask the user only for decisions that are theirs (story approvals, voice, credits).
2. **Delete.** No planning documents, no long reports, no re-research of confirmed facts, no new frame when an old one
   fits (`"key"`/`"keys"` in `shots_fx.json`), no animation on every shot (3 to 5 key moments at most), no re-alignment
   when the recording is unchanged. Messages to the user: short, Taglish, result first.
3. **Simplify.** One episode = one folder with the same ten files (below). One background plate per location,
   characters on green, composited. Copy the previous episode's `key_prompts.json` blocks and character strings verbatim.
4. **Accelerate.** Run `bash pipeline/setup.sh` in the background at the start. Batch searches in one turn. Generate
   drafts with the free NVIDIA endpoint first; spend Figma credits only on the worst frames. Preview with
   `--size 720 --until N` before a full render.
5. **Automate last.** Use the scripts; do not hand-do what they do. Only add a script after a step has been done by
   hand twice.

## Fixed rules (do not break)
- No paid APIs. Never ask for secrets in chat. Never commit MP4s or voice files.
- The user records the voice in ElevenLabs and uploads the MP3. Never clone or imitate a voice.
- Indio, Usman, M, the medallion and Indio's family are fiction and are labelled so in every caption and pinned
  comment, next to the real record. Indio only witnesses. No invented words for real people.
- Usman exists only while Indio is time travelling.
- Every claim in a script has a row in `facts.md` (two sources, status), and a "could not verify" list.
- Tell the user before spending Figma credits (about 75 images a day, shared, resets 00:00 UTC).
- Tell the user when something is finished and send the file so it plays (SendUserFile, display render).

## Episode file set (`history-indio/videos/epNN-slug/`)
`script.txt` (330-390 words, tone tag per sentence, 8 beats) -> `sentences.json` (`pipeline/make_sentences.py`) ->
`script_elevenlabs.txt` (same sentences, v3 tags, years as spoken words) -> `facts.md` -> `captions.md` ->
`endcard.txt` -> `key_prompts.json` -> `shots_fx.json` -> `plates/ chars/ full/` -> `keyframes_sheet.jpg`.
`keys/` is git-ignored.

## Commands
```
bash history-indio/pipeline/setup.sh                                   # once per machine, background
P=/opt/vc/bin/python; cd history-indio
$P pipeline/make_keys.py videos/<slug>                                 # drafts + composites into keys/
$P pipeline/align_audio.py <voice.mp3> videos/<slug>/sentences.json videos/<slug>/timings.json
$P pipeline/build_anime.py videos/<slug> videos/<slug>/keys <voice.mp3> <out.mp4>   # add --size 720 --until N to preview
```
Deliver: contact sheet check, MP4 to the user, captions from `captions.md`, the "could not verify" list, tick
`topics.md`, add a dated section to `HANDOFF.md`, commit and push.

## Story shape (8 beats of about 20 s, about 6 shots each)
hook; intro line + present-day problem; push to a real marker; the jump and Usman; the event; the twist; the
fairness beat (certain / disputed / legend / fiction); return + cliffhanger + question + follow line.
Vary arrival, connection and twist from the previous two episodes. Indio's voice: cool, calm, short sentences,
slang about once per two or three sentences, none in history lines.

## Kaizen (always the last step)
After every finished unit or user correction, read `kaizen.md` in this folder and do it: name one waste, make one
small fix, add one line to `history-indio/KAIZEN.md`, tell the user in one sentence.
