"""Episode 18: spec for lib/make_episode.sh, written by lib/specgen.py (facts in facts.md)."""
import shotkit
EP, MODEL, WB = 18, 'cb750_1969', 1.46
HOOK_BIG, HOOK_LINE = '1969', 'The first\nsuperbike.'
TITLE, TITLE_SIZE = 'HONDA CB750', 100
CLOSE_ORDER = ['engine', 'brakes', 'frame', 'exhaust']
CLOSE = {'engine': ('INLINE FOUR · 736 CC', 'engine', (270, 190)), 'brakes': ('FRONT DISC BRAKE', 'brakes', (270, 190)), 'frame': ('DOUBLE CRADLE', 'frame', (260, 190)), 'exhaust': ('FOUR PIPES', 'exhaust', (470, 190))}
EXL = [('front_wheel', 'FRONT WHEEL'), ('handlebar', 'HANDLEBAR'), ('tank', 'TANK'), ('engine', 'ENGINE'), ('frame', 'FRAME'), ('rear_wheel', 'REAR WHEEL'), ('saddle', 'SEAT'), ('exhaust', 'EXHAUST')]
RIDE_TITLE = 'DAYTONA, 1970'
NEXT_BIG, NEXT_SMALL = 'NEXT: THE NEW YORK STEAK', 'EP 19  ·  KAWASAKI Z1, 1972'
ENGINE_RPM, ROAD_BAND = 6000, [150, 900]
LINES = [
    ('hook', 'The first superbike.', 'Nineteen sixty-nine. The first superbike.'),
    ('turn', 'The Honda CB750: the first motorcycle to be called a “superbike”.', 'The Honda C B seven-fifty. The first motorcycle to be called a superbike.'),
    ('engine', 'A transverse inline four, single overhead cam, 736 cc.', 'A transverse inline four, single overhead cam. Seven hundred and thirty-six cc.'),
    ('brakes', 'A front disc brake, on a bike people could afford.', 'A front disc brake, on a bike people could afford.'),
    ('frame', 'Honda’s first double cradle frame.', "Honda's first double cradle frame."),
    ('exhaust', 'Four cylinders, four pipes. An electric starter, too.', 'Four cylinders, four pipes. And an electric starter.'),
    ('explode', 'Engine, frame, fork, wheels: 218 kg dry. Price: $1,495.', 'Engine, frame, fork, wheels. Fourteen ninety-five dollars.'),
    ('ride', 'March 1970: Dick Mann wins the Daytona 200 on the racing CR750.', 'March nineteen seventy. Dick Mann wins the Daytona two hundred, on the racing C R seven-fifty.'),
    ('ride', 'By a few seconds, on a failing engine.', 'By a few seconds, on a failing engine.'),
    ('outro', 'Top speed: 125 mph.', 'Top speed, a hundred and twenty-five.'),
    ('outro', None, 'Next: the New York Steak.'),
]
def shots(ease, out): return shotkit.standard(ease, out, CLOSE_ORDER, z=0.55, presets={}, ride_z=0.88)
COVER_PROMPT = 'Wide photograph, photorealistic, eye level, 50mm lens. An empty wide American coastal highway with palm trees, soft morning light from the left, light haze. The road fills the lower third of the picture.'
THUMB_PROMPT = 'Tall vertical photograph, photorealistic, eye level, 35mm lens. An empty wide American coastal highway with palm trees, soft morning light, bright sky at the top. The road fills the lower half of the picture.'
THUMB_BIG, THUMB_NAME = '1969', 'HONDA CB750'
