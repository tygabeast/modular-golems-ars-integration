"""Arcane Golem Armour: the shapes of the four pieces (cowl, gambeson, legguards, boots) for Modular Golems' Metal Golem.

Deliberately restrained, in the manner of Modular Golems' own Wind Spirit set: the head is covered, the torso is covered, the
upper arms and forearms get sleeves and cuffs, the hips get a guard and the feet get boots; the legs and most of the arms stay
visible. Every part hangs off one of the golem's own bones and uses that bone's local coordinates (+x = the golem's left,
-y = up, -z = front). A part is (name, bone, pose, boxes); pose = (x, y, z, rx, ry, rz) is the part's offset and rotation (radians)
inside the bone; a box is (material, x, y, z, w, h, d) with integer w, h, d.
Materials: cloth variants (tunic, sleeve, cuff, hood, sash, boot), gold, silver.
"""
PIECES = ['helmet', 'chestplate', 'leggings', 'boots']
Z = (0, 0, 0, 0, 0, 0)


def mir_arm(parts, bone_map, suffix):
    out = []
    for name, bone, pose, boxes in parts:
        x, y, z, rx, ry, rz = pose
        nb = [(m, -(bx + w) + (0.02 if False else 0), by, bz, w, h, d) for (m, bx, by, bz, w, h, d) in boxes]
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
        ('hood', 'head', Z, [('hood', -4.5, -12.5, -6, 9, 11, 9)]),
        ('circlet', 'head', Z, [('gold', -5, -9.5, -6.5, 10, 2, 10)]),
        ('gem', 'head', Z, [('silver', -1.5, -10, -7.5, 3, 3, 1)]),
        ('peak', 'head', Z, [('hood', -3, -14.5, -3, 6, 2, 7), ('hood', -2, -16.5, -0.5, 4, 2, 5)]),
    ]


def chestplate():
    arm = [
        ('sleeve', 'right_arm', Z, [('sleeve', -14.5, -3, -3.5, 6, 10, 7)]),
        ('cap', 'right_arm', Z, [('sleeve', -15, -4.5, -4, 6, 2, 8)]),
        ('cuff', 'right_forearm', Z, [('cuff', -13.5, 0.5, -6.5, 5, 7, 7)]),
    ]
    body = [
        ('tunic', 'body', Z, [('tunic', -9.5, -2.5, -6.5, 19, 13, 12)]),
        ('clasp', 'body', Z, [('silver', -2, -0.5, -7.5, 4, 5, 1)]),
    ]
    bm = {'right_arm': 'left_arm', 'right_forearm': 'left_forearm'}
    return body + arm + mir_arm(arm, bm, '_l')


def leggings():
    body = [
        ('sash', 'body', Z, [('sash', -5.5, 9.5, -4, 11, 3, 8)]),
        ('tabard', 'body', Z, [('sash', -3, 12, -4.75, 6, 6, 1)]),
        ('buckle', 'body', Z, [('silver', -1, 9.5, -5, 2, 2, 1)]),
    ]
    leg = [('hip', 'right_leg', (0, 0, 0, 0, 0, 0), [('sash', -4, -9, -3.5, 7, 5, 6)])]
    return body + leg + mir_leg(leg, '_l')


def boots():
    leg = [
        ('boot', 'right_leg', Z, [('boot', -4, 7.5, -3.5, 7, 5, 7)]),
    ]
    return leg + mir_leg(leg, '_l')


BUILD = {'helmet': helmet, 'chestplate': chestplate, 'leggings': leggings, 'boots': boots}
