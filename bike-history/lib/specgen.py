"""Writes epNN/spec.py files for the generic pipeline from compact Python (used for episodes 10 onward)."""
EXL_M = [('front_wheel', 'FRONT WHEEL'), ('handlebar', 'HANDLEBAR'), ('tank', 'TANK'), ('engine', 'ENGINE'), ('frame', 'FRAME'),
         ('rear_wheel', 'REAR WHEEL'), ('saddle', 'SEAT'), ('exhaust', 'EXHAUST')]
def bg(desc):
    return (f'Wide photograph, photorealistic, eye level, 50mm lens. {desc}, soft morning light from the left, light haze. The road fills the lower third of the picture.',
            f'Tall vertical photograph, photorealistic, eye level, 35mm lens. {desc}, soft morning light, bright sky at the top. The road fills the lower half of the picture.')
def write(path, ep, model, wb, hook_big, hook_line, title, tsize, close, exl, ride_title, nb, ns, rpm, band, lines, scene, tb, tn,
          presets=None, z=0.55, ride_z=0.88):
    order = [k for k, _ in close]; close_d = {k: v for k, v in close}; cover, thumb = bg(scene)
    s = f'"""Episode {ep}: spec for lib/make_episode.sh, written by lib/specgen.py (facts in facts.md)."""\nimport shotkit\n'
    s += f"EP, MODEL, WB = {ep}, {model!r}, {wb}\nHOOK_BIG, HOOK_LINE = {hook_big!r}, {hook_line!r}\nTITLE, TITLE_SIZE = {title!r}, {tsize}\n"
    s += f"CLOSE_ORDER = {order!r}\nCLOSE = {close_d!r}\nEXL = {exl!r}\nRIDE_TITLE = {ride_title!r}\nNEXT_BIG, NEXT_SMALL = {nb!r}, {ns!r}\n"
    s += f"ENGINE_RPM, ROAD_BAND = {rpm!r}, {band!r}\nLINES = [\n" + ''.join(f"    {l!r},\n" for l in lines) + "]\n"
    s += f"def shots(ease, out): return shotkit.standard(ease, out, CLOSE_ORDER, z={z}, presets={(presets or {})!r}, ride_z={ride_z})\n"
    s += f"COVER_PROMPT = {cover!r}\nTHUMB_PROMPT = {thumb!r}\nTHUMB_BIG, THUMB_NAME = {tb!r}, {tn!r}\n"
    open(path, 'w').write(s)
