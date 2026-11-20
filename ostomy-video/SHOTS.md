# Ostomy teaser: shot list

Job: remake the idea of a reference teaser, with our ostomy product pulled out of the bag instead of a paper.
The reference video and the product photo are NOT in this repository (it is public). They stay on the owner's private page.

## The reference, measured

- 20.4 s file, 576x1024 upright, 30 fps, with sound. The last 2.1 s is the app's own outro, not part of the idea.
  The idea itself runs about 18.3 s.
- One continuous take (no cuts) until the end card. The camera does not move: it lies INSIDE a bag, looking straight up
  at a clear blue sky through the opening. Dark fabric edges frame the left and right sides the whole time.
- No face. Only a woman's hands (rings, light nail colour) and a dark sleeve.
- Sound: silent for the first 0.5 s, then one continuous sound bed to the end. No voice-over was checked by ear;
  the owner should say if the reference has speech or only music.

| # | Time | What happens | Framing |
|---|---|---|---|
| 1 | 0.0-3.0 s | A hand holds the bag's straps closed above the lens, then lets go. Sky behind. | Hand centre-left, small in frame |
| 2 | 3.0-6.0 s | The arm in a dark sleeve reaches down into the bag toward the lens. The frame darkens as the sleeve covers it. | Sleeve fills the frame |
| 3 | 6.0-8.0 s | Both hands lift a crumpled white sheet out and start to open it against the sky. | Hands top and bottom, object centre |
| 4 | 8.0-15.0 s | The sheet is smoothed flat and held still: small brand name on top, two big words under it. This is the long hold (about 7 s) so the words can be read. | Object fills about 60% of the frame |
| 5 | 15.0-18.3 s | A white end card slides in over the shot: brand name only, centred, thin serif type. | Flat card |

Pacing: 6 s of build-up, 2 s reveal, 7 s hold, 3 s end card.

## Our version (same shots, our own everything)

| # | Time | Ours |
|---|---|---|
| 1 | 0-3 s | Same view from inside a bag, sky above. An original woman's hand opens the bag. |
| 2 | 3-6 s | Dark sleeve reaches in, frame darkens. |
| 3 | 6-8 s | Hands lift the PRODUCT out, folded. |
| 4 | 8-15 s | Product opened and held flat against the sky, front side to the lens. Our own caption under it (words to come from the owner). |
| 5 | 15-18 s | Our own end card: our brand name, our type, our colours. |

Not taken from the reference: its brand name, logo, paper design, footage, sound, end card.

Owner's rule: NO watermark on our video. No app logo, no account handle burned in, no generator mark.
The final file comes from our own builder, which adds none; any picture or clip that arrives with a mark is rejected.

## The product (from the owner's photo)

Navy-blue fabric piece with black edge binding: a wide curved body, a round opening with a black ring near the middle,
a clear window panel below it, a zip pocket on the left side, and a strap at each end. It must be shown exactly so.
It is built from the owner's photo, never invented by a picture model. Name and exact purpose: to be confirmed by the owner;
no medical claims beyond the product page.

The photo we have is dim, on a wooden desk, with a screen icon over the bottom. A clean one is needed
(flat, daylight, plain background, front and back).

## What free tools can and cannot do here

- Cannot: match filmed footage. Real cloth being unfolded by real hands, in one take, is beyond the free picture and
  motion tools (short 3.5 s clips, about 6 a day, and they redraw the product wrongly).
- Best result, zero cost: the owner films the 15 s take on a phone (phone in a tote bag, lens up, outdoors on a clear day).
  We then do the edit, caption, end card and sound.
- Nearest version without filming: an illustrated/animated remake. Sky and bag edges drawn in code, an illustrated hand
  (fingers counted on every frame), and the product cut out from the owner's clean photo, moved by our own video builder.
  It will look drawn, not filmed.

## Open questions for the owner

1. Product name and brand, exactly as they should appear.
2. Caption and end-card words ("coming soon" or something else).
3. Where it will be posted.
4. Film it himself, or the illustrated version.
5. A clean product photo (front and back) or the product page link.

## Checks before anything is sent

Every frame decodes; no watermark anywhere; fingers counted on every picture; product matches the photo; text readable on a phone.

## Version built (owner's later direction: realistic, pure code, "coming out of the paper bag")

Brand: SIIL Ostomy. Platform: Facebook. 1080x1920, 30 fps, 18 s, no watermark.

| Time | What happens |
|---|---|
| 0-2.2 s | Inside a kraft paper bag, looking up at the sky through the opening. The bag rustles. |
| 2.2-3.5 s | The frame darkens as the belt passes the lens. |
| 2.6-5.8 s | The belt is pulled up and out of the bag, swinging, then hangs in the opening. |
| 5.8-15 s | Hold. Caption on the bag wall from 9.2 s: SIIL OSTOMY / COMING SOON (placeholder until the owner confirms). |
| 15-18 s | White end card slides in: SIIL / OSTOMY. |

