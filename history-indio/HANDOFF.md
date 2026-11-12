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
- MID-SEASON TWIST (user, 2026-11-12): Indio turns out to be a descendant ("apo") of José Rizal through one of Rizal's sweethearts. This is FICTION and must be labelled so in the episode's captions and pinned comment: history records no surviving descendants of Rizal (to be verified before scripting: his son with Josephine Bracken died shortly after birth). Proposed handling: never state as fact that a named real woman secretly bore Rizal's child; reveal it through the Lolo's medallion and Usman (proposed: Usman is Rizal's own childhood dog, which is why he knew Indio's name in Episode 1). Foreshadowing already planted in Episode 1: the dog's name and "Kumapit ka, Indio!".
- Every delivery ends with ready-to-paste captions (Facebook, YouTube Shorts, TikTok, Instagram, pinned sources comment).

## Look decision (user, 2026-11-12)
The user saw the Blender cel-shaded renders and did not like them. They want to STAY with the painted Figma anime still quality (videos/limahong-1574/keys/). Do not use the Blender host clips in videos; the four Limahong clips were cancelled mid-render. Blender on this machine cannot reach that painted quality. Real movement at that quality needs image-to-video on the stills (Wan 2.2 Space, needs a free Hugging Face token the user has not given).

## Companion (confirmed by the user, 2026-11-12)
Usman is an aspin (the name, after Rizal's first dog, still needs verifying). He talks, but only Indio and animals understand him. He can smell when a story is not true AND when there is danger.

## Story format (user direction, 2026-11-12)
Every episode is a journey: Indio travels and ends up witnessing one significant event in history. Tell it as a small story with little things that link up, not as a lecture.
**Vary it every episode. Do not reuse the same shape** (user correction: he must NOT always arrive confused). Change three things each time and check the previous episodes so none repeats back to back:
- **How he arrives / his state**: puzzled is only one option. Others (my suggestions): he comes on purpose looking for something, is hungry or tired and just wants to eat, is in a hurry, is mistaken for someone else, is already in the middle of trouble, is on an errand for someone.
- **How he gets connected to the event**: meeting a person is only one option. Others (my suggestions): an object he picks up or is handed, a job he takes, a mistake he makes, something he overhears, someone he helps, someone chasing him.
- **The twist**: a different kind each episode (who the person really is, what the small detail really was, the event is not what the textbooks say, he was looking at the wrong side, and so on).
The user's own examples of small beats: he walks around, sees a vendor (ale), hears sudden shouting, notices a detail that turns out to be the event.

## Open problem: real character movement
The user wants frame-by-frame anime motion, not animated stills. Tried so far:
- Wan 2.2 image-to-video on a free Hugging Face Space (`upsampler-wan-2-2-14b-image-to-video.hf.space`, host allowed): works, but needs a Hugging Face token for quota; the user declined the token form once.
- ElevenLabs image/edit tools: "free generations busy" on every attempt.
- Midjourney (via the anime-mj prompt plugin): paid, manual.
- Blender: WORKS (see `blender/README.md`). `bpy` 5.3.0 on CPU renders a rigged CC0 VRoid character with cel shading at ~5.6 s/frame (720x1280). `blender/host_shot.py --shot greet|twist|point|powerup` makes host action clips on a night beach set; `blender/render_limahong_clips.sh` renders the four used in limahong-1574 (hybrid: Figma stills + a few Blender host clips). Every action is hand-posed in code; the model is a recoloured sample, not a custom host.

## Other open items
- Limahong end card should say "LABAN SA MGA PIRATA!"; its last eight shots reuse frames.
- Daily routine `History Indio daily episode` (trig_013S2RKFoJnajV9psukW9qQZ, 00:20 UTC, fresh session, model claude-opus-5-5) prepares the next series episode from `SERIES.md`. Created without the Figma connector or a repo source attached (the tool could not pass them); the user has to add both in the claude.ai routines UI or runs will do text work only.
- Hourly routine `History Indio hourly video` (trig_017Q375Zo6SavwfxqnvaybYB) is paused.
- YouTube auto-upload needs the Claude desktop app's built-in browser; not connected to cloud sessions.

## Motion plan (user, 2026-11-12)
Save tokens and effort: do NOT animate every shot. Most shots stay as painted stills with the animator's effects (parallax, transitions, auras, speed lines). Only the key moments (hook, climax, plot twist, final follow line; 3–5 per video) get real AI image-to-video motion. Primary model: Wan 2.2 (HF Space `Upsampler/wan-2-2-14b-image-to-video`). Backup: Tencent HunyuanVideo image-to-video (the user's "10-cent generator"). Both need Hugging Face access that can run Spaces: the connector currently refuses `invoke` ("gradio=none"), and direct use needs a read token for the Space host. `build_anime.py` already plays a clip for a line via `"clip": "clips/cNN.mp4"` in `shots_fx.json`.

