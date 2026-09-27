"""The living-room pocket doors the walk opens on its way in.

Round 6: the first leaves were plain walnut slabs and read as wall panels.
Each leaf is now a stile-and-rail door with a recessed slat panel, a reeded
glass light framed in black, and a long bronze pull, set in a black steel
casing with a marble threshold. Glass and pulls are drawn live in the
browser (reflection and translucency cannot be baked); the frames, panels
and casing carry baked light.

Client round 5 (September 2026): after Services, the walk should not fly in
from outside; it should stand in the hall before a door, watch it open, and
walk through into the living room.

The doors sit in the living room's opening off the gallery (the 2.8 x 2.8 m
aperture at x 2.3..5.1 in the south gallery partition, y = 6). Two walnut
leaves meet in the middle and slide apart into pockets in the wall, so
nothing swings into the room.

They are built here and not in add_decor.py on purpose: the house's lightmap
is baked with the doorway open (the rooms either side light each other), and
the leaves move at runtime, so they cannot share that atlas. Instead each
leaf's full diffuse look (albedo and baked light) is baked to its own
texture here, in the closed position, and drawn unlit in the browser.

    blender -b -P build_door.py            # writes runtime/door.glb
    cp runtime/door.glb ../../public/models/door.glb

Blender space: x runs along the gallery, y = 6 is the partition's centre,
+y is the gallery side the camera stands on.
"""
import bpy, math, os, sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'runtime'
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'premium-interior.blend'))
scene = bpy.context.scene
M = {m.name: m for m in bpy.data.materials}

X0, X1 = 2.3, 5.1          # opening jambs
Y = 6.0                    # partition centre line
HEIGHT = 2.755             # under the 2.76 lintel
THICK = 0.056
LEAF = (X1 - X0) / 2 + 0.006   # a whisker of overlap at the meeting stiles


def box(name, loc, size, material, bevel=0.004):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(M[material])
    if bevel:
        b = o.modifiers.new('Edge', 'BEVEL')
        b.width = bevel
        b.segments = 2
    return o


def box_uv(o, scale=None, vertical=True):
    """Box-projected UVs at the material's metre scale, slats running up."""
    me = o.data
    uv = me.uv_layers.get('UVMap') or me.uv_layers.new(name='UVMap')
    scale = scale or o.data.materials[0].get('uv_meters', 1)
    for p in me.polygons:
        axis = max(range(3), key=lambda k: abs(p.normal[k]))
        axes = ([1 - axis, 2] if vertical else [0, 1]) if axis in (0, 1) else [0, 1]
        for li in p.loop_indices:
            c = o.matrix_world @ me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv = (c[axes[0]] / scale, c[axes[1]] / scale)


