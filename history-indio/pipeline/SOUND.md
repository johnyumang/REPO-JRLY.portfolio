# Sound for History Indio

What we learned about how animated films and short vertical videos are sounded, what we chose, and how to write a sound plan.
The research was done with web searches, working from the search summaries: no page was opened and read in full
(every source below says `opened: false`). Treat the numbers as starting points that people in the trade quote, not as standards.

## 1. The layers of a film's sound

A film's sound is built in layers that play at the same time. Each has its own job:

| Layer | Its job | What we make |
|---|---|---|
| Dialogue / narration | The message. Always on top. | Indio's voice (the recording) |
| Ambience bed ("room tone" indoors, "air tone" outdoors) | Says where we are. It never stops: a scene with no bed sounds like a hole, so cuts sound choppy. | `amb`: night insects, rain, wind, sea, forest, city, crowd, fire, indoor, office |
| Foley | Makes the characters touch the world: footsteps by surface, cloth, props. Without it, characters seem to float. | `foley`: steps on earth, grass, stone, wood, wet street; cloth; paper; a door; a dog's paws, panting, growl |
| Spot effects | Single events: thunder, a cannon, a bell, an impact. | `spot` |
| Walla | The murmur of many people with no words you can follow. Loop groups record it in post-production; the name comes from actors repeating "walla walla". It makes a place sound full without fighting the dialogue. | `crowd` bed, `walla`, `cheer`, `whisper` |
| Music and stingers | Emotion. Stingers (a riser, a hit) mark a turn. | `music` |
| Silence | A beat of silence just before a hit lets the ear reset, so the hit lands harder. | `"hush"` on a spot effect |

The usual order of work: dialogue first, then ambience and effects at lower levels, music last, ducked under the voice.

## 2. Levels under the voice

The sources disagree on exact numbers, but they cluster:

- Music under speech: about 12 to 25 dB under the voice (tutorials quote -18 to -25 dB for music under interviews; Premiere's
  auto-ducking suggests -12 dB for a gentle duck and -18 dB for a clear one).
- Ducking (the dip while someone speaks): 6 to 12 dB is a gentle-to-normal dip, with short ramps; -30 dB nearly removes the layer.
- Effects: about 10 to 20 dB under the voice, background effects (birds) 20 to 30 dB under. Effects may be louder than that
  when nobody is speaking: that is where a hit goes.
- Judge by intelligibility, not by the meter.

