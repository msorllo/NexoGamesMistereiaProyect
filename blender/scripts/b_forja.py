"""FORJA (app 27): taller de herrero. Modela todos los assets, exporta GLB, guarda .blend y renderiza el icono.
Ejes Blender: Z arriba. En Three.js: x=x, y=z, z=-y.
Convenciones de los assets:
- Armas y lingote: la hoja apunta a +X y empieza en x=0 (guarda). Plana en XY, grosor en Z. La hoja usa el material 'Hoja'.
- Martillo: origen en el extremo del mango, mango hacia +X, cara de golpeo hacia -Z.
- Tenazas: origen en la boca (donde muerden), mangos hacia +X.
- Fuelle / Fuelle cuero / Fuelle tapa: origen en la bisagra (x=.08, z=0). La tapa se modela abierta TH0 grados.
- Fragua: origen en el suelo, la boca mira a -Y (a +Z en Three).
"""
import sys, os, math, random; HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
from blib import *
import bmesh
from mathutils import Vector, Matrix
reset()
random.seed(27)

# ---------------- materiales ----------------
IRON_ANV = mat('Hierro yunque', '#34312e', .5, .85)
FACE = mat('Cara pulida', '#a9adb2', .2, 1.0)
HOLE = mat('Hueco', '#050404', 1.0)
BARK = mat('Corteza', '#3a2a1e', .95)
BARK2 = mat('Corteza oscura', '#2a1d14', .95)
RING1 = mat('Madera tocón', '#a47a50', .8)
RING2 = mat('Anillo', '#6f4a2e', .85)
BRICKS = [mat('Ladrillo A', '#6b2e20', .9), mat('Ladrillo B', '#7a3f28', .9), mat('Ladrillo C', '#5c281c', .92), mat('Ladrillo D', '#4d241a', .95)]
SOOT = mat('Hollín', '#161110', 1.0)
MORTAR = mat('Mortero', '#4a3f37', .98)
STONES = [mat('Piedra A', '#4a423b', .9), mat('Piedra B', '#3b342f', .92), mat('Piedra C', '#554b42', .88)]
HOOD = mat('Hierro campana', '#26221f', .62, .75)
RIVET = mat('Remache', '#3b3631', .45, .9)
COAL = mat('Carbón', '#141110', .85)
EMBER = mat('Brasa', '#2a120a', .9, 0, emit='#ff5a1f', emit_str=3.0)
WOODH = mat('Fresno', '#a37649', .6)
LEATHER = mat('Cuero', '#5a3620', .72)
LEATHER_D = mat('Cuero oscuro', '#2e1d14', .7)
IRON_B = mat('Hierro negro', '#1f1d1c', .48, .85)
BRASS = mat('Latón viejo', '#a4803f', .35, 1.0)
OAKS = [mat('Roble A', '#6b4a2f', .75), mat('Roble B', '#5c3f27', .78), mat('Roble C', '#7a5635', .74)]
HOOP = mat('Hierro aro', '#2b2724', .5, .8)
WATER = mat('Agua', '#10222a', .04)
STEEL = mat('Hoja', '#c3c8ce', .26, 1.0)
INGOT = mat('Lingote', '#595653', .45, .95)
GUARD = mat('Guarda', '#3a3633', .35, .9)
GOLDB = mat('Bronce', '#b0864a', .3, 1.0)
PLANKS = [mat('Tablón A', '#4a3322', .82), mat('Tablón B', '#3d2a1c', .85), mat('Tablón C', '#56402b', .8)]
SLABS = [mat('Losa A', '#3b342f', .86), mat('Losa B', '#302a26', .9), mat('Losa C', '#453d36', .84)]
GRIT = mat('Arenisca', '#8a7b66', .96)
GLASSM = mat('Vidrio luna', '#23384f', .15, 0, emit='#5d7fa8', emit_str=0.9)
TORCH = mat('Llama antorcha', '#ffb347', .5, 0, emit='#ff8a2a', emit_str=6.0)


# ---------------- helpers propios ----------------
def mk(name, verts, faces, mats=None, fmat=None, smooth=False):
    me = bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in verts], [], faces); me.update()
    o = bpy.data.objects.new(name, me); C.collection.objects.link(o)
    if mats:
        for m in (mats if isinstance(mats, (list, tuple)) else [mats]): me.materials.append(m)
    if fmat:
        for i, p in enumerate(me.polygons): p.material_index = fmat[i]
    for p in me.polygons: p.use_smooth = smooth
    fixn(o)
    return o


def fixn(o):
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data); bm.free(); o.data.update()
    return o


def loft(name, secs, m, closed=True, cap0=True, cap1=True, smooth=False):
    """secs: lista de anillos (listas de puntos 3D, mismo número). Un anillo de 1 punto = punta."""
    verts, faces, idx = [], [], []
    for s in secs:
        idx.append(list(range(len(verts), len(verts) + len(s)))); verts += s
    for a, b in zip(idx, idx[1:]):
        n = max(len(a), len(b))
        rng = range(n) if closed else range(n - 1)
        for i in rng:
            j = (i + 1) % n
            if len(a) == 1: faces.append((a[0], b[i], b[j]))
            elif len(b) == 1: faces.append((a[i], a[j], b[0]))
            else: faces.append((a[i], a[j], b[j], b[i]))
    if cap0 and len(idx[0]) > 2: faces.append(tuple(reversed(idx[0])))
    if cap1 and len(idx[-1]) > 2: faces.append(tuple(idx[-1]))
    return mk(name, verts, faces, m, smooth=smooth)


def smooth_angle(o, deg=35):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); C.view_layer.objects.active = o
    try: bpy.ops.object.shade_smooth_by_angle(angle=math.radians(deg))
    except Exception: bpy.ops.object.shade_smooth()
    return o


