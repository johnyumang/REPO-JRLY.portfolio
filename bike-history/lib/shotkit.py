"""Ready-made camera moves for the generic pipeline. In render, `rot` turns the bike; the camera looks from world -Y,
so rot 0 shows the bike's right side (-Y) and rot 180 its left side (+Y). Chains and front discs sit on the left in
lib/moto.py, exhausts and shafts on the right.
usage in a spec:  def shots(ease, out): return shotkit.standard(ease, out, ['engine', 'drive', ...], z=0.55, big=True)"""
import math
PRESET = {   # name: (rot start, el, dist, target, extra)
    'engine': (-22, 10, 2.6, (0.02, 0, 0.48), {}), 'tank': (-30, 26, 2.5, (0.15, 0, 0.85), {}),
    'drive': (165, 10, 2.7, (-0.35, 0, 0.40), {'spin_r': -240}), 'shaft': (-20, 10, 2.7, (-0.35, 0, 0.40), {'spin_r': -240}),
    'fork': (-40, 10, 2.5, (0.55, 0, 0.55), {}), 'brakes': (160, 8, 2.2, (0.62, 0, 0.35), {'spin_f': -60}),
    'rear_suspension': (-150, 12, 2.5, (-0.45, 0, 0.50), {}), 'exhaust': (-25, 8, 2.7, (-0.30, 0, 0.35), {}),
    'frame': (-35, 14, 3.4, (0.10, 0, 0.65), {}), 'fairing': (-32, 8, 3.1, (0.35, 0, 0.70), {}),
    'saddle': (-25, 14, 3.0, (-0.25, 0, 0.75), {}), 'headlight': (-60, 8, 2.1, (0.60, 0, 0.85), {}),
    'body': (-150, 10, 3.0, (-0.30, 0, 0.50), {}), 'handlebar': (-35, 30, 2.3, (0.45, 0, 0.95), {}),
    'front_wheel': (-10, 4, 2.6, (0.60, 0, 0.35), {'spin_f': -120}), 'rear_wheel': (-170, 4, 2.6, (-0.62, 0, 0.35), {'spin_r': -120}),
}
def standard(ease, out, close, z=0.55, big=True, presets=None, ride_z=0.88):
    P = dict(PRESET, **(presets or {})); k = 1.12 if big else 1.0
    def hook(u): return dict(rot=-150 + 190 * out(u), el=10, dist=k * (5.8 - 0.8 * out(u)), target=(0, 0, z), spin_f=-90 * u, spin_r=-90 * u)
    def turn(u): return dict(rot=40 + 360 * u, el=6 + 20 * math.sin(math.pi * u) ** 2, dist=k * 5.0, target=(0, 0, z))
    def explode(u): return dict(rot=28 + 22 * u, el=16, dist=k * 6.2, target=(0, 0, z + 0.07), explode=ease(min(1, u / 0.3)))
    def ride(u): return dict(rot=0, el=2.5, dist=k * 5.8, target=(0, 0, ride_z), spin_f=-360 * u, spin_r=-360 * u)
    def close_shot(name):
        r0, el, d, tg, ex = P[name]
        def f(u):
            p = dict(rot=r0 + 14 * u, el=el, dist=d - 0.25 * ease(u), target=tg)
            for kk, vv in ex.items(): p[kk] = vv * u
            return p
        return f
    return [('hook', 72, hook), ('turn', 168, turn)] + [(n, 144, close_shot(n)) for n in close] + [('explode', 192, explode), ('ride', 16, ride)]
