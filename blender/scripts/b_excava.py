import sys, os, math, random; HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE); sys.path.insert(0, HERE)
from blib import *
reset(); random.seed(5)
BONE = mat('Hueso fósil', '#e3d2ad', .8); BONE2 = mat('Hueso oscuro', '#b59a6a', .85); TOOTH = mat('Diente', '#f7efd8', .4)
AMB = mat('Ámbar', '#ff9a1f', .08, 0, emit='#ff7a00', emit_str=.8, alpha=.8); BUG = mat('Mosquito', '#2a1a0a', .6)
STONE = mat('Piedra fósil', '#8c8378', .9); CLAY = mat('Terracota', '#c0663a', .75); CLAY2 = mat('Terracota oscura', '#7f3a1d', .8)
GOLD = mat('Oro moneda', '#ffcf40', .2, 1); CRY = mat('Cristal', '#b58cff', .05, 0, emit='#9b6bff', emit_str=1.2, alpha=.85); IRON = mat('Hierro pico', '#6b7580', .35, .9)
HAND = mat('Mango', '#8a5a36', .65)

# Cráneo de dinosaurio (mira a +X)
sk = [prim('sphere', loc=(0, 0, .3), segments=24, ring_count=12, radius=1, scale=(.55, .28, .26), m=BONE, smooth=True),
      prim('sphere', loc=(.45, 0, .22), segments=20, ring_count=10, radius=1, scale=(.4, .18, .15), m=BONE, smooth=True),
      prim('sphere', loc=(.3, 0, .06), segments=20, ring_count=10, radius=1, scale=(.55, .16, .07), m=BONE2, smooth=True)]
for s in (1, -1):
    sk.append(prim('sphere', loc=(-.05, s * .23, .38), segments=12, ring_count=8, radius=.09, m=mat('Cuenca', '#3a2c1c', .9), smooth=True))
    sk.append(prim('sphere', loc=(.4, s * .15, .3), segments=10, ring_count=6, radius=.05, m=mat('Cuenca', '#3a2c1c', .9), smooth=True))
    for i in range(7):
        x = .08 + i * .1
        sk.append(prim('cone', loc=(x, s * .12, .13), rot=(math.pi, 0, 0), vertices=6, radius1=.025, radius2=0, depth=.1, m=TOOTH))
sk.append(prim('cone', loc=(-.35, 0, .55), rot=(0, math.radians(-50), 0), vertices=8, radius1=.08, radius2=0, depth=.35, m=BONE2, smooth=True))
join(sk, 'Craneo')

# Amonites (espiral logarítmica)
pts = []
for i in range(120):
    a = i / 120 * 5.2 * math.pi; r = .03 * math.exp(.19 * a)
    pts.append((r * math.cos(a), 0, r * math.sin(a) + .35))
am = curve_tube(pts, .0, STONE)
bpy.data.objects.remove(am, do_unlink=True)
parts = []
for i in range(0, 120, 3):
    a = i / 120 * 5.2 * math.pi; r = .03 * math.exp(.19 * a)
    parts.append(prim('sphere', loc=(r * math.cos(a), 0, r * math.sin(a) + .35), segments=10, ring_count=6, radius=r * .38 + .01, scale=(1, .7, 1), m=STONE if i % 6 else BONE2, smooth=True))
join(parts, 'Amonites')

# Trilobites
tr = [prim('sphere', loc=(0, 0, .05), segments=20, ring_count=10, radius=1, scale=(.35, .24, .07), m=STONE, smooth=True),
      prim('sphere', loc=(.28, 0, .06), segments=16, ring_count=8, radius=1, scale=(.12, .25, .07), m=BONE2, smooth=True)]
for i in range(9):
    x = .18 - i * .06
    tr.append(prim('torus', loc=(x, 0, .06), rot=(0, math.pi / 2, 0), major_radius=1, minor_radius=.08, major_segments=24, minor_segments=4, scale=(.06, .24 * (1 - i * .07), 1), m=BONE2))
tr.append(prim('cube', loc=(0, 0, .12), scale=(.33, .05, .02), m=BONE2))
join(tr, 'Trilobites')

# Ámbar con mosquito
ab = prim('ico', subdivisions=2, radius=.2, scale=(1.2, .9, .8), loc=(0, 0, .16), m=AMB); displace(ab, .04, .3, 6)
bg = [prim('sphere', loc=(0, 0, .16), segments=8, ring_count=6, radius=.03, scale=(2, 1, 1), m=BUG), curve_tube([(-.02, .0, .17), (-.05, .08, .2)], .004, BUG), curve_tube([(-.02, 0, .17), (-.05, -.08, .2)], .004, BUG)]
join([ab] + bg, 'Ambar')

