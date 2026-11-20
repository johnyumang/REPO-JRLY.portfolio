"""lotus108_1992: a config of the generic bicycle builder (lib/cycle.py). Sizes follow the episode facts where stated, else guesses."""
from cycle import build_parts
C = dict(wheel_r=0.34, tyre=0.012, wb=0.98, frame='monocoque', bars='aero', brakes=None, gears=1, wheels='disc', bb_z=0.29, head_z=0.86, seat_z=0.93, paint=(0.05, 0.05, 0.06), frame_paint=(0.08, 0.08, 0.09))
def build(): return build_parts(C)
