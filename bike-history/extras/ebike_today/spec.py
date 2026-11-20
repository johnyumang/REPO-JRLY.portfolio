"""Bonus episode (was episode 30: spec for lib/make_episode.sh, written by lib/specgen.py (facts in facts.md)."""
EP, MODEL, WB = 30, 'ebike_today', 1.14
HOOK_BIG, HOOK_LINE = 'TODAY', 'The motor\ncomes back.'
TITLE, TITLE_SIZE = 'THE E-BIKE', 120
CLOSE_ORDER = ['motor', 'battery', 'pedals', 'handlebar']
CLOSE = {'motor': ('MID-DRIVE MOTOR', 'motor', (260, 190)), 'battery': ('LITHIUM-ION BATTERY', 'battery', (290, 190)), 'pedals': ('PEDAL SENSOR', 'pedals', (250, 190)), 'handlebar': ('DISPLAY', 'display', (270, 190))}
EXL = [('front_wheel', 'FRONT WHEEL'), ('handlebar', 'HANDLEBAR'), ('saddle', 'SADDLE'), ('frame', 'FRAME'), ('rear_wheel', 'REAR WHEEL'), ('motor', 'MOTOR'), ('battery', 'BATTERY'), ('pedals', 'CRANKS')]
RIDE_TITLE = 'TODAY'
NEXT_BIG, NEXT_SMALL = 'THE END · WATCH EP 1', 'FROM 1817 TO TODAY'
ENGINE_RPM, ROAD_BAND = None, [100, 700]
LINES = [
    ('hook', 'The motor comes back.', 'Today. The motor comes back.'),
    ('turn', 'The modern e-bike. The first electric bicycle patent: Ogden Bolton, 1895.', 'The modern e-bike. The first electric bicycle patent? Ogden Bolton, eighteen ninety-five.'),
    ('motor', 'A mid-drive motor near the pedals drives the chain: about 250 to 500 W.', 'A mid-drive motor near the pedals drives the chain. Two-fifty to five hundred watts.'),
    ('battery', 'Lithium-ion batteries: one charge, 40 to 120 km.', 'Lithium-ion batteries. One charge, forty to a hundred and twenty kilometres.'),
    ('pedals', 'Sensors read your pedalling speed, force, or both.', 'Sensors read your pedalling speed, force, or both.'),
    ('handlebar', 'In Europe, the motor cuts out at 25 km/h.', 'In Europe, the motor cuts out at twenty-five kilometres an hour.'),
    ('explode', 'Motor, battery, frame, wheels, gears, brakes.', 'Take it apart. Motor, battery, frame, wheels, gears, brakes.'),
    ('ride', 'EU e-bike sales: over 5 million in 2021.', 'E-bike sales in the E U, over five million in twenty twenty-one.'),
    ('ride', 'Still two wheels. Still a rider.', 'Still two wheels. Still a rider.'),
    ('outro', 'That’s the story, from 1817 to today.', "That's the story."),
    ('outro', None, 'Start again at episode one.'),
]
def shots(ease, out):
    import shotkit                      # imported here so the spec can be read without lib/ on the path
    return shotkit.standard(ease, out, CLOSE_ORDER, z=0.5, presets={'motor': (-20, 8, 1.9, (0.02, 0, 0.36), {}), 'battery': (-25, 12, 2.2, (0.22, 0, 0.62), {}), 'pedals': (-30, 10, 2.0, (0.0, 0, 0.34), {}), 'handlebar': (-35, 32, 1.7, (0.36, 0, 0.98), {})}, ride_z=0.85)
COVER_PROMPT = 'Wide photograph, photorealistic, eye level, 50mm lens. An empty modern city bike lane beside a river with trees and glass buildings, soft morning light from the left, light haze. The road fills the lower third of the picture.'
THUMB_PROMPT = 'Tall vertical photograph, photorealistic, eye level, 35mm lens. An empty modern city bike lane beside a river with trees and glass buildings, soft morning light, bright sky at the top. The road fills the lower half of the picture.'
THUMB_BIG, THUMB_NAME = 'TODAY', 'THE E-BIKE'
