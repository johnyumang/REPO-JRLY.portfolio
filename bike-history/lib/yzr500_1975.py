"""yzr500_1975: a config of the generic builder (lib/moto.py). Sizes follow the episode facts where stated, else guesses."""
from moto import build_parts
C = dict(wb=1.38, rf=0.31, rr=0.32, tyre=0.06, engine='inline4', fins=False, cyl_tilt=35, fork='tele', rear='twinshock', drive='chain', brake='twin_disc', spokes=0, cast_arms=6, fairing='full', bars='clipon', tank_len=0.45, seat_z=0.78, head_z=0.92, exhaust='twin', lights=False, paint=(0.92, 0.92, 0.90), frame_paint=(0.75, 0.70, 0.10), seat_len=0.35)
def build(): return build_parts(C)
