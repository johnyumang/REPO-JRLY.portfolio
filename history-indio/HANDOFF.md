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
- NEW FORMAT from the video after Kodigo ni Kalantiaw (user, 2026-11-12): the host is named Indio and every video is his POV as a time traveller who jumps between eras to witness events (first-person eyewitness narration: "nandito ako ngayon sa...", "nakikita ko..."). The intro line replaces "Mga ka-Indio, tsaa time.": "Ako 'to si Indio. Samahan mo akong mag-time travel, at tuklasin ang history natin." Keyframes should put Indio inside the scenes as a witness. Kalantiaw keeps the old intro (script was already handed over for recording).
- SERIES BIBLE (agreed in chat 2026-11-12; Claude's proposals marked "proposed" until the user confirms): Episode 1 is the origin: modern-day Indio, job hunting in QC, fails, goes home broke; his Lolo's medallion (agimat) + reading a historical marker aloud = time jump (proposed; first jump to the 1896 Cry in Balintawak/Pugad Lawin). User wants: character development; an intense love story that feels real; Indio's clothes change in every era; a smart dog companion named after Rizal's first dog (Usman, to be verified) who can talk, but only Indio and animals understand him. Proposed: the agimat changes Indio's clothes automatically on arrival; the dog is an aspin who can also smell when a story is not true (drives the fairness beat); the love interest is fictional (a second time traveller), never a real historical person; Indio only witnesses, never changes events.
- Every delivery ends with ready-to-paste captions (Facebook, YouTube Shorts, TikTok, Instagram, pinned sources comment).

## Open problem: real character movement
The user wants frame-by-frame anime motion, not animated stills. Tried so far:
- Wan 2.2 image-to-video on a free Hugging Face Space (`upsampler-wan-2-2-14b-image-to-video.hf.space`, host allowed): works, but needs a Hugging Face token for quota; the user declined the token form once.
- ElevenLabs image/edit tools: "free generations busy" on every attempt.
- Midjourney (via the anime-mj prompt plugin): paid, manual.
- Blender: WORKS (see `blender/README.md`). `bpy` 5.3.0 on CPU renders a rigged CC0 VRoid character with cel shading at ~5.6 s/frame (720x1280); a 4 s proof shot was delivered 2026-11-11. A full 3-minute video ≈ 6.7 h of rendering and every action is hand-posed in code; the model is a recoloured sample, not a custom host.

## Other open items
- Limahong end card should say "LABAN SA MGA PIRATA!"; its last eight shots reuse frames.
- Hourly routine `History Indio hourly video` (trig_017Q375Zo6SavwfxqnvaybYB) is paused.
- YouTube auto-upload needs the Claude desktop app's built-in browser; not connected to cloud sessions.
