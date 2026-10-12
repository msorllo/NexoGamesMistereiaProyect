"""NOVA SURGE (app 31) · GRUPO A: jugador, recogibles, entorno y enemigos pequeños.
Ejes de Blender: Z arriba, morro de las naves hacia +Y (en three: -Z = arriba de la pantalla). Origen en el centro del
asset a la altura z=0 salvo que se indique. Materiales SOLO de nova_mats.M().

Pivotes y notas para el código:
- Nave: origen en el centro (z=0 = plano del ala). Toberas en x=±0.23, y=-0.78 (z=0.025). Cañones en x=±0.1, y=+0.5.
- Dron: escolta del jugador; cañón en y=+0.26.
- Torreta_Base: origen abajo en el centro (z=0 = suelo). La Torreta_Cabeza se coloca en (0, 0, 0.34) de la base
  (en three: y=+0.34). Torreta_Cabeza: origen en el eje de giro (base de la cabeza), cañones hacia +Y, bocas en
  x=±0.1, y=+0.76, z=0.12.
- Plataforma: origen en el centro de la cubierta (z=0 = superficie donde se posa la nave); el cuerpo queda por debajo.
- Casco_Panel: 8x8 que tesela en Y (x∈[-4,4], y∈[-4,4]); la chapa superior está en z=0 y los greebles suben hasta ~0.6.
- Tuberia: eje a lo largo de Y (8 de largo, tesela en Y), eje del tubo en z=0.
- Antena: origen en la base (z=0), sube hasta z=3.
- Asteroides/Mina/Baliza/Roca_Azufre: origen en el centro de masa.
"""
import math, random
import bpy, bmesh
from mathutils import Vector, Matrix
from blib import C, prim, bevel, join, displace
from nova_mats import M

TAU = math.tau
OUT = []
RNG = random.Random(31)


# =====================================================================================  utilidades
def fixn(o):
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data); bm.free(); o.data.update()
    return o


def mk(name, verts, faces, mats, fmat=None, fix=True):
    me = bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces]); me.update()
    o = bpy.data.objects.new(name, me); C.collection.objects.link(o)
    for m in (mats if isinstance(mats, (list, tuple)) else [mats]): me.materials.append(m)
    if fmat:
        for i, p in enumerate(me.polygons): p.material_index = fmat[i]
    if fix: fixn(o)
    return o


def area(pts):
    return sum(pts[i - 1][0] * pts[i][1] - pts[i][0] * pts[i - 1][1] for i in range(len(pts))) / 2


def ccw(pts):
    return list(pts) if area(pts) > 0 else list(reversed(pts))


def symo(half):
    """half: puntos x>=0 del centro delantero al centro trasero -> contorno simétrico completo (CCW)"""
    return ccw(list(half) + [(-x, y) for x, y in reversed(half[1:-1])])


def circ(r, n, a0=0.0, cx=0.0, cy=0.0, sy=1.0):
    return [(cx + r * math.cos(a0 + i / n * TAU), cy + sy * r * math.sin(a0 + i / n * TAU)) for i in range(n)]


def offset2d(pts, d):
    """contorno CCW encogido d (miter)"""
    n = len(pts); out = []
    for i in range(n):
        p0, p1, p2 = Vector(pts[i - 1]), Vector(pts[i]), Vector(pts[(i + 1) % n])
        e1 = (p1 - p0).normalized(); e2 = (p2 - p1).normalized()
        n1 = Vector((-e1.y, e1.x)); n2 = Vector((-e2.y, e2.x))
        b = n1 + n2
        b = n1 if b.length < 1e-6 else b.normalized()
        out.append(tuple(p1 + b * (d / max(.35, b.dot(n1)))))
    return out


def prism(pts, z0, z1, m, inner=None, name='pr'):
    n = len(pts)
    if inner is None:
        v = [(x, y, z0) for x, y in pts] + [(x, y, z1) for x, y in pts]
        f = [tuple(range(n))[::-1], tuple(range(n, 2 * n))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    else:
        v = [(x, y, z0) for x, y in pts] + [(x, y, z1) for x, y in pts] + [(x, y, z0) for x, y in inner] + [(x, y, z1) for x, y in inner]
        ob, ot, ib, it = 0, n, 2 * n, 3 * n; f = []
        for i in range(n):
            j = (i + 1) % n
            f += [(ot + i, ot + j, it + j, it + i), (ob + i, ib + i, ib + j, ob + j), (ob + i, ob + j, ot + j, ot + i), (ib + i, it + i, it + j, ib + j)]
    return mk(name, v, f, m)


def plate(pts, z0, z1, m, ch=0.0, pm=None, pin=.05, pd=.01, rise=False, name='pl'):
    """prisma con la arista superior achaflanada (ch) y panel insertado opcional de material pm"""
    pts = ccw(pts)
    bm = bmesh.new()
    b = [bm.verts.new((x, y, z0)) for x, y in pts]
    t = [bm.verts.new((x, y, z1 - ch)) for x, y in pts]
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n; bm.faces.new((b[i], b[j], t[j], t[i]))
    top = bm.faces.new(t); bm.faces.new(list(reversed(b)))
    if ch > 0: bmesh.ops.inset_region(bm, faces=[top], thickness=ch, depth=ch, use_even_offset=True)
    mats = [m]
    if pm is not None:
        bmesh.ops.inset_region(bm, faces=[top], thickness=pin, depth=(pd if rise else -pd), use_even_offset=True)
        top.material_index = 1; mats.append(pm)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); C.collection.objects.link(o)
    for mm in mats: me.materials.append(mm)
    return o


def box(x0, x1, y0, y1, z0, z1, m, drop=()):
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = {'b': (0, 3, 2, 1), 't': (4, 5, 6, 7), '-y': (0, 1, 5, 4), '+y': (2, 3, 7, 6), '-x': (3, 0, 4, 7), '+x': (1, 2, 6, 5)}
    return mk('box', v, [f[k] for k in f if k not in drop], m, fix=False)


def ell(cx, cy, cz, rx, rz, n=12, a0=0.0):
    """anillo perpendicular a Y"""
    return [(cx + rx * math.cos(a0 + i / n * TAU), cy, cz + rz * math.sin(a0 + i / n * TAU)) for i in range(n)]


def loft(secs, mats, cap0=True, cap1=True, band=None, name='loft'):
    verts, faces, idx, fm = [], [], [], []
    for s in secs:
        idx.append(list(range(len(verts), len(verts) + len(s)))); verts += s
    for k, (a, b) in enumerate(zip(idx, idx[1:])):
        n = max(len(a), len(b))
        for i in range(n):
            j = (i + 1) % n
            if len(a) == 1: faces.append((a[0], b[i], b[j]))
            elif len(b) == 1: faces.append((a[i], a[j], b[0]))
            else: faces.append((a[i], a[j], b[j], b[i]))
            fm.append(band[k] if band else 0)
    if cap0 and len(idx[0]) > 2: faces.append(tuple(reversed(idx[0]))); fm.append(band[0] if band else 0)
    if cap1 and len(idx[-1]) > 2: faces.append(tuple(idx[-1])); fm.append(band[-1] if band else 0)
    return mk(name, verts, faces, mats, fm if band else None)


