"""Episode 23: spec for lib/make_episode.sh, written by lib/specgen.py (facts in facts.md)."""
EP, MODEL, WB = 23, 'gsxr750_1985', 1.41
HOOK_BIG, HOOK_LINE = '1985', 'A race bike\nwith lights.'
TITLE, TITLE_SIZE = 'SUZUKI GSX-R750', 84
CLOSE_ORDER = ['frame', 'engine', 'brakes', 'front_wheel']
CLOSE = {'frame': ('ALUMINIUM FRAME', 'frame', (260, 190)), 'engine': ('AIR + OIL COOLED', 'engine', (270, 190)), 'brakes': ('4-PISTON CALIPERS', 'brakes', (270, 190)), 'front_wheel': ('18-INCH WHEELS', 'front_wheel', (270, 190))}
EXL = [('front_wheel', 'FRONT WHEEL'), ('handlebar', 'HANDLEBAR'), ('tank', 'TANK'), ('engine', 'ENGINE'), ('frame', 'FRAME'), ('rear_wheel', 'REAR WHEEL'), ('saddle', 'SEAT'), ('fairing', 'FAIRING')]
RIDE_TITLE = 'COLOGNE, 1984'
NEXT_BIG, NEXT_SMALL = 'NEXT: A SUPERBIKE ICON', 'EP 24  ·  DUCATI 916, 1994'
ENGINE_RPM, ROAD_BAND = 9000, [150, 900]
LINES = [
    ('hook', 'A race bike with lights.', 'Nineteen eighty-five. A race bike with lights.'),
    ('turn', 'The Suzuki GSX-R750, designed by Hiroshi Fujiwara.', 'The Suzuki G S X R seven-fifty, designed by Hiroshi Fujiwara.'),
    ('frame', 'A light aluminium alloy frame.', 'A light, aluminium alloy frame.'),
    ('engine', 'Air-and-oil cooled to save weight: about 750 cc, four cylinders.', 'Air and oil cooled, to save weight. Four cylinders, about seven-fifty cc.'),
    ('brakes', 'Twin front discs, four-piston calipers.', 'Twin front discs, with four-piston calipers.'),
    ('front_wheel', '18-inch wheels, front and rear.', 'Eighteen-inch wheels, front and rear.'),
    ('explode', 'Frame, engine, fairing, wheels.', 'Take it apart. Frame, engine, fairing, wheels.'),
    ('ride', '“The lightest of the superbikes, by a good margin.”', 'The lightest of the superbikes, by a good margin.'),
    ('ride', 'Six speeds, a chain, and flat-slide racing carburettors.', 'Six speeds, a chain, and flat-slide racing carburettors.'),
    ('outro', 'A racer you could ride to work.', 'A racer you could ride to work.'),
    ('outro', None, 'Next: a superbike icon.'),
]
def shots(ease, out):
    import shotkit                      # imported here so the spec can be read without lib/ on the path
    return shotkit.standard(ease, out, CLOSE_ORDER, z=0.55, presets={}, ride_z=0.85)
COVER_PROMPT = 'Wide photograph, photorealistic, eye level, 50mm lens. An empty modern race circuit straight with painted kerbs, soft morning light from the left, light haze. The road fills the lower third of the picture.'
THUMB_PROMPT = 'Tall vertical photograph, photorealistic, eye level, 35mm lens. An empty modern race circuit straight with painted kerbs, soft morning light, bright sky at the top. The road fills the lower half of the picture.'
THUMB_BIG, THUMB_NAME = '1985', 'GSX-R750'
