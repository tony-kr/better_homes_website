"""Poster stills for the five walk rooms, from the website's own camera views.

The site shows /models/<room>-preview.webp while the 3D house loads, and in
place of it if WebGL fails, so each poster has to match the live framing.
The views below are WALK_VIEWS in src/data/journey.js, in three.js space;
keep the two in step.

    blender -b -P render_walk_previews.py
    python3 package_web.py        # encodes renders/interiors/*.png to webp
"""
import bpy, math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'premium-interior.blend'))
scene = bpy.context.scene

# three.js (x, y, z) is Blender (x, -z, y)
WALK_VIEWS = {
    'living': ([7.2, 1.6, -0.9], [0.4, 1.3, -3.2], 48),
    'dining': ([7.6, 1.6, -4.8], [11.9, 1.25, -1.7], 50),
    'kitchen': ([12.6, 1.6, -5.4], [16.0, 1.2, -1.8], 52),
    'bedroom': ([12.6, 1.6, -9.0], [15.2, 1.0, -12.8], 52),
    'patio': ([1.95, 1.6, 3.45], [9.0, 1.1, 1.2], 48),
}


def to_blender(v):
    return Vector((v[0], -v[2], v[1]))


prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.get_devices()
gpus = [d for d in prefs.devices if d.type != 'CPU']
if gpus:
    prefs.compute_device_type = gpus[0].type
    for d in prefs.devices:
        d.use = d.type != 'CPU'
    scene.cycles.device = 'GPU'
scene.render.engine = 'CYCLES'
scene.cycles.samples = 160
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = 1120, 720
scene.render.resolution_percentage = 100

cam = scene.camera
cam.data.sensor_fit = 'VERTICAL'
out = ROOT / 'renders' / 'interiors'
for key, (pos, target, fov) in WALK_VIEWS.items():
    cam.location = to_blender(pos)
    cam.rotation_euler = (to_blender(target) - to_blender(pos)).to_track_quat('-Z', 'Y').to_euler()
    cam.data.angle_y = math.radians(fov)
    scene.render.filepath = str(out / f'{key}.png')
    bpy.ops.render.render(write_still=True)
    print('WALK_PREVIEW', key, flush=True)
