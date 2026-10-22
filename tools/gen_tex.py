import numpy as np, os
from PIL import Image
from mats import MATS
TYPES = ['metal_golem', 'humanoid_golem', 'dog_golem']

def hashn(x, y, seed=0):
    h = (x * 374761393 + y * 668265263 + seed * 2147483647) & 0xFFFFFFFF
    h = (h ^ (h >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0

def ramp_at(ramp, n):
    n = min(max(n, 0), 0.9999) * (len(ramp) - 1); i = int(n); f = n - i
    a, b = ramp[i], ramp[i + 1]
    return tuple(a[k] + (b[k] - a[k]) * f for k in range(3))

from geom import IRON, PLAYER, WOLF
MODELS = {'metal_golem': IRON, 'humanoid_golem': PLAYER, 'dog_golem': WOLF}
# role per part index: 0 head, 1 body, 2 arm/tail, 3 leg
ROLES = {'metal_golem': [0, 1, 2, 2, 3, 3], 'humanoid_golem': [0, 1, 2, 2, 3, 3], 'dog_golem': [0, 1, 1, 3, 3, 3, 3, 2]}
_FM = {}

def face_map(ftype, w, h):
    """per-pixel face info: canonical (mirrored) x, y in face, face w/h, kind, role, layer; plus mirror source for symmetrising."""
    if ftype in _FM: return _FM[ftype]
    shape = (h, w)
    fxc = np.zeros(shape, int); fy = np.zeros(shape, int); fw = np.ones(shape, int); fh = np.ones(shape, int)
    kind = np.full(shape, 5); role = np.zeros(shape, int); layer = np.zeros(shape, int); covered = np.zeros(shape, bool)
    src = np.tile(np.arange(w), (h, 1))  # mirror source x for each pixel (same row)
    for yy in range(h):
        for xx in range(w): fxc[yy, xx] = min(xx, w - 1 - xx); fy[yy, xx] = yy
    for pi, part in enumerate(MODELS[ftype][2]):
        for cu in part['cubes']:
            u, v, _, _, _, cw, ch, cd, infl, _m = cu
            cw, ch, cd = int(round(cw)), int(round(ch)), int(round(cd))
            rects = [(u + cd, v + cd, cw, ch, 0), (u + 2 * cd + cw, v + cd, cw, ch, 1), (u, v + cd, cd, ch, 2),
                     (u + cd + cw, v + cd, cd, ch, 2), (u + cd, v, cw, cd, 3), (u + cd + cw, v, cw, cd, 4)]
            for rx, ry, rw, rh, k in rects:
                for yy in range(rh):
                    for xx in range(rw):
                        px, py = rx + xx, ry + yy
                        if px >= w or py >= h: continue
                        fxc[py, px] = min(xx, rw - 1 - xx); fy[py, px] = yy; fw[py, px] = rw; fh[py, px] = rh
                        kind[py, px] = k; role[py, px] = ROLES[ftype][pi]; layer[py, px] = 1 if infl > 0 else 0
                        src[py, px] = rx + rw - 1 - xx; covered[py, px] = True
    _FM[ftype] = (fxc, fy, fw, fh, kind, role, layer, src, covered)
    return _FM[ftype]


def tidy(mat, rl, kd, fx, fy, fw, fh, X, Y):
    """flat, role-based colouring (AC-golem style). returns (rgb, glow_alpha or 0, is_gold)"""
    r = mat['ramp']; acc = mat['accent']
    deep, dark, main, light, hi = r[0], r[1], r[2], r[3], r[4]
    pat = mat.get('patch')
    sec = pat[0] if pat else None
    Z = mat.get('zones')
    if '_sd' not in mat: mat['_sd'] = sum(ord(ch) for ch in mat['key']) * 7
    sd = mat.get('style')
    def sh(c, f): return tuple(min(255, v * f) for v in c)
    side = kd in (0, 1, 2)
    cmax = (fw - 1) // 2
    glow = 0; gold = False
    border = fx == 0 or fy == 0 or fy == fh - 1
    if not side:
        c = sh(light if kd == 3 else dark, 1.0)
        if border: c = sh(c, 0.8)
        return c, 0, False
    c = main
    if rl == 0:    # head
        c = main
        if fy == 1: c = light
        if fy >= fh - 3: c = dark
        if Z and kd == 0 and fy in (fh // 2, fh // 2 + 1) and fx >= cmax - 0: c = Z['head']
    elif rl == 1:  # body / torso
        c = main
        in_panel = kd in (0, 1) and fw >= 6 and fx >= 2 and 2 <= fy <= fh - 3
        if in_panel:
            c = Z['panel'] if Z else light
            if fx == 2 or fy == 2 or fy == fh - 3: c = sh(Z['panel'], 0.55) if Z else sh(dark, 1.0)
            gy = fh // 3
            if (fx == cmax or (mat.get('glowcuff') and fx == cmax - 1)) and fy in (gy + 1, gy + 2): c = (Z['gem'] if Z else acc); glow = 0 if Z else 0.85
            elif (fx in (cmax - 1, cmax) and fy in (gy, gy + 3)) or (fx == cmax - 1 and fy in (gy + 1, gy + 2)): c = hi
        if fy >= fh - 2: c = dark
    elif rl == 2:  # arms / tail
        c = main
        if fy >= int(fh * 0.62):
            c = Z['cuff'] if Z else (sec if sec else light)
            if fy == int(fh * 0.62): c = sh(Z['cuff'], 0.55) if Z else dark
        if fy == fh - 1: c = deep
        if mat.get('glowcuff') and fy > int(fh * 0.62) and fy < fh - 1 and 0 < fx < fw - 1: c = sh(acc, 0.8); glow = 0.65
    else:          # legs
        c = dark if sd != 'plain' else main
        c = sh(main, 0.8) if not Z else sh(main, 0.92)
        if fy >= int(fh * 0.55):
            c = Z['boot'] if Z else deep
            if fy == int(fh * 0.55): c = sh(Z['boot'], 0.6) if Z else dark
    # very faint motif for identity (symmetric)
    if rl in (1, 2) and c == main:
        if sd in ('flame', 'crack'): c = sh(c, 1.08 if (fx // 2) % 2 else 0.95)
        elif sd == 'wave': c = sh(c, 1.08 if (fy // 2) % 2 else 0.95)
        elif sd in ('stone', 'elemental'): c = sh(c, 1.07 if ((fx // 2) + (fy // 2)) % 2 else 0.95)
        elif sd == 'runes' and fy % 6 == 3 and fx % 3 == 1: c = light
    gemc = (c is acc) or (c is hi)
    if not gemc and not gold:
        amp = mat.get('noise', 0.10)
        h1 = hashn(X, Y, mat['_sd']); h2 = hashn(X // 2, Y // 2, mat['_sd'] + 9)
        c = sh(c, 1 + amp * (h1 - 0.5) * 2 + 0.5 * amp * (h2 - 0.5) * 2)
    if border and c is not acc: c = sh(c, 0.82)
    if mat.get('trim') and rl != 0:
        top_line = (rl == 2 and fy == int(fh * 0.62)) or (rl == 3 and fy == int(fh * 0.55)) or (rl == 1 and kd in (0, 1) and fw >= 6 and fx >= 2 and fy == 2)
        if top_line and (fx // 2) % 3 != 2: gold = True
    return c, glow, gold

SIZES = {'metal_golem': (128, 128), 'humanoid_golem': (64, 64), 'dog_golem': (64, 32)}
# whether the inflated (second-layer) boxes are part of the model's used texture area
USE_LAYER1 = {'metal_golem': True, 'humanoid_golem': False, 'dog_golem': True}
# glowing "slot" pixels, keyed by (role, face kind, face width, face height); values are canonical (mirrored) (x, y) in the face
SLOTS = {
    'metal_golem': {(0, 0, 8, 10): {(1, 5), (1, 6), (2, 5), (2, 6)}},
    'humanoid_golem': {(0, 0, 8, 8): {(1, 4), (2, 4)}, (1, 0, 8, 12): {(1, 6), (2, 6), (3, 6)}},
    'dog_golem': {(0, 0, 6, 6): {(1, 2)}, (0, 0, 3, 3): {(0, 2), (1, 2)}},
}

HEAD_FRONT_U = 40   # humanoid head front face, outer layer: first texture column
ELEM = {'fire': (232, 80, 26), 'water': (42, 120, 216), 'earth': (58, 168, 58), 'air': (214, 240, 255)}

def gem_cols(mat):
    """front-face column -> gem colour: one gem in the accent colour, or one per element for combinations."""
    el = mat.get('elems')
    if not el: return {3: tuple(mat['accent']), 4: tuple(mat['accent'])}
    cs = [ELEM[e] for e in el]
    if len(cs) == 2: return {2: cs[0], 3: cs[0], 4: cs[1], 5: cs[1]}
    return {2 + i: c for i, c in enumerate(cs)}

def recolor(mat, seed, ftype):
    w, h = SIZES[ftype]
    fxc, fyy, fww, fhh, kind, role, layer, src, covered = face_map(ftype, w, h)
    op = covered & ((layer == 0) | USE_LAYER1[ftype] | ((ftype == 'humanoid_golem') & (layer == 1) & (role == 0)))
    out = np.zeros((h, w, 4)); emi = np.zeros((h, w, 4))
    slots = SLOTS[ftype]
    acc = mat['accent']
    for y in range(h):
        for x in range(w):
            if not op[y, x]: continue
            fx, fy, fw, fh, kd, rl, ly = int(fxc[y, x]), int(fyy[y, x]), int(fww[y, x]), int(fhh[y, x]), int(kind[y, x]), int(role[y, x]), int(layer[y, x])
            if ftype == 'humanoid_golem' and ly == 1:   # circlet + gems on the head's outer layer
                if kd in (0, 1, 2) and fy in (0, 1):
                    sh = 1.0 if fy == 0 else 0.8
                    gc = gem_cols(mat).get(x - HEAD_FRONT_U) if kd == 0 else None   # true column on the 8-wide front face
                    if gc: out[y, x] = (*gc, 255); emi[y, x] = (*[int(v * 0.85) for v in gc], 255)
                    else: out[y, x] = (240 * sh, 196 * sh, 52 * sh, 255)
                elif kd == 0 and fy == 2 and (x - HEAD_FRONT_U) in gem_cols(mat): out[y, x] = (240 * 0.8, 196 * 0.8, 52 * 0.8, 255)
                continue
            X = fx + 97 * (kd + 1) + 389 * rl + 53 * ly; Y = fy   # canonical coords: identical for left/right limbs
            slot = ly == 0 and (fx, fy) in slots.get((rl, kd, fw, fh), ())
            tc, tg, tgold = tidy(mat, rl, kd, fx, fy, fw, fh, X, Y)
            if slot and rl in (0, 1) and kd == 0:
                c = tuple(v * 0.85 for v in acc); emi[y, x] = (*[int(v * 0.85) for v in acc], 255)
            elif tgold: c = (240 * 0.9, 196 * 0.9, 52 * 0.9)
            else:
                c = tc
                if tg: emi[y, x] = (*[int(v * tg) for v in acc], 255)
            out[y, x] = (*c, 255)
    return Image.fromarray(out.astype(np.uint8), 'RGBA'), Image.fromarray(emi.astype(np.uint8), 'RGBA')

GLYPH = {
 'gem': ["..X..", ".XXX.", "XXXXX", ".XXX.", "..X.."], 'flame': ["..X..", ".XXX.", ".XXX.", "XXXXX", ".XXX."],
 'drop': ["..X..", ".XXX.", "XXXXX", "XXXXX", ".XXX."], 'peak': ["..X..", ".XXX.", "XXXXX", "XXXXX", "XXXXX"],
 'swirl': ["X.X.X", ".XXX.", "XX.XX", ".XXX.", "X.X.X"], 'star': ["..X..", "..X..", "XXXXX", "..X..", "..X.."],
 'shield': ["XXXXX", "XXXXX", "XXXXX", ".XXX.", "..X.."], 'eye': [".....", ".XXX.", "X.X.X", ".XXX.", "....."],
 'wisp': [".XXX.", "X.X.X", "XXXXX", "XXXXX", "X.X.X"], 'dune': ["X...X", ".XXX.", ".....", ".XXX.", "X...X"],
 'magma': ["X.X.X", ".XXX.", "XXXXX", ".XXX.", "X.X.X"], 'bubble': [".XXX.", "X...X", "X.X.X", "X...X", ".XXX."],
 'spark': ["X...X", ".X.X.", "..X..", ".X.X.", "X...X"], 'cloud': [".XX..", "XXXXX", "XXXXX", "XXXXX", "....."],
 'bolt': ["..X..", ".XXX.", "..X..", ".XXX.", "..X.."], 'prism': ["..X..", ".X.X.", "X...X", ".X.X.", "..X.."],
}

def construct_icon(mat):
    ramp, acc = mat['ramp'], mat['accent']
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0)); px = im.load()
    dark = tuple(int(v * 0.35) for v in ramp[0]); metal = [(120, 90, 24), (200, 160, 40), (250, 214, 90)] if mat.get('trim') else [(70, 74, 84), (120, 126, 138), (170, 176, 188)]
    def fill(x0, y0, x1, y1, col):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1): px[x, y] = (*col, 255)
    # body: front 1..11 x 5..14, top strip, right side
    fill(1, 5, 11, 14, ramp[2])
    for y in range(5, 15):            # vertical shading on the front
        for x in range(1, 12):
            f = 0.0 + (y - 5) / 9 * -0.28 + (1 - (x - 1) / 10) * 0.12
            px[x, y] = (*[int(min(255, max(0, v * (1 + f)))) for v in ramp[2]], 255)
    for i in range(4):                # top strip (parallelogram)
        for x in range(1 + (3 - i), 12 + (3 - i)):
            if x < 15: px[x, 2 + i] = (*ramp[3], 255)
    for i in range(10):               # right side
        for k in range(3):
            xx, yy = 12 + k, 5 + i - k
            if 2 <= yy <= 14 and xx < 15 and 5 + i <= 14: px[xx, yy] = (*ramp[1], 255)
    # metal frame corners and edges
    for x in range(1, 12): px[x, 5] = (*metal[2], 255); px[x, 14] = (*metal[0], 255)
    for y in range(5, 15): px[1, y] = (*metal[1], 255); px[11, y] = (*metal[0], 255)
    for (x, y) in ((1, 5), (11, 5), (1, 14), (11, 14)): px[x, y] = (*metal[2], 255)
    # core inlay
    fill(3, 7, 9, 13, dark)
    fill(4, 8, 8, 12, tuple(int(v * 0.18) for v in acc))
    g = GLYPH[mat['emblem']]
    for gy, row in enumerate(g):
        for gx, ch in enumerate(row):
            if ch == 'X': px[4 + gx, 8 + gy] = tuple(int(v * 0.9) for v in acc) + (255,) if mat['emblem'] != 'prism' else (240, 240, 246, 255)
    # outline
    src = im.copy(); sp = src.load()
    for y in range(16):
        for x in range(16):
            if sp[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < 16 and 0 <= yy < 16 and sp[xx, yy][3] > 0: px[x, y] = (*dark, 255); break
    return im

def build_all(outdir):
    if outdir: os.makedirs(outdir, exist_ok=True)
    res = {}
    for i, mat in enumerate(MATS):
        d = {}
        for t in TYPES:
            tex, emi = recolor(mat, i * 17 + 3, t)
            d[t] = (tex, emi)
        res[mat['key']] = (d, construct_icon(mat))
    return res

if __name__ == '__main__':
    r = build_all('/tmp/x')
    print('ok', len(r))
