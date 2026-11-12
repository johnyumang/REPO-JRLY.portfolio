# History Indio — time-travel series template

Read with `HANDOFF.md` (series bible) and `README.md` (Anime workflow). Episode 1 (`videos/ep01-ang-unang-talon/`) is the worked example; copy its file set.

## Premise
Indio (full name José Indalecio Bracken, see Canon v2), a jobless young man from Quezon City, carries his Lolo's bronze medallion. When he reads a historical marker aloud while holding it, he jumps to that moment in history, and Usman (a talking aspin only Indio and animals understand) appears beside him. **Usman does not exist in the real world: he shows up only while Indio is time travelling and is gone when Indio returns (user, 2026-11-12).** Episode 3 is Indio's back story and Episode 4 is Usman's. They only witness; they never change events. Usman appears only when Indio jumps and stays in the past: he comes out of the light at the moment of the jump and is gone when Indio returns to the present. Why is the mystery answered in Episode 4 (Usman's back story). Each jump leaves one new tattoo on Indio. Exception from Episode 6: while Indio is stranded in the past without the medallion, Usman stays with him (he is still never in the present day).

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
- Indio, Usman, the medallion, the woman, Indio's family, the gamit and the medallion datus are fiction. Every episode's captions and pinned comment say: "Kathang-isip sina Indio at Usman; totoo ang kasaysayan."
- Indio never talks to, touches or influences a real historical person. Animals Usman talks to give jokes, never facts.
- The love interest is fictional (a second time traveller), never a real historical person.
- No invented quotes from real people. At least two dated sources per claim in `facts.md`.
- One approved exception (user, 2026-11-12): the soul of a real datu inside a medallion may speak invented lines. Always labelled fiction in the fairness beat, captions and pinned comment, with that datu's real record stated beside it. No other real person ever gets invented words, thoughts or actions.

## Pictures
Build every keyframe prompt from `characters/series_cast.json` (style block, character strings verbatim, end line). Write `key_prompts.json` first, then generate. About 34 new frames per episode; reuse frames for the rest with "key"/"keys" in `shots_fx.json`. Sentence 0 is a cold open on the three most dramatic frames. Put the end-card line in `videos/<slug>/endcard.txt`.

## Season arc
- Episodes 1–4: Indio learns the rules; Usman's two powers; the woman appears at the edge of each jump.
- Mid-season twist: Indio learns he is descended from José Rizal (fiction; see HANDOFF.md for how to handle it honestly) and that Usman was Rizal's dog.
- Late season: who the woman is, why their timelines run out of step, and what the Lolo knew.
- Arc of Indio himself: from "walang trabaho, walang tiwala sa sarili" to someone with a mission.

## Chapter structure (director's plan, 2026-11-12; the user asked Claude to sequence)
One chapter (season) = 8 episodes of about 3 minutes = about 24 minutes, the length of one TV anime episode. It follows the film "eight sequences" model: each episode is one sequence of the chapter's story.
1. Ep 1 — ordinary world + the first jump (Pugad Lawin 1896)
2. Ep 2 — learning the rules; M appears (British sa Maynila 1762)
3. Ep 3 — Indio's back story from his Lola (Kawit, 12 June 1898)
4. Ep 4 — midpoint: who Usman is (Calamba 1869)
5. Ep 5 — things get harder; M closes in (Treaty of Paris, Dec 1898)
6. Ep 6 — the low point: M steals the medallion; she had been luring him
7. Ep 7 — Indio without the medallion, chasing M
8. Ep 8 — climax and a cliffhanger into Chapter 2
Inside every episode: 8 beats of about 20 seconds and about 6 shots each (roughly 44–48 shots): hook; intro + present-day problem; the push to the marker; the jump and Usman; the event; the twist; the fairness beat; return + cliffhanger + question/follow.
Chapter 2 opens with Ep 9: the time of Jesus (user decision 2026-11-12, "maybe 9"; biblically accurate; see HANDOFF.md).

