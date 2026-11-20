"""cb750_1969: a config of the generic builder (lib/moto.py). Sizes follow the episode facts where stated, else guesses."""
from moto import build_parts
C = dict(wb=1.455, rf=0.33, rr=0.33, tyre=0.05, engine='inline4', fork='tele', rear='twinshock', drive='chain', brake='disc', spokes=40, tank_len=0.50, seat_z=0.81, head_z=0.98, exhaust='twin', paint=(0.55, 0.12, 0.05), engine_col=(0.65, 0.65, 0.63), seat_len=0.55)
def build(): return build_parts(C)