## NVIDIA free endpoint (backup stills only) — tested 2026-11-12
- Key is saved as a network secret for `ai.api.nvidia.com` in env JRLY-1; send **no** Authorization header.
- Works: `POST https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.2-klein-4b` body `{"prompt","width":768,"height":1344,"seed","steps":4}`, header `NVCF-POLL-SECONDS`; image is `artifacts[0].base64` (JPEG, ~3 s). Helper: `pipeline/nvidia_still.py`.
- Quality is below the Figma stills (generic look, weak prompt following, odd props). Use only when Figma's daily credits run out, mainly for backgrounds/filler.
- Unreliable: `flux-3-image-klein` (worked once, then 502/504). FLUX.1-schnell/dev fail on NVIDIA's side.
- Not usable: image editing (`flux.1-kontext-dev`, klein `image`) only accepts NVIDIA's own sample images, not ours. No video model answered at ~70 addresses tried (Cosmos, Wan, Hunyuan, LTX, SVD...).

## Shot rules from the user (2026-11-12)
- Prefer **close-up / zoomed character shots** (head-and-shoulders, detailed ink style). Avoid full-body shots with weapons or bare torsos: the generators get swords and anatomy wrong.
- **Background must match the scene and be 100% consistent.** Method: draw ONE background plate per location (no people), reuse that same plate in every shot of the scene (different crop + blur), generate the character on a plain white background, then run `pipeline/composite_shot.py character.jpg plate.jpg out.jpg [x y scale blur]` (cuts out the white, grades for scene light, composites). Tested with NVIDIA FLUX.2 klein; works. Known gap: the character's face still drifts between shots (no reference-image input).

## Episode 2 (started 2026-11-12): `videos/ep02-british-sa-maynila`
- British capture of Manila, 1762. Shape: Indio arrives WITH a job (delivery rider, pancit order from "M" to Baluarte de San Diego), lands already in the middle of the bombardment; connection = his own wrong assumption ("sakop na ang buong Pilipinas"); twist = only Manila and Cavite were held, and peace was signed in Paris before anyone there knew Manila had fallen. Next episode must use a different arrival, connection and twist.
- Story thread: "M" (the mystery woman) placed the order and tipped him; Indio now has two tattoos; he works as a delivery rider.
- Keyframes: `pipeline/make_keys.py videos/<slug>` builds everything from `key_prompts.json` (plates, characters on white, full frames, per-shot composite). Files already in `plates/ chars/ full/` are kept, so a Figma-made image saved under the same name replaces the NVIDIA draft; re-run to recomposite. On 2026-11-12 Figma credits ran out after one image (`plates/siege.png`); everything else is NVIDIA FLUX.2 klein.
- Web pages could not be opened directly from the session (DNS); facts rest on search summaries cross-checked across pages (see `facts.md`).
- Episode 2 `keys/` is not committed (100 MB of composites): rebuild it any time with `/opt/vc/bin/python pipeline/make_keys.py videos/ep02-british-sa-maynila` (uses the committed `plates/ chars/ full/`; no credits spent). `keyframes_sheet.jpg` shows the current drafts. NVIDIA limits met: prompts over 800 characters are refused; it cannot draw pancit on a bilao or Indio and Usman together reliably; teal clothes clash with the green key (rider jacket is orange).
- To upgrade with Figma after credits reset: generate the character with the full prompt from `key_prompts.json` (ask for a flat bright green background), save it as `chars/<name>.png`, delete the `.jpg`, re-run make_keys. Priority: indio_shock (needs the bilao of pancit), indio_usman, usman_*, indio_* faces.
