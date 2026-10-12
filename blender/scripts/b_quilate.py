"""QUILATE · atelier de joyería. Modela en bpy/bmesh:
- Gemas con facetas reales: Brillante (tabla, estrellas, cometas, medias de corona, rondín, pabellón con principales y medias),
  Oval / Pera / Corazón / Princesa (brillantes modificados sobre su contorno) y Esmeralda (talla en escalera). Melee.
- Cabezas de garras ajustadas a cada talla (las garras se empujan con un BVH para abrazar la gema sin atravesarla),
  halos con asientos, chatones (bisel), aro comfort-fit, aro pavé, asa, gancho, eslabón.
- Escenario: pedestal, cojín de ranura, busto expositor, soporte de pendientes, ciclorama, lupa, estuche, vitrina.
Convenciones (Blender, Z arriba): el anillo está en el plano XZ con el eje en Y; la gema mira a +Z con el
rondín en z=0 y su longitud a lo largo de Y. Todas las gemas tienen área de rondín = pi*0.5^2 (diámetro 1 equivalente).
Las posiciones de melee y granos se exportan como extras glTF (userData.q en three.js).
"""
import sys, os, math, json, bisect, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
from blib import *
import bmesh
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
reset()
random.seed(30)
TAU = math.tau

# ---------------------------------------------------------------- materiales
METAL = mat('Metal', '#e6c173', .12, 1)
DECOR = mat('Laton', '#d9b36a', .22, 1)
VEL = mat('Terciopelo', '#0f5c4a', .92)
MARB = mat('Marmol', '#f1f1ef', .22)
LACA = mat('Laca', '#121316', .18)
CUERO = mat('Cuero', '#1b1d21', .55)
CICLO = mat('Ciclorama', '#e6e8ec', .9)
GLASS = mat('Cristal', '#f4f8fb', .02, alpha=.25)
def gem_mat(name, col):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = hexrgb(col)
    p.inputs['Roughness'].default_value = 0.0
    p.inputs['IOR'].default_value = 2.42
    p.inputs['Transmission Weight'].default_value = 1.0
    m.diffuse_color = hexrgb(col)
    return m
GEM = gem_mat('Gema', '#ffffff')

# ---------------------------------------------------------------- utilidades de malla
def to_obj(bm, name, m, smooth=False):
    for f in bm.faces: f.smooth = smooth
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); C.collection.objects.link(o)
    if m: o.data.materials.append(m)
    return o

def loft(name, rings, m, close_ring=True, close_path=False, cap=True, smooth=True):
    bm = bmesh.new()
    V = [[bm.verts.new(p) for p in r] for r in rings]
    n, R = len(V[0]), len(V)
    for i in range(R - 1 + (1 if close_path else 0)):
        a, b = V[i], V[(i + 1) % R]
        for j in range(n if close_ring else n - 1):
            j2 = (j + 1) % n
            try: bm.faces.new((a[j], a[j2], b[j2], b[j]))
            except ValueError: pass
    if cap and not close_path:
        for r in (V[0], V[-1]):
            try: bm.faces.new(r)
            except ValueError: pass
    return to_obj(bm, name, m, smooth)

def frames(pts, closed, up=None):
    n = len(pts); T = []
    for i in range(n):
        if closed: t = pts[(i + 1) % n] - pts[i - 1]
        else: t = pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]
        T.append(t.normalized())
    N = []
    if up is not None:
        for t in T: N.append((up - t * up.dot(t)).normalized())
    else:
        a = Vector((0, 0, 1)) if abs(T[0].z) < .9 else Vector((1, 0, 0))
        N.append((a - T[0] * a.dot(T[0])).normalized())
        for i in range(1, n):
            nn = N[-1] - T[i] * N[-1].dot(T[i]); N.append(nn.normalized())
    B = [T[i].cross(N[i]) for i in range(n)]
    return T, N, B

def tube(name, pts, r, m, sides=6, closed=False, up=None):
    T, N, B = frames(pts, closed, up)
    rings = [[pts[i] + N[i] * (r * math.cos(TAU * k / sides)) + B[i] * (r * math.sin(TAU * k / sides)) for k in range(sides)]
             for i in range(len(pts))]
    return loft(name, rings, m, close_path=closed, cap=not closed)

def catmull(pts, sub=3, closed=False):
    out = []; n = len(pts)
    for i in (range(n) if closed else range(n - 1)):
        p0 = pts[i - 1] if (closed or i > 0) else pts[0]; p1 = pts[i]; p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else pts[-1]
        for s in range(sub):
            t = s / sub; t2 = t * t; t3 = t2 * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    if not closed: out.append(pts[-1].copy())
    return out

def sphere(loc, r, m, seg=8, rings=5):
    return prim('sphere', loc=loc, segments=seg, ring_count=rings, radius=r, m=m, smooth=True)

def lathe_y(name, prof, m, steps=64, smooth=True):
    """Superficie de revolución alrededor del eje Y (eje del anillo). prof(phi) -> lista de (u radial, w axial)."""
    rings = []
    for i in range(steps):
        ph = TAU * i / steps
        rings.append([Vector((u * math.cos(ph), w, u * math.sin(ph))) for (u, w) in prof(ph)])
    # rings = anillos a lo largo de phi; cada anillo = sección cerrada
    return loft(name, rings, m, close_ring=True, close_path=True, smooth=smooth)

