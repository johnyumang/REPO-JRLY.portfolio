"""History Indio — Blender host action clips (720x1280, CPU only, headless `bpy` wheel).

    python host_shot.py --model host.glb --out frames/ --shot greet|twist|point|powerup --seconds 2.76 [--fps 30]

Look (per .claude/skills/anime-style): unlit toon shader with 3 constant value steps from N.L of one key
light, hard terminators, inverted-hull outlines (Solidify + flipped normals), limited palette.
Character animation is sampled "on twos" (constant keys) and on ones during the strike; camera on ones.
"""
import argparse, json, math, os, random, struct, sys, time
import bpy, bmesh
from mathutils import Vector, Quaternion, Matrix

ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--engine", default="CYCLES")
ap.add_argument("--samples", type=int, default=12)
ap.add_argument("--frames", default="")
ap.add_argument("--shot", default="powerup")
ap.add_argument("--seconds", type=float, default=4.0)
ap.add_argument("--fps", type=int, default=30)
ap.add_argument("--step", type=int, default=1)
ap.add_argument("--scale", type=int, default=100)
ap.add_argument("--save", default="")
A = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])
END = math.ceil(A.seconds * A.fps)
F0, F1 = [int(x) for x in A.frames.split("-")] if A.frames else (1, END)
SHOT = A.shot
random.seed(7)

# ---------------------------------------------------------------- import
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=A.model, bone_heuristic="TEMPERANCE")
S = bpy.context.scene
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
body, face, hair = (bpy.data.objects[n] for n in ("Body", "Face", "Hair001"))
for o in list(bpy.data.objects):
    if o.type == "MESH" and o not in (body, face, hair):
        bpy.data.objects.remove(o)

with open(A.model, "rb") as f:  # morph target names live in the glTF JSON chunk
    f.read(12)
    n, _ = struct.unpack("<I4s", f.read(8))
    GLTF = json.loads(f.read(n))
_names = next(m for m in GLTF["meshes"] if m["name"].startswith("Face"))["primitives"][0]["extras"]["targetNames"]
EXPR = {nm.split("_Fcl_")[1]: i for i, nm in enumerate(_names)}  # e.g. BRW_Angry, EYE_Close, MTH_A
KEYS = face.data.shape_keys.key_blocks


def bone(n):
    return arm.pose.bones[n]


HEAD = bone("J_Bip_C_Head").head.copy()
HIPS = bone("J_Bip_C_Hips").head.copy()

# ---------------------------------------------------------------- shared FX values (animated once, used by all materials)
fx = bpy.data.node_groups.new("HI_FX", "ShaderNodeTree")
fx_out = fx.nodes.new("NodeGroupOutput")
for nm in ("Flash", "Aura", "Time", "Lines"):
    fx.interface.new_socket(nm, in_out="OUTPUT", socket_type="NodeSocketFloat")
    v = fx.nodes.new("ShaderNodeValue")
    v.name = nm
    fx.links.new(v.outputs[0], fx_out.inputs[nm])

LIGHT = Vector((-0.55, 0.62, 0.56)).normalized()  # single key light, camera-left and above
SHADOW = (0.34, 0.36, 0.66)                       # cool moonlit shadow multiplier
FIRE = Vector((0.62, 0.45, -0.42)).normalized()   # warm firelight from low on the right
GOLD = (1.0, 0.72, 0.22, 1)


def mix(nt, fac, a, b):
    m = nt.nodes.new("ShaderNodeMix")
    m.data_type = "RGBA"
    for sock, val in ((m.inputs[0], fac), (m.inputs[6], a), (m.inputs[7], b)):
        if hasattr(val, "links") or hasattr(val, "is_linked"):
            nt.links.new(val, sock)
        else:
            sock.default_value = val
    return m.outputs[2]


def math_node(nt, op, a, b=None, c=None):
    m = nt.nodes.new("ShaderNodeMath")
    m.operation = op
    for i, val in enumerate((a, b, c)):
        if val is None:
            continue
        if hasattr(val, "is_linked"):
            nt.links.new(val, m.inputs[i])
        else:
            m.inputs[i].default_value = val
    return m.outputs[0]


def new_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    g = nt.nodes.new("ShaderNodeGroup")
    g.node_tree = fx
    return m, nt, out, g


def emit(nt, out, color, alpha=None):
    e = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(color, e.inputs[0])
    if alpha is None:
        nt.links.new(e.outputs[0], out.inputs[0])
        return
    t = nt.nodes.new("ShaderNodeBsdfTransparent")
    ms = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(alpha, ms.inputs[0])
    nt.links.new(t.outputs[0], ms.inputs[1])
    nt.links.new(e.outputs[0], ms.inputs[2])
    nt.links.new(ms.outputs[0], out.inputs[0])


def toon(name, color=None, image=None, tint=(1, 1, 1), lit=True, alpha=False, thr=0.5, hi=0.93, rim=True,
         mono=False, sleeve=None):
    """3-step cel shader: shadow / base / highlight, constant ramp on N.L, unlit (emission)."""
    m, nt, out, g = new_mat(name)
    a_sock = None
    if image:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = image
        src = tex.outputs[0]
        if mono:  # recolour: keep the painted values, replace the hue
            bw = nt.nodes.new("ShaderNodeRGBToBW")
            nt.links.new(src, bw.inputs[0])
            src = bw.outputs[0]
        base = mix(nt, 1.0, src, (*tint, 1))
        nt.nodes[-1].blend_type = "MULTIPLY"
        if alpha:
            a_sock = tex.outputs[1]
    else:
        rgb = nt.nodes.new("ShaderNodeRGB")
        rgb.outputs[0].default_value = (*color, 1)
        base = rgb.outputs[0]
    if sleeve:  # bare arms: everything beyond the armhole (measured on the rest pose) is skin
        at = nt.nodes.new("ShaderNodeAttribute")
        at.attribute_name = "restx"
        base = mix(nt, math_node(nt, "GREATER_THAN", math_node(nt, "ABSOLUTE", at.outputs["Fac"]), sleeve[0]), base, (*sleeve[1], 1))
    col = base
    if lit:
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        dot = nt.nodes.new("ShaderNodeVectorMath")
        dot.operation = "DOT_PRODUCT"
        nt.links.new(geo.outputs["Normal"], dot.inputs[0])
        dot.inputs[1].default_value = LIGHT
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.interpolation = "CONSTANT"
        e = ramp.color_ramp.elements
        e[0].position, e[0].color = 0.0, (*SHADOW, 1)
        e[1].position, e[1].color = thr, (1, 1, 1, 1)
        h = e.new(hi)
        h.color = (1.22, 1.16, 1.02, 1)
        nt.links.new(math_node(nt, "MULTIPLY_ADD", dot.outputs["Value"], 0.5, 0.5), ramp.inputs[0])
        col = mix(nt, 1.0, base, ramp.outputs[0])
        nt.nodes[-1].blend_type = "MULTIPLY"
        fd = nt.nodes.new("ShaderNodeVectorMath")  # hard-edged warm firelight patch
        fd.operation = "DOT_PRODUCT"
        nt.links.new(geo.outputs["Normal"], fd.inputs[0])
        fd.inputs[1].default_value = FIRE
        warm = mix(nt, 1.0, col, (1.55, 1.08, 0.66, 1))
        nt.nodes[-1].blend_type = "MULTIPLY"
        col = mix(nt, math_node(nt, "GREATER_THAN", fd.outputs["Value"], 0.58), col, warm)
        if rim:  # flat gold rim band while the aura burns
            lw = nt.nodes.new("ShaderNodeLayerWeight")
            lw.inputs[0].default_value = 0.5
            band = math_node(nt, "GREATER_THAN", lw.outputs["Facing"], 0.74)
            col = mix(nt, math_node(nt, "MULTIPLY", band, math_node(nt, "MINIMUM", g.outputs["Aura"], 1.0)), col, GOLD)
    col = mix(nt, g.outputs["Flash"], col, (0, 0, 0, 1))  # impact frame: black silhouette
    emit(nt, out, col, a_sock)
    return m


