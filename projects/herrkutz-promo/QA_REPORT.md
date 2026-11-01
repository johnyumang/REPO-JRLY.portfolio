# Herrkutz Barbershop: final QA report and fix log

**Deliverables**
| File | Length | Use |
|---|---|---|
| `HerrkutzAd15.mp4` | 15.0 s · 450 frames · 720×1280 · −13.6 LUFS | Paid ads (Reels / TikTok / Shorts / Stories) |
| `HerrkutzPremium30.mp4` | 30.0 s · 900 frames · 720×1280 · fixed (v2) | Organic posts, longer placements |

---

## 1. How the QA was done (measured, not eyeballed)
`premium/qa.py` runs on the finished MP4. Re-run it after any change:

| Check | Method | What counts as a fail |
|---|---|---|
| Flash frames and flicker | Average brightness (YAVG) of every frame; a jump of more than 12 that isn't at a planned cut | Any hit |
| Hidden cuts in the source | `select=gt(scene,0.08)` on the raw upload | A shot whose source range crosses one |
| Jump cuts and repeated shots | Similarity (SSIM) between the last frame before each cut and the first frame after it | Above 0.75 on the same angle |
| Duplicate / frozen frames | Similarity of each frame to the next; `freezedetect` | Above 0.995 inside a moving shot |
| Exposure pumping | 2nd-difference of YAVG per shot | mean > 2 |
| Frame-exact timing | Count every frame | Not exactly 450 or 900 |
| Audio clicks | Biggest sample-to-sample jump within ±1 ms of each cut, compared with the median | A spike that isn't one of the planned hits |
| Readability | Visual check of every caption over its background | Text over the white cape |

## 2. What was found in the first 30s premium cut, and how each was fixed

| # | Type | Where | Cause | Fix |
|---|---|---|---|---|
| G1 | **Glitch: 3 flash frames** | 11.67–11.73 s | The clipper shot ran past a hidden source cut at 15.167 s, so 3 frames of the night sign appeared | The shot now ends at 15.147 s |
| G2 | **Glitch: 8 wrong frames** | 22.00–22.27 s | The night-sign shot started at 15.00 s, before that hidden cut, so the interior shot showed first, under the "door is open" caption | It now starts at 15.20 s |
| G3 | **Glitch: 2 stray frames** | ≈9.43 s | A shaping shot crossed the hidden cut at 9.933 s (ceiling) | The shot now ends at 9.90 s |
| G4 | **Glitch: stray frames under the reveal** | 15.27 s | The reveal started at 32.55 s, before the hidden cut at 32.60 s | It now starts at 32.62 s |
| F1 | **Awkward flicker: white flash** | 15.27–15.53 s | A full-white fade, with brightness 235 dropping 15 per frame for 8 frames | Replaced with a soft 45%-strength white bloom that eases out over 0.3 s |
| F2 | **Phone auto-exposure pumping** | before shot, door shots | The phone camera adjusting brightness on its own | Every live shot gets `deflicker=size=7:mode=pm` |
| F3 | **Zoom stepping** | slow push-ins, split screen | `zoompan` rounds position to whole pixels, so slow zooms move in visible steps | Zoom at 3× resolution, then downscale with Lanczos (sub-pixel smooth) |
| R1 | **Jump cut** | 3.00 s | BEFORE was two pieces of one continuous take | Merged into one 4.5 s shot |
| R2 | **Jump cut** | 8.50 s | Two pieces of one take of the barber shaping | Merged into one 2.0 s shot |
| R3 | **Jump cut** | 10.50 s | Wide clipper shot and tight clipper shot were one take | Merged into one 2.27 s shot |
| R4 | **Repeated footage** | 12.25–15.25 s | The source ranges overlapped by 0.5 s and 0.2 s, so the same moments played twice | Replaced by one 3.0 s walk-through shot (29.55–32.55 s) |
| R5 | **Repeated shot** | 23.27 s | Two storefront exteriors from almost the same angle, back to back | Replaced the first with a hand pushing the door open (26.5 s) |
| T1 | **Text 1 frame out of sync** | from 11.7 s on | Shot lengths of 37.5 frames got rounded, pushing every later cut 1 frame | Frame-exact edit list (`edl2.py`, asserts 900 frames) |
| A1 | **Warbly audio** | slow-motion shots | Original audio was time-stretched with `atempo` | Slow-motion shots use real-time audio from the same moment |
| A2 | **Possible clicks at cuts** | every cut | Audio was cut hard | 12 ms fade in and 15 ms fade out on every shot |
| L1 | **Caption hard to read** | captions over the white cape | Low contrast | Subtle dark gradient over the bottom 40% of the frame; "…to this." moved to the top |

**Result after the fixes:** no flash frames, no shots shorter than 4 frames, and cut similarity of 0.51–0.72, so every cut is a real change of shot. Exactly 900 frames (30s) and 450 frames (15s). The big audio values at the cuts are the planned boom, whoosh and snip hits.

