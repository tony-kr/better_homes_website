"""Golden-hour hero stills for the landing page.

The live three.js exterior is built for speed, and at the landing's framing it
reads as a model. The landing opens on these Cycles stills instead, and the
page crossfades into the live house as you scroll toward the door.

    blender -b -P render_hero.py                 # desktop + mobile, full quality
    blender -b -P render_hero.py -- --draft      # quarter samples, half size

Writes runtime/hero-{desktop,mobile}.png. Shots and the sun live in
hero-shots.json. The sky is painted first by paint_hero_sky.py, in each
camera's own view, and mapped onto a dome here (see sky_dome), which keeps the
cloud colour art-directable and still lets the pool reflect it.

Uses the dressed interior (premium-interior.blend, after add_decor.py) so the
furnished, lamp-lit rooms show through the glazing, plus the architectural
parts of runtime/exterior.glb: roof, fascia, soffit, mullions, plinth, deck,
lawn and reflecting pool. The low-poly trees, hedges and the south courtyard
wall are left out; olive trees from add_decor.py stand in for the trees.
"""
import bpy, json, math, random, sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
TEX = ROOT / 'textures'
OUT = ROOT / 'runtime'
draft = '--draft' in sys.argv

bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'premium-interior.blend'))
scene = bpy.context.scene
random.seed(7)

# ---------------------------------------------------------- exterior parts
before = set(scene.objects)
bpy.ops.import_scene.gltf(filepath=str(OUT / 'exterior.glb'))
for o in set(scene.objects) - before:
    names = ' '.join(m.name for m in getattr(o.data, 'materials', []) if m)
    if any(k in names for k in ('Canopy', 'Hedge', 'Bark')):
        bpy.data.objects.remove(o, do_unlink=True)
for o in scene.objects:
    if o.name.startswith(('South garden boundary', 'North garden boundary', 'Garden perimeter planter', 'Landscape')):
        o.hide_render = True
# The concept's small potted plants line the terrace like a fence; the olive
# trees from add_decor.py carry the terrace on their own.
# Their meshes are authored in world space with the origin at 0, so test the
# bounds rather than the object position.
def centre(o):
    return sum((o.matrix_world @ Vector(c) for c in o.bound_box), Vector()) / 8


for o in scene.objects:
    if o.name.startswith(('Botanical leaf', 'Plant stem', 'Stone planter', 'Foliage')) and not (0 <= centre(o).y <= 14):
        o.hide_render = True

# Plant helpers are shared with add_decor.py rather than copied.
M = {m.name: m for m in bpy.data.materials}
added = []
src = (ROOT / 'add_decor.py').read_text()
helpers = src.split('# -------------------------------------------------------------- helpers')[1].split('# ======================================================== living')[0]
exec(compile(helpers, str(ROOT / 'add_decor.py'), 'exec'))


def garden_tree(x, y, height=6.0, spread=2.6, seed=0):
    """A multi-stemmed garden tree with a broad, open crown. Built from the
    same olive leaf as the planters, scaled up, so it reads at a distance."""
    rnd = random.Random(seed)
    base = Vector((x, y, -.05))
    crowns = []
    for s in range(4):
        a = s * 1.7 + rnd.uniform(-.3, .3)
        lean = Vector((math.cos(a), math.sin(a), 0))
        mid = base + lean * spread * .18 + Vector((0, 0, height * .38))
        tip = base + lean * spread * .5 + Vector((0, 0, height * rnd.uniform(.62, .74)))
        stem([tuple(base), tuple(mid), tuple(tip)], .07 * (1 - s * .12))
        crowns.append(tip)
        for b in range(3):
            ba = a + (b - 1) * .8
            twig = tip + Vector((math.cos(ba) * spread * .35, math.sin(ba) * spread * .35, rnd.uniform(.3, .9)))
            stem([tuple(tip), tuple(twig)], .03)
            crowns.append(twig)
    for c in range(130):
        anchor = crowns[c % len(crowns)]
        cc = anchor + Vector((rnd.uniform(-1, 1) * spread * .4, rnd.uniform(-1, 1) * spread * .4, rnd.uniform(-.4, .7)))
        for k in range(40):
            at = cc + Vector((rnd.uniform(-.4, .4), rnd.uniform(-.4, .4), rnd.uniform(-.3, .3)))
            d = (at - anchor).normalized() + Vector((0, 0, .5))
            place_leaf(OLIVE, at, d, rnd.uniform(0, 3.1), rnd.uniform(2.6, 3.4))