**What we chose** (in `sound_design.py`, against the voice's gated RMS): beds -6 dB and music -5 dB between words, both ducked 5 dB
while the voice speaks, so the whole bed sits about 11 to 12 dB under speech (the build log prints `bed_vs_voice_in_speech_db`);
foley -8 dB, spot effects -4 dB, ducked only 3 dB so they can still peak between words, and softly limited so no effect passes
the voice's own peak. Beds cross-fade over 0.6 s at line changes. The finished mix then goes through the same loudness guard as
before (`soundtrack.loudnorm2`: -16 LUFS within 0.5, true peak at or under -1.5 dBTP after the AAC encode).
These are louder than the "music at -20 dB" of talking-head video on purpose: this is a cartoon that wants the air of a film,
and the narration is close and dense. If the voice ever sounds buried, lower `AMB_DB`/`MUSIC_DB` by 2 to 3 dB, not the voice.

## 3. Sound in short vertical videos

- The first second decides whether people stay: start with a hit or a strong sound, not a fade-in.
- Riser, whoosh and impact are the three effects every short-video guide recommends: a riser builds to a moment, a whoosh
  carries a cut, an impact lands it.
- Keep them sparse: one guide suggests 3 to 5 noticeable effects per 30 seconds; more distracts from the voice.
- Sound changes are "pattern interrupts": a beat drop, a whoosh, or a sudden silence re-hooks attention.
(All of these come from creator and vendor blogs, not studies.)

## 4. Philippine instruments: whose they are, and when to use them

Use an instrument only where it belongs. Our hero is Tagalog and most episodes are set in Tagalog Manila and its provinces.

| Instrument | Whose it is | Use it for |
|---|---|---|
| Kulintang (a row of knobbed gongs), agung (big hanging gongs), dabakan (drum) (`music: gongs`, `spot: gong`) | Mindanao and Sulu: the Maguindanao, Maranao, Tausug, Sama-Bajau, Iranun, Yakan and others; related gong music among Lumad peoples (T'boli, Blaan, Subanon). | Scenes set among those peoples (Sulu, Lanao, Maguindanao, the sultanates). NOT under a Tagalog scene as if it were Tagalog music. |
| Gangsa (flat gongs) | The Cordillera: Kalinga, Ifugao, Bontok, Ibaloi, Kankanai, Isneg, Tingguian and others. | Cordillera scenes only (we do not synthesise it yet; the `gong` is a boss gong, not a flat gangsa). |
| Kubing (bamboo jaw harp) | Maranao, Maguindanao, T'boli and others; jaw harps are found in many regions (one source names a Tagalog-region name, barmbaw). | Not built yet. |
| Nose flutes (tongali, kalleleng) | Cordillera (Ifugao, Kalinga, Bontok, Kankanai). | Cordillera scenes. |
| Bamboo flute (`music: flute`) | Bamboo flutes are found all over the islands; the names plawta/palawta/flauta are borrowed from the Spanish flauta. | A neutral "old Philippines / countryside" colour. Do not call it a specific people's instrument. |
| Guitar, bandurria, the rondalla (`music: guitar`) | Came with Spain and became Filipino over the colonial centuries; the rondalla took its present shape in the late 1800s and spread in the American time. The kundiman (Tagalog song, triple time, starting in minor) is accompanied this way; "Jocelynang Baliwag" was the kundiman of the 1896 revolutionaries of Bulacan. | Tagalog lowland scenes from the Spanish time to today; emotion. Our `guitar` is a fingerpicked 3/4 in A minor in that spirit. |
| Banda (town brass band, `music: band`) | Spanish regimental bands and town bands (in Nueva Ecija, Malabon and elsewhere) in the late 1800s; the Malabon bamboo band (musikong bumbong) helped the Katipunan hide weapons at the 24 August 1896 feast. The banda is the sound of 1898 public events (fiestas, the June 1898 independence ceremonies). | Fiestas, parades, 1898. Not a secret Katipunan gathering. |
| Heartbeat drum, drone (`music: heartbeat`, `music: drone`) | Not an ethnic instrument: film language for tension and dread. | Magic, danger, the time leap. |

We did not find a reliable source on pre-colonial Tagalog instruments (William Henry Scott's *Barangay* and José Maceda's work
would be where to look). Until someone reads them, do not invent a "pre-colonial Tagalog" sound.

## 5. What the generators sound like (honest notes)

Everything is synthesised in code. I cannot hear: these notes come from the numbers (`sound_design.py --report` prints level,
peak, crest and the spectrum centroid of each one) and from how each is built. A person should listen to each WAV the report
writes before trusting it.

Each generator is normalised to -24 dBFS over the part that sounds (the mix rescales it again). Spectrum centroids from the
report (Hz, magnitude-weighted, so broadband noise reads high): wind 302, sea 778, city 568, crowd 686, fire 1888, indoor 1378,
office 1452, night insects 3360, rain light 5030, heavy 4589; steps earth 1472, wood 824, stone 4492, grass 4702, wet 3525;
cloth 5413, paper tear 6270, door 1615, dog paws 3864, panting 1529, growl 628; cannon 157, thunder 324, bell 395, gong 110,
impact 467, whoosh 5793, riser 5221, shimmer 5539, drone 187, heartbeat 102, cheer 3283, whisper 4322, walla 3942;
guitar 2441, flute 2170, gongs 384, band 4166. Crest factors (peak over RMS) run from about 8 dB (flute, drone) to 30 dB
(stone steps, paper): the clicky ones are the transient sounds, as they should be.

Likely convincing (noise-shaped textures, which synthesis does well): **rain light and heavy, wind, sea, fire, indoor and office
room tone, city rumble, thunder, cannon, impact, whoosh, riser, drone, heartbeat, splash**. Listen for: rain that sounds like
frying (too many high drops: lower `_rain`'s drop rate), wind without movement, a thunder that ends too cleanly.

Middling: **footsteps** (earth and wood are believable thuds; stone and wet are clicky; listen for "typewriter" regularity),
**cloth**, **paper tear** (listen for whether it sounds like paper or like static), **dog paws**, **crowd** at a distance
(a far murmur is forgiving), **bell** (bell partials are right, the strike is simple), **night insects** (crickets are just
pulsed sines: they may sound electronic).

Will sound like a synthesiser: **guitar** (Karplus-Strong pluck: recognisably a plucked string, but plain and too even),
**flute** (a sine with breath: reads as "flute" from a distance), **band** (sawtooth brass: sounds like a toy organ; use sparingly),
**gongs/kulintang** (sine-based), **walla up close, cheer and whisper** (speech-shaped noise with no words: from far away it
reads as people, close up it may sound like wind with a lisp), **growl** and **dog panting** (they may sound mechanical).
For the cheer of "Mabuhay!" and for whispers, a real recording of people (even a few friends, layered) would beat anything here.

## 6. How to write a sound plan for an episode (videos/<slug>/sound.json)

1. Read the episode's `sentences.json` and `timings.json`; the keys of the plan are the ORIGINAL sentence numbers, like `shots_fx.json`.
2. For each change of place, set `"amb"` (one name or a list; `"city:-8"` puts that bed 8 dB lower) and `"music"`; lines without an entry keep the bed of the line before.
3. Add foley and spot effects with `"at"` in seconds from the start of that line (a riser's `"at"` is where it peaks); `"gain"` in dB, `"hush"` for a silence before a hit; keep it to a few noticeable effects per 30 seconds.
4. Add `"_": {"whoosh_cuts": true}` for a soft whoosh on every cut; use `"level"` (dB) to pull a whole stretch down or up.
5. Build as usual with `build_anime.py`; check the printed `bed_vs_voice_in_speech_db` (about -10 to -13 is right) and the loudness lines. No sound.json: the episode sounds exactly as before.

Names: ambience `night_insects rain_light rain_heavy wind sea forest city crowd fire indoor office`; foley and spot
`steps_earth steps_grass steps_stone steps_wood steps_wet` (with `pace` walk/run/sneak and `count`) `cloth paper_tear paper_tear_many door
dog_paws dog_pant growl cannon thunder bell splash gong impact whoosh riser shimmer drone heartbeat cheer whisper walla`; music
`none guitar flute gongs band drone heartbeat`.

## Sources (all opened: false; read as search summaries)

- Mixing levels: pixflow.net "How to Mix Dialogue, Music, and Sound Effects in Premiere Pro" (https://pixflow.net/blog/?p=92478); iZotope "Mixing audio for video, part 4" (https://www.izotope.com/en/learn/mixing-audio-for-video-part-4-mixing-techniques); Storyblocks "7 essential audio editing tips" (https://www.storyblocks.com/resources/tutorials/7-essential-audio-editing-tips); Syracuse "The Art of Sound Mixing" (https://nhtraining.syr.edu/the-art-of-sound-mixing/); cursa.app Fairlight essentials (https://cursa.app/en/page/davinci-resolve-fairlight-essentials-audio-cleanup-levels-and-basic-mixing). opened: false
- Ducking: Boris FX "What is audio ducking" (https://borisfx.com/blog/what-is-audio-ducking-and-how-is-it-used/); Magnific "Auto ducking in Premiere Pro" (https://www.magnific.com/blog/how-to-use-auto-ducking-in-premiere-pro-for-clean-professional-audio/); Mubert auto-ducking docs (https://mubert.com/tools/cast/docs/auto-ducking). opened: false
- Short-form sound: fish.audio "Using sound effects for short-form content" (https://fish.audio/blog/using-sound-effects-for-short-form-content); FluxNote "Faceless shorts retention tips 2026" (https://fluxnote.io/guides/faceless-shorts-retention-tips-2026); recapio "3 essential sound effects" (https://recapio.com/digest/3-essential-sound-effects-sounddesign-by-gaku-lange). opened: false
- Walla and room tone: FilmSound.org "Walla" (https://filmsound.org/terminology/walla.htm); TravSonic "What is walla recording" (https://www.travsonic.com/walla-recording-for-film-and-how-to-master-this-essential-audio-technique/); ProVideo Coalition "The ABCs of sound, part II" (https://www.provideocoalition.com/the-abcs-of-sound-part-ii/); O'Reilly, *Sound Design for...*, ch. 6 "Walla/Group/Loop Group" (https://www.oreilly.com/library/view/sound-design-for/9781317557920/xhtml/Ch06.xhtml). opened: false
- Layers and silence: BINUS "Using sound to enhance animated stories" (https://binus.ac.id/bandung/dkv/2025/11/04/using-sound-to-enhance-animated-stories/); Sound On Sound "Sound design for visual media" (https://www.soundonsound.com/techniques/sound-design-visual-media-radio); MyAnimeList "Good Vibrations: the undervalued artistry of an anime's soundscape" (https://myanimelist.net/featured/2271/Good_Vibrations__The_Undervalued_Artistry_of_an_Anime%E2%80%99s_Soundscape). opened: false
- Procedural sound: Designing Sound, interview with Andy Farnell (https://designingsound.org/2012/01/18/procedural-audio-interview-with-andy-farnell/); QMUL "Procedural audio review" (https://www.eecs.qmul.ac.uk/~josh/documents/2023/Procedural%20audio%20review.pdf). opened: false
- Gongs and Mindanao instruments: Wikipedia "Agung" (https://en.wikipedia.org/wiki/Agung); Center for World Music "The Maguindanaoan kulintang" (https://centerforworldmusic.org/tag/kulintang); hellomusictheory "Filipino instruments" (https://hellomusictheory.com/learn/filipino-instruments/). opened: false
- Cordillera and flutes: NCCA article (https://ncca.gov.ph/?p=3478); National Library of the Philippines digital collection (https://nlpdl.nlp.gov.ph/CC01/NLP00VM052mcd/v5/v2.pdf). opened: false
- Rondalla, bandurria: Wikipedia "Bandurria" (https://en.wikipedia.org/wiki/Bandurria) and "Rondalla" (https://www.wikiwand.com/en/Rondalla); PBS SoCal Artbound on rondalla (https://pbssocal.org/shows/artbound/this-master-rondalla-musician-is-preserving-the-sounds-of-philippine-culture-in-l-a). opened: false
- Bands and kundiman of 1896: Philstar "Malabon bamboo band remembers Katipunan past" (https://philstar.com/nation/2018/08/28/1846382/malabon-bamboo-band-remembers-katipunan-past); Humanities Diliman, on Spanish regimental bands (https://journals.upd.edu.ph/index.php/humanitiesdiliman/article/download/4430/4019); Filipinas Heritage Library "Philippine band music" (https://www.filipinaslibrary.org.ph/?p=1676); Wikipedia "Kundiman" (https://en.wikipedia.org/wiki/Kundiman). opened: false
