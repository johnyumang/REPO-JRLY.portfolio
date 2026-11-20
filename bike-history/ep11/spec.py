"""Episode 11: generated spec for lib/make_episode.sh (facts in facts.md)."""
import math, shotkit
EP, MODEL, WB = 11, 'bmwr32', 1.38
HOOK_BIG, HOOK_LINE = '1923', 'BMW’s first\nmotorcycle.'
TITLE, TITLE_SIZE = 'BMW R 32', 104
CLOSE_ORDER = ['engine', 'shaft', 'frame', 'rear_wheel']
CLOSE = {'engine': ('FLAT-TWIN · 494 CC', 'engine', (270, 190)), 'shaft': ('SHAFT DRIVE', 'drive', (470, 190)), 'frame': ('TUBE FRAME', 'frame', (260, 190)), 'rear_wheel': ('RIGID REAR', 'rear_wheel', (470, 190))}
EXL = [('front_wheel', 'FRONT WHEEL'), ('handlebar', 'HANDLEBAR'), ('tank', 'TANK'), ('engine', 'ENGINE'), ('frame', 'FRAME'), ('rear_wheel', 'REAR WHEEL'), ('saddle', 'SEAT'), ('drive', 'SHAFT')]
RIDE_TITLE = 'PARIS, 1923'
NEXT_BIG, NEXT_SMALL = 'NEXT: THE KNUCKLEHEAD', 'EP 12  ·  HARLEY-DAVIDSON E, 1936'
ENGINE_RPM, ROAD_BAND = 2200, [150, 900]
LINES = [
    ('hook', 'BMW’s first motorcycle.', "Nineteen twenty-three. B M W's first motorcycle."),
    ('turn', 'The R 32, designed by Max Friz. It debuted at the Paris Auto Show.', 'The R thirty-two, designed by Max Fritz. It debuted at the Paris Auto Show.'),
    ('engine', 'A flat twin: 494 cc, air-cooled, 8.5 hp.', 'A flat twin. Four hundred and ninety-four cc, air-cooled, eight and a half horsepower.'),
    ('shaft', 'No chain: a shaft drives the rear wheel.', 'No chain. A shaft drives the rear wheel.'),
    ('frame', 'A steel tube frame, with two down tubes under the engine.', 'A steel tube frame, with two down tubes under the engine.'),
    ('rear_wheel', 'No rear springs, and the first ones had no front brake.', 'No rear springs. And the first ones had no front brake.'),
    ('explode', 'Engine, gearbox, shaft, frame, wheels: 122 kg wet.', 'Engine, gearbox, shaft, frame, wheels. One hundred and twenty-two kilos.'),
    ('ride', '3,090 were built, from 1923 to 1926.', 'Three thousand and ninety were built, from nineteen twenty-three to twenty-six.'),
    ('ride', 'Top speed: 95 km/h.', 'Top speed, ninety-five kilometres an hour.'),
    ('outro', 'BMW kept shaft drive until 1994.', 'B M W kept it until ninety-four.'),
    ('outro', None, 'Next: the Knucklehead.'),
]
def shots(ease, out): return shotkit.standard(ease, out, CLOSE_ORDER, z=0.55, presets={}, ride_z=0.88)
COVER_PROMPT = 'Wide photograph, photorealistic, eye level, 50mm lens. An empty old country road through rolling fields with tall poplar trees, soft morning light from the left, light haze. The road fills the lower third of the picture.'
THUMB_PROMPT = 'Tall vertical photograph, photorealistic, eye level, 35mm lens. An empty old country road through rolling fields with tall poplar trees, soft morning light, bright sky at the top. The road fills the lower half of the picture.'
THUMB_BIG, THUMB_NAME = '1923', 'BMW R 32'
