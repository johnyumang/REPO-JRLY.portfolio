# Sound audit — Episode 1, version 4 (16 Nov)

Measured on the files, not by ear. Voice columns come from the dialogue stem (the assembled voice track); the bed is the mix minus the voice (gain fitted by least squares).
LUFS = K-weighted loudness over the line. Voice sim = WavLM speaker similarity to the speaker's own reference (Indio: the centroid of the owner's recording; the others: their cast clip); lines under 0.5 s are not measured.
Edges: level of the first / last 5 ms of sound when it starts or stops from digital silence ("soft" = it fades in/out). Bed hits = 50 ms windows where music/effects come within 3 dB of the voice on that line.
Room floor = the quiet parts inside the line against its median level (a noisier or wetter take has a higher floor); flagged when 8 dB from the same voice elsewhere.
Recogniser = what the speech recogniser heard for the line's chunk, words of the script missing from it.

## Summary

- VERSION 4 (the file sent on 16 Nov): 104 lines; lines with any flag 77
  - voice off its own reference: 31 (Indio lines under 0.93: 20 of 28; Indio similarity min 0.801, median 0.901)
  - level more than 2 LU off the speaker median: 0; pitch more than 15% off: 11; time-stretched: 0; speed outside 4.0-7.0: 25
  - gaps under 0.15 s: 0; dead air over 1.2 s: 0; hard-cut starts/ends: 1; sound before the first word: 0
  - bed less than 12 dB under the voice: 2; an effect as loud as the word on top of it: 1; recogniser word errors: 8; room unlike the same voice elsewhere: 29; another voice within 10 s over 0.90 similarity: 5

## Version 4, line by line

