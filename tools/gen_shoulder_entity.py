"""Entity texture for the Arcane Shoulder Wand (64x64), laid out for Modular Golems' beacon-cannon shoulder model.

On the golem's back the weapon rests upright (a mount with a straight tube pointing up) and swings forward to aim; here the
tube is painted as a wand (crystal tip, gold collar, wooden shaft) and the base as a crystal reservoir. Boxes (u, v, w, h, d):
  reservoir (0,0) 6x9x7 | cap (0,16) 6x5x7 | back plate (12,42) 4x11x2 | housing (26,0) 5x8x6
  wand (26,14) 3x14x5 | wand core (0,28) 2x14x4 | collars (32,33) and (32,40) 4x1x6 | joint (12,33) 5x4x5

  python3 gen_shoulder_entity.py <out_dir>   -> arcane_shoulder_wand.png
"""
import sys
from gen_bow_entity import Tex, OUT, CRY, GLOW, GOLD, GEM

WOOD = [(132, 78, 112), (98, 56, 86), (70, 38, 62)]


def framed(inner, edge=GOLD[1], corner=GOLD[2]):
    def f(i, j, w, h):
        if w >= 3 and h >= 3 and (i in (0, w - 1)) and (j in (0, h - 1)): return corner
        if i in (0, w - 1) or j in (0, h - 1): return edge
        return inner(i - 1, j - 1, w - 2, h - 2)
    return f


def crystal_fill(i, j, w, h):
    """Source reservoir: glowing near the top, deep violet at the bottom, a bright speck column on the left."""
    t = j / max(1, h - 1)
    shade = 0 if (i == 0 and j % 3 == 0) else 1 if t < 0.35 else 2 if t < 0.7 else 3
    if i == w - 1: shade = min(4, shade + 1)
    return CRY[shade]


def housing_face(i, j, w, h):
    return WOOD[0] if j == 0 else WOOD[1] if j < h - 1 else WOOD[2]


def housing_with_gem(i, j, w, h):
    cx, cy = (w - 1) / 2, (h - 1) / 2
    if abs(i - cx) <= 1 and abs(j - cy) <= 1: return GLOW if abs(i - cx) < 0.6 and abs(j - cy) < 0.6 else GEM[1 if (i + j) % 2 else 0]
    return housing_face(i, j, w, h)


def plate(i, j, w, h):
    if (i, j) in ((0, 1), (w - 1, 1), (0, h - 2), (w - 1, h - 2)): return GOLD[3]
    return GOLD[1] if i < w // 2 else GOLD[2]


def ring(i, j, w, h):
    return GOLD[0] if (i + j) % 3 else GOLD[1]


def core(i, j, w, h):
    return WOOD[1] if i % 2 else WOOD[2]


def joint(i, j, w, h):
    cx, cy = (w - 1) / 2, (h - 1) / 2
    if abs(i - cx) < 1 and abs(j - cy) < 1: return GEM[0]
    if i in (0, w - 1) or j in (0, h - 1): return GOLD[2]
    return GOLD[0] if j == 1 else GOLD[1]


def wand_side(i, j, w, h):
    """The tube is 14 rows tall, tip at the top: faceted crystal, a gold collar, then a wooden shaft with gem flecks."""
    last = w - 1
    if j == 0: return GLOW if i in (0, 1) else CRY[0]
    if j <= 4:
        shade = min(3, j - 1 + (1 if i == last else 0))
        return CRY[0] if (i == 0 and j <= 2) else CRY[shade]
    if j == 5: return GOLD[0] if i == 0 else GOLD[1] if i < last else GOLD[2]
    if j == h - 1: return GOLD[2]
    if (j + 2 * i) % 6 == 0: return GEM[1]
    return WOOD[0] if i == 0 else WOOD[1] if i < last else WOOD[2]


def wand_tip(i, j, w, h):
    return GLOW if (i, j) == (1, 2) else CRY[0] if i + j < 4 else CRY[1]


def wand_foot(i, j, w, h):
    return GOLD[2]


def build():
    t = Tex()
    t.box(0, 0, 6, 9, 7, framed(crystal_fill), framed(crystal_fill), framed(crystal_fill), framed(crystal_fill))
    t.box(0, 16, 6, 5, 7, framed(housing_face), framed(housing_face), framed(housing_with_gem), framed(housing_with_gem))
    t.box(12, 42, 4, 11, 2, plate, plate, plate, plate)
    t.box(26, 0, 5, 8, 6, framed(housing_face), framed(housing_face), framed(housing_with_gem), framed(housing_with_gem))
    t.box(0, 28, 2, 14, 4, core, core, core, core)
    t.box(26, 14, 3, 14, 5, wand_tip, wand_foot, wand_side, wand_side)
    t.box(32, 33, 4, 1, 6, ring, ring, ring, ring)
    t.box(32, 40, 4, 1, 6, ring, ring, ring, ring)
    t.box(12, 33, 5, 4, 5, joint, joint, joint, joint)
    return t.im


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    build().save(out + '/arcane_shoulder_wand.png')
