# Style presets

Paste the style block unchanged at the start of every keyframe prompt in a video. End every prompt
with: `Vertical 9:16. No text, no logos, no watermarks.`

| Preset | Style block |
|---|---|
| komiks (default) | Classic Filipino komiks illustration: bold black ink outlines, flat colours with halftone dot shading, aged newsprint paper texture, dramatic panel composition, hand-lettered feel, 1970s Pinoy comic-book cover energy. |
| explainer-3d | Semi-realistic 3D CGI render in the style of viral 3D explainer shorts: realistic anatomy with slightly stylised proportions, detailed skin with subsurface scattering, realistic cloth and hair, clean physically based materials, dramatic cinematic studio lighting, shallow depth of field, crisp high-detail render. |
| anime-modern | Modern Japanese TV anime: crisp clean line art, cel shading with two-tone shadows, vivid saturated colour, painted skies with light rays, dynamic low-angle composition. |
| anime-90s | Retro 1990s hand-drawn anime cel: hand-inked outlines, flat cel colours with hard shadows, hand-painted gouache backgrounds, slight film grain, muted nostalgic palette. |
| feature-3d | High-end stylised 3D animated feature look: appealing expressive character design, soft global illumination, rich colour, detailed fabric and hair, cinematic rim light, gentle depth of field. |
| painterly | Painterly stylised animation: 3D forms with visible hand-painted brush strokes, graphic-novel ink accents, bold lighting with teal and magenta contrast, gritty textured detail. |

## Model choice (ElevenLabs creative tools)
- Hero frame and plain text-to-image: the tool's default image model.
- Any keyframe that must match a character sheet: a model that takes reference images and holds a
  character across shots (the tool description names which; at time of writing `gemini-3-pro-image`),
  with the sheet attached via `connect_from`.
- List what the workspace can run with `creative_get_flow_node_types` before choosing; model names
  change.
- A "free generations are busy" error means nothing was charged. Do not retry in the same turn.

## Prompt shape
`<style block> Scene: <who, described by clothes and build>, <one action>. <setting>. <camera:
low angle / close-up / wide>. <lighting>. Vertical 9:16. No text, no logos, no watermarks.`

For real public figures in `explainer-3d`, describe hands, podiums, name plates and silhouettes —
not a face.
