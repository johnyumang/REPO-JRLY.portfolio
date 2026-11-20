"""Episode 17: spec for lib/make_episode.sh, written by lib/specgen.py (facts in facts.md)."""
EP, MODEL, WB = 17, 'supercub1958', 1.18
HOOK_BIG, HOOK_LINE = '1958', 'The most\nproduced ever.'
TITLE, TITLE_SIZE = 'HONDA SUPER CUB', 82
CLOSE_ORDER = ['engine', 'body', 'handlebar', 'front_wheel']
CLOSE = {'engine': ('49 CC FOUR-STROKE', 'engine', (260, 190)), 'body': ('STEP-THROUGH', 'body', (470, 190)), 'handlebar': ('NO CLUTCH LEVER', 'handlebar', (280, 190)), 'front_wheel': ('17-INCH WHEELS', 'front_wheel', (270, 190))}
EXL = [('front_wheel', 'FRONT WHEEL'), ('handlebar', 'HANDLEBAR'), ('body', 'BODY'), ('engine', 'ENGINE'), ('rear_wheel', 'REAR WHEEL'), ('saddle', 'SEAT'), ('exhaust', 'EXHAUST')]
RIDE_TITLE = 'OVER 100 MILLION'
NEXT_BIG, NEXT_SMALL = 'NEXT: THE SUPERBIKE', 'EP 18  ·  HONDA CB750, 1969'
ENGINE_RPM, ROAD_BAND = 4000, [200, 1100]
LINES = [
    ('hook', 'The most produced motor vehicle ever.', 'Nineteen fifty-eight. The most produced motor vehicle ever.'),
    ('turn', 'The Honda Super Cub. The idea came from a 1956 trip through Germany.', 'The Honda Super Cub. The idea came from a trip through Germany in nineteen fifty-six.'),
    ('engine', 'A 49 cc four-stroke single: about 4.5 hp.', 'A forty-nine cc four-stroke single. About four and a half horsepower.'),
    ('body', 'A step-through pressed-steel frame: easy to get on.', 'A step-through, pressed steel frame. Easy to get on.'),
    ('handlebar', 'No clutch lever: a centrifugal clutch and a foot gear change.', 'No clutch lever. A centrifugal clutch, and a foot gear change.'),
    ('front_wheel', '17-inch wire wheels, and a leading-link front fork.', 'Seventeen-inch wire wheels, and a leading link fork.'),
    ('explode', 'Body, engine, wheels, seat, carrier.', 'Take it apart. Body, engine, wheels, seat, carrier.'),
    ('ride', 'Over 100 million built by 2017.', 'Over one hundred million were built by twenty seventeen.'),
    ('ride', 'Top speed: about 69 km/h.', 'Top speed, about sixty-nine kilometres an hour.'),
    ('outro', 'Honda built a new factory in Suzuka for it.', 'Honda built a new factory in Suzuka for it.'),
    ('outro', None, 'Next: the first superbike.'),
]
def shots(ease, out):
    import shotkit                      # imported here so the spec can be read without lib/ on the path
    return shotkit.standard(ease, out, CLOSE_ORDER, z=0.5, presets={'engine': (-20, 8, 2.0, (0.1, 0, 0.35), {}), 'body': (-30, 10, 2.8, (0.05, 0, 0.55), {}), 'front_wheel': (-15, 6, 2.2, (0.55, 0, 0.32), {'spin_f': -120})}, ride_z=0.88)
COVER_PROMPT = 'Wide photograph, photorealistic, eye level, 50mm lens. An empty narrow street in a small Japanese town with low wooden houses and shop signs without text, soft morning light from the left, light haze. The road fills the lower third of the picture.'
THUMB_PROMPT = 'Tall vertical photograph, photorealistic, eye level, 35mm lens. An empty narrow street in a small Japanese town with low wooden houses and shop signs without text, soft morning light, bright sky at the top. The road fills the lower half of the picture.'
THUMB_BIG, THUMB_NAME = '1958', 'SUPER CUB'
