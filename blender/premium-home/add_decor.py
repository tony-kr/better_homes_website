"""Wall dressing for the five rooms the website walks through.

Client feedback, September 2026: the walls read as plain plaster, not the work
of a premium interior studio. This pass adds fluted oak panelling, book-matched
marble, framed artwork, a walnut sideboard, open shelving, and potted plants to
the living room, dining, kitchen, primary bedroom and terrace, plus a run of
framed pieces down the gallery the camera travels through.

    python3 make_decor_textures.py                      # once, writes textures/
    blender -b -P add_decor.py                          # dresses premium-interior.blend
    blender -b -P add_decor.py -- --preview living,dining   # plus draft Cycles stills

The undressed source is kept as premium-interior.pre-decor.blend. Running this
again starts from that copy, so the pass never stacks on itself.

Coordinates are Blender metres: the glazed south facade is y = 0, the gallery
runs y 6..8, and the living room is x 0..7 (see concept-rooms.json).
"""
import bpy, bmesh, math, random, shutil, sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
SRC = ROOT / 'premium-interior.blend'
CLEAN = ROOT / 'premium-interior.pre-decor.blend'
TEX = ROOT / 'textures'
if not CLEAN.exists():
    shutil.copy2(SRC, CLEAN)
bpy.ops.wm.open_mainfile(filepath=str(CLEAN))
scene = bpy.context.scene
random.seed(51)
M = {m.name: m for m in bpy.data.materials}
added = []


# ------------------------------------------------------------ materials
def principled(m):
    return next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')


