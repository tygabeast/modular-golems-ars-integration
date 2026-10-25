"""PROPOSAL: Aegis golem armour, a plate set in the manner of the Omniguard set (ivory plate, gold trim, the four elemental gems,
dark boots). Same rules as armor_spec.py: parts hang off the golem's bones in the bone's local coordinates; no rotations.
Materials: plate variants (helm, cuirass, pauldron, vambrace, faulds, cuff), navy, gold, and gems (red, blue, green, yellow)."""
PIECES = ['helmet', 'chestplate', 'leggings', 'boots']
Z = (0, 0, 0, 0, 0, 0)
SWAP = {'red': 'green', 'blue': 'yellow'}


def mir_arm(parts, bone_map, suffix, swap=None):
    out = []
    for name, bone, pose, boxes in parts:
        x, y, z, rx, ry, rz = pose
        nb = [((swap or {}).get(m, m), -(bx + w), by, bz, w, h, d) for (m, bx, by, bz, w, h, d) in boxes]
        out.append((name + suffix, bone_map[bone], (-x, y, z, rx, -ry, -rz), nb))
    return out


def mir_leg(parts, suffix):
    out = []
    for name, bone, pose, boxes in parts:
        x, y, z, rx, ry, rz = pose
        nb = [(m, -1 - (bx + w), by, bz, w, h, d) for (m, bx, by, bz, w, h, d) in boxes]
        out.append((name + suffix, 'left_leg', (-x, y, z, rx, -ry, -rz), nb))
    return out


def helmet():
    return [
        ('helm', 'head', Z, [('helm', -4.5, -12.5, -6, 9, 11, 9)]),
        ('crest', 'head', Z, [('crest', -1, -15.5, -5, 2, 3, 9)]),
        ('gem', 'head', Z, [('blue', -1, -11.5, -6.5, 2, 2, 1)]),
    ]


def chestplate():
    arm = [
        ('pauldron', 'right_arm', Z, [('pauldron', -15, -4.5, -4.5, 7, 3, 9), ('lame', -14.5, -1.5, -4, 6, 2, 8)]),
        ('sockets', 'right_arm', Z, [('gold', -14.5, -5.5, -2, 3, 1, 3), ('gold', -11.5, -5.5, -2, 3, 1, 3)]),
        ('gems', 'right_arm', Z, [('red', -14, -7.5, -1.5, 2, 2, 2), ('blue', -11, -7.5, -1.5, 2, 2, 2)]),
        ('vambrace', 'right_forearm', Z, [('vambrace', -13.5, 0.5, -6.5, 5, 7, 7)]),
    ]
    body = [
        ('cuirass', 'body', Z, [('cuirass', -9.5, -2.5, -6.5, 19, 13, 12)]),
        ('frame', 'body', Z, [('gold', -3, 0, -7.5, 6, 6, 1)]),
        ('core', 'body', Z, [('green', -2, 1, -8.5, 4, 4, 1)]),
        ('gorget', 'body', Z, [('pauldron', -5, -4.5, -4, 10, 2, 8)]),
    ]
    bm = {'right_arm': 'left_arm', 'right_forearm': 'left_forearm'}
    return body + arm + mir_arm(arm, bm, '_l', SWAP)


def leggings():
    body = [
        ('faulds', 'body', Z, [('faulds', -5.5, 9.5, -4, 11, 4, 8)]),
        ('tasset', 'body', Z, [('faulds', -3, 13.5, -4.75, 6, 5, 1)]),
        ('buckle', 'body', Z, [('gold', -1.5, 9.5, -5, 3, 3, 1)]),
    ]
    leg = [('cuff', 'right_leg', Z, [('cuff', -4, -4, -4, 7, 5, 7)])]
    return body + leg + mir_leg(leg, '_l')


def boots():
    leg = [('boot', 'right_leg', Z, [('boot', -4, 7.5, -3.5, 7, 5, 7)])]
    return leg + mir_leg(leg, '_l')


BUILD = {'helmet': helmet, 'chestplate': chestplate, 'leggings': leggings, 'boots': boots}
