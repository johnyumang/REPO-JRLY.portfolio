<!-- Part of the /indio bundle. Run as: /indio kaizen [what just finished] -->
# Kaizen: one small improvement after every piece of work

Kaizen = change for the better, in small steps, every time, by the people doing the work. Never a big redesign.

## When
After each finished unit (an episode's files, a delivered MP4, a frame upgrade) and after every user correction.
Takes five minutes at most. Skip nothing; if there is no waste to fix, write "none" and stop.

## Steps (PDCA: plan, do, check, act)
1. **Check (go and see).** Look at what actually happened, not what was planned: which step took longest, what was
   redone, what the user corrected, what was asked that was already written down, which frames were rejected.
2. **Name one waste.** Pick the single biggest from: rework, waiting, repeated reading or research, unused output
   (files nobody needed), unnecessary questions to the user, spent credits that were thrown away, defects reaching
   the user.
3. **Ask why (up to five times)** until the cause is something in the workflow, not a one-off.
4. **Act: one small fix, now.** In order of preference: delete a step; fix the wording of a rule in
   `.claude/skills/indio/SKILL.md`; add a line to `HANDOFF.md`; add a word to `pipeline/respell.json` or a string to
   `characters/series_cast.json`; change a script default. Write a new script only for a step done by hand twice.
5. **Standardise.** Add one line to `history-indio/KAIZEN.md`: date, waste, cause, fix, where the fix lives.
   Commit and push with the work.
6. **Next time, check that the fix held.** If the same waste shows up again, the fix was wrong: replace it.

## Rules
- One improvement per run. Small and finished beats large and planned.
- Fix the process, never blame. A user correction is the best input: record it the same turn.
- Never loosen the fixed rules in the parent skill (`SKILL.md`) (honesty labels, no paid APIs, no secrets, no committed MP4s or
  voice files, the user's own voice only).
- Tell the user the improvement in one Taglish sentence.
