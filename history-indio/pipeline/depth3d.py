#!/usr/bin/env python3
"""Strong 3D camera for build_anime.py (opt-in: "depth": "strong" or a 3D move name in shots_fx.json).
The keyframe is split once into two depth layers: a near layer (figure, near ground) with a soft, edge-snapped alpha,
and a far layer whose hidden part behind the near layer is filled by mirroring the surrounding background.
Each layer is moved by its own smoothed depth, so near and far separate without torn or smeared edges.
Moves: dolly_in/out, orbit_left/right, crane_up/down, rack_focus, and stronger versions of the classic moves.
prep3d() returns None when the depth map is nearly flat; the caller then uses the normal parallax."""
import numpy as np, cv2

MOVES3D = ('dolly_in', 'dolly_out', 'orbit_left', 'orbit_right', 'crane_up', 'crane_down', 'rack_focus')
FALLBACK = {'dolly_in': 'push_in', 'dolly_out': 'pull_out', 'orbit_left': 'pan_left', 'orbit_right': 'pan_right',
            'crane_up': 'tilt_up', 'crane_down': 'tilt_down', 'rack_focus': 'push_in'}       # used when a depth map is flat


def _guided(I, p, r, eps):
    """edge-aware smoothing of p, following the edges of guide I (He et al. guided filter, grey guide)."""
    m = lambda x: cv2.boxFilter(x, -1, (r, r))
    mI, mp = m(I), m(p); a = (m(I * p) - mI * mp) / (m(I * I) - mI * mI + eps); b = mp - a * mI
    return m(a) * I + m(b)


