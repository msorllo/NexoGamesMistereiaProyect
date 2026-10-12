"""26 · TOURBILLON — assets de relojería (platina, ejes con rubí, ruedas con dientes reales,
barrilete, escape con áncora y volante, puente, jaula de tourbillon, fase lunar y reloj completo).
Convenciones: plano de giro XY de Blender (→ XZ en three), origen en el eje, diente centrado en +X.
Módulo común de engranaje M = r/dientes = 1/24 → RuedaS 12 d / r .5, RuedaM 18 d / r .75, RuedaL 24 d / r 1.0,
Barril 27 d / r 1.125, piñón del Escape 12 d / r .5. Plano de engrane: z .31–.39 (centro .35)."""
import sys, os, math, random; HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
from blib import *
import bmesh
reset()
TAU = math.tau
MOD = 1 / 24
ZC, TH = .35, .08          # plano de engrane y grosor de las ruedas

BRASS = mat('Latón', '#d8b06a', .22, 1)
GOLD = mat('Oro chatón', '#d6b36a', .26, 1)
STEEL = mat('Acero pulido', '#dde1e7', .1, 1)
RHOD = mat('Rodio platina', '#c9ced6', .35, 1)
BLUE = mat('Acero pavonado', '#2446a8', .26, 1)
RUBY = mat('Rubí', '#d0103a', .06, 0, emit='#ff1f4f', emit_str=.6)
SLOT = mat('Ranura', '#0a0c10', .6, .3)
DIAL = mat('Esfera', '#e9e6df', .45, .2)
IDX = mat('Índices', '#e8ecf2', .14, 1)
HAND = mat('Agujas', '#dfe3ea', .12, 1)
CASE = mat('Acero caja', '#cfd4db', .24, 1)
LAPIS = mat('Lapislázuli', '#10225e', .4, .1)
MOON = mat('Oro luna', '#e8c878', .3, 1)


# ---------------------------------------------------------------- helpers
def finish(o, sharp=32):
    for p in o.data.polygons: p.use_smooth = True
    try: o.data.set_sharp_from_angle(angle=math.radians(sharp))
    except Exception: pass
    return o


