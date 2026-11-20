"""Episode 26: spec for lib/make_episode.sh, written by lib/specgen.py (facts in facts.md)."""
EP, MODEL, WB = 26, 'hayabusa1999', 1.485
HOOK_BIG, HOOK_LINE = '1999', 'The falcon.'
TITLE, TITLE_SIZE = 'SUZUKI HAYABUSA', 88
CLOSE_ORDER = ['engine', 'frame', 'brakes', 'fork']
CLOSE = {'engine': ('1,299 CC FOUR', 'engine', (270, 190)), 'frame': ('TWIN-BEAM FRAME', 'frame', (260, 190)), 'brakes': ('6-PISTON CALIPERS', 'brakes', (270, 190)), 'fork': ('INVERTED FORK', 'fork', (470, 190))}
EXL = [('front_wheel', 'FRONT WHEEL'), ('handlebar', 'HANDLEBAR'), ('tank', 'TANK'), ('engine', 'ENGINE'), ('frame', 'FRAME'), ('rear_wheel', 'REAR WHEEL'), ('saddle', 'SEAT'), ('fairing', 'FAIRING')]
RIDE_TITLE = '312 KM/H'
NEXT_BIG, NEXT_SMALL = 'NEXT: FIVE CYLINDERS', 'EP 27  ·  HONDA RC211V, 2002'
ENGINE_RPM, ROAD_BAND = 9500, [150, 900]
LINES = [
    ('hook', 'The falcon.', 'Nineteen ninety-nine. The falcon.'),
    ('turn', 'The Suzuki Hayabusa: Japanese for peregrine falcon, a hunter of blackbirds.', 'The Suzuki Hayabusa. Japanese for peregrine falcon, a hunter of blackbirds.'),
    ('engine', 'A 1,299 cc inline four: 173 hp claimed.', 'A thirteen hundred cc inline four. A hundred and seventy-three horsepower, claimed.'),
    ('frame', 'A twin-beam frame.', 'A twin-beam frame.'),
    ('brakes', 'Six-piston calipers on 320 mm discs.', 'Six-piston calipers, on three hundred and twenty millimetre discs.'),
    ('fork', 'An inverted, fully adjustable fork.', 'An inverted, fully adjustable fork.'),
    ('explode', 'Engine, frame, fairing, wheels.', 'Take it apart. Engine, frame, fairing, wheels.'),
    ('ride', 'Top speed: about 312 km/h, claimed. Sources vary.', 'Top speed, about three hundred and twelve kilometres an hour, claimed.'),
    ('ride', 'From late 2000, makers agreed to limit top speeds to about 300.', 'From late two thousand, makers agreed to limit top speeds to about three hundred.'),
    ('outro', 'Built in Toyokawa, Japan.', 'Built in Toyokawa, Japan.'),
    ('outro', None, 'Next: five cylinders.'),
]
def shots(ease, out):
    import shotkit                      # imported here so the spec can be read without lib/ on the path
    return shotkit.standard(ease, out, CLOSE_ORDER, z=0.55, presets={}, ride_z=0.85)
COVER_PROMPT = 'Wide photograph, photorealistic, eye level, 50mm lens. An empty long straight highway across flat farmland to the horizon, soft morning light from the left, light haze. The road fills the lower third of the picture.'
THUMB_PROMPT = 'Tall vertical photograph, photorealistic, eye level, 35mm lens. An empty long straight highway across flat farmland to the horizon, soft morning light, bright sky at the top. The road fills the lower half of the picture.'
THUMB_BIG, THUMB_NAME = '1999', 'HAYABUSA'
