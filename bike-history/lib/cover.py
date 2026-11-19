"""One cover photo per episode: our 3D bike rendered in Cycles over an empty AI-made background (FLUX on the free
NVIDIA endpoint; image models cannot draw old bikes correctly, so the bike itself is always our model).
usage: python3 cover.py MODEL_MODULE "BACKGROUND PROMPT" OUT.jpg [yaw_degrees]
Output 1920x1080 JPEG, bike in the right half, space on the left for the title."""
import sys, os, math, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
MOD, PROMPT, OUT = sys.argv[1], sys.argv[2], sys.argv[3]; YAW = float(sys.argv[4]) if len(sys.argv) > 4 else -28
tmp = tempfile.mkdtemp(); bike_png, bg_jpg = os.path.join(tmp, 'bike.png'), os.path.join(tmp, 'bg.jpg')
RENDER = f'''
import bpy, sys, math
from mathutils import Vector
sys.path.insert(0, {HERE!r}); import {MOD} as M
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
B = M.build(); B['root'].rotation_euler = (0, 0, math.radians({YAW})); B['steer'].rotation_euler = (0, 0, math.radians(8))
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(62), 0, math.radians(-70)))
L = bpy.context.object.data; L.energy = 4.5; L.color = (1, 0.88, 0.72); L.angle = 0.08
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (0.85, 0.80, 0.74, 1); bg.inputs[1].default_value = 0.7
bpy.ops.mesh.primitive_plane_add(size=30); bpy.context.object.is_shadow_catcher = True
cd = bpy.data.cameras.new('c'); cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 50
t = Vector((0, 0, 0.5)); cam.location = t + Vector((0.0, -6.4, 0.75)); cam.rotation_euler = (t - cam.location).to_track_quat('-Z', 'Y').to_euler()
cd.shift_x = -0.17; cd.shift_y = 0.10
r = sc.render; r.engine = 'CYCLES'; r.resolution_x, r.resolution_y = 1920, 1080; r.film_transparent = True
sc.cycles.samples = 64; sc.cycles.use_denoising = True; sc.cycles.max_bounces = 3; sc.view_settings.view_transform = 'Standard'
r.image_settings.color_mode = 'RGBA'; r.filepath = {bike_png!r}; bpy.ops.render.render(write_still=True)
'''
subprocess.run([sys.executable, '-c', RENDER], check=True, capture_output=True)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'history-indio', 'pipeline'))
from nvidia_still import call
ok = False                                      # the filter sometimes blocks a prompt: retry plainer wording
for p in (PROMPT + ' Empty scene, nobody in it. No text.', PROMPT):
    for model in ('black-forest-labs/flux-3-image-klein', 'black-forest-labs/flux.2-klein-4b'):
        ok = ok or call(model, {'prompt': p, 'width': 1344, 'height': 768}, bg_jpg)
if not ok: sys.exit('no background came back: reword the prompt')
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageChops
bike = Image.open(bike_png).convert('RGBA'); a = bike.getchannel('A')
rgb = ImageEnhance.Color(ImageEnhance.Brightness(bike.convert('RGB')).enhance(0.80)).enhance(0.85)
rgb = ImageChops.multiply(rgb, Image.new('RGB', rgb.size, (255, 236, 210)))
solid = a.point(lambda v: 255 if v > 200 else 0); shade = a.point(lambda v: int(v * 0.8) if v <= 200 else 0)
bb = solid.getbbox()
bg = Image.open(bg_jpg).convert('RGB').resize((1920, 1080), Image.LANCZOS)
m = Image.new('L', (1920, 1080), 0); y = bb[3] - 6
ImageDraw.Draw(m).ellipse([bb[0] - 30, y - 22, bb[2] + 30, y + 26], fill=120)
m = ImageChops.lighter(m.filter(ImageFilter.GaussianBlur(18)), shade.filter(ImageFilter.GaussianBlur(3)))
out = Image.composite(Image.new('RGB', bg.size, (35, 28, 22)), bg, m)
k = Image.merge('RGBA', (*rgb.filter(ImageFilter.GaussianBlur(0.6)).split(), solid.filter(ImageFilter.GaussianBlur(0.7))))
out.paste(k, (0, 0), k)
out = Image.blend(out, ImageChops.screen(out, Image.new('RGB', out.size, (255, 214, 160))), 0.06)
out.save(OUT, quality=93); print('cover', OUT, 'bike bbox', bb)