def lathe_z(name, prof, m, steps=48, smooth=True):
    """Revolución alrededor de Z. prof = lista de (r, z) de abajo arriba (abierta: se tapa con los extremos r=0)."""
    bm = bmesh.new(); rings = []
    for (r, z) in prof:
        if r < 1e-6: rings.append([bm.verts.new((0, 0, z))])
        else: rings.append([bm.verts.new((r * math.cos(TAU * i / steps), r * math.sin(TAU * i / steps), z)) for i in range(steps)])
    for a, b in zip(rings, rings[1:]):
        if len(a) == 1 and len(b) == 1: continue
        if len(a) == 1:
            for i in range(steps): bm.faces.new((a[0], b[i], b[(i + 1) % steps]))
        elif len(b) == 1:
            for i in range(steps): bm.faces.new((a[i], a[(i + 1) % steps], b[0]))
        else:
            for i in range(steps): bm.faces.new((a[i], a[(i + 1) % steps], b[(i + 1) % steps], b[i]))
    return to_obj(bm, name, m, smooth)

def rbox(name, sx, sy, sz, loc, m, bw=.04, seg=2):
    o = prim('cube', loc=loc, scale=(sx, sy, sz), m=m)
    return bevel(o, bw, seg)

def setq(o, **kw):
    o['q'] = json.dumps(kw, separators=(',', ':'))

def r4(v): return [round(v.x, 4), round(v.y, 4), round(v.z, 4)]

# ---------------------------------------------------------------- contornos (plano XY, antihorario, a=0 en +Y)
class Outline:
    def __init__(self, raw=None, poly=None, n=720):
        if poly is None: P = [Vector((*raw(TAU * i / n), 0)) for i in range(n)]
        else:
            P = []
            for i in range(len(poly)):   # densificar polígono uniformemente
                a, b = Vector((*poly[i], 0)), Vector((*poly[(i + 1) % len(poly)], 0)); k = max(1, int((b - a).length * 400))
                for s in range(k): P.append(a.lerp(b, s / k))
            n = len(P)
        A = cx = cy = 0.0
        for i in range(n):
            x0, y0, x1, y1 = P[i].x, P[i].y, P[(i + 1) % n].x, P[(i + 1) % n].y
            c = x0 * y1 - x1 * y0; A += c; cx += (x0 + x1) * c; cy += (y0 + y1) * c
        A *= .5; cx /= 6 * A; cy /= 6 * A
        self.k = math.sqrt(math.pi * .25 / abs(A)); self.c = Vector((cx, cy, 0))
        self.P = [self.tf(p) for p in P]; self.n = n
        self.L = [0.0]
        for i in range(1, n + 1): self.L.append(self.L[-1] + (self.P[i % n] - self.P[i - 1]).length)
        self.total = self.L[-1]
    def tf(self, p): return Vector(((p.x - self.c.x) * self.k, (p.y - self.c.y) * self.k, 0))
    def at(self, a):
        s = (a % TAU) / TAU * self.total
        i = min(bisect.bisect_right(self.L, s) - 1, self.n - 1)
        t = (s - self.L[i]) / max(1e-9, self.L[i + 1] - self.L[i])
        return self.P[i].lerp(self.P[(i + 1) % self.n], t)
    def normal(self, a, h=.006):
        d = self.at(a + h) - self.at(a - h)
        return Vector((d.y, -d.x, 0)).normalized()
    def poly(self, n=240): return [self.at(TAU * i / n) for i in range(n)]

def seg_inter(a, b, c, d):
    r = b - a; s = d - c; den = r.x * s.y - r.y * s.x
    if abs(den) < 1e-12: return None
    t = ((c.x - a.x) * s.y - (c.y - a.y) * s.x) / den; u = ((c.x - a.x) * r.y - (c.y - a.y) * r.x) / den
    if 1e-9 < t < 1 - 1e-9 and 1e-9 < u < 1 - 1e-9: return a + r * t
    return None

