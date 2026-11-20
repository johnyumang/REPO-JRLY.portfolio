"""Episode 28: spec for lib/make_episode.sh, written by lib/specgen.py (facts in facts.md)."""
EP, MODEL, WB = 28, 's1000rr_2009', 1.42
HOOK_BIG, HOOK_LINE = '2009', 'A superbike\nfrom BMW.'
TITLE, TITLE_SIZE = 'BMW S 1000 RR', 92
CLOSE_ORDER = ['engine', 'frame', 'fork', 'brakes']
CLOSE = {'engine': ('998 CC INLINE FOUR', 'engine', (270, 190)), 'frame': ('ALUMINIUM TWIN-SPAR', 'frame', (280, 190)), 'fork': ('46 MM INVERTED FORK', 'fork', (470, 190)), 'brakes': ('TWIN 320 MM DISCS', 'brakes', (270, 190))}
EXL = [('front_wheel', 'FRONT WHEEL'), ('handlebar', 'HANDLEBAR'), ('tank', 'TANK'), ('engine', 'ENGINE'), ('frame', 'FRAME'), ('rear_wheel', 'REAR WHEEL'), ('saddle', 'SEAT'), ('fairing', 'FAIRING')]
RIDE_TITLE = 'ISLE OF MAN, 2014'
NEXT_BIG, NEXT_SMALL = 'NEXT: A V4 FROM MOTOGP', 'EP 29  ·  DUCATI PANIGALE V4, 2018'
ENGINE_RPM, ROAD_BAND = 11000, [150, 900]
LINES = [
    ('hook', 'A superbike from BMW.', 'Two thousand nine. A superbike from B M W.'),
    ('turn', 'The BMW S 1000 RR.', 'The B M W S one thousand R R.'),
    ('engine', 'A 998 cc inline four, liquid-cooled.', 'A nine hundred and ninety-eight cc inline four, liquid-cooled.'),
    ('frame', 'An aluminium twin-spar frame.', 'An aluminium twin-spar frame.'),
    ('fork', 'A 46 mm inverted fork.', 'A forty-six millimetre, inverted fork.'),
    ('brakes', 'Twin 320 mm front discs, four-piston calipers.', 'Twin three-twenty millimetre front discs, with four-piston calipers.'),
    ('explode', 'Engine, frame, fairing, wheels.', 'Take it apart. Engine, frame, fairing, wheels.'),
    ('ride', 'Isle of Man, 31 May 2014: Michael Dunlop wins the Superbike TT.', 'Isle of Man, May twenty fourteen. Michael Dunlop wins the Superbike T T.'),
    ('ride', 'On 6 June, he wins the Senior TT too.', 'A week later, he wins the Senior T T too.'),
    ('outro', '2012: Marco Melandri wins at Donington Park.', 'Twenty twelve: a win at Donington.'),
    ('outro', None, 'Next: a V four from Moto G P.'),
]
def shots(ease, out):
    import shotkit                      # imported here so the spec can be read without lib/ on the path
    return shotkit.standard(ease, out, CLOSE_ORDER, z=0.55, presets={}, ride_z=0.85)
COVER_PROMPT = 'Wide photograph, photorealistic, eye level, 50mm lens. An empty narrow island road between stone walls and green hills under a grey sky, soft morning light from the left, light haze. The road fills the lower third of the picture.'
THUMB_PROMPT = 'Tall vertical photograph, photorealistic, eye level, 35mm lens. An empty narrow island road between stone walls and green hills under a grey sky, soft morning light, bright sky at the top. The road fills the lower half of the picture.'
THUMB_BIG, THUMB_NAME = '2009', 'BMW S 1000 RR'
