import numpy as np, math
from PIL import Image

def faces(cube):
    u, v, x, y, z, w, h, d, inf, mir = cube
    x0, y0, z0 = x - inf, y - inf, z - inf
    x1, y1, z1 = x + w + inf, y + h + inf, z + d + inf
    # corner order per face gives (origin, +s axis, +t axis) in model space, plus uv rect
    P = lambda a, b, c: np.array([a, b, c], float)
    f = []
    # up (-y side): top face, uv (u+d, v) size w x d ; s along +x, t along +z
    f.append((P(x0, y0, z0), P(x1, y0, z0), P(x0, y0, z1), (u + d, v, w, d)))
    # down (+y): uv (u+d+w, v) size w x d ; t goes toward -z so that it's flipped
    f.append((P(x0, y1, z1), P(x1, y1, z1), P(x0, y1, z0), (u + d + w, v, w, d)))
    # west (-x): uv (u, v+d) size d x h ; s along +z... viewed from -x, left=front(-z)? s from -z to +z reversed
    f.append((P(x0, y0, z1), P(x0, y0, z0), P(x0, y1, z1), (u, v + d, d, h)))
    # north (front, -z): uv (u+d, v+d) size w x h ; viewed from -z, left is +x
    f.append((P(x0, y0, z0), P(x1, y0, z0), P(x0, y1, z0), (u + d, v + d, w, h)))
    # east (+x): uv (u+d+w, v+d) size d x h ; viewed from +x left is -z
    f.append((P(x1, y0, z0), P(x1, y0, z1), P(x1, y1, z0), (u + d + w, v + d, d, h)))
    # south (back, +z): uv (u+d+w+d, v+d) size w x h ; viewed from +z left is -x
    f.append((P(x1, y0, z1), P(x0, y0, z1), P(x1, y1, z1), (u + 2 * d + w, v + d, w, h)))
    if mir:
        f[2], f[4] = (f[2][0], f[2][1], f[2][2], f[4][3][:0] + (u + d + w, v + d, d, h)), (f[4][0], f[4][1], f[4][2], (u, v + d, d, h))
    return f, mir

def rot(p, r):
    rx, ry, rz = r
    cx, sx = math.cos(rx), math.sin(rx); cy, sy = math.cos(ry), math.sin(ry); cz, sz = math.cos(rz), math.sin(rz)
    X = np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]]); Y = np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]]); Z = np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
    return Z @ Y @ X @ p

SHADE = [1.0, 0.55, 0.78, 0.9, 0.78, 0.7]  # up, down, west, north, east, south

def render(model, tex, size=160, yaw=-35, pitch=18, scale=None, ymin=None, flat=False):
    tw, th, parts = model
    tex = np.array(tex.convert("RGBA"))
    quads = []
    for part in parts:
        for cube in part["cubes"]:
            fs, mir = faces(cube)
            for k, (o, a, b, uv) in enumerate(fs):
                pts = [rot(q, part["r"]) + np.array(part["p"], float) for q in (o, a, b)]
                quads.append((pts, uv, mir, k))
    ya, pa = math.radians(yaw), math.radians(pitch)
    def cam(p):
        # model: +y down, front is -z; we look from the front (-z side), rotate by yaw about y, then pitch about x
        x, y, z = p
        x, z = x * math.cos(ya) + z * math.sin(ya), -x * math.sin(ya) + z * math.cos(ya)
        y, z = y * math.cos(pa) - z * math.sin(pa), y * math.sin(pa) + z * math.cos(pa)
        return np.array([x, y, z])
    allp = np.array([cam(q) for pts, *_ in quads for q in pts])
    ext = max(np.ptp(allp[:, 0]), np.ptp(allp[:, 1]))
    sc = (size * 0.9) / ext if scale is None else scale
    cx = (allp[:, 0].min() + allp[:, 0].max()) / 2; cy = (allp[:, 1].min() + allp[:, 1].max()) / 2
    S = 3  # supersample
    W = size * S
    img = np.zeros((W, W, 4), float); zb = np.full((W, W), 1e9)
    for pts, uv, mir, k in quads:
        o, a, b = [cam(q) for q in pts]
        sa, sb = a - o, b - o
        # screen coords
        def scr(p): return np.array([(p[0] - cx) * sc * S + W / 2, (p[1] - cy) * sc * S + W / 2])
        O = scr(o); A = scr(a) - O; B = scr(b) - O
        det = A[0] * B[1] - A[1] * B[0]
        if abs(det) < 1e-6: continue
        # backface: front-facing check via normal z
        n = np.cross(sa, sb)
        corners = [O, O + A, O + B, O + A + B]
        x0 = int(max(0, min(c[0] for c in corners))); x1 = int(min(W - 1, max(c[0] for c in corners)) + 1)
        y0 = int(max(0, min(c[1] for c in corners))); y1 = int(min(W - 1, max(c[1] for c in corners)) + 1)
        if x1 <= x0 or y1 <= y0: continue
        xs, ys = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
        dx, dy = xs - O[0], ys - O[1]
        s = (dx * B[1] - dy * B[0]) / det; t = (A[0] * dy - A[1] * dx) / det
        m = (s >= 0) & (s < 1) & (t >= 0) & (t < 1)
        if not m.any(): continue
        u0, v0, uw, vh = uv
        if mir: s = 1 - s
        uu = np.clip((u0 + s * uw).astype(int), 0, tw - 1); vv = np.clip((v0 + t * vh).astype(int), 0, th - 1)
        col = tex[vv * 0 + vv, uu]  # RGBA
        z = o[2] + s * sa[2] + t * sb[2]
        ok = m & (col[..., 3] > 20) & (z < zb[y0:y1, x0:x1])
        ys_i, xs_i = np.nonzero(ok)
        sh = 1.0 if flat else SHADE[k]
        for yi, xi in zip(ys_i, xs_i):
            c = col[yi, xi].astype(float); c[:3] *= sh
            img[y0 + yi, x0 + xi] = c; zb[y0 + yi, x0 + xi] = z[yi, xi]
    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGBA").resize((size, size), Image.LANCZOS)
    return out
