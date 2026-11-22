"""gsxr750_1985: a config of the generic builder (lib/moto.py). Sizes follow the episode facts where stated, else guesses."""
from moto import build_parts
C = dict(wb=1.41, rf=0.31, rr=0.31, tyre=0.06, engine='inline4', fins=True, cyl_tilt=30, fork='tele', rear='mono', drive='chain', brake='twin_disc', spokes=0, cast_arms=3, fairing='full', bars='clipon', tank_len=0.45, seat_z=0.81, head_z=0.95, exhaust='low', paint=(0.15, 0.25, 0.75), frame_paint=(0.75, 0.75, 0.78), seat_len=0.42)
def build(): return build_parts(C)
