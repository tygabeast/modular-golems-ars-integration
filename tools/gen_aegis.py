"""PROPOSAL textures for the Aegis golem armour (shapes in aegis_spec.py): ivory plate, gold trim, elemental gems, navy boots."""
import sys
from PIL import Image
import aegis_spec as S

SIZE = {'helmet': (64, 64), 'chestplate': (128, 64), 'leggings': (64, 32), 'boots': (64, 32)}
P = [(246, 244, 236), (224, 222, 214), (196, 194, 190), (160, 160, 164)]   # ivory plate, light -> dark
N = [(64, 78, 122), (46, 58, 98), (34, 42, 74), (22, 28, 52)]               # navy
D = (30, 34, 58)                                                              # seam / shadow
G = [(255, 236, 140), (240, 196, 52), (190, 140, 34), (130, 92, 28)]          # gold
GEM = {'red': [(255, 150, 130), (214, 52, 44), (150, 28, 30), (96, 16, 22)],
       'blue': [(170, 210, 255), (60, 130, 230), (34, 80, 170), (20, 44, 110)],
       'green': [(170, 255, 170), (50, 190, 80), (28, 130, 56), (16, 80, 40)],
       'yellow': [(255, 250, 170), (250, 214, 60), (200, 150, 30), (140, 96, 20)]}


def rect(b):
    m, x, y, z, w, h, d = b
    return 2 * (w + d), h + d


def pack(piece):
    W, H = SIZE[piece]
    items = []
    for pi, (name, bone, pose, boxes) in enumerate(S.BUILD[piece]()):
        for bi, b in enumerate(boxes):
            rw, rh = rect(b)
            items.append((rh, rw, pi, bi))
    items.sort(reverse=True)
    out = []; x = y = shelf = 0
    for rh, rw, pi, bi in items:
        if x + rw > W: x = 0; y += shelf; shelf = 0
        if y + rh > H: raise SystemExit(f'{piece}: texture {W}x{H} too small')
        out.append((pi, bi, x, y)); x += rw; shelf = max(shelf, rh)
    return out


def hsh(a, b, c=0):
    n = (a * 73856093) ^ (b * 19349663) ^ (c * 83492791)
    return ((n >> 7) & 255) / 255.0


def side_row(face):
    return face in ('west', 'east', 'north', 'south')


