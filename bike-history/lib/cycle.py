"""Generic parametric bicycle (mountain bike, track monocoque, e-bike) built from named parts, driven by a config dict.
Same interface as draisine.build(). Keys: wheel_r, tyre, wb, frame 'diamond'|'monocoque', bars 'flat'|'drop'|'aero',
brakes 'cantilever'|'disc'|None, gears (cassette sprockets), wheels 'spoked'|'disc', ebike True (mid motor, down-tube
battery, display), susp_fork True, paint, frame_paint. Units: metres; X forward, Y left, Z up."""
import bpy, math
from mathutils import Vector

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

def build_parts(C):
    M = dict(wood=_mat('wood', (0.45, 0.24, 0.10), 0.55, wood=True),
             iron=_mat('iron', (0.07, 0.07, 0.08), 0.4, 0.9),
             paint=_mat('paint', C.get('paint', (0.05, 0.05, 0.06)), 0.28, 0.5),
             frame_paint=_mat('frame_paint', C.get('frame_paint', C.get('paint', (0.05, 0.05, 0.06))), 0.35, 0.5),
             chrome=_mat('chrome', (0.8, 0.8, 0.8), 0.15, 1.0),
             engine=_mat('engine', C.get('engine_col', (0.45, 0.45, 0.44)), 0.5, 0.8),
             black=_mat('black', (0.03, 0.03, 0.035), 0.45, 0.2),
             glass=_mat('glass', (0.6, 0.7, 0.75), 0.05, 0.0),
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

    g = lambda k, d=None: C.get(k, d)
    R, TY, WB = g('wheel_r', 0.335), g('tyre', 0.027), g('wb', 1.08)
    XF, XR = WB / 2 + 0.03, -WB / 2 + 0.03
    BB = (0.0, 0, g('bb_z', 0.30)); HT = (XF - 0.17, 0, g('head_z', 0.92)); ST = (-0.17, 0, g('seat_z', 0.88))
    root = part('bike', (0, 0, 0)); P = {}
    def wheel(name, x, parent):
        w = part(name, (x, 0, R), parent)
        ring(name + '_tyre', R - TY, TY, (x, 0, R), w, 'rubber', 1.0)
        ring(name + '_rim', R - 2 * TY, 0.010, (x, 0, R), w, 'black', 1.6)
        rod(name + '_hub', (x, -0.05, R), (x, 0.05, R), 0.022, w, 'engine')
        if g('wheels', 'spoked') == 'disc':
            rod(name + '_disc', (x, -0.012, R), (x, 0.012, R), R - 2 * TY, w, 'black')
        else:
            for i in range(32):
                a = i * 2 * math.pi / 32; c, s_ = math.cos(a), math.sin(a); y = 0.035 if i % 2 else -0.035
                rod(f'{name}_spoke{i}', (x + 0.02 * c, y, R + 0.02 * s_), (x + (R - 2 * TY) * c, 0, R + (R - 2 * TY) * s_), 0.0018, w, 'chrome')
        return w
    P['rear_wheel'] = rw = wheel('rear_wheel', XR, root)
    steer = part('steer', (XF, 0, 0), root)
    P['front_wheel'] = fw = wheel('front_wheel', XF, steer)
    f = P['frame'] = part('frame', (0, 0, 0.6), root)
    if g('frame', 'diamond') == 'diamond':
        rod('head_tube', (HT[0] + 0.03, 0, HT[2] - 0.15), (HT[0], 0, HT[2] + 0.02), 0.020, f, 'frame_paint')
        rod('top_tube', (HT[0], 0, HT[2] - 0.02), ST, 0.016, f, 'frame_paint')
        rod('down_tube', (HT[0] + 0.02, 0, HT[2] - 0.12), BB, 0.022 if g('ebike') else 0.019, f, 'frame_paint')
        rod('seat_tube', BB, (ST[0] - 0.01, 0, ST[2] + 0.05), 0.016, f, 'frame_paint')
        for s, sn in ((1, 'L'), (-1, 'R')):
            rod('chain_stay_' + sn, (BB[0], s * 0.03, BB[2]), (XR, s * 0.065, R), 0.010, f, 'frame_paint')
            rod('seat_stay_' + sn, (ST[0], s * 0.015, ST[2] - 0.03), (XR, s * 0.065, R), 0.009, f, 'frame_paint')
    else:                                          # carbon monocoque: one aerofoil shell from head to bottom bracket and saddle
        def shell(nm, loc, sc_, pitch):
            bpy.ops.mesh.primitive_uv_sphere_add(segments=40, ring_count=20, location=loc); o = bpy.context.object
            o.scale = sc_; o.rotation_euler = (0, math.radians(pitch), 0)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True); return _fin(o, nm, f, 'frame_paint')
        shell('mono_front', ((HT[0] + BB[0]) / 2, 0, (HT[2] + BB[2]) / 2 + 0.04), (0.36, 0.022, 0.07), 52)
        shell('mono_seat', ((BB[0] + ST[0]) / 2, 0, (BB[2] + ST[2]) / 2), (0.32, 0.022, 0.065), -78)
        shell('mono_top', ((HT[0] + ST[0]) / 2, 0, (HT[2] + ST[2]) / 2 - 0.02), (0.36, 0.02, 0.05), 4)
        shell('mono_rear', ((BB[0] + XR) / 2, 0.035, (BB[2] + R) / 2 + 0.02), (0.30, 0.016, 0.04), 8)
    fk = P['fork'] = part('fork', ((XF + HT[0]) / 2, 0, 0.6), steer)
    for s, sn in ((1, 'L'), (-1, 'R')) if g('frame', 'diamond') == 'diamond' else ((1, 'L'),):
        if g('susp_fork'):
            rod('fork_lower_' + sn, (XF, s * 0.055, R), (XF - 0.10, s * 0.055, R + 0.28), 0.020, fk, 'black')
            rod('fork_upper_' + sn, (XF - 0.08, s * 0.055, R + 0.22), (HT[0] + 0.03, s * 0.055, HT[2] - 0.15), 0.016, fk, 'chrome')
        else:
            rod('fork_blade_' + sn, (XF, s * 0.05, R), (HT[0] + 0.03, s * 0.05, HT[2] - 0.15), 0.012, fk, 'frame_paint')
    rod('fork_crown', (HT[0] + 0.03, -0.055, HT[2] - 0.15), (HT[0] + 0.03, 0.055, HT[2] - 0.15), 0.015, fk, 'frame_paint')
    hb = P['handlebar'] = part('handlebar', (HT[0] - 0.05, 0, HT[2] + 0.08), steer)
    rod('stem', (HT[0], 0, HT[2] + 0.02), (HT[0] - 0.08, 0, HT[2] + 0.08), 0.013, hb, 'black')
    bars = g('bars', 'flat')
    if bars == 'flat':
        rod('bar', (HT[0] - 0.08, -0.32, HT[2] + 0.09), (HT[0] - 0.08, 0.32, HT[2] + 0.09), 0.011, hb, 'black')
        for s in (1, -1): rod('grip', (HT[0] - 0.08, s * 0.24, HT[2] + 0.09), (HT[0] - 0.08, s * 0.33, HT[2] + 0.09), 0.016, hb, 'rubber')
    elif bars == 'aero':
        for s in (1, -1): tube('bar', [(HT[0] - 0.08, 0, HT[2] + 0.08), (HT[0] - 0.02, s * 0.12, HT[2] + 0.06), (HT[0] + 0.18, s * 0.06, HT[2] + 0.10)], 0.011, hb, 'black')
    else:
        for s in (1, -1): tube('bar', [(HT[0] - 0.08, 0, HT[2] + 0.08), (HT[0] - 0.06, s * 0.20, HT[2] + 0.08), (HT[0] + 0.04, s * 0.21, HT[2] + 0.02), (HT[0] - 0.02, s * 0.21, HT[2] - 0.06)], 0.011, hb, 'black')
    if g('ebike'): box('display', (0.06, 0.08, 0.02), (HT[0] - 0.08, 0.10, HT[2] + 0.12), hb, 'glass', 0.005)
    br = P['brakes'] = part('brakes', (XF, 0.06, R), fw)
    if g('brakes') == 'cantilever':
        for s in (1, -1): rod('canti', (XF - 0.06, s * 0.05, 2 * R - 0.05), (XF - 0.10, s * 0.09, 2 * R - 0.10), 0.008, br, 'chrome')
    elif g('brakes') == 'disc':
        ring('disc_rotor', 0.08, 0.004, (XF, 0.06, R), br, 'chrome', 0.3); box('caliper', (0.05, 0.03, 0.04), (XF - 0.06, 0.07, R + 0.05), br, 'black', 0.008)
        ring('rear_rotor', 0.08, 0.004, (XR, 0.07, R), rw, 'chrome', 0.3)
    dv = P['drive'] = part('drive', ((BB[0] + XR) / 2, -0.06, R), root)
    ring('chainring', 0.10, 0.006, (BB[0], -0.065, BB[2]), dv, 'chrome')
    for j in range(g('gears', 1)): ring(f'cog{j}', 0.03 + 0.008 * j, 0.004, (XR, -0.05 - 0.005 * j, R), dv, 'chrome')
    if g('gears', 1) > 1: box('derailleur', (0.04, 0.02, 0.07), (XR + 0.02, -0.075, R - 0.07), dv, 'black', 0.005)
    d = math.hypot(BB[0] - XR, BB[2] - R); ang = math.atan2(BB[2] - R, BB[0] - XR); off = math.asin((0.10 - 0.045) / d)
    for sgn, nm in ((1, 'top'), (-1, 'bottom')):
        a = ang + sgn * (math.pi / 2 - off)
        rod('chain_' + nm, (XR + 0.045 * math.cos(a), -0.065, R + 0.045 * math.sin(a)), (BB[0] + 0.10 * math.cos(a), -0.065, BB[2] + 0.10 * math.sin(a)), 0.004, dv, 'black')
    pd = P['pedals'] = part('pedals', BB, root)
    for s, sn, ph in ((1, 'L', 0.0), (-1, 'R', math.pi)):
        ex, ez = BB[0] + 0.17 * math.cos(ph), BB[2] + 0.17 * math.sin(ph)
        rod('crank_' + sn, (BB[0], s * 0.075, BB[2]), (ex, s * 0.075, ez), 0.010, pd, 'black')
        box('pedal_' + sn, (0.06, 0.09, 0.02), (ex, s * 0.125, ez), pd, 'black', 0.004)
    if g('ebike'):
        mo = P['motor'] = part('motor', BB, root)
        rod('motor_unit', (BB[0] + 0.04, -0.06, BB[2] + 0.02), (BB[0] + 0.04, 0.06, BB[2] + 0.02), 0.075, mo, 'black')
        bt = P['battery'] = part('battery', ((HT[0] + BB[0]) / 2, 0, (HT[2] + BB[2]) / 2), root)
        dvec = Vector(BB) - Vector((HT[0] + 0.02, 0, HT[2] - 0.12)); mid = Vector((HT[0] + 0.02, 0, HT[2] - 0.12)) + dvec * 0.55
        bpy.ops.mesh.primitive_cube_add(size=1, location=tuple(mid + Vector((0, 0, 0.045)))); o = bpy.context.object
        o.scale = (dvec.length * 0.62, 0.07, 0.06); o.rotation_euler = (0, -math.atan2(dvec.z, dvec.x) + math.pi, 0)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True); _fin(o, 'battery_pack', bt, 'paint', False)
    sd = P['saddle'] = part('saddle', ST, root)
    rod('seat_post', (ST[0] - 0.01, 0, ST[2]), (ST[0] - 0.03, 0, ST[2] + 0.12), 0.013, sd, 'chrome')
    box('saddle_seat', (0.26, 0.13, 0.04), (ST[0] - 0.05, 0, ST[2] + 0.14), sd, 'black', 0.02)
    def anchor(name, loc, p):
        e = bpy.data.objects.new('A_' + name, None); col.objects.link(e)
        e.location = Vector(loc) - origin[p.name]; e.parent = p; return e
    A = dict(frame=anchor('frame', ((HT[0] + BB[0]) / 2, 0.03, (HT[2] + BB[2]) / 2 + 0.05), f), front_wheel=anchor('front_wheel', (XF, 0, R), fw),
             rear_wheel=anchor('rear_wheel', (XR, 0, R), rw), tyre=anchor('tyre', (XF + (R - TY) * 0.71, 0.0, R - (R - TY) * 0.71), fw),
             fork=anchor('fork', (XF - 0.05, 0.05, R + 0.15), fk), handlebar=anchor('handlebar', (HT[0] - 0.08, 0.28, HT[2] + 0.09), hb),
             brakes=anchor('brakes', (XF - 0.06, 0.07, R + 0.05) if g('brakes') == 'disc' else (XF - 0.08, 0.06, 2 * R - 0.07), br),
             drive=anchor('drive', (XR, -0.06, R + 0.03), dv), pedals=anchor('pedals', (BB[0] + 0.17, 0.125, BB[2]), pd),
             saddle=anchor('saddle', (ST[0] - 0.05, 0, ST[2] + 0.16), sd),
             foot_l=anchor('foot_l', (BB[0] + 0.17, 0.125, BB[2]), pd), foot_r=anchor('foot_r', (BB[0] - 0.17, -0.125, BB[2]), pd),
             hands=anchor('hands', (HT[0] - 0.10, 0, HT[2] + 0.10), hb), seat=anchor('seat', (ST[0] - 0.07, 0, ST[2] + 0.17), sd),
             ground_r=anchor('ground_r', (XR, 0, 0), root), ground_f=anchor('ground_f', (XF, 0, 0), root))
    if g('ebike'):
        A['motor'] = anchor('motor', (BB[0] + 0.04, 0.07, BB[2] + 0.02), P['motor']); A['battery'] = anchor('battery', tuple(mid + Vector((0, 0.07, 0.05))), P['battery'])
        A['display'] = anchor('display', (HT[0] - 0.08, 0.12, HT[2] + 0.13), hb)
    EXO = dict(front_wheel=(0.40, 0, 0), fork=(0.20, 0, 0.30), handlebar=(0.05, 0, 0.40), brakes=(0.1, 0.30, 0), saddle=(0, 0, 0.35),
               drive=(0, -0.35, 0), pedals=(0, 0.30, -0.15), rear_wheel=(-0.40, 0, 0), frame=(0, 0, 0), motor=(0, 0.35, -0.20), battery=(0.15, 0.35, 0.20))
    base = {k_: v_.location.copy() for k_, v_ in P.items()}
    def explode(k_):
        for n_, o_ in P.items(): o_.location = base[n_] + Vector(EXO.get(n_, (0, 0, 0))) * k_
    return dict(root=root, steer=steer, parts=P, anchors=A, explode=explode, wheelbase=XF - XR)
