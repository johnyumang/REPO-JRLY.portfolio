"""vincent1948: a config of the generic builder (lib/moto.py). Sizes follow the episode facts where stated, else guesses."""
from moto import build_parts
C = dict(wb=1.435, rf=0.34, rr=0.34, tyre=0.05, engine='vtwin', v_angle=50, cc_scale=1.15, fork='girder', rear='mono', drive='chain', brake='drum', spokes=40, tank_len=0.52, seat_z=0.80, head_z=0.97, bars='wide', exhaust='low', paint=(0.04, 0.04, 0.05), engine_col=(0.12, 0.12, 0.13), seat_len=0.40)
def build(): return build_parts(C)
