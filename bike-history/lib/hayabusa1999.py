"""hayabusa1999: a config of the generic builder (lib/moto.py). Sizes follow the episode facts where stated, else guesses."""
from moto import build_parts
C = dict(wb=1.485, rf=0.31, rr=0.32, tyre=0.065, engine='inline4', fins=False, cyl_tilt=30, fork='tele', rear='mono', drive='chain', brake='twin_disc', spokes=0, cast_arms=3, fairing='full', bars='clipon', tank_len=0.48, seat_z=0.80, head_z=0.96, exhaust='twin', paint=(0.52, 0.48, 0.40), frame_paint=(0.6, 0.6, 0.62), seat_len=0.45)
def build(): return build_parts(C)
