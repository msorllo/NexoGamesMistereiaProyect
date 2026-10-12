"""CAIRN (29) · piedras de río, piedras raras, farol de piedra, bambú, helecho, musgo, orilla y hoja.
Genera blender/glb/cairn.glb, blender/blend/cairn.blend y blender/renders/cairn.png (icono).
Convención: cada piedra tiene el origen en el centro de su base (z=0 abajo) → en Three.js y=0 es el apoyo.
"""
import sys, os, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
from blib import *
import bmesh
from mathutils import Vector, noise

reset(); random.seed(29)

# ---------------------------------------------------------------- materiales
def M(name, color, rough=.5, metal=0., emit=None, es=1., alpha=1.):
    return mat(name, color, rough, metal, emit, es, alpha)

# ---------------------------------------------------------------- helpers propios
def mesh_obj(bm, name, m, smooth=True):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); C.collection.objects.link(o)
    if m: o.data.materials.append(m)
    for p in o.data.polygons: p.use_smooth = smooth
    return o


def tube(points, radius, m, sides=6, name='tube', r_end=None, cap=True):
    """Tubo ligero (bmesh) a lo largo de una polilínea; radio lineal de radius a r_end."""
    pts = [Vector(p) for p in points]; n = len(pts)
    bm = bmesh.new(); rings = []
    ref = Vector((0, 0, 1))
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        if abs(t.dot(ref)) > .95: ref = Vector((1, 0, 0))
        u = t.cross(ref).normalized(); w = t.cross(u).normalized()
        rr = radius if r_end is None else radius + (r_end - radius) * i / (n - 1)
        rings.append([bm.verts.new(p + (u * math.cos(a) + w * math.sin(a)) * rr) for a in [k / sides * math.tau for k in range(sides)]])
    for a, b in zip(rings, rings[1:]):
        for k in range(sides): bm.faces.new((a[k], a[(k + 1) % sides], b[(k + 1) % sides], b[k]))
    if cap: bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1])
    return mesh_obj(bm, name, m)

def base_origin(o):
    """Centra en XY y pone la base (z mínima) en z=0."""
    vs = [v.co for v in o.data.vertices]
    minx = min(v.x for v in vs); maxx = max(v.x for v in vs)
    miny = min(v.y for v in vs); maxy = max(v.y for v in vs); minz = min(v.z for v in vs)
    off = Vector(((minx + maxx) / 2, (miny + maxy) / 2, minz))
    for v in o.data.vertices: v.co -= off
    return o

def fbm(p, oct=3):
    return noise.fractal(p, .55, 2.0, oct, noise_basis='PERLIN_ORIGINAL')

