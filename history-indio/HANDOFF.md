# History Indio — handoff note (2026-11-11)

Read this first in a new session. Then read `history-indio/README.md` ("Anime workflow").

## STATE AT HANDOVER (2026-11-12, session stopped by the user to continue in a new session)
- **Episode 1 `videos/ep01-ang-unang-talon`**: everything is in the repo except the voice and the MP4. `script.txt` / `script_elevenlabs.txt` / `script_plain.txt` are the version the user actually recorded (cool, calm, no slang); `timings.json` is aligned to that recording (140 s, 42 sentences). The render was started and then stopped on the user's request, so NO MP4 exists. To finish: the user re-uploads the Episode 1 MP3 (voice files are never committed), then `bash pipeline/setup.sh` and `/opt/vc/bin/python pipeline/build_anime.py videos/ep01-ang-unang-talon videos/ep01-ang-unang-talon/keys <voice.mp3> <out.mp4>`; timings need no re-alignment if it is the same recording. Then contact sheet check, tick the episode in topics.md, send the MP4, end with captions (`captions.md` is a draft).
- Episode 1 frames still wrong: 15 (missing; sentences 15, 17, 34 temporarily use key 8), 25 (photo on an 1890s cedula, modern flag), 27 (church and modern flag). Prompts for 15 are in `key_prompts.json`; 25 and 27 need "no photograph, no flag, no church" added. The scheduled redo was cancelled at handover.
- A "young stunna" slang version of the Episode 1 script exists in git history (commit 78e9dee) if the user records it later; the user wants Indio cool and calm with that slang used sparingly (see SERIES.md).
- **Kodigo ni Kalantiaw `videos/kodigo-ni-kalantiaw`**: script, 36 keyframes, shots, end card and draft captions done; waiting for the user's MP3; no timings yet.
- Voice: the ElevenLabs connector refused twice ("Free Tier access has been disabled", unusual activity); the user declined the Fish Audio key form; the Hugging Face connector lists Spaces but invoke is disabled ("gradio=none"). The user generates the voice themselves and uploads it.
- Figma: about 75 images used on 2026-11-12 (resets 00:00 UTC).

## UPDATE 2026-11-12 06:30 UTC (supersedes the Episode 1 lines above)
- User correction: **Usman appears only when Indio time-travels and exists only in the past; he is never in the present day.** Episode 3 is Usman's backstory and the user's team is preparing it (reserved in topics.md).
- Episode 1 script was rewritten for this (v2, cool voice with sparing "young stunna" slang, 42 sentences). The uploaded recording is of the OLD script, so `timings.json` is stale: Episode 1 needs a NEW recording, then align again.
- Frames to generate from `key_prompts.json` once Figma credits reset: 10, 12, 13, 14, 15, 16, 25, 27, 35, 37 (the old k10–k14, k16, k35, k37 show the dog in the present day and must be replaced; delete old k11). After frame 15 exists, remove the `"key": 8` fallbacks in shots_fx.json (15 uses its own frame; 17 and 34 use key 15).
- A 720p preview of the OLD version was rendered for the user to judge the look only.

- 2026-11-12 08:05 UTC: Episode 1 artifact page (draft build preview at 540x960, script, QA sheet, keyframes, captions): https://claude.ai/artifact/4Gho44urgCb2e5gexbi4w3 (private to the user; republish from the Episode 1 session to update).

## UPDATE 2026-11-12 07:45 UTC — Episode 1 built from the new recording
- The user recorded script v2; `timings.json` is aligned to it (141.6 s). Built at 1080p with DRAFT frames: k10, k12, k13, k14, k16, k37 are NVIDIA FLUX.2 klein scenery (no characters); sentences 15/17/34 reuse k08, 25 reuses k24, 27 reuses k20, 35 reuses k12, 11 reuses k07. Old k11, k25, k27, k35 were deleted.
- To upgrade when Figma credits reset: generate 10, 12, 13, 14, 15, 16, 25, 27, 35, 37 from `key_prompts.json`, drop the matching "key" fallbacks in shots_fx.json, rebuild (same recording, no re-alignment). Voice file is not in the repo.

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

