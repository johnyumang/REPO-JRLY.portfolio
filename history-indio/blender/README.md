# Blender proof shot (real character movement, free, CPU only)

`bash setup.sh` once, then `bash render.sh` → `/opt/bl/out/host_shot.mp4` (4 s, 24 fps, 720x1280). Never commit MP4s.

- **Blender**: `pip install bpy` (5.3.0, Python 3.13) in a venv. It needs Mesa GL/Vulkan libraries installed (`setup.sh`) or it crashes on start.
- **Character**: VRoid sample `HairSample_Male.vrm` from github.com/madjin/vrm-samples, licence CC0 (stated in the file's VRM meta). Fetched at setup, not committed. Imported with Blender's glTF importer (file renamed `.glb`); no VRM add-on needed. `host_shot.py` re-dresses it: brown skin tint, indigo vest (sleeves shaded as bare arms), red headband with tails, red sash, gold earrings.
- **Look** (`.claude/skills/anime-style`): unlit 3-step toon shader from N·L of one key light with constant colour ramps, hard terminators, inverted-hull outlines (Solidify, flipped normals), cel flame aura, speed lines, impact frame.
- **Animation**: key poses in `host_shot.py` (`COIL`, `WIND`, `STRIKE`, `OVER`, `HOLD`), blended and sampled on twos (on ones through the strike); feet planted with a hand-written two-bone IK; face via the model's morph targets; camera on ones.

## Measured (4 CPU cores, no GPU, 720x1280)
- Cycles, 12 samples: 5.6 s/frame (96 frames in 9 min).
- EEVEE on software GL, 8 samples: 5.5 s/frame after a 35 s shader warm-up. No advantage.
- A 3-minute video at 24 fps is 4,320 frames ≈ 6.7 hours of rendering; about half that if held shots render on twos.

## Not working / limits
- No cast shadows (shading is N·L only) and no hair or cloth physics: hair and cloth use Wave modifiers, VRM spring bones are ignored.
- The sample model is a generic VRoid body in a hoodie; it is recoloured, not a true likeness of the host. A proper host needs a custom VRoid Studio model (free, but a desktop app).
- Every action must be posed by hand in code (about 30 lines per action). No motion capture library is wired in.
- Backgrounds are simple procedural shapes, far below the painted Figma stills.