def rock(name, dims, seed, m, subdiv=4, decim=.42, amp=.1, freq=1.3, flat=(.55, .5), squish=.22, egg=0., pits=0., bumps=0.,
         facets=0, smooth_it=2, shade=True):
    """Canto rodado: icoesfera deformada con ruido, aplanada arriba y abajo para poder apilarse."""
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=1.0)
    off = Vector((seed * 7.31, seed * 3.17, seed * 5.71))
    rnd = random.Random(seed)
    planes = []
    for k in range(facets):
        n = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-.6, .6))).normalized()
        planes.append((n, rnd.uniform(.62, .86)))
    for v in bm.verts:
        d = v.co.normalized()
        r = 1 + amp * fbm(d * freq + off)
        if bumps: r += bumps * max(0, noise.noise(d * 5.5 + off)) ** .7
        if pits:
            dist = noise.voronoi(d * 3.2 + off)[0][0]
            r -= pits * max(0., .42 - dist) ** 1.3 * 3
        p = d * r
        for n, dd in planes:
            s = p.dot(n)
            if s > dd: p = p - n * (s - dd) * .92
        p = Vector((p.x * dims[0], p.y * dims[1], p.z * dims[2]))
        if egg: p.x *= 1 + egg * d.x
        t = dims[2] * flat[0]; b = -dims[2] * flat[1]
        if p.z > t: p.z = t + (p.z - t) * squish
        if p.z < b: p.z = b + (p.z - b) * squish
        v.co = p
    if smooth_it:
        bmesh.ops.smooth_vert(bm, verts=bm.verts, factor=.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
        if smooth_it > 1: bmesh.ops.smooth_vert(bm, verts=bm.verts, factor=.35, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    o = mesh_obj(bm, name, m, shade)
    if decim and decim < 1 and subdiv >= 4:
        md = o.modifiers.new('dc', 'DECIMATE'); md.ratio = decim
        C.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier='dc')
    return base_origin(o)

def finish(objs, name):
    """Une, pone origen en el centro de la base (z=0)."""
    o = join(objs, name, (0, 0, 0))
    return base_origin(o)

def hex_cone(loc, r, h, m, rot=(0, 0, 0)):
    return prim('cone', loc=loc, rot=rot, vertices=6, radius1=r, radius2=0, depth=h, m=m)

# ================================================================ PIEDRAS COMUNES
SL = M('Piedra 1', '#4b5157', .34); GR = M('Piedra 2', '#8d8c86', .4); SA = M('Piedra 3', '#8b7a66', .45)
GG = M('Piedra 4', '#6c7466', .36); BA = M('Piedra 5', '#3a3d40', .3); BG = M('Piedra 6', '#697781', .35)
QZ = M('Piedra 7', '#b9b2a2', .38); SB = M('Piedra 8', '#565c5e', .33)
rock('Piedra1', (.46, .34, .11), 1, SL, amp=.07, freq=1.1, flat=(.4, .45), squish=.15, egg=.08)
rock('Piedra2', (.32, .29, .19), 2, GR, amp=.09, freq=1.4, flat=(.62, .55), squish=.2)
rock('Piedra3', (.5, .25, .14), 3, SA, amp=.08, freq=1.2, flat=(.5, .45), squish=.2, egg=.12)
rock('Piedra4', (.38, .36, .12), 4, GG, amp=.06, freq=1.0, flat=(.45, .45), squish=.16)
rock('Piedra5', (.34, .25, .17), 5, BA, amp=.1, freq=1.5, flat=(.6, .5), squish=.22, egg=.18)
rock('Piedra6', (.44, .38, .1), 6, BG, amp=.05, freq=.9, flat=(.35, .35), squish=.2)
rock('Piedra7', (.27, .24, .16), 7, QZ, amp=.11, freq=1.6, flat=(.6, .55), squish=.24)
rock('Piedra8', (.55, .28, .1), 8, SB, amp=.07, freq=1.1, flat=(.4, .45), squish=.15, egg=-.1)

# ================================================================ PIEDRAS RARAS
rock('Jade', (.33, .27, .13), 11, M('Jade', '#3f8f63', .18), amp=.05, freq=1.0, flat=(.5, .5), squish=.25)
rock('Obsidiana', (.34, .28, .16), 12, M('Obsidiana', '#0d0e12', .06), subdiv=3, amp=.06, facets=11, flat=(.62, .6),
     squish=.1, smooth_it=0, shade=False)
rock('Cuarzo', (.3, .26, .15), 13, M('Cuarzo rosa', '#e5a9b6', .22), subdiv=4, amp=.06, facets=6, flat=(.58, .55),
     squish=.18, smooth_it=1)
rock('Meteorito', (.31, .27, .16), 14, M('Meteorito', '#3b3632', .42, .65), amp=.12, freq=1.8, pits=.09, flat=(.58, .55), squish=.25, smooth_it=1)
rock('Lapis', (.33, .27, .13), 15, M('Lapislázuli', '#1f3a8a', .28), amp=.05, facets=5, flat=(.5, .5), squish=.2, smooth_it=2)
rock('Turquesa', (.3, .27, .14), 16, M('Turquesa', '#3fb2a7', .4), amp=.07, bumps=.07, flat=(.55, .5), squish=.22)
rock('Malaquita', (.35, .27, .13), 17, M('Malaquita', '#1f7a4c', .22), amp=.06, bumps=.05, flat=(.5, .5), squish=.2)
rock('Opalo', (.31, .25, .13), 18, M('Ópalo', '#e8eef0', .12), amp=.04, flat=(.5, .5), squish=.25)

# Ámbar con insecto dentro
amb = rock('Ambar_s', (.28, .23, .15), 19, M('Ámbar', '#d9831c', .12), amp=.09, freq=1.2, flat=(.6, .55), squish=.25)
BUG = M('Insecto', '#2b1a0d', .5)
bug = [prim('sphere', loc=(0, 0, .15), segments=10, ring_count=6, radius=.022, scale=(2.2, 1, 1), m=BUG, smooth=True),
       prim('sphere', loc=(.055, 0, .152), segments=8, ring_count=5, radius=.014, m=BUG, smooth=True)]
for s in (1, -1):
    bug.append(prim('sphere', loc=(-.01, s * .04, .165), segments=8, ring_count=4, radius=.035, scale=(1, .45, .08),
                    rot=(0, 0, s * .5), m=M('Ala', '#6b4a2a', .3), smooth=True))
    for k in range(3):
        bug.append(tube([(.02 - k * .02, s * .01, .15), (.02 - k * .025, s * .05, .13), (.01 - k * .03, s * .06, .12)], .003, BUG, 3))
finish([amb] + bug, 'Ambar')

# Geoda: cáscara rugosa abierta arriba, anillo de calcedonia y cristales morados
GEO_OUT = M('Geoda corteza', '#7a6f63', .8); GEO_BAND = M('Geoda calcedonia', '#cfc6d8', .35)
GEO_CRY = M('Geoda cristal', '#8a4fd8', .08, emit='#8d45ff', es=2.2)
prof = [(.01, 0), (.18, .005), (.28, .05), (.33, .13), (.33, .21), (.3, .27), (.27, .28), (.225, .28), (.2, .22), (.16, .14), (.08, .1), (.01, .095)]
shell = lathe(prof, GEO_OUT, 'geoshell', steps=28)
for v in shell.data.vertices:
    d = Vector((v.co.x, v.co.y, v.co.z * .6)).normalized()
    k = 1 + .09 * fbm(d * 2.2 + Vector((3, 1, 2)))
    if v.co.z < .27: v.co.x *= k; v.co.y *= k
band = prim('torus', loc=(0, 0, .277), major_radius=.25, minor_radius=.028, major_segments=24, minor_segments=5, scale=(1, 1, .45), m=GEO_BAND, smooth=True)
cr = []
rg = random.Random(7)
for k in range(34):
    a = rg.uniform(0, math.tau); rr = rg.uniform(.02, .19)
    x, y = rr * math.cos(a), rr * math.sin(a)
    zb = .1 + (rr / .2) ** 2 * .12
    h = rg.uniform(.07, .13)
    tilt = (rr / .2) * .9
    c = prim('cone', loc=(0, 0, 0), vertices=6, radius1=rg.uniform(.018, .03), radius2=0, depth=h, m=GEO_CRY)
    c.rotation_euler = (tilt * math.sin(a), -tilt * math.cos(a), rg.uniform(0, 1))
    # colocar la base del cristal en la pared interior
    c.location = (x - math.sin(tilt) * math.cos(a) * h * .3, y - math.sin(tilt) * math.sin(a) * h * .3, zb + h * .45 * math.cos(tilt))
    cr.append(c)
bpy.ops.object.select_all(action='DESELECT')
for c in cr: c.select_set(True)
C.view_layer.objects.active = cr[0]; bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for c in cr:
    for v in c.data.vertices:
        if v.co.z > .262: v.co.z = .262   # que ningún cristal sobresalga del borde
finish([shell, band] + cr, 'Geoda')

# Pirita: racimo de cubos metálicos sobre matriz gris
PYR = M('Pirita', '#c9a64a', .22, 1.); MAT = M('Matriz', '#6f6a62', .8)
base = rock('pir_b', (.3, .26, .09), 21, MAT, amp=.08, flat=(.5, .5), squish=.3)
cubes = [base]
rp = random.Random(4)
spots = [(0, 0, .12, .1), (.13, .06, .09, .08), (-.12, -.04, .1, .085), (.05, -.12, .08, .07), (-.06, .12, .085, .07), (.18, -.07, .06, .05), (-.19, .08, .06, .05)]
for (x, y, z, s) in spots:
    c = bevel(prim('cube', loc=(x, y, z + s * .2), rot=(rp.uniform(-.15, .15), rp.uniform(-.15, .15), rp.uniform(0, 1.5)), scale=(s, s, s), m=PYR), .006, 1)
    cubes.append(c)
finish(cubes, 'Pirita')

# Fósil: laja con amonites en relieve arriba
FOS = M('Fósil laja', '#b3a58a', .7); SHELL = M('Fósil concha', '#d9c9a3', .45)
slab = rock('fos_s', (.36, .3, .1), 23, FOS, amp=.05, flat=(.45, .45), squish=.18)
top = max(v.co.z for v in slab.data.vertices)
pts = []
for i in range(150):
    a = i / 150 * 4.4 * math.pi; r = .012 * math.exp(.2 * a)
    pts.append((r * math.cos(a), r * math.sin(a), top - .005))
spiral = tube(pts[::2], .004, SHELL, 6, 'amm', r_end=.02)
for v in spiral.data.vertices: v.co.z = min(v.co.z, top + .018)
ribs = []
for i in range(20, 150, 10):
    a = i / 150 * 4.4 * math.pi; r = .012 * math.exp(.2 * a)
    ribs.append(prim('cube', loc=(r * math.cos(a), r * math.sin(a), top + .008), rot=(0, 0, a), scale=(.004, .018 + r * .1, .008), m=SHELL))
finish([slab, spiral] + ribs, 'Fosil')

# ================================================================ ESCENARIO
# Roca base: bloque grande de la orilla, plano arriba (tapa ≈ 0.5 sobre el agua)
rb = rock('Roca base', (1.25, 1.0, .75), 31, M('Roca base', '#5d615d', .55), subdiv=5, decim=.45, amp=.1, freq=1.1, flat=(.25, .9), squish=.08, egg=.06, smooth_it=2)
# musgo en la base de la roca (queda en la línea de agua)
MOSS = M('Musgo', '#5c7a3c', .9)

# Orilla (primer plano): terreno que baja al agua + guijarros
SAND = M('Arena húmeda', '#6d6457', .75); GRAV = M('Grava', '#857c6e', .9); SOIL = M('Tierra musgo', '#4e5e3a', .95)
bm = bmesh.new()
NX, NY = 56, 16; W, D = 22., 6.
vs = []
for j in range(NY + 1):
    row = []
    for i in range(NX + 1):
        x = -W / 2 + W * i / NX; y = -D * j / NY          # y blender 0 → -6 (hacia la cámara)
        t = j / NY
        h = -.55 + .95 * (1 - (1 - t) ** 2.2) + .12 * fbm(Vector((x * .35, y * .35, 1.3))) + .04 * noise.noise(Vector((x * 2.1, y * 2.1, 4)))
        row.append(bm.verts.new((x, y, h)))
    vs.append(row)
for j in range(NY):
    for i in range(NX):
        f = bm.faces.new((vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]))
        zc = sum(v.co.z for v in f.verts) / 4
        n = noise.noise(Vector((f.calc_center_median().x * .6, f.calc_center_median().y * .6, 7)))
        f.material_index = 0 if zc < .06 else (2 if zc + n * .15 > .3 else 1)
