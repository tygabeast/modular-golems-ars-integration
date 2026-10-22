# material definitions shared by the generators: id, display name, source item, ramp (dark->light), accent (glow), style, emblem
H = lambda s: tuple(int(s[i:i+2], 16) for i in (1, 3, 5))
def R(*cs): return [H(c) for c in cs]


MATS = [
 # key, ns, name, item, ramp (dark->light), accent (glow/slots), style, emblem, extras:
 #   trim: gold rune trim like the Ars armour sets; patch: (colour, density) secondary colour patches; bias: shifts brightness; crackglow
 dict(key="source_gem", ns="ars_nouveau", name="Source Gem", item="ars_nouveau:source_gem",
      ramp=R("#240c33","#5a1d78","#8e3fb8","#c377e0","#f0c8ff"), accent=H("#e87af0"), style="runes", emblem="gem"),
 dict(key="fire", ns="ars_nouveau", name="Fire", item="ars_nouveau:fire_essence",
      ramp=R("#1a0606","#4a0e10","#a01a14","#dc3a22","#ff8c48"), accent=H("#ff6a28"), style="crack", emblem="flame", trim=True, crackglow=True, glowcuff=True),
 dict(key="water", ns="ars_nouveau", name="Water", item="ars_nouveau:water_essence",
      ramp=R("#0c2636","#12506a","#2a8aa8","#7cc8e0","#e4f6ff"), accent=H("#8fe8ff"), style="wave", emblem="drop", trim=True),
 dict(key="earth", ns="ars_nouveau", name="Earth", item="ars_nouveau:earth_essence",
      ramp=R("#0e2210","#1c4a1c","#307428","#6aa04a","#bfe0a8"), accent=H("#d8b03a"), style="stone", emblem="peak", trim=True, sparse=True, patch=(H("#9a7428"), 0.22)),
 dict(key="air", ns="ars_nouveau", name="Air", item="ars_nouveau:air_essence",
      ramp=R("#585c68","#8c909c","#bcc0c8","#e2e4ea","#ffffff"), accent=H("#9fd8ff"), style="cloud", emblem="swirl", trim=True),
 dict(key="conjuration", ns="ars_nouveau", name="Conjuration", item="ars_nouveau:conjuration_essence",
      ramp=R("#08224a","#10508a","#1a82b8","#3cc0d6","#cffff0"), accent=H("#58dcdc"), style="runes", emblem="star", trim=True),
 dict(key="abjuration", ns="ars_nouveau", name="Abjuration", item="ars_nouveau:abjuration_essence",
      ramp=R("#3a0a66","#6e12a8","#a822b8","#e43ccc","#ffd8ee"), accent=H("#f070dc"), style="plain", emblem="shield", trim=True),
 dict(key="manipulation", ns="ars_nouveau", name="Manipulation", item="ars_nouveau:manipulation_essence",
      ramp=R("#3a1406","#8a3c0a","#d26c12","#f4a436","#fff0c8"), accent=H("#ffb830"), style="swirl", emblem="eye", trim=True),
 dict(key="anima", ns="ars_elemental", name="Anima", item="ars_elemental:anima_essence",
      ramp=R("#1b1d22","#3c4048","#6f7682","#b4bcc8","#f6f8ff"), accent=H("#8ce8c8"), style="cloud", emblem="wisp", trim=True),
 dict(key="silt", elems=['earth', 'air'], ns="ars_elemancy", name="Silt", item="ars_elemancy:silt_essence",
      ramp=R("#5a4228","#9a7e50","#d4be94","#f2e6cc","#fffaf0"), accent=H("#f0d890"), style="stone", emblem="dune", trim=True, bias=0.12),
 dict(key="lava", elems=['fire', 'earth'], ns="ars_elemancy", name="Lava", item="ars_elemancy:lava_essence",
      ramp=R("#1c0e08","#54240c","#b84c0a","#ec8a1c","#ffd24a"), accent=H("#ffc83c"), style="flame", emblem="magma", trim=True, patch=(H("#2a1608"), 0.18), glowcuff=True),
 dict(key="mire", elems=['water', 'earth'], ns="ars_elemancy", name="Mire", item="ars_elemancy:mire_essence",
      ramp=R("#060a06","#10201a","#1a3c26","#2e5a36","#5c6a3c"), accent=H("#d4c898"), style="stone", emblem="bubble", trim=True, sparse=True, patch=(H("#4a3620"), 0.14)),
 dict(key="cinder", elems=['fire', 'air'], ns="ars_elemancy", name="Cinder", item="ars_elemancy:cinder_essence",
      ramp=R("#0a0606","#1c0e0e","#381414","#6a2012","#b84418"), accent=H("#ff6a1c"), style="crack", emblem="spark", trim=True, crackglow=True, glowcuff=True),
 dict(key="vapor", elems=['fire', 'water'], ns="ars_elemancy", name="Vapor", item="ars_elemancy:vapor_essence",
      ramp=R("#6a7690","#9aa8c0","#c4d0e2","#e6edf6","#ffffff"), accent=H("#b0e4ff"), style="cloud", emblem="cloud", trim=True, bias=0.1),
 dict(key="tempest", elems=['water', 'air'], ns="ars_elemancy", name="Tempest", item="ars_elemancy:tempest_essence",
      ramp=R("#0e0e12","#3a3c44","#7c7e88","#b8bac4","#eeeef2"), accent=H("#ffe050"), style="cloud", emblem="bolt", trim=True),
 dict(key="shard", elems=['fire', 'water', 'earth', 'air'], ns="ars_elemancy", name="Elemancer Shard", item="ars_elemancy:elemancer_essence",
      ramp=R("#4a4a54","#9c9ca6","#e4e4ea","#f4f4f8","#ffffff"), accent=H("#fff0b8"), style="plain", emblem="prism", trim=True,
      zones=dict(panel=H("#9a1a18"), cuff=H("#1a3a78"), boot=H("#1a5a1a"), head=H("#7aa0d8"), gem=H("#f0e060")),
      quad=[H("#e8501a"), H("#2a78d8"), H("#3aa83a"), H("#f0e060")]),
]
