# Episode 1 facts: the Draisine (Laufmaschine), 1817

Checked on 2026-11-19. "Opened" means the page was read in this session. Anything not opened is marked and is
NOT used as a number on screen.

## What the opened sources say

| Fact | Value | Source |
|---|---|---|
| Maker | Karl Drais (Karl von Drais), of Baden, Germany | Wikipedia "Karl Drais" (opened) |
| Year | 1817 | both pages (opened) |
| First reported ride | 12 June 1817, from Mannheim to the "Schwetzinger Relaishaus" (a coaching inn at Rheinau), about 7 km (4.3 mi) away; the round trip took a little more than an hour | Wikipedia "Karl Drais" (opened) |
| Speed | top speed around 10 mph (16 km/h) on level ground | Wikipedia "Dandy horse" (opened) |
| Protection | a grand-ducal privilege for 10 years in Baden, 12 January 1818; patented in France in February 1818 as a "vélocipède" | "Karl Drais" and "Dandy horse" (opened) |
| How it is ridden | the rider sits astride and pushes the ground with the feet; the front wheel and handlebar are hinged to steer | "Dandy horse" (opened) |
| Materials | wood; a c. 1820 example is described as cherry wood and softwood | "Karl Drais", photo caption (opened) |
| Names | Laufmaschine ("running machine"), Draisine, draisienne, vélocipède, hobby-horse, dandy horse, swiftwalker, pedestrian curricle | both pages (opened) |
| English copy | Denis Johnson of London, sold 1818 to 1819, with a curved wooden frame and larger wheels | "Dandy horse" (opened) |
| Why it faded | roads were rutted, so riders took to the pavements; cities banned the machines (Germany, Britain, the United States, Calcutta are named) | both pages (opened) |

Links: https://en.wikipedia.org/wiki/Karl_Drais and https://en.wikipedia.org/wiki/Dandy_horse

## Where sources disagree, or stay silent

- **Why he built it.** "Dandy horse" says Drais was inspired "at least in part" by the horse shortage after the 1815
  Tambora eruption and the 1816 "Year Without a Summer". "Karl Drais" does not mention it. The idea comes from the
  historian Hans-Erhard Lessing and other historians doubt it (not opened this session). So the pilot does NOT say it.
- **Patent date.** "12 January 1818" (Baden privilege) and "February 1818" (French patent) are two different
  documents, not a contradiction.
- **Average speed.** Not stated. 2 x 7 km in "a little more than an hour" is about 13 km/h; this is our own
  arithmetic and the screen says "roughly".
- **The route.** It is often retold as "Mannheim to Schwetzingen". The opened page says the inn was at Rheinau, on
  the Schwetzingen road, so the screen says "a coaching inn on the Schwetzingen road".
- **Weight, wheel size.** Not in the opened pages. Commonly quoted: about 22 kg, wheels about 27 in (69 cm).
  Not opened this session, so not shown as numbers. The model uses 69 cm wheels.
- **Brake and armrest.** Not in the opened pages. Museum descriptions of Drais's machine mention a cord-operated
  brake on the rear wheel and a padded "balancing board" for the forearms (not opened this session). Both are shown
  and named in the pilot: **please confirm before publishing**, or these two close-ups should be swapped for others.
- **A second long ride** (Gernsbach to Baden-Baden, 1817) is often cited; not in the opened pages, not used.

## Text on screen (must match the table above)

1817 / The first bicycle had NO pedals. / THE DRAISINE / Built by Karl Drais in Mannheim, Germany. / He called it the
Laufmaschine: the "running machine". / STEERING / ARMREST / SADDLE · NO PEDALS / BRAKE / Eight main parts. Mostly wood,
with iron fittings. No pedals, no chain, no gears. / 12 JUNE 1817 / Karl Drais rides out of Mannheim: about 7 km to a
coaching inn on the Schwetzingen road, then back. / The round trip takes a little over an hour. Roughly 13 km/h, and
no horse. / Riders used the smooth pavements. Cities banned the machine, and the craze faded. / NEXT: SOMEONE ADDS
PEDALS / EP 2 · THE VELOCIPEDE, 1860s

Open points on the text: "Built in Mannheim" (the ride started there; where the machine was made is not stated in
the opened pages); "iron fittings" and "eight main parts" describe our model.

## The 3D model

Built in code from named parts (`lib/draisine.py`): frame (beam, rear stays, braces, steering pin), front wheel,
rear wheel, fork, handlebar (tiller and bar), armrest, saddle, brake (shoe, arm, cord). Each wheel: wooden rim, iron
tyre, hub, axle, 8 spokes. Wheelbase 1.2 m, wheels 0.69 m, overall length about 1.9 m, saddle about 0.9 m high.

Not checked against a museum photo or period drawing: image hosts were blocked from this machine. The tiller, the
armrest stand and the spoke count are simplified guesses. A reference photo from the owner would fix this.
