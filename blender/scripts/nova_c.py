"""NOVA SURGE (app 31) · GRUPO C: jefes finales de sector.
Trituradora (+ Brazo_Sierra + Sierra), Hidra (Cabeza, Segmento, Cola), Acorazado (+ Torreta, Canon, Puente)
y NOVA (Nucleo, Placa, Anillo).

Convenciones (Blender, Z arriba; en three: x=x, y=z, z=-y):
- Morro / frente hacia +Y. El código gira 180º a los enemigos.
- Piezas que se montan sobre otra (Torreta, Canon, Puente): origen en el pivote, con z=0 en su base.
- Puntos de montaje y pivotes: ver MOUNTS al final (el programador del juego los usa tal cual).
Materiales: SOLO M('Nombre') de nova_mats.py. Presupuesto del grupo: GLB <= 380 KB.
"""
import math, random
import bpy, bmesh
from mathutils import Vector, Matrix, Euler
from blib import C, join, lathe
from nova_mats import M

TAU = math.tau
ASSETS = []


# ------------------------------------------------------------------ helpers de malla
def fixn(o):
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data); bm.free(); o.data.update()
    return o


def mk(name, verts, faces, mats, fmat=None, smooth=False, fix=True):
    me = bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces]); me.update()
    o = bpy.data.objects.new(name, me); C.collection.objects.link(o)
    for m in (mats if isinstance(mats, (list, tuple)) else [mats]): me.materials.append(m)
    if fmat:
        for i, p in enumerate(me.polygons): p.material_index = fmat[i]
    for p in me.polygons: p.use_smooth = smooth
    if fix: fixn(o)
    return o


def finish(o, deg=34):
    """suavizado por ángulo: comparte vértices en superficies curvas y deja aristas vivas (menos KB)."""
    for p in o.data.polygons: p.use_smooth = True
    try: o.data.set_sharp_from_angle(angle=math.radians(deg))
    except Exception: pass
    return o


def loft(name, secs, m, closed=True, cap0=True, cap1=True, smooth=False):
    verts, faces, idx = [], [], []
    for s in secs:
        idx.append(list(range(len(verts), len(verts) + len(s)))); verts += [tuple(p) for p in s]
    for a, b in zip(idx, idx[1:]):
        n = max(len(a), len(b))
        for i in (range(n) if closed else range(n - 1)):
            j = (i + 1) % n
            if len(a) == 1: faces.append((a[0], b[i], b[j]))
            elif len(b) == 1: faces.append((a[i], a[j], b[0]))
            else: faces.append((a[i], a[j], b[j], b[i]))
    if cap0 and len(idx[0]) > 2: faces.append(tuple(reversed(idx[0])))
    if cap1 and len(idx[-1]) > 2: faces.append(tuple(idx[-1]))
    return mk(name, verts, faces, m, smooth=smooth)


def xf(o, loc=(0, 0, 0), rot=(0, 0, 0), sc=None):
    m = Matrix.Translation(Vector(loc)) @ Euler(rot).to_matrix().to_4x4()
    if sc: m = m @ Matrix.Diagonal((*sc, 1))
    o.data.transform(m); o.data.update()
    return o


def cp(o):
    d = o.copy(); d.data = o.data.copy(); C.collection.objects.link(d); return d


def mx(o):
    """copia espejada en X (invierte el sentido de las caras para que las normales sigan fuera)."""
    d = cp(o); d.data.transform(Matrix.Scale(-1, 4, (1, 0, 0)))
    bm = bmesh.new(); bm.from_mesh(d.data); bmesh.ops.reverse_faces(bm, faces=bm.faces); bm.to_mesh(d.data); bm.free()
    d.data.update(); return d


def sym(o):
    return [o, mx(o)]


def around(o, n, a0=0.0):
    out = [o]
    for k in range(1, n):
        out.append(xf(cp(o), rot=(0, 0, a0 + k * TAU / n)))
    return out


def offset_poly(pts, d):
    n = len(pts)
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    s = 1 if area > 0 else -1
    out = []
    for i in range(n):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]

        def inn(a, b):
            ex, ey = b[0] - a[0], b[1] - a[1]; L = math.hypot(ex, ey) or 1
            return (-ey / L * s, ex / L * s)
        n1, n2 = inn(p0, p1), inn(p1, p2)
        k = 1 + n1[0] * n2[0] + n1[1] * n2[1]
        k = max(k, .35)
        out.append((p1[0] + (n1[0] + n2[0]) / k * d, p1[1] + (n1[1] + n2[1]) / k * d))
    return out


def prism(pts, z0, z1, m, ch=0.0, bottom=False, name='pr'):
    """extruye un contorno 2D; ch = chaflán superior. Sin cara inferior (no se ve desde la cámara)."""
    rings = [[(x, y, z0) for x, y in pts]]
    if ch > 0:
        rings.append([(x, y, z1 - ch) for x, y in pts])
        rings.append([(x, y, z1) for x, y in offset_poly(pts, ch)])
    else:
        rings.append([(x, y, z1) for x, y in pts])
    return loft(name, rings, m, cap0=bottom, cap1=True)


