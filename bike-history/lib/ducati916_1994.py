"""ducati916_1994: a config of the generic builder (lib/moto.py). Sizes follow the episode facts where stated, else guesses."""
from moto import build_parts
C = dict(wb=1.41, rf=0.31, rr=0.32, tyre=0.06, engine='vtwin', v_angle=90, fins=False, fork='tele', rear='mono', drive='chain', brake='twin_disc', spokes=0, cast_arms=3, fairing='full', bars='clipon', tank_len=0.45, seat_z=0.79, head_z=0.95, exhaust='under', paint=(0.70, 0.04, 0.04), frame_paint=(0.75, 0.06, 0.05), seat_len=0.38)
def build(): return build_parts(C)
