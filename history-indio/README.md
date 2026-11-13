# History Indio — video workflow

Tagalog/Taglish komiks-style explainers about Philippine history, myths and legends (1080x1920, 30 fps, ~3 min).

## Make a video
1. **Pick** the next topic from `topics.md`.
2. **Research**: at least two dated sources per claim → `videos/<slug>/facts.md` (claim, link, date, status).
3. **Script**: `videos/<slug>/script.txt`, 330–380 words, hook first, a fairness beat, and a closing question
   for the comments (see the skill for the options).
4. **Shots**: `videos/<slug>/shots.mjs` — one shot per sentence or half-sentence (3–6 s). Copy
   `videos/kanyon-na-banig/shots.mjs` as the template; characters and props are listed in `engine3d/stage.html`
   (`CAST`, `POSE`, `PROPS`). Add new cast entries there when a story needs them.
5. **Build**: `bash pipeline/setup.sh` once, then `bash pipeline/make_video.sh <slug>`.
   Output: `/opt/work/<slug>/final.mp4` and `qa_sheet.jpg`. Look at the sheet before sending.
   Subtitles are burned in automatically from the script timings.
6. **Captions**: write `videos/<slug>/captions.md` (Facebook, YouTube Shorts title/description/tags, TikTok, Instagram,
   pinned sources comment; main keyword in the first line; only claims the script makes). Copy an existing one as the template.
7. **Deliver** the MP4, what could not be verified, and END the message with the captions ready to paste. MP4s and voice files are not committed (this repo is public).

## Pieces
- `engine3d/` — cel-shaded 3D stage (three.js) that renders one still per shot.
- `skills/cinematic-explainer-short/` — the skill: team stages, style presets, komiks filter, motion-comic script.
- `skills/indio-voice/` — the voice skill: expressive Filipino narration in the narrator's voice with the open
  OmniVoice model (no ElevenLabs), tone and reaction tags, and a speech-recognition check.
- `pipeline/` — `make_sentences.py` (tagged script → sentences), `soundtrack.py` (music + SFX at half the
  voice level), `build_video.py`, `make_video.sh`. `tts_mms.py` only makes a neutral fallback voice sample.
- `characters/`, `styleboard/` — earlier look-dev.

## Voice
Set `HI_VOICE_REF=/path/to/narrator.wav` (about 10 s, clean, no music, with `narrator.txt` beside it) to get
the narrator's voice. Keep that file out of this repo. Without it the video uses a neutral Tagalog voice.
Write tone tags (`[excited]`, `[suspense]`…) and reaction tags (`[laughter]`, `[sigh]`) into `script.txt`;
see the indio-voice skill.