def plate_base(face, i, j, w, h, seed, ramp=P):
    sh = {'up': 0, 'down': 3, 'west': 2, 'east': 1, 'north': 1, 'south': 2}[face]
    r = hsh(i, j, seed)
    if r > 0.78: sh -= 1
    elif r < 0.16: sh += 1
    if side_row(face) and j % 2 == 1 and hsh(j, i // 3, seed + 5) > 0.6: sh += 1   # faint plate grain
    c = ramp[max(0, min(3, sh))]
    k = int((hsh(i, j, seed + 11) - 0.5) * 16)
    return tuple(max(0, min(255, v + k)) for v in c)


def d_is_plate(w, h):
    return w <= 4 and h == 5


def paint(m, face, i, j, w, h, seed):
    side = face in ('west', 'east', 'north', 'south')
    if m == 'gold':
        s = {'up': 0, 'down': 3, 'west': 2, 'east': 2, 'north': 1, 'south': 2}[face]
        if i == 0 or j == 0: s = max(0, s - 1)
        elif i == w - 1 or j == h - 1: s = min(3, s + 1)
        return G[s]
    if m in GEM:
        g = GEM[m]
        if face in ('up', 'down') or w <= 1 or h <= 1: return g[2]
        if i == 0 and j == 0: return g[0]
        if i in (0, w - 1) or j in (0, h - 1): return g[3] if face in ('south', 'east') else g[2]
        return g[1] if (i + j) % 3 else g[0]
    if m == 'boot':
        c = plate_base(face, i, j, w, h, seed, N)
        if side:
            if j == 0: return G[1]
            if j == 1 and h > 4: return G[2]
            if j == h - 1: return D
            if face == 'north' and j >= h - 3: return N[3]
        return c
    c = plate_base(face, i, j, w, h, seed)
    if not side:
        return c
    if m == 'helm':
        if w == 1 or d_is_plate(w, h): return G[1] if j in (0, h - 1) else c                  # cheek plates: gold edges
        if face == 'north' and 4 <= j <= 6 and 1 <= i <= w - 2: return D if j != 4 else N[2]      # visor slit
        if face == 'north' and j in (3, 7) and 1 <= i <= w - 2: return G[1] if j == 3 else G[2]   # visor frame
        if face == 'north' and j == 5 and i in (1, w - 2): return G[2]
        if j == 0: return G[1]
        if j == h - 1: return G[2]
        if face in ('north', 'south', 'east', 'west') and j > 7 and i % 2 == 1 and j % 2 == 0: return P[3]   # vents
        if face in ('south',) and i == w // 2: return P[3]
    if m == 'crest':
        if j == 0 or j == h - 1: return G[1]
        return N[1] if face in ('north', 'south', 'east', 'west') and j == 1 else c
    if m == 'lame':
        if j == h - 1: return G[1]
        if j == 0: return N[2]
        if i % 4 == 0: return P[3]
    if m == 'cuirass':
        if face == 'north' and 3 <= i <= w - 4 and 1 <= j <= 7 and (i in (3, w - 4) or j in (1, 7)): return G[2]    # frame around the core gem
        if face == 'south':
            cx = (w - 1) // 2
            for (dx, dy, col) in ((0, 3, 'red'), (-3, 6, 'blue'), (3, 6, 'green'), (0, 9, 'yellow')):
                if i == cx + dx and j == dy: return GEM[col][1]
                if abs(i - (cx + dx)) <= 1 and abs(j - dy) <= 1 and (i, j) != (cx + dx, dy) and (abs(i - (cx + dx)) + abs(j - dy)) == 1: return GEM[col][3]
            if (abs(i - cx) + abs(j - 6) == 3) and 3 < j < 9: return G[1]                                           # diamond of the four elements
        if j == 0: return G[1] if i % 2 == 0 else G[2]
        if j == h - 1: return G[1]
        if j == h - 2: return G[2]
        if j == h - 4 and face in ('north', 'south'): return N[1]
        if face in ('north', 'south') and (i in (3, w - 4)) and 2 <= j <= h - 5: return P[3]    # panel seams
    if m == 'pauldron':
        if j == h - 1: return G[1]
        if j == h - 2: return G[2]
        if i == 0 or i == w - 1: return P[3] if j < h - 2 else c
    if m == 'vambrace':
        if j == 0 or j == h - 1: return G[1]
        if j == 1 or j == h - 2: return N[2]
        if j == 3: return P[3]
    if m == 'faulds' and face in ('north', 'south') and w >= 8 and i in (3, w - 4) and 0 < j < h - 1: return G[2]
    if m in ('faulds', 'cuff'):
        if j == h - 1: return G[1]
        if j == h - 2 and h > 3: return G[2]
        if j == 0 and m == 'faulds': return G[2]
    return c


def paint_box(im, u, v, b, seed, clear=()):
    m, x, y, z, w, h, d = b
    faces = [('up', u + d, v, w, d), ('down', u + d + w, v, w, d), ('west', u, v + d, d, h), ('north', u + d, v + d, w, h),
             ('east', u + d + w, v + d, d, h), ('south', u + 2 * d + w, v + d, w, h)]
    for name, fx, fy, fw, fh in faces:
        for j in range(fh):
            for i in range(fw):
                if (name, i, j) in clear: continue
                im.putpixel((fx + i, fy + j), (*paint(m, name, i, j, fw, fh, seed), 255))


def build(piece):
    W, H = SIZE[piece]
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    parts = S.BUILD[piece]()
    for pi, bi, u, v in pack(piece):
        name, bone, pose, boxes = parts[pi]
        b = boxes[bi]; clear = set()
        if piece == 'helmet' and name == 'hood':        # face opening: the golem's own face shows through
            m, x, y, z, w, h, d = b
            for j in range(4, 9):
                for i in range(1, w - 1): clear.add(('north', i, j))
        paint_box(im, u, v, b, pi * 7 + bi, clear)
    return im


def uvs(piece):
    return {(pi, bi): (u, v) for pi, bi, u, v in pack(piece)}


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    for p in S.PIECES:
        build(p).save(f'{out}/{p}.png')