def outline_mat():
    """Inverted hull: the flipped shell shows only where it faces the camera, i.e. around the silhouette."""
    m, nt, out, g = new_mat("HI_Outline")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    col = mix(nt, g.outputs["Flash"], (0.035, 0.02, 0.05, 1), (1, 1, 1, 1))
    emit(nt, out, col, math_node(nt, "SUBTRACT", 1.0, geo.outputs["Backfacing"]))
    m.use_backface_culling = True
    return m


OUTLINE = outline_mat()


def add_outline(obj, thick, vgroup=None):
    obj.data.materials.append(OUTLINE)
    s = obj.modifiers.new("Hull", "SOLIDIFY")
    s.thickness, s.offset = thick, 1.0
    s.use_flip_normals, s.use_rim = True, False
    s.material_offset = 999
    if vgroup:
        s.vertex_group = vgroup


# ---------------------------------------------------------------- character materials
SKIN_TINT = (0.50, 0.30, 0.19)
PAL = dict(indigo=(0.020, 0.016, 0.085), red=(0.62, 0.03, 0.03), hair=(0.006, 0.006, 0.012),
           pants=(0.014, 0.014, 0.026), sandal=(0.10, 0.05, 0.03), gold=(0.95, 0.62, 0.10))


def tex_of(mat):
    return next(n.image for n in mat.node_tree.nodes if n.type == "TEX_IMAGE")


def mean_color(img):
    import numpy as np
    px = np.empty(len(img.pixels), dtype=np.float32)
    img.pixels.foreach_get(px)
    px = px.reshape(-1, 4)
    c = px[px[:, 3] > 0.9][:, :3].mean(axis=0)
    return tuple(float(x) ** 2.2 for x in c)  # sRGB -> linear (approx.)


def slot(obj, key):
    return next(i for i, m in enumerate(obj.data.materials) if key in m.name)


skin_img = tex_of(body.data.materials[slot(body, "Body")])
flat_skin = tuple(a * b for a, b in zip(mean_color(skin_img), SKIN_TINT))
body.data.materials[slot(body, "Body")] = toon("HI_Skin", image=skin_img, tint=SKIN_TINT)
# drop the sample hoodie's hood and strings so the top reads as a vest
vgn = {g.index: g.name for g in body.vertex_groups}
hood = {v.index for v in body.data.vertices if v.groups and "Hood" in vgn[max(v.groups, key=lambda g: g.weight).group]}
bm = bmesh.new()
bm.from_mesh(body.data)
bmesh.ops.delete(bm, geom=[f for f in bm.faces if all(v.index in hood for v in f.verts)], context="FACES")
bm.to_mesh(body.data)
bm.free()
ARMHOLE = abs(bone("J_Bip_R_UpperArm").head.x) + 0.02
rx = body.data.attributes.new("restx", "FLOAT", "POINT")
rx.data.foreach_set("value", [v.co.x for v in body.data.vertices])
body.data.materials[slot(body, "Tops")] = toon("HI_Vest", PAL["indigo"], sleeve=(ARMHOLE, flat_skin))
body.data.materials[slot(body, "Bottoms")] = toon("HI_Pants", PAL["pants"])
body.data.materials[slot(body, "Shoes")] = toon("HI_Sandal", PAL["sandal"])
hair.data.materials[0] = toon("HI_Hair", PAL["hair"], hi=0.80)
hair.data.materials[0].node_tree.nodes["Color Ramp"].color_ramp.elements[2].color = (3.0, 3.0, 5.0, 1)

for i, m in enumerate(list(face.data.materials)):
    img = tex_of(m)
    if "Face_00_SKIN" in m.name:
        face.data.materials[i] = toon("HI_FaceSkin", image=img, tint=SKIN_TINT, thr=0.36, hi=2.0)
    elif "Brow" in m.name or "Eyeline" in m.name or "Eyelash" in m.name:
        face.data.materials[i] = toon("HI_" + m.name[-12:], image=img, tint=(0.05, 0.04, 0.05), lit=False, alpha=True)
    elif "Iris" in m.name:
        face.data.materials[i] = toon("HI_Iris", image=img, tint=(1.0, 0.45, 0.2), lit=False, alpha=True, mono=True)
    else:
        face.data.materials[i] = toon("HI_" + m.name[-12:], image=img, lit=False, alpha=True)

add_outline(body, 0.008)
add_outline(hair, 0.006)
fg = face.vertex_groups.new(name="hull")  # outline only the skin, not the eye/brow cards
fs = slot(face, "FaceSkin")
fg.add(list({i for p in face.data.polygons if p.material_index == fs for i in p.vertices}), 1.0, "REPLACE")
add_outline(face, 0.005, "hull")

# hair lifts and ripples while the aura burns (tips move most)
hw = hair.vertex_groups.new(name="tips")
c = HEAD + Vector((0, 0, 0.08))
for v in hair.data.vertices:
    hw.add([v.index], min(1.0, max(0.0, ((v.co - c).length - 0.10) / 0.10)), "REPLACE")
wv = hair.modifiers.new("Wave", "WAVE")
wv.use_normal, wv.use_x, wv.use_y, wv.use_cyclic = True, True, True, True
wv.height, wv.width, wv.speed, wv.narrowness, wv.time_offset = 0.0, 0.11, 0.035, 5.0, -200
wv.vertex_group = "tips"
hair.modifiers.move(len(hair.modifiers) - 1, 0)


# ---------------------------------------------------------------- costume pieces
def mesh_obj(name, verts, faces, mat, uvs=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    if uvs:
        uv = me.uv_layers.new(name="uv")
        for poly in me.polygons:
            for li, vi in zip(poly.loop_indices, poly.vertices):
                uv.data[li].uv = uvs[vi]
    me.materials.append(mat)
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    S.collection.objects.link(o)
    return o


def follow(o, bname):
    c = o.constraints.new("CHILD_OF")
    c.target, c.subtarget = arm, bname
    c.inverse_matrix = (arm.matrix_world @ bone(bname).matrix).inverted()


def band(name, center, rx, ry, height, target, offset, mat, bname, seg=64, tilt=0.0):
    """A cloth ring shrink-wrapped onto the character, then frozen and bound to one bone."""
    verts, faces = [], []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        dz = tilt * math.cos(a)
        for k in (0, 1, 2):
            verts.append((center.x + rx * math.sin(a), center.y + ry * math.cos(a), center.z + dz + height * (k / 2 - 0.5)))
    for i in range(seg):
        j = (i + 1) % seg
        for k in (0, 1):
            faces.append((i * 3 + k, j * 3 + k, j * 3 + k + 1, i * 3 + k + 1))
    o = mesh_obj(name, verts, faces, mat)
    sw = o.modifiers.new("sw", "SHRINKWRAP")
    sw.target, sw.offset, sw.wrap_method = target, offset, "NEAREST_SURFACEPOINT"
    bpy.context.view_layer.update()
    me = bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    o.modifiers.clear()
    o.data = me
    sm = o.modifiers.new("smooth", "SMOOTH")
    sm.factor, sm.iterations = 0.6, 6
    follow(o, bname)
    add_outline(o, 0.007)
    return o


def strip(name, origin, length, w0, w1, mat, bname, seg=14):
    """A cloth tail along local +X with a travelling wave; the root stays pinned."""
    verts, faces = [], []
    for i in range(seg + 1):
        t = i / seg
        w = w0 + (w1 - w0) * t
        verts += [(length * t, -w / 2, 0), (length * t, w / 2, 0)]
    for i in range(seg):
        faces.append((2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1))
    o = mesh_obj(name, verts, faces, mat)
    g = o.vertex_groups.new(name="w")
    for i in range(seg + 1):
        g.add([2 * i, 2 * i + 1], (i / seg) ** 1.2, "REPLACE")
    wm = o.modifiers.new("Wave", "WAVE")
    wm.use_x, wm.use_y, wm.use_normal, wm.use_cyclic = True, False, False, True
    wm.height, wm.width, wm.speed, wm.narrowness, wm.time_offset = 0.02, 0.30, 0.05, 4.0, -200
    wm.vertex_group = "w"
    o.location = origin
    o.rotation_mode = "QUATERNION"
    follow(o, bname)
    sol = o.modifiers.new("thick", "SOLIDIFY")
    sol.thickness = 0.006
    add_outline(o, 0.004)
    return o


def aim(direction, roll=0.0):
    q = Vector(direction).normalized().to_track_quat("X", "Z")
    return q @ Quaternion((1, 0, 0), math.radians(roll))


RED = toon("HI_Red", PAL["red"])
band("Headband", HEAD + Vector((0, 0.0, 0.118)), 0.17, 0.19, 0.05, hair, 0.005, RED, "J_Bip_C_Head", tilt=0.012)
KNOT = HEAD + Vector((0.035, -0.115, 0.10))
tails = [strip("Tail%d" % i, KNOT, L, 0.05, 0.028, RED, "J_Bip_C_Head") for i, L in enumerate((0.50, 0.40))]
band("Sash", HIPS + Vector((0, 0, 0.075)), 0.26, 0.22, 0.12, body, 0.012, RED, "J_Bip_C_Spine")
sash_tail = strip("SashTail", HIPS + Vector((-0.10, 0.115, 0.06)), 0.50, 0.10, 0.07, RED, "J_Bip_C_Hips")
GOLDM = toon("HI_Gold", PAL["gold"], hi=0.7)
for sx in (-1, 1):
    vs = [(0, 0, 0)] + [(0, 0.024 * math.cos(a), 0.024 * math.sin(a)) for a in [2 * math.pi * i / 16 for i in range(16)]]
    e = mesh_obj("Earring", vs, [(0, 1 + i, 1 + (i + 1) % 16) for i in range(16)], GOLDM)
    e.location = HEAD + Vector((sx * 0.083, 0.0, -0.005))
    e.rotation_euler = (0, 0, sx * math.radians(-35))
    follow(e, "J_Bip_C_Head")
    sol = e.modifiers.new("thick", "SOLIDIFY")
    sol.thickness = 0.004
    add_outline(e, 0.003)


# ---------------------------------------------------------------- set: night beach village, aura, lines
def plane(name, w, h, mat, loc, rot=(math.pi / 2, 0, 0)):
    o = mesh_obj(name, [(-w / 2, -h / 2, 0), (w / 2, -h / 2, 0), (w / 2, h / 2, 0), (-w / 2, h / 2, 0)],
                 [(0, 1, 2, 3)], mat, uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])
    o.location, o.rotation_euler = loc, rot
    return o


