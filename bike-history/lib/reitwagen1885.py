"""Parametric Daimler Reitwagen (Gottlieb Daimler and Wilhelm Maybach, Cannstatt, 1885) built from named parts.
Units: metres. X forward, Y left, Z up, ground at z=0. Same interface as draisine.build().
A wooden frame, wooden wheels with iron tyres, a single-cylinder engine standing upright under the saddle, a belt to
the rear wheel (the 1885 drive), and two small side wheels to keep it upright. Sizes are typical, not
measured: see ep06/facts.md."""
import bpy, math
from mathutils import Vector

RF, RR = 0.34, 0.39          # front and rear wheel radius
XF, XR = 0.62, -0.58

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
    for s, sn in ((1, 'L'), (-1, 'R')):                      # two wooden side beams
        box('beam_' + sn, (1.02, 0.04, 0.07), (-0.05, s * 0.085, 0.62), f, 'wood', 0.006)
        box('rear_upright_' + sn, (0.05, 0.035, 0.30), (XR + 0.02, s * 0.085, 0.50), f, 'wood', 0.005)
    for x in (-0.48, 0.0, 0.38):
        box('cross_beam', (0.05, 0.21, 0.04), (x, 0, 0.62), f, 'wood', 0.005)
    box('head_block', (0.10, 0.12, 0.30), (0.46, 0, 0.74), f, 'wood', 0.008)
    box('front_brace', (0.30, 0.10, 0.04), (0.33, 0, 0.66), f, 'wood', 0.005)
    def wheel(name, x, r, spokes, parent):
        w = part(name, (x, 0, r), parent)
        ring(name + '_rim', r - 0.03, 0.022, (x, 0, r), w, 'wood', 0.9)
        ring(name + '_tyre', r - 0.008, 0.010, (x, 0, r), w, 'iron', 1.6)
        rod(name + '_hub', (x, -0.065, r), (x, 0.065, r), 0.045, w, 'wood')
        rod(name + '_axle', (x, -0.12, r), (x, 0.12, r), 0.012, w, 'iron')
        for i in range(spokes):
            a = i * 2 * math.pi / spokes; c, s_ = math.cos(a), math.sin(a)
            rod(f'{name}_spoke{i}', (x + 0.04 * c, 0, r + 0.04 * s_), (x + (r - 0.045) * c, 0, r + (r - 0.045) * s_), 0.011, w, 'wood')
        return w
    P['rear_wheel'] = rw = wheel('rear_wheel', XR, RR, 12, root)
    steer = part('steer', (XF, 0, 0), root)
    P['front_wheel'] = wheel('front_wheel', XF, RF, 10, steer)
    fk = P['fork'] = part('fork', (0.55, 0, 0.6), steer)
    for s, sn in ((1, 'L'), (-1, 'R')):
        rod('fork_blade_' + sn, (XF, s * 0.07, RF), (0.47, s * 0.07, 0.90), 0.014, fk, 'iron')
    rod('fork_crown', (0.47, -0.07, 0.90), (0.47, 0.07, 0.90), 0.014, fk, 'iron')
    hb = P['handlebar'] = part('handlebar', (0.40, 0, 1.0), steer)
    rod('steer_column', (0.47, 0, 0.90), (0.43, 0, 1.06), 0.014, hb, 'iron')
    rod('bar', (0.43, -0.30, 1.06), (0.43, 0.30, 1.06), 0.013, hb, 'iron')
    for s in (1, -1): rod('grip', (0.43, s * 0.22, 1.06), (0.43, s * 0.32, 1.06), 0.02, hb, 'wood')
    # the engine stands upright between the beams, under the saddle
    en = P['engine'] = part('engine', (0.05, 0, 0.62), root)
    CX = 0.05
    rod('crankcase', (CX, -0.075, 0.42), (CX, 0.075, 0.42), 0.10, en, 'iron')
    rod('flywheel', (CX, 0.08, 0.42), (CX, 0.10, 0.42), 0.13, en, 'iron')
    rod('cylinder', (CX, 0, 0.50), (CX, 0, 0.82), 0.055, en, 'iron')
    for k in range(7): ring(f'fin{k}', 0.052, 0.006, (CX, 0, 0.56 + k * 0.035), en, 'iron')
    rod('cyl_head', (CX, 0, 0.82), (CX, 0, 0.86), 0.065, en, 'iron')
    rod('hot_tube', (CX + 0.05, 0, 0.84), (CX + 0.10, 0, 0.88), 0.008, en, 'brass')
    rod('burner', (CX + 0.10, 0, 0.86), (CX + 0.10, 0, 0.92), 0.018, en, 'brass')
    rod('carburettor', (CX - 0.08, 0.04, 0.76), (CX - 0.12, 0.04, 0.70), 0.025, en, 'brass')
    # drive (1885): a belt from the engine pulley to a big pulley on the rear wheel; gears came with the 1886 rebuild
    dv = P['drive'] = part('drive', (-0.25, -0.12, 0.42), root)
    EP, RP, re_, rr_ = (CX, -0.12, 0.42), (XR, -0.12, RR), 0.055, 0.22
    rod('engine_pulley', (CX, -0.09, 0.42), (CX, -0.14, 0.42), re_, dv, 'brass')
    ring('rear_pulley', rr_, 0.012, (XR, -0.12, RR), dv, 'brass')
    d = math.hypot(EP[0] - RP[0], EP[2] - RP[2]); ang = math.atan2(EP[2] - RP[2], EP[0] - RP[0]); off = math.asin((rr_ - re_) / d)
    for sgn, nm in ((1, 'top'), (-1, 'bottom')):
        a_ = ang + sgn * (math.pi / 2 - off)
        rod('belt_' + nm, (RP[0] + rr_ * math.cos(a_), -0.125, RP[2] + rr_ * math.sin(a_)), (EP[0] + re_ * math.cos(a_), -0.125, EP[2] + re_ * math.sin(a_)), 0.008, dv, 'belt')
    # two small side wheels on springs keep it from falling over
    ow = P['side_wheels'] = part('side_wheels', (-0.15, 0, 0.12), root)
    for s, sn in ((1, 'L'), (-1, 'R')):
        rod('outrigger_' + sn, (-0.15, s * 0.09, 0.58), (-0.15, s * 0.24, 0.14), 0.011, ow, 'iron')
        ring('side_wheel_' + sn, 0.10, 0.012, (-0.15, s * 0.25, 0.11), ow, 'wood')
        for k in range(6):
            t = k * math.pi / 3
            rod('side_spoke', (-0.15, s * 0.25, 0.11), (-0.15 + 0.095 * math.cos(t), s * 0.25, 0.11 + 0.095 * math.sin(t)), 0.006, ow, 'wood')
    sd = P['saddle'] = part('saddle', (0.0, 0, 0.98), root)
    box('saddle_seat', (0.36, 0.26, 0.07), (0.0, 0, 0.97), sd, 'leather', 0.03)
    for x in (-0.12, 0.12):
        for s in (1, -1): rod('saddle_post', (x, s * 0.085, 0.655), (x, s * 0.085, 0.935), 0.01, sd, 'iron')

    def anchor(name, loc, p):
        e = bpy.data.objects.new('A_' + name, None); col.objects.link(e)
        e.location = Vector(loc) - origin[p.name]; e.parent = p; return e
    A = dict(engine=anchor('engine', (CX, 0.06, 0.66), en), frame=anchor('frame', (-0.30, 0.10, 0.62), f),
             drive=anchor('drive', ((CX + XR) / 2, -0.125, (0.42 + RR) / 2 + 0.10), dv), side_wheels=anchor('side_wheels', (-0.15, 0.25, 0.11), ow),
             saddle=anchor('saddle', (0.0, 0, 1.01), sd), handlebar=anchor('handlebar', (0.43, 0.28, 1.06), hb),
             fork=anchor('fork', (0.55, 0.07, 0.62), fk), front_wheel=anchor('front_wheel', (XF, 0, RF), P['front_wheel']),
             rear_wheel=anchor('rear_wheel', (XR, 0, RR), rw),
             foot_l=anchor('foot_l', (0.20, 0.16, 0.30), f), foot_r=anchor('foot_r', (0.22, -0.16, 0.30), f),
             hands=anchor('hands', (0.40, 0, 1.06), hb), seat=anchor('seat', (-0.02, 0, 1.01), sd),
             ground_r=anchor('ground_r', (XR, 0, 0), root), ground_f=anchor('ground_f', (XF, 0, 0), root))
    EX = dict(front_wheel=(0.45, 0, 0), fork=(0.20, 0, 0.30), handlebar=(0.05, 0, 0.45), engine=(0, 0.42, 0.10),
              drive=(0, -0.40, 0), side_wheels=(0, 0, -0.08), saddle=(0, 0, 0.42), rear_wheel=(-0.45, 0, 0), frame=(0, 0, 0))
    base = {k: v.location.copy() for k, v in P.items()}
    def explode(k):
        for n, o in P.items(): o.location = base[n] + Vector(EX[n]) * k
    return dict(root=root, steer=steer, parts=P, anchors=A, explode=explode, wheelbase=XF - XR)
