"""Render the 3D shots of episode 6 as transparent PNG frames plus label anchors (pixel positions).
usage: python3 render_episode.py EP_DIR OUTDIR [shot,shot] [step]"""
import bpy, sys, os, json, math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib, importlib.util
_sp = importlib.util.spec_from_file_location('spec', os.path.join(sys.argv[1], 'spec.py')); SPEC = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(SPEC)
sys.argv = sys.argv[1:]
draisine = importlib.import_module(SPEC.MODEL)
OUT = sys.argv[1]; ONLY = sys.argv[2].split(',') if len(sys.argv) > 2 and sys.argv[2] else None
STEP = int(sys.argv[3]) if len(sys.argv) > 3 else 1
W, H, FPS = 720, 1280, 24
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
B = draisine.build()
# no ground plane: the ground shadow is drawn in compose.py (a full-frame shadow catcher made frames 3x slower)
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(50), 0, math.radians(35)))
bpy.context.object.data.energy = 4.0; bpy.context.object.data.angle = 0.12
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (0.95, 0.93, 0.9, 1); bg.inputs[1].default_value = 0.9
cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
cd.lens = 50; cd.shift_y = -0.10      # subject sits above centre, captions go below
r = sc.render; r.engine = 'CYCLES'; r.resolution_x, r.resolution_y = W, H; r.film_transparent = True
sc.cycles.samples = 12; sc.cycles.use_denoising = False; sc.cycles.max_bounces = 1; sc.cycles.device = 'CPU'
sc.cycles.use_adaptive_sampling = False
sc.view_settings.view_transform = 'Standard'; r.image_settings.file_format = 'PNG'; r.image_settings.color_mode = 'RGBA'
r.image_settings.compression = 30; r.use_persistent_data = True

def ease(u): return u * u * (3 - 2 * u)
def out(u): return 1 - (1 - u) ** 3
D = math.radians
# each shot: n frames and f(u) -> dict(rot, el, dist, target(bike space), steer, spin_f, spin_r, explode)
SHOTS = SPEC.shots(ease, out)

for name, n, fn in SHOTS:
    if ONLY and name not in ONLY: continue
    d = os.path.join(OUT, name); os.makedirs(d, exist_ok=True); anchors = {}
    for i in range(0, n, STEP):
        fp = os.path.join(d, f'{i:04d}.png')
        p = fn(i / n if name == 'ride' else i / max(1, n - 1))
        B['root'].rotation_euler = (0, 0, D(p['rot']))
        B['steer'].rotation_euler = (0, 0, D(p.get('steer', 0)))
        B['parts']['front_wheel'].rotation_euler = (0, D(-p.get('spin_f', 0)), 0)
        B['parts']['rear_wheel'].rotation_euler = (0, D(-p.get('spin_r', 0)), 0)
        B['explode'](p.get('explode', 0))
        bpy.context.view_layer.update()
        t = B['root'].matrix_world @ Vector(p['target']); el = D(p['el'])
        cam.location = t + p['dist'] * Vector((0, -math.cos(el), math.sin(el)))
        cam.rotation_euler = (t - cam.location).to_track_quat('-Z', 'Y').to_euler()
        bpy.context.view_layer.update()
        a = {}
        for k, e in B['anchors'].items():
            v = world_to_camera_view(sc, cam, e.matrix_world.translation)
            a[k] = [round(v.x * W, 1), round((1 - v.y) * H, 1)]
        anchors[i] = a
        if not os.path.exists(fp):
            r.filepath = fp; bpy.ops.render.render(write_still=True)
    json.dump(anchors, open(os.path.join(d, 'anchors.json'), 'w'))
    print('SHOT', name, 'done', flush=True)
