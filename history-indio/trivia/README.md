# Trivia breaks: "PATALASTAS NI USMAN"

Every episode from Episode 3 to Episode 50 has one short joke break of about 12 to 20 seconds. Chibi Indio and chibi Usman stop the story and tell one surprising, true fact about the Philippines, then go back to the story.

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
- **What a second look taught us (13 Nov: 19 of 48 breaks were moved):**
  - A cliffhanger about a plan, a mystery or a journey is the right place. A cliffhanger about whether someone lives is not: never at the peak of a rescue or a battle, and never right before a death, a burial, a prayer or an oath.
  - Read the two sentences on each side of the cut aloud. If the second one finishes the first (a question and its answer, a reveal and the line that proves it, a line and Usman's reply), the cut is in the wrong place: move it to just before the pair, or to after it.
  - In a grave episode look for a seam the story itself has lightened: the end of a montage, a change of place or time, best of all right after one of Usman's own small jokes.
  - The silent gap after the chosen sentence must be at least 0.35 s in `timings.json`.
  - Keep it in the middle: not later than about 55% of the episode's length. A break after the story has resolved holds nobody.
- `gap` in the file is the pause between the break's own lines. It has nothing to do with the silent gap in the story; leave it alone when you move a break.
- `insert_after_sentence` is the index in `timings.json`, or in `sentences.json` if the episode has no timings yet.
- `insert_time` is the middle of the silent gap after that sentence. It is given only when `timings.json` exists.

## Matching a fact to an episode
- The fact is random on purpose and is never about the episode's own subject.
- **Match the mood.** A grave episode (an execution, a massacre, a flood, martial law, a scripture-heavy scene) gets a gentle nature fact and a mild joke, and its file says `"grave": true`. The tool then makes the quiet break by itself: a dark night-blue screen with soft gold and cream words, no rays, dots or sparkles, and a fade from black and back to black. The sound has no jingle: one soft low tone at the start and a slow, low hum under the voices, with no beat. A light episode can take the silliest fact.
- `palette` is `sun`, `sea` or `leaf`, following the fact: land animals and food are sun, sea life is sea, plants and forest are leaf.

## Adding facts
- Add an object to `pool.json` with a new `id` and all the fields used by the others.
- Have it checked by a second reader before use, and keep a used fact out of the spares.

## The chibi sprites
- `trivia/sprites/indio.png` is the young Indio (about twenty, red headband). `trivia/sprites/usman.png` is Usman. Every break uses these two unless the episode's file says otherwise.
- An episode can name another sprite: `"sprites": {"INDIO": "indio_s5"}` in its `trivia_break.json` makes the tool use `trivia/sprites/indio_s5.png`.
- `indio_s5.png` is the older Indio of Season 5 (in his forties, long grey coat). It is a first try and no episode points at it yet; a better one is being drawn. When it is ready the conductor adds the field to the Season 5 episodes and says so.

