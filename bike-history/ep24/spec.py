"""Episode 24: spec for lib/make_episode.sh, written by lib/specgen.py (facts in facts.md)."""
EP, MODEL, WB = 24, 'ducati916_1994', 1.41
HOOK_BIG, HOOK_LINE = '1994', 'The superbike\nicon.'
TITLE, TITLE_SIZE = 'DUCATI 916', 110
CLOSE_ORDER = ['engine', 'frame', 'rear_suspension', 'brakes']
CLOSE = {'engine': ('90° V-TWIN · 916 CC', 'engine', (270, 190)), 'frame': ('TRELLIS FRAME', 'frame', (260, 190)), 'rear_suspension': ('SINGLE-SIDED ARM', 'rear_suspension', (470, 190)), 'brakes': ('TWIN 320 MM DISCS', 'brakes', (270, 190))}
EXL = [('front_wheel', 'FRONT WHEEL'), ('handlebar', 'HANDLEBAR'), ('tank', 'TANK'), ('engine', 'ENGINE'), ('frame', 'FRAME'), ('rear_wheel', 'REAR WHEEL'), ('saddle', 'SEAT'), ('fairing', 'FAIRING')]
RIDE_TITLE = 'WSBK, 1994'
NEXT_BIG, NEXT_SMALL = 'NEXT: ONE LITRE, LESS WEIGHT', 'EP 25  ·  YAMAHA YZF-R1, 1998'
ENGINE_RPM, ROAD_BAND = 7000, [150, 900]
LINES = [
    ('hook', 'The superbike icon.', 'Nineteen ninety-four. The superbike icon.'),
    ('turn', 'The Ducati 916, by Massimo Tamburini and his team in San Marino.', 'The Ducati nine-sixteen, by Massimo Tamburini and his team, in San Marino.'),
    ('engine', 'A 90-degree V-twin: 916 cc, desmodromic valves.', 'A ninety-degree V twin. Nine hundred and sixteen cc, with desmodromic valves.'),
    ('frame', 'A chrome-moly steel trellis frame.', 'A chrome-moly steel trellis frame.'),
    ('rear_suspension', 'A single-sided swingarm, for faster wheel changes in races.', 'A single-sided swingarm, for faster wheel changes in races.'),
    ('brakes', 'Twin 320 mm front discs.', 'Twin, three hundred and twenty millimetre front discs.'),
    ('explode', 'Engine, frame, fairing, swingarm, wheels: 194.5 kg dry.', 'Engine, frame, fairing, swingarm, wheels. A hundred and ninety-five kilos.'),
    ('ride', '1994: Carl Fogarty wins the World Superbike title on the 916.', 'Nineteen ninety-four. Carl Fogarty wins the World Superbike title, on the nine-sixteen.'),
    ('ride', 'Ducati won the title with it in 1994, ’95, ’96 and ’98.', 'Ducati won the title with it four times.'),
    ('outro', 'Then came the 996.', 'Then came the nine-nine-six.'),
    ('outro', None, 'Next: a litre, and less weight.'),
]
def shots(ease, out):
    import shotkit                      # imported here so the spec can be read without lib/ on the path
    return shotkit.standard(ease, out, CLOSE_ORDER, z=0.55, presets={}, ride_z=0.85)
COVER_PROMPT = 'Wide photograph, photorealistic, eye level, 50mm lens. An empty Italian race circuit straight with red and white kerbs and hills behind, soft morning light from the left, light haze. The road fills the lower third of the picture.'
THUMB_PROMPT = 'Tall vertical photograph, photorealistic, eye level, 35mm lens. An empty Italian race circuit straight with red and white kerbs and hills behind, soft morning light, bright sky at the top. The road fills the lower half of the picture.'
THUMB_BIG, THUMB_NAME = '1994', 'DUCATI 916'
