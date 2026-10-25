# Modular Golems - Ars Integration (source)

Code addon for **Modular Golems 3.1.43** on **NeoForge 21.1.x / Minecraft 1.21.1**, adding golem materials for
**Ars Nouveau**, **Ars Elemental** and **Ars Elemancy** (only Ars Nouveau is required; Ars Elemental and Ars Elemancy are optional - Anima, the six combination essences and the Elemancer Shard only appear when their mod is installed).

## Materials and abilities
| Material (item) | Ability | Material (item) | Ability |
|---|---|---|---|
| Source Gem | Source Leech | Silt essence | Sandblast |
| Fire essence | Ember Touch | Lava essence | Molten Shell (+ fire immune) |
| Water essence | Tidal Chill | Mire essence | Quagmire |
| Earth essence | Tremor (+ explosion resistant) | Cinder essence | Ash Cloud (+ fire immune) |
| Air essence | Gale Step | Vapor essence | Scalding Steam |
| Conjuration essence | Spectral Fangs | Tempest essence | Thunderstrike (+ thunder immune) |
| Abjuration essence | Arcane Ward | Elemancer Shard | Elemental Surge |
| Manipulation essence | Telekinesis | Anima essence | Soul Siphon |

Each material has golem textures for the metal, humanoid and dog golems (with emissive layers where used), stats, and a
**construct** item (`modulargolems:arcane_<material>_construct`).

## Crafting (Enchanting Apparatus only)
1. **Construct** (makes 3): reagent block/ingot by tier (iron block, gold block, diamond block, netherite ingot) with
   6 of the essence plus 2 supporting items on pedestals (combination essences use their two parent essences, the
   shard uses 4 shards plus Fire/Water/Earth/Air essence).
2. **Golem part**: reagent = the plain part (e.g. `modulargolems:metal_golem_body`), pedestals = 4-6 constructs of that
   material. The result carries the material, so it works exactly like Alex's Caves / Cataclysm parts.
All 8 part types per material (humanoid body/legs/arms, metal body/legs/arm, dog body/legs) have a recipe.
3. The Ars items are added to Modular Golems' `modulargolems:special_crafting_material` tag, which switches off the anvil shortcut
   (blank part + material item), so parts can only be made at the apparatus. Repairing a golem with its material still works.

