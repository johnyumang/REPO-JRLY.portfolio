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
6. **Deliver** the MP4 with what could not be verified. MP4s and voice files are not committed (this repo is public).

## Pieces
- `engine3d/` — cel-shaded 3D stage (three.js) that renders one still per shot.
- `skills/cinematic-explainer-short/` — the skill: team stages, style presets, komiks filter, motion-comic script.
- `pipeline/` — `tts_mms.py` (Tagalog base read, Hugging Face `facebook/mms-tts-tgl`), `vc_chatterbox.py`
  (converts the read to the narrator's voice, Hugging Face `ResembleAI/chatterbox`), `soundtrack.py`
  (music + SFX at half the voice level), `build_video.py`, `make_video.sh`.
- `characters/`, `styleboard/` — earlier look-dev.

## Voice
Set `HI_VOICE_REF=/path/to/narrator.wav` (15–25 s, clean, no music) to get the narrator's voice.
Keep that file out of this repo. Without it the video uses the plain TTS voice.
