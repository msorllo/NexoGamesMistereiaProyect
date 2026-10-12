"""COLMENA (app 28): colmenar sobre una loma flotante, panal, abeja, flores (azahar, lavanda, girasol, romero, brezo, margarita),
tarro, ahumador, apicultor, naranjo, moneda, mariposa, valla, nube, hierba… Exporta colmena.glb + .blend + icono.
Convención: frente = -Y de Blender (= +Z en three.js). Todo a escala de escena (colmena ≈ .8 de alto)."""
import sys, os, math, random; HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
from blib import *
import bmesh
reset(); random.seed(28)
TAU = math.tau

# ---------- materiales ----------
def pmat(name, color, rough=.55, metal=0., trans=0., ior=1.45, coat=0., coat_r=.1, sheen=0., emit=None, emit_str=1., alpha=1., spec=None):
    m = mat(name, color, rough, metal, emit, emit_str, alpha)
    p = m.node_tree.nodes.get('Principled BSDF')
    if trans: p.inputs['Transmission Weight'].default_value = trans; p.inputs['IOR'].default_value = ior
    if coat: p.inputs['Coat Weight'].default_value = coat; p.inputs['Coat Roughness'].default_value = coat_r
    if sheen: p.inputs['Sheen Weight'].default_value = sheen
    if spec is not None: p.inputs['Specular IOR Level'].default_value = spec
    return m

PAINT_A = pmat('Pintura crema', '#e8dcbc', .78)
PAINT_B = pmat('Pintura salvia', '#93b3a6', .78)
WOOD = pmat('Madera vieja', '#7a5534', .85)
WOOD_D = pmat('Madera oscura', '#4a321f', .9)
WOOD_L = pmat('Madera clara', '#b8905f', .8)
SHADOW = pmat('Piquera', '#1a1008', .95)
ZINC = pmat('Chapa galvanizada', '#b9bec2', .38, .9)
STONE = pmat('Piedra caliza', '#b7ada0', .9)
WAX = pmat('Cera', '#f2cc6b', .42, spec=.6)
WAX_B = pmat('Cera base', '#e3b447', .5)
HONEY = pmat('Miel', '#f2a900', .08, trans=.6, ior=1.5, coat=.6, coat_r=.05)
BEE_Y = pmat('Abeja amarillo', '#e3a21a', .55, sheen=.6)
BEE_K = pmat('Abeja negro', '#1d140c', .5, sheen=.4)
BEE_T = pmat('Abeja torax', '#8a5a22', .9, sheen=1.)
BEE_E = pmat('Abeja ojo', '#0c0806', .15, coat=1)
WING = pmat('Ala abeja', '#eef6ff', .15, alpha=.38)
STEM = pmat('Tallo', '#4f7a2a', .7)
LEAF = pmat('Hoja', '#3f6a24', .6)
LEAF_OR = pmat('Hoja naranjo', '#2e5a1d', .35, coat=.4)
AZAHAR = pmat('Azahar', '#fffdf6', .45, sheen=.5)
POLLEN = pmat('Estambre', '#f4c430', .6)
LAV = pmat('Lavanda', '#7d5fc0', .7)
LAV_L = pmat('Hoja lavanda', '#8aa187', .8)
SUN_P = pmat('Petalo girasol', '#f7b500', .6)
SUN_C = pmat('Disco girasol', '#3b2410', .95)
ROS = pmat('Romero', '#4e6b4c', .75)
ROS_F = pmat('Flor romero', '#a9b8ea', .55)
HEA = pmat('Brezo', '#c05a94', .7)
HEA_L = pmat('Hoja brezo', '#4a5d2c', .85)
DAISY = pmat('Margarita', '#fbfaf2', .6)
POPPY = pmat('Amapola', '#d8321f', .55)
GLASS = pmat('Vidrio', '#ffffff', .04, trans=1., ior=1.5)
CLOTH = pmat('Tela cuadros', '#b53a2a', .95, sheen=.8)
TWINE = pmat('Cuerda', '#c9a46a', .95)
LABEL = pmat('Etiqueta', '#f6ecd0', .85)
STEEL = pmat('Acero', '#c9ced3', .28, 1.)
LEATHER = pmat('Cuero', '#7b4a2a', .7)
SUIT = pmat('Traje apicultor', '#f4f2ea', .85, sheen=.4)
GLOVE = pmat('Guante', '#c9a36a', .75)
SKIN = pmat('Piel', '#d9a07a', .6)
VEIL = pmat('Velo', '#1b1b1b', .9, alpha=.55)
GRASS = pmat('Hierba prado', '#6f9a36', .9)
SOIL = pmat('Tierra', '#6b4428', .95)
SOIL_D = pmat('Tierra honda', '#4f3220', .95)
ROCK = pmat('Roca', '#8d8173', .95)
BARK = pmat('Corteza', '#5c4330', .9)
ORANGE = pmat('Naranja', '#f07a12', .45, coat=.3)
GOLD = pmat('Oro moneda', '#f5c14b', .25, 1.)
BUT_O = pmat('Mariposa ala', '#f08a1c', .6)
BUT_K = pmat('Mariposa borde', '#1a120c', .6)
CLOUD = pmat('Nube', '#ffffff', .95)
BLADE = pmat('Brizna', '#7aa83c', .75)
SIGN = pmat('Cartel', '#c9a577', .85)

# ---------- helpers ----------
def mesh_obj(name, verts, faces, mats, fmat=None, smooth=False):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    o = bpy.data.objects.new(name, me); C.collection.objects.link(o)
    for m in mats: me.materials.append(m)
    if fmat:
        for i, p in enumerate(me.polygons): p.material_index = fmat[i]
    if smooth:
        for p in me.polygons: p.use_smooth = True
    return o

def place(o, loc=(0, 0, 0), rot=(0, 0, 0), s=1.):
    o.location = loc; o.rotation_euler = rot; o.scale = (s, s, s) if not isinstance(s, tuple) else s
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); C.view_layer.objects.active = o
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return o