HZ = [[v.co.z for v in row] for row in vs]
orilla = mesh_obj(bm, 'orilla_t', None)
for mm in (SAND, GRAV, SOIL): orilla.data.materials.append(mm)
def terrain_h(x, y):
    j = min(NY - 1e-6, max(0, -y / D * NY)); i = min(NX - 1e-6, max(0, (x + W / 2) / W * NX))
    j0, i0 = int(j), int(i); fj, fi = j - j0, i - i0
    z = lambda a, b: HZ[a][b]
    return (z(j0, i0) * (1 - fi) + z(j0, i0 + 1) * fi) * (1 - fj) + (z(j0 + 1, i0) * (1 - fi) + z(j0 + 1, i0 + 1) * fi) * fj
peb = [orilla]
PEB = [M('Guijarro claro', '#9b958a', .5), M('Guijarro oscuro', '#4a4d4f', .4), M('Guijarro ocre', '#8a7458', .55)]
rq = random.Random(11)
for k in range(38):
    x = rq.uniform(-9, 9); y = -rq.uniform(.3, 5.6)
    if abs(x) < 1.6 and y > -2.2: continue
    s = rq.uniform(.05, .16)
    g = rock('g%d' % k, (s * rq.uniform(1, 1.5), s, s * rq.uniform(.45, .7)), 100 + k, PEB[k % 3], subdiv=2, amp=.1, flat=(.5, .5), squish=.4, smooth_it=1)
    g.location = (x, y, terrain_h(x, y) - s * .12); g.rotation_euler = (0, 0, rq.uniform(0, 6.3))
    peb.append(g)
