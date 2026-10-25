"""Source-tier golem weapons: procedural 32x32 held textures, 16x16 icons and a 16x16 mecha bow.
All art is original and drawn at 45 degrees on a (t, w) grid: t runs up the weapon, w runs across it.
Pixel (x, y) = (x0 + t + w, y0 - t + w), so w < 0 is the upper-left (lit) side."""
from PIL import Image

OUT = (30, 16, 52)
CRY = [(244, 228, 255), (206, 164, 255), (164, 114, 240), (118, 72, 196), (78, 44, 140)]   # lit -> shaded crystal
GLOW = (255, 244, 255)
GOLD = [(255, 236, 140), (240, 196, 52), (190, 140, 34), (130, 92, 28)]
WOOD = [(132, 78, 112), (98, 56, 86), (70, 38, 62)]
GEM = [(255, 190, 255), (232, 120, 255), (150, 60, 200)]


class Canvas:
    def __init__(self, size, x0, y0):
        self.n, self.x0, self.y0 = size, x0, y0
        self.px = {}

    def put(self, t, w, c):
        x, y = self.x0 + t + w, self.y0 - t + w
        for xx in (x, x + 1):
            if 0 <= xx < self.n and 0 <= y < self.n:
                self.px[(xx, y)] = c

    def raw(self, x, y, c):
        if 0 <= x < self.n and 0 <= y < self.n:
            self.px[(x, y)] = c

    def outline(self):
        add = {}
        for (x, y) in self.px:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                p = (x + dx, y + dy)
                if p not in self.px and 0 <= p[0] < self.n and 0 <= p[1] < self.n:
                    add[p] = OUT
        self.px.update(add)

    def image(self):
        im = Image.new('RGBA', (self.n, self.n), (0, 0, 0, 0))
        for (x, y), c in self.px.items():
            im.putpixel((x, y), (*c, 255))
        return im


def _blade_col(w, lo, hi):
    """crystal shading across the blade: lit edge, bright core line, shaded edge."""
    if w == lo: return CRY[0]
    if w == hi: return CRY[4]
    if w == 0: return CRY[1]
    return CRY[2] if w < 0 else CRY[3]


def sword(big=True):
    c = Canvas(32 if big else 16, 3 if big else 1, 28 if big else 14)
    if big:
        for t in (0, 1): [c.put(t, w, GOLD[1 if w else 0]) for w in (-1, 0, 1)]
        c.put(0, 0, GEM[1])
        for t in range(2, 7): c.put(t, 0, WOOD[t % 2])                   # grip
        for w in range(-3, 4):                                         # crossguard
            c.put(7, w, GOLD[0] if w < 0 else GOLD[1] if w == 0 else GOLD[2])
            if abs(w) <= 2: c.put(8, w, GOLD[1] if w < 0 else GOLD[2])
        c.put(7, 0, GEM[0]); c.put(8, 0, GEM[1])
        prof = [1, 1] + [2] * 10 + [1, 1, 1, 0]                                # blade half-width by t
        shade = {-2: CRY[0], -1: CRY[1], 0: CRY[2], 1: CRY[3], 2: CRY[4]}
        for i, hw in enumerate(prof):
            for w in range(-hw, hw + 1):
                col = shade[w] if hw == 2 else {-1: CRY[0], 0: CRY[1], 1: CRY[3]}[w]
                if w == 0 and i in (3, 4, 8, 9): col = GLOW                    # rune glints on the fuller
                if w == -hw and i == len(prof) - 1: col = CRY[0]
                c.put(9 + i, w, col)
        c.put(9 + len(prof), 0, CRY[0])
    else:
        c.put(0, 0, GOLD[1]); c.put(1, 0, WOOD[0]); c.put(2, 0, WOOD[1])
        for w in (-2, -1, 0, 1, 2): c.put(3, w, GOLD[0] if w < 0 else GOLD[2])
        c.put(3, 0, GEM[0])
        prof = [0] * 7 + [0, 0, 0]
        for i, hw in enumerate(prof):
            for w in range(-hw, hw + 1):
                col = GLOW if i % 3 == 1 else CRY[1] if i % 2 else CRY[0]
                c.put(4 + i, w, col)
        c.put(4 + len(prof), 0, CRY[0])
    c.outline()
    return c.image()


