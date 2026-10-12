"""NOVA SURGE · GRUPO B: enemigos grandes y jefes intermedios.
Assets (nombre exacto, morro hacia +Y de Blender, origen en el centro a la altura z=0 salvo que se diga):
  Escudero (1.6) + Escudo (placa curva delante; origen = centro del Escudero -> se coloca en la MISMA posición)
  Saltador (1.2) · Portador (2.6) · Centinela (2.0) · Aplastador (4 x 2 x 1.5, golpea por los extremos ±X)
  Pilon (0.8 x 0.8 x 1.6 alto, origen en el centro; emisor del haz a z=+0.62)
  Rompehielos (4.5) + Taladro (origen en el eje, en la base del cono; gira sobre Y de Blender; va en (0, 2.2, -0.05)
  del Rompehielos)
  Reina (5 de ancho) · Prisma_Nucleo (2.5) + Prisma_Petalo (origen en la bisagra, eje de bisagra = X local, el pétalo
  se extiende hacia +Y local; 6 alrededor del núcleo a radio 1.38) · Gemelo (3)
Materiales: M('Nombre') de nova_mats.py + B_Cristal (propio de este grupo).
Presupuesto: sin caras inferiores en piezas apoyadas, franjas de peligro como calcas de una cara, cilindros sin tapas ocultas."""
import math
import bpy, bmesh
from mathutils import Vector, Matrix
from blib import C, prim, bevel, join, mat
from nova_mats import M

TAU = math.tau
ASSETS = []


# ------------------------------------------------------------------ utilidades de geometría
def _obj(name, bm, mats):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); C.collection.objects.link(o)
    for m in mats: me.materials.append(m)
    return o


def mk(name, verts, faces, mats, fmat=None, recalc=True):
    me = bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in verts], [], faces); me.update()
    o = bpy.data.objects.new(name, me); C.collection.objects.link(o)
    for m in (mats if isinstance(mats, (list, tuple)) else [mats]): me.materials.append(m)
    if fmat:
        for i, p in enumerate(me.polygons): p.material_index = fmat[i]
    if recalc:
        bm = bmesh.new(); bm.from_mesh(me)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(me); bm.free(); me.update()
    return o


def area(pts):
    return sum(pts[i - 1][0] * pts[i][1] - pts[i][0] * pts[i - 1][1] for i in range(len(pts))) / 2


def sym(half):
    """half: puntos con x>=0 desde el centro delantero hasta el centro trasero -> contorno completo simétrico"""
    return half + [(-x, y) for x, y in reversed(half[1:-1])]


def mx(pts, sx):
    return [(x * sx, y) for x, y in pts]


def rot2(pts, a, c=(0, 0)):
    ca, sa = math.cos(a), math.sin(a)
    return [(c[0] + x * ca - y * sa, c[1] + x * sa + y * ca) for x, y in pts]


def rect(cx, cy, w, h, a=0.0):
    return rot2([(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)], a, (cx, cy))


def circ(r, n, a0=0.0, cx=0.0, cy=0.0, sy=1.0):
    return [(cx + r * math.cos(a0 + i / n * TAU), cy + sy * r * math.sin(a0 + i / n * TAU)) for i in range(n)]


def plate(pts, z0, z1, m, ch=0.0, pm=None, pin=.1, pd=.02, rise=False, bot=True, name='pl'):
    """Prisma de un contorno 2D con la cara superior achaflanada (ch) y, opcional, un panel insertado de material pm
    (hundido pd, o elevado si rise)."""
    if area(pts) < 0: pts = pts[::-1]
    bm = bmesh.new()
    b = [bm.verts.new((x, y, z0)) for x, y in pts]
    t = [bm.verts.new((x, y, z1 - ch)) for x, y in pts]
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n; bm.faces.new((b[i], b[j], t[j], t[i]))
    top = bm.faces.new(t)
    if bot: bm.faces.new(list(reversed(b)))
    if ch > 0: bmesh.ops.inset_region(bm, faces=[top], thickness=ch, depth=ch, use_even_offset=True)
    mats = [m]
    if pm is not None:
        bmesh.ops.inset_region(bm, faces=[top], thickness=pin, depth=(pd if rise else -pd), use_even_offset=True)
        top.material_index = 1; mats.append(pm)
    return _obj(name, bm, mats)


def decal(pts, z, m):
    """cara plana de un solo polígono a la altura z (mirando a +Z)"""
    if area(pts) < 0: pts = pts[::-1]
    return mk('dc', [(x, y, z) for x, y in pts], [tuple(range(len(pts)))], m, recalc=False)


def ring(r0, r1, z0, z1, n, m, a0=0.0, bot=False, inner=True, name='ring'):
    o_ = circ(r1, n, a0); i_ = circ(r0, n, a0)
    bm = bmesh.new()
    ot = [bm.verts.new((x, y, z1)) for x, y in o_]; ob = [bm.verts.new((x, y, z0)) for x, y in o_]
    it = [bm.verts.new((x, y, z1)) for x, y in i_]; ib = [bm.verts.new((x, y, z0)) for x, y in i_]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((ot[i], ot[j], it[j], it[i]))
        if bot: bm.faces.new((ob[i], ib[i], ib[j], ob[j]))
        bm.faces.new((ob[i], ob[j], ot[j], ot[i]))
        if inner: bm.faces.new((ib[i], it[i], it[j], ib[j]))
    return _obj(name, bm, [m])


def loft(secs, m, closed=True, cap0=True, cap1=True, name='loft', fmat=None, mats=None):
    """secs: anillos (listas de puntos 3D con el mismo número). Anillo de 1 punto = punta."""
    verts, faces, idx = [], [], []
    for s in secs:
        idx.append(list(range(len(verts), len(verts) + len(s)))); verts += s
    for a, b in zip(idx, idx[1:]):
        n = max(len(a), len(b))
        for i in (range(n) if closed else range(n - 1)):
            j = (i + 1) % n
            if len(a) == 1: faces.append((a[0], b[i], b[j]))
            elif len(b) == 1: faces.append((a[i], a[j], b[0]))
            else: faces.append((a[i], a[j], b[j], b[i]))
    if cap0 and len(idx[0]) > 2: faces.append(tuple(reversed(idx[0])))
    if cap1 and len(idx[-1]) > 2: faces.append(tuple(idx[-1]))
    return mk(name, verts, faces, mats or m, fmat=fmat(faces) if fmat else None)


