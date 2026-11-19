"""Parametric Draisine (Laufmaschine, Karl Drais, 1817) built from named parts.
Units: metres. X forward, Y left, Z up, ground at z=0.
Every part is an Empty with mesh children, so it can be spun, steered, exploded and labelled.
Dimensions: wheels about 27 in (0.69 m), wheelbase 1.2 m, overall about 1.9 m (see ep01/facts.md).
The tiller and armrest stand are simplified shapes."""
import bpy, math
from mathutils import Vector

R = 0.345          # wheel radius
WB = 1.2           # wheelbase
XR, XF = -WB / 2, WB / 2

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
    M = dict(wood=_mat('wood', (0.50, 0.27, 0.11), 0.55, wood=True),
             wood2=_mat('wood_light', (0.62, 0.40, 0.18), 0.55, wood=True),
             iron=_mat('iron', (0.06, 0.06, 0.07), 0.45, 0.9),
             leather=_mat('leather', (0.16, 0.07, 0.04), 0.7),
             cord=_mat('cord', (0.75, 0.68, 0.50), 0.9))
    col = bpy.context.scene.collection
    origin = {}
    def part(name, loc, parent=None):
        e = bpy.data.objects.new(name, None); col.objects.link(e)
        po = origin[parent.name] if parent else Vector()
        e.location = Vector(loc) - po; e.parent = parent; origin[name] = Vector(loc); return e
    def _fin(o, name, p, m, bevel=0.0):
        o.name = name; o.location = Vector(o.location) - origin[p.name]; o.parent = p
        o.data.materials.append(M[m])
        if bevel:
            md = o.modifiers.new('bv', 'BEVEL'); md.width = bevel; md.segments = 2
        for poly in o.data.polygons: poly.use_smooth = True
        return o
    def box(name, size, loc, p, m, bevel=0.006):
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.object
        o.scale = size; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        _fin(o, name, p, m, bevel)
        for poly in o.data.polygons: poly.use_smooth = False
        return o
    def rod(name, a, b, r, p, m, square=False):
        a, b = Vector(a), Vector(b); d = b - a
        if square:
            bpy.ops.mesh.primitive_cube_add(size=1, location=(a + b) / 2); o = bpy.context.object
            o.scale = (2 * r, 2 * r, d.length); bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        else:
            bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d.length, vertices=20, location=(a + b) / 2)
            o = bpy.context.object
        o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
        _fin(o, name, p, m, 0.004 if square else 0)
        if square:
            for poly in o.data.polygons: poly.use_smooth = False
        return o
    def ring(name, major, minor, loc, p, m, flat=1.0):
        bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=64, minor_segments=12,
                                         location=loc, rotation=(math.pi / 2, 0, 0))
        o = bpy.context.object; o.scale = (1, 1, flat); return _fin(o, name, p, m)

    root = part('bike', (0, 0, 0))
    P = {}
    # frame: beam, rear stays, braces, steering pin
    f = P['frame'] = part('frame', (0, 0, 0), root)
    box('beam', (1.38, 0.06, 0.07), (-0.03, 0, 0.78), f, 'wood', 0.008)
    box('rear_bracket', (0.07, 0.19, 0.05), (XR, 0, 0.78), f, 'wood')
    for s, sn in ((1, 'L'), (-1, 'R')):
        rod('rear_stay_' + sn, (XR, s * 0.078, R - 0.03), (XR, s * 0.078, 0.80), 0.013, f, 'wood', True)
        rod('brace_' + sn, (XR, s * 0.078, R + 0.02), (-0.20, s * 0.042, 0.76), 0.008, f, 'iron')
    rod('steer_pin', (XF, 0, 0.72), (XF, 0, 0.93), 0.011, f, 'iron')
    # wheels
    def wheel(name, x, parent):
        w = part(name, (x, 0, R), parent)
        ring(name + '_rim', R - 0.030, 0.024, (x, 0, R), w, 'wood2', 0.8)
        ring(name + '_tyre', R - 0.008, 0.010, (x, 0, R), w, 'iron', 1.6)
        rod(name + '_hub', (x, -0.06, R), (x, 0.06, R), 0.042, w, 'wood')
        rod(name + '_axle', (x, -0.095, R), (x, 0.095, R), 0.011, w, 'iron')
        for i in range(8):
            a = i * math.pi / 4
            c, s_ = math.cos(a), math.sin(a)
            rod(f'{name}_spoke{i}', (x + 0.035 * c, 0, R + 0.035 * s_), (x + 0.30 * c, 0, R + 0.30 * s_), 0.011, w, 'wood2')
        return w
    P['rear_wheel'] = wheel('rear_wheel', XR, root)
    steer = part('steer', (XF, 0, 0), root)
    P['front_wheel'] = wheel('front_wheel', XF, steer)
    fk = P['fork'] = part('fork', (XF, 0, 0.875), steer)
    box('fork_crown', (0.07, 0.19, 0.05), (XF, 0, 0.875), fk, 'wood')
    for s, sn in ((1, 'L'), (-1, 'R')):
        rod('fork_blade_' + sn, (XF, s * 0.078, R - 0.03), (XF, s * 0.078, 0.875), 0.013, fk, 'wood', True)
    hb = P['handlebar'] = part('handlebar', (0.42, 0, 1.08), steer)
    rod('tiller', (XF - 0.01, 0, 0.895), (0.42, 0, 1.08), 0.013, hb, 'iron')
    rod('bar', (0.42, -0.22, 1.08), (0.42, 0.22, 1.08), 0.016, hb, 'wood2')
    # saddle
    sd = P['saddle'] = part('saddle', (-0.12, 0, 0.86), root)
    box('cushion', (0.36, 0.20, 0.06), (-0.12, 0, 0.86), sd, 'leather', 0.022)
    for x in (-0.22, -0.02):
        rod('saddle_post', (x, 0, 0.81), (x, 0, 0.84), 0.012, sd, 'iron')
    # armrest (balancing board)
    ar = P['armrest'] = part('armrest', (0.22, 0, 1.0), root)
    box('board', (0.10, 0.34, 0.035), (0.22, 0, 1.0), ar, 'leather', 0.014)
    for s in (1, -1):
        rod('armrest_stay', (0.20, s * 0.022, 0.81), (0.22, s * 0.12, 0.99), 0.008, ar, 'iron')
    # brake: shoe on the rear tyre, pulled by a cord
    br = P['brake'] = part('brake', (-0.36, 0, 0.64), root)
    ang = math.radians(40)
    sx, sz = XR + (R + 0.022) * math.sin(ang), R + (R + 0.022) * math.cos(ang)
    tx, tz = 0.04 * math.cos(ang), -0.04 * math.sin(ang)      # shoe lies along the tyre
    rod('brake_shoe', (sx - tx, 0, sz - tz), (sx + tx, 0, sz + tz), 0.016, br, 'wood', True)
    rod('brake_arm', (sx, 0, sz), (sx + 0.02, 0, 0.75), 0.007, br, 'iron')
    rod('cord_a', (sx + 0.02, 0.036, 0.775), (0.26, 0.036, 0.775), 0.004, br, 'cord')
    rod('cord_b', (0.26, 0.036, 0.775), (0.40, 0.036, 1.045), 0.004, br, 'cord')

    def anchor(name, loc, p):
        e = bpy.data.objects.new('A_' + name, None); col.objects.link(e)
        e.location = Vector(loc) - origin[p.name]; e.parent = p; return e
    A = dict(steering=anchor('steering', (XF, 0, 0.90), fk), handlebar=anchor('handlebar', (0.42, 0.10, 1.08), hb),
             armrest=anchor('armrest', (0.22, 0, 1.02), ar), saddle=anchor('saddle', (-0.12, 0, 0.89), sd),
             brake=anchor('brake', (sx, 0, sz), br), front_wheel=anchor('front_wheel', (XF, 0, R), P['front_wheel']),
             rear_wheel=anchor('rear_wheel', (XR, 0, R), P['rear_wheel']), frame=anchor('frame', (0.05, 0, 0.80), f),
             hands=anchor('hands', (0.42, 0, 1.10), hb), seat=anchor('seat', (-0.12, 0, 0.90), sd),
             ground_r=anchor('ground_r', (XR, 0, 0), root), ground_f=anchor('ground_f', (XF, 0, 0), root))
    # explode offsets in bike space (frame stays put)
    EX = dict(front_wheel=(0.42, 0, 0), fork=(0.16, 0, 0.26), handlebar=(-0.05, 0, 0.55), armrest=(0, 0, 0.32),
              saddle=(-0.05, 0, 0.30), rear_wheel=(-0.45, 0, 0), brake=(-0.02, 0.0, -0.22), frame=(0, 0, 0))
    base = {k: v.location.copy() for k, v in P.items()}
    def explode(k):
        for n, o in P.items(): o.location = base[n] + Vector(EX[n]) * k
    return dict(root=root, steer=steer, parts=P, anchors=A, explode=explode)