def box(x0, x1, y0, y1, z0, z1, m, name='box', drop=()):
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = {'b': (0, 3, 2, 1), 't': (4, 5, 6, 7), '-y': (0, 1, 5, 4), '+y': (2, 3, 7, 6), '-x': (3, 0, 4, 7), '+x': (1, 2, 6, 5)}
    return mk(name, v, [f[k] for k in f if k not in drop], m)


def chamf(sx, sy, sz, ch, m, name='ch'):
    """caja centrada con la cara +Z achaflanada y sin cara inferior (36 vértices exportados)"""
    x, y, z, c = sx / 2, sy / 2, sz / 2, ch
    v = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z), (-x, -y, z - c), (x, -y, z - c), (x, y, z - c), (-x, y, z - c),
         (-x + c, -y + c, z), (x - c, -y + c, z), (x - c, y - c, z), (-x + c, y - c, z)]
    f = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 9, 8), (5, 6, 10, 9), (6, 7, 11, 10), (7, 4, 8, 11), (8, 9, 10, 11)]
    return mk(name, v, f, m)


def dup(src, loc=(0, 0, 0), rot=(0, 0, 0), sc=(1, 1, 1), m=None):
    d = src.copy(); d.data = src.data.copy(); C.collection.objects.link(d)
    d.location = loc; d.rotation_euler = rot; d.scale = sc
    if m is not None: d.data.materials[0] = m
    return d


def ico(loc, r, m, sub=1, jit=.25, sc=(1, 1, 1)):
    o = prim('ico', loc=loc, subdivisions=sub, radius=r, m=m)
    for v in o.data.vertices:
        v.co = Vector((v.co.x * sc[0], v.co.y * sc[1], v.co.z * sc[2])) * (1 + random.uniform(-jit, jit))
    for p in o.data.polygons: p.use_smooth = True
    return o


def ellipse(cx, cy, cz, ry, rz, n=12, axis='x', ph=0.0):
    """anillo elíptico perpendicular al eje dado"""
    out = []
    for i in range(n):
        a = i / n * math.tau + ph
        if axis == 'x': out.append((cx, cy + ry * math.cos(a), cz + rz * math.sin(a)))
        elif axis == 'y': out.append((cx + ry * math.cos(a), cy, cz + rz * math.sin(a)))
        else: out.append((cx + ry * math.cos(a), cy + rz * math.sin(a), cz))
    return out


def helix(x0, x1, r, turns, y=0, z=0, n=48):
    pts = []
    for i in range(n + 1):
        t = i / n; a = t * turns * math.tau
        pts.append((x0 + (x1 - x0) * t, y + r * math.cos(a), z + r * math.sin(a)))
    return pts


ASSETS = []
def done(objs, name, origin=(0, 0, 0)):
    o = join(objs, name, origin); ASSETS.append(name); return o


# =============== YUNQUE ===============
def anvil():
    P = []
    # cuerpo: secciones horizontales (z, xmin, xmax, media anchura)
    S = [(0, -.25, .23, .125), (.035, -.25, .23, .125), (.06, -.21, .19, .095), (.1, -.15, .13, .068), (.14, -.13, .11, .06),
         (.175, -.15, .14, .066), (.205, -.25, .2, .076), (.225, -.31, .205, .078), (.285, -.31, .205, .078)]
    secs = []
    for z, x0, x1, w in S:
        c = .012  # chaflán de esquina
        secs.append([(x0 + c, -w, z), (x1 - c, -w, z), (x1, -w + c, z), (x1, w - c, z), (x1 - c, w, z), (x0 + c, w, z), (x0, w - c, z), (x0, -w + c, z)])
    body = loft('anv', secs, IRON_ANV)
    bevel(body, .006, 2); smooth_angle(body, 40); P.append(body)
    # cara pulida (soldada) y mesa
    face = box(-.305, .13, -.074, .074, .285, .3, FACE); bevel(face, .004, 2); P.append(face)
    # cuerno: loft de elipses a lo largo de X
    hs = []
    for i in range(14):
        u = i / 13; x = .2 + .33 * u; r = .07 * (1 - u) ** 1.05 + .005
        zc = .238 + .012 * u * u
        hs.append(ellipse(x, 0, zc, r, r * .8, 16))
    horn = loft('horn', hs, IRON_ANV, smooth=True); P.append(horn)
    # agujeros (hardy y pritchel)
    P.append(box(-.265, -.24, -.0125, .0125, .296, .3015, HOLE))
    P.append(prim('cyl', loc=(-.2, 0, .2985), vertices=10, radius=.008, depth=.006, m=HOLE))
    # pequeños pies marcados
    for sx in (-.2, .18):
        for sy in (-1, 1):
            f = box(sx - .045, sx + .045, sy * .125 - .02, sy * .125 + .02, 0, .012, IRON_ANV); P.append(f)
    return done(P, 'Yunque')


