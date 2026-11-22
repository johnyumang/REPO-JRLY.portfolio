"""One cover photo per episode: our 3D bike rendered in Cycles over an empty AI-made background (FLUX on the free
NVIDIA endpoint; image models cannot draw old bikes correctly, so the bike itself is always our model).
usage: python3 cover.py MODEL_MODULE "BACKGROUND PROMPT" OUT.jpg [yaw_degrees] [v "BIG" "SMALL" "TAG"]
Default: 1920x1080, bike in the right half, space on the left. With v: the vertical thumbnail, 1080x1920,
bike in the lower half and the text drawn on top."""
import sys, os, math, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
MOD, PROMPT, OUT = sys.argv[1], sys.argv[2], sys.argv[3]; YAW = float(sys.argv[4]) if len(sys.argv) > 4 else -28
VERT = len(sys.argv) > 5 and sys.argv[5] == 'v'; TXT = sys.argv[6:9] if VERT else []
WW, HH = (1080, 1920) if VERT else (1920, 1080)
SHIFT = (0.0, 0.16) if VERT else (-0.17, 0.10)
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
cd.shift_x = {SHIFT[0]}; cd.shift_y = {SHIFT[1]}
r = sc.render; r.engine = 'CYCLES'; r.resolution_x, r.resolution_y = {WW}, {HH}; r.film_transparent = True
sc.cycles.samples = 64; sc.cycles.use_denoising = True; sc.cycles.max_bounces = 3; sc.view_settings.view_transform = 'Standard'
r.image_settings.color_mode = 'RGBA'; r.filepath = {bike_png!r}; bpy.ops.render.render(write_still=True)
'''
subprocess.run([sys.executable, '-c', RENDER], check=True, capture_output=True)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'history-indio', 'pipeline'))
from nvidia_still import call
ok = False                                      # the filter sometimes blocks a prompt: retry plainer wording
for p in (PROMPT + ' Empty scene, nobody in it. No text.', PROMPT):
    for model in ('black-forest-labs/flux-3-image-klein', 'black-forest-labs/flux.2-klein-4b'):
        ok = ok or call(model, {'prompt': p, 'width': 768 if VERT else 1344, 'height': 1344 if VERT else 768}, bg_jpg)
if not ok: sys.exit('no background came back: reword the prompt')
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageChops, ImageFont
bike = Image.open(bike_png).convert('RGBA'); a = bike.getchannel('A')
rgb = ImageEnhance.Color(ImageEnhance.Brightness(bike.convert('RGB')).enhance(0.80)).enhance(0.85)
rgb = ImageChops.multiply(rgb, Image.new('RGB', rgb.size, (255, 236, 210)))
solid = a.point(lambda v: 255 if v > 200 else 0); shade = a.point(lambda v: int(v * 0.8) if v <= 200 else 0)
bb = solid.getbbox()
bg = Image.open(bg_jpg).convert('RGB').resize((WW, HH), Image.LANCZOS)
m = Image.new('L', (WW, HH), 0); y = bb[3] - 6
ImageDraw.Draw(m).ellipse([bb[0] - 30, y - 22, bb[2] + 30, y + 26], fill=120)
m = ImageChops.lighter(m.filter(ImageFilter.GaussianBlur(18)), shade.filter(ImageFilter.GaussianBlur(3)))
out = Image.composite(Image.new('RGB', bg.size, (35, 28, 22)), bg, m)
k = Image.merge('RGBA', (*rgb.filter(ImageFilter.GaussianBlur(0.6)).split(), solid.filter(ImageFilter.GaussianBlur(0.7))))
out.paste(k, (0, 0), k)
out = Image.blend(out, ImageChops.screen(out, Image.new('RGB', out.size, (255, 214, 160))), 0.06)
if TXT:                                          # thumbnail text: big year, the machine, the series tag
    FD = os.path.join(HERE, '..', '..', 'history-indio', 'pipeline', 'fonts', 'Anton-Regular.ttf')
    sh = Image.new('L', out.size, 0); dd = ImageDraw.Draw(sh)
    lines = [(TXT[0], 300, (196, 44, 30), 380), (TXT[1], 120, (255, 248, 236), 690), (TXT[2], 64, (255, 230, 190), 120)]
    for t, sz, _, y in lines:
        dd.text((WW // 2, y), t, font=ImageFont.truetype(FD, sz), anchor='mm', fill=255)
    out = Image.composite(Image.new('RGB', out.size, (20, 14, 10)), out, sh.filter(ImageFilter.GaussianBlur(14)).point(lambda v: min(255, v * 2)))
    d2 = ImageDraw.Draw(out)
    for t, sz, colr, y in lines:
        d2.text((WW // 2, y), t, font=ImageFont.truetype(FD, sz), anchor='mm', fill=colr, stroke_width=max(2, sz // 40), stroke_fill=(20, 14, 10))
out.save(OUT, quality=93); print('cover', OUT, 'bike bbox', bb)
