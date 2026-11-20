"""Episode 7: the pneumatic tyre, 1888 (shown on a safety bicycle of 1889). For lib/make_episode.sh."""
import math
EP, MODEL, WB = 7, 'dunlop1888', 1.17
HOOK_BIG, HOOK_LINE = '1888', 'Air in\nthe tyres.'
TITLE, TITLE_SIZE = 'THE AIR TYRE', 100
CLOSE_ORDER = ['tyre', 'tube', 'frame', 'chain']
CLOSE = {'tyre': ('AIR-FILLED TYRE', 'tyre', (260, 190)), 'tube': ('INNER TUBE', 'tube', (470, 190)),
         'frame': ('SAFETY BICYCLE', 'frame', (280, 190)), 'chain': ('CHAIN DRIVE', 'chain', (470, 190))}
EXL = [('front_wheel', 'FRONT WHEEL'), ('tube', 'INNER TUBE'), ('handlebar', 'HANDLEBAR'), ('saddle', 'SADDLE'),
       ('frame', 'FRAME'), ('rear_wheel', 'REAR WHEEL'), ('chain', 'CHAIN'), ('pedals', 'PEDALS')]
RIDE_TITLE = '18 MAY 1889'
NEXT_BIG, NEXT_SMALL = 'NEXT: A MOTORCYCLE TO BUY', 'EP 8  ·  HILDEBRAND & WOLFMÜLLER, 1894'
ENGINE_RPM, ROAD_BAND = None, [120, 700]
LINES = [
    ('hook', 'Air in the tyres.', 'Eighteen eighty-eight. Air in the tyres.'),
    ('turn', 'In Belfast, John Boyd Dunlop made an air-filled tyre for his son’s tricycle.', 'In Belfast, John Boyd Dunlop made an air-filled tyre for his son\'s tricycle.'),
    ('tyre', 'Before this, tyres were solid rubber, and rough streets shook the rider.', 'Before this, tyres were solid rubber, and rough streets shook the rider.'),
    ('tube', 'Inside: a tube full of air that softens every bump.', 'Inside, a tube full of air softens every bump.'),
    ('frame', 'By 1889, safety bicycles rolled on Dunlop’s tyres.', 'By eighteen eighty-nine, safety bicycles rolled on Dunlop\'s tyres.'),
    ('chain', 'Patented 7 December 1888. But Robert Thomson had patented an air tyre in 1845.', 'Patented in December eighteen eighty-eight. But Robert Thomson had patented an air tyre in eighteen forty-five.'),
    ('explode', 'Wheels, inner tube, frame, chain, pedals, saddle.', 'Take it apart. Wheels, the inner tube, frame, chain, pedals, saddle.'),
    ('ride', 'Belfast, May 1889: Willie Hume races on air tyres at the Queen’s College Sports.', 'Belfast, May eighteen eighty-nine. Willie Hume races on air tyres at the Queen\'s College Sports.'),
    ('ride', 'He wins all four cycling races.', 'He wins all four cycling races.'),
    ('outro', 'Dunlop’s patent was later ruled invalid.', 'Dunlop\'s patent was later ruled invalid.'),
    ('outro', None, 'Next: a motorcycle you could buy.'),
]
def shots(ease, out):
    def hook(u): return dict(rot=-150 + 190 * out(u), el=10, dist=5.8 - 0.8 * out(u), target=(0, 0, 0.55), spin_f=-90 * u, spin_r=-90 * u)
    def turn(u): return dict(rot=40 + 360 * u, el=6 + 20 * math.sin(math.pi * u) ** 2, dist=5.0, target=(0, 0, 0.55))
    def tyre(u): return dict(rot=-18 + 12 * u, el=6, dist=2.3 - 0.25 * ease(u), target=(0.55, 0, 0.40), spin_f=-80 * u)
    def tube(u): return dict(rot=-55 + 10 * u, el=12, dist=2.8, target=(0.62, 0, 0.45), move={'tube': (0.25 * ease(min(1, u / 0.6)), 0.35 * ease(min(1, u / 0.6)), 0)})
    def frame(u): return dict(rot=-35 + 14 * u, el=14, dist=3.3 - 0.3 * ease(u), target=(0.12, 0, 0.66))
    def chain(u): return dict(rot=-165 + 14 * u, el=10, dist=2.6 - 0.25 * ease(u), target=(-0.25, 0, 0.42), spin_r=-240 * u)
    def explode(u): return dict(rot=28 + 22 * u, el=16, dist=6.2, target=(0, 0, 0.62), explode=ease(min(1, u / 0.3)))
    def ride(u): return dict(rot=0, el=2.5, dist=5.8, target=(0, 0, 0.90), spin_f=-360 * u, spin_r=-360 * u)
    return [('hook', 72, hook), ('turn', 168, turn), ('tyre', 144, tyre), ('tube', 144, tube),
            ('frame', 144, frame), ('chain', 144, chain), ('explode', 192, explode), ('ride', 16, ride)]

COVER_PROMPT = ('Wide photograph, photorealistic, eye level, 50mm lens. An empty grass sports field with a cinder running track, '
                'an old wooden grandstand softly out of focus, soft spring morning light from the left, light haze. The track fills the lower third of the picture.')
THUMB_PROMPT = ('Tall vertical photograph, photorealistic, eye level, 35mm lens. An empty grass sports field with a cinder running track, '
                'an old wooden grandstand softly out of focus, soft spring morning light, bright sky at the top. The track fills the lower half of the picture.')
THUMB_BIG, THUMB_NAME = '1888', 'AIR IN THE TYRES'