# =============== TOCÓN ===============
def stump():
    P = []; R = .2; H = .5; na = 30; nz = 8
    ridge = [random.uniform(-.018, .018) for _ in range(na)]
    rings = []
    for k in range(nz + 1):
        z = H * k / nz
        flare = .07 * math.exp(-z * 14)
        ring = []
        for i in range(na):
            a = i / na * math.tau
            r = R + flare * (1 + .6 * math.sin(a * 5 + 1)) + ridge[i] + .004 * math.sin(z * 40 + i)
            ring.append((r * math.cos(a), r * math.sin(a), z if k < nz else H))
        rings.append(ring)
    bark = loft('bark', rings, BARK, cap0=False, cap1=False, smooth=True)
    for i, p in enumerate(bark.data.polygons):
        if (i // nz) % 3 == 0: p.material_index = 0
    P.append(bark)
    # corte superior con anillos alternos
    verts, faces, fm = [(0, 0, H - .004)], [], []
    nr = 11; prev = [0] * na
    for k in range(1, nr + 1):
        rr = (R - .012) * k / nr
        cur = []
        for i in range(na):
            a = i / na * math.tau
            w = rr * (1 + .02 * math.sin(a * 3 + k))
            verts.append((w * math.cos(a), w * math.sin(a), H - .004)); cur.append(len(verts) - 1)
        for i in range(na):
            j = (i + 1) % na
            if k == 1: faces.append((0, cur[i], cur[j]))
            else: faces.append((prev[i], cur[i], cur[j], prev[j]))
            fm.append(k % 2)
        prev = cur
    top = mk('top', verts, faces, [RING1, RING2], fm); P.append(top)
    # grieta radial
    P.append(box(0, R - .02, -.004, .004, H - .006, H - .002, HOLE))
    return done(P, 'Tocón')


# =============== FRAGUA ===============
MW, SPR, AR = .26, .95, .26  # media anchura de la boca, arranque del arco, radio
def arch_top(x):
    return SPR + math.sqrt(max(0, AR * AR - x * x)) if abs(x) < AR else None


def forge():
    P = []
    W, D = .55, .45
    # núcleo de la base de piedra + núcleo del horno (con cámara abierta al frente)
    P.append(box(-W + .03, W - .03, -D + .03, D - .03, 0, .7, MORTAR))
    P.append(box(-W + .03, W - .03, 0, D - .03, .7, 1.35, SOOT))
    P.append(box(-W + .03, -.3, -D + .03, 0, .7, 1.35, SOOT))
    P.append(box(.3, W - .03, -D + .03, 0, .7, 1.35, SOOT))
    P.append(box(-.3, .3, -D + .03, 0, 1.23, 1.35, SOOT))
    # placa frontal de mortero con hueco en arco
    N = 30; xs = [-W + .02 + (2 * W - .04) * i / N for i in range(N + 1)]
    verts, faces = [], []
    for i in range(N):
        xa, xb = xs[i], xs[i + 1]
        ya = -D + .06
        def bot(x):
            t = arch_top(x)
            return t if t is not None else .7
        za, zb = bot(xa), bot(xb)
        b = len(verts); verts += [(xa, ya, za), (xb, ya, zb), (xb, ya, 1.35), (xa, ya, 1.35)]
        faces.append((b, b + 1, b + 2, b + 3))
    plate = mk('plate', verts, faces, MORTAR)
    sd = plate.modifiers.new('s', 'SOLIDIFY'); sd.thickness = .04; C.view_layer.objects.active = plate; bpy.ops.object.modifier_apply(modifier='s')
    P.append(plate)
    # ladrillo base
    brick = box(-.1, .1, -.05, .05, -.032, .032, BRICKS[0], 'brick', drop=('+y',))
    ch = .075; rows = 9
    # frente
    for r in range(rows):
        z0 = .705 + r * ch; z1 = z0 + ch - .01; zc = (z0 + z1) / 2
        off = .1 if r % 2 else 0
        x = -W - off
        while x < W:
            xa, xb = max(x, -W), min(x + .2, W); x += .212
            if xb - xa < .04: continue
            segs = [(xa, xb)]
            # recorte por la boca y la rosca del arco
            if z0 < SPR + AR + .11:
                if zc < SPR: hw = MW + .012
                else:
                    dz = max(0, z0 - SPR); hw = math.sqrt(max(0, (AR + .11) ** 2 - dz * dz)) if dz < AR + .11 else 0
                if hw > 0:
                    segs = []
                    if xa < -hw: segs.append((xa, min(xb, -hw)))
                    if xb > hw: segs.append((max(xa, hw), xb))
            for a, b in segs:
                if b - a < .035: continue
                m = random.choice(BRICKS)
                d = dup(brick, loc=((a + b) / 2, -D + .005 + random.uniform(-.004, .006), zc), rot=(random.uniform(-.02, .02), 0, random.uniform(-.01, .01)), sc=((b - a) / .2, 1, 1), m=m)
                P.append(d)
    # dovelas del arco
    nv = 13
    for k in range(nv):
        a0 = k / nv * math.pi + .008; a1 = (k + 1) / nv * math.pi - .008
        r0, r1 = AR + .005, AR + .105
        pts = []
        for (r, a) in ((r0, a0), (r1, a0), (r1, a1), (r0, a1)):
            pts.append((r * math.cos(a), r * math.sin(a) + SPR))
        v = [(x, -D - .005, z) for x, z in pts] + [(x, -D + .09, z) for x, z in pts]
        f = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
        P.append(mk('vous', v, f, random.choice(BRICKS)))
    # laterales
    P.append(box(-W - .005, -W + .03, -D, D, .7, 1.35, BRICKS[3]))
    for s in (1,):
        for r in range(rows):
            z0 = .705 + r * ch; zc = z0 + (ch - .01) / 2
            off = .1 if (r + 1) % 2 else 0
            y = -D - off
            while y < D:
                ya, yb = max(y, -D), min(y + .2, D); y += .212
                if yb - ya < .04: continue
                d = dup(brick, loc=(s * (W - .005), (ya + yb) / 2, zc), rot=(0, 0, math.pi / 2 * s), sc=((yb - ya) / .2, 1, 1), m=random.choice(BRICKS))
                P.append(d)
    # base de piedra (sillares biselados)
    stone = chamf(1, 1, 1, .09, STONES[0], 'stone'); stone.data.transform(Matrix.Rotation(math.pi / 2, 4, 'X'))
    def stones_row(axis, s, length):
        for rr, (z0, h) in enumerate(((0, .22), (.23, .23), (.47, .22))):
            pos = -length - (.13 if rr % 2 else 0)
            while pos < length:
                L = random.uniform(.24, .36); a, b = max(pos, -length), min(pos + L, length); pos += L + .012
                if b - a < .06: continue
                c = (a + b) / 2; zc = z0 + h / 2 + .005
                sc = ((b - a) / 1.0, .12 + random.uniform(0, .02), h / 1.0)
                if axis == 'x':
                    loc = (c, s * (D - .05 + random.uniform(-.006, .008)), zc); rot = (0, random.uniform(-.02, .02), random.uniform(-.015, .015))
                else:
                    loc = (s * (W - .05 + random.uniform(-.006, .008)), c, zc); rot = (0, random.uniform(-.02, .02), math.pi / 2 + random.uniform(-.015, .015))
                P.append(dup(stone, loc=loc, rot=rot, sc=sc, m=random.choice(STONES)))
    stones_row('x', -1, W + .02)
    stones_row('y', -1, D); stones_row('y', 1, D)
    bpy.data.objects.remove(stone, do_unlink=True); bpy.data.objects.remove(brick, do_unlink=True)
    # repisa de la boca
    sill = box(-.34, .34, -D - .12, -D + .08, .64, .7, STONES[2]); bevel(sill, .012, 1); P.append(sill)
    # losa superior
    slab = box(-W - .06, W + .06, -D - .06, D + .06, 1.35, 1.44, STONES[1]); bevel(slab, .02, 1); P.append(slab)
    # campana de humos (chapa) con remaches
    hb, ht = (.5, .43), (.2, .18)
    v = [(-hb[0], -hb[1], 1.44), (hb[0], -hb[1], 1.44), (hb[0], hb[1], 1.44), (-hb[0], hb[1], 1.44),
         (-ht[0], -ht[1], 1.98), (ht[0], -ht[1], 1.98), (ht[0], ht[1], 1.98), (-ht[0], ht[1], 1.98)]
    hood = mk('hood', v, [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], HOOD)
    sd = hood.modifiers.new('s', 'SOLIDIFY'); sd.thickness = .02; C.view_layer.objects.active = hood; bpy.ops.object.modifier_apply(modifier='s')
    P.append(hood)
    for k in range(9):
        t = (k + .5) / 9; x = -hb[0] + 2 * hb[0] * t
        P.append(prim('cone', loc=(x, -hb[1] - .01, 1.47), rot=(math.pi / 2, 0, 0), vertices=5, radius1=.012, radius2=.005, depth=.008, m=RIVET))
    for t in (.33, .66):
        z = 1.44 + .54 * t; wx = hb[0] + (ht[0] - hb[0]) * t; wy = hb[1] + (ht[1] - hb[1]) * t
        P.append(box(-wx - .012, wx + .012, -wy - .016, -wy + .01, z - .015, z + .015, IRON_B))
    # chimenea
    P.append(box(-.17, .17, -.15, .15, 1.98, 3.4, HOOD))
    for z in (2.3, 2.8, 3.3):
        P.append(box(-.185, .185, -.165, .165, z - .02, z + .02, IRON_B))
    # tobera lateral (a la izquierda) para el fuelle
    P.append(prim('cyl', loc=(-W - .12, 0, .78), rot=(0, math.pi / 2, 0), vertices=12, radius=.035, depth=.26, m=IRON_B))
    P.append(prim('torus', loc=(-W - .02, 0, .78), rot=(0, math.pi / 2, 0), major_radius=.045, minor_radius=.012, major_segments=14, minor_segments=5, m=IRON_B))
    # atizador apoyado
    P.append(curve_tube([(W + .07, -D + .05, .02), (W + .07, -D - .02, 1.05)], .009, IRON_B, res=6))
    P.append(prim('torus', loc=(W + .07, -D - .025, 1.09), rot=(math.pi / 2, 0, 0), major_radius=.03, minor_radius=.008, major_segments=12, minor_segments=5, m=IRON_B))
    return done(P, 'Fragua')


def embers():
    P = []
    for i in range(46):
        a = random.uniform(0, math.tau); rr = math.sqrt(random.random()) * .24
        x, y = rr * math.cos(a) * 1.05, rr * math.sin(a) * .75 - .2
        z = .72 + (.09 * (1 - (rr / .26) ** 2)) + random.uniform(0, .02)
        m = EMBER if random.random() < .62 else COAL
        P.append(ico((x, y, z), random.uniform(.028, .048), m, 1, .28, (1, random.uniform(.7, 1.1), random.uniform(.6, .85))))
    return done(P, 'Brasas')


# =============== MARTILLO ===============
def hammer():
    P = []
    hx = .34
    blk = box(hx - .024, hx + .024, -.022, .022, -.04, .045, IRON_B); bevel(blk, .005, 2); smooth_angle(blk, 50); P.append(blk)
    face = prim('cyl', loc=(hx, 0, -.058), vertices=18, radius=.026, depth=.04, m=IRON_B)
    bevel(face, .004, 2); smooth_angle(face, 50); P.append(face)
    # peña en cuña
    v = [(hx - .024, -.022, .045), (hx + .024, -.022, .045), (hx + .024, .022, .045), (hx - .024, .022, .045),
         (hx - .006, -.024, .1), (hx + .006, -.024, .1), (hx + .006, .024, .1), (hx - .006, .024, .1)]
    peen = mk('peen', v, [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7)], IRON_B); P.append(peen)
    # mango
    secs = []
    for i in range(12):
        u = i / 11; x = -.0 + (hx + .03) * u
        ry = .014 + .003 * math.cos(u * math.pi * 1.2) ; rz = ry * 1.35
        secs.append(ellipse(x, 0, 0, ry, rz, 12, 'x'))
    P.append(loft('handle', secs, WOODH, smooth=True))
    P.append(box(hx - .006, hx + .006, -.012, .012, .045, .05, IRON_B))  # cuña
    P.append(curve_tube(helix(.01, .13, .02, 7), .004, LEATHER_D, res=4))
    return done(P, 'Martillo')


