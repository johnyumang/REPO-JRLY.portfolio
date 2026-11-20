"""Episode 6: the Daimler Reitwagen, 1885. Everything the generic pipeline needs (lib/make_episode.sh)."""
import math
EP, MODEL, WB = 6, 'reitwagen1885', 1.20
HOOK_BIG, HOOK_LINE = '1885', 'A motorcycle\nmade of wood.'
TITLE, TITLE_SIZE = 'THE REITWAGEN', 96
CLOSE_ORDER = ['engine', 'frame', 'drive', 'side_wheels']
CLOSE = {'engine': ('ONE CYLINDER · 264 CC', 'engine', (300, 190)), 'frame': ('WOODEN FRAME', 'frame', (250, 190)),
         'drive': ('BELT DRIVE', 'drive', (470, 190)), 'side_wheels': ('SIDE WHEELS', 'side_wheels', (250, 190))}
EXL = [('front_wheel', 'FRONT WHEEL'), ('handlebar', 'HANDLEBAR'), ('saddle', 'SADDLE'), ('engine', 'ENGINE'),
       ('frame', 'FRAME'), ('rear_wheel', 'REAR WHEEL'), ('drive', 'BELT'), ('side_wheels', 'SIDE WHEELS')]
RIDE_TITLE = 'NOVEMBER 1885'
NEXT_BIG, NEXT_SMALL = 'NEXT: AIR IN THE TYRES', 'EP 7  ·  THE PNEUMATIC TYRE, 1888'
ENGINE_RPM, ROAD_BAND = 600, [150, 900]
# (segment, subtitle or None, words spoken). Respelled for the voice: Reitwagen = Ryte-vahgen, Maybach = My-bahk,
# Cannstatt = Kahnshtat, Untertürkheim = Oonter-turk-hime.
LINES = [
    ('hook', 'A motorcycle made of wood.', 'Eighteen eighty-five. A motorcycle made of wood.'),
    ('turn', 'The Reitwagen, “riding car”, by Gottlieb Daimler and Wilhelm Maybach.', 'This is the Ryte-vahgen, the riding car, by Gottlieb Daimler and Wilhelm My-bahk.'),
    ('engine', 'One cylinder, 264 cc, half a horsepower.', 'One cylinder, two hundred and sixty-four cc, half a horsepower.'),
    ('frame', 'Wooden beams for a frame. Wooden wheels with iron tyres.', 'Wooden beams for a frame. Wooden wheels with iron tyres.'),
    ('drive', 'A belt carries the power to the rear wheel.', 'A belt carries the power to the rear wheel.'),
    ('side_wheels', 'Two small side wheels on springs keep it upright.', 'Two small side wheels on springs keep it upright.'),
    ('explode', 'Engine, wooden frame, belt, side wheels, saddle: about 90 kilos.', 'Engine, wooden frame, belt, side wheels, saddle. About ninety kilos.'),
    ('ride', 'November 1885: its first trip, Cannstatt to Untertürkheim.', 'In November eighteen eighty-five it made its first trip, from Kahnshtat to Oonter-turk-hime.'),
    ('ride', 'The hot ignition tube sat right under the seat. The seat caught fire.', 'The hot ignition tube sat right under the seat. The seat caught fire.'),
    ('outro', 'Who rode it first? The sources differ.', 'Who rode it first? The sources differ.'),
    ('outro', None, 'Next: air in the tyres.'),
]
def shots(ease, out):
    def hook(u): return dict(rot=-150 + 190 * out(u), el=10, dist=5.6 - 0.8 * out(u), target=(0, 0, 0.55), spin_f=-90 * u, spin_r=-90 * u)
    def turn(u): return dict(rot=40 + 360 * u, el=6 + 20 * math.sin(math.pi * u) ** 2, dist=4.8, target=(0, 0, 0.55))
    def engine(u): return dict(rot=-20 + 16 * u, el=10, dist=2.6 - 0.25 * ease(u), target=(0.05, 0, 0.62))
    def frame(u): return dict(rot=-35 + 14 * u, el=30, dist=2.8 - 0.25 * ease(u), target=(-0.05, 0, 0.62))
    def drive(u): return dict(rot=-160 + 14 * u, el=10, dist=2.6 - 0.25 * ease(u), target=(-0.25, 0, 0.48), spin_r=-200 * u)
    def side_wheels(u): return dict(rot=-60 + 16 * u, el=8, dist=2.8 - 0.25 * ease(u), target=(-0.15, 0, 0.40))
    def explode(u): return dict(rot=28 + 22 * u, el=16, dist=6.0, target=(0, 0, 0.62), explode=ease(min(1, u / 0.3)))
    def ride(u): return dict(rot=0, el=2.5, dist=5.6, target=(0, 0, 0.90), spin_f=-360 * u, spin_r=-360 * u * 0.34 / 0.39)
    return [('hook', 72, hook), ('turn', 168, turn), ('engine', 144, engine), ('frame', 144, frame),
            ('drive', 144, drive), ('side_wheels', 144, side_wheels), ('explode', 192, explode), ('ride', 16, ride)]
COVER_PROMPT = ('Wide photograph, photorealistic, eye level, 50mm lens. An empty garden path beside an old glass-fronted '
                'summer house and fruit trees, soft morning light from the left, light haze. The gravel path fills the lower third of the picture.')
THUMB_PROMPT = ('Tall vertical photograph, photorealistic, eye level, 35mm lens. An empty garden path beside an old glass-fronted '
                'summer house and fruit trees, soft morning light, bright sky at the top. The gravel path fills the lower half of the picture.')
THUMB_BIG, THUMB_NAME = '1885', 'THE WOODEN MOTORCYCLE'