def offset_clean(poly, d):
    """Desplaza un polígono CCW hacia fuera d con uniones redondeadas y quita bucles (hendiduras cóncavas)."""
    n = len(poly); out = []
    for i in range(n):
        p0, p1, p2 = poly[i - 1], poly[i], poly[(i + 1) % n]
        e1 = (p1 - p0).normalized(); e2 = (p2 - p1).normalized()
        n1 = Vector((e1.y, -e1.x, 0)); n2 = Vector((e2.y, -e2.x, 0))
        cr = e1.x * e2.y - e1.y * e2.x
        if cr >= 0:   # convexo: arco
            a1 = math.atan2(n1.y, n1.x); a2 = math.atan2(n2.y, n2.x)
            while a2 < a1: a2 += TAU
            k = max(1, int((a2 - a1) / math.radians(6)))
            for s in range(k + 1):
                a = a1 + (a2 - a1) * s / k; out.append(p1 + Vector((math.cos(a), math.sin(a), 0)) * d)
        else:
            out.append(p1 + n1 * d); out.append(p1 + n2 * d)
    # quitar bucles locales
    changed = True; guard = 0
    while changed and guard < 60:
        changed = False; guard += 1; n = len(out)
        for i in range(n):
            a, b = out[i], out[(i + 1) % n]
            for k in range(2, min(n // 2, 120)):
                j = (i + k) % n; c, d2 = out[j], out[(j + 1) % n]
                x = seg_inter(a, b, c, d2)
                if x is not None:
                    if j > i: out = out[:i + 1] + [x] + out[j + 1:]
                    else: out = [x] + out[j + 1:i + 1]
                    changed = True; break
            if changed: break
    return out

def resample(poly, count=None, spacing=None, closed=True):
    L = [0.0]; n = len(poly)
    for i in range(1, n + (1 if closed else 0)): L.append(L[-1] + (poly[i % n] - poly[i - 1]).length)
    tot = L[-1]
    if count is None: count = max(3, round(tot / spacing))
    out = []
    for s in range(count):
        t = tot * s / count; i = min(bisect.bisect_right(L, t) - 1, len(L) - 2)
        f = (t - L[i]) / max(1e-9, L[i + 1] - L[i]); out.append(poly[i % n].lerp(poly[(i + 1) % n], f))
    return out

def poly_normals(pts):
    n = len(pts); N = []
    for i in range(n):
        d = pts[(i + 1) % n] - pts[i - 1]; N.append(Vector((d.y, -d.x, 0)).normalized())
    return N

def closest_on(poly, p):
    best = None; bd = 1e9; n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]; ab = b - a; t = max(0, min(1, (p - a).dot(ab) / max(1e-12, ab.dot(ab))))
        q = a + ab * t; dd = (q - p).length_squared
        if dd < bd: bd = dd; best = q
    return best

# contornos de cada talla
O_ROUND = Outline(lambda t: (-.5 * math.sin(t), .5 * math.cos(t)))
O_OVAL = Outline(lambda t: (-.415 * math.sin(t), .602 * math.cos(t)))
O_PEAR = Outline(lambda t: (-math.sin(t) * math.sin(t / 2) ** 1.0 * .74, math.cos(t)))
O_HEART = Outline(lambda t: (-math.sin(t) ** 3 * 1.08, (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 16))
_h = .5
O_PRIN = Outline(poly=[(0, _h), (-_h, _h), (-_h, -_h), (_h, -_h), (_h, _h)])
_hx, _hy, _cc = .5, .5 * 1.45, .5 * .36
_oct = [(-_hx + _cc, _hy), (-_hx, _hy - _cc), (-_hx, -_hy + _cc), (-_hx + _cc, -_hy), (_hx - _cc, -_hy), (_hx, -_hy + _cc), (_hx, _hy - _cc), (_hx - _cc, _hy)]
O_EMER = Outline(poly=[(0, _hy)] + _oct)
OCT = [O_EMER.tf(Vector((x, y, 0))) for (x, y) in _oct]

# ---------------------------------------------------------------- gemas
def gem_brilliant(name, OL, tr=.56, ch=.16, pd=.43, gt=.03, rs=.78, rp=.22, G=32, K=8):
    bm = bmesh.new(); step = TAU / K; gs = G // K; c8 = math.cos(step / 2)
    V = lambda a, rho, z: bm.verts.new((*(OL.at(a) * rho).xy, z))
    zs = gt / 2 + (ch - gt / 2) * (1 - rs * c8) / (1 - tr)
    zp = -gt / 2 - (pd - gt / 2) * (1 - rp * c8)
    T = [V(k * step, tr, ch) for k in range(K)]
    S = [V((k + .5) * step, rs, zs) for k in range(K)]
    GU = [V(j * TAU / G, 1, gt / 2) for j in range(G)]
    GL = [V(j * TAU / G, 1, -gt / 2) for j in range(G)]
    P = [V((k + .5) * step, rp, zp) for k in range(K)]
    Cu = bm.verts.new((0, 0, -pd))
    F = lambda *vs: bm.faces.new(vs)
    F(*T)
    for k in range(K):
        k1 = (k + 1) % K
        F(T[k], T[k1], S[k])
        F(T[k], S[k - 1], GU[gs * k]); F(T[k], GU[gs * k], S[k])
        for i in range(gs): F(S[k], GU[(gs * k + i) % G], GU[(gs * k + i + 1) % G])
        for i in range(gs): F(P[k], GL[(gs * k + i + 1) % G], GL[(gs * k + i) % G])
        F(GL[gs * k], P[k - 1], Cu); F(GL[gs * k], Cu, P[k])
    for j in range(G): F(GU[j], GL[j], GL[(j + 1) % G], GU[(j + 1) % G])
    o = to_obj(bm, name, GEM, smooth=False)
    setq(o, pd=pd, ch=ch, gt=gt, cut=name)
    return o

def gem_step(name, corners, gt=.03, crown=((.9, .058), (.8, .098), (.69, .118)), pav=((.84, -.15), (.66, -.27), (.47, -.37)), keel=(.08, .38, -.43)):
    bm = bmesh.new()
    ring = lambda s, z: [bm.verts.new((c.x * s, c.y * s, z)) for c in corners]
    R = [ring(1, gt / 2)] + [ring(s, z) for (s, z) in crown]
    L = [ring(1, -gt / 2)] + [ring(s, z) for (s, z) in pav]
    Kr = [bm.verts.new((c.x * keel[0], c.y * keel[1], keel[2])) for c in corners]
    n = len(corners)
    def band(a, b):
        for i in range(n):
            j = (i + 1) % n; bm.faces.new((a[i], a[j], b[j], b[i]))
    for a, b in zip(R, R[1:]): band(a, b)
    bm.faces.new(R[-1])
    band(R[0], L[0])
    for a, b in zip(L, L[1:]): band(a, b)
    for i in range(n):
        j = (i + 1) % n; bm.faces.new((L[-1][i], L[-1][j], Kr[j])); bm.faces.new((L[-1][i], Kr[j], Kr[i]))
    bm.faces.new(Kr)
    o = to_obj(bm, name, GEM, smooth=False)
    setq(o, pd=-keel[2], ch=crown[-1][1], gt=gt, cut=name)
    return o

CUTS = {
    'Brillante': dict(OL=O_ROUND, prongs=[0, 60, 120, 180, 240, 300]),
    'Oval': dict(OL=O_OVAL, prongs=[0, 60, 120, 180, 240, 300]),
    'Pera': dict(OL=O_PEAR, prongs=[0, 112, 162, 198, 248]),
    'Corazon': dict(OL=O_HEART, prongs=[64, 180, 296]),
    'Princesa': dict(OL=O_PRIN, prongs=[45, 135, 225, 315]),
    'Esmeralda': dict(OL=O_EMER, prongs=None),
}
GEMS = {}
GEMS['Brillante'] = gem_brilliant('Brillante', O_ROUND)
GEMS['Oval'] = gem_brilliant('Oval', O_OVAL)
GEMS['Pera'] = gem_brilliant('Pera', O_PEAR, pd=.45)
GEMS['Corazon'] = gem_brilliant('Corazon', O_HEART, pd=.44, rs=.8)
GEMS['Princesa'] = gem_brilliant('Princesa', O_PRIN, tr=.7, ch=.11, pd=.52, rs=.86, rp=.3)
GEMS['Esmeralda'] = gem_step('Esmeralda', OCT)
MELEE = gem_brilliant('Melee', O_ROUND, G=16)
# garras de la esmeralda: en el centro de cada chaflán
def _param_of(OL, p):
    best = 0; bd = 1e9
    for i in range(720):
        a = TAU * i / 720; d = (OL.at(a) - p).length
        if d < bd: bd = d; best = a
    return best
CUTS['Esmeralda']['prongs'] = [math.degrees(_param_of(O_EMER, (OCT[i] + OCT[i + 1]) / 2)) for i in (0, 2, 4, 6)]
for k in CUTS: CUTS[k]['gem'] = GEMS[k]

def bvh_of(o):
    me = o.data
    return BVHTree.FromPolygons([v.co.copy() for v in me.vertices], [tuple(p.vertices) for p in me.polygons])

def clear(bvh, p, dmin, it=8):
    for _ in range(it):
        loc, nor, idx, dist = bvh.find_nearest(p)
        if loc is None: break
        v = p - loc; inside = v.dot(nor) < 0
        if not inside and dist >= dmin - 1e-5: break
        p = loc + nor.normalized() * dmin
    return p

def top_at_center(o, axis_w=.05):
    """máxima Y (hacia la punta en colgante) de los vértices cerca de x=0: punto de enganche del asa."""
    ys = [v.co.y for v in o.data.vertices if abs(v.co.x) < axis_w]
    return max(ys) if ys else max(v.co.y for v in o.data.vertices)

# ---------------------------------------------------------------- cabezas de garras
PR = .052          # radio de garra (unidades de gema normalizada)
def prong_path(cut, a):
    c = CUTS[cut]; OL = c['OL']; gem = c['gem']; q = json.loads(gem['q']); pd, gt = q['pd'], q['gt']
    bvh = c.setdefault('bvh', bvh_of(gem))
    Q = OL.at(math.radians(a)); n = OL.normal(math.radians(a)); rb = PR * 1.22
    tp = Q - n * .065
    hit = bvh.ray_cast(Vector((tp.x, tp.y, 2)), Vector((0, 0, -1)))
    zt = hit[0].z if hit[0] else gt / 2
    tip = clear(bvh, Vector((tp.x, tp.y, zt + rb)), rb * .97)
    ctrl = [tip,
            clear(bvh, Q + n * (PR * .45) + Vector((0, 0, gt / 2 + PR * .95)), PR + .004),
            clear(bvh, Q + n * (PR + .006), PR + .004)]
    for f in (.3, .58, .82):
        p = Q * (1 - f); p.z = -gt / 2 - f * (pd - gt / 2); ctrl.append(clear(bvh, p, PR + .004))
    base = Q * .12; base.z = -pd - .1; ctrl.append(base)
    pts = catmull(ctrl, 3)
    pts = [pts[0]] + [clear(bvh, p, PR + .003) if p.z > -pd + .02 else p for p in pts[1:]]
    return pts, tip, rb

def build_head(cut):
    c = CUTS[cut]; OL = c['OL']; gem = c['gem']; q = json.loads(gem['q']); pd, gt = q['pd'], q['gt']
    bvh = c.setdefault('bvh', bvh_of(gem))
    parts = []
    for a in c['prongs']:
        pts, tip, rb = prong_path(cut, a)
        parts.append(tube('g', pts, PR, METAL, sides=7))
        parts.append(sphere(tip, rb, METAL, 9, 6))
    # rail de la galería (a media altura del pabellón)
    f = .44; rr = PR * .7; ring = []
    for i in range(44):
        a = TAU * i / 44; p = OL.at(a) * (1 - f); p.z = -gt / 2 - f * (pd - gt / 2); ring.append(clear(bvh, p, rr + .004))
    for _ in range(2):
        ring = [(ring[i - 1] + ring[i] * 2 + ring[(i + 1) % len(ring)]) / 4 for i in range(len(ring))]
        ring = [clear(bvh, p, rr + .004) for p in ring]
    parts.append(tube('r', ring, rr, METAL, sides=6, closed=True, up=Vector((0, 0, 1))))
    # base: anillo y vástago donde convergen las garras
    zb = -pd - .1
    parts.append(prim('torus', loc=(0, 0, zb), major_radius=.075, minor_radius=.045, major_segments=16, minor_segments=6, m=METAL, smooth=True))
    parts.append(lathe_z('st', [(0, zb - .16), (.085, zb - .16), (.1, zb - .12), (.09, zb + .02), (0, zb + .02)], METAL, steps=16))
    o = join(parts, 'Garras_' + cut)
    setq(o, top=round(top_at_center(o), 4), bottom=round(zb - .16, 4))
    return o

HEADS = {k: build_head(k) for k in CUTS}

# ---------------------------------------------------------------- halos
MR = .07   # radio de melee en el halo
def build_halo(cut):
    c = CUTS[cut]; OL = c['OL']
    poly = OL.poly(240)
    mid = offset_clean(poly, .125 + .015 + MR)
    sp = 2 * MR + .02
    mel = resample(mid, spacing=sp)
    nm = poly_normals(mel)
    zt = -.018
    melee = [Vector((p.x, p.y, zt + .005)) for p in mel]
    beads = []
    for i in range(len(mel)):
        a, b = mel[i], mel[(i + 1) % len(mel)]; m_ = (a + b) / 2; nn = (nm[i] + nm[(i + 1) % len(mel)]).normalized()
        for s in (-1, 1): beads.append(Vector((m_.x, m_.y, zt + .01)) + nn * (s * (MR + .006)))
    band = resample(mid, count=max(64, len(mel) * 3)); bn = poly_normals(band)
    prof = [(-MR - .022, -.03), (-MR - .012, zt), (MR + .012, zt), (MR + .022, -.03), (MR + .022, -.11), (MR + .01, -.13), (-MR - .01, -.13), (-MR - .022, -.11)]
    rings = [[Vector((p.x, p.y, 0)) + n_ * d + Vector((0, 0, z)) for (d, z) in prof] for p, n_ in zip(band, bn)]
    parts = [loft('hb', rings, METAL, close_ring=True, close_path=True)]
    # puentes: de cada garra al aro del halo
    for a in c['prongs']:
        pts, _, _ = prong_path(cut, a)
        p0 = min(pts, key=lambda p: abs(p.z + .07))
        q2 = closest_on(mid, Vector((p0.x, p0.y, 0))); d = Vector((q2.x - p0.x, q2.y - p0.y, 0))
        p1 = Vector((q2.x, q2.y, p0.z)) - d.normalized() * (MR * .6)
        parts.append(tube('br', [p0, p1], .03, METAL, sides=6))
    o = join(parts, 'Halo_' + cut)
    setq(o, melee=[r4(p) for p in melee], ms=MR * 2, beads=[r4(p) for p in beads], br=.022, top=round(top_at_center(o, .06), 4))
    return o

HALOS = {k: build_halo(k) for k in CUTS}

# ---------------------------------------------------------------- chatones (bisel)
def build_bezel(cut):
    c = CUTS[cut]; OL = c['OL']; gem = c['gem']; q = json.loads(gem['q']); pd = q['pd']
    bvh = c.setdefault('bvh', bvh_of(gem)); zs = pd / .43
    prof = [(1, -.03, .052), (1, -.012, .072), (1, .03, .08), (1, .058, .068), (1, .068, .04), (1, .068, -.07),
            (.74, .05, -.25 * zs), (.4, .03, -.42 * zs), (.34, 0, -.45 * zs), (.37, -.012, -.405 * zs),
            (.7, .004, -.215 * zs), (1, .004, -.02), (1, .004, .02)]
    N = 72; S = [TAU * i / N for i in range(N)]
    base = [OL.at(a) for a in S]; nrm = [OL.normal(a) for a in S]
    cache = {}
    def cl(k, d):
        key = (k, d)
        if key not in cache: cache[key] = offset_clean([p * k for p in OL.poly(200)], d)
        return cache[key]
    rings = []
    for i in range(N):
        r = []
        for (k, d, z) in prof:
            p = base[i] * k + nrm[i] * d
            if d > .02: p = closest_on(cl(k, d), p)
            v = Vector((p.x, p.y, z))
            if d < 0: v = clear(bvh, v, .008)
            r.append(v)
        rings.append(r)
    o = loft('Bisel_' + cut, rings, METAL, close_ring=True, close_path=True)
    setq(o, top=round(top_at_center(o, .06), 4), bottom=round(-.45 * zs, 4))
    return o

BEZELS = {k: build_bezel(k) for k in CUTS}

# ---------------------------------------------------------------- aros
RIN = 1.0
def shank_prof(T0, T1, W0, W1, p, n=18):
    def prof(ph):
        f = ((1 + math.sin(ph)) / 2) ** 2
        T = T0 + (T1 - T0) * f; W = W0 + (W1 - W0) * f; rc = RIN + T / 2; out = []
        for i in range(n):
            t = TAU * i / n; c, s = math.cos(t), math.sin(t)
            out.append((rc + T / 2 * math.copysign(abs(c) ** p, c), W / 2 * math.copysign(abs(s) ** p, s)))
        return out
    return prof
ARO = lathe_y('Aro', shank_prof(.13, .17, .24, .30, .58), METAL, steps=84)
setq(ARO, rin=RIN, tb=.13, tt=.17, wb=.24, wt=.30)

PT, PW = .16, .30
AROP = lathe_y('AroPave', shank_prof(PT, PT, PW, PW, .42), METAL, steps=96)
pm, pb, ang = .05, [], []
step_a = (2 * pm + .016) / (RIN + PT)
a = math.radians(22)
while a < math.radians(118):
    ang.append(a); a += step_a
pmel = []
for s in (1, -1):
    for a in ang:
        ph = math.pi / 2 + s * a; u = RIN + PT + .004
        pos = Vector((u * math.cos(ph), 0, u * math.sin(ph))); nor = Vector((math.cos(ph), 0, math.sin(ph)))
        pmel.append(r4(pos) + r4(nor))
    for i in range(len(ang) - 1):
        ph = math.pi / 2 + s * (ang[i] + ang[i + 1]) / 2; u = RIN + PT + .01
        for w in (-1, 1): pb.append(r4(Vector((u * math.cos(ph), w * (pm + .014), u * math.sin(ph)))))
setq(AROP, rin=RIN, t=PT, w=PW, melee=pmel, ms=pm * 2, beads=pb, br=.018)

# ---------------------------------------------------------------- asa, gancho, eslabón, grano
def ellipse_yz(cz, by, bz, n=24):
    return [Vector((0, by * math.sin(TAU * i / n), cz + bz * math.cos(TAU * i / n))) for i in range(n)]
rw = .026; bz_ = .12
asa = [tube('a', ellipse_yz(-(bz_ - rw), .075, bz_), rw, METAL, sides=7, closed=True, up=Vector((1, 0, 0))),
       lathe_z('tab', [(0, -.33), (.03, -.33), (.036, -.3), (.03, -.2), (0, -.2)], METAL, steps=12)]
ASA = join(asa, 'Asa')
setq(ASA, bottom=-.33, wire=rw)

Ra, gw = .17, .018
hook = []
arc = [Vector((0, -Ra * math.cos(t), -(Ra - gw) + Ra * math.sin(t))) for t in [math.pi * i / 16 for i in range(17)]]
front = [Vector((0, -Ra, -(Ra - gw) - .07 * i)) for i in range(1, 7)]
back = [Vector((0, Ra + .01 * i, -(Ra - gw) - .075 * i)) for i in range(1, 9)]
path = list(reversed(front)) + arc + back
hook.append(tube('h', catmull(path, 2), gw, METAL, sides=6))
zl = -(Ra - gw) - .07 * 6
hook.append(sphere((0, -Ra, -(Ra - gw) - .2), .045, METAL, 10, 7))
hook.append(prim('torus', loc=(0, -Ra, zl - .05), rot=(math.pi / 2, 0, 0), major_radius=.05, minor_radius=gw, major_segments=16, minor_segments=6, m=METAL, smooth=True))
GANCHO = join(hook, 'Gancho')
setq(GANCHO, bottom=[0, round(-Ra, 4), round(zl - .1 - gw, 4)])

lk = [Vector((.03 * math.cos(t) + math.copysign(.02, math.cos(t)), 0, .026 * math.sin(t))) for t in [TAU * i / 14 for i in range(14)]]
ESL = tube('Eslabon', lk, .0105, METAL, sides=5, closed=True, up=Vector((0, 1, 0)))
setq(ESL, pitch=.074, wire=.0105)
GRANO = sphere((0, 0, 0), 1, METAL, 8, 5); GRANO.name = GRANO.data.name = 'Grano'

# ---------------------------------------------------------------- escenario
# pedestal (origen en la base)
PED = lathe_z('Pedestal', [(0, 0), (1.9, 0), (1.95, .03), (1.95, .1), (1.86, .14), (1.8, .2), (1.8, 1.22), (1.86, 1.26), (1.9, 1.3),
                           (1.9, 1.36), (1.87, 1.4), (0, 1.4)], MARB, steps=64)
PED.data.polygons.foreach_set('use_smooth', [False] * len(PED.data.polygons))
PED.data.polygons.foreach_set('use_smooth', [True] * len(PED.data.polygons))
trim = prim('torus', loc=(0, 0, 1.235), major_radius=1.805, minor_radius=.018, major_segments=64, minor_segments=6, m=DECOR, smooth=True)
PED = join([PED, trim], 'Pedestal')
setq(PED, top=1.4)

# cojín de ranura: rodillos a lo largo de X a ambos lados del plano del anillo
RR, RL = .42, 1.25
roll_prof = []
for i in range(9):
    t = math.pi / 2 * i / 8; roll_prof.append((RR * math.cos(t) * .98, RL + RR * .55 * math.sin(t) - RR * .55))
cj = []
for s in (1, -1):
    yc = s * (.12 + .004 + RR)
    prof = [(0, -RL)] + [(r, -z) for (r, z) in reversed(roll_prof)] + [(r, z) for (r, z) in roll_prof] + [(0, RL)]
    o = lathe_z('roll', [(r, z) for (r, z) in prof], VEL, steps=20)
    o.rotation_euler = (0, math.pi / 2, 0); o.location = (0, yc, .2 + RR - .05)
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); C.view_layer.objects.active = o
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    cj.append(o)
cj.append(rbox('cb', 1.3, 1.02, .12, (0, 0, .12), VEL, .08, 3))
COJIN = join(cj, 'Cojin')
zc = .2 + RR - .05
setq(COJIN, ring=round(zc + RIN + .13, 4))

# busto expositor (plancha con cuello y hombros), cara frontal hacia -Y
bpts = []
for i in range(13): t = math.pi * i / 12; bpts.append((.52 * math.cos(t), 4.05 + .18 * math.sin(t)))
bpts += [(-.52, 3.35), (-.62, 3.02), (-.95, 2.8), (-1.32, 2.62), (-1.46, 2.35), (-1.5, 1.2), (-1.56, .22), (1.56, .22), (1.5, 1.2), (1.46, 2.35), (1.32, 2.62), (.95, 2.8), (.62, 3.02), (.52, 3.35)]
cu = bpy.data.curves.new('busto', 'CURVE'); cu.dimensions = '2D'; cu.fill_mode = 'BOTH'
cu.extrude = .12; cu.bevel_depth = .06; cu.bevel_resolution = 3
sp = cu.splines.new('POLY'); sp.points.add(len(bpts) - 1)
for i, (x, y) in enumerate(bpts): sp.points[i].co = (x, y, 0, 1)
sp.use_cyclic_u = True
ob = bpy.data.objects.new('busto', cu); C.collection.objects.link(ob); ob.rotation_euler = (math.pi / 2, 0, 0)
bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); C.view_layer.objects.active = ob
bpy.ops.object.convert(target='MESH'); ob = C.active_object; ob.data.materials.append(VEL)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True); bpy.ops.object.shade_smooth()
foot = rbox('pie', 1.75, .62, .11, (0, 0, .11), LACA, .05, 3)
BUSTO = join([ob, foot], 'Busto')
ys = [v.co.y for v in BUSTO.data.vertices if v.co.z > 1]
zn = 3.62
nk = [abs(v.co.x) for v in BUSTO.data.vertices if abs(v.co.z - zn) < .08]
setq(BUSTO, front=round(min(ys), 4), back=round(max(ys), 4), neck_z=zn, neck_hw=round(max(nk) if nk else .58, 4), edge=.06)

