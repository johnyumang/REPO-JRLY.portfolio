# CONSISTENCY — ep10v2 Batang Indio, 51 stills (`full/bk_NN.jpg`, 768x1344)

## Corrections after this audit (16 Nov, on central's list)

- **bk_32** redrawn (draw c13): Usman's own right ear folded, left ear up; hero's left hand 4 fingers + thumb, right hand resting on the dog; handkerchief on the left wrist. Replaces the code-painted ear.
- **bk_35** redrawn (draw c8): topknot on top of the head (no ponytail), handkerchief on the left wrist, one person, no dog.
- **bk_24** corrected in code: the white front paw and the white chin tuft darkened to Usman's black (the white chest patch stays; it is in his cast line).
- **bk_18** corrected in code: the pseudo-letters on the medal rim smoothed into a plain raised rim.
- **Backpack colour:** the earlier note "cast sheet says brown" was this audit's briefing error. `characters/series_cast.json` named no colour; it now says "a small charcoal backpack", which is what all 51 stills show.
- **Empty classroom (central's second list):** bk_09, bk_12, bk_14, bk_17, bk_45, bk_48 and bk_51 were re-framed in code from the same paintings: cropped closer on the speaker, and the room behind the speaker blurred and darkened by depth, so the empty desks no longer read against the full class of bk_10. No new drawing.
- **bk_18** the medal boy's hair darkened from brown to black; **bk_31** Ma'am Celia's blouse graded from cream to her yellow; **bk_22** re-framed lower so Indio's face is not cut at the chin.
- **bk_52** Lolo does wear his glasses in this close-up (thin wire frames, eyes lowered); nothing changed.


Audit C. Method: the 20 redrawn / mirrored stills (04, 05, 06, 08, 09, 13, 16, 20, 23, 24, 25, 26, 30, 32, 35, 36, 37, 43, 44, 47) and the 5 stills with code-added writing (09, 14, 40, 42, 53) were looked at whole, then every hand, small face, animal and wrist was cropped at 3x (`/opt/work/build/ep10v2/audit_crops_c/C_NN_*.jpg`, contact sheets `sheet_NN_*.jpg`) and looked at again. The other 31 rows are carried over, condensed, from `audit_A.md` / `audit_B.md` and were NOT re-inspected (marked "carried"). Pixel areas are (x0-x1, y0-y1) in the 768x1344 still. "Own left/right" = the character's own side. bk_41 and bk_46 do not exist.

Totals: REDRAW 1 · MINOR 19 · OK 31.

## Worst first

**REDRAW**

1. **bk_32** — Usman has BOTH ears erect and pointed (own right ear 465-545, 465-625 fully upright; own left ear 625-735, 540-690 pointed outward). No folded ear at all, on a close-up of the dog; mirroring cannot fix it. An inpaint of the own-right ear only (465-545, 465-625) would be enough. Also grey-white toes on all four paws (280-610, 1220-1320) and a tail that lies far from the body (65-200, 1215-1305). **FIXED after this audit: the own-right ear was repainted in code as a folded ear (the three fresh draws all had two erect or two dropped ears); now MINOR (flat-looking fold at 3x, grey-white toes).**

**Notable MINOR (new look)**

2. **bk_37** — red handkerchief hangs at the LEFT ELBOW / backpack edge (655-768, 1060-1255), not on a wrist; his left hand (185-300, 880-1000) has a bare wrist.
3. **bk_35** — hair is tied as a low ponytail at the back of the head (500-570, 515-600), not a topknot on the crown.
4. **bk_24** — white "sock" on Usman's front paw (430-500, 835-890) and white chin (265-340, 520-565); folded ear only half folded (110-240, 255-370).
5. **bk_43** — Usman's eyes are bright yellow (225-300, 585-640 and 460-500, 560-610); brown / amber in 05, 08, 24, 32.
6. **bk_05** — white toes on Usman's front paw (215-300, 1250-1320), white streaks on chest (150-330, 1010-1150).
7. **bk_30** — stray grey vertical pole in the classroom (148-172, 360-800); pupils' shirts blue-grey, not white.
8. **bk_06** — lens in the fist is ring-sized (250-292, 968-1012), not palm-sized.
9. **bk_08** — white bib runs from chest down the belly (380-470, 540-860).
10. **bk_25** — raw whole banana on a stick (360-475, 620-790); girl has two braids.

**Notable MINOR (carried, not re-inspected)**

11. bk_15 — handkerchief knotted at upper arm / strap (560-750, 780-990), not on the left wrist.
12. bk_34 — indoor window frame and sill pasted into the open yard (50-215, 190-720; 200-768, 700-900).
13. bk_38 — huge open book floats against the tree, held by nothing (60-768, 70-810).
14. bk_18 — gibberish lettering round the medal rim (345-430, 305-390); medal boy has brown centre-parted hair.
15. bk_07 — main boy's two hands are fingerless blobs (570-605, 645-685; 640-690, 650-695).
16. bk_10 — melted half-faces (140-170, 465-560); teacher's hands blobs (540-600, 470-500).
17. bk_11 — raised hand shows palm creases although seen from behind (210-530, 140-510).
18. bk_01 — 3-4 finger blob hand with no arm (228-248, 490-520); smudged face (235-268, 560-585).
19. bk_14 — "WILLIAM HENRY SCOTT" is a clean flat overlay on a worn cover (293-527, 688-760).

**Whole-set note:** the hero's backpack is BLACK / charcoal in every still where it shows (03-06, 15, 21, 23, 29, 32, 35, 36, 37, 39, 44, 47). The cast sheet says brown. It is consistent with itself, so no still is marked down for it; either the cast sheet or all hero stills need changing.

**Fixed since audits A / B (confirmed):** 04 (one hero, topknot, Usman has kerchief), 05 (wrist and ears now correct), 06 (woman now holds the umbrella), 08 / 24 / 43 (ears now correct side), 09 (boy's hair black), 13 (no giant head, clean edges), 16 (no red horns, white uniforms), 20 (three clean children), 23 / 44 / 47 (handkerchief now on left wrist), 26 (uniforms), 30 (teacher's hand, book blank), 36 (body coherent, seen from behind), 37 (paper blank).

## Table

| still | people | hands (count; fingers per hand) | bare feet (toes) | hero identity (topknot / backpack / medallion / handkerchief wrist) | Usman (colour, kerchief, ears, legs) | clones / bystanders | writing | other faults (pixel area) | verdict |
|---|---|---|---|---|---|---|---|---|---|
| bk_01 | 9 (carried) | 5; one is a 3-4 finger blob with no arm (228-248, 490-520) | none | boy, n/a | – | 8 children in window, no clones reported | none | smudged half-face (235-268, 560-585); louvres bend | MINOR (carried) |
| bk_02 | 1 | 2 clasped, fine | 1 foot, 5 toes | boy, n/a | – (tan stray: 4 paws, 1 tail) | none | none | none | OK (carried) |
| bk_03 | 1 (cropped at nose) | 1; thumb + 4 | none | medallion yes; lens has no handle; wrist out of frame; backpack black | – | none | none | none | OK (carried) |
| bk_04 | about 14: hero and woman by tree, about 12 children in yard | 1 readable (hero's own right fist, 485-500, 1050-1075), count unsure, too small; children's hands unsure, too small | none | topknot yes; backpack yes (black); medallion not visible (seen from behind); left wrist hidden | black, red kerchief yes, 1 tail; ears unsure, too small (two small bumps 480-520, 1160-1180); legs hidden (sits, seen from behind) | children all differ in pose; faces blank at this size | none | woman's umbrella hand hidden behind her; nothing else | MINOR |
| bk_05 | 1 | 1; 4 fingers on bark, thumb hidden, joins LEFT arm | none | topknot yes; backpack yes (black); medallion yes; handkerchief on LEFT wrist (correct) | black, kerchief yes, own RIGHT ear folded (120-230, 830-900), own left upright (correct); 1 tail; 2 front legs seen, hind legs hidden | none | none | white toes (215-300, 1250-1320), white chest streaks (150-330, 1010-1150); toe count on that paw unsure | MINOR |
| bk_06 | 2 | 3; hero fist 4 knuckles + thumb; woman's shoulder hand thumb + 4; umbrella hand thumb + 4 | none | topknot yes; backpack yes (black); medallion yes; handkerchief on LEFT wrist (correct), hand in pocket | – | none | none | lens ring-sized (250-292, 968-1012); umbrella now held | MINOR |
| bk_07 | 9 (carried) | 2 readable, both fingerless blobs (570-605, 645-685; 640-690, 650-695) | none | boy, no tuft | – | not reported | none | blank white face (250-290, 470-500) | MINOR (carried) |
| bk_08 | 0 | – | – | – | black, kerchief yes, own RIGHT ear folded (130-220, 340-440), own left upright (correct); 4 legs, 1 tail | none | none | white bib chest to belly (380-470, 540-860); thin light line over nose (360-400, 385-395) | MINOR |
| bk_09 | 4 (standing boy, boy from behind, 2 half-heads at lens edge) | 0 clearly visible (boy's hands at his sides, unsure, too small) | none | boy: short black hair, white polo | – | none | "PINAKAMATANDANG BATAS" (283-575, 450-475): readable, correct, not mirrored, on the board; soft chalk look | none | OK |
| bk_10 | about 16 (carried) | 2 teacher's, blobs, fingers unsure (540-600, 470-500) | none | boy, hands behind back | – | not reported | none | melted half-faces (140-170, 465-560) | MINOR (carried) |
| bk_11 | about 22, from behind (carried) | 1; thumb + 4, palm creases drawn on a hand seen from behind (210-530, 140-510) | none | n/a | – | not reported | none | very long arm | MINOR (carried) |
| bk_12 | 1 | 0 | none | boy, tuft yes | – | none | none (board and covers clean) | none | OK (carried) |
| bk_13 | 5 + 1 cropped torso (main boy, 3 laughing boys, faint boy far back, torso at left edge) | 1; fist, 4 knuckles (710-768, 920-980) | none | boy: side-parted black hair, white polo | – | laughing boys differ (two share a face type, different pose and hair) | none | faint far child has no face detail (115-165, 545-610), acceptable | OK |
| bk_14 | 1 | 2; 4 fingers on each side of the cover, thumbs behind the book | none | boy, tuft yes | – | none | "WILLIAM HENRY SCOTT" (293-527, 688-760): readable, correct, not mirrored; flat clean overlay on a worn cover | none | MINOR |
| bk_15 | 1 (carried) | 2; raised hand thumb + 4, other grips arm | none | medallion yes; backpack black; handkerchief at strap / upper arm (560-750, 780-990), NOT left wrist | – | none | none | none | MINOR (carried) |
| bk_16 | 6 (runner + 5 pupils from behind) | 0 readable (runner's arms hold books; unsure, too small) | none (runner wears shoes) | boy runner: black hair, white shirt, shorts | – | 5 heads from behind, each a different cut and size | none | odd inner-ear line on left pupil (130-160, 820-880), trivial | OK |
| bk_17 | 1 (carried) | 2; one cut by frame, count unsure; other 4 fingers | none | n/a | – | none | none | none | OK (carried) |
| bk_18 | 3 (carried) | 2, fine | none | boy from behind | – | none | gibberish round medal rim (345-430, 305-390) | medal boy brown centre-parted hair; medal hangs low | MINOR (carried) |
| bk_19 | 1 | 2, fine | none | boy, tuft yes | – (tan stray, 1 tail) | none | none | none | OK (carried) |
| bk_20 | 3 (boy, girl with ponytail, boy) | 1; 4 fingers (85-170, 720-790); the other five hands are tucked under folded arms | none | children, n/a | – | three different faces | none | row of six folded forearms reads a little rubbery (190-650, 570-830) | OK |
| bk_21 | 1 | 1 fist | none | topknot yes; backpack black; medallion yes; handkerchief LEFT wrist | – | none | none | none | OK (carried) |
| bk_22 | 2, cropped | 1; thumb + 4 | none | medallion yes | – | none | none | none | OK (carried) |
| bk_23 | 1 | 0 (arm cut below the wrist) | none | topknot yes; backpack yes (black); medallion yes; handkerchief on LEFT wrist (440-600, 1180-1344) (correct after mirror) | – | none | none | none; nothing mirrored-looking | OK |
| bk_24 | 1 (legs only) | 0 | none (shoe) | – | black, kerchief yes, own RIGHT ear folded sideways (110-240, 255-370), own left upright (correct side); 3 legs in frame, tail out of frame | none | none | white front paw (430-500, 835-890); white chin (265-340, 520-565); folded ear only half folded | MINOR |
| bk_25 | 2 (girl, boy) | 3; girl's stick hand thumb + 4 (350-410, 735-790), knee hand 4 fingers (310-390, 825-870), boy's fist about 4 (525-580, 900-950), small | none (sock and shoe) | boy: short black hair, white polo with blue collar trim | – (tan scruffy stray, white muzzle, 3 paws seen, matches bk_02 / 19 type) | none | none | raw whole banana on a stick (360-475, 620-790); girl has TWO braids | MINOR |
| bk_26 | 3 (teacher, boy, girl) | about 4, small: teacher's and boy's hands fused in a clasp (340-400, 860-915), girl's joined (460-520, 930-980); counts unsure, too small | girl's and boy's shins cut by lens edge, no toes visible | boy: short black hair, white polo | – | none | none | none; uniforms now match | OK |
| bk_27 | 2 | 0 | none | n/a | – | none | none | none | OK (carried) |
| bk_28 | 1 | 1; 4 fingers, thumb hidden | none | medal boy | – | none | rim pseudo-engraving (360-440, 930-1030), acceptable | none | OK (carried) |
| bk_29 | 1 | 0 fully visible | none | topknot yes; backpack black; medallion yes; handkerchief LEFT wrist | – | none | none | none | OK (carried) |
| bk_30 | 6 (teacher, Lolo at door, 4 pupils from behind) | 1; teacher's hand under the book, thumb + fingers folded, count unsure (370-445, 815-865); Lolo's hands hidden | none | n/a | – | 4 pupils, different hair and shirts | none (book cover blank) | stray grey vertical pole (148-172, 360-800); pupils' shirts blue-grey; one has a dark bag strap | MINOR |
| bk_31 | 2 | 4, join arms, count unsure | none | n/a | – | none | paper has faint hatch only | none | OK (carried) |
| bk_32 | 1 + dog | 2; upper (left) hand 4 fingers, thumb hidden; lower hand 2 fingertips showing (290-500, 990-1190) | none (shoes) | topknot yes; backpack yes (black); medallion yes; handkerchief on LEFT wrist (correct) | black, kerchief yes; BOTH EARS ERECT (465-545, 465-625 and 625-735, 540-690), no folded ear; 4 paws; 1 tail | none | none | grey-white toes on all paws (280-610, 1220-1320); tail far from body (65-200, 1215-1305) | MINOR (ear folded in code after audit) (or inpaint the ear) |
| bk_33 | 1 (lens view) | 2, count unsure, too small | none | n/a | – | none | none | none | OK (carried) |
| bk_34 | 1 (lens view) | 1, count unsure | none | n/a | – | none | none | indoor window pasted in yard (50-215, 190-720; 200-768, 700-900) | MINOR (carried) |
| bk_35 | 1 | 2; near (left) hand thumb + 4 (390-500, 1200-1320); far hand thumb + 4 (230-290, 1150-1270) | none | hair tied as LOW PONYTAIL at the back (500-570, 515-600), not a topknot; backpack yes (black); medallion yes; handkerchief on LEFT wrist (correct after mirror) | – | none | gate plaques (0-40, 750-790; 695-730, 785-820) are illegible smudges, no mirrored letters | none | MINOR |
| bk_36 | 1 (from behind, top-down) | 0 (both arms go down out of sight) | none | topknot yes, seen from above (360-410, 830-880); backpack yes (black); medallion and wrist not visible | – | none | none | body now coherent; spoon lies by the hole (515-545, 595-735) | OK |
| bk_37 | 1 | 2; both thumb + 4, join arms (185-300, 880-1000; 400-550, 900-1010) | none | topknot yes; backpack yes (black); medallion yes; handkerchief NOT on a wrist: hangs at the left elbow / pack edge (655-768, 1060-1255) | – | none | none (paper blank) | none | MINOR |
| bk_38 | 0 | – | – | – | – | none | page blank; plaque illegible | open book floats on the tree (60-768, 70-810) | MINOR (carried) |
| bk_39 | 1 | 2, fine | none | topknot yes; backpack black; medallion yes; handkerchief LEFT wrist | – | none | page has ship sketches only | none | OK (carried) |
| bk_40 | 0 | – | – | – (medallion on desk) | – | none | "May itinuro ba / sa'yo sa eskwela / na hindi pala / totoo?" (240-640, 310-650): readable, not mirrored, follows the page slant; crisp against painted paper | none | OK |
| bk_42 | 0 | – | – | – | – | none | "Tama ka." in red (345-550, 585-655): readable, not mirrored, on the paper; does not bend at the fold | none | OK |
| bk_43 | 0 + dog (portrait) | – | – | – | black, kerchief yes, own RIGHT ear folded (0-160, 330-490), own left upright (correct after mirror); legs and tail out of frame | none | none | eyes bright yellow (225-300, 585-640; 460-500, 560-610), brown elsewhere | MINOR |
| bk_44 | 1 | 1; 4 fingers with nails on the upper arm, thumb hidden (520-690, 920-1060); the left hand is tucked | none | topknot yes; backpack yes (black); medallion yes; handkerchief on the tucked LEFT wrist (240-370, 920-1120) (correct after mirror) | – | none | none | none | OK |
| bk_45 | 1 | 0 | none | boy | – | none | blank paper | none | OK (carried) |
| bk_47 | 1 | 1; fist on the wire, cut by frame, count unsure (590-740, 1290-1344) | none | topknot yes; backpack yes (black); medallion yes; handkerchief on LEFT wrist (560-720, 1220-1320) (correct after mirror) | – | none | none | none | OK |
| bk_48 | 1 | 0 | none | boy | – | none | book has no text | none | OK (carried) |
| bk_49 | 1 | 2; thumb + 4, and 4 fingers | none | Bea | – | none | none | none | OK (carried) |
| bk_50 | 1 | 0 | none | medal boy | – | none | none | none | OK (carried) |
| bk_51 | 1 | 1 full (thumb + 4) + a fingertip | none | Ma'am Celia | – | none | book and paper blank | none | OK (carried) |
| bk_52 | 1 | 0 | none | Lolo | – | none | none | none | OK (carried) |
| bk_53 | 0 | – | – | – | – | none | "Mag-ingat sa batang / laging nauuna." (270-690, 585-765): readable, not mirrored, follows the page | none | OK |

Limits of this audit: finger counts on hands under about 40 px (04, 09, 16, 26) are given as "unsure, too small" and were not guessed. No other black dog appears in any of the 20 stills looked at; the only other dog is the tan stray (bk_25).
