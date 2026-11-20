"""Episode 16: spec for lib/make_episode.sh, written by lib/specgen.py (facts in facts.md)."""
import shotkit
EP, MODEL, WB = 16, 'manx1950', 1.4
HOOK_BIG, HOOK_LINE = '1950', 'Riding on\na featherbed.'
TITLE, TITLE_SIZE = 'NORTON MANX', 100
CLOSE_ORDER = ['engine', 'frame', 'fork', 'rear_suspension']
CLOSE = {'engine': ('DOHC SINGLE · 499 CC', 'engine', (270, 190)), 'frame': ('FEATHERBED FRAME', 'frame', (280, 190)), 'fork': ('TELESCOPIC FORK', 'fork', (470, 190)), 'rear_suspension': ('SWINGARM', 'rear_suspension', (470, 190))}
EXL = [('front_wheel', 'FRONT WHEEL'), ('handlebar', 'HANDLEBAR'), ('tank', 'TANK'), ('engine', 'ENGINE'), ('frame', 'FRAME'), ('rear_wheel', 'REAR WHEEL'), ('saddle', 'SEAT'), ('exhaust', 'EXHAUST')]
RIDE_TITLE = 'ISLE OF MAN, 1950'
NEXT_BIG, NEXT_SMALL = 'NEXT: 100 MILLION', 'EP 17  ·  HONDA SUPER CUB, 1958'
ENGINE_RPM, ROAD_BAND = 2600, [150, 900]
LINES = [
    ('hook', 'Riding on a featherbed.', 'Nineteen fifty. Riding on a featherbed.'),
    ('turn', 'The Norton Manx, built to win the Isle of Man TT.', 'The Norton Manx, built to win the Isle of Man T T.'),
    ('engine', 'A 499 cc single with double overhead cams.', 'A four hundred and ninety-nine cc single, with double overhead cams.'),
    ('frame', 'The Featherbed frame, by Rex McCandless of Belfast: over forty feet of tubing.', 'The Featherbed frame, by Rex McCandless of Belfast. Over forty feet of tubing.'),
    ('fork', 'A telescopic fork in front, a swingarm behind.', 'A telescopic fork in front. A swingarm behind.'),
    ('rear_suspension', 'A tester said: like riding on a featherbed. The old frame: a garden gate.', 'A tester said it was like riding on a featherbed. The old frame, a garden gate.'),
    ('explode', 'Engine, frame, fork, wheels: 140 kg dry.', 'Engine, frame, fork, wheels. One hundred and forty kilos.'),
    ('ride', '1950 Senior TT: Geoff Duke wins on the new frame.', 'The nineteen fifty Senior T T. Geoff Duke wins on the new frame.'),
    ('ride', 'Lap record 93.33 mph. Nortons take the top three places.', 'Lap record, ninety-three point three. Nortons take the top three places.'),
    ('outro', 'Duke won three world titles for Norton.', 'Duke won three world titles for Norton.'),
    ('outro', None, 'Next: the most produced vehicle ever.'),
]
def shots(ease, out): return shotkit.standard(ease, out, CLOSE_ORDER, z=0.55, presets={}, ride_z=0.88)
COVER_PROMPT = 'Wide photograph, photorealistic, eye level, 50mm lens. An empty winding island road between stone walls and green fields, sea in the distance, soft morning light from the left, light haze. The road fills the lower third of the picture.'
THUMB_PROMPT = 'Tall vertical photograph, photorealistic, eye level, 35mm lens. An empty winding island road between stone walls and green fields, sea in the distance, soft morning light, bright sky at the top. The road fills the lower half of the picture.'
THUMB_BIG, THUMB_NAME = '1950', 'NORTON MANX'
