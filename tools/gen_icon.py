"""Mod icon: the four elemental metal golem heads rendered from the generated textures, one per corner, turned inward.
Original artwork (MIT)."""
import os
from PIL import Image
from geom import IRON
from render import render
from gen_tex import build_all
from mats import MATS

def build(size=512):
    res = build_all(None)
    head = (IRON[0], IRON[1], [IRON[2][0]])          # head part only
    cell = size // 2
    out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    for key, (cx, cy), yaw in (('fire', (0, 0), -35), ('water', (1, 0), 35), ('earth', (0, 1), -35), ('air', (1, 1), 35)):
        tex, emi = res[key][0]['metal_golem']
        a = render(head, tex, size=cell, yaw=yaw, pitch=8, scale=cell / 14.5)
        e = render(head, emi, size=cell, yaw=yaw, pitch=8, scale=cell / 14.5, flat=True)
        a.alpha_composite(e)
        out.alpha_composite(a, (cx * cell, cy * cell))
    return out

if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'meta', 'logo.png')
    build().save(out); print('saved', out)
