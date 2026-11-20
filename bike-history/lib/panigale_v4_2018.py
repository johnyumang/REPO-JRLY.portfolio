"""panigale_v4_2018: a config of the generic builder (lib/moto.py). Sizes follow the episode facts where stated, else guesses."""
from moto import build_parts
C = dict(wb=1.47, rf=0.31, rr=0.32, tyre=0.065, engine='v4', v_angle=90, fins=False, fork='tele', rear='mono', drive='chain', brake='twin_disc', spokes=0, cast_arms=5, fairing='full', bars='clipon', tank_len=0.44, seat_z=0.83, head_z=0.95, exhaust='under', paint=(0.75, 0.04, 0.04), frame_paint=(0.15, 0.15, 0.16), seat_len=0.34)
def build(): return build_parts(C)
