"""z1_1972: a config of the generic builder (lib/moto.py). Sizes follow the episode facts where stated, else guesses."""
from moto import build_parts
C = dict(wb=1.49, rf=0.33, rr=0.33, tyre=0.05, engine='inline4', fork='tele', rear='twinshock', drive='chain', brake='disc', spokes=40, tank_len=0.52, seat_z=0.81, head_z=0.98, exhaust='twin', paint=(0.35, 0.15, 0.05), engine_col=(0.12, 0.12, 0.13), seat_len=0.58)
def build(): return build_parts(C)