How it is made: `cut.py` cuts the belt out of the owner's own photo and paints over the sewn-in label (another
brand's name). `build.py` computes everything else: paper bag, light, sky, motion, sound. No hand is shown: a hand
drawn in code does not look real, so the belt is held from above, out of frame. The photo, the cut-out and the
video stay outside this public repository.

Honest limit: this is a computed scene around a real product photo. It is not filmed footage and does not pass for it.

## Final direction: realistic, generated (owner: "a hand pulls out the frosted bag with the brand name")

The pure-code version did not look real. This one does, using two open-source models on free endpoints:

| Step | Model (open-source repo) | Where it runs, free | Script |
|---|---|---|---|
| Photoreal key stills | FLUX (black-forest-labs/flux) | NVIDIA catalog endpoint | `still.py` |
| Real motion, 3.5 s per still | Wan 2.2 image-to-video (Wan-Video/Wan2.2) | Hugging Face Space, about 6 clips a day | `../history-indio/pipeline/wan_clip.py` |
| Edit, upscale to 1080x1920, sound, end card | our own code + ffmpeg | here | `assemble.py` |

| Time | Shot |
|---|---|
| 0-3.2 s | Inside a kraft paper bag looking up at the sky; a woman's hand (rings, dark sleeve) reaches in and covers the lens |
| 3.2-4.8 s | The hand lifts a frosted pouch, packed full with the folded black belt, up out of the bag |
| 4.8-11.5 s | Two hands hold the pouch against the sky: SIIL OSTOMY printed on it |
| 11.5-14.8 s | White end card slides in: SIIL / OSTOMY / COMING SOON (tagline is a placeholder: `TAGLINE=...`) |

Owner's rules applied: the belt is folded and fills the whole pouch, no gap; no watermark; no face.
Limits: the pouch and belt are generated, not the real packaging; the pull clip is cut after 1.65 s because the model
empties the pouch later in the clip; motion clips are 480x832 upscaled. Tried and not usable here: FLUX Kontext on the
NVIDIA catalog (accepts only its own example pictures), Qwen-Image-Edit Spaces (host not reachable from this machine).

### Version 3 (owner: "physics look AI, no hole in the middle, the hand is outside the plastic")

- The generated pull clip is gone: it was where the motion looked artificial. Now, as in the reference: the hand covers
  the lens, the frame goes dark, and the pouch is already held up against the sky.
- The held shot is ONE photoreal still moved by code only (pulled back from the lens, then hand-held drift), so the
  pouch, hands and letters cannot bend. Only the reach clip is generated motion.
- New hold still: the pouch is one solid black rectangle (no slit in the middle); both hands pinch its edges from outside.
- 12.96 s. Build: `assemble.py REACH.mp4 HOLD.jpg OUT.mp4`.

### Version 4 (owner: "the hand and sleeve must come from OUTSIDE the bag, in through the opening")

- Stills re-made: the paper walls surround the frame on all four sides; the arm is seen only through the opening,
  against the sky, coming over the rim. Nothing comes out of the paper walls.
- New reach clip from that still. First take showed a face looking into the bag (not allowed); second take, with
  "no face, no head" in the prompt, is clean and is the one used.
- Held shot: pouch and both hands are outside the bag, seen through the opening.

### Version 5 (owner: "the reach is correct; the pull must be seamless, no cut")

- No cut any more. The hand covers the lens, the frame goes dark, and that dark IS the black pouch on the lens:
  it then leaves the lens and rises out through the opening until it is held against the sky.
- How: `assemble.py` splits the hold still into two layers (hands + pouch keyed off the blue sky; the bag with a clean
  sky) and moves only the hands + pouch, so the bag stays put. In front of the paper while inside the bag, hidden by
  the rim once above it.
- The motion Space had no free quota left that day, so the pull is not generated motion: fingers do not flex in it.

### Version 6 (owner: "the physics is still not right, not smooth")

What was wrong in v5: the pull was a flat cut-out of the still, scaled by code. No real hand or pouch movement, and the
reach clip ran at 16 fps inside a 30 fps video.

What v6 does (all in `assemble.py`; clips from `wan.py`):

- **The pull is real generated motion, played backwards.** A clip was made FROM the hold still: the hands lower the
  pouch onto the lens. Reversed, the pouch leaves the lens, rises out of the bag (it tilts, the upper hand carries it,
  the lower hand comes to meet it) and lands exactly on the hold still. The last frame is therefore guaranteed.
- **True 30 fps.** In-between frames come from RIFE (hzwer/Practical-RIFE 4.25 lite, ONNX export
  `t9749/rife-4.25-lite-onnx` on Hugging Face, MIT), not from repeated frames.