def uv_xy(nt):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["UV"], sep.inputs[0])
    return sep.outputs[0], sep.outputs[1]


def noise(nt, x, y, w, scale=1.0, detail=2.0):
    cx = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(x, cx.inputs[0])
    nt.links.new(y, cx.inputs[1])
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.noise_dimensions = "4D"
    n.inputs["Scale"].default_value, n.inputs["Detail"].default_value = scale, detail
    nt.links.new(cx.outputs[0], n.inputs["Vector"])
    if hasattr(w, "is_linked"):
        nt.links.new(w, n.inputs["W"])
    else:
        n.inputs["W"].default_value = w
    return n.outputs[0]


def finish(nt, out, g, col, darken, alpha=None):
    """Shared tail for set materials: dim while the aura burns, go white on the impact frame."""
    dark = math_node(nt, "SUBTRACT", 1.0, math_node(nt, "MULTIPLY", math_node(nt, "MINIMUM", g.outputs["Aura"], 1.0), darken))
    sc = nt.nodes.new("ShaderNodeVectorMath")
    sc.operation = "SCALE"
    if hasattr(col, "is_linked"):
        nt.links.new(col, sc.inputs[0])
    else:
        sc.inputs[0].default_value = col[:3]
    nt.links.new(dark, sc.inputs["Scale"])
    emit(nt, out, mix(nt, g.outputs["Flash"], sc.outputs[0], (1, 1, 1, 1)), alpha)


MOON_U, MOON_V = 0.5 + 4.5 / 220, 0.20


def sky_mat():
    m, nt, out, g = new_mat("HI_Sky")
    u, v = uv_xy(nt)
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    e = ramp.color_ramp.elements
    e[0].position, e[0].color = 0.0, (0.055, 0.10, 0.26, 1)
    e[1].position, e[1].color = 1.0, (0.004, 0.006, 0.03, 1)
    for pos, colr in ((0.12, (0.025, 0.045, 0.15, 1)), (0.35, (0.010, 0.016, 0.07, 1))):
        ramp.color_ramp.elements.new(pos).color = colr
    nt.links.new(v, ramp.inputs[0])
    cl = noise(nt, math_node(nt, "MULTIPLY", u, 16.0), math_node(nt, "MULTIPLY", v, 46.0), 3.0, 1.0, 4.0)
    cr = nt.nodes.new("ShaderNodeValToRGB")  # two-step painted clouds, moonlit on top
    cr.color_ramp.interpolation = "CONSTANT"
    ce = cr.color_ramp.elements
    ce[0].position, ce[0].color = 0.0, (0, 0, 0, 1)
    ce[1].position, ce[1].color = 0.55, (0.02, 0.035, 0.10, 1)
    cr.color_ramp.elements.new(0.63).color = (0.07, 0.11, 0.24, 1)
    nt.links.new(cl, cr.inputs[0])
    add = nt.nodes.new("ShaderNodeVectorMath")
    nt.links.new(ramp.outputs[0], add.inputs[0])
    nt.links.new(cr.outputs[0], add.inputs[1])
    st = noise(nt, math_node(nt, "MULTIPLY", u, 2600.0), math_node(nt, "MULTIPLY", v, 1300.0), 1.0, 1.0, 0.0)
    stars = math_node(nt, "MULTIPLY", math_node(nt, "GREATER_THAN", st, 0.80), math_node(nt, "LESS_THAN", cl, 0.5))
    col = mix(nt, stars, add.outputs[0], (0.55, 0.62, 0.8, 1))
    du = math_node(nt, "MULTIPLY", math_node(nt, "SUBTRACT", u, MOON_U), 220.0)
    dv = math_node(nt, "MULTIPLY", math_node(nt, "SUBTRACT", v, MOON_V), 110.0)
    d = math_node(nt, "SQRT", math_node(nt, "ADD", math_node(nt, "MULTIPLY", du, du), math_node(nt, "MULTIPLY", dv, dv)))
    col = mix(nt, math_node(nt, "LESS_THAN", d, 4.6), col, (0.10, 0.16, 0.34, 1))   # halo
    col = mix(nt, math_node(nt, "LESS_THAN", d, 2.6), col, (1.35, 1.35, 1.2, 1))    # moon
    finish(nt, out, g, col, 0.62)
    return m


def sea_mat():
    m, nt, out, g = new_mat("HI_Sea")
    u, v = uv_xy(nt)
    n = noise(nt, math_node(nt, "MULTIPLY", u, 70.0), math_node(nt, "MULTIPLY", v, 900.0), math_node(nt, "MULTIPLY", g.outputs["Time"], 0.5), 1.0, 1.0)
    band = math_node(nt, "LESS_THAN", math_node(nt, "ABSOLUTE", math_node(nt, "SUBTRACT", u, MOON_U)), math_node(nt, "MULTIPLY_ADD", v, -0.035, 0.05))
    col = mix(nt, math_node(nt, "GREATER_THAN", n, 0.66), (0.008, 0.02, 0.07, 1), (0.03, 0.06, 0.16, 1))
    col = mix(nt, math_node(nt, "MULTIPLY", band, math_node(nt, "GREATER_THAN", n, 0.52)), col, (0.55, 0.65, 0.8, 1))
    finish(nt, out, g, col, 0.5)
    return m


def flat_mat(name, color, darken=0.5):
    m, nt, out, g = new_mat(name)
    finish(nt, out, g, color, darken)
    return m


