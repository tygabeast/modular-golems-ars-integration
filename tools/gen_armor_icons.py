"""16x16 inventory icons for the Arcane golem armour: violet cloth, thin gold trim, one pale clasp. All art is original."""
from gen_icons import P, _rect
import gen_armor as A
V, G, SV, D = A.V, A.G, A.SV, A.D


def shade(x, x0, x1):
    return V[0] if x == x0 else V[1] if x < (x0 + x1) / 2 else V[2] if x < x1 else V[3]


def helmet():
    p = P()
    _rect(p, 6, 1, 9, 2, lambda x, y: shade(x, 6, 9))                 # stepped peak
    _rect(p, 4, 3, 11, 4, lambda x, y: shade(x, 4, 11))
    _rect(p, 3, 5, 12, 13, lambda x, y: shade(x, 3, 12))              # hood
    for x in range(3, 13): p.s(x, 7, G[0] if x < 8 else G[1]); p.s(x, 8, G[2])   # circlet
    p.s(7, 7, SV[0]); p.s(8, 7, SV[1]); p.s(7, 8, SV[1]); p.s(8, 8, SV[2])
    for x in range(5, 11):                                            # face opening
        for y in range(9, 13): p.s(x, y, D)
    for x in range(3, 13): p.s(x, 13, V[3])
    p.outline(); return p.img()


def chestplate():
    p = P()
    _rect(p, 4, 3, 11, 14, lambda x, y: shade(x, 4, 11))              # tunic
    for x in range(4, 12): p.s(x, 3, G[1]); p.s(x, 13, G[1] if x < 8 else G[2]); p.s(x, 14, G[2])
    for (x0, x1) in ((0, 3), (12, 15)):                               # sleeves
        _rect(p, x0, 3, x1, 9, lambda x, y: shade(x, x0, x1))
        for x in range(x0, x1 + 1): p.s(x, 3, G[1]); p.s(x, 9, G[2])
    for y in range(5, 9): p.s(7, y, G[1]); p.s(8, y, G[2])            # scroll
    p.s(6, 6, G[1]); p.s(9, 7, G[2])
    p.s(7, 4, SV[0]); p.s(8, 4, SV[1])                                # clasp
    p.outline(); return p.img()


def leggings():
    p = P()
    for x in range(3, 13): p.s(x, 2, G[0] if x < 8 else G[1]); p.s(x, 3, V[1] if x < 8 else V[2]); p.s(x, 4, G[2])
    p.s(7, 3, SV[0]); p.s(8, 3, SV[1])
    _rect(p, 6, 5, 9, 11, lambda x, y: shade(x, 6, 9))                # tabard
    for x in range(6, 10): p.s(x, 11, G[1])
    for (x0, x1) in ((2, 6), (9, 13)):                                # hip guards
        _rect(p, x0, 5, x1, 8, lambda x, y: shade(x, x0, x1))
        for x in range(x0, x1 + 1): p.s(x, 8, G[1])
    p.outline(); return p.img()


def _boot(p, dx, dy, back):
    f = (lambda c: c) if not back else (lambda c: V[min(3, V.index(c) + 1)] if c in V else c)
    for y in range(3, 9):
        for x in range(7, 12): p.s(x + dx, y + dy, f(shade(x, 7, 11)))
    for y in range(9, 12):
        for x in range(3, 12): p.s(x + dx, y + dy, f(V[1] if y == 9 else V[2] if y == 10 else V[3]))
    for x in range(7, 12): p.s(x + dx, 3 + dy, G[1]); p.s(x + dx, 4 + dy, G[2])


def boots():
    p = P()
    _boot(p, 3, -2, True)
    _boot(p, 0, 1, False)
    p.outline(); return p.img()
