"""norton1907: a config of the generic builder (lib/moto.py). Sizes follow the episode facts where stated, else guesses."""
from moto import build_parts
C = dict(wb=1.30, rf=0.34, rr=0.34, tyre=0.032, engine='vtwin', v_angle=45, cc_scale=0.8, fork='girder', rear='rigid', drive='belt', brake='drum', spokes=36, tank_len=0.40, seat_z=0.84, head_z=0.96, bars='wide', exhaust='low', lights=False, paint=(0.05, 0.05, 0.06), engine_col=(0.55, 0.55, 0.53), seat_len=0.26)
def build(): return build_parts(C)
