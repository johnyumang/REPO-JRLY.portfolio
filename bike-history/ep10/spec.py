"""Episode 10: generated spec for lib/make_episode.sh (facts in facts.md)."""
import math, shotkit
EP, MODEL, WB = 10, 'norton1907', 1.3
HOOK_BIG, HOOK_LINE = '1907', 'The first\nTT race.'
TITLE, TITLE_SIZE = 'NORTON AT THE TT', 80
CLOSE_ORDER = ['engine', 'tank', 'fork', 'frame']
CLOSE = {'engine': ('PEUGEOT V-TWIN', 'engine', (260, 190)), 'tank': ('FUEL TANK', 'tank', (250, 190)), 'fork': ('FRONT FORK', 'fork', (470, 190)), 'frame': ('FRAME', 'frame', (250, 190))}
EXL = [('front_wheel', 'FRONT WHEEL'), ('handlebar', 'HANDLEBAR'), ('tank', 'TANK'), ('engine', 'ENGINE'), ('frame', 'FRAME'), ('rear_wheel', 'REAR WHEEL'), ('saddle', 'SEAT'), ('exhaust', 'EXHAUST')]
RIDE_TITLE = '28 MAY 1907'
NEXT_BIG, NEXT_SMALL = 'NEXT: BMW’S FIRST', 'EP 11  ·  BMW R 32, 1923'
ENGINE_RPM, ROAD_BAND = 1800, [150, 900]
LINES = [
    ('hook', 'The first TT race.', 'Nineteen-oh-seven. The first T T race.'),
    ('turn', 'The Norton that won it. James Lansdowne Norton built his machines in Birmingham.', 'This is the Norton that won it. James Lansdowne Norton built his machines in Birmingham.'),
    ('engine', 'Its engine: a twin from Peugeot of France.', 'Its engine, a twin, came from Peugeot of France.'),
    ('tank', 'The race: ten laps of the St John’s short course, Isle of Man.', "The race. Ten laps of the Saint John's short course, on the Isle of Man."),
    ('fork', 'Two classes: single cylinders and twins.', 'There were two classes. Single cylinders, and twins.'),
    ('frame', 'Number 22: Rem Fowler, a toolmaker, on the Norton.', 'Number twenty-two was Rem Fowler, a toolmaker, on the Norton.'),
    ('explode', 'Engine, tank, frame, fork, wheels.', 'Take it apart. Engine, tank, frame, fork, wheels.'),
    ('ride', 'Rem Fowler wins the twin-cylinder class, at about 36 mph.', 'Rem Fowler won the twin-cylinder class, at about thirty-six miles an hour.'),
    ('ride', 'His fastest lap, 42.91 mph, is a new record.', 'His fastest lap, forty-two point nine, was a new record.'),
    ('outro', 'Charlie Collier won the singles.', 'Charlie Collier won the singles.'),
    ('outro', None, "Next: B M W's first motorcycle."),
]
def shots(ease, out): return shotkit.standard(ease, out, CLOSE_ORDER, z=0.55, presets={}, ride_z=0.88)
COVER_PROMPT = 'Wide photograph, photorealistic, eye level, 50mm lens. An empty narrow country road winding between low stone walls and green hills on an island, soft morning light from the left, light haze. The road fills the lower third of the picture.'
THUMB_PROMPT = 'Tall vertical photograph, photorealistic, eye level, 35mm lens. An empty narrow country road winding between low stone walls and green hills on an island, soft morning light, bright sky at the top. The road fills the lower half of the picture.'
THUMB_BIG, THUMB_NAME = '1907', 'THE FIRST TT'
