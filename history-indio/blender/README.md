# Blender proof shot (real character movement, free, CPU only)

`bash setup.sh` once, then `bash render_limahong_clips.sh` → `/opt/bl/out/clips/c02.mp4, c31.mp4, c39.mp4, c41.mp4` (30 fps, 720x1280, silent).
One shot: `python host_shot.py --model host.glb --out frames/ --shot greet|twist|point|powerup --seconds N`.

Shots: `greet` (turns to the viewer, raises a cup), `twist` (back to camera, snaps round, impact frame), `point` (lunges and points at the viewer), `powerup` (fist raised, gold aura). Set: night beach village in the colours of `videos/limahong-1574/keys/k02.png`. To add a shot, copy a `shot_*` function: key poses, a mouth/eye function, camera keys, effect keys.

- **Blender**: `pip install bpy` (5.3.0, Python 3.13) in a venv. It needs Mesa GL/Vulkan libraries installed (`setup.sh`) or it crashes on start.
- **Character**: VRoid sample `HairSample_Male.vrm` from github.com/madjin/vrm-samples, licence CC0 (stated in the file's VRM meta). Fetched at setup, not committed. Imported with Blender's glTF importer (file renamed `.glb`); no VRM add-on needed. `host_shot.py` re-dresses it: brown skin tint, indigo vest (sleeves shaded as bare arms), red headband with tails, red sash, gold earrings.
- **Look** (`.claude/skills/anime-style`): unlit 3-step toon shader from N·L of one key light with constant colour ramps, hard terminators, inverted-hull outlines (Solidify, flipped normals), cel flame aura, speed lines, impact frame.
- **Animation**: key poses in the `shot_*` functions, blended and sampled on twos (on ones through the strike); feet planted with a hand-written two-bone IK; face via the model's morph targets; camera on ones.

## Measured (4 CPU cores, no GPU, 720x1280)
- Cycles, 12 samples: 5.6 s/frame (96 frames in 9 min).
- EEVEE on software GL, 8 samples: 5.5 s/frame after a 35 s shader warm-up. No advantage.
- A 3-minute video at 24 fps is 4,320 frames ≈ 6.7 hours of rendering; about half that if held shots render on twos.

## Not working / limits
- Mouths flap on twos; they are not lip-synced to the words.
- No cast shadows (shading is N·L only) and no hair or cloth physics: hair and cloth use Wave modifiers, VRM spring bones are ignored.
- The sample model is a generic VRoid body in a hoodie; it is recoloured, not a true likeness of the host. A proper host needs a custom VRoid Studio model (free, but a desktop app).
- Every action must be posed by hand in code (about 30 lines per action). No motion capture library is wired in.
- Backgrounds are simple procedural shapes, far below the painted Figma stills.
