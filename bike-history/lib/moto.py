"""Generic parametric motorcycle (and scooter / step-through) built from named parts, driven by a config dict C.
Each episode model is a small file: `from moto import build_parts; def build(): return build_parts(dict(...))`.
Same interface as draisine.build(). Shapes are simplified on purpose: proportions and part layout follow the facts
of each machine, details do not. Units: metres, X forward, Y left, Z up, ground at z=0.

Keys (all optional): wb wheelbase; rf, rr wheel radius incl. tyre; tyre tyre section radius; spokes (0 = cast/disc
wheels); rake degrees; head_z; seat_z; engine 'single'|'vtwin'|'boxer'|'inline4'|'twin'|'v5'|'scooter'|'stepthrough';
cc_scale engine size; fins True/False; fork 'girder'|'tele'|'leading'; rear 'rigid'|'plunger'|'twinshock'|'mono';
brake 'drum'|'disc'|'twin_disc'; drive 'chain'|'shaft'|'belt'; fairing None|'half'|'full'; tank_len; paint, frame_paint,
engine_col colours; seat_len; bars 'flat'|'clipon'|'wide'; exhaust 'low'|'high'|'under'|'twin'; lights True."""
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
    WB, RF, RR, TY = g('wb', 1.40), g('rf', 0.33), g('rr', 0.33), g('tyre', 0.05)
    XF, XR = WB / 2, -WB / 2
    rake = math.radians(g('rake', 27)); HZ = g('head_z', 0.95); SZ = g('seat_z', 0.80)
    HX = XF - (HZ - RF) * math.tan(rake)                       # top of the fork, on the steering axis
    root = part('bike', (0, 0, 0)); P = {}
    body = g('engine', 'inline4') in ('scooter', 'stepthrough')
    # ---------------- wheels
    def wheel(name, x, r, parent):
        w = part(name, (x, 0, r), parent)
        ring(name + '_tyre', r - TY, TY, (x, 0, r), w, 'rubber', 1.0)
        ring(name + '_rim', r - 2 * TY, 0.012, (x, 0, r), w, 'chrome' if g('spokes', 36) else 'black', 1.4)
        rod(name + '_hub', (x, -0.06, r), (x, 0.06, r), 0.045, w, 'engine')
        n = g('spokes', 36)
        if n:
            for i in range(n):
                a = i * 2 * math.pi / n; c, s_ = math.cos(a), math.sin(a); y = 0.05 if i % 2 else -0.05
                rod(f'{name}_spoke{i}', (x + 0.04 * c, y, r + 0.04 * s_), (x + (r - 2 * TY) * c, 0, r + (r - 2 * TY) * s_), 0.0025, w, 'chrome')
        else:
            for i in range(g('cast_arms', 5)):
                a = i * 2 * math.pi / g('cast_arms', 5); c, s_ = math.cos(a), math.sin(a)
                rod(f'{name}_arm{i}', (x + 0.04 * c, 0, r + 0.04 * s_), (x + (r - 2 * TY) * c, 0, r + (r - 2 * TY) * s_), 0.018, w, 'black')
        return w
    P['rear_wheel'] = rw = wheel('rear_wheel', XR, RR, root)
    steer = part('steer', (XF, 0, 0), root)
    P['front_wheel'] = fw = wheel('front_wheel', XF, RF, steer)
    # ---------------- brakes
    br = P['brakes'] = part('brakes', (XF, 0.08, RF), fw)
    if g('brake', 'drum') == 'drum':
        rod('front_drum', (XF, 0.03, RF), (XF, 0.08, RF), RF * 0.38, br, 'engine')
    else:
        for s in ((1,) if g('brake') == 'disc' else (1, -1)):
            ring('disc', RF * 0.52, 0.022, (XF, s * 0.078, RF), br, 'chrome', 0.25)
            for j in range(5): rod('disc_arm', (XF, s * 0.078, RF), (XF + RF * 0.5 * math.cos(j * 1.2566), s * 0.078, RF + RF * 0.5 * math.sin(j * 1.2566)), 0.008, br, 'chrome')
            box('caliper', (0.07, 0.04, 0.05), (XF - RF * 0.45, s * 0.095, RF + RF * 0.25), br, 'black', 0.01)
    # ---------------- front suspension
    fk = P['fork'] = part('fork', ((XF + HX) / 2, 0, (RF + HZ) / 2), steer)
    for s, sn in ((1, 'L'), (-1, 'R')):
        if g('fork', 'tele') == 'tele':
            rod('fork_lower_' + sn, (XF, s * 0.10, RF), (XF - 0.25 * math.sin(rake), s * 0.10, RF + 0.25 * math.cos(rake)), 0.026, fk, 'engine')
            rod('fork_upper_' + sn, (XF - 0.2 * math.sin(rake), s * 0.10, RF + 0.2 * math.cos(rake)), (HX, s * 0.10, HZ), 0.019, fk, 'chrome')
        else:
            rod('fork_blade_' + sn, (XF, s * 0.09, RF), (HX, s * 0.09, HZ), 0.015, fk, 'frame_paint')
            rod('girder_' + sn, (XF + 0.06, s * 0.09, RF + 0.10), (HX + 0.06, s * 0.09, HZ - 0.05), 0.011, fk, 'frame_paint')
            rod('fork_spring_' + sn, (HX + 0.03, s * 0.05, HZ - 0.18), (HX + 0.03, s * 0.05, HZ - 0.02), 0.018, fk, 'chrome')
    rod('triple_clamp', (HX, -0.11, HZ), (HX, 0.11, HZ), 0.018, fk, 'black')
    # ---------------- handlebar, lights
    hb = P['handlebar'] = part('handlebar', (HX - 0.05, 0, HZ + 0.08), steer)
    bars = g('bars', 'wide'); bz = HZ + (0.02 if bars == 'clipon' else 0.12); bw = 0.30 if bars == 'clipon' else 0.38
    for s in (1, -1):
        tube('bar', [(HX, 0, bz), (HX - 0.03, s * bw * 0.5, bz + 0.01), (HX - 0.10, s * bw, bz - (0.03 if bars == 'clipon' else 0.0))], 0.011, hb, 'chrome')
        rod('grip', (HX - 0.10, s * bw, bz), (HX - 0.12, s * (bw + 0.09), bz), 0.017, hb, 'black')
    if g('lights', True):
        rod('headlight', (HX + 0.09, 0, HZ - 0.06), (HX + 0.15, 0, HZ - 0.06), 0.085, hb, 'chrome')
        rod('lens', (HX + 0.15, 0, HZ - 0.06), (HX + 0.16, 0, HZ - 0.06), 0.075, hb, 'glass')
    # ---------------- frame
    f = P['frame'] = part('frame', (0, 0, 0.5), root)
    EX_, EZ = g('engine_x', 0.0), g('engine_z', RR + 0.08)
    if not body:
        rod('head_tube', (HX, 0, HZ - 0.16), (HX, 0, HZ), 0.03, f, 'frame_paint')
        rod('backbone', (HX, 0, HZ - 0.03), (XR + 0.42, 0, SZ - 0.10), 0.026, f, 'frame_paint')
        tube('down_tube', [(HX, 0, HZ - 0.14), (EX_ + 0.30, 0, EZ - 0.05), (EX_ + 0.05, 0, EZ - 0.22), (XR + 0.45, 0, EZ - 0.12)], 0.022, f, 'frame_paint')
        rod('seat_rail', (XR + 0.42, 0, SZ - 0.10), (XR + 0.05, 0, SZ - 0.02), 0.018, f, 'frame_paint')
        rod('frame_rear', (XR + 0.45, 0, EZ - 0.12), (XR + 0.42, 0, SZ - 0.10), 0.022, f, 'frame_paint')
    # ---------------- rear suspension / swingarm
    rs = P['rear_suspension'] = part('rear_suspension', (XR + 0.2, 0, RR + 0.1), root)
    PV = (XR + 0.45, EZ - 0.08)                                 # swingarm pivot
    if not body:
        for s, sn in ((1, 'L'), (-1, 'R')):
            rod('swingarm_' + sn, (PV[0], s * 0.09, PV[1]), (XR, s * 0.09, RR), 0.02, rs, 'frame_paint' if g('rear', 'twinshock') == 'rigid' else 'engine')
            if g('rear', 'twinshock') == 'twinshock':
                rod('shock_' + sn, (XR + 0.06, s * 0.11, RR + 0.03), (XR + 0.16, s * 0.11, SZ - 0.06), 0.022, rs, 'chrome')
                rod('spring_' + sn, (XR + 0.08, s * 0.11, RR + 0.10), (XR + 0.14, s * 0.11, SZ - 0.10), 0.03, rs, 'paint')
            elif g('rear') in ('rigid', 'plunger'):
                rod('rear_stay_' + sn, (XR, s * 0.09, RR), (XR + 0.42, s * 0.03, SZ - 0.10), 0.016, rs, 'frame_paint')
                if g('rear') == 'plunger': rod('plunger_' + sn, (XR, s * 0.10, RR - 0.06), (XR, s * 0.10, RR + 0.08), 0.022, rs, 'chrome')
        if g('rear', 'twinshock') == 'mono':
            rod('monoshock', (PV[0] + 0.02, 0, PV[1] + 0.05), (PV[0] - 0.06, 0, SZ - 0.12), 0.025, rs, 'paint')
    # ---------------- engine
    en = P['engine'] = part('engine', (EX_, 0, EZ + 0.1), root)
    t = g('engine', 'inline4'); k = g('cc_scale', 1.0); fins = g('fins', True)
    def cylinder(x0, z0, ang, y=0.0, r=0.045, L=0.20, nm='cyl'):
        dx, dz = math.sin(ang), math.cos(ang)
        rod(nm, (x0, y, z0), (x0 + L * k * dx, y, z0 + L * k * dz), r * k, en, 'engine')
        rod(nm + '_head', (x0 + L * k * dx, y, z0 + L * k * dz), (x0 + (L + 0.05) * k * dx, y, z0 + (L + 0.05) * k * dz), r * k * 1.15, en, 'engine')
        if fins:
            for j in range(6):
                q = 0.25 + j * 0.12
                ring(f'{nm}_fin{j}', r * k * 1.05, 0.006, (x0 + L * k * q * dx, y, z0 + L * k * q * dz), en, 'engine').rotation_euler = (0, ang, 0)
    if t == 'single':
        rod('crankcase', (EX_, -0.08, EZ), (EX_, 0.08, EZ), 0.13 * k, en, 'engine'); cylinder(EX_ + 0.02, EZ + 0.08, math.radians(10), r=0.055, L=0.22)
    elif t in ('vtwin', 'v5'):
        rod('crankcase', (EX_, -0.09, EZ), (EX_, 0.09, EZ), 0.14 * k, en, 'engine')
        a = math.radians(g('v_angle', 45)) / 2
        nf, nr = (1, 1) if t == 'vtwin' else (3, 2)
        for i in range(nf): cylinder(EX_ + 0.03, EZ + 0.06, a, y=(i - (nf - 1) / 2) * 0.08, nm=f'cyl_f{i}')
        for i in range(nr): cylinder(EX_ - 0.03, EZ + 0.06, -a, y=(i - (nr - 1) / 2) * 0.08, nm=f'cyl_r{i}')
    elif t == 'boxer':
        box('crankcase', (0.30 * k, 0.20, 0.22 * k), (EX_, 0, EZ), en, 'engine', 0.04)
        for s in (1, -1):
            dy = s * 0.10
            rod('cyl_' + str(s), (EX_ + 0.04, dy, EZ + 0.04), (EX_ + 0.04, s * 0.26 * k, EZ + 0.06), 0.05 * k, en, 'engine')
            rod('head_' + str(s), (EX_ + 0.04, s * 0.26 * k, EZ + 0.06), (EX_ + 0.04, s * 0.31 * k, EZ + 0.06), 0.065 * k, en, 'engine')
            if fins:
                for j in range(5): ring(f'bfin{s}{j}', 0.055 * k, 0.006, (EX_ + 0.04, s * (0.13 + j * 0.025) * k, EZ + 0.05), en, 'engine').rotation_euler = (math.pi / 2, 0, 0)
    elif t in ('inline4', 'twin'):
        n = 4 if t == 'inline4' else 2
        box('crankcase', (0.34 * k, 0.12 * n * k + 0.08, 0.20 * k), (EX_, 0, EZ), en, 'engine', 0.03)
        ang = math.radians(g('cyl_tilt', 15))
        for i in range(n): cylinder(EX_ + 0.03, EZ + 0.08, ang, y=(i - (n - 1) / 2) * 0.10 * k, r=0.042, L=0.18, nm=f'cyl{i}')
        if not fins: box('block', (0.16 * k, 0.11 * n * k, 0.18 * k), (EX_ + 0.06, 0, EZ + 0.17 * k), en, 'engine', 0.02)
    elif t == 'scooter':
        box('engine_unit', (0.36, 0.16, 0.20), (XR + 0.22, -0.10, RR + 0.02), en, 'engine', 0.04)
    elif t == 'stepthrough':
        rod('crankcase', (EX_, -0.07, EZ), (EX_, 0.07, EZ), 0.09, en, 'engine'); cylinder(EX_ + 0.04, EZ + 0.02, math.radians(80), r=0.04, L=0.16)
    # ---------------- exhaust
    ex = P['exhaust'] = part('exhaust', (0, -0.15, RR), root)
    side = [-1] if g('exhaust', 'low') != 'twin' else [-1, 1]
    for s in side:
        zx = RR + (0.25 if g('exhaust', 'low') == 'high' else 0.0)
        tube('header', [(EX_ + 0.15, s * 0.06, EZ + 0.12), (EX_ + 0.22, s * 0.12, EZ - 0.10), (EX_ - 0.10, s * 0.16, zx - 0.05), (XR + 0.35, s * 0.17, zx)], 0.02, ex, 'chrome')
        rod('muffler', (XR + 0.38, s * 0.17, zx), (XR - 0.05, s * 0.17, zx + 0.06), 0.045, ex, 'chrome' if g('exhaust', 'low') != 'under' else 'black')
    # ---------------- drive
    dv = P['drive'] = part('drive', ((PV[0] + XR) / 2, 0.11, RR), root)
    d_ = g('drive', 'chain')
    if d_ == 'shaft':
        rod('shaft_tube', (PV[0], -0.10, PV[1]), (XR, -0.10, RR), 0.035, dv, 'engine'); rod('final_drive', (XR, -0.06, RR), (XR, -0.13, RR), 0.07, dv, 'engine')
    elif d_ in ('chain', 'belt'):
        ring('front_sprocket', 0.05, 0.008, (PV[0] + 0.05, 0.11, PV[1]), dv, 'chrome'); ring('rear_sprocket', RR * 0.45, 0.009, (XR, 0.11, RR), dv, 'chrome')
        for sgn in (1, -1):
            rod('chain', (PV[0] + 0.05, 0.11, PV[1] + sgn * 0.05), (XR, 0.11, RR + sgn * RR * 0.45), 0.005 if d_ == 'chain' else 0.012, dv, 'black')
    # ---------------- tank and seat (or body panels)
    tk = P['tank'] = part('tank', ((HX + XR + 0.42) / 2, 0, HZ - 0.02), root)
    if not body:
        tl = g('tank_len', 0.50); tx = HX - 0.08 - tl / 2
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=(tx, 0, HZ - 0.02)); o = bpy.context.object
        o.scale = (tl / 2, 0.15, 0.12); bpy.ops.object.transform_apply(location=False, rotation=False, scale=True); _fin(o, 'tank_body', tk, 'paint')
        rod('filler_cap', (tx + 0.05, 0, HZ + 0.09), (tx + 0.05, 0, HZ + 0.11), 0.03, tk, 'chrome')
    sd = P['saddle'] = part('saddle', (XR + 0.35, 0, SZ), root)
    sl = g('seat_len', 0.55)
    box('seat', (sl, 0.26, 0.09), (XR + 0.42 + (0.0 if body else 0.0) - sl / 2 + 0.05, 0, SZ), sd, 'black', 0.035)
    if body:
        bd = P['body'] = part('body', (0, 0, 0.5), root)
        if t == 'scooter':
            bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=(XR + 0.25, 0, RR + 0.18)); o = bpy.context.object
            o.scale = (0.38, 0.22, 0.22); bpy.ops.object.transform_apply(location=False, rotation=False, scale=True); _fin(o, 'rear_body', bd, 'paint')
            box('floorboard', (0.50, 0.30, 0.03), (0.05, 0, 0.22), bd, 'black', 0.01)
            box('leg_shield', (0.05, 0.42, 0.62), (HX - 0.06, 0, 0.55), bd, 'paint', 0.05)
            rod('front_mudguard', (XF - 0.05, 0, RF + 0.12), (XF + 0.10, 0, RF + 0.10), 0.09, bd, 'paint')
        else:
            tube('step_frame', [(HX, 0, HZ - 0.08), (0.20, 0, 0.45), (-0.05, 0, 0.38), (XR + 0.30, 0, SZ - 0.12)], 0.06, bd, 'paint')
            box('leg_shield', (0.04, 0.36, 0.40), (HX - 0.09, 0, HZ - 0.32), bd, 'paint', 0.04)
            box('rear_carrier', (0.30, 0.20, 0.02), (XR + 0.05, 0, SZ + 0.02), bd, 'black', 0.005)
            for s, sn in ((1, 'L'), (-1, 'R')):
                rod('swingarm_' + sn, (XR + 0.45, s * 0.09, RR + 0.02), (XR, s * 0.09, RR), 0.02, rs, 'paint')
                rod('shock_' + sn, (XR + 0.05, s * 0.10, RR + 0.03), (XR + 0.15, s * 0.10, SZ - 0.06), 0.02, rs, 'chrome')
    # ---------------- fairing
    if g('fairing'):
        fa = P['fairing'] = part('fairing', (HX - 0.05, 0, HZ - 0.15), root)
        full = g('fairing') == 'full'
        def shell(nm, loc, sc_, pitch=0.0, m='paint'):
            bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=loc); o = bpy.context.object
            o.scale = sc_; o.rotation_euler = (0, math.radians(pitch), 0)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True); return _fin(o, nm, fa, m)
        if full:
            shell('nose', (HX - 0.02, 0, HZ - 0.16), (0.36, 0.15, 0.17), 14)          # long, narrow, nose down
            shell('belly', (EX_ + 0.08, 0, EZ - 0.04), (0.36, 0.15, 0.12), -4)
            shell('tail_cowl', (XR + 0.22, 0, SZ + 0.03), (0.28, 0.095, 0.07), -10)
        else:
            shell('nose', (HX + 0.02, 0, HZ - 0.02), (0.17, 0.22, 0.17))
        bpy.ops.mesh.primitive_cube_add(size=1, location=(HX + 0.08, 0, HZ + (0.06 if full else 0.16))); o = bpy.context.object
        o.scale = (0.012, 0.20, 0.14); o.rotation_euler = (0, math.radians(-40), 0)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True); _fin(o, 'windscreen', fa, 'glass', False)
    def anchor(name, loc, p):
        e = bpy.data.objects.new('A_' + name, None); col.objects.link(e)
        e.location = Vector(loc) - origin[p.name]; e.parent = p; return e
    fz = EZ - 0.05
    A = dict(engine=anchor('engine', (EX_ + 0.08, 0.10, EZ + 0.12), en), tank=anchor('tank', (HX - 0.30, 0.12, HZ + 0.02), tk),
             saddle=anchor('saddle', (XR + 0.35, 0, SZ + 0.05), sd), front_wheel=anchor('front_wheel', (XF, 0, RF), fw),
             rear_wheel=anchor('rear_wheel', (XR, 0, RR), rw), fork=anchor('fork', (XF - 0.12 * math.sin(rake), 0.10, RF + 0.12), fk),
             brakes=anchor('brakes', (XF - RF * 0.3, 0.09, RF + RF * 0.3), br), frame=anchor('frame', (HX - 0.25, 0, HZ - 0.08), f),
             rear_suspension=anchor('rear_suspension', (XR + 0.12, 0.11, (RR + SZ) / 2), rs), exhaust=anchor('exhaust', (XR + 0.15, -0.17, RR + 0.03), ex),
             drive=anchor('drive', ((PV[0] + XR) / 2, 0.11, (PV[1] + RR) / 2 + 0.04), dv), handlebar=anchor('handlebar', (HX - 0.10, 0.30, HZ + 0.10), hb),
             headlight=anchor('headlight', (HX + 0.16, 0, HZ - 0.06), hb),
             foot_l=anchor('foot_l', (PV[0] + 0.06, 0.18, fz), root), foot_r=anchor('foot_r', (PV[0] + 0.06, -0.18, fz), root),
             hands=anchor('hands', (HX - 0.12, 0, HZ + 0.10), hb), seat=anchor('seat', (XR + 0.40, 0, SZ + 0.06), sd),
             ground_r=anchor('ground_r', (XR, 0, 0), root), ground_f=anchor('ground_f', (XF, 0, 0), root))
    if 'fairing' in P: A['fairing'] = anchor('fairing', (HX - 0.15, 0.20, HZ - 0.20), P['fairing'])
    if 'body' in P: A['body'] = anchor('body', (XR + 0.25, 0.20, RR + 0.20), P['body'])
    EXO = dict(front_wheel=(0.45, 0, 0), fork=(0.25, 0, 0.30), handlebar=(0.05, 0, 0.45), brakes=(0.10, 0.35, 0.0), tank=(0, 0, 0.40),
               saddle=(-0.05, 0, 0.42), engine=(0, 0.50, -0.05), exhaust=(0, -0.45, -0.05), drive=(0, 0.35, -0.15),
               rear_suspension=(-0.15, 0, 0.30), rear_wheel=(-0.45, 0, 0), frame=(0, 0, 0), fairing=(0.30, 0, 0.35), body=(0, -0.30, 0.25))
    base = {k_: v_.location.copy() for k_, v_ in P.items()}
    def explode(k_):
        for n_, o_ in P.items(): o_.location = base[n_] + Vector(EXO.get(n_, (0, 0, 0))) * k_
    return dict(root=root, steer=steer, parts=P, anchors=A, explode=explode, wheelbase=WB)
