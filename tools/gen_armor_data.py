"""Data for the Arcane golem armour: worn textures, inventory icons, item models, recipes, tags, Guide pages, language."""
import os
import gen_armor, gen_armor_icons

SG, ES = 'ars_nouveau:source_gem', 'ars_nouveau:{}_essence'
PIECES = [  # spec piece, item key, display name, vanilla reagent, pedestals, source cost, enchantable tag, guide blurb
    dict(p='helmet', key='arcane_helmet', name='Arcane Cowl', reagent='minecraft:diamond_helmet', tag='head_armor',
         ped=[SG] * 4 + [ES.format('abjuration')] * 2 + [ES.format('manipulation')] * 2, cost=3000, armor=11),
    dict(p='chestplate', key='arcane_chestplate', name='Arcane Tunic', reagent='minecraft:diamond_chestplate', tag='chest_armor',
         ped=[SG] * 4 + [ES.format('abjuration')] * 4, cost=5000, armor=14),
    dict(p='leggings', key='arcane_shinguard', name='Arcane Sash', reagent='minecraft:diamond_leggings', tag='leg_armor',
         ped=[SG] * 4 + [ES.format('abjuration')] * 2 + [ES.format('earth')] * 2, cost=4000, armor=8),
    dict(p='boots', key='arcane_boots', name='Arcane Boots', reagent='minecraft:diamond_boots', tag='foot_armor',
         ped=[SG] * 4 + [ES.format('abjuration')] * 2 + [ES.format('air')] * 2, cost=3000, armor=6),
]
GUIDE = ('Part of the Arcane armour for Metal Golems: violet cloth and gold, in the manner of the Battlemage outfit. Each piece worn gives the golem one level of '
         'Source Mantle: 4%% less magic damage and 1 health regained every 5 seconds, so the full set gives 16%% and about 0.8 health per second. '
         'Armour %d, toughness 6 (diamond tier). Crafted at an Enchanting Apparatus from the matching diamond armour piece.')


def build(w, R, lang):
    icons = {'helmet': gen_armor_icons.helmet(), 'chestplate': gen_armor_icons.chestplate(),
             'leggings': gen_armor_icons.leggings(), 'boots': gen_armor_icons.boots()}
    worn = f'{R}/assets/modulargolems/textures/equipments'
    icon = f'{R}/assets/modulargolems/textures/item/equipments'
    os.makedirs(worn, exist_ok=True); os.makedirs(icon, exist_ok=True)
    cat = 'modulargolems:arcane_armor'
    w('assets/modulargolems/patchouli_books/golem_guide/en_us/categories/arcane_armor.json', {
        'name': 'Arcane Armor', 'description': 'Violet and gold golem armour that shields against magic', 'icon': 'modulargolems:arcane_chestplate', 'flag': 'mod:ars_nouveau'})
    for i, a in enumerate(PIECES):
        k = a['key']
        gen_armor.build(a['p']).save(f'{worn}/{k}.png')
        icons[a['p']].save(f'{icon}/{k}.png')
        w(f'assets/modulargolems/models/item/{k}.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'modulargolems:item/equipments/{k}'}})
        lang[f'item.modulargolems.{k}'] = a['name']
        w(f'data/mg_arcane/recipe/armor/{k}.json', {
            'type': 'ars_nouveau:enchanting_apparatus', 'keepNbtOfReagent': False,
            'neoforge:conditions': [{'type': 'neoforge:mod_loaded', 'modid': 'ars_nouveau'}],
            'pedestalItems': [{'item': x} for x in a['ped']], 'reagent': {'item': a['reagent']},
            'result': {'count': 1, 'id': f'modulargolems:{k}'}, 'sourceCost': a['cost']})
        w(f'assets/modulargolems/patchouli_books/golem_guide/en_us/entries/arcane_armor/{k}.json', {
            'flag': 'mod:ars_nouveau', 'name': a['name'], 'icon': f'modulargolems:{k}', 'category': cat, 'sortnum': 3500 + i,
            'pages': [{'type': 'patchouli:spotlight', 'item': f'modulargolems:{k}', 'text': GUIDE % a['armor']}]})
    # registrate's .tag() only runs at datagen time, so the tags the items need at runtime are shipped here
    def ids(tag=None): return [{'id': f'modulargolems:{x["key"]}', 'required': False} for x in PIECES if tag is None or x['tag'] == tag]
    w('data/minecraft/tags/item/enchantable/armor.json', {'values': ids()})
    for t in ('head_armor', 'chest_armor', 'leg_armor', 'foot_armor'):
        w(f'data/minecraft/tags/item/enchantable/{t}.json', {'values': ids(t)})
