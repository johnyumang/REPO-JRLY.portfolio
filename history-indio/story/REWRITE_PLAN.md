# INDIO: ANG SAKSI — rewrite plan for the 50 scripts

14 November 2026. Text only; nothing in `videos/` is changed by this plan. It turns each episode as it is
(`story/CONSISTENCY.md`, `story/consistency/epNN-NN.md`) into the form and the story of `story/BIBLE.md`.
Episode 1 is rewritten in full as the sample: `story/ep01_v2/`.

## 1. What changes in all 50 (read once)

| # | Change | In the current scripts |
|---|---|---|
| A | **Third-person scenes.** New master script per episode: `script_multispeaker.txt`, one line per turn: `TAGAPAGSALAYSAY:` (short, place and time), `(what people do)` as its own line for the picture, then `NAME: [tone] line`. Indio's whisper to us is `INDIO (sa atin):`. | Indio narrates 42 to 67 of every 42 to 82 sentences |
| B | **A friend of that time or place** in the fourth seat, with a child's or worker's voice; Indio learns the history from the friend and from what he sees. | Indio recites dates he could not know |
| C | **One fall, one comeback** per episode, by one of his own gifts; kinds of twist per BIBLE section 10. | Most episodes have a sting, not a fall |
| D | **Cut the spoken fairness-and-label block** ("Umungol si Usman, kaya linawin natin ... Tiyak ... Pinagtatalunan ... Kathang-isip ...") in every episode. The certain and the disputed move to the end trivia; uncertainty inside the story is Usman's u-MU-ngol in the scene. | 47 episodes; sentence ranges in the table below |
| E | **Trivia at the END**: `trivia_break.json` gets `insert_after_sentence` = the last story line, and its two speakers give the real moment's facts (from `facts.md`) instead of a general fact. | Spliced after sentence 12 to 36 in Episodes 3 to 50 |
| F | **No generic follow line.** The story ends on the cliffhanger; then the one question of the episode; then the trivia. `endcard.txt` carries the episode's question, not "FOLLOW = ...". | The same follow sentence in 41 episodes |
| G | **Opening.** The hook is line 1. "Ako 'to si Indio." is said once, where it lands. "Samahan mo akong mag-time travel, at tuklasin ang history natin." is cut everywhere. | 49 episodes open the same way |
| H | **Meta words out**: "Season 2", "season", "episode". | Ep 8 s37, Ep 9 s78, Ep 21 s4, Ep 22 s30, Ep 23 s30, Ep 25 s48 |
| I | **u-MU-ngol**: in every `sentences.json`, the `say` field of "umungol" is written "umúngol" / "u-MU-ngol" as the voice tool needs; checked by ear on the first take. | 40 episodes |
| J | Canon fixes of BIBLE section 9 (marks, the star, the money, Usman, names, San Lorenzo). | Listed per episode below |

**Voice: all 50 are re-voiced.** The form changes who speaks, so no episode can keep its narration track.
What can be reused is single takes of lines that survive word for word (the "kept" column). New designed
voices needed, once, for the whole series: TAGAPAGSALAYSAY (one calm storyteller, never a clone of a real
person); a pool of six "friend" voices (two boys, two girls, an old man, an old woman) reused across episodes;
ANG LALAKING NAKAPUTI (the same voice in Ep 11, 13, 30, 48). Existing designed voices stay: M, Usman, Lola,
Lolo, Rico, Tubal, Sinag, Tala, Albo, Totoy, Bea, JM, Ma'am Celia, the diwa.

**Pictures.** The machines redrawing stills should draw from the new `shots.md` of each episode as it is
written, not from the old sentences. Until an episode's v2 exists, a redraw of its old still is still useful
only for scenes marked "kept" below.

**Length** stays: Ep 1 to 8 about 380 spoken words; Ep 9 to 49 about 750; Ep 50 about 350. Stage directions in
(parentheses) are not spoken and do not count.

**Order of work** (most broken or most watched first): 1 (done as sample), 2 to 8 (they are what a new viewer
meets, and they are short), 14-15 and 20 (the fall and the turn), 9, 30, 37, 48, then the rest in order.

Numbers in the last columns are estimates from the audit: "kept" = sentences that can stay word for word;
"cut" = sentences removed outright (the rest are reworded); "new" = lines newly written or reworded (dialogue lines are shorter than narration
lines, so the count rises while the word count holds). The exact count is fixed when each script is written.