def bx(loc, size, m, bv=.006, seg=1):
    o = prim('cube', loc=loc, scale=(size[0] / 2, size[1] / 2, size[2] / 2), m=m)
    return bevel(o, bv, seg) if bv else o

def petal(L, W, cup, m, segs=3, name='petal', tip=.2):
    """pétalo curvado que crece hacia +Y desde el origen, cóncavo hacia +Z"""
    vs, fs = [], []
    for i in range(segs + 1):
        t = i / segs; w = W * math.sin(math.pi * (0.12 + 0.88 * t) ** (1 - tip)) * (1 - .25 * t)
        y = L * t; z = cup * t * t
        vs += [(-w, y, z + cup * .35 * t), (0, y, z), (w, y, z + cup * .35 * t)]
    for i in range(segs):
        a = i * 3
        fs += [(a, a + 3, a + 4, a + 1), (a + 1, a + 4, a + 5, a + 2)]
    return mesh_obj(name, vs, fs, [m], smooth=True)

def leaf(L, W, m, bend=.3, name='leaf'):
    return petal(L, W, bend, m, 3, name, tip=.45)

def tube(pts, r, m, res=1):
    o = curve_tube(pts, r, m)
    o.data.name = 'tube'
    return o

def lowtube(pts, r, m, sides=5):
    """tubo facetado barato (pocos vértices)"""
    vs, fs = [], []
    n = len(pts)
    for i, p in enumerate(pts):
        a = Vector(pts[max(0, i - 1)]); b = Vector(pts[min(n - 1, i + 1)]); d = (b - a).normalized()
        up = Vector((0, 0, 1)) if abs(d.z) < .9 else Vector((1, 0, 0))
        u = d.cross(up).normalized(); v = d.cross(u).normalized()
        rr = r * (1 - .55 * i / max(1, n - 1))
        for k in range(sides):
            an = k / sides * TAU
            vs.append(tuple(Vector(p) + (u * math.cos(an) + v * math.sin(an)) * rr))
    for i in range(n - 1):
        for k in range(sides):
            a = i * sides + k; b = i * sides + (k + 1) % sides
            fs.append((a, b, b + sides, a + sides))
    return mesh_obj('lt', vs, fs, [m], smooth=True)

def hexring(r, y, rot=math.pi / 2):
    return [(r * math.cos(rot + k * TAU / 6), y, r * math.sin(rot + k * TAU / 6)) for k in range(6)]

# =====================================================================================
# COLMENA Langstroth
# =====================================================================================
W, D = .50, .44
cp = []
for sx in (-1, 1):  # soporte: dos largueros + patas
    cp.append(bx((sx * .19, 0, .13), (.05, D + .12, .05), WOOD_D, .004))
    for sy in (-1, 1): cp.append(bx((sx * .19, sy * (D / 2 + .01), .055), (.055, .055, .11), WOOD_D, .004))
cp.append(bx((0, -.02, .175), (W + .02, D + .06, .03), WOOD, .004))                     # suelo
cp.append(place(bx((0, 0, 0), (W - .02, .11, .018), WOOD, .003), (0, -D / 2 - .07, .168), (-.12, 0, 0)))  # piquera (tabla de vuelo)
for sx in (-1, 1): cp.append(bx((sx * (W / 2 - .01), -.01, .2), (.02, D + .02, .025), WOOD, .003))
cp.append(bx((0, D / 2 - .01, .2), (W, .02, .025), WOOD, .003))
cp.append(bx((0, -D / 2 + .05, .2), (W - .05, .02, .022), SHADOW, 0))                   # oscuridad de la entrada
cp.append(bx((.16, -D / 2 - .004, .2), (.12, .018, .022), WOOD_L, .003))                   # reductor de piquera
z = .2125
for i, (h, m) in enumerate([(.24, PAINT_A), (.24, PAINT_B), (.16, PAINT_A)]):
    cp.append(bx((0, 0, z + h / 2), (W, D, h - .006), m, .008, 2))
    for sx in (-1, 1):  # listones-asa laterales
        cp.append(bx((sx * (W / 2 + .008), 0, z + h * .72), (.016, .16, .026), m, .004))
    cp.append(bx((0, -D / 2 - .004, z + h * .72), (.13, .012, .03), m, .004))
    z += h
cp.append(bx((0, 0, z + .035), (W + .05, D + .05, .07), WOOD_L, .006))                   # tapa telescópica
cp.append(bx((0, 0, z + .075), (W + .08, D + .08, .012), ZINC, .003))                    # chapa
for sx in (-1, 1): cp.append(bx((sx * (W / 2 + .04), 0, z + .052), (.008, D + .08, .045), ZINC, .002))
for sy in (-1, 1): cp.append(bx((0, sy * (D / 2 + .04), z + .052), (W + .08, .008, .045), ZINC, .002))
st = prim('cube', loc=(.08, .05, z + .12), scale=(.11, .07, .04), m=STONE); bevel(st, .02, 2); displace(st, .012, .15, 3)
st.rotation_euler = (0, 0, .35); cp.append(place(st))
cp.append(bx((-.14, -D / 2 - .012, .56), (.07, .006, .045), ZINC, .002))                  # chapita numerada
join(cp, 'Colmena', origin=(0, 0, 0))

# =====================================================================================
# MARCO expositor + panal (celda) + celda de miel
# =====================================================================================
FW, FB = 1.7, .05
Z0 = .25
mk = [bx((0, 0, Z0 + .015), (FW - .1, .06, .03), WOOD_L, .004),                          # barra inferior
      bx((0, 0, Z0 + 1.15 - .025), (FW + .22, .07, .05), WOOD_L, .006)]                    # barra superior con orejetas
