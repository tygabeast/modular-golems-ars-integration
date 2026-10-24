"""Upgrade items: 16x16 icons, models, apparatus recipes, guide entries and language. Original art (MIT)."""
from PIL import Image

# key, display name, modifier description (also used as guide text), accent colour, 7x7 glyph, reagent, pedestal items, source cost
UPGRADES = [
 dict(key='arcane_recall', name='Arcane Recall', accent=(170, 110, 255),
      guide='Upgrade for golems. When the golem is idle and strays too far from you, it teleports back to your side. Has a cooldown. Distance and cooldown can be set in the config.',
      glyph=["..XXX..", ".X...X.", "X..X..X", "X.XXX.X", "X..X..X", ".X...X.", "..XXX.."],
      reagent='minecraft:ender_pearl', cost=2500,
      ped=['ars_nouveau:source_gem'] * 2 + ['ars_nouveau:manipulation_essence'] * 2 + ['ars_nouveau:conjuration_essence'] * 2 + ['ars_nouveau:air_essence'] * 2),
 dict(key='spell_sponge', name='Spell Sponge', accent=(80, 220, 220),
      guide='Upgrade for golems. Magic damage, including Ars spells, is halved, and each magic hit heals the golem a little.',
      glyph=["..XXX..", ".XX.XX.", "XX.X.XX", "X.XXX.X", "XX.X.XX", ".XX.XX.", "..XXX.."],
      reagent='minecraft:amethyst_shard', cost=2500,
      ped=['ars_nouveau:abjuration_essence'] * 4 + ['ars_nouveau:source_gem'] * 2 + ['ars_nouveau:water_essence'] * 2),
 dict(key='magelight_core', name='Magelight Core', accent=(255, 236, 140),
      guide='Upgrade for golems. The golem glows with magelight: while you are close to it, you get Night Vision.',
      glyph=["...X...", "X..X..X", ".X.X.X.", "XXXXXXX", ".X.X.X.", "X..X..X", "...X..."],
      reagent='minecraft:glowstone', cost=2000,
      ped=['ars_nouveau:source_gem'] * 3 + ['ars_nouveau:fire_essence'] * 2 + ['ars_nouveau:air_essence'] * 2 + ['ars_nouveau:manipulation_essence']),
 dict(key='source_surge', name='Source Surge', accent=(255, 150, 60),
      guide='Upgrade for golems. When a mob hits you, nearby golems with this upgrade surge with Speed and Strength for a few seconds. Has a cooldown.',
      glyph=["...X...", "..XXX..", ".XXXXX.", "...X...", "..XXX..", ".XXXXX.", "...X..."],
      reagent='minecraft:redstone_block', cost=3000,
      ped=['ars_nouveau:source_gem'] * 4 + ['ars_nouveau:fire_essence'] * 2 + ['ars_nouveau:air_essence'] * 2),
 dict(key='glyph_strike', name='Glyph Strike', accent=(240, 110, 220),
      guide='Upgrade for golems. Hits sometimes lay a glyph effect on the target: Hex, Shocked or Snared (Slowness if Ars does not provide them). At most once per second.',
      glyph=["...X...", "..XXX..", ".XX.XX.", "XXX.XXX", ".XX.XX.", "..XXX..", "...X..."],
      reagent='ars_nouveau:wilden_horn', cost=3000,
      ped=['ars_nouveau:source_gem'] * 4 + ['ars_nouveau:conjuration_essence'] * 2 + ['ars_nouveau:abjuration_essence'] * 2),
]

