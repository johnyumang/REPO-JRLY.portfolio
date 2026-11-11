"""History Indio — Blender proof shot: the host raises a fist and shouts (4 s, 24 fps, 720x1280).

Runs headless with the `bpy` wheel, CPU only:
    python host_shot.py --model host.glb --out frames/ [--engine CYCLES|BLENDER_EEVEE] [--frames 1-96]

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
ap.add_argument("--frames", default="1-96")
ap.add_argument("--step", type=int, default=1)
ap.add_argument("--scale", type=int, default=100)
ap.add_argument("--save", default="")
ap.add_argument("--closeup", action="store_true", help="debug: frame the head")
A = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])
F0, F1 = [int(x) for x in A.frames.split("-")]
END = 96
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
SHADOW = (0.50, 0.40, 0.62)                       # cool dusk shadow multiplier
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
PAL = dict(indigo=(0.030, 0.022, 0.15), red=(0.62, 0.03, 0.03), hair=(0.006, 0.006, 0.012),
           pants=(0.42, 0.33, 0.22), sandal=(0.10, 0.05, 0.03), gold=(0.95, 0.62, 0.10))


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


# ---------------------------------------------------------------- set: sky, ground, aura, lines
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


def sky_mat():
    m, nt, out, g = new_mat("HI_Sky")
    u, v = uv_xy(nt)
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    e = ramp.color_ramp.elements
    e[0].position, e[0].color = 0.0, (1.0, 0.42, 0.10, 1)
    e[1].position, e[1].color = 1.0, (0.012, 0.012, 0.09, 1)
    for pos, colr in ((0.10, (0.72, 0.13, 0.20, 1)), (0.30, (0.16, 0.05, 0.28, 1))):
        ramp.color_ramp.elements.new(pos).color = colr
    nt.links.new(v, ramp.inputs[0])
    # two-step painted clouds, stretched sideways
    cl = noise(nt, math_node(nt, "MULTIPLY", u, 5.0), math_node(nt, "MULTIPLY", v, 26.0), 3.0, 1.0, 4.0)
    cr = nt.nodes.new("ShaderNodeValToRGB")
    cr.color_ramp.interpolation = "CONSTANT"
    ce = cr.color_ramp.elements
    ce[0].position, ce[0].color = 0.0, (0, 0, 0, 1)
    ce[1].position, ce[1].color = 0.56, (0.10, 0.03, 0.07, 1)
    cr.color_ramp.elements.new(0.64).color = (0.42, 0.13, 0.10, 1)
    nt.links.new(cl, cr.inputs[0])
    add = nt.nodes.new("ShaderNodeVectorMath")
    nt.links.new(ramp.outputs[0], add.inputs[0])
    nt.links.new(cr.outputs[0], add.inputs[1])
    # sun disc near the horizon
    du = math_node(nt, "MULTIPLY", math_node(nt, "SUBTRACT", u, 0.56), 1.5)
    dv = math_node(nt, "SUBTRACT", v, 0.035)
    d = math_node(nt, "SQRT", math_node(nt, "ADD", math_node(nt, "MULTIPLY", du, du), math_node(nt, "MULTIPLY", dv, dv)))
    col = mix(nt, math_node(nt, "LESS_THAN", d, 0.035), add.outputs[0], (1.6, 1.2, 0.55, 1))
    dark = math_node(nt, "SUBTRACT", 1.0, math_node(nt, "MULTIPLY", math_node(nt, "MINIMUM", g.outputs["Aura"], 1.0), 0.62))
    sc = nt.nodes.new("ShaderNodeVectorMath")
    sc.operation = "SCALE"
    nt.links.new(col, sc.inputs[0])
    nt.links.new(dark, sc.inputs["Scale"])
    emit(nt, out, mix(nt, g.outputs["Flash"], sc.outputs[0], (1, 1, 1, 1)))
    return m


def flat_mat(name, color, darken=0.5):
    m, nt, out, g = new_mat(name)
    dark = math_node(nt, "SUBTRACT", 1.0, math_node(nt, "MULTIPLY", math_node(nt, "MINIMUM", g.outputs["Aura"], 1.0), darken))
    sc = nt.nodes.new("ShaderNodeVectorMath")
    sc.operation = "SCALE"
    sc.inputs[0].default_value = color[:3]
    nt.links.new(dark, sc.inputs["Scale"])
    emit(nt, out, mix(nt, g.outputs["Flash"], sc.outputs[0], (1, 1, 1, 1)))
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
    e[0].position, e[0].color = 0.0, (1.0, 0.16, 0.02, 1)
    e[1].position, e[1].color = 0.20, (1.0, 0.55, 0.05, 1)
    ramp.color_ramp.elements.new(0.48).color = (1.0, 0.9, 0.45, 1)
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
gm = bpy.data.meshes.new("Ground")
bm = bmesh.new()
bmesh.ops.create_circle(bm, cap_ends=True, segments=48, radius=90)
bm.to_mesh(gm)
bm.free()
ground = bpy.data.objects.new("Ground", gm)
S.collection.objects.link(ground)
gm.materials.append(flat_mat("HI_Ground", (0.10, 0.05, 0.085, 1), 0.35))
# far ridge silhouette
rv, rf, N = [], [], 60
for i in range(N + 1):
    x = -110 + 220 * i / N
    hgt = 3 + 5 * abs(math.sin(i * 0.37)) + 3 * random.random() + (9 if 8 < i < 20 else 0) * abs(math.sin(i * 0.5))
    rv += [(x, 0, 0), (x, 0, hgt)]
for i in range(N):
    rf.append((2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1))
mesh_obj("Ridge", rv, rf, flat_mat("HI_Ridge", (0.05, 0.02, 0.09, 1), 0.5)).location = (0, -66, 0)
# contact shadow blob
bv = [(0, 0, 0)] + [(0.62 * math.cos(a), 0.36 * math.sin(a), 0) for a in [2 * math.pi * i / 32 for i in range(32)]]
mesh_obj("Blob", bv, [(0, 1 + i, 1 + (i + 1) % 32) for i in range(32)], flat_mat("HI_Blob", (0.03, 0.012, 0.035, 1), 0.0)).location = (0, 0, 0.004)

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

# rising sparks and the ground shock ring
SPARK = flat_mat("HI_Spark", (1.0, 0.85, 0.35, 1), 0.0)
sparks = []
for i in range(34):
    a, r = random.uniform(0, 2 * math.pi), random.uniform(0.35, 1.25)
    h = random.uniform(0.05, 0.13)
    o = mesh_obj("Spark", [(0, 0, -h), (0.012, 0, 0), (0, 0, h), (-0.012, 0, 0), (0, 0.012, 0), (0, -0.012, 0)],
                 [(0, 1, 2, 3), (0, 4, 2, 5)], SPARK)
    sparks.append((o, r * math.cos(a), r * math.sin(a) * 0.7, random.randint(10, 20), random.randint(0, 20)))
rv, rf = [], []
for i in range(48):
    a = 2 * math.pi * i / 48
    rv += [(0.86 * math.cos(a), 0.86 * math.sin(a), 0), (math.cos(a), math.sin(a), 0)]
for i in range(48):
    j = (i + 1) % 48
    rf.append((2 * i, 2 * i + 1, 2 * j + 1, 2 * j))
ring = mesh_obj("Ring", rv, rf, flat_mat("HI_Ring", (1.0, 0.9, 0.55, 1), 0.0))
ring.location = (0, 0, 0.012)

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
    P = pb.parent.matrix.to_quaternion() @ (REST[pb.parent.name].inverted() @ R)
    pb.rotation_mode = "QUATERNION"
    pb.rotation_quaternion = P.inverted() @ (D @ R)


FINGERS = ["Index", "Middle", "Ring", "Little"]


def fist(pose, side, amt=1.0):
    s = 1 if side == "R" else -1
    for fgr in FINGERS:
        for j, deg in zip((1, 2, 3), (72, 88, 60)):
            pose["J_Bip_%s_%s%d" % (side, fgr, j)] = [("y", s * deg * amt)]
    pose["J_Bip_%s_Thumb1" % side] = [("y", s * 28 * amt), ("z", -s * 22 * amt)]
    pose["J_Bip_%s_Thumb2" % side] = [("z", -s * 30 * amt)]
    pose["J_Bip_%s_Thumb3" % side] = [("z", -s * 40 * amt)]
    return pose


def P(hips=(0, 0, 0), **bones):
    pose = {"J_Bip_" + k: v for k, v in bones.items()}
    fist(pose, "R")
    fist(pose, "L")
    pose["_hips"] = Vector(hips)
    return pose


# character right = +X, forward = +Y. +x leans back / looks up, +z turns to the character's left.
COIL = P(hips=(0, -0.02, -0.13),
         C_Hips=[("x", -6)], C_Spine=[("x", -10)], C_Chest=[("x", -9)], C_UpperChest=[("x", -5)],
         C_Neck=[("x", -12)], C_Head=[("x", -22)],
         R_UpperArm=[("y", 62), ("x", 8)], R_LowerArm=[("z", 78)],
         L_UpperArm=[("y", -62), ("x", 8)], L_LowerArm=[("z", -78)])
WIND = P(hips=(0.03, -0.05, -0.23),
         C_Hips=[("x", -8), ("z", -10)], C_Spine=[("x", -12), ("z", -10)], C_Chest=[("x", -8), ("z", -10)],
         C_UpperChest=[("x", -4), ("z", -6)], C_Neck=[("x", -4), ("z", 14)], C_Head=[("x", -4), ("z", 18)],
         R_Shoulder=[("y", 8)], R_UpperArm=[("y", 74), ("x", -34)], R_LowerArm=[("z", 112)],
         L_UpperArm=[("y", -50), ("x", 28)], L_LowerArm=[("z", -70)])
STRIKE = P(hips=(-0.02, 0.02, -0.03),
           C_Hips=[("x", 4), ("z", 8)], C_Spine=[("x", 7), ("z", 6)], C_Chest=[("x", 8), ("z", 5)],
           C_UpperChest=[("x", 6), ("z", 4)], C_Neck=[("x", 6)], C_Head=[("x", 9), ("z", -6)],
           R_Shoulder=[("y", -22)], R_UpperArm=[("y", -76), ("x", -6)], R_LowerArm=[("z", 12)], R_Hand=[("z", 10)],
           L_Shoulder=[("y", -6)], L_UpperArm=[("y", -66), ("x", -26)], L_LowerArm=[("z", -104)])
OVER = P(hips=(-0.02, 0.03, 0.0),
         C_Hips=[("x", 6), ("z", 10)], C_Spine=[("x", 11), ("z", 7)], C_Chest=[("x", 11), ("z", 6)],
         C_UpperChest=[("x", 8), ("z", 5)], C_Neck=[("x", 14)], C_Head=[("x", 22), ("z", -6)],
         R_Shoulder=[("y", -28)], R_UpperArm=[("y", -88), ("x", -12)], R_LowerArm=[("z", 4)], R_Hand=[("z", 6)],
         L_Shoulder=[("y", -8)], L_UpperArm=[("y", -70), ("x", -34)], L_LowerArm=[("z", -112)])
HOLD = P(hips=(-0.02, 0.01, -0.06),
         C_Hips=[("x", 3), ("z", 8)], C_Spine=[("x", 6), ("z", 6)], C_Chest=[("x", 7), ("z", 5)],
         C_UpperChest=[("x", 5), ("z", 4)], C_Neck=[("x", 3)], C_Head=[("x", 3), ("z", -8)],
         R_Shoulder=[("y", -22)], R_UpperArm=[("y", -74), ("x", -4)], R_LowerArm=[("z", 20)], R_Hand=[("z", 10)],
         L_Shoulder=[("y", -6)], L_UpperArm=[("y", -64), ("x", -24)], L_LowerArm=[("z", -100)])
HOLD2 = dict(HOLD)
HOLD2.update({"_hips": Vector((-0.02, 0.0, -0.10)), "J_Bip_C_Head": [("x", -5), ("z", -12)],
              "J_Bip_C_Neck": [("x", 0)], "J_Bip_R_LowerArm": [("z", 30)]})

ease_io = lambda t: t * t * (3 - 2 * t)
ease_in = lambda t: t * t * t
ease_out = lambda t: 1 - (1 - t) ** 3
TIMELINE = [(1, COIL, None), (17, COIL, ease_io), (26, WIND, ease_io), (31, STRIKE, ease_in),
            (34, OVER, ease_out), (40, HOLD, ease_io), (END, HOLD2, ease_io)]
POSED = sorted({k for _, p, _ in TIMELINE for k in p if not k.startswith("_")})


def pose_at(f):
    for (fa, pa, _), (fb, pb_, e) in zip(TIMELINE, TIMELINE[1:]):
        if fa <= f <= fb:
            t = e((f - fa) / (fb - fa)) if fb > fa else 0
            out = {k: quat(pa.get(k, [])).slerp(quat(pb_.get(k, [])), t) for k in POSED}
            out["_hips"] = pa["_hips"].lerp(pb_["_hips"], t)
            return out
    raise ValueError(f)


LEGS = {}
for side, sx in (("R", 1), ("L", -1)):
    th, sh, ft = (bone("J_Bip_%s_%s" % (side, n)) for n in ("UpperLeg", "LowerLeg", "Foot"))
    LEGS[side] = dict(th=th, sh=sh, ft=ft, l1=(sh.head - th.head).length, l2=(ft.head - sh.head).length,
                      d1=(sh.head - th.head).normalized(), d2=(ft.head - sh.head).normalized(),
                      ankle=Vector((sx * 0.27, 0.10 if side == "L" else -0.12, ft.head.z)),
                      knee=Vector((sx * 0.55, 1.0, 0)).normalized(), yaw=-sx * (30 if side == "R" else 12))


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


hips_pb = bone("J_Bip_C_Hips")
HIPS_R = hips_pb.bone.matrix_local.to_3x3().inverted()
prefs = bpy.context.preferences.edit


def set_expr(vals, f):
    w = {EXPR[k]: v for k, v in vals.items()}
    for i, kb in enumerate(KEYS[1:]):
        kb.value = w.get(i, 0.0)
        kb.keyframe_insert("value", frame=f)


def expr_at(f):
    e = {"BRW_Angry": 1.0, "EYE_Angry": 0.55}
    if f < 22:
        e.update(EYE_Close=1.0, EYE_Angry=0.0, MTH_Angry=0.6)
    elif f < 30:
        e.update(MTH_Angry=0.5, MTH_I=0.6)
    elif f < 40:
        e.update(MTH_A=1.0)
    else:
        e.update(MTH_A=0.8 + 0.2 * math.sin(f * 1.3), MTH_O=0.15)
    return e


# character keys: on twos, on ones through the strike
char_frames = [f for f in range(1, END + 1) if f % 2 == 1 or 26 <= f <= 36]
prefs.keyframe_new_interpolation_type = "CONSTANT"
for f in char_frames:
    p = pose_at(f)
    if f > 40:  # held pose stays alive: strain tremble
        k = 1 if (f // 2) % 2 else -1
        p["J_Bip_R_UpperArm"] = Quaternion(Y, math.radians(1.6 * k)) @ p["J_Bip_R_UpperArm"]
        p["J_Bip_C_Chest"] = Quaternion(Z, math.radians(0.8 * k)) @ p["J_Bip_C_Chest"]
        p["J_Bip_C_Head"] = Quaternion(X, math.radians(0.9 * k)) @ p["J_Bip_C_Head"]
    for name in POSED:
        set_rel(bone(name), p[name])
    hips_pb.location = HIPS_R @ p["_hips"]
    bpy.context.view_layer.update()
    for L in LEGS.values():
        solve_leg(L)
    bpy.context.view_layer.update()
    for name in POSED + [L[k].name for L in LEGS.values() for k in ("th", "sh", "ft")]:
        bone(name).keyframe_insert("rotation_quaternion", frame=f)
    hips_pb.keyframe_insert("location", frame=f)
    set_expr(expr_at(f), f)
    # cloth: hangs, whips back on the wind-up, then streams up in the aura
    burn = f >= 32
    for i, t in enumerate(tails):
        flick = math.sin(f * 0.9 + i * 1.7)
        d = Vector((0.25 - 0.3 * i, -0.75, 0.55 + 0.25 * flick + 0.2 * i)) if burn else \
            Vector((0.12 - 0.2 * i, -0.45, -0.85 + (0.5 if 22 <= f < 32 else 0)))
        t.rotation_quaternion = aim(d, 25 * flick if burn else 0)
        t.keyframe_insert("rotation_quaternion", frame=f)
        t.modifiers["Wave"].height = 0.05 if burn else 0.012
        t.modifiers["Wave"].keyframe_insert("height", frame=f)
    flick = math.sin(f * 0.8)
    sash_tail.rotation_quaternion = aim(Vector((-0.55 - 0.15 * flick, 0.25, 0.25 + 0.2 * flick)) if burn else Vector((-0.08, 0.10, -1)),
                                        20 * flick if burn else 0)
    sash_tail.keyframe_insert("rotation_quaternion", frame=f)
    sash_tail.modifiers["Wave"].height = 0.06 if burn else 0.01
    sash_tail.modifiers["Wave"].keyframe_insert("height", frame=f)
    wv.height = 0.016 if burn else 0.0
    wv.keyframe_insert("height", frame=f)
    fx.nodes["Time"].outputs[0].default_value = f / 24
    fx.nodes["Time"].outputs[0].keyframe_insert("default_value", frame=f)

# FX, camera: linear / smooth keys on ones
prefs.keyframe_new_interpolation_type = "LINEAR"


def key(node, pairs):
    for f, v in pairs:
        fx.nodes[node].outputs[0].default_value = v
        fx.nodes[node].outputs[0].keyframe_insert("default_value", frame=f)


key("Flash", [(1, 0), (30, 0), (31, 1), (32, 1), (33, 0), (END, 0)])
key("Aura", [(1, 0), (32, 0), (33, 0.75), (36, 1.3), (42, 1.0), (END, 1.08)])
key("Lines", [(1, 0), (32, 0), (33, 1), (52, 1), (64, 0.0), (END, 0)])
for o, x, y, period, phase in sparks:
    f = 33 - phase
    while f < END + period:
        for ff, z in ((f, -0.3), (f + period - 1, 3.6)):
            o.location = (x, y, z)
            o.keyframe_insert("location", frame=ff)
        f += period
    for ff, sc in ((1, 0), (32, 0), (33, 1)):
        o.scale = (sc, sc, sc)
        o.keyframe_insert("scale", frame=ff)
for f, sc in ((1, 0), (32, 0), (33, 0.5), (46, 5.5), (47, 0), (END, 0)):
    ring.scale = (sc, sc, 1)
    ring.keyframe_insert("scale", frame=f)

prefs.keyframe_new_interpolation_type = "BEZIER"
CAMKEYS = [  # frame, camera position, look-at, lens
    (1, (0.85, 2.75, 0.70), (0.0, 0, 0.95), 50),
    (26, (0.45, 2.20, 0.55), (0.0, 0, 0.98), 50),
    (30, (0.35, 2.10, 0.52), (0.0, 0, 1.05), 50),
    (34, (-0.70, 3.55, 0.24), (0.02, 0, 1.22), 32),
    (END, (-0.95, 2.35, 0.42), (0.03, 0, 1.42), 40),
]
for f, loc, look, lens in CAMKEYS:
    cam.location, tgt.location, cam_data.lens = loc, look, lens
    cam.keyframe_insert("location", frame=f)
    tgt.keyframe_insert("location", frame=f)
    cam_data.keyframe_insert("lens", frame=f)
# impact shake rides on a delta so it does not disturb the move
for f in range(30, 50):
    amp = 0.0 if f < 33 or f > 47 else 0.07 * (1 - (f - 33) / 15)
    tgt.delta_location = (random.uniform(-amp, amp), 0, random.uniform(-amp, amp))
    tgt.keyframe_insert("delta_location", frame=f)

# ---------------------------------------------------------------- render
if A.closeup:
    cam.animation_data_clear(); tgt.animation_data_clear(); cam_data.animation_data_clear()
    tr.target, tr.subtarget = arm, "J_Bip_C_Head"
    cam.location, cam_data.lens = (-0.2, 1.3, 1.25), 50
S.frame_start, S.frame_end = 1, END
S.render.fps = 24
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
print("TIMING engine=%s samples=%d frames=%d first=%.2fs mean_after_first=%.2fs total=%.1fs" % (
    A.engine, A.samples, len(times), times[0], sum(steady) / len(steady), sum(times)), flush=True)