# ------------------------------------------------------- water and lawn
water = bpy.data.materials.get('Ext Water')
if water:
    p = next(n for n in water.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value = (.006, .012, .014, 1)
    p.inputs['Roughness'].default_value = .015
    p.inputs['Metallic'].default_value = 0
    p.inputs['IOR'].default_value = 1.33
# The lawn slab's top is coplanar with the water, which hides the pool; lift
# the water a few centimetres so it reads, and take the stepping stones out
# of the foreground.
import bmesh
for o in scene.objects:
    mats = [m.name for m in getattr(o.data, 'materials', []) if m]
    if 'Ext Water' in mats:
        o.location.z += .045
    if 'Ext Coping' in mats and o.type == 'MESH':
        bm = bmesh.new()
        bm.from_mesh(o.data)
        mw = o.matrix_world
        doomed = [f for f in bm.faces if 9.5 < (mw @ f.calc_center_median()).x < 12.5 and -17 < (mw @ f.calc_center_median()).y < -10.5]
        bmesh.ops.delete(bm, geom=doomed, context='FACES')
        bm.to_mesh(o.data)
        bm.free()
lawn = bpy.data.materials.get('Ext Lawn')
if lawn:
    nodes, links = lawn.node_tree.nodes, lawn.node_tree.links
    p = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
    coord = nodes.new('ShaderNodeTexCoord')
    big = nodes.new('ShaderNodeTexNoise')
    big.inputs['Scale'].default_value = .08
    big.inputs['Detail'].default_value = 6
    fine = nodes.new('ShaderNodeTexNoise')
    fine.inputs['Scale'].default_value = 3.0
    fine.inputs['Detail'].default_value = 8
    links.new(coord.outputs['Object'], big.inputs['Vector'])
    links.new(coord.outputs['Object'], fine.inputs['Vector'])
    mix = nodes.new('ShaderNodeMix')
    mix.data_type = 'FLOAT'
    mix.inputs['Factor'].default_value = .35
    links.new(big.outputs['Fac'], mix.inputs['A'])
    links.new(fine.outputs['Fac'], mix.inputs['B'])
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = .35
    ramp.color_ramp.elements[0].color = (.07, .09, .03, 1)
    ramp.color_ramp.elements[1].position = .7
    ramp.color_ramp.elements[1].color = (.2, .2, .07, 1)
    links.new(mix.outputs['Result'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], p.inputs['Base Color'])
    p.inputs['Roughness'].default_value = .95
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = .25
    links.new(fine.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], p.inputs['Normal'])

for i, (x, y, h, sp) in enumerate(((-5.0, -2.5, 6.2, 2.8), (-7.5, 8.0, 7.0, 3.0), (25.0, -2.0, 6.4, 2.8), (27.0, 9.0, 7.2, 3.1), (4.0, 21.0, 7.5, 3.2), (16.0, 22.0, 6.8, 3.0))):
    garden_tree(x, y, h, sp, i)

# ----------------------------------------------------------------- light
world = bpy.data.worlds.new('Golden hour')
world.use_nodes = True
scene.world = world
nt = world.node_tree
sky = nt.nodes.new('ShaderNodeTexSky')
sky.sky_type = 'MULTIPLE_SCATTERING'
sky.sun_disc = False
sky.sun_elevation = math.radians(json.loads((ROOT / 'hero-shots.json').read_text())['sun']['elevationDeg'])
# Sun low behind the camera's right shoulder, raking across the glazed front
SUN_AZ = math.radians(json.loads((ROOT / 'hero-shots.json').read_text())['sun']['azimuthDeg'])
sky.sun_rotation = SUN_AZ
bg = nt.nodes['Background']
nt.links.new(sky.outputs[0], bg.inputs[0])
bg.inputs[1].default_value = .35

