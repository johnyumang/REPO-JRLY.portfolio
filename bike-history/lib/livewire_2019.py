"""livewire_2019: a config of the generic builder (lib/moto.py). Sizes follow the episode facts where stated, else guesses."""
from moto import build_parts
C = dict(wb=1.49, rf=0.31, rr=0.32, tyre=0.06, engine='electric', fork='tele', rear='mono', drive='belt', brake='twin_disc', spokes=0, cast_arms=5, fairing=None, bars='wide', tank_len=0.42, seat_z=0.78, head_z=0.95, paint=(0.85, 0.35, 0.05), frame_paint=(0.12, 0.12, 0.13), engine_col=(0.55, 0.55, 0.57), seat_len=0.42)
def build(): return build_parts(C)
