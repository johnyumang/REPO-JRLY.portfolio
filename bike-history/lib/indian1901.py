"""Parametric Indian motorized bicycle (Hendee and Hedstrom, Springfield, 1901) built from named parts.
Units: metres. X forward, Y left, Z up, ground at z=0. Same interface as draisine.build().
A diamond frame whose seat tube is the single-cylinder engine, Hedstrom's carburettor, bicycle pedals, a tank over the
rear wheel and chain drive. Sizes, colour and the tank shape are guesses (no 1901 sizes found). See ep09/facts.md."""
import bpy, math
from mathutils import Vector

R = 0.37                     # about 29 in wheels on air-filled tyres (sizes are typical, not checked)
XF, XR = 0.62, -0.55
BB = (0.04, 0, 0.28)         # bottom bracket
CR = 0.16

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
             rubber=_mat('rubber', (0.02, 0.02, 0.02), 0.8),
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
    HT, HB, ST = (0.50, 0, 0.98), (0.53, 0, 0.84), (-0.08, 0, 0.92)
    rod('head_tube', HB, (0.51, 0, 1.0), 0.020, f, 'paint')
    rod('top_tube', (0.51, 0, 0.96), ST, 0.016, f, 'paint')
    rod('down_tube', (0.53, 0, 0.86), BB, 0.019, f, 'paint')
    en = P['engine'] = part('engine', ((BB[0] + ST[0]) / 2, 0, 0.55), root)    # the engine is the seat tube
    d_ = (Vector(ST) - Vector(BB)).normalized()
    p0 = Vector(BB) + d_ * 0.12; p1 = Vector(BB) + d_ * 0.42
    rod('crankcase', (BB[0] - 0.02, -0.06, BB[2] + 0.10), (BB[0] - 0.02, 0.06, BB[2] + 0.10), 0.09, en, 'nickel')
    rod('cylinder', tuple(p0), tuple(p1), 0.048, en, 'iron')
    for j in range(8): ring(f'fin{j}', 0.05, 0.006, tuple(p0 + d_ * (0.03 + j * 0.035)), en, 'iron').rotation_euler = (0, math.atan2(d_.x, d_.z), 0)
    rod('cyl_head', tuple(p1), tuple(p1 + d_ * 0.05), 0.055, en, 'iron')
    rod('seat_tube_top', tuple(p1 + d_ * 0.05), ST, 0.017, f, 'paint')
    cb = P['carburettor'] = part('carburettor', (BB[0] + 0.1, 0.07, BB[2] + 0.3), root)
    rod('carb_body', (p0.x + 0.10, 0.07, p0.z + 0.10), (p0.x + 0.10, 0.07, p0.z + 0.20), 0.025, cb, 'brass')
    rod('intake', (p0.x + 0.10, 0.07, p0.z + 0.20), tuple(p1 + Vector((0.02, 0.04, -0.02))), 0.009, cb, 'brass')
    tk = P['tank'] = part('tank', (XR + 0.15, 0, R + 0.42), root)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=(XR + 0.15, 0, 2 * R + 0.10)); o = bpy.context.object
    o.scale = (0.26, 0.09, 0.07); bpy.ops.object.transform_apply(location=False, rotation=False, scale=True); _fin(o, 'camelback_tank', tk, 'paint')
    for s, sn in ((1, 'L'), (-1, 'R')):
        rod('chain_stay_' + sn, (BB[0], s * 0.03, BB[2]), (XR, s * 0.055, R), 0.010, f, 'paint')
        rod('seat_stay_' + sn, (ST[0], s * 0.015, ST[2] - 0.02), (XR, s * 0.055, R), 0.009, f, 'paint')
    def wheel(name, x, parent):
        w = part(name, (x, 0, R), parent)
        ring(name + '_rim', R - 0.040, 0.010, (x, 0, R), w, 'nickel', 1.2)
        ring(name + '_tyre', R - 0.020, 0.026, (x, 0, R), w, 'rubber', 1.0)          # fat air-filled cover
        rod(name + '_valve', (x, 0, R + R - 0.045), (x, 0, R + R - 0.085), 0.006, w, 'nickel')
        rod(name + '_hub', (x, -0.05, R), (x, 0.05, R), 0.026, w, 'nickel')
        for i in range(36):
            a = i * 2 * math.pi / 36; c, s_ = math.cos(a), math.sin(a); y = 0.04 if i % 2 else -0.04
            rod(f'{name}_spoke{i}', (x + 0.022 * c, y, R + 0.022 * s_), (x + (R - 0.045) * c, 0, R + (R - 0.045) * s_), 0.0024, w, 'nickel')
        return w
    P['rear_wheel'] = rw = wheel('rear_wheel', XR, root)
    steer = part('steer', (XF, 0, 0), root)
    P['front_wheel'] = wheel('front_wheel', XF, steer)
    fk = P['fork'] = part('fork', (0.58, 0, 0.7), steer)
    rod('fork_crown', (0.53, -0.06, 0.88), (0.53, 0.06, 0.88), 0.013, fk, 'paint')
    for s, sn in ((1, 'L'), (-1, 'R')):
        rod('fork_blade_' + sn, (XF, s * 0.06, R), (0.53, s * 0.06, 0.88), 0.012, fk, 'paint')
    hb = P['handlebar'] = part('handlebar', (0.47, 0, 1.10), steer)
    rod('stem', (0.51, 0, 1.0), (0.50, 0, 1.12), 0.012, hb, 'nickel')
    for s in (1, -1):
        tube('bar', [(0.50, 0, 1.12), (0.47, s * 0.16, 1.12), (0.36, s * 0.27, 1.08)], 0.010, hb, 'nickel')
        rod('grip', (0.36, s * 0.27, 1.08), (0.28, s * 0.28, 1.07), 0.017, hb, 'wood')
    # drive: chainring at the pedals, a chain to a small sprocket on the rear hub (right side)
    ch = P['chain'] = part('chain', ((BB[0] + XR) / 2, -0.07, 0.32), root)
    ring('chainring', 0.10, 0.007, (BB[0], -0.065, BB[2]), ch, 'nickel')
    ring('sprocket', 0.045, 0.007, (XR, -0.065, R), ch, 'nickel')
    d = math.hypot(BB[0] - XR, BB[2] - R); ang = math.atan2(BB[2] - R, BB[0] - XR); off = math.asin((0.10 - 0.045) / d)
    for sgn, nm in ((1, 'top'), (-1, 'bottom')):
        a = ang + sgn * (math.pi / 2 - off)
        rod('chain_' + nm, (XR + 0.045 * math.cos(a), -0.065, R + 0.045 * math.sin(a)), (BB[0] + 0.10 * math.cos(a), -0.065, BB[2] + 0.10 * math.sin(a)), 0.005, ch, 'iron')
    pd = P['pedals'] = part('pedals', BB, root)
    rod('bottom_bracket', (BB[0], -0.05, BB[2]), (BB[0], 0.05, BB[2]), 0.022, pd, 'nickel')
    for s, sn, ph in ((1, 'L', 0.0), (-1, 'R', math.pi)):
        ex, ez = BB[0] + CR * math.cos(ph), BB[2] + CR * math.sin(ph)
        rod('crank_' + sn, (BB[0], s * 0.075, BB[2]), (ex, s * 0.075, ez), 0.009, pd, 'nickel')
        box('pedal_' + sn, (0.05, 0.08, 0.025), (ex, s * 0.125, ez), pd, 'rubber', 0.005)
    sd = P['saddle'] = part('saddle', (-0.12, 0, 0.98), root)
    rod('seat_post', (-0.10, 0, 0.92), (-0.11, 0, 0.97), 0.011, sd, 'nickel')
    box('saddle_seat', (0.24, 0.17, 0.05), (-0.13, 0, 0.995), sd, 'leather', 0.02)
    for s in (1, -1): ring('saddle_spring', 0.02, 0.004, (-0.21, s * 0.055, 0.955), sd, 'nickel')

    def anchor(name, loc, p):
        e = bpy.data.objects.new('A_' + name, None); col.objects.link(e)
        e.location = Vector(loc) - origin[p.name]; e.parent = p; return e
    A = dict(tyre=anchor('tyre', (XF + (R - 0.02) * 0.71, -0.03, R - (R - 0.02) * 0.71), P['front_wheel']),
             engine=anchor('engine', tuple(p0 + d_ * 0.15 + Vector((0, 0.05, 0))), en), carburettor=anchor('carburettor', (p0.x + 0.10, 0.10, p0.z + 0.15), cb),
             tank=anchor('tank', (XR + 0.15, 0.08, 2 * R + 0.10), tk),
             valve=anchor('valve', (XF, 0, 2 * R - 0.07), P['front_wheel']),
             chain=anchor('chain', ((BB[0] + XR) / 2, -0.065, (BB[2] + R) / 2 + 0.07), ch), pedals=anchor('pedals', (BB[0] + CR, 0.125, BB[2]), pd),
             saddle=anchor('saddle', (-0.13, 0, 1.02), sd), handlebar=anchor('handlebar', (0.36, 0.27, 1.08), hb),
             steering=anchor('steering', (0.52, 0, 0.95), fk), fork=anchor('fork', (0.58, 0.055, 0.62), fk),
             front_wheel=anchor('front_wheel', (XF, 0, R), P['front_wheel']), rear_wheel=anchor('rear_wheel', (XR, 0, R), rw),
             frame=anchor('frame', (0.25, 0, 0.62), f),
             foot_l=anchor('foot_l', (BB[0] + CR, 0.125, BB[2]), pd), foot_r=anchor('foot_r', (BB[0] - CR, -0.125, BB[2]), pd),
             hands=anchor('hands', (0.32, 0, 1.08), hb), seat=anchor('seat', (-0.14, 0, 1.02), sd),
             ground_r=anchor('ground_r', (XR, 0, 0), root), ground_f=anchor('ground_f', (XF, 0, 0), root))
    EX = dict(engine=(0, 0.45, 0.05), carburettor=(0.1, 0.40, 0.25), tank=(-0.1, 0, 0.35), front_wheel=(0.45, 0, 0), fork=(0.18, 0, 0.30), handlebar=(0.05, 0, 0.45), chain=(0, -0.40, 0), pedals=(0, 0.30, -0.15),
              saddle=(-0.05, 0, 0.40), rear_wheel=(-0.45, 0, 0), frame=(0, 0, 0))
    base = {k: v.location.copy() for k, v in P.items()}
    def explode(k):
        for n, o in P.items(): o.location = base[n] + Vector(EX[n]) * k
    return dict(root=root, steer=steer, parts=P, anchors=A, explode=explode, wheelbase=XF - XR)
