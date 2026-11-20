"""Episode 15: spec for lib/make_episode.sh, written by lib/specgen.py (facts in facts.md)."""
import shotkit
EP, MODEL, WB = 15, 'vincent1948', 1.435
HOOK_BIG, HOOK_LINE = '1948', 'A V-twin\nbuilt for speed.'
TITLE, TITLE_SIZE = 'VINCENT BLACK SHADOW', 66
CLOSE_ORDER = ['engine', 'frame', 'rear_suspension', 'brakes']
CLOSE = {'engine': ('V-TWIN · 998 CC', 'engine', (260, 190)), 'frame': ('ENGINE AS FRAME', 'frame', (280, 190)), 'rear_suspension': ('CANTILEVER REAR', 'rear_suspension', (470, 190)), 'brakes': ('TWIN DRUMS', 'brakes', (250, 190))}
EXL = [('front_wheel', 'FRONT WHEEL'), ('handlebar', 'HANDLEBAR'), ('tank', 'TANK'), ('engine', 'ENGINE'), ('frame', 'FRAME'), ('rear_wheel', 'REAR WHEEL'), ('saddle', 'SEAT'), ('exhaust', 'EXHAUST')]
RIDE_TITLE = '13 SEPT 1948'
NEXT_BIG, NEXT_SMALL = 'NEXT: A FEATHERBED', 'EP 16  ·  NORTON MANX, 1950'
ENGINE_RPM, ROAD_BAND = 1800, [150, 900]
LINES = [
    ('hook', 'A V-twin built for speed.', 'Nineteen forty-eight. A V twin, built for speed.'),
    ('turn', 'The Vincent Black Shadow, from Stevenage, England.', 'The Vincent Black Shadow, from Stevenage, England.'),
    ('engine', 'A 998 cc V-twin, 55 bhp.', 'A nine hundred and ninety-eight cc V twin. Fifty-five horsepower.'),
    ('frame', 'No down tubes: the engine is part of the frame.', 'No down tubes. The engine itself is part of the frame.'),
    ('rear_suspension', 'A cantilever rear suspension.', 'A cantilever rear suspension.'),
    ('brakes', 'Twin drum brakes, front and rear.', 'Twin drum brakes, front and rear.'),
    ('explode', 'Engine, frame, fork, wheels: 208 kg dry.', 'Engine, frame, fork, wheels. Two hundred and eight kilos.'),
    ('ride', 'Bonneville Salt Flats, Utah: Rollie Free lies flat, in a bathing suit.', 'September thirteenth, nineteen forty-eight. Bonneville Salt Flats, Utah. Rollie Free lies flat, in a bathing suit.'),
    ('ride', '150.313 mph, on a Vincent.', 'One hundred and fifty point three miles an hour, on a Vincent.'),
    ('outro', 'Built until 1955.', 'It was built until nineteen fifty-five.'),
    ('outro', None, 'Next: riding on a featherbed.'),
]
def shots(ease, out): return shotkit.standard(ease, out, CLOSE_ORDER, z=0.55, presets={}, ride_z=0.88)
COVER_PROMPT = 'Wide photograph, photorealistic, eye level, 50mm lens. An empty flat white salt lake under a huge blue sky, distant mountains, soft morning light from the left, light haze. The road fills the lower third of the picture.'
THUMB_PROMPT = 'Tall vertical photograph, photorealistic, eye level, 35mm lens. An empty flat white salt lake under a huge blue sky, distant mountains, soft morning light, bright sky at the top. The road fills the lower half of the picture.'
THUMB_BIG, THUMB_NAME = '1948', 'BLACK SHADOW'