# ---- icon drawing -------------------------------------------------------------------------------------------------
# Same structure as Modular Golems' own upgrade icons (framed bevelled tile, an outlined picture, a small up-arrow badge
# bottom right), drawn in this addon's purple, gold and accent colours. All art is procedural and original.
import math
OUT = (30, 16, 52)
def _mix(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
def _shade(c, f): return tuple(max(0, min(255, int(v * f))) for v in c)

def _frame(px):
    gold_hi, gold, gold_d = (255, 226, 120), (240, 196, 52), (176, 130, 30)
    edge_a, edge_b = (74, 42, 118), (52, 30, 88)
    for i in range(16):
        for (x, y) in ((i, 0), (i, 15), (0, i), (15, i)):
            near_end = i <= 2 or i >= 13
            px[x, y] = (*(gold if near_end else (edge_a if (i in (3, 4, 11, 12)) else edge_b)), 255)
    for (x, y) in ((0, 0), (15, 0), (0, 15), (15, 15)): px[x, y] = (*gold_hi, 255)
    for (x, y) in ((1, 1), (14, 1), (1, 14), (14, 14)): px[x, y] = (*gold_d, 255)
    for i in range(2, 14):
        px[i, 1] = (122, 78, 180, 255); px[14, i] = (110, 70, 166, 255)
        px[i, 14] = (62, 36, 100, 255); px[1, i] = (70, 42, 112, 255)
    for y in range(2, 14):
        for x in range(2, 14):
            px[x, y] = (*_mix((92, 58, 140), (70, 42, 108), (y - 2) / 11), 255)

def _outline(layer, w=12, h=12):
    """layer: dict (x,y)->rgb. returns dict with a dark 1px outline added around the shape."""
    out = dict(layer)
    for (x, y) in layer:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p = (x + dx, y + dy)
            if p not in layer: out[p] = OUT
    return out

def _picture(key):
    """Pictures are drawn in a 10x10 box (x, y in 1..10) around the centre (5.5, 5.5); the outline adds one more pixel."""
    L = {}
    def put(x, y, c): L[(x, y)] = c
    C = 5.5
    if key == 'arcane_recall':        # violet portal ring with a bright swirl and sparkles
        for y in range(12):
            for x in range(12):
                dx, dy = x - C, y - C
                r = math.hypot(dx, dy)
                if 2.5 <= r <= 4.6:
                    t = 0.5 + (-dx - dy) / (2 * 4.6) * 0.9
                    put(x, y, _mix((88, 48, 168), (214, 170, 255), max(0, min(1, t))))
                elif r < 2.5:
                    put(x, y, _mix((26, 12, 60), (60, 30, 120), 0.5 + dx * 0.1))
        for (x, y, c) in ((5, 4, (230, 200, 255)), (6, 5, (200, 150, 255)), (6, 6, (170, 110, 255)), (5, 7, (200, 150, 255)), (4, 6, (150, 100, 235)), (4, 5, (190, 140, 255))):
            put(x, y, c)
        put(6, 4, (255, 255, 255))
    elif key == 'spell_sponge':       # cyan sponge block with holes and a spark
        for y in range(3, 10):
            for x in range(1, 11):
                put(x, y, _mix((130, 238, 238), (40, 140, 160), (y - 3) / 6))
        for x in range(1, 11): put(x, 3, (190, 255, 255)); put(x, 9, (28, 110, 134))
        for (x, y) in ((3, 5), (7, 4), (5, 7), (8, 7), (2, 7), (9, 5), (6, 5)): put(x, y, (24, 96, 120))
        put(4, 4, (255, 255, 255))
        for (x, y, c) in ((8, 1, (255, 255, 255)), (7, 1, (170, 255, 255)), (9, 1, (170, 255, 255)), (8, 0, (170, 255, 255)), (8, 2, (170, 255, 255))): 
            if 0 <= y: put(x, y, c)
    elif key == 'magelight_core':     # glowing orb with rays
        for y in range(12):
            for x in range(12):
                r = math.hypot(x - C, y - C)
                if r <= 2.9:
                    put(x, y, _mix((255, 255, 250), (255, 214, 90), min(1, r / 2.9) ** 1.4))
        for (x, y) in ((5, 1), (6, 1), (5, 2), (6, 2), (5, 9), (6, 9), (5, 10), (6, 10), (1, 5), (1, 6), (2, 5), (2, 6), (9, 5), (9, 6), (10, 5), (10, 6)):
            put(x, y, (255, 240, 150))
        for (x, y) in ((2, 2), (9, 2), (2, 9), (9, 9), (3, 3), (8, 3), (3, 8), (8, 8)):
            put(x, y, (255, 208, 90))
    elif key == 'source_surge':       # lightning bolt
        poly = [(7, 1), (3, 6), (5.5, 6), (4, 10.5), (9, 4.8), (6.5, 4.8), (8.5, 1)]
        def inside(px_, py_):
            n = len(poly); c = False; j = n - 1
            for i in range(n):
                xi, yi = poly[i]; xj, yj = poly[j]
                if (yi > py_) != (yj > py_) and px_ < (xj - xi) * (py_ - yi) / (yj - yi) + xi: c = not c
                j = i
            return c
        for y in range(12):
            for x in range(12):
                if inside(x + 0.5, y + 0.5):
                    put(x, y, _mix((255, 232, 130), (226, 96, 24), (y - 1) / 9))
        for (x, y) in ((7, 2), (6, 4), (4, 6)):
            if (x, y) in L: put(x, y, (255, 250, 200))
    elif key == 'glyph_strike':       # faceted magenta rune stone
        for y in range(12):
            for x in range(12):
                dx, dy = x - C, y - C
                if abs(dx) + abs(dy) <= 4.6:
                    base = {(True, True): (255, 170, 240), (False, True): (240, 110, 220), (True, False): (196, 70, 180), (False, False): (140, 40, 130)}[(dx < 0, dy < 0)]
                    put(x, y, base)
                if abs(dx) + abs(dy) <= 2.6: put(x, y, (46, 14, 60))
        for (x, y) in ((5, 4), (6, 4), (5, 5), (6, 5), (5, 6), (6, 6), (5, 7), (6, 7), (4, 5), (7, 5), (4, 6), (7, 6)): put(x, y, (255, 214, 250))
        put(5, 5, (255, 255, 255)); put(6, 6, (255, 190, 245))
    return L

_ARROW = ["..XX..", ".XXXX.", "XXXXXX", ".XXXX.", "..XX..", "..XX..", "..XX.."]
def _arrow():
    L = {}
    for y, row in enumerate(_ARROW):
        for x, ch in enumerate(row):
            if ch == 'X':
                t = y / 6
                c = _mix((255, 238, 150), (196, 142, 28), t)
                if x <= 1 or (2 - x == y and y <= 2): c = _shade(c, 1.12)
                L[(x, y)] = c
    return L

def icon(u):
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0)); px = im.load()
    _frame(px)
    pic = _outline(_picture(u['key']))
    for (x, y), c in pic.items():
        X, Y = x + 2, y + 2                      # picture sits in the upper left of the plate
        if 2 <= X <= 13 and 2 <= Y <= 13: px[X, Y] = (*c, 255)
    arrow = _outline(_arrow())
    for (x, y), c in arrow.items():
        X, Y = x + 9, y + 8                      # up-arrow badge bottom right, like Modular Golems' upgrades
        if 2 <= X <= 15 and 2 <= Y <= 14: px[X, Y] = (*c, 255)
    return im