# soporte de pendientes (dos postes + barra)
so = []
for s in (1, -1):
    so.append(lathe_z('p', [(0, 0), (.24, 0), (.25, .03), (.22, .07), (.08, .1), (.055, .16), (.055, 3.1), (.075, 3.14), (.075, 3.26), (0, 3.26)], LACA, steps=24))
    so[-1].location.x = s * 1.6
    so.append(sphere((s * 1.6, 0, 3.32), .085, DECOR, 12, 8))
so.append(prim('cyl', loc=(0, 0, 3.2), rot=(0, math.pi / 2, 0), vertices=16, radius=.045, depth=3.2, m=DECOR, smooth=True))
SOPORTE = join(so, 'Soporte')
setq(SOPORTE, bar_z=3.2, bar_r=.045, post_x=1.6)

# ciclorama (suelo que se curva en pared)
prof = [(-16, 0), (0, 0), (3.5, 0)]
for i in range(1, 10): t = math.pi / 2 * i / 9; prof.append((3.5 + 6 * math.sin(t), 6 - 6 * math.cos(t)))
prof += [(9.5, 22)]
rings = [[Vector((x, y, z)) for (y, z) in prof] for x in (-40, 40)]
bm = bmesh.new(); A = [bm.verts.new(p) for p in rings[0]]; B = [bm.verts.new(p) for p in rings[1]]
for i in range(len(prof) - 1): bm.faces.new((A[i], B[i], B[i + 1], A[i + 1]))
CICL = to_obj(bm, 'Ciclorama', CICLO, smooth=True)
for f in CICL.data.polygons:
    if f.normal.z < 0 or f.normal.y > 0: pass