def tongs():
    P = []
    for s in (1, -1):
        pts = [(-.01, 0, s * .012), (.03, 0, s * .014), (.07, 0, s * .002), (.1, 0, -s * .01), (.3, 0, -s * .03), (.46, 0, -s * .034)]
        P.append(curve_tube(pts, .007, IRON_B, res=4))
        P.append(box(-.035, .02, -.012, .012, s * .008 - .004 + (.004 if s > 0 else 0), s * .008 + .004 + (.004 if s > 0 else 0), IRON_B))
    P.append(prim('cyl', loc=(.075, 0, 0), rot=(math.pi / 2, 0, 0), vertices=10, radius=.011, depth=.03, m=RIVET))
    P.append(prim('torus', loc=(.44, 0, 0), rot=(0, math.pi / 2, 0), major_radius=.035, minor_radius=.005, major_segments=12, minor_segments=4, m=IRON_B))
    return done(P, 'Tenazas')


# =============== FUELLE ===============
TH0 = math.radians(16)
def bellows_outline():
    pts = [(.08, -.05)]
    for i in range(15):
        a = -1.95 + 3.9 * i / 14
        pts.append((.44 + .2 * math.cos(a - math.pi) * -1, .2 * math.sin(a)))
    pts.append((.08, .05))
    return pts