def revolve_y(profile, m, n=12, cx=0.0, cz=0.0, a0=0.0):
    """perfil cerrado (r, y) girado alrededor de un eje paralelo a Y que pasa por (cx, ·, cz)"""
    rings = [[(cx + r * math.cos(a0 + i / n * TAU), y, cz + r * math.sin(a0 + i / n * TAU)) for i in range(n)] for r, y in profile]
    verts = [p for rg in rings for p in rg]; faces = []; K = len(rings)
    for k in range(K):
        a, b = k * n, ((k + 1) % K) * n
        for i in range(n):
            j = (i + 1) % n; faces.append((a + i, a + j, b + j, b + i))
    return mk('rev', verts, faces, m)


def cylb(p0, p1, r, m, n=8, r2=None, cap=True):
    """cilindro (o cono si r2) de p0 a p1; cap=False sin tapas (cuando quedan ocultas)"""
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0
    rot = tuple(d.to_track_quat('Z', 'Y').to_euler())
    fill = 'NGON' if cap else 'NOTHING'
    if r2 is None:
        return prim('cyl', loc=tuple((p0 + p1) / 2), rot=rot, vertices=n, radius=r, depth=d.length, m=m, end_fill_type=fill)
    return prim('cone', loc=tuple((p0 + p1) / 2), rot=rot, vertices=n, radius1=r, radius2=r2, depth=d.length, m=m, end_fill_type=fill)


PERM = Matrix(((0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)))   # (a,b,c) -> x=c, y=a, z=b


def fin(pts_yz, t, m):
    """aleta: contorno en el plano (y, z), grosor t en X"""
    o = prism(ccw(pts_yz), -t / 2, t / 2, m); o.data.transform(PERM); o.data.update(); return o


def xf(o, m4):
    if o.location.length > 0:
        o.data.transform(Matrix.Translation(o.location)); o.location = (0, 0, 0)
    o.data.transform(m4); o.data.update(); return o


def symx(o):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); C.view_layer.objects.active = o
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    md = o.modifiers.new('mr', 'MIRROR'); md.use_axis[0] = True; md.use_mirror_merge = True; md.merge_threshold = 1e-4
    bpy.ops.object.modifier_apply(modifier='mr')
    return o


def mirror(objs):
    return symx(join(objs, 'tmp_mirror'))


def done(parts, name, origin=(0, 0, 0), sharp=62, flat=False, strip=None):
    """une, fija el origen y sombrea. strip=umbral: borra las caras que miran hacia abajo (normal.z < strip), que la
    cámara del juego (siempre por encima, ~35º) nunca ve; ahorra triángulos y KB del GLB."""
    o = join(parts, name, origin)
    me = o.data
    if strip is not None:
        bm = bmesh.new(); bm.from_mesh(me)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.normal.z < strip], context='FACES')
        bm.to_mesh(me); bm.free(); me.update()
    if flat:
        for p in me.polygons: p.use_smooth = False
    else:
        for p in me.polygons: p.use_smooth = True
        try: me.set_sharp_from_angle(angle=math.radians(sharp))
        except Exception: pass
        # normales ponderadas por área: caras grandes planas, biseles redondeados, sin partir vértices
        wn = o.modifiers.new('wn', 'WEIGHTED_NORMAL'); wn.keep_sharp = True; wn.mode = 'FACE_AREA'; wn.weight = 50
        bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); C.view_layer.objects.active = o
        bpy.ops.object.modifier_apply(modifier='wn')
    while me.uv_layers: me.uv_layers.remove(me.uv_layers[0])
    OUT.append(name)
    return o


def stripe(p0, p1, w0, w1, z0, z1, m, side=None):
    """banda recta entre p0 y p1 (2D) de w0 a w1 hacia la normal izquierda"""
    a, b = Vector(p0), Vector(p1); u = (b - a).normalized(); n = Vector((-u.y, u.x))
    return prism(ccw([tuple(a + n * w0), tuple(b + n * w0), tuple(b + n * w1), tuple(a + n * w1)]), z0, z1, m)




def decal(pts, z, m):
    """calcomanía: una sola cara plana (mirando a +Z) a la altura z. Para franjas, luces y marcas finas: ahorra las
    caras laterales y la inferior, que desde la cámara del juego no se ven."""
    pts = ccw(pts)
    return mk('dc', [(x, y, z) for x, y in pts], [tuple(range(len(pts)))], m, fix=False)


def ring_decal(ro, ri, n, z, m, cx=0.0, cy=0.0, a0=0.0):
    """anillo plano (corona circular) mirando a +Z"""
    o = circ(ro, n, a0, cx, cy); i = circ(ri, n, a0, cx, cy)
    v = [(x, y, z) for x, y in o] + [(x, y, z) for x, y in i]
    return mk('rd', v, [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)], m, fix=False)
