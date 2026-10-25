import sys, os, json, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_tex import build_all, TYPES
from mats import MATS
import gen_upgrades, gen_weapons, gen_armor_data
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'main', 'resources')
shutil.rmtree(R, ignore_errors=True)
# static metadata (mods.toml, LICENSE, NOTICE) lives in meta/ so a regeneration can never drop it
META = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'meta')
shutil.copytree(META, R)
def w(path, data):
    p = os.path.join(R, path); os.makedirs(os.path.dirname(p), exist_ok=True)
    if isinstance(data, (dict, list)): data = json.dumps(data, indent=2)
    open(p, 'w').write(data)

# stats, abilities, tiers
INFO = {  # key: (attack, health, extra stats, extra modifiers, ability id, tier)
 'source_gem': (14, 120, {'modulargolems:weight': -0.2}, {}, 'source_leech', 1),
 'fire': (18, 100, {}, {'modulargolems:fire_immune': 1}, 'ember_touch', 1),
 'water': (14, 140, {}, {}, 'tidal_chill', 1),
 'earth': (16, 200, {'modulargolems:knockback_resistance': 0.5}, {'modulargolems:explosion_resistant': 1}, 'tremor', 1),
 'air': (14, 90, {'modulargolems:weight': -0.4}, {}, 'gale_step', 1),
 'conjuration': (18, 110, {}, {}, 'spectral_fangs', 2),
 'abjuration': (12, 180, {}, {}, 'arcane_ward', 2),
 'manipulation': (16, 120, {}, {}, 'telekinesis', 2),
 'anima': (20, 150, {}, {}, 'soul_siphon', 2),
 'silt': (18, 140, {}, {}, 'sandblast', 3),
 'lava': (24, 220, {}, {'modulargolems:fire_immune': 1}, 'molten_shell', 3),
 'mire': (16, 260, {'modulargolems:knockback_resistance': 0.5}, {}, 'quagmire', 3),
 'cinder': (24, 160, {}, {'modulargolems:fire_immune': 1}, 'ash_cloud', 3),
 'vapor': (20, 140, {'modulargolems:weight': -0.2}, {}, 'scalding_steam', 3),
 'tempest': (26, 200, {'modulargolems:weight': -0.2}, {'modulargolems:thunder_immune': 1}, 'thunderstrike', 3),
 'shard': (30, 300, {'modulargolems:sweep': 1.0, 'modulargolems:weight': -0.2}, {}, 'elemental_surge', 4),
}
ABILITY_NAME = {k: v[4] for k, v in INFO.items()}
PARENTS = {'silt': ('earth', 'air'), 'lava': ('fire', 'earth'), 'mire': ('water', 'earth'),
           'cinder': ('fire', 'air'), 'vapor': ('fire', 'water'), 'tempest': ('water', 'air')}
KEYITEM = {m['key']: m['item'] for m in MATS}
REAGENT = {1: 'minecraft:iron_block', 2: 'minecraft:gold_block', 3: 'minecraft:diamond_block', 4: 'minecraft:netherite_ingot'}
PARTS = [('humanoid_golem_body', 6, 1500), ('humanoid_golem_legs', 4, 1000), ('humanoid_golem_arms', 4, 1000),
         ('metal_golem_body', 6, 1500), ('metal_golem_legs', 4, 1000), ('metal_golem_arm', 4, 800),
         ('dog_golem_body', 5, 1200), ('dog_golem_legs', 4, 1000)]
def cname(k): return f'arcane_{k}_construct'

