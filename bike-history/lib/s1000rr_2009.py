"""s1000rr_2009: a config of the generic builder (lib/moto.py). Sizes follow the episode facts where stated, else guesses."""
from moto import build_parts
C = dict(wb=1.43, rf=0.31, rr=0.32, tyre=0.065, engine='inline4', fins=False, cyl_tilt=32, fork='tele', rear='mono', drive='chain', brake='twin_disc', spokes=0, cast_arms=5, fairing='full', bars='clipon', tank_len=0.44, seat_z=0.82, head_z=0.95, exhaust='under', paint=(0.90, 0.90, 0.92), frame_paint=(0.65, 0.65, 0.68), seat_len=0.36)
def build(): return build_parts(C)
