"""ebike_today: a config of the generic bicycle builder (lib/cycle.py). Sizes follow the episode facts where stated, else guesses."""
from cycle import build_parts
C = dict(wheel_r=0.36, tyre=0.03, wb=1.14, frame='diamond', bars='flat', brakes='disc', gears=9, ebike=True, susp_fork=True, paint=(0.15, 0.17, 0.2), frame_paint=(0.18, 0.35, 0.45))
def build(): return build_parts(C)
