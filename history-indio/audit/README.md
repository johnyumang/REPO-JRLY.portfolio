# Cross-check of stills (before the final pass)

CROSS-CHECK OF STILLS before the final pass. All 50 episodes are built, and every episode will be republished once more (fixes plus the trivia break), so this is the moment to catch bad stills. You audit ANOTHER machine's episodes, with fresh eyes: the episodes named in the message you received. This is a text report only: do not redraw, do not rebuild, do not change those episodes' files.

HOW. git pull first. For each episode (folder history-indio/videos/epNN-*): key_prompts.json maps every shot to its still ("shots" gives the full / plate / char names; the files are in full/, plates/ and chars/). Make contact sheets of at most 6 stills per sheet, each still at least 480 px wide with its file name printed under it (your own small script; write the sheets to your scratchpad, not the repository), and LOOK at every still that a shot uses. Before you report a still, open it at full size; if it is fine at full size, drop it.

REPORT THESE (must_fix = a viewer on a phone would notice within about 3 seconds; otherwise minor):
1. writing: letters, words, numbers, pseudo-text or rows of glyphs anywhere (signs, books, papers, screens, plaques, maps, clothes), unless the script needs that exact readable text and it is right. A blank surface is right.
2. panels: comic panels, a collage, a split screen, a frame inside the frame, a border.
3. logo: a logo, watermark, signature or app / user-interface element drawn into the picture.
4. anatomy: extra or missing limbs or fingers that jump out, a face on an object, a character drawn twice where the script has one.
5. flag: a wrong Philippine flag (right is: a white triangle at the hoist with a sun and three stars, a blue stripe above a red one), or another nation's flag where it does not belong.
6. place: Japanese, Chinese or Korean signage, shrines, torii or cherry blossom in a Philippine scene.
7. off_model: Indio (small topknot; period outfit = red headband, off-white collarless shirt, bronze medallion; modern outfit = orange windbreaker over a white polo, medallion) or Usman (black street dog, white chest patch, one folded ear, red kerchief) clearly wrong.
Do not report taste, style or slight softness. An empty list is a good result: do not invent defects.

WRITE one file per episode, history-indio/audit/stills/epNN.json:
{"episode": NN, "audited_by": "<your machine's nickname>", "stills_looked_at": N, "clean": true or false, "defects": [{"still": "full/name.jpg", "shots": [numbers], "type": "writing|panels|logo|anatomy|flag|place|off_model", "must_fix": true or false, "what": "one sentence: what and where in the picture"}]}
Commit and push those files only (pull --rebase first; no model names in files or commits). Then ONE message to me: per episode, stills looked at, must-fix count, minor count, and the worst one in a sentence. Your own episodes' work folders, takes and MP4s stay untouched; publish nothing.

## What the owning machine does with a report (the stills fix)
The machine that holds an episode's work folder fixes that episode's stills:
1. `git pull`, then read `audit/stills/epNN.json`. Look at every `must_fix` still yourself at full size, with the script beside you. If you agree, redraw it; if you do not (the script needs that text and it is right, or it cannot be seen at phone size), add `"rejected": "reason"` to that entry. Minor entries: fix only when one try is enough.
2. Redraw the way the episode's stills were made (edit the prompt in `key_prompts.json`, then the still tool for that one still). What works: ONE moment per picture; add "Single image, no panels, no border, no black bars, the picture fills the whole vertical frame."; name the place ("a street in Tondo, Manila, Philippines"); for signs, papers, plaques, screens and books say "blank, no writing, no letters, no characters" and hide the text area with a hand, an angle or blur when it keeps coming back; never ask for "illegible scribbles"; say "Philippine street, no Asian-language signs" where shop signs appear; one of each character; Usman is a black short-haired street dog with a white chest patch, one folded ear and a red kerchief.
3. LOOK at every redraw at full size before you keep it. A redraw that is worse than the original is thrown away and the entry gets `"rejected": "redraw was worse (n tries)"` after three tries.
4. Add `"fixed": true` to each fixed entry, commit the stills, `key_prompts.json`, the sheet and the json (pull --rebase first), and recomposite the keys of the changed shots.
5. Rebuild only when the conductor's message says so (Season 1 rebuilds at once; the other seasons rebuild once, in the final pass, together with the voice fixes and the trivia break). Nothing is published until the conductor says so.