def bellows():
    ol = bellows_outline()
    # tablero inferior + caballete + tobera
    P = []
    bot = mk('bb', [(x, y, -.025) for x, y in ol] + [(x, y, 0) for x, y in ol],
             [tuple(range(len(ol)))[::-1], tuple(range(len(ol), 2 * len(ol)))] + [(i, (i + 1) % len(ol), len(ol) + (i + 1) % len(ol), len(ol) + i) for i in range(len(ol))], OAKS[2])
    P.append(bot)
    P.append(prim('cone', loc=(-.03, 0, .006), rot=(0, -math.pi / 2, 0), vertices=12, radius1=.038, radius2=.013, depth=.24, m=BRASS))
    for x in (.18, .56):
        for s in (-1, 1):
            P.append(box(x - .018, x + .018, s * .13 - .018, s * .13 + .018, -.55, -.025, OAKS[1]))
        P.append(box(x - .015, x + .015, -.15, .15, -.36, -.33, OAKS[0]))
    P.append(box(.16, .58, -.01, .01, -.45, -.42, OAKS[0]))
    for (x, y) in ol[1:-1:2]:
        P.append(ico((x * .97 + .01, y * .95, .004), .008, BRASS, 1, 0))
    base = done(P, 'Fuelle', (.08, 0, 0))
    # cuero en acordeón (cuña)
    rings = []; K = 9
    cx = sum(p[0] for p in ol) / len(ol)
    for k in range(K + 1):
        f = k / K; ins = .9 if k % 2 else 1.0
        ring = []
        for (x, y) in ol:
            xx = cx + (x - cx) * ins if k not in (0, K) else x
            yy = y * ins
            z = f * max(0, (xx - .08)) * math.tan(TH0)
            ring.append((xx, yy, z))
        rings.append(ring)
    lea = loft('lea', rings, LEATHER, cap0=False, cap1=False, smooth=True)
    done([lea], 'Fuelle cuero', (.08, 0, 0))
    # tapa (abierta TH0) con asa
    T = []
    top = mk('tb', [(x, y, 0) for x, y in ol] + [(x, y, .025) for x, y in ol],
             [tuple(range(len(ol)))[::-1], tuple(range(len(ol), 2 * len(ol)))] + [(i, (i + 1) % len(ol), len(ol) + (i + 1) % len(ol), len(ol) + i) for i in range(len(ol))], OAKS[0])
    T.append(top)
    T.append(box(.6, .66, -.02, .02, .02, .07, OAKS[1])); T.append(curve_tube([(.63, -.09, .06), (.63, .09, .06)], .014, WOODH, res=6))
    for (x, y) in ol[2:-2:2]:
        T.append(ico((x * .97 + .01, y * .95, .027), .008, BRASS, 1, 0))
    for o in T:
        bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); C.view_layer.objects.active = o
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        o.data.transform(Matrix.Translation((-.08, 0, 0)))
        o.data.transform(Matrix.Rotation(-TH0, 4, 'Y'))
        o.data.transform(Matrix.Translation((.08, 0, 0)))
    done(T, 'Fuelle tapa', (.08, 0, 0))


