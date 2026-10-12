import sys, os, math; HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE); sys.path.insert(0, HERE)
from blib import *
reset()
RED = mat('Rojo faro', '#d7263d', .45); WHITE = mat('Blanco faro', '#f4f1ea', .5); DARK = mat('Hierro', '#1f2a36', .35, .6)
GLASS = mat('Linterna', '#ffe9a8', .1, 0, emit='#ffd35a', emit_str=6); ROCK = mat('Roca', '#5b6470', .9); ROCK2 = mat('Roca oscura', '#3d4450', .95)
WOOD = mat('Madera', '#8a5a36', .7); SILVER = mat('Espejo', '#e8f1ff', .05, 1.0); BRASS = mat('Latón', '#c9a24a', .3, 1.0)
SAND = mat('Arena', '#e8d3a0', .95); GRASS = mat('Hierba costa', '#6fae6a', .9); SAIL = mat('Vela', '#fff8ea', .8)
HULL = mat('Casco', '#2f5d8a', .5); HULL2 = mat('Casco rojo', '#b33a3a', .5); LAMP = mat('Farol barco', '#ffcf6b', .2, emit='#ffb938', emit_str=4)

# ---------- Faro ----------
parts = []
base = prim('cyl', loc=(0, 0, .15), vertices=24, radius=.62, depth=.3, m=ROCK2); parts.append(bevel(base, .05))
n = 6
for i in range(n):
    z0 = .3 + i * .42; r0 = .5 - i * .035; r1 = .5 - (i + 1) * .035
    c = prim('cone', loc=(0, 0, z0 + .21), vertices=32, radius1=r0, radius2=r1, depth=.42, m=RED if i % 2 == 0 else WHITE, smooth=True)
    parts.append(c)
top = .3 + n * .42
gal = prim('cyl', loc=(0, 0, top + .04), vertices=32, radius=.46, depth=.08, m=DARK); parts.append(gal)
rail = prim('torus', loc=(0, 0, top + .22), major_radius=.43, minor_radius=.018, major_segments=40, minor_segments=6, m=DARK); parts.append(rail)
for k in range(12):
    a = k / 12 * math.tau
    parts.append(prim('cyl', loc=(.43 * math.cos(a), .43 * math.sin(a), top + .13), vertices=6, radius=.012, depth=.18, m=DARK))
lan = prim('cyl', loc=(0, 0, top + .32), vertices=16, radius=.26, depth=.5, m=GLASS); parts.append(lan)
for k in range(8):
    a = k / 8 * math.tau
    parts.append(prim('cube', loc=(.26 * math.cos(a), .26 * math.sin(a), top + .32), rot=(0, 0, a), scale=(.02, .02, .25), m=DARK))
roof = prim('cone', loc=(0, 0, top + .72), vertices=32, radius1=.34, radius2=.02, depth=.3, m=RED, smooth=True); parts.append(roof)
parts.append(prim('sphere', loc=(0, 0, top + .9), segments=12, ring_count=8, radius=.06, m=BRASS, smooth=True))
door = prim('cube', loc=(0, -.5, .55), scale=(.12, .05, .2), m=DARK); parts.append(door)
for i in (1, 3):
    parts.append(prim('cube', loc=(0, -.46 + i * .004, .3 + i * .42 + .2), scale=(.07, .03, .09), m=GLASS))
join(parts, 'Faro')

# ---------- Espejo (gira sobre Z) ----------
p = []
p.append(bevel(prim('cyl', loc=(0, 0, .05), vertices=20, radius=.3, depth=.1, m=WOOD), .02))
p.append(prim('cyl', loc=(0, 0, .25), vertices=8, radius=.04, depth=.35, m=BRASS, smooth=True))
fr = prim('torus', loc=(0, 0, .62), rot=(math.pi / 2, 0, 0), major_radius=.3, minor_radius=.04, major_segments=32, minor_segments=8, m=BRASS, smooth=True); p.append(fr)
mir = prim('cyl', loc=(0, 0, .62), rot=(math.pi / 2, 0, 0), vertices=32, radius=.29, depth=.03, m=SILVER, smooth=True); p.append(mir)
back = prim('cyl', loc=(0, .03, .62), rot=(math.pi / 2, 0, 0), vertices=32, radius=.29, depth=.02, m=WOOD); p.append(back)
join(p, 'Espejo')

