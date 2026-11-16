# Brief for the writer of one Episode (version 2), batch 3 onward

You write ONE episode of "INDIO: ANG SAKSI" (Tagalog/Taglish, vertical animated short) as text only: no pictures,
no audio. Work only inside `history-indio/story/epNN_v2/` (create it). Do not commit or push. Do not touch any
other file. No model names in files.

## Read first (in this order; paths from `history-indio/`)
1. `story/BIBLE.md`: sections 0, 2, 3, 4, 5, 8, 9, the row of your episode AND the rows before and after it in
   section 10, section 12 (guard rails) and section 14 (rulings; they win over any row).
2. `story/CONSISTENCY.md`: sections 9 to 13 (the running lists of what Episodes 1 to 18 already used, and rules
   9, 10 and 11), and `story/_parts/REVISION_BATCH3.md` (section A is binding on you from the first draft:
   scenes with people talking, the storyteller at most half of the words; section B holds rulings on how he
   jumps, the lens, the lamp, the knots and where things are).
3. `pipeline/CAMERA.md` (the camera table).
4. The model of the form: `story/ep18_v2/` (all of `script_multispeaker.txt`, `facts.md`, `shots.md`) and the
   spoken lines of the episode just before yours, if its `story/epNN_v2/` exists. Match the layout exactly.
5. The old episode: `videos/epNN-*/script_multispeaker.txt` and `videos/epNN-*/facts.md`. The old `facts.md` holds
   the real history with its sources; keep what is sourced, and use the row of `story/REWRITE_PLAN.md` for your
   episode to see what the old script got wrong.
6. `story/_parts/derive.py` (you will run it).

## The rules (all binding)
1. **Hook.** At 0.0 a shout or a blow that is a flash-forward of the episode's worst moment, then one Indio aside
   that states the trouble, then "Ako 'to si Indio. ..." in one short line.
2. **His now.** The present-day part is under 40 seconds, and holds ONE everyday thing of today with its true
   origin and a joke, in Indio's voice. Your thing is assigned below; verify its origin with a web search (two
   sources if you can; if only one, or it is "commonly told", say "sabi nila" in the line and say so in facts.md).
   A real living person may be named at most once, kindly, never shown; better none.
3. **Hero line.** A significant real figure who appears speaks one iconic line on camera, only if attested or
   firmly traditional; facts.md says which. If it is a rendering, facts.md says so and the trivia must not call it
   a quote. If none exists, none.
4. A hero's wife or partner, if in the scene: one short tender moment between adults; invented parts marked in
   facts.md.
5. No scene, place or picture idea repeated from earlier episodes; `shots.md` opens with a "Must not resemble"
   paragraph naming what it avoids.
6. Trivia only at the END (a commented `# --- TRIVIA` block as in the model, up to 25 seconds). No follow card.
   No talk of "kathang-isip" inside the story.
7. Mark stress for hard words with `# SAY: word=respelling` (e.g. umungol = u-MU-ngol, cedula = SE-du-la).
8. **Length: 520 to 540 spoken words for the story** (derive.py prints the count; the builds showed that 590
   words runs over four minutes). Clear beats short, but stay in that band.
9. **Told like a storyteller.** Nothing the viewer needs may live only in a stage line. TAGAPAGSALAYSAY tells each
   action in a full, plain sentence in the third person: who does what, and why it matters. Stage lines in
   (parentheses) are picture notes only. One thread at a time; cut a side thread rather than leave it half told.
   Do not have the storyteller say what a character says in the very next line.
10. **Camera.** `shots.md` has the columns `# | Sent. | What we see | Camera`; Camera is
    `size / angle / move / reason (five words or fewer)` from CAMERA.md, with `; fx:`, `; dof:`, `; in:` only where
    its table allows; size and angle come first in "What we see"; exactly two or three rows start with
    `**HIGH POINT** ` and only they (plus one establishing `crane_down`) use orbit, crane or dolly; the size
    changes at every cut; a reveal says where it ends. **No shot is hands only or an object only with no person:
    every still shows a face or a body** (an insert of a paper or a medallion is held by someone we can see).
11. **Nobody arrives unintroduced.** Every person, animal, object or place that matters is introduced by
    TAGAPAGSALAYSAY at first sight, in one plain sentence saying who or what it is and why it is there, BEFORE it
    speaks or matters; a character is seen before it is heard. This includes M ("si M, ang babaeng may mapa ng mga
    medalyon") and Usman ("si Usman, ang aso niyang nagsasalita") every episode. Deliberate mysteries stay, but the
    storyteller says plainly that Indio does not know who it is. Every cause is said: why he is there, why they
    fear him, why they let him go.

## The shape
Third person scenes: a short storyteller line, picture notes in parentheses, then dialogue. No talking heads.
Indio does not know history: a FRIEND of that time shows him; he whispers today's sabi-sabi to us against what he
sees; he jokes. A want drives every scene. The episode has its own plot and twist: a FALL (he seems to have
lost, and it costs him), then a COMEBACK that comes from his own gift or an honest act (not from luck, and "he
confessed so it worked" is rationed: do not use it unless your bible row says so), then a small show-off, then the
cliffhanger of your bible row, then one spoken question to the viewer ("Ikaw, ka-Indio: ...").

## Guard rails (never broken)
- The real part is true and sourced: `facts.md` gives each real claim, the sentence it supports (`sN`), and its
  sources (two where possible), and marks every invented thing as invented.
- Invented words only for people long dead, and nothing that puts guilt or a false belief on them. Living people,
  parties, companies and churches are never given words or put in scandal. God is given no words; scripture is
  exact (book and verse, read by the storyteller) or marked "buod". A sacred rite (a Mass, a prayer) is seen from
  a distance, in silence, with no joke inside it. The real outcome of history stands.
- Usman is never in the present day before Episode 30. Marks, gifts, medallions, knots, the three wishes, the
  rival, the villains and what may be named when: exactly as BIBLE.md says (section 14 wins).
- No racist imagery; foreign peoples are people, not monsters. Creatures of folklore are named as their own
  cultures name them.

## What to write (in `story/epNN_v2/`)
- `script_multispeaker.txt`: the master, in the model's exact format (`# --- scene` headers, `(stage lines)`,
  `NAME: [tone] text`, `INDIO (sa atin):` for asides, tone tags of letters and spaces only, `# SAY:` lines, the
  commented trivia block at the end).
- Run `python3 story/_parts/derive.py story/epNN_v2 -v` from `history-indio/`; it writes `script.txt` and
  `sentences.json`. Fix until it passes and the story is 520 to 540 words.
- `facts.md` and `shots.md` in the model's layout, with sentence numbers that match `sentences.json`.
- Then read ONLY your spoken lines once as a stranger and fix anything unintroduced or unexplained.

## Dialogue first (the lesson of batch 3)
The first drafts of Episodes 13 to 18 had the storyteller at 54 to 65 percent of the words and were sent back.
Write yours so that derive.py shows TAGAPAGSALAYSAY at 45 percent or less; the fall and the comeback are
played in lines; the storyteller never runs more than three sentences without a character speaking; the friend
has at least six lines and Usman at least four in a jump. Introduce M, Usman and the lens in a short clause,
not the same long phrase every time.

## Report back (short)
Title; sentences and words; today-thing and how sure its origin is; the hook (words, picture, kind); the fall;
the comeback; the friend; gear, medallion, knot or mark gained or lost; hero line and its status; plants made
that later episodes must pay; anything you could not source or any rule you could not meet.
