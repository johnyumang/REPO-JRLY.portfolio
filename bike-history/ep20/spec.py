"""Episode 20: spec for lib/make_episode.sh, written by lib/specgen.py (facts in facts.md)."""
EP, MODEL, WB = 20, 'yzr500_1975', 1.38
HOOK_BIG, HOOK_LINE = '1975', 'A two-stroke\nchampion.'
TITLE, TITLE_SIZE = 'YAMAHA YZR500', 92
CLOSE_ORDER = ['engine', 'fairing', 'frame', 'exhaust']
CLOSE = {'engine': ('TWO-STROKE FOUR', 'engine', (270, 190)), 'fairing': ('RACING FAIRING', 'fairing', (270, 190)), 'frame': ('CHROMOLY FRAME', 'frame', (260, 190)), 'exhaust': ('EXPANSION PIPES', 'exhaust', (470, 190))}
EXL = [('front_wheel', 'FRONT WHEEL'), ('handlebar', 'HANDLEBAR'), ('tank', 'TANK'), ('engine', 'ENGINE'), ('frame', 'FRAME'), ('rear_wheel', 'REAR WHEEL'), ('saddle', 'SEAT'), ('fairing', 'FAIRING')]
RIDE_TITLE = '1975 WORLD TITLE'
NEXT_BIG, NEXT_SMALL = 'NEXT: THE DESERT', 'EP 21  ·  BMW R 80 G/S, 1980'
ENGINE_RPM, ROAD_BAND = 9000, [200, 1300]
LINES = [
    ('hook', 'A two-stroke champion.', 'Nineteen seventy-five. A two-stroke champion.'),
    ('turn', 'The Yamaha YZR500: this one is the 0W23 factory racer.', 'The Yamaha Y Z R five hundred. This one is the oh W twenty-three factory racer.'),
    ('engine', 'A two-stroke inline four: 494.7 cc, liquid-cooled.', 'A two-stroke inline four. Four hundred and ninety-five cc, liquid-cooled.'),
    ('fairing', 'A full racing fairing, made for the track.', 'A full racing fairing, made for the track.'),
    ('frame', 'A chromoly steel frame. Aluminium came only in 1980.', 'A chromoly steel frame. Aluminium came only in nineteen eighty.'),
    ('exhaust', 'The 500 cc class had been won by four-strokes, until now.', 'The five hundred class had always been won by four-strokes. Until now.'),
    ('explode', 'Engine, fairing, frame, fork, wheels.', 'Take it apart. Engine, fairing, frame, fork, wheels.'),
    ('ride', '1975: Giacomo Agostini wins the 500 cc world title on the 0W23.', 'Nineteen seventy-five. Giacomo Agostini wins the five hundred world title, on the oh W twenty-three.'),
    ('ride', 'The first premier-class title for a two-stroke.', 'The first premier class title for a two-stroke.'),
    ('outro', 'Kenny Roberts won three more.', 'Kenny Roberts won three more.'),
    ('outro', None, 'Next: into the desert.'),
]
def shots(ease, out):
    import shotkit                      # imported here so the spec can be read without lib/ on the path
    return shotkit.standard(ease, out, CLOSE_ORDER, z=0.52, presets={}, ride_z=0.88)
COVER_PROMPT = 'Wide photograph, photorealistic, eye level, 50mm lens. An empty race track straight with red and white kerbs and a grandstand in the distance, soft morning light from the left, light haze. The road fills the lower third of the picture.'
THUMB_PROMPT = 'Tall vertical photograph, photorealistic, eye level, 35mm lens. An empty race track straight with red and white kerbs and a grandstand in the distance, soft morning light, bright sky at the top. The road fills the lower half of the picture.'
THUMB_BIG, THUMB_NAME = '1975', 'YAMAHA YZR500'