CICL.data.flip_normals() if CICL.data.polygons[0].normal.z < 0 else None

# lupa (tumbada en el suelo, lente en XY)
lp = [prim('torus', loc=(0, 0, .05), major_radius=.46, minor_radius=.05, major_segments=40, minor_segments=8, m=DECOR, smooth=True),
      lathe_z('lente', [(0, .02), (.43, .035), (.43, .065), (0, .08)], GLASS, steps=40)]
hd = lathe_z('mango', [(0, 0), (.07, 0), (.1, .05), (.1, 1.2), (.08, 1.3), (0, 1.32)], LACA, steps=16)
hd.rotation_euler = (0, math.pi / 2, 0); hd.location = (.5, 0, .1)
fer = prim('cyl', loc=(.56, 0, .1), rot=(0, math.pi / 2, 0), vertices=16, radius=.105, depth=.14, m=DECOR, smooth=True)
lp += [hd, fer]
LUPA = join(lp, 'Lupa')

# estuche (base) y tapa con bisagra
eb = [rbox('e', .7, .62, .3, (0, 0, .3), CUERO, .08, 3),
      rbox('ei', .6, .52, .02, (0, 0, .6), VEL, .02, 1)]
for s in (1, -1):
    r_ = prim('cyl', loc=(0, s * .15, .6), rot=(0, math.pi / 2, 0), vertices=18, radius=.14, depth=1.1, m=VEL, smooth=True)
    eb.append(r_)
