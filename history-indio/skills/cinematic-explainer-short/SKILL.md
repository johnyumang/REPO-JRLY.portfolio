---
name: cinematic-explainer-short
description: Produce a vertical History Indio short (1080x1920, 30 fps) about Philippine history, myths and legends in the Pinoy Komiks look (halftone ink, newsprint, caption boxes), run as a small studio team (research, script, storyboard, look-dev, keyframes, motion, voice, sound, edit, QA). Also covers the alternative looks (anime, semi-realistic 3D explainer, feature-film 3D, painterly). Use this whenever the user asks for a History Indio video, a Philippine history or mythology explainer, a "komiks style" short, video ideas for the channel, or says the flat cartoon look is not good enough, even if they do not name this skill.
---

# History Indio short (Pinoy Komiks house style)

The channel's house look is Pinoy Komiks: halftone ink on newsprint, bold outlines and caption
boxes, like a page from an old Filipino comic. The default subject is Philippine history, myths and
legends. What makes it feel like a studio made it is everything around the picture: a tight
script, a storyboard, locked character sheets, and an edit timed to the voice. Run the stages below in order and keep a task
list so the user can see where the job is.

## Topics and ideas
When the user has no topic, offer 10 ideas mixed across pre-colonial, Spanish, American and wartime
eras plus myths and legends. For each: a title, the hook line, the twist, and whether it is
documented history, a disputed account, a debunked hoax, or folklore. Label these honestly in the
video too ("ayon sa alamat" for legends) — presenting a legend as fact is the fastest way to lose
a history audience. Prefer the dead and the mythical; they need no likeness caution.

## Two ways to make komiks frames
- **Render + filter (default, free, faces identical):** draw or render the shot with the project's
  own character engine, then run `python3 scripts/komiks_filter.py in.png out.png`. Because the
  characters are built from fixed parameters, every face matches its sheet exactly.
- **Generated keyframes:** use the `komiks` preset in `references/style-presets.md` with the
  character sheet attached as a reference. Richer drawing, costs credits, faces stay close rather
  than exact. Running the filter over generated frames as well gives all shots one shared texture.

## What this can and cannot do (tell the user up front)
- The real studios behind this look use Blender and a large animation team. This skill reaches a
  similar look with generated keyframes. It is not frame-perfect 3D animation.
- A generated character stays close across shots, not identical. Locking a reference sheet and
  anchoring every keyframe to it is what keeps drift small.
- Every generation spends the user's credits. Price it first (`estimate_only`) and get a yes before
  any batch of video clips. If generation is unavailable or too costly, use the motion-comic route
  in Stage 6 — stills with camera moves still read as a finished short.

## Real people and news
Explainers about current events name real people, so the look has to stay honest.
- Anime, painterly and stylised 3D are fine for real public figures because nobody mistakes them
  for footage. Add a name plate the first time each person appears.
- In the semi-realistic 3D look, do not render a recognisable realistic face of a real person, and
  never show them doing or saying something they did not do. Show them through hands, podiums,
  name plates, silhouettes and props, and keep realistic faces for fictional characters such as the
  host. A realistic fake of a real politician is misleading even inside a "cartoon" channel.
- Every claim in the script needs a source. Say "ayon sa [outlet]" for single-source details and
  mark allegations as allegations. No invented quotes.

## Stage 1 — Research desk
Search for the story, collect at least two dated sources per claim, and write `work/facts.md`:
claim, source link, date, and status (confirmed / single source / alleged / disputed). Anything not
in this file does not go in the script.

## Stage 2 — Script
Write narration only, about 2 words per second for Taglish (a 3-minute video is 330–380 words).
1. Hook in the first line: a paradox or a small object with big consequences. No greeting first.
2. Open loop: promise the answer, then delay it.
3. Escalation in 3–5 beats, each raising the stakes and each one drawable.
4. A fairness beat: what is proven, what is alleged, what is opinion.
5. Payoff and a question for the comments.
Save `work/script.txt` and a source table. Get the user's approval before generating anything.

## Stage 3 — Storyboard
One shot every 3–6 seconds. Write `work/shots.json` with, per shot: `id`, the narration line it
covers, `subject`, `action`, `camera` (push_in, pull_out, pan_left, pan_right, tilt_up, tilt_down,
hold), `shot_size`, and which characters appear. Vary shot sizes; open on the hook image; give the
payoff line its own shot. Prefer one clear subject per frame — generators and phone screens both
punish clutter.

## Stage 4 — Look-dev (style lock)
Read `references/style-presets.md`. Use `komiks` unless the user asks for another look. Generate one hero frame in
that style and show it. Do not go further until they approve the look.

Then build a reference sheet per recurring character (front, 3/4, side, a few expressions, plain
background) and save it under `characters/<name>/`. Reuse a saved sheet if one exists — a new sheet
means a new face. Wire the sheet in as a reference image for every keyframe that character is in,
using a model that holds a character across shots (see the presets file).

## Stage 5 — Keyframes
Generate one 9:16 keyframe per shot. Prompt = style block (identical for every shot) + subject +
action + camera + lighting. Keep the style block word-for-word the same; changing it mid-video is
the commonest cause of a look that drifts. Build a contact sheet, look at it yourself, and
regenerate any frame with wrong hands, stray text, or an off-model face before the user sees it.
Send the sheet to the user before spending on motion.

## Stage 6 — Motion
Two routes; choose by budget.
- **Image-to-video** (full look): animate each approved keyframe into a 4–6 s clip. Describe one
  motion per clip (a gesture, a camera move), never a list. Estimate the total first.
- **Motion comic** (free): `python3 scripts/motion_comic.py work/shots.json voice.mp3 out.mp4`
  animates stills with eased camera moves and hard cuts on the shot times. Mix routes freely —
  spend video credits on the hook and the payoff, use stills for the rest.

## Stage 7 — Voice, sound, edit
- Voice: the user's own recording, or their cloned voice if one is in their account. Never present
  a stock voice as theirs. The picture is cut to the voice; do not re-time the voice.
- Timing: align the script to the audio (word timestamps if a transcriber is available, otherwise
  silence detection) and set each shot's `start`/`end` in `shots.json`.
- Music and effects sit at half the voice level (−6 dB). One whoosh or hit per cut at most.
- Encode H.264 + AAC, 1080x1920, 30 fps.

## Stage 8 — QA and delivery
Check: duration matches the voice, no black or frozen stretches, no garbled text in frames, names
spelled right, every on-screen claim matches `facts.md`. Send the MP4 with a short list of what
could not be verified — sources not read in full, quotes not checked against a recording, shots
where the character drifted.
