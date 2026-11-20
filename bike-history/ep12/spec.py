"""Episode 12: generated spec for lib/make_episode.sh (facts in facts.md)."""
import math, shotkit
EP, MODEL, WB = 12, 'knuckle1936', 1.5
HOOK_BIG, HOOK_LINE = '1936', 'Overhead\nvalves.'
TITLE, TITLE_SIZE = 'THE KNUCKLEHEAD', 92
CLOSE_ORDER = ['engine', 'rockers', 'saddle', 'frame']
CLOSE = {'engine': ('OHV V-TWIN · 61 CI', 'engine', (270, 190)), 'rockers': ('ROCKER BOXES', 'engine', (470, 190)), 'saddle': ('OIL TANK UNDER SEAT', 'saddle', (300, 190)), 'frame': ('NEW FRAME', 'frame', (250, 190))}
EXL = [('front_wheel', 'FRONT WHEEL'), ('handlebar', 'HANDLEBAR'), ('tank', 'TANK'), ('engine', 'ENGINE'), ('frame', 'FRAME'), ('rear_wheel', 'REAR WHEEL'), ('saddle', 'SEAT'), ('exhaust', 'EXHAUST')]
RIDE_TITLE = 'DAYTONA, 1937'
NEXT_BIG, NEXT_SMALL = 'NEXT: TWO SIDE BY SIDE', 'EP 13  ·  TRIUMPH SPEED TWIN, 1937'
ENGINE_RPM, ROAD_BAND = 1600, [150, 900]
LINES = [
    ('hook', 'Overhead valves.', 'Nineteen thirty-six. Overhead valves.'),
    ('turn', 'Harley-Davidson’s Model E: later nicknamed the Knucklehead.', "This is Harley-Davidson's Model E, later nicknamed the Knucklehead."),
    ('engine', 'A 45-degree V-twin, 61 cubic inches: about 1,000 cc.', 'A forty-five degree V twin. Sixty-one cubic inches, about a thousand cc.'),
    ('rockers', 'The nickname came decades later, from the shape of the rocker boxes.', 'The nickname came decades later, from the shape of the rocker boxes.'),
    ('saddle', 'Dry-sump oiling: a horseshoe oil tank sits under the seat.', 'Dry-sump oiling. A horseshoe oil tank sits under the seat.'),
    ('frame', 'The taller engine needed a new frame.', 'The taller engine needed a new frame.'),
    ('explode', 'Engine, oil tank, frame, fork, wheels.', 'Take it apart. Engine, oil tank, frame, fork, wheels.'),
    ('ride', '1937: Joe Petrali sets a record on a streamlined Model E.', 'In nineteen thirty-seven, Joe Petrali set a record on a streamlined Model E.'),
    ('ride', '136 mph, at Daytona Beach.', 'One hundred and thirty-six miles an hour, at Daytona Beach.'),
    ('outro', 'Its valves were redesigned in year one.', 'Its valves were redesigned in year one.'),
    ('outro', None, 'Next: two cylinders, side by side.'),
]
def shots(ease, out): return shotkit.standard(ease, out, CLOSE_ORDER, z=0.55, presets={'rockers': (-15, 18, 1.9, (0.05, 0, 0.72), {})}, ride_z=0.88)
COVER_PROMPT = 'Wide photograph, photorealistic, eye level, 50mm lens. An empty two-lane American desert highway with a few telegraph poles, soft morning light from the left, light haze. The road fills the lower third of the picture.'
THUMB_PROMPT = 'Tall vertical photograph, photorealistic, eye level, 35mm lens. An empty two-lane American desert highway with a few telegraph poles, soft morning light, bright sky at the top. The road fills the lower half of the picture.'
THUMB_BIG, THUMB_NAME = '1936', 'THE KNUCKLEHEAD'
