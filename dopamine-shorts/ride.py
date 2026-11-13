"""CPU ride engine (no GPU, always available): a world plate + its depth map -> endless forward dolly with parallax,
a separate bike-cockpit layer, suspension-driven jolts (world moves against the bars), ballistic particles, grain.
usage: ride.py <shot.json> <out.mp4>
shot: {"plate","cockpit","dur","vp":[x,y] (0..1),"speed","rough","fx":"dust|drops|spray|sparks|embers|stars","seed","bumps":[t,...] optional,"slow":factor}"""
import sys, json, subprocess, numpy as np, onnxruntime as ort
from PIL import Image, ImageFilter
from scipy import ndimage
S = json.load(open(sys.argv[1])); out = sys.argv[2]; W, H, FPS = 1080, 1920, 30; M = 1.12
rng = np.random.default_rng(S.get('seed', 1)); D = S['dur']; N = int(round(D*FPS))
BW, BH = int(W*M), int(H*M)
plate = Image.open(S['plate']).convert('RGB').resize((BW, BH), Image.LANCZOS)
P = np.asarray(plate).astype(np.float32)/255
# ---- depth (disparity: 1 = near) ----
sess = ort.InferenceSession(S.get('depth_model', '../models/depth_s.onnx'), providers=['CPUExecutionProvider'])
im = np.asarray(plate.resize((518, 910), Image.BICUBIC)).astype(np.float32)/255
x = ((im - [0.485, 0.456, 0.406])/[0.229, 0.224, 0.225]).transpose(2, 0, 1)[None].astype(np.float32)
d = sess.run(None, {'pixel_values': x})[0][0]; d = (d - d.min())/(d.max() - d.min() + 1e-6)
d = np.asarray(Image.fromarray((d*255).astype(np.uint8)).resize((BW, BH), Image.BICUBIC).filter(ImageFilter.GaussianBlur(6))).astype(np.float32)/255
Z = 1/(d*1.0 + 0.10)                                    # distance: near ~0.9, far ~10
vx, vy = S['vp'][0]*BW, S['vp'][1]*BH
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); ox, oy = (BW-W)/2, (BH-H)/2
def warp(s, dx, dy):
    """view after moving forward by s (same units as Z): inverse warp with 2 fixed-point steps"""
    qx, qy = xx + ox + dx, yy + oy + dy; px, py = qx, qy
    for _ in range(2):
        z = ndimage.map_coordinates(Z, [py, px], order=1, mode='nearest'); m = z/np.maximum(z - s, 0.12)
        px, py = vx + (qx - vx)/m, vy + (qy - vy)/m
    return np.stack([ndimage.map_coordinates(P[..., c], [py, px], order=1, mode='nearest') for c in range(3)], -1), m
# ---- suspension: bumps -> fork (2.4 Hz, zeta 0.45) + chatter ----
SIM = 600; n = int(D*SIM); f = np.zeros(n); R = S.get('rough', 0.6); bl = S.get('bumps')
if bl is None:
    bl, t = [], 0.0
    while True:
        t += rng.exponential(0.5/(0.3+R))
        if t >= D: break
        bl.append(t)
amps = []
for t in bl:
    a = (rng.uniform(2.2, 3.2) if rng.random() < 0.25 else rng.uniform(0.7, 1.5)); i = int(t*SIM); f[i:i+8] += a*1500; amps.append([round(float(t), 3), round(float(a), 2)])
def msd(f, hz, z):
    w = 2*np.pi*hz; x = v = 0.0; y = np.zeros(len(f)); dt = 1/SIM
    for k in range(len(f)): v += (f[k] - 2*z*w*v - w*w*x)*dt; x += v*dt; y[k] = x
    return y
