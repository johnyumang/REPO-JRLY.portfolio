"""stumpjumper1981: a config of the generic bicycle builder (lib/cycle.py). Sizes follow the episode facts where stated, else guesses."""
from cycle import build_parts
C = dict(wheel_r=0.34, tyre=0.036, wb=1.08, frame='diamond', bars='flat', brakes='cantilever', gears=5, paint=(0.7, 0.1, 0.1), frame_paint=(0.7, 0.12, 0.1))
def build(): return build_parts(C)