## Anime workflow (current house style)
The channel now uses an anime look with real movement. Use `videos/limahong-1574/` as the template.
1. Pick the first unchecked topic in `topics.md`; research; write `facts.md`.
**Format (from the video after Kodigo ni Kalantiaw):** time-travel eyewitness story. The host, Indio, narrates in
first person as he jumps between eras and witnesses the events himself. Right after the hook he says: "Ako 'to si Indio.
Samahan mo akong mag-time travel, at tuklasin ang history natin." (this replaces "Mga ka-Indio, tsaa time."). Show Indio
inside the keyframes as a witness. The fairness beat stays: Indio says what is proven, disputed or legend.
2. Write `script.txt` (330–380 spoken words, one tone tag at sentence starts, hook in sentence one, a fairness
   beat, a closing question, and a final in-character follow line such as "At mag-follow na kayo, guys, para sa
   dagdag lakas ko laban sa ...!"). Run `python3 pipeline/make_sentences.py videos/<slug>/script.txt videos/<slug>/sentences.json`.
3. Write `script_elevenlabs.txt`: the same sentences in the same order with ElevenLabs v3 tags
   ([excited] [serious] [dramatic] [suspenseful] [playful] [curious] [warm] [sad] [triumphant] [whispers] [laughs] [sighs]),
   years written as spoken words. Give it to the user; they record it in ElevenLabs and upload the MP3.
4. Keyframes: one vertical anime image per sentence with the Figma image tool (file key `MYfJYKGrPOiKVT0En76EEM`,
   model `gpt-image-2.5-sunburst`, 1152x2048), saved as `videos/<slug>/keys/kNN.png`. Start every prompt with the
   style block in `videos/limahong-1574/` prompts / the README of the skill, describe recurring characters
   identically, no text in images. The free Figma plan allows roughly 75 images a day (resets 00:00 UTC);
   if credits run out, reuse frames with `"key"`/`"keys"` in `shots_fx.json`.
5. `shots_fx.json`: effects per sentence (water, embers, sparkle, spray, bubbles, shake, punch, flash) and optional
   `move`. Sentence 0 should be a cold open: `"keys": [a, b, c]` listing the three most dramatic frames.
6. When the user's MP3 arrives: `python pipeline/align_audio.py voice.mp3 videos/<slug>/sentences.json videos/<slug>/timings.json`
   then `python pipeline/build_anime.py videos/<slug> videos/<slug>/keys voice.mp3 out.mp4` (use `/opt/vc/bin/python`
   after `bash pipeline/setup.sh`). It adds depth-parallax motion, effects, the History Indio logo and end card,
   subtitles, and music/SFX at half the voice level. Set the end-card line per video in `pipeline/branding.py`.
7. Look at a contact sheet of the result, then deliver the MP4 and END the message with captions
   (`captions.md`: Facebook, YouTube Shorts title/description/tags, TikTok, Instagram, pinned sources comment).
8. Movement: write a puppet rig for each keyframe (`videos/<slug>/rigs/kNN.json`, see `pipeline/PUPPET.md`). `build_anime.py` picks rigs up
   automatically, so the painted still itself moves (head, arms, breathing, hair, cloth, fire, water, blinks). This is the approved way to get movement.
Never commit MP4s or voice files: the repo is public.

## 3D perspective moves
Opt-in per shot in `shots_fx.json` (Season 2); shots without them build exactly as before. Code: `pipeline/depth3d.py`.
The keyframe is split into a near layer (figure, near ground) and a far layer; the background hidden behind the near
layer is filled by mirroring, and each layer moves by its own smoothed depth, so near and far separate without torn edges.
- `"depth": "strong"` — stronger, layered parallax for the classic moves (`push_in`, `pull_out`, `pan_*`, `tilt_*`).
- `"move": "dolly_in"` / `"dolly_out"` — the camera travels toward / away: the subject grows faster than the background,
  which recedes slightly (a light dolly-zoom). Use for a figure against a deep background, reveals and endings.
- `"orbit_left"` / `"orbit_right"` — the camera arcs around the subject: near and far slide in opposite directions.
  Use for a standing character, a figure in front of a crowd, objects on a table with a room behind.
- `"crane_up"` / `"crane_down"` — vertical arc with a slight tilt. Use for crowds in front of a building, ships on the sea, vistas.
- `"rack_focus"` — the focus pulls from the background to the subject (`"focus_to": "far"` for the reverse). Use for a
  quiet beat, a figure looking at a landscape, or to switch attention between a near object and the scene.
- `"dof": "far"` or `"near"` — optional light depth-of-field on the layer the shot is not about (with any 3D move or strong shot).
Example: `"12": {"move": "orbit_left", "fx": ["embers"], "dof": "far"}`. All effects still work on top.
Not for: flat pictures (letters, maps, screens, close-ups of a page) — the builder detects them and uses the normal move;
heavy crowds with many overlaps (keep `crane_*`/`orbit_*` there, they uncover little); thin structures against the sky
(masts, spears, ropes) and hands at the edge of a figure, which may separate from the body on a big move.
Cost: about the same as the classic moves at 720 wide (about 1 s per keyframe to make the layers).

## Chibi trivia break ("PATALASTAS NI USMAN")
From Episode 3 on, each episode stops once, around its best-retention point (after about one minute, in a pause
after a cliffhanger line), for an 18–23 s joke "commercial": one true, non-cliché fact about the Philippines (animals
welcome), told by chibi Indio and chibi Usman. Line 1 is always Usman: "Teka, patalastas muna!"; the last is always
Indio: "Balik sa kuwento, par!"; 2–4 lines between (at most 40 words). Every fact needs two independent reputable
sources, shown on screen in the `source` line. No real brand, company, party or living person ever appears.
`pipeline/trivia_break.py` (numpy + Pillow + soundfile + ffmpeg, run with `/opt/vc/bin/python`):
```
python pipeline/trivia_break.py cutout --in art.png --out sprite.png [--bg auto|green|magenta|white] [--outline 14]
python pipeline/trivia_break.py render --spec spec.json --out break.mp4 [--size 720x1280] [--fps 30] [--sheet sheet.jpg] [--stills 2,9,16] [--guides]
python pipeline/trivia_break.py splice --video episode.mp4 --brk break.mp4 --at 81.20 --out out.mp4 [--force]
```
- `cutout`: one subject on a flat green/magenta/white background → RGBA sticker (flood fill from the borders, so green
  or white parts inside the subject stay; soft edges, spill removed, white outline, drop shadow).
- `render`: the spec (title, subtitle, palette `sun`/`sea`/`leaf`, sprites INDIO/USMAN, subjects with label and
  from_line, lines with speaker/text/wav/emphasis, source, countdown_text; paths relative to the spec) becomes the
  break: synthesised sting, bed (18 dB under the voice) and whoosh, mastered to −16 LUFS / −1.5 dBTP, 48 kHz stereo.
  The layout boxes are fixed (`BOLD` in the script, all inside the phone safe area; only the chibis' feet may stand in
  the bottom app margin, their face zone may not); the drawn extents of every element, with the time each is on
  screen, are computed first and the command exits with code 3 naming any overlap, so nothing ever covers a face or
  the subject. Look at the `--sheet` before using a break. Optional spec fields: `"layout": "classic"` renders the
  version-1 frame (`BOXES`); `joke_line` (index; default the line before the last: the listener cracks up on it);
  `subjects[].pulse` (words that make the subject pulse; default its label).
- `splice`: cuts the break in at `--at` (rounded to a frame) with 0.20 s audio fades, one re-encode, then the loudness
  guard and the full-decode check. It refuses a cut inside speech and warns (with the quietest frame nearby) when the
  120 ms around the cut is not 12 dB under the episode's average. Voice and video files stay out of this repo.
- The whole job for one episode, on the render machine that holds its work folder and final MP4 (from `history-indio/`,
  `HI_VOICE_REC` set, nothing else heavy running):
  ```
  /opt/vc/bin/python pipeline/trivia_voice.py videos/<slug> --out $HI_VOICE_WORK/<slug>/trivia [--takes 3] [--cast DIR]
  /opt/vc/bin/python pipeline/trivia_break.py episode videos/<slug> --voice $HI_VOICE_WORK/<slug>/trivia --video <final>.mp4 --out <final>_trivia.mp4
  ```
  `trivia_voice.py` records the lines of `trivia_break.json`: INDIO with the clone of the user's own recording exactly as
  `gen_ms.py` makes Indio lines (tones: line 1 and the last excited, a question curious, the rest playful; a line's `tone`
  overrides; `grave` makes Indio warm), USMAN with his designed voice (`USMAN.wav` + `.txt` from `--cast`, else
  `$HI_VOICE_WORK/cast`, else `/opt/work/voice/cast`). Up to `--takes` takes per line, judged by the voice_clone checks
  (first word, no stray token at either end, words, speaker similarity, numbers) and the best kept; a line's `say` is what
  is spoken and judged, `text` stays the caption. Trimmed to 60 ms, 48 kHz mono 16-bit, about −18 LUFS; `l{i}_{SPEAKER}.wav`
  and `takes.json`. Exit 1 naming the line if no take is acceptable; warns if the speech is outside 12–20 s. It unloads the
  listeners and waits for 12 GB free before each generation round (the voice model takes about 11 GB).
  `trivia_break.py episode` builds the spec (sticker `trivia/stickers/epNN.png`, error if missing; `--set
  subjects.0.image=PATH` for a test), picks the pause (0.22 s, widened up to 0.40 s for 18–23 s; never speeds audio up),
  `"calm": true` for a grave episode (no shake or flash, softer sting, slower pops), cuts in the gap after
  `insert_after_sentence` of the CURRENT `timings.json` at the quietest 40 ms of the video's own audio (refused unless
  12 dB under the episode average), renders with a sheet, splices, checks (duration, both streams, every frame decodes,
  −16 LUFS, true peak ≤ −1.5 dBTP) and prints one summary line and the sheet and two frames to look at.