## Episodes 6–8 (Claude's plan as director, 2026-11-12; decided under the user's standing rule "wag na akong hintayin"; the user may change it)
- **Ep 6 (written, `videos/ep06-ang-huling-umaga`):** M finally asks to meet at Rizal Park at 6 am; the marker on the execution spot sends Indio to Bagumbayan, 30 December 1896. M stands beside him for the first time. At the volley she takes the medallion and vanishes, leaving a note: "Hindi sa'yo ang medalyon. Ibabalik ko lang sa pinanggalingan." Indio cannot return: no new tattoo, and for the first time Usman does not vanish. Shape: arrival = a date he dressed up for; connection = the person he trusts; twist = he was watching the wrong thing.
- **Ep 7 (written, `videos/ep07-ang-sulat-ni-lolo`):** the Lolo's back story. Stranded at Bagumbayan, no medallion, phone at 9%, one unopened photo from the Lola: the Lolo's letter, found under the lining of the Episode 3 box. Usman follows the guards to Paco (Rizal's secret burial, Narcisa's search, the RPJ marker, exhumation August 1898; today Paco Park). The letter names him José Indalecio, says the Lolo also made five jumps and refused M on this same morning, and points to a buried lens (first gamit). Hints only: the Lolo talking to the medallion and something answering; the bedtime story of twelve datus asleep in bronze and "ang Huling Tala". Ends: wait for M in Kawit on 12 June 1898; "hindi ang medalyon ang hinahanap nila, apo. Ang Huling Tala." No new tattoo.
- **Ep 8 (finale, planned):** the loop closes. M is the woman who carried the toddler wearing the medallion in Kawit in 1898 (Episode 3): she did not steal the medallion, she delivered it to the child Indio descends from, so that one day it would reach Indio. Fiction, labelled, with the real record of the Rizal–Bracken son stated beside it. Cliffhanger: how Indio gets home leads into Chapter 2.
- Threads: the empty box (Ep 3) and the Lolo's letter (Ep 4) are paid off in Episode 7. Still open for Episode 8: the five raised fingers (Ep 5), M at Kawit, and how Indio gets home.
- Decided by Claude under the standing rule (the user may change it); Episode 8 recommendations are in the HANDOFF.md line of 2026-11-12 (story worker).

## Canon v2 (user, 2026-11-12)
Overrides anything above that contradicts it. One season = one chapter of 8 episodes.
1. **Indio's name:** José Indalecio Bracken. "Indio" comes from Indalecio, and echoes "Indios Bravos", the name Rizal's circle in Paris took during the 1889 Exposition (inspired by the Wild West show; documented by José Alejandrino's memoir and a 22 September 1889 collective letter; Rizal's own surviving letters do not name it). The name is the conductor's proposal on the user's instruction (surname Bracken, contains José, "Indio" tied to the real name): **proposed, user may rename**. Fiction, always with the real record beside it: the son of Rizal and Josephine Bracken was born prematurely in Dapitan and did not survive; Rizal has no known descendants. The audience learns the name in Episode 7 (the Lolo's letter).
2. **Mga gamit:** besides the medallion, Indio collects things along the way. Each can be used inside a scene to see the truth of that moment ("deep dive", like a game item), and works even without the medallion. Each gamit has one clear power and one limit. First gamit (Episode 7): **ang lente**, an old golden-rimmed lens the Lolo buried at the foot of the Paco wall. Power: looked through, a place shows what truly happened there, days passing in moments; what is only legend stays blurred. Limit: it shows, it never lets him act. It is also how he can follow M without the medallion.
3. **The great mystery, "Ang Huling Tala"** (proposed name; tala = star and written record): mentioned through the series, never explained when mentioned. At the end of Season 1 it turns out to be a medallion and a kasulatan. That medallion grants three wishes. The kasulatan is a map that opens Season 2.
4. **Season 2** is more openly fiction: a hunt across Asia for the twelve medallions, each with its own attribute and power.
5. **The medallion datus:** every medallion carries the soul of a datu who really existed in Philippine history; the datu has a power and speaks (an anting-anting, the local counterpart of a genie). Rule change approved by the user: the datu souls may speak invented lines, always labelled fiction in the fairness beat, captions and pinned comment, with the real record of that datu stated beside it. No other real person ever gets invented words, thoughts or actions.
6. **Episode 7** is the Lolo's back story and only HINTS at 3–5 (the Lolo talking to the medallion and something answering; his bedtime story of twelve datus asleep in bronze and "ang Huling Tala").
7. **A Season 1 trailer** comes before launch (`videos/trailer-season1/`, produced by others).
8. **Standing rule (user, 2026-11-12, "tuloy-tuloy na sa paggawa, wag na akong hintayin sa lahat"):** stories, names, frames, voice and music are decided and done, then reported so the user can change them. Stop only for spending money, secrets and posting to the user's public accounts.

