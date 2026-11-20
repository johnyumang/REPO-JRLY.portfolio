"""knuckle1936: a config of the generic builder (lib/moto.py). Sizes follow the episode facts where stated, else guesses."""
from moto import build_parts
C = dict(wb=1.50, rf=0.33, rr=0.33, tyre=0.06, engine='vtwin', v_angle=45, cc_scale=1.1, fork='girder', rear='rigid', drive='chain', brake='drum', spokes=40, tank_len=0.55, seat_z=0.72, head_z=0.92, bars='wide', exhaust='low', paint=(0.12, 0.25, 0.15), engine_col=(0.55, 0.55, 0.53), seat_len=0.34)
def build(): return build_parts(C)
