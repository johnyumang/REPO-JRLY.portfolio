"""bmwr32: a config of the generic builder (lib/moto.py). Sizes follow the episode facts where stated, else guesses."""
from moto import build_parts
C = dict(wb=1.38, rf=0.36, rr=0.36, tyre=0.045, engine='boxer', fork='leading', rear='rigid', drive='shaft', brake='drum', spokes=36, tank_len=0.42, seat_z=0.74, head_z=0.95, bars='wide', exhaust='twin', paint=(0.03, 0.03, 0.04), cc_scale=0.9, seat_len=0.30)
def build(): return build_parts(C)
