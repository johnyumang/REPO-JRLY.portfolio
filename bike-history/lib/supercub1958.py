"""supercub1958: a config of the generic builder (lib/moto.py). Sizes follow the episode facts where stated, else guesses."""
from moto import build_parts
C = dict(wb=1.18, rf=0.29, rr=0.29, tyre=0.035, engine='stepthrough', spokes=36, fork='leading', rear='twinshock', drive='chain', brake='drum', seat_z=0.76, head_z=0.95, rake=24, bars='wide', exhaust='low', paint=(0.62, 0.10, 0.10), engine_col=(0.55, 0.55, 0.52), seat_len=0.42)
def build(): return build_parts(C)