sun = bpy.data.lights.new('Low sun', 'SUN')
sun.energy = 5.0
sun.color = (1.0, .52, .26)
sun.angle = math.radians(1.0)
so = bpy.data.objects.new('Low sun', sun)
scene.collection.objects.link(so)
so.rotation_euler = (math.pi / 2 - sky.sun_elevation, 0, SUN_AZ)
for o in scene.objects:
    if o.type == 'LIGHT' and o.data.type == 'SUN' and o is not so:
        o.hide_render = True
    # Window sky fills were daytime stand-ins; at dusk the lamps carry the rooms
    if o.type == 'LIGHT' and 'sky fill' in o.name:
        o.hide_render = True
    if o.type == 'LIGHT' and o.data.type == 'AREA' and 'sky fill' not in o.name:
        o.data.energy *= 3.2
        o.data.color = (1.0, .78, .55)

# ------------------------------------------------------------- sky dome
# A hemisphere around the camera carrying paint_hero_sky.py's image, UV'd by
# projecting every vertex through the shot's camera. The camera sees exactly
# the painted pixels; the pool and the glazing reflect the same sky. The
# dome is invisible to diffuse and shadow rays, so the Nishita world above
# still does the lighting.
def sky_dome(key, shot):
    old = bpy.data.objects.get('Sky dome')
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    pos = Vector(shot['pos'])
    bpy.ops.mesh.primitive_uv_sphere_add(segments=256, ring_count=128, radius=900, location=pos)
    dome = bpy.context.object
    dome.name = 'Sky dome'
    me = dome.data
    f = (Vector(shot['target']) - pos).normalized()
    r = f.cross(Vector((0, 0, 1))).normalized()
    u = r.cross(f)
    W, H = shot['res']
    half = 18.0 / shot['lens']
    tx, ty = (half, half * H / W) if W >= H else (half * W / H, half)
    # the primitive ships a lat-long map; overwrite it rather than adding one
    uv = me.uv_layers[0]
    for loop in me.loops:
        v = me.vertices[loop.vertex_index].co.normalized()
        depth = max(v.dot(f), 1e-3)
        x = v.dot(r) / depth / tx
        y = v.dot(u) / depth / ty
        uv.data[loop.index].uv = (x * .5 + .5, y * .5 + .5)
    for p in me.polygons:
        p.use_smooth = True
    m = bpy.data.materials.new('Painted sky ' + key)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    tex = nt.nodes.new('ShaderNodeTexImage')
    tex.image = bpy.data.images.load(str(OUT / f'hero-sky-{key}.png'), check_existing=False)
    tex.extension = 'EXTEND'
    tex.interpolation = 'Cubic'
    em = nt.nodes.new('ShaderNodeEmission')
    # The painted values are display colours; AgX lifts and compresses them,
    # so the strength is tuned to land the sky close to its painted look.
    em.inputs['Strength'].default_value = SKY_STRENGTH
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(tex.outputs['Color'], em.inputs['Color'])
    nt.links.new(em.outputs[0], out.inputs['Surface'])
    me.materials.append(m)
    dome.visible_diffuse = False
    dome.visible_shadow = False
    dome.visible_volume_scatter = False
    return dome


SKY_STRENGTH = 1.0

# ---------------------------------------------------------------- render
scene.render.engine = 'CYCLES'
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.get_devices()
gpus = [d for d in prefs.devices if d.type != 'CPU']
if gpus:
    prefs.compute_device_type = gpus[0].type
    for d in prefs.devices:
        d.use = d.type != 'CPU'
    scene.cycles.device = 'GPU'
scene.cycles.samples = 64 if draft else 384
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 8
scene.render.film_transparent = False
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Punchy'
scene.view_settings.exposure = .15

cam = scene.camera
CFG = json.loads((ROOT / 'hero-shots.json').read_text())
SHOTS = CFG['shots']
meta = {}
only = sys.argv[sys.argv.index('--only') + 1].split(',') if '--only' in sys.argv else list(SHOTS)
for key in only:
    s = SHOTS[key]
    scene.render.resolution_x, scene.render.resolution_y = s['res']
    scene.render.resolution_percentage = 50 if draft else 100
    sky_dome(key, s)
    cam.location = s['pos']
    d = Vector(s['target']) - Vector(s['pos'])
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = s['lens']
    cam.data.sensor_fit = 'AUTO'
    cam.data.clip_end = 3000
    scene.render.filepath = str(OUT / f'hero-{key}.png')
    bpy.ops.render.render(write_still=True)
    meta[key] = dict(s, pitch=math.degrees(math.asin(d.normalized().z)))
    print('HERO_RENDERED', key, flush=True)
(OUT / 'hero-shots.json').write_text(json.dumps(meta, indent=2))
