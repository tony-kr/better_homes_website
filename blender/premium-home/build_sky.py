"""Golden-hour equirectangular sky for the Better Homes landing view.

    blender -b --factory-startup -P build_sky.py
    SKY_QUICK=1 ...   # 1024x512 iteration render

The cloud field is a shader, not a volume, so it renders in seconds. Depth
comes from sampling the same noise twice, once offset toward the sun, and
using the difference as a lighting term. That gives lit tops and shadowed
undersides without paying for volumetrics.
"""
import bpy, math, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sky')
os.makedirs(OUT, exist_ok=True)

SUN_ROT = math.radians(252)
SUN_ELEV = math.radians(5.0)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 32
sc.cycles.use_denoising = False

w = bpy.data.worlds.new('GoldenHour')
sc.world = w
w.use_nodes = True
nt = w.node_tree
nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputWorld')
bg = nt.nodes.new('ShaderNodeBackground')
nt.links.new(bg.outputs[0], out.inputs[0])

# ------------------------------------------------------------------- sky
# Painted rather than simulated: the reference is a warm, saturated sunset and
# the atmosphere model keeps landing on pale blue. SUN_DIR drives both the
# horizon warmth and the glow.
SUN_DIR = (math.cos(SUN_ELEV) * math.cos(SUN_ROT),
           math.cos(SUN_ELEV) * math.sin(SUN_ROT),
           math.sin(SUN_ELEV))

geo = nt.nodes.new('ShaderNodeNewGeometry')
# Incoming points back toward the camera, so flip it to get the view direction
flip = nt.nodes.new('ShaderNodeVectorMath')
flip.operation = 'SCALE'
flip.inputs['Scale'].default_value = -1.0
nt.links.new(geo.outputs['Incoming'], flip.inputs[0])
DIRECTION = flip.outputs['Vector']

sep = nt.nodes.new('ShaderNodeSeparateXYZ')
nt.links.new(DIRECTION, sep.inputs[0])

# 0 at the horizon, 1 at the zenith
height = nt.nodes.new('ShaderNodeMath')
height.operation = 'MULTIPLY_ADD'
height.inputs[1].default_value = 0.5
height.inputs[2].default_value = 0.5
nt.links.new(sep.outputs['Z'], height.inputs[0])

# How closely we are looking into the sun
sundot = nt.nodes.new('ShaderNodeVectorMath')
sundot.operation = 'DOT_PRODUCT'
sundot.inputs[1].default_value = SUN_DIR
nt.links.new(DIRECTION, sundot.inputs[0])

warmth = nt.nodes.new('ShaderNodeMath')
warmth.operation = 'MULTIPLY_ADD'
warmth.inputs[1].default_value = 0.5
warmth.inputs[2].default_value = 0.5
nt.links.new(sundot.outputs['Value'], warmth.inputs[0])

# Horizon colour swings from cool mauve opposite the sun to gold at it
horizon = nt.nodes.new('ShaderNodeValToRGB')
horizon.color_ramp.interpolation = 'B_SPLINE'
he = horizon.color_ramp.elements
he[0].position = 0.10; he[0].color = (0.21, 0.20, 0.33, 1)
he[1].position = 1.00; he[1].color = (2.60, 1.35, 0.52, 1)
horizon.color_ramp.elements.new(0.46).color = (0.72, 0.36, 0.34, 1)
horizon.color_ramp.elements.new(0.70).color = (1.35, 0.62, 0.32, 1)
horizon.color_ramp.elements.new(0.88).color = (2.00, 1.00, 0.44, 1)
nt.links.new(warmth.outputs[0], horizon.inputs[0])

# Vertical falloff from that horizon into deep blue overhead
lift = nt.nodes.new('ShaderNodeValToRGB')
lift.color_ramp.interpolation = 'EASE'
le = lift.color_ramp.elements
le[0].position = 0.50; le[0].color = (0, 0, 0, 1)
le[1].position = 0.78; le[1].color = (1, 1, 1, 1)
nt.links.new(height.outputs[0], lift.inputs[0])