bpy.ops.object.select_all(action='DESELECT')
for g in peb[1:]: g.select_set(True)
C.view_layer.objects.active = peb[1]; bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
# matas de musgo en la orilla
for k in range(10):
    x = rq.uniform(-10, 10); y = -rq.uniform(2.5, 5.8)
    s = rq.uniform(.15, .35)
    mo = rock('mo%d' % k, (s * 1.3, s, s * .35), 200 + k, MOSS, subdiv=2, amp=.2, freq=2, flat=(.6, .2), squish=.5, smooth_it=1)
    mo.location = (x, y, terrain_h(x, y) - .03); peb.append(mo)
    mo.select_set(True)
C.view_layer.objects.active = peb[-1]; bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
o = join(peb, 'Orilla', (0, 0, 0))

# Farol de piedra (tōrō, estilo kasuga)
ST = M('Piedra farol', '#8b8d84', .85); LAMP = M('Luz farol', '#ffd29a', .4, emit='#ffb865', es=6.0); PAPER = M('Papel farol', '#f2e2c4', .6, emit='#ffb865', es=1.6)
tp = []
tp.append(bevel(prim('cyl', loc=(0, 0, .06), vertices=6, radius=.3, depth=.12, m=ST), .015, 1))
tp.append(bevel(prim('cyl', loc=(0, 0, .15), vertices=6, radius=.22, depth=.06, m=ST), .01, 1))
tp.append(prim('cyl', loc=(0, 0, .42), vertices=14, radius=.085, depth=.5, m=ST, smooth=True))
for z in (.3, .55): tp.append(prim('torus', loc=(0, 0, z), major_radius=.088, minor_radius=.014, major_segments=14, minor_segments=4, m=ST, smooth=True))
tp.append(prim('cone', loc=(0, 0, .71), vertices=6, radius1=.12, radius2=.25, depth=.12, m=ST))
tp.append(bevel(prim('cyl', loc=(0, 0, .79), vertices=6, radius=.26, depth=.05, m=ST), .008, 1))
tp.append(prim('cyl', loc=(0, 0, .92), vertices=6, radius=.13, depth=.21, m=LAMP))
for k in range(6):
    a = k / 6 * math.tau
    tp.append(bevel(prim('cube', loc=(.165 * math.cos(a), .165 * math.sin(a), .92), rot=(0, 0, a), scale=(.025, .03, .115), m=ST), .006, 1))