def solid(name, color, rough=.6, metal=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    p = principled(m)
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    m.diffuse_color = (*color, 1)
    M[name] = m
    return m


def pbr(name, stem, uv_meters, normal_strength=.25):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nodes, links = m.node_tree.nodes, m.node_tree.links
    p = principled(m)
    for suffix, socket in (('color', 'Base Color'), ('rough', 'Roughness'), ('normal', 'Normal')):
        img = bpy.data.images.load(str(TEX / f'{stem}-{suffix}.png'), check_existing=True)
        if suffix != 'color':
            img.colorspace_settings.name = 'Non-Color'
        t = nodes.new('ShaderNodeTexImage')
        t.image = img
        if suffix == 'normal':
            n = nodes.new('ShaderNodeNormalMap')
            n.inputs['Strength'].default_value = normal_strength
            links.new(t.outputs['Color'], n.inputs['Color'])
            links.new(n.outputs[0], p.inputs[socket])
        else:
            links.new(t.outputs['Color'], p.inputs[socket])
    m['uv_meters'] = uv_meters
    M[name] = m
    return m


def artwork(name, stem):
    """Canvas material that maps its image once across the face (fit UVs)."""
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    p = principled(m)
    img = bpy.data.images.load(str(TEX / f'{stem}.png'), check_existing=True)
    t = m.node_tree.nodes.new('ShaderNodeTexImage')
    t.image = img
    m.node_tree.links.new(t.outputs['Color'], p.inputs['Base Color'])
    p.inputs['Roughness'].default_value = .85
    m['fit_uv'] = True
    M[name] = m
    return m


pbr('Fluted oak', 'fluted-oak', .6, .45)
pbr('Marble', 'marble', 2.4, .15)
pbr('Walnut', 'walnut', 1.6, .2)
pbr('Glazed ceramic', 'ceramic', .5, .2)
pbr('Dark ceramic', 'ceramic-dark', .5, .2)
solid('Frame black', (.028, .026, .024), .42)
solid('Mat board', (.86, .84, .80), .9)
solid('Olive leaf', (.16, .21, .12), .55)
solid('Fig leaf', (.07, .16, .06), .42)
solid('Bark', (.16, .12, .09), .85)
solid('Potting soil', (.07, .055, .04), 1)
solid('Lemon', (.78, .6, .12), .45)
solid('Dried stem', (.52, .43, .30), .8)
ART = {k: artwork(f'Art {k}', f'art-{k}') for k in ('arches', 'enso', 'field', 'horizon', 'botanical', 'stones', 'collage', 'organic', 'blocks')}

# Reference redesign (client round 4): walnut slats, jute, boucle, stone
pbr('Walnut slat', 'walnut-slat', .6, .5)
pbr('Jute', 'jute', .9, .45)
pbr('Boucle', 'boucle', .45, .45)
pbr('Stone', 'stone', .8, .25)


def emissive(name, color, strength):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    p = principled(m)
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Emission Color'].default_value = (*color, 1)
    p.inputs['Emission Strength'].default_value = strength
    m.diffuse_color = (*color, 1)
    M[name] = m
    return m


emissive('LED warm', (1.0, .74, .46), 9)
solid('Headboard sand', (.62, .55, .46), .9)


# -------------------------------------------------------------- helpers
def box(name, loc, size, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(M[material] if isinstance(material, str) else material)
    if bevel:
        b = o.modifiers.new('Edge', 'BEVEL')
        b.width = bevel
        b.segments = 2
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    added.append(o)
    return o


def cyl(name, loc, r, depth, material, verts=40, r2=None):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r if r2 is None else r2,
                                    depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(M[material])
    for p in o.data.polygons:
        p.use_smooth = True
    added.append(o)
    return o


def remove(*prefixes, within=None):
    for o in list(scene.objects):
        if not any(o.name.startswith(p) for p in prefixes):
            continue
        if within:
            c = o.matrix_world.translation
            x0, y0, x1, y1 = within
            if not (x0 <= c.x <= x1 and y0 <= c.y <= y1):
                continue
        bpy.data.objects.remove(o, do_unlink=True)


# Wall normal: which way the dressed face looks into the room.
#   '+x' = on a west wall looking east, '-x' = east wall looking west,
#   '+y' = on a south-side wall looking north, '-y' = north wall looking south.
def on_wall(face, plane, along, z, w, h, depth):
    """Centre and size for a slab of `depth` fixed to the wall plane."""
    axis, sign = face[1], (1 if face[0] == '+' else -1)
    c = plane + sign * depth / 2
    if axis == 'x':
        return (c, along, z), (depth, w, h)
    return (along, c, z), (w, depth, h)


def panel(name, face, plane, a0, a1, z0, z1, material, depth=.03):
    loc, size = on_wall(face, plane, (a0 + a1) / 2, (z0 + z1) / 2, a1 - a0, z1 - z0, depth)
    return box(name, loc, size, material, .002)


def framed_art(face, plane, along, z, w, h, art, mat=.07):
    """Black oak frame, white mat, artwork recessed behind the mat window."""
    sign = 1 if face[0] == '+' else -1
    fd = .035
    loc, size = on_wall(face, plane, along, z, w, h, fd)
    frame = box('Art frame', loc, size, 'Frame black', .004)
    # mat board sits proud of the frame's back, just behind the frame lip
    inner_w, inner_h = w - .05, h - .05
    loc, size = on_wall(face, plane + sign * fd, along, z, inner_w, inner_h, .004)
    box('Art mat', loc, size, 'Mat board')
    loc, size = on_wall(face, plane + sign * (fd + .004), along, z, inner_w - 2 * mat, inner_h - 2 * mat, .002)
    canvas = box('Artwork', loc, size, ART[art])
    # the frame is solid, so hollow its front so the mat shows through
    loc, size = on_wall(face, plane + sign * (fd - .012), along, z, inner_w, inner_h, .03)
    cut = box('cut', loc, size, 'Frame black')
    mod = frame.modifiers.new('Window', 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.solver = 'EXACT'
    mod.object = cut
    bpy.context.view_layer.objects.active = frame
    bpy.ops.object.modifier_apply(modifier='Window')
    bpy.data.objects.remove(cut, do_unlink=True)
    added.remove(cut)
    return canvas


def leaf_mesh(name, length, width, material, fold=.25):
    """A single curved leaf: pointed ellipse with a folded midrib."""
    verts, faces = [], []
    n = 7
    for i in range(n + 1):
        t = i / n
        half = width * math.sin(math.pi * t) ** .8 / 2
        bend = -.18 * length * t * t
        verts += [(-half, t * length, bend + half * fold * .5), (0, t * length, bend), (half, t * length, bend + half * fold * .5)]
    for i in range(n):
        a = i * 3
        faces += [(a, a + 3, a + 4, a + 1), (a + 1, a + 4, a + 5, a + 2)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.materials.append(M[material])
    for p in me.polygons:
        p.use_smooth = True
    return me


FIG = leaf_mesh('Fig leaf', .26, .19, 'Fig leaf', .5)
OLIVE = leaf_mesh('Olive leaf', .085, .018, 'Olive leaf', .2)
SWORD = leaf_mesh('Sword leaf', 1.0, .075, 'Fig leaf', .6)


def place_leaf(me, at, direction, roll, scale=1.0):
    o = bpy.data.objects.new(me.name, me)
    scene.collection.objects.link(o)
    o.location = at
    q = Vector(direction).normalized().to_track_quat('Y', 'Z')
    o.rotation_euler = q.to_euler()
    o.rotation_euler.rotate_axis('Y', roll)
    o.scale = (scale, scale, scale)
    added.append(o)
    return o


def stem(points, radius, material='Bark'):
    cu = bpy.data.curves.new('Stem', 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = radius
    cu.bevel_resolution = 2
    sp = cu.splines.new('POLY')
    sp.points.add(len(points) - 1)
    for p, co in zip(sp.points, points):
        p.co = (*co, 1)
    cu.materials.append(M[material])
    o = bpy.data.objects.new('Plant stem', cu)
    scene.collection.objects.link(o)
    added.append(o)
    return o


def pot(x, y, r, h, material='Glazed ceramic', taper=.82):
    cyl('Planter', (x, y, h / 2), r, h, material, 48, r * taper)
    cyl('Potting soil', (x, y, h - .03), r * .92, .02, 'Potting soil', 32)


def fiddle_leaf(x, y, height=1.9, pot_r=.24):
    """Fiddle-leaf fig: tall ceramic pot, a single trunk, broad leaves up top."""
    ph = .5
    pot(x, y, pot_r, ph)
    top = ph + height
    lean = Vector((random.uniform(-.08, .08), random.uniform(-.08, .08), 0))
    pts = [Vector((x, y, ph - .02)) + lean * (t * t) + Vector((0, 0, t * (height - .1))) for t in (0, .35, .7, 1)]
    stem([tuple(p) for p in pts], .018)
    for i in range(46):
        t = .32 + .68 * (i / 46)
        base = pts[0].lerp(pts[-1], t)
        a = i * 2.39996
        out = Vector((math.cos(a), math.sin(a), .35 + random.uniform(-.25, .35)))
        place_leaf(FIG, base + out * .02, out, random.uniform(-.6, .6), random.uniform(.85, 1.25))


def olive_tree(x, y, height=2.2, pot_r=.34, material='Dark ceramic'):
    """Multi-stem olive in a wide planter: a dense, rounded crown of fine
    silvery leaves carried on three leaning stems."""
    ph = .6
    pot(x, y, pot_r, ph, material, .88)
    crown = Vector((x, y, ph + height * .78))
    for s in range(3):
        a = s * 2.1 + .4
        tip = Vector((x + math.cos(a) * .22, y + math.sin(a) * .22, ph + height * random.uniform(.72, .82)))
        mid = Vector((x + math.cos(a) * .08, y + math.sin(a) * .08, ph + height * .4))
        stem([(x, y, ph - .02), tuple(mid), tuple(tip)], .03)
        for b in range(3):
            ba = a + (b - 1) * .9
            twig = tip + Vector((math.cos(ba) * .3, math.sin(ba) * .3, random.uniform(.05, .3)))
            stem([tuple(tip), tuple(twig)], .012)
    rx, rz = height * .3, height * .2
    for c in range(34):
        u = random.uniform(0, 2 * math.pi)
        v = random.uniform(-.6, 1)
        r = random.uniform(.55, 1)
        cc = crown + Vector((math.cos(u) * rx * r * math.sqrt(1 - v * v), math.sin(u) * rx * r * math.sqrt(1 - v * v), v * rz))
        for k in range(30):
            at = cc + Vector((random.uniform(-.13, .13), random.uniform(-.13, .13), random.uniform(-.1, .1)))
            d = (at - crown).normalized() + Vector((0, 0, .4))
            place_leaf(OLIVE, at, d, random.uniform(0, 3.1), random.uniform(1.1, 1.6))


def snake_plant(x, y, pot_r=.17):
    ph = .34
    pot(x, y, pot_r, ph, 'Dark ceramic', .9)
    for i in range(13):
        a = i * 2.39996
        at = Vector((x + math.cos(a) * pot_r * .45, y + math.sin(a) * pot_r * .45, ph - .03))
        d = Vector((math.cos(a) * .12, math.sin(a) * .12, 1))
        place_leaf(SWORD, at, d, random.uniform(0, 3.1), random.uniform(.55, .95))


def vase_with_stems(x, y, z, h=.34):
    cyl('Stoneware vase', (x, y, z + h / 2), .085, h, 'Glazed ceramic', 40, .05)
    for i in range(7):
        a = i * 0.9 - 2.7
        tip = (x + math.sin(a) * .28, y + math.cos(a) * .1, z + h + .45 + random.uniform(-.1, .15))
        stem([(x, y, z + h * .6), (x + math.sin(a) * .08, y, z + h + .15), tip], .0035, 'Dried stem')
        for k in range(10):
            t = .55 + k * .045
            p = Vector((x, y, z + h * .6)).lerp(Vector(tip), t)
            place_leaf(OLIVE, p, Vector((math.sin(a), .2, .8)), k * .9, .8)


def books(x, y, z, count, along='x'):
    tones = ['Book cream', 'Book dark', 'Oat velvet', 'Paper']
    off = 0
    for i in range(count):
        t = .022 + random.random() * .018
        h = .2 + random.random() * .07
        d = .15 + random.random() * .03
        loc = (x + off, y, z + h / 2) if along == 'x' else (x, y + off, z + h / 2)
        size = (t, d, h) if along == 'x' else (d, t, h)
        box('Shelf book', loc, size, tones[i % 4], .002)
        off += t + .002


# ======================================================== living, x 0..7
remove('Art frame', 'Art canvas', 'Abstract relief art', within=(0, 0, 7, 6))
# West wall: fluted oak full height either side of a book-matched marble
# slab, the media joinery sitting in front of the marble.
W_FACE = .1
panel('Fluted oak panelling', '+x', W_FACE, .2, 1.95, 0, 2.93, 'Fluted oak')
panel('Fluted oak panelling', '+x', W_FACE, 4.05, 5.8, 0, 2.93, 'Fluted oak')
panel('Marble feature slab', '+x', W_FACE, 1.95, 4.05, 0, 2.93, 'Marble', .025)
for a in (1.95, 4.05):
    panel('Bronze shadow gap', '+x', W_FACE, a - .006, a + .006, 0, 2.93, 'Bronze', .034)
framed_art('+x', W_FACE + .025, 3.0, 1.72, 1.2, 1.2, 'collage', .1)
# Gallery wall behind the sofa: a pair of framed pieces, olive tree between
G_FACE = 5.91
framed_art('-y', G_FACE, 1.2, 1.62, .86, 1.08, 'organic')
framed_art('-y', G_FACE, 6.05, 1.62, .86, 1.08, 'blocks')
panel('Oak wainscot', '-y', G_FACE, .1, 2.3, 0, .95, 'Fluted oak', .02)
panel('Oak wainscot', '-y', G_FACE, 5.1, 7.0, 0, .95, 'Fluted oak', .02)
fiddle_leaf(.55, 5.35, 1.75)
# Side table with a lamp and books at the sofa's west arm
cyl('Walnut side table', (1.15, 4.25, .27), .24, .54, 'Walnut', 48)
cyl('Table lamp base', (1.15, 4.25, .66), .07, .24, 'Glazed ceramic', 40, .05)
cyl('Table lamp shade', (1.15, 4.25, .9), .17, .24, 'Linen', 40, .13)
books(1.0, 4.15, .54, 3)

# ======================================================== dining, x 7..12
# Kitchen screen, dining face (x = 11.91, y 0..3): oak panelled wall, a long
# walnut sideboard, a large artwork and a vase of dried stems.
S_FACE = 11.91
panel('Fluted oak panelling', '-x', S_FACE, .3, 2.98, 0, 2.93, 'Fluted oak')
box('Walnut sideboard', (S_FACE - .03 - .22, 1.64, .4), (.44, 2.1, .74), 'Walnut', .01)
box('Sideboard marble top', (S_FACE - .03 - .225, 1.64, .785), (.46, 2.14, .03), 'Marble', .004)
for yy in (.86, 1.38, 1.9, 2.42):
    box('Sideboard door line', (S_FACE - .03 - .445, yy, .4), (.004, .004, .62), 'Bronze')
framed_art('-x', S_FACE - .03, 1.64, 1.8, 1.1, 1.3, 'organic')
vase_with_stems(S_FACE - .25, 2.35, .8)
cyl('Stoneware bowl', (S_FACE - .25, 1.0, .83), .13, .07, 'Dark ceramic', 40, .09)
# Dining gallery wall: a tall botanical and a snake plant in the corner
# (11.4, 5.25) is the dining camera stop, so the plant keeps to the far corner
framed_art('-y', G_FACE, 11.33, 1.6, .7, 1.0, 'botanical')
snake_plant(7.45, 5.5)

# ======================================================= kitchen, x 12..17
K_FACE = 12.09
panel('Fluted oak panelling', '+x', K_FACE, .3, 2.98, 0, 2.93, 'Fluted oak')
framed_art('+x', K_FACE + .03, 1.64, 1.75, .9, 1.15, 'enso')
# Marble splashback and a floating oak shelf over the east counter
E_FACE = 16.9
panel('Marble splashback', '-x', E_FACE, 4.18, 5.8, .97, 2.2, 'Marble', .02)
box('Floating oak shelf', (E_FACE - .02 - .14, 4.99, 1.72), (.28, 1.6, .045), 'Oak', .003)
for yy, h, mat in ((4.45, .22, 'Glazed ceramic'), (4.62, .16, 'Dark ceramic'), (5.4, .26, 'Glazed ceramic')):
    cyl('Shelf ceramic', (E_FACE - .15, yy, 1.745 + h / 2), .06, h, mat, 32, .045)
books(E_FACE - .15, 4.9, 1.745, 5, along='y')
# Fruit bowl on the island, herbs by the sink
cyl('Fruit bowl', (14.1, 3.55, 1.02), .18, .08, 'Dark ceramic', 48, .12)
for i in range(5):
    a = i * 1.26
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=.04,
                                         location=(14.1 + math.cos(a) * .08, 3.55 + math.sin(a) * .08, 1.08))
    o = bpy.context.object
    o.name = 'Lemon'
    o.scale = (1, 1, 1.15)
    o.data.materials.append(M['Lemon'])
    for p in o.data.polygons:
        p.use_smooth = True
    added.append(o)
snake_plant(16.0, .6, .15)

# ====================================================== bedroom, x 12..17, y 8..14
B_WEST = 12.09
panel('Fluted oak panelling', '+x', B_WEST, 8.3, 13.55, 0, 1.1, 'Fluted oak', .02)
panel('Oak dado rail', '+x', B_WEST + .02, 8.3, 13.55, 1.09, 1.13, 'Oak', .015)
framed_art('+x', B_WEST, 10.9, 1.85, 1.6, 1.25, 'blocks', .08)
B_EAST = 16.91
framed_art('-x', B_EAST, 11.0, 1.62, .6, .82, 'botanical')
fiddle_leaf(16.5, 8.5, 1.55, .2)
box('Upholstered bench', (14.5, 10.95, .23), (1.6, .45, .1), 'Oat velvet', .03)
for dx in (-.72, .72):
    box('Bench leg', (14.5 + dx, 10.95, .09), (.05, .38, .18), 'Walnut', .005)

# ====================================================== garden borders
# The concept's outdoor plants are low-poly sprigs that read as plastic from
# the terrace; the perimeter planters get a clean row of sansevieria instead.
def centre(o):
    return sum((o.matrix_world @ Vector(c) for c in o.bound_box), Vector()) / 8


for o in list(scene.objects):
    if o.name.startswith(('Botanical leaf', 'Plant stem', 'Foliage')) and not (0 <= centre(o).y <= 14):
        bpy.data.objects.remove(o, do_unlink=True)
for o in list(scene.objects):
    if o.name.startswith('Stone planter') and centre(o).y < -4:
        bpy.data.objects.remove(o, do_unlink=True)
for yy in (-5.4, 15.8):
    for i in range(22):
        x = -3.6 + i * 1.3
        at = (x + random.uniform(-.15, .15), yy + random.uniform(-.2, .2))
        first = len(added)
        snake_plant(*at, .16)
        # planted in the bed, not potted: drop the pot, sink the leaves in
        for o in added[first:]:
            if o.name.startswith(('Planter', 'Potting soil')):
                bpy.data.objects.remove(o, do_unlink=True)
            else:
                o.location.z += .1
        del added[first:first + 2]

# ====================================================== terrace, y -4..0
for x, y, h in ((9.8, -3.5, 2.3), (14.6, -3.5, 2.1), (17.3, -.9, 2.4)):
    olive_tree(x, y, h, .38, 'Stone')
for x in (9.2, 12.8):
    snake_plant(x, -.45, .2)

# ===================================================== gallery, y 6..8
# A run of framed pieces on the north partition, between the bedroom doors.
N_FACE = 7.91
for x, art in ((1.6, 'collage'), (5.25, 'botanical'), (8.75, 'blocks'), (12.2, 'organic'), (16.2, 'field')):
    framed_art('-y', N_FACE, x, 1.62, .7 if art != 'stones' else 1.1, .9 if art != 'stones' else .76, art)

# =========================================== reference redesign (round 4)
# The client's references (interiors/ in the site repo) share one language:
# walnut slat walls washed with warm LED, travertine and cream marble,
# boucle and linen, jute rugs, walnut frames, olive trees in stone pots,
# collage art, and low golden sun through the glass. Everything below moves
# the five walk rooms onto that palette and relights the house for it.
def centre_of(o):
    return sum((o.matrix_world @ Vector(c) for c in o.bound_box), Vector()) / 8


def pick(prefixes, region=None):
    """Objects whose name starts with any prefix, optionally inside (x0, y0, x1, y1)."""
    if isinstance(prefixes, str):
        prefixes = (prefixes,)
    out = []
    for o in scene.objects:
        if not o.name.startswith(prefixes) or o.type not in ('MESH', 'CURVE'):
            continue
        if region:
            c = centre_of(o)
            x0, y0, x1, y1 = region
            if not (x0 <= c.x <= x1 and y0 <= c.y <= y1):
                continue
        out.append(o)
    return out


def restyle(prefixes, material, region=None):
    for o in pick(prefixes, region):
        o.data.materials.clear()
        o.data.materials.append(M[material])
        if o not in added:
            added.append(o)  # so the UV pass re-projects it at the new scale


def drop(prefixes, region=None):
    for o in pick(prefixes, region):
        if o in added:
            added.remove(o)
        bpy.data.objects.remove(o, do_unlink=True)


def wash(name, loc, size, power=70, color=(1.0, .72, .45), aim=(0, 0, -1)):
    """A rectangular warm light that grazes down a slat panel, the LED
    backlight in the references. Baked, so it costs nothing at runtime."""
    d = bpy.data.lights.new(name, 'AREA')
    d.shape = 'RECTANGLE'
    d.size, d.size_y = size
    d.energy = power
    d.color = color
    o = bpy.data.objects.new(name, d)
    scene.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = Vector(aim).to_track_quat('-Z', 'Y').to_euler()
    o.visible_camera = False
    d.spread = math.radians(70)
    return o


HOUSE = (0, 0, 20, 14)
LIVING, DINING, KITCHEN, BEDROOM, TERRACE = (0, 0, 7, 6), (7, 0, 12, 6), (12, 0, 17, 6), (12, 8, 17, 14), (-1, -5, 21, 0)
PUBLIC = (0, 0, 17, 6)

# ------------------------------------------------ shared: finishes
restyle(('Fluted oak panelling', 'Oak wainscot'), 'Walnut slat')
restyle(('Living wool rug', 'Dining rug', 'Primary rug'), 'Jute')
restyle(('Sofa soft base', 'Sofa back', 'Sofa cushion', 'Sofa arm', 'Tailored chair seat', 'Tailored chair back',
         'Stool seat', 'Upholstered bench', 'Upholstered bed base'), 'Boucle')
restyle(('Sofa oak plinth', 'Chair oak arm', 'Chair turned oak leg', 'Media joinery', 'Bedside drawer',
         'Oak dado rail', 'Floating oak shelf', 'Stool base'), 'Walnut')
# Scatter cushions and throws in caramel, as in every reference
p = principled(M['Oat velvet'])
p.inputs['Base Color'].default_value = (.46, .27, .14, 1)
M['Oat velvet'].diffuse_color = (.46, .27, .14, 1)

# Linear slot lights in the ceiling near the glass
for x0, x1 in ((0.4, 6.6), (7.4, 11.6), (12.4, 16.6)):
    box('Ceiling slot light', ((x0 + x1) / 2, 0.75, 3.085), (x1 - x0, .035, .012), 'LED warm')

# ------------------------------------------------------ living
# Marble centre, walnut slats either side, each slat panel washed from above
drop(('Stone planter', 'Plant stem', 'Botanical leaf', 'Foliage'), LIVING)
for a0, a1 in ((.2, 1.95), (4.05, 5.8)):
    wash('Slat wash living', (0.24, (a0 + a1) / 2, 2.88), (0.08, a1 - a0), 160, aim=(0.12, 0, -1))
    box('Slat cove LED', (0.2, (a0 + a1) / 2, 2.925), (.03, a1 - a0, .012), 'LED warm')
wash('Marble wash', (0.26, 3.0, 2.88), (0.08, 2.1), 110, aim=(0.1, 0, -1))
olive_tree(0.8, 0.85, 1.9, .3, 'Stone')
# console styling: a vase and a bowl on the walnut unit
cyl('Stoneware vase', (0.36, 1.75, .71 + .16), .09, .32, 'Dark ceramic', 40, .06)
cyl('Stoneware bowl', (0.36, 4.2, .71 + .04), .15, .08, 'Stone', 40, .1)
books(0.25, 3.9, .71, 3, along='y')

# ------------------------------------------------------ dining
# Travertine slab on a single plinth, dome pendants in stone
drop(('Oval dining top', 'Dining pedestal'), DINING)
box('Travertine dining slab', (9.4, 2.8, .745), (1.12, 2.6, .07), 'Travertine', .012)
box('Travertine dining plinth', (9.4, 2.8, .355), (.46, 1.5, .71), 'Travertine', .01)
drop('Pendant shade', DINING)
for y in (2.0, 3.6):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=.42, location=(9.4, y, 2.22))
    dome = bpy.context.object
    dome.name = 'Stone dome pendant'
    bm = bmesh.new()
    bm.from_mesh(dome.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -1e-4], context='VERTS')
    bm.to_mesh(dome.data)
    bm.free()
    dome.data.materials.append(M['Stone'])
    sol = dome.modifiers.new('Shell', 'SOLIDIFY')
    sol.thickness = .02
    for f in dome.data.polygons:
        f.use_smooth = True
    added.append(dome)
olive_tree(8.05, .62, 1.7, .28, 'Stone')
# a picture light over the sideboard artwork
box('Picture light', (S_FACE - .08, 1.64, 2.5), (.05, .5, .035), 'Bronze', .008)
wash('Picture light glow', (S_FACE - .14, 1.64, 2.44), (.08, .5), 18, aim=(0.35, 0, -1))

# ------------------------------------------------------ kitchen
restyle(('Tall kitchen unit', 'Tall cabinet door', 'Kitchen drawer carcass', 'Kitchen drawer front', 'Kitchen island'),
        'Walnut', KITCHEN)
restyle('Pendant shade', 'Stone', KITCHEN)
restyle(('Waterfall stone island', 'Island stone end'), 'Marble', KITCHEN)
box('Shelf LED', (E_FACE - .16, 4.99, 1.692), (.02, 1.5, .01), 'LED warm')
wash('Shelf wash', (E_FACE - .12, 4.99, 1.68), (.06, 1.5), 22, aim=(0.3, 0, -1))
cyl('Stoneware vase', (14.6, 2.1, .98 + .15), .09, .3, 'Stone', 40, .06)

# ------------------------------------------------------ bedroom
# The wall behind the bed becomes a textured stone-plaster panel between two
# walnut slat piers, with an upholstered headboard and art above it
drop(('Oak headboard', 'Headboard wall backing', 'Full-height linen curtain', 'Curtain track'), (12, 13.3, 17, 14.2))
drop(('Lamp shade',), BEDROOM)
box('Limewash feature panel', (14.5, 13.56, 1.55), (3.82, .06, 3.1), 'Stone', .004)
restyle('Headboard side pier', 'Walnut slat', BEDROOM)
for x in (12.37, 16.63):
    wash('Slat wash bedroom', (x, 13.5, 2.95), (0.4, 0.08), 120, aim=(0, 0.15, -1))
# Channel-tufted headboard in sand linen
for i in range(8):
    box('Headboard channel', (14.5 - 1.25 + (i + .5) * 2.5 / 8, 13.46, .74), (2.5 / 8 - .012, .14, 1.12), 'Headboard sand', .05)
for x in (13.95, 15.05):
    box('Euro pillow', (x, 13.18, .9), (.95, .16, .56), 'Paper', .12).rotation_euler = (-.28, 0, 0)
framed_art('-y', 13.53, 14.5, 2.08, 1.25, .88, 'blocks', .07)
for x in (13.07, 15.93):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=.17, location=(x, 13.0, .9))
    shade = bpy.context.object
    shade.name = 'Mushroom lamp shade'
    shade.scale = (1, 1, .62)
    shade.data.materials.append(M['Stone'])
    for f in shade.data.polygons:
        f.use_smooth = True
    added.append(shade)
    cyl('Mushroom lamp stem', (x, 13.0, .74), .014, .14, 'Bronze', 16)
restyle('Bedside lamp base', 'Stone', BEDROOM)
# caramel throw across the foot of the bed, cushions against the headboard
# A caramel throw draped across the foot of the bed
verts, faces = [], []
nx, ny = 60, 12
for j in range(ny + 1):
    yy = 11.45 + .55 * j / ny
    for i in range(nx + 1):
        u = -1.3 + 2.6 * i / nx
        over = max(0.0, abs(u) - 1.06)
        z = .76 - (over / .24) ** 1.6 * .4 if over > 0 else .76 + .006 * math.sin(u * 9 + j)
        xx = 14.5 + (min(abs(u), 1.06) + over * .18) * (1 if u >= 0 else -1)
        verts.append((xx, yy + .02 * math.sin(i * .5), max(z, .32)))
for j in range(ny):
    for i in range(nx):
        a = j * (nx + 1) + i
        faces.append((a, a + 1, a + nx + 2, a + nx + 1))
me = bpy.data.meshes.new('Throw')
me.from_pydata(verts, [], faces)
me.materials.append(M['Oat velvet'])
for f in me.polygons:
    f.use_smooth = True
th = bpy.data.objects.new('Caramel throw', me)
scene.collection.objects.link(th)
th.modifiers.new('Weight', 'SOLIDIFY').thickness = .018
added.append(th)
for x in (14.1, 14.9):
    o = box('Bed cushion', (x, 12.95, .86), (.5, .16, .4), 'Oat velvet', .07)
    o.rotation_euler = (.2, 0, 0)
olive_tree(12.5, 12.0, 1.6, .24, 'Stone')

# ------------------------------------------------------ terrace
restyle(('Terrace table', 'Terrace table pedestal'), 'Travertine', TERRACE)
restyle(('Chair oak arm', 'Chair turned oak leg'), 'Walnut', TERRACE)
# walnut slats on the facade piers between the glazing
for a0, a1 in ((5.42, 7.58), (11.42, 12.55)):
    panel('Facade walnut slats', '-y', -0.1, a0, a1, 0.06, 2.9, 'Walnut slat', .03)
# planter uplights along the terrace edge
for x in (9.8, 14.6):
    wash('Planter uplight', (x, -3.2, .15), (.3, .3), 25, aim=(0, 0, 1))

# Glass must not block the sun: Cycles casts no light through refraction,
# so the glazing is made shadow-free for the bake
for o in scene.objects:
    if o.type == 'MESH' and any(m and m.name == 'Glass' for m in o.data.materials):
        o.visible_shadow = False

# ------------------------------------------------------ light
# Golden hour: a low warm sun from the south-west rakes through the glazing
# and across the floors; the window fills and the world turn warm and soft.
for o in scene.objects:
    if o.type == 'LIGHT' and o.data.type == 'SUN':
        o.hide_render = True
    if o.type == 'LIGHT' and 'sky fill' in o.name:
        o.data.color = (1.0, .84, .66)
        o.data.energy *= .4
sun = bpy.data.lights.new('Golden sun', 'SUN')
sun.energy = 6.5
sun.color = (1.0, .72, .47)
sun.angle = math.radians(1.5)
so = bpy.data.objects.new('Golden sun', sun)
scene.collection.objects.link(so)
EL, AZ = math.radians(17), math.radians(-38)
so.rotation_euler = (math.pi / 2 - EL, 0, AZ)
world = scene.world
if world and world.use_nodes:
    bg = next((n for n in world.node_tree.nodes if n.type == 'BACKGROUND'), None)
    if bg:
        bg.inputs[0].default_value = (.95, .8, .64, 1)
        bg.inputs[1].default_value = .26

# --------------------------------------------------------------- UVs
# Same rule as build_interior.py: box-projected at the material's metre scale.
# Artwork canvases instead take the whole image once across their front face.
bpy.context.view_layer.update()
for o in added:
    if o.type != 'MESH' or not o.data.materials:
        continue
    m = o.data.materials[0]
    me = o.data
    uv = me.uv_layers.get('UVMap') or me.uv_layers.new(name='UVMap')
    if m.get('fit_uv'):
        co = [o.matrix_world @ v.co for v in me.vertices]
        span = [max(c[k] for c in co) - min(c[k] for c in co) for k in range(3)]
        lo = [min(c[k] for c in co) for k in range(3)]
        thin = min(range(3), key=lambda k: span[k])
        a, b = [k for k in range(3) if k != thin]
        a, b = (a, b) if a != 2 else (b, a)
        for p in me.polygons:
            for li in p.loop_indices:
                c = o.matrix_world @ me.vertices[me.loops[li].vertex_index].co
                u = (c[a] - lo[a]) / max(span[a], 1e-6)
                v = (c[2] - lo[2]) / max(span[2], 1e-6)
                # canvases on +x / -y faces read mirrored without this flip
                if (thin == 0 and p.normal.x > 0) or (thin == 1 and p.normal.y < 0):
                    u = 1 - u
                uv.data[li].uv = (u, v)
        continue
    scale = m.get('uv_meters', 1)
    for p in me.polygons:
        axis = max(range(3), key=lambda k: abs(p.normal[k]))
        axes = [k for k in range(3) if k != axis]
        # fluted panels need the flutes to run vertically: u along the wall
        if m.name in ('Fluted oak', 'Walnut slat') and axis in (0, 1):
            axes = [1 - axis, 2]
        for li in p.loop_indices:
            c = o.matrix_world @ me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv = (c[axes[0]] / scale, c[axes[1]] / scale)

for img in bpy.data.images:
    if img.source == 'FILE' and not img.packed_file:
        img.pack()
scene['stage'] = 'Wall dressing pass (add_decor.py) applied'
bpy.ops.wm.save_as_mainfile(filepath=str(SRC))
print('DECOR_ADDED', len(added), 'objects', flush=True)

# ------------------------------------------------------- draft previews
if '--preview' in sys.argv:
    import json
    only = sys.argv[sys.argv.index('--preview') + 1].split(',')
    views = json.loads((ROOT / 'interior-cameras.json').read_text())
    extra = {}
    if '--views' in sys.argv:
        extra = json.loads(Path(sys.argv[sys.argv.index('--views') + 1]).read_text())
    cam = scene.camera or next(o for o in scene.objects if o.type == 'CAMERA')
    scene.camera = cam
    out = ROOT / 'renders' / 'decor'
    out.mkdir(exist_ok=True)
    scene.render.resolution_x, scene.render.resolution_y = 1400, 900
    scene.render.resolution_percentage = 60
    scene.cycles.samples = 40
    for key in only:
        v = extra.get(key) or views[key]
        cam.location = v['position']
        cam.rotation_euler = (Vector(v['target']) - Vector(v['position'])).to_track_quat('-Z', 'Y').to_euler()
        cam.data.lens = v.get('lens', 23)
        scene.render.filepath = str(out / f'{key}.png')
        bpy.ops.render.render(write_still=True)
        print('PREVIEW', key, flush=True)
