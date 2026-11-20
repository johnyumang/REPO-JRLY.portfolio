"""rc211v_2002: a config of the generic builder (lib/moto.py). Sizes follow the episode facts where stated, else guesses."""
from moto import build_parts
C = dict(wb=1.44, rf=0.31, rr=0.30, tyre=0.065, engine='v5', v_angle=75.5, fins=False, fork='tele', rear='mono', drive='chain', brake='twin_disc', spokes=0, cast_arms=5, fairing='full', bars='clipon', tank_len=0.42, seat_z=0.82, head_z=0.93, exhaust='under', lights=False, paint=(0.92, 0.92, 0.92), frame_paint=(0.6, 0.6, 0.62), seat_len=0.32)
def build(): return build_parts(C)
