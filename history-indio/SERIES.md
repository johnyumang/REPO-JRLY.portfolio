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
- **Ep 8 (finale, written, `videos/ep08-ang-huling-tala`; direction decided by the conductor 2026-11-12; the user may change it):** the loop closes at Kawit on 12 June 1898, seen "from the other side".
  - *The wait:* 529 days from 30 December 1896 (about a year and a half). Indio survives by working: the first job he ever kept (his arc: from jobless to someone with a mission). Usman stays.
  - *The history:* the same afternoon as Episode 3 but only NEW true facts (from `facts.md`: what the Acta says about American protection, the one American signer, who sewed the flag and the Rizal niece among them, Alapan, what became of the proclamation), tied to Episode 5: six months later the country is signed away in Paris.
  - *The loop:* from the back of the crowd Indio sees his earlier self (three tattoos) and a second Usman at the front, and keeps away. M carries the toddler for a moment and hangs the medallion on him: "pinanggalingan" in her note meant this child. She is not his mother and not a villain. She asked the Lolo, he refused, so with Indio she took it; without that the medallion never reaches Indio.
  - *The five fingers (Ep 5):* a count, not a goodbye. Five marks; the sixth jump is not made alone.
  - *Ang Huling Tala:* hidden in the handle of the red umbrella that has been in plain sight since Paris: a small star medallion (three wishes, asleep until the twelve are awake: the conductor's reading of the user's "3 wish", open to change) and a kasulatan that looks blank. Through the lens (shows only what is true) the map appears: twelve points across Asia.
  - *The first datu:* as the child receives the family medallion, the voice that used to answer the Lolo speaks one line to Indio (which datu: see `datu_notes.md`). Labelled fiction with his real record beside it.
  - *"Sila":* one figure in the crowd watching the umbrella, not the flag. No more than that.
  - *Ending:* Indio does not go home. M's medallion heats, the sixth mark appears, and the first point on the map lights far to the west of Asia, two thousand years back (the door to Episode 9, without fixing its event). One line for the Lola.
  - Fairness beat: certain / commonly mistaken / fiction, plus the real record of the Rizal and Bracken son and of the datu.
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


## Season 2 timeline, Episodes 1–10 (conductor's proposal, 2026-11-12, on the user's instruction; the user may change any row)
Fixed by the user: Season 2 Episode 1 is the time of Jesus (biblically accurate); Episode 2 is a deep dive into Indio as a child, a schoolboy who naturally loved History; then the hunt for the medallions. Working title of the season: "Ang Labindalawa". Overall numbering continues (S2E1 = Episode 9).
Where Season 1 leaves them: Indio (six marks, no medallion of his own), M (her own medallion), Usman, the lens, the sleeping star medallion (three wishes, asleep until the twelve are awake) and the kasulatan (a map of twelve points across Asia). Each point is a real, documented meeting between the Philippines and its neighbours. Indio only witnesses. Medallions, datu voices and powers are fiction, labelled, with the real record beside them. Every historical item below is from the conductor's memory and MUST be verified with dated sources before any script is written; a stop whose record does not hold is swapped, not bent.

| S2 ep | Overall | Working title | Where and when | True history to teach | Medallion / diwa (fiction) | Indio's story |
|---|---|---|---|---|---|---|
| 1 | 9 | Limang Tinapay | Galilee, about AD 30 | The feeding of the five thousand, the one miracle told in all four Gospels (Mateo 14, Marcos 6, Lucas 9, Juan 6); what each account adds | None: the first point on the map is a lesson, not a medallion. The star stays asleep | The man with three wishes in his pocket watches sharing feed a crowd. Sixth jump, with M |
| 2 | 10 | Batang Indio | Quezon City, about 2012 (Grade 5) | A thing schoolbooks got wrong and how historians proved it (first choice: the Code of Kalantiaw hoax; the repo already has research in `videos/kodigo-ni-kalantiaw`) | None: through the lens Indio sees his own childhood | The boy who corrected his textbook; the Lolo teaching him to read markers aloud; who was already watching him; why he stopped |
| 3 | 11 | Ang Sugo ng Butuan | Kaifeng, Song China, 1003–1011 | Butuan's missions to the Chinese court recorded in the Song history | Rajah Kiling of Butuan: "Ang Sugo" (every language is understood) | First medallion of the hunt; Indio learns to listen before he speaks |
| 4 | 12 | Ang Haring Inilibing sa Tsina | Dezhou, Shandong, 1417 | A ruler of Sulu, Paduka Pahala, visits the Yongle Emperor, dies on the way home; his tomb and descendants are still there | Paduka Pahala: "Ang Daan Pauwi" (one sure way home, once) | Indio can go home to the Lola and chooses not to yet |
| 5 | 13 | Ang Kasulatang Tanso | Luzon and Medang (Java), year 900 | The Laguna Copperplate Inscription: a debt in gold forgiven, the oldest dated document of the Philippines, naming Tundun and Medang | Jayadewa of Tundun: "Ang Kasulatan" (any writing can be read; a debt can be cancelled) | The blank kasulatan shows a second layer: who drew the map |
| 6 | 14 | Mga Luzones | Malacca, 1511 | People of Luzon in Malacca when the Portuguese took it (Tomé Pires; Regimo de Raja) | M's own medallion is named: Datu Sikatuna of Bohol, "Ang Sandugo" (a promise that lets two jump as one) | Who M is and why her time runs out of step with his |
| 7 | 15 | Ang Prinsipe ng Luzon | Brunei Bay, 1521 | Young Ache of Maynila, later Rajah Matanda, serving the Sultan of Brunei, captured by the survivors of Magellan's fleet | Rajah Matanda: "Ang Dagat" (a jump across place, not time) | "Sila" strike for the first time; a medallion is lost |
| 8 | 16 | Ang Sabwatan | Japan and Tondo, 1587–1588 | Magat Salamat and the Tondo conspiracy, which looked to Japan and Brunei for help | Magat Salamat: "Ang Lihim" (to pass unseen) | Indio keeps a secret from M; trust is tested |
| 9 | 17 | Ang Tinig | Maguindanao and Ternate, 1630s–1640s | Sultan Kudarat, his recorded speech to the Maranao, his dealings with Ternate and the Dutch | Sultan Kudarat: "Ang Tinig" (courage that spreads) | Indio, who started with no confidence, speaks up |
| 10 | 18 | Ang Sariling Dagat | Mactan, 27 April 1521 | The battle of Mactan from the shore: what Pigafetta wrote and what is legend | Lapulapu: "Ang Kalasag" (cannot be harmed while protecting others) | Finale: "sila" unmasked; nine of the twelve awake; the star stirs. Three medallions and the three wishes are left for Season 3 |

Rules for S2E1 (decided by the conductor because the user left them open; change on request): the event is the feeding of the five thousand; quotations come only from a public-domain Tagalog Bible (Ang Dating Biblia, 1905) with book, chapter and verse on screen; nothing is put in Jesus's mouth that is not in the text; He is seen from afar or from behind, never in close-up; no jokes and no medallion business inside the scene; Indio, M and Usman stand at the edge of the crowd and touch nothing. The fairness beat says what all four accounts share and what only one tells.
