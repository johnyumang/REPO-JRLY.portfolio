"""Parametric penny-farthing ("ordinary", high-wheeler, 1870s-1880s) built from named parts.
Units: metres. X forward, Y left, Z up, ground at z=0. Same interface as draisine.build().
Front wheel 1.32 m (52 in, sized to the rider's leg), rear 0.44 m, thin wire spokes, solid rubber tyres, hollow steel
backbone, mounting step, spoon brake on the front tyre. See ep03/facts.md."""
import bpy, math
from mathutils import Vector

RF, RR = 0.66, 0.22
XF, XR = 0.25, -0.72
CR = 0.14

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
    HEAD = (XF - 0.07, 0, 1.40)
    f = P['frame'] = part('frame', (-0.2, 0, 1.0), root)
    # backbone follows the back of the big wheel down to the little rear wheel
    pts = [HEAD]
    for a in (25, 50, 75, 100):
        t = math.radians(a); pts.append((XF - (RF + 0.07) * math.sin(t), 0, RF + (RF + 0.07) * math.cos(t)))
    pts.append((XR + 0.03, 0, RR + 0.30))          # ends above the rear wheel, clear of its spokes
    tube('backbone', pts, 0.022, f, 'paint')
    for s, sn in ((1, 'L'), (-1, 'R')):
        rod('rear_fork_' + sn, (XR + 0.03, s * 0.012, RR + 0.30), (XR, s * 0.045, RR), 0.010, f, 'paint')
    rod('head', (XF - 0.07, 0, 1.36), (XF - 0.07, 0, 1.50), 0.028, f, 'nickel')
    bx, bz = XR + 0.13, RR + 0.31                     # the mounting step sits above the rear wheel
    st = P['step'] = part('step', (bx, 0.04, bz), root)
    rod('step_stem', (bx, 0.0, bz), (bx, 0.06, bz), 0.008, st, 'nickel')
    box('step_pad', (0.05, 0.06, 0.012), (bx, 0.09, bz), st, 'nickel', 0.003)
    def wheel(name, x, r, spokes, parent, rs=0.0028):
        w = part(name, (x, 0, r), parent)
        ring(name + '_rim', r - 0.022, 0.010, (x, 0, r), w, 'nickel', 1.2)
        ring(name + '_tyre', r - 0.010, 0.013, (x, 0, r), w, 'rubber', 1.0)
        rod(name + '_hub', (x, -0.06, r), (x, 0.06, r), 0.035 if r > 0.4 else 0.022, w, 'nickel')
        for i in range(spokes):                        # spokes alternate between the two hub flanges
            a = i * 2 * math.pi / spokes; c, s_ = math.cos(a), math.sin(a); y = 0.05 if i % 2 else -0.05
            rod(f'{name}_spoke{i}', (x + 0.03 * c, y, r + 0.03 * s_), (x + (r - 0.03) * c, 0, r + (r - 0.03) * s_), rs, w, 'nickel')
        return w
    P['rear_wheel'] = wheel('rear_wheel', XR, RR, 20, root)
    steer = part('steer', (XF, 0, 0), root)
    P['front_wheel'] = fw = wheel('front_wheel', XF, RF, 48, steer)
    cr = P['pedals'] = part('pedals', (XF, 0, RF), fw)
    for s, sn, ph in ((1, 'L', 0.0), (-1, 'R', math.pi)):
        ex, ez = XF + CR * math.cos(ph), RF + CR * math.sin(ph)
        rod('crank_' + sn, (XF, s * 0.09, RF), (ex, s * 0.09, ez), 0.010, cr, 'nickel')
        rod('pedal_pin_' + sn, (ex, s * 0.09, ez), (ex, s * 0.17, ez), 0.006, cr, 'nickel')
        box('pedal_' + sn, (0.05, 0.07, 0.03), (ex, s * 0.14, ez), cr, 'rubber', 0.006)
    fk = P['fork'] = part('fork', (XF, 0, 1.0), steer)
    rod('fork_crown', (XF - 0.07, -0.075, 1.38), (XF - 0.07, 0.075, 1.38), 0.016, fk, 'paint')
    for s, sn in ((1, 'L'), (-1, 'R')):
        rod('fork_blade_' + sn, (XF, s * 0.075, RF), (XF - 0.07, s * 0.075, 1.38), 0.014, fk, 'paint')
    hb = P['handlebar'] = part('handlebar', (XF - 0.07, 0, 1.50), steer)
    rod('stem', (XF - 0.07, 0, 1.44), (XF - 0.07, 0, 1.52), 0.014, hb, 'nickel')
    for s in (1, -1):
        rod('bar', (XF - 0.07, 0, 1.52), (XF - 0.12, s * 0.30, 1.44), 0.011, hb, 'nickel')
        rod('grip', (XF - 0.12, s * 0.30, 1.44), (XF - 0.16, s * 0.36, 1.42), 0.019, hb, 'wood')
    sd = P['saddle'] = part('saddle', (XF - 0.24, 0, 1.43), root)
    box('saddle_seat', (0.24, 0.16, 0.05), (XF - 0.24, 0, 1.46), sd, 'leather', 0.02)
    rod('saddle_spring', (XF - 0.33, 0, 1.40), (XF - 0.14, 0, 1.43), 0.008, sd, 'nickel')
    br = P['brake'] = part('brake', (XF - 0.1, 0, 1.35), steer)
    ang = math.radians(-14); sx, sz = XF + (RF + 0.022) * math.sin(ang), RF + (RF + 0.022) * math.cos(ang)
    tx, tz = 0.05 * math.cos(ang), -0.05 * math.sin(ang)
    rod('brake_spoon', (sx - tx, 0, sz - tz), (sx + tx, 0, sz + tz), 0.014, br, 'nickel')
    rod('brake_rod', (sx, 0, sz + 0.01), (XF - 0.07, 0.03, 1.48), 0.006, br, 'nickel')
    rod('brake_lever', (XF - 0.07, 0.03, 1.48), (XF - 0.11, 0.24, 1.47), 0.006, br, 'nickel')

    def anchor(name, loc, p):
        e = bpy.data.objects.new('A_' + name, None); col.objects.link(e)
        e.location = Vector(loc) - origin[p.name]; e.parent = p; return e
    A = dict(pedals=anchor('pedals', (XF + CR, 0.14, RF), cr), front_wheel=anchor('front_wheel', (XF, 0, RF), fw),
             spokes=anchor('spokes', (XF + RF * 0.45, 0.0, RF + RF * 0.30), fw), step=anchor('step', (bx, 0.09, bz), st),
             brake=anchor('brake', (sx, 0, sz), br), saddle=anchor('saddle', (XF - 0.24, 0, 1.47), sd),
             handlebar=anchor('handlebar', (XF - 0.12, 0.30, 1.44), hb), fork=anchor('fork', (XF - 0.03, 0.075, 1.0), fk),
             rear_wheel=anchor('rear_wheel', (XR, 0, RR), P['rear_wheel']), frame=anchor('frame', pts[3], f),
             foot_l=anchor('foot_l', (XF + CR, 0.14, RF), cr), foot_r=anchor('foot_r', (XF - CR, -0.14, RF), cr),
             hands=anchor('hands', (XF - 0.13, 0, 1.45), hb), seat=anchor('seat', (XF - 0.26, 0, 1.48), sd),
             ground_r=anchor('ground_r', (XR, 0, 0), root), ground_f=anchor('ground_f', (XF, 0, 0), root))
    EX = dict(front_wheel=(0.55, 0, 0), pedals=(0, 0.30, 0), fork=(0.15, 0, 0.35), handlebar=(0.0, 0, 0.55), brake=(0.35, 0, 0.35),
              saddle=(-0.1, 0, 0.35), rear_wheel=(-0.40, 0, 0), step=(0, 0.25, -0.1), frame=(0, 0, 0))
    base = {k: v.location.copy() for k, v in P.items()}
    def explode(k):
        for n, o in P.items(): o.location = base[n] + Vector(EX[n]) * k
    return dict(root=root, steer=steer, parts=P, anchors=A, explode=explode, wheelbase=XF - XR)
