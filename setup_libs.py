#!/usr/bin/env python3
"""Fill libs/ for compiling.

Put these in libs/ first:
  modulargolems-3.1.43.jar   (or newer 3.x)
  l2library-3.0.8.jar
This script then pulls the nested jar-in-jar files out of them (L2Core, Registrate, L2Serial,
L2DamageTracker, mob_weapon_api ...), because those are not on any public maven.
"""
import zipfile, pathlib, shutil
libs = pathlib.Path(__file__).parent / 'libs'
libs.mkdir(exist_ok=True)
roots = [p for p in libs.glob('*.jar')]
n = 0
for j in roots:
    with zipfile.ZipFile(j) as z:
        for name in z.namelist():
            if name.startswith('META-INF/jarjar/') and name.endswith('.jar'):
                out = libs / pathlib.Path(name).name
                if not out.exists():
                    out.write_bytes(z.read(name)); n += 1
print(f'extracted {n} nested jars into {libs}')
