"""Texture packing/painting for the Arcane Golem Armour (shapes in armor_spec.py). All art is original: deep violet cloth, gold
scroll trim and pale silver clasps.

  python3 gen_armor.py <out_dir>   -> helmet.png, chestplate.png, leggings.png, boots.png (one texture per piece)
"""
import sys
from PIL import Image
import armor_spec as S

SIZE = {'helmet': (64, 64), 'chestplate': (128, 64), 'leggings': (64, 32), 'boots': (64, 32)}
V = [(106, 72, 170), (82, 50, 140), (62, 36, 112), (44, 24, 84)]            # violet cloth, light -> dark
D = (30, 14, 58)                                                               # seam / shadow
G = [(255, 236, 140), (240, 196, 52), (190, 140, 34), (130, 92, 28)]          # gold
SV = [(248, 248, 255), (204, 208, 244), (150, 156, 210), (104, 108, 168)]      # silver

CURL = ["######.",
        "#.....#",
        "#.###.#",
        "#.#.#.#",
        "#.#.###",
        "#.#....",
        "#.#####"]


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


def cloth_base(face, i, j, w, h, seed):
    s = {'up': 0, 'down': 3, 'west': 2, 'east': 1, 'north': 1, 'south': 2}[face]
    if face in ('west', 'east', 'north', 'south') and h >= 6 and j > h * 0.7: s += 1
    r = hsh(i, j, seed)
    if r > 0.86: s -= 1
    elif r < 0.12: s += 1
    if face in ('west', 'east', 'north', 'south') and j % 2 == 1 and hsh(j, i // 3, seed + 5) > 0.55: s += 1   # woven thread rows
    c = V[max(0, min(3, s))]
    k = int((hsh(i, j, seed + 11) - 0.5) * 10)                                                              # fine grain
    return tuple(max(0, min(255, v + k)) for v in c)


def gold_line(j, rows):  # a 1px gold line with shading
    return G[1]


def stamp(sprite, i, j, ox, oy, mirror=False):
    sw = len(sprite[0])
    x = i - ox; y = j - oy
    if mirror: x = sw - 1 - x
    if 0 <= y < len(sprite) and 0 <= x < sw and sprite[y][x] == '#': return True
    return False


def paint(m, face, i, j, w, h, seed):
    if m == 'gold':
        s = {'up': 0, 'down': 3, 'west': 2, 'east': 2, 'north': 1, 'south': 2}[face]
        if i == 0 or j == 0: s = max(0, s - 1)
        elif i == w - 1 or j == h - 1: s = min(3, s + 1)
        return G[s]
    if m == 'silver':
        cx, cy = (w - 1) / 2, (h - 1) / 2
        if face in ('up', 'down') or w <= 1 or h <= 1: return SV[2]
        edge = i in (0, w - 1) or j in (0, h - 1)
        if edge: return G[2] if (i + j) % 2 else G[1]
        return SV[0] if (i + j) % 3 == 0 else SV[1] if (i + j) % 3 == 1 else SV[2]
    # ---- cloth variants
    c = cloth_base(face, i, j, w, h, seed)
    side = face in ('west', 'east', 'north', 'south')
    if m == 'tunic' and side:
        if j == 0 and face != 'up': return G[1] if i % 2 == 0 else G[2]            # collar line
        if j == h - 1: return G[1]                                                    # hem
        if j == h - 2: return G[2]
        if j == h - 4 and face in ('north', 'south'): return D                        # belt line
        if face == 'north':
            if stamp(CURL, i, j, 3, 3) or stamp(CURL, i, j, w - 10, 3, True): return G[1]
        if face == 'south':
            if stamp(CURL, i, j, 3, 3) or stamp(CURL, i, j, w - 10, 3, True): return G[2]
    if m == 'sleeve' and side:
        if j == h - 1: return G[1]
        if j == h - 2: return G[2]
        if j == 0: return G[2]
    if m == 'cuff' and side:
        if j == 0 or j == h - 1: return G[1]
        if j == 1 and h > 4: return G[2]
        if j == h - 2 and h > 4: return D
    if m == 'hood' and side:
        if j == h - 1: return D
    if m == 'sash' and side:
        if j == 0: return G[1]
        if j == h - 1: return G[1] if h > 1 else c
        if j == h - 2 and h > 3: return G[2]
    if m == 'boot' and side:
        if j == h - 1: return D
        if j == 0: return G[1]
        if j == 1 and h > 4: return G[2]
        if face == 'north' and j > h - 3: return V[3]
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