zenith = nt.nodes.new('ShaderNodeRGB')
zenith.outputs[0].default_value = (0.075, 0.115, 0.26, 1)

sky = nt.nodes.new('ShaderNodeMix')
sky.data_type = 'RGBA'
sky.blend_type = 'MIX'
nt.links.new(lift.outputs[0], sky.inputs['Factor'])
nt.links.new(horizon.outputs[0], sky.inputs[6])
nt.links.new(zenith.outputs[0], sky.inputs[7])

# Sun glow: a tight power of the dot product, added over the gradient
glow_pow = nt.nodes.new('ShaderNodeMath')
glow_pow.operation = 'POWER'
glow_pow.inputs[1].default_value = 90.0
nt.links.new(warmth.outputs[0], glow_pow.inputs[0])

glow_amt = nt.nodes.new('ShaderNodeMath')
glow_amt.operation = 'MULTIPLY'
glow_amt.inputs[1].default_value = 12.0
nt.links.new(glow_pow.outputs[0], glow_amt.inputs[0])

glow_col = nt.nodes.new('ShaderNodeMix')
glow_col.data_type = 'RGBA'
glow_col.blend_type = 'ADD'
glow_col.inputs['Factor'].default_value = 1.0
nt.links.new(sky.outputs[2], glow_col.inputs[6])
sun_tint = nt.nodes.new('ShaderNodeCombineColor')
sun_tint.inputs[0].default_value = 1.0
sun_tint.inputs[1].default_value = 0.72
sun_tint.inputs[2].default_value = 0.42
glow_scaled = nt.nodes.new('ShaderNodeVectorMath')
glow_scaled.operation = 'SCALE'
nt.links.new(sun_tint.outputs[0], glow_scaled.inputs[0])
nt.links.new(glow_amt.outputs[0], glow_scaled.inputs['Scale'])
nt.links.new(glow_scaled.outputs['Vector'], glow_col.inputs[7])
SKY_COLOR = glow_col.outputs[2]


def noise(scale, detail, rough, distortion=0.0):
    n = nt.nodes.new('ShaderNodeTexNoise')
    n.noise_dimensions = '3D'
    n.inputs['Scale'].default_value = scale
    n.inputs['Detail'].default_value = detail
    n.inputs['Roughness'].default_value = rough
    if 'Distortion' in n.inputs:
        n.inputs['Distortion'].default_value = distortion
    return n


def cloud_field(offset):
    """Noise stack sampled along the view direction, optionally nudged
    toward the sun so the second copy can act as a shadow probe."""
    m = nt.nodes.new('ShaderNodeMapping')
    # Squash Z so the layer reads as a sheet overhead rather than a sphere
    m.inputs['Scale'].default_value = (1.0, 1.0, 2.8)
    m.inputs['Location'].default_value = offset
    nt.links.new(DIRECTION, m.inputs['Vector'])

    banks = noise(1.5, 10.0, 0.58, 0.9)
    nt.links.new(m.outputs['Vector'], banks.inputs['Vector'])
    wisps = noise(4.4, 14.0, 0.70, 1.8)
    nt.links.new(m.outputs['Vector'], wisps.inputs['Vector'])

    mix = nt.nodes.new('ShaderNodeMix')
    mix.data_type = 'FLOAT'
    mix.inputs['Factor'].default_value = 0.38
    nt.links.new(banks.outputs['Fac'], mix.inputs[2])
    nt.links.new(wisps.outputs['Fac'], mix.inputs[3])
    return mix


density = cloud_field((0.0, 0.0, 0.0))
# Shadow probe, displaced toward the sun in the horizontal plane
probe = cloud_field((-math.cos(SUN_ROT) * 0.13, -math.sin(SUN_ROT) * 0.13, -0.05))

# Coverage: generous, with soft torn edges
shape = nt.nodes.new('ShaderNodeValToRGB')
shape.color_ramp.interpolation = 'EASE'
shape.color_ramp.elements[0].position = 0.455
shape.color_ramp.elements[1].position = 0.655
nt.links.new(density.outputs[0], shape.inputs[0])