## Picture quality pass (the owner's word on 13 November: "Ang dami kong nakikitang AI slop, extra fingers ... dapat high quality")
The first cross-check hunted writing. This pass hunts what makes a picture look machine-made. The bar is higher: a fault counts when a viewer who PAUSES the video would see it, not only when it jumps out in three seconds.

**Look at** every key (the finished frame of every shot, `keys/kNN.png`) at full size, and every hand, face and held object again at 3x. Report in `audit/slop/epNN.json`:
1. `hands`: count the fingers of every visible hand (a thumb and four fingers). Extra, missing, fused or boneless fingers; two thumbs; a hand that melts into what it holds or into another person; a hand growing from the wrong place.
2. `limbs`: an extra or missing arm or leg, a limb bent the wrong way, a foot or shoe that is a blob.
3. `face`: eyes that do not match, a broken mouth or teeth, a second face, features sliding off.
4. `merge`: two bodies, or a body and an object, grown together (a mother's arm that becomes the child's, hair that becomes a hat).
5. `bleed`: a pattern or colour on the wrong surface (a dress print on a bare arm, a tattoo that is cloth).
6. `object`: a thing that could not exist or work (a trumpet with two bells, a spoon that is a finger, a door in the sky, a chair with five legs).
7. `off_model`: Indio, Usman, M or a named character who would not be recognised as the same person or dog as in the episode's other shots (face shape, hair, skin tone, build, outfit of that scene). Usman: a slim black short-haired street dog, white chest patch, ONE folded ear, red kerchief.
8. `style`: a still drawn in another style than the episode (a painterly poster, a manga page, a 3D render) so that the cut to it jolts.
9. `duplicate`: the same person twice in one picture where the script has one.
10. `writing`: as before (any letter-like mark), if one was missed.
Each entry: `{"key": "k07", "shots": [7], "still": "chars/lola_thumb.jpg", "type": "...", "must_fix": true|false, "what": "one plain sentence", "where": "which hand / corner"}`. `must_fix` = seen on a paused phone screen. An empty list is a good result; do not invent faults, and do not report taste.

**Fix**, cheapest clean way first:
1. *Reframe.* If the fault is at the edge, change the shot's crop in `key_prompts.json` (`x`, `y`, `s`) so it is out of the frame, when the picture still tells its moment.
2. *Redraw without the risk.* Most hands need not be seen: "hands at his sides, out of frame", "hands behind her back", "arms crossed, hands tucked under the arms", "holding it with both hands hidden behind the object". Say the count when a hand must show: "one hand, a thumb and four fingers, holding ...". One moment, one or two people, no crowd close to the camera.
3. *Redraw and choose.* With the backup engine draw up to four pictures (new seed each time, one call at a time) and keep one only if every hand, face and object passes at 3x. Paste the character strings from `characters/series_cast.json` word for word.
   - **Draw at full quality.** Most of the old slop came from the 4-step model. `make_keys.py --redo NAME` now draws with `flux-3-image-klein` at 30 steps, guidance 4 and a negative prompt (extra, fused or missing fingers, extra limbs, duplicate people, distorted faces, text, panels) by itself; `pipeline/flux_hq.py` does the same for a single picture outside an episode. If the log says "drawn by the 4-step fallback model", treat that picture as a draft and redo it when the better model answers.
   - It is still a machine: one close-up in the first tests grew two hands nobody asked for. Look at every picture.
4. *Hand it to the conductor* when four tries fail or the shot is a close-up the story hangs on: add `"needs_figma": true` and `"figma_prompt": "..."` (the full prompt you would use). The conductor draws those with the better engine when its daily credits return, most important shots first.
A redraw that is not clearly better is thrown away. Keep the old file beside your work until the episode is rebuilt. Mark `"fixed": true`, recomposite the changed keys, commit stills, `key_prompts.json` and the json; rebuild when the conductor says so.

