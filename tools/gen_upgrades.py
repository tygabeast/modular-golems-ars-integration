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

def icon(u):
    a = u['accent']; im = Image.new('RGBA', (16, 16), (0, 0, 0, 0)); px = im.load()
    dark = (30, 16, 52); mid = (66, 34, 104); light = (104, 62, 156); gold = (240, 196, 52); gold_d = (176, 130, 30)
    # rounded plate 1..14
    for y in range(1, 15):
        for x in range(1, 15):
            if (x in (1, 14)) and (y in (1, 14)): continue
            t = (y - 1) / 13
            px[x, y] = (*[int(m + (l - m) * (1 - t)) for m, l in zip(mid, light)], 255)
    for x in range(2, 14):
        px[x, 1] = (*gold, 255); px[x, 14] = (*gold_d, 255)
    for y in range(2, 14):
        px[1, y] = (*gold, 255); px[14, y] = (*gold_d, 255)
    for y in range(3, 13):
        for x in range(3, 13): px[x, y] = (*dark, 255)
    g = u['glyph']
    for gy, row in enumerate(g):
        for gx, ch in enumerate(row):
            if ch == 'X':
                f = 1.0 if gy < 4 else 0.85
                px[4 + gx - 0, 4 + gy - 0] = (*[int(min(255, v * f)) for v in a], 255)
    # outline
    src = im.copy(); sp = src.load()
    for y in range(16):
        for x in range(16):
            if sp[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < 16 and 0 <= yy < 16 and sp[xx, yy][3] > 0: px[x, y] = (*dark, 255); break
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
