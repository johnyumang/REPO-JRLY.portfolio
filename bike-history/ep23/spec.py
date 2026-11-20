"""Episode 23: spec for lib/make_episode.sh, written by lib/specgen.py (facts in facts.md)."""
import shotkit
EP, MODEL, WB = 23, 'gpz900r_1984', 1.495
HOOK_BIG, HOOK_LINE = '1984', 'The first\nNinja.'
TITLE, TITLE_SIZE = 'KAWASAKI GPZ900R', 80
CLOSE_ORDER = ['engine', 'frame', 'fairing', 'rear_suspension']
CLOSE = {'engine': ('16 VALVES · 908 CC', 'engine', (270, 190)), 'frame': ('NO DOWN TUBES', 'frame', (260, 190)), 'fairing': ('FULL FAIRING', 'fairing', (270, 190)), 'rear_suspension': ('UNI-TRAK REAR', 'rear_suspension', (470, 190))}
EXL = [('front_wheel', 'FRONT WHEEL'), ('handlebar', 'HANDLEBAR'), ('tank', 'TANK'), ('engine', 'ENGINE'), ('frame', 'FRAME'), ('rear_wheel', 'REAR WHEEL'), ('saddle', 'SEAT'), ('fairing', 'FAIRING')]
RIDE_TITLE = '1984 – 2003'
NEXT_BIG, NEXT_SMALL = 'NEXT: A RACER WITH LIGHTS', 'EP 24  ·  SUZUKI GSX-R750, 1985'
ENGINE_RPM, ROAD_BAND = 8000, [150, 900]
LINES = [
    ('hook', 'The first Ninja.', 'Nineteen eighty-four. The first Ninja.'),
    ('turn', 'The Kawasaki GPZ900R, developed in secret over six years.', 'The Kawasaki G P Z nine hundred R. Developed in secret, over six years.'),
    ('engine', 'The first 16-valve liquid-cooled inline four on a motorcycle: 908 cc, 115 bhp.', 'The first sixteen-valve, liquid-cooled inline four on a motorcycle.'),
    ('frame', 'Tests showed the down tubes carried almost no weight, so they went.', 'Tests showed the down tubes carried almost no weight. So they went.'),
    ('fairing', 'A full fairing, and a 16-inch front wheel.', 'A full fairing, and a sixteen-inch front wheel.'),
    ('rear_suspension', 'Uni-Trak rear suspension, with an air shock.', 'Uni-Trak rear suspension, with an air shock.'),
    ('explode', 'Engine, frame, fairing, wheels: 228 kg.', 'Engine, frame, fairing, wheels. Two hundred and twenty-eight kilos.'),
    ('ride', 'It starred in the film Top Gun.', 'It starred in the film Top Gun.'),
    ('ride', 'Built from 1984 to 2003.', 'And it was built from nineteen eighty-four to two thousand three.'),
    ('outro', 'Nineteen years in production.', 'Nineteen years in production.'),
    ('outro', None, 'Next: a race bike with lights.'),
]
def shots(ease, out): return shotkit.standard(ease, out, CLOSE_ORDER, z=0.55, presets={}, ride_z=0.85)
COVER_PROMPT = 'Wide photograph, photorealistic, eye level, 50mm lens. An empty runway beside a desert airfield at sunrise, soft morning light from the left, light haze. The road fills the lower third of the picture.'
THUMB_PROMPT = 'Tall vertical photograph, photorealistic, eye level, 35mm lens. An empty runway beside a desert airfield at sunrise, soft morning light, bright sky at the top. The road fills the lower half of the picture.'
THUMB_BIG, THUMB_NAME = '1984', 'THE FIRST NINJA'
