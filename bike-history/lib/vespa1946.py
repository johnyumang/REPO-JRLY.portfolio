"""vespa1946: a config of the generic builder (lib/moto.py). Sizes follow the episode facts where stated, else guesses."""
from moto import build_parts
C = dict(wb=1.15, rf=0.20, rr=0.20, tyre=0.055, engine='scooter', spokes=0, cast_arms=4, fork='tele', rear='rigid', drive='none', brake='drum', seat_z=0.64, head_z=0.86, rake=20, bars='wide', exhaust='under', paint=(0.55, 0.68, 0.60), engine_col=(0.5, 0.5, 0.48), seat_len=0.40)
def build(): return build_parts(C)