## 3. The 15-second ad: structure (Hook + 3)
Research basis: the opening seconds decide the hook rate (3 s on Meta, 2 s on TikTok); a 15 s ad has room for a hook, a proof point and a call to action; nothing should sit still in the first two seconds; use vertical 9:16; include a location tag.

| Time | Frames | Shot (source) | Layer / move | Text | Music / SFX |
|---|---|---|---|---|---|
| 0.00–1.50 | 45 | **HOOK, BEFORE:** long hair, caped (0.00–1.20 s at 0.8×), grey grade | Slow push-in, then a zoom-through with motion blur at the end | BEFORE · *From this…* | Mozart enters on beat 1 |
| 1.50–2.50 | 30 | Barber pole (3.00 s) | Zoom-out settle (1.35→1.0) | HERRKUTZ | Whoosh |
| 2.50–3.50 | 30 | Scissors up, branded chair (4.40 s) | Micro push | MEASURED. | Scissor snips on the beat |
| 3.50–4.50 | 30 | Comb and shears (6.20 s) | Micro push | SHAPED. | Snips |
| 4.50–5.50 | 30 | Clipper at the nape (14.00 s) | Micro push | DETAILED. | Clipper hum |
| 5.50–6.00 | 15 | Push toward client (32.00 s) | Fast push, then zoom-through with blur | — | Whoosh |
| 6.00–8.50 | 75 | **AFTER reveal** (32.62 s, 0.3× slow motion) | Zoom-out reveal (1.30→1.0), white bloom, warm light leak | AFTER · *…to this.* | **Full strings plus low boom** (phrase 2) |
| 8.50–12.00 | 105 | **Split screen BEFORE / AFTER** (stills at 0.30 s and 32.80 s) | Slow push on both halves, gold divider | BEFORE / AFTER · *Walk in. Walk out sharper.* | Strings continue |
| 12.00–15.00 | 90 | **Call to action:** storefront at night (18.00 s, 0.5×) | Zoom-out reveal, light leak, gold light sweep over the logo | HERRKUTZ · BARBERSHOP · **1170 P. Jacinto St., Brgy. 165 · Bagbaguin, Caloocan City** · WE'RE OPEN | Final G-major chord, shimmer, fade out |

**Music:** Mozart, *Eine kleine Nachtmusik* K.525, opening of the first movement. The composition is public domain, and this recording was synthesized here, so it's free to use in ads. It plays at 160 BPM, so each 4-bar phrase lasts 6.0 s and phrase 2 starts exactly on the reveal at 6.0 s.

**Visual layers:** all generated in this edit, with no downloaded stock assets:
- zoom-through transitions with motion blur
- zoom-out reveals
- a slow-motion ramp into the reveal
- a soft white bloom
- warm light leaks at 6.0 s and 12.0 s
- a gold light sweep over the logo at 12.55 s
- the split-screen comparison
- a grey "before" and warm "after" colour grade
- film grain and a vignette

## 4. Before publishing
- Confirm the BEFORE and AFTER client is the same person, because the ad's promise depends on it.
- Check the address spelling on the end card: **1170 P. Jacinto St., Brgy. 165, Bagbaguin, Caloocan City**.
- If the platform allows, upload at 1080×1920. The source is 720p, so this is upscaled and gains no real detail.

