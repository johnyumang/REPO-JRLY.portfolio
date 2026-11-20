"""Episode 30: spec for lib/make_episode.sh, written by lib/specgen.py (facts in facts.md)."""
import shotkit
EP, MODEL, WB = 30, 'livewire_2019', 1.49
HOOK_BIG, HOOK_LINE = '2019', 'Harley goes\nelectric.'
TITLE, TITLE_SIZE = 'THE LIVEWIRE', 110
CLOSE_ORDER = ['engine', 'battery', 'drive', 'brakes']
CLOSE = {'engine': ('ELECTRIC MOTOR · 105 HP', 'engine', (290, 190)), 'battery': ('15.5 KWH BATTERY', 'engine', (270, 190)), 'drive': ('ONE SPEED · BELT', 'drive', (470, 190)), 'brakes': ('MONOBLOC CALIPERS', 'brakes', (270, 190))}
EXL = [('front_wheel', 'FRONT WHEEL'), ('handlebar', 'HANDLEBAR'), ('tank', 'TANK'), ('engine', 'MOTOR + BATTERY'), ('frame', 'FRAME'), ('rear_wheel', 'REAR WHEEL'), ('saddle', 'SEAT'), ('drive', 'BELT')]
RIDE_TITLE = 'MARCH 2020'
NEXT_BIG, NEXT_SMALL = 'THE END · WATCH EP 1', 'FROM 1817 TO TODAY'
ELECTRIC = True
ENGINE_RPM, ROAD_BAND = None, [150, 900]
LINES = [
    ('hook', 'Harley-Davidson goes electric.', 'Twenty nineteen. Harley-Davidson goes electric.'),
    ('turn', 'The Harley-Davidson LiveWire: its first electric vehicle.', 'The Harley-Davidson LiveWire. Its first electric vehicle.'),
    ('engine', 'A liquid-cooled electric motor: 105 hp.', 'A liquid-cooled electric motor. One hundred and five horsepower.'),
    ('battery', 'A 15.5 kWh battery, with DC fast charging.', 'A fifteen and a half kilowatt-hour battery, with fast charging.'),
    ('drive', 'One speed and a belt: no gears to change.', 'One speed, and a belt. No gears to change.'),
    ('brakes', 'Four-piston monobloc calipers, twin front discs.', 'Four-piston monobloc calipers, on twin front discs.'),
    ('explode', 'Motor, battery, frame, wheels: 255 kg.', 'Motor, battery, frame, wheels. Two hundred and fifty-five kilos.'),
    ('ride', 'March 2020: Michel von Tell rides 1,723 km in 24 hours.', 'March twenty twenty. Michel von Tell rides seventeen hundred kilometres in twenty-four hours.'),
    ('ride', 'An unofficial distance record for an electric motorcycle.', 'An unofficial record, for an electric motorcycle.'),
    ('outro', 'That’s the story, from 1817 to today.', "That's the story."),
    ('outro', None, 'Start again at episode one.'),
]
def shots(ease, out): return shotkit.standard(ease, out, CLOSE_ORDER, z=0.55, presets={'battery': (-15, 14, 2.4, (0.02, 0, 0.6), {}), 'drive': (165, 10, 2.7, (-0.35, 0, 0.4), {'spin_r': -240})}, ride_z=0.85)
COVER_PROMPT = 'Wide photograph, photorealistic, eye level, 50mm lens. An empty modern city street at dusk with glass buildings and street lights, soft morning light from the left, light haze. The road fills the lower third of the picture.'
THUMB_PROMPT = 'Tall vertical photograph, photorealistic, eye level, 35mm lens. An empty modern city street at dusk with glass buildings and street lights, soft morning light, bright sky at the top. The road fills the lower half of the picture.'
THUMB_BIG, THUMB_NAME = '2019', 'THE LIVEWIRE'
