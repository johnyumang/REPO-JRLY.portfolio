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
Never commit MP4s or voice files: the repo is public.
