"""manx1950: a config of the generic builder (lib/moto.py). Sizes follow the episode facts where stated, else guesses."""
from moto import build_parts
C = dict(wb=1.40, rf=0.34, rr=0.34, tyre=0.05, engine='single', cc_scale=1.05, fork='tele', rear='twinshock', drive='chain', brake='drum', spokes=40, tank_len=0.62, seat_z=0.80, head_z=0.95, bars='clipon', exhaust='low', lights=False, paint=(0.72, 0.72, 0.74), frame_paint=(0.05, 0.05, 0.06), seat_len=0.40)
def build(): return build_parts(C)
