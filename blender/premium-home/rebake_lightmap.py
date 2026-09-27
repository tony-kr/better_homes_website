"""Re-bake the runtime lightmap and write the web copies.

The first shipped atlas was baked at 24-48 samples and encoded lossy, so every
wall carried path-tracer speckle that the codec then smeared into blotches.
Baking clean and denoised means the encoder has almost nothing to chew on: the
q90 result is both sharper and smaller than the old q100 one.

    blender -b -P rebake_lightmap.py
"""
import bpy, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PUB = ROOT / 'public/models'

bpy.ops.wm.open_mainfile(filepath=str(HERE / 'runtime/web-bake.blend'))
sc = bpy.context.scene

prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.get_devices()
gpus = [d for d in prefs.devices if d.type != 'CPU']
if gpus:
    prefs.compute_device_type = gpus[0].type
    for d in prefs.devices:
        d.use = d.type != 'CPU'
    sc.cycles.device = 'GPU'

sc.cycles.samples = int(os.environ.get('BAKE_SAMPLES', 512))
sc.cycles.use_denoising = True
for attr, val in (('denoiser', 'OPENIMAGEDENOISE'),
                  ('denoising_input_passes', 'RGB_ALBEDO_NORMAL'),
                  ('denoising_prefilter', 'ACCURATE')):
    try:
        setattr(sc.cycles, attr, val)
    except Exception as exc:
        print('denoise attr skipped:', attr, exc)

sc.render.bake.use_pass_direct = True
sc.render.bake.use_pass_indirect = True
sc.render.bake.use_pass_color = False
sc.render.bake.margin = 20

bpy.ops.object.select_all(action='DESELECT')
house = bpy.data.objects['PremiumHome_Opaque']
house.select_set(True)
bpy.context.view_layer.objects.active = house
house.data.uv_layers.active = house.data.uv_layers['LightmapUV']

result = bpy.ops.object.bake(type='DIFFUSE', uv_layer='LightmapUV')
assert 'FINISHED' in result, result

image = bpy.data.images['Home irradiance']
image.filepath_raw = str(HERE / 'runtime/home-lightmap.png')
image.file_format = 'PNG'
image.save()


def web_copy(path, size, quality):
    copy = image.copy()
    if size:
        copy.scale(size, size)
    copy.filepath_raw = str(path)
    copy.file_format = 'WEBP'
    sc.render.image_settings.quality = quality
    copy.save(quality=quality)
    bpy.data.images.remove(copy)
    print('WROTE', path.name, os.path.getsize(path))


web_copy(PUB / 'home-lightmap.webp', None, 90)
web_copy(PUB / 'home-lightmap-mobile.webp', 2048, 88)
print('REBAKE_COMPLETE')
