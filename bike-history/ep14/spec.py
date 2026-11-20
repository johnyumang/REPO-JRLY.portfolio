"""Episode 14: spec for lib/make_episode.sh, written by lib/specgen.py (facts in facts.md)."""
EP, MODEL, WB = 14, 'vespa1946', 1.15
HOOK_BIG, HOOK_LINE = '1946', 'A wasp\nfrom Italy.'
TITLE, TITLE_SIZE = 'THE VESPA', 110
CLOSE_ORDER = ['body', 'engine', 'front_wheel', 'handlebar']
CLOSE = {'body': ('MONOCOQUE BODY', 'body', (470, 190)), 'engine': ('98 CC TWO-STROKE', 'engine', (270, 190)), 'front_wheel': ('8-INCH WHEELS', 'front_wheel', (270, 190)), 'handlebar': ('TWISTGRIP GEARS', 'handlebar', (270, 190))}
EXL = [('front_wheel', 'FRONT WHEEL'), ('handlebar', 'HANDLEBAR'), ('body', 'BODY'), ('engine', 'ENGINE'), ('rear_wheel', 'REAR WHEEL'), ('saddle', 'SEAT'), ('exhaust', 'EXHAUST')]
RIDE_TITLE = 'MILAN, 1946'
NEXT_BIG, NEXT_SMALL = 'NEXT: A RECORD ON THE SALT', 'EP 15  ·  VINCENT BLACK SHADOW, 1948'
ENGINE_RPM, ROAD_BAND = 3000, [200, 1200]
LINES = [
    ('hook', 'A wasp from Italy.', 'Nineteen forty-six. A wasp from Italy.'),
    ('turn', 'The Vespa, by Piaggio of Pontedera. The design is credited to aircraft engineer Corradino D’Ascanio.', 'The Vespa, by Pee-ah-jo of Pontedera. Its design is credited to aircraft engineer Corradino Dahs-kahn-yo.'),
    ('body', 'One of the first monocoques: the pressed-steel body is the frame.', 'One of the first monocoques. The pressed steel body is the frame.'),
    ('engine', 'A 98 cc two-stroke under the body drives the rear wheel directly.', 'A ninety-eight cc two-stroke, under the body, drives the rear wheel directly.'),
    ('front_wheel', 'Small 8-inch wheels.', 'Small, eight-inch wheels.'),
    ('handlebar', 'Three gears, changed with a twistgrip.', 'Three gears, changed with a twist grip.'),
    ('explode', 'Body, engine, wheels, handlebar, seat.', 'Take it apart. Body, engine, wheels, handlebar, seat.'),
    ('ride', 'Enrico Piaggio saw it: “It looks like a wasp!” Vespa, in Italian.', 'Enrico Pee-ah-jo saw it and said: it looks like a wasp! Vespa, in Italian.'),
    ('ride', 'Its public debut: the 1946 Milan Fair.', 'Its public debut, the Milan Fair, nineteen forty-six.'),
    ('outro', 'About 2,500 sold in 1947.', 'About twenty-five hundred sold in forty-seven.'),
    ('outro', None, 'Next: a record on the salt.'),
]
def shots(ease, out):
    import shotkit                      # imported here so the spec can be read without lib/ on the path
    return shotkit.standard(ease, out, CLOSE_ORDER, z=0.45, presets={'engine': (-25, 10, 2.2, (-0.3, 0, 0.3), {}), 'body': (-150, 10, 2.6, (-0.2, 0, 0.4), {}), 'front_wheel': (-30, 6, 2.0, (0.52, 0, 0.25), {'spin_f': -120})}, ride_z=0.8)
COVER_PROMPT = 'Wide photograph, photorealistic, eye level, 50mm lens. An empty sunny Italian piazza with pale ochre buildings and a stone fountain, soft morning light from the left, light haze. The road fills the lower third of the picture.'
THUMB_PROMPT = 'Tall vertical photograph, photorealistic, eye level, 35mm lens. An empty sunny Italian piazza with pale ochre buildings and a stone fountain, soft morning light, bright sky at the top. The road fills the lower half of the picture.'
THUMB_BIG, THUMB_NAME = '1946', 'THE VESPA'