eb.append(prim('cube', loc=(0, -.625, .52), scale=(.62, .006, .012), m=DECOR))
ESTUCHE = join(eb, 'Estuche')
et = [rbox('t', .7, .62, .16, (0, 0, .76), CUERO, .08, 3), rbox('ti', .6, .52, .01, (0, 0, .61), VEL, .02, 1),
      prim('cube', loc=(0, -.625, .7), scale=(.62, .006, .012), m=DECOR)]
TAPA = join(et, 'EstucheTapa', origin=(0, .62, .6))

# vitrina (fondo)
vt = []
W_, D_, H_ = 1.3, .6, 3.4
for sx in (1, -1):
    for sy in (1, -1):
        vt.append(prim('cube', loc=(sx * W_, sy * D_, H_ / 2), scale=(.03, .03, H_ / 2), m=DECOR))
for z in (.35, 2.0, H_):
    vt.append(prim('cube', loc=(0, 0, z), scale=(W_ + .03, D_ + .03, .025), m=DECOR))
vt.append(rbox('base', W_ + .05, D_ + .05, .17, (0, 0, .17), LACA, .03, 2))
vt.append(prim('cube', loc=(0, 0, 1.2), scale=(W_, D_, .82), m=GLASS))
vt.append(prim('cube', loc=(0, 0, 2.7), scale=(W_, D_, .68), m=GLASS))
VITRINA = join(vt, 'Vitrina')