for sx in (-1, 1):
    mk.append(bx((sx * (FW / 2 - .025), 0, Z0 + .575), (FB, .06, 1.15), WOOD_L, .005))
    for sy in (-1, 1):  # patas en A
        leg = bx((0, 0, 0), (.05, .05, .62), WOOD, .004)
        mk.append(place(leg, (sx * (FW / 2 - .025), sy * .16, .3), (sy * .5, 0, 0)))
    mk.append(bx((sx * (FW / 2 - .025), 0, .07), (.05, .5, .04), WOOD, .004))
    for k in range(4):  # clavos
        mk.append(prim('cyl', loc=(sx * (FW / 2 - .025), -.032, Z0 + .15 + k * .28), rot=(math.pi / 2, 0, 0), vertices=6, radius=.008, depth=.006, m=STEEL))
mk.append(bx((0, .006, Z0 + .575), (FW - .09, .012, 1.08), WAX_B, 0))                       # lámina de cera estampada
join(mk, 'Marco', origin=(0, 0, 0))

R_CELL, WALL, DEPTH = .058, .0075, .06
def cell_mesh(name):
    o, i_ = hexring(R_CELL, 0), hexring(R_CELL - WALL, 0)
    of, if_ = hexring(R_CELL, -DEPTH), hexring(R_CELL - WALL, -DEPTH)
    vs = o + i_ + of + if_ + [(0, -.004, 0)]
    fs = []
    for k in range(6):
        n = (k + 1) % 6
        fs.append((12 + k, 12 + n, 18 + n, 18 + k))   # borde frontal
        fs.append((0 + k, 0 + n, 12 + n, 12 + k))     # pared exterior
        fs.append((18 + k, 18 + n, 6 + n, 6 + k))     # pared interior
        fs.append((6 + k, 6 + n, 24))                 # fondo (piramidal)
    ob = mesh_obj(name, vs, fs, [WAX]); return ob
cell_mesh('Panal')

def honey_mesh(name):
    r = R_CELL - WALL - .001
    b, f = hexring(r, -.001), hexring(r, -DEPTH + .006)
    vs = b + f + [(0, -DEPTH - .002, 0), (0, -.001, 0)]
    fs = []
    for k in range(6):
        n = (k + 1) % 6
        fs.append((k, n, 6 + n, 6 + k)); fs.append((6 + k, 6 + n, 12)); fs.append((n, k, 13))
    ob = mesh_obj(name, vs, fs, [HONEY]); return ob
honey_mesh('Celda miel')

# =====================================================================================
# ABEJA (+ Ala). Mira hacia -Y (= +Z en three). ~.09 de largo
# =====================================================================================
bp = []
ab = prim('sphere', loc=(0, .032, -.002), segments=12, ring_count=8, radius=1, scale=(.019, .03, .018), smooth=True, m=BEE_Y)
ab.data.materials.append(BEE_K)
for v in ab.data.vertices:
    if v.co.y > 0: f = 1 - .5 * (v.co.y / .03) ** 2; v.co.x *= f; v.co.z *= f
for p in ab.data.polygons:
    y = p.center.y
    if (-.012 < y < -.003) or (.006 < y < .015) or y > .024: p.material_index = 1
bp.append(ab)
bp.append(prim('sphere', loc=(0, 0, .002), segments=10, ring_count=7, radius=.017, smooth=True, m=BEE_T))
bp.append(prim('sphere', loc=(0, -.025, .002), segments=10, ring_count=6, radius=1, scale=(.0135, .011, .013), smooth=True, m=BEE_K))
for s in (-1, 1):
    bp.append(prim('sphere', loc=(s * .0105, -.027, .005), segments=8, ring_count=5, radius=1, scale=(.005, .007, .009), smooth=True, m=BEE_E))
    bp.append(lowtube([(s * .005, -.034, .01), (s * .012, -.046, .022), (s * .02, -.055, .018)], .0016, BEE_K, 4))
    for k, (yy, sp) in enumerate([(-.008, -.5), (.0, 0), (.008, .6)]):
        bp.append(lowtube([(s * .01, yy, -.008), (s * .026, yy + sp * .01, -.014), (s * .03, yy + sp * .02, -.03)], .0018, BEE_K, 4))
join(bp, 'Abeja', origin=(0, 0, 0))

def wing_shape(L, Wd, n=9):
    pts = []
    for k in range(n):
        a = k / (n - 1) * math.pi
        pts.append((L * .5 * (1 - math.cos(a)), Wd * math.sin(a) * (1 - .3 * (k / n))))
    return pts
wl = []
for s in (-1, 1):
    for (L, Wd, ang, off) in [(.058, .018, .42, 0), (.04, .013, .75, .004)]:
        sh = wing_shape(L, Wd)
        vs = [(0, 0, 0)] + [(s * x, y * .9, 0) for (x, y) in sh] + [(s * x, -y * .35, 0) for (x, y) in reversed(sh[1:-1])]
        fs = [tuple([0] + list(range(1, len(vs))))]
        o = mesh_obj('w', vs, fs, [WING])
        place(o, (s * .006, off, .016), (0, -s * .35, s * ang))
        wl.append(o)
join(wl, 'Ala', origin=(0, 0, .016))

# =====================================================================================
# FLORES
# =====================================================================================
def blossom(center, m_pet, m_ctr, r=.05, n=5, cup=.02, stam=8, facing=(0, 0, 0)):
    parts = []
    for k in range(n):
        p = petal(r, r * .45, cup, m_pet)
        place(p, (0, 0, 0), (0, 0, k / n * TAU))
        parts.append(p)
    parts.append(prim('sphere', loc=(0, 0, .006), segments=8, ring_count=5, radius=r * .22, m=m_ctr, smooth=True))
    for k in range(stam):
        a = k / stam * TAU
        parts.append(lowtube([(0, 0, .004), (math.cos(a) * r * .25, math.sin(a) * r * .25, r * .45)], .0022, POLLEN, 3))
        parts.append(prim('cube', loc=(math.cos(a) * r * .26, math.sin(a) * r * .26, r * .47), scale=(.004, .004, .004), m=POLLEN))
    b = join(parts, 'bl')
    place(b, center, facing)
    return b

