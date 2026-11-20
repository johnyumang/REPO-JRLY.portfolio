"""Bonus episode (was episode 25: spec for lib/make_episode.sh, written by lib/specgen.py (facts in facts.md)."""
EP, MODEL, WB = 25, 'lotus108_1992', 0.98
HOOK_BIG, HOOK_LINE = '1992', 'A bike from\na car maker.'
TITLE, TITLE_SIZE = 'LOTUS 108', 110
CLOSE_ORDER = ['frame', 'fork', 'handlebar', 'front_wheel']
CLOSE = {'frame': ('CARBON MONOCOQUE', 'frame', (280, 190)), 'fork': ('UNI-AXLE', 'fork', (470, 190)), 'handlebar': ('AERO BARS', 'handlebar', (270, 190)), 'front_wheel': ('DISC WHEELS', 'front_wheel', (270, 190))}
EXL = [('front_wheel', 'FRONT WHEEL'), ('handlebar', 'BARS'), ('saddle', 'SADDLE'), ('frame', 'MONOCOQUE'), ('rear_wheel', 'REAR WHEEL'), ('fork', 'FORK'), ('pedals', 'CRANKS')]
RIDE_TITLE = '27 JULY 1992'
NEXT_BIG, NEXT_SMALL = 'NEXT: A SUPERBIKE ICON', 'EP 26  ·  DUCATI 916, 1994'
ENGINE_RPM, ROAD_BAND = None, [300, 1500]
LINES = [
    ('hook', 'A bike from a car maker.', 'Nineteen ninety-two. A bike from a car maker.'),
    ('turn', 'The Lotus 108: designed by Mike Burrows, developed by Lotus Engineering.', 'The Lotus one-oh-eight. Designed by Mike Burrows, developed by Lotus Engineering.'),
    ('frame', 'A carbon composite monocoque with an aerofoil shape.', 'A carbon composite monocoque, with an aerofoil shape.'),
    ('fork', 'Lotus called it a “uni-axle” design.', 'Lotus called it a uni-axle design.'),
    ('handlebar', 'Built for the 4,000 m pursuit, on the track.', 'Built for the four thousand metre pursuit, on the track.'),
    ('front_wheel', 'Only sixteen were built.', 'Only sixteen were built.'),
    ('explode', 'Monocoque, fork, wheels, bars, saddle.', 'Take it apart. Monocoque, fork, wheels, bars, saddle.'),
    ('ride', 'Barcelona Olympics: Chris Boardman wins the 4,000 m individual pursuit.', 'Barcelona, nineteen ninety-two. Chris Boardman wins the individual pursuit.'),
    ('ride', 'In the final he catches world champion Jens Lehmann.', 'In the final, he catches world champion Jens Lehmann.'),
    ('outro', 'Replicas sold for £15,000 each.', 'Replicas sold for fifteen thousand pounds.'),
    ('outro', None, 'Next: a superbike icon.'),
]
def shots(ease, out):
    import shotkit                      # imported here so the spec can be read without lib/ on the path
    return shotkit.standard(ease, out, CLOSE_ORDER, z=0.5, presets={'drive': (-20, 10, 2.4, (-0.4, 0, 0.38), {'spin_r': -240}), 'brakes': (-40, 18, 2.0, (0.42, 0, 0.62), {}), 'fork': (-40, 10, 2.3, (0.5, 0, 0.5), {}), 'frame': (-35, 12, 3.0, (0.05, 0, 0.6), {}), 'front_wheel': (-10, 4, 2.4, (0.55, 0, 0.36), {'spin_f': -120}), 'handlebar': (-35, 30, 2.0, (0.38, 0, 0.92), {})}, ride_z=0.85)
COVER_PROMPT = 'Wide photograph, photorealistic, eye level, 50mm lens. An empty indoor wooden velodrome track with steep banking, soft light, soft morning light from the left, light haze. The road fills the lower third of the picture.'
THUMB_PROMPT = 'Tall vertical photograph, photorealistic, eye level, 35mm lens. An empty indoor wooden velodrome track with steep banking, soft light, soft morning light, bright sky at the top. The road fills the lower half of the picture.'
THUMB_BIG, THUMB_NAME = '1992', 'LOTUS 108'