## Movement on the painted stills (APPROVED by the user 2026-11-12: "Yan okay na yan, go")
- Method: puppet rigs. `pipeline/puppet_still.py` + one `videos/<slug>/rigs/kNN.json` per keyframe; `build_anime.py` uses rigs automatically. Full guide: `pipeline/PUPPET.md`. Local, CPU, free, keeps the Figma quality; about 0.25 s/frame at 720p.
- Limits: small motions only (no walking, turning, new poses); regions are hand-placed per still.
- 2026-11-12: Limahong puppet-rig reel and per-still status are on a private Artifact page: https://claude.ai/artifact/GcNCWFVmX8SRVTVLEQbueG
- Every video from now on should have a rig for every keyframe. limahong-1574 has rigs for all 33 keyframes (k00 to k32); it only needs a rebuild with the voice.
- Wan 2.2 image-to-video (for full-body motion) is still blocked: needs the user's Hugging Face token as a network secret for `upsampler-wan-2-2-14b-image-to-video.hf.space`.

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
- PAUSED by the user on 2026-11-12 ("manual muna"): daily routine `History Indio daily episode` (trig_013S2RKFoJnajV9psukW9qQZ, 00:20 UTC, fresh session, model claude-opus-5-5) prepares the next series episode from `SERIES.md`. Created without the Figma connector or a repo source attached (the tool could not pass them); the user has to add both in the claude.ai routines UI or runs will do text work only.
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

## Usman rule (user correction, 2026-11-12) — overrides anything above
- Usman is NOT in the real world. He appears only while Indio is time travelling and is gone when Indio returns. No Usman in modern-day lines or frames.
- Episode 3 is Usman's back story (replaces the Treaty of Paris slot; later topics shift one episode).
- Episode 2 script and frames were fixed to follow this. Episode 1's SCRIPT was fixed in v2 (commit 6c25672: Indio is alone in QC, the dog comes out of the light at the jump, is gone on return, and is named on return; whether to name him inside 1896 instead is awaiting the user). Episode 1 still needs a new recording and 10 new frames (list in the UPDATE section near the top).

## Season plan from the user (2026-11-12) — overrides the older season arc
- Ep 3: Usman's back story (`videos/ep03-ang-aso-ni-pepe`: he is the dog young Rizal left in Calamba in June 1869; that link is fiction and is labelled so).
- Ep 4: Treaty of Paris 1898 (separate session "History Indio – Episode 4").
- Ep 5: Indio's back story, revealed by his LOLA in the province.
- Ep 6: the medallion is stolen by the woman who has been watching him (M). Twist: she only lured Indio; the episode explains why she took it.
- Still open (ask the user when scripting): what Indio's back story is, and the woman's motive.

## Re-sequenced by the user (2026-11-12, later) — overrides the season plan above
Ep 3 = Indio's back story (`videos/ep03-ang-sabi-ni-lola`: Lola in Kawit; he sees an ancestor wearing the medallion on 12 June 1898; fiction, labelled). Ep 4 = Usman's back story (`videos/ep04-ang-aso-ni-pepe`). Ep 5 = Treaty of Paris (other session). Ep 6 = medallion stolen by M. Ep 7–8 proposed (see SERIES.md "Chapter structure"). Indio's and Usman's back stories are Claude's proposals as director; the user has not yet read them.

## Episode 9, not 7 (user moved it, 2026-11-12): the time of Jesus — opens Chapter 2
- The user wants Episode 7 set in Jesus' era and biblically correct "based on the newest Bible". Open with the user: which translation, and which single event Indio witnesses.
- Rules to keep: only events and words that are in the Gospels, each with chapter and verse in facts.md; say where the four Gospels differ; no invented dialogue for Jesus or any biblical person; Indio and Usman only watch from the crowd; modern translations are copyrighted, so paraphrase and cite verses instead of quoting long passages; label Indio, Usman and M as fiction as usual.
- As Episode 9 it comes after the Chapter 1 finale, so how Indio travels depends on how Episode 8 ends.

## Indio and Rizal (user reminder, 2026-11-12)
Indio IS a relative of "Pepe" (José Rizal). Episode 4 now ends with the Lola's text: "apo, kadugo natin ang batang 'yan." Handling (Claude's recommendation, to keep it honest): Indio descends from the wider Mercado-Rizal family (Rizal had many siblings with descendants), NOT from a secret child of Rizal, and never through a named real woman. Always labelled fiction in captions and the pinned comment. Episode 3's ancestor in Kawit (the medallion keeper) can be from that same family.