for k in range(6):
    a = (k + .5) / 6 * math.tau
    if k % 3 == 0:  # dos ventanas con papel de celosía; el resto abiertas
        tp.append(prim('cube', loc=(.13 * math.cos(a), .13 * math.sin(a), .92), rot=(0, 0, a), scale=(.004, .075, .09), m=PAPER))
tp.append(bevel(prim('cyl', loc=(0, 0, 1.045), vertices=6, radius=.21, depth=.04, m=ST), .008, 1))
# tejado curvo con puntas levantadas
bm = bmesh.new()
R = .42; ring = []
for k in range(6):
    a = k / 6 * math.tau
    ring.append(bm.verts.new((R * math.cos(a), R * math.sin(a), 1.08)))
mid = []
for k in range(6):
    a = k / 6 * math.tau; a2 = (k + .5) / 6 * math.tau
    mid.append(bm.verts.new((R * .87 * math.cos(a2), R * .87 * math.sin(a2), 1.065)))
up = [bm.verts.new((.16 * math.cos(k / 6 * math.tau), .16 * math.sin(k / 6 * math.tau), 1.2)) for k in range(6)]
apex = bm.verts.new((0, 0, 1.26))
for k in range(6):
    k1 = (k + 1) % 6
    bm.faces.new((ring[k], mid[k], up[k]))
    bm.faces.new((mid[k], ring[k1], up[k1]))
    bm.faces.new((mid[k], up[k1], up[k]))
    bm.faces.new((up[k], up[k1], apex))