def rect(x0, x1, y0, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def rbox(cx, cy, sx, sy):
    return rect(cx - sx / 2, cx + sx / 2, cy - sy / 2, cy + sy / 2)


def box(x0, x1, y0, y1, z0, z1, m, ch=0.0, bottom=False):
    return prism(rect(x0, x1, y0, y1), z0, z1, m, ch, bottom)


def circ(r, n, a0=0.0, cx=0.0, cy=0.0):
    return [(cx + r * math.cos(a0 + i / n * TAU), cy + r * math.sin(a0 + i / n * TAU)) for i in range(n)]


def arcpoly(r0, r1, a0, a1, n=4):
    """sector de corona (plano)"""
    out = [(r1 * math.cos(a0 + (a1 - a0) * i / n), r1 * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
    out += [(r0 * math.cos(a1 - (a1 - a0) * i / n), r0 * math.sin(a1 - (a1 - a0) * i / n)) for i in range(n + 1)]
    return out


def tube(p0, p1, r0, r1, m, n=8, cap0=True, cap1=True, smooth=True):
    a, b = Vector(p0), Vector(p1); d = (b - a).normalized()
    t = Vector((0, 0, 1)) if abs(d.z) < .9 else Vector((1, 0, 0))
    u = d.cross(t).normalized(); v = d.cross(u)
    ring = lambda c, r: [tuple(c + (u * math.cos(i / n * TAU) + v * math.sin(i / n * TAU)) * r) for i in range(n)]
    secs = [ring(a, r0), ring(b, r1) if r1 > 0 else [tuple(b)]]
    o = loft('tb', secs, m, cap0=cap0, cap1=cap1 and r1 > 0)
    if smooth:
        for p in o.data.polygons: p.use_smooth = abs(Vector(p.normal).dot(d)) < .5
    return o


def cyl(x, y, z0, z1, r, m, n=12, smooth=True):
    return tube((x, y, z0), (x, y, z1), r, r, m, n, cap0=False, smooth=smooth)


def decal(c, u, v, m):
    """quad plano: c ± u ± v, normal = u × v (sin recalcular)."""
    c, u, v = Vector(c), Vector(u), Vector(v)
    vs = [c - u - v, c + u - v, c + u + v, c - u + v]
    return mk('dc', vs, [(0, 1, 2, 3)], m, fix=False)


def dot(x, y, z, s, m, rz=0.0):
    """luz / pegatina plana mirando a +Z"""
    u = (s * math.cos(rz), s * math.sin(rz), 0); v = (-s * math.sin(rz), s * math.cos(rz), 0)
    return decal((x, y, z), u, v, m)


def disc(x, y, z, r, m, n=8):
    vs = [(x + r * math.cos(i / n * TAU), y + r * math.sin(i / n * TAU), z) for i in range(n)]
    return mk('ds', vs, [tuple(range(n))], m, fix=False)


def hazard(L, W, n, z=0.0, sh=None):
    """franja de peligro plana a lo largo de +X (0..L), centrada en Y, mirando a +Z"""
    sh = W * .8 if sh is None else sh
    s = L / n; verts, faces, fm = [], [], []
    cl = lambda x: min(max(x, 0.0), L)
    for k in range(-1, n + 1):
        xb0, xb1, xt0, xt1 = cl(k * s - sh / 2), cl((k + 1) * s - sh / 2), cl(k * s + sh / 2), cl((k + 1) * s + sh / 2)
        if xb1 - xb0 < 1e-5 and xt1 - xt0 < 1e-5: continue
        b = len(verts)
        verts += [(xb0, -W / 2, z), (xb1, -W / 2, z), (xt1, W / 2, z), (xt0, W / 2, z)]
        faces.append((b, b + 1, b + 2, b + 3)); fm.append(k % 2)
    o = mk('hz', verts, faces, [M('Peligro_Amarillo'), M('Peligro_Negro')], fm, fix=False)
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-6)
    bm.to_mesh(o.data); bm.free()
    return o


def inset(o, pred, t=.06, d=-.03, mi=None):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
    fs = [f for f in bm.faces if pred(f)]
    if fs:
        bmesh.ops.inset_individual(bm, faces=fs, thickness=t, depth=d, use_even_offset=True)
        if mi is not None:
            for f in fs: f.material_index = mi
    bm.to_mesh(o.data); bm.free(); o.data.update()
    return o


def fin(y0, y1, zb, h, th, m, back=.15, x=0.0):
    """aleta dorsal triangular en el plano YZ (punta inclinada hacia -Y), grosor th en X"""
    pts = [(y0, zb), (y1, zb), (y0 - back, zb + h)]
    vs = [(x - th / 2, y, z) for y, z in pts] + [(x + th / 2, y, z) for y, z in pts]
    return mk('fin', vs, [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)], m)


def dome(cx, cy, cz, r, rz, mats, nlon=24, nlat=4, slit=None):
    """casquete (hemisferio superior). slit: semiancho angular (rad) de la pupila alrededor de ±Y -> material 1"""
    verts, faces, fm = [], [], []
    rings = []
    for j in range(nlat):
        lat = j / nlat * (math.pi / 2)
        ring = []
        for i in range(nlon):
            lon = i / nlon * TAU
            ring.append(len(verts)); verts.append((cx + r * math.cos(lat) * math.cos(lon), cy + r * math.cos(lat) * math.sin(lon), cz + rz * math.sin(lat)))
        rings.append(ring)
    top = len(verts); verts.append((cx, cy, cz + rz))

    def mat_of(i):
        if slit is None: return 0
        lon = (i + .5) / nlon * TAU
        return 1 if min(abs(lon - math.pi / 2), abs(lon - 3 * math.pi / 2)) < slit else 0
    for j in range(nlat - 1):
        for i in range(nlon):
            k = (i + 1) % nlon
            faces.append((rings[j][i], rings[j][k], rings[j + 1][k], rings[j + 1][i])); fm.append(mat_of(i))
    for i in range(nlon):
        k = (i + 1) % nlon
        faces.append((rings[-1][i], rings[-1][k], top)); fm.append(mat_of(i))
    return mk('dome', verts, faces, mats, fm, smooth=True)


def hexsec(y, w, zt, zm, zb, tw=.6, bw=.6):
    return [(w, y, zm), (w * tw, y, zt), (-w * tw, y, zt), (-w, y, zm), (-w * bw, y, zb), (w * bw, y, zb)]


def octsec(y, w, h, zc=0.0, c=.35):
    return [(w, y, zc - h * (1 - c)), (w, y, zc + h * (1 - c)), (w * (1 - c * .9), y, zc + h), (-w * (1 - c * .9), y, zc + h),
            (-w, y, zc + h * (1 - c)), (-w, y, zc - h * (1 - c)), (-w * (1 - c * .9), y, zc - h), (w * (1 - c * .9), y, zc - h)]


GLOW = {'Enemigo_Luz', 'Punto_Debil', 'Nova_Costura', 'Nova_Plasma', 'Luz_Blanca', 'Motor'}


def glow_smooth(o):
    """las piezas 100 % emisivas no necesitan normales partidas: se suavizan para compartir vértices (menos KB en el GLB)"""
    ms = [m.name for m in o.data.materials if m]
    if ms and all(n in GLOW for n in ms):
        for p in o.data.polygons: p.use_smooth = True
        a = o.data.attributes.get('sharp_edge')
        if a: o.data.attributes.remove(a)
        a = o.data.attributes.get('sharp_face')
        if a: o.data.attributes.remove(a)


def done(P, name, origin=(0, 0, 0)):
    for o in P: glow_smooth(o)
    o = join(P, name, origin)
    ASSETS.append(name)
    return o


top_up = lambda f, k=.9: f.normal.z > k


# ================================================================== TRITURADORA
def octr(ap, z, n=8):
    R = ap / math.cos(math.pi / n); ph = math.pi / n
    return [(R * math.cos(ph + i * TAU / n), R * math.sin(ph + i * TAU / n), z) for i in range(n)]


def trituradora():
    E, EP, L, MD, S = M('Enemigo'), M('Enemigo_Panel'), M('Enemigo_Luz'), M('Metal_Oscuro'), M('Sierra')
    P = []
    # casco octogonal con faldón y cubierta
    hull = loft('tr_hull', [octr(1.7, -.7), octr(2.3, -.42), octr(2.42, -.26), octr(2.42, .26), octr(2.18, .44), octr(1.9, .58)], [E, EP])
    diag = lambda f: abs(abs(f.normal.x) - abs(f.normal.y)) < .25 and abs(f.normal.x) > .3
    inset(hull, lambda f: abs(f.normal.z) < .2 and diag(f), .1, -.05, 1)
    inset(hull, lambda f: .3 < f.normal.z < .9, .08, -.03, 1)
    P.append(finish(hull, 30))
    # placas de cubierta en las diagonales (entre los anclajes)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        P.append(prism(arcpoly(1.42, 1.84, a - .44, a + .44, 3), .58, .7, EP, ch=.04))
        # chimenea de extracción
        cx, cy = 1.62 * math.cos(a + .52), 1.62 * math.sin(a + .52)
        P.append(cyl(cx, cy, .58, 1.14, .19, E, n=8))
        P.append(disc(cx, cy, 1.141, .13, L, 8))
        # luces de cubierta
        P.append(dot(1.95 * math.cos(a - .2), 1.95 * math.sin(a - .2), .52, .05, L, a))
        # toma de mineral (en la diagonal, sobresale del casco)
        tk = []
        h = prism([(2.1, -.5), (3.0, -.36), (3.0, .36), (2.1, .5)], -.34, .3, E, ch=.08)
        tk.append(h)
        tk.append(decal((3.006, 0, -.04), (0, .3, 0), (0, 0, .21), MD))
        for zz in (-.16, -.04, .08):
            tk.append(decal((3.012, 0, zz), (0, .26, 0), (0, 0, .022), L))
        tk.append(decal((2.5, 0, .301), (.3, 0, 0), (0, .24, 0), EP))
        for o in tk: xf(o, rot=(0, 0, a))
        P += tk
    # carriles de peligro hacia cada brazo
    for k in range(4):
        hz = xf(hazard(.5, .4, 4, .585), loc=(1.36, 0, 0))
        P.append(xf(hz, rot=(0, 0, k * math.pi / 2)))
    # anclajes de los 4 brazos (en +X y girados)
    for k in range(4):
        a = k * math.pi / 2; an = []
        an.append(prism([(2.05, -.78), (2.95, -.62), (2.95, .62), (2.05, .78)], -.46, .5, E, ch=.1))
        for sy in (-1, 1):
            an.append(decal((2.5, sy * .705, 0), (.36, sy * -.07, 0), (0, 0, -.2 * sy), EP))
        end = [(2.6, -.5), (3.0, -.5)] + [(3.0 + .5 * math.cos(-math.pi / 2 + i / 4 * math.pi), .5 * math.sin(-math.pi / 2 + i / 4 * math.pi)) for i in range(1, 4)] + [(3.0, .5), (2.6, .5)]
        an.append(prism(end, .3, .48, E))
        an.append(cyl(3.0, 0, -.5, .56, .17, MD, n=10))
        an.append(disc(3.0, 0, .561, .1, L, 8))
        an.append(xf(hazard(.34, .5, 3, .49), loc=(2.62, 0, 0)))
        an.append(dot(2.9, .38, .505, .045, L)); an.append(dot(2.9, -.38, .505, .045, L))
        for o in an: xf(o, rot=(0, 0, a))
        P += an
    # collar del ojo (cubo central)
    col = lathe([(1.34, .56), (1.3, .86), (1.08, 1.07), (.86, 1.02), (.8, .84)], E, 'col', steps=16)
    P.append(finish(col, 40))
    # dientes trituradores alrededor del ojo
    for k in range(8):
        a = k * TAU / 8 + TAU / 16
        t = prism([(1.02, -.15), (1.02, .15), (.66, .03), (.66, -.03)], .96, 1.14, S)
        P.append(xf(t, rot=(0, 0, a)))
        P.append(dot(1.2 * math.cos(a + TAU / 16), 1.2 * math.sin(a + TAU / 16), 1.0, .04, L, a))
    P.append(cyl(0, 0, .74, .86, .82, MD, n=16))
    P.append(disc(0, 0, .861, .82, MD, 16))
    P.append(dome(0, 0, .82, .58, .44, [M('Punto_Debil'), MD], nlon=20, nlat=4, slit=.17))
    # antenas
    for a, h in ((math.radians(20), 1.0), (math.radians(200), .8)):
        x, y = 1.6 * math.cos(a), 1.6 * math.sin(a)
        P.append(tube((x, y, .6), (x, y, .6 + h), .035, .02, E, n=5))
        P.append(dot(x, y, .61 + h, .06, L))
    return done(P, 'Trituradora')


# ================================================================== BRAZO_SIERRA
SAW_AT = (0.0, 3.45, 0.62)   # centro de la Sierra respecto al origen del Brazo_Sierra


def brazo():
    E, EP, L, MD, S = M('Enemigo'), M('Enemigo_Panel'), M('Enemigo_Luz'), M('Metal_Oscuro'), M('Sierra')
    P = []
    # nudillo (va entre las horquillas del anclaje)
    P.append(cyl(0, 0, -.26, .26, .42, E, n=14))
    P.append(disc(0, 0, .261, .42, E, 14))
    P.append(cyl(0, 0, .26, .32, .24, MD, n=10)); P.append(disc(0, 0, .321, .24, MD, 10))
    P.append(disc(0, 0, .325, .09, L, 6))
    # brazo superior
    up = loft('up', [octsec(.25, .3, .19), octsec(.5, .38, .23), octsec(1.7, .33, .2), octsec(1.95, .24, .15)], [E, EP])
    inset(up, lambda f: f.normal.z > .95, .05, -.02, 1)
    P.append(finish(up, 30))
    # codo
    P.append(cyl(0, 2.05, -.22, .22, .31, MD, n=12)); P.append(disc(0, 2.05, .221, .31, MD, 12))
    P.append(disc(0, 2.05, .225, .12, L, 6))
    # antebrazo
    fo = loft('fo', [octsec(2.2, .26, .17), octsec(2.4, .31, .2), octsec(3.05, .29, .18), octsec(3.2, .24, .15)], [E, EP])
    P.append(finish(fo, 30))
    P.append(xf(hazard(.6, .3, 4, .205), rot=(0, 0, math.pi / 2), loc=(0, 2.45, 0)))
    # hidráulicos
    P.append(tube((0, .45, .3), (0, 1.3, .3), .09, .09, MD, n=8))
    P.append(tube((0, 1.3, .3), (0, 1.95, .26), .045, .045, S, n=6, cap0=False))
    P.append(box(-.1, .1, .38, .52, .2, .36, E))
    for sx in (-1, 1):
        P.append(tube((sx * .34, 2.3, .02), (sx * .34, 2.85, .02), .07, .07, MD, n=6))
        P.append(tube((sx * .34, 2.85, .02), (sx * .3, 3.25, .02), .035, .035, S, n=5, cap0=False))
        P.append(decal((sx * .381, 1.1, 0), (0, sx * .5, 0), (0, 0, .11), EP))
        P.append(decal((sx * .383, 1.7, .03), (0, sx * .06, 0), (0, 0, .05), L))
    # motor de la sierra
    x, y = SAW_AT[0], SAW_AT[1]
    P.append(cyl(x, y, -.18, .42, .42, E, n=14)); P.append(disc(x, y, .421, .42, E, 14))
    P.append(cyl(x, y, .2, .32, .46, EP, n=14))
    P.append(cyl(x, y, .42, .56, .15, MD, n=8))
    for k in range(4):
        a = k * TAU / 4 + TAU / 8
        P.append(dot(x + .3 * math.cos(a), y + .3 * math.sin(a), .425, .035, L, a))
    return done(P, 'Brazo_Sierra')


# ================================================================== SIERRA
def sierra():
    S, MD, L, PA = M('Sierra'), M('Metal_Oscuro'), M('Enemigo_Luz'), M('Peligro_Amarillo')
    P = []
    N = 16; R0, R1, Rm, Ri, H = .92, 1.1, .74, .3, .045
    prof = []
    for k in range(N):
        a = k / N * TAU; s = TAU / N
        prof += [(a, R0), (a + .38 * s, R0 - .07), (a + .86 * s, R1)]
    n = len(prof)
    verts, faces, fm = [], [], []
    ot = [len(verts) + i for i in range(n)]; verts += [(r * math.cos(a), r * math.sin(a), H) for a, r in prof]
    ob = [len(verts) + i for i in range(n)]; verts += [(r * math.cos(a), r * math.sin(a), -H) for a, r in prof]
    mt = [len(verts) + i for i in range(n)]; verts += [(Rm * math.cos(a), Rm * math.sin(a), H) for a, r in prof]
    it = [len(verts) + i for i in range(n)]; verts += [(Ri * math.cos(a), Ri * math.sin(a), H + .02) for a, r in prof]
    mt2 = [len(verts) + i for i in range(n)]; verts += [(Rm * math.cos(a), Rm * math.sin(a), H + .02) for a, r in prof]
    for i in range(n):
        j = (i + 1) % n
        faces.append((ot[i], ot[j], mt[j], mt[i])); fm.append(0)       # corona dentada
        faces.append((mt[i], mt[j], mt2[j], mt2[i])); fm.append(0)     # escalón
        faces.append((mt2[i], mt2[j], it[j], it[i])); fm.append(1 if (i // 3) % 4 == 0 else 0)   # plato con franjas oscuras
        faces.append((ob[j], ob[i], ot[i], ot[j])); fm.append(0)       # canto
    o = mk('saw', verts, faces, [S, MD], fm)
    P.append(finish(o, 30))
    # buje, tornillos y marcas asimétricas (para que se lea el giro)
    P.append(cyl(0, 0, H, H + .14, .3, MD, n=12)); P.append(disc(0, 0, H + .141, .3, MD, 12))
    P.append(disc(0, 0, H + .145, .11, L, 8))
    for k in range(6):
        a = k * TAU / 6
        P.append(dot(.2 * math.cos(a), .2 * math.sin(a), H + .143, .03, S, a))
    for k in range(3):
        a = k * TAU / 3 + .3
        tri = [(.5 * math.cos(a + .18), .5 * math.sin(a + .18), H + .021), (.5 * math.cos(a - .18), .5 * math.sin(a - .18), H + .021), (.7 * math.cos(a), .7 * math.sin(a), H + .021)]
        P.append(mk('mk', tri, [(0, 1, 2)], PA, fix=False))
    return done(P, 'Sierra')


# ================================================================== HIDRA
def keelsec(y, w, zt, zm, zb, ks=.82, bw=.6):
    """sección con quilla central (lomo en V muy abierta): lee como cráneo de víbora desde arriba"""
    return [(w, y, zm), (w * .66, y, zt * ks), (0, y, zt), (-w * .66, y, zt * ks), (-w, y, zm), (-w * bw, y, zb), (w * bw, y, zb)]


def hidra_cabeza():
    E, EP, L, MD, S, PD = M('Enemigo'), M('Enemigo_Panel'), M('Enemigo_Luz'), M('Metal_Oscuro'), M('Sierra'), M('Punto_Debil')
    P = []
    # cráneo de víbora: ancho en las bisagras de la mandíbula, hocico estrecho hacia +Y
    sk = loft('skull', [keelsec(-1.3, .5, .44, .08, -.24), keelsec(-.85, .92, .6, .1, -.22), keelsec(-.3, .98, .62, .06, -.14),
                        keelsec(.35, .7, .5, .02, -.1), keelsec(.95, .4, .34, -.02, -.1), keelsec(1.32, .16, .18, -.05, -.09),
                        keelsec(1.45, .05, .08, -.06, -.08)], [E, EP])
    inset(sk, lambda f: f.normal.z > .8 and -1.1 < f.calc_center_median().y < .4, .11, -.03, 1)
    P.append(finish(sk, 28))
    # quilla blindada sobre el lomo (se lee la dirección de ataque)
    P.append(loft('keel', [[(.07, -1.2, .44), (0, -1.2, .52), (-.07, -1.2, .44)], [(.08, -.3, .6), (0, -.3, .7), (-.08, -.3, .6)],
                           [(.06, .8, .37), (0, .8, .44), (-.06, .8, .37)], [(0, 1.2, .24)]], E, closed=False, cap0=True, cap1=False))
    # mandíbula inferior abierta (se ve el rojo de las fauces por delante del hocico)
    jaw = loft('jaw', [hexsec(-.7, .6, -.12, -.25, -.4), hexsec(.2, .6, -.12, -.25, -.42), hexsec(.9, .36, -.12, -.2, -.3), hexsec(1.45, .1, -.12, -.15, -.2)], E)
    jaw.data.transform(Matrix.Translation((0, -.7, -.12)) @ Matrix.Rotation(math.radians(-12), 4, 'X') @ Matrix.Translation((0, .7, .12)))
    P.append(finish(jaw, 28))
    P.append(prism([(-.44, -.5), (.44, -.5), (.2, 1.3), (-.2, 1.3)], -.2, -.13, L))
    for sx in (-1, 1):
        P.append(tube((sx * .14, 1.28, -.06), (sx * .12, 1.36, -.44), .07, 0, S, n=5))
        P.append(tube((sx * .3, .9, -.05), (sx * .28, .94, -.3), .05, 0, S, n=4))
        P.append(dot(sx * .1, 1.36, .1, .035, L))                      # fosas sensoras
    # mandíbulas-pinza: nacen en la bisagra y abrazan el hocico por fuera (silueta de tenaza vista desde arriba)
    for sx in (-1, 1):
        secs = []
        K = 7
        for i in range(K):
            t = i / K
            cx = sx * (1.0 + .28 * math.sin(math.pi * t) - .72 * t); cy = -.45 + 2.05 * t; cz = -.02 + .06 * math.sin(math.pi * t)
            w, h = .2 * (1 - t) + .045, .14 * (1 - t) + .035
            secs.append([(cx + w, cy, cz), (cx, cy, cz + h), (cx - w, cy, cz), (cx, cy, cz - h)])
        secs.append([(sx * .24, 1.78, .02)])
        P.append(finish(loft('md', secs, [S]), 40))
        # dientes de sierra en el borde interior de la pinza
        for t in (.35, .55, .75):
            cx = sx * (1.0 + .28 * math.sin(math.pi * t) - .72 * t); cy = -.45 + 2.05 * t
            P.append(tube((cx, cy, .0), (cx - sx * .26, cy + .08, .0), .05, 0, MD, n=4))
        # pistón de la bisagra y luz
        P.append(cyl(sx * .98, -.45, -.12, .24, .2, MD, n=8)); P.append(disc(sx * .98, -.45, .241, .2, MD, 8))
        P.append(disc(sx * .98, -.45, .245, .08, L, 6))
        P.append(tube((sx * .98, -.45, .16), (sx * 1.12, .35, .14), .045, .045, S, n=5))
    # capucha de cobra detrás (flecos blindados)
    for sx in (-1, 1):
        hood = [(.82, -.2), (1.42, -.62), (1.5, -1.1), (1.2, -1.36), (.6, -1.26)]
        hood = [(sx * x, y) for x, y in hood]
        if sx < 0: hood = hood[::-1]
        P.append(prism(hood, .04, .18, EP, ch=.05))
        for (x, y) in ((1.33, -.68), (1.42, -1.06), (1.16, -1.28)):
            P.append(dot(sx * x, y, .182, .045, L))
        P.append(tube((sx * .8, -.4, .19), (sx * 1.34, -1.12, .19), .035, .035, E, n=4))
        P.append(tube((sx * .72, -.7, .19), (sx * 1.04, -1.3, .19), .035, .035, E, n=4))
    # ojos (PUNTOS DÉBILES): dos pares de rendijas en cuencas oscuras, mirando arriba y hacia fuera
    for sx in (-1, 1):
        for (x, y, z, L0, W0, rz) in ((.5, .3, .43, .5, .16, 24), (.72, -.35, .5, .3, .11, 14)):
            eye = [(0, L0 / 2), (W0, L0 * .1), (W0 * .6, -L0 / 2), (-W0 * .5, -L0 * .3), (-W0 * .6, L0 * .2)]
            sock = offset_poly(eye, -.05)
            for (poly, mm, z0, z1, ch) in ((sock, MD, z - .12, z + .03, 0), (eye, PD, z - .05, z + .08, .03)):
                pts = [(px * sx, py) for px, py in poly]
                if sx < 0: pts = pts[::-1]
                o = prism(pts, z0, z1, mm, ch=ch)
                P.append(xf(o, loc=(sx * x, y, 0), rot=(0, 0, -sx * math.radians(rz))))
    # cuernos traseros y cuello
    for sx in (-1, 1):
        P.append(tube((sx * .42, -.95, .46), (sx * .8, -1.56, .68), .11, 0, E, n=6))
    P.append(tube((0, -1.3, 0), (0, -1.5, 0), .34, .34, MD, n=10))
    return done(P, 'Hidra_Cabeza')


def seg_body(E, EP, MD, L, y0=-.75, y1=.75, w=.8, h=.42):
    P = []
    b = loft('sb', [octsec(y0, w * .7, h * .7), octsec(y0 + .15, w, h), octsec(y1 - .2, w, h), octsec(y1, w * .74, h * .76)], E)
    P.append(finish(b, 30))
    return P


def hidra_segmento():
    E, EP, L, MD, S = M('Enemigo'), M('Enemigo_Panel'), M('Enemigo_Luz'), M('Metal_Oscuro'), M('Sierra')
    P = seg_body(E, EP, MD, L)
    # caparazón en cheurón (indica sentido de avance)
    P.append(prism([(-.6, -.62), (0, -.38), (.6, -.62), (.66, .28), (0, .64), (-.66, .28)], .36, .5, EP, ch=.05))
    # aletas laterales
    for sx in (-1, 1):
        f = [(.74, .32), (1.02, -.18), (1.0, -.56), (.74, -.34)]
        f = [(sx * x, y) for x, y in f]
        if sx < 0: f = f[::-1]
        P.append(prism(f, -.08, .08, E, ch=.03))
        P.append(dot(sx * .96, -.42, .082, .045, L))
        P.append(decal((sx * .805, .1, -.05), (0, sx * .3, 0), (0, 0, .06), L))
    # acoples
    P.append(tube((0, .72, 0), (0, .92, 0), .3, .3, MD, n=10))
    P.append(tube((0, -.92, 0), (0, -.72, 0), .36, .36, MD, n=10))
    # torreta
    P.append(cyl(0, -.08, .46, .58, .36, MD, n=12))
    tur = lathe([(.3, .56), (.3, .66), (.22, .78), (0.0, .82)], E, 'tur', steps=10)
    xf(tur, loc=(0, -.08, 0)); P.append(finish(tur, 40))
    for sx in (-1, 1):
        P.append(tube((sx * .08, .1, .68), (sx * .08, .58, .68), .045, .045, MD, n=6))
    P.append(box(-.14, .14, .12, .26, .6, .76, E))
    P.append(dot(0, .1, .79, .05, L))
    return done(P, 'Hidra_Segmento')


def hidra_cola():
    E, EP, L, MD, S = M('Enemigo'), M('Enemigo_Panel'), M('Enemigo_Luz'), M('Metal_Oscuro'), M('Sierra')
    P = []
    b = loft('tl', [octsec(.8, .6, .34), octsec(.55, .64, .36), octsec(.02, .5, .28), octsec(-.08, .44, .25),
                    octsec(-.55, .36, .2), octsec(-.65, .3, .17), octsec(-1.05, .18, .1), octsec(-1.15, .12, .07)], E)
    P.append(finish(b, 30))
    P.append(prism([(-.5, -.05), (0, .15), (.5, -.05), (.52, .6), (0, .82), (-.52, .6)], .26, .38, EP, ch=.04))
    P.append(prism([(-.34, -.62), (0, -.48), (.34, -.62), (.38, -.12), (0, .04), (-.38, -.12)], .16, .26, EP, ch=.03))
    # aguijón
    vs = [(0, -1.0, 0), (-.36, -1.35, 0), (0, -2.05, 0), (.36, -1.35, 0), (0, -1.3, .09), (0, -1.3, -.09)]
    fs = [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (1, 0, 5), (2, 1, 5), (3, 2, 5), (0, 3, 5)]
    P.append(mk('st', vs, fs, S))
    P.append(tube((0, -1.05, .06), (0, -1.75, .03), .03, .01, L, n=4))
    for sx in (-1, 1):
        f = [(.46, .1), (.78, -.35), (.72, -.6), (.42, -.3)]
        f = [(sx * x, y) for x, y in f]
        if sx < 0: f = f[::-1]
        P.append(prism(f, -.06, .06, E, ch=.03))
        P.append(dot(sx * .68, -.5, .062, .04, L))
    P.append(tube((0, .78, 0), (0, .95, 0), .3, .3, MD, n=10))
    return done(P, 'Hidra_Cola', origin=(0, -.55, 0))


# ================================================================== ACORAZADO
# montajes (coordenadas en el Acorazado, z = altura de la base de la pieza)
TURRETS = [(-1.75, 3.35, .72), (1.75, 3.35, .72), (-3.55, -2.9, .52), (3.55, -2.9, .52)]
CANNON = (0.0, 1.35, .72)
BRIDGE = (0.0, -2.0, .6)
HANGARS = [(-1.65, -5.3, .6), (1.65, -5.3, .6)]   # centro de la boca de cada hangar (salen hacia +Y)


def acorazado():
    E, EP, L, MD, S, LB = M('Enemigo'), M('Enemigo_Panel'), M('Enemigo_Luz'), M('Metal_Oscuro'), M('Sierra'), M('Luz_Blanca')
    P = []

    def sec(y, wd, wb, wk, zd=.6, zb=.22, zk=-.65):
        return [(wd, y, zd), (wb, y, zb), (wk, y, zk), (-wk, y, zk), (-wb, y, zb), (-wd, y, zd)]
    hull = loft('hull', [sec(7.0, .14, .18, .04, .5, .3, .05), sec(5.8, 1.05, 1.2, .42, .56, .24, -.35), sec(3.8, 2.2, 2.45, 1.05),
                         sec(1.5, 2.95, 3.2, 1.55), sec(-4.2, 3.05, 3.3, 1.75), sec(-6.4, 2.85, 3.1, 1.65), sec(-6.95, 2.6, 2.8, 1.45, .55, .2, -.5)], [E, EP])
    # cinturón blindado en los costados
    inset(hull, lambda f: abs(f.normal.z) < .5 and f.calc_center_median().y < 5, .12, -.04, 1)
    P.append(finish(hull, 25))
    # alas laterales (sponsons) con borde dentado
    for sx in (-1, 1):
        w = [(2.85, 2.2), (4.45, .7), (4.5, -.9), (4.05, -1.3), (4.42, -2.1), (4.42, -4.1), (3.0, -5.7)]
        wi = offset_poly(w[::-1], .28)[::-1]
        if sx < 0:
            w = [(-x, y) for x, y in w][::-1]; wi = [(-x, y) for x, y in wi][::-1]
        else:
            w = w[::-1]; wi = wi[::-1]
        P.append(prism(w, -.1, .46, E, ch=.12))
        P.append(prism(wi, .46, .5, EP))
        # motor del ala
        P.append(tube((sx * 3.7, -4.9, .12), (sx * 3.7, -6.0, .12), .3, .36, MD, n=10))
        P.append(disc(0, 0, 0, .28, L, 10)); xf(P[-1], loc=(sx * 3.7, -6.01, .12), rot=(math.pi / 2, 0, 0))
        # antenas en la punta del ala
        P.append(tube((sx * 4.2, .45, .46), (sx * 4.2, .45, 1.45), .035, .02, E, n=5))
        P.append(dot(sx * 4.2, .45, 1.46, .07, L))
        # luces del borde
        for (x, y) in ((4.3, .1), (4.3, -.7), (4.28, -2.5), (4.28, -3.4)):
            P.append(dot(sx * x, y, .505, .05, L))
    # --- proa: foso del cañón, raíles y cheurones
    P.append(box(-.5, .5, 2.4, 6.3, .6, .62, MD))
    for sx in (-1, 1):
        P.append(box(sx * .5 - .12, sx * .5 + .12, 2.3, 6.4, .6, .78, EP, ch=.05))
    for i, y in enumerate((2.9, 3.6, 4.3, 5.0, 5.7)):
        P.append(dot(0, y, .625, .08, LB if i % 2 else L))
    for sx in (-1, 1):
        for y0 in (4.0, 5.0):
            wd = lambda y: 2.2 + (1.05 - 2.2) * (y - 3.8) / 2.0
            ch = [(sx * .8, y0), (sx * (wd(y0) - .2), y0 - .5), (sx * (wd(y0 + .45) - .2), y0 - .05), (sx * .8, y0 + .45)]
            if sx < 0: ch = ch[::-1]
            P.append(prism(ch, .56, .66, EP))
    # --- montajes de torretas y cañón (anillos) — deja el hueco libre
    for (x, y, z) in TURRETS:
        P.append(cyl(x, y, z - .14, z, .72, MD, n=12)); P.append(disc(x, y, z + .001, .72, MD, 12))
        P.append(xf(hazard(.3, .12, 3, z + .004), loc=(x - .15, y - .66, 0)))
        for k in range(4):
            a = k * TAU / 4 + TAU / 8
            P.append(dot(x + .64 * math.cos(a), y + .64 * math.sin(a), z + .005, .04, L, a))
    x, y, z = CANNON
    P.append(cyl(x, y, .6, z, 1.1, MD, n=16)); P.append(disc(x, y, z + .001, 1.1, MD, 16))
    for k in range(10):
        a = k * TAU / 10
        P.append(dot(x + 1.02 * math.cos(a), y + 1.02 * math.sin(a), z + .005, .045, L, a))
    # --- zona central: plataforma del puente y placas de cubierta
    bx, by, bz = BRIDGE
    P.append(box(bx - 1.75, bx + 1.75, by - 1.2, by + 1.2, .6, bz + .06, MD))
    for sx in (-1, 1):
        for i, y0 in enumerate((-.5, .35)):
            x0, x1 = sorted((sx * 1.35, sx * 2.65))
            P.append(box(x0, x1, y0, y0 + .7, .6, .67, EP if i else E, ch=.03))
        # rejillas de ventilación
        for k in range(5):
            xx = sx * (1.3 + k * .26)
            P.append(decal((xx, -1.3, .63), (.07, 0, 0), (0, .35, 0), MD))
        P.append(decal((sx * 1.82, -1.3, .605), (.7, 0, 0), (0, .38, 0), L))
        # radar
        rd = lathe([(.02, 0), (.3, .12), (.36, .2)], E, 'rd', steps=10)
        xf(rd, loc=(sx * 2.4, -3.6, .75), rot=(math.radians(-25), 0, 0)); P.append(finish(rd, 50))
        P.append(tube((sx * 2.4, -3.6, .6), (sx * 2.4, -3.6, .78), .05, .05, MD, n=5))
    # --- popa: hangares, espina y motores
    for (hx, hy, hz) in HANGARS:
        sxn = 1 if hx > 0 else -1
        P.append(box(hx - .75, hx + .75, hy - 1.05, hy + .95, .6, .62, MD))           # suelo oscuro
        P.append(box(hx - .82, hx - .66, hy - 1.1, hy + .95, .6, .98, E, ch=.04))       # paredes
        P.append(box(hx + .66, hx + .82, hy - 1.1, hy + .95, .6, .98, E, ch=.04))
        P.append(box(hx - .82, hx + .82, hy - 1.25, hy - 1.05, .6, .98, E, ch=.04))
        P.append(box(hx - .66, hx + .66, hy - 1.05, hy - .2, .9, .96, EP))              # compuerta a medio abrir
        P.append(decal((hx, hy - 1.04, .78), (0, 0, .12), (.6, 0, 0), L))
        for k in range(3):
            P.append(dot(hx - .4 + k * .4, hy + .1, .625, .06, L))
        P.append(xf(hazard(1.64, .16, 8, .985), loc=(hx - .82, hy + .87, 0)))
        for k in range(3):
            P.append(dot(hx, hy + 1.25 + k * .38, .605, .06, LB))
    P.append(box(-.72, .72, -6.7, -3.3, .6, .98, E, ch=.1))
    for k in range(6):
        yy = -6.3 + k * .5
        P.append(decal((0, yy, .99), (.5, 0, 0), (0, .08, 0), MD))
    P.append(decal((0, -4.8, .985), (.55, 0, 0), (0, 1.4, 0), L))
    for (x, r) in ((-1.55, .44), (0, .5), (1.55, .44)):
        P.append(tube((x, -6.7, .1), (x, -7.25, .1), r * .9, r, MD, n=12))
        P.append(disc(0, 0, 0, r * .85, L, 12)); xf(P[-1], loc=(x, -7.26, .1), rot=(math.pi / 2, 0, 0))
    for sx in (-1, 1):
        P.append(tube((sx * 2.4, -6.4, .6), (sx * 2.4, -6.4, 1.6), .035, .02, E, n=5))
        P.append(dot(sx * 2.4, -6.4, 1.61, .07, L))
    # luces del borde del casco
    for sx in (-1, 1):
        for y in (6.0, 5.2, 4.4, 3.2, 2.2, -4.8):
            t = (y - 3.8) / 2.0
            wd = 2.2 + (1.05 - 2.2) * t if y > 3.8 else (2.95 + (2.2 - 2.95) * (y - 1.5) / 2.3 if y > 1.5 else 3.0)
            P.append(dot(sx * (wd - .12), y, .605, .045, L))
    return done(P, 'Acorazado')


def acorazado_torreta():
    E, EP, L, MD = M('Enemigo'), M('Enemigo_Panel'), M('Enemigo_Luz'), M('Metal_Oscuro')
    P = []
    P.append(cyl(0, 0, 0, .14, .6, MD, n=14))
    h0 = [(-.58, -.45), (-.3, -.62), (.3, -.62), (.58, -.45), (.52, .3), (.28, .46), (-.28, .46), (-.52, .3)]
    h1 = [(x * .78, y * .78 - .04) for x, y in h0]
    sh = loft('th', [[(x, y, .12) for x, y in h0], [(x, y, .36) for x, y in h0], [(x, y, .55) for x, y in h1]], [E, EP], cap0=False)
    inset(sh, lambda f: f.normal.z > .95, .07, -.02, 1)
    P.append(finish(sh, 30))
    P.append(box(-.3, .3, .38, .56, .2, .48, MD, ch=.04))
    for sx in (-1, 1):
        P.append(tube((sx * .15, .5, .34), (sx * .15, 1.0, .34), .065, .065, MD, n=8))
        P.append(tube((sx * .15, .66, .34), (sx * .15, .74, .34), .085, .085, E, n=8))
        P.append(tube((sx * .15, .9, .34), (sx * .15, 1.04, .34), .09, .09, E, n=8))
        P.append(disc(0, 0, 0, .06, L, 6)); xf(P[-1], loc=(sx * .15, 1.042, .34), rot=(-math.pi / 2, 0, 0))
    # lomo blindado, escotilla y rejilla trasera sobre la cubierta
    P.append(box(-.06, .06, -.42, .3, .52, .6, E, ch=.02))
    P.append(cyl(.22, -.18, .52, .6, .11, MD, n=8)); P.append(disc(.22, -.18, .601, .11, MD, 8))
    for k in range(3):
        yy = -.44 + k * .07
        P.append(box(-.36, -.12, yy - .02, yy + .02, .52, .57, MD))
    P.append(dot(-.22, .18, .556, .05, L))
    P.append(tube((-.3, -.4, .5), (-.3, -.4, .9), .02, .012, E, n=4))
    P.append(dot(-.3, -.4, .905, .04, L))
    return done(P, 'Acorazado_Torreta')


def acorazado_canon():
    E, EP, L, MD, S = M('Enemigo'), M('Enemigo_Panel'), M('Enemigo_Luz'), M('Metal_Oscuro'), M('Sierra')
    P = []
    P.append(cyl(0, 0, 0, .2, 1.0, MD, n=18))
    hs = [(-.85, -1.0), (.85, -1.0), (.95, -.2), (.7, .95), (-.7, .95), (-.95, -.2)]
    h = prism(hs, .15, .85, [E, EP], ch=.16)
    inset(h, lambda f: f.normal.z > .95, .1, -.03, 1)
    P.append(finish(h, 30))
    for sx in (-1, 1):
        P.append(tube((sx * .98, -.85, .45), (sx * .98, .55, .45), .16, .16, EP, n=8))
        P.append(dot(sx * .6, -.75, .853, .05, L))
        # condensadores de carga a los lados del canal
        for yy in (-.45, -.1, .25):
            P.append(tube((sx * .16, yy, .9), (sx * .58, yy, .9), .075, .075, MD, n=6))
            P.append(tube((sx * .3, yy, .9), (sx * .38, yy, .9), .09, .09, S, n=6))
    # canal de energía (se ilumina al cargar el láser)
    P.append(box(-.07, .07, -.7, .85, .8, .86, L))
    # cañón de raíles
    for sx in (-1, 1):
        P.append(box(sx * .22 - .08, sx * .22 + .08, .7, 3.95, .38, .7, E, ch=.04))
    P.append(box(-.14, .14, .7, 3.9, .4, .5, L))
    for k in range(5):
        y = 1.2 + k * .6
        P.append(box(-.38, .38, y - .09, y + .09, .34, .76, MD, ch=.03))
    P.append(prism([(-.45, 3.8), (.45, 3.8), (.38, 4.12), (-.38, 4.12)], .32, .78, E, ch=.05))
    P.append(decal((0, 4.121, .55), (0, 0, .12), (.24, 0, 0), L))
    P.append(box(-.22, .22, -1.0, -.7, .85, .98, MD))
    return done(P, 'Acorazado_Canon')


def acorazado_puente():
    E, EP, L, MD, PD = M('Enemigo'), M('Enemigo_Panel'), M('Enemigo_Luz'), M('Metal_Oscuro'), M('Punto_Debil')
    P = []
    P.append(prism([(-1.5, -1.0), (1.5, -1.0), (1.5, .55), (1.1, 1.0), (-1.1, 1.0), (-1.5, .55)], 0, .7, E, ch=.1))
    # nivel medio con banda de ventanas
    t1 = [(-1.2, -.85), (1.2, -.85), (1.2, .45), (.9, .78), (-.9, .78), (-1.2, .45)]
    P.append(prism(t1, .7, .95, E))
    P.append(prism(offset_poly(t1, .05), .95, 1.12, PD))
    P.append(prism(t1, 1.12, 1.32, E, ch=.06))
    # nivel superior
    t2 = [(-.8, -.7), (.8, -.7), (.8, .2), (.55, .45), (-.55, .45), (-.8, .2)]
    P.append(prism(t2, 1.32, 1.46, EP))
    P.append(prism(offset_poly(t2, .04), 1.46, 1.58, PD))
    P.append(prism(t2, 1.58, 1.7, E, ch=.05))
    # alerones del puente
    for sx in (-1, 1):
        P.append(box(min(sx * 1.2, sx * 1.55), max(sx * 1.2, sx * 1.55), -.1, .5, 1.0, 1.08, E))
        P.append(dot(sx * 1.5, .4, 1.085, .04, L))
    # mástil, radar y antenas
    P.append(tube((0, -.3, 1.7), (0, -.3, 2.05), .07, .05, MD, n=6))
    rd = lathe([(.02, 0), (.22, .08), (.26, .14)], E, 'rd2', steps=10)
    xf(rd, loc=(0, -.3, 2.02), rot=(math.radians(20), 0, 0)); P.append(finish(rd, 50))
    for sx in (-1, 1):
        P.append(tube((sx * .6, -.55, 1.7), (sx * .6, -.55, 2.1), .025, .015, E, n=4))
        P.append(dot(sx * .6, -.55, 2.105, .04, L))
    P.append(decal((0, -.2, 1.705), (.45, 0, 0), (0, .18, 0), EP))
    return done(P, 'Acorazado_Puente')


# ================================================================== NOVA
def sp(r, lon, lat):
    return (r * math.cos(lat) * math.cos(lon), r * math.cos(lat) * math.sin(lon), r * math.sin(lat))


def spatch(lon0, lon1, lat0, lat1, r0, r1, m, n=3):
    verts, faces, idx = [], [], {}
    L = lambda i, j: (lon0 + (lon1 - lon0) * i / n, lat0 + (lat1 - lat0) * j / n)
    for i in range(n + 1):
        for j in range(n + 1):
            idx[i, j] = len(verts); verts.append(sp(r1, *L(i, j)))
    for i in range(n):
        for j in range(n):
            faces.append((idx[i, j], idx[i + 1, j], idx[i + 1, j + 1], idx[i, j + 1]))
    border = [(i, 0) for i in range(n)] + [(n, j) for j in range(n)] + [(i, n) for i in range(n, 0, -1)] + [(0, j) for j in range(n, 0, -1)]
    base = []
    for (i, j) in border:
        base.append(len(verts)); verts.append(sp(r0, *L(i, j)))
    B = len(border)
    for k in range(B):
        faces.append((base[k], base[(k + 1) % B], idx[border[(k + 1) % B]], idx[border[k]]))
    o = mk('sp', verts, faces, m)
    return finish(o, 55)


def nova_nucleo():
    B, K, PL = M('Nova_Blindaje'), M('Nova_Costura'), M('Nova_Plasma')
    P = []
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=7, radius=1.9)
    me = bpy.data.meshes.new('core'); bm.to_mesh(me); bm.free()
    core = bpy.data.objects.new('core', me); C.collection.objects.link(core); me.materials.append(K)
    for p in me.polygons: p.use_smooth = True
    P.append(core)
    g = math.radians(3.2)
    bands = [(-46, -16, 7), (-12, 12, 8), (16, 46, 7), (50, 78, 5)]   # la banda polar inferior no se ve desde la cámara
    plasma = {(1, 1), (1, 5), (0, 3), (2, 6), (3, 2)}
    for bi, (la0, la1, n) in enumerate(bands):
        la0, la1 = math.radians(la0), math.radians(la1)
        cl = math.cos((la0 + la1) / 2)
        off = (bi % 2) * .5
        for k in range(n):
            lo0 = (k + off) / n * TAU + g / cl; lo1 = (k + 1 + off) / n * TAU - g / cl
            if (bi, k) in plasma:
                # placa partida: dos medias placas que se abren y dejan ver una grieta de plasma
                gm = (lo1 - lo0) * .17; lm = (lo0 + lo1) / 2
                P.append(spatch(lo0, lm - gm, la0, la1, 1.86, 2.02, B, 1))
                P.append(spatch(lm + gm, lo1, la0, la1, 1.86, 2.02, B, 1))
                P.append(spatch(lm - gm - .03, lm + gm + .03, la0 + .03, la1 - .03, 1.84, 1.95, PL, 1))
                # costilla de sujeción que cruza la grieta
                lt = (la0 + la1) / 2
                P.append(spatch(lm - gm - .02, lm + gm + .02, lt - .035, lt + .035, 1.9, 2.0, B, 1))
            else:
                thick = 2.06 if bi == 1 else 2.0
                P.append(spatch(lo0, lo1, la0, la1, 1.86, thick, B, 1 if bi == 0 else 2))
    # casquetes polares de plasma con corona
    for sgn in (1,):
        cap = dome(0, 0, 0, .52, .1, [PL], nlon=12, nlat=2)
        xf(cap, loc=(0, 0, sgn * 1.9))
        P.append(cap)
        for k in range(6):
            a = k * TAU / 6
            P.append(spatch(a - .12, a + .12, sgn * math.radians(71), sgn * math.radians(80), 1.88, 2.1, B, 1))
    # aletas coronales en el ecuador (rompen la silueta circular vista desde arriba)
    for k in range(8):
        a = k * TAU / 8 + TAU / 16
        f = prism([(1.9, -.06), (2.32, -.03), (2.32, .03), (1.9, .06)], -.2, .2, B, bottom=True)
        P.append(xf(f, rot=(0, 0, a)))
        P.append(xf(decal((2.321, 0, 0), (0, .03, 0), (0, 0, .16), K), rot=(0, 0, a)))
    return done(P, 'Nova_Nucleo')


def nova_placa():
    B, K, PL = M('Nova_Blindaje'), M('Nova_Costura'), M('Nova_Plasma')
    P = []
    nx, ny = 6, 3
    Rs = 3.0

    def pt(u, v, top=True):
        hw = 1.2 * (1 + .1 * v)
        x = u * hw; y = v * .8 - .22 * (u ** 2) + .11
        z = math.sqrt(max(Rs * Rs - x * x - (v * .8) ** 2, 0)) - Rs + .32
        return (x, y, z if top else z - .2)
    verts, faces, fm = [], [], []
    top = {}; bot = {}
    for i in range(nx + 1):
        for j in range(ny + 1):
            u, v = -1 + 2 * i / nx, -1 + 2 * j / ny
            top[i, j] = len(verts); verts.append(pt(u, v))
            bot[i, j] = len(verts); verts.append(pt(u, v, False))
    for i in range(nx):
        for j in range(ny):
            faces.append((top[i, j], top[i + 1, j], top[i + 1, j + 1], top[i, j + 1])); fm.append(0)
            faces.append((bot[i, j], bot[i, j + 1], bot[i + 1, j + 1], bot[i + 1, j])); fm.append(0)
    border = [(i, 0) for i in range(nx)] + [(nx, j) for j in range(ny)] + [(i, ny) for i in range(nx, 0, -1)] + [(0, j) for j in range(ny, 0, -1)]
    Bn = len(border)
    for k in range(Bn):
        a, b = border[k], border[(k + 1) % Bn]
        faces.append((bot[a], bot[b], top[b], top[a])); fm.append(1 if a[1] == ny and b[1] == ny else 0)
    o = mk('pl', verts, faces, [B, K], fm)
    P.append(finish(o, 35))
    # costuras incandescentes y runas sobre la cara superior
    for (u0, u1, v) in ((-.9, .9, -.45), (-.9, .9, .45)):
        pts = [pt(u0 + (u1 - u0) * t / 6, v) for t in range(7)]
        for a, b in zip(pts, pts[1:]):
            d = Vector(b) - Vector(a); c = (Vector(a) + Vector(b)) / 2 + Vector((0, 0, .012))
            P.append(decal(c, d / 2, Vector((0, .025, 0)), K))
    for (u, v, w, h) in ((-.55, 0, .09, .22), (-.35, .05, .2, .04), (0, 0, .045, .26), (0, 0, .2, .045), (.35, -.05, .2, .04), (.55, 0, .09, .22)):
        c = Vector(pt(u, v)) + Vector((0, 0, .014))
        P.append(decal(c, (w / 2, 0, 0), (0, h / 2, 0), PL if (u == 0) else K))
    for u in (-.85, .85):
        for v in (-.7, .7):
            c = Vector(pt(u, v)) + Vector((0, 0, .012))
            P.append(disc(c.x, c.y, c.z, .05, K, 6))
    return done(P, 'Nova_Placa')


def nova_anillo():
    B, K, PL = M('Nova_Blindaje'), M('Nova_Costura'), M('Nova_Plasma')
    P = []
    R, w, h, N = 3.2, .3, .22, 10
    gap = math.radians(4.5)

    def block(a0, a1, ww, hh, m, steps=2, caps=True):
        secs = []
        for s in range(steps + 1):
            a = a0 + (a1 - a0) * s / steps; c, sn = math.cos(a), math.sin(a)
            pr = [(ww, 0), (ww * .55, hh), (-ww * .55, hh), (-ww, 0), (-ww * .55, -hh), (ww * .55, -hh)]
            secs.append([((R + dx) * c, (R + dx) * sn, dz) for dx, dz in pr])
        return loft('ab', secs, m, cap0=caps, cap1=caps)
    def lining(a0, a1, side=-1, steps=3):
        """franja emisiva sobre la cara inclinada interior (side=-1) o exterior (side=1): perfila el anillo visto desde arriba"""
        nx_, nz_ = .85 * side, .52; e = .006
        prof = [(side * (w * .55 + w * .45 * t) + nx_ * e, h - h * t + nz_ * e) for t in (.12, .8)]
        vs, fs = [], []
        for s in range(steps + 1):
            a = a0 + (a1 - a0) * s / steps; c, sn = math.cos(a), math.sin(a)
            vs += [((R + dx) * c, (R + dx) * sn, dz) for dx, dz in prof]
        for s in range(steps):
            i = 2 * s; fs.append((i, i + 2, i + 3, i + 1))
        o = mk('ln', vs, fs, K, fix=False)
        if o.data.polygons[0].normal.z < 0:
            for p in o.data.polygons: p.flip()
        return o
    for k in range(N):
        a0 = k * TAU / N + gap / 2; a1 = (k + 1) * TAU / N - gap / 2
        P.append(finish(block(a0, a1, w, h, B), 35))
        P.append(lining(a0 + .03, a1 - .03, -1)); P.append(lining(a0 + .05, a1 - .05, 1))
        P.append(block(a1 - .02, a1 + gap + .02, w * .62, h * .6, K, 1, caps=False))
        # runa en la cara superior (varía por segmento)
        am = (a0 + a1) / 2; c, s = math.cos(am), math.sin(am)
        t = Vector((-s, c, 0)); r = Vector((c, s, 0))
        base = r * R + Vector((0, 0, h + .006))
        pat = [(0, 0, .16, .025), (((k % 3) - 1) * .06, .0, .025, .1)] if k % 4 else [(0, 0, .03, .12), (-.07, 0, .025, .07), (.07, 0, .025, .07)]
        for (dt, dr, ht, hr) in pat:
            P.append(decal(base + t * dt + r * dr, r * hr, t * ht, K))
    for k in range(4):
        a = k * TAU / 4 + TAU / 32
        # nodo de plasma: cristal bipiramidal hexagonal (facetado, barato)
        ring = [(.38 * math.cos(i * TAU / 6), .38 * math.sin(i * TAU / 6), 0) for i in range(6)]
        ob = mk('node', ring + [(0, 0, .4), (0, 0, -.4)], [(i, (i + 1) % 6, 6) for i in range(6)] + [((i + 1) % 6, i, 7) for i in range(6)], PL)
        xf(ob, rot=(0, 0, a))
        xf(ob, loc=(R * math.cos(a), R * math.sin(a), 0), sc=(1, 1, .85)); P.append(ob)
        P.append(finish(block(a - .2, a + .2, w * 1.12, h * 1.2, B, 2), 35))
    return done(P, 'Nova_Anillo')


# ================================================================== montaje (para el programador del juego)
# Coordenadas Blender (x, y, z) relativas al ORIGEN del objeto padre. En three: (x, z, -y); rz de Blender = ry en three.
MOUNTS = {
    # 4 brazos: posición del pivote (origen del Brazo_Sierra) y giro Z para que el brazo (que crece hacia +Y) salga radial
    'Trituradora': {'brazos': [(3.0 * math.cos(k * math.pi / 2), 3.0 * math.sin(k * math.pi / 2), 0.0, k * math.pi / 2 - math.pi / 2) for k in range(4)],
                    'ojo': (0.0, 0.0, 1.0), 'radio': 3.1},
    'Brazo_Sierra': {'sierra': SAW_AT, 'radio_sierra': 1.1},
    'Hidra': {'cabeza_a_segmento': 2.35, 'paso_segmento': 1.75, 'segmento_a_cola': 2.35, 'radio_segmento': .9, 'radio_cabeza': 1.3},
    'Acorazado': {'torretas': TURRETS, 'canon': CANNON, 'puente': (BRIDGE[0], BRIDGE[1], BRIDGE[2] + .06), 'hangares': HANGARS},
    'Nova': {'radio_placas': 3.3, 'radio_nucleo': 2.0, 'radio_anillo': 3.5},
}


# ================================================================== build
def build():
    random.seed(31)
    trituradora(); brazo(); sierra()
    hidra_cabeza(); hidra_segmento(); hidra_cola()
    acorazado(); acorazado_torreta(); acorazado_canon(); acorazado_puente()
    nova_nucleo(); nova_placa(); nova_anillo()
    return list(ASSETS)