## Bloodline and the Usman link (user, 2026-11-12) — the core of the series
- FICTION premise from the user: Indio descends from the son of José Rizal and Josephine Bracken. Real record: that son (usually called Francisco) was born prematurely in Dapitan and died within hours or was stillborn (sources say late 1895 or 1896). In the series he secretly lived. Always label this as fiction in captions and the pinned comment, and state the real record next to it.
- Why Usman knows Indio: Usman was the boy Pepe's dog, and Indio carries Pepe's blood ("kaamoy mo kasi siya", end of Episode 4).
- Episode 3 plants it: in Kawit, June 1898, a woman carries a two-year-old boy who wears the medallion: "ang lolo ng Lolo ko" (the generations fit a child born about 1896). Episode 3 does not say whose child he is. Episode 4 ends with the Lola's text "kadugo natin ang batang 'yan". The full Dapitan reveal (who saved the baby, where the medallion came from) is still unwritten: a later episode.

## State at hand-over to the central session (2026-11-12, about 08:00 UTC)
- Ep 2, 3, 4 each have: script.txt, script_elevenlabs.txt, sentences.json, facts.md, captions.md, endcard.txt, key_prompts.json, shots_fx.json, plates/ chars/ full/ (NVIDIA drafts) and keyframes_sheet.jpg. `keys/` is git-ignored: rebuild with `pipeline/make_keys.py videos/<slug>` (needs `bash pipeline/setup.sh` first on a new machine; about 15 minutes).
- No video exists for Ep 2–4: all three wait for the user's ElevenLabs MP3 (their voice there is called "Young Stunna"). Do not clone or imitate that or any other voice with other tools; the user rejected the open-model voices tried (a female sample voice and five designed male voices).
- Known bad draft frames to redo with Figma when credits reset (00:00 UTC, about 75/day shared by all sessions): Ep 2 k00 (should hold a bilao of pancit), all Usman and Indio faces (they drift between shots); Ep 3 k18 (the flag is drawn wrong: must be blue over red with a white triangle, sun and three stars), k22; Ep 4 k21 (pony), k24.
- A one-time reminder is scheduled in the old Episode 2 session for 00:03 UTC 13 Nov to do the Figma upgrade; the central session should do it instead.
- Another session ("History Indio – real movement") relayed that the user wants real character movement solved before more videos are finished and asked video sessions to pause builds. The user did not confirm this in the Episode 2 session; ask them.
- Sessions: "History Indio – next video" = Episode 1; "History Indio – Episode 4" = Treaty of Paris, now Episode 5.