# =============== BARRIL + AGUA ===============
def barrel():
    P = []; H = .78; N = 18
    def rad(z): return .25 + .05 * math.sin(math.pi * z / H)
    for i in range(N):
        a0 = i / N * math.tau + .01; a1 = (i + 1) / N * math.tau - .01
        rows = 6; cols = 2; outer, inner = [], []
        verts = []; faces = []
        for r in range(rows + 1):
            z = H * r / rows
            for c in range(cols + 1):
                a = a0 + (a1 - a0) * c / cols; R = rad(z) + (.004 * math.sin(i * 7.3))
                verts.append((R * math.cos(a), R * math.sin(a), z))
        off = len(verts)
        for r in range(rows + 1):
            z = H * r / rows
            for c in range(cols + 1):
                a = a0 + (a1 - a0) * c / cols; R = rad(z) - .026
                verts.append((R * math.cos(a), R * math.sin(a), z))
        g = lambda r, c, o=0: o + r * (cols + 1) + c
        for r in range(rows):
            for c in range(cols):
                faces.append((g(r, c), g(r, c + 1), g(r + 1, c + 1), g(r + 1, c)))
                faces.append((g(r, c, off), g(r + 1, c, off), g(r + 1, c + 1, off), g(r, c + 1, off)))
        for c in range(cols):
            faces.append((g(rows, c), g(rows, c + 1), g(rows, c + 1, off), g(rows, c, off)))
            faces.append((g(0, c), g(0, c, off), g(0, c + 1, off), g(0, c + 1)))
        for r in range(rows):
            faces.append((g(r, 0), g(r + 1, 0), g(r + 1, 0, off), g(r, 0, off)))
            faces.append((g(r, cols), g(r, cols, off), g(r + 1, cols, off), g(r + 1, cols)))
        st = mk('stave', verts, faces, OAKS[i % 3], smooth=True)
        smooth_angle(st, 30)
        P.append(st)
    for z in (.08, .2, H - .2, H - .08):
        R = rad(z) + .004
        ring = lathe([(R, z - .022), (R + .007, z - .018), (R + .007, z + .018), (R, z + .022)], HOOP, 'hoop', 30)
        P.append(ring)
        P.append(ico((R + .008, 0, z), .006, RIVET, 1, 0))
    P.append(prim('cyl', loc=(0, 0, .05), vertices=32, radius=rad(.05) - .02, depth=.02, m=OAKS[1]))
    done(P, 'Barril')
    # agua: disco con anillos para la ondulación en Three
    verts, faces = [(0, 0, 0)], []
    na, nr = 36, 8; R = rad(.64) - .024; prev = None
    for k in range(1, nr + 1):
        rr = R * k / nr; cur = []
        for i in range(na):
            a = i / na * math.tau; verts.append((rr * math.cos(a), rr * math.sin(a), 0)); cur.append(len(verts) - 1)
        for i in range(na):
            j = (i + 1) % na
            faces.append((0, cur[i], cur[j]) if prev is None else (prev[i], cur[i], cur[j], prev[j]))
        prev = cur
    w = mk('water', verts, faces, WATER, smooth=True)
    w.location = (0, 0, .64); bpy.ops.object.select_all(action='DESELECT'); w.select_set(True); C.view_layer.objects.active = w
    bpy.ops.object.transform_apply(location=True)
    done([w], 'Agua', (0, 0, .64))


# =============== ARMAS ===============
def blade_secs(L, hwf, t, fuller=(0, 0, 0), tip=.14):
    """hoja a lo largo de X [0,L]. hwf(u)->media anchura. fuller=(u0,u1,prof)"""
    secs = []; n = 14
    for i in range(n + 1):
        u = i / n; x = L * u
        hw = hwf(u); th = t * (1 - .45 * u)
        if u > 1 - tip:
            k = (u - (1 - tip)) / tip; hw *= math.sqrt(max(0, 1 - k * k)) if k < 1 else 0; th *= (1 - k * .8)
        if i == n: secs.append([(x + .004, 0, 0)]); break
        fd = fuller[2] if fuller[0] <= u <= fuller[1] else 0
        secs.append([(x, hw, 0), (x, hw * .42, th), (x, 0, th * (1 - fd)), (x, -hw * .42, th), (x, -hw, 0), (x, -hw * .42, -th), (x, 0, -th * (1 - fd)), (x, hw * .42, -th)])
    return secs


def hilt(P, gw, gl, pr, lea_turns=8, guard_curve=0.0):
    # guarda
    g = box(-.022, 0, -gw, gw, -.011, .011, GUARD); bevel(g, .004, 2); smooth_angle(g, 50); P.append(g)
    for s in (-1, 1):
        P.append(ico((-.011, s * (gw + .004), 0), .016, GUARD, 1, .0, (1, 1, 1)))
        if guard_curve:
            P.append(curve_tube([(-.011, s * gw, 0), (-.011 + guard_curve * .5, s * (gw + .03), 0), (guard_curve, s * (gw + .05), 0)], .008, GUARD, res=4))
    # empuñadura
    secs = []
    for i in range(8):
        u = i / 7; x = -.022 - gl * u; r = .0125 + .003 * math.sin(u * math.pi)
        secs.append(ellipse(x, 0, 0, r, r * .8, 10, 'x'))
    P.append(loft('grip', secs, LEATHER_D, smooth=True))
    P.append(curve_tube(helix(-.024, -.022 - gl, .0138, lea_turns), .0035, LEATHER, res=4))
    # pomo
    p = ico((-.022 - gl - pr * .8, 0, 0), pr, GOLDB, 2, .0, (1, 1, .75)); P.append(p)
    P.append(prim('cyl', loc=(-.022 - gl - .004, 0, 0), rot=(0, math.pi / 2, 0), vertices=10, radius=.016, depth=.01, m=GUARD))


