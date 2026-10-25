"""Entity (held-by-golem) textures for the Arcane Mecha Bow, 64x64, laid out for Modular Golems' code-defined bow model.

The model (GolemBows.createMainHand) is a set of boxes; each box reads its six faces from a fixed place in the texture, so the
layout below follows the box sizes and texture offsets of that model. Everything painted here is original art in the mg_arcane
crystal / gold palette (see gen_weapons.py for the item art that uses the same colours).

  python3 gen_bow_entity.py <out_dir>   -> arcane_mecha_bow.png, arcane_mecha_bow_pulling.png
"""
import sys
from PIL import Image

OUT = (30, 16, 52)
CRY = [(244, 228, 255), (206, 164, 255), (164, 114, 240), (118, 72, 196), (78, 44, 140)]
GLOW = (240, 226, 255)
GOLD = [(255, 236, 140), (240, 196, 52), (190, 140, 34), (130, 92, 28)]
GEM = [(255, 190, 255), (232, 120, 255), (150, 60, 200)]


class Tex:
    def __init__(self):
        self.im = Image.new('RGBA', (64, 64), (0, 0, 0, 0))

    def px(self, x, y, c):
        if 0 <= x < 64 and 0 <= y < 64: self.im.putpixel((x, y), (*c, 255))

    def rect(self, x, y, w, h, fn):
        for j in range(h):
            for i in range(w): self.px(x + i, y + j, fn(i, j, w, h))

    def box(self, u, v, w, h, d, top, bottom, side, end):
        """Paints the six faces of a w x h x d model box whose texture offset is (u, v).
        side(i, j, w, h) paints the faces along the box's length, end() the two end faces, top/bottom the caps."""
        self.rect(u + d, v, w, d, top)              # top
        self.rect(u + d + w, v, w, d, bottom)       # bottom
        self.rect(u, v + d, d, h, side)             # west
        self.rect(u + d, v + d, w, h, end)          # north
        self.rect(u + d + w, v + d, d, h, side)     # east
        self.rect(u + 2 * d + w, v + d, w, h, end)  # south


# ---- paint functions ---------------------------------------------------------------------------------------------------

def limb(i, j, w, h):
    """Crystal limb face, lit on the left, glowing toward the tip (top rows), with a gold joint band every few pixels."""
    if j % 4 == 3: return GOLD[1] if i == 0 else GOLD[2]
    shade = min(3, 1 + j // 3)
    if w <= 2 and i == w - 1: shade = min(4, shade + 1)
    if i == 0: shade = max(0, shade - 1)
    return CRY[shade]


def limb_end(i, j, w, h):
    return CRY[3] if j < h - 1 else CRY[4]


def cap(i, j, w, h):
    return GOLD[1]


def stub(i, j, w, h):
    """Short crystal limb root (2x2x4) with a gold ring."""
    return GOLD[1] if i == w - 1 or j == 0 else CRY[1 + (i + j) % 2]


def riser_side(i, j, w, h):
    if j == 0: return GOLD[0] if i % 5 else GOLD[1]
    if i % 5 == 4: return GOLD[3]
    if i in (3, 4, 5) and w >= 8: return GEM[1 if i == 4 else 2] if i == 4 else GOLD[2]
    return GOLD[2]


def riser_end(i, j, w, h):
    return GOLD[2]


def gem_face(i, j, w, h):
    return GEM[0] if (i + j) % 3 == 0 else GEM[1] if (i + j) % 3 == 1 else GEM[2]


def cam_side(i, j, w, h):
    """Cam wheel long faces: gold with an axle line down the middle."""
    if j == h // 2: return GOLD[3]
    return GOLD[0] if j == 0 else GOLD[1] if j < h // 2 else GOLD[2]


def cam_end(i, j, w, h):
    cx, cy = w // 2, h // 2
    if (i, j) == (cx, cy): return OUT
    return GOLD[0] if i + j < cx + cy else GOLD[2] if i + j > cx + cy else GOLD[1]


def cam_cap(i, j, w, h):
    return GOLD[1]


# ---- the plane that carries the string (and the arrow while drawing) ---------------------------------------------------

def line(t, p0, p1, col, thick=False, mirror=False, edge=None):
    (x0, y0), (x1, y1) = p0, p1
    n = max(abs(x1 - x0), abs(y1 - y0))
    for k in range(n + 1):
        x = round(x0 + (x1 - x0) * k / n)
        y = round(y0 + (y1 - y0) * k / n)
        c = col(k, n) if callable(col) else col
        for xx in ((x, 43 - x) if mirror else (x,)):
            t.px(xx, y, c)
            if thick: t.px(xx + 1, y, edge or CRY[1])


def plane(t, pulling):
    """East face of the string plane is x22..43, y22..43 (the west face is the same drawing mirrored)."""
    tipA, tipB = (25, 22), (43, 40)
    if not pulling:
        line(t, tipA, tipB, GLOW, thick=True, edge=CRY[1], mirror=True)
        return
    nock = (39, 26)
    line(t, tipA, nock, GLOW, thick=False, mirror=True)
    line(t, nock, tipB, GLOW, thick=False, mirror=True)
    head = (23, 41)
    # shaft: alternating glow / crystal so the arrow reads as an energy bolt
    line(t, nock, (head[0] + 2, head[1] - 2), lambda k, n: GLOW if k % 2 == 0 else CRY[1])
    # crystal arrow head
    for (x, y, c) in ((22, 43, CRY[3]), (22, 42, CRY[2]), (23, 42, CRY[1]), (22, 41, CRY[2]), (23, 41, CRY[0]), (24, 41, CRY[1]),
                      (23, 40, CRY[1]), (24, 40, CRY[0]), (25, 40, CRY[2]), (24, 42, CRY[2]), (23, 43, CRY[3]), (24, 43, CRY[4])):
        t.px(x, y, c)
    # fletching
    for (x, y, c) in ((36, 25, GEM[1]), (37, 24, GEM[0]), (38, 23, GEM[1]), (39, 22, GEM[0]), (41, 24, GEM[1]), (42, 23, GEM[0]),
                      (40, 25, GEM[2]), (41, 26, GEM[2]), (40, 27, GEM[1]), (37, 28, GEM[2]), (38, 28, GEM[1]), (39, 22, GEM[0]),
                      (35, 27, GEM[2]), (36, 28, GEM[1]), (41, 22, GEM[1]), (42, 25, GEM[2])):
        t.px(x, y, c)


def build(pulling):
    t = Tex()
    # "crossbow" bar = the riser: 2x2x10 at (0,44)
    t.box(0, 44, 2, 2, 10, riser_end, riser_end, riser_side, riser_end)
    # little crystal blocks at the limb roots: 2x2x4 at (24,44)
    t.box(24, 44, 2, 2, 4, stub, stub, stub, stub)
    # grip gem: 1x3x3 at (24,50)
    t.box(24, 50, 1, 3, 3, gem_face, gem_face, gem_face, gem_face)
    # long limbs: 2x8x2 at (44,34) and (44,44)
    t.box(44, 34, 2, 8, 2, cap, cap, limb, limb_end)
    t.box(44, 44, 2, 8, 2, cap, cap, limb, limb_end)
    # cam wheels: 3x3x6 at (44,9)
    t.box(44, 9, 3, 3, 6, cam_cap, cam_cap, cam_side, cam_end)
    plane(t, pulling)
    return t.im


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    build(False).save(out + '/arcane_mecha_bow.png')
    build(True).save(out + '/arcane_mecha_bow_pulling.png')
