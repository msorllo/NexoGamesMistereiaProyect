import sys, os, math, random; HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE); sys.path.insert(0, HERE)
from blib import *
reset()
WOOD = mat('Nogal', '#6b3a1f', .45); WOOD2 = mat('Nogal claro', '#9a5a2e', .45); GOLD = mat('Oro viejo', '#d4a94e', .28, 1)
VEL = mat('Terciopelo', '#7a1030', .95); BRASS = mat('Latón', '#e0b75a', .22, 1); STEEL = mat('Acero', '#d9dee6', .18, 1)
SKIN = mat('Porcelana', '#f6e6dc', .35); TUTU = mat('Tutú', '#ffc2d6', .6); HAIR = mat('Pelo', '#3a2418', .5); MIR = mat('Espejo tapa', '#dfe9ff', .03, 1)

# Caja (sin tapa): 2.4 x 1.4 x .8, interior de terciopelo
bx = []
W, D, Hh, t = 1.2, .7, .8, .08
bx.append(bevel(prim('cube', loc=(0, 0, t / 2), scale=(W, D, t / 2), m=WOOD), .02))
for s in (1, -1):
    bx.append(bevel(prim('cube', loc=(0, s * (D - t / 2), Hh / 2), scale=(W, t / 2, Hh / 2), m=WOOD), .02))
    bx.append(bevel(prim('cube', loc=(s * (W - t / 2), 0, Hh / 2), scale=(t / 2, D, Hh / 2), m=WOOD), .02))
bx.append(prim('cube', loc=(0, 0, t + .005), scale=(W - t, D - t, .005), m=VEL))
for z in (.1, Hh - .06):
    for s in (1, -1):
        bx.append(prim('cube', loc=(0, s * (D + .005), z), scale=(W + .005, .012, .025), m=GOLD))
for x in (-W, W):
    for y in (-D, D):
        bx.append(prim('sphere', loc=(x, y, -.02), segments=12, ring_count=8, radius=.09, m=GOLD, smooth=True))
join(bx, 'Caja')

# Tapa: bisagra en (0, D, Hh). Dibujada cerrada sobre la caja, gira sobre X.
ld = [bevel(prim('cube', loc=(0, 0, Hh + .06), scale=(W, D, .06), m=WOOD), .02),
      prim('cube', loc=(0, 0, Hh + .125), scale=(W * .7, D * .6, .008), m=WOOD2),
      prim('cube', loc=(0, 0, Hh - .004), scale=(W * .8, D * .75, .004), m=MIR)]
for k in range(4):
    a = k / 4 * math.tau + .785
    ld.append(prim('sphere', loc=(W * .55 * math.cos(a), D * .45 * math.sin(a), Hh + .13), segments=8, ring_count=6, radius=.04, m=GOLD))
join(ld, 'Tapa', origin=(0, D, Hh))

# Cilindro (tambor) con eje en X, centrado en (0,0,0)
dr = [prim('cyl', rot=(0, math.pi / 2, 0), vertices=48, radius=.22, depth=1.2, m=BRASS, smooth=True)]
for s in (1, -1): dr.append(prim('cyl', loc=(s * .62, 0, 0), rot=(0, math.pi / 2, 0), vertices=32, radius=.25, depth=.04, m=GOLD, smooth=True))
dr.append(prim('cyl', rot=(0, math.pi / 2, 0), vertices=12, radius=.03, depth=1.5, m=STEEL))
join(dr, 'Tambor')

# Púa (pin) pequeña, apuntando a +Z
join([prim('cyl', loc=(0, 0, .025), vertices=8, radius=.012, depth=.05, m=STEEL, smooth=True)], 'Pua')

# Peine: 15 dientes a lo largo de X, apuntando a -Y, base en y=0
cb = [bevel(prim('cube', loc=(0, .1, 0), scale=(.62, .08, .05), m=STEEL), .01)]
for i in range(15):
    x = -.56 + i * .08; L = .34 - i * .012
    cb.append(prim('cube', loc=(x, .02 - L / 2, 0), scale=(.028, L / 2, .012), m=STEEL))
join(cb, 'Peine')

# Manivela (eje en X)
mv = [prim('cyl', loc=(.12, 0, 0), rot=(0, math.pi / 2, 0), vertices=12, radius=.03, depth=.24, m=BRASS),
      prim('cube', loc=(.24, 0, -.12), scale=(.02, .02, .14), m=BRASS),
      prim('cyl', loc=(.3, 0, -.24), rot=(0, math.pi / 2, 0), vertices=12, radius=.035, depth=.12, m=WOOD2, smooth=True)]
join(mv, 'Manivela')

# Bailarina sobre peana giratoria
bl = [prim('cyl', loc=(0, 0, .03), vertices=32, radius=.22, depth=.06, m=GOLD, smooth=True),
      prim('cyl', loc=(0, 0, .09), vertices=32, radius=.17, depth=.06, m=VEL, smooth=True),
      prim('cyl', loc=(0, 0, .28), vertices=8, radius=.012, depth=.3, m=SKIN),  # pierna apoyo
      curve_tube([(0, 0, .3), (.08, 0, .34), (.2, 0, .36)], .012, SKIN),        # pierna arabesque
      prim('cone', loc=(0, 0, .44), vertices=24, radius1=.2, radius2=.04, depth=.08, m=TUTU, smooth=True),
      prim('cone', loc=(0, 0, .56), vertices=16, radius1=.045, radius2=.035, depth=.2, m=TUTU, smooth=True),
      prim('sphere', loc=(0, 0, .72), segments=16, ring_count=10, radius=.055, m=SKIN, smooth=True),
      prim('sphere', loc=(-.03, 0, .77), segments=10, ring_count=8, radius=.035, m=HAIR, smooth=True),
      curve_tube([(0, .04, .62), (0, .12, .72), (0, .08, .86)], .01, SKIN),
      curve_tube([(0, -.04, .62), (0, -.12, .72), (0, -.08, .86)], .01, SKIN)]
join(bl, 'Bailarina')

ASSETS = ['Caja', 'Tapa', 'Tambor', 'Pua', 'Peine', 'Manivela', 'Bailarina']
export_glb(ROOT+'/glb/caja.glb', ASSETS)
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/blend/caja.blend')
for n in ASSETS: bpy.data.objects[n].hide_render = True
prim('plane', size=20, m=mat('Mesa', '#2a1a14', .6))
dup = showcase(['Caja', 'Tapa', 'Tambor', 'Peine', 'Bailarina', 'Manivela'],
               [(0, 0, .12), (0, .7, .92), (.25, .1, .55), (.25, -.3, .5), (-.55, -.05, .21), (1.2, .1, .55)],
               [(0, 0, 0), (math.radians(-100), 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, .5), (0, 0, 0)], [1, 1, 1, 1, 2.1, 1])
dup[1].location = (0, .7, .92)
render_icon(ROOT+'/renders/caja.png', '#3a1426', (1.6, -2.9, 2.2), (-.2, 0, .75), lens=38,
            lights=[('AREA', (2, -2, 3), 250, '#ffe2b8'), ('POINT', (-1.2, -.6, 1.6), 60, '#ffb3cf'), ('SUN', (-2, 3, 5), 1.5, '#c9b8ff')])
print('OK caja')