def aura_mat(name, back=True):
    """Cel flame: a noise-eaten teardrop that scrolls upward, in three flat colours."""
    m, nt, out, g = new_mat(name)
    u, v = uv_xy(nt)
    T = g.outputs["Time"]
    ax = math_node(nt, "ABSOLUTE", math_node(nt, "MULTIPLY", math_node(nt, "SUBTRACT", u, 0.5), 2.0))
    n = noise(nt, math_node(nt, "MULTIPLY", u, 5.0),
              math_node(nt, "SUBTRACT", math_node(nt, "MULTIPLY", v, 3.2), math_node(nt, "MULTIPLY", T, 3.4)),
              math_node(nt, "MULTIPLY", T, 0.9), 1.0, 2.5)
    width = math_node(nt, "MULTIPLY", math_node(nt, "POWER", math_node(nt, "SUBTRACT", 1.0, v), 0.55), 0.33)
    wob = math_node(nt, "MULTIPLY", math_node(nt, "SUBTRACT", n, 0.5), math_node(nt, "MULTIPLY_ADD", v, 0.9, 0.22))
    mval = math_node(nt, "SUBTRACT", math_node(nt, "ADD", width, wob), ax)
    mval = math_node(nt, "SUBTRACT", mval, math_node(nt, "MULTIPLY", math_node(nt, "SUBTRACT", 1.0, g.outputs["Aura"]), 0.9))
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    e = ramp.color_ramp.elements
    e[0].position, e[0].color = 0.0, (1.0, 0.30, 0.02, 1)
    e[1].position, e[1].color = 0.20, (1.0, 0.62, 0.06, 1)
    ramp.color_ramp.elements.new(0.48).color = (1.0, 0.92, 0.5, 1)
    nt.links.new(math_node(nt, "MULTIPLY", mval, 1.5), ramp.inputs[0])
    inside = math_node(nt, "GREATER_THAN", mval, 0.0 if back else 0.02)
    if not back:  # front layer: only thin licks near the edge so the character stays readable
        inside = math_node(nt, "MULTIPLY", inside, math_node(nt, "LESS_THAN", mval, 0.075))
    emit(nt, out, ramp.outputs[0], math_node(nt, "MULTIPLY", inside, math_node(nt, "SUBTRACT", 1.0, g.outputs["Flash"])))
    return m


def lines_mat():
    """Radial speed lines on a card in front of the lens; reshuffled every two frames."""
    m, nt, out, g = new_mat("HI_Lines")
    u, v = uv_xy(nt)
    x, y = math_node(nt, "SUBTRACT", u, 0.5), math_node(nt, "MULTIPLY", math_node(nt, "SUBTRACT", v, 0.5), 16 / 9)
    ang = math_node(nt, "ARCTAN2", y, x)
    r = math_node(nt, "SQRT", math_node(nt, "ADD", math_node(nt, "MULTIPLY", x, x), math_node(nt, "MULTIPLY", y, y)))
    n = noise(nt, math_node(nt, "MULTIPLY", math_node(nt, "COSINE", ang), 26.0),
              math_node(nt, "MULTIPLY", math_node(nt, "SINE", ang), 26.0), math_node(nt, "MULTIPLY", g.outputs["Time"], 37.0), 1.0, 0.0)
    line = math_node(nt, "GREATER_THAN", n, 0.60)
    edge = math_node(nt, "GREATER_THAN", r, math_node(nt, "MULTIPLY_ADD", n, -0.45, 0.72))
    a = math_node(nt, "MULTIPLY", math_node(nt, "MULTIPLY", line, edge), g.outputs["Lines"])
    rgb = nt.nodes.new("ShaderNodeRGB")
    rgb.outputs[0].default_value = (1, 0.97, 0.85, 1)
    emit(nt, out, rgb.outputs[0], a)
    return m


plane("Sky", 220, 110, sky_mat(), (0, -70, 52))
plane("Sea", 220, 58, sea_mat(), (0, -40, 0.03), (0, 0, 0))
gm = bpy.data.meshes.new("Ground")
bm = bmesh.new()
bmesh.ops.create_circle(bm, cap_ends=True, segments=48, radius=90)
bm.to_mesh(gm)
bm.free()
ground = bpy.data.objects.new("Ground", gm)
S.collection.objects.link(ground)
gm.materials.append(flat_mat("HI_Ground", (0.030, 0.026, 0.045, 1), 0.35))
rv, rf, N = [], [], 60  # far island ridge
for i in range(N + 1):
    x = -110 + 220 * i / N
    hgt = 2 + 4 * abs(math.sin(i * 0.37)) + 2 * random.random() + (10 if 22 < i < 30 else 0) * abs(math.sin((i - 22) * 0.4))
    rv += [(x, 0, 0), (x, 0, hgt)]
for i in range(N):
    rf.append((2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1))
mesh_obj("Ridge", rv, rf, flat_mat("HI_Ridge", (0.010, 0.018, 0.06, 1), 0.5)).location = (0, -68, 0)
bv = [(0, 0, 0)] + [(0.62 * math.cos(a), 0.36 * math.sin(a), 0) for a in [2 * math.pi * i / 32 for i in range(32)]]
mesh_obj("Blob", bv, [(0, 1 + i, 1 + (i + 1) % 32) for i in range(32)], flat_mat("HI_Blob", (0.008, 0.006, 0.016, 1), 0.0)).location = (0, 0, 0.004)

DARKWOOD = flat_mat("HI_Wood", (0.014, 0.011, 0.028, 1), 0.4)
ROOF = flat_mat("HI_Roof", (0.035, 0.028, 0.05, 1), 0.4)
GLOW = flat_mat("HI_Window", (1.0, 0.50, 0.10, 1), 0.2)
FLAME = flat_mat("HI_Flame", (1.0, 0.78, 0.25, 1), 0.2)