# Azahar: ramita de naranjo con flores blancas cerosas y hojas brillantes
az = [lowtube([(0, 0, 0), (.02, .01, .16), (-.01, .02, .3)], .012, BARK, 5)]
az.append(lowtube([(.02, .01, .16), (.1, -.02, .26)], .007, BARK, 4))
az.append(lowtube([(-.005, .015, .22), (-.1, .03, .3)], .007, BARK, 4))
for (p, rt) in [((-.01, .02, .3), (.2, 0, 0)), ((.1, -.02, .26), (.2, .7, .3)), ((-.1, .03, .3), (-.1, -.7, 0))]:
    az.append(blossom(p, AZAHAR, POLLEN, .05, 5, .025, 7, rt))
for (p, rt) in [((.05, .0, .31), (0, .3, 0)), ((-.05, .0, .34), (0, -.3, 0))]:
    az.append(prim('sphere', loc=p, segments=8, ring_count=5, radius=1, scale=(.012, .012, .02), m=AZAHAR, smooth=True))
for k in range(9):
    lf = leaf(.1, .035, LEAF_OR, .03)
    a = k / 9 * TAU + random.uniform(-.3, .3)
    place(lf, (math.cos(a) * .02, math.sin(a) * .02, .08 + k * .025), (random.uniform(.6, 1.1), 0, a - math.pi / 2))
    az.append(lf)
join(az, 'FlorAzahar')

# Lavanda: mata con espigas
lv = []
for k in range(9):
    a = k / 9 * TAU + random.uniform(-.2, .2); tilt = random.uniform(.1, .35); hgt = random.uniform(.34, .46)
    top = (math.cos(a) * math.sin(tilt) * hgt, math.sin(a) * math.sin(tilt) * hgt, math.cos(tilt) * hgt)
    lv.append(lowtube([(0, 0, 0), (top[0] * .5, top[1] * .5, top[2] * .52), top], .0045, LAV_L, 3))
    for j in range(8):
        t = .72 + j * .04
        c = (top[0] * t / 1.0, top[1] * t, top[2] * t)
        for q in range(2):
            b = prim('cone', vertices=4, radius1=.011 * (1 - j * .05), radius2=0, depth=.022, m=LAV)
            place(b, (c[0] + (q - .5) * .008, c[1], c[2]), (random.uniform(-.3, .3), random.uniform(-.3, .3), j * .9 + q * 1.6))
            lv.append(b)
for k in range(8):
    a = k / 8 * TAU
    lf = leaf(.09, .008, LAV_L, .02); place(lf, (0, 0, .005), (1.0, 0, a)); lv.append(lf)
join(lv, 'Lavanda')

# Girasol
gs = [lowtube([(0, 0, 0), (.01, 0, .35), (.02, -.02, .62)], .012, STEM, 6)]
for (z_, a) in [(.18, 0), (.32, 2.4), (.46, 4.4)]:
    lf = leaf(.16, .07, LEAF, .05); place(lf, (0, 0, z_), (1.1, 0, a)); gs.append(lf)
head = []
disc = prim('cyl', vertices=18, radius=.07, depth=.025, m=SUN_C); displace(disc, .006, .02, 5)
head.append(disc)
head.append(prim('cone', loc=(0, 0, -.022), vertices=18, radius1=.04, radius2=.075, depth=.025, m=STEM))
for ring, (n, L) in enumerate([(16, .075), (16, .065)]):
    for k in range(n):
        p = petal(L, .018, .015, SUN_P, 2)
        for v in p.data.vertices: v.co.y += .058; v.co.z -= ring * .004
        place(p, (0, 0, .004), (0, 0, (k + ring * .5) / n * TAU))
        head.append(p)
hd = join(head, 'hd')
place(hd, (.02, -.03, .63), (1.15, 0, 0))
gs.append(hd)
join(gs, 'Girasol')

# Romero
rs = []
for k in range(8):
    a = k / 8 * TAU + random.uniform(-.3, .3); tilt = random.uniform(.25, .6); hgt = random.uniform(.26, .36)
    pts = [(0, 0, 0)]
    for j in range(1, 4):
        t = j / 3
        pts.append((math.cos(a) * math.sin(tilt) * hgt * t, math.sin(a) * math.sin(tilt) * hgt * t, math.cos(tilt) * hgt * t))
    rs.append(lowtube(pts, .006, BARK, 4))
    for j in range(12):
        t = .25 + j / 12 * .75; c = Vector(pts[-1]) * t
        n_ = prim('cone', vertices=3, radius1=.004, radius2=0, depth=.045, m=ROS)
        place(n_, tuple(c), (random.uniform(.5, 1.2), 0, random.uniform(0, TAU)))
        rs.append(n_)
    for j in range(2):
        c = Vector(pts[-1]) * (.7 + j * .2)
        rs.append(prim('ico', subdivisions=1, radius=.011, loc=tuple(c + Vector((0, 0, .01))), m=ROS_F))
join(rs, 'Romero')

# Brezo: mata baja con campanillas rosas
hs = []
for k in range(10):
    a = k / 10 * TAU + random.uniform(-.3, .3); tilt = random.uniform(.3, .75); hgt = random.uniform(.18, .26)
    top = (math.cos(a) * math.sin(tilt) * hgt, math.sin(a) * math.sin(tilt) * hgt, math.cos(tilt) * hgt)
    hs.append(lowtube([(0, 0, 0), top], .004, HEA_L, 3))
    for j in range(5):
        t = .45 + j * .11; c = (top[0] * t, top[1] * t, top[2] * t)
        b = prim('cone', vertices=5, radius1=.009, radius2=.004, depth=.014, m=HEA)
        place(b, (c[0] + random.uniform(-.01, .01), c[1] + random.uniform(-.01, .01), c[2]), (random.uniform(-.4, .4), random.uniform(-.4, .4), 0))
        hs.append(b)
mound = prim('ico', subdivisions=2, radius=.1, scale=(1.3, 1.3, .55), loc=(0, 0, .02), m=HEA_L); displace(mound, .03, .05, 7); hs.append(mound)
join(hs, 'Brezo')