# Ánfora (torno)
prof = [(.0, 0), (.06, 0), (.1, .03), (.18, .15), (.22, .3), (.2, .45), (.12, .58), (.06, .66), (.06, .74), (.09, .78)]
af = lathe(prof, CLAY, 'anf')
sol = af.modifiers.new('s', 'SOLIDIFY'); sol.thickness = .015; C.view_layer.objects.active = af; bpy.ops.object.modifier_apply(modifier='s')
parts = [af]
for s in (1, -1): parts.append(curve_tube([(0, s * .07, .7), (0, s * .2, .68), (0, s * .2, .5)], .015, CLAY2))
parts.append(prim('torus', loc=(0, 0, .35), major_radius=.215, minor_radius=.01, major_segments=32, minor_segments=4, m=CLAY2))
join(parts, 'Anfora')

# Moneda de oro
mo = [prim('cyl', loc=(0, 0, .015), vertices=32, radius=.12, depth=.03, m=GOLD, smooth=True), prim('torus', loc=(0, 0, .03), major_radius=.105, minor_radius=.008, major_segments=32, minor_segments=4, m=GOLD),
      prim('cyl', loc=(0, 0, .032), vertices=5, radius=.05, depth=.005, m=GOLD)]
join(mo, 'Moneda')

# Geoda de cristales
ge = [prim('ico', subdivisions=2, radius=.25, scale=(1, 1, .6), loc=(0, 0, .1), m=STONE)]
for k in range(9):
    a = random.uniform(0, math.tau); tilt = random.uniform(.1, .6)
    c = prim('cone', loc=(.08 * math.cos(a), .08 * math.sin(a), .25), vertices=6, radius1=.05, radius2=0, depth=random.uniform(.2, .4), m=CRY)
    c.rotation_euler = (tilt * math.sin(a), -tilt * math.cos(a), 0); ge.append(c)
join(ge, 'Geoda')

# Herramientas
pk = [prim('cyl', loc=(0, 0, .45), vertices=10, radius=.035, depth=.9, m=HAND, smooth=True),
      prim('cone', loc=(.18, 0, .88), rot=(0, math.pi / 2, 0), vertices=6, radius1=.05, radius2=.005, depth=.36, m=IRON),
      prim('cone', loc=(-.18, 0, .88), rot=(0, -math.pi / 2, 0), vertices=6, radius1=.05, radius2=.005, depth=.36, m=IRON)]
join(pk, 'Pico')
br = [prim('cyl', loc=(0, 0, .2), vertices=10, radius=.025, depth=.4, m=HAND, smooth=True), bevel(prim('cube', loc=(0, 0, .45), scale=(.07, .025, .06), m=mat('Cerdas', '#d9b77a', .9)), .01)]
join(br, 'Pincel')

ASSETS = ['Craneo', 'Amonites', 'Trilobites', 'Ambar', 'Anfora', 'Moneda', 'Geoda', 'Pico', 'Pincel']
export_glb(ROOT+'/glb/excava.glb', ASSETS)
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/blend/excava.blend')
for n in ASSETS: bpy.data.objects[n].hide_render = True
dirt = prim('plane', size=20, m=mat('Tierra', '#8a5a3b', .95))
for k in range(30):
    prim('ico', subdivisions=1, radius=random.uniform(.03, .08), loc=(random.uniform(-2, 2), random.uniform(-1, 2), .02), m=mat('Guijarro', '#a77a55', .9))
showcase(['Craneo', 'Amonites', 'Ambar', 'Pico', 'Moneda', 'Geoda'],
         [(-.2, .2, 0), (1.05, .5, 0), (.9, -.55, 0), (-1.2, .9, 0), (.2, -.8, 0), (-1.05, -.55, 0)],
         [(0, 0, .5), (0, 0, .3), (0, 0, .5), (0, math.radians(70), .3), (.3, 0, 0), (0, 0, 0)], [1.5, 1.4, 1.5, 1.2, 1.4, 1.3])
render_icon(ROOT+'/renders/excava.png', '#d99a5b', (0, -3.4, 3.4), (0, 0, .2), lens=38,
            lights=[('SUN', (3, -2, 6), 4.5, '#fff0d0'), ('AREA', (-3, -2, 2), 150, '#ffc890')])
print('OK excava')