# =====================================================================================  JUGADOR
def nave():
    """Caza del jugador: morro afilado, cabina oscura, tomas de aire laterales, alas en flecha con franja ácida,
    dos góndolas con toberas emisivas y derivas inclinadas. 1.5 de largo, 1.3 de envergadura."""
    CAS, ACE, CAB, MOT = M('Casco'), M('Casco_Acento'), M('Cabina'), M('Motor')
    P, S = [], []
    # --- fuselaje con quilla lateral (chine): (y, media anchura, techo, suelo)
    FS = [(.62, .034, .034, -.016), (.47, .07, .07, -.034), (.3, .1, .102, -.048), (.1, .122, .122, -.056),
          (-.14, .126, .118, -.058), (-.4, .108, .1, -.052), (-.58, .07, .074, -.04)]

    def sec(y, w, zt, zb):
        return [(w, y, .004), (w * .74, y, zt * .8), (w * .3, y, zt), (-w * .3, y, zt), (-w * .74, y, zt * .8),
                (-w, y, .004), (-w * .6, y, zb), (w * .6, y, zb)]
    P.append(loft([[(0, .76, .006)]] + [sec(*s) for s in FS], CAS))

    def ztop(y):
        pts = [(s[0], s[2]) for s in FS]
        if y >= pts[0][0]: return pts[0][1]
        for (y0, z0), (y1, z1) in zip(pts, pts[1:]):
            if y1 <= y <= y0: return z0 + (z1 - z0) * (y - y0) / (y1 - y0)
        return pts[-1][1]

    def half(cx, y, cz, rx, rz, n=7):
        return [(cx + rx * math.cos(i / (n - 1) * math.pi), y, cz + rz * math.sin(i / (n - 1) * math.pi)) for i in range(n)]
    # --- cabina: burbuja alargada y marco
    cs = []
    for y, rx, rz in [(.52, 0, 0), (.46, .026, .022), (.38, .045, .044), (.27, .057, .06), (.16, .057, .058),
                      (.07, .046, .042), (.0, .026, .022), (-.04, 0, 0)]:
        zc = ztop(y) - .01
        cs.append([(0, y, zc + .002)] if rx == 0 else half(0, y, zc, rx, rz))
    P.append(loft(cs, CAB))
    zf = ztop(.2) - .01
    P.append(loft([half(0, .215, zf, .062, .066), half(0, .195, zf, .062, .066)], CAS))
    # --- lomo oscuro con respiraderos ácidos
    def ridge(y0, y1, hw, dz0, dz1, m, n=5):
        ss = []
        for i in range(n + 1):
            y = y0 + (y1 - y0) * i / n; z = ztop(y)
            ss.append([(hw, y, z - dz0), (hw * .75, y, z + dz1), (-hw * .75, y, z + dz1), (-hw, y, z - dz0)])
        return loft(ss, m)
    P.append(ridge(-.03, -.56, .044, .02, .01, ACE))
    for y in (-.2, -.28, -.36):
        P.append(ridge(y + .022, y - .022, .028, 0, .018, MOT, 1))
    P.append(cylb((0, -.575, .02), (0, -.66, .02), .05, ACE, 8, r2=.022))                 # cono de cola
    # --- lado derecho (se refleja)
    # toma de aire en cuña, boca oscura inclinada y cañón
    io = ccw([(.1, .3), (.205, .19), (.215, -.14), (.1, -.14)])
    it = plate(io, -.045, .072, CAS, ch=.014); S.append(it)
    A_, B_ = Vector((.1, .3)), Vector((.205, .19)); u = (B_ - A_).normalized(); nn = Vector((u.y, -u.x))
    S.append(prism(ccw([tuple(A_ + u * .012 + nn * .003), tuple(B_ - u * .01 + nn * .003), tuple(B_ - u * .01 - nn * .03),
                        tuple(A_ + u * .012 - nn * .03)]), -.03, .056, ACE))
    S.append(cylb((.19, .1, .0), (.19, .44, .0), .013, ACE, 6))
    S.append(cylb((.19, .2, .0), (.19, .28, .0), .024, CAS, 6))
    # ala en flecha (quebrada) con líneas de panel y franja ácida junto al borde de ataque
    wo = ccw([(.1, .2), (.36, -.12), (.6, -.36), (.645, -.37), (.66, -.5), (.44, -.47), (.37, -.56), (.1, -.6)])
    S.append(plate(wo, -.02, .02, CAS, ch=.01))
    le0, le1 = Vector((.1, .2)), Vector((.6, -.36)); ul = (le1 - le0).normalized(); ni = Vector((-ul.y, ul.x))
    if ni.x > 0: ni = -ni
    for d0 in (.075, .15):                                  # líneas de panel paralelas al borde de ataque
        S.append(decal([tuple(le0 + (le1 - le0) * .42 + ni * d0), tuple(le0 + (le1 - le0) * .82 + ni * d0),
                        tuple(le0 + (le1 - le0) * .82 + ni * (d0 + .012)), tuple(le0 + (le1 - le0) * .42 + ni * (d0 + .012))], .0215, ACE))
    q0, q1 = le0 + (le1 - le0) * .38, le0 + (le1 - le0) * .93
    S.append(decal([tuple(q0 + ni * .028), tuple(q1 + ni * .028), tuple(q1 + ni * .046), tuple(q0 + ni * .046)], .0215, MOT))
    # vaina de punta de ala: misil/cañón con luz ácida trasera
    S.append(cylb((.655, -.54, .006), (.655, -.24, .006), .024, ACE, 6))
    S.append(cylb((.655, -.24, .006), (.655, -.1, .006), .024, CAS, 6, r2=.003))
    S.append(cylb((.655, -.555, .006), (.655, -.54, .006), .018, MOT, 6))
    # góndola del motor
    NX, NZ = .165, .024
    ns = [(-.05, .04, .034), (-.13, .07, .062), (-.22, .08, .07), (-.56, .08, .07), (-.61, .077, .067)]
    S.append(loft([[(NX, -.0, NZ)]] + [ell(NX, y, NZ, rx, rz, 10) for y, rx, rz in ns], CAS))
    S.append(revolve_y([(.066, -.6), (.086, -.605), (.092, -.66), (.088, -.72), (.074, -.73), (.068, -.68)], ACE, 10, NX, NZ))
    S.append(cylb((NX, -.7, NZ), (NX, -.69, NZ), .07, MOT, 10, cap=True))
    S.append(cylb((NX, -.695, NZ), (NX, -.78, NZ), .045, MOT, 8, r2=.0))
    S.append(box(NX - .03, NX + .03, -.52, -.3, NZ + .064, NZ + .084, ACE, drop=('b',)))
    for y in (-.49, -.44, -.39):
        S.append(decal([(NX - .02, y), (NX + .02, y), (NX + .02, y + .026), (NX - .02, y + .026)], NZ + .0855, MOT))
    # deriva inclinada hacia fuera con punta oscura
    for pts, m in (([(-.4, .07), (-.64, .07), (-.68, .25), (-.57, .25)], CAS), ([(-.57, .25), (-.68, .25), (-.7, .31), (-.63, .31)], ACE)):
        f_ = fin(pts, .02, m); xf(f_, Matrix.Translation((NX + .03, 0, 0)) @ Matrix.Rotation(.4, 4, 'Y')); S.append(f_)
    P.append(mirror(S))
    return done(P, 'Nave')


def dron():
    """Dron de escolta (mod 'drones'): núcleo octogonal con ojo, anillo ácido y dos vainas con motor."""
    CAS, ACE, CAB, MOT = M('Casco'), M('Casco_Acento'), M('Cabina'), M('Motor')
    P, S = [], []
    P.append(plate(circ(.13, 8, TAU / 16), -.045, .055, CAS, ch=.018))
    P.append(prism(circ(.086, 8, TAU / 16), .05, .068, MOT, inner=circ(.066, 8, TAU / 16)))
    P.append(cylb((0, 0, .04), (0, 0, .074), .06, CAB, 8))
    P.append(cylb((0, .1, .0), (0, .27, .0), .016, ACE, 6))
    P.append(cylb((0, .1, .0), (0, .17, .0), .03, ACE, 6))
    S.append(cylb((.2, -.12, 0), (.2, .07, 0), .044, CAS, 8, cap=False))
    S.append(cylb((.2, .07, 0), (.2, .16, 0), .044, ACE, 8, r2=.012, cap=False))
    S.append(cylb((.2, -.135, 0), (.2, -.12, 0), .036, MOT, 8))
    S.append(box(.1, .17, -.06, .03, -.018, .022, ACE, drop=('-x', '+x')))
    f_ = fin([(-.02, .03), (-.12, .03), (-.13, .1), (-.07, .1)], .014, CAS)
    xf(f_, Matrix.Translation((.2, 0, 0))); S.append(f_)
    P.append(mirror(S))
    return done(P, 'Dron')


# =====================================================================================  RECOGIBLES
def chatarra():
    """Tuerca-engranaje de 6 dientes (0.35) con agujero hexagonal y chaflán."""
    CH = M('Chatarra')
    n, rr, ra = 6, .128, .175
    pts = []
    for k in range(n):
        a = k / n * TAU; p = TAU / n
        for rad, f in ((rr, -.24), (ra, -.13), (ra, .13), (rr, .24)):
            pts.append((rad * math.cos(a + f * p), rad * math.sin(a + f * p)))
    ap = .052
    inner = []
    for x, y in pts:
        th = math.atan2(y, x); t = (th + math.pi / 6) % (math.pi / 3) - math.pi / 6
        r = ap / math.cos(t); inner.append((r * math.cos(th), r * math.sin(th)))
    g = prism(pts, -.034, .034, CH, inner=inner)
    return done([g], 'Chatarra', sharp=30)


