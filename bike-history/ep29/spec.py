"""Episode 29: spec for lib/make_episode.sh, written by lib/specgen.py (facts in facts.md)."""
EP, MODEL, WB = 29, 'panigale_v4_2018', 1.469
HOOK_BIG, HOOK_LINE = '2018', 'A V4 from\nMotoGP.'
TITLE, TITLE_SIZE = 'DUCATI PANIGALE V4', 72
CLOSE_ORDER = ['engine', 'frame', 'rear_suspension', 'brakes']
CLOSE = {'engine': ('V4 · 1,103 CC', 'engine', (260, 190)), 'frame': ('ALUMINIUM FRAME', 'frame', (260, 190)), 'rear_suspension': ('SINGLE-SIDED ARM', 'rear_suspension', (470, 190)), 'brakes': ('STYLEMA CALIPERS', 'brakes', (270, 190))}
EXL = [('front_wheel', 'FRONT WHEEL'), ('handlebar', 'HANDLEBAR'), ('tank', 'TANK'), ('engine', 'ENGINE'), ('frame', 'FRAME'), ('rear_wheel', 'REAR WHEEL'), ('saddle', 'SEAT'), ('fairing', 'FAIRING')]
RIDE_TITLE = 'MANDALIKA, 2022'
NEXT_BIG, NEXT_SMALL = 'NEXT: HARLEY GOES ELECTRIC', 'EP 30  ·  HARLEY-DAVIDSON LIVEWIRE, 2019'
ENGINE_RPM, ROAD_BAND = 11000, [150, 900]
LINES = [
    ('hook', 'A V4 from MotoGP.', 'Twenty eighteen. A V four, from Moto G P.'),
    ('turn', 'The Ducati Panigale V4: its engine is derived from the Desmosedici race bike.', 'The Ducati Panigale V four. Its engine comes from the Desmosedici race bike.'),
    ('engine', 'A 90-degree V4, 1,103 cc.', 'A ninety-degree V four. Eleven hundred and three cc.'),
    ('frame', 'An aluminium frame around the engine.', 'An aluminium frame, around the engine.'),
    ('rear_suspension', 'A single-sided swingarm, and a 43 mm Showa fork.', 'A single-sided swingarm, and a forty-three millimetre Showa fork.'),
    ('brakes', 'Brembo Stylema calipers on twin 330 mm discs.', 'Brembo Stylema calipers, on twin three-thirty millimetre discs.'),
    ('explode', 'Engine, frame, fairing, wheels: 173 kg dry.', 'Engine, frame, fairing, wheels. One hundred and seventy-three kilos.'),
    ('ride', '2022, Indonesia: Álvaro Bautista clinches the World Superbike title.', 'Twenty twenty-two, in Indonesia. Alvaro Bautista clinches the World Superbike title.'),
    ('ride', 'Sixteen wins that season.', 'Sixteen wins that season.'),
    ('outro', 'He had won on his debut, Phillip Island 2019.', 'He had won on his debut, at Phillip Island.'),
    ('outro', None, 'Next: Harley goes electric.'),
]
def shots(ease, out):
    import shotkit                      # imported here so the spec can be read without lib/ on the path
    return shotkit.standard(ease, out, CLOSE_ORDER, z=0.55, presets={}, ride_z=0.85)
COVER_PROMPT = 'Wide photograph, photorealistic, eye level, 50mm lens. An empty modern race circuit straight beside palm trees and the sea, soft morning light from the left, light haze. The road fills the lower third of the picture.'
THUMB_PROMPT = 'Tall vertical photograph, photorealistic, eye level, 35mm lens. An empty modern race circuit straight beside palm trees and the sea, soft morning light, bright sky at the top. The road fills the lower half of the picture.'
THUMB_BIG, THUMB_NAME = '2018', 'PANIGALE V4'
