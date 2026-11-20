"""r1_1998: a config of the generic builder (lib/moto.py). Sizes follow the episode facts where stated, else guesses."""
from moto import build_parts
C = dict(wb=1.40, rf=0.31, rr=0.32, tyre=0.06, engine='inline4', fins=False, cyl_tilt=30, fork='tele', rear='mono', drive='chain', brake='twin_disc', spokes=0, cast_arms=5, fairing='full', bars='clipon', tank_len=0.42, seat_z=0.82, head_z=0.95, exhaust='under', paint=(0.10, 0.22, 0.65), frame_paint=(0.7, 0.7, 0.72), seat_len=0.38)
def build(): return build_parts(C)