def potencia():
    """Cápsula P (0.6): cuerpo oscuro, casquetes ácidos emisivos y una P en relieve arriba."""
    ACE, CAS, POT = M('Casco_Acento'), M('Casco'), M('Potencia')
    P = []
    body = box(-.135, .135, -.15, .15, -.085, .085, ACE); bevel(body, .03, 1); P.append(body)
    for s in (1, -1):
        arc = [(s * (.13 + .15 * math.cos(a)), .15 * math.sin(a)) for a in [(-math.pi / 2 + i / 6 * math.pi) for i in range(7)]]
        P.append(plate(arc, -.075, .075, POT, ch=.03))
        P.append(box(s * .125 - .012, s * .125 + .012, -.158, .158, -.09, .09, CAS))
    # "P" en relieve
    P.append(box(-.07, -.034, -.112, .112, .07, .11, POT, drop=('b',)))
    arc = [math.pi / 2 - i / 5 * math.pi for i in range(6)]
    out = [(-.05, .112)] + [(.018 + .056 * math.cos(a), .056 + .056 * math.sin(a)) for a in arc] + [(-.05, 0)]
    inn = [(-.034, .08)] + [(.018 + .024 * math.cos(a), .056 + .024 * math.sin(a)) for a in arc] + [(-.034, .032)]
    P.append(prism(out, .07, .11, POT, inner=inn))
    return done(P, 'Potencia')


def bomba_item():
    """Bomba (0.6): obús naranja con banda de luz, anillo oscuro y aletas en cruz."""
    BO, ACE, LB = M('Bomba'), M('Casco_Acento'), M('Luz_Blanca')
    prof = [(.285, .05, 0), (.25, .1, 0), (.2, .135, 0), (.185, .142, 2), (.165, .15, 0), (.06, .158, 0), (.035, .166, 1),
            (-.005, .166, 1), (-.03, .158, 0), (-.13, .14, 0), (-.2, .1, 1), (-.24, .07, 1)]
    secs = [[(0, .305, 0)]] + [ell(0, y, 0, r, r, 10) for y, r, _ in prof]
    P = [loft(secs, [BO, ACE, LB], band=[0] + [b for _, _, b in prof[1:]])]
    for k in range(4):
        f_ = prism(ccw([(.06, -.12), (.17, -.22), (.175, -.3), (.05, -.27)]), -.009, .009, ACE)
        xf(f_, Matrix.Rotation(k * TAU / 4 + TAU / 8, 4, 'Y')); P.append(f_)
    P.append(revolve_y([(.15, -.25), (.18, -.25), (.18, -.3), (.15, -.3)], ACE, 10))
    return done(P, 'Bomba_Item')


def reparacion():
    """Reparación (0.6): cruz hueso con halo ácido dentro de un anillo oscuro con cuatro luces."""
    REP, ACE, MOT = M('Reparacion'), M('Casco_Acento'), M('Motor')
    P = []
    a, L = .068, .2
    cross = [(a, L), (-a, L), (-a, a), (-L, a), (-L, -a), (-a, -a), (-a, -L), (a, -L), (a, -a), (L, -a), (L, a), (a, a)]
    P.append(plate(cross, -.05, .075, REP, ch=.022))
    P.append(prism(circ(.3, 12, TAU / 24), -.035, .03, ACE, inner=circ(.25, 12, TAU / 24)))
    P.append(decal(circ(.25, 12, TAU / 24), -.02, ACE))
    for k in range(4):
        ang = TAU / 8 + k * TAU / 4
        c, s_ = .275 * math.cos(ang), .275 * math.sin(ang)
        l_ = box(-.022, .022, -.03, .03, .03, .046, MOT, drop=('b',)); xf(l_, Matrix.Translation((c, s_, 0)) @ Matrix.Rotation(ang, 4, 'Z')); P.append(l_)
    return done(P, 'Reparacion')


# =====================================================================================  ENTORNO
def plataforma():
    """Plataforma de hangar hexagonal (6 de ancho entre vértices): cubierta por sectores, círculo de aterrizaje,
    cheurones, franjas de peligro, balizas ácidas y torretas de esquina con luz. Origen: centro de la cubierta."""
    EST, MO, MOT, PA = M('Estructura'), M('Metal_Oscuro'), M('Motor'), M('Peligro_Amarillo')
    P = []
    H = lambda r: circ(r, 6)
    P.append(plate(H(3.0), -.34, -.06, EST, ch=.04))
    P.append(prism(H(2.45), -.62, -.34, MO))
    P.append(prism(H(2.8), -.08, 0, MO))
    P.append(prism(H(3.0), -.06, .07, EST, inner=H(2.8)))
    for i in range(6):
        a0, a1 = i / 6 * TAU, (i + 1) / 6 * TAU
        tr = [(1.55 * math.cos(a0), 1.55 * math.sin(a0)), (2.72 * math.cos(a0), 2.72 * math.sin(a0)),
              (2.72 * math.cos(a1), 2.72 * math.sin(a1)), (1.55 * math.cos(a1), 1.55 * math.sin(a1))]
        P.append(prism(offset2d(ccw(tr), .06), 0, .03, EST))
        am = (a0 + a1) / 2                                   # guía de luces ácidas hacia el centro
        for k in range(3):
            rr = 1.72 + k * .32
            l_ = decal([(-.06, -.045), (.06, -.045), (.06, .045), (-.06, .045)], .034, MOT)
            xf(l_, Matrix.Translation((rr * math.cos(am), rr * math.sin(am), 0)) @ Matrix.Rotation(am, 4, 'Z')); P.append(l_)
    P.append(plate(circ(1.18, 20), 0, .035, EST, ch=.015))
    P.append(ring_decal(1.42, 1.3, 24, .004, PA))
    P.append(ring_decal(.96, .9, 20, .038, MOT))
    for k in range(3):                                       # cheurones centrales (apuntan a +Y)
        y = -.35 + k * .28
        for sx in (-1, 1):
            P.append(decal([(sx * -.02, y + .2), (sx * .3, y), (sx * .3, y + .08), (sx * -.02, y + .28)], .038, PA))
    for rot in (0, math.pi):                                 # franjas de peligro delante y detrás
        R4 = Matrix.Rotation(rot, 4, 'Z')
        for k in range(8):
            x0 = -1.25 + k * .31
            s_ = decal([(x0, -2.595), (x0 + .15, -2.595), (x0 + .26, -2.435), (x0 + .11, -2.435)], .074, PA); xf(s_, R4); P.append(s_)
    for i in range(6):                                       # torretas de esquina y tiras de luz en el canto
        a = i / 6 * TAU
        T4 = Matrix.Translation((2.88 * math.cos(a), 2.88 * math.sin(a), 0)) @ Matrix.Rotation(a, 4, 'Z')
        t = box(-.16, .16, -.16, .16, .07, .34, EST, drop=('b',)); xf(t, T4); P.append(t)
        l_ = decal([(-.08, -.08), (.08, -.08), (.08, .08), (-.08, .08)], .342, MOT); xf(l_, T4); P.append(l_)
        am = a + TAU / 12; yy = -3.0 * math.cos(TAU / 12) - .004       # tira de luz en el canto (cara hacia fuera)
        l2 = mk('l2', [(-.7, yy, -.24), (.7, yy, -.24), (.7, yy, -.17), (-.7, yy, -.17)], [(0, 1, 2, 3)], MOT, fix=False)
        xf(l2, Matrix.Rotation(am - math.pi / 2, 4, 'Z')); P.append(l2)
    return done(P, 'Plataforma', strip=-.9, sharp=50)


