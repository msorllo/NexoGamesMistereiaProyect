import sys, os, math, random; HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE); sys.path.insert(0, HERE)
from blib import *
reset(); random.seed(7)
BALL = mat('Bola', '#fbfbff', .35); POLE = mat('Mástil', '#e9ecff', .3, .8); FLAG = mat('Bandera', '#ff3fa4', .6, emit='#ff3fa4', emit_str=.6)
AST = mat('Asteroide', '#6b5a7a', .95); AST2 = mat('Cráter', '#453a55', .95); CUP = mat('Hoyo', '#0a0616', .9)
NEON = mat('Neón cian', '#39f3ff', .2, 0, emit='#39f3ff', emit_str=5); NEON2 = mat('Neón rosa', '#ff4fd8', .2, 0, emit='#ff4fd8', emit_str=5)
PLAN = mat('Planeta', '#ffb23f', .7); RING = mat('Anillo', '#ffe6b0', .5); UFO = mat('Ovni', '#b9c3d6', .25, .9); DOME = mat('Cúpula', '#8ef2ff', .1, 0, emit='#8ef2ff', emit_str=1.5, alpha=.6)
TEE = mat('Tee', '#2bd49a', .6); GREEN = mat('Césped lunar', '#3d2d74', .85)

# Bola
b = prim('ico', subdivisions=3, radius=.12, loc=(0, 0, .12), m=BALL); b.data.polygons.foreach_set('use_smooth', [True] * len(b.data.polygons)); join([b], 'Bola', (0, 0, .12))

# Bandera + hoyo
f = [prim('cyl', loc=(0, 0, .7), vertices=10, radius=.025, depth=1.4, m=POLE, smooth=True),
     prim('sphere', loc=(0, 0, 1.42), segments=12, ring_count=8, radius=.05, m=NEON, smooth=True)]
import bmesh as _bm
me = bpy.data.meshes.new('flag'); bm = _bm.new()
vs = [bm.verts.new(p) for p in [(0, 0, 1.35), (.55, 0, 1.2), (0, 0, 1.02)]]; bm.faces.new(vs); bm.to_mesh(me); bm.free()
fo = bpy.data.objects.new('flag', me); C.collection.objects.link(fo); me.materials.append(FLAG)
fo.modifiers.new('s', 'SOLIDIFY').thickness = .02; C.view_layer.objects.active = fo; bpy.ops.object.modifier_apply(modifier='s'); f.append(fo)
join(f, 'Bandera')
h = [prim('cyl', loc=(0, 0, .005), vertices=32, radius=.2, depth=.01, m=CUP), prim('torus', loc=(0, 0, .012), major_radius=.21, minor_radius=.02, major_segments=32, minor_segments=6, m=NEON2)]
join(h, 'Hoyo')

# Asteroides (3 variantes)
for i, (r, sc) in enumerate([(.5, (1, .8, .7)), (.8, (1.2, 1, .8)), (.35, (1, 1, 1))]):
    a = prim('ico', subdivisions=3, radius=r, scale=sc, m=AST); displace(a, r * .35, .5, i + 3)
    for k in range(3):
        c = prim('sphere', loc=(random.uniform(-r, r) * .5, -r * .8, random.uniform(-r, r) * .4), segments=10, ring_count=6, radius=r * .22, scale=(1, .35, 1), m=AST2)
        a = join([a, c], 'tmp')
    join([a], 'Asteroide%d' % (i + 1))

# Bumper (seta de neón)
bu = [prim('cyl', loc=(0, 0, .12), vertices=24, radius=.22, depth=.24, m=UFO, smooth=True), prim('torus', loc=(0, 0, .22), major_radius=.22, minor_radius=.035, major_segments=32, minor_segments=8, m=NEON, smooth=True),
      prim('sphere', loc=(0, 0, .26), segments=16, ring_count=8, radius=.14, scale=(1, 1, .5), m=NEON2, smooth=True)]
join(bu, 'Bumper')

# Portal
po = [prim('torus', loc=(0, 0, .5), rot=(math.pi / 2, 0, 0), major_radius=.45, minor_radius=.06, major_segments=40, minor_segments=10, m=NEON, smooth=True),
      prim('cyl', loc=(0, 0, .5), rot=(math.pi / 2, 0, 0), vertices=32, radius=.42, depth=.01, m=mat('Vórtice', '#7a2cff', .2, 0, emit='#a45cff', emit_str=3, alpha=.7))]
join(po, 'Portal')

# Planeta con anillo
pl = [prim('sphere', segments=32, ring_count=16, radius=1, m=PLAN, smooth=True), prim('torus', rot=(.35, 0, 0), major_radius=1.6, minor_radius=.12, major_segments=64, minor_segments=4, scale=(1, 1, .15), m=RING, smooth=True)]
join(pl, 'Planeta')

# Ovni
u = [prim('sphere', segments=32, ring_count=12, radius=.6, scale=(1, 1, .28), m=UFO, smooth=True), prim('sphere', loc=(0, 0, .14), segments=24, ring_count=12, radius=.3, m=DOME, smooth=True)]
for k in range(8):
    a = k / 8 * math.tau; u.append(prim('sphere', loc=(.55 * math.cos(a), .55 * math.sin(a), -.02), segments=8, ring_count=6, radius=.05, m=NEON2 if k % 2 else NEON))
join(u, 'Ovni')

# Tee
join([bevel(prim('cyl', loc=(0, 0, .03), vertices=6, radius=.35, depth=.06, m=TEE), .02)], 'Tee')

ASSETS = ['Bola', 'Bandera', 'Hoyo', 'Asteroide1', 'Asteroide2', 'Asteroide3', 'Bumper', 'Portal', 'Planeta', 'Ovni', 'Tee']
export_glb(ROOT+'/glb/golf.glb', ASSETS)
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/blend/golf.blend')
for n in ASSETS: bpy.data.objects[n].hide_render = True
gr = prim('cube', loc=(0, 0, -.1), scale=(1.8, 1.8, .1), m=GREEN); bevel(gr, .08)
showcase(['Asteroide2', 'Bandera', 'Hoyo', 'Bola', 'Planeta', 'Bumper', 'Ovni'],
         [(0, .2, -1.55), (.5, .3, 0), (.5, .3, 0), (-.4, -.7, 0), (-2.4, 3.5, 2.2), (-.9, .6, 0), (1.9, 2.2, 2.3)],
         [(0, 0, 0), (0, 0, .6), (0, 0, 0), (0, 0, 0), (.2, .3, 0), (0, 0, 0), (.2, -.2, 0)], [2.2, 1, 1, 1.3, .9, 1, .8])
ST = mat('Estrella', '#ffffff', 1, 0, emit='#ffffff', emit_str=8)
for _ in range(50): prim('ico', subdivisions=1, radius=.025, loc=(random.uniform(-7, 6), random.uniform(4, 10), random.uniform(-1, 7)), m=ST)
render_icon(ROOT+'/renders/golf.png', '#12062b', (3.4, -4.6, 3.2), (-.1, .4, .5), lens=34,
            lights=[('SUN', (2, -3, 6), 2.5, '#fff0ff'), ('POINT', (-1, 0, 1.5), 120, '#39f3ff'), ('POINT', (1.5, .5, 1.2), 120, '#ff4fd8')])
print('OK golf')