## 2. Episode by episode

### Season 1 (about 380 words each)

| Ep | New scenes | Cut from the current script | Twist and what is added (BIBLE) | Now -> kept / cut / new |
|---|---|---|---|---|
| 1 | Sample written: the job window; the pawnshop (wax print, three triangles); the shrine in the rain (Rico's tarpaulin); the camp, seized; the tearing; back in the rain | s2 intro; s21 to s27 told history; s28 to s33 fairness; s41 follow | Mistaken identity. Islaw; first Udyok unknowing; the woman across the street stays | 42 -> 9 / 33 / 49 |
| 2 | The order slip "M"; the empty baluarte; inside the wall, Sepa's kitchen; the gate that will not listen; the rats and the drain; cold pancit | s2; s27 to s36 (ten told sentences: surrender, ransom, Anda, Paris, 1764: to trivia); s34 fairness; s47 follow | He arrives too late. Dinig costs him the pancit. "R.B., five stars." M's tip message | 48 -> 8 / 38 / 44 |
| 3 | Lola Ising's question (named at once; a red umbrella dries behind the door); the box; Kawit from the back row; he grabs at the woman; Tinong; two medallions | s3; s27 to s30 fairness and label; s36 "ang lolo ng Lolo ko" becomes Lola's guess, said as a guess; s42 follow | Wrong target. First Malas, unknowing. "Lolo Isidro" named. Third mark | 43 -> 9 / 30 / 42 |
| 4 | The taunt about Rico; the one word "Calamba"; the stone house; the big dog bares its teeth; "Ako 'yan, par"; the karomata leaves; Lola's text | s3; s7 "Isang salita lang ang iniwan niya" stays and s40 "lumang sulat" becomes "may nakita akong sobre, hindi ko pa nabubuksan" (fixes the Lolo's legacy); s28 to s32; s43 | False betrayal. Andoy. "Kaamoy mo siya" | 44 -> 10 / 30 / 42 |
| 5 | The ₱20 note; the hotel kitchen with Ambo; the great door; the paper with the number; "Wala."; the right window; five fingers | s2; s15 to s16 the spoken "Bente milyones" becomes a number on a paper; s26 to s34 told history; s35 to s39 fairness; s50 | He wins the wrong thing. Fifth mark costs his last ₱20 | 51 -> 10 / 36 / 44 |
| 6 | The ironed polo; the empty park; M's hand; Kiko the water boy; "Huwag kang pipikit"; he shuts his eyes; the note; Usman stays | s4; s37 to s42; s60. "ikaanim na talon" wording removed | Betrayal. No mark because he blinked (said by Usman: "Pumikit ka, par.") | 61 -> 14 / 40 / 44 |
| 7 | 9% battery; the wagon to Paco; Imo; the letter read in pieces between scenes; the phone dies; the lente dug up | s2; s7 wrong-voice line; s30 to s34; s45. The letter says "lima ang marka ko" (marks, not jumps) | The secret kept from him. Name José Indalecio Bracken; "Ang Huling Tala" | 46 -> 11 / 28 / 42 |
| 8 | The bakery, 529 days; Kawit from behind; he goes for the medallion; the commotion is himself; "Sino ka ba?" "Wala. Tambay lang."; the diwa's one line; the umbrella handle | s0 "tatlo" becomes "dalawa"; s3; s7 to s12 told history; s19 "ikaanim na talon"; s26 to s29; s33 "dalawang libong taon"; s37 "Season 2" | Time loop. Sixth mark for staying. A man with a raised phone in 1898 | 38 -> 8 / 26 / 44 |

### Season 2 (about 750 words each)