def prism(outer, z0, z1, m, inner=None, name='pr'):
    """Extruye un contorno 2D (CCW). Con 'inner' (mismo nº de puntos) crea un anillo."""
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    ot = [bm.verts.new((x, y, z1)) for x, y in outer]
    ob = [bm.verts.new((x, y, z0)) for x, y in outer]
    n = len(outer)
    if inner:
        it = [bm.verts.new((x, y, z1)) for x, y in inner]
        ib = [bm.verts.new((x, y, z0)) for x, y in inner]
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((ot[i], ot[j], it[j], it[i]))
            bm.faces.new((ob[i], ib[i], ib[j], ob[j]))
            bm.faces.new((ob[i], ob[j], ot[j], ot[i]))
            bm.faces.new((ib[i], it[i], it[j], ib[j]))
    else:
        bm.faces.new(ot); bm.faces.new(list(reversed(ob)))
        for i in range(n):
            j = (i + 1) % n; bm.faces.new((ob[i], ob[j], ot[j], ot[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); C.collection.objects.link(o); me.materials.append(m)
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); C.view_layer.objects.active = o
    return o


def circ(r, n, a0=0.0, cx=0.0, cy=0.0):
    return [(cx + r * math.cos(a0 + i / n * TAU), cy + r * math.sin(a0 + i / n * TAU)) for i in range(n)]


def gear_pts(n, r, m=MOD):
    """Contorno de rueda con dientes (perfil tipo cicloidal de relojería), diente centrado en +X."""
    p = TAU / n; rr = r - 1.25 * m; ra = r + m
    prof = [(rr, -.5), (rr, -.3), (r, -.25), (r + .6 * m, -.19), (ra, -.1),
            (ra, .1), (r + .6 * m, .19), (r, .25), (rr, .3)]
    pts = []
    for k in range(n):
        a = k * p
        for rad, f in prof: pts.append((rad * math.cos(a + f * p), rad * math.sin(a + f * p)))
    return pts


def inner_of(pts, r):
    return [(r * math.cos(math.atan2(y, x)), r * math.sin(math.atan2(y, x))) for x, y in pts]


def cyl(r, z0, z1, m, n=32, x=0, y=0, bv=0):
    o = prim('cyl', loc=(x, y, (z0 + z1) / 2), vertices=n, radius=r, depth=z1 - z0, m=m)
    if bv: bevel(o, bv, 1)
    return finish(o)


def spoke(r0, r1, a0, curve, w0, w1, z0, z1, m, segs=10):
    L, R = [], []
    def c(t):
        rad = r0 + (r1 - r0) * t; ang = a0 + curve * math.sin(t * math.pi * .5) * (1 if curve else 0)
        return rad * math.cos(ang), rad * math.sin(ang)
    for i in range(segs + 1):
        t = i / segs; x, y = c(t); x2, y2 = c(min(1, t + 1e-3)); x1, y1 = c(max(0, t - 1e-3))
        tx, ty = x2 - x1, y2 - y1; l = math.hypot(tx, ty) or 1; nx, ny = -ty / l, tx / l
        w = (w0 + (w1 - w0) * t * t) / 2
        L.append((x + nx * w, y + ny * w)); R.append((x - nx * w, y - ny * w))
    return finish(prism(R + L[::-1], z0, z1, m, name='spoke'))


def screw(x, y, z, r=.06, m=None, rot=0.0, h=.035):
    """Tornillo pavonado de cabeza abombada con ranura."""
    m = m or BLUE
    head = prim('sphere', loc=(x, y, z), segments=16, ring_count=6, radius=r, scale=(1, 1, h / r), m=m)
    for v in head.data.vertices:
        if v.co.z < 0: v.co.z = 0
    head.location = (x, y, z); finish(head, 60)
    sl = prim('cube', loc=(x, y, z + h * .92), rot=(0, 0, rot), scale=(r * .95, r * .16, h * .22), m=SLOT)
    return [head, sl]


def jewel(x, y, z, r=.075):
    """Chatón de oro + rubí abombado con agujero de pivote, cara superior en z."""
    out = [finish(bevel(prim('cyl', loc=(x, y, z - .025), vertices=32, radius=r * 1.9, depth=.05, m=GOLD), .01, 1))]
    rb = prim('sphere', loc=(x, y, z), segments=20, ring_count=8, radius=r, scale=(1, 1, .45), m=RUBY)
    for v in rb.data.vertices:
        if v.co.z < 0: v.co.z = 0
    rb.location = (x, y, z); out.append(finish(rb, 70))
    out.append(cyl(r * .22, z + r * .38, z + r * .47, SLOT, 10, x, y))
    return out


def wheel(n, r, name, style):
    parts = []
    rr = r - 1.25 * MOD
    rin = rr - (.06 if r < .6 else .075)
    pts = gear_pts(n, r)
    rim = prism(pts, ZC - TH / 2, ZC + TH / 2, BRASS, inner=inner_of(pts, rin), name=name + 'rim')
    parts.append(finish(rim))
    hub = .1 if r < .6 else (.12 if r < .9 else .14)
    k = {'S': 4, 'M': 5, 'L': 6}[style]
    for i in range(k):
        a = i / k * TAU + (TAU / k / 2)
        if style == 'S':
            parts.append(spoke(hub * .7, rin + .02, a, 0, .05, .2, ZC - .028, ZC + .028, BRASS, 4))
        else:
            parts.append(spoke(hub * .7, rin + .02, a, .55 if style == 'M' else .7, .05, .075, ZC - .028, ZC + .028, BRASS, 10))
    parts.append(cyl(hub, ZC - .045, ZC + .045, BRASS, 32, bv=.01))
    parts.append(cyl(hub * .5, ZC + .045, ZC + .085, STEEL, 24, bv=.008))                    # virola
    parts.append(cyl(.03, .02, ZC + .15, STEEL, 12))                                           # eje
    parts.append(finish(prim('cone', loc=(0, 0, ZC + .17), vertices=12, radius1=.03, radius2=.008, depth=.04, m=STEEL)))
    pin = gear_pts(8, .105, .105 / 8)                                                           # piñón inferior
    parts.append(finish(prism(pin, .12, .26, STEEL, name='pin')))
    return join(parts, name)


def quantize_glb(path, QS=4096):
    """KHR_mesh_quantization: POSITION -> int16 (x4096, stride 8), NORMAL -> int8 normalizado (stride 4).
    La app lo devuelve a float32 al cargar (FX.load -> dequant). Reduce el GLB a menos de la mitad."""
    import json, struct
    d = open(path, 'rb').read()
    jl = struct.unpack('<I', d[12:16])[0]; J = json.loads(d[20:20 + jl]); bo = 20 + jl
    bl = struct.unpack('<I', d[bo:bo + 4])[0]; BIN = d[bo + 8:bo + 8 + bl]
    views, acc = J['bufferViews'], J['accessors']
    def raw(a):
        v = views[a['bufferView']]; o = v.get('byteOffset', 0) + a.get('byteOffset', 0)
        n = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[a['type']]; cs = {5126: 4, 5123: 2, 5125: 4, 5121: 1}[a['componentType']]
        return BIN[o:o + a['count'] * n * cs]
    out = bytearray(); nviews = []
    def push(data, target=None, stride=None):
        while len(out) % 4: out.append(0)
        v = {'buffer': 0, 'byteOffset': len(out), 'byteLength': len(data)}
        if target: v['target'] = target
        if stride: v['byteStride'] = stride
        out.extend(data); nviews.append(v); return len(nviews) - 1
    pos_ids, nor_ids = set(), set()
    for m in J['meshes']:
        for p in m['primitives']:
            pos_ids.add(p['attributes']['POSITION']); nor_ids.add(p['attributes'].get('NORMAL', -1))
    for i, a in enumerate(acc):
        r = raw(a)
        if i in pos_ids:
            f = struct.unpack('<%df' % (a['count'] * 3), r); q = bytearray()
            for k in range(a['count']):
                q += struct.pack('<hhhh', *[max(-32767, min(32767, round(f[k * 3 + c] * QS))) for c in range(3)], 0)
            a['bufferView'] = push(bytes(q), 34962, 8); a['componentType'] = 5122; a.pop('byteOffset', None)
            a['min'] = [round(x * QS) for x in a['min']]; a['max'] = [round(x * QS) for x in a['max']]
        elif i in nor_ids:
            f = struct.unpack('<%df' % (a['count'] * 3), r); q = bytearray()
            for k in range(a['count']):
                q += struct.pack('<bbbb', *[max(-127, min(127, round(f[k * 3 + c] * 127))) for c in range(3)], 0)
            a['bufferView'] = push(bytes(q), 34962, 4); a['componentType'] = 5120; a['normalized'] = True; a.pop('byteOffset', None)
            a.pop('min', None); a.pop('max', None)
        else:
            tv = views[a['bufferView']].get('target'); a['bufferView'] = push(r, tv); a.pop('byteOffset', None)
    J['bufferViews'] = nviews; J['buffers'] = [{'byteLength': len(out)}]
    for k in ('extensionsUsed', 'extensionsRequired'):
        J[k] = sorted(set(J.get(k, [])) | {'KHR_mesh_quantization'})
    js = json.dumps(J, separators=(',', ':')).encode()
    while len(js) % 4: js += b' '
    while len(out) % 4: out.append(0)
    total = 12 + 8 + len(js) + 8 + len(out)
    g = struct.pack('<III', 0x46546C67, 2, total) + struct.pack('<II', len(js), 0x4E4F534A) + js + struct.pack('<II', len(out), 0x004E4942) + bytes(out)
    open(path, 'wb').write(g)


# ---------------------------------------------------------------- Platina
prof = [(.02, 0), (5.05, 0), (5.05, .1), (5.09, .14), (5.34, .14), (5.4, .1), (5.4, -.42), (5.34, -.5), (.02, -.5)]
pl = lathe(prof, RHOD, 'plat', 128); finish(pl, 25)
pp = [pl]
for i in range(10):
    a = i / 10 * TAU + .31
    pp += screw(5.22 * math.cos(a), 5.22 * math.sin(a), .14, .075, rot=a * 1.7 + i)
PL = join(pp, 'Platina')
while PL.data.uv_layers: PL.data.uv_layers.remove(PL.data.uv_layers[0])
uvl = PL.data.uv_layers.new(name='UVMap')
for poly in PL.data.polygons:
    for li in poly.loop_indices:
        v = PL.data.vertices[PL.data.loops[li].vertex_index].co
        uvl.data[li].uv = (v.x / 10.8 + .5, v.y / 10.8 + .5)

# ---------------------------------------------------------------- Eje (pivote con rubí y tornillos de chatón)
ej = []
ej.append(finish(prism(circ(.2, 32), -.002, .012, STEEL, inner=circ(.15, 32), name='sink')))
ej += jewel(0, 0, .06, .075)
ej += screw(.17, .08, .012, .055, rot=.6)
ej += screw(-.17, -.08, .012, .055, rot=2.1)
join(ej, 'Eje')

# ---------------------------------------------------------------- Ruedas
wheel(12, .5, 'RuedaS', 'S')
wheel(18, .75, 'RuedaM', 'M')
wheel(24, 1.0, 'RuedaL', 'L')

# ---------------------------------------------------------------- Barril
b = []
bp = gear_pts(27, 1.125)
b.append(finish(prism(bp, ZC - TH / 2, ZC + TH / 2, BRASS, inner=inner_of(bp, .96), name='brim')))
drum = lathe([(0, .24), (.97, .24), (1.0, .27), (1.0, .6), (.98, .63), (.9, .64), (0, .64)], BRASS, 'drum', 64); finish(drum, 30)
b.append(drum)
b.append(finish(prism(circ(.93, 64), .64, .652, STEEL, inner=circ(.6, 64), name='cover')))
# espiral grabada en la tapa
sp = [(.62 + (.9 - .62) * t / 3.0 * 1.0, t) for t in [i / 60 * 3.0 for i in range(61)]]
cu = bpy.data.curves.new('spiral', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = .007; cu.bevel_resolution = 0
spl = cu.splines.new('POLY'); spl.points.add(len(sp) - 1)
for i, (rad, t) in enumerate(sp):
    a = t * TAU * .999; spl.points[i].co = (rad * math.cos(a), rad * math.sin(a), .656, 1)
so = bpy.data.objects.new('spiral', cu); C.collection.objects.link(so)
bpy.ops.object.select_all(action='DESELECT'); so.select_set(True); C.view_layer.objects.active = so
bpy.ops.object.convert(target='MESH'); so = C.active_object; so.data.materials.append(BLUE); b.append(so)
# trinquete (dientes de sierra) y cuadrado del árbol
rt = []
for k in range(30):
    a = k / 30 * TAU; a2 = (k + 1) / 30 * TAU
    rt += [(.5 * math.cos(a), .5 * math.sin(a)), (.56 * math.cos(a2 - .01), .56 * math.sin(a2 - .01))]
b.append(finish(bevel(prism(rt, .652, .72, STEEL, name='ratchet'), .006, 1)))
b.append(finish(bevel(prim('cube', loc=(0, 0, .745), scale=(.09, .09, .03), m=STEEL), .01, 1)))
b.append(cyl(.06, .02, .26, STEEL, 16))
for i in range(3):
    a = i / 3 * TAU + .5
    b += screw(.34 * math.cos(a), .34 * math.sin(a), .72, .05, rot=a * 2)
join(b, 'Barril')

# ---------------------------------------------------------------- Escape (piñón de 12 + rueda de escape de 15 dientes en gancho)
e = []
ep = gear_pts(12, .5)
e.append(finish(prism(ep, ZC - TH / 2, ZC + TH / 2, STEEL, inner=inner_of(ep, .36), name='epin')))
e.append(finish(prism(circ(.37, 36), ZC - .02, ZC + .02, STEEL, inner=circ(.12, 36), name='eweb')))
for i in range(6):
    a = i / 6 * TAU
    e.append(cyl(.035, ZC - .03, ZC + .03, BLUE, 12, .25 * math.cos(a), .25 * math.sin(a)))
e.append(cyl(.13, ZC - .05, ZC + .05, STEEL, 24, bv=.01))
e.append(cyl(.03, .02, .86, STEEL, 12))
ew = []
for k in range(15):
    a0 = k / 15 * TAU; p = TAU / 15
    for rad, f in [(.4, 0), (.46, .16), (.52, .33), (.55, .39), (.555, .45), (.5, .5), (.43, .7)]:
        ew.append((rad * math.cos(a0 + f * p), rad * math.sin(a0 + f * p)))
e.append(finish(prism(ew, .70, .74, BRASS, inner=inner_of(ew, .34), name='ewheel')))
for i in range(3):
    e.append(spoke(.08, .36, i / 3 * TAU + .3, .35, .045, .06, .705, .735, BRASS, 8))
e.append(cyl(.09, .69, .75, BRASS, 24, bv=.008))
e.append(finish(prim('cone', loc=(0, 0, .88), vertices=12, radius1=.03, radius2=.008, depth=.04, m=STEEL)))
join(e, 'Escape')

# ---------------------------------------------------------------- Áncora (pivote en origen, el escape queda en -X a .78)
an = []
EX = -.78
P1 = (EX + .55 * math.cos(math.radians(38)), .55 * math.sin(math.radians(38)))
P2 = (P1[0], -P1[1])
def bar(a, b_, w, z0, z1, m):
    dx, dy = b_[0] - a[0], b_[1] - a[1]; l = math.hypot(dx, dy); nx, ny = -dy / l * w / 2, dx / l * w / 2
    return finish(prism([(a[0] - nx, a[1] - ny), (b_[0] - nx, b_[1] - ny), (b_[0] + nx, b_[1] + ny), (a[0] + nx, a[1] + ny)], z0, z1, m, name='bar'))
an.append(bevel(bar((0, 0), (P1[0] + .05, P1[1] + .02), .075, .76, .8, STEEL), .006, 1))
an.append(bevel(bar((0, 0), (P2[0] + .05, P2[1] - .02), .075, .76, .8, STEEL), .006, 1))
an.append(bevel(bar((0, 0), (.6, 0), .06, .76, .8, STEEL), .006, 1))
an.append(bevel(bar((.56, .02), (.68, .085), .04, .76, .8, STEEL), .004, 1))
an.append(bevel(bar((.56, -.02), (.68, -.085), .04, .76, .8, STEEL), .004, 1))
an.append(cyl(.012, .72, .8, STEEL, 8, .62, 0))
for P, s in ((P1, 1), (P2, -1)):
    ang = math.atan2(P[1], P[0] - EX)
    an.append(finish(prim('cube', loc=(P[0], P[1], .75), rot=(0, 0, ang), scale=(.05, .018, .05), m=RUBY), 60))
an.append(cyl(.065, .75, .81, STEEL, 24, bv=.008))
an.append(cyl(.02, .7, .86, STEEL, 10))
join(an, 'Ancora')

# ---------------------------------------------------------------- Volante (plano z=0) + Espiral
vo = []
vo.append(finish(bevel(prism(circ(.62, 64), -.03, .03, GOLD, inner=circ(.555, 64), name='vrim'), .006, 1)))
vo.append(bevel(bar((-.57, 0), (.57, 0), .07, -.018, .018, GOLD), .005, 1))
for i in range(4):
    a = i / 4 * TAU + TAU / 8
    o = prim('cyl', loc=(.645 * math.cos(a), .645 * math.sin(a), 0), rot=(0, math.pi / 2, a), vertices=12, radius=.035, depth=.06, m=BLUE)
    vo.append(finish(o))
for i in range(4):
    a = i / 4 * TAU + TAU / 8 + TAU / 16
    vo.append(finish(prim('cube', loc=(.588 * math.cos(a), .588 * math.sin(a), .035), rot=(0, 0, a), scale=(.014, .03, .008), m=BLUE)))
vo.append(cyl(.035, -.16, .16, STEEL, 12))
vo.append(cyl(.075, -.03, .03, GOLD, 24, bv=.006))
vo.append(cyl(.13, -.09, -.07, STEEL, 32))
vo.append(cyl(.018, -.12, -.07, RUBY, 8, .1, 0))
join(vo, 'Volante')
spp = []
for i in range(7 * 32 + 1):
    t = i / 32; rad = .07 + (.34 - .07) * t / 7; a = t * TAU
    spp.append((rad * math.cos(a), rad * math.sin(a), .08))
cu = bpy.data.curves.new('hs', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = .0055; cu.bevel_resolution = 0
spl = cu.splines.new('POLY'); spl.points.add(len(spp) - 1)
for i, pt in enumerate(spp): spl.points[i].co = (*pt, 1)
ho = bpy.data.objects.new('hs', cu); C.collection.objects.link(ho)
bpy.ops.object.select_all(action='DESELECT'); ho.select_set(True); C.view_layer.objects.active = ho
bpy.ops.object.convert(target='MESH'); ho = C.active_object; ho.data.materials.append(BLUE)
hs = [ho, cyl(.05, .06, .1, STEEL, 16), bar((.34, 0), (.46, .05), .025, .075, .09, STEEL)]
join(hs, 'Espiral')

# ---------------------------------------------------------------- Puente (del barrilete: origen sobre el eje, brazo hacia +X)
def wbridge(x):
    return .47 - .18 * math.sin(min(1, max(0, x / 2.2)) * math.pi) + .03 * x / 2.2
out = []
for i in range(17): a = math.pi / 2 + i / 16 * math.pi; out.append((.47 * math.cos(a), .47 * math.sin(a)))
for i in range(1, 24): x = i / 24 * 2.2; out.append((x, -wbridge(x)))
for i in range(17): a = -math.pi / 2 + i / 16 * math.pi; out.append((2.2 + .5 * math.cos(a), .5 * math.sin(a)))
for i in range(23, 0, -1): x = i / 24 * 2.2; out.append((x, wbridge(x)))
pu = [finish(bevel(prism(out, .8, .92, STEEL, name='bridge'), .035, 1), 30)]
pu += jewel(0, 0, .95, .07)
pu += screw(1.55, .0, .92, .075, rot=.4)
pu += screw(2.35, .25, .92, .075, rot=1.3)
pu.append(cyl(.06, .02, .8, STEEL, 12, 2.2, 0))
join(pu, 'Puente')

# ---------------------------------------------------------------- Jaula de tourbillon (centro en el eje del volante, z=0 en el plano del volante)
ja = []
for z0 in (-.2, .24):
    ja.append(finish(bevel(prism(circ(.86, 48), z0, z0 + .045, STEEL, inner=circ(.78, 48), name='jr'), .008, 1)))
    for i in range(3):
        a = i / 3 * TAU + (.5 if z0 > 0 else 1.5)
        ja.append(bevel(bar((0, 0), (.8 * math.cos(a), .8 * math.sin(a)), .09, z0, z0 + .045, STEEL), .008, 1))
for i in range(3):
    a = i / 3 * TAU + 1.0
    ja.append(cyl(.035, -.2, .28, STEEL, 10, .82 * math.cos(a), .82 * math.sin(a)))
    ja += screw(.55 * math.cos(a + .5), .55 * math.sin(a + .5), .285, .045, rot=a)
ja.append(cyl(.1, .24, .3, STEEL, 24, bv=.008))
join(ja, 'Jaula')

# ---------------------------------------------------------------- Fase lunar: disco (gira) + tapa con ventana
lu = [finish(prism(circ(.42, 64), 0, .02, LAPIS, name='ld'))]
for s in (1, -1):
    lu.append(finish(prism(circ(.12, 32, 0, 0, .25 * s), .02, .03, MOON, name='moon')))
random.seed(7)
for i in range(14):
    a = random.uniform(0, TAU); rr_ = random.uniform(.12, .38)
    if min(math.hypot(rr_ * math.cos(a), rr_ * math.sin(a) - .25 * s_) for s_ in (1, -1)) < .16: continue
    lu.append(finish(prim('ico', subdivisions=0, loc=(rr_ * math.cos(a), rr_ * math.sin(a), .025), radius=.014, m=MOON), 80))
join(lu, 'Luna')
tp = [(-.4, 0), (-.375, 0)]
for i in range(1, 12): a = math.pi - i / 12 * math.pi; tp.append((-.25 + .125 * math.cos(a), .125 * math.sin(a)))
tp += [(-.125, 0), (.125, 0)]
for i in range(1, 12): a = math.pi - i / 12 * math.pi; tp.append((.25 + .125 * math.cos(a), .125 * math.sin(a)))
tp += [(.375, 0), (.4, 0)]
for i in range(1, 24): a = -i / 24 * math.pi; tp.append((.4 * math.cos(a), .4 * math.sin(a)))
lt = [finish(prism(tp, .04, .06, STEEL, name='lcov'))]
lt.append(finish(bevel(prism(circ(.5, 64), 0, .07, GOLD, inner=circ(.4, 64), name='lbez'), .01, 1)))
join(lt, 'LunaTapa')

# ---------------------------------------------------------------- Reloj de vitrina (esfera hacia +Z, las 12 hacia +Y)
cp = [(0, -.3), (.62, -.31), (.78, -.29), (.9, -.24), (.98, -.15), (1.01, -.04), (1.01, .06), (.99, .12), (.97, .15),
      (.965, .2), (.93, .25), (.87, .27), (.84, .26), (.83, .2), (.83, .1)]
ca = [finish(lathe(cp, CASE, 'case', 72), 28)]
for sx in (1, -1):
    for sy in (1, -1):
        lg = prim('cube', loc=(sx * .42, sy * 1.05, -.06), rot=(sy * .22, 0, 0), scale=(.09, .32, .085), m=CASE)
        ca.append(finish(bevel(lg, .035, 2), 35))
ca.append(cyl(.075, -.05, .05, CASE, 16))
ca[-1].rotation_euler = (0, math.pi / 2, 0); ca[-1].location = (1.05, 0, 0)
cr = prim('cyl', loc=(0, 0, 0), vertices=32, radius=.15, depth=.14, m=CASE)
for v in cr.data.vertices:
    if abs(v.co.z) < .069 and False: pass
bm_ = bmesh.new(); bm_.from_mesh(cr.data)
for v in bm_.verts:
    a = math.atan2(v.co.y, v.co.x); k = round(a / (TAU / 32))
    if k % 2: v.co.x *= .88; v.co.y *= .88
bm_.to_mesh(cr.data); bm_.free()
bevel(cr, .02, 1); finish(cr, 40)
cr.rotation_euler = (0, math.pi / 2, 0); cr.location = (1.17, 0, 0)
ca.append(cr)
bpy.ops.object.select_all(action='DESELECT')
for o in ca[-2:]: o.select_set(True)
C.view_layer.objects.active = ca[-1]; bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
join(ca, 'Caja')

es = [finish(prism(circ(.835, 72), .08, .1, DIAL, name='dial'))]
for i in range(12):
    a = math.pi / 2 - i / 12 * TAU
    w = .028 if i else .022
    for dx in ((-.028, .028) if i == 0 else (0,)):
        o = prim('cube', loc=(.66 * math.cos(a) + dx * math.cos(a - math.pi / 2), .66 * math.sin(a) + dx * math.sin(a - math.pi / 2), .112),
                 rot=(0, 0, a), scale=(.075, w / 2 if i else .012, .012), m=IDX)
        es.append(finish(bevel(o, .006, 1), 40))
for i in range(60):
    if i % 5 == 0: continue
    a = i / 60 * TAU
    es.append(prim('plane', loc=(.785 * math.cos(a), .785 * math.sin(a), .101), rot=(0, 0, a), scale=(.018, .003, 1), m=IDX))
es.append(finish(prism(circ(.2, 48, 0, 0, -.4), .1, .106, IDX, inner=circ(.185, 48, 0, 0, -.4), name='sub')))
es.append(cyl(.03, .1, .21, IDX, 12))
join(es, 'Esfera')

def dauphine(L, w, z, name, tail=.08):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    T = bm.verts.new((0, L, z)); BL = bm.verts.new((-w / 2, 0, z)); BR = bm.verts.new((w / 2, 0, z)); TL = bm.verts.new((0, -tail, z))
    R0 = bm.verts.new((0, 0, z + .014))
    for f in ((BL, R0, T), (R0, BR, T), (TL, R0, BL), (TL, BR, R0), (T, BR, TL, BL)): bm.faces.new(f)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); C.collection.objects.link(o); me.materials.append(HAND)
    for p in o.data.polygons: p.use_smooth = False
    return [o, cyl(.045, z - .004, z + .006, HAND, 20)]
join(dauphine(.45, .075, .15, 'ah'), 'AgujaH')
join(dauphine(.7, .06, .17, 'am'), 'AgujaM')
sn = [bar((0, -.2), (0, .76), .012, .19, .197, RUBY), cyl(.028, .186, .2, RUBY, 16), cyl(.04, .186, .2, RUBY, 16, 0, -.17)]
join(sn, 'AgujaS')

ASSETS = ['Platina', 'Eje', 'RuedaS', 'RuedaM', 'RuedaL', 'Barril', 'Escape', 'Ancora', 'Volante', 'Espiral', 'Puente',
          'Jaula', 'Luna', 'LunaTapa', 'Caja', 'Esfera', 'AgujaH', 'AgujaM', 'AgujaS']
for n_ in ASSETS:
    me = bpy.data.objects[n_].data
    if n_ != 'Platina':
        while me.uv_layers: me.uv_layers.remove(me.uv_layers[0])
tot = 0
for n_ in ASSETS:
    ob = bpy.data.objects[n_]; nv = len(ob.data.vertices); nf = len(ob.data.polygons); tot += nv
    print('%-9s verts %5d faces %5d' % (n_, nv, nf))
print('TOTAL verts', tot)
export_glb(ROOT + '/glb/tourbillon.glb', ASSETS)
quantize_glb(ROOT + '/glb/tourbillon.glb')
bpy.ops.wm.save_as_mainfile(filepath=ROOT + '/blend/tourbillon.blend')
print('GLB', os.path.getsize(ROOT + '/glb/tourbillon.glb'))

# ---------------------------------------------------------------- Icono: rueda L + escape + rubíes, macro con luz lateral cálida
if '--noicon' not in sys.argv:
    for n_ in ASSETS: bpy.data.objects[n_].hide_render = True
    def phase(nA, thA, phi, nB):   # ángulo de B para que engrane con A
        return phi + math.pi + math.pi / nB - (thA - phi) * nA / nB
    thL = .0
    phiE = math.radians(-18); E = (1.5 * math.cos(phiE), 1.5 * math.sin(phiE))
    phiS = math.radians(150); S = (1.5 * math.cos(phiS), 1.5 * math.sin(phiS))
    sc = showcase(['Platina', 'RuedaL', 'Escape', 'RuedaS', 'Eje', 'Eje', 'Eje', 'Ancora'],
                  [(-.6, 3.9, 0), (0, 0, 0), (E[0], E[1], 0), (S[0], S[1], 0), (.2, -1.45, 0), (-1.2, -1.2, 0), (2.4, -1.25, 0),
                   (E[0] + .78 * math.cos(phiE), E[1] + .78 * math.sin(phiE), 0)],
                  [(0, 0, 0), (0, 0, thL), (0, 0, phase(24, thL, phiE, 12)), (0, 0, phase(24, thL, phiS, 12)), (0, 0, .3), (0, 0, 1.4), (0, 0, 2.2), (0, 0, phiE + math.pi)])
    render_icon(ROOT + '/renders/tourbillon.png', '#1b2230', (-1.1, -3.6, 3.3), (.45, -.15, .3), lens=46, samples=64,
                lights=[('AREA', (4.5, -1.5, 2.2), 380, '#ffc98a'), ('AREA', (-4, 2, 3.5), 160, '#8fb0ff'),
                        ('AREA', (0, 0, 7), 90, '#ffffff'), ('POINT', (1.4, -1.2, 1.4), 18, '#ff4060')])
    print('OK tourbillon')
