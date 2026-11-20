"""Episode 9: the Indian motorized bicycle, 1901. For lib/make_episode.sh."""
import math
EP, MODEL, WB = 9, 'indian1901', 1.17
HOOK_BIG, HOOK_LINE = '1901', 'America gets\na motorcycle.'
TITLE, TITLE_SIZE = 'THE INDIAN', 104
CLOSE_ORDER = ['engine', 'carburettor', 'frame', 'pedals']
CLOSE = {'engine': ('SINGLE · 1.75 BHP', 'engine', (250, 190)), 'carburettor': ('CARBURETTOR', 'carburettor', (470, 190)),
         'frame': ('DIAMOND FRAME', 'frame', (280, 190)), 'pedals': ('PEDALS', 'pedals', (250, 190))}
EXL = [('front_wheel', 'FRONT WHEEL'), ('handlebar', 'HANDLEBAR'), ('tank', 'TANK'), ('engine', 'ENGINE'),
       ('frame', 'FRAME'), ('rear_wheel', 'REAR WHEEL'), ('chain', 'CHAIN'), ('pedals', 'PEDALS')]
RIDE_TITLE = '1 JUNE 1901'
NEXT_BIG, NEXT_SMALL = 'NEXT: THE FIRST TT RACE', 'EP 10  ·  NORTON, 1907'
ENGINE_RPM, ROAD_BAND = 1400, [120, 800]
LINES = [
    ('hook', 'America gets a motorcycle.', 'Nineteen-oh-one. America gets a motorcycle.'),
    ('turn', 'The Indian: George Hendee and Oscar Hedstrom, Springfield, Massachusetts.', 'The Indian, by George Hendee and Oscar Hedstrom, of Springfield, Massachusetts.'),
    ('engine', 'One cylinder, 1.75 hp. The engine is part of the frame.', 'One cylinder, one point seven five horsepower. Part of the frame.'),
    ('carburettor', 'Hedstrom designed his own carburettor.', 'Hedstrom designed his own carburettor.'),
    ('frame', 'A diamond frame, like a bicycle.', 'A diamond frame, just like a bicycle.'),
    ('pedals', 'Hendee wanted a motorized bicycle: pedals and all.', 'Hendee wanted a motorized bicycle. Pedals and all.'),
    ('explode', 'Engine, tank, frame, chain, pedals, wheels.', 'Take it apart. Engine, tank, frame, chain, pedals, wheels.'),
    ('ride', '1 June 1901: first public demonstration, Cross Street, Springfield.', 'June first, nineteen-oh-one. First public demonstration, Cross Street, Springfield.'),
    ('ride', '1903: Hedstrom sets a world record, 56 mph.', 'In nineteen-oh-three, Hedstrom set a world record. Fifty-six miles an hour.'),
    ('outro', '1911: Indians take the top three at the TT.', 'Nineteen eleven: a T T sweep.'),
    ('outro', None, 'Next: the first T T race.'),
]
def shots(ease, out):
    def hook(u): return dict(rot=-150 + 190 * out(u), el=10, dist=5.8 - 0.8 * out(u), target=(0, 0, 0.55), spin_f=-90 * u, spin_r=-90 * u)
    def turn(u): return dict(rot=40 + 360 * u, el=6 + 20 * math.sin(math.pi * u) ** 2, dist=5.0, target=(0, 0, 0.55))
    def engine(u): return dict(rot=-20 + 16 * u, el=10, dist=2.4 - 0.25 * ease(u), target=(0.0, 0, 0.52))
    def carburettor(u): return dict(rot=-55 + 12 * u, el=14, dist=1.9 - 0.2 * ease(u), target=(0.10, 0, 0.50))
    def frame(u): return dict(rot=-35 + 14 * u, el=14, dist=3.3 - 0.3 * ease(u), target=(0.12, 0, 0.66))
    def pedals(u): return dict(rot=-40 + 14 * u, el=10, dist=2.3 - 0.25 * ease(u), target=(0.04, 0, 0.40))
    def explode(u): return dict(rot=28 + 22 * u, el=16, dist=6.2, target=(0, 0, 0.62), explode=ease(min(1, u / 0.3)))
    def ride(u): return dict(rot=0, el=2.5, dist=5.8, target=(0, 0, 0.90), spin_f=-360 * u, spin_r=-360 * u)
    return [('hook', 72, hook), ('turn', 168, turn), ('engine', 144, engine), ('carburettor', 144, carburettor),
            ('frame', 144, frame), ('pedals', 144, pedals), ('explode', 192, explode), ('ride', 16, ride)]
COVER_PROMPT = ('Wide photograph, photorealistic, eye level, 50mm lens. An empty New England town street with painted wooden '
                'storefronts and leafy trees softly out of focus, a dirt road, warm morning light from the left, light haze. The road fills the lower third of the picture.')
THUMB_PROMPT = ('Tall vertical photograph, photorealistic, eye level, 35mm lens. An empty New England town street with painted wooden '
                'storefronts and leafy trees on both sides softly out of focus, a dirt road, warm morning light, bright sky at the top. The road fills the lower half of the picture.')
THUMB_BIG, THUMB_NAME = '1901', 'THE INDIAN'
