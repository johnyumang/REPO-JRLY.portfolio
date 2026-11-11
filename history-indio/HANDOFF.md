# History Indio — handoff note (2026-11-11)

Read this first in a new session. Then read `history-indio/README.md` ("Anime workflow").

## What exists
- Channel: History Indio (Tagalog/Taglish history and myth explainers, vertical, ~3 min). Branch: `claude/eager-davinci-9qu2gg`. Repo is PUBLIC: never commit MP4s or voice files.
- Finished videos: `kanyon-na-banig` (komiks look), `bakunawa-pitong-buwan` and `limahong-1574` (anime look, user's ElevenLabs voice). Captions are in each folder's `captions.md`.
- In progress in another session: Kodigo ni Kalantiaw (script and prompts pushed; waiting on Figma credits and the user's voice recording).
- Pipeline: Figma image tool makes one anime keyframe per sentence (file key `MYfJYKGrPOiKVT0En76EEM`, free plan ≈ 75 images/day, resets 00:00 UTC) → user records `script_elevenlabs.txt` in ElevenLabs and uploads the MP3 → `pipeline/align_audio.py` → `pipeline/build_anime.py` (depth parallax, transitions, auras, speed lines, impact frames, logo, end card, subtitles, music at half voice level; `--size 720` and `--until N` for fast previews).
- Branding: `pipeline/branding.py`, `branding/` (logo, YouTube profile pictures, banner).
- Skills: `skills/cinematic-explainer-short`, `skills/indio-voice` (OmniVoice fallback voice), `.claude/skills/anime-style` (Blender cel-shading art direction, third-party).

## User's standing preferences
- Decide and execute; don't ask for approval on routine choices. No paid APIs. ElevenLabs is used only by the user for voice.
- Every video: climax in the first 3 seconds, History Indio logo, an in-character follow line at the end, a closing question for comments.
- Every delivery ends with ready-to-paste captions (Facebook, YouTube Shorts, TikTok, Instagram, pinned sources comment).

## Open problem: real character movement
The user wants frame-by-frame anime motion, not animated stills. Tried so far:
- Wan 2.2 image-to-video on a free Hugging Face Space (`upsampler-wan-2-2-14b-image-to-video.hf.space`, host allowed): works, but needs a Hugging Face token for quota; the user declined the token form once.
- ElevenLabs image/edit tools: "free generations busy" on every attempt.
- Midjourney (via the anime-mj prompt plugin): paid, manual.
- Blender: not installed; `pip install bpy` (5.3.0, Python 3.13) and `apt-get install blender` (4.0.2, after `apt-get update`) are both available. No GPU, so CPU rendering only. Needs rigged anime character models (e.g. VRM).

## Other open items
- Limahong end card should say "LABAN SA MGA PIRATA!"; its last eight shots reuse frames.
- Hourly routine `History Indio hourly video` (trig_017Q375Zo6SavwfxqnvaybYB) is paused.
- YouTube auto-upload needs the Claude desktop app's built-in browser; not connected to cloud sessions.