# ---------- Barco ----------
b = []
hull = prim('cube', loc=(0, 0, .12), scale=(.42, .16, .1), m=HULL)
bm_ = hull.data
for v in bm_.vertices:
    if v.co.z < .12: v.co.x *= .75; v.co.y *= .6
    if v.co.x > .3: v.co.y *= .25
b.append(bevel(hull, .03))
b.append(prim('cube', loc=(0, 0, .23), scale=(.36, .13, .015), m=WOOD))
b.append(prim('cyl', loc=(-.02, 0, .6), vertices=8, radius=.018, depth=.75, m=WOOD))
import bmesh as _bm
me = bpy.data.meshes.new('sail'); bmm = _bm.new()
v1 = bmm.verts.new((0, 0, .3)); v2 = bmm.verts.new((0, 0, .95)); v3 = bmm.verts.new((.32, 0, .32)); bmm.faces.new((v1, v3, v2)); bmm.to_mesh(me); bmm.free()
so = bpy.data.objects.new('sail', me); C.collection.objects.link(so); me.materials.append(SAIL)
so.modifiers.new('s', 'SOLIDIFY').thickness = .02; C.view_layer.objects.active = so; bpy.ops.object.modifier_apply(modifier='s'); b.append(so)
b.append(prim('sphere', loc=(-.3, 0, .32), segments=12, ring_count=8, radius=.05, m=LAMP, smooth=True))
join(b, 'Barco')

# ---------- Roca ----------
r = prim('ico', subdivisions=2, radius=.42, loc=(0, 0, .2), scale=(1, .9, .7), m=ROCK); displace(r, .18, .45, 1)
r2 = prim('ico', subdivisions=1, radius=.2, loc=(.3, .15, .1), m=ROCK2); displace(r2, .08, .3, 2)
join([r, r2], 'Roca')

# ---------- Casilla (tile de isla) ----------
t = prim('cube', loc=(0, 0, -.1), scale=(.48, .48, .1), m=SAND); bevel(t, .04)
g = prim('cube', loc=(0, 0, .005), scale=(.44, .44, .012), m=GRASS); bevel(g, .01)
join([t, g], 'Casilla')

# ---------- Boya ----------
bo = [prim('cyl', loc=(0, 0, .15), vertices=16, radius=.14, depth=.3, m=RED, smooth=True),
      prim('cyl', loc=(0, 0, .33), vertices=16, radius=.1, depth=.08, m=WHITE, smooth=True),
      prim('sphere', loc=(0, 0, .42), segments=12, ring_count=8, radius=.06, m=LAMP, smooth=True)]
join(bo, 'Boya')

ASSETS = ['Faro', 'Espejo', 'Barco', 'Roca', 'Casilla', 'Boya']
export_glb(ROOT+'/glb/faro.glb', ASSETS)
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/blend/faro.blend')
# ---------- Icono ----------
for n_ in ASSETS: bpy.data.objects[n_].hide_render = True
sea = prim('plane', size=30, m=mat('Mar', '#0f2c4a', .25, .1))
isl = showcase(['Roca', 'Faro', 'Roca', 'Barco'], [(0, 0, -.25), (0, 0, 0), (.9, .6, -.3), (1.3, -1.4, -.02)], [(0, 0, 0), (0, 0, 0), (0, 0, 2), (0, 0, 2.4)], [3.2, 1, 1.5, 1.4])
import random
random.seed(3)
ST=mat('Estrella','#ffffff',1,0,emit='#ffffff',emit_str=8)
for _ in range(40): prim('ico',subdivisions=1,radius=.03,loc=(random.uniform(-9,6),random.uniform(6,12),random.uniform(2,8)),m=ST)
render_icon(ROOT+'/renders/faro.png', '#0b1a33', (4.6, -6.4, 2.6), (.2, 0, 1.5), lens=38,
            lights=[('SUN', (-3, -2, 6), 1.2, '#9fb8ff'), ('POINT', (0, 0, 3.3), 250, '#ffd35a'), ('AREA', (4, -5, 4), 300, '#ffc58a')])
print('OK faro')