## Sources (research, Nov 2026)
- Hook and length: [Stackmatix, TikTok hook-first 3 seconds](https://stackmatix.com/blog/tiktok-creative-best-practices-2026) · [Segwise, frame-by-frame ad anatomy](https://segwise.ai/blog/anatomy-top-performing-video-ad-frame-by-frame) · [Fluxnote, video ad length](https://fluxnote.io/guides/how-long-should-video-ads-be) · [Tiger Pistol, vertical video best practices](https://tigerpistol.com/vertical-video-ad-best-practices/) · [marketingagency.sg, Video ads guide 2026](https://marketingagency.sg/video-ads-guide/)
- Editing techniques: [Kapwing, speed ramp](https://www.kapwing.com/resources/how-to-use-the-speed-ramp-effect/) · [CapCut, zoom transitions](https://www.capcut.com/resource/zoom-transition-in-premiere-pro) · [Imagineer, zoom plus blur](https://blog.imagineersystems.com/blog/how-to-do-a-zoom-transition-in-premiere-pro-4-steps) · [Pippit, barber before/after templates](https://www.pippit.ai/templates/before-after-barber)
- Barbershop promo and prompt structure: [Fluxnote, barbershop promo videos](https://fluxnote.io/guides/how-to-make-promo-videos-for-barbershop) · [Renderforest, AI video editor prompts](https://www.renderforest.com/blog/ai-video-editor-prompts) · [Invideo, salon/barbershop promo](https://info.invideo.io/best-ai-create-salon-barbershop-promo-video-invideo)

Most of these are vendor blogs, so treat their benchmark numbers as directional, not as Meta or TikTok documentation.

---

## 5. Variant: `HerrkutzPunk15.mp4` (15 s, punk, bright and vivid)
**Look:** saturation ×1.65, lifted exposure, no vignette, no dark frames. BEFORE is bright black-and-white xerox at a choppy 8 fps. The end card is a pink-to-yellow duotone.

**Techniques:**
- an RGB split and camera-shake hit on every cut
- a stop-motion before shot
- a zoom punch with motion blur
- a slow-motion reveal with a 2-frame pink/yellow stamp; that's the only flash, kept under 3 per second for photosensitivity safety
- a torn-paper split screen
- ransom-note text that slams in
- a 180 BPM original punk-rock track (E-C-G-D) with stop-time breaks on the reveal and end card

**AI-generated B-roll:** four stills made with Canva AI. They show objects and graphics only, with no people and nothing from the real shop. Each appears for 0.33 s as a posterized, xerox-style insert:
| Time | Image | Canva media id |
|---|---|---|
| 1.00–1.33 | Clippers in a paint explosion | MAHZrskRHck |
| 2.33–2.67 | Razor and scissors on hot pink | MAHZri9sRH8 |
| 4.00–4.33 | Flying hair clippings on blue | MAHZrl-BG4w |
| 11.33–11.67 | Graffiti barber pole | MAHZrh02OQE |

These are 112×199 previews (`punk/ai/`), because this environment's network policy blocks `media.canva.com`. Allow that domain and re-render to use the full 944×1680 images.

| Time | Shot | Text |
|---|---|---|
| 0.00–1.00 | BEFORE (stop-motion) | BAD / HAIR / DAY? |
| 1.00–1.33 | AI clippers | — |
| 1.33–2.33 | Barber pole | HERRKUTZ / BARBERSHOP |
| 2.33–2.67 | AI razor | — |
| 2.67–4.00 | Scissors, comb | SNIP. / SHAPE. |
| 4.00–4.33 | AI hair | — |
| 4.33–5.33 | Clipper, zoom punch | BUZZ. |
| 5.33–8.33 | AFTER reveal (0.28× slow motion) | AFTER / FRESH. |
| 8.33–11.33 | Torn split BEFORE/AFTER | WALK IN. / WALK OUT SHARPER. |
| 11.33–11.67 | AI graffiti pole | — |
| 11.67–15.00 | Duotone storefront | HERRKUTZ · BARBERSHOP · 1170 P. JACINTO ST., BRGY. 165 · BAGBAGUIN, CALOOCAN CITY · WE'RE OPEN · PULL UP. |

QA: 450 frames; the only brightness jump is the planned reveal stamp at 5.4 s; cut similarity 0.40–0.73; −15.5 LUFS, peak −2.6 dBFS. The reveal stays inside the source take (32.62–33.46 s).

---

## 6. Fix: AFTER haircut cropped in the split screens
**Where:** the split screens in all three cuts (premium 30s at 17.8–22.0s, classical 15s at 8.5–12.0s, punk 15s at 8.3–11.3s, so around the 11s mark in both 15s cuts).
**Cause:** the AFTER half was cut from source rows 520–1160. The new haircut starts at about row 410, so the top of the cut, the most important part, was missing.
**Fix:** the AFTER crop now starts at row 300, giving about 110 px of headroom above the hair even after the slow zoom-in. BEFORE moved to row 240. All three cuts were re-rendered.

---

## 7. Variant: `HerrkutzModern15.mp4` (15 s, modern, viral, "Premium haircut, starts @ ₱130")
Viral formula: the result first with a price hook, then a rewind, then the before, fast process cuts, the reveal, the before/after, and the price card.

| Time | Shot | Captions (word pop, white with a yellow keyword) | Audio |
|---|---|---|---|
| 0.0–1.0 | AFTER, tight on the haircut | ₱130 FOR / **THIS?** | Drop playing |
| 1.0–1.5 | Rewind (walk-through reversed at 2×, RGB smear) | ◀◀ REWIND | Tape-rewind sweep |
| 1.5–3.0 | BEFORE (desaturated) | WALKED IN / **LIKE THIS…** | Beat rebuilds |
| 3.0–7.0 | 8 process shots, 0.5 s each on the beat, zoom settle on each cut | **CUT. SHAPE. DETAIL. FINISH.** | Pops and whooshes |
| 7.0–9.0 | AFTER reveal (0.28× slow motion) | WALKED OUT / **LIKE THIS.** | Riser, then boom and drop |
| 9.0–11.5 | Split: BEFORE on top, AFTER slides in (full haircut visible) | BEFORE · AFTER · **STARTS @ ₱130** | |
| 11.5–15.0 | Bright card over a blurred storefront | PREMIUM HAIRCUT · STARTS @ **₱130** · HERRKUTZ BARBERSHOP · 1170 P. Jacinto St., Brgy. 165 · Bagbaguin, Caloocan City · WE'RE OPEN | Cash-register "ching" on the price |

There's also a yellow progress bar along the bottom, a common retention cue. Music: an original 120 BPM bounce track (Am–F–C–G); 1 beat = 15 frames, so every cut lands on a beat.
QA: 450 frames; the only brightness jump is the planned 2-frame white pop on the reveal at 7.07 s; cut similarity 0.58–0.75; about −14 LUFS.
