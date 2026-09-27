"""Exterior dressing for the residence.

The shipped model is interior-first: outside it is a flat box on a dark plane,
which is why the landing shot could never look like the reference. This adds
the architecture and the landscape the outside needs, as a separate GLB so the
interior model and its lightmap are never touched.

Built in Blender Z-up. three.js (x, y, z) maps to Blender (x, -z, y), so the
glazed front elevation of the house, at three z = +4, is Blender y = -4.
"""
import bpy, math, os
from mathutils import Vector

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'runtime')
os.makedirs(OUT, exist_ok=True)

# Measured off the shipped mesh, not assumed. In three.js space the house
# mass sits at x 0..20, z -14..0 with the glazed front at z = 0, and a
# courtyard wall runs round it at z = -18, z = +8, x = -9 and x = +29.
# Blender y is -z, so the house is y 0..14 and the terrace is y -8..0.
HX = (0.0, 20.0)
HY = (0.0, 14.0)
YARD = (-8.0, 18.0)        # courtyard walls, Blender y
YARD_X = (-9.0, 29.0)
ROOF = 3.30
OVERHANG = 1.15

M = math.radians


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'


_MATS = {}


def hx(s):
    s = s.lstrip('#')
    srgb = [int(s[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(lin(c) for c in srgb)


def mat(name, base, rough=0.8, metal=0.0, alpha=1.0, emit=None, emit_str=0.0):
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*base, 1.0)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if emit is not None:
        if 'Emission Color' in b.inputs:
            b.inputs['Emission Color'].default_value = (*emit, 1.0)
            b.inputs['Emission Strength'].default_value = emit_str
    if alpha < 1.0:
        b.inputs['Alpha'].default_value = alpha
        m.blend_method = 'BLEND'
    _MATS[name] = m
    return m


def box(name, size, loc, material, rot=(0, 0, 0), bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=2, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(material)
    if bevel > 0:
        md = o.modifiers.new('b', 'BEVEL')
        md.width = bevel
        md.segments = 2
        md.limit_method = 'ANGLE'
        bpy.ops.object.modifier_apply(modifier=md.name)
    return o


def cyl(name, r, h, loc, material, verts=12, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, rotation=rot, vertices=verts)
    o = bpy.context.active_object
    o.name = name
    o.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return o


def sphere(name, r, loc, material, scale=(1, 1, 1), rot=(0, 0, 0), segs=12, rings=7):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, rotation=rot, segments=segs, ring_count=rings)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return o


def build():
    reset()
    P = {
        'render': mat('Ext Render', hx('#efe9e0'), rough=0.85),
        'stone': mat('Ext Travertine', hx('#d9cdba'), rough=0.72),
        'fascia': mat('Ext Fascia', hx('#2b2a28'), rough=0.42, metal=0.35),
        'soffit': mat('Ext Soffit Oak', hx('#8a6340'), rough=0.6),
        'mullion': mat('Ext Mullion', hx('#22211f'), rough=0.34, metal=0.65),
        'deck': mat('Ext Deck', hx('#cfc3ad'), rough=0.78),
        'water': mat('Ext Water', hx('#20323d'), rough=0.035, metal=0.1),
        'coping': mat('Ext Coping', hx('#e0d6c4'), rough=0.6),
        'lawn': mat('Ext Lawn', hx('#71855c'), rough=0.94),
        'hedge': mat('Ext Hedge', hx('#4c5e3c'), rough=0.9),
        'bark': mat('Ext Bark', hx('#453a2f'), rough=0.9),
        'canopy': mat('Ext Canopy', hx('#5a7043'), rough=0.82),
        'canopy2': mat('Ext Canopy Warm', hx('#6e854a'), rough=0.82),
        'lamp': mat('Ext Lamp', hx('#3a2a16'), rough=0.5, emit=hx('#ffc98a'), emit_str=4.0),
    }

    # ---------------------------------------------------------- ground
    # Sits just above the shipped dark plane so the site reads as lawn
    # Large enough that its edge never reads as a horizon line
    box('lawn', (1400, 1400, 0.08), ((HX[0] + HX[1]) / 2, (HY[0] + HY[1]) / 2, -0.10), P['lawn'])

    # ------------------------------------------------- roof and soffit
    rx = (HX[0] - OVERHANG, HX[1] + OVERHANG)
    ry = (HY[0] - OVERHANG, HY[1] + OVERHANG)
    w, d = rx[1] - rx[0], ry[1] - ry[0]
    cx, cy = (rx[0] + rx[1]) / 2, (ry[0] + ry[1]) / 2

    box('roof_slab', (w, d, 0.22), (cx, cy, ROOF + 0.11), P['render'])
    # A dark shadow line under the slab edge is what makes a roof read as thin.
    # The fascia wraps the slab 2 cm proud of it: sharing the slab's edge
    # plane made the two z-fight into a black and white shimmer (client
    # review, September 2026).
    P2 = 0.02
    for tag, size, loc in (
        ('s', (w + 2 * P2, 0.09, 0.26), (cx, ry[0] + 0.045 - P2, ROOF + 0.10)),
        ('n', (w + 2 * P2, 0.09, 0.26), (cx, ry[1] - 0.045 + P2, ROOF + 0.10)),
        ('w', (0.09, d + 2 * P2, 0.26), (rx[0] + 0.045 - P2, cy, ROOF + 0.10)),
        ('e', (0.09, d + 2 * P2, 0.26), (rx[1] - 0.045 + P2, cy, ROOF + 0.10)),
    ):
        box('fascia_' + tag, size, loc, P['fascia'])

    # Warm timber under the overhang, visible from below and from the terrace
    for tag, size, loc in (
        ('s', (w, OVERHANG, 0.04), (cx, HY[0] - OVERHANG / 2, ROOF - 0.025)),
        ('n', (w, OVERHANG, 0.04), (cx, HY[1] + OVERHANG / 2, ROOF - 0.025)),
        ('w', (OVERHANG, d, 0.04), (HX[0] - OVERHANG / 2, cy, ROOF - 0.025)),
        ('e', (OVERHANG, d, 0.04), (HX[1] + OVERHANG / 2, cy, ROOF - 0.025)),
    ):
        box('soffit_' + tag, size, loc, P['soffit'])

    # ------------------------------------------------------ base course
    for tag, size, loc in (
        ('s', (HX[1] - HX[0] + 0.24, 0.12, 0.42), ((HX[0] + HX[1]) / 2, HY[0] - 0.06, 0.21)),
        ('n', (HX[1] - HX[0] + 0.24, 0.12, 0.42), ((HX[0] + HX[1]) / 2, HY[1] + 0.06, 0.21)),
        ('w', (0.12, HY[1] - HY[0], 0.42), (HX[0] - 0.06, (HY[0] + HY[1]) / 2, 0.21)),
        ('e', (0.12, HY[1] - HY[0], 0.42), (HX[1] + 0.06, (HY[0] + HY[1]) / 2, 0.21)),
    ):
        box('plinth_' + tag, size, loc, P['stone'])

    # ------------------------------------------- mullions on the front
    # Slim verticals over the existing glazing so it reads as a window wall
    n_bays = 9
    step = (HX[1] - HX[0] - 1.0) / n_bays
    for i in range(n_bays + 1):
        x = HX[0] + 0.5 + i * step
        box('mullion_%02d' % i, (0.07, 0.14, ROOF - 0.1), (x, HY[0] - 0.09, (ROOF - 0.1) / 2), P['mullion'])
    box('transom', (HX[1] - HX[0] - 1.0, 0.1, 0.06), ((HX[0] + HX[1]) / 2, HY[0] - 0.09, 2.45), P['mullion'])
    box('head_rail', (HX[1] - HX[0] - 1.0, 0.12, 0.09), ((HX[0] + HX[1]) / 2, HY[0] - 0.09, ROOF - 0.12), P['mullion'])

    # ------------------------------------------------- terrace and pool
    # The courtyard is only eight metres deep, so deck and pool share it
    box('deck', (YARD_X[1] - YARD_X[0], 3.4, 0.10), ((YARD_X[0] + YARD_X[1]) / 2, HY[0] - 1.7, -0.02), P['deck'])
    box('deck_edge', (YARD_X[1] - YARD_X[0], 0.18, 0.16), ((YARD_X[0] + YARD_X[1]) / 2, HY[0] - 3.4, -0.06), P['stone'])

    # The courtyard is too tight for water, so the reflecting pool sits in
    # the lawn beyond the wall, where it can hold the sky and the house.
    px, py = (-1.0, 23.0), (-21.0, -12.5)
    pw, pd = px[1] - px[0], py[1] - py[0]
    pcx, pcy = (px[0] + px[1]) / 2, (py[0] + py[1]) / 2
    box('pool_basin', (pw + 0.8, pd + 0.8, 0.5), (pcx, pcy, -0.42), P['coping'])
    box('pool_water', (pw, pd, 0.06), (pcx, pcy, -0.09), P['water'])
    for tag, size, loc in (
        ('n', (pw + 0.8, 0.4, 0.12), (pcx, py[1] + 0.2, -0.06)),
        ('s', (pw + 0.8, 0.4, 0.12), (pcx, py[0] - 0.2, -0.06)),
        ('w', (0.4, pd + 0.8, 0.12), (px[0] - 0.2, pcy, -0.06)),
        ('e', (0.4, pd + 0.8, 0.12), (px[1] + 0.2, pcy, -0.06)),
    ):
        box('pool_cope_' + tag, size, loc, P['coping'])

    # ------------------------------------------------------- planting
    def hedge(name, x0, x1, y, h=0.85, d=0.9):
        box(name, (x1 - x0, d, h), ((x0 + x1) / 2, y, h / 2 - 0.05), P['hedge'], bevel=0.12)

    # Softening the courtyard wall from the inside, and the lawn beyond it
    hedge('hedge_yard_w', YARD_X[0] + 0.4, 2.0, YARD[0] + 0.9, h=0.7, d=0.8)
    hedge('hedge_yard_e', 18.0, YARD_X[1] - 0.4, YARD[0] + 0.9, h=0.7, d=0.8)
    hedge('hedge_outer_w', -16.0, -3.0, YARD[0] - 4.6, h=0.9, d=1.1)
    hedge('hedge_outer_e', 23.5, 36.0, YARD[0] - 4.6, h=0.9, d=1.1)

    def tree(name, loc, h=6.0, spread=2.4, tufts=6):
        cyl(name + '_trunk', 0.17, h * 0.6, (loc[0], loc[1], loc[2] + h * 0.3), P['bark'], verts=8)
        for i in range(tufts):
            a = i * 2.399
            rad = spread * (0.3 + 0.5 * ((i % 3) / 3))
            z = loc[2] + h * (0.56 + 0.34 * ((i % 4) / 4))
            sphere(name + '_t%d' % i, spread * 0.55,
                   (loc[0] + math.cos(a) * rad * 0.7, loc[1] + math.sin(a) * rad * 0.7, z),
                   P['canopy'] if i % 2 else P['canopy2'], scale=(1, 1, 0.7))

    # Kept clear of the approach corridor, which runs from roughly
    # (31, -21) to (-4, 7) in this space. A tree on that line fills the
    # landing frame and hides the house.
    # All outside the courtyard, and clear of the approach corridor, which
    # runs roughly from (31, -21) to (-4, 7) in this space.
    # The sphere-cluster trees and shrubs read as toys through the bedroom
    # window and from the terrace (client review, September 2026), so the
    # realtime exterior carries none. The landing's trees are in the Cycles
    # hero render instead, and the terrace has real olives (add_decor.py).
    if os.environ.get('EXTERIOR_TREES'):
        tree('tree_w1', (-15.0, 6.0, -0.05), 6.6, 2.6, 7)
        tree('tree_w2', (-13.0, 17.0, -0.05), 5.6, 2.2, 6)
        tree('tree_e1', (34.0, 6.0, -0.05), 6.4, 2.5, 7)
        tree('tree_e2', (37.0, 17.0, -0.05), 5.8, 2.3, 6)
        tree('tree_n1', (6.0, 24.0, -0.05), 7.0, 2.8, 7)
        tree('tree_n2', (20.0, 23.0, -0.05), 6.0, 2.4, 6)
        tree('tree_s1', (-18.0, -16.0, -0.05), 6.2, 2.5, 6)

        for i in range(12):
            x = -4.0 + i * 2.8
            sphere('shrub_%02d' % i, 0.5, (x, YARD[0] - 2.0, 0.2), P['hedge'], scale=(1, 1, 0.72))

    for i in range(4):
        box('stone_%02d' % i, (1.6, 0.9, 0.1), (11.0, YARD[0] - 3.4 - i * 1.5, -0.04), P['coping'])

    # ---------------------------------------------------- step lighting
    for i in range(8):
        x = 1.8 + i * 2.4
        box('step_light_%02d' % i, (0.3, 0.05, 0.035), (x, HY[0] - 3.3, 0.02), P['lamp'])

    # ---------------------------------------------------------- merge
    bpy.ops.object.select_all(action='DESELECT')
    groups = {}
    for o in list(bpy.context.scene.objects):
        if o.type != 'MESH' or not o.data.materials:
            continue
        groups.setdefault(o.data.materials[0].name, []).append(o)
    for name, objs in groups.items():
        if len(objs) < 2:
            continue
        bpy.ops.object.select_all(action='DESELECT')
        for o in objs:
            o.select_set(True)
        bpy.context.view_layer.objects.active = objs[0]
        bpy.ops.object.join()
        bpy.context.view_layer.objects.active.name = 'Ext_' + name.replace(' ', '_')
    bpy.ops.object.select_all(action='SELECT')

    deps = bpy.context.evaluated_depsgraph_get()
    tris = 0
    for o in bpy.context.scene.objects:
        if o.type != 'MESH':
            continue
        me = o.evaluated_get(deps).to_mesh()
        me.calc_loop_triangles()
        tris += len(me.loop_triangles)
        o.evaluated_get(deps).to_mesh_clear()
    meshes = len([o for o in bpy.context.scene.objects if o.type == 'MESH'])
    print('EXT_STATS meshes=%d triangles=%d materials=%d' % (meshes, tris, len(bpy.data.materials)))

    path = os.path.join(OUT, 'exterior.glb')
    want = dict(filepath=path, export_format='GLB', export_apply=True, export_yup=True,
                use_selection=True, export_materials='EXPORT', export_cameras=False,
                export_lights=False, export_animations=False, export_texcoords=False,
                export_normals=True, export_draco_mesh_compression_enable=True,
                export_draco_mesh_compression_level=6)
    valid = bpy.ops.export_scene.gltf.get_rna_type().properties.keys()
    bpy.ops.export_scene.gltf(**{k: v for k, v in want.items() if k in valid})
    print('EXT_EXPORTED', path, os.path.getsize(path))


build()