| Ep | New scenes | Cut | Twist and what is added | Now -> kept / cut / new |
|---|---|---|---|---|
| 9 | Under the tree at Kawit (ten dots and two lessons, said once); the edge of the crowd with Yoni; the Gospel scene seen from far, verses exact with reference, the rest "sa buod", no jokes; night, the hooded man; the lamp dies and burns | s3; s17 "Nahanap niya ang una" becomes "ang ibang labing-isa, sa papel"; s18 "ikaanim"; s20; s25 to s46 (22 told sentences) reduced to what he sees; s31 to s36 reworded "Nakasulat sa Juan..."; s53 "gaya sa Kawit"; s63 to s75; s76 "sa bulsa ko"; s78 "Season 2"; s81 | The test in disguise. A white lock under the hood; Usman does not growl | 82 -> 14 / 52 / 62 |
| 10 | The corridor (the boy sent out); the medal goes to the first-honor boy; the strays at the gate; "Ako po ang nagbura ng pisara"; Saturday markers with Lolo Isidro; Ma'am Celia kept the paper; the tin | s0 or s57 (fourteen years, one number); s2; s28 to s36; s50 to s55; s73. A Lola beat on his first return (pays "itabi mo ang sinigang ko") | Stolen credit. The three gifts as a child. Ma'am Celia named | 74 -> 16 / 40 / 60 |
| 11 | No fare in Surigao; the wish by accident, hand on the umbrella; the banker in white; the pickup sinks; under water; Ang Sugo; first knot; the shadow | s3; s45 the diwa's "Ang Galilea"; s52 the star listed as his gear; s58 to s63; s69 | The enemy is the guard. YAMAN on the hologram; the red cord | 70 -> 14 / 34 / 58 |
| 12 | Ten vehicles; Lumban with Bini; the year 900 seen, not read (he cannot read Kawi yet); the netted tikbalang, tyre tracks, the ring light; shirt inside out; Ang Kasulatan; the house contract | s3; s13 to s20 told history; s15 to s18 reading before the medallion; s52 to s58; s65 | The rival got there first. A bitten nail in the mud | 66 -> 12 / 34 / 58 |
| 13 | The yacht; thirteen glasses; the Mass seen from the trees, in silence, no jokes inside it; Mang Laon's fish; the dim Kalakal; the moon and the phone | s3; s17 to s24; s34 to s35 the diwa lines that contradict the trade; s57 Usman in the present; s57 to s63; s67 | The gift fails: a fight he loses outright. Sinag's golden cup, unnamed | 68 -> 12 / 36 / 56 |
| 14 | JM and the tyre receipt; fifty; the kuta with Ambing; the kapre; the tall man; the condo, a back and a golden cup; the garage floor | s3; s55 to s61; s67. "Ilusyon lang ang hawak mo, Mister Bracken" added | The price comes due. K 35 to 18 | 68 -> 20 / 30 / 48 |
| 15 | One pandesal; the garage cat; Totoy ("Si Tatay, nasa malayo. Nagtatayo ng pader."); medallions re-warm one by one; Dezhou through the lens; the woman in white; Lola Ising's kitchen | s3; s12 and s29 "Malamig ang lahat" against the Dagat working; s24 naming the Daan Pauwi early; s26 to s27 the dropped motor (it becomes the vehicle); s64 to s69; s75 | The lie he wants to believe. The fifty are in JM's name | 76 -> 22 / 32 / 46 |
| 16 | "Walang sikreto"; Sakai with Kichi; the plot of Tondo seen through the lens as one word that sinks it; the kappa; he bows; he tells M | s3; s64 to s69 (and "Tubal" first heard in the label); s76 | The secret kept. M says "Tubal" in the story | 77 -> 16 / 36 / 54 |
| 17 | The warehouse on the Thames; Rico live; 1888 with Nell; a man bent over a book, far off; Lundag; under the porcelain; "Bukas na lang" | s3; s27 to s29 the invented act for Lolo Pepe becomes what the family says; s55 to s61; s70 | Stolen credit. Rico named | 71 -> 14 / 36 / 56 |
| 18 | The pier, selling on the pavement; the bag stolen; the grandfather; the jaguar; Lupita; one mangga for the bridge; the toy galleon | s3; s4, s5, s8, s38 the money contradictions; s17 to s30; s38 to s42 bread becomes fruit; s55 to s61; s70 | Mistaken identity. The Kalakal relights | 71 -> 12 / 40 / 58 |
| 19 | Three million views; Bapa Usop's coffee; 1639 from afar, no words; the nest; the Tinig dumb; three confessions live; the sarimanok | s2; s19 to s28; s43 to s44 "hindi ako nagnakaw" becomes "hiram, at ibabalik ko"; s54 to s60; s67 | The witness is doubted. "Kaklase mo 'yon." The ka-Indio counter appears | 68 -> 18 / 30 / 52 |
| 20 | The vans; Rico lifts the Kalasag; the battle from the mangroves with Buyong; the siyokoy and the collars; he lets the prize go; "Indio."; the anting; the key | s2; s31 and s33 Lihim then Tinig; s48 the star moves; s51 Usman in the present; s51 to s56; s64 | The rival got there first. Seventh mark | 65 -> 14 / 30 / 56 |

