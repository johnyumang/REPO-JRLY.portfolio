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

## What the owning machine does with a report
In the final pass, the machine that holds an episode reads audit/stills/epNN.json, looks at each must_fix still itself at full size, redraws the ones it agrees with (no writing, no panels, one moment), and for each one it rejects adds "rejected": "reason" to that entry. Minor entries are fixed only when cheap.
