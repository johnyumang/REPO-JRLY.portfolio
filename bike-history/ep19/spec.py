"""Episode 19: spec for lib/make_episode.sh, written by lib/specgen.py (facts in facts.md)."""
import shotkit
EP, MODEL, WB = 19, 'z1_1972', 1.49
HOOK_BIG, HOOK_LINE = '1972', 'Twin cams,\nfour cylinders.'
TITLE, TITLE_SIZE = 'KAWASAKI Z1', 100
CLOSE_ORDER = ['engine', 'frame', 'brakes', 'rear_suspension']
CLOSE = {'engine': ('DOHC FOUR · 903 CC', 'engine', (270, 190)), 'frame': ('DUPLEX CRADLE', 'frame', (260, 190)), 'brakes': ('290 MM DISC', 'brakes', (270, 190)), 'rear_suspension': ('SWINGARM', 'rear_suspension', (470, 190))}
EXL = [('front_wheel', 'FRONT WHEEL'), ('handlebar', 'HANDLEBAR'), ('tank', 'TANK'), ('engine', 'ENGINE'), ('frame', 'FRAME'), ('rear_wheel', 'REAR WHEEL'), ('saddle', 'SEAT'), ('exhaust', 'EXHAUST')]
RIDE_TITLE = 'DAYTONA, 1972'
NEXT_BIG, NEXT_SMALL = 'NEXT: TWO-STROKE CHAMPION', 'EP 20  ·  YAMAHA YZR500, 1975'
ENGINE_RPM, ROAD_BAND = 6500, [150, 900]
LINES = [
    ('hook', 'Twin cams, four cylinders.', 'Nineteen seventy-two. Twin cams, four cylinders.'),
    ('turn', 'The Kawasaki Z1. Its project name: “New York Steak”.', 'The Kawasaki Z one. Its project name: New York Steak.'),
    ('engine', 'A 903 cc air-cooled inline four with double overhead cams: 82 PS.', 'Nine hundred and three cc. An air-cooled inline four, with double overhead cams.'),
    ('frame', 'A full duplex cradle frame.', 'A full duplex cradle frame.'),
    ('brakes', 'An 11.5-inch front disc; a second one was optional.', 'An eleven and a half inch front disc. A second one was optional.'),
    ('rear_suspension', 'Telescopic fork in front, swingarm behind. Five speeds, chain drive.', 'Telescopic fork in front, swingarm behind. Five speeds, and a chain.'),
    ('explode', 'Engine, frame, fork, wheels: 230 kg dry.', 'Engine, frame, fork, wheels. Two hundred and thirty kilos.'),
    ('ride', '1972, Daytona: a 24-hour record, 2,631 miles at 109.64 mph.', 'Daytona, nineteen seventy-two. A twenty-four hour record. Twenty-six hundred miles, at a hundred and nine an hour.'),
    ('ride', 'Top speed: about 130 mph.', 'Top speed, about a hundred and thirty.'),
    ('outro', 'About 85,000 were built.', 'About eighty-five thousand were built.'),
    ('outro', None, 'Next: a two-stroke champion.'),
]
def shots(ease, out): return shotkit.standard(ease, out, CLOSE_ORDER, z=0.55, presets={}, ride_z=0.88)
COVER_PROMPT = 'Wide photograph, photorealistic, eye level, 50mm lens. An empty banked race track straight beside the sea under a clear sky, soft morning light from the left, light haze. The road fills the lower third of the picture.'
THUMB_PROMPT = 'Tall vertical photograph, photorealistic, eye level, 35mm lens. An empty banked race track straight beside the sea under a clear sky, soft morning light, bright sky at the top. The road fills the lower half of the picture.'
THUMB_BIG, THUMB_NAME = '1972', 'KAWASAKI Z1'