bm.faces.new(list(reversed(ring[:1] + [mid[0]] + ring[1:2] + [mid[1]] + ring[2:3] + [mid[2]] + ring[3:4] + [mid[3]] + ring[4:5] + [mid[4]] + ring[5:6] + [mid[5]])))
for k in range(6): ring[k].co.z += .05
roof = mesh_obj(bm, 'roof', ST, smooth=False)
sol = roof.modifiers.new('s', 'SOLIDIFY'); sol.thickness = .05; C.view_layer.objects.active = roof; bpy.ops.object.modifier_apply(modifier='s')
bevel(roof, .01, 1); tp.append(roof)
for k in range(6):
    a = k / 6 * math.tau
    tp.append(prim('sphere', loc=(.43 * math.cos(a), .43 * math.sin(a), 1.145), segments=8, ring_count=5, radius=.028, scale=(1, 1, 1.4), m=ST, smooth=True))
hj = lathe([(0.001, 1.25), (.05, 1.25), (.07, 1.29), (.06, 1.33), (.03, 1.37), (.008, 1.41), (.001, 1.42)], ST, 'hoju', 12)
tp.append(hj)
for k in range(5):
    a = k * 1.3
    mm = rock('tm%d' % k, (.1, .07, .03), 300 + k, MOSS, subdiv=2, amp=.2, flat=(.6, .3), squish=.5, smooth_it=1)
    mm.location = (.24 * math.cos(a), .24 * math.sin(a), 1.13 + (.24 - .24) ); mm.rotation_euler = (0, -.3 * math.cos(a), a)
    tp.append(mm)
mm = rock('tmb', (.25, .2, .05), 309, MOSS, subdiv=2, amp=.2, flat=(.6, .3), squish=.5, smooth_it=1); mm.location = (.05, -.05, .1); tp.append(mm)
toro = join(tp, 'Toro', (0, 0, 0))

# Bambú: tallos con nudos, ramitas y hojas
CUL = M('Bambú', '#7d9446', .45); CUL2 = M('Bambú viejo', '#a39c55', .5); LEAF = M('Hoja bambú', '#5f8a3a', .55)
bb = []
rb2 = random.Random(3)
def leaf_mesh(p, dirv, L, Wd, m):
    bm = bmesh.new()
    dirv = dirv.normalized(); side = dirv.cross(Vector((0, 0, 1)))
    if side.length < .1: side = Vector((1, 0, 0))
    side.normalize(); upv = side.cross(dirv)
    pts = [p, p + dirv * L * .3 + side * Wd + upv * Wd * .3, p + dirv * L * .3 - side * Wd + upv * Wd * .3,
           p + dirv * L * .65 + side * Wd * .7 - upv * L * .05, p + dirv * L * .65 - side * Wd * .7 - upv * L * .05,
           p + dirv * L - upv * L * .18, p + dirv * L * .3 + upv * Wd * .6, p + dirv * L * .65 + upv * Wd * .2]
    v = [bm.verts.new(q) for q in pts]
    for f in ((0, 1, 6), (0, 6, 2), (1, 3, 7, 6), (6, 7, 4, 2), (3, 5, 7), (7, 5, 4)): bm.faces.new([v[i] for i in f])
    return mesh_obj(bm, 'leaf', m)
