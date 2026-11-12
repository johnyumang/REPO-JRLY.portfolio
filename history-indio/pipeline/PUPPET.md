# Puppet rigs: real movement on the painted stills (local, CPU, free)

The user approved this look on 2026-11-12: the painted Figma still itself moves (head, arms, breathing, hair,
cloth, fire, steam, water, blinks), keeping full painted quality. It is NOT AI video and needs no token.

## How it plugs in
`build_anime.py` uses `videos/<slug>/rigs/kNN.json` automatically for any line whose keyframe is `kNN.png`.
Stills without a rig keep the old depth-parallax. Rigged shots do not get the `fx` list from `shots_fx.json`
(embers, aura, speed lines): put sparks, flames and shake in the rig instead.

## Make a rig for one still (about 5 minutes)
1. `python pipeline/puppet_still.py --grid videos/<slug>/keys/kNN.png /tmp/kNN_grid.jpg` and LOOK at it.
   All rig coordinates are in that 720x1280 grid. For eyes: `--zoom still.png out.jpg X0 Y0` (300 px crop, 3x).
2. Write `videos/<slug>/rigs/kNN.json` (copy `videos/limahong-1574/rigs/k02.json`).
3. Preview: `python pipeline/puppet_still.py rigs/kNN.json keys/kNN.png /tmp/kNN.mp4 --seconds 4`, pull a few
   frames with ffmpeg and LOOK: nothing should tear, smear or drag the background visibly.

## Rig format
```json
{"camera": {"zoom": [1.0, 1.07], "focus": [x, y], "shake": {"at": 0.4, "amp": 14, "len": 0.5}},
 "blink":  {"skin": [x, y], "eyes": [{"c": [x, y], "r": [rx, ry], "tilt": deg}], "times": [1.1, 4.4]},
 "effects": [ ... ]}
```
Masks: `{"ellipse": [cx, cy, rx, ry, angle]}` or `{"poly": [[x, y], ...]}`, or a list of them (union);
`"minus": true` subtracts; `"soft"` is the feather in px (default 25). `at` = `[start, in, hold_end, out]` as
fractions of the shot (0 to 1), so a gesture fits any line length.

| fx | what it does | keys |
|---|---|---|
| `turn` | rotates a region about a pivot: idle sway plus an optional gesture | `mask, pivot, sway, speed, phase, gesture, at, lift` |
| `bob` | slides a region back and forth (boats, floating things) | `mask, dx, dy, speed` |
| `breath` | chest rises and falls | `ellipse, amp, period` |
| `wind` | travelling wave (hair, cloth, flags, sails, leaves, smoke) | `mask, amp, wave, speed, axis` |
| `flame` | fire licks upward and flickers | `mask, amp` |
| `shimmer` | water glints | `mask, amp, speed` |
| `glow` | flickering light on an area | `mask, amount` |
| `sparks` | rising embers | `box [x0, x1, y_bottom, y_top], n, color (BGR), drift` |
| `steam` | soft rising puffs (steam, mist; dark `color` for smoke) | `from, rise, spread, size, color, strength` |

## Rules that keep it clean
- Small moves only: head turn 3 to 5 degrees, arm gesture 5 to 8 degrees, sway 1 to 2 degrees. Bigger tears the paint.
- Pivot = the joint (neck base, elbow, shoulder), not the middle of the part.
- Feather generously (soft 25 to 45) and keep masks off high-contrast background edges.
- `shimmer` is a sideways ripple, not a glint: it shreds anything solid inside its mask. Subtract hulls, posts and rocks from water masks (`"minus": true`) and keep `amp` about 1.5 to 2.
- `steam` `size` is a multiplier (about 1 to 2), not pixels; big values wash out the frame and render very slowly.
- `skin` for blinks = a clean patch of cheek right under an eye. Skip `blink` if eyes are tiny, closed or hidden.
- Every shot gets at least: one character motion, one ambient motion (wind, water, fire, clouds), and the camera.
- It cannot do walking, turning around or a new pose. For those, generate a second still and cut.