### Season 3

| Ep | New scenes | Cut | Twist and what is added | Now -> kept / cut / new |
|---|---|---|---|---|
| 21 | (Retitled "Ang Ate sa Hamog".) Rico's convoy feasted; Nanay Pacing; the fog shuts; the coat steps out; Tala; Lola's kitchen | s3; s4 "season"; s4 to s11 recap; s8 to s10 giving away; s55 to s61; s66 the number of marks; s70 | The enemy is the guard | 71 -> 14 / 36 / 54 |
| 22 | Tay Sebyo's balangay; the plain with Nuri; the seal on the foreman's brick; the tongues break; he cannot understand M; Usman is clear; the brick falls | s3; s22 scripture reworded as "sa buod"; s30 "season"; s57 to s62; s67 | The gift fails. Proof the Dinig is his | 68 -> 14 / 34 / 54 |
| 23 | He climbs to hit someone; Sami; the giant; the Kalasag flattened; weapons down; the coat of Galilee comes off; Albo | s3; s30 "season"; s62 to s66; s68 the Biringan retry; s73. "Teodoro" only on a paper | Wrong target | 74 -> 16 / 34 / 52 |
| 24 | The call with Ma'am Celia; Ilos; the crown; "Natutukso ako."; "Ikaw ang nasa condo."; M caught; the Pugita; the tabò | s2; s51 to s57; s59 to s60 the retry; s64 | The prize is a trap. The Tabò ng Bukal won | 65 -> 14 / 28 / 54 |
| 25 | Bea's call; Pema; the yeti; the stone clock; three breaths over and over; Usman's tail; the salok to the yeti; the flooded Kawit in the clock | s2; s20 and s25 "anak ng puti", "taong maputla"; s24 the inner sun; s26 "noong unang gunaw"; s29 the marked disc; s48 "season"; s49 to s54; s56 the retry; s62 | Time loop. Rule and cost of the three breaths | 63 -> 12 / 30 / 54 |
| 26 | Twelve days of nothing; the nahual on watch; "Alin dito ang totoo?"; the night of the ceremony, short, by suggestion; Sinag; the sorting; the healer draws on the key | s3; s4 to s5 the retry; s53 the unchecked figure; s55; s59; s70 the groove from the vision; s73 | The test in disguise. The Malas can be trained | 74 -> 16 / 34 / 52 |
| 27 | The balete upside down; Hiraya; the table he must not eat from; ten seconds with his mother; the Tabò does nothing; three conditions; "Mikaela" | s2; s50 to s55; s63 | False victory. The yeti tracks Tala's shadow | 64 -> 16 / 26 / 50 |
| 28 | The sixth plate; Lucban with Selang, 1841 seen from far, without words; Papa's flashlight; Giliw bars M; she gives the Sandugo; Lolo Isidro; the tambuli | s3; s22 to s34 (eleven sentences of dates, to trivia; one date said once); s39 "naming"; s66 to s71; s76 | Sacrifice. "Hindi sa tanso 'yan, apo." | 77 -> 14 / 40 / 52 |
| 29 | Seven doors; Limot, the man carving L; one salok; Hilig, Sinag's door; Sakim, his own face under fifty vehicles; Kurakot | s3; s50 the firm's logo stays only after the name check; s67 to s73; s70 scripture; s78 | The dilemma. "Hindi ka malas, anak. Nagmamalas ka." | 79 -> 22 / 30 / 44 |
| 30 | Poot; Linlang; Palalo, the voice; he kneels; the blade; the door marked sero; then THREE scenes, played: the lie cut in Biringan, Albo at the feather, the Daan Pauwi and the table | s3; s45 to s60 the climax told in sixteen sentences becomes three played scenes; s57 "ang laki mo na"; s61 to s67; s66 scripture; s72 | He loses on purpose. Usman stays from here | 73 -> 14 / 36 / 56 |
| 31 | The first sinigang; the water; the roofs (kapre's tree, Yúmud, the Binti); the Tabò is dry for Lola; Rico lands; the cardboard sign | s3; s59 to s63; s62 the barangay etymology (to trivia, as disputed); the wall becomes San Lorenzo's; s73 | Stolen credit | 74 -> 16 / 32 / 52 |

### Season 4

| Ep | New scenes | Cut | Twist and what is added | Now -> kept / cut / new |
|---|---|---|---|---|
| 32 | The key, the chair, the debt; the wall of sacks; the shore with Amihan, a harvest divided; "Ako muna"; Kap Ramil talks; the canal | s2; s26 the Yúmud's origin (one wording: Manobo folklore, in trivia); s38; s52; s54 to s58 Sinag (cut: not one of her six); s59 to s62 the near-kiss; s63 to s67; s71 | He wins the wrong thing. "Par. Hindi mo suot ang Tinig." | 72 -> 14 / 34 / 52 |
| 33 | The free wall; Tikoy in 1574, the palisade seen from behind it; the clause; Vangie in gloves; the giant sets posts by night; September, it holds | s2; Sinag's casino; s60 to s64 the near-kiss; s65 to s69; s73 | The prize is a trap. Tubal: who measured the door under Banahaw | 74 -> 14 / 34 / 54 |
| 34 | The third night of the budget; Entong at the press in Malolos, delegates seen from the doorway; the line read aloud; morning, three small lines; the logo upside down | s2; s56 to s59 he narrates a room he is not in (becomes a played scene); s60 "40" kept once; Sinag's offer; s60 to s65; s69 | False victory | 70 -> 14 / 32 / 54 |
| 35 | The perfect signature; "Akin"; the garage sealed; Loleng outside Bilibid, the word "bandido"; the blade will not cut; the bottle poured out | s3; s17 and s60 the 2025 investigations; s56 to s61; s61 and s63 "ang partido ko"; s67 | The frame-up | 68 -> 16 / 30 / 50 |
| 36 | The flight; the window on Morrison Hill with Mei, three people sewing, no words; pigeons and wharf rats; the register: "R. Paredes"; the tyre receipt, JM; nine faces; the call | s3; s14 "tatlong babae"; s53 to s58; s57 the legal reading; Sinag as older Indio; s63 | Betrayal | 64 -> 12 / 30 / 54 |
| 37 | The salok for Usman; Bini in 900, what a cleared debt is to a child; Rico testifies; one plain question; "Ako muna"; Mang Nesto, JM; "Saksi ako." | s3; s6 "hindi ko na kailangan ng medalyon"; s28 Sinag offers the presidency at 35; s40 "Tiyak" of the invented wall; s56 to s61; s67 | The witness is doubted. Ang Saksi, joined, for the first time | 68 -> 20 / 28 / 48 |
| 38 | The storm of 37 is this flood (no jump in years here); the garage opens; seven children; the gate; the glove; "Wala nang akin dito."; the Pugita | s3; s4 "tatlong taon"; s49 to s50 he watches the sabotage and does nothing (he goes back for evidence, and uses it); s52; s58 to s61; s68 | The helper is the enemy. Vangie's ring | 69 -> 16 / 30 / 52 |
| 39 | "Makalipas ang ilang taon" (said here, once); the debate, Rico hosts; Badong in Tondo, a name people are afraid to say, seen from far; the Tinig dies on air; the confession; the count | s3; s6 and s22 kept as story; s27 and s29 the invented scene around Asiong Salonga; s46 to s52; s61 "Naputol na naman"; s64 | The gift fails | 65 -> 12 / 30 / 54 |
| 40 | Sixty arks; Nonoy at the dig, the planks; the Orasan, people left behind; the list; Rico's name; the nail in Totoy's hand | s3; s11 M speaking God's words (becomes "Nakasulat sa Genesis 9:11: ..."); s12 and s59 one word for the verse; s28 against s52; s55 to s60; s65 "Naputol na naman"; s68 | The dilemma. "Tay?" | 69 -> 14 / 30 / 54 |
| 41 | 100%; Peping selling papers in 1935, faces, no words; the bronze marker; the staff; the sky; one kneel; the first ark | s3; s25 "nasa payong ni M"; s58 to s62; s60 to s61 scripture; s68 | The price comes due | 69 -> 14 / 34 / 52 |

### Season 5

| Ep | New scenes | Cut | Twist and what is added | Now -> kept / cut / new |
|---|---|---|---|---|
| 42 | The clip from 1521 played back; the roof; he strikes; the moon cracks; silence; "Pasensya na."; the eyes behind the moon | s3; s40 "kasabay ng kaalaman ko"; s59 to s67; s66 Genesis in the first person; s72 | The enemy is the guard. Dinig mastered | 73 -> 14 / 36 / 52 |
| 43 | The pier with Totoy; the horn; nothing; Albo turns away; "Ilusyon lang"; then all of them; the counter | s3; s43 Albo answering; s51 the weapon "discovered" again; s60 to s66; s71 | He arrives too late (so it seems). "Sugo" proven | 72 -> 12 / 36 / 54 |
| 44 | False faces in the bay; Lola Auring's flashlight; a demon as M; three dark breaths; Ang Huwad cracks; he shields Rico; the window on 1570 | s3; s6 verse as narration; s23 to s27 the answering by the roofs kept as story, once; s54 to s59; s64. Played, not told (62 of 65 sentences are his) | Mistaken identity. Malas mastered | 65 -> 10 / 38 / 58 |
| 45 | Three nights, three shores, each one beat and one diwa; Bohol, the nail gun, Totoy; Tala beside Tubal; her finger | s3; s22 "ang ama ni Totoy" in one clause becomes the scene; s54 to s55 the summons; s56 to s62; s67. Six landings cut to three played and three seen in passing | False betrayal | 68 -> 12 / 36 / 54 |
| 46 | "Pumili ka"; Albo; Tala lays down the contracts; the oldest contract is a brick; Sinag undone; the handle | s3; s20 to s23 the growl "discovered"; s32 "hindi kailanman pumili" against Ep 43 (now true); s53 "pala" works because Ep 41 no longer tells it; s58 to s63; s59 scripture; s68 | Sacrifice | 69 -> 16 / 30 / 50 |
| 47 | The wish; the white night; the table; "Bukas na ngayon."; the door closes; morning; her light leaves the hologram | s3; s17 "unang pagkakataon"; s55 to s56 with any sign that heaven approves; s62 to s66; s67; s70 | The price comes due | 71 -> 18 / 28 / 46 |
| 48 | The banker's face; "Lucifer."; the wound; Rico holds the tabò; the lies cut one by one; seven heads go quiet; the ring drops; he lowers the sword; the woman of the first night | s3; s11 "dagdag lakas" reveal (already in 43); s14, s17 left open; s15; s64 to s70 (the name now comes inside the story); s73 | He loses on purpose. What the dog saw | 74 -> 20 / 28 / 46 |
| 49 | One wish; three ways to spend it; the clock; "ang unang hardin"; the door marked sero; the last salok on the mud; Rico and the child; goodbyes | s3; s12 against s24; s28 to s29 the notebook line (in the Lolo's hand, dated long ago); s41; s57 to s62; s59 Genesis with "Nakasulat"; s65 | The lie he wants to believe | 66 -> 16 / 26 / 46 |
| 50 | The walk; the child reads the marker; nothing; Lola Ising on a bench; the old sidecar motor; behind the door: a shepherd, a staff, a dog, a baby | s4 and s16 the markers that carry the three words stay as picture; s14 to s16; s17 the question moves to the end | Time loop, broken | 29 -> 12 / 8 / 22 |

## 3. Totals

- Sentences now: 3,286. Kept word for word: about 707 (22%). Cut outright: about 1,629. The other 950 or so
  are reworded into dialogue. Lines in the new scripts that are newly written or reworded: about 2,541
  (shorter lines; the spoken word count per episode does not rise).
- The spoken fiction-and-fairness block removed: 47 episodes, about 300 sentences.
- Voice: 50 of 50 re-voiced; about one line in five can reuse an existing take.
- Trivia break: 48 files change (`insert_after_sentence` and the lines); Episodes 1 and 2 gain an end trivia.
- Files per episode when its v2 is written: `script_multispeaker.txt` (master), `script.txt`, `sentences.json`
  (with `speaker`, and `kind: "stage"` for the unspoken lines), `facts.md` (the old rows kept, plus a table of
  what is invented), `shots.md` (one row per shot, drawn from the stage lines).

## 4. Checks before any re-voice (from BIBLE section 12)

1. Search the new invented names against living public figures and real Philippine firms: Aling Charing, Lola
   Auring, Islaw, the friends of each time; and once more "Alcaín Builders" and "Dalisdis Diking Corporation".
2. Two sources for the mango of Episode 18 (the galleon trade and Mexico's "mango de Manila").
3. An independent reader for each of the three briefs on `BIBLE.md` (the panel's judges were stopped by the
   account's weekly limit).
4. The cold-reader test of the Episode 1 sample (`story/ep01_v2/COLD_READ.md`).
