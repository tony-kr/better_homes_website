# -*- coding: utf-8 -*-
"""Draw-call optimisation + preview rendering. Exec'd inside build_house.py."""
import bpy, math, os
from mathutils import Vector

def merge_by_material():
    """Join meshes per (collection, material). 739 objects -> ~130 draw calls."""
    before = len([o for o in bpy.context.scene.objects if o.type == 'MESH'])
    for coll in list(bpy.data.collections):
        groups = {}
        for o in list(coll.objects):
            if o.type != 'MESH' or not o.data.materials:
                continue
            groups.setdefault(o.data.materials[0].name, []).append(o)
        for mname, objs in groups.items():
            if len(objs) < 2:
                continue
            bpy.ops.object.select_all(action='DESELECT')
            for o in objs:
                o.select_set(True)
            bpy.context.view_layer.objects.active = objs[0]
            bpy.ops.object.join()
            bpy.context.view_layer.objects.active.name = '%s__%s' % (coll.name, mname.replace(' ', '_'))
    bpy.ops.object.select_all(action='DESELECT')
    after = len([o for o in bpy.context.scene.objects if o.type == 'MESH'])
    print('MERGE %d -> %d meshes' % (before, after))


def setup_preview_world():
    """Blue-hour sky + practical lights. Preview only — never exported."""
    w = bpy.data.worlds.new('Dusk')
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes['Background']
    try:
        sky = nt.nodes.new('ShaderNodeTexSky')
        sky.sky_type = 'NISHITA'
        sky.sun_elevation = math.radians(-2.2)
        sky.sun_rotation = math.radians(212)
        sky.sun_intensity = 0.5
        sky.altitude = 120
        sky.air_density = 1.9
        sky.dust_density = 3.2
        nt.links.new(sky.outputs[0], bg.inputs[0])
        bg.inputs[1].default_value = 0.55
    except Exception:
        bg.inputs[0].default_value = (0.035, 0.062, 0.115, 1.0)
        bg.inputs[1].default_value = 1.0

    prev = bpy.data.collections.new('PREVIEW_LIGHTS')
    bpy.context.scene.collection.children.link(prev)

    def area(name, loc, size, energy, color, rot=(0, 0, 0), sy=None):
        d = bpy.data.lights.new(name, 'AREA')
        d.shape = 'RECTANGLE' if sy else 'SQUARE'
        d.size = size
        if sy:
            d.size_y = sy
        d.energy = energy
        d.color = color
        o = bpy.data.objects.new(name, d)
        o.location = loc
        o.rotation_euler = rot
        prev.objects.link(o)

    def sun(name, energy, color, rot):
        d = bpy.data.lights.new(name, 'SUN')
        d.energy = energy
        d.color = color
        d.angle = math.radians(8)
        o = bpy.data.objects.new(name, d)
        o.rotation_euler = rot
        prev.objects.link(o)

    warm = (1.0, 0.76, 0.50)
    amber = (1.0, 0.62, 0.34)
    cool = (0.48, 0.63, 0.95)

    # last cold light in the sky, raking the glazed elevation
    sun('dusk_key', 0.55, cool, (math.radians(76), 0, math.radians(-38)))
    # ceiling wash per room, dialled well back so lamps do the work
    for x in (-12.0, -5.0, 1.0, 6.4):
        area('wash_%d' % int(x), (x, 1.6, 3.02), 4.4, 52, warm, sy=4.4)
    # wall-washing so the blank plaster planes get some grade
    area('wash_west', (-15.4, 1.5, 2.1), 0.6, 26, amber, rot=(0, math.radians(-78), 0), sy=5.0)
    area('wash_bed_w', (4.5, 2.0, 2.0), 0.6, 20, amber, rot=(0, math.radians(78), 0), sy=4.0)
    area('wash_gal', (-2.0, -3.5, 3.28), 2.6, 60, warm, sy=26.0)
    # warm pools under the fittings
    area('pool_living', (-12.0, 1.1, 1.95), 2.2, 42, warm, sy=2.2)
    area('pool_living_b', (-14.6, 0.0, 1.5), 1.2, 22, amber, sy=1.2)
    area('pool_dining', (-5.0, 1.5, 1.95), 1.7, 40, warm, sy=1.7)
    area('pool_kitchen', (1.0, 1.55, 1.85), 1.9, 44, warm, sy=1.4)
    area('pool_kitchen_b', (-1.1, 4.4, 1.4), 3.0, 16, warm, sy=0.5)
    area('pool_bed', (6.2, 3.6, 1.85), 2.2, 34, warm, sy=2.0)
    area('pool_bed_lamp', (6.2, 4.4, 0.75), 2.6, 14, amber, sy=0.6)
    area('pool_patio', (16.4, 0.9, 2.6), 3.2, 44, warm, sy=3.2)
    area('fire_pool', (16.4, 0.55, 0.75), 0.9, 30, (1.0, 0.45, 0.16))
    # a low cool fill from the garden so exteriors and glass read
    area('fill_south', (-2.0, -22.0, 7.0), 30.0, 26, cool,
         rot=(math.radians(66), 0, 0), sy=30.0)
    area('fill_north', (-2.0, 14.0, 7.0), 30.0, 12, cool,
         rot=(math.radians(-66), 0, 0), sy=30.0)


def render_previews(journey, outdir, res=(960, 540), samples=48, only=None, web=False):
    os.makedirs(outdir, exist_ok=True)
    sc = bpy.context.scene
    try:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    except Exception:
        sc.render.engine = 'BLENDER_EEVEE'
    ee = getattr(sc, 'eevee', None)
    if ee:
        for attr, val in (('taa_render_samples', samples), ('use_gtao', True),
                          ('use_bloom', True), ('use_raytracing', True),
                          ('use_shadows', True), ('use_volumetric_lights', False)):
            if hasattr(ee, attr):
                try:
                    setattr(ee, attr, val)
                except Exception:
                    pass
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = 'JPEG'
    sc.render.image_settings.quality = 88
    sc.view_settings.view_transform = 'AgX' if 'AgX' in \
        [v.name for v in bpy.types.ColorManagedViewSettings.bl_rna.properties['view_transform'].enum_items] else 'Filmic'
    sc.view_settings.look = 'AgX - Medium High Contrast' if sc.view_settings.view_transform == 'AgX' else 'None'
    sc.view_settings.exposure = 0.72

    cam_data = bpy.data.cameras.new('PreviewCam')
    cam = bpy.data.objects.new('PreviewCam', cam_data)
    bpy.context.scene.collection.objects.link(cam)
    sc.camera = cam

    REF = 16.0 / 9.0
    for (cid, pos, tgt, fov) in journey:
        if only and cid not in only:
            continue
        cam_data.lens_unit = 'FOV'
        if web:
            # Reproduce the browser exactly: three.js fov is VERTICAL, and the
            # value it gets is the Blender angle converted against 16:9.
            fov_y = 2.0 * math.atan(math.tan(math.radians(fov) / 2.0) / REF)
            aspect = res[0] / float(res[1])
            widen = 15 if aspect < 0.72 else 10 if aspect < 1.0 else 4 if aspect < 1.4 else 0
            cam_data.sensor_fit = 'VERTICAL'
            cam_data.angle_y = fov_y + math.radians(widen)
        else:
            cam_data.sensor_fit = 'AUTO'
            cam_data.angle = math.radians(fov)
        cam.location = Vector(pos)
        d = Vector(tgt) - Vector(pos)
        cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
        sc.render.filepath = os.path.join(outdir, '%s.jpg' % cid)
        bpy.ops.render.render(write_still=True)
        print('PREVIEW %s' % sc.render.filepath)