def axe(big=True):
    c = Canvas(32 if big else 16, 3 if big else 1, 28 if big else 14)
    if big:
        c.put(0, 0, GEM[1]); c.put(1, 0, GOLD[1])
        for t in range(2, 23): c.put(t, 0, WOOD[t % 3 if t % 3 < 3 else 0] if t not in (6, 7, 15) else GOLD[1])
        for t in (13, 14):                                              # collar
            for w in (-1, 0, 1): c.put(t, w, GOLD[0] if w < 0 else GOLD[2])
        # crescent head on the lit side: outer disc minus inner disc, cutting edge convex outward
        import math
        for t in range(12, 25):
            for w in range(-9, 0):
                ro = math.hypot(t - 18.0, w - 0.5)
                ri = math.hypot(t - 18.5, w - 3.0)
                if ro <= 7.6 and ri > 5.6:
                    d = ro / 7.6
                    col = CRY[0] if d > 0.86 else CRY[1] if d > 0.62 else CRY[2] if d > 0.4 else CRY[3]
                    if ri < 6.6: col = GOLD[1] if (t + w) % 3 == 0 else col      # inner trim
                    c.put(t, w, col)
        c.put(18, -7, GLOW); c.put(17, -7, GLOW); c.put(14, -5, GLOW)
        for t, e in {16: 1, 17: 2, 18: 3, 19: 2, 20: 1}.items():                     # back spike
            for w in range(1, e + 1): c.put(t, w, CRY[3] if w < e else CRY[4])
        c.put(17, -3, GLOW); c.put(18, -3, GLOW); c.put(16, -2, GLOW)
        c.put(23, 0, GOLD[0])
    else:
        c.put(0, 0, GOLD[1])
        for t in range(1, 12): c.put(t, 0, WOOD[t % 2])
        for t, e in {8: 1, 9: 2, 10: 2, 11: 2, 12: 1}.items():
            for w in range(-e, 0): c.put(t, w, CRY[0] if w == -e else CRY[1] if w > -e + 1 else CRY[2])
        c.put(10, 1, CRY[3]); c.put(11, 1, CRY[4])
        c.put(10, -1, GLOW)
        c.put(12, 0, GOLD[0])
    c.outline()
    return c.image()


def spear(big=True):
    c = Canvas(32 if big else 16, 2 if big else 1, 29 if big else 14)
    if big:
        c.put(0, 0, GEM[1])
        for t in range(1, 21): c.put(t, 0, WOOD[t % 3] if t not in (8, 9, 17) else GOLD[1])
        for w in (-1, 0, 1): c.put(19, w, GOLD[0] if w < 0 else GOLD[2]); c.put(20, w, GOLD[1] if w < 0 else GOLD[3])
        prof = [1, 1, 2, 2, 2, 1, 1, 1, 0, 0]                            # leaf head
        for i, hw in enumerate(prof):
            for w in range(-hw, hw + 1):
                col = _blade_col(w, -hw, hw)
                if w == 0 and hw >= 1: col = GLOW if i in (2, 5) else CRY[1]
                c.put(21 + i, w, col)
        c.put(21 + len(prof), 0, CRY[0])
    else:
        c.put(0, 0, GOLD[1])
        for t in range(1, 9): c.put(t, 0, WOOD[t % 2])
        c.put(8, -1, GOLD[0]); c.put(8, 1, GOLD[2])
        for i, hw in enumerate([0, 1, 1, 0, 0, 0]):
            for w in range(-hw, hw + 1):
                c.put(9 + i, w, CRY[0] if w == -hw and hw else CRY[3] if w == hw and hw else GLOW if w == 0 and i == 2 else CRY[1])
        c.put(15, 0, CRY[0])
    c.outline()
    return c.image()


