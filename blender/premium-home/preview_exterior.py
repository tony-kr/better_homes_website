"""Render candidate landing framings straight from the shipped GLB.

Faster than guessing in the browser: same geometry, same sky, so whatever
reads well here will read well on the page.
"""
import bpy, math, os, sys, mathutils

ROOT = '/Users/tonykr/Documents/Freelance/Better_Homes_Astra'
OUT = '/tmp/frames'
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'BLENDER_EEVEE'

bpy.ops.import_scene.gltf(filepath=ROOT + '/public/models/premium-home.glb')
bpy.ops.import_scene.gltf(filepath=ROOT + '/public/models/exterior.glb')

# Report the real massing, ignoring the ground plane
xs, ys, zs = [], [], []
for o in sc.objects:
    if o.type != 'MESH':
        continue
    for corner in o.bound_box:
        p = o.matrix_world @ mathutils.Vector(corner)
        xs.append(p.x); ys.append(p.y); zs.append(p.z)
print('MODEL_BOUNDS x %.1f..%.1f  y %.1f..%.1f  z %.1f..%.1f' % (
    min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)))

# Sky as world, matching the site
w = bpy.data.worlds.new('Sky')
sc.world = w
w.use_nodes = True
nt = w.node_tree
bgnode = nt.nodes['Background']
env = nt.nodes.new('ShaderNodeTexEnvironment')
env.image = bpy.data.images.load(ROOT + '/public/sky/golden-sky.webp')
nt.links.new(env.outputs[0], bgnode.inputs[0])
bgnode.inputs[1].default_value = 1.0

sun = bpy.data.lights.new('sun', 'SUN')
sun.energy = 4.5
sun.color = (1.0, 0.82, 0.62)
sun_obj = bpy.data.objects.new('sun', sun)
sun_obj.rotation_euler = (math.radians(80), 0, math.radians(252))
sc.collection.objects.link(sun_obj)

cam_data = bpy.data.cameras.new('cam')
cam = bpy.data.objects.new('cam', cam_data)
sc.collection.objects.link(cam)
sc.camera = cam
cam_data.sensor_fit = 'VERTICAL'

sc.render.resolution_x = 1600
sc.render.resolution_y = 840
sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.quality = 88
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Punchy'
sc.view_settings.exposure = 1.2

# three.js fov is vertical degrees, so angle_y maps one to one
CANDIDATES = [
    ('exterior', (34.0, 11.0, 34.0), (10.0, 3.6, -6.0), 36),
]
def to_blender(v):
    return mathutils.Vector((v[0], -v[2], v[1]))


for name, pos, tgt, fov in CANDIDATES:
    cam.location = to_blender(pos)
    d = to_blender(tgt) - to_blender(pos)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    cam_data.angle_y = math.radians(fov)
    sc.render.filepath = os.path.join(OUT, '%s.png' % name)
    bpy.ops.render.render(write_still=True)
    print('FRAME', name, pos, fov)

print('FRAMES_DONE')
