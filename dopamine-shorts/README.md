# dopamine-shorts

19.0 s vertical (1080x1920) "dopamine" shorts: a first-person ride that passes through impossible worlds and loops.
No video or audio is kept in this repository; everything is rebuilt from these scripts in a scratch folder.

| Script | What it does |
| --- | --- |
| `still.py` | Photoreal 9:16 still on the free NVIDIA endpoint (world plates without the bike, and the bike cockpit on green). |
| `comp.py` | Keys the one cockpit and pastes it on a plate, so the bike is identical in every shot (first frames for image-to-video). |
| `wan.py` | Image-to-video on the Wan 2.2 Space (480x832, 16 fps). The free GPU quota is about six 4 s clips a day. |
| `ride.py` | CPU ride engine, no GPU: depth-map forward dolly with parallax, separate bike layer, suspension jolts, ballistic particles, grain. Needs `../models/depth_s.onnx` (Depth Anything V2 small, ONNX). |
| `suspension.py` | Adds suspension-driven camera jolts to an existing clip. |
| `sfx.py`, `sfx2.py` | Synthesized soundtrack (no samples, no music): beds, beat, fork thuds at the simulated bump times, impacts at cuts. |
| `assemble.py` | Joins shots with full-frame colour dips, builds the soundtrack, muxes to exactly 19.0 s. |
| `build.py` | Older assembler for image-to-video clips and still push-ins. |
| `sheet.sh` | Contact sheet of a clip for frame-by-frame checking. |

`shots/*.json` are the seven shots of video 1 (forest, puddle, whale, skyscraper, lava, ringed planet, forest).

Rules: no brands, logos, real people or text in the pictures; loudness about -14 LUFS, true peak at or under -1 dBTP;
every video is checked frame by frame by a reader who did not make it. Sources are 768x1344 stills and 480p clips, so
1080x1920 is the honest master size.
