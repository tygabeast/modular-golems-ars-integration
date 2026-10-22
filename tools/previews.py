import sys, os
from PIL import Image, ImageDraw, ImageFont
from geom import IRON, PLAYER, WOLF
from render import render
from gen_tex import build_all, TYPES
from mats import MATS
OUT = 'prev'
res = build_all(None)
MODELS = {'metal_golem': IRON, 'humanoid_golem': PLAYER, 'dog_golem': WOLF}
try: F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15); FS = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 11)
except Exception: F = FS = ImageFont.load_default()
BG = (44, 46, 56, 255)

# 1) constructs
sh = Image.new('RGBA', (8 * 150, 2 * 170 + 10), BG); d = ImageDraw.Draw(sh)
for i, m in enumerate(MATS):
    ic = res[m['key']][1].resize((128, 128), Image.NEAREST)
    x, y = (i % 8) * 150 + 11, (i // 8) * 170 + 8
    sh.paste(ic, (x, y), ic); d.text((x, y + 134), m['name'], font=FS, fill=(230, 230, 240))
sh.save(f'{OUT}/mg_arcane_constructs.png')

# 2) golem renders, 8 materials per image
CELL = 210
for part in (0, 1):
    ms = MATS[part * 8:(part + 1) * 8]
    img = Image.new('RGBA', (150 + 3 * CELL + 90, len(ms) * CELL), BG); d = ImageDraw.Draw(img)
    for r, m in enumerate(ms):
        y = r * CELL
        d.text((10, y + CELL // 2 - 8), m['name'], font=F, fill=(240, 240, 250))
        for c, t in enumerate(TYPES):
            tex, emi = res[m['key']][0][t]
            a = render(MODELS[t], tex, size=CELL, yaw=-35, pitch=15)
            e = render(MODELS[t], emi, size=CELL, yaw=-35, pitch=15, flat=True)
            a.alpha_composite(e)
            img.paste(a, (150 + c * CELL, y), a)
        ic = res[m['key']][1].resize((64, 64), Image.NEAREST)
        img.paste(ic, (150 + 3 * CELL + 10, y + CELL // 2 - 32), ic)
    img.save(f'{OUT}/mg_arcane_golems_{part + 1}.png')

# 3) raw metal golem textures
raw = Image.new('RGBA', (4 * 266, 4 * 266), BG); d = ImageDraw.Draw(raw)
for i, m in enumerate(MATS):
    tex = res[m['key']][0]['metal_golem'][0].resize((256, 256), Image.NEAREST)
    x, y = (i % 4) * 266, (i // 4) * 266
    raw.paste(tex, (x, y), tex); d.text((x + 4, y + 240), m['name'], font=FS, fill=(255, 255, 255))
raw.save(f'{OUT}/mg_arcane_metal_textures.png')
print('done')
