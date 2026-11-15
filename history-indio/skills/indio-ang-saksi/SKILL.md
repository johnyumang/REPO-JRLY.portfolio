---
name: indio-ang-saksi
description: Produce an episode of "Indio: Ang Saksi" (History Indio, new format) - a Tagalog vertical animated short (720x1280 or 1080x1920) with a storyteller who tells every action, a multi-voice cast (Indio cloned from the owner's own recording, every other voice designed), painted "Bakunawa look" stills with no still used twice, real writing on signs, motivated camera moves, code-made sound design, trivia at the very end and no follow card. Use when asked to write, voice, draw, build, repair or check an Indio episode, or to continue the season from the repository.
---

# Indio: Ang Saksi — one episode, start to finish

Everything lives in the repository `johnyumang/REPO-JRLY.portfolio`, folder `history-indio/`. Work from that folder.
This skill is the map; the files it names are the law. Read them before acting, in this order:

1. `LOCAL_SETUP.md` — machine setup, what is free, the eight steps, the eight consistency checks.
   `ENGINES.md` — every engine used (all free), its limit, its key and its script. Use only these; when a
   free quota is used up, wait for it to refill. Never switch to a paid service.
2. `story/CONSISTENCY.md` — rules that never change (looks, names, the villains' sign of three slanted strokes,
   hero lines, tender moments, the storyteller rule, the camera rule, lists of hooks and today-things already used).
3. `story/BIBLE.md`, `story/REWRITE_PLAN.md` — the whole story and what each episode must do.
4. `story/ep01_v2/` and `videos/ep01v2-ang-unang-talon/` — the model episode (script, shots, prompts, camera, sound).
5. `audit/README.md` — how the pictures are drawn and judged.
6. `pipeline/CAMERA.md`, `pipeline/SOUND.md`, `pipeline/voice_clone/README.md`.

## What the owner requires (do not trade these away)
- **Story:** the first 3 seconds are a shout or a blow at 0.00, a flash-forward of the worst moment. Then a short
  present-day part with ONE everyday thing of today and its true origin. TAGAPAGSALAYSAY tells each action in a full
  plain sentence; nothing the viewer needs may live only in a stage line. About 80% invented, 20% true; `facts.md`
  marks which. A significant hero speaks his or her iconic line on camera (attested or firmly traditional only).
  Where the hero had a wife or partner: one short tender moment, adults, hands / forehead / embrace only.
  Trivia only at the very end. No follow card. No talk of "kathang-isip" inside the story. Nothing repeated from an
  earlier episode.
- **Pictures:** the Bakunawa look on every frame. Three draws per shot, choose at 3x zoom, redraw on any fault.
  Character descriptions copied word for word into every prompt. No still used by two lines; a long line gets a second
  still or one continuous hold. Real words on anything meant to be read (`pipeline/sign_text.py`,
  `pipeline/baybayin.py`); nothing blank, no scribble. Usman is never in the present day before Episode 30.
- **Camera:** shot size and angle are drawn into the still; the move goes in `shots_fx.json` with a five-word reason
  (`"why"`). No reason, no move. `"_": {"trans_default": "cut"}`; other transitions only where `CAMERA.md` allows.
- **Voices:** Indio is cloned ONLY from the owner's own recording; clone no one else. Every other voice is designed
  from a written description. One voice per character across all episodes: reuse the saved references. All storyteller
  lines voiced in one session. No time-stretching. "cedula" is SE-du-la; "umungol" is u-MU-ngol.
- **Sound:** each speaker levelled to within 1 LU of their own median; gaps 0.30-0.45 s in a scene, 0.7-0.9 s between
  scenes, 0.5 s hush before the hero's line; music and effects at least 14 dB under any voice; no effect on a word.
  Final mix -16 LUFS +/-0.5, true peak <= -1.5 dBTP.
- **Never:** paid services, secrets in files or chat, audio / video / voice files in the repository (it is public).

## The steps
1. **Script** → `videos/<slug>/script_multispeaker.txt` (`NAME: [tone] line`; stage lines in parentheses are picture
   notes only; `INDIO (sa atin):` for asides). Then `story/_parts/derive.py` for `script.txt` and `sentences.json`.
   Write `facts.md`. Have a fresh reader read ONLY the spoken lines and say who wants what, what went wrong, how it
   was solved; fix what they could not follow.
2. **Shots** → `shots.md` with a Camera column (size / angle / move / reason; 2-3 HIGH POINT rows), and
   `key_prompts.json` (`subject` starting with size and angle, `setting`, `light`).
3. **Voices** → new characters: description in `pipeline/voice_clone/cast_design.json`, `castdesign.py`, `castqc.py`
   (keep any two voices that speak within 10 s under 0.90 similarity). Then
   `HI_VOICE_REC=<owner's recording> bash pipeline/voice_clone/run_multispeaker.sh videos/<slug> <slug>`.
4. **Pictures** → `python pipeline/draw_pick.py <dir> <prompt.json> <seeds> "<negative>"`, one request at a time.
   Needs `NVIDIA_API_KEY` in the environment (free key from build.nvidia.com).
5. **Writing in pictures**, then copy the chosen stills to `videos/<slug>/keys/`.
6. **Camera and sound** → `shots_fx.json`, `sound.json`, `endcard.txt` containing `NONE`, `trivia_break.json`.
7. **Build** → `python pipeline/build_anime.py videos/<slug> videos/<slug>/keys <voice file> out.mp4 --size 720`.
8. **Check before anyone sees it:** every frame decodes; loudness; sheets at 2.5 frames a second, every one looked
   at; 10 fps strips of every big move and transition (no judder, no cut in the middle of a word); the eight
   consistency checks, one row per shot; a per-line sound audit (level, speaker similarity, pitch, speed, gap, clipped
   ends, bed level, wrong words). A fault means redraw or re-voice, not a note. Then a person listens once.

## What is not in the repository (bring it yourself)
- The owner's Episode 1 voice recording (for the Indio clone).
- The designed cast references (TAGAPAGSALAYSAY, USMAN, BONIFACIO, ORIANG, ISLAW, LOLO, RIZAL, M ...): the owner can
  download them from his private "Cast Kit" pages; put them in `$HI_VOICE_WORK/cast/` as `NAME.wav` + `NAME.txt`.
- The chosen stills (`keys/`) and all audio and video.

## Honest limits
Judging pictures and Tagalog takes a strong model and a person's ear; the scripts carry the method, not the taste.
The free picture service is slow and sometimes refuses a prompt (reword it). Real motion clips need a graphics card.
