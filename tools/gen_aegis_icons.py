"""16x16 inventory icons for the Aegis golem armour: ivory plate, gold trim, elemental gems, navy boots. All art is original."""
from gen_icons import P, _rect
import gen_aegis as A
PL, N, G, D, GEM = A.P, A.N, A.G, A.D, A.GEM


def shade(x, x0, x1, ramp=PL):
    return ramp[0] if x == x0 else ramp[1] if x < (x0 + x1) / 2 else ramp[2] if x < x1 else ramp[3]


def helmet():
    p = P()
    _rect(p, 6, 0, 9, 2, lambda x, y: G[1] if y == 0 else shade(x, 6, 9))                  # crest
    p.s(7, 1, N[1]); p.s(8, 1, N[1])
    _rect(p, 3, 3, 12, 13, lambda x, y: shade(x, 3, 12))                                   # helm
    for x in range(3, 13): p.s(x, 3, G[0] if x < 8 else G[1]); p.s(x, 13, G[2])
    for x in range(4, 12): p.s(x, 6, G[1]); p.s(x, 10, G[2])
    for x in range(5, 11):                                                                 # visor
        for y in range(7, 10): p.s(x, y, D if y != 7 else N[2])
    p.s(7, 4, GEM['blue'][0]); p.s(8, 4, GEM['blue'][1])
    p.outline(); return p.img()


def chestplate():
    p = P()
    _rect(p, 4, 3, 11, 14, lambda x, y: shade(x, 4, 11))
    for x in range(4, 12): p.s(x, 3, G[1]); p.s(x, 13, G[1] if x < 8 else G[2]); p.s(x, 14, G[2]); p.s(x, 11, N[1])
    for (x0, x1, a, b) in ((0, 3, 'red', 'blue'), (12, 15, 'green', 'yellow')):               # pauldrons
        _rect(p, x0, 4, x1, 6, lambda x, y: shade(x, x0, x1))
        for x in range(x0, x1 + 1): p.s(x, 4, G[1]); p.s(x, 7, G[2]); p.s(x, 6, N[2])
        p.s(x0, 3, GEM[a][1]); p.s(x0 + 1, 3, GEM[a][2]); p.s(x1 - 1, 3, GEM[b][1]); p.s(x1, 3, GEM[b][2])
    _rect(p, 6, 6, 9, 9, lambda x, y: G[1] if x in (6, 9) or y in (6, 9) else GEM['green'][1])   # core gem
    p.s(7, 7, GEM['green'][0])
    p.outline(); return p.img()


def leggings():
    p = P()
    _rect(p, 3, 2, 12, 5, lambda x, y: shade(x, 3, 12))
    for x in range(3, 13): p.s(x, 2, G[0] if x < 8 else G[1]); p.s(x, 5, G[2])
    p.s(7, 3, G[1]); p.s(8, 3, G[1]); p.s(7, 4, G[2]); p.s(8, 4, G[2])
    _rect(p, 6, 6, 9, 12, lambda x, y: shade(x, 6, 9))                                       # tasset
    for x in range(6, 10): p.s(x, 12, G[1])
    for (x0, x1) in ((2, 6), (9, 13)):                                                        # leg cuffs
        _rect(p, x0, 6, x1, 10, lambda x, y: shade(x, x0, x1))
        for x in range(x0, x1 + 1): p.s(x, 6, N[2]); p.s(x, 10, G[1])
    p.outline(); return p.img()


def _boot(p, dx, dy, back):
    f = (lambda c: c) if not back else (lambda c: N[min(3, N.index(c) + 1)] if c in N else c)
    for y in range(3, 9):
        for x in range(7, 12): p.s(x + dx, y + dy, f(shade(x, 7, 11, N)))
    for y in range(9, 12):
        for x in range(3, 12): p.s(x + dx, y + dy, f(N[1] if y == 9 else N[2] if y == 10 else N[3]))
    for x in range(7, 12): p.s(x + dx, 3 + dy, G[1]); p.s(x + dx, 4 + dy, G[2])


def boots():
    p = P()
    _boot(p, 3, -2, True)
    _boot(p, 0, 1, False)
    p.outline(); return p.img()
