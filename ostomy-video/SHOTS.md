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
