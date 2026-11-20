"""Episode 21: spec for lib/make_episode.sh, written by lib/specgen.py (facts in facts.md)."""
import shotkit
EP, MODEL, WB = 21, 'r80gs_1980', 1.465
HOOK_BIG, HOOK_LINE = '1980', 'The first big\nadventure bike.'
TITLE, TITLE_SIZE = 'BMW R 80 G/S', 92
CLOSE_ORDER = ['engine', 'rear_suspension', 'shaft', 'front_wheel']
CLOSE = {'engine': ('BOXER · 797.5 CC', 'engine', (270, 190)), 'rear_suspension': ('MONOLEVER', 'rear_suspension', (470, 190)), 'shaft': ('SHAFT DRIVE', 'drive', (470, 190)), 'front_wheel': ('21-INCH FRONT', 'front_wheel', (270, 190))}
EXL = [('front_wheel', 'FRONT WHEEL'), ('handlebar', 'HANDLEBAR'), ('tank', 'TANK'), ('engine', 'ENGINE'), ('frame', 'FRAME'), ('rear_wheel', 'REAR WHEEL'), ('saddle', 'SEAT'), ('drive', 'SHAFT')]
RIDE_TITLE = 'PARIS–DAKAR, 1981'
NEXT_BIG, NEXT_SMALL = 'NEXT: INTO THE MOUNTAINS', 'EP 22  ·  SPECIALIZED STUMPJUMPER, 1981'
ENGINE_RPM, ROAD_BAND = 3200, [150, 1000]
LINES = [
    ('hook', 'The first big adventure bike.', 'Nineteen eighty. The first big adventure bike.'),
    ('turn', 'The BMW R 80 G/S, built in Berlin: the first large multisport bike on the market.', 'The B M W R eighty G S, built in Berlin. The first large multisport bike on the market.'),
    ('engine', 'A 797.5 cc flat twin: 50 hp.', 'An eight hundred cc flat twin. Fifty horsepower.'),
    ('rear_suspension', 'The Monolever: a single-sided swingarm and one shock.', 'The Monolever. A single-sided swingarm, and one shock.'),
    ('shaft', 'Five speeds and shaft drive, even in the dirt.', 'Five speeds, and shaft drive. Even in the dirt.'),
    ('front_wheel', 'A big 21-inch front wheel for rough ground.', 'A big, twenty-one inch front wheel.'),
    ('explode', 'Engine, shaft, frame, fork, wheels: 186 kg wet.', 'Engine, shaft, frame, fork, wheels. One hundred and eighty-six kilos.'),
    ('ride', 'January 1981: Hubert Auriol wins the Paris–Dakar motorcycle class.', 'January nineteen eighty-one. Hubert Oriol wins the Paris Dakar.'),
    ('ride', 'Across the Sahara, on a prepared R 80 G/S.', 'Across the Sahara, on a prepared R eighty G S.'),
    ('outro', '21,864 were built, until 1987.', 'Twenty-one thousand were built, until eighty-seven.'),
    ('outro', None, 'Next: into the mountains.'),
]
def shots(ease, out): return shotkit.standard(ease, out, CLOSE_ORDER, z=0.55, presets={'front_wheel': (-10, 4, 2.6, (0.6, 0, 0.38), {'spin_f': -120})}, ride_z=0.95)
COVER_PROMPT = 'Wide photograph, photorealistic, eye level, 50mm lens. An empty sandy desert track between low dunes under a pale sky, soft morning light from the left, light haze. The road fills the lower third of the picture.'
THUMB_PROMPT = 'Tall vertical photograph, photorealistic, eye level, 35mm lens. An empty sandy desert track between low dunes under a pale sky, soft morning light, bright sky at the top. The road fills the lower half of the picture.'
THUMB_BIG, THUMB_NAME = '1980', 'BMW R 80 G/S'
