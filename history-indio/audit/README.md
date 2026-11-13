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