# Margarita (milflores): tres margaritas y una amapola
ms = []
for (x, y, h) in [(0, 0, .3), (.06, .04, .24), (-.05, .03, .2)]:
    ms.append(lowtube([(x, y, 0), (x + .01, y, h * .6), (x, y - .01, h)], .004, STEM, 4))
    parts = []
    for k in range(13):
        p = petal(.035, .008, .004, DAISY, 2); place(p, (0, 0, 0), (0, 0, k / 13 * TAU)); parts.append(p)
    parts.append(prim('sphere', loc=(0, 0, .003), segments=8, ring_count=5, radius=1, scale=(.012, .012, .007), m=POLLEN, smooth=True))
    b = join(parts, 'mb'); place(b, (x, y - .01, h), (.35, 0, 0)); ms.append(b)
ms.append(lowtube([(-.02, -.05, 0), (-.03, -.05, .2), (-.02, -.06, .34)], .0035, STEM, 4))
cup = lathe([(.001, 0), (.02, .004), (.033, .018), (.036, .035)], POPPY, 'poppy', 10)
place(cup, (-.02, -.06, .335)); ms.append(cup)
ms.append(prim('sphere', loc=(-.02, -.06, .345), segments=6, ring_count=4, radius=.008, m=SUN_C))
for k in range(5):
    lf = leaf(.08, .015, LEAF, .02); place(lf, (0, 0, .005), (1.1, 0, k / 5 * TAU)); ms.append(lf)
join(ms, 'Margarita')

# Hierba (mata de briznas, se mece en shader)
hb = []
for k in range(7):
    a = k / 7 * TAU + random.uniform(-.3, .3); h = random.uniform(.13, .22); lean = random.uniform(.1, .35)
    vs, fs = [], []
    for j in range(4):
        t = j / 3; w = .009 * (1 - t) + .0005
        cx = math.cos(a) * lean * h * t * t; cy = math.sin(a) * lean * h * t * t
        px, py = -math.sin(a) * w, math.cos(a) * w
        vs += [(cx - px, cy - py, h * t), (cx + px, cy + py, h * t)]
    for j in range(3): fs.append((j * 2, j * 2 + 1, j * 2 + 3, j * 2 + 2))
    o = mesh_obj('bl', vs, fs, [BLADE], smooth=True); place(o, (math.cos(a) * .015, math.sin(a) * .015, 0)); hb.append(o)
join(hb, 'Hierba')

# =====================================================================================
# TARRO de miel (vidrio + miel interior + tapa de tela + cuerda + etiqueta)
# =====================================================================================
jp = [(.001, 0), (.055, 0), (.066, .008), (.07, .03), (.07, .16), (.064, .19), (.05, .205), (.047, .215), (.049, .232), (.047, .24)]
ip = [(r - .005 if r > .01 else r, z + (.005 if i == 0 else 0)) for i, (r, z) in enumerate(jp)]
outer = lathe(jp, GLASS, 'jo', 28)
tj = [outer]
tj.append(lathe([(.063, .045), (.0715, .045), (.0715, .13), (.063, .13)], LABEL, 'lbl', 28))
lid = prim('cyl', loc=(0, 0, .245), vertices=24, radius=.052, depth=.012, m=CLOTH)
tj.append(lid)
cl = prim('circle', loc=(0, 0, .251), vertices=24, radius=.09, fill_type='NGON', m=CLOTH)
for v in cl.data.vertices:
    rr = math.hypot(v.co.x, v.co.y)
    if rr > .05:
        k = (rr - .05) / .04; ang = math.atan2(v.co.y, v.co.x)
        v.co.x *= .58 + .02 * math.sin(ang * 6); v.co.y *= .58 + .02 * math.sin(ang * 6); v.co.z -= k * .05 * (1 + .25 * math.sin(ang * 6))
tj.append(subsurf(cl, 1))
tj.append(prim('torus', loc=(0, 0, .226), major_radius=.052, minor_radius=.0035, major_segments=24, minor_segments=4, m=TWINE))
tj.append(lowtube([(.05, -.01, .226), (.07, -.02, .2), (.075, -.018, .17)], .003, TWINE, 4))
tj.append(lowtube([(.05, .01, .226), (.066, .03, .19), (.062, .04, .16)], .003, TWINE, 4))
join(tj, 'Tarro')
hm = lathe([(.001, .006), (.06, .006), (.064, .03), (.064, .16), (.001, .16)], HONEY, 'hm', 24)
bm_ = bmesh.new(); bm_.from_mesh(hm.data); bmesh.ops.contextual_create(bm_, geom=[v for v in bm_.verts if abs(v.co.z - .16) < 1e-4]); bm_.to_mesh(hm.data); bm_.free()
join([hm], 'Tarro miel', origin=(0, 0, .006))

# Caja de fruta (para apoyar el tarro)
cj = []
for sy in (-1, 1):
    for k in range(3): cj.append(bx((0, sy * .17, .035 + k * .075), (.42, .018, .055), WOOD_L, .004))
for sx in (-1, 1):
    for k in range(3): cj.append(bx((sx * .2, 0, .035 + k * .075), (.018, .32, .055), WOOD_L, .004))
    for sy in (-1, 1): cj.append(bx((sx * .2, sy * .17, .11), (.03, .03, .22), WOOD, .004))
for k in range(5): cj.append(bx((-.16 + k * .08, 0, .215), (.07, .34, .012), WOOD_L, .003))
join(cj, 'Caja')

# =====================================================================================
# AHUMADOR y APICULTOR
# =====================================================================================
ah = [lathe([(.001, 0), (.055, 0), (.058, .006), (.058, .19), (.055, .2)], STEEL, 'ahb', 20)]
ah.append(lathe([(.056, .2), (.058, .21), (.045, .25), (.02, .27), (.018, .29)], STEEL, 'aht', 20))
ah.append(lowtube([(0, 0, .285), (0, -.02, .31), (0, -.05, .315)], .016, STEEL, 8))
for k in range(12):
    a = k / 12 * TAU
    ah.append(prim('cube', loc=(math.cos(a) * .066, math.sin(a) * .066, .1), scale=(.004, .004, .085), m=STEEL))