## Upgrades
Five upgrade items (Modular Golems' upgrades tab), each crafted at the Enchanting Apparatus and applied like any other golem upgrade:
| Upgrade | Effect |
|---|---|
| Arcane Recall | An idle golem that strays too far from its owner teleports back (cooldown) |
| Spell Sponge | Magic damage (including Ars spells) is halved and each magic hit heals the golem |
| Magelight Core | The owner gets Night Vision while near the golem |
| Source Surge | When a mob hits the owner, the golem gains Speed and Strength for a few seconds (cooldown) |
| Glyph Strike | Hits sometimes apply Hex, Shocked or Snared (Ars effects looked up by id; Slowness if missing) |
Each has a Guide entry under Upgrades. Their numbers are in the `[upgrades]` section of the config.

## Arcane weapons
Golem weapons that cast an Ars Nouveau spell on hit, set up the same way as the Enchanter's Sword:
place the weapon on a Scribe's Table, make a spell in your spell book, then shift-right click the table with that spell active.
| Item | Notes |
|---|---|
| Arcane Golem Sword, Axe, Spear | Cast on every hit (cooldown). The spell must have no Form glyph: the weapon supplies Touch. |
| Arcane Mecha Bow | Works like the Enchanter's Bow: the table adds a Projectile glyph (so the spell still may not have a Form glyph) and the golem fires spell arrows that resolve the spell where they land. No arrows needed. Un-scribed, it is a normal mecha bow that uses arrows. |
| Arcane Shoulder Wand | Based on the Enchanter's Wand, for a Metal Golem's shoulder slot. The table adds Projectile and Accelerate (so the spell may not have a Form glyph) and the golem fires the spell at its target, on its own cooldown and range. Reuses the Beacon Cannon's shoulder model, aim and swing-up animation, painted as a wand. |
Like Ars' own gear, a scribed weapon shows its spell as glyph icons in the tooltip (names while Shift is held, or always if Ars' `glyphTooltips` setting is off).
Each is crafted at an Enchanting Apparatus from the matching diamond golem weapon (the bow from the iron mecha bow, the wand from an Enchanter's Wand) and has a Guide entry under Arcane Weapons.
Ars Nouveau charges no mana to non-player casters, so the limits are `weaponCooldown` (ticks between casts per golem) and the optional `weaponMaxCost` (refuse spells above this mana cost) in the `[weapons]` config section.
The casting code uses Ars' `EntitySpellResolver` and `ICasterTool` (compile against Ars Nouveau 1.21.1-5.13.3: put its jar in `libs/` too).

## Arcane armour
A set for Metal Golems in violet cloth and gold: Arcane Cowl, Tunic, Sash and Boots (armour 11 / 14 / 8 / 6, toughness 6, the same tier as Modular Golems' diamond-grade sets).
The shapes are custom and deliberately restrained, with about the coverage of Wind Spirit: head and torso covered, short sleeves with forearm cuffs, a hip sash and low boots.
Each piece worn adds one level of **Source Mantle**: 4% less magic damage and 1 health regained every 5 seconds per piece (full set: 16% and about 0.8 health per second).
Crafted at an Enchanting Apparatus from the matching vanilla diamond armour piece, 4 Source Gems, 2 Abjuration Essence and 2 Magebloom Fiber (the same for every piece), and has a Guide entry under Arcane Armor.
The shapes and textures come from one description (`tools/armor_spec.py`): `tools/gen_armor.py` paints the textures and `tools/gen_armor_java.py` writes `ArmorLayers.java` (client only).

## Config (`config/mg_arcane-common.toml`)
* `targets` - who area abilities (Tremor, Quagmire, Ash Cloud) may affect besides the golem's own target:
  `HOSTILE` (default), `ALL_MOBS`, `ALL_MOBS_AND_PLAYERS`. The owner, the owner's pets and the owner's golems are never affected.
* `[weapons]`: `weaponCooldown`, `weaponMaxCost`, `shoulderCooldown`, `shoulderRange`.
* `[armor]`: `mantleReduction`, `mantleHeal`, `mantleInterval` (Source Mantle, per piece worn).
* `[upgrades]`: `recallDistance`, `recallCooldown`, `spongeHeal`, `lightRadius`, `surgeDuration`, `surgeCooldown`, `glyphChance`.
* `auraInterval`, `splashFraction`, `fangCooldown`, `lightningCooldown`, `lightningChance`, `lightningDamage`.
  Thunderstrike's bolt is visual only (no fire, never hurts the owner or pets); damage goes to the target and enemies within 2.5 blocks.

## Guide, textures and icon
* One Modular Golem Guide (Patchouli) entry per material, shown only when that material's mod is installed.
* Humanoid golem heads carry a gold circlet with a glowing gem; combination materials show one gem per element
  (Lava: Fire + Earth, Silt: Earth + Air, Mire: Water + Earth, Cinder: Fire + Air, Vapor: Fire + Water, Tempest: Water + Air,
  Elemancer Shard: all four).
* `meta/logo.png` is the mod icon: the Fire, Water, Earth and Air metal golem heads rendered from the generated textures
  (`tools/gen_icon.py`).

## Performance
Auras scan only while the golem has a target, once per `auraInterval` ticks and staggered by entity id; on-hit effects do no scanning;
Tremor's splash is guarded against re-entry; nothing runs on the client.

## Build
1. Put in `libs/`: `modulargolems-3.1.43.jar`, `l2library-3.0.8.jar`.
2. `python3 setup_libs.py`  (extracts L2Core, Registrate, L2Serial, L2DamageTracker, mob_weapon_api from the jar-in-jar folders)
3. `gradle build`  (JDK 21, Gradle 8.8+). Output: `build/libs/mg_arcane-<version>.jar` (version is set in `build.gradle` and `meta/META-INF/neoforge.mods.toml`)

The addon does not reference any Ars classes (items are referenced by id), so Ars jars are not needed to compile.

## Licence
MIT, copyright Tygabeast (see `LICENSE` and `NOTICE.md`). All textures are generated by the scripts in `tools/`; no third-party texture files are used.

## Generated resources
Everything under `src/main/resources/` except `META-INF`, `LICENSE`, `NOTICE.md` and `logo.png` is generated by `tools/` and committed
so the mod builds without Python. To regenerate: `python3 tools/gen_data.py` (needs Python with Pillow and NumPy; no input files).
Static files live in `meta/`; edit them there, because the generator copies `meta/` over the resources folder.
`tools/previews.py` and `tools/render.py` only make preview images.

## Status
Compiles against NeoForge 21.1.256 and Modular Golems 3.1.43 and has been playtested by the author.
The Spectral Fangs ability has not been confirmed against the owner in-game.
The repository has no Gradle wrapper: add one from the NeoForge MDK (`gradle wrapper`) if you want `./gradlew`.
