"""Episode 27: spec for lib/make_episode.sh, written by lib/specgen.py (facts in facts.md)."""
import shotkit
EP, MODEL, WB = 27, 'rc211v_2002', 1.44
HOOK_BIG, HOOK_LINE = '2002', 'Five\ncylinders.'
TITLE, TITLE_SIZE = 'HONDA RC211V', 100
CLOSE_ORDER = ['engine', 'frame', 'rear_suspension', 'front_wheel']
CLOSE = {'engine': ('V5 · 990 CC', 'engine', (260, 190)), 'frame': ('TWIN-SPAR FRAME', 'frame', (260, 190)), 'rear_suspension': ('PRO-LINK REAR', 'rear_suspension', (470, 190)), 'front_wheel': ('17-INCH FRONT', 'front_wheel', (270, 190))}
EXL = [('front_wheel', 'FRONT WHEEL'), ('handlebar', 'HANDLEBAR'), ('tank', 'TANK'), ('engine', 'ENGINE'), ('frame', 'FRAME'), ('rear_wheel', 'REAR WHEEL'), ('saddle', 'SEAT'), ('fairing', 'FAIRING')]
RIDE_TITLE = 'SUZUKA, 2002'
NEXT_BIG, NEXT_SMALL = 'NEXT: BMW’S SUPERBIKE', 'EP 28  ·  BMW S 1000 RR, 2009'
ENGINE_RPM, ROAD_BAND = 12000, [150, 900]
LINES = [
    ('hook', 'Five cylinders.', 'Two thousand two. Five cylinders.'),
    ('turn', 'The Honda RC211V, built to replace the two-stroke NSR500.', 'The Honda R C two-eleven V. Built to replace the two-stroke N S R five hundred.'),
    ('engine', 'A V5: five cylinders, 990 cc.', 'A V five. Five cylinders, nine ninety cc.'),
    ('frame', 'A twin-spar frame.', 'A twin-spar frame.'),
    ('rear_suspension', 'Pro-Link rear suspension.', 'Pro-Link rear suspension.'),
    ('front_wheel', 'A 17-inch front wheel, 16.5 at the back.', 'A seventeen-inch front wheel. Sixteen and a half at the back.'),
    ('explode', 'Engine, frame, fairing, wheels: about 148 kg dry.', 'Engine, frame, fairing, wheels. About a hundred and forty-eight kilos.'),
    ('ride', 'Suzuka, 7 April 2002: Valentino Rossi wins the opener, in the wet.', 'Suzuka, April two thousand two. Valentino Rossi wins the first race, in the wet.'),
    ('ride', 'He clinches the title in Rio with four races left.', 'He clinches the title in Rio, with four races left.'),
    ('outro', '11 wins that year.', 'Eleven wins that year.'),
    ('outro', None, 'Next: B M W\'s superbike.'),
]
def shots(ease, out): return shotkit.standard(ease, out, CLOSE_ORDER, z=0.55, presets={}, ride_z=0.85)
COVER_PROMPT = 'Wide photograph, photorealistic, eye level, 50mm lens. An empty modern race circuit straight at dusk with grandstands far away, soft morning light from the left, light haze. The road fills the lower third of the picture.'
THUMB_PROMPT = 'Tall vertical photograph, photorealistic, eye level, 35mm lens. An empty modern race circuit straight at dusk with grandstands far away, soft morning light, bright sky at the top. The road fills the lower half of the picture.'
THUMB_BIG, THUMB_NAME = '2002', 'RC211V'
