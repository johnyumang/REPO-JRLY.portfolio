# Trivia breaks: "PATALASTAS NI USMAN"

Every episode from Episode 3 to Episode 50 has one short joke break of 18 to 23 seconds. Chibi Indio and chibi Usman stop the story and tell one surprising, true fact about the Philippines, then go back to the story.

- On-screen title: **PATALASTAS NI USMAN**, with a small second line, *trivia lang, walang bayad*.
- `pool.json` holds the facts. Each `videos/<slug>/trivia_break.json` says which fact an episode uses, its lines, and where the break goes.

## Rules for a fact
1. **Two independent reputable sources** say it. Prefer IUCN, a national museum or government science agency, Britannica, National Geographic, a peer-reviewed paper or a university.
   - Record each source with its URL and what the page says.
   - Set `"opened": true` only if you opened the page itself. A search summary is `false`.
2. **No myths and no disputed records.**
   - Never use: the yo-yo as an ancient weapon, a Filipino inventing the fluorescent lamp, the Code of Kalantiaw, "7,107 islands", or the tarsier as "the smallest primate".
   - "Only", "smallest", "largest" and "first" need a source that says exactly that. Otherwise write "isa sa".
3. **Not a cliché.** Skip what every schoolbook says, such as the national bird, how the jeepney began, or Mayon's cone. Aim for the fact a viewer would repeat to a friend that night.
4. **Nothing sad, political or religious.** Nothing about a living person, and nothing that mocks a region, language or people. No real company, brand, product or party.
5. **Variety.** No two facts about the same animal, plant or place. Spread the categories; at least 20 animals.
6. **Second reader, required.** A separate checker tries to refute every fact with its own searches, defaulting to "does not hold" when unsure.
   - Only facts with `"checked_by_second_reader": true` may go into an episode.
   - Reword or drop whatever does not survive.

## Rules for the lines
- Line 1 is always `USMAN: Teka, patalastas muna!`
- The last line is always `INDIO: Balik sa kuwento, par!`
- Between them go 2 to 4 short lines, INDIO and USMAN taking turns, at most 40 words together. They tell the one fact and end on a small joke.
- Indio is warm and quick and says "par"; Usman is dry and funny.
- Taglish as the show speaks it. Use short words a voice says cleanly, spell numbers as they are said, and avoid tongue-twisters.
- State a fact no more strongly than its sources do.
- `emphasis` lists one or two words per line to show bigger on screen.

## Where the break goes
- **Window:** 55–100 seconds into a Season 1 episode (Episodes 4–8, about 2.5 minutes long); 60–130 seconds into the others. Never in the first 50 seconds.
- **Spot:** the silent gap right after the strongest open-loop line in that window (a cliffhanger, a question, a reveal half-made), so the viewer waits through the break for the answer.
- **Never:**
  - inside or right before the fairness beat ("linawin natin" / "lilinawin ko");
  - inside a scripture quotation or the fiction disclaimer;
  - between two sentences that make one thought.
- `insert_after_sentence` is the index in `timings.json`, or in `sentences.json` if the episode has no timings yet.
- `insert_time` is the middle of the silent gap after that sentence. It is given only when `timings.json` exists.

## Matching a fact to an episode
- The fact is random on purpose and is never about the episode's own subject.
- **Match the mood.** A grave episode (an execution, a massacre, a flood, martial law, a scripture-heavy scene) gets a gentle nature fact and a mild joke, and its file says `"grave": true`, so the conductor can decide whether to soften the bumper. A light episode can take the silliest fact.
- `palette` is `sun`, `sea` or `leaf`, following the fact: land animals and food are sun, sea life is sea, plants and forest are leaf.

## Adding facts
- Add an object to `pool.json` with a new `id` and all the fields used by the others.
- Have it checked by a second reader before use, and keep a used fact out of the spares.