for zz in (.03, .17): ah.append(prim('torus', loc=(0, 0, zz), major_radius=.066, minor_radius=.004, major_segments=20, minor_segments=4, m=STEEL))
for dz in (0, .038):
    ah.append(bx((.105 + dz, 0, .12), (.012, .07, .2), WOOD, .003))
ah.append(bx((.123, 0, .11), (.03, .06, .15), LEATHER, .008))
join(ah, 'Ahumador')

ap = []
for sx in (-1, 1):
    ap.append(lowtube([(sx * .09, 0, .08), (sx * .095, .01, .45), (sx * .1, 0, .8)], .075, SUIT, 8))
    ap.append(bx((sx * .09, -.03, .05), (.12, .22, .1), SUIT, .03, 2))                    # botas
ap.append(prim('sphere', loc=(0, 0, 1.05), segments=16, ring_count=10, radius=1, scale=(.2, .15, .33), m=SUIT, smooth=True))
ap.append(prim('cyl', loc=(0, 0, .82), vertices=16, radius=.18, depth=.05, m=WOOD_D))   # cinturón
for sx in (-1, 1):
    arm = lowtube([(sx * .19, 0, 1.25), (sx * .28, -.05, 1.05), (sx * .22, -.2, .92)], .06, SUIT, 7); ap.append(arm)
    ap.append(prim('sphere', loc=(sx * .21, -.24, .92), segments=10, ring_count=6, radius=.055, m=GLOVE, smooth=True))
ap.append(prim('sphere', loc=(0, -.01, 1.46), segments=14, ring_count=9, radius=.12, m=SKIN, smooth=True))
ap.append(prim('cyl', loc=(0, 0, 1.58), vertices=24, radius=.28, depth=.015, m=SUIT))  # ala del sombrero
ap.append(prim('cyl', loc=(0, 0, 1.63), vertices=20, radius=.13, depth=.1, m=SUIT))
veil = lathe([(.25, 1.575), (.2, 1.45), (.17, 1.33), (.15, 1.3)], VEIL, 'veil', 20); ap.append(veil)
ap.append(prim('cube', loc=(0, -.145, 1.1), scale=(.008, .01, .2), m=GLOVE))              # cremallera
join(ap, 'Apicultor')

# =====================================================================================
# LOMA (isla flotante). Altura = h(x,z) en coordenadas three (z = -y de Blender)
# =====================================================================================
def H(x, z):
    r = math.hypot(x, z)
    h = .85 * math.exp(-((x + .2) ** 2 / 10 + (z + .9) ** 2 / 7)) + .1 * math.sin(.9 * x + .4) * math.cos(.7 * z) + .05 * math.sin(1.7 * x - 1.1 * z)
    return h
def RIM(a): return 6.3 + .25 * math.sin(3 * a) + .15 * math.sin(5 * a + 1)
RINGS, SEG = 18, 60
vs, fs, fm = [(0, 0, H(0, 0))], [], []
for i in range(1, RINGS + 1):
    t = i / RINGS
    for k in range(SEG):
        a = k / SEG * TAU; R = RIM(a) * t; x, z = R * math.cos(a), R * math.sin(a)
        dz = -.22 * max(0, (t - .82) / .18) ** 2
        vs.append((x, -z, H(x, z) + dz))
for k in range(SEG): fs.append((0, 1 + k, 1 + (k + 1) % SEG)); fm.append(0)
for i in range(RINGS - 1):
    for k in range(SEG):
        a = 1 + i * SEG + k; b = 1 + i * SEG + (k + 1) % SEG
        fs.append((a, a + SEG, b + SEG, b)); fm.append(0)
# faldón de tierra y roca
top0 = 1 + (RINGS - 1) * SEG
LAY = [(.02, 1.0, 1), (.18, .995, 1), (.4, .97, 2), (.75, .9, 2), (1.2, .76, 3), (1.7, .56, 3), (2.2, .34, 3), (2.6, .16, 3)]
prev = [top0 + k for k in range(SEG)]
for (dep, sc, mi) in LAY:
    cur = []
    for k in range(SEG):
        a = k / SEG * TAU; R = RIM(a) * sc * (1 + (random.uniform(-.04, .04) if dep > .3 else 0))
        x, z = R * math.cos(a), R * math.sin(a)
        base = H(RIM(a) * math.cos(a), RIM(a) * math.sin(a)) - .22
        cur.append(len(vs)); vs.append((x, -z, base - dep - (random.uniform(0, .12) if dep > .3 else 0)))
    for k in range(SEG):
        n = (k + 1) % SEG
        fs.append((prev[k], cur[k], cur[n], prev[n])); fm.append(mi)
    prev = cur
tip = len(vs); vs.append((0, 0, -3.4))
for k in range(SEG): fs.append((prev[k], tip, prev[(k + 1) % SEG])); fm.append(3)
loma = mesh_obj('Loma', vs, fs, [GRASS, SOIL, SOIL_D, ROCK], fm, smooth=True)
_b = bmesh.new(); _b.from_mesh(loma.data); bmesh.ops.recalc_face_normals(_b, faces=_b.faces); _b.to_mesh(loma.data); _b.free()
bpy.ops.object.select_all(action='DESELECT'); loma.select_set(True); C.view_layer.objects.active = loma
# piedras incrustadas en el faldón
rk = [loma]
for k in range(16):
    a = random.uniform(0, TAU); dep = random.uniform(.5, 1.8); sc = 1 - dep * .22
    R = RIM(a) * sc + .02
    p = prim('ico', subdivisions=1, radius=random.uniform(.18, .38), loc=(R * math.cos(a), -R * math.sin(a), H(RIM(a) * math.cos(a), RIM(a) * math.sin(a)) - .22 - dep), m=ROCK)
    displace(p, .08, .3, 20 + k); rk.append(p)
