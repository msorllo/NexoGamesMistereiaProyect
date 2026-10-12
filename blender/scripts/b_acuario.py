import sys, os, math, random; HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE); sys.path.insert(0, HERE)
from blib import *
import bmesh as _bm
reset(); random.seed(11)
EYE = mat('Ojo', '#0b0b12', .2); EYEW = mat('Ojo blanco', '#ffffff', .3)

def fin(verts, m, th=.015):
    me = bpy.data.meshes.new('fin'); bm = _bm.new(); vs = [bm.verts.new(v) for v in verts]; bm.faces.new(vs); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('fin', me); C.collection.objects.link(o); me.materials.append(m)
    o.modifiers.new('s', 'SOLIDIFY').thickness = th; C.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier='s')
    return o

def fish(name, body, stripe, finc, L=.5, H=.22, W=.12, stripes=0, globe=False):
    """Pez mirando a +X, con cola en -X."""
    B = mat(name + ' cuerpo', body, .4); S = mat(name + ' franja', stripe, .45); F = mat(name + ' aleta', finc, .5)
    parts = []
    bd = prim('sphere', segments=24, ring_count=14, radius=1, scale=(L, W, H) if not globe else (L, L * .9, L * .9), m=B, smooth=True); parts.append(bd)
    if globe:
        for k in range(26):
            th = random.uniform(0, math.tau); ph = random.uniform(.3, 2.8)
            d = Vector((math.cos(th) * math.sin(ph), math.sin(th) * math.sin(ph), math.cos(ph)))
            sp = prim('cone', loc=tuple(d * L * .92), vertices=4, radius1=.025, radius2=0, depth=.1, m=F)
            sp.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); parts.append(sp)
    for i in range(stripes):
        x = L * (.45 - i * .45)
        parts.append(prim('torus', loc=(x, 0, 0), rot=(0, math.pi / 2, 0), major_radius=1, minor_radius=.06, major_segments=32, minor_segments=6, scale=(H * 1.02 * (1 - abs(x) / L * .6), W * 1.05 * (1 - abs(x) / L * .6), 1), m=S, smooth=True))
    tx = -L * (1 if not globe else .9)
    parts.append(fin([(tx + .05, 0, 0), (tx - L * .55, 0, H * .95), (tx - L * .4, 0, 0), (tx - L * .55, 0, -H * .95)], F))
    parts.append(fin([(L * .2, 0, H * .9), (-L * .4, 0, H * 1.5), (-L * .5, 0, H * .7)], F))
    for s in (1, -1):
        parts.append(prim('sphere', loc=(L * .62, s * W * .75, H * .25), segments=12, ring_count=8, radius=H * .22, m=EYEW, smooth=True))
        parts.append(prim('sphere', loc=(L * .68, s * W * .9, H * .27), segments=10, ring_count=6, radius=H * .12, m=EYE, smooth=True))
        parts.append(fin([(L * .25, s * W * .9, -H * .2), (L * .0, s * W * 2.2, -H * .6), (-L * .05, s * W * .9, -H * .3)], F))
    return join(parts, name)

fish('PezPayaso', '#ff7a1a', '#ffffff', '#ff9a3d', .42, .2, .11, stripes=3)
fish('PezCirujano', '#2a5bff', '#101a3a', '#ffd21f', .5, .3, .08, stripes=0)
fish('PezGlobo', '#f2d27a', '#c99a3a', '#f7b267', .3, .3, .3, globe=True)
fish('PezNeon', '#27e0ff', '#ff2b55', '#9af7ff', .38, .1, .07, stripes=1)
fish('PezLuna', '#c9c3ff', '#8d7bff', '#e6e2ff', .45, .34, .06, stripes=0)

# Coral ramificado
CR = mat('Coral', '#ff5d8f', .7); pts = []
def branch(p, d, l, depth, acc):
    q = (p[0] + d[0] * l, p[1] + d[1] * l, p[2] + d[2] * l)
    acc.append(curve_tube([p, q], .05 * (depth + 1) * .6, CR))
    if depth > 0:
        for k in range(2):
            nd = Vector(d) + Vector((random.uniform(-.7, .7), random.uniform(-.7, .7), .3)); nd.normalize()
            branch(q, tuple(nd), l * .72, depth - 1, acc)
    else:
        acc.append(prim('sphere', loc=q, segments=8, ring_count=6, radius=.07, m=CR, smooth=True))
