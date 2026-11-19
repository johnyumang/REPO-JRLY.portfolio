"""Render the 3D shots of episode 2 as transparent PNG frames plus label anchors (pixel positions).
usage: python3 render.py OUTDIR [shot,shot] [step]"""
import bpy, sys, os, json, math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import velocipede as draisine
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
def hook(u): return dict(rot=-150 + 190 * out(u), el=10, dist=6.4 - 0.8 * out(u), target=(0, 0, 0.60), spin_f=-120 * u)
def turn(u): return dict(rot=40 + 360 * u, el=6 + 22 * math.sin(math.pi * u) ** 2, dist=5.2, target=(0, 0, 0.60))
def pedals(u): return dict(rot=-62 + 16 * u, el=10, dist=2.7 - 0.3 * ease(u), target=(0.50, 0, 0.52), spin_f=-540 * u)
def spring(u): return dict(rot=-8 + 14 * u, el=10, dist=2.8 - 0.3 * ease(u), target=(0.0, 0, 0.82))
def brake(u): return dict(rot=-150 + 14 * u, el=16, dist=1.9 - 0.25 * ease(u), target=(-0.62, 0, 0.66), spin_r=-(900 * u - 450 * u * u))
def tyres(u): return dict(rot=12 + 10 * u, el=6, dist=3.0 - 0.3 * ease(u), target=(0.50, 0, 0.50), spin_f=-160 * u)
def explode(u): return dict(rot=28 + 22 * u, el=14, dist=6.3, target=(0, 0, 0.75), explode=ease(min(1, u / 0.3)))
def ride(u): return dict(rot=0, el=2.5, dist=6.2, target=(0, 0, 0.98), spin_f=-360 * u, spin_r=-360 * u * 0.45 / 0.39)
SHOTS = [('hook', 72, hook), ('turn', 168, turn), ('pedals', 144, pedals), ('spring', 144, spring),
         ('brake', 144, brake), ('tyres', 144, tyres), ('explode', 192, explode), ('ride', 16, ride)]

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