for k in range(9):  # raíces colgando
    a = random.uniform(0, TAU); R = RIM(a) * .99
    x, y = R * math.cos(a), -R * math.sin(a); zt = H(R * math.cos(a), R * math.sin(a)) - .25
    rk.append(lowtube([(x, y, zt), (x * 1.01, y * 1.01, zt - .25), (x * .99, y * .99, zt - .5 - random.uniform(0, .3))], .025, BARK, 4))
join(rk, 'Loma')

# Piedra suelta
pd = prim('ico', subdivisions=2, radius=.18, scale=(1.2, 1, .6), loc=(0, 0, .05), m=STONE); displace(pd, .05, .2, 31)
bpy.ops.object.shade_smooth(); join([pd], 'Piedra')

# =====================================================================================
# NARANJO
# =====================================================================================
tr = [lowtube([(0, 0, -.1), (.05, .02, .6), (0, 0, 1.1)], .1, BARK, 8)]
for (a, l) in [(.3, .7), (2.2, .6), (4.1, .65), (5.3, .5)]:
    tr.append(lowtube([(0, 0, .95), (math.cos(a) * l * .5, math.sin(a) * l * .5, 1.25), (math.cos(a) * l, math.sin(a) * l, 1.55)], .045, BARK, 5))
for k, (x, y, z, r) in enumerate([(0, 0, 1.75, .75), (.55, .2, 1.55, .5), (-.5, -.1, 1.6, .55), (.1, -.5, 1.55, .5), (-.15, .5, 1.62, .5), (.05, .05, 2.2, .5)]):
    c = prim('ico', subdivisions=2, radius=r, loc=(x, y, z), scale=(1, 1, .82), m=LEAF_OR); displace(c, .12, .25, 40 + k)
    bpy.ops.object.shade_smooth(); tr.append(c)
for k in range(18):
    a = random.uniform(0, TAU); el = random.uniform(-.2, .9); r = .78
    p = (math.cos(a) * math.cos(el) * r * 1.05, math.sin(a) * math.cos(el) * r * 1.05, 1.72 + math.sin(el) * r * .8)
    tr.append(prim('sphere', loc=p, segments=8, ring_count=5, radius=.065, m=ORANGE, smooth=True))
for k in range(26):
    a = random.uniform(0, TAU); el = random.uniform(-.1, 1.1); r = .82
    p = (math.cos(a) * math.cos(el) * r, math.sin(a) * math.cos(el) * r, 1.74 + math.sin(el) * r * .82)
    tr.append(prim('ico', subdivisions=0, radius=.03, loc=p, m=AZAHAR))
join(tr, 'Arbol naranjo')

# =====================================================================================
# MONEDA, MARIPOSA, VALLA, NUBE, CARTEL
# =====================================================================================
mo = [prim('cyl', rot=(math.pi / 2, 0, 0), vertices=28, radius=.09, depth=.016, m=GOLD)]
bevel(mo[0], .004, 1)
for s in (-1, 1):
    mo.append(prim('torus', loc=(0, s * .008, 0), rot=(math.pi / 2, 0, 0), major_radius=.08, minor_radius=.005, major_segments=28, minor_segments=4, m=GOLD))
    hx = prim('cyl', loc=(0, s * .009, 0), rot=(math.pi / 2, 0, math.pi / 6), vertices=6, radius=.042, depth=.006, m=GOLD); mo.append(hx)
join(mo, 'Moneda')

mb = [prim('sphere', segments=8, ring_count=6, radius=1, scale=(.008, .05, .008), m=BUT_K, smooth=True),
      prim('sphere', loc=(0, -.05, .002), segments=8, ring_count=5, radius=.01, m=BUT_K, smooth=True)]
for s in (-1, 1): mb.append(lowtube([(s * .003, -.055, .005), (s * .015, -.085, .02)], .0015, BUT_K, 3))
join(mb, 'Mariposa')
# ala de mariposa (lado +X, bisagra en el origen): abanico con borde oscuro
def but_wing():
    outline = []
    for k in range(18):
        t = k / 17; a = -1.9 + t * 2.9
        r = (.085 if a > -.35 else .065) * (1 + .15 * math.sin(t * math.pi * 3))
        outline.append((math.cos(a) * r * 1.1, math.sin(a) * r, 0))
    vs = [(0.002, 0, 0)] + outline + [(p[0] * .72, p[1] * .72, 0) for p in outline]
    n = len(outline); fs = []; fm_ = []
    for k in range(n - 1):
        fs.append((0, 1 + n + k, 1 + n + k + 1)); fm_.append(0)
        fs.append((1 + n + k, 1 + k, 1 + k + 1, 1 + n + k + 1)); fm_.append(1)
    return mesh_obj('AlaMariposa', vs, fs, [BUT_O, BUT_K], fm_)
bw = but_wing()
for v in bw.data.vertices: v.co.x, v.co.y = v.co.x, -v.co.y  # borde de ataque hacia delante (-Y)
join([bw], 'AlaMariposa')

vl = []
for sx in (-1, 1):
    p = bx((sx * .5, 0, .22), (.07, .07, .5), WOOD, .01, 2); vl.append(p)
    vl.append(prim('cone', loc=(sx * .5, 0, .5), vertices=4, radius1=.05, radius2=.0, depth=.06, rot=(0, 0, math.pi / 4), m=WOOD))
for zz in (.16, .36):
    r_ = bx((0, 0, zz), (1.08, .04, .07), WOOD, .008, 1)
    for v in r_.data.vertices: v.co.z += math.sin(v.co.x * 3) * .008
    vl.append(r_)
join(vl, 'Valla')

nb = []
for (x, y, z, r) in [(0, 0, 0, .55), (.55, .1, -.08, .42), (-.55, -.05, -.1, .4), (.25, -.1, .25, .38), (-.25, .1, .2, .36), (.95, 0, -.15, .28), (-.9, 0, -.18, .26)]:
    c = prim('ico', subdivisions=2, radius=r, loc=(x, y, z), scale=(1, .8, .85), m=CLOUD); bpy.ops.object.shade_smooth(); nb.append(c)
join(nb, 'Nube')

