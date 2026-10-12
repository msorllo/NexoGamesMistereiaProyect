"""NOVA SURGE (app 31): script maestro. Construye los 3 grupos de assets (nova_a, nova_b, nova_c), exporta el GLB,
guarda el .blend y renderiza el icono.
Ejes Blender: Z arriba. En Three.js: x=x, y=z, z=-y. Naves con el morro hacia +Y de Blender (= arriba de la pantalla en el juego).
Materiales: SIEMPRE M('Nombre') de nova_mats.py (tabla única).

Uso (desde cualquier carpeta):
  blender -b -P blender/scripts/b_nova.py                              -> todo: glb/nova.glb + blend/nova.blend + renders/nova.png
  blender -b -P blender/scripts/b_nova.py -- --only a                  -> solo el grupo A, exporta a un GLB temporal y lista triángulos
  blender -b -P blender/scripts/b_nova.py -- --only b --preview x.png  -> además renderiza una hoja de contacto (vista del juego)
  blender -b -P blender/scripts/b_nova.py -- --noicon                  -> todo menos el icono
Cada grupo es un módulo nova_<g>.py con una función build() que crea sus objetos (uno por asset, nombre exacto) y devuelve la lista de nombres.
"""
import sys, os, math, tempfile, importlib
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
import bpy
from mathutils import Vector
from blib import *

ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
def arg(name, default=None):
    return ARGS[ARGS.index(name) + 1] if name in ARGS and ARGS.index(name) + 1 < len(ARGS) else default
ONLY = arg('--only')
GROUPS = [ONLY] if ONLY else ['a', 'b', 'c']

reset()
names = []
for g in GROUPS:
    mod = importlib.import_module('nova_' + g)
    got = mod.build()
    missing = [n for n in got if n not in bpy.data.objects]
    if missing: raise SystemExit(f'nova_{g}.build() devolvió nombres que no existen: {missing}')
    names += got
dups = {n for n in names if names.count(n) > 1}
if dups: raise SystemExit(f'Nombres repetidos: {dups}')

# informe de triángulos
tot = 0
for n in names:
    o = bpy.data.objects[n]
    tris = sum(len(p.vertices) - 2 for p in o.data.polygons) if o.type == 'MESH' else 0
    tot += tris; print(f'  {n:<22} {tris:>6} tris  dims={tuple(round(d, 2) for d in o.dimensions)}')
print(f'TOTAL {len(names)} objetos · {tot} triángulos')

glb = ROOT + '/glb/nova.glb' if not ONLY else os.path.join(tempfile.gettempdir(), f'nova_{ONLY}_test.glb')
bpy.ops.object.select_all(action='DESELECT')
for n in names: bpy.data.objects[n].select_set(True)
bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True, export_apply=True,
                          export_yup=True, export_materials='EXPORT', export_texcoords=False)
print('GLB', glb, round(os.path.getsize(glb) / 1024), 'KB')

def contact_sheet(path, objs):
    """Coloca los objetos en rejilla y renderiza con una cámara parecida a la del juego (desde arriba, inclinada ~35º)."""
    objs = sorted(objs, key=lambda o: -max(o.dimensions))
    cols = max(1, math.ceil(math.sqrt(len(objs) * 1.4))); x = y = rowh = 0; maxw = 0
    for i, o in enumerate(objs):
        w = max(o.dimensions.x, 1.0) + 1.2; h = max(o.dimensions.y, 1.0) + 1.2
        if i and i % cols == 0: x = 0; y -= rowh; rowh = 0
        o.location = (x + w / 2, y - h / 2, 0); x += w; rowh = max(rowh, h); maxw = max(maxw, x)
    cx, cy = maxw / 2, (y - rowh) / 2; span = max(maxw, -(y - rowh))
    render_icon(path, '#0b0f08', (cx, cy - span * .55, span * .95), (cx, cy, 0), lens=36, size=1024, samples=24,
                lights=[('SUN', (cx + 4, cy - 6, 12), 3.2, '#f4f6ee'), ('AREA', (cx - span * .6, cy - span * .4, span * .5), 900, '#c8ff1f'),
                        ('AREA', (cx + span * .6, cy + span * .3, span * .4), 700, '#8fd6ff')])

prev = arg('--preview')
if ONLY:
    if prev: contact_sheet(prev, [bpy.data.objects[n] for n in names]); print('PREVIEW', prev)
    print('OK nova grupo', ONLY); raise SystemExit(0)

bpy.ops.wm.save_as_mainfile(filepath=ROOT + '/blend/nova.blend')
if prev: contact_sheet(prev, [bpy.data.objects[n] for n in names])

# ---------------- icono ----------------
if '--noicon' not in ARGS and not prev:
    for n in names: bpy.data.objects[n].hide_render = True
    ship = showcase(['Nave'], [(0, -.2, 0)], [(math.radians(-18), math.radians(-14), math.radians(8))], [1.55])[0]
    if 'Trituradora' in bpy.data.objects:
        showcase(['Trituradora'], [(0, 7.5, -3.2)], [(math.radians(8), 0, math.radians(180))], [.8])
    from nova_mats import M
    for sx, sy in [(-.28, 1.6), (.28, 1.6), (-.28, 2.7), (.28, 2.7), (-.28, 3.8), (.28, 3.8)]:
        prim('cyl', loc=(sx, sy, .05), rot=(math.pi / 2, 0, 0), scale=(.07, .07, .32), m=M('Motor'), vertices=10)
    render_icon(ROOT + '/renders/nova.png', '#0b0f08', (0, -4.6, 4.2), (0, .9, 0), lens=44, samples=64,
                lights=[('SUN', (3, -4, 9), 2.6, '#f4f6ee'), ('AREA', (-3.5, -2, 2.5), 700, '#c8ff1f'), ('AREA', (3.5, 3, 3), 600, '#ff2e4d')])
print('OK nova')