def bow():
    """16x16 mecha bow: jointed crystal limbs, gold riser block with a gem, cam wheels at the tips, glowing string."""
    import math
    P = {}
    cx, cy, r = 13.0, 13.0, 10.5
    for k in range(6, 85, 2):
        a = math.radians(k)
        x, y = round(cx - r * math.sin(a)), round(cy - r * math.cos(a))
        col = CRY[0] if k < 30 else CRY[1] if k < 60 else CRY[2]
        P[(x, y)] = col
        P[(x + 1, y)] = CRY[3]
        if k in (24, 26, 64, 66): P[(x, y)] = GOLD[1]; P[(x + 1, y)] = GOLD[2]   # joint bands
    for (x, y) in ((4, 4), (5, 4), (4, 5), (5, 5), (6, 5), (5, 6)): P[(x, y)] = GOLD[1]
    P[(4, 4)] = GOLD[0]; P[(6, 5)] = GOLD[2]; P[(5, 6)] = GOLD[2]; P[(5, 5)] = GEM[0]
    for (cx2, cy2) in ((13, 2), (2, 13)):                                  # cam wheels
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if (dx, dy) != (0, 0): P[(cx2 + dx, cy2 + dy)] = GOLD[0] if dx + dy < 0 else GOLD[1] if dx + dy == 0 else GOLD[2]
        P[(cx2, cy2)] = OUT
    for k in range(4, 12):
        P.setdefault((15 - k, k), (240, 226, 255))
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for (x, y), c in P.items():
        if 0 <= x < 16 and 0 <= y < 16: im.putpixel((x, y), (*c, 255))
    O = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for (x, y) in P:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in P and 0 <= q[0] < 16 and 0 <= q[1] < 16: O.putpixel(q, (*OUT, 255))
    O.alpha_composite(im)
    return O


def build_all():
    return {
        'sword': sword(True), 'sword_icon': sword(False),
        'axe': axe(True), 'axe_icon': axe(False),
        'spear': spear(True), 'spear_icon': spear(False),
        'bow': bow(),
    }


if __name__ == '__main__':
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    for k, im in build_all().items():
        im.save(f'{out}/{k}.png')


# ---- data generation -----------------------------------------------------------------------------------------------
PARENT = {'sword': 'modulargolems:item/sword', 'axe': 'modulargolems:item/battle_axe', 'spear': 'modulargolems:item/long_weapon'}
SG, ES = 'ars_nouveau:source_gem', 'ars_nouveau:{}_essence'
WEAPONS = [  # key, display name, vanilla-golem reagent, pedestal items, source cost
    dict(key='arcane_golem_sword', kind='sword', name='Arcane Golem Sword', reagent='modulargolems:diamond_golem_sword',
         ped=[SG] * 4 + [ES.format('manipulation')] * 2 + [ES.format('abjuration'), ES.format('fire')], cost=4000),
    dict(key='arcane_golem_axe', kind='axe', name='Arcane Golem Axe', reagent='modulargolems:diamond_golem_axe',
         ped=[SG] * 4 + [ES.format('earth')] * 2 + [ES.format('manipulation'), ES.format('fire')], cost=4000),
    dict(key='arcane_golem_spear', kind='spear', name='Arcane Golem Spear', reagent='modulargolems:diamond_golem_spear',
         ped=[SG] * 4 + [ES.format('air')] * 2 + [ES.format('manipulation'), ES.format('conjuration')], cost=4000),
    dict(key='arcane_mecha_bow', kind='bow', name='Arcane Mecha Bow', reagent='modulargolems:iron_mecha_bow',
         ped=[SG] * 4 + [ES.format('air')] * 2 + [ES.format('conjuration')] * 2, cost=4000),
]
GUIDE = {
    'sword': 'A golem sword that casts a spell on every hit, like the Enchanter\'s Sword. Place it on a Scribe\'s Table, make a spell in your spell book, then shift-right click the table with that spell active. The spell must not have a Form glyph: the weapon provides Touch.',
    'axe': 'A golem axe that casts a spell on hit. Scribe it exactly like the Enchanter\'s Sword: no Form glyph, the weapon provides Touch.',
    'spear': 'A golem spear that casts a spell on hit. Scribe it exactly like the Enchanter\'s Sword: no Form glyph, the weapon provides Touch.',
    'bow': 'A golem mecha bow that fires spell arrows, like the Enchanter\'s Bow. Place it on a Scribe\'s Table, make a spell in your spell book, then shift-right click the table with that spell active. The spell must not have a Form glyph: the bow provides Projectile. It needs no arrows. Without a spell it is an ordinary mecha bow.',
}
NOTE = '$(br2)Ars Nouveau does not charge golems mana, so casts are limited by a cooldown (and an optional cost cap) in the config. Crafted at an Enchanting Apparatus from the matching diamond golem weapon.'