def weapons():
    # Daga
    P = [loft('b', blade_secs(.27, lambda u: .018 + .01 * math.sin(min(1, u / .75) * math.pi) * (1 - u * .2), .0045, (0, .5, .25), .3), STEEL)]
    hilt(P, .05, .1, .018, 6)
    done(P, 'Daga')
    # Espada
    P = [loft('b', blade_secs(.78, lambda u: .027 - .007 * u, .005, (.02, .62, .35), .16), STEEL)]
    hilt(P, .1, .17, .024, 9, .015)
    done(P, 'Espada')
    # Mandoble
    def hw(u):
        return .02 if u < .1 else .031 - .01 * u
    P = [loft('b', blade_secs(1.08, hw, .006, (.12, .7, .3), .12), STEEL)]
    for s in (-1, 1):
        P.append(box(.1, .125, s * .02, s * .045, -.005, .005, STEEL))
    hilt(P, .17, .32, .03, 14, .03)
    done(P, 'Mandoble')
    # Hacha: mango a lo largo de X, cabeza hacia +Y cerca de x=0
    P = []
    secs = []
    for i in range(10):
        u = i / 9; x = -.5 + .62 * u; r = .016 + .004 * math.sin(u * 3)
        secs.append(ellipse(x, 0, 0, r * .8, r, 10, 'x'))
    P.append(loft('haft', secs, WOODH, smooth=True))
    P.append(curve_tube(helix(-.5, -.34, .017, 6), .0038, LEATHER, res=4))
    P.append(prim('cyl', loc=(-.505, 0, 0), rot=(0, math.pi / 2, 0), vertices=10, radius=.02, depth=.012, m=GUARD))
    # cabeza: loft de secciones a lo largo de Y (del ojo al filo)
    hs = []
    for i in range(13):
        v = i / 12; y = .025 + .175 * v
        c = .05 - .03 * v ** 1.5         # el filo cae hacia el mango (barba)
        half = .032 + .085 * v ** 2.2
        th = .018 * (1 - v) ** 1.2 + .0016
        xs = [c - half, c - half * .5, c, c + half * .5, c + half]
        ring = [(x, y, th) for x in xs] + [(x, y, -th) for x in reversed(xs)]
        if i == 12: ring = [(x, y + .003 * (1 - abs(x - c) / half), 0) for x in xs] + [(x, y + .003 * (1 - abs(x - c) / half), 0) for x in reversed(xs)]
        hs.append(ring)
    P.append(loft('head', hs, STEEL))
    eye = box(.012, .088, -.04, .026, -.02, .02, STEEL); bevel(eye, .004, 1); P.append(eye)
    poll = box(.02, .08, -.06, -.039, -.017, .017, STEEL); bevel(poll, .003, 1); P.append(poll)
    done(P, 'Hacha')
    # Lingote
    ing = box(-.11, .11, -.026, .026, 0, .032, INGOT); bevel(ing, .007, 2); smooth_angle(ing, 50)
    done([ing], 'Lingote')


# =============== ARMERÍA Y DECORADO ===============
def decor():
    # Soporte: pletina + gancho en J (origen en la pared, el gancho sale a -Y)
    P = [box(-.02, .02, -.012, 0, -.05, .05, IRON_B)]
    P.append(curve_tube([(0, -.012, .0), (0, -.06, -.005), (0, -.085, .01), (0, -.085, .035)], .008, IRON_B, res=5))
    for z in (-.03, .03): P.append(ico((0, -.014, z), .006, RIVET, 1, 0))
    done(P, 'Soporte')
    # Pared de tablones (3 m x 2.6 m), origen abajo al centro, cara a -Y
    P = []; n = 12; w = 3.0 / n
    for i in range(n):
        x0 = -1.5 + i * w + .004; x1 = x0 + w - .008
        hh = 2.6 + random.uniform(-.02, .02); dd = .035 + random.uniform(-.006, .006)
        b = chamf(x1 - x0, hh, dd, .008, random.choice(PLANKS)); b.data.transform(Matrix.Rotation(math.pi / 2, 4, 'X')); b.location = ((x0 + x1) / 2, -dd / 2, hh / 2); P.append(b)
        for z in (.45, 2.1):
            P.append(prim('cone', loc=((x0 + x1) / 2, -.068, z), rot=(math.pi / 2, 0, 0), vertices=5, radius1=.009, radius2=.004, depth=.008, m=IRON_B))
    for z in (.45, 2.1):
        b = box(-1.5, 1.5, -.065, -.035, z - .06, z + .06, PLANKS[1]); bevel(b, .008, 1); P.append(b)
    done(P, 'Pared')
    # Ventana (marco + cruz + vidrio emisivo tenue)
    P = [box(-.42, .42, -.02, .02, 0, 1.05, OAKS[1], drop=())]
    P[0].data.materials[0] = OAKS[1]
    fr = []
    for (x0, x1, z0, z1) in ((-.46, .46, -.05, .03), (-.46, .46, 1.02, 1.1), (-.46, -.38, -.05, 1.1), (.38, .46, -.05, 1.1), (-.03, .03, 0, 1.05), (-.42, .42, .5, .56)):
        b = box(x0, x1, -.06, .01, z0, z1, OAKS[0]); fr.append(b)
    bpy.data.objects.remove(P[0], do_unlink=True)
    fr.append(box(-.38, .38, -.012, -.004, .03, 1.02, GLASSM))
    done(fr, 'Ventana')
    # Piedra de afilar
    P = []
    wheel = prim('cyl', loc=(0, 0, .72), rot=(math.pi / 2, 0, 0), vertices=32, radius=.27, depth=.08, m=GRIT); bevel(wheel, .015, 2); smooth_angle(wheel, 50); P.append(wheel)
    P.append(prim('cyl', loc=(0, 0, .72), rot=(math.pi / 2, 0, 0), vertices=10, radius=.018, depth=.42, m=IRON_B))
    for s in (-1, 1):
        P.append(curve_tube([(-.35, s * .19, 0), (0, s * .19, .72), (.35, s * .19, 0)], .03, OAKS[0], res=4))
        P.append(box(-.4, .4, s * .19 - .03, s * .19 + .03, .0, .05, OAKS[1]))
    P.append(curve_tube([(0, .21, .72), (0, .24, .72), (.13, .24, .72), (.13, .31, .72)], .01, IRON_B, res=4))
    P.append(prim('cyl', loc=(.13, .33, .72), rot=(math.pi / 2, 0, 0), vertices=10, radius=.015, depth=.07, m=WOODH))
    tr = box(-.25, .25, -.1, .1, .25, .42, OAKS[2]); bevel(tr, .01, 1); P.append(tr)
    P.append(box(-.23, .23, -.08, .08, .4, .405, WATER))
    for s in (-1, 1): P.append(box(-.25, .25, s * .12 - .015, s * .12 + .015, .0, .25, OAKS[1]))
    done(P, 'Piedra afilar')
    # Suelo de losas (5 x 4 m)
    P = []
    slab = chamf(1, 1, 1, .05, SLABS[0], 'slab')
    nx, ny, s = 10, 7, .5
    for i in range(nx):
        for j in range(ny):
            off = .25 if j % 2 else 0
            x = -2.5 + (i + .5) * s + off
            if x > 2.5: x -= 5
            P.append(dup(slab, loc=(x, -1.75 + (j + .5) * s, -.03 + random.uniform(-.003, .003)),
                         rot=(random.uniform(-.004, .004), random.uniform(-.004, .004), random.uniform(-.012, .012)),
                         sc=(s - .008, s - .008, .06), m=random.choice(SLABS)))
    bpy.data.objects.remove(slab, do_unlink=True)
    done(P, 'Suelo')
    # Antorcha de pared (origen en la pared)
    P = [box(-.04, .04, -.02, 0, -.08, .06, IRON_B)]
    P.append(curve_tube([(0, -.02, 0), (0, -.1, .04), (0, -.14, .1)], .01, IRON_B, res=4))
    P.append(prim('cone', loc=(0, -.16, .2), rot=(-.35, 0, 0), vertices=10, radius1=.02, radius2=.035, depth=.22, m=WOODH))
    P.append(ico((0, -.2, .33), .04, TORCH, 1, .1, (1, 1, 1.3)))
    done(P, 'Antorcha')
    # Cubo de carbón
    P = [lathe([(.13, 0), (.16, .3), (.165, .305), (.155, .305), (.12, .01), (0, .01)], HOOP, 'cubo', 24)]
    P.append(prim('torus', loc=(0, 0, .3), rot=(math.pi / 2, 0, 0), major_radius=.16, minor_radius=.004, major_segments=24, minor_segments=4, m=IRON_B))
    for i in range(9):
        a = random.uniform(0, math.tau); r = random.uniform(0, .11)
        P.append(ico((r * math.cos(a), r * math.sin(a), .28 + random.uniform(0, .03)), random.uniform(.03, .045), COAL, 1, .3))
    done(P, 'Cubo')