def join(parts, name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts:
        o.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.join()
    o = bpy.context.object
    o.name = name
    return o


STILE, TOP, BOTTOM = 0.13, 0.13, 0.28
MID0, MID1 = 0.98, 1.10          # the mid rail between panel and glass
GLASS_TOP = HEIGHT - TOP


def leaf(side):
    """One leaf, read as a door rather than a panel: a walnut stile-and-rail
    frame, a recessed walnut slat panel low, reeded glass above framed by a
    slim black bead, and a long bronze pull on each face near the meeting
    stile. `side` -1 is the left leaf from the hall, +1 the right."""
    # the left leaf (from the hall) spans centre -> right jamb, larger x
    x0 = (X0 + X1) / 2 if side < 0 else X0 + 0.003
    x1 = x0 + LEAF - 0.003
    cx, w = (x0 + x1) / 2, x1 - x0
    z = lambda a, b: ((a + b) / 2, b - a)
    frame = []
    for sx in (x0 + STILE / 2, x1 - STILE / 2):
        zc, zh = z(0.005, HEIGHT + 0.005)
        frame.append(box('Door stile', (sx, Y, zc), (STILE, THICK, zh), 'Walnut', 0.003))
    for a, b in ((0.005, BOTTOM), (MID0, MID1), (GLASS_TOP, HEIGHT + 0.005)):
        zc, zh = z(a, b)
        frame.append(box('Door rail', (cx, Y, zc), (w - 2 * STILE + 0.002, THICK, zh), 'Walnut', 0.003))
    zc, zh = z(BOTTOM, MID0)
    frame.append(box('Door panel', (cx, Y, zc), (w - 2 * STILE + 0.004, THICK - 0.024, zh + 0.004), 'Walnut slat', 0.002))
    # black bead framing the glass, both faces
    gx0, gx1 = x0 + STILE, x1 - STILE
    for face in (-1, 1):
        yy = Y + face * (THICK / 2 - 0.006)
        for a, b in ((MID1, MID1 + 0.018), (GLASS_TOP - 0.018, GLASS_TOP)):
            zc, zh = z(a, b)
            frame.append(box('Glass bead', (cx, yy, zc), (gx1 - gx0, 0.014, zh), 'Frame black', 0.002))
        for bx in (gx0 + 0.009, gx1 - 0.009):
            zc, zh = z(MID1, GLASS_TOP)
            frame.append(box('Glass bead', (bx, yy, zc), (0.018, 0.014, zh), 'Frame black', 0.002))
    for o in frame:
        box_uv(o)
    body = join(frame, 'DoorLeft' if side < 0 else 'DoorRight')
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

    # reeded glass: its own mesh and material, drawn live in the browser
    zc, zh = z(MID1 + 0.01, GLASS_TOP - 0.01)
    glass = box('Reeded glass', (cx, Y, zc), (gx1 - gx0 - 0.01, 0.012, zh), M['Glass'].name, 0)
    glass.data.materials.clear()
    glass.data.materials.append(bpy.data.materials.get('DoorGlass') or bpy.data.materials.new('DoorGlass'))
    box_uv(glass, scale=0.6)
    glass.visible_shadow = False
    glass.name = f'{body.name}Glass'

    # brushed bronze pull, both faces, on the meeting stile
    pull_x = (x0 + STILE / 2) if side < 0 else (x1 - STILE / 2)
    pulls = []
    for face in (-1, 1):
        y = Y + face * (THICK / 2 + 0.042)
        pulls.append(box('Door pull', (pull_x, y, 1.25), (0.028, 0.028, 1.4), 'Bronze', 0.008))
        for zz in (0.62, 1.25, 1.88):
            pulls.append(box('Door pull post', (pull_x, Y + face * (THICK / 2 + 0.02), zz), (0.018, 0.04, 0.018), 'Bronze', 0.003))
    pull = join(pulls, f'{body.name}Pull')
    pull.data.materials.clear()
    pull.data.materials.append(bpy.data.materials.get('DoorPull') or bpy.data.materials.new('DoorPull'))

    for child in (glass, pull):
        child.parent = body
        child.matrix_parent_inverse = body.matrix_world.inverted()
    return body


def casing():
    """Matte black steel casing round the opening on both faces, and a marble
    threshold: the frame that makes the leaves read as a doorway."""
    parts = []
    for face in (-1, 1):
        yy = Y + face * (0.09 + 0.02)
        for xx in (X0 - 0.05, X1 + 0.05):
            parts.append(box('Door casing', (xx, yy, 1.45), (0.1, 0.04, 2.9), 'Frame black', 0.004))
        parts.append(box('Door casing', ((X0 + X1) / 2, yy, 2.85), (X1 - X0 + 0.2, 0.04, 0.1), 'Frame black', 0.004))
    parts.append(box('Door threshold', ((X0 + X1) / 2, Y, 0.006), (X1 - X0, 0.2, 0.012), 'Marble', 0.002))
    for o in parts:
        box_uv(o, vertical=False)
    return join(parts, 'DoorCasing')


leaves = [leaf(-1), leaf(1)]
frame_casing = casing()
baked_parts = leaves + [frame_casing]

# ------------------------------------------------------------------ bake
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.get_devices()
gpus = [d for d in prefs.devices if d.type != 'CPU']
if gpus:
    prefs.compute_device_type = gpus[0].type
    for d in prefs.devices:
        d.use = d.type != 'CPU'
    scene.cycles.device = 'GPU'
scene.render.engine = 'CYCLES'
scene.cycles.samples = int(os.environ.get('BAKE_SAMPLES', 512))
scene.cycles.use_denoising = True
bake = scene.render.bake
bake.use_pass_direct = True
bake.use_pass_indirect = True
bake.use_pass_color = True     # albedo in: the browser draws these unlit
bake.margin = 8

for o in baked_parts:
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bake_uv = o.data.uv_layers.new(name='BakeUV')
    o.data.uv_layers.active = bake_uv
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.01)
    bpy.ops.object.mode_set(mode='OBJECT')
    img = bpy.data.images.new(f'{o.name} baked', 1024, 2048 if o in leaves else 1024, alpha=False)
    for m in o.data.materials:
        n = m.node_tree.nodes.new('ShaderNodeTexImage')
        n.image = img
        m.node_tree.nodes.active = n
    result = bpy.ops.object.bake(type='DIFFUSE', uv_layer='BakeUV')
    assert 'FINISHED' in result, result
    img.filepath_raw = str(OUT / f'{o.name.lower()}-baked.png')
    img.file_format = 'PNG'
    img.save()
    # swap to one material that carries only the baked image on BakeUV
    baked = bpy.data.materials.new(f'{o.name} Baked')
    baked.use_nodes = True
    nt = baked.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    tex = nt.nodes.new('ShaderNodeTexImage')
    tex.image = img
    uvn = nt.nodes.new('ShaderNodeUVMap')
    uvn.uv_map = 'BakeUV'
    nt.links.new(uvn.outputs[0], tex.inputs['Vector'])
    nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    o.data.materials.clear()
    o.data.materials.append(baked)
    if 'UVMap' in o.data.uv_layers:
        o.data.uv_layers.remove(o.data.uv_layers['UVMap'])
    print('DOOR_BAKED', o.name, flush=True)

# ---------------------------------------------------------------- export
bpy.ops.object.select_all(action='DESELECT')
for o in baked_parts:
    o.select_set(True)
    for child in o.children:
        child.select_set(True)
kwargs = dict(filepath=str(OUT / 'door.glb'), export_format='GLB', use_selection=True, export_apply=True,
              export_yup=True, export_materials='EXPORT', export_cameras=False, export_lights=False,
              export_animations=False, export_texcoords=True, export_normals=True,
              export_image_format='WEBP', export_image_quality=90)
valid = bpy.ops.export_scene.gltf.get_rna_type().properties.keys()
bpy.ops.export_scene.gltf(**{k: v for k, v in kwargs.items() if k in valid})
for o in baked_parts:
    print('DOOR_NODE', o.name, tuple(round(v, 4) for v in o.location), tuple(round(v, 4) for v in o.dimensions))
print('DOOR_EXPORTED', os.path.getsize(OUT / 'door.glb'), flush=True)