def casco_panel():
    """Placa de megaestructura 8x8 que tesela en Y: chapa, zanjas oscuras con tuberías, placas grandes con rejillas,
    tanques, torres con baliza, respiraderos y luces rojas. La chapa superior está en z=0."""
    EST, MO, LUZ = M('Estructura'), M('Metal_Oscuro'), M('Enemigo_Luz')
    rng = random.Random(8)
    P = [box(-4, 4, -4, 4, -.4, 0, EST, drop=('+y', '-y', 'b'))]
    P.append(box(-3.95, -2.3, -4, 4, 0, .006, MO, drop=('+y', '-y', 'b')))
    P.append(box(-.25, 1.25, -4, 4, 0, .006, MO, drop=('+y', '-y', 'b')))
    P.append(cylb((-3.35, -4, .21), (-3.35, 4, .21), .2, EST, 8, cap=False))
    P.append(cylb((-2.78, -4, .14), (-2.78, 4, .14), .13, EST, 8, cap=False))
    for y in (-3, -1, 1, 3):
        P.append(box(-3.65, -2.55, y - .09, y + .09, 0, .45, MO, drop=('b',)))
    for y in (-2, 0, 2):
        P.append(cylb((-3.35, y - .07, .21), (-3.35, y + .07, .21), .245, MO, 8, cap=False))
    for x in (.12, .88):
        P.append(box(x - .045, x + .045, -4, 4, .006, .07, EST, drop=('+y', '-y', 'b')))
    for y in (-3, -1, 1, 3):
        P.append(decal([(.4, y - .12), (.6, y - .12), (.6, y + .12), (.4, y + .12)], .01, LUZ))
    for y0, y1 in ((-3.9, -.1), (.1, 3.9)):
        P.append(plate([(-2.2, y0), (-.3, y0), (-.3, y1), (-2.2, y1)], 0, .26, EST, ch=.05))
    P.append(decal([(-2.0, -3.6), (-.5, -3.6), (-.5, -2.3), (-2.0, -2.3)], .262, MO))
    P.append(decal([(-1.9, -1.9), (-.6, -1.9), (-.6, -.5), (-1.9, -.5)], .262, MO))
    for k in range(6):
        y = -1.78 + k * .22
        P.append(box(-1.86, -.64, y, y + .07, .262, .3, EST, drop=('b', '+y')))
    P.append(prism(circ(.55, 12, 0, -1.25, 2.2), .26, .31, EST, inner=circ(.4, 12, 0, -1.25, 2.2)))
    P.append(decal(circ(.4, 12, 0, -1.25, 2.2), .27, MO))
    P.append(cylb((-1.25, 2.2, .272), (-1.25, 2.2, .33), .12, EST, 8))
    P.append(box(-1.3, -1.2, .5, 1.4, .26, .3, MO, drop=('b',)))
    P.append(box(-1.3, -.5, .5, .6, .26, .3, MO, drop=('b',)))
    P.append(box(-.42, -.34, 3.3, 3.5, .26, .3, LUZ, drop=('b',)))
    kind_ch = lambda ci, ri: (ci + ri) % 2 == 1
    cols = ((1.35, 2.6), (2.7, 3.95)); rows = ((-3.95, -2.05), (-1.95, -.05), (.05, 1.95), (2.05, 3.95))
    for ci, (x0, x1) in enumerate(cols):
        for ri, (y0, y1) in enumerate(rows):
            h = rng.choice((.1, .16, .22, .3))
            P.append(plate([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 0, h, EST, ch=(.04 if kind_ch(ci, ri) else 0),
                           pm=(MO if (ci + ri) % 2 == 0 else None), pin=.18, pd=.015))
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            kind = (ci * 4 + ri) % 4
            if kind == 1:        # tanque tumbado con abrazaderas
                P.append(cylb((cx, y0 + .3, h + .17), (cx, y1 - .3, h + .17), .17, EST, 6))
                for yy in (y0 + .45, y1 - .45):
                    P.append(box(cx - .2, cx + .2, yy - .05, yy + .05, h, h + .3, MO, drop=('b',)))
            elif kind == 2:      # torre con antena y baliza
                P.append(plate([(cx - .28, cy - .28), (cx + .28, cy - .28), (cx + .28, cy + .28), (cx - .28, cy + .28)], h, h + .45, EST, ch=.04))
                P.append(cylb((cx + .12, cy + .12, h + .45), (cx + .12, cy + .12, h + .95), .025, MO, 5, cap=False))
                P.append(box(cx + .07, cx + .17, cy + .07, cy + .17, h + .95, h + 1.02, LUZ))
                P.append(box(cx - .2, cx + .05, cy - .29, cy - .27, h + .15, h + .35, MO, drop=('b',)))
            elif kind == 3:      # respiradero de aletas
                for k in range(4):
                    xx = x0 + .24 + k * .24
                    P.append(box(xx, xx + .07, cy - .6, cy + .6, h, h + .12, MO, drop=('b',)))
            else:                # cajas
                P.append(box(cx - .4, cx + .15, cy - .5, cy + .25, h, h + .16, MO, drop=('b',)))
                P.append(decal([(cx + .22, cy - .6), (cx + .4, cy - .6), (cx + .4, cy + .6), (cx + .22, cy + .6)], h + .004, MO))
    return done(P, 'Casco_Panel', strip=-.9)


def tuberia():
    """Tubería de 8 (eje Y, tesela en Y) con bridas, soportes, tubo auxiliar, válvula y una luz roja."""
    EST, MO, LUZ = M('Estructura'), M('Metal_Oscuro'), M('Enemigo_Luz')
    P = [cylb((0, -4, 0), (0, 4, 0), .22, EST, 8, cap=False)]
    P.append(cylb((.34, -4, -.08), (.34, 4, -.08), .065, MO, 6, cap=False))
    for y in (-3.93, -2, 0, 2, 3.93):
        P.append(cylb((0, y - .075, 0), (0, y + .075, 0), .29, MO, 8))
    for y in (-3, 3):
        P.append(box(-.12, .45, y - .08, y + .08, -.22, -.02, MO))
    P.append(cylb((0, 1, .2), (0, 1, .42), .03, MO, 6))
    P.append(prim('torus', loc=(0, 1, .42), major_radius=.14, minor_radius=.022, major_segments=8, minor_segments=4, m=EST))
    P.append(cylb((-.14, 1, .42), (.14, 1, .42), .014, EST, 4, cap=False))
    P.append(box(-.05, .05, -1.1, -.9, .2, .26, LUZ))
    return done(P, 'Tuberia')


def antena():
    """Antena de 3 de alto (origen en la base): mástil troncocónico con anillos, travesaño con luces rojas,
    parábola y baliza en la punta."""
    EST, MO, LUZ = M('Estructura'), M('Metal_Oscuro'), M('Enemigo_Luz')
    P = []
    P.append(plate([(-.3, -.3), (.3, -.3), (.3, .3), (-.3, .3)], 0, .12, EST, ch=.03))
    for sx in (-1, 1):
        for sy in (-1, 1):
            P.append(box(sx * .22 - .03, sx * .22 + .03, sy * .22 - .03, sy * .22 + .03, .12, .15, MO, drop=('b',)))
    P.append(loft([[(x, y, z) for x, y in ((w, w), (-w, w), (-w, -w), (w, -w))] for w, z in ((.11, .12), (.045, 2.6))], MO, cap0=False))
    for z in (.6, 1.1, 1.6, 2.1):
        w = .11 - (.11 - .045) * (z - .12) / 2.48 + .015
        P.append(box(-w, w, -w, w, z, z + .06, EST))
    P.append(box(-.5, .5, -.035, .035, 2.0, 2.06, EST))
    for sx in (-1, 1):
        P.append(box(sx * .5 - .04, sx * .5 + .04, -.04, .04, 1.98, 2.1, LUZ))
    dish = prim('cone', loc=(0, 0, 0), vertices=10, radius1=.02, radius2=.34, depth=.14, m=EST, end_fill_type='NOTHING')
    xf(dish, Matrix.Translation((.2, 0, 1.45)) @ Matrix.Rotation(-.9, 4, 'Y')); P.append(dish)
    P.append(cylb((.05, 0, 1.4), (.2, 0, 1.45), .025, MO, 6, cap=False))
    P.append(cylb((.2, 0, 1.45), (.38, 0, 1.58), .012, MO, 4, cap=False))
    P.append(cylb((0, 0, 2.6), (0, 0, 2.9), .014, MO, 5, cap=False))
    P.append(prim('ico', loc=(0, 0, 2.93), subdivisions=1, radius=.07, m=LUZ))
    return done(P, 'Antena', strip=-.9, sharp=65)


def roca_azufre():
    """Roca de la nebulosa (1.5): roca facetada con vetas incandescentes de azufre hundidas y cristales."""
    RO, AZ = M('Roca'), M('Azufre')
    rng = random.Random(5)
    o = prim('ico', subdivisions=2, radius=.72, m=RO); o.data.materials.append(AZ)
    for v in o.data.vertices:
        v.co = Vector((v.co.x * 1.08, v.co.y * .92, v.co.z * .72)) * (1 + rng.uniform(-.1, .1))
    displace(o, .16, .55, 51)
    bm = bmesh.new(); bm.from_mesh(o.data); bm.normal_update()
    planes = [(Vector((.8, .3, .5)).normalized(), .08), (Vector((-.3, .9, .2)).normalized(), -.12)]
    veins = [f for f in bm.faces if f.normal.z > -.4 and any(abs(f.calc_center_median().dot(n) - c) < .1 for n, c in planes)]
    bmesh.ops.inset_individual(bm, faces=veins, thickness=.06, depth=-.07, use_even_offset=True)
    for f in veins: f.material_index = 1
    bm.to_mesh(o.data); bm.free()
    P = [o]
    for d, L in (((.5, .3, .8), .42), ((-.6, -.2, .7), .34), ((.1, -.7, .6), .3)):
        dv = Vector(d).normalized(); p0 = dv * .42
        P.append(cylb(tuple(p0 - dv * .1), tuple(p0 + dv * L), .08, AZ, 5, r2=.0, cap=False))
    return done(P, 'Roca_Azufre', sharp=24)


def baliza():
    """Baliza giratoria (1): cuerpo octogonal, cúpula roja emisiva con jaula, cuatro brazos con luces."""
    EST, MO, LUZ = M('Estructura'), M('Metal_Oscuro'), M('Enemigo_Luz')
    P = []
    P.append(plate(circ(.2, 8, TAU / 16), -.14, .12, EST, ch=.03))
    P.append(prism(circ(.215, 8, TAU / 16), -.03, .03, MO))
    P.append(cylb((0, 0, .12), (0, 0, .17), .13, MO, 8, cap=False))
    lamp = prim('sphere', loc=(0, 0, .17), segments=8, ring_count=4, radius=.1, m=LUZ)
    for v in lamp.data.vertices:
        if v.co.z < 0: v.co.z = 0
    P.append(lamp)
    for k in range(2):
        a = k / 2 * math.pi + TAU / 8
        P.append(xf(box(-.112, .112, -.012, .012, .25, .28, MO), Matrix.Rotation(a, 4, 'Z')))
    for k in range(4):
        a = k / 4 * TAU; ca, sa = math.cos(a), math.sin(a)
        arm = box(.16, .42, -.035, .035, -.03, .03, EST); xf(arm, Matrix.Rotation(a, 4, 'Z')); P.append(arm)
        pod = plate([(.37, -.05), (.47, -.05), (.47, .05), (.37, .05)], -.05, .05, MO, ch=.015); xf(pod, Matrix.Rotation(a, 4, 'Z')); P.append(pod)
        l_ = decal([(.395, -.025), (.445, -.025), (.445, .025), (.395, .025)], .052, LUZ); xf(l_, Matrix.Rotation(a, 4, 'Z')); P.append(l_)
    P.append(cylb((0, 0, -.14), (0, 0, -.4), .02, MO, 5, r2=.004, cap=False))
    return done(P, 'Baliza', sharp=65)


# =====================================================================================  ENEMIGOS PEQUEÑOS
def scale_mesh(o, k):
    o.data.transform(Matrix.Scale(k, 4)); o.data.update(); C.view_layer.update(); return o


def dardo():
    """Dardo (1.1): punta de flecha estrecha, lomo con panel burdeos, ojo rojo y luces en las puntas."""
    EN, EP, LUZ = M('Enemigo'), M('Enemigo_Panel'), M('Enemigo_Luz')
    P, S = [], []
    half = [(0, .56), (.09, .24), (.2, -.05), (.37, -.34), (.37, -.46), (.22, -.38), (.12, -.52), (0, -.42)]
    P.append(plate(symo(half), -.025, .025, EN, ch=.012))

    def sec(y, w_, h):
        return [(w_, y, -.02), (w_ * .6, y, h * .8), (0, y, h), (-w_ * .6, y, h * .8), (-w_, y, -.02), (0, y, -.05)]
    P.append(loft([[(0, .6, .005)]] + [sec(*s) for s in ((.45, .035, .05), (.2, .07, .1), (-.1, .08, .11), (-.35, .06, .08), (-.46, .045, .06))], EN))
    P.append(box(-.03, .03, .26, .36, .05, .09, LUZ))
    P.append(prism(ccw([(-.05, .1), (.05, .1), (.035, -.3), (-.035, -.3)]), .08, .12, EP))
    P.append(cylb((0, -.47, .02), (0, -.45, .02), .035, LUZ, 8))
    S.append(prism(ccw([(.12, -.1), (.22, -.12), (.33, -.36), (.14, -.3)]), .02, .034, EP))
    S.append(cylb((.37, -.4, 0), (.37, -.1, 0), .02, EN, 6, r2=.002))
    S.append(cylb((.37, -.44, 0), (.37, -.4, 0), .02, LUZ, 6))
    P.append(mirror(S))
    return done(P, 'Dardo', strip=-.9)


def caza():
    """Caza (1.8 de envergadura): ala de murciélago con cañones en las alas, cuerpo central blindado,
    triple ojo rojo, paneles burdeos y derivas."""
    EN, EP, LUZ, MO = M('Enemigo'), M('Enemigo_Panel'), M('Enemigo_Luz'), M('Metal_Oscuro')
    P, S = [], []
    half = [(0, .62), (.12, .4), (.3, .22), (.6, .04), (.88, .34), (.94, .2), (.8, -.08), (.6, -.34), (.34, -.3), (.24, -.48), (0, -.4)]
    P.append(plate(symo(half), -.035, .035, EN, ch=.016))

    def sec(y, w_, h):
        return [(w_, y, -.03), (w_ * .75, y, h * .75), (w_ * .3, y, h), (-w_ * .3, y, h), (-w_ * .75, y, h * .75), (-w_, y, -.03), (-w_ * .5, y, -.07), (w_ * .5, y, -.07)]
    P.append(loft([[(0, .66, .01)]] + [sec(*s) for s in ((.5, .07, .08), (.3, .15, .16), (0, .19, .2), (-.3, .17, .16), (-.46, .12, .1))], EN))
    P.append(prism(ccw([(-.08, .18), (.08, .18), (.1, -.24), (-.1, -.24)]), .15, .21, EP))
    for x, y in ((0, .36), (.055, .3), (-.055, .3)):
        P.append(cylb((x, y, .1), (x, y, .15 + (.012 if x == 0 else 0)), .028, LUZ, 8))
    for y in (-.06, -.12):
        P.append(box(-.06, .06, y, y + .03, .205, .22, LUZ, drop=('b',)))
    S.append(decal([(.22, .16), (.54, .0), (.57, -.26), (.38, -.24), (.28, -.34), (.22, -.3)], .037, EP))
    S.append(decal([(.68, .1), (.84, .28), (.88, .22), (.76, .04)], .037, EP))
    S.append(decal([(.3, .12), (.52, .0), (.53, -.03), (.3, .09)], .038, LUZ))
    S.append(cylb((.62, -.3, .02), (.62, .36, .02), .045, MO, 8))
    S.append(cylb((.62, .2, .02), (.62, .36, .02), .058, EN, 8))
    S.append(cylb((.62, .36, .02), (.62, .46, .02), .03, MO, 8))
    S.append(cylb((.62, .46, .02), (.62, .48, .02), .024, LUZ, 8))
    S.append(cylb((.62, -.32, .02), (.62, -.3, .02), .036, LUZ, 8))
    S.append(cylb((.87, .24, .03), (.87, .24, .05), .025, LUZ, 6))
    S.append(cylb((.09, -.47, .03), (.09, -.43, .03), .045, LUZ, 8))
    S.append(revolve_y([(.045, -.3), (.062, -.32), (.062, -.44), (.05, -.44)], MO, 8, .09, .03))
    f_ = fin([(-.16, .08), (-.42, .08), (-.46, .24), (-.36, .24)], .02, EP)
    xf(f_, Matrix.Translation((.16, 0, 0)) @ Matrix.Rotation(.35, 4, 'Y')); S.append(f_)
    P.append(mirror(S))
    return done(P, 'Caza', strip=-.9)


TB, TH = 1.27, 1.12       # escala de la base y de la cabeza de la torreta
TMOUNT = .34 * TB         # altura del eje de giro sobre el suelo


def torreta():
    """Torreta (base 1.3): base octogonal con patas y luces; cabeza con doble cañón (origen en el eje de giro)."""
    EN, EP, LUZ, MO = M('Enemigo'), M('Enemigo_Panel'), M('Enemigo_Luz'), M('Metal_Oscuro')
    P = []
    P.append(plate(circ(.5, 8, TAU / 16), 0, .15, EN, ch=.03))
    for k in range(4):
        a = TAU / 8 + k * TAU / 4
        ft = plate([(.28, -.09), (.66, -.06), (.66, .06), (.28, .09)], 0, .1, MO, ch=.025)
        xf(ft, Matrix.Rotation(a, 4, 'Z')); P.append(ft)
        P.append(cylb((.56 * math.cos(a), .56 * math.sin(a), .1), (.56 * math.cos(a), .56 * math.sin(a), .12), .03, EN, 6))
    P.append(plate(circ(.38, 8, TAU / 16), .15, .3, EP, ch=.025))
    for k in range(4):
        l_ = box(.34, .372, -.06, .06, .19, .24, LUZ); xf(l_, Matrix.Rotation(k * TAU / 4, 4, 'Z')); P.append(l_)
    P.append(cylb((0, 0, .3), (0, 0, .34), .32, MO, 12))
    scale_mesh(done(P, 'Torreta_Base', strip=-.9), TB)
    H = []
    H.append(plate([(-.22, -.24), (.22, -.24), (.28, -.05), (.2, .2), (-.2, .2), (-.28, -.05)], 0, .24, EN, ch=.04, pm=EP, pin=.05, pd=.012, rise=True))
    H.append(box(-.09, .09, .19, .215, .09, .165, LUZ))
    H.append(box(-.16, .16, -.36, -.24, .03, .2, MO))
    for k in range(3):
        H.append(box(-.13 + k * .1, -.09 + k * .1, -.365, -.3, .2, .215, EN))
    for sx in (-1, 1):
        H.append(cylb((sx * .1, .12, .12), (sx * .1, .38, .12), .06, EN, 8))
        H.append(cylb((sx * .1, .38, .12), (sx * .1, .68, .12), .038, MO, 8, cap=False))
        H.append(cylb((sx * .1, .64, .12), (sx * .1, .74, .12), .055, EN, 8))
        H.append(cylb((sx * .1, .74, .12), (sx * .1, .76, .12), .03, LUZ, 8))
    scale_mesh(done(H, 'Torreta_Cabeza', strip=-.9), TH)


def mina():
    """Mina (1.0): esfera blindada con cinturón burdeos, 16 pinchos con punta roja y núcleo rojo emisivo arriba."""
    EN, EP, LUZ, MO = M('Enemigo'), M('Enemigo_Panel'), M('Enemigo_Luz'), M('Metal_Oscuro')
    P = [prim('ico', subdivisions=2, radius=.27, m=EN)]
    P.append(prism(circ(.29, 12), -.055, .055, EP))
    for k in range(4):
        l_ = box(.28, .3, -.05, .05, -.03, .03, LUZ); xf(l_, Matrix.Rotation(TAU / 8 + k * TAU / 4, 4, 'Z')); P.append(l_)
    dome = prim('sphere', loc=(0, 0, .2), segments=8, ring_count=4, radius=.11, m=LUZ)
    for v in dome.data.vertices:
        if v.co.z < 0: v.co.z = 0
    P.append(dome)
    P.append(prism(circ(.14, 8, TAU / 16), .19, .23, MO, inner=circ(.105, 8, TAU / 16)))
    dirs = [(math.cos(k / 8 * TAU), math.sin(k / 8 * TAU), 0) for k in range(8)]
    for el in (.75,):
        dirs += [(math.cos(k / 4 * TAU + TAU / 8) * math.cos(el), math.sin(k / 4 * TAU + TAU / 8) * math.cos(el), math.sin(el)) for k in range(4)]
    for d in dirs:
        dv = Vector(d).normalized(); L = .26 if abs(dv.z) < .1 else .2
        p0 = dv * .2; p1 = dv * (.22 + L * .72); p2 = dv * (.22 + L)
        P.append(cylb(tuple(p0), tuple(p1), .055, MO, 5, r2=.024, cap=False))
        P.append(cylb(tuple(p1), tuple(p2), .024, LUZ, 5, r2=.0, cap=False))
    return done(P, 'Mina', sharp=75)


def avispa():
    """Avispa (0.6): dron insecto con cabeza de ojos rojos, abdomen a franjas burdeos, aguijón y dos pares de alas."""
    EN, EP, LUZ = M('Enemigo'), M('Enemigo_Panel'), M('Enemigo_Luz')
    P, S = [], []
    P.append(prim('sphere', loc=(0, .2, .03), segments=8, ring_count=4, radius=.07, scale=(1, .95, .8), m=EN))
    P.append(prim('sphere', loc=(0, .06, .035), segments=8, ring_count=4, radius=.085, scale=(1, 1.15, .85), m=EN))
    prof = [(-.02, .05, .045), (-.07, .09, .08), (-.14, .1, .09), (-.21, .09, .08), (-.27, .06, .055), (-.31, .03, .03)]
    secs = [ell(0, y, .03, r, rz, 8) for y, r, rz in prof] + [[(0, -.33, .03)]]
    P.append(loft(secs, [EN, EP], band=[0, 1, 0, 1, 0, 0], cap0=True))
    P.append(cylb((0, -.33, .03), (0, -.4, .03), .018, LUZ, 5, r2=.0, cap=False))
    S.append(prim('ico', loc=(.045, .238, .055), subdivisions=1, radius=.038, m=LUZ))
    S.append(cylb((.03, .25, .0), (.012, .31, -.005), .014, EN, 4, r2=.003, cap=False))
    for ang, L, W, y in ((.25, .27, .075, .09), (.75, .2, .055, .03)):
        pts = [(L / 2 + L / 2 * math.cos(a), W * math.sin(a)) for a in [i / 8 * TAU for i in range(8)]]
        wg = prism(pts, -.005, .005, EP)
        xf(wg, Matrix.Translation((.05, y, .1)) @ Matrix.Rotation(-ang, 4, 'Z') @ Matrix.Rotation(-.18, 4, 'X'))
        S.append(wg)
    for y, l in ((.1, .14), (.04, .15), (-.02, .13)):
        S.append(cylb((.05, y, .0), (.05 + l * .7, y - .04, -.07), .01, EN, 4, cap=False))
    P.append(mirror(S))
    return scale_mesh(done(P, 'Avispa', sharp=65), .86)


def kamikaze():
    """Kamikaze (1.0): dardo corto con un motor enorme detrás (toberas rojas), aletas en X y rejilla de luz."""
    EN, EP, LUZ, MO = M('Enemigo'), M('Enemigo_Panel'), M('Enemigo_Luz'), M('Metal_Oscuro')
    P = []
    P.append(cylb((0, .1, 0), (0, .44, 0), .075, EP, 8, r2=.018, cap=False))
    P.append(cylb((0, .44, 0), (0, .5, 0), .018, LUZ, 8, r2=.0, cap=False))
    P.append(cylb((0, -.04, 0), (0, .1, 0), .07, EN, 8, cap=False))
    for y in (.02, .12):
        P.append(cylb((0, y - .012, 0), (0, y + .012, 0), .082, MO, 8))
    prof = [(-.02, .1), (-.07, .185), (-.12, .2), (-.42, .2), (-.47, .18)]
    P.append(loft([ell(0, y, 0, r, r, 10, TAU / 20) for y, r in prof], [EN, EP], band=[0, 1, 0, 1]))
    P.append(revolve_y([(.13, -.46), (.178, -.47), (.17, -.52), (.14, -.52)], MO, 10, a0=TAU / 20))
    P.append(cylb((0, -.49, 0), (0, -.47, 0), .14, LUZ, 10))
    P.append(box(-.13, .13, -.36, -.16, .15, .21, MO))
    for y in (-.33, -.27, -.21):
        P.append(box(-.1, .1, y, y + .03, .205, .215, LUZ, drop=('b',)))
    for k in range(4):
        f_ = prism(ccw([(.17, -.2), (.34, -.34), (.34, -.46), (.17, -.44)]), -.012, .012, EP)
        xf(f_, Matrix.Rotation(TAU / 8 + k * TAU / 4, 4, 'Y')); P.append(f_)
    return done(P, 'Kamikaze')





def asteroide(name, size, sub, seed, shards, rock=.28, sharp=26):
    """Asteroide de hielo facetado: icosfera desplazada con placas de roca y cristales de hielo."""
    HI, RO = M('Hielo'), M('Roca')
    rng = random.Random(seed)
    o = prim('ico', subdivisions=sub, radius=1.0, m=HI); o.data.materials.append(RO)
    sc = (1.0, rng.uniform(.8, .92), rng.uniform(.72, .85))
    for v in o.data.vertices:
        v.co = Vector((v.co.x * sc[0], v.co.y * sc[1], v.co.z * sc[2])) * (1 + rng.uniform(-.07, .07))
    displace(o, .22, .7, seed)
    ph = [rng.uniform(0, 6) for _ in range(3)]
    for p in o.data.polygons:
        c = p.center
        f = math.sin(c.x * 2.3 + ph[0]) + math.sin(c.y * 2.9 + ph[1]) + math.sin(c.z * 3.4 + ph[2])
        if f > 3 * (1 - rock) - 1.7: p.material_index = 1
    P = [o]
    for i in range(shards):
        d = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(.2, 1))).normalized()
        p0 = d * .7; L = rng.uniform(.35, .6)
        P.append(cylb(tuple(p0), tuple(p0 + d * L), rng.uniform(.1, .15), HI, 5, r2=.0, cap=False))
    ob = done(P, name, sharp=sharp)
    vs = [v.co for v in ob.data.vertices]
    k = size / max(max(v[i] for v in vs) - min(v[i] for v in vs) for i in range(3))
    return scale_mesh(ob, k)


# =====================================================================================  build
def build():
    OUT.clear()
    nave(); dron()
    chatarra(); potencia(); bomba_item(); reparacion()
    plataforma(); casco_panel(); tuberia(); antena(); roca_azufre(); baliza()
    dardo(); caza(); torreta(); mina(); avispa(); kamikaze()
    asteroide('Asteroide_G', 3.2, 2, 11, 4)
    asteroide('Asteroide_M', 1.8, 2, 23, 2)
    asteroide('Asteroide_P', .9, 2, 37, 1, rock=.2, sharp=18)
    return list(OUT)