cs_ = [bx((0, 0, .2), (.035, .035, .4), WOOD, .006), bx((0, -.02, .36), (.3, .02, .16), SIGN, .01, 2)]
join(cs_, 'Cartel')

ASSETS = ['Colmena', 'Marco', 'Panal', 'Celda miel', 'Abeja', 'Ala', 'FlorAzahar', 'Lavanda', 'Girasol', 'Romero', 'Brezo', 'Margarita',
          'Hierba', 'Tarro', 'Tarro miel', 'Caja', 'Ahumador', 'Apicultor', 'Loma', 'Piedra', 'Arbol naranjo', 'Moneda', 'Mariposa',
          'AlaMariposa', 'Valla', 'Nube', 'Cartel']
keep_only(ASSETS)
for n in ASSETS:  # sombreado suave por ángulo: comparte vértices en caras planas (GLB mucho más ligero)
    o = bpy.data.objects[n]
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); C.view_layer.objects.active = o
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(50 if n not in ('Loma', 'Nube', 'Arbol naranjo') else 80))
bpy.ops.object.select_all(action='DESELECT')
for n in ASSETS: bpy.data.objects[n].select_set(True)
bpy.ops.export_scene.gltf(filepath=ROOT + '/glb/colmena.glb', export_format='GLB', use_selection=True, export_apply=True,
                          export_yup=True, export_materials='EXPORT', export_texcoords=False)
bpy.ops.wm.save_as_mainfile(filepath=ROOT + '/blend/colmena.blend')
print('GLB', os.path.getsize(ROOT + '/glb/colmena.glb'))
if '--noicon' in sys.argv: sys.exit(0)

# =====================================================================================
# ICONO: trozo de panal con miel goteando + abeja, luz cálida de tarde
# =====================================================================================
for n in ASSETS: bpy.data.objects[n].hide_render = True
dx, dz = R_CELL * math.sqrt(3), R_CELL * 1.5
cells = []
for row in range(-3, 4):
    for col in range(-4, 5):
        x = col * dx + (dx / 2 if row % 2 else 0); z = -row * dz
        if (x / 1.0) ** 2 / .36 ** 2 + (z) ** 2 / .3 ** 2 > 1: continue
        cells.append((x, z))
grp = []
for (x, z) in cells:
    c = bpy.data.objects['Panal'].copy(); C.collection.objects.link(c); c.hide_render = False; c.location = (x, 0, z); grp.append(c)
    if random.random() < .82:
        h = bpy.data.objects['Celda miel'].copy(); C.collection.objects.link(h); h.hide_render = False; h.location = (x, 0, z); grp.append(h)
HON_I = pmat('Miel icono', '#d98200', .05, trans=.3, ior=1.5, coat=1., coat_r=.02, emit='#c86a00', emit_str=.45)
for g in grp:
    if g.data and g.data.materials and g.data.materials[0].name == 'Miel': g.data = g.data.copy(); g.data.materials[0] = HON_I
drip = lathe([(.0, 0), (.014, .003), (.017, .02), (.011, .05), (.007, .085), (.005, .12)], HON_I, 'drip', 16)
place(drip, (-.06, -.035, -.375)); grp.append(drip)
drop = prim('sphere', loc=(-.06, -.035, -.405), segments=16, ring_count=10, radius=1, scale=(.021, .021, .028), m=HON_I, smooth=True)
for v in drop.data.vertices:
    if v.co.z > 0: v.co.x *= 1 - v.co.z / .04; v.co.y *= 1 - v.co.z / .04
grp.append(drop)
emp = bpy.data.objects.new('comb', None); C.collection.objects.link(emp)
for g in grp: g.parent = emp
emp.rotation_euler = (0, 0, -.28); emp.location = (-.06, 0, .03)
bee = bpy.data.objects['Abeja'].copy(); C.collection.objects.link(bee); bee.hide_render = False
wg = bpy.data.objects['Ala'].copy(); C.collection.objects.link(wg); wg.hide_render = False
bee.scale = (3.1, 3.1, 3.1); bee.location = (.2, -.3, .2); bee.rotation_euler = (.3, -.25, -1.05)
wg.parent = bee; wg.location = (0, 0, .016); wg.scale = (1, 1, 1.3)

def icon(path, bg, cam_loc, target, lens, samples, lights):
    sc = C.scene
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = hexrgb(bg)
    w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0
    cam = bpy.data.objects.new('IconCam', bpy.data.cameras.new('IconCam')); sc.collection.objects.link(cam)
    cam.data.lens = lens; cam.location = cam_loc
    cam.rotation_euler = (Vector(target) - Vector(cam_loc)).to_track_quat('-Z', 'Y').to_euler(); sc.camera = cam
    for (kind, loc, energy, color, size) in lights:
        L = bpy.data.lights.new('L', kind); L.energy = energy; L.color = hexrgb(color)[:3]
        if kind == 'AREA': L.size = size
        else: L.angle = size
        lo = bpy.data.objects.new('L', L); sc.collection.objects.link(lo); lo.location = loc
        lo.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.render.engine = 'CYCLES'; sc.cycles.samples = samples; sc.cycles.device = 'CPU'; sc.cycles.use_denoising = True
    sc.render.resolution_x = sc.render.resolution_y = 256; sc.render.film_transparent = False
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'; sc.view_settings.exposure = -.35
    sc.render.image_settings.file_format = 'PNG'; sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
# fondo: una lámina del color de la app detrás para que la sombra dé volumen
bgp = prim('plane', size=6, loc=(0, .6, 0), rot=(math.pi / 2, 0, 0), m=pmat('Fondo icono', '#f6e7b0', 1.))
icon(ROOT + '/renders/colmena.png', '#f6e7b0', (.3, -1.75, .22), (.03, 0, -.03), 60, 56,
     [('SUN', (-2, -2.5, 3), 2.2, '#ffcf8a', .12), ('AREA', (2, -2, .3), 40, '#fff1c9', 2), ('AREA', (.5, .2, 2.5), 70, '#ffb347', 1.5)])
print('OK colmena')