- **Even steps.** Measured: the motion model moves in uneven steps (big, small, big, small, up to 3x apart), so a
  16 fps clip feels like 8. Both clips are re-spaced by their measured movement before interpolating: optical flow for
  the reach; the tracked size and position of the word SIIL for the pull. Unevenness of the movement per output frame
  (0 = perfectly even): pull 0.22 -> 0.14; the pouch's size change per frame is now one smooth slowing curve.
- **The join is physical, not an edit effect.** The palm closes on the lens (push-in, defocus, the light shut out);
  the pouch then lifts off the lens (optical pull-back on a minimum-jerk path with size = 1/distance, defocus clearing,
  light returning). One slow hand-held drift runs under the whole video.
- **The small word is kept right.** While moving, the motion model scrambles OSTOMY (OSEOMY, OBEOWT). SIIL stays
  correct, so it is tracked on every frame and OSTOMY is re-laid from the still at the right place and size.
- 13.2 s. Build: `assemble.py REACH.mp4 LOWER.mp4 HOLD.jpg RIFE.onnx OUT.mp4`.

Free quota that day: the Space counts GPU seconds (`wan.py` prints the request: 68 s for 3.5 s at 6 steps). Only 31 s
were left, so the pull clip is 2.0 s at 4 steps (exactly 31 s). Still open: the reach was generated in a different
paper bag than the hold; the dark moment hides the change, but with fresh quota the reach can be remade inside the
same bag (start from the hold still's bag with an empty opening).

### Review of v6 and version 7 (owner: "still not fluid smooth realistic, review it")

Measured on the v6 file (540x960 analysis copy):

| Section | Sharpness | What the measurement shows |
|---|---|---|
| Reach, 0.3-3.0 s | 76 | Three times softer than the hold: a 480x832 clip enlarged 2.3x |
| Cover + dark + lift-off, 3.0-4.0 s | 5-14 | One second that is mostly an effect made in code; 0.33 s fully black |
| Pull, 4.0-4.9 s | 152 | Real motion, but a 2 s / 4-step clip, backwards, enlarged |
| Hold, 5.3-9.9 s | 258 | With the camera drift removed, NOTHING in the picture moved: a frozen photo for 35 % of the video |

Also: the reach and the hold are two different paper bags; the reach hand changes shape oddly mid-move (model artefact).

v7 fixes the one thing fixable without new clips: the hold is alive. The hands' own small movements in the first five
frames of the pull clip are measured as optical flow and applied to the full-resolution still, back and forth. Sharpness
steps are closer (76 / 151 / 170). Not fixed, need fresh motion quota: one bag from start to end, a full-quality pull,
a sharper reach, a shorter dark. Honest ceiling: free 480p image-to-video stitched in three parts will not pass for one
filmed take; a current paid video model, or 15 seconds filmed on a phone, would.

### Brand change: ESTES (logo) / OSTOMY

Owner sent the ESTES logo file and asked for it on the pouch with OSTOMY under it. `assemble.py` with `LOGO=<file>`:
the lettering the picture model wrote (SIIL / OSTOMY) is erased on the hold still and on every clip frame, and the real
logo is laid in its place, following the tracked position and size; the end card uses the same lock-up. The logo is cut
from the owner's file, never redrawn by a model. The logo file stays outside this public repository.
`still.py` still asks the picture model for "SIIL": that word is only the tracking target and is replaced.
OSTOMY is set in spaced capitals (Inter) to match the wordmark; the owner wrote "Ostomy". Tagline still a placeholder.

Logo turned (owner: "rotate the logo to the right so it's like landscape"): `LOGO_TURN=right` turns the lock-up a
quarter turn clockwise on the pouch and sets it larger along the pouch's long side (reads with the pouch held
landscape). The end card stays upright.

Logo small and 4K (owner: "just small, subtle, in the middle" and "ensure it's HD 4K"):
- `LOGO_SIZE=1.15 LOGO_OPACITY=0.85`: small lock-up in the middle of the pouch's black face (still turned right). The
  old lettering is now wiped wide and smoothed on every frame, because the small lock-up no longer covers its place.
- `SCALE=2` gives 2160x3840. The sources are only 480x832 (clips) and 768x1344 (still), so `UPSCALE=<model>` runs every
  clip frame and the still through Real-ESRGAN general-x4v3 (xinntao/Real-ESRGAN, BSD-3; ONNX export
  `tamnvcc/Real-ESRGAN-General-x4v3_float` on Hugging Face; `upscale.py`, CPU, about 4 s per clip frame) before they
  are placed, and the lock-up and end card are drawn at 4K. Honest: this is a 4K file with sharper edges and lettering,
  not footage shot in 4K; fine paper and skin texture is the upscaler's guess.
