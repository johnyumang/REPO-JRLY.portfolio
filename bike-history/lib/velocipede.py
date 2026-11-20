"""Parametric Michaux-type velocipede ("boneshaker", France, late 1860s) built from named parts.
Units: metres. X forward, Y left, Z up, ground at z=0. Same interface as draisine.build().
Pedals and cranks are fixed to the front hub (direct drive), so they turn with the front wheel.
Sizes are typical of the type (front wheel about 0.9 m, rear about 0.78 m): see ep02/facts.md."""
import bpy, math
from mathutils import Vector

RF, RR = 0.45, 0.39          # wheel radii
XF, XR = 0.55, -0.62         # axle positions
CR = 0.13                    # crank length

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
             paint=_mat('paint', (0.10, 0.16, 0.12), 0.35, 0.5),      # dark green enamel on the iron frame
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
    # frame: the serpentine iron backbone from the steering head down to the rear stays
    HEAD = (XF - 0.06, 0, 1.00)
    f = P['frame'] = part('frame', (0, 0, 0.7), root)
    tube('backbone', [HEAD, (0.30, 0, 0.98), (0.05, 0, 0.80), (-0.25, 0, 0.62), (-0.48, 0, 0.56)], 0.022, f, 'paint')
    rod('head_tube', (XF - 0.06, 0, 0.93), (XF - 0.06, 0, 1.06), 0.03, f, 'paint')
    for s, sn in ((1, 'L'), (-1, 'R')):
        rod('rear_stay_' + sn, (-0.48, s * 0.012, 0.56), (XR, s * 0.065, RR), 0.012, f, 'paint')
    rod('stay_bridge', (-0.52, -0.05, 0.53), (-0.52, 0.05, 0.53), 0.008, f, 'paint')
    def wheel(name, x, r, spokes, parent):
        w = part(name, (x, 0, r), parent)
        ring(name + '_rim', r - 0.03, 0.022, (x, 0, r), w, 'wood', 0.8)
        ring(name + '_tyre', r - 0.008, 0.010, (x, 0, r), w, 'iron', 1.6)
        rod(name + '_hub', (x, -0.07, r), (x, 0.07, r), 0.045, w, 'wood')
        rod(name + '_axle', (x, -0.10, r), (x, 0.10, r), 0.012, w, 'iron')
        for i in range(spokes):
            a = i * 2 * math.pi / spokes; c, s_ = math.cos(a), math.sin(a)
            rod(f'{name}_spoke{i}', (x + 0.04 * c, 0, r + 0.04 * s_), (x + (r - 0.045) * c, 0, r + (r - 0.045) * s_), 0.010, w, 'wood')
        return w
    P['rear_wheel'] = wheel('rear_wheel', XR, RR, 10, root)
    steer = part('steer', (XF, 0, 0), root)
    P['front_wheel'] = fw = wheel('front_wheel', XF, RF, 12, steer)
    # cranks and pedals ride on the front hub
    cr = P['pedals'] = part('pedals', (XF, 0, RF), fw)
    for s, sn, ph in ((1, 'L', 0.0), (-1, 'R', math.pi)):
        ex, ez = XF + CR * math.cos(ph), RF + CR * math.sin(ph)
        rod('crank_' + sn, (XF, s * 0.105, RF), (ex, s * 0.105, ez), 0.011, cr, 'iron')
        rod('pedal_pin_' + sn, (ex, s * 0.10, ez), (ex, s * 0.19, ez), 0.007, cr, 'iron')
        box('pedal_' + sn, (0.05, 0.08, 0.045), (ex, s * 0.155, ez), cr, 'brass', 0.008)
    fk = P['fork'] = part('fork', (XF, 0, 0.95), steer)
    rod('fork_crown', (XF, -0.075, 0.95), (XF, 0.075, 0.95), 0.016, fk, 'paint')
    for s, sn in ((1, 'L'), (-1, 'R')):
        rod('fork_blade_' + sn, (XF, s * 0.075, RF), (XF, s * 0.075, 0.95), 0.013, fk, 'paint')
    rod('steer_column', (XF - 0.06, 0, 0.92), (XF - 0.06, 0, 1.12), 0.016, fk, 'iron')
    rod('crown_link', (XF, 0, 0.95), (XF - 0.06, 0, 0.94), 0.016, fk, 'paint')
    hb = P['handlebar'] = part('handlebar', (XF - 0.06, 0, 1.12), steer)
    rod('bar', (XF - 0.06, -0.27, 1.12), (XF - 0.06, 0.27, 1.12), 0.014, hb, 'iron')
    for s in (1, -1): rod('grip', (XF - 0.06, s * 0.20, 1.12), (XF - 0.06, s * 0.30, 1.12), 0.022, hb, 'wood')
    # saddle on a long leaf spring
    sd = P['saddle'] = part('saddle', (0.05, 0, 0.95), root)
    rod('spring', (0.42, 0, 1.04), (-0.38, 0, 0.66), 0.010, sd, 'iron')
    rod('spring_post', (-0.38, 0, 0.60), (-0.38, 0, 0.67), 0.012, sd, 'iron')
    box('saddle_seat', (0.26, 0.17, 0.05), (0.05, 0, 0.92), sd, 'leather', 0.02)
    # brake: a wooden pad pressed on the rear tyre by an iron lever; the cord to the handlebar is our guess
    br = P['brake'] = part('brake', (-0.52, 0, 0.70), root)
    ang = math.radians(28); sx, sz = XR + (RR + 0.02) * math.sin(ang), RR + (RR + 0.02) * math.cos(ang)
    tx, tz = 0.05 * math.cos(ang), -0.05 * math.sin(ang)
    rod('brake_pad', (sx - tx, 0, sz - tz), (sx + tx, 0, sz + tz), 0.018, br, 'wood')   # a wooden pad on an iron lever
    rod('brake_lever', (sx, 0, sz), (-0.47, 0.03, 0.60), 0.008, br, 'iron')
    rod('brake_cord', (-0.47, 0.03, 0.60), (XF - 0.06, 0.03, 1.08), 0.004, br, 'cord')

    def anchor(name, loc, p):
        e = bpy.data.objects.new('A_' + name, None); col.objects.link(e)
        e.location = Vector(loc) - origin[p.name]; e.parent = p; return e
    A = dict(pedals=anchor('pedals', (XF + CR, 0.155, RF), cr), crank=anchor('crank', (XF + CR / 2, 0.105, RF), cr),
             saddle=anchor('saddle', (0.05, 0, 0.95), sd), spring=anchor('spring', (-0.20, 0, 0.75), sd),
             brake=anchor('brake', (sx, 0, sz), br), handlebar=anchor('handlebar', (XF - 0.06, 0.22, 1.12), hb),
             front_wheel=anchor('front_wheel', (XF, 0, RF), fw), rear_wheel=anchor('rear_wheel', (XR, 0, RR), P['rear_wheel']),
             tyre=anchor('tyre', (XF - RF * 0.71, 0.0, RF - RF * 0.71), fw), frame=anchor('frame', (0.05, 0, 0.80), f),
             fork=anchor('fork', (XF, 0.075, 0.75), fk),
             foot_l=anchor('foot_l', (XF + CR, 0.155, RF), cr), foot_r=anchor('foot_r', (XF - CR, -0.155, RF), cr),
             hands=anchor('hands', (XF - 0.06, 0, 1.13), hb), seat=anchor('seat', (0.05, 0, 0.96), sd),
             ground_r=anchor('ground_r', (XR, 0, 0), root), ground_f=anchor('ground_f', (XF, 0, 0), root))
    EX = dict(front_wheel=(0.45, 0, 0), pedals=(0, 0.28, 0), fork=(0.12, 0, 0.30), handlebar=(0.0, 0, 0.55),
              saddle=(0, 0, 0.35), rear_wheel=(-0.45, 0, 0), brake=(-0.05, 0, -0.25), frame=(0, 0, 0))
    base = {k: v.location.copy() for k, v in P.items()}
    def explode(k):
        for n, o in P.items(): o.location = base[n] + Vector(EX[n]) * k
    return dict(root=root, steer=steer, parts=P, anchors=A, explode=explode)