for k in range(7):
    x, y = rb2.uniform(-.45, .45), rb2.uniform(-.35, .35)
    H = rb2.uniform(3.2, 5.4); r = rb2.uniform(.045, .07); lean = Vector((rb2.uniform(-.25, .25), rb2.uniform(-.2, .2), 0))
    m = CUL if k % 3 else CUL2
    n = int(H / .42)
    pts = [(x + lean.x * (i / n) ** 2, y + lean.y * (i / n) ** 2, H * i / n) for i in range(n + 1)]
    tube_o = tube(pts, r, m, 8, 'culm', r_end=r * .75)
    bb.append(tube_o)
    for i in range(1, n):
        px, py, pz = pts[i]
        bb.append(prim('torus', loc=(px, py, pz), major_radius=r * (1.0 - .25 * i / n), minor_radius=r * .2, major_segments=8, minor_segments=3, m=m, smooth=True))
        if i > n * .45 and rb2.random() < .75:
            a = rb2.uniform(0, math.tau); dv = Vector((math.cos(a), math.sin(a), rb2.uniform(.25, .7)))
            tip = Vector((px, py, pz)) + dv * rb2.uniform(.25, .5)
            bb.append(tube([(px, py, pz), tuple(tip)], .01, m, 3, 'twig', r_end=.005))
            for q in range(rb2.randint(3, 5)):
                la = a + rb2.uniform(-1.3, 1.3); ld = Vector((math.cos(la), math.sin(la), rb2.uniform(-.7, -.1)))
                bb.append(leaf_mesh(tip, ld, rb2.uniform(.26, .38), rb2.uniform(.035, .05), LEAF))
bambu = join(bb, 'Bambu', (0, 0, 0))

# Helecho: frondes arqueadas con foliolos
FERN = M('Helecho', '#4c7a35', .6)
hp = []
rf = random.Random(8)
for k in range(8):
    a = k / 8 * math.tau + rf.uniform(-.2, .2); L = rf.uniform(.55, .8)
    dvec = Vector((math.cos(a), math.sin(a), 0))
    pts = []
    for i in range(12):
        t = i / 11
        pts.append(Vector((0, 0, .02)) + dvec * L * t + Vector((0, 0, L * (.9 * t - .95 * t * t))))
    hp.append(tube([tuple(p) for p in pts], .008, FERN, 3, 'rach', r_end=.003))
    side = dvec.cross(Vector((0, 0, 1))).normalized()
    for i in range(1, 11):
        p = pts[i]; w = .09 * math.sin(math.pi * i / 11) + .02
        for s in (1, -1):
            bm = bmesh.new()
            tipv = p + side * s * w + dvec * .03 + Vector((0, 0, -.02))
            v0 = bm.verts.new(p - dvec * .018); v1 = bm.verts.new(tipv); v2 = bm.verts.new(p + dvec * .022)
            bm.faces.new((v0, v1, v2)); hp.append(mesh_obj(bm, 'pin', FERN))
helecho = join(hp, 'Helecho', (0, 0, 0))

# Musgo: montículos
mg = []
for k in range(4):
    s = random.uniform(.12, .26)
    m_ = rock('mg%d' % k, (s * 1.2, s, s * .45), 400 + k, MOSS, subdiv=3, amp=.25, freq=2.2, flat=(.7, .1), squish=.5, smooth_it=1)
    m_.location = (random.uniform(-.35, .35), random.uniform(-.3, .3), 0); mg.append(m_)
bpy.ops.object.select_all(action='DESELECT')
for m_ in mg: m_.select_set(True)
C.view_layer.objects.active = mg[0]; bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
join(mg, 'Musgo', (0, 0, 0))

# Hoja (para el viento): hoja de bambú suelta
hoja = leaf_mesh(Vector((-.07, 0, 0)), Vector((1, 0, 0)), .15, .02, M('Hoja suelta', '#8aa04a', .6))
hoja.name = 'Hoja'; hoja.data.name = 'Hoja'

# ---------------------------------------------------------------- export
COMMON = ['Piedra%d' % i for i in range(1, 9)]
RARE = ['Jade', 'Obsidiana', 'Geoda', 'Cuarzo', 'Ambar', 'Meteorito', 'Lapis', 'Pirita', 'Turquesa', 'Malaquita', 'Opalo', 'Fosil']
SCENE = ['Roca base', 'Orilla', 'Toro', 'Bambu', 'Helecho', 'Musgo', 'Hoja']
ASSETS = COMMON + RARE + SCENE
keep_only(ASSETS)
for n in ASSETS:
    ob = bpy.data.objects[n]; ob.location = (0, 0, 0)
    print('%-12s verts %5d  dims %s' % (n, len(ob.data.vertices), tuple(round(d, 3) for d in ob.dimensions)))
