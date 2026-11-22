"""Suspension-driven camera: random trail bumps -> fork (mass-spring-damper) -> per-frame dy / roll / blur.
usage: suspension.py <in.mp4> <out.mp4> <seconds> [roughness 0..1] [seed]  -> also writes <out>.bumps.json for synced thuds"""
import sys, json, subprocess, numpy as np
inp, out, D = sys.argv[1], sys.argv[2], float(sys.argv[3]); R = float(sys.argv[4]) if len(sys.argv) > 4 else 0.6
rng = np.random.default_rng(int(sys.argv[5]) if len(sys.argv) > 5 else 3); FPS = 32; SIM = 1000
n = int(D*SIM); force = np.zeros(n); bumps = []
t = 0.0
while t < D:                                           # roots and rocks: Poisson-spaced impulses, a few big hits
    t += rng.exponential(0.35/(0.4+R)); i = int(t*SIM)
    if i >= n: break
    big = rng.random() < 0.18; a = (rng.uniform(2.5, 4.0) if big else rng.uniform(0.6, 1.6))*R
    force[i:i+12] += a*900; bumps.append({"t": round(t, 3), "a": round(a, 3)})
force += rng.standard_normal(n)*60*R                     # chatter / washboard
# front fork ~2.2 Hz, damping ratio 0.35 (rebound visible but settles), plus rider-body layer at 0.9 Hz
def msd(f, hz, z):
    w = 2*np.pi*hz; x = v = 0.0; y = np.zeros(len(f)); dt = 1/SIM
    for k in range(len(f)): acc = f[k] - 2*z*w*v - w*w*x; v += acc*dt; x += v*dt; y[k] = x
    return y
fork = msd(force, 2.2, 0.35); body = msd(force*0.5, 0.9, 0.6) + msd(rng.standard_normal(n)*400*R, 6.0, 0.5)*0.4
idx = (np.arange(int(D*FPS))/FPS*SIM).astype(int)
dy = (fork*1.0 + body*0.5)[idx]; dy = dy/ (np.abs(dy).max()+1e-9) * 0.028 * 1920 * min(1, R+0.3)     # peak ~2.8% of frame height
roll = (msd(rng.standard_normal(n)*300*R, 1.4, 0.45) + fork*0.3)[idx]; roll = roll/(np.abs(roll).max()+1e-9)*1.6   # degrees
dx = (body*0.4)[idx]; dx = dx/(np.abs(dx).max()+1e-9)*0.008*1080
vel = np.abs(np.gradient(dy))                           # vertical blur proportional to jolt speed
json.dump(bumps, open(out + '.bumps.json', 'w'))
# render frame by frame with numpy via ffmpeg pipes (scale 1.10 crop margin so edges never show)
import shlex
W, H = 1080, 1920
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", inp, "-vf", f"scale={int(W*1.1)}:{int(H*1.1)}:flags=lanczos,fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
from scipy import ndimage
BW, BH = int(W*1.1), int(H*1.1); fsz = BW*BH*3; k = 0
while k < len(dy):
    buf = dec.stdout.read(fsz)
    if len(buf) < fsz: break
    f = np.frombuffer(buf, np.uint8).reshape(BH, BW, 3).astype(np.float32)
    if abs(roll[k]) > 0.05: f = ndimage.rotate(f, roll[k], reshape=False, order=1, mode='nearest')
    b = int(min(14, vel[k]*0.9))
    if b >= 2: f = ndimage.uniform_filter1d(f, b, axis=0)
    cy = int((BH-H)/2 + dy[k]); cx = int((BW-W)/2 + dx[k])
    cy = max(0, min(BH-H, cy)); cx = max(0, min(BW-W, cx))
    enc.stdin.write(np.clip(f[cy:cy+H, cx:cx+W], 0, 255).astype(np.uint8).tobytes()); k += 1
enc.stdin.close(); enc.wait(); print('frames', k, 'bumps', len(bumps))