res = build_all(None)
lang = {}
for m in MATS:
    k, ns = m['key'], m['ns']; atk, hp, ex, mods, ab, tier = INFO[k]
    mid = f'{ns}:{k}'
    stats = {'modulargolems:attack': float(atk), 'modulargolems:max_health': float(hp)}
    stats.update({a: float(b) for a, b in ex.items()})
    ing = {'item': m['item']}
    mm = {'modulargolems:' + ab: 1}; mm.update(mods)
    w(f'data/{ns}/modulargolems_config/materials/{k}.json', {
        'ingredients': {mid: ing}, 'modifiers': {mid: mm}, 'partLimitation': {},
        'repairIngredients': {mid: ing}, 'stats': {mid: stats}})
    lang[f'golem_material.{ns}.{k}'] = m['name']
    lang[f'item.modulargolems.{cname(k)}'] = f"{m['name']} Construct"
    # textures
    d, icon = res[k]
    for t in TYPES:
        tex, emi = d[t]
        base = f'assets/{ns}/textures/entity/{t}/{k}'
        os.makedirs(os.path.dirname(os.path.join(R, base)), exist_ok=True)
        tex.save(os.path.join(R, base + '.png'))
        if emi.getchannel('A').getbbox(): emi.save(os.path.join(R, base + '_emissive.png'))
    os.makedirs(f'{R}/assets/modulargolems/textures/item', exist_ok=True)
    icon.save(f'{R}/assets/modulargolems/textures/item/{cname(k)}.png')
    w(f'assets/modulargolems/models/item/{cname(k)}.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'modulargolems:item/{cname(k)}'}})
    # construct recipe (apparatus): 6 own + 2 supporting
    own = [{'item': m['item']}] * 6
    if k in PARENTS: sup = [{'item': KEYITEM[p]} for p in PARENTS[k]]
    elif k == 'shard': own = [{'item': m['item']}] * 4; sup = [{'item': KEYITEM[p]} for p in ('fire', 'water', 'earth', 'air')]
    elif k == 'anima': sup = [{'item': KEYITEM['source_gem']}] * 2
    else: sup = [{'item': 'minecraft:gold_ingot'}] * 2
    cond = [] if ns == 'ars_nouveau' else [{'type': 'neoforge:mod_loaded', 'modid': ns}]
    cw = {'neoforge:conditions': cond} if cond else {}
    w(f'data/mg_arcane/recipe/construct/{k}.json', {**cw,
        'type': 'ars_nouveau:enchanting_apparatus', 'keepNbtOfReagent': False,
        'pedestalItems': own + sup, 'reagent': {'item': REAGENT[tier]},
        'result': {'count': 3, 'id': f'modulargolems:{cname(k)}'}, 'sourceCost': 500 * (tier + 1)})
    # part recipes
    for part, n, cost in PARTS:
        w(f'data/mg_arcane/recipe/part/{k}_{part}.json', {**cw,
            'type': 'ars_nouveau:enchanting_apparatus', 'keepNbtOfReagent': False,
            'pedestalItems': [{'item': f'modulargolems:{cname(k)}'}] * n,
            'reagent': {'item': f'modulargolems:{part}'},
            'result': {'count': 1, 'id': f'modulargolems:{part}', 'components': {'modulargolems:part_material': mid}},
            'sourceCost': int(cost * (0.6 + 0.4 * tier))})

# Modular Golem Guide (Patchouli) pages: one material entry per material, shown only when the material's mod is loaded
GUIDE = {  # key: what the ability does, in the player's words
 'source_gem': 'Source Leech: the golem heals for a share of the damage it deals. Light parts, so it is quick on its feet.',
 'fire': 'Ember Touch: hits set the target on fire. The golem is immune to fire.',
 'water': 'Tidal Chill: hits slow the target.',
 'earth': 'Tremor: hits splash damage to nearby enemies and knock them back. Very tough, resists knockback and explosions.',
 'air': 'Gale Step: the golem takes no fall damage and its hits knock targets upward. Very light.',
 'conjuration': 'Spectral Fangs: hits summon spectral fangs under the target, on a cooldown.',
 'abjuration': 'Arcane Ward: takes less magic damage and slowly regrows an absorption shield.',
 'manipulation': 'Telekinesis: hits drag the target toward the golem.',
 'anima': 'Soul Siphon: killing a target restores some of the golem\'s health.',
 'silt': 'Sandblast: hits blind the target.',
 'lava': 'Molten Shell: melee attackers are set on fire. The golem is immune to fire.',
 'mire': 'Quagmire: nearby enemies are slowed while the golem fights. Very tough, resists knockback.',
 'cinder': 'Ash Cloud: nearby enemies are weakened while the golem fights. The golem is immune to fire.',
 'vapor': 'Scalding Steam: hits deal bonus damage. Light parts.',
 'tempest': 'Thunderstrike: hits can call down lightning on the target and nearby enemies, on a cooldown. The golem is immune to lightning.',
 'shard': 'Elemental Surge: hits deal bonus damage and cycle through burning, chilling, weakening and launching the target. The strongest of the Ars materials.',
}
def holder(item, parts, mat):
    ps = ','.join('{part:"modulargolems:%s",material:"%s"}' % (p, mat) for p in parts)
    return f'modulargolems:{item}[modulargolems:golem_materials={{parts:[{ps}]}}]'
JEI = 'Use JEI (press R) to check part stats of each part made of this material.'
for i, m in enumerate(MATS):
    k, ns = m['key'], m['ns']; mid = f'{ns}:{k}'; tier = INFO[k][5]
    pre = ('Main material to craft %s golem parts. ' % m['name'])
    post = '$(br2)Craft the construct at an Enchanting Apparatus, then use constructs on the apparatus to make the golem parts.'
    if k in PARENTS: post = '$(br2)Needs the %s and %s essences to craft the construct, then parts are made at an Enchanting Apparatus.' % tuple(p.capitalize() for p in PARENTS[k]) + ' Its circlet carries a gem for each element.'
    elif k == 'shard': post = '$(br2)Needs the four elemental essences to craft the construct, then parts are made at an Enchanting Apparatus. Its circlet carries all four gems.'
    elif k == 'anima': post = '$(br2)Needs Source Gems to craft the construct, then parts are made at an Enchanting Apparatus.'
    pages = [
      {'type': 'patchouli:spotlight', 'item': f'modulargolems:{cname(k)}', 'text': pre + GUIDE[k] + post},
      {'type': 'patchouli:spotlight', 'item': holder('metal_golem_holder', ['metal_golem_arm', 'metal_golem_body', 'metal_golem_arm', 'metal_golem_legs'], mid), 'text': JEI},
      {'type': 'patchouli:spotlight', 'item': holder('humanoid_golem_holder', ['humanoid_golem_body', 'humanoid_golem_arms', 'humanoid_golem_legs'], mid), 'text': JEI},
      {'type': 'patchouli:spotlight', 'item': holder('dog_golem_holder', ['dog_golem_body', 'dog_golem_legs'], mid), 'text': JEI}]
    w(f'assets/modulargolems/patchouli_books/golem_guide/en_us/entries/materials/arcane_{k}.json', {
        'flag': f'mod:{ns}', 'name': m['name'], 'icon': f'modulargolems:{cname(k)}',
        'category': 'modulargolems:materials', 'sortnum': 2000 + i, 'pages': pages})

# the anvil lets any "part + material ingredient" make a material part; this tag opts our items out so parts need the apparatus
w('data/modulargolems/tags/item/special_crafting_material.json',
  {'values': [{'id': m['item'], 'required': False} for m in MATS]})
# modifier lang
DESC = {  # id: (name, desc)
 'source_leech': ('Source Leech', 'Heal %s of the damage dealt'),
 'ember_touch': ('Ember Touch', 'Set attack targets on fire for %s seconds'),
 'tidal_chill': ('Tidal Chill', 'Slow attack targets for %s seconds (Slowness %s)'),
 'tremor': ('Tremor', 'Hits splash %s of their damage to nearby enemies within %s blocks and knock them back'),
 'gale_step': ('Gale Step', 'Immune to fall damage. Hits knock targets upward'),
 'spectral_fangs': ('Spectral Fangs', 'Hits summon %s spectral fang(s) under the target, once every %s seconds'),
 'arcane_ward': ('Arcane Ward', 'Take %s less magic damage and slowly regrow up to %s absorption'),
 'telekinesis': ('Telekinesis', 'Hits drag the target toward the golem'),
 'soul_siphon': ('Soul Siphon', 'Killing a target heals %s of max health'),
 'sandblast': ('Sandblast', 'Blind attack targets for %s seconds'),
 'quagmire': ('Quagmire', 'Enemies within %s blocks are slowed (Slowness %s) while the golem fights'),
 'molten_shell': ('Molten Shell', 'Melee attackers are set on fire for %s seconds'),
 'ash_cloud': ('Ash Cloud', 'Enemies within %s blocks are weakened while the golem fights'),
 'scalding_steam': ('Scalding Steam', 'Hits deal %s extra damage'),
 'thunderstrike': ('Thunderstrike', 'Hits have a %s chance to call lightning for %s damage (cooldown %s seconds)'),
 'elemental_surge': ('Elemental Surge', 'Hits deal %s extra damage and cycle burn, chill, weaken and launch'),
}
DESC.update({  # upgrade modifier descriptions (the %s values are filled in by the code)
 'arcane_recall': ('Arcane Recall', 'Teleports back to its owner when idle and %s or more blocks away (cooldown %s seconds)'),
 'spell_sponge': ('Spell Sponge', 'Takes half damage from magic and heals %s health per magic hit'),
 'magelight_core': ('Magelight Core', 'Its owner gets Night Vision within %s blocks'),
 'source_surge': ('Source Surge', 'When its owner is hit by a mob, gains Speed and Strength for %s seconds (cooldown %s seconds)'),
 'glyph_strike': ('Glyph Strike', '%s chance per hit to lay Hex, Shocked or Snared on the target'),
 'source_mantle': ('Source Mantle', 'Take %s less magic damage and regain %s health every %s seconds'),
})
gen_upgrades.build(w, R, lang, DESC)
gen_weapons.build(w, R, lang)
gen_armor_data.build(w, R, lang)
for i, (n, d) in DESC.items():
    lang[f'modifier.modulargolems.{i}'] = n; lang[f'modifier.modulargolems.{i}.desc'] = d
w('assets/modulargolems/lang/en_us.json', dict(sorted(lang.items())))
w('pack.mcmeta', {'pack': {'description': 'Modular Golems - Ars Integration', 'pack_format': 48}})
print('files', sum(len(f) for _, _, f in os.walk(R)))