acc = []; branch((0, 0, 0), (0, 0, 1), .45, 3, acc); join(acc, 'Coral')
# Coral cerebro
CB = mat('Coral cerebro', '#b9e36a', .8); c = prim('ico', subdivisions=3, radius=.35, scale=(1, 1, .7), loc=(0, 0, .15), m=CB); displace(c, .06, .08, 9); bpy.ops.object.shade_smooth(); join([c], 'CoralCerebro')
# Alga (lámina ondulada, se anima en la web)
AL = mat('Alga', '#2fbf71', .6); al = []
for k in range(3):
    pts_ = [(math.sin(t * .9 + k) * .12 + (k - 1) * .12, 0, t * .35) for t in range(7)]
    al.append(curve_tube(pts_, .035, AL))
join(al, 'Alga')
# Cofre del tesoro
WD = mat('Madera cofre', '#7a4a26', .7); GD = mat('Oro', '#ffcc33', .25, 1); GEM = mat('Gema', '#ff2b6b', .1, 0, emit='#ff2b6b', emit_str=1.5)
ch = [bevel(prim('cube', loc=(0, 0, .15), scale=(.3, .2, .15), m=WD), .02)]
lid = prim('cyl', loc=(0, 0, .3), rot=(0, math.pi / 2, 0), vertices=16, radius=.2, depth=.6, scale=(1, 1, 1), m=WD)
for v in lid.data.vertices:
    if v.co.z < 0: v.co.z = 0
ch.append(lid)
for x in (-.22, 0, .22): ch.append(prim('cube', loc=(x, 0, .22), scale=(.025, .205, .23), m=GD))
ch.append(prim('cube', loc=(0, -.21, .28), scale=(.05, .02, .06), m=GD))
for k in range(6): ch.append(prim('cyl', loc=(random.uniform(-.2, .2), random.uniform(-.1, .1), .42 + k * .015), vertices=12, radius=.05, depth=.015, m=GD))
ch.append(prim('ico', subdivisions=1, radius=.05, loc=(.1, .05, .47), m=GEM))
join(ch, 'Cofre')
# Castillo
ST = mat('Piedra castillo', '#d9c7a3', .9); RF = mat('Tejado', '#3c78d8', .6)
cs = [bevel(prim('cube', loc=(0, 0, .3), scale=(.35, .35, .3), m=ST), .02)]
for x, y in [(-.35, -.35), (.35, -.35), (-.35, .35), (.35, .35)]:
    cs.append(prim('cyl', loc=(x, y, .4), vertices=12, radius=.12, depth=.8, m=ST))
    cs.append(prim('cone', loc=(x, y, .92), vertices=12, radius1=.15, radius2=0, depth=.3, m=RF))
cs.append(prim('cube', loc=(0, -.36, .15), scale=(.1, .02, .15), m=mat('Puerta', '#1c1c2e', .8)))
join(cs, 'Castillo')
# Concha
SH = mat('Concha', '#ffd6c9', .5)
cn = [prim('cone', loc=(0, .04 * k, .02), rot=(math.radians(-80), 0, math.radians(-40 + k * 16)), vertices=3, radius1=.05, radius2=.005, depth=.35, m=SH) for k in range(6)]
join(cn, 'Concha')
# Roca de fondo
r = prim('ico', subdivisions=2, radius=.5, scale=(1.2, .8, .6), loc=(0, 0, .15), m=mat('Roca marina', '#4a5b6a', .95)); displace(r, .15, .4, 4); join([r], 'RocaMar')

ASSETS = ['PezPayaso', 'PezCirujano', 'PezGlobo', 'PezNeon', 'PezLuna', 'Coral', 'CoralCerebro', 'Alga', 'Cofre', 'Castillo', 'Concha', 'RocaMar']
export_glb(ROOT+'/glb/acuario.glb', ASSETS)
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/blend/acuario.blend')
for n in ASSETS: bpy.data.objects[n].hide_render = True
prim('plane', size=20, loc=(0, 0, 0), m=mat('Arena fondo', '#e9d6a8', .95))
showcase(['PezPayaso', 'PezCirujano', 'Coral', 'CoralCerebro', 'Alga', 'Cofre', 'PezGlobo'],
         [(.1, 0, 1.2), (-.9, .9, 1.9), (-1.1, .6, 0), (1.1, .4, 0), (1.3, 1.2, 0), (.2, .5, 0), (1.3, -.2, 1.9)],
         [(0, 0, -.3), (0, 0, .4), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, .3), (0, 0, 2.8)], [1.6, 1.1, 1.1, 1, 1.4, 1.2, 1.1])
render_icon(ROOT+'/renders/acuario.png', '#0a7fa8', (0, -4.8, 1.6), (0, 0, 1.05), lens=36,
            lights=[('SUN', (1, -1, 8), 4, '#e8fbff'), ('AREA', (-3, -3, 3), 300, '#7ff0ff')])
print('OK acuario')