anvil(); stump(); forge(); embers(); hammer(); tongs(); bellows(); barrel(); weapons(); decor()

# ---------------- exportación (sin UV: los materiales no usan texturas; las UV de las hojas se generan en la app) ----------------
bpy.ops.object.select_all(action='DESELECT')
for n in ASSETS: bpy.data.objects[n].select_set(True)
bpy.ops.export_scene.gltf(filepath=ROOT + '/glb/forja.glb', export_format='GLB', use_selection=True, export_apply=True,
                          export_yup=True, export_materials='EXPORT', export_texcoords=False)
bpy.ops.wm.save_as_mainfile(filepath=ROOT + '/blend/forja.blend')
print('GLB', os.path.getsize(ROOT + '/glb/forja.glb'))

# ---------------- icono ----------------
if '--noicon' not in sys.argv:
    for n in ASSETS: bpy.data.objects[n].hide_render = True
    HOT = mat('Hoja al rojo', '#3a1206', .4, .3, emit='#ff7a22', emit_str=22)
    SPK = mat('Chispa', '#ffd27a', .5, 0, emit='#ffc15a', emit_str=30)
    fl = prim('plane', size=12, m=mat('Suelo icono', '#1c120d', .9))
    showcase(['Tocón', 'Yunque'], [(0, 0, 0), (0, 0, .5)], [(0, 0, 0), (0, 0, 0)], [1, 1])
    sw = bpy.data.objects['Espada']; d = sw.copy(); d.data = sw.data.copy(); C.collection.objects.link(d); d.hide_render = False
    for i, m in enumerate(d.data.materials):
        if m and m.name == 'Hoja': d.data.materials[i] = HOT
    d.location = (-.3, -.22, .803); d.rotation_euler = (0, 0, .78)
    hm = bpy.data.objects['Martillo']; h = hm.copy(); C.collection.objects.link(h); h.hide_render = False
    h.location = (.52, .02, 1.02); h.rotation_euler = (0, -.3, math.pi)
    random.seed(4)
    imp = Vector((.1, 0, .81))
    for k in range(34):
        a = random.uniform(0, math.tau); el = random.uniform(.15, 1.2); L = random.uniform(.05, .16)
        dv = Vector((math.cos(a) * math.cos(el), math.sin(a) * math.cos(el), math.sin(el)))
        p0 = imp + dv * random.uniform(.05, .45)
        c = curve_tube([tuple(p0), tuple(p0 + dv * L)], .0035, SPK, res=2)
    render_icon(ROOT + '/renders/forja.png', '#2a1710', (1.2, -1.45, 1.2), (-.02, 0, .7), lens=46, samples=56,
                lights=[('POINT', (-.7, -.6, 1.1), 260, '#ff7a2a'), ('AREA', (1.3, -1.4, 2.0), 260, '#ffd6a8'), ('AREA', (-.6, 1.3, 1.6), 220, '#8ea2b5'), ('POINT', (.05, -.1, .95), 25, '#ff8a3a')])
print('OK forja')