| # | start | speaker | text | LUFS (Δ med) | voice sim (med) | f0 Hz (Δ%) | syl/s | gap s | edges in/out dB | bed under voice dB / hits | recogniser | room floor | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0 | KATIPUNERO | Nasaan ang cedula mo?! | -18.5 (+0.2) | 0.953 (0.943) | 162.0 (+5) | 6.3 | - | -17 / soft | 20.2 / 0 | ok | -8 | ok |
| 1 | 1.6 | INDIO | Walang cedula, kaya may itak sa leeg ko ngayon. | -19.5 (-0.1) | 0.929 (0.901) | 125.0 (+3) | 6.3 | 0.46 | soft / -27 | 18.7 / 0 | missing/changed: ko | -33 | voice 0.929; words: ko |
| 2 | 4.4 | INDIO | Ako 'to si Indio. | -19.1 (+0.3) | 0.946 (0.901) | 143.0 (+18) | 6.7 | 0.43 | soft / soft | 19.0 / 0 | ok | -17 | pitch +18% |
| 3 | 5.6 | INDIO | Malas daw ako. | -19.3 (+0.1) | 0.848 (0.901) | 115.0 (-5) | 6.8 | 0.35 | soft / soft | 16.5 / 0 | ok | -12 | voice 0.848 |
| 4 | 6.8 | INDIO | Ganito 'yan nagsimula. | -19.2 (+0.2) | 0.866 (0.901) | 100.0 (-17) | 8.8 | 0.42 | soft / soft | 17.2 / 0 | ok | -11 | voice 0.866; pitch -17%; speed 8.8 |
| 5 | 8.6 | TAGAPAGSALAYSAY | Kaninang umaga, sa Quezon City, pumila si Indio para sa trab | -19.8 (-0.5) | 0.98 (0.97) | 107.0 (+0) | 4.7 | 0.85 | -10 / soft | 20.8 / 0 | ok | -61 | hard-cut start (-10 dB) |
| 6 | 13.7 | INDIO | Maghapon akong pumila. | -19.4 (+0.0) | 0.9 (0.901) | 131.0 (+8) | 6.4 | 0.46 | soft / soft | 22.0 / 0 | ok | -24 | voice 0.900 |
| 7 | 15.4 | INDIO | Wala pala akong cedula, 'yung resibo ng buwis. | -19.9 (-0.5) | 0.937 (0.901) | 121.0 (+0) | 5.8 | 0.42 | soft / soft | 22.2 / 0 | ok | -72 | room drier than the same voice elsewhere (floor -38 dB) |
| 8 | 18.5 | INDIO | Hindi ko alam na kailangan pala 'yon. | -19.6 (-0.2) | 0.885 (0.901) | 116.0 (-4) | 8.3 | 0.42 | soft / soft | 23.1 / 0 | missing/changed: yon | -28 | voice 0.885; speed 8.3; words: yon |
| 9 | 20.4 | TAGAPAGSALAYSAY | Kaya dinala niya sa sanglaan ang nag-iisang mana niya: ang l | -19.3 (+0.0) | 0.965 (0.97) | 100.0 (-7) | 5.9 | 0.46 | -20 / soft | 21.3 / 0 | ok | -59 | ok |
| 10 | 25.8 | INDIO | Pamasahe lang po sana. | -19.2 (+0.2) | 0.897 (0.901) | 114.0 (-6) | 6.6 | 0.46 | soft / soft | 23.3 / 0 | ok | -6 | voice 0.897 |
| 11 | 27.5 | MAY-ARI | Tanso lang 'yan, tol. | -17.3 (+0.2) | 0.909 (0.855) | 123.0 (+2) | 3.8 | 0.46 | soft / soft | 17.3 / 0 | ok | -16 | speed 3.8 |
| 12 | 29.2 | MAY-ARI | Walang halaga. | -17.6 (-0.1) | 0.8 (0.855) | 117.0 (-3) | 6.0 | 0.42 | soft / soft | 21.1 / 0 | ok | -9 | voice 0.800 (median 0.855) |
| 13 | 30.6 | TAGAPAGSALAYSAY | Sa likod ng may-ari, may katulong na kinakalawang ang kamay. | -19.2 (+0.1) | 0.96 (0.97) | 108.0 (+1) | 5.9 | 0.46 | -29 / soft | 20.8 / 0 | ok | -54 | ok |
| 14 | 34.4 | TAGAPAGSALAYSAY | Bago ibinalik ang medalyon, palihim niya itong idiniin sa is | -19.1 (+0.2) | 0.985 (0.97) | 106.0 (-1) | 6.3 | 0.42 | -24 / soft | 21.2 / 0 | ok | -37 | room noisier/wetter than the same voice elsewhere (floor +17 dB) |
| 15 | 39.3 | INDIO | Gutom na 'ko. | -19.4 (+0.0) | 0.801 (0.901) | 156.0 (+29) | 6.2 | 0.46 | -23 / soft | 18.6 / 0 | ok | -18 | voice 0.801; pitch +29% |
| 16 | 40.4 | TAGAPAGSALAYSAY | Sa kanto, may paresan. | -19.4 (-0.1) | 0.98 (0.97) | 116.0 (+8) | 3.2 | 0.47 | soft / soft | 17.6 / 0 | ok | -62 | speed 3.2 |
| 17 | 43.0 | TAGAPAGSALAYSAY | Hindi niya kaya ang isang mangkok. | -19.0 (+0.3) | 0.97 (0.97) | 110.0 (+3) | 7.3 | 0.43 | soft / soft | 21.6 / 0 | ok | -21 | speed 7.3; room noisier/wetter than the same voice elsewhere (floor +33 dB) |
| 18 | 44.9 | TAGAPAGSALAYSAY | Tinapay lang ang nabili niya. | -19.5 (-0.2) | 0.967 (0.97) | 117.0 (+9) | 4.9 | 0.42 | soft / soft | 18.3 / 0 | ok | -64 | room drier than the same voice elsewhere (floor -10 dB) |
| 19 | 47.4 | INDIO | Pares: taga-Quezon City, gaya ko. | -19.6 (-0.2) | 0.856 (0.901) | 115.0 (-5) | 3.5 | 0.47 | soft / soft | 17.2 / 0 | ok | -72 | voice 0.856; speed 3.5; room drier than the same voice elsewhere (floor -38 dB) |
| 20 | 50.7 | INDIO | Sabi nila, nagsimula ito sa Retiro noong 1979. | -19.7 (-0.3) | 0.972 (0.901) | 118.0 (-2) | 3.4 | 0.43 | soft / soft | 20.5 / 0 | ok | -41 | speed 3.4 |
| 21 | 55.5 | INDIO | Ngayon, nasa buong Pilipinas na. | -19.7 (-0.3) | 0.907 (0.901) | 105.0 (-13) | 5.5 | 0.42 | soft / soft | 19.2 / 0 | ok | -55 | voice 0.907; room drier than the same voice elsewhere (floor -21 dB) |
| 22 | 57.8 | INDIO | Diwata, baka naman! | -20.0 (-0.6) | 0.917 (0.901) | 174.0 (+44) | 4.8 | 0.43 | soft / soft | 21.0 / 0 | ok | -57 | voice 0.917; pitch +44% |
| 23 | 60.1 | TAGAPAGSALAYSAY | Pagsapit ng gabi, bumuhos ang ulan. | -19.5 (-0.2) | 0.982 (0.97) | 118.0 (+10) | 4.8 | 0.85 | -23 / soft | 18.2 / 0 | ok | -56 | ok |
| 24 | 63.0 | TAGAPAGSALAYSAY | Sumilong si Indio sa dambana ng Pugad Lawin, sa Bahay Toro. | -19.3 (+0.0) | 0.983 (0.97) | 104.0 (-3) | 5.0 | 0.42 | soft / soft | 20.3 / 0 | missing/changed: pugad lawin | -35 | room noisier/wetter than the same voice elsewhere (floor +18 dB); words: pugad lawin |
| 25 | 67.5 | INDIO | Wala akong kausap. | -19.2 (+0.2) | 0.808 (0.901) | 125.0 (+3) | 6.5 | 0.47 | soft / soft | 20.0 / 0 | ok | -11 | voice 0.808 |
| 26 | 68.8 | INDIO | Marker na lang. | -19.9 (-0.5) | 0.867 (0.901) | 118.0 (-2) | 5.6 | 0.41 | soft / soft | 20.0 / 0 | ok | -19 | voice 0.867; voice close to TAGAPAGSALAYSAY 0.90, TAGAPAGSALAYSAY 0.92 |
| 27 | 70.0 | TAGAPAGSALAYSAY | Binasa niya nang malakas ang nakasulat. | -18.7 (+0.6) | 0.953 (0.97) | 102.0 (-5) | 6.7 | 0.46 | -28 / soft | 19.1 / 0 | ok | -13 | room noisier/wetter than the same voice elsewhere (floor +41 dB) |
| 28 | 72.5 | TAGAPAGSALAYSAY | Uminit ang medalyon sa dibdib niya. | -18.8 (+0.5) | 0.966 (0.97) | 105.0 (-2) | 6.5 | 0.42 | -25 / soft | 22.0 / 0 | ok | -11 | room noisier/wetter than the same voice elsewhere (floor +43 dB); voice close to INDIO 0.90 |
| 29 | 74.8 | TAGAPAGSALAYSAY | At tumigil sa ere ang mga patak ng ulan. | -19.4 (-0.1) | 0.982 (0.97) | 105.0 (-2) | 5.9 | 0.42 | soft / soft | 21.2 / 0 | ok | -29 | room noisier/wetter than the same voice elsewhere (floor +25 dB) |
| 30 | 77.6 | TAGAPAGSALAYSAY | Mula sa liwanag, lumundag ang isang asong itim. | -19.4 (-0.1) | 0.971 (0.97) | 108.0 (+1) | 5.0 | 0.42 | -19 / soft | 21.0 / 0 | ok | -59 | voice close to INDIO 0.92 |
| 31 | 81.2 | USMAN | Kumapit ka, Indio! | -19.3 (+0.2) | 0.828 (0.901) | 253.0 (+4) | 5.6 | 0.46 | -18 / soft | 16.3 / 0 | ok | -25 | voice 0.828 (median 0.901) |
| 32 | 82.8 | INDIO | Teka, nagsalita 'yung aso? | -20.2 (-0.8) | 0.901 (0.901) | 122.0 (+1) | 5.4 | 0.47 | soft / soft | 21.2 / 0 | ok | -70 | voice 0.901; room drier than the same voice elsewhere (floor -36 dB) |
| 33 | 85.3 | TAGAPAGSALAYSAY | Agosto 1896. | -18.6 (+0.7) | 0.969 (0.97) | 114.0 (+7) | 1.2 | 0.84 | -22 / soft | 19.8 / 0 | ok | -15 | speed 1.2 |
| 34 | 88.2 | TAGAPAGSALAYSAY | Isang bakuran sa labas ng Maynila, puno ng mga Katipunero. | -19.1 (+0.2) | 0.977 (0.97) | 110.0 (+3) | 5.9 | 0.42 | -29 / soft | 20.5 / 0 | ok | -53 | ok |
| 35 | 92.2 | TAGAPAGSALAYSAY | Hinablot si Indio, at hinarang ng isang batang may itak. | -19.4 (-0.1) | 0.981 (0.97) | 111.0 (+4) | 4.9 | 0.42 | soft / soft | 20.9 / 0 | ok | -50 | ok |
| 36 | 96.3 | TAGAPAGSALAYSAY | Siya si Islaw. | -18.9 (+0.4) | 0.899 (0.97) | 100.0 (-7) | 5.3 | 0.42 | -14 / soft | 20.8 / 0 | ok | -14 | voice 0.899 (median 0.970) |
| 37 | 97.7 | TAGAPAGSALAYSAY | Labindalawang taong gulang, anak ng magsasaka, at bantay ng  | -19.3 (+0.0) | 0.978 (0.97) | 104.0 (-3) | 4.9 | 0.42 | -29 / soft | 20.2 / 0 | ok | -63 | room drier than the same voice elsewhere (floor -9 dB) |
| 38 | 103.5 | ISLAW | Sino ka? | -16.6 (+0.8) | - (0.929) | 249.0 (+0) | 6.5 | 0.46 | soft / soft | 20.6 / 0 | ok | -15 | ok |
| 39 | 104.3 | ISLAW | Sino'ng nagsama sa'yo rito? | -17.1 (+0.3) | 0.897 (0.929) | 265.0 (+6) | 7.3 | 0.42 | soft / soft | 14.2 / 0 | ok | -12 | voice 0.897 (median 0.929); speed 7.3 |
| 40 | 106.0 | TAGAPAGSALAYSAY | Lumapit ang pinuno ng mga bantay, isang Katipunerong hindi n | -19.1 (+0.2) | 0.979 (0.97) | 107.0 (+0) | 5.7 | 0.47 | soft / soft | 19.4 / 0 | ok | -43 | room noisier/wetter than the same voice elsewhere (floor +11 dB); voice close to KATIPUNERO 0.91 |
| 41 | 110.7 | KATIPUNERO | May nagsumbong sa amin sa Kastila. | -18.5 (+0.2) | 0.944 (0.943) | 145.0 (-6) | 6.5 | 0.47 | soft / soft | 17.9 / 0 | ok | -12 | room noisier/wetter than the same voice elsewhere (floor +25 dB) |
| 42 | 112.8 | KATIPUNERO | Kaya lahat ng narito, may dalang cedula ngayong gabi. | -19.4 (-0.7) | 0.955 (0.943) | 149.0 (-4) | 6.3 | 0.42 | soft / soft | 19.4 / 0 | ok | -37 | voice close to TAGAPAGSALAYSAY 0.91 |
| 43 | 116.1 | KATIPUNERO | Ilabas mo ang sa'yo. | -18.4 (+0.3) | 0.93 (0.943) | 143.0 (-8) | 7.2 | 0.42 | soft / soft | 17.6 / 0 | ok | -13 | speed 7.2 |
| 44 | 117.5 | INDIO | Cedula? | -19.9 (-0.5) | - (0.901) | 153.0 (+26) | 6.4 | 0.47 | soft / soft | 20.8 / 0 | ok | -9 | pitch +26% |
| 45 | 118.4 | INDIO | 'Yan din ang hinanap sa akin kaninang umaga. | -19.2 (+0.2) | 0.949 (0.901) | 123.0 (+2) | 7.1 | 0.42 | soft / soft | 16.2 / 0 | ok | -15 | speed 7.1; room noisier/wetter than the same voice elsewhere (floor +19 dB) |
| 46 | 121.0 | KATIPUNERO | Walang papel, walang kakilala. | -18.9 (-0.2) | 0.943 (0.943) | 155.0 (+0) | 5.8 | 0.47 | soft / soft | 16.4 / 0 | ok | -48 | room drier than the same voice elsewhere (floor -12 dB) |
| 47 | 123.2 | KATIPUNERO | Espiya 'yan. | -19.7 (-1.0) | 0.811 (0.943) | 164.0 (+6) | 6.0 | 0.43 | soft / soft | 16.6 / 0 | missing/changed: espiya yan | -34 | voice 0.811 (median 0.943); words: espiya yan |
| 48 | 124.3 | TAGAPAGSALAYSAY | Itinali ang mga kamay niya. | -19.3 (+0.0) | 0.955 (0.97) | 107.0 (+0) | 6.7 | 0.47 | -23 / soft | 20.0 / 0 | ok | -14 | room noisier/wetter than the same voice elsewhere (floor +40 dB) |
| 49 | 126.2 | TAGAPAGSALAYSAY | Idinikit ang itak sa leeg niya. | -19.2 (+0.1) | 0.951 (0.97) | 112.0 (+5) | 6.5 | 0.42 | soft / soft | 19.0 / 0 | ok | -31 | room noisier/wetter than the same voice elsewhere (floor +23 dB) |
| 50 | 128.4 | INDIO | Unang araw ko sa nakaraan. | -19.4 (+0.0) | 0.946 (0.901) | 120.0 (-1) | 6.5 | 0.47 | soft / soft | 23.0 / 0 | ok | -10 | room noisier/wetter than the same voice elsewhere (floor +24 dB) |
| 51 | 130.2 | INDIO | Mukhang huling araw ko na rin. | -19.3 (+0.1) | 0.89 (0.901) | 104.0 (-14) | 7.2 | 0.43 | soft / soft | 18.7 / 0 | ok | -20 | voice 0.890; speed 7.2; room noisier/wetter than the same voice elsewhere (floor +13 dB) |
| 52 | 131.9 | USMAN | Par. | -19.5 (+0.0) | - (0.901) | 244.0 (+0) | 2.9 | 0.47 | soft / soft | 21.4 / 0 | ok | -13 | speed 2.9 |
| 53 | 132.6 | USMAN | Sabihin mo ang totoo. | -19.3 (+0.2) | 0.848 (0.901) | 196.0 (-20) | 6.4 | 0.39 | soft / soft | 15.9 / 0 | ok | -13 | voice 0.848 (median 0.901); pitch -20% |
| 54 | 134.1 | USMAN | 'Yun lang ang meron ka. | -19.9 (-0.4) | 0.959 (0.901) | 170.0 (-30) | 6.1 | 0.43 | soft / soft | 11.8 / 0 | ok | -10 | pitch -30%; bed 11.8 dB under |
| 55 | 135.6 | INDIO | Wala akong cedula. | -19.3 (+0.1) | 0.889 (0.901) | 129.0 (+7) | 7.6 | 0.47 | soft / soft | 23.3 / 0 | ok | -10 | voice 0.889; speed 7.6 |
| 56 | 136.9 | INDIO | Wala akong trabaho. | -19.3 (+0.1) | 0.868 (0.901) | 115.0 (-5) | 6.8 | 0.43 | soft / soft | 24.6 / 0 | ok | -15 | voice 0.868 |
| 57 | 138.4 | INDIO | Wala akong kahit ano. | -19.8 (-0.4) | 0.881 (0.901) | 113.0 (-7) | 8.6 | 0.42 | soft / soft | 21.4 / 0 | ok | -32 | voice 0.881; speed 8.6 |
| 58 | 139.7 | INDIO | Kaya nga ako napadpad dito. | -20.3 (-0.9) | 0.929 (0.901) | 144.0 (+19) | 7.0 | 0.43 | soft / soft | 23.5 / 0 | ok | -35 | voice 0.929; pitch +19% |
| 59 | 141.6 | TAGAPAGSALAYSAY | Natigilan ang bata. | -19.2 (+0.1) | 0.936 (0.97) | 98.0 (-8) | 5.6 | 0.47 | soft / soft | 22.8 / 0 | ok | -20 | voice 0.936 (median 0.970) |
| 60 | 143.3 | TAGAPAGSALAYSAY | Bumaba ang itak. | -19.4 (-0.1) | 0.961 (0.97) | 102.0 (-5) | 5.7 | 0.43 | soft / soft | 22.1 / 0 | ok | -35 | ok |
| 61 | 144.8 | ISLAW | Wala rin akong cedula. | -16.9 (+0.5) | 0.9 (0.929) | 268.0 (+8) | 7.3 | 0.47 | -28 / soft | 16.9 / 0 | ok | -10 | speed 7.3 |
| 62 | 146.3 | ISLAW | Hindi kayang bayaran ni Itay. | -17.4 (+0.0) | 0.949 (0.929) | 209.0 (-16) | 7.5 | 0.43 | soft / soft | 14.5 / 0 | ok | -14 | speed 7.5 |
| 63 | 148.2 | TAGAPAGSALAYSAY | Saka lumapit ang mga aso ng kampo. | -18.9 (+0.4) | 0.947 (0.97) | 100.0 (-7) | 5.7 | 0.46 | soft / soft | 19.5 / 0 | ok | -26 | room noisier/wetter than the same voice elsewhere (floor +27 dB) |
| 64 | 150.7 | TAGAPAGSALAYSAY | Inamoy siya, kinain ang tinapay niya, at humiga sa paanan ni | -19.7 (-0.4) | 0.958 (0.97) | 110.0 (+3) | 5.6 | 0.43 | soft / soft | 21.2 / 0 | ok | -61 | ok |
| 65 | 155.1 | USMAN | Kinausap ko sila. | -18.9 (+0.6) | 0.907 (0.901) | 258.0 (+6) | 6.8 | 0.47 | -18 / soft | 14.6 / 0 | ok | -19 | ok |
| 66 | 156.4 | USMAN | May bayad nga lang: hapunan mo. | -19.5 (+0.0) | 0.933 (0.901) | 222.0 (-9) | 6.1 | 0.43 | -29 / soft | 17.8 / 0 | ok | -11 | ok |
| 67 | 158.3 | ISLAW | Hindi tumatahimik ang aso sa espiya. | -17.3 (+0.1) | 0.932 (0.929) | 229.0 (-8) | 7.6 | 0.47 | soft / soft | 11.8 / 1 | ok | -26 | speed 7.6; bed 11.8 dB under; effect on a word (1); room drier than the same voice elsewhere (floor -10 dB) |
| 68 | 160.6 | ISLAW | Kalagan n'yo siya. | -17.4 (+0.0) | 0.778 (0.929) | 276.0 (+11) | 9.1 | 0.42 | -12 / soft | 23.4 / 0 | ok | -13 | voice 0.778 (median 0.929); speed 9.1 |
| 69 | 161.7 | KATIPUNERO | Sino ka ba talaga? | -18.7 (+0.0) | 0.86 (0.943) | 174.0 (+12) | 8.2 | 0.46 | soft / soft | 19.5 / 0 | ok | -14 | voice 0.860 (median 0.943); speed 8.2 |
| 70 | 163.0 | INDIO | Wala. | -19.8 (-0.4) | - (0.901) | - (-) | 8.3 | 0.46 | soft / soft | 20.8 / 0 | ok | -9 | speed 8.3 |
| 71 | 163.7 | INDIO | Tambay lang. | -19.3 (+0.1) | 0.919 (0.901) | 104.0 (-14) | 5.9 | 0.43 | soft / soft | 22.0 / 0 | ok | -12 | voice 0.919 |
| 72 | 165.0 | TAGAPAGSALAYSAY | Sa gilid ng liwanag, may mag-asawang nagpapaalam. | -19.5 (-0.2) | 0.986 (0.97) | 124.0 (+16) | 5.1 | 0.84 | soft / soft | 22.4 / 0 | ok | -59 | pitch +16% |
| 73 | 168.6 | TAGAPAGSALAYSAY | Ang babae, si Oriang. | -20.1 (-0.8) | 0.968 (0.97) | 103.0 (-4) | 3.3 | 0.43 | -26 / soft | 18.6 / 0 | ok | -57 | speed 3.3 |
| 74 | 170.8 | TAGAPAGSALAYSAY | Itinali niya ang pulang panyo sa leeg ng lalaki. | -19.2 (+0.1) | 0.987 (0.97) | 104.0 (-3) | 6.3 | 0.43 | -18 / soft | 22.8 / 0 | ok | -21 | room noisier/wetter than the same voice elsewhere (floor +32 dB) |
| 75 | 174.0 | ORIANG | Kapag pinunit mo 'yan, wala na tayong uuwian. | -19.2 (+0.0) | 0.969 (0.969) | 182.0 (+0) | 4.8 | 0.47 | soft / soft | 22.6 / 0 | ok | -32 | ok |
| 76 | 177.4 | BONIFACIO | Kaya nga pupunitin ko. | -18.2 (+0.4) | 0.893 (0.893) | 181.0 (+6) | 6.9 | 0.47 | soft / soft | 23.6 / 0 | missing/changed: pupunitin | -20 | words: pupunitin |
| 77 | 178.9 | BONIFACIO | Para may uuwian ang lahat. | -18.6 (+0.0) | 0.904 (0.893) | 170.0 (+0) | 5.4 | 0.43 | soft / soft | 23.8 / 0 | ok | -22 | ok |
| 78 | 180.9 | USMAN | Huwag kang tumitig, par. | -19.9 (-0.4) | 0.846 (0.901) | 254.0 (+4) | 5.7 | 0.47 | soft / soft | 22.6 / 0 | missing/changed: tumitig par | -41 | voice 0.846 (median 0.901); words: tumitig par |
| 79 | 182.6 | TAGAPAGSALAYSAY | Humakbang ang lalaki sa liwanag, at itinaas ang kanyang cedu | -19.4 (-0.1) | 0.987 (0.97) | 108.0 (+1) | 5.8 | 0.47 | soft / soft | 20.4 / 0 | ok | -53 | ok |
| 80 | 186.7 | ISLAW | Ang Supremo. | -17.6 (-0.2) | 0.95 (0.929) | 252.0 (+1) | 3.7 | 0.47 | soft / soft | 17.1 / 0 | ok | -49 | speed 3.7 |
| 81 | 188.2 | ISLAW | Si Andres Bonifacio. | -17.9 (-0.5) | 0.94 (0.929) | 246.0 (-1) | 5.6 | 0.42 | soft / soft | 18.1 / 0 | ok | -13 | ok |
| 82 | 190.0 | BONIFACIO | Punitin ang mga cedula! | -18.8 (-0.2) | 0.869 (0.893) | 170.0 (+0) | 6.5 | 0.55 | soft / soft | 20.0 / 0 | ok | -14 | ok |
| 83 | 191.7 | MGA KATIPUNERO | Mabuhay ang Pilipinas! | -18.1 (+0.0) | 0.832 (0.832) | 196.0 (+0) | 5.8 | 0.47 | -28 / soft | 18.2 / 0 | ok | -24 | ok |
| 84 | 193.5 | ISLAW | Buwis namin 'yan sa Kastila. | -17.3 (+0.1) | 0.926 (0.929) | 260.0 (+4) | 6.5 | 0.47 | -28 / soft | 14.0 / 0 | missing/changed: buwis | -15 | words: buwis |
| 85 | 195.3 | ISLAW | Kapag pinunit mo, wala nang atrasan. | -17.7 (-0.3) | 0.932 (0.929) | 219.0 (-12) | 5.6 | 0.43 | -13 / soft | 15.0 / 0 | ok | -40 | room drier than the same voice elsewhere (floor -25 dB) |
| 86 | 198.0 | INDIO | 'Yung papel na kulang sa akin kaninang umaga, pinupunit nila | -19.5 (-0.1) | 0.963 (0.901) | 108.0 (-11) | 6.7 | 0.47 | soft / soft | 17.0 / 0 | ok | -34 | ok |
| 87 | 202.5 | TAGAPAGSALAYSAY | Walang mapunit si Islaw, kaya kamao na lang ang itinaas nila | -19.4 (-0.1) | 0.982 (0.97) | 105.0 (-2) | 5.3 | 0.47 | soft / soft | 20.8 / 0 | ok | -58 | ok |
| 88 | 207.3 | ISLAW | Kuya, babalik ka ba? | -17.6 (-0.2) | 0.909 (0.929) | 230.0 (-8) | 4.7 | 0.46 | soft / soft | 13.5 / 0 | ok | -57 | ok |
| 89 | 209.6 | TAGAPAGSALAYSAY | Bago pa siya makasagot, lumamig ang medalyon. | -19.4 (-0.1) | 0.971 (0.97) | 100.0 (-7) | 5.6 | 0.84 | -28 / soft | 20.8 / 0 | ok | -61 | ok |
| 90 | 212.9 | USMAN | May marka ka na, par. | -19.8 (-0.3) | 0.917 (0.901) | 256.0 (+5) | 4.9 | 0.47 | soft / soft | 22.5 / 0 | ok | -41 | ok |
| 91 | 214.6 | USMAN | Una pa lang 'yan. | -19.7 (-0.2) | 0.896 (0.901) | 230.0 (-6) | 6.9 | 0.43 | soft / soft | 15.2 / 0 | ok | -13 | ok |
| 92 | 215.8 | TAGAPAGSALAYSAY | Quezon City ulit. | -18.8 (+0.5) | 0.959 (0.97) | 114.0 (+7) | 4.4 | 0.47 | soft / soft | 22.2 / 0 | ok | -17 | ok |
| 93 | 217.3 | TAGAPAGSALAYSAY | Ulan. | -18.6 (+0.7) | - (0.97) | 97.0 (-9) | 4.1 | 0.43 | soft / soft | 21.7 / 0 | ok | -8 | ok |
| 94 | 218.3 | TAGAPAGSALAYSAY | Wala na ang aso. | -18.8 (+0.5) | 0.894 (0.97) | 100.0 (-7) | 5.9 | 0.42 | soft / soft | 21.4 / 0 | ok | -10 | voice 0.894 (median 0.970) |
| 95 | 219.7 | TAGAPAGSALAYSAY | Pero sa braso ni Indio, may guhit na umuusok pa. | -19.5 (-0.2) | 0.973 (0.97) | 111.0 (+4) | 4.9 | 0.42 | -23 / soft | 20.7 / 0 | ok | -63 | room drier than the same voice elsewhere (floor -9 dB) |
| 96 | 223.4 | INDIO | Aray. | -18.7 (+0.7) | - (0.901) | 163.0 (+35) | 7.4 | 0.47 | soft / soft | 21.1 / 0 | ok | -9 | pitch +35%; speed 7.4 |
| 97 | 224.1 | INDIO | Usman. | -19.3 (+0.1) | - (0.901) | 187.0 (+55) | 6.5 | 0.42 | soft / soft | 20.1 / 0 | ok | -7 | pitch +55% |
| 98 | 224.8 | INDIO | 'Yun ang itatawag ko sa'yo. | -19.1 (+0.3) | 0.888 (0.901) | 110.0 (-9) | 8.4 | 0.43 | soft / soft | 23.3 / 0 | ok | -18 | voice 0.888; speed 8.4; room noisier/wetter than the same voice elsewhere (floor +16 dB) |
| 99 | 226.3 | INDIO | Pangalan ng aso sa mga kuwento ni Lolo. | -19.2 (+0.2) | 0.939 (0.901) | 125.0 (+3) | 7.0 | 0.43 | soft / soft | 22.0 / 0 | ok | -16 | room noisier/wetter than the same voice elsewhere (floor +18 dB) |
| 100 | 228.8 | TAGAPAGSALAYSAY | Sa kabilang kalye, may babaeng nakatitig sa kanya, na parang | -19.5 (-0.2) | 0.976 (0.97) | 108.0 (+1) | 5.1 | 0.46 | soft / soft | 18.2 / 0 | ok | -62 | ok |
| 101 | 234.0 | TAGAPAGSALAYSAY | Sa sanglaan, hawak ng katulong ang pagkit: buong-buo ang bak | -19.6 (-0.3) | 0.966 (0.97) | 111.0 (+4) | 4.1 | 0.43 | soft / soft | 19.2 / 0 | missing/changed: sa sanglaan | -62 | room drier than the same voice elsewhere (floor -9 dB); words: sa sanglaan |
| 102 | 239.6 | KATULONG | Tanso lang pala, ha. | -19.1 (+0.0) | 0.855 (0.855) | 192.0 (+0) | 5.4 | 0.47 | soft / soft | 18.5 / 0 | ok | -14 | ok |
| 103 | 241.2 | INDIO | Ikaw, ka-Indio: kung hinanapan ka ng papel na wala ka, magsi | -20.0 (-0.6) | 0.957 (0.901) | 139.0 (+15) | 5.3 | 0.47 | soft / soft | 20.7 / 0 | ok | -72 | room drier than the same voice elsewhere (floor -38 dB) |

