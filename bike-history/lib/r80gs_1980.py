"""r80gs_1980: a config of the generic builder (lib/moto.py). Sizes follow the episode facts where stated, else guesses."""
from moto import build_parts
C = dict(wb=1.465, rf=0.37, rr=0.34, tyre=0.05, engine='boxer', fork='tele', rear='mono', drive='shaft', brake='disc', spokes=40, tank_len=0.50, seat_z=0.86, head_z=1.05, rake=28, exhaust='high', paint=(0.92, 0.92, 0.92), frame_paint=(0.05, 0.05, 0.06), seat_len=0.62)
def build(): return build_parts(C)
