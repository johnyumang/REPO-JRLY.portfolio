"""speedtwin1937: a config of the generic builder (lib/moto.py). Sizes follow the episode facts where stated, else guesses."""
from moto import build_parts
C = dict(wb=1.40, rf=0.33, rr=0.33, tyre=0.05, engine='twin', cyl_tilt=0, cc_scale=0.85, fork='girder', rear='rigid', drive='chain', brake='drum', spokes=40, tank_len=0.48, seat_z=0.76, head_z=0.95, bars='wide', exhaust='twin', paint=(0.45, 0.10, 0.12), engine_col=(0.6, 0.6, 0.58), seat_len=0.30)
def build(): return build_parts(C)