### Character lint: run it before you redraw (80 of the first 172 must-fix faults were off-model characters)
An off-model Indio, Usman or M comes from the prompt, not from bad luck: each episode described them in its own words, and `nv_replace` rewrote even the pasted cast strings before sending. Redrawing from such a prompt draws the same fault again.
1. **Before any redraw of an episode:** `python3 pipeline/cast_lint.py videos/epNN-slug` (no argument = all episodes, `--json` for a machine). Exit 0 = clean; exit 1 = something is listed. Per prompt it names every character mention that is not the string in `characters/series_cast.json` (NEAR other words, MISSING a constant such as the topknot, medallion, tattoos, chest patch, folded ear, kerchief, WRONG contradicts the cast such as "ears up", a headband in a present-day scene or the wrong tattoo count), the "he is alone, no dog, no animals" clause of present-day prompts (only "no dog" when the shot has another animal or a creature), characters in plates, `nv_replace` entries that rewrite cast strings, and every prompt over 800 characters as make_keys sends it. Exit 2 = it could not run (bad arguments, a broken cast file, an unreadable episode file; the other episodes are still listed), so a gate can tell a broken file from drift.
2. **If it finds drift:** `python3 pipeline/cast_fix.py --ep videos/epNN-slug` (a dry run: read every before/after), then the same with `--write`. The cast string replaces the article and head noun ("a lean young Filipino man"); after it, a phrase is dropped only if every word in it is one the cast string now covers (hair, skin, the episode's clothes, headband, medallion, tattoos, handkerchief, chest patch, ears, kerchief, M's coat). The first phrase with any other word (a place, action, expression or prop: "on a yacht deck", "grips his hand", "with eyes closed") ends the description and stays, with everything after it; a prompt that would still lose a non-description word, or that describes the character again after the scene words, is left alone. One string per character per prompt: "Indio pointing" after his description stays a name. It picks the right Indio string (the episode's era outfit, saved in `indio_outfits` or built from `indio_era_template` with the clothes the episode already names and N-1 tattoos up to ep06; the present-day string; `indio_s5` from ep42; the schoolboy in Episode 10), adds the missing clause, removes the `nv_replace` entries that only shorten a cast string or that no prompt uses, and if a prompt then passes 800 it trims scene filler only (anti-text words END already says, not in the ep01 flat layout; decorative adjectives; "detailed background"; the long single-image line; never the style line). Files are re-read right before writing and written atomically; pull first, commit `key_prompts.json` right after. `--save-outfit` also saves the built era outfits into the shared `series_cast.json` (written first, atomically): do that as its own reviewed step.
3. **What it leaves for you** (listed under LEFT ALONE, and by the lint as NOCANON, UNSURE, STORY, DOUBLE, SECOND, NV_STORY, LENGTH, PLATE_PERSON): Indio at an age or in an outfit the cast file has no string for (ep32-ep41, a suit, a barong: add the string to the cast file first), a man or dog it cannot be sure is Indio or Usman, a deliberate "no tattoos" / "bare neck", an episode that draws Indio with a bare neck anywhere (prompts or `nv_replace`: M took the medallion in ep06; once decided, `--wear-medallion`), M in a shot where she holds something else, has her own umbrella, era clothes or the crescent medallion, a second description of the same character, a prompt that will not fit 800 even with its scene trimmed (shorten the scene by hand), and a person in a plate. Run `cast_lint` again after `cast_fix`.
4. **Then redraw:** a changed prompt only takes effect when its still is drawn again. `audit/slop/_character_drift.json` lists, per episode, the stills whose prompt (as make_keys sends it) changed in the 13 Nov pass; redraw those and nothing else for this reason.

### Usman's ears (13 Nov)
The cast string's "one folded ear" alone often draws two upright or two folded ears. When a still with Usman is redrawn,
add the sentence `usman_ears_clause` of `characters/series_cast.json` right after the usman string: "The dog's left ear
stands upright and pointed, only the dog's right ear is folded down; the dog's face is all black with no white on it,
the white patch is only on the dog's chest." Every part must name THE DOG: the first wording ("his face is all black")
painted Indio's face black when he stood close to the dog (Episode 35), and one draw put the dog's head on his body.
After any redraw with Usman, look at every human face at 3x. Do not redraw a still only for which ear is folded:
redraw when both ears are up, both are folded, or the face has white on it.

### The many-draws way (13 Nov): for a still that failed its redraws
A still marked `needs_figma` after four tries is not hopeless on the free model. On 13 Nov this closed 12 of 15 such stills:
1. **Describe each character from the episode's KEPT stills**, not from memory or only from the cast file: skin tone, hair,
   clothes, the drawing style of the face. Open two or three kept stills first.
2. **Take the risky thing out of the picture** while it still tells its moment: hands in pockets or out of frame, one hand on
   the sword instead of two, figures seen from the side or from behind, the dog apart from the people, one action only.
3. **Draw six at a time** with `pipeline/draw_pick.py`, look at the sheet, then at the best two or three at full size and at
   3x on every hand, face and the dog. A candidate with any countable fault is out. If none is clean, change the WORDS, not
   only the seeds; at most three rounds.
4. **Put the clean one beside the kept stills** of the same characters. A clean picture of a different-looking person is not a fix.
5. **A second reader who did not draw it** compares old and new and may put the old one back (`judge_note` in the audit entry).
A character drawn for the green key must have no green on it. A map, a flag or a count of lights is drawn in code
(`pipeline/ph_map.py`; the eight-ray sun of Episode 36), never by the image model.

## The Bakunawa look for a whole episode (pilot: Episode 2, 13 Nov)
The owner on 13 November: the pictures of the Bakunawa reel are the quality he wants ("Use the same Quality Graphics, I think
there is a roll back"). That reel was one FULL painted picture per shot (`pipeline/flux_hq.py`: dark-fantasy key visual, ink
line, hard shadows, rim light, deep painted background). The 50 episodes drifted to a flatter look (a character cut out on a
blurred plate). The pilot redrew all 37 keys of Episode 2 as full painted scenes; nothing else of the episode changed (same
narration, timings, shots_fx, subtitles). How it was done, so any machine can do the same for its episode:

1. **Plan before drawing** (one file, `plan.json`, outside the repo): fixed CAST strings (one per character and period, written
   from the episode's kept stills and `characters/series_cast.json`; Usman's string ends with the ears sentence word for word),
   fixed PLACE strings, and for every key: the lines it is shown under, `subject` (framing first, then the cast string, then
   the action), `setting` (the place string), `light`, and a hand note. Draw one ANCHOR per main character first and look at it.
2. **Draw**: `pipeline/draw_pick.py <dir> <p.json> <seeds> "<negative>"` with a JSON prompt `{"subject","setting","light"}`
   (that form uses the flux_hq look). Three draws a key, the choice at 3x, new words when none is clean. Hands hidden or resting.
3. **Put them in**: the kept picture is `videos/<slug>/full/bk_<NN>.jpg`; in `key_prompts.json` the old `shots` are copied to
   `shots_before_bakunawa` and every shot becomes `{"full": "bk_<NN>"}`; delete the old `keys/k*.png` and `keys/depth`, run
   `make_keys.py`. `shots_fx.json` is not touched.
4. **Two judges who did not draw** (one: characters, period and continuity from picture to picture; one: machine faults,
   framing against the subtitle band at about 63% of the height, and pictures that fall out of the look), then a fixer.
   Hand the fixer the judges' list as a FILE: in the pilot the list was passed inline and was cut off, so one key was missed.
5. **Build and check** as always (loudness, every frame decodes, a frames sheet that is LOOKED at, v3 beside v4).

What the pilot taught:
- A picture falls out of the look (flat cel, even light) mostly when the `light` is weak. Write the light as a scene ("hard
  orange firelight from the burning city behind him, deep shadows on half his face, rim light, smoke, embers") and add
  "richly painted, detailed ink linework, textured brushwork"; negative: "flat cel shading, flat even lighting, cartoon, tv
  animation, thick even outlines, poster, clip art".
- The subject belongs in the UPPER half ("in the upper half of the picture ... the lower half is only dark stones"): the
  subtitles cross about 63%.
- Seen from behind, the model hangs the medallion on his back: write "only the cord at the back of his neck, the medallion not
  visible", or turn him three-quarter with the medallion on his chest.
- Crossed arms beside the dog drew a third hand: arms at his sides with the hands below the frame, the dog a body-width apart.
- Period words must be spelled out and repeated in the negative (a tricorne became a Napoleonic bicorne; a 1762 shore got a
  modern skyline: "beyond the walls only palm groves, nipa huts and low tiled roofs of 1762, no modern buildings").
- Small things must be given a size ("each coin the size of a fingertip").
- The service refuses some proper names (a bastion's name was refused in every draw): describe the place without the name.
- Cost: about 70 minutes on one machine for 37 keys with four drawers, the two judges, 13 redraws and the build.