def build(w, R, lang, desc):
    import os
    os.makedirs(f'{R}/assets/modulargolems/textures/item', exist_ok=True)
    tag = []
    for u in UPGRADES:
        k = u['key']
        icon(u).save(f'{R}/assets/modulargolems/textures/item/{k}.png')
        w(f'assets/modulargolems/models/item/{k}.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'modulargolems:item/{k}'}})
        lang[f'item.modulargolems.{k}'] = f"{u['name']} Upgrade"
        w(f'data/mg_arcane/recipe/upgrade/{k}.json', {
            'type': 'ars_nouveau:enchanting_apparatus', 'keepNbtOfReagent': False,
            'pedestalItems': [{'item': i} for i in u['ped']], 'reagent': {'item': u['reagent']},
            'result': {'count': 1, 'id': f'modulargolems:{k}'}, 'sourceCost': u['cost']})
        w(f'assets/modulargolems/patchouli_books/golem_guide/en_us/entries/upgrades/{k}.json', {
            'flag': 'mod:ars_nouveau', 'name': f"{u['name']} Upgrade", 'icon': f'modulargolems:{k}',
            'category': 'modulargolems:upgrades', 'sortnum': 2000 + UPGRADES.index(u),
            'pages': [{'type': 'patchouli:spotlight', 'item': f'modulargolems:{k}', 'text': u['guide'] + '$(br2)Crafted at an Enchanting Apparatus.'}]})
        lang[f'modifier.modulargolems.{k}'] = u['name']
        tag.append({'id': f'modulargolems:{k}', 'required': False})
    w('data/modulargolems/tags/item/upgrades.json', {'values': tag})