def box(name, x0, x1, y0, y1, z0, z1, mat):
    v = [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    f = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return mesh_obj(name, v, f, mat)


def hut(x, y, s=1.0):
    """Stilt house silhouette with a lit doorway, in the spirit of the k02 key frame."""
    for sx in (-1.3, 1.3):
        for sy in (-0.9, 0.9):
            box("Stilt", x + (sx - 0.07) * s, x + (sx + 0.07) * s, y + (sy - 0.07) * s, y + (sy + 0.07) * s, 0, 1.3 * s, DARKWOOD)
    box("Floor", x - 1.6 * s, x + 1.6 * s, y - 1.1 * s, y + 1.1 * s, 1.25 * s, 1.4 * s, DARKWOOD)
    box("Wall", x - 1.4 * s, x + 1.4 * s, y - 0.95 * s, y + 0.95 * s, 1.4 * s, 2.7 * s, DARKWOOD)
    r = [(x - 1.9 * s, y - 1.3 * s, 2.6 * s), (x + 1.9 * s, y - 1.3 * s, 2.6 * s), (x + 1.9 * s, y + 1.3 * s, 2.6 * s),
         (x - 1.9 * s, y + 1.3 * s, 2.6 * s), (x - 1.1 * s, y, 4.3 * s), (x + 1.1 * s, y, 4.3 * s)]
    mesh_obj("Roof", r, [(0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5)], ROOF)
    box("Door", x - 0.35 * s, x + 0.35 * s, y + 0.95 * s, y + 0.97 * s, 1.4 * s, 2.35 * s, GLOW)
    box("Win", x + 0.75 * s, x + 1.15 * s, y + 0.95 * s, y + 0.97 * s, 1.85 * s, 2.3 * s, GLOW)


def palm(x, y, h=7.0, lean=1.2):
    v, f = [], []
    for i in range(9):
        t = i / 8
        cx, w = x + lean * t * t, 0.16 - 0.07 * t
        v += [(cx - w, y, h * t), (cx + w, y, h * t)]
    for i in range(8):
        f.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
    top = Vector((x + lean, y, h))
    for k in range(9):
        a = math.radians(-20 + k * 28)
        base = len(v)
        for i in range(7):
            t = i / 6
            p = top + Vector((math.cos(a) * 2.6 * t, 0, math.sin(a) * 2.6 * t - 1.9 * t * t))
            w = 0.34 * math.sin(math.pi * min(1, t + 0.12))
            v += [(p.x, p.y, p.z - w), (p.x, p.y, p.z + w)]
        for i in range(6):
            f.append((base + 2 * i, base + 2 * i + 1, base + 2 * i + 3, base + 2 * i + 2))
    mesh_obj("Palm", v, f, DARKWOOD)


hut(-3.1, -9.5, 1.0)
hut(3.3, -13.0, 1.1)
hut(8.5, -19.0, 1.2)
palm(-1.9, -6.5, 7.5, 1.3)
palm(5.2, -16.0, 9.0, -1.6)
torches = []
for tx, ty in ((1.55, -3.2), (-1.75, -4.4)):
    box("Pole", tx - 0.03, tx + 0.03, ty - 0.03, ty + 0.03, 0, 1.55, DARKWOOD)
    fl = mesh_obj("TorchFlame", [(0, 0, 0), (0.09, 0, 0.12), (0, 0, 0.42), (-0.09, 0, 0.12), (0, 0.09, 0.12), (0, -0.09, 0.12)],
                  [(0, 1, 2, 3), (0, 4, 2, 5)], FLAME)
    fl.location = (tx, ty, 1.55)
    torches.append(fl)

aura_back = plane("AuraBack", 3.6, 4.2, aura_mat("HI_AuraBack", True), (0, -0.45, 2.05))
aura_front = plane("AuraFront", 3.6, 4.2, aura_mat("HI_AuraFront", False), (0, 0.45, 2.05))

cam_data = bpy.data.cameras.new("Cam")
cam = bpy.data.objects.new("Cam", cam_data)
S.collection.objects.link(cam)
S.camera = cam
cam_data.sensor_fit, cam_data.sensor_height, cam_data.lens, cam_data.clip_end = "VERTICAL", 36, 42, 400
tgt = bpy.data.objects.new("CamTarget", None)
S.collection.objects.link(tgt)
tr = cam.constraints.new("TRACK_TO")
tr.target, tr.track_axis, tr.up_axis = tgt, "TRACK_NEGATIVE_Z", "UP_Y"
lines = plane("Lines", 1.0, 16 / 9, lines_mat(), (0, 0, -1.0), (0, 0, 0))
lines.parent = cam
lines.scale = (1.1, 1.1, 1.1)

SPARK = flat_mat("HI_Spark", (1.0, 0.85, 0.35, 1), 0.0)
sparks = []
if SHOT == "powerup":
    for i in range(34):
        a, r = random.uniform(0, 2 * math.pi), random.uniform(0.35, 1.25)
        h = random.uniform(0.05, 0.13)
        o = mesh_obj("Spark", [(0, 0, -h), (0.012, 0, 0), (0, 0, h), (-0.012, 0, 0), (0, 0.012, 0), (0, -0.012, 0)],
                     [(0, 1, 2, 3), (0, 4, 2, 5)], SPARK)
        sparks.append((o, r * math.cos(a), r * math.sin(a) * 0.7, random.randint(12, 24), random.randint(0, 24)))
    rv, rf = [], []
    for i in range(48):
        a = 2 * math.pi * i / 48
        rv += [(0.86 * math.cos(a), 0.86 * math.sin(a), 0), (math.cos(a), math.sin(a), 0)]
    for i in range(48):
        j = (i + 1) % 48
        rf.append((2 * i, 2 * i + 1, 2 * j + 1, 2 * j))
    ring = mesh_obj("Ring", rv, rf, flat_mat("HI_Ring", (1.0, 0.9, 0.55, 1), 0.0))
    ring.location = (0, 0, 0.012)

if SHOT == "greet":  # clay tea cup in the right fist (grip axis = rest +Y, opening at +Y)
    hc = bone("J_Bip_R_Hand").head + Vector((0.082, 0.0, -0.047))
    cv, cf, n = [], [], 20
    for r, y in ((0.026, -0.05), (0.041, 0.045), (0.035, 0.035)):
        cv += [(hc.x + r * math.cos(2 * math.pi * i / n), hc.y + y, hc.z + r * math.sin(2 * math.pi * i / n)) for i in range(n)]
    for i in range(n):
        j = (i + 1) % n
        cf += [(i, j, n + j, n + i), (n + i, n + j, 2 * n + j, 2 * n + i)]
    cf += [tuple(range(n - 1, -1, -1))]
    cup = mesh_obj("Cup", cv, cf, toon("HI_Clay", (0.20, 0.085, 0.04)))
    cup.data.materials.append(toon("HI_Tea", (0.10, 0.035, 0.012), lit=False))
    tea = mesh_obj("Tea", cv[2 * n:], [tuple(range(n))], cup.data.materials[1])
    for o in (cup, tea):
        follow(o, "J_Bip_R_Hand")
    add_outline(cup, 0.004)

# ---------------------------------------------------------------- posing
X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
AX = dict(x=X, y=Y, z=Z)
REST = {b.name: b.bone.matrix_local.to_quaternion() for b in arm.pose.bones}


def quat(spec):
    """spec: [('y', -80), ('x', 10)] = world-axis turns (degrees) applied in order, relative to the T-pose."""
    q = Quaternion()
    for ax, deg in spec:
        q = Quaternion(AX[ax], math.radians(deg)) @ q
    return q


def set_rel(pb, D):  # D rides on the parent's motion (plain FK)
    R = REST[pb.name]
    pb.rotation_mode = "QUATERNION"
    pb.rotation_quaternion = R.inverted() @ D @ R


def set_abs(pb, D):  # D is the bone's final turn in armature space, whatever the parents did
    R = REST[pb.name]
    Pq = pb.parent.matrix.to_quaternion() @ (REST[pb.parent.name].inverted() @ R)
    pb.rotation_mode = "QUATERNION"
    pb.rotation_quaternion = Pq.inverted() @ (D @ R)


FINGERS = ["Index", "Middle", "Ring", "Little"]


def fist(pose, side, amt=1.0, point=False):
    s = 1 if side == "R" else -1
    for fgr in FINGERS:
        k = 0.04 if (point and fgr == "Index") else amt
        for j, deg in zip((1, 2, 3), (72, 88, 60)):
            pose["J_Bip_%s_%s%d" % (side, fgr, j)] = [("y", s * deg * k)]
    pose["J_Bip_%s_Thumb1" % side] = [("y", s * 28 * amt), ("z", -s * 22 * amt)]
    pose["J_Bip_%s_Thumb2" % side] = [("z", -s * 30 * amt)]
    pose["J_Bip_%s_Thumb3" % side] = [("z", -s * 40 * amt)]
    return pose


def P(hips=(0, 0, 0), yaw=0.0, fR=1.0, fL=1.0, point=False, **bones):
    """A key pose. Character right = +X, forward = +Y; +x leans back / looks up, +z turns to the character's left."""
    pose = {"J_Bip_" + k: v for k, v in bones.items()}
    fist(pose, "R", fR, point)
    fist(pose, "L", fL)
    pose["_hips"], pose["_yaw"] = Vector(hips), yaw
    return pose


ease_io = lambda t: t * t * (3 - 2 * t)
ease_in = lambda t: t * t * t
ease_out = lambda t: 1 - (1 - t) ** 3
WIDE = dict(x=0.27, yl=0.10, yr=-0.12, yawr=30, yawl=12)
NARROW = dict(x=0.115, yl=0.03, yr=-0.03, yawr=14, yawl=14)
ARMS_DOWN = dict(R_UpperArm=[("y", 74)], R_LowerArm=[("z", 12)], L_UpperArm=[("y", -74)], L_LowerArm=[("z", -12)])
HIP_L = dict(L_UpperArm=[("y", -60), ("x", -18)], L_LowerArm=[("z", -98)])


def sec(t):
    return max(1, round(t * A.fps) + 1)


def talk(f, amt=1.0):
    """Mouth flaps on twos; not lip-synced to the words."""
    k = (f // 3) % 6
    return [{"MTH_A": 0.5}, {"MTH_I": 0.4}, {"MTH_O": 0.45}, {"MTH_A": 0.25}, {"MTH_E": 0.35}, {}][k] if amt else {}


# ---- shot: greet ("Mga ka-Indio, tsaa time.") — turns to the viewer and raises a cup
def shot_greet():
    cupA = dict(R_UpperArm=[("y", 70), ("x", 12)], R_LowerArm=[("z", 72)])
    toast = dict(R_Shoulder=[("y", -4)], R_UpperArm=[("y", 52), ("x", 30)], R_LowerArm=[("z", 84)])
    a0 = P(yaw=38, fR=0.62, fL=0.35, C_Head=[("z", 22)], C_Neck=[("z", 8)], C_Spine=[("x", -2)],
           L_UpperArm=[("y", -72)], L_LowerArm=[("z", -14)], **cupA)
    a1 = P(yaw=6, fR=0.62, fL=0.35, hips=(0, 0, -0.01), C_Head=[("z", -6), ("y", -5)], C_Chest=[("z", -4)],
           L_UpperArm=[("y", -72)], L_LowerArm=[("z", -14)], **cupA)
    a2 = P(yaw=2, fR=0.62, fL=1.0, hips=(0.02, 0.02, -0.02), C_Head=[("z", -4), ("y", 9), ("x", 3)], C_Chest=[("x", 3), ("z", 5)],
           C_Spine=[("y", -3)], **HIP_L, **toast)
    a3 = dict(a2)
    a3.update({"J_Bip_R_UpperArm": [("y", 46), ("x", 38)], "J_Bip_R_LowerArm": [("z", 90)], "_hips": Vector((0.02, 0.03, 0.0))})
    a4 = dict(a2)
    a4.update({"J_Bip_C_Head": [("z", -2), ("y", 6), ("x", 0)], "_hips": Vector((0.02, 0.02, -0.03))})
    tl = [(1, a0, None), (sec(0.2), a0, ease_io), (sec(0.6), a1, ease_io), (sec(1.05), a2, ease_in), (sec(1.2), a3, ease_out),
          (sec(1.5), a2, ease_io), (END, a4, ease_io)]

    def expr(f):
        e = {"BRW_Joy": 0.7, "MTH_Joy": 0.3}
        if sec(0.25) <= f:
            e.update(talk(f))
        if sec(1.05) <= f <= sec(1.7):
            e = {"BRW_Joy": 1.0, "EYE_Joy": 1.0, "MTH_Joy": 0.8}
        return e

    cams = [(1, (0.55, 2.35, 1.30), (0, 0, 1.22), 45), (sec(1.0), (0.42, 2.0, 1.32), (0.02, 0, 1.27), 45),
            (END, (0.34, 1.78, 1.34), (0.03, 0, 1.30), 45)]
    return dict(tl=tl, expr=expr, cams=cams, stance=NARROW, ones=(sec(0.95), sec(1.3)), fx={})


# ---- shot: twist ("Pero eto ang plot twist.") — back to camera, snaps round, impact frame
def shot_twist():
    hit = sec(0.5)
    t0 = P(yaw=168, fR=0.25, fL=0.25, C_Head=[("x", -4)], **ARMS_DOWN)
    t1 = P(yaw=80, fR=0.2, fL=0.2, hips=(0, 0, -0.07), C_Head=[("z", -38)], C_Neck=[("z", -14)], C_Chest=[("z", -16)],
           R_UpperArm=[("y", 58)], R_LowerArm=[("z", 30)], L_UpperArm=[("y", -58)], L_LowerArm=[("z", -30)])
    flare = dict(R_UpperArm=[("y", 58), ("x", 22)], R_LowerArm=[("z", 112)], R_Hand=[("y", -20)],
                 L_UpperArm=[("y", -58), ("x", 22)], L_LowerArm=[("z", -112)], L_Hand=[("y", 20)])
    t2 = P(yaw=-8, fR=0.06, fL=0.06, hips=(0, -0.06, -0.09), C_Spine=[("x", 8)], C_Chest=[("x", 6)], C_Head=[("x", -6), ("z", 6)],
           R_Shoulder=[("y", -14)], L_Shoulder=[("y", 14)], **flare)
    t3 = P(yaw=-10, fR=0.0, fL=0.0, hips=(0, -0.09, -0.06), C_Spine=[("x", 13)], C_Chest=[("x", 9)], C_Head=[("x", -10), ("z", 6)],
           R_Shoulder=[("y", -20)], L_Shoulder=[("y", 20)], R_UpperArm=[("y", 48), ("x", 28)], R_LowerArm=[("z", 124)],
           R_Hand=[("y", -30)], L_UpperArm=[("y", -48), ("x", 28)], L_LowerArm=[("z", -124)], L_Hand=[("y", 30)])
    t4 = P(yaw=-8, fR=0.1, fL=0.1, hips=(0, -0.05, -0.08), C_Spine=[("x", 6)], C_Chest=[("x", 5)], C_Head=[("x", -5), ("z", 5)],
           R_Shoulder=[("y", -12)], L_Shoulder=[("y", 12)], **flare)
    t5 = dict(t4)
    t5.update({"_hips": Vector((0, -0.03, -0.10)), "J_Bip_C_Head": [("x", -8), ("z", 3)]})
    tl = [(1, t0, None), (hit - 7, t0, ease_io), (hit - 3, t1, ease_in), (hit, t2, ease_out), (hit + 3, t3, ease_out),
          (hit + 11, t4, ease_io), (END, t5, ease_io)]

    def expr(f):
        if f < hit - 2:
            return {}
        return {"BRW_Surprised": 1.0, "EYE_Surprised": 1.0, "MTH_Surprised": 0.5, "MTH_O": 0.35 if f < hit + 16 else 0.15}

    cams = [(1, (0.35, 2.75, 1.32), (0, 0, 1.2), 42), (hit - 1, (0.3, 2.65, 1.32), (0, 0, 1.22), 42),
            (hit + 3, (0.16, 1.42, 1.36), (0.0, 0, 1.44), 34), (END, (0.10, 1.22, 1.38), (0.0, 0, 1.45), 34)]
    fx = dict(Flash=[(1, 0), (hit - 1, 0), (hit, 1), (hit + 1, 1), (hit + 2, 0), (END, 0)],
              Lines=[(1, 0), (hit + 1, 0), (hit + 2, 1), (hit + 22, 1), (hit + 34, 0), (END, 0)])
    return dict(tl=tl, expr=expr, cams=cams, stance=NARROW, ones=(hit - 8, hit + 6), fx=fx, shake=(hit + 2, 14, 0.05),
                whip=(hit - 6, hit + 8))


# ---- shot: point ("Kaya ikaw, ka-Indio, i-comment mo.") — lunges and points at the viewer
def shot_point():
    hit = sec(0.75)
    hipR = dict(R_UpperArm=[("y", 60), ("x", -18)], R_LowerArm=[("z", 98)])
    q0 = P(yaw=22, C_Spine=[("x", 4)], C_Head=[("z", -18), ("y", -6)], **hipR, **HIP_L)
    q1 = P(yaw=36, hips=(0, -0.05, -0.08), C_Spine=[("x", 2), ("z", -10)], C_Chest=[("z", -12)], C_Head=[("z", -22)],
           R_UpperArm=[("y", 62), ("x", -40)], R_LowerArm=[("z", 122)], **HIP_L)
    aim_arm = dict(R_Shoulder=[("z", 12)], R_UpperArm=[("z", 64), ("x", 17)], R_LowerArm=[("z", 3)], R_Hand=[])
    q2 = P(yaw=-6, point=True, hips=(0.0, 0.13, -0.11), C_Hips=[("x", -6)], C_Spine=[("x", -9), ("z", 8)], C_Chest=[("x", -6), ("z", 8)],
           C_Neck=[("x", 6)], C_Head=[("x", 9), ("z", -8)], L_UpperArm=[("y", -58), ("x", -36)], L_LowerArm=[("z", -104)], **aim_arm)
    q3 = dict(q2)
    q3.update({"_hips": Vector((0.0, 0.19, -0.12)), "J_Bip_R_UpperArm": [("z", 68), ("x", 20)], "J_Bip_C_Spine": [("x", -13), ("z", 10)]})
    q4 = dict(q2)
    q4.update({"_hips": Vector((0.0, 0.11, -0.13)), "J_Bip_C_Head": [("x", 7), ("z", -8), ("y", 7)]})
    tl = [(1, q0, None), (hit - 13, q0, ease_io), (hit - 4, q1, ease_io), (hit, q2, ease_in), (hit + 3, q3, ease_out),
          (hit + 10, q2, ease_io), (END, q4, ease_io)]

    def expr(f):
        e = {"BRW_Fun": 0.6, "BRW_Angry": 0.35, "MTH_Fun": 0.6}
        e.update(talk(f))
        if f >= sec(2.0):
            e.update(EYE_Close_L=1.0, MTH_Fun=1.0)
        return e

    def extra(f, p):  # two small jabs on "i-comment mo"
        if f > hit + 12:
            k = max(0.0, math.sin((f - hit - 12) * 2 * math.pi / (0.55 * A.fps)))
            p["J_Bip_R_LowerArm"] = Quaternion(X, math.radians(-7 * k)) @ p["J_Bip_R_LowerArm"]
            p["_hips"] = p["_hips"] + Vector((0, 0.02 * k, 0))

    cams = [(1, (0.75, 2.55, 1.30), (0, 0, 1.2), 42), (hit - 3, (0.62, 2.35, 1.28), (0, 0.1, 1.22), 42),
            (hit + 2, (0.30, 1.72, 1.24), (-0.02, 0.2, 1.33), 24), (END, (0.27, 1.60, 1.26), (-0.02, 0.2, 1.34), 24)]
    fx = dict(Lines=[(1, 0), (hit - 1, 0), (hit, 1), (hit + 16, 1), (hit + 26, 0), (END, 0)])
    return dict(tl=tl, expr=expr, cams=cams, stance=NARROW, ones=(hit - 6, hit + 6), fx=fx, shake=(hit, 10, 0.035), extra=extra)


# ---- shot: powerup (follow line) — coils, drives a fist up, gold aura
def shot_powerup():
    hit = sec(1.15)
    coil = P(hips=(0, -0.02, -0.13), C_Hips=[("x", -6)], C_Spine=[("x", -10)], C_Chest=[("x", -9)], C_UpperChest=[("x", -5)],
             C_Neck=[("x", -6)], C_Head=[("x", -6)],
             R_UpperArm=[("y", 62), ("x", 8)], R_LowerArm=[("z", 78)], L_UpperArm=[("y", -62), ("x", 8)], L_LowerArm=[("z", -78)])
    wind = P(hips=(0.03, -0.05, -0.23), C_Hips=[("x", -8), ("z", -10)], C_Spine=[("x", -12), ("z", -10)], C_Chest=[("x", -8), ("z", -10)],
             C_UpperChest=[("x", -4), ("z", -6)], C_Neck=[("x", -4), ("z", 14)], C_Head=[("x", -4), ("z", 18)],
             R_Shoulder=[("y", 8)], R_UpperArm=[("y", 74), ("x", -34)], R_LowerArm=[("z", 112)],
             L_UpperArm=[("y", -50), ("x", 28)], L_LowerArm=[("z", -70)])
    strike = P(hips=(-0.02, 0.02, -0.03), C_Hips=[("x", 4), ("z", 8)], C_Spine=[("x", 7), ("z", 6)], C_Chest=[("x", 8), ("z", 5)],
               C_UpperChest=[("x", 6), ("z", 4)], C_Neck=[("x", 6)], C_Head=[("x", 9), ("z", -6)],
               R_Shoulder=[("y", -22)], R_UpperArm=[("y", -76), ("x", -6)], R_LowerArm=[("z", 12)], R_Hand=[("z", 10)],
               L_Shoulder=[("y", -6)], L_UpperArm=[("y", -66), ("x", -26)], L_LowerArm=[("z", -104)])
    over = P(hips=(-0.02, 0.03, 0.0), C_Hips=[("x", 6), ("z", 10)], C_Spine=[("x", 11), ("z", 7)], C_Chest=[("x", 11), ("z", 6)],
             C_UpperChest=[("x", 8), ("z", 5)], C_Neck=[("x", 14)], C_Head=[("x", 22), ("z", -6)],
             R_Shoulder=[("y", -28)], R_UpperArm=[("y", -88), ("x", -12)], R_LowerArm=[("z", 4)], R_Hand=[("z", 6)],
             L_Shoulder=[("y", -8)], L_UpperArm=[("y", -70), ("x", -34)], L_LowerArm=[("z", -112)])
    hold = P(hips=(-0.02, 0.01, -0.06), C_Hips=[("x", 3), ("z", 8)], C_Spine=[("x", 6), ("z", 6)], C_Chest=[("x", 7), ("z", 5)],
             C_UpperChest=[("x", 5), ("z", 4)], C_Neck=[("x", 3)], C_Head=[("x", 3), ("z", -8)],
             R_Shoulder=[("y", -22)], R_UpperArm=[("y", -74), ("x", -4)], R_LowerArm=[("z", 20)], R_Hand=[("z", 10)],
             L_Shoulder=[("y", -6)], L_UpperArm=[("y", -64), ("x", -24)], L_LowerArm=[("z", -100)])
    hold2 = dict(hold)
    hold2.update({"_hips": Vector((-0.02, 0.0, -0.10)), "J_Bip_C_Head": [("x", -5), ("z", -12)], "J_Bip_C_Neck": [],
                  "J_Bip_R_LowerArm": [("z", 30)]})
    tl = [(1, coil, None), (hit - 20, coil, ease_io), (hit - 6, wind, ease_io), (hit, strike, ease_in), (hit + 4, over, ease_out),
          (hit + 11, hold, ease_io), (END, hold2, ease_io)]

    def expr(f):
        e = {"BRW_Angry": 1.0, "EYE_Angry": 0.55}
        if f < hit - 1:
            e.update(talk(f))
        elif f < hit + 12:
            e.update(MTH_A=1.0)
        else:
            e.update(MTH_A=0.8 + 0.2 * math.sin(f * 1.3), MTH_O=0.15)
        return e

    cams = [(1, (0.85, 2.75, 0.70), (0.0, 0, 0.95), 50), (hit - 6, (0.45, 2.20, 0.55), (0.0, 0, 0.98), 50),
            (hit - 1, (0.35, 2.10, 0.52), (0.0, 0, 1.05), 50), (hit + 4, (-0.70, 3.55, 0.24), (0.02, 0, 1.22), 32),
            (END, (-0.95, 2.30, 0.42), (0.03, 0, 1.42), 40)]
    fx = dict(Flash=[(1, 0), (hit - 1, 0), (hit, 1), (hit + 1, 1), (hit + 2, 0), (END, 0)],
              Aura=[(1, 0), (hit + 1, 0), (hit + 2, 0.75), (hit + 6, 1.3), (hit + 13, 1.0), (END, 1.08)],
              Lines=[(1, 0), (hit + 1, 0), (hit + 2, 1), (hit + 26, 1), (hit + 40, 0), (END, 0)])
    return dict(tl=tl, expr=expr, cams=cams, stance=WIDE, ones=(hit - 6, hit + 6), fx=fx, shake=(hit + 2, 16, 0.07), burn=hit + 1)


SH = dict(greet=shot_greet, twist=shot_twist, point=shot_point, powerup=shot_powerup)[SHOT]()
TIMELINE = SH["tl"]
POSED = sorted({k for _, p, _ in TIMELINE for k in p if not k.startswith("_")})


def pose_at(f):
    for (fa, pa, _), (fb, pb_, e) in zip(TIMELINE, TIMELINE[1:]):
        if fa <= f <= fb:
            t = e((f - fa) / (fb - fa)) if fb > fa else 0
            out = {k: quat(pa.get(k, [])).slerp(quat(pb_.get(k, [])), t) for k in POSED}
            out["_hips"] = pa["_hips"].lerp(pb_["_hips"], t)
            out["_yaw"] = pa["_yaw"] + (pb_["_yaw"] - pa["_yaw"]) * t
            return out
    raise ValueError(f)


ST = SH["stance"]
LEGS = {}
for side, sx in (("R", 1), ("L", -1)):
    th, sh, ft = (bone("J_Bip_%s_%s" % (side, n)) for n in ("UpperLeg", "LowerLeg", "Foot"))
    LEGS[side] = dict(th=th, sh=sh, ft=ft, l1=(sh.head - th.head).length, l2=(ft.head - sh.head).length,
                      d1=(sh.head - th.head).normalized(), d2=(ft.head - sh.head).normalized(),
                      ankle=Vector((sx * ST["x"], ST["yl"] if side == "L" else ST["yr"], ft.head.z)),
                      knee=Vector((sx * 0.55, 1.0, 0)).normalized(), yaw=-sx * (ST["yawr"] if side == "R" else ST["yawl"]))


def solve_leg(L):
    """Two-bone IK by hand so the feet stay planted while the hips drop, shift and twist."""
    hip = L["th"].head.copy()
    to = L["ankle"] - hip
    d = min(to.length, (L["l1"] + L["l2"]) * 0.999)
    n = to.normalized()
    a = (L["l1"] ** 2 - L["l2"] ** 2 + d * d) / (2 * d)
    h = math.sqrt(max(L["l1"] ** 2 - a * a, 0))
    side = (L["knee"] - n * L["knee"].dot(n)).normalized()
    knee = hip + n * a + side * h
    set_abs(L["th"], L["d1"].rotation_difference((knee - hip).normalized()))
    bpy.context.view_layer.update()
    set_abs(L["sh"], L["d2"].rotation_difference((hip + n * d - knee).normalized()))
    bpy.context.view_layer.update()
    set_abs(L["ft"], Quaternion(Z, math.radians(L["yaw"])))


arm.rotation_mode = "XYZ"
hips_pb = bone("J_Bip_C_Hips")
HIPS_R = hips_pb.bone.matrix_local.to_3x3().inverted()
prefs = bpy.context.preferences.edit


def set_expr(vals, f):
    w = {EXPR[k]: v for k, v in vals.items()}
    for i, kb in enumerate(KEYS[1:]):
        kb.value = w.get(i, 0.0)
        kb.keyframe_insert("value", frame=f)


# character keys: on twos, on ones through the fast part
o0, o1 = SH["ones"]
last_key = TIMELINE[-2][0]
burn_at = SH.get("burn", 10 ** 6)
whip = SH.get("whip", (0, -1))
char_frames = [f for f in range(1, END + 1) if f % 2 == 1 or o0 <= f <= o1]
prefs.keyframe_new_interpolation_type = "CONSTANT"
for f in char_frames:
    p = pose_at(f)
    if "extra" in SH:
        SH["extra"](f, p)
    if f > last_key and SHOT in ("powerup", "twist"):  # held pose stays alive: strain tremble
        k = 1 if (f // 2) % 2 else -1
        p["J_Bip_R_UpperArm"] = Quaternion(Y, math.radians(1.6 * k)) @ p["J_Bip_R_UpperArm"]
        p["J_Bip_C_Chest"] = Quaternion(Z, math.radians(0.8 * k)) @ p["J_Bip_C_Chest"]
        p["J_Bip_C_Head"] = Quaternion(X, math.radians(0.9 * k)) @ p["J_Bip_C_Head"]
    for name in POSED:
        set_rel(bone(name), p[name])
    hips_pb.location = HIPS_R @ p["_hips"]
    arm.rotation_euler = (0, 0, math.radians(p["_yaw"]))
    arm.keyframe_insert("rotation_euler", frame=f)
    bpy.context.view_layer.update()
    for L in LEGS.values():
        solve_leg(L)
    bpy.context.view_layer.update()
    for name in POSED + [L[k].name for L in LEGS.values() for k in ("th", "sh", "ft")]:
        bone(name).keyframe_insert("rotation_quaternion", frame=f)
    hips_pb.keyframe_insert("location", frame=f)
    set_expr(SH["expr"](f), f)
    # cloth: hangs and sways, whips out on a spin, streams up in the aura
    burn, wh = f >= burn_at, whip[0] <= f <= whip[1]
    for i, t in enumerate(tails):
        flick = math.sin(f * 0.75 + i * 1.7)
        if burn:
            d = Vector((0.25 - 0.3 * i, -0.75, 0.55 + 0.25 * flick + 0.2 * i))
        elif wh:
            d = Vector((-0.9, -0.35 - 0.2 * i, 0.15 + 0.2 * flick))
        else:
            d = Vector((0.12 - 0.2 * i + 0.05 * flick, -0.45, -0.85))
        t.rotation_quaternion = aim(d, 25 * flick if (burn or wh) else 0)
        t.keyframe_insert("rotation_quaternion", frame=f)
        t.modifiers["Wave"].height = 0.05 if (burn or wh) else 0.014
        t.modifiers["Wave"].keyframe_insert("height", frame=f)
    flick = math.sin(f * 0.65)
    if burn:
        d = Vector((-0.55 - 0.15 * flick, 0.25, 0.25 + 0.2 * flick))
    elif wh:
        d = Vector((-0.8, 0.3, -0.35))
    else:
        d = Vector((-0.08 + 0.03 * flick, 0.10, -1))
    sash_tail.rotation_quaternion = aim(d, 20 * flick if burn else 0)
    sash_tail.keyframe_insert("rotation_quaternion", frame=f)
    sash_tail.modifiers["Wave"].height = 0.06 if (burn or wh) else 0.012
    sash_tail.modifiers["Wave"].keyframe_insert("height", frame=f)
    wv.height = 0.016 if burn else (0.008 if wh else 0.0)
    wv.keyframe_insert("height", frame=f)
    fx.nodes["Time"].outputs[0].default_value = f / A.fps
    fx.nodes["Time"].outputs[0].keyframe_insert("default_value", frame=f)
    for fl in torches:
        fl.scale = (random.uniform(0.8, 1.2), 1, random.uniform(0.75, 1.3))
        fl.keyframe_insert("scale", frame=f)

# FX, camera: linear / smooth keys on ones
prefs.keyframe_new_interpolation_type = "LINEAR"
for node in ("Flash", "Aura", "Lines"):
    for f, v in SH["fx"].get(node, [(1, 0), (END, 0)]):
        fx.nodes[node].outputs[0].default_value = v
        fx.nodes[node].outputs[0].keyframe_insert("default_value", frame=f)
if sparks:
    for o, x, y, period, phase in sparks:
        f = burn_at - phase
        while f < END + period:
            for ff, z in ((f, -0.3), (f + period - 1, 3.6)):
                o.location = (x, y, z)
                o.keyframe_insert("location", frame=ff)
            f += period
        for ff, sc in ((1, 0), (burn_at, 0), (burn_at + 1, 1)):
            o.scale = (sc, sc, sc)
            o.keyframe_insert("scale", frame=ff)
    for f, sc in ((1, 0), (burn_at, 0), (burn_at + 1, 0.5), (burn_at + 16, 5.5), (burn_at + 17, 0), (END, 0)):
        ring.scale = (sc, sc, 1)
        ring.keyframe_insert("scale", frame=f)

prefs.keyframe_new_interpolation_type = "BEZIER"
for f, loc, look, lens in SH["cams"]:
    cam.location, tgt.location, cam_data.lens = loc, look, lens
    cam.keyframe_insert("location", frame=f)
    tgt.keyframe_insert("location", frame=f)
    cam_data.keyframe_insert("lens", frame=f)
if "shake" in SH:  # impact shake rides on a delta so it does not disturb the move
    s0, sl, samp = SH["shake"]
    for f in range(s0 - 2, s0 + sl + 3):
        amp = 0.0 if f < s0 or f > s0 + sl else samp * (1 - (f - s0) / sl)
        tgt.delta_location = (random.uniform(-amp, amp), 0, random.uniform(-amp, amp))
        tgt.keyframe_insert("delta_location", frame=f)

# ---------------------------------------------------------------- render
S.frame_start, S.frame_end = 1, END
S.render.fps = A.fps
S.render.resolution_x, S.render.resolution_y, S.render.resolution_percentage = 720, 1280, A.scale
S.render.image_settings.file_format = "PNG"
S.render.image_settings.color_mode = "RGB"
S.render.image_settings.compression = 15
S.view_settings.view_transform = "Standard"
S.world = bpy.data.worlds.new("W")
S.render.engine = A.engine
if A.engine == "CYCLES":
    c = S.cycles
    c.device, c.samples, c.use_denoising, c.use_adaptive_sampling = "CPU", A.samples, False, False
    c.max_bounces, c.diffuse_bounces, c.glossy_bounces, c.transmission_bounces = 0, 0, 0, 0
    c.transparent_max_bounces = 24
    c.pixel_filter_type, c.filter_width = "BLACKMAN_HARRIS", 1.3
    S.render.use_persistent_data = True
    S.render.threads_mode = "AUTO"
else:
    S.eevee.taa_render_samples = A.samples
if A.save:
    bpy.ops.wm.save_as_mainfile(filepath=A.save)

os.makedirs(A.out, exist_ok=True)
times = []
for f in range(F0, F1 + 1, A.step):
    S.frame_set(f)
    S.render.filepath = os.path.join(A.out, "f%04d.png" % f)
    t = time.time()
    bpy.ops.render.render(write_still=True)
    times.append(time.time() - t)
    print("FRAME %d %.2fs" % (f, times[-1]), flush=True)
steady = times[1:] or times
print("TIMING shot=%s engine=%s samples=%d frames=%d first=%.2fs mean_after_first=%.2fs total=%.1fs" % (
    SHOT, A.engine, A.samples, len(times), times[0], sum(steady) / len(steady), sum(times)), flush=True)