def box(x0, x1, y0, y1, z0, z1, m, bv=0.0, drop=('b',)):
    f = {'b': (0, 3, 2, 1), 't': (4, 5, 6, 7), '-y': (0, 1, 5, 4), '+x': (1, 2, 6, 5), '+y': (2, 3, 7, 6), '-x': (3, 0, 4, 7)}
    o = mk('box', [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
           [f[k] for k in f if k not in drop], m, recalc=False)
    if bv: bevel(o, bv, 1)
    return o


def obox(c, size, rz, m, drop=('b',)):
    """caja centrada en c, girada rz sobre Z"""
    o = box(-size[0] / 2, size[0] / 2, -size[1] / 2, size[1] / 2, -size[2] / 2, size[2] / 2, m, drop=drop)
    o.data.transform(Matrix.Rotation(rz, 4, 'Z')); o.data.transform(Matrix.Translation(c))
    return o


def seg(a, b, w, h, m, z=None):
    """listón recto (caja) de A a B en planta, ancho w, alto h, apoyado en z"""
    A, B = Vector(a), Vector(b); d = B - A
    return obox(((A.x + B.x) / 2, (A.y + B.y) / 2, (z if z is not None else A.z) + h / 2), (d.length, w, h), math.atan2(d.y, d.x), m)


def _basis(d):
    up = Vector((0, 0, 1)) if abs(d.z) < .9 else Vector((1, 0, 0))
    s = d.cross(up).normalized(); u = s.cross(d).normalized()
    return s, u


def tube(p0, p1, r0, r1, n, m, cap0=True, cap1=True, a0=0.0):
    """cilindro/cono de p0 a p1 (r1=0 -> punta)"""
    P0, P1 = Vector(p0), Vector(p1); d = (P1 - P0).normalized(); s, u = _basis(d)
    rg = lambda P, r: [tuple(P + (s * math.cos(a0 + i / n * TAU) + u * math.sin(a0 + i / n * TAU)) * r) for i in range(n)]
    secs = [rg(P0, r0), rg(P1, r1) if r1 > 0 else [tuple(P1)]]
    return loft(secs, m, cap0=cap0, cap1=cap1)


def disk(c, nrm, r, n, m, a0=0.0):
    C_, d = Vector(c), Vector(nrm).normalized(); s, u = _basis(d)
    pts = [tuple(C_ + (s * math.cos(a0 + i / n * TAU) + u * math.sin(a0 + i / n * TAU)) * r) for i in range(n)]
    o = mk('dk', pts, [tuple(range(n))], m, recalc=False)
    if o.data.polygons[0].normal.dot(d) < 0: o.data.flip_normals()
    return o


def quad(pts, nrm, m):
    """cara plana (calca) con la normal hacia nrm"""
    o = mk('qd', pts, [tuple(range(len(pts)))], m, recalc=False)
    if o.data.polygons[0].normal.dot(Vector(nrm)) < 0: o.data.flip_normals()
    return o


def gem(c, r, h_up, h_dn, n, m, a0=0.0, sx=1.0, sy=1.0):
    """bipirámide (cristal) de n lados"""
    cx, cy, cz = c
    eq = [(cx + sx * r * math.cos(a0 + i / n * TAU), cy + sy * r * math.sin(a0 + i / n * TAU), cz) for i in range(n)]
    secs = ([[(cx, cy, cz - h_dn)]] if h_dn > 0 else []) + [eq, [(cx, cy, cz + h_up)]]
    return loft(secs, m, cap0=h_dn <= 0)


def spike(base, tip, w, t, m, up=(0, 0, 1), cap=False):
    """pirámide de sección rombo desde base hasta tip"""
    b, tp = Vector(base), Vector(tip); d = (tp - b).normalized(); u = Vector(up)
    side = d.cross(u).normalized(); u = side.cross(d).normalized()
    sec = [b + side * w / 2, b + u * t / 2, b - side * w / 2, b - u * t / 2]
    return loft([[tuple(p) for p in sec], [tuple(tp)]], m, cap0=cap)


def stripes(O, U, V, N, n, m, lift=.006, sl=None):
    """franjas de peligro diagonales (calcas de una cara) sobre el paralelogramo O + s·U + t·V, elevadas 'lift' en N.
    n franjas; sl = desplazamiento diagonal en unidades de U (por defecto 45º)."""
    O, U, V, N = Vector(O), Vector(U), Vector(V), Vector(N).normalized()
    O = O + N * lift
    if sl is None: sl = V.length / U.length
    w = 1 / (2 * n); verts, faces = [], []
    cl = lambda t: min(1.0, max(0.0, t))
    k = -int(sl / (2 * w)) - 2
    while k * 2 * w < 1:
        t0 = k * 2 * w; k += 1
        q = [O + U * cl(t0), O + U * cl(t0 + w), O + U * cl(t0 + w + sl) + V, O + U * cl(t0 + sl) + V]
        uq = []
        for p in q:
            if all((p - r).length > 1e-4 for r in uq): uq.append(p)
        if len(uq) < 3: continue
        if len(uq) == 3 and ((uq[1] - uq[0]).cross(uq[2] - uq[0])).length < 1e-4: continue
        nv = (uq[1] - uq[0]).cross(uq[2] - uq[0])
        if nv.dot(N) < 0: uq = uq[::-1]
        faces.append(tuple(range(len(verts), len(verts) + len(uq)))); verts += [tuple(p) for p in uq]
    return [mk('st', verts, faces, m, recalc=False)] if faces else []


def finish(o, deg=34):
    for p in o.data.polygons: p.use_smooth = True
    try: o.data.set_sharp_from_angle(angle=math.radians(deg))
    except Exception:
        for p in o.data.polygons: p.use_smooth = False
    return o


def done(parts, name, origin=(0, 0, 0), deg=34):
    o = join(parts, name, origin)
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bm.to_mesh(o.data); bm.free()
    finish(o, deg)
    ASSETS.append(name)
    return o


# ------------------------------------------------------------------ materiales
def mats():
    global E, PN, L, D, G, W, Y, K, S, CH, SH, CR, LB
    E, PN, L, D = M('Enemigo'), M('Enemigo_Panel'), M('Enemigo_Luz'), M('Metal_Oscuro')
    G, W, Y, K = M('Oro_Elite'), M('Punto_Debil'), M('Peligro_Amarillo'), M('Peligro_Negro')
    S, CH, SH, LB = M('Sierra'), M('Chatarra'), M('Escudo_Energia'), M('Luz_Blanca')
    # cristal rubí oscuro para Saltador y Prisma (brillo tenue, facetas marcadas)
    CR = mat('B_Cristal', '#6e1830', rough=.1, metal=.35, emit='#ff2e4d', emit_str=.9)


def lights(pts, m, s=.05, h=.03):
    return [box(x - s / 2, x + s / 2, y - s / 2, y + s / 2, z, z + h, m) for x, y, z in pts]


def engine(x, y, z, r, L_, n=10):
    """tobera hacia -Y. (x, y) = boca trasera; la carcasa llega hasta y+L_"""
    return [tube((x, y + L_, z), (x, y + .05, z), r * .92, r, n, E, cap0=False, cap1=False),
            tube((x, y + .05, z), (x, y - .02, z), r * 1.08, r * 1.08, n, D, cap0=False, cap1=False),
            disk((x, y - .02, z), (0, -1, 0), r * 1.08, n, D),
            disk((x, y - .03, z), (0, -1, 0), r * .74, n, L)]


# ================================================================== ESCUDERO + ESCUDO
def escudero():
    P = []
    hull = sym([(0, .66), (.26, .63), (.48, .4), (.58, 0), (.54, -.4), (.34, -.64), (0, -.58)])
    P.append(plate(hull, -.16, .2, E, ch=.06, pm=PN, pin=.14, pd=.025))
    P.append(box(-.05, .05, -.55, .1, .17, .23, E))                      # lomo que parte el panel
    for sx in (-1, 1):
        # faldón blindado lateral
        P.append(plate(mx([(.52, .34), (.76, .16), (.8, -.36), (.62, -.56), (.5, -.1)], sx), -.24, .13, E, ch=.045, pm=PN, pin=.08, pd=.015, bot=False))
        # brazo proyector del escudo
        P.append(plate(mx([(.3, .36), (.48, .32), (.56, .78), (.42, .86)], sx), -.05, .12, D, ch=.03, bot=False))
        P.append(tube((sx * .49, .82, -.02), (sx * .49, .82, .08), .09, .09, 8, E, cap0=False, cap1=False))
        P.append(tube((sx * .49, .82, .08), (sx * .49, .82, .17), .065, .03, 8, L, cap0=False))
        P += engine(sx * .3, -.72, .0, .13, .3)
        P += lights([(sx * .72, .05, .13), (sx * .72, -.2, .13)], L, .06, .02)
        for k in range(3):                                                 # tomas de aire
            P.append(box(sx * .22 - .09, sx * .22 + .09, -.3 - k * .08, -.27 - k * .08, .17, .185, D))
    # torreta de orbes (hexagonal) + cañón gordo
    P.append(plate(circ(.25, 6, math.pi / 6), .14, .36, E, ch=.05, pm=PN, pin=.06, pd=.015, bot=False))
    P.append(tube((0, .15, .27), (0, .6, .27), .085, .085, 10, D, cap0=False, cap1=False))
    P.append(tube((0, .58, .27), (0, .68, .27), .115, .115, 10, E, cap0=False, cap1=False))
    P.append(disk((0, .68, .27), (0, 1, 0), .115, 10, L))
    P.append(box(-.16, .16, .2, .235, .26, .32, L))                        # rendija-ojo
    P.append(tube((-.13, -.12, .3), (-.13, -.12, .55), .012, .012, 4, D, cap0=False, cap1=False))
    P.append(box(-.15, -.11, -.14, -.1, .55, .59, L))
    done(P, 'Escudero')

    # Escudo: 5 losetas curvas de energía con juntas (arco frontal centrado en el Escudero, radio 1.0)
    R, A0, A1, nt = 1.0, math.radians(36), math.radians(144), 5
    gap = math.radians(1.6); th = .05
    zs = [(-.22, -.02), (.14, .05), (.5, -.02)]
    P = []
    for t in range(nt):
        ta = A0 + (A1 - A0) * t / nt + gap; tb = A0 + (A1 - A0) * (t + 1) / nt - gap
        verts = []; na = 2; rows = len(zs)
        for side, off in ((0, th / 2), (1, -th / 2)):
            for j, (z, bu) in enumerate(zs):
                for i in range(na + 1):
                    a = ta + (tb - ta) * i / na
                    u = abs((a - A0) / (A1 - A0) - .5) * 2
                    rr = R + bu * (1 - u * u) + off
                    verts.append((rr * math.cos(a), rr * math.sin(a), z * (1 - .22 * u * u)))
        g = lambda s, j, i: s * rows * (na + 1) + j * (na + 1) + i
        faces = []
        for j in range(rows - 1):
            for i in range(na):
                faces.append((g(0, j, i), g(0, j, i + 1), g(0, j + 1, i + 1), g(0, j + 1, i)))
                faces.append((g(1, j, i), g(1, j + 1, i), g(1, j + 1, i + 1), g(1, j, i + 1)))
        for i in range(na):
            faces.append((g(0, rows - 1, i), g(0, rows - 1, i + 1), g(1, rows - 1, i + 1), g(1, rows - 1, i)))
        for j in range(rows - 1):
            faces.append((g(0, j, 0), g(0, j + 1, 0), g(1, j + 1, 0), g(1, j, 0)))
            faces.append((g(0, j, na), g(1, j, na), g(1, j + 1, na), g(0, j + 1, na)))
        P.append(mk('esc', verts, faces, SH))
    done(P, 'Escudo', deg=50)


# ================================================================== SALTADOR
def saltador():
    P = []
    P.append(plate(circ(.27, 6, math.pi / 2), -.12, .1, E, ch=.04, pm=PN, pin=.06, pd=.012))
    P.append(gem((0, 0, .1), .17, .38, 0, 6, CR, math.pi / 2))             # núcleo de cristal
    P.append(gem((0, .0, .1), .1, .5, 0, 3, L, math.pi / 2))                  # chispa interior (asoma)
    for ang, Ln, w in ((90, .64, .2), (210, .56, .18), (330, .56, .18)):
        a = math.radians(ang); d = Vector((math.cos(a), math.sin(a), 0))
        P.append(spike(d * .16 + Vector((0, 0, .02)), d * Ln + Vector((0, 0, -.02)), w, .17, CR, cap=True))
        P.append(spike(d * .2 + Vector((0, 0, .09)), d * (Ln * .78) + Vector((0, 0, .03)), .045, .05, E))   # nervio
        P.append(obox(d * .26, (.1, .16, .2), a + math.pi / 2, E))                                        # zócalo
        P.append(obox(d * (Ln * .5) + Vector((0, 0, .07)), (.04, .04, .03), a, L))
    for ang in (150, 30, 270):
        a = math.radians(ang); d = Vector((math.cos(a), math.sin(a), 0))
        P.append(spike(d * .2, d * .42 + Vector((0, 0, .05)), .13, .09, E))
    P.append(ring(.44, .5, -.03, .01, 12, D, math.pi / 12))                 # anillo de salto
    for ang in (60, 180, 300):
        a = math.radians(ang)
        P.append(obox((.47 * math.cos(a), .47 * math.sin(a), .0), (.1, .07, .08), a, L, drop=()))
    done(P, 'Saltador', deg=30)


# ================================================================== PORTADOR
def portador():
    P = []
    hull = sym([(0, 1.3), (.5, 1.27), (.84, 1.02), (.98, .62), (1.0, -.88), (.86, -1.18), (0, -1.24)])
    P.append(plate(hull, -.34, .06, E, ch=.08))
    P.append(decal([(-.86, -.92), (.86, -.92), (.86, .66), (-.86, .66)], .025, D))       # piso de la bodega
    for sx in (-1, 1):
        P.append(box(sx * .98 - .09, sx * .98 + .09, -.95, .7, .02, .3, E))             # bordas
        P += stripes((sx * .98 - .08, -.9, .3), (0, 1.55, 0), (.16, 0, 0), (0, 0, 1), 7, Y)
        P += engine(sx * .62, -1.5, -.06, .22, .42, 10)
        P.append(plate(mx([(.45, -1.02), (.82, -1.02), (.82, -1.2), (.45, -1.2)], sx), .06, .24, E, ch=.04, bot=False))
        P += lights([(sx * 1.03, .5, -.02), (sx * 1.03, -.1, -.02), (sx * 1.03, -.7, -.02)], L, .06, .05)
        for k in range(3):
            P.append(seg((sx * .98, .45 - k * .5, .3), (sx * .98, .3 - k * .5, .3), .2, .03, D))
    P.append(box(-.9, .9, -1.0, -.9, .02, .34, E))                                        # mamparo trasero
    # cajas de chatarra (piñata)
    for (x, y, h, rz) in ((-.42, .36, .34, .04), (.43, .38, .28, -.05), (-.44, -.15, .3, -.03),
                          (.42, -.13, .38, .06), (-.4, -.62, .26, .02), (.44, -.63, .32, -.04)):
        P.append(plate(rect(x, y, .66, .42, rz), .025, .025 + h, CH, ch=.03, bot=False))
        for dx in (-.16, .18):
            c = rot2([(dx, 0)], rz)[0]
            P.append(obox((x + c[0], y + c[1], .025 + h / 2 + .006), (.07, .44, h), rz, D))
    P.append(plate(rect(-.38, .33, .4, .3, .25), .365, .6, CH, ch=.025, bot=False))       # cajas apiladas
    P.append(plate(rect(.43, -.14, .34, .26, -.3), .405, .6, CH, ch=.025, bot=False))
    # cabina delantera
    cab = sym([(0, 1.24), (.4, 1.2), (.66, .98), (.7, .7), (0, .68)])
    P.append(plate(cab, .04, .46, E, ch=.08, pm=PN, pin=.12, pd=.02, bot=False))
    P.append(plate(sym([(0, 1.19), (.38, 1.14), (.5, 1.02), (0, 1.06)]), .3, .43, L, bot=False))   # parabrisas
    P += lights([(-.52, 1.1, .08), (.52, 1.1, .08)], LB, .08, .04)
    P.append(tube((.45, .82, .38), (.45, .82, .72), .014, .014, 4, D, cap0=False, cap1=False))
    P.append(box(.43, .47, .8, .84, .72, .76, L))
    for k in range(4):
        P.append(box(-.34 + k * .16, -.24 + k * .16, .74, .8, .44, .47, D))              # rejillas
    done(P, 'Portador')


# ================================================================== CENTINELA (élite)
def centinela():
    P = []
    P.append(plate(circ(.6, 8, math.pi / 8), -.26, .16, E, ch=.07, pm=PN, pin=.1, pd=.02))
    P.append(plate(circ(.66, 8, math.pi / 8), -.1, -.01, G, ch=.02, bot=False))         # cinturón dorado
    prof = [(.42, .1), (.38, .26), (.26, .38), (.12, .44)]                                 # cúpula facetada
    secs = [[(r * math.cos(a), r * math.sin(a), z) for a in [math.pi / 8 + i / 8 * TAU for i in range(8)]] for r, z in prof]
    P.append(loft(secs + [[(0, 0, .46)]], E, cap0=False))
    P.append(ring(.2, .27, .36, .42, 8, G, math.pi / 8, inner=False))
    P.append(gem((0, 0, .44), .1, .18, 0, 4, G, math.pi / 4))
    P.append(obox((0, .4, .26), (.26, .07, .07), 0, L))                                   # ojo frontal
    for k in range(8):                                                                      # pinchos radiales
        a = math.pi / 2 + k * TAU / 8; d = Vector((math.cos(a), math.sin(a), 0))
        Ln = (.92 if k == 0 else 1.0) if k % 2 == 0 else .8
        P.append(spike(d * .5 + Vector((0, 0, -.02)), d * (Ln - .18), .24, .22, E))
        b = d * (Ln - .24); P.append(spike(b + Vector((0, 0, -.015)), d * Ln + Vector((0, 0, -.02)), .12, .11, G))
        a2 = a + TAU / 16; P.append(obox((.62 * math.cos(a2), .62 * math.sin(a2), .06), (.05, .09, .05), a2, L))
    for k in range(4):                                                                      # pinchos dorsales
        a = math.pi / 4 + k * TAU / 4; d = Vector((math.cos(a), math.sin(a), 0))
        P.append(spike(d * .3 + Vector((0, 0, .28)), d * .52 + Vector((0, 0, .56)), .09, .09, G))
    for sx in (-1, 1):                                                                      # cañones gemelos
        P.append(tube((sx * .2, .5, .05), (sx * .2, .92, .05), .05, .05, 6, D, cap0=False, cap1=False))
        P.append(tube((sx * .2, .88, .05), (sx * .2, .95, .05), .065, .065, 6, E, cap0=False, cap1=False))
        P.append(disk((sx * .2, .95, .05), (0, 1, 0), .065, 6, L))
    done(P, 'Centinela', deg=30)


# ================================================================== APLASTADOR
def aplastador():
    P = []
    P.append(plate([(-1.6, -1.0), (1.6, -1.0), (1.6, 1.0), (-1.6, 1.0)], -.6, .82, E, ch=.1))
    for x0, x1 in ((-1.45, -.35), (.35, 1.45)):                                          # placas atornilladas
        P.append(plate([(x0, -.8), (x1, -.8), (x1, .8), (x0, .8)], .78, .88, PN, ch=.04, bot=False))
        for yy in (-.62, .62):
            for xx in (x0 + .12, x1 - .12):
                P.append(tube((xx, yy, .88), (xx, yy, .92), .04, .04, 6, D, cap0=False))
    for yy in (-.45, .45):                                                                # pistones hidráulicos
        P.append(tube((-1.35, yy, .92), (1.35, yy, .92), .12, .12, 8, D, cap0=False, cap1=False))
        for xx in (-1.35, 1.35):
            P.append(tube((xx - .11, yy, .92), (xx + .11, yy, .92), .17, .17, 8, E))
        P.append(tube((-.25, yy, .92), (.25, yy, .92), .16, .16, 8, S))
    P.append(plate([(-.3, -.7), (.3, -.7), (.3, .7), (-.3, .7)], .78, .84, D, bot=False))  # rejilla de ventilación
    for k in range(7):
        P.append(box(-.26, .26, -.6 + k * .2, -.55 + k * .2, .84, .87, E))
    for sy in (-1, 1):                                                                    # costados: paneles y rejillas
        yf = sy * 1.006
        for x0, x1 in ((-1.45, -.2), (.2, 1.45)):
            P.append(quad([(x0, yf, -.42), (x1, yf, -.42), (x1, yf, .5), (x0, yf, .5)], (0, sy, 0), PN))
        for k in range(4):
            P.append(quad([(-.12, yf + sy * .002, -.3 + k * .2), (.12, yf + sy * .002, -.3 + k * .2), (.12, yf + sy * .002, -.24 + k * .2), (-.12, yf + sy * .002, -.24 + k * .2)], (0, sy, 0), L if k == 3 else D))
    P.append(tube((0, 0, .84), (0, 0, .95), .1, .1, 8, E, cap0=False))                    # baliza giratoria
    P.append(gem((0, 0, .95), .08, .09, 0, 8, L))
    for sx in (-1, 1):                                                                     # parachoques de peligro
        xa, xb = sorted((sx * 1.6, sx * 2.0)); xo = xb if sx > 0 else xa
        P.append(plate([(xa, -1.0), (xb, -1.0), (xb, 1.0), (xa, 1.0)], -.6, .82, K, ch=.03))
        P += stripes((xa + .03, -.97, .82), (0, 1.94, 0), (xb - xa - .06, 0, 0), (0, 0, 1), 5, Y)
        P += stripes((xo, -.97, -.6), (0, 1.94, 0), (0, 0, 1.36), (sx, 0, 0), 5, Y, sl=.3)
        for yy in (-.55, .55):                                                             # cuernos de impacto
            P.append(spike((xo, yy, .1), (xo + sx * .22, yy, .1), .3, .3, D))
        P += lights([(sx * 1.5, -.9, .82), (sx * 1.5, .9, .82)], L, .08, .04)
    done(P, 'Aplastador', deg=30)


# ================================================================== PILÓN (puerta láser)
def pilon():
    P = []
    P.append(plate([(-.4, -.4), (.4, -.4), (.4, .4), (-.4, .4)], -.8, -.6, K, ch=.04))
    for k in range(4):
        R = Matrix.Rotation(k * math.pi / 2, 4, 'Z')
        P += stripes(R @ Vector((-.34, -.35, -.6)), R @ Vector((.68, 0, 0)), R @ Vector((0, .09, 0)), (0, 0, 1), 3, Y)
    secs = []                                                                             # fuste octogonal
    for r, z in ((.26, -.62), (.2, -.2), (.17, .4), (.2, .46)):
        secs.append([(r * math.cos(a), r * math.sin(a), z) for a in [math.pi / 8 + i / 8 * TAU for i in range(8)]])
    P.append(loft(secs, E, cap0=False, cap1=False))
    for k in range(4):                                                                    # aletas en X
        a = math.pi / 4 + k * math.pi / 2; d = Vector((math.cos(a), math.sin(a), 0))
        v = [(d * .14 + Vector((0, 0, -.6))), (d * .38 + Vector((0, 0, -.6))), (d * .3 + Vector((0, 0, -.35))), (d * .16 + Vector((0, 0, .25)))]
        nrm = Vector((-d.y, d.x, 0)) * .03
        verts = [tuple(p + nrm) for p in v] + [tuple(p - nrm) for p in v]
        P.append(mk('fin', verts, [(0, 1, 2, 3), (7, 6, 5, 4), (1, 5, 6, 2), (2, 6, 7, 3)], PN))
        P.append(box(d.x * .3 - .025, d.x * .3 + .025, d.y * .3 - .025, d.y * .3 + .025, -.42, -.34, L))
    P.append(ring(.12, .27, .44, .56, 8, D, math.pi / 8))                                 # cabezal emisor
    P.append(gem((0, 0, .62), .15, .16, .1, 8, L, math.pi / 8))
    for k in range(4):
        a = k * math.pi / 2; d = Vector((math.cos(a), math.sin(a), 0))
        P.append(spike(d * .22 + Vector((0, 0, .54)), d * .15 + Vector((0, 0, .8)), .07, .07, E))
    P.append(ring(.21, .24, .6, .64, 8, L, math.pi / 8, inner=False))
    done(P, 'Pilon', deg=30)


# ================================================================== ROMPEHIELOS + TALADRO
def rompehielos():
    P = []
    hull = sym([(0, 1.95), (.5, 1.9), (1.05, 1.3), (1.12, .55), (.98, -.35), (1.08, -1.25), (.9, -2.05), (.46, -2.25), (0, -2.2)])
    P.append(plate(hull, -.38, .12, E, ch=.1, pm=PN, pin=.22, pd=.03))
    P.append(box(-.06, .06, -2.0, -1.0, .07, .16, E))
    for sx in (-1, 1):
        # proa en V (quitanieves) con franjas y dientes rompehielos
        blade = mx([(.22, 2.32), (.5, 2.3), (1.62, 1.12), (1.56, .82), (1.1, 1.18)], sx)
        P.append(plate(blade, -.44, .06, K, ch=.05, bot=False))
        A = Vector((sx * .5, 2.2, .06)); B = Vector((sx * 1.5, 1.12, .06))
        P += stripes(A, B - A, Vector((-sx * .13, -.13, 0)), (0, 0, 1), 6, Y)
        for k in range(4):
            t = (k + .5) / 4; p = Vector((sx * .5, 2.3, -.2)).lerp(Vector((sx * 1.62, 1.12, -.2)), t)
            nrm = Vector((sx * .7, .7, 0)).normalized()
            P.append(spike(p - nrm * .05, p + nrm * .22, .16, .2, S))
        # patines laterales
        P.append(plate(mx([(1.05, .45), (1.3, .3), (1.32, -.75), (1.12, -.95), (1.0, -.3)], sx), -.3, .02, E, ch=.04, bot=False))
        P += lights([(sx * 1.24, .15, .02), (sx * 1.25, -.25, .02), (sx * 1.24, -.65, .02)], L, .07, .03)
        P += engine(sx * .55, -2.46, -.05, .26, .5, 10)
        # brazos de grúa plegados con foco
        P.append(box(sx * .82 - .06, sx * .82 + .06, -.2, 1.0, .1, .22, D))
        P.append(obox((sx * .82, 1.02, .2), (.18, .18, .14), 0, E))
        P.append(obox((sx * .82, 1.06, .3), (.1, .06, .06), 0, LB))
        for k in range(4):                                                                   # tomas de aire
            P.append(box(sx * .62 - .12, sx * .62 + .12, -.62 - k * .11, -.58 - k * .11, .115, .14, D))
        # chimenea
        fun = rot2(circ(.2, 8, 0, 0, 0, 1.5), 0)
        fun = [(x + sx * .42, y - .55) for x, y in fun]
        P.append(plate(fun, .12, .78, E, ch=.03, bot=False))
        P.append(decal([(x, y) for x, y in rot2(circ(.15, 8, 0, 0, 0, 1.5), 0, (sx * .42, -.55))], .781, K))
        P.append(plate([(sx * .42 + (x - sx * .42) * 1.05, -.55 + (y + .55) * 1.05) for x, y in fun], .5, .6, PN, bot=False))
    P += engine(0, -2.5, .02, .3, .55, 10)
    # collar del taladro en el morro
    P.append(tube((0, 1.86, -.05), (0, 2.12, -.05), .5, .5, 10, D, cap0=False))
    P.append(tube((0, 2.08, -.05), (0, 2.2, -.05), .42, .42, 10, E, cap0=False))
    # superestructura: puente escalonado
    br = sym([(0, .95), (.42, .9), (.56, .5), (.52, -.3), (0, -.34)])
    P.append(plate(br, .08, .45, E, ch=.07, pm=PN, pin=.12, pd=.02, bot=False))
    P.append(plate(sym([(0, .7), (.3, .66), (.36, .3), (0, .26)]), .4, .66, E, ch=.06, bot=False))
    P.append(plate(sym([(0, .69), (.28, .64), (.32, .5), (0, .54)]), .55, .64, L, bot=False))       # ventanal
    P.append(tube((-.2, .05, .6), (-.2, .05, 1.05), .015, .015, 4, D, cap0=False, cap1=False))
    P.append(box(-.225, -.175, .03, .07, 1.03, 1.07, L))
    P.append(tube((.2, .1, .6), (.2, .1, .78), .05, .05, 6, E, cap0=False))                  # radar
    P.append(plate(rect(.2, .1, .34, .1, .4), .78, .82, D, bot=False))
    # punto débil trasero: reactor expuesto con rejilla
    P.append(plate(sym([(0, -1.05), (.5, -1.1), (.55, -1.75), (0, -1.85)]), .05, .2, D, ch=.03, bot=False))
    P.append(plate(sym([(0, -1.18), (.38, -1.2), (.42, -1.66), (0, -1.74)]), .1, .24, W, bot=False))
    for k in range(4):
        P.append(box(-.44, .44, -1.28 - k * .12, -1.24 - k * .12, .24, .29, E))
    P += stripes((-.55, -1.95, .12), (1.1, 0, 0), (0, .13, 0), (0, 0, 1), 5, Y, sl=.12)
    done(P, 'Rompehielos')

    # --- Taladro: cono con estrías helicoidales (acero/oscuro alternos), eje = Y, origen en la base sobre el eje
    lob, Ld, Rd = 5, 1.5, .5
    secs = []
    for i in range(7):
        u = i / 6; y = Ld * .9 * u; r = Rd * (1 - u * .9) ** .8 + .015; tw = u * 2.4
        secs.append([(r * (1.0 if k % 2 == 0 else .62) * math.cos(k / (2 * lob) * TAU + tw), y,
                      r * (1.0 if k % 2 == 0 else .62) * math.sin(k / (2 * lob) * TAU + tw)) for k in range(2 * lob)])
    secs.append([(0, Ld, 0)])
    nr = 2 * lob
    P = [loft(secs, S, cap0=False, mats=[Y, D, S], fmat=lambda fs: [2 if i >= nr * 6 else (i % nr) % 2 for i in range(len(fs))])]
    # collar giratorio con franjas
    col = tube((0, -.14, 0), (0, .02, 0), .52, .52, 12, K, cap0=False, cap1=False)
    col.data.materials.append(Y)
    for p in col.data.polygons:
        ang = math.atan2(p.center.z, p.center.x)
        p.material_index = int(((ang + math.pi) / TAU) * 12) % 2
    P.append(col)
    P.append(disk((0, .02, 0), (0, 1, 0), .52, 12, D))
    P.append(tube((0, -.2, 0), (0, -.14, 0), .38, .38, 12, D, cap1=False))
    done(P, 'Taladro', origin=(0, -.2, 0), deg=40)


# ================================================================== LA REINA
def reina():
    P = []
    th = sym([(0, 1.05), (.42, .98), (.66, .55), (.7, -.1), (.52, -.55), (0, -.62)])     # tórax
    P.append(plate(th, -.3, .3, E, ch=.1, pm=PN, pin=.14, pd=.025))
    for (x, y) in ((-.28, .3), (.28, .3), (0, -.2)):                                       # compuertas de la colmena
        P.append(plate(circ(.12, 6, 0, x, y), .26, .32, D, bot=False))
        P.append(decal(circ(.075, 6, 0, x, y), .321, L))
    hd = sym([(0, 1.9), (.18, 1.88), (.4, 1.6), (.44, 1.2), (.3, .98), (0, .95)])         # cabeza
    P.append(plate(hd, -.2, .3, E, ch=.08, pm=PN, pin=.1, pd=.02))
    for sx in (-1, 1):
        P.append(gem((sx * .32, 1.5, .2), .14, .1, 0, 6, L, 0, 1, 1.4))                   # ojos compuestos
        pts = [(.1, 1.8), (.3, 1.85), (.44, 2.05), (.42, 2.35), (.3, 2.5), (.33, 2.3), (.3, 2.1), (.16, 2.0)]
        P.append(plate(mx(pts, sx), -.12, .08, D, ch=.03, bot=False))                     # mandíbulas
        P.append(spike((sx * .34, 2.4, -.02), (sx * .22, 2.62, -.03), .09, .08, L))
    for x, h in ((-.26, .22), (-.13, .3), (0, .38), (.13, .3), (.26, .22)):              # corona
        P.append(spike((x, 1.12, .24), (x * 1.2, 1.02, .24 + h), .1, .08, G))
    P.append(box(-.32, .32, 1.06, 1.16, .2, .3, G))
    for sx in (-1, 1):                                                                     # alas: marco + membrana + nervios
        w1 = [(.55, .7), (1.3, 1.05), (2.2, .95), (2.5, .5), (2.2, .05), (1.2, -.05), (.6, .1)]
        w2 = [(.55, -.1), (1.2, -.2), (2.05, -.35), (2.2, -.75), (1.8, -1.15), (1.0, -1.0), (.5, -.45)]
        for w, z in ((w1, .12), (w2, .02)):
            P.append(plate(mx(w, sx), z, z + .08, E, ch=.02, pm=PN, pin=.1, pd=.02, bot=False))
        for (a, b, z) in (((.65, .45), (2.35, .55), .18), ((.9, .35), (2.1, .15), .18), ((1.4, .7), (2.15, .85), .18),
                          ((.6, -.35), (2.05, -.6), .08), ((.9, -.55), (1.7, -1.0), .08)):
            P.append(seg((sx * a[0], a[1], 0), (sx * b[0], b[1], 0), .045, .04, E, z))
        P.append(obox((sx * 2.46, .5, .21), (.1, .16, .04), 0, L))
        P.append(obox((sx * 2.17, -.76, .11), (.1, .16, .04), 0, L))
        for k, y in enumerate((.6, .2, -.25)):                                            # patas
            P.append(spike((sx * .6, y, -.2), (sx * 1.0, y + .1, -.35), .09, .09, D))
            P.append(spike((sx * .98, y + .1, -.35), (sx * 1.15, y + .35 - k * .25, -.5), .07, .07, D))
    # abdomen: bulbo emisivo (punto débil) con placas de blindaje que dejan ver rendijas
    rad = lambda u: .28 + .6 * math.sin(min(1, u * 1.15) * math.pi) ** .8
    secs = []
    for i in range(9):
        u = i / 8; y = -.45 - 2.1 * u; r = rad(u) if i < 8 else .1
        secs.append([(r * math.cos(a), y, .02 + r * .72 * math.sin(a)) for a in [k / 10 * TAU for k in range(10)]])
    P.append(loft(secs + [[(0, -2.62, .02)]], W, cap0=False))
    nn = 7
    for (u0, u1) in ((.08, .2), (.28, .42), (.5, .64), (.72, .84)):
        rs = []
        for u in (u0, (u0 + u1) / 2, u1):
            y = -.45 - 2.1 * u; r = rad(u) * 1.07
            rs.append([(r * math.cos(a), y, .02 + r * .72 * math.sin(a)) for a in [math.radians(-12) + k / (nn - 1) * math.radians(204) for k in range(nn)]])
        inner = [[(x * .9, y, .02 + (z - .02) * .9) for x, y, z in r_] for r_ in rs]
        verts = []; faces = []
        for r_ in rs + inner: verts += r_
        for j in range(2):
            for k in range(nn - 1):
                a = j * nn + k; b = (j + 1) * nn + k
                faces.append((a, a + 1, b + 1, b))
        for k in range(nn - 1):
            faces.append((k, 3 * nn + k, 3 * nn + k + 1, k + 1))
            faces.append((2 * nn + k, 2 * nn + k + 1, 5 * nn + k + 1, 5 * nn + k))
        P.append(mk('arm', verts, faces, E))
        P.append(seg((0, -.45 - 2.1 * u0, 0), (0, -.45 - 2.1 * u1, 0), .08, .04, G, .02 + rad((u0 + u1) / 2) * 1.07 * .72 - .01))
    P.append(spike((0, -2.5, .02), (0, -2.95, -.02), .16, .14, D))                         # aguijón
    done(P, 'Reina', deg=32)


# ================================================================== EL PRISMA
def prisma():
    # núcleo: octaedro facetado de cristal (2.5 de ancho, 1.8 de alto) con ventanas emisivas arriba
    bm = bmesh.new()
    R, Hh = 1.25, .9
    v = [bm.verts.new(p) for p in ((R, 0, 0), (0, R, 0), (-R, 0, 0), (0, -R, 0), (0, 0, Hh), (0, 0, -Hh))]
    tops = [bm.faces.new((v[i], v[(i + 1) % 4], v[4])) for i in range(4)]
    bots = [bm.faces.new((v[(i + 1) % 4], v[i], v[5])) for i in range(4)]
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.inset_individual(bm, faces=tops, thickness=.2, depth=-.1, use_even_offset=True)
    for f in tops: f.material_index = 1
    bmesh.ops.inset_individual(bm, faces=bots, thickness=.22, depth=.05, use_even_offset=True)
    P = [_obj('oct', bm, [CR, W])]
    P.append(gem((0, 0, Hh - .06), .16, .22, 0, 4, CR))                                   # cresta
    for k in range(4):                                                                     # aristas superiores de metal
        a = k * math.pi / 2; e = Vector((R * math.cos(a), R * math.sin(a), 0))
        P.append(spike(e * .98 + Vector((0, 0, .02)), Vector((0, 0, Hh + .02)), .07, .06, E, up=(-e.y, e.x, 0)))
    P.append(ring(1.26, 1.36, -.1, .1, 12, D, math.pi / 12))                               # anillo ecuatorial
    for k in range(6):
        a = math.pi / 2 + k * TAU / 6
        P.append(obox((1.31 * math.cos(a), 1.31 * math.sin(a), .12), (.34, .14, .12), a + math.pi / 2, E))
        a2 = a + TAU / 12
        P.append(obox((1.36 * math.cos(a2), 1.36 * math.sin(a2), .07), (.12, .05, .05), a2 + math.pi / 2, L))
    done(P, 'Prisma_Nucleo', deg=25)

    # pétalo: bisagra en el origen (eje X), se extiende hacia +Y. Cara exterior de cristal facetado con marco de metal.
    P = []
    out = [(-.62, .05), (.62, .05), (.52, .95), (0, 1.8), (-.52, .95)]
    P.append(plate(out, -.06, .04, E, ch=.025, pm=PN, pin=.06, pd=0.0, bot=True))
    verts = [(-.46, .16, .04), (.46, .16, .04), (.38, .92, .04), (0, 1.56, .04), (-.38, .92, .04),
             (0, .24, .2), (0, .95, .26), (.2, .6, .17), (-.2, .6, .17)]
    faces = [(0, 1, 5), (1, 7, 5), (1, 2, 7), (2, 6, 7), (2, 3, 6), (3, 4, 6), (4, 8, 6), (4, 0, 8), (0, 5, 8), (5, 7, 6), (5, 6, 8)]
    P.append(mk('pc', verts, faces, CR))
    vb = [(x, y, -.01 - z) for x, y, z in verts]                                          # cara interior (se ve cerrado)
    vb[5] = (0, .3, -.16); vb[6] = (0, 1.05, -.2)
    P.append(mk('pcb', vb, faces, CR))
    P.append(obox((0, 1.35, .12), (.06, .2, .05), 0, L))
    P.append(obox((0, 1.35, -.13), (.06, .2, .05), 0, L, drop=('t',)))
    P.append(tube((-.5, 0, 0), (.5, 0, 0), .09, .09, 8, E))
    for sx in (-1, 1):
        P.append(obox((sx * .5, .52, .05), (.04, .6, .03), sx * .11, L))
    done(P, 'Prisma_Petalo', deg=25)


# ================================================================== GEMELO
def gemelo():
    P = []
    prof = [(-1.25, .2, .14, .12), (-.9, .3, .22, .16), (-.2, .3, .26, .18), (.5, .24, .22, .14), (1.05, .14, .14, .09), (1.45, .03, .05, .03)]
    secs = []
    for y, w, zt, zb in prof:
        secs.append([(w, y, 0), (w * .6, y, zt), (0, y, zt * 1.15), (-w * .6, y, zt), (-w, y, 0), (-w * .5, y, -zb), (w * .5, y, -zb)])
    secs.append([(0, 1.55, 0)])
    P.append(loft(secs, E))
    P.append(gem((0, .55, .26), .12, .08, 0, 4, CR, math.pi / 2, 1, 3.2))                 # cabina de cristal
    for sx in (-1, 1):
        wing = mx([(.2, .45), (.55, .15), (1.2, -.55), (1.26, -.9), (.95, -.95), (.62, -.78), (.2, -1.05)], sx)
        P.append(plate(wing, -.06, .06, E, ch=.025, pm=PN, pin=.12, pd=.015))
        P.append(seg((sx * .56, .13, 0), (sx * 1.2, -.53, 0), .05, .03, L, .03))           # borde de ataque luminoso
        P.append(plate(mx([(.14, .95), (.55, 1.12), (.6, .98), (.16, .7)], sx), -.02, .05, E, ch=.015))   # canard
        P.append(tube((sx * 1.26, -1.02, .02), (sx * 1.26, -.08, .02), .09, .09, 8, E, cap1=False))    # góndola
        P.append(tube((sx * 1.26, -.08, .02), (sx * 1.26, .1, .02), .09, 0, 8, D))
        P.append(gem((sx * 1.15, -.45, .08), .08, .07, .07, 6, L))                          # emisor del haz
        fin = [(sx * .42, -.55, .12), (sx * .42, -1.15, .12), (sx * .56, -1.3, .62), (sx * .56, -1.0, .62)]
        nrm = Vector((math.cos(.35), 0, -math.sin(.35) * sx)) * .025
        verts = [tuple(Vector(p) + nrm) for p in fin] + [tuple(Vector(p) - nrm) for p in fin]
        P.append(mk('fin', verts, [(0, 1, 2, 3), (7, 6, 5, 4), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], PN))
        P.append(box(sx * .56 - .02, sx * .56 + .02, -1.28, -1.02, .6, .64, L))
        P += engine(sx * .22, -1.5, .0, .15, .45, 10)
        P.append(tube((sx * .34, .2, -.02), (sx * .34, .9, -.02), .035, .035, 6, D, cap0=False, cap1=False))   # cañones
        P.append(disk((sx * .34, .9, -.02), (0, 1, 0), .035, 6, L))
        P.append(plate(mx([(.2, .3), (.36, .2), (.36, -.1), (.2, -.05)], sx), .0, .2, D, ch=.02, bot=False))  # tomas
    P.append(plate(sym([(0, .25), (.1, .2), (.12, -.9), (0, -1.0)]), .2, .3, PN, ch=.03, bot=False))           # lomo
    P += lights([(0, -1.2, .2)], L, .07, .04)
    done(P, 'Gemelo', deg=30)


# ------------------------------------------------------------------ build
def build():
    ASSETS.clear()
    mats()
    escudero(); saltador(); portador(); centinela(); aplastador(); pilon()
    rompehielos(); reina(); prisma(); gemelo()
    return list(ASSETS)
