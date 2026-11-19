"""Parametric first Harley-Davidson (Milwaukee, 1903-1905: single-cylinder engine in a loop frame, leather belt drive,
bicycle pedals) built from named parts. Units: metres. X forward, Y left, Z up, ground at z=0.
Same interface as draisine.build(). Sizes are typical of the type; see ep04/facts.md for what is checked."""
import bpy, math
from mathutils import Vector

R = 0.355                    # 28 in wheels with tyres
XF, XR = 0.66, -0.64

def _mat(name, col, rough=0.6, metal=0.0, wood=False):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if wood:
        tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping')
        mp.inputs['Scale'].default_value = (3, 40, 40)
        nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 6
        rp = nt.nodes.new('ShaderNodeValToRGB')
        rp.color_ramp.elements[0].position = 0.35; rp.color_ramp.elements[1].position = 0.7
        rp.color_ramp.elements[0].color = (*[c * 0.55 for c in col], 1); rp.color_ramp.elements[1].color = (*col, 1)
        nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], nz.inputs['Vector'])
        nt.links.new(nz.outputs['Fac'], rp.inputs['Fac']); nt.links.new(rp.outputs['Color'], b.inputs['Base Color'])
    return m

def build():
    M = dict(wood=_mat('wood', (0.45, 0.24, 0.10), 0.55, wood=True),
             iron=_mat('iron', (0.07, 0.07, 0.08), 0.4, 0.9),
             paint=_mat('paint', (0.05, 0.05, 0.06), 0.30, 0.6),      # black enamel on the steel tube
             rubber=_mat('rubber', (0.03, 0.03, 0.03), 0.8),
             alu=_mat('alu', (0.42, 0.41, 0.38), 0.62, 0.8),     # cast aluminium, satin
             belt=_mat('belt', (0.30, 0.17, 0.08), 0.75),
             nickel=_mat('nickel', (0.75, 0.75, 0.72), 0.25, 1.0),
             brass=_mat('brass', (0.75, 0.55, 0.22), 0.3, 1.0),
             leather=_mat('leather', (0.16, 0.07, 0.04), 0.7),
             cord=_mat('cord', (0.75, 0.68, 0.50), 0.9))
    col = bpy.context.scene.collection; origin = {}
    def part(name, loc, parent=None):
        e = bpy.data.objects.new(name, None); col.objects.link(e)
        po = origin[parent.name] if parent else Vector()
        e.location = Vector(loc) - po; e.parent = parent; origin[name] = Vector(loc); return e
    def _fin(o, name, p, m, smooth=True):
        o.name = name; o.location = Vector(o.location) - origin[p.name]; o.parent = p
        o.data.materials.append(M[m])
        for poly in o.data.polygons: poly.use_smooth = smooth
        return o
    def box(name, size, loc, p, m, bevel=0.006):
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.object
        o.scale = size; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        if bevel: md = o.modifiers.new('bv', 'BEVEL'); md.width = bevel; md.segments = 2
        return _fin(o, name, p, m, False)
    def rod(name, a, b, r, p, m):
        a, b = Vector(a), Vector(b); d = b - a
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d.length, vertices=20, location=(a + b) / 2)
        o = bpy.context.object; o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
        return _fin(o, name, p, m)
    def ring(name, major, minor, loc, p, m, flat=1.0):
        bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=72, minor_segments=12,
                                         location=loc, rotation=(math.pi / 2, 0, 0))
        o = bpy.context.object; o.scale = (1, 1, flat); return _fin(o, name, p, m)
    def tube(name, pts, r, p, m):
        cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 4
        sp = cu.splines.new('NURBS'); sp.points.add(len(pts) - 1); sp.use_endpoint_u = True; sp.order_u = 3
        for i, q in enumerate(pts): sp.points[i].co = (*q, 1)
        o = bpy.data.objects.new(name, cu); col.objects.link(o)
        bpy.context.view_layer.objects.active = o; o.select_set(True); bpy.ops.object.convert(target='MESH'); o.select_set(False)
        return _fin(o, name, p, m)

    root = part('bike', (0, 0, 0)); P = {}
    f = P['frame'] = part('frame', (0, 0, 0.6), root)
    HT, HB = (0.47, 0, 0.98), (0.48, 0, 0.86)          # head tube top and bottom
    rod('head_tube', HB, HT, 0.022, f, 'paint')
    rod('top_tube', (0.47, 0, 0.95), (-0.13, 0, 0.92), 0.017, f, 'paint')
    tube('loop', [HB, (0.40, 0, 0.55), (0.30, 0, 0.24), (0.12, 0, 0.17), (-0.10, 0, 0.20), (-0.14, 0, 0.40), (-0.13, 0, 0.92)], 0.018, f, 'paint')
    for s, sn in ((1, 'L'), (-1, 'R')):
        rod('chain_stay_' + sn, (-0.12, s * 0.02, 0.24), (XR, s * 0.06, R), 0.011, f, 'paint')
        rod('seat_stay_' + sn, (-0.13, s * 0.02, 0.88), (XR, s * 0.06, R), 0.010, f, 'paint')
    def wheel(name, x, parent):
        w = part(name, (x, 0, R), parent)
        ring(name + '_rim', R - 0.035, 0.010, (x, 0, R), w, 'paint', 1.3)
        ring(name + '_tyre', R - 0.026, 0.028, (x, 0, R), w, 'rubber', 1.0)
        rod(name + '_hub', (x, -0.055, R), (x, 0.055, R), 0.028, w, 'nickel')
        for i in range(36):
            a = i * 2 * math.pi / 36; c, s_ = math.cos(a), math.sin(a); y = 0.045 if i % 2 else -0.045
            rod(f'{name}_spoke{i}', (x + 0.024 * c, y, R + 0.024 * s_), (x + (R - 0.045) * c, 0, R + (R - 0.045) * s_), 0.0022, w, 'nickel')
        return w
    P['rear_wheel'] = rw = wheel('rear_wheel', XR, root)
    steer = part('steer', (XF, 0, 0), root)
    P['front_wheel'] = wheel('front_wheel', XF, steer)
    fk = P['fork'] = part('fork', (0.55, 0, 0.8), steer)
    rod('fork_crown', (0.49, -0.06, 0.85), (0.49, 0.06, 0.85), 0.014, fk, 'paint')
    for s, sn in ((1, 'L'), (-1, 'R')):
        rod('fork_blade_' + sn, (XF, s * 0.06, R), (0.49, s * 0.06, 0.85), 0.013, fk, 'paint')
    hb = P['handlebar'] = part('handlebar', (0.45, 0, 1.03), steer)
    rod('stem', (0.47, 0, 0.98), (0.47, 0, 1.05), 0.013, hb, 'nickel')
    for s in (1, -1):
        tube('bar', [(0.47, 0, 1.05), (0.45, s * 0.18, 1.06), (0.32, s * 0.28, 1.04)], 0.011, hb, 'nickel')
        rod('grip', (0.32, s * 0.28, 1.04), (0.24, s * 0.29, 1.03), 0.017, hb, 'rubber')
    # the engine: crankcase, finned cylinder, head; the flywheels sit inside the crankcase
    en = P['engine'] = part('engine', (0.12, 0, 0.45), root)
    CX, CZ = 0.12, 0.34
    rod('crankcase', (CX, -0.07, CZ), (CX, 0.07, CZ), 0.13, en, 'alu')
    rod('cylinder', (CX + 0.01, 0, CZ + 0.10), (CX + 0.03, 0, 0.66), 0.048, en, 'paint')
    for k in range(9):
        z = CZ + 0.14 + k * 0.026; ring(f'fin{k}', 0.044, 0.008, (CX + 0.012 + 0.002 * k, 0, z), en, 'paint').rotation_euler = (0, 0, 0)
    rod('cyl_head', (CX + 0.03, 0, 0.66), (CX + 0.035, 0, 0.71), 0.055, en, 'alu')
    rod('spark_plug', (CX + 0.035, 0, 0.71), (CX + 0.05, 0, 0.76), 0.008, en, 'nickel')
    rod('carburettor', (CX - 0.08, 0.0, 0.58), (CX - 0.02, 0, 0.60), 0.022, en, 'nickel')
    rod('exhaust', (CX + 0.06, 0, 0.62), (0.33, 0, 0.30), 0.016, en, 'nickel')
    rod('muffler', (0.25, 0, 0.22), (0.42, 0, 0.30), 0.045, en, 'paint')
    tk = P['tank'] = part('tank', (0.17, 0, 0.85), root)
    box('tank_body', (0.44, 0.12, 0.13), (0.17, 0, 0.855), tk, 'paint', 0.03)
    rod('filler_cap', (0.30, 0, 0.92), (0.30, 0, 0.945), 0.018, tk, 'nickel')
    # drive: leather belt from the engine pulley to a big pulley on the rear wheel (right side)
    dv = P['belt'] = part('belt', (-0.2, -0.10, 0.35), root)
    EP, RP = (CX, -0.10, CZ), (XR, -0.085, R)
    re_, rr_ = 0.05, 0.22
    rod('engine_pulley', (CX, -0.075, CZ), (CX, -0.12, CZ), re_, dv, 'nickel')
    ring('rear_pulley', rr_, 0.010, (XR, -0.085, R), dv, 'nickel')
    d = math.hypot(EP[0] - RP[0], EP[2] - RP[2]); ang = math.atan2(EP[2] - RP[2], EP[0] - RP[0]); off = math.asin((rr_ - re_) / d)
    for sgn, nm in ((1, 'top'), (-1, 'bottom')):
        a = ang + sgn * (math.pi / 2 - off)
        p1 = (RP[0] + rr_ * math.cos(a), -0.095, RP[2] + rr_ * math.sin(a)); p2 = (EP[0] + re_ * math.cos(a), -0.095, EP[2] + re_ * math.sin(a))
        box('belt_' + nm, (0.01, 0.024, 0.006), (0, 0, 0), dv, 'belt', 0).scale = (1, 1, 1)
        bpy.data.objects.remove(bpy.data.objects['belt_' + nm])
        rod('belt_' + nm, p1, p2, 0.008, dv, 'belt')
    # pedals: bicycle crank and a chain to the rear wheel (left side), for starting and for hills
    pd = P['pedals'] = part('pedals', (-0.12, 0, 0.24), root)
    BB = (-0.12, 0, 0.24)
    rod('bottom_bracket', (BB[0], -0.05, BB[2]), (BB[0], 0.05, BB[2]), 0.022, pd, 'nickel')
    ring('chainring', 0.08, 0.006, (BB[0], 0.06, BB[2]), pd, 'nickel')
    for s, sn, ph in ((1, 'L', 0.0), (-1, 'R', math.pi)):
        ex, ez = BB[0] + 0.16 * math.cos(ph), BB[2] + 0.16 * math.sin(ph)
        rod('crank_' + sn, (BB[0], s * 0.07, BB[2]), (ex, s * 0.07, ez), 0.009, pd, 'nickel')
        box('pedal_' + sn, (0.05, 0.08, 0.025), (ex, s * 0.12, ez), pd, 'rubber', 0.005)
    rod('chain_top', (BB[0], 0.062, BB[2] + 0.08), (XR, 0.062, R + 0.035), 0.004, pd, 'iron')
    rod('chain_bot', (BB[0], 0.062, BB[2] - 0.08), (XR, 0.062, R - 0.035), 0.004, pd, 'iron')
    sd = P['saddle'] = part('saddle', (-0.16, 0, 0.98), root)
    rod('seat_post', (-0.13, 0, 0.90), (-0.15, 0, 0.98), 0.012, sd, 'nickel')
    box('saddle_seat', (0.26, 0.19, 0.06), (-0.17, 0, 1.0), sd, 'leather', 0.022)
    for s in (1, -1): ring('saddle_spring', 0.022, 0.004, (-0.26, s * 0.06, 0.955), sd, 'nickel')

    def anchor(name, loc, p):
        e = bpy.data.objects.new('A_' + name, None); col.objects.link(e)
        e.location = Vector(loc) - origin[p.name]; e.parent = p; return e
    A = dict(engine=anchor('engine', (CX + 0.02, 0.05, 0.52), en), tank=anchor('tank', (0.17, 0.06, 0.86), tk),
             belt=anchor('belt', ((CX + XR) / 2, -0.10, (CZ + R) / 2 + 0.12), dv), pedals=anchor('pedals', (BB[0] + 0.16, 0.12, BB[2]), pd),
             saddle=anchor('saddle', (-0.17, 0, 1.03), sd), handlebar=anchor('handlebar', (0.32, 0.28, 1.04), hb),
             fork=anchor('fork', (0.58, 0.06, 0.60), fk), front_wheel=anchor('front_wheel', (XF, 0, R), P['front_wheel']),
             rear_wheel=anchor('rear_wheel', (XR, 0, R), rw), frame=anchor('frame', (0.30, 0, 0.24), f),
             foot_l=anchor('foot_l', (BB[0] + 0.16, 0.12, BB[2]), pd), foot_r=anchor('foot_r', (BB[0] - 0.16, -0.12, BB[2]), pd),
             hands=anchor('hands', (0.28, 0, 1.04), hb), seat=anchor('seat', (-0.18, 0, 1.03), sd),
             ground_r=anchor('ground_r', (XR, 0, 0), root), ground_f=anchor('ground_f', (XF, 0, 0), root))
    EX = dict(front_wheel=(0.45, 0, 0), fork=(0.18, 0, 0.30), handlebar=(0.05, 0, 0.45), tank=(0, 0, 0.45), engine=(0, 0.45, -0.05),
              belt=(0, -0.40, 0), pedals=(0, 0.30, -0.20), saddle=(-0.05, 0, 0.40), rear_wheel=(-0.45, 0, 0), frame=(0, 0, 0))
    base = {k: v.location.copy() for k, v in P.items()}
    def explode(k):
        for n, o in P.items(): o.location = base[n] + Vector(EX[n]) * k
    return dict(root=root, steer=steer, parts=P, anchors=A, explode=explode, wheelbase=XF - XR)
