"""Episode 13: generated spec for lib/make_episode.sh (facts in facts.md)."""
import math, shotkit
EP, MODEL, WB = 13, 'speedtwin1937', 1.4
HOOK_BIG, HOOK_LINE = '1937', 'Two cylinders,\nside by side.'
TITLE, TITLE_SIZE = 'TRIUMPH SPEED TWIN', 72
CLOSE_ORDER = ['engine', 'fork', 'saddle', 'drive']
CLOSE = {'engine': ('PARALLEL TWIN · 498 CC', 'engine', (290, 190)), 'fork': ('GIRDER FORK', 'fork', (470, 190)), 'saddle': ('SPRUNG SADDLE', 'saddle', (280, 190)), 'drive': ('4 SPEEDS · CHAIN', 'drive', (470, 190))}
EXL = [('front_wheel', 'FRONT WHEEL'), ('handlebar', 'HANDLEBAR'), ('tank', 'TANK'), ('engine', 'ENGINE'), ('frame', 'FRAME'), ('rear_wheel', 'REAR WHEEL'), ('saddle', 'SEAT'), ('exhaust', 'EXHAUST')]
RIDE_TITLE = 'LONDON, 1952'
NEXT_BIG, NEXT_SMALL = 'NEXT: A WASP FROM ITALY', 'EP 14  ·  VESPA, 1946'
ENGINE_RPM, ROAD_BAND = 2400, [150, 900]
LINES = [
    ('hook', 'Two cylinders, side by side.', 'Nineteen thirty-seven. Two cylinders, side by side.'),
    ('turn', 'The Triumph Speed Twin, by Edward Turner. It sold for £75.', 'The Triumph Speed Twin, by Edward Turner. It sold for seventy-five pounds.'),
    ('engine', 'A parallel twin: 498 cc, 27 bhp.', 'A parallel twin. Four hundred and ninety-eight cc, twenty-seven horsepower.'),
    ('fork', 'A girder fork at the front.', 'A girder fork at the front.'),
    ('saddle', 'No rear springs: the sprung saddle was the only rear suspension.', 'No rear springs. The sprung saddle was the only rear suspension.'),
    ('drive', 'Four speeds, and a chain to the rear wheel.', 'Four speeds, and a chain to the rear wheel.'),
    ('explode', 'Engine, gearbox, frame, fork, wheels: 166 kg dry.', 'Engine, gearbox, frame, fork, wheels. One hundred and sixty-six kilos.'),
    ('ride', 'It became the standard other twins were judged by.', 'It became the standard other twins were judged by.'),
    ('ride', 'From 1952, London police escort riders used Speed Twins.', 'From nineteen fifty-two, London police escort riders used Speed Twins.'),
    ('outro', 'In 1940, the factory was bombed.', 'In nineteen forty, the factory was bombed.'),
    ('outro', None, 'Next: a wasp from Italy.'),
]
def shots(ease, out): return shotkit.standard(ease, out, CLOSE_ORDER, z=0.55, presets={}, ride_z=0.88)
COVER_PROMPT = 'Wide photograph, photorealistic, eye level, 50mm lens. An empty English country lane between green hedgerows, soft morning light from the left, light haze. The road fills the lower third of the picture.'
THUMB_PROMPT = 'Tall vertical photograph, photorealistic, eye level, 35mm lens. An empty English country lane between green hedgerows, soft morning light, bright sky at the top. The road fills the lower half of the picture.'
THUMB_BIG, THUMB_NAME = '1937', 'THE SPEED TWIN'
