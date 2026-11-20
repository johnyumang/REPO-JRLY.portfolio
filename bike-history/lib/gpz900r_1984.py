"""gpz900r_1984: a config of the generic builder (lib/moto.py). Sizes follow the episode facts where stated, else guesses."""
from moto import build_parts
C = dict(wb=1.495, rf=0.30, rr=0.33, tyre=0.06, engine='inline4', fins=False, cyl_tilt=30, fork='tele', rear='mono', drive='chain', brake='twin_disc', spokes=0, cast_arms=6, fairing='full', bars='clipon', tank_len=0.50, seat_z=0.79, head_z=0.95, exhaust='low', paint=(0.85, 0.10, 0.08), frame_paint=(0.1, 0.1, 0.1), seat_len=0.48)
def build(): return build_parts(C)
