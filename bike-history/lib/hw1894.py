"""Parametric Hildebrand & Wolfmüller (Munich, 1894) built from named parts. Same interface as draisine.build().
A step-through duplex steel frame, two horizontal water-cooled cylinders whose connecting rods drive cranks on the
rear wheel directly (no chain, no clutch, no pedals), the water tank shaped as the rear mudguard, a spoon brake on
the front tyre, air tyres. Front wheel 26 in, rear 22 in (see ep08/facts.md); the wheelbase is our guess."""
import bpy, math
from mathutils import Vector

RF, RR = 0.33, 0.28
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
    f = P['frame'] = part('frame', (0, 0, 0.5), root)
    for s, sn in ((1, 'L'), (-1, 'R')):                     # the duplex frame: two tubes each side, step-through
        tube('lower_' + sn, [(0.50, s * 0.03, 0.92), (0.40, s * 0.07, 0.45), (0.30, s * 0.09, 0.20), (-0.10, s * 0.09, 0.18), (XR + 0.10, s * 0.08, RR)], 0.016, f, 'paint')
        tube('upper_' + sn, [(0.50, s * 0.03, 0.88), (0.10, s * 0.06, 0.62), (-0.22, s * 0.07, 0.62), (XR + 0.05, s * 0.07, RR + 0.06)], 0.014, f, 'paint')
    rod('head_tube', (0.52, 0, 0.84), (0.50, 0, 1.0), 0.022, f, 'paint')
    def wheel(name, x, r, parent):
        w = part(name, (x, 0, r), parent)
        ring(name + '_rim', r - 0.035, 0.010, (x, 0, r), w, 'nickel', 1.2)
        ring(name + '_tyre', r - 0.022, 0.024, (x, 0, r), w, 'rubber', 1.0)
        rod(name + '_hub', (x, -0.05, r), (x, 0.05, r), 0.03, w, 'nickel')
        for i in range(32):
            a = i * 2 * math.pi / 32; c, s_ = math.cos(a), math.sin(a); y = 0.04 if i % 2 else -0.04
            rod(f'{name}_spoke{i}', (x + 0.025 * c, y, r + 0.025 * s_), (x + (r - 0.04) * c, 0, r + (r - 0.04) * s_), 0.0024, w, 'nickel')
        return w
    P['rear_wheel'] = rw = wheel('rear_wheel', XR, RR, root)
    for s in (1, -1):                                        # cranks on the rear axle, outside the wheel
        rod('rear_crank', (XR, s * 0.10, RR), (XR + 0.09, s * 0.10, RR + 0.03), 0.012, rw, 'iron')
    steer = part('steer', (XF, 0, 0), root)
    P['front_wheel'] = wheel('front_wheel', XF, RF, steer)
    fk = P['fork'] = part('fork', (0.58, 0, 0.6), steer)
    for s, sn in ((1, 'L'), (-1, 'R')):
        rod('fork_blade_' + sn, (XF, s * 0.05, RF), (0.51, s * 0.05, 0.86), 0.012, fk, 'paint')
    hb = P['handlebar'] = part('handlebar', (0.46, 0, 1.05), steer)
    rod('stem', (0.50, 0, 0.98), (0.49, 0, 1.08), 0.012, hb, 'nickel')
    for s in (1, -1):
        tube('bar', [(0.49, 0, 1.08), (0.46, s * 0.18, 1.08), (0.36, s * 0.30, 1.05)], 0.010, hb, 'nickel')
        rod('grip', (0.36, s * 0.30, 1.05), (0.28, s * 0.31, 1.04), 0.016, hb, 'wood')
    br = P['brake'] = part('brake', (XF - 0.05, 0, 2 * RF), steer)
    ang = math.radians(-15); sx, sz = XF + (RF + 0.012) * math.sin(ang), RF + (RF + 0.012) * math.cos(ang)
    rod('spoon', (sx - 0.04, 0, sz + 0.01), (sx + 0.04, 0, sz - 0.01), 0.013, br, 'iron')
    rod('brake_rod', (sx, 0, sz), (0.49, 0.03, 1.04), 0.005, br, 'nickel')
    # engine: two horizontal cylinders side by side, low in the frame, heads forward
    en = P['engine'] = part('engine', (0.12, 0, 0.30), root)
    for s, sn in ((1, 'L'), (-1, 'R')):
        rod('cylinder_' + sn, (-0.02, s * 0.075, 0.30), (0.34, s * 0.075, 0.30), 0.06, en, 'iron')
        rod('water_jacket_' + sn, (0.04, s * 0.075, 0.30), (0.30, s * 0.075, 0.30), 0.068, en, 'brass')
        rod('cyl_head_' + sn, (0.34, s * 0.075, 0.30), (0.38, s * 0.075, 0.30), 0.07, en, 'iron')
    rod('hot_tube', (0.38, 0, 0.34), (0.42, 0, 0.42), 0.008, en, 'brass')
    box('fuel_tank', (0.32, 0.13, 0.12), (0.18, 0, 0.56), en, 'paint', 0.02)
    # drive: connecting rods from the pistons straight back to the cranks on the rear wheel
    dv = P['drive'] = part('drive', (-0.3, 0, 0.3), root)
    for s, sn in ((1, 'L'), (-1, 'R')):
        rod('con_rod_' + sn, (-0.02, s * 0.10, 0.30), (XR + 0.09, s * 0.10, RR + 0.03), 0.011, dv, 'iron')
    # the water tank is the rear mudguard
    wt = P['water_tank'] = part('water_tank', (XR, 0, RR + 0.2), root)
    pts = [(XR + (RR + 0.07) * math.cos(math.radians(a)), 0, RR + (RR + 0.07) * math.sin(math.radians(a))) for a in (10, 40, 70, 100, 130, 160)]
    tube('water_mudguard', pts, 0.055, wt, 'brass')
    sd = P['saddle'] = part('saddle', (-0.22, 0, 0.72), root)
    rod('seat_post', (-0.20, 0, 0.62), (-0.21, 0, 0.70), 0.012, sd, 'nickel')
    box('saddle_seat', (0.24, 0.17, 0.05), (-0.22, 0, 0.72), sd, 'leather', 0.02)
    def anchor(name, loc, p):
        e = bpy.data.objects.new('A_' + name, None); col.objects.link(e)
        e.location = Vector(loc) - origin[p.name]; e.parent = p; return e
    A = dict(engine=anchor('engine', (0.18, 0.14, 0.30), en), water_tank=anchor('water_tank', (XR + 0.05, 0.06, 2 * RR + 0.07), wt),
             drive=anchor('drive', (-0.30, 0.10, 0.29), dv), brake=anchor('brake', (sx, 0, sz), br),
             saddle=anchor('saddle', (-0.22, 0, 0.75), sd), handlebar=anchor('handlebar', (0.36, 0.30, 1.05), hb),
             fork=anchor('fork', (0.60, 0.05, 0.55), fk), front_wheel=anchor('front_wheel', (XF, 0, RF), P['front_wheel']),
             rear_wheel=anchor('rear_wheel', (XR, 0, RR), rw), frame=anchor('frame', (0.40, 0.07, 0.45), f),
             foot_l=anchor('foot_l', (0.10, 0.16, 0.22), f), foot_r=anchor('foot_r', (0.10, -0.16, 0.22), f),
             hands=anchor('hands', (0.33, 0, 1.06), hb), seat=anchor('seat', (-0.24, 0, 0.76), sd),
             ground_r=anchor('ground_r', (XR, 0, 0), root), ground_f=anchor('ground_f', (XF, 0, 0), root))
    EX = dict(front_wheel=(0.45, 0, 0), fork=(0.18, 0, 0.30), handlebar=(0.05, 0, 0.45), brake=(0.30, 0, 0.30), engine=(0, 0.45, 0.05),
              drive=(0, -0.40, 0), water_tank=(-0.15, 0, 0.35), saddle=(0, 0, 0.40), rear_wheel=(-0.45, 0, 0), frame=(0, 0, 0))
    base = {k: v.location.copy() for k, v in P.items()}
    def explode(k):
        for n, o in P.items(): o.location = base[n] + Vector(EX[n]) * k
    return dict(root=root, steer=steer, parts=P, anchors=A, explode=explode, wheelbase=XF - XR)