def _nearest(valid):
    """for every pixel, the row/col of the nearest valid pixel, and the distance to it."""
    dist, lab = cv2.distanceTransformWithLabels((~valid).astype(np.uint8), cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    ys, xs = np.nonzero(valid); ly = np.zeros(lab.max() + 1, np.int32); lx = ly.copy()
    ly[lab[ys, xs]] = ys; lx[lab[ys, xs]] = xs
    return ly[lab], lx[lab], dist


def _normconv(d, w, sig):
    """smooth d using only the pixels weighted by w."""
    return cv2.GaussianBlur(d * w, (0, 0), sig) / np.maximum(cv2.GaussianBlur(w, (0, 0), sig), 1e-4)


def plane_residual(dep):
    """how far the depth map is from one tilted plane (depth maps are normalised, so their range says nothing).
    Measured on History Indio keyframes: letters and maps 0.04-0.07, figures, crowds and vistas 0.09-0.28."""
    d = cv2.resize(dep.astype(np.float32), (64, 112), interpolation=cv2.INTER_AREA); yy, xx = np.mgrid[0:112, 0:64] / 100.0
    A = np.stack([np.ones(d.size), xx.ravel(), yy.ravel()], 1); c, *_ = np.linalg.lstsq(A, d.ravel(), rcond=None)
    return float(np.std(d.ravel() - A @ c))


def prep3d(im, dep, blur_px):
    """im: the cover-fit keyframe (uint8 BGR); dep: raw depth (1 = near) at any size; blur_px: depth-of-field blur in im px.
    Returns the layer set, or None when the picture has too little depth to separate."""
    h, w = im.shape[:2]
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    d = cv2.resize(dep.astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)
    d = np.clip(_guided(gray, d, max(5, w // 90) | 1, 2e-3), 0, 1)                           # depth edges snap to picture edges
    p3, p50, p97 = np.percentile(d, (3, 50, 97))
    if p97 - p3 < 0.30 or plane_residual(dep) < 0.08: return None                            # flat picture (a letter, a map, a wall)
    th, _ = cv2.threshold((d * 255).astype(np.uint8), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU); th /= 255
    th = float(np.clip(th, p3 + 0.25 * (p97 - p3), p3 + 0.80 * (p97 - p3)))
    wd = 0.04; a = np.clip((d - th + wd) / (2 * wd), 0, 1); a = a * a * (3 - 2 * a)          # soft on depth ramps, crisp at depth jumps
    a = np.clip((_guided(gray, a, 7, 1e-4) - 0.35) / 0.3, 0, 1); a = a * a * (3 - 2 * a)     # matte snapped to colour edges, then made crisp
    a[a < 0.03] = 0                                                                          # (half-transparent edges would double when the layers separate)
    kc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * (w // 28) + 1,) * 2)              # close gaps between arm and body etc.: they move with the figure
    a = np.maximum(a, cv2.GaussianBlur(cv2.morphologyEx(a, cv2.MORPH_CLOSE, kc), (0, 0), 2))
    frac = float(a.mean())
    if frac < 0.015 or frac > 0.9: return None                                               # nothing separates from the rest
    core = a > 0.5
    ny, nx, dist = _nearest(core)
    # along real depth jumps the near layer also carries a thin ring of the original pixels (opaque, then fading), so any
    # outline or fringe of the figure travels with it; on smooth depth ramps (crowds, sea, ground) no ring is needed
    el = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1,) * 2); kr = el(max(3, w // 70))
    jump = cv2.GaussianBlur(cv2.dilate(((cv2.dilate(d, kr) - cv2.erode(d, kr)) > 0.15).astype(np.float32), el(w // 50)), (0, 0), 3)
    r1, r2 = w / 120, w / 70
    a = np.maximum(a, np.clip((r2 - dist) / (r2 - r1), 0, 1) * jump).astype(np.float32)
    # near layer: true colour wherever it shows; outside it, colour pushed outward so its edge never samples background
    fg = np.where((a > 0.02)[..., None], im, im[ny, nx])
    # far layer: the area behind the near layer is filled by mirroring the background across the silhouette
    hole = cv2.dilate((a > 0.02).astype(np.uint8), el(2)) > 0
    by, bx, bd = _nearest(~hole); YY, XX = np.mgrid[0:h, 0:w]
    my_ = np.clip(2 * by - YY, 0, h - 1); mx_ = np.clip(2 * bx - XX, 0, w - 1)
    bad = hole[my_, mx_]; my_ = np.where(bad, by, my_); mx_ = np.where(bad, bx, mx_)
    fill = im[my_, mx_].astype(np.float32)
    deep = np.clip(bd / (w / 12), 0, 1)[..., None]                                          # crisp near the edge, calmer deeper in
    fill = cv2.GaussianBlur(fill, (0, 0), 0.8) * (1 - deep) + cv2.GaussianBlur(fill, (0, 0), w / 160) * deep
    bg = np.where(hole[..., None], fill, im.astype(np.float32))
    # displacement depth per layer: smooth inside each layer so faces, text and props move rigidly (no rubber warping)
    dfg = _normconv(d, a, w / 22); dfg = dfg[ny, nx] * (1 - a) + dfg * a                     # constant outside the figure: silhouette stays intact
    dfg = cv2.GaussianBlur(dfg, (0, 0), w / 60)
    wb = (1 - a) * (~hole); dbg = _normconv(d, wb + 1e-3 * (1 - wb), w / 40)
    dbg = np.where(hole, dbg[by, bx], dbg); dbg = cv2.GaussianBlur(dbg, (0, 0), w / 50)
    q_subj = float(np.median(d[core])); q_far = float(p3)
    sig = max(0.8, blur_px)                                                                  # depth-of-field versions of each layer
    bgb = cv2.GaussianBlur(bg, (0, 0), sig)
    a_b = cv2.GaussianBlur(a, (0, 0), sig * 0.8); fgb = cv2.GaussianBlur(fg.astype(np.float32), (0, 0), sig)
    u8 = lambda x: np.clip(x, 0, 255).astype(np.uint8)
    ys, xs = np.nonzero(core)
    return dict(fg=np.dstack([fg, u8(a * 255)]), fgb=np.dstack([u8(fgb), u8(a_b * 255)]), bg=u8(bg), bgb=u8(bgb),
                dfg=dfg.astype(np.float32), dbg=dbg.astype(np.float32), q_subj=q_subj, q_far=q_far, th=th,
                cx=float(xs.mean()) / w, cy=float(ys.mean()) / h, frac=frac)


def camera(move, e):
    """camera for eased progress e: zoom, crop pan, parallax per unit of depth (fractions of the frame), growth per unit of
    depth, keystone tilt, pivot ('subj' = the subject stays put, 'far' = the background stays put), focus pull."""
    u = 2 * e - 1; c = dict(z=1.07, px=0.0, py=0.0, tx=0.0, ty=0.0, k=0.0, key=0.0, piv='subj', fov=0.0)
    if move in ('dolly_in', 'dolly_out'):
        p = e if move == 'dolly_in' else 1 - e
        c.update(z=1.07 + 0.05 * p, k=0.30 * p, fov=-0.035 * p, piv='far')                   # near grows faster than far; field of view widens a touch
    elif move in ('orbit_left', 'orbit_right'):
        sgn = 1 if move == 'orbit_left' else -1
        c.update(z=1.10, tx=0.062 * sgn * u, key=0.02 * sgn * u)                              # near and far slide in opposite directions around the subject
    elif move in ('crane_up', 'crane_down'):
        sgn = 1 if move == 'crane_up' else -1
        c.update(z=1.10 + 0.02 * e, ty=0.046 * sgn * u, py=-0.22 * sgn * u, key=0.0)           # vertical arc: near drops, far rises, the frame tilts
        c['tilt'] = 0.025 * sgn * u
    elif move == 'rack_focus':
        c.update(z=1.07 + 0.03 * e, tx=0.012 * u)
    elif move == 'push_in': c.update(z=1.03 + 0.13 * e, k=0.14 * e, piv='far')
    elif move == 'pull_out': c.update(z=1.16 - 0.13 * e, k=0.14 * (1 - e), piv='far')
    elif move == 'pan_left': c.update(z=1.08, px=-u * 0.5, tx=-0.06 * u, piv='far')
    elif move == 'pan_right': c.update(z=1.08, px=u * 0.5, tx=0.06 * u, piv='far')
    elif move == 'tilt_up': c.update(z=1.08, py=-u * 0.5, ty=-0.05 * u, piv='far')
    elif move == 'tilt_down': c.update(z=1.08, py=u * 0.5, ty=0.05 * u, piv='far')
    return c


_GRID = {}


def _grid(W, H, f=4):
    """output pixel coordinates sampled every f px (pixel centres line up with cv2.resize's bilinear upsampling)."""
    if (W, H) not in _GRID:
        xs = (np.arange(W // f, dtype=np.float32) + 0.5) * f - 0.5; ys = (np.arange(H // f, dtype=np.float32) + 0.5) * f - 0.5
        _GRID[W, H] = np.meshgrid(xs, ys)
    return _GRID[W, H]


def frame3d(L, e, t, move, fx, W, H, zoom_extra=1.0, focus=(0.5, 0.5), dof=None, focus_to='near', shake=(0.0, 0.0)):
    """one frame (float32 BGR, before glow/particles/vignette), the near layer's sampling maps, and source px per output px.
    The sampling maps are smooth (each layer's depth is smoothed), so they are computed at quarter size and upsampled."""
    ih, iw = L['bg'].shape[:2]; fit = min(iw / W, ih / H); c = camera(move, e)
    z = c['z'] * zoom_extra
    if 'punch' in fx and t < 0.2: z *= 1 + 0.10 * (1 - t / 0.2) ** 2
    s = fit / z; w, h = W * s, H * s
    fxp = focus[0] if focus != (0.5, 0.5) else 0.5 + (L['cx'] - 0.5) * 0.35                  # lean the frame toward the subject
    x0 = float(np.clip((iw - w) * (fxp + c['px'] * 0.9), 0, iw - w)) + shake[0]
    y0 = float(np.clip((ih - h) * (focus[1] + c['py'] * 0.9), 0, ih - h)) + shake[1]
    cxo = float(np.clip((L['cx'] * iw - x0) / s, W * 0.25, W * 0.75)); cyo = float(np.clip((L['cy'] * ih - y0) / s, H * 0.3, H * 0.7))   # growth centre = subject on screen
    q0 = L['q_subj'] if c['piv'] == 'subj' else L['q_far']
    XX, YY = _grid(W, H); bx = x0 + XX * s; by = y0 + YY * s
    qf = None                                                                                # rack focus / depth of field: blur by distance to the focus depth
    if move == 'rack_focus':
        a0, a1 = (L['q_far'], L['q_subj']) if focus_to == 'near' else (L['q_subj'], L['q_far'])
        qf = a0 + (a1 - a0) * min(1.0, max(0.0, (e - 0.15) / 0.7))
    elif dof in ('far', 'near'): qf = L['q_subj'] if dof == 'far' else L['q_far']
    up = lambda m: cv2.resize(m, (W, H), interpolation=cv2.INTER_LINEAR)
    out = []
    for lay in ('bg', 'fg'):
        r = cv2.remap(L['d' + lay], bx, by, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE) - q0
        g = (1 + c['fov']) * (1 + c['k'] * r)                                               # per-pixel magnification: near grows faster
        X = cxo + (XX - cxo) / g - c['tx'] * W * r; Y = cyo + (YY - cyo) / g - c['ty'] * H * r
        if c['key']: Y = Y - (YY - H / 2) * c['key'] * (XX / W - 0.5)                          # slight yaw keystone: the near side of the arc grows taller
        if c.get('tilt'): X = X - (XX - W / 2) * c['tilt'] * (YY / H - 0.5)                    # slight pitch keystone
        if 'water' in fx and lay == 'bg':                                                    # shimmer on the far lower part (the sea)
            wm = np.clip((YY / H - 0.45) * 3, 0, 1) * np.clip(0.3 - r, 0, 1) * 1.6
            X = X + wm * 3.2 * np.sin(YY * 0.045 + t * 2.6); Y = Y + wm * 2.2 * np.sin(XX * 0.02 + YY * 0.06 + t * 3.1)
        mx = up((x0 + X * s).astype(np.float32)); my = up((y0 + Y * s).astype(np.float32))
        img = cv2.remap(L[lay], mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        if qf is not None:
            bw = np.clip(np.abs(r + q0 - qf) * 2.6 - 0.15, 0, 1 if move == 'rack_focus' else 0.6).astype(np.float32)
            if bw.max() > 0.01:
                bw = up(bw); img = cv2.blendLinear(img, cv2.remap(L[lay + 'b'], mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT), 1 - bw, bw)
        out.append((img, mx, my))
    (bg, _, _), (fg, mfx, mfy) = out
    a = fg[..., 3].astype(np.float32) * (1 / 255)
    return cv2.blendLinear(fg[..., :3], bg, a, 1 - a).astype(np.float32), mfx, mfy, s
