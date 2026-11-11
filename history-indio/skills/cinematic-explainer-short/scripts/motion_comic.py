#!/usr/bin/env python3
"""Motion comic: animate still keyframes with eased camera moves, cut to the voice.

usage: motion_comic.py shots.json voice.(mp3|wav) out.mp4 [--fps 30]
shots.json: [{"image": "k01.png", "start": 0.0, "end": 4.2, "camera": "push_in"}, ...]
camera: push_in | pull_out | pan_left | pan_right | tilt_up | tilt_down | hold
Images are cover-fitted to 1080x1920. Audio is copied through untouched in timing.
"""
import json, os, subprocess, sys
from PIL import Image

W, H = 1080, 1920


def ease(x):
    return x * x * x * (x * (x * 6 - 15) + 10)


def cover(im, scale=1.25):
    """Resize so the image covers the frame with `scale` headroom for moves."""
    k = max(W * scale / im.width, H * scale / im.height)
    return im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)


def window(cam, t, iw, ih):
    """Return crop box (x, y, w, h) at progress t in 0..1."""
    e = ease(t)
    z0, z1, dx, dy = 1.12, 1.12, 0.0, 0.0
    if cam == 'push_in': z0, z1 = 1.0, 1.22
    elif cam == 'pull_out': z0, z1 = 1.22, 1.0
    elif cam == 'pan_left': dx = 0.5 - e
    elif cam == 'pan_right': dx = e - 0.5
    elif cam == 'tilt_up': dy = 0.5 - e
    elif cam == 'tilt_down': dy = e - 0.5
    else: z0, z1 = 1.04, 1.08          # hold still creeps so nothing freezes
    z = z0 + (z1 - z0) * e
    fit = min(iw / W, ih / H)           # largest window that fits
    w, h = W * fit / z, H * fit / z
    x = (iw - w) / 2 + dx * (iw - w)
    y = (ih - h) / 2 + dy * (ih - h)
    return x, y, w, h


def main():
    a = sys.argv[1:]
    fps = int(a[a.index('--fps') + 1]) if '--fps' in a else 30
    shots_path, audio, out = a[0], a[1], a[2]
    shots = json.load(open(shots_path))
    base = os.path.dirname(os.path.abspath(shots_path))
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                           '-r', str(fps), '-i', '-', '-i', audio, '-c:v', 'libx264', '-crf', '17', '-pix_fmt', 'yuv420p',
                           '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    f = 0
    for s in shots:
        im = cover(Image.open(os.path.join(base, s['image'])).convert('RGB'))
        f1 = round(s['end'] * fps)
        n = max(1, f1 - f)
        for i in range(n):
            x, y, w, h = window(s.get('camera', 'hold'), i / max(1, n - 1), im.width, im.height)
            fr = im.resize((W, H), Image.BICUBIC, box=(x, y, x + w, y + h))
            ff.stdin.write(fr.tobytes())
        f = f1
    ff.stdin.close()
    sys.exit(ff.wait())


if __name__ == '__main__':
    main()