os.makedirs(ROOT + '/glb', exist_ok=True); os.makedirs(ROOT + '/blend', exist_ok=True); os.makedirs(ROOT + '/renders', exist_ok=True)
bpy.ops.object.select_all(action='DESELECT')
for n in ASSETS: bpy.data.objects[n].select_set(True)
bpy.ops.export_scene.gltf(filepath=ROOT + '/glb/cairn.glb', export_format='GLB', use_selection=True, export_apply=True,
                          export_yup=True, export_materials='EXPORT', export_texcoords=False)
bpy.ops.wm.save_as_mainfile(filepath=ROOT + '/blend/cairn.blend')
print('GLB', os.path.getsize(ROOT + '/glb/cairn.glb'))

if '--noicon' in sys.argv: sys.exit(0)
# ---------------------------------------------------------------- icono (Cycles)
# Detalle solo para el render: moteado en las piedras, agua y niebla fingida con planos
def mottle(mname, scale=6., amt=.25):
    m = bpy.data.materials[mname]; nt = m.node_tree; p = nt.nodes['Principled BSDF']
    base = tuple(p.inputs['Base Color'].default_value)
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = scale
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
    mix.inputs[6].default_value = base; mix.inputs[7].default_value = tuple(c * (1 - amt) for c in base[:3]) + (1,)
    nt.links.new(nz.outputs['Fac'], mix.inputs[0]); nt.links.new(mix.outputs[2], p.inputs['Base Color'])
    try: p.inputs['Coat Weight'].default_value = .5
    except Exception: pass
for n in ['Piedra 1', 'Piedra 2', 'Piedra 3', 'Piedra 4', 'Piedra 5', 'Piedra 6', 'Piedra 7', 'Roca base']: mottle(n)
for n in ASSETS: bpy.data.objects[n].hide_render = True
water = prim('plane', loc=(0, 2, -.02), size=40, m=M('Agua icono', '#2d6b6e', .05))
cairn = ['Piedra6', 'Piedra4', 'Piedra2', 'Piedra5', 'Piedra7']
SC = 1.55
rb_top = bpy.data.objects['Roca base'].dimensions.z
z = rb_top - .62 - .01
pos = []
for i, n in enumerate(cairn):
    pos.append((.035 * (-1) ** i, 0, z)); z += bpy.data.objects[n].dimensions.z * SC - .012
dups = showcase(['Roca base'] + cairn + ['Toro', 'Bambu', 'Bambu', 'Musgo', 'Helecho'],
                [(0, .3, -.62)] + pos + [(-1.15, 1.3, -.35), (1.9, 3.2, -.3), (-2.6, 4.2, -.3), (.9, -.7, -.05), (-1.3, -.4, 0)],
                [(0, 0, .3)] + [(0, 0, i * .8 + .2) for i in range(5)] + [(0, 0, .5), (0, 0, 0), (0, 0, 1), (0, 0, 0), (0, 0, 0)],
                [1.0] + [SC] * 5 + [1.5, 1, 1, .8, .9])
for k, (y, a) in enumerate([(1.2, .35), (2.6, .5), (3.8, .6)]):
    pl = prim('plane', loc=(0, y, 1.5), rot=(math.pi / 2, 0, 0), size=14, m=M('Niebla %d' % k, '#b7c4be', 1., alpha=a))
render_icon(ROOT + '/renders/cairn.png', '#aebcb6', (0, -4.8, 1.1), (0, 0, .98), lens=58, samples=56,
            lights=[('SUN', (-4, -3, 5), 3.4, '#ffe2bd'), ('AREA', (4, -3, 2), 160, '#c8e0e6'), ('POINT', (-1.15, 1.0, 1.35), 80, '#ffb865')])
print('OK cairn')
