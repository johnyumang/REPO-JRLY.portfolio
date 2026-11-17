# Indio Studio + animate pipeline

Pictures in, moving anime out. Two parts:

- **studio/** – a web app (shot board) for trying takes shot by shot and picking the best one. Lives on Vercel.
- **pipeline/animate/** – the local workflow that makes the finished 1920x1080 video. Runs on the cloud machine or your PC.

## The workflow

```
videos/<ep>/key_prompts.json + shots_fx.json + timings.json + script
        |
        v
  motion.py ............ manifest.json: one shot per still, one motion prompt per shot, cut times from the voice
        |
        v
  stills.py ............ 16:9 version of each still (redrawn wide with the free draw service; fallback: fit on blur)
        |
        +--> (optional) studio: import manifest -> Generate takes -> pick one per shot -> Export manifest
        |
        v
  i2v.py ............... clips/<shot>.mp4 per shot (wan-free = free, minimax = credits); studio picks are downloaded
        |
        v
  remotion/ ............ 1920x1080, 30 fps: hard cuts, kinetic captions (yellow, uppercase, black outline,
        |                speaker label, bottom band away from faces), logo, flash + shake only on shouts,
        |                dip to black (never a cross-dissolve) where a shot is marked "fade"
        v
  renorm.sh ............ audio to -16 LUFS, true peak <= -1.5 dBTP  ->  <work>/<ep>_animated.mp4
```

One command does all of it:

```
bash pipeline/animate/run.sh ep01b-1min --voice /path/to/voice.wav            # whole episode, free provider
bash pipeline/animate/run.sh ep01b-1min --voice v.wav --shots 0-1             # quick test: first 2 shots
bash pipeline/animate/run.sh ep01b-1min --voice v.wav --manifest exported.json   # use the takes picked in the studio
```

Output goes to `/opt/work/animate/<ep>/` (change with `--work`). Nothing it makes goes into the repo: no clips, no
voice, no renders. Run it again and finished clips are kept; delete a clip to make it again.

Needs: Python 3 with `gradio_client` and `pillow` (run.sh makes a venv if missing), ffmpeg, Node 18+, and a Chromium
(`CHROME=/path/to/chrome`, default `/opt/pw-browsers/chromium`). First render runs `npm install` in `remotion/`.

## Motion prompt rules (motion.py)

1. Keep the art style – animate the painting, never restyle it.
2. One continuous shot – no camera cuts inside a clip.
3. Only the motion the line needs – a shout moves, a narrated line just breathes. The camera move comes from
   `shots_fx.json`, and only when it has a "why" (see `pipeline/CAMERA.md`).
4. Faces stay on model.
5. No hands-only shots – a still that is only hands gets a warning; redraw it with a face in frame.

Edit any prompt in the manifest (or in the studio) before generating. Mabilis lang.

## Deploy the studio on Vercel (owner does this, free Hobby plan)

1. vercel.com -> Add New -> Project -> import this GitHub repo.
2. **Root Directory**: `history-indio/studio`. Framework: Next.js (auto). Build command: default.
3. Settings -> Environment Variables. Type the values there yourself, never in the repo or in chat:
   - `STUDIO_PASSCODE` – required. Without it the whole studio stays locked.
   - `MINIMAX_API_KEY` – only if you want the paid provider.
   - `MINIMAX_API_HOST` – `https://api.minimax.io` (or the China host if your account is there).
   - `MINIMAX_MODEL`, `MINIMAX_RESOLUTION` – optional; leave empty for the defaults.
   - `HF_TOKEN` – optional, for the local pipeline (more free GPU time). The studio does not need it.
4. Deploy. Open the site, type the passcode, import a manifest (from motion.py, or paste one).

Every server route answers in seconds (create a task, check a task); the waiting happens in your browser, so it fits
the Hobby limits. There is no database: the board is saved in your browser and in the JSON you export.

## Free vs credits

| | Cost | Notes |
|---|---|---|
| wan-free (Hugging Face Space) | free | up to 5 s per take; shared GPU, may queue; a daily limit per connection ("quota exceeded" = try later or use the local pipeline) |
| draw service for 16:9 stills | free | same one the episodes already use |
| Remotion render, loudness | free | runs on your machine |
| Vercel Hobby | free | |
| **minimax** | **spends MiniMax credits on every take** | studio asks before each take; 6 or 10 s clips; download links expire in about an hour, so export and run the pipeline soon |

The MiniMax request/response shapes are kept in one place (`studio/lib/providers/minimax.ts`, mirrored in
`i2v.py`). They were written without access to the official docs page and are marked UNVERIFIED there; check the
first real task and fix that one file if a field differs.