# ---------------------------------------------------------------- exportar
ASSETS = list(GEMS) + ['Melee'] + [o.name for o in HEADS.values()] + [o.name for o in HALOS.values()] + [o.name for o in BEZELS.values()] + \
         ['Aro', 'AroPave', 'Asa', 'Gancho', 'Eslabon', 'Grano', 'Pedestal', 'Cojin', 'Busto', 'Soporte', 'Ciclorama', 'Lupa', 'Estuche', 'EstucheTapa', 'Vitrina']
keep_only(ASSETS)
for n in ASSETS:
    o = bpy.data.objects[n]
    if o.name.startswith(('Garras', 'Halo', 'Bisel', 'Aro', 'Asa', 'Gancho', 'Eslabon', 'Grano')):
        pass
bpy.ops.object.select_all(action='DESELECT')
for n in ASSETS: bpy.data.objects[n].select_set(True)
os.makedirs(ROOT + '/glb', exist_ok=True); os.makedirs(ROOT + '/blend', exist_ok=True); os.makedirs(ROOT + '/renders', exist_ok=True)
bpy.ops.export_scene.gltf(filepath=ROOT + '/glb/quilate.glb', export_format='GLB', use_selection=True, export_apply=True,
                          export_yup=True, export_materials='EXPORT', export_texcoords=False, export_normals=True, export_extras=True)