def build(w, R, lang):
    import os
    d = f'{R}/assets/modulargolems/textures/item/equipments'
    os.makedirs(d, exist_ok=True)
    imgs = build_all()
    import gen_bow_entity
    e = f'{R}/assets/modulargolems/textures/equipments'
    os.makedirs(e, exist_ok=True)
    gen_bow_entity.build(False).save(f'{e}/arcane_mecha_bow.png')
    gen_bow_entity.build(True).save(f'{e}/arcane_mecha_bow_pulling.png')
    cat = 'modulargolems:arcane_weapons'
    w('assets/modulargolems/patchouli_books/golem_guide/en_us/categories/arcane_weapons.json', {
        'name': 'Arcane Weapons', 'description': 'Golem weapons that cast Ars Nouveau spells', 'icon': 'modulargolems:arcane_golem_sword', 'flag': 'mod:ars_nouveau'})
    for i, wp in enumerate(WEAPONS):
        k, kind = wp['key'], wp['kind']
        if kind == 'bow':
            imgs['bow'].save(f'{d}/{k}.png')
            w(f'assets/modulargolems/models/item/{k}.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'modulargolems:item/equipments/{k}'}})
        else:
            imgs[kind].save(f'{d}/{k}.png'); imgs[kind + '_icon'].save(f'{d}/{k}_icon.png')
            w(f'assets/modulargolems/models/item/{k}.json', {
                'base': {'parent': PARENT[kind], 'textures': {'layer0': f'modulargolems:item/equipments/{k}'}},
                'gui_light': 'front', 'loader': 'neoforge:separate_transforms',
                'perspectives': {'gui': {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'modulargolems:item/equipments/{k}_icon'}}}})
        lang[f'item.modulargolems.{k}'] = wp['name']
        w(f'data/mg_arcane/recipe/weapon/{k}.json', {
            'type': 'ars_nouveau:enchanting_apparatus', 'keepNbtOfReagent': False,
            'neoforge:conditions': [{'type': 'neoforge:mod_loaded', 'modid': 'ars_nouveau'}],
            'pedestalItems': [{'item': x} for x in wp['ped']], 'reagent': {'item': wp['reagent']},
            'result': {'count': 1, 'id': f'modulargolems:{k}'}, 'sourceCost': wp['cost']})
        w(f'assets/modulargolems/patchouli_books/golem_guide/en_us/entries/arcane_weapons/{k}.json', {
            'flag': 'mod:ars_nouveau', 'name': wp['name'], 'icon': f'modulargolems:{k}', 'category': cat, 'sortnum': 3000 + i,
            'pages': [{'type': 'patchouli:spotlight', 'item': f'modulargolems:{k}', 'text': GUIDE[kind] + NOTE}]})

    # registrate's .tag() only runs at datagen time, so the tags the items need at runtime are shipped here
    def ids(kinds): return [{'id': f'modulargolems:{x["key"]}', 'required': False} for x in WEAPONS if x['kind'] in kinds]
    w('data/minecraft/tags/item/enchantable/sword.json', {'values': ids(('sword', 'axe', 'spear'))})
    w('data/minecraft/tags/item/enchantable/sharp_weapon.json', {'values': ids(('sword', 'axe', 'spear'))})
    w('data/minecraft/tags/item/enchantable/bow.json', {'values': ids(('bow',))})
    w('data/modulargolems/tags/item/shield_breaker_weapons.json', {'values': ids(('axe', 'spear'))})