## Episode 5 (2026-11-12): `videos/ep05-dalawampung-milyon` — Treaty of Paris, 10 December 1898
- The session's brief called this "Episode 4" (`ep04-dalawampung-milyon`); it was renamed to Episode 5 to follow the re-sequencing above. If the user wants it back as Episode 4, rename the folder and change "Apat na ang tattoo ko" / "Lima na ang tattoo ko" to three / four, and M's five fingers to four.
- Shape: Indio REFUSES to jump (four tattoos, tired) and is tricked: a twenty-peso bill tucked beside the Agoncillo marker (Santuario del Santo Cristo, San Juan) carries a handwritten copy of the marker signed "M"; connection = a number he overhears through a window ("bente milyones"); twist = he was at the wrong window: no Filipino was at the table, Agoncillo was never admitted and protested two days later, and Spain signed away what it barely held. Links back to Episode 3 ("anim na buwan pa lang mula ... Kawit"; Marcela Agoncillo). The next episode must use a different arrival, connection and twist.
- Story thread: five tattoos at the end; Indio SEES "M" for the first time (red umbrella across the street, raises five fingers, gone). The follow line does not name Usman (modern-day line).
- 380 words, 51 sentences (line 3 now picks up Episode 4's cliffhanger: "puyat pa ako sa text ni Lola"; the follow line still leaves Usman out, per the brief). Waiting for the user's MP3; then `bash pipeline/setup.sh` (this session only put numpy/opencv in /opt/vc), `align_audio.py`, `build_anime.py`.
- Frames: all NVIDIA FLUX.2 klein drafts, no Figma credits spent. Redo with Figma first: full/tattoo (shows four tattoos, needs five), usman_growl (blue eyes), usman_bonjour and usman_look (no white chest patch), full/war, Indio faces.
- NVIDIA content filter: a blocked prompt returns `finishReason: CONTENT_FILTERED` with an empty image (make_keys prints "argument should be a bytes-like object"). Words that tripped it here: "grand" with a building or room, "government building", "state room", "legislative chamber", "San Juan Metro Manila", "rifle muzzle flashes", "banknote". Reword (ornate / large / paper bill / orange flashes).
- Weak spots (facts.md): the San Juan marker rests on Wikimedia Commons photo captions only; room and hour of the signing unconfirmed (the script names neither).
- 2026-11-12: Episode 5 outputs (script to record, draft keyframe sheet, captions, unverified list) are on a private Artifact page: https://claude.ai/artifact/9VWRWeoNi9bi6pU5aJF2Be (no video yet; waiting for the MP3).

- 2026-11-12: main session outputs page (video status + copyable captions for Limahong and Bakunawa): https://claude.ai/artifact/SmsW31dKNBEDsUGvcC1Xn6 — Limahong is final per the user; do not rebuild it.

## UPDATE 2026-11-12 08:50 UTC — central session
- **Skill bundle (user request):** `.claude/skills/indio/` is the father skill `/indio` (Neocortex principle + Elon Musk five-step principle + the episode workflow), with Kaizen inside it (`kaizen.md`; log in `history-indio/KAIZEN.md`). Use it instead of re-reading the long notes. Do not make separate History Indio skills; add to the bundle.
- **Board (user request):** private Artifact page with every episode's stage and the ElevenLabs scripts with copy buttons: https://claude.ai/artifact/QiKdeQGV7tMTt2DJTVwPVC . Source file is rebuilt in the session scratchpad; update it whenever something finishes. The user wants each session to publish its outputs as Artifacts (message sent to the Ep 1, Ep 5, movement and producer sessions) and wants to be told, with the file shown, whenever something is finished. Later wish: connect the board to their social pages to schedule posts one by one (not set up).
- **Episode 6 written:** `videos/ep06-ang-huling-umaga` (Bagumbayan, 30 Dec 1896): full file set and NVIDIA draft frames. The free generator refuses prompts with rifles; they were reworded (men standing at attention, smoke and birds). Story is a proposal (see SERIES.md "Episodes 6–8"); assumes Episode 5 leaves Indio with five tattoos and only messages from M.
- Episode 6 frames to redo with Figma: k00 (firing line), k46 (five tattoos), Usman frames k16/k33/k37/k54, Indio faces.
- Ep 2–4 `keys/` were rebuilt on this machine. Still no MP3 for any episode.
- Episode 4's facts.md still describes the older "wider Mercado-Rizal family" handling; the newer bloodline premise (son of Rizal and Bracken, fiction) is in Episode 3 and 6 facts and overrides it.

## UPDATE 2026-11-12 09:40 UTC — multi-speaker voice (user: "we can have multi speaker okay?")
- Each of Ep 2, 3, 4, 6 now also has `script_multispeaker.txt` (speakers INDIO, USMAN, LOLA, M) for ElevenLabs v3 Text to Dialogue. Same words in the same order as `script_elevenlabs.txt`, so `sentences.json` and alignment are unchanged; the user exports ONE MP3. Only fictional characters get a voice; real people still never speak. Both versions are on the board.
- The user approved Episode 1 ("approved ep 1"); relayed to the Episode 1 session.

## UPDATE 2026-11-12 10:00 UTC — frames need no approval (user)
- "wag akong hintayin bago mag generate ng frames" and "approve na agad ang frame na minungkahi": generate frames without waiting, proposed frames are approved, and Figma credits may be spent without asking first (report the count afterwards). This overrides "tell the user before spending credits".
- Figma was tried at about 10:00 UTC: "Insufficient Figma AI credits", resets 2026-11-13 00:00 UTC. The central session has a one-time task at 00:05 UTC to upgrade the worst frames at once (order: Ep 2, Ep 6, Ep 3, Ep 4).