fork = msd(f, 2.4, 0.45); chat = msd(rng.standard_normal(n)*2500, 15, 0.3)
idx = (np.arange(N)/FPS*SIM).astype(int)
big = np.abs(fork).max() + 1e-9
dyw = fork[idx]/big*0.022*H*min(1, R+0.2) + chat[idx]/(np.abs(chat).max()+1e-9)*0.002*H*R          # world vs bars
roll = msd(rng.standard_normal(n)*800, 1.2, 0.5)[idx]; roll = roll/(np.abs(roll).max()+1e-9)*0.8*R
json.dump(amps, open(out + '.bumps.json', 'w'))
# ---- cockpit layer (keyed once) ----
c = np.asarray(Image.open(S['cockpit']).convert('RGB').resize((W, H), Image.LANCZOS)).astype(np.float32)/255
g = c[..., 1] - np.maximum(c[..., 0], c[..., 2]); a = 1 - np.clip((g - 0.06)/0.14, 0, 1)
a = np.asarray(Image.fromarray((a*255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.5))).astype(np.float32)/255
fg = c.copy(); fg[..., 1] -= np.clip(g, 0, 1)
amb = P[int(BH*0.65):].reshape(-1, 3).mean(0); fg = fg*(0.55 + 0.9*P.mean())*(0.6 + 0.4*amb/(amb.mean()+1e-6))
sh = np.asarray(Image.fromarray((a*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(24))).astype(np.float32)/255
CK = np.dstack([fg, a, sh])
# ---- particles: screen-space ballistic ----
fx = S.get('fx', 'dust'); NP = {'dust': 120, 'drops': 500, 'spray': 300, 'sparks': 260, 'embers': 160, 'stars': 200}.get(fx, 0)
def spawn(k):
    if fx == 'sparks': return np.column_stack([np.full(k, W/2)+rng.normal(0, 12, k), np.full(k, H*0.66), rng.normal(0, 520, k), -rng.uniform(250, 1500, k), rng.uniform(0.25, 0.7, k)])
    if fx == 'embers': return np.column_stack([rng.uniform(0, W, k), rng.uniform(H*0.3, H, k), rng.normal(0, 40, k), -rng.uniform(60, 260, k), rng.uniform(1.5, 4, k)])
    if fx in ('drops', 'spray'):
        ang = rng.uniform(-1.2, 1.2, k); sp = rng.uniform(500, 2400, k)*(0.5 if fx == 'spray' else 1)
        return np.column_stack([np.full(k, W/2)+rng.normal(0, 90, k), np.full(k, H*(0.62 if fx == 'drops' else 0.5)), np.sin(ang)*sp, -np.cos(ang)*sp, rng.uniform(0.8, 2.2, k)])
    r = rng.uniform(20, 300, k); th = rng.uniform(0, 6.283, k)       # dust / stars: stream out of the vanishing point
    return np.column_stack([W*S['vp'][0] + r*np.cos(th), H*S['vp'][1] + r*np.sin(th), np.cos(th)*r*2.5, np.sin(th)*r*2.5, rng.uniform(0.6, 1.6, k)])
pt = spawn(NP) if NP else np.zeros((0, 5)); age = rng.uniform(0, 1, NP)*pt[:, 4] if NP else np.zeros(0)
COL = {'dust': (0.9, 0.8, 0.6), 'drops': (0.95, 0.97, 1.0), 'spray': (1.0, 0.95, 0.85), 'sparks': (1.0, 0.65, 0.2), 'embers': (1.0, 0.45, 0.1), 'stars': (0.9, 0.95, 1.0)}.get(fx, (1, 1, 1))
GRAV = {'drops': 2600, 'spray': 900, 'sparks': 2200, 'embers': -40}.get(fx, 0); SL = S.get('slow', 1.0)
def particles(layer, dt):
    global pt, age
    if not NP: return
    for sub in range(4):                                             # sub-steps draw the streak (motion blur)
        h = dt/4*SL; pt[:, 3] += GRAV*h; pt[:, 0] += pt[:, 2]*h; pt[:, 1] += pt[:, 3]*h; age += h
        if fx in ('dust', 'stars'): pt[:, 2] *= 1 + 3*h; pt[:, 3] *= 1 + 3*h
        life = np.clip(1 - age/pt[:, 4], 0, 1); xi = pt[:, 0].astype(int); yi = pt[:, 1].astype(int)
        ok = (xi > 1) & (xi < W-2) & (yi > 1) & (yi < H-2) & (life > 0)
        br = life[ok]*{'dust': 0.10, 'drops': 0.30, 'spray': 0.16, 'sparks': 0.6, 'embers': 0.45, 'stars': 0.35}[fx]
        for ddx in (0, 1):
            for ddy in (0, 1): np.add.at(layer, (yi[ok]+ddy, xi[ok]+ddx), br)
    dead = (age > pt[:, 4]) | (pt[:, 0] < 0) | (pt[:, 0] > W) | (pt[:, 1] > H) | (pt[:, 1] < 0)
    if dead.any() and fx not in ('drops',): pt[dead] = spawn(int(dead.sum())); age[dead] = 0
# ---- render ----
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "15", "-preset", "medium", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
T = S.get('period', 1.4); SMAX = S.get('speed', 0.5); vel = np.gradient(dyw)
for k in range(N):
    t = k/FPS*SL; ph = (t/T) % 1.0; ph2 = (ph + 0.5) % 1.0
    w1 = 1 - abs(2*ph - 1); w2 = 1 - w1                              # two phases of the same dolly, cross-faded: endless forward flow
    A, m1 = warp(ph*SMAX, 0, dyw[k]); B, _ = warp(ph2*SMAX, 0, dyw[k]); fr = A*w1 + B*w2
    if S.get('blur', 1):                                             # speed blur grows toward the frame edges
        rad = np.clip(np.hypot(xx - W*S['vp'][0], yy - H*S['vp'][1])/H, 0, 1)[..., None]
        bl_ = np.asarray(Image.fromarray((fr*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5*SL))).astype(np.float32)/255
        fr = fr*(1 - rad*0.8) + bl_*rad*0.8
    b = int(min(12, abs(vel[k])*0.6))
    if b >= 2: fr = ndimage.uniform_filter1d(fr, b, axis=0)
    lay = np.zeros((H, W), np.float32); particles(lay, 1/FPS)
    if NP: lay = ndimage.gaussian_filter(lay, 1.3 if fx != 'dust' else 3); fr = fr + lay[..., None]*np.array(COL, np.float32)*3
    ck = CK
    if abs(roll[k]) > 0.03 or True:
        ck = ndimage.shift(CK, (-dyw[k]*0.18, roll[k]*3, 0), order=1, mode='nearest')
    fr = fr*(1 - 0.28*ck[..., 4:5]); fr = ck[..., :3]*ck[..., 3:4] + fr*(1 - ck[..., 3:4])
    fr = fr + rng.normal(0, 0.012, (H, W, 1)).astype(np.float32)   # grain last
    enc.stdin.write((np.clip(fr, 0, 1)*255).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait(); print('ok', out, N, 'frames', len(amps), 'bumps')
