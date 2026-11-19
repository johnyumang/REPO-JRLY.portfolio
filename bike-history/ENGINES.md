# Bike History: engines and licences

Licence files were read on 2026-11-19 (the LICENSE file of each repository). Free tools only.

| Tool | Licence (as read) | Use here |
|---|---|---|
| Blender, as the `bpy` Python module (github.com/blender/blender) | GNU GPL | MAIN ENGINE. Headless, CPU, Cycles. The GPL covers the program, not the pictures it renders. Our scripts import `bpy`, so if they are published they are GPL-compatible code. |
| three.js (github.com/mrdoob/three.js) | MIT | Spare renderer (already used in history-indio/engine3d). Not needed so far. |
| BlenderProc (github.com/DLR-RM/BlenderProc) | GPL-3.0 | Not used; plain `bpy` was enough. |
| microsoft/TRELLIS | MIT | Image-to-3D fallback, not used. Meshes come out as one fused lump. |
| VAST-AI-Research/TripoSR | MIT | Same, can run on CPU. Not used. |
| TencentARC/InstantMesh | Apache-2.0 | Same. Not used. |
| Tencent-Hunyuan/Hunyuan3D-2 | Tencent Hunyuan 3D 2.0 Community License: its own terms, and it says it does not apply in the EU, UK and South Korea | AVOID until the owner reads it. |
| Stability-AI/stable-fast-3d | Stability AI Community License: its own terms (free use has conditions) | AVOID until the owner reads it. |
| ahujasid/blender-mcp | MIT | Drives a desktop Blender; needs the owner's computer. Later. |
| Pillow, NumPy, SciPy, soundfile, ffmpeg | open source | 2D drawing, sound synthesis, encoding. |
| Fonts: Anton, Archivo Black (history-indio/pipeline/fonts) | SIL OFL | On-screen text. |

## What we learned on this machine (4 CPU cores, no GPU)

- EEVEE needs a graphics driver; with software Mesa it took 30 to 40 s a frame. Not usable.
- Workbench is fast (0.4 s) but flat.
- Cycles on CPU, 12 samples, 1 bounce, no denoiser, transparent film: about 2 to 4 s a 720x1280 frame.
- A full-frame shadow-catcher ground made every frame about 3x slower, so the ground shadow is drawn in 2D.
- `bpy.ops.object.transform_apply` applies location and rotation too unless told not to: always pass all three flags.
- Setup: `pip install bpy numpy pillow scipy soundfile`, plus the Mesa/X libraries listed in history-indio/blender/setup.sh.
