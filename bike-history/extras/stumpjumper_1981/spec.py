"""Bonus episode (was episode 22: spec for lib/make_episode.sh, written by lib/specgen.py (facts in facts.md)."""
import shotkit
EP, MODEL, WB = 22, 'stumpjumper1981', 1.08
HOOK_BIG, HOOK_LINE = '1981', 'Off the road.'
TITLE, TITLE_SIZE = 'STUMPJUMPER', 100
CLOSE_ORDER = ['frame', 'drive', 'brakes', 'front_wheel']
CLOSE = {'frame': ('WELDED STEEL FRAME', 'frame', (280, 190)), 'drive': ('15 SPEEDS', 'drive', (470, 190)), 'brakes': ('CANTILEVER BRAKES', 'brakes', (280, 190)), 'front_wheel': ('26-INCH WHEELS', 'front_wheel', (270, 190))}
EXL = [('front_wheel', 'FRONT WHEEL'), ('handlebar', 'HANDLEBAR'), ('saddle', 'SADDLE'), ('frame', 'FRAME'), ('rear_wheel', 'REAR WHEEL'), ('drive', 'GEARS'), ('pedals', 'CRANKS'), ('fork', 'FORK')]
RIDE_TITLE = '1981'
NEXT_BIG, NEXT_SMALL = 'NEXT: THE FIRST NINJA', 'EP 23  ·  KAWASAKI GPZ900R, 1984'
ENGINE_RPM, ROAD_BAND = None, [100, 700]
LINES = [
    ('hook', 'Off the road.', 'Nineteen eighty-one. Off the road.'),
    ('turn', 'The Specialized Stumpjumper: the first mass-produced mountain bike.', 'The Specialized Stumpjumper. The first mass-produced mountain bike.'),
    ('frame', 'A welded steel frame. The first ones were made in Japan.', 'A welded steel frame. The first ones were made in Japan.'),
    ('drive', 'Fifteen speeds, from road-bike gears.', 'Fifteen speeds, from road bike gears.'),
    ('brakes', 'Mafac cantilever brakes.', 'Mah-fack cantilever brakes.'),
    ('front_wheel', 'Wide 26-inch wheels: the first mountain-bike standard.', 'Wide, twenty-six inch wheels. The first mountain bike standard.'),
    ('explode', 'Frame, wheels, gears, brakes, flat bars: just under 30 pounds.', 'Frame, wheels, gears, brakes, flat bars. Just under thirty pounds.'),
    ('ride', '$750, complete. Or $395 for the frame alone.', 'Seven hundred and fifty dollars, complete. Or three ninety-five for the frame.'),
    ('ride', 'No suspension at all.', 'And no suspension at all.'),
    ('outro', 'The first 125 sold out in six days.', 'The first batch sold out in six days.'),
    ('outro', None, 'Next: the first Ninja.'),
]
def shots(ease, out): return shotkit.standard(ease, out, CLOSE_ORDER, z=0.5, presets={'drive': (-20, 10, 2.4, (-0.4, 0, 0.38), {'spin_r': -240}), 'brakes': (-40, 18, 2.0, (0.42, 0, 0.62), {}), 'fork': (-40, 10, 2.3, (0.5, 0, 0.5), {}), 'frame': (-35, 12, 3.0, (0.05, 0, 0.6), {}), 'front_wheel': (-10, 4, 2.4, (0.55, 0, 0.36), {'spin_f': -120}), 'handlebar': (-35, 30, 2.0, (0.38, 0, 0.92), {})}, ride_z=0.85)
COVER_PROMPT = 'Wide photograph, photorealistic, eye level, 50mm lens. An empty dirt trail through a pine forest on a mountain slope, soft morning light from the left, light haze. The road fills the lower third of the picture.'
THUMB_PROMPT = 'Tall vertical photograph, photorealistic, eye level, 35mm lens. An empty dirt trail through a pine forest on a mountain slope, soft morning light, bright sky at the top. The road fills the lower half of the picture.'
THUMB_BIG, THUMB_NAME = '1981', 'STUMPJUMPER'