# Clouds live from just above the horizon to near the zenith
band = nt.nodes.new('ShaderNodeValToRGB')
band.color_ramp.interpolation = 'B_SPLINE'
be = band.color_ramp.elements
be[0].position = 0.495
be[0].color = (0, 0, 0, 1)
be[1].position = 0.545
be[1].color = (1, 1, 1, 1)
band.color_ramp.elements.new(0.72).color = (1, 1, 1, 1)
band.color_ramp.elements.new(0.97).color = (0.12, 0.12, 0.12, 1)
nt.links.new(height.outputs[0], band.inputs[0])

mask = nt.nodes.new('ShaderNodeMath')
mask.operation = 'MULTIPLY'
nt.links.new(shape.outputs[0], mask.inputs[0])
nt.links.new(band.outputs[0], mask.inputs[1])

# Lighting term: the sun-side probe minus local density. Positive where the
# cloud faces the sun, negative in its own shadow.
diff = nt.nodes.new('ShaderNodeMath')
diff.operation = 'SUBTRACT'
nt.links.new(probe.outputs[0], diff.inputs[0])
nt.links.new(density.outputs[0], diff.inputs[1])

lit = nt.nodes.new('ShaderNodeMath')
lit.operation = 'MULTIPLY_ADD'
lit.inputs[1].default_value = 3.4
lit.inputs[2].default_value = 0.5
nt.links.new(diff.outputs[0], lit.inputs[0])

shade = nt.nodes.new('ShaderNodeValToRGB')
shade.color_ramp.interpolation = 'EASE'
se = shade.color_ramp.elements
se[0].position = 0.04
se[0].color = (0.26, 0.19, 0.24, 1)      # shadow, soft grey plum
se[1].position = 0.96
se[1].color = (1.75, 1.45, 1.12, 1)      # sunlit rim, above white
shade.color_ramp.elements.new(0.30).color = (0.52, 0.31, 0.30, 1)   # dusty rose
shade.color_ramp.elements.new(0.52).color = (0.96, 0.52, 0.33, 1)   # coral
shade.color_ramp.elements.new(0.74).color = (1.30, 0.88, 0.58, 1)   # amber
nt.links.new(lit.outputs[0], shade.inputs[0])

blend = nt.nodes.new('ShaderNodeMix')
blend.data_type = 'RGBA'
blend.blend_type = 'MIX'
nt.links.new(mask.outputs[0], blend.inputs['Factor'])
nt.links.new(SKY_COLOR, blend.inputs[6])
nt.links.new(shade.outputs[0], blend.inputs[7])
nt.links.new(blend.outputs[2], bg.inputs['Color'])
bg.inputs['Strength'].default_value = 1.0

# ---------------------------------------------- equirectangular capture
cam_data = bpy.data.cameras.new('SkyCam')
cam_data.type = 'PANO'
for holder, attr in ((cam_data, 'panorama_type'), (getattr(cam_data, 'cycles', None), 'panorama_type')):
    if holder is None:
        continue
    try:
        setattr(holder, attr, 'EQUIRECTANGULAR')
    except Exception:
        pass
cam = bpy.data.objects.new('SkyCam', cam_data)
sc.collection.objects.link(cam)
cam.rotation_euler = (math.radians(90), 0, 0)
sc.camera = cam

QUICK = os.environ.get('SKY_QUICK') == '1'
sc.render.resolution_x = 1024 if QUICK else 4096
sc.render.resolution_y = 512 if QUICK else 2048

if not QUICK:
    sc.render.image_settings.file_format = 'OPEN_EXR'
    sc.render.image_settings.color_depth = '16'
    sc.render.image_settings.exr_codec = 'DWAA'
    sc.view_settings.view_transform = 'Standard'
    sc.render.filepath = OUT + '/golden-sky.exr'
    bpy.ops.render.render(write_still=True)

sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_depth = '8'
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Punchy'
sc.view_settings.exposure = 0.0
sc.render.filepath = OUT + ('/quick-sky.png' if QUICK else '/golden-sky.png')
bpy.ops.render.render(write_still=True)

print('SKY_DONE', OUT)
