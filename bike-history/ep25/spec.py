"""Episode 25: spec for lib/make_episode.sh, written by lib/specgen.py (facts in facts.md)."""
EP, MODEL, WB = 25, 'r1_1998', 1.4
HOOK_BIG, HOOK_LINE = '1998', 'One litre,\nless weight.'
TITLE, TITLE_SIZE = 'YAMAHA YZF-R1', 92
CLOSE_ORDER = ['engine', 'gearbox', 'carbs', 'fork']
CLOSE = {'engine': ('20 VALVES · 998 CC', 'engine', (270, 190)), 'gearbox': ('STACKED GEARBOX', 'engine', (280, 190)), 'carbs': ('4 CARBURETTORS', 'engine', (270, 190)), 'fork': ('UPSIDE-DOWN FORK', 'fork', (470, 190))}
EXL = [('front_wheel', 'FRONT WHEEL'), ('handlebar', 'HANDLEBAR'), ('tank', 'TANK'), ('engine', 'ENGINE'), ('frame', 'FRAME'), ('rear_wheel', 'REAR WHEEL'), ('saddle', 'SEAT'), ('fairing', 'FAIRING')]
RIDE_TITLE = 'MACAU'
NEXT_BIG, NEXT_SMALL = 'NEXT: THE FALCON', 'EP 26  ·  SUZUKI HAYABUSA, 1999'
ENGINE_RPM, ROAD_BAND = 9500, [150, 900]
LINES = [
    ('hook', 'One litre, less weight.', 'Nineteen ninety-eight. One litre, less weight.'),
    ('turn', 'The Yamaha YZF-R1.', 'The Yamaha Y Z F R one.'),
    ('engine', '998 cc, 20 valves, double overhead cams: about 150 hp.', 'Nine hundred and ninety-eight cc. Twenty valves. About a hundred and fifty horsepower.'),
    ('gearbox', 'A stacked gearbox: the shafts sit one above the other, so the engine is short.', 'A stacked gearbox. The shafts sit one above the other, so the engine is short.'),
    ('carbs', 'Four 40 mm carburettors.', 'Four, forty millimetre carburettors.'),
    ('fork', 'A 41 mm upside-down fork.', 'A forty-one millimetre, upside down fork.'),
    ('explode', 'Engine, frame, fairing, wheels: 190 kg dry.', 'Engine, frame, fairing, wheels. One hundred and ninety kilos.'),
    ('ride', 'Top speed: about 270 km/h.', 'Top speed, about two hundred and seventy kilometres an hour.'),
    ('ride', 'R1s won five Macau Grand Prix races, 1999 to 2013.', 'This model won the Macau Grand Prix five times.'),
    ('outro', 'A crossplane crank came in 2009.', 'A crossplane crank came in two thousand nine.'),
    ('outro', None, 'Next: the falcon.'),
]
def shots(ease, out):
    import shotkit                      # imported here so the spec can be read without lib/ on the path
    return shotkit.standard(ease, out, CLOSE_ORDER, z=0.55, presets={'gearbox': (-10, 6, 2.3, (0.0, 0, 0.4), {}), 'carbs': (-30, 20, 1.9, (-0.02, 0, 0.62), {})}, ride_z=0.85)
COVER_PROMPT = 'Wide photograph, photorealistic, eye level, 50mm lens. An empty winding coastal road above a blue sea, soft morning light from the left, light haze. The road fills the lower third of the picture.'
THUMB_PROMPT = 'Tall vertical photograph, photorealistic, eye level, 35mm lens. An empty winding coastal road above a blue sea, soft morning light, bright sky at the top. The road fills the lower half of the picture.'
THUMB_BIG, THUMB_NAME = '1998', 'YAMAHA R1'