# ordenar en rejilla para el .blend
for i, n in enumerate(ASSETS):
    o = bpy.data.objects[n]
    if n not in ('Ciclorama',): o.location = ((i % 8) * 4.5 - 16, (i // 8) * 4.5, 0)
bpy.ops.wm.save_as_mainfile(filepath=ROOT + '/blend/quilate.blend')
for n in ASSETS:
    o = bpy.data.objects[n]; o.location = (0, 0, 0); o.hide_render = True

if '--noicon' in sys.argv:
    print('OK quilate (sin icono)'); sys.exit(0)

# ---------------------------------------------------------------- icono: solitario de oro amarillo con brillante sobre terciopelo esmeralda
for o in list(bpy.data.objects):
    o.hide_render=True
def dup(n,loc=(0,0,0),s=1):
    src=bpy.data.objects[n];d=src.copy();d.data=src.data;C.scene.collection.objects.link(d);d.hide_render=False;d.location=(0,0,0);d.rotation_euler=(0,0,0);d.scale=(s,s,s);return d
ring=dup('Aro')
hq=json.loads(bpy.data.objects['Garras_Brillante']['q'])
S=.95;gz=1.0+.17+S*(-hq['bottom'])-S*.03
head=dup('Garras_Brillante',s=S);head.location=(0,0,gz)
gem=dup('Brillante',s=S);gem.location=(0,0,gz)
print('bottom',hq['bottom'],'gz',gz)
emp=bpy.data.objects.new('grp',None);C.scene.collection.objects.link(emp)
for o in (ring,head,gem):o.parent=emp
emp.rotation_euler=(math.radians(10),0,math.radians(-28));emp.location=(0,0,1.35)
# gema: diamante con dispersión aproximada
gm=bpy.data.materials.new('GemIcon');gm.use_nodes=True;p=gm.node_tree.nodes['Principled BSDF']
p.inputs['Base Color'].default_value=(1,1,1,1);p.inputs['Roughness'].default_value=0;p.inputs['IOR'].default_value=2.42;p.inputs['Transmission Weight'].default_value=1
gem.data=gem.data.copy();gem.data.materials.clear();gem.data.materials.append(gm)
fl=prim('plane',loc=(0,0,0),size=60,m=mat('SueloIcono','#0f5c4a',.55))
render_icon(ROOT + '/renders/quilate.png','#0b3f33',(0,-7.6,3.6),(0,0,1.95),lens=58,size=256,samples=64,
 lights=[('AREA',(-3,-3,6),900,'#ffffff'),('AREA',(4,-2,3.5),600,'#fff1dc'),('AREA',(0,4,5),500,'#eef3ff'),('POINT',(1.2,-2.5,3.2),120,'#ffffff')])
print('OK quilate')
