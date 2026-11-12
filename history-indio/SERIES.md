# History Indio — time-travel series template

Read with `HANDOFF.md` (series bible) and `README.md` (Anime workflow). Episode 1 (`videos/ep01-ang-unang-talon/`) is the worked example; copy its file set.

## Premise
Indio, a jobless young man from Quezon City, carries his Lolo's bronze medallion. When he reads a historical marker aloud while holding it, he jumps to that moment in history, and Usman (a talking aspin only Indio and animals understand) appears beside him. **Usman does not exist in the real world: he shows up only while Indio is time travelling and is gone when Indio returns (user, 2026-11-12).** Episode 3 is Usman's back story. They only witness; they never change events. Usman appears only when Indio jumps and stays in the past: he comes out of the light at the moment of the jump and is gone when Indio returns to the present. Why is the mystery answered in Episode 3 (Usman's backstory, prepared by the user's team). Each jump leaves one new tattoo on Indio.

## Episode skeleton (330–380 spoken words, one narrator voice: Indio, first person)
1. **Hook (sentence 1):** the most dramatic moment of the jump, stated as something Indio is seeing.
2. **Intro (fixed):** "Ako 'to si Indio. Samahan mo akong mag-time travel, at tuklasin ang history natin."
3. **Modern-day beat (3–6 sentences):** Indio's real life moves forward one small step (job hunt, money, family, the mystery woman) and leads him to a real marker or historical site. Name the real place.
4. **The jump (2–4 sentences):** medallion heats up; the agimat changes his clothes; Usman says one short line (spoken by Indio as narrator).
5. **What he witnesses (10–14 sentences):** the event, told as an eyewitness. Only claims that are in `facts.md`.
6. **Fairness beat (3–5 sentences):** Usman growls when a story is uncertain; Indio says what is certain, what is disputed, what is legend.
7. **Return + character beat (3–5 sentences):** back to the present; new tattoo; one step in Indio's arc or the love-story mystery; a small cliffhanger.
8. **Closing question** for the comments, then the follow line: "At mag-follow na kayo, guys, para sa dagdag lakas namin ni Usman sa susunod na talon!"

## Indio's voice (user direction, 2026-11-12)
Cool and calm, like a quiet anime lead who starts weak and levels up: short sentences, understatement, dry humour, no shouting, no girl-talk slang ("te", "mhie"), with "young stunna" street slang used sparingly, about one word per two or three sentences (par, tol, repapips, olats, goods, chill lang, sheesh, lupet, angas, no cap, dehins, werpa). Keep the history lines and the fairness beat free of slang. He gets visibly more capable each episode (one tattoo per jump is his "level"). Inspiration is the vibe only; never copy another series' character, lines or look.

## Honesty rules
- Indio, Usman, the medallion, the woman and Indio's family are fiction. Every episode's captions and pinned comment say: "Kathang-isip sina Indio at Usman; totoo ang kasaysayan."
- Indio never talks to, touches or influences a real historical person. Animals Usman talks to give jokes, never facts.
- The love interest is fictional (a second time traveller), never a real historical person.
- No invented quotes from real people. At least two dated sources per claim in `facts.md`.

## Pictures
Build every keyframe prompt from `characters/series_cast.json` (style block, character strings verbatim, end line). Write `key_prompts.json` first, then generate. About 34 new frames per episode; reuse frames for the rest with "key"/"keys" in `shots_fx.json`. Sentence 0 is a cold open on the three most dramatic frames. Put the end-card line in `videos/<slug>/endcard.txt`.

## Season arc
- Episodes 1–4: Indio learns the rules; Usman's two powers; the woman appears at the edge of each jump.
- Mid-season twist: Indio learns he is descended from José Rizal (fiction; see HANDOFF.md for how to handle it honestly) and that Usman was Rizal's dog.
- Late season: who the woman is, why their timelines run out of step, and what the Lolo knew.
- Arc of Indio himself: from "walang trabaho, walang tiwala sa sarili" to someone with a mission.
