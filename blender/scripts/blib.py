"""Utilidades de modelado para Blender (bpy) usadas por los scripts de cada app."""
import bpy, math, bmesh
from mathutils import Vector, Matrix

C = bpy.context

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def hexrgb(h, a=1.0):
    h = h.lstrip('#'); r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
    lin = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (lin(r), lin(g), lin(b), a)

_mats = {}
def mat(name, color, rough=0.55, metal=0.0, emit=None, emit_str=1.0, alpha=1.0):
    if name in _mats: return _mats[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = hexrgb(color)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    if emit:
        p.inputs['Emission Color'].default_value = hexrgb(emit)
        p.inputs['Emission Strength'].default_value = emit_str
    if alpha < 1:
        p.inputs['Alpha'].default_value = alpha
        try: m.surface_render_method = 'BLENDED'
        except Exception: m.blend_method = 'BLEND'
    m.diffuse_color = hexrgb(color, alpha)
    _mats[name] = m
    return m

OPS = {
    'cube': bpy.ops.mesh.primitive_cube_add, 'cyl': bpy.ops.mesh.primitive_cylinder_add,
    'cone': bpy.ops.mesh.primitive_cone_add, 'sphere': bpy.ops.mesh.primitive_uv_sphere_add,
    'ico': bpy.ops.mesh.primitive_ico_sphere_add, 'torus': bpy.ops.mesh.primitive_torus_add,
    'plane': bpy.ops.mesh.primitive_plane_add, 'circle': bpy.ops.mesh.primitive_circle_add,
}

def prim(kind, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), m=None, smooth=False, **kw):
    OPS[kind](location=loc, rotation=rot, **kw)
    o = C.active_object
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if m: o.data.materials.append(m)
    if smooth: bpy.ops.object.shade_smooth()
    return o

def bevel(o, w=0.03, seg=2):
    md = o.modifiers.new('bv', 'BEVEL'); md.width = w; md.segments = seg; md.limit_method = 'ANGLE'
    C.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier='bv')
    return o

def subsurf(o, lv=1):
    md = o.modifiers.new('ss', 'SUBSURF'); md.levels = lv; md.render_levels = lv
    C.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier='ss')
    return o

def displace(o, strength=0.15, size=0.6, seed=0):
    tex = bpy.data.textures.new('n%d' % seed, 'CLOUDS'); tex.noise_scale = size
    md = o.modifiers.new('dp', 'DISPLACE'); md.texture = tex; md.strength = strength
    C.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier='dp')
    return o

def join(objs, name, origin=(0, 0, 0)):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    C.view_layer.objects.active = objs[0]
    if len(objs) > 1: bpy.ops.object.join()
    o = C.active_object; o.name = name; o.data.name = name
    # origen en 'origin' manteniendo la geometría en coordenadas de mundo
    C.scene.cursor.location = origin
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    o.location = (0, 0, 0)
    C.scene.cursor.location = (0, 0, 0)
    return o

def curve_tube(points, radius, m, name='tube', res=8):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = radius; cu.bevel_resolution = 2
    sp = cu.splines.new('POLY'); sp.points.add(len(points) - 1)
    for i, p in enumerate(points): sp.points[i].co = (*p, 1)
    ob = bpy.data.objects.new(name, cu); C.collection.objects.link(ob)
    C.view_layer.objects.active = ob; bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True)
    bpy.ops.object.convert(target='MESH'); o = C.active_object
    if m: o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return o

def lathe(profile, m, name='lathe', steps=32):
    """profile: lista de (radio, z). Genera superficie de revolución."""
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    rings = []
    for (r, z) in profile:
        ring = [bm.verts.new((r * math.cos(a), r * math.sin(a), z)) for a in [i / steps * 2 * math.pi for i in range(steps)]]
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        for i in range(steps):
            bm.faces.new((a[i], a[(i + 1) % steps], b[(i + 1) % steps], b[i]))
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); C.collection.objects.link(o)
    o.data.materials.append(m)
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); C.view_layer.objects.active = o
    bpy.ops.object.shade_smooth()
    return o

def keep_only(names):
    for o in list(bpy.data.objects):
        if o.name not in names: bpy.data.objects.remove(o, do_unlink=True)

def export_glb(path, names):
    bpy.ops.object.select_all(action='DESELECT')
    for n in names: bpy.data.objects[n].select_set(True)
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_apply=True,
                              export_yup=True, export_materials='EXPORT')

def showcase(names, positions, rotations=None, scales=None):
    """Duplica los assets en una composición para el icono. Devuelve los duplicados."""
    out = []
    for i, n in enumerate(names):
        src = bpy.data.objects[n]
        d = src.copy(); d.data = src.data; C.collection.objects.link(d); d.hide_render = False
        d.location = positions[i]
        if rotations: d.rotation_euler = rotations[i]
        if scales: d.scale = (scales[i],) * 3
        out.append(d)
    return out

def render_icon(path, bg, cam_loc, target=(0, 0, 0), lens=50, size=256, samples=48, lights=None, hide=()):
    sc = C.scene
    for n in hide: bpy.data.objects[n].hide_render = True
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = hexrgb(bg)
    w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0
    cam = bpy.data.objects.new('IconCam', bpy.data.cameras.new('IconCam')); sc.collection.objects.link(cam)
    cam.data.lens = lens; cam.location = cam_loc
    d = Vector(target) - Vector(cam_loc); cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler(); sc.camera = cam
    for (kind, loc, energy, color) in (lights or [('SUN', (4, -4, 8), 3.5, '#fff4e0'), ('AREA', (-5, -3, 4), 400, '#b8d4ff')]):
        L = bpy.data.lights.new('L', kind); L.energy = energy; L.color = hexrgb(color)[:3]
        if kind == 'AREA': L.size = 4
        lo = bpy.data.objects.new('L', L); sc.collection.objects.link(lo); lo.location = loc
        lo.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.render.engine = 'CYCLES'; sc.cycles.samples = samples; sc.cycles.device = 'CPU'
    try: sc.cycles.use_denoising = True
    except Exception: pass
    sc.render.resolution_x = sc.render.resolution_y = size; sc.render.film_transparent = False
    sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Punchy'
    sc.render.image_settings.file_format = 'PNG'; sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
