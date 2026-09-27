"""Export the approved native home with UV1 baked diffuse lighting."""
import bpy,math,json,time,os
from pathlib import Path
R=Path(__file__).resolve().parent;OUT=R/'runtime';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'premium-interior.blend'))
s=bpy.context.scene
p=bpy.context.preferences.addons['cycles'].preferences;p.get_devices();gpus=[d for d in p.devices if d.type!='CPU']
if gpus:
 p.compute_device_type=gpus[0].type
 for d in p.devices:d.use=d.type!='CPU'
 s.cycles.device='GPU'
s.cycles.samples=int(os.environ.get('BAKE_SAMPLES',24));s.cycles.use_denoising=True
# Give every texture an explicit UV0 binding before UV1 becomes bake-active.
for m in bpy.data.materials:
 if not m.use_nodes:continue
 nodes=m.node_tree.nodes;links=m.node_tree.links;uv=nodes.new('ShaderNodeUVMap');uv.uv_map='UVMap'
 for n in list(nodes):
  if n.type=='TEX_IMAGE' and not n.inputs['Vector'].is_linked:links.new(uv.outputs[0],n.inputs['Vector'])
# Apply evaluated geometry once; retain two groups for opaque and glass.
bpy.ops.object.select_all(action='DESELECT')
for o in s.objects:
 if o.type in ('MESH','CURVE') and not o.hide_render:o.select_set(True)
bpy.context.view_layer.objects.active=next(o for o in s.objects if o.select_get())
bpy.ops.object.convert(target='MESH')
opaque=[];glass=[];foliage=[]
# Foliage is thousands of tiny leaves: in the atlas it starves the walls and
# floors of texels, so it ships as its own mesh lit by the sky at runtime.
FOLIAGE=('Olive leaf','Fig leaf','Leaves','Bark','Dried stem')
# The site plane is 64 x 55 m and hidden under the exterior lawn at runtime,
# yet in the atlas it took the lion's share of the texels; leave it out.
for o in list(s.objects):
 if o.name.startswith('Landscape'):bpy.data.objects.remove(o,do_unlink=True)
for o in list(s.objects):
 if o.type!='MESH' or o.hide_render:continue
 names=[m.name for m in o.data.materials if m]
 if any(n in ('Glass','Water') for n in names):glass.append(o)
 elif names and all(n in FOLIAGE for n in names):foliage.append(o)
 else:opaque.append(o)
def join(objects,name):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;return o
house=join(opaque,'PremiumHome_Opaque');glazing=join(glass,'PremiumHome_Glass') if glass else None;leaves=join(foliage,'PremiumHome_Foliage') if foliage else None
bpy.ops.object.select_all(action='DESELECT');house.select_set(True);bpy.context.view_layer.objects.active=house
# Pack a separate atlas for indirect and direct diffuse light; material UVs remain intact.
uv=house.data.uv_layers.new(name='LightmapUV');house.data.uv_layers.active=uv
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.002,area_weight=.2,scale_to_bounds=True)
bpy.ops.object.mode_set(mode='OBJECT');print('UV1_ATLAS_READY',len(house.data.polygons),flush=True)
image=bpy.data.images.new('Home irradiance',width=4096,height=4096,alpha=False,float_buffer=False)
image.filepath_raw=str(OUT/'home-lightmap.png');image.file_format='PNG'
for m in house.data.materials:
 if m is None:continue
 n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=image;n.label='Runtime lightmap; UV1';m.node_tree.nodes.active=n
s.render.bake.use_pass_direct=True;s.render.bake.use_pass_indirect=True;s.render.bake.use_pass_color=False;s.render.bake.margin=12
result=bpy.ops.object.bake(type='DIFFUSE',uv_layer='LightmapUV');assert 'FINISHED' in result,result
image.save();print('LIGHTMAP_BAKED',flush=True)
# Low-frequency baked light is sampled using the second UV set in Three.js.
house.data.uv_layers.active_index=0
for uv in house.data.uv_layers:uv.active_render=uv.name=='UVMap'
house['lightmap']='home-lightmap.webp';house['lightmapUV']=1;house['source']='premium-interior.blend'
# Source remains full-resolution; portable web copies use smaller roughness/normal maps.
for m in house.data.materials:
 if m is None or not m.use_nodes:continue
 for n in m.node_tree.nodes:
  if n.type!='TEX_IMAGE' or n.image is None or n.image==image:continue
  old=n.image;stem=Path(old.filepath).name
  size=512 if '-normal' in stem else 256 if '-rough' in stem else 1024
  if old.size[0]>size:old.scale(size,size)
# Export only the two optimized mesh groups. Lights are supplied by the shared manifest.
bpy.ops.object.select_all(action='DESELECT');house.select_set(True)
if glazing:glazing.select_set(True)
if leaves:leaves.select_set(True)
kwargs=dict(filepath=str(OUT/'premium-home.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_animations=False,export_texcoords=True,export_normals=True,export_extras=True,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6,export_draco_texcoord_quantization=16)
valid=bpy.ops.export_scene.gltf.get_rna_type().properties.keys();kwargs={k:v for k,v in kwargs.items() if k in valid}
bpy.ops.export_scene.gltf(**kwargs)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'web-bake.blend'))
print('WEB_EXPORT_COMPLETE',os.path.getsize(OUT/'premium-home.glb'),flush=True)
