"""Episode 8: Hildebrand & Wolfmüller, 1894. For lib/make_episode.sh."""
import math
EP, MODEL, WB = 8, 'hw1894', 1.30
HOOK_BIG, HOOK_LINE = '1894', 'A motorcycle\nyou could buy.'
TITLE, TITLE_SIZE = 'HILDEBRAND & WOLFMÜLLER', 64
CLOSE_ORDER = ['engine', 'water_tank', 'drive', 'brake']
CLOSE = {'engine': ('TWIN · 1,489 CC', 'engine', (260, 190)), 'water_tank': ('WATER TANK', 'water_tank', (470, 190)),
         'drive': ('CONNECTING RODS', 'drive', (300, 190)), 'brake': ('SPOON BRAKE', 'brake', (470, 190))}
EXL = [('front_wheel', 'FRONT WHEEL'), ('handlebar', 'HANDLEBAR'), ('saddle', 'SADDLE'), ('engine', 'ENGINE'),
       ('frame', 'FRAME'), ('rear_wheel', 'REAR WHEEL'), ('drive', 'CON RODS'), ('water_tank', 'WATER TANK')]
RIDE_TITLE = 'MUNICH, 1894'
NEXT_BIG, NEXT_SMALL = 'NEXT: AMERICA’S INDIAN', 'EP 9  ·  INDIAN, 1901'
ENGINE_RPM, ROAD_BAND = 480, [120, 800]
# Wolfmüller respelled Volf-myuller for the voice.
LINES = [
    ('hook', 'A motorcycle you could buy.', 'Eighteen ninety-four. A motorcycle you could buy.'),
    ('turn', 'The Hildebrand & Wolfmüller, Munich: often called the first production motorcycle.', 'The Hildebrand and Volf-myuller, from Munich. Often called the first production motorcycle.'),
    ('engine', 'Two cylinders, 1,489 cc, 2.5 hp at just 240 rpm.', 'Two cylinders, fourteen hundred and eighty-nine cc, at just two hundred and forty r p m.'),
    ('water_tank', 'Water-cooled: the water tank is the rear mudguard.', 'Water-cooled. The water tank is the rear mudguard.'),
    ('drive', 'No chain: connecting rods turn the rear wheel directly.', 'No chain. Connecting rods turn the rear wheel directly.'),
    ('brake', 'A spoon brake on the front tyre, and tyres full of air.', 'A spoon brake on the front tyre, and tyres full of air.'),
    ('explode', 'Engine, connecting rods, water tank, frame, wheels: about 50 kg dry.', 'Engine, connecting rods, water tank, frame, wheels. About fifty kilos.'),
    ('ride', 'No pedals, no clutch: to start, you ran alongside and jumped on.', 'No pedals, no clutch. To start, you ran alongside and jumped on.'),
    ('ride', 'About 2,000 were built. Top speed: 45 km/h.', 'About two thousand were built. Top speed, forty-five kilometres an hour.'),
    ('outro', 'By 1901, a faster machine took its crown.', 'By nineteen-oh-one, a faster machine took its crown.'),
    ('outro', None, 'Next: America\'s Indian.'),
]
def shots(ease, out):
    def hook(u): return dict(rot=-150 + 190 * out(u), el=10, dist=5.8 - 0.8 * out(u), target=(0, 0, 0.50), spin_f=-90 * u, spin_r=-90 * u)
    def turn(u): return dict(rot=40 + 360 * u, el=6 + 20 * math.sin(math.pi * u) ** 2, dist=5.0, target=(0, 0, 0.50))
    def engine(u): return dict(rot=-20 + 16 * u, el=12, dist=2.4 - 0.25 * ease(u), target=(0.15, 0, 0.40))
    def water_tank(u): return dict(rot=-150 + 14 * u, el=16, dist=2.4 - 0.25 * ease(u), target=(-0.55, 0, 0.45))
    def drive(u): return dict(rot=-30 + 14 * u, el=8, dist=2.8 - 0.25 * ease(u), target=(-0.25, 0, 0.35), spin_r=-180 * u)
    def brake(u): return dict(rot=-60 + 12 * u, el=30, dist=1.9 - 0.2 * ease(u), target=(0.62, 0, 0.70), spin_f=-(500 * u - 250 * u * u))
    def explode(u): return dict(rot=28 + 22 * u, el=16, dist=6.0, target=(0, 0, 0.55), explode=ease(min(1, u / 0.3)))
    def ride(u): return dict(rot=0, el=2.5, dist=5.8, target=(0, 0, 0.85), spin_f=-360 * u, spin_r=-360 * u * 0.33 / 0.28)
    return [('hook', 72, hook), ('turn', 168, turn), ('engine', 144, engine), ('water_tank', 144, water_tank),
            ('drive', 144, drive), ('brake', 144, brake), ('explode', 192, explode), ('ride', 16, ride)]
COVER_PROMPT = ('Wide photograph, photorealistic, eye level, 50mm lens. An empty cobbled square with old pastel townhouses softly '
                'out of focus, soft morning light from the left, light haze. The cobbles fill the lower third of the picture.')
THUMB_PROMPT = ('Tall vertical photograph, photorealistic, eye level, 35mm lens. An empty cobbled square with old pastel townhouses '
                'on both sides softly out of focus, soft morning light, bright sky at the top. The cobbles fill the lower half of the picture.')
THUMB_BIG, THUMB_NAME = '1894', 'THE FIRST TO BUY'
