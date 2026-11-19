# Bike History

Vertical 60-second episodes, one machine each, from the first bicycle to today. The bike is a real 3D model built
in code from named parts; everything around it (paper background, labels, the rider, the road) is drawn in 2D.

- `SERIES.md`: the season list (draft).
- `ENGINES.md`: the free tools, their licences, and what works on a CPU-only machine.
- `lib/draisine.py`: the parametric model for episode 1. A new bike is a new file like it.
- `ep01/facts.md`: facts with sources, and the exact text on screen.
- `ep01/render.py` (3D frames + label anchors), `ep01/compose.py` (2D layers and text), `ep01/narration.py` (voice and subtitle timing),
  `ep01/sound.py` (sound in code), `ep01/build.sh` (all stages). Frames, audio and video are written outside the repo.

Narration: English, a stock Kokoro voice (no cloning), with subtitles taken from the same lines.

## Rule from the owner

Every finished video ships with its post caption and ONE cover photo (not several options), in the same message.
Cover: `python3 lib/cover.py <model module> "<empty background prompt>" OUT.jpg`. Keep it in `epNN/caption.md`,
in the language of the narration, with facts only from that episode's `facts.md`.
