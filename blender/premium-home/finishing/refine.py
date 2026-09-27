"""Additive finishing pass. Never modifies website files or the approved source."""
import bpy,math,random,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];F=R/'finishing'
bpy.ops.wm.open_mainfile(filepath=str(R/'premium-interior.blend'))
s=bpy.context.scene;random.seed(271)
def pbr(m):return next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
# Fine, exportable image textures. Keep existing palette and material identities.
for name,stem in [('Boucle','boucle'),('Linen','linen'),('Paper','linen'),('Jute','jute'),('Rug','jute')]:
 m=bpy.data.materials.get(name)
 if not m:continue
 for n in m.node_tree.nodes:
  if n.type!='TEX_IMAGE' or not n.image:continue
  suffix=next((k for k in ['color','rough','normal'] if k in Path(n.image.filepath).name),None)
  if suffix:
   im=bpy.data.images.load(str(F/'textures'/f'{stem}-{suffix}.png'),check_existing=True)
   if suffix!='color':im.colorspace_settings.name='Non-Color'
   n.image=im
 for n in m.node_tree.nodes:
  if n.type=='NORMAL_MAP':n.inputs['Strength'].default_value=.5
 p=pbr(m);p.inputs['Sheen Weight'].default_value=.22;p.inputs['Sheen Roughness'].default_value=.65
# Add fine weave to previously entirely smooth textiles while preserving their colors.
for name in ['Oat velvet','Headboard sand']:
 m=bpy.data.materials.get(name)
 if not m:continue
 p=pbr(m);nodes=m.node_tree.nodes;links=m.node_tree.links
 t=nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(F/'textures/linen-normal.png'),check_existing=True);t.image.colorspace_settings.name='Non-Color'
 n=nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.32;links.new(t.outputs['Color'],n.inputs['Color']);links.new(n.outputs[0],p.inputs['Normal'])
 p.inputs['Sheen Weight'].default_value=.28;p.inputs['Roughness'].default_value=.86
# Wood and stone retain their texture maps; reduce plastic-looking specular.
for name in ['Walnut','Walnut slat','Oak']:
 m=bpy.data.materials.get(name)
 if m:pbr(m).inputs['Specular IOR Level'].default_value=.28
for name in ['Marble','Travertine','Stone']:
 m=bpy.data.materials.get(name)
 if m:
  pbr(m).inputs['Specular IOR Level'].default_value=.32
  for n in m.node_tree.nodes:
   if n.type=='NORMAL_MAP':n.inputs['Strength'].default_value=.12
def uv_project(o,scale=.45):
 me=o.data;uv=me.uv_layers.get('UVMap') or me.uv_layers.new(name='UVMap')
 for p in me.polygons:
  axes=[a for a in range(3) if a!=max(range(3),key=lambda a:abs(p.normal[a]))]
  for li in p.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co
   uv.data[li].uv=(v[axes[0]]/scale,v[axes[1]]/scale)
def pillow(name,loc,dims,material,rotation=(0,0,0),thin=1):
 axes=[i for i in range(3) if i!=thin];a,b=[dims[i]/2 for i in axes];c=dims[thin]/2
 n=24;verts=[];faces=[]
 for side in [-1,1]:
  for j in range(n+1):
   v=j/n*2-1
   for i in range(n+1):
    u=i/n*2-1
    fullness=max(0,(1-u*u)*(1-v*v))**.42
    edge=math.exp(-((1-abs(u))/.18)**2)+math.exp(-((1-abs(v))/.18)**2)
    wrinkle=.003*edge*math.sin(u*37+v*19)*fullness
    xyz=[0,0,0];xyz[axes[0]]=a*u*math.sqrt(1-.10*v*v);xyz[axes[1]]=b*v*math.sqrt(1-.10*u*u)
    xyz[thin]=side*(c*(.12+.88*fullness)+wrinkle);verts.append(xyz)
 off=(n+1)**2
 for j in range(n):
  for i in range(n):
   k=j*(n+1)+i;quad=(k,k+1,k+n+2,k+n+1);faces.append(tuple(reversed(quad)));faces.append(tuple(v+off for v in quad))
 boundary=list(range(n+1))+[j*(n+1)+n for j in range(1,n+1)]+[n*(n+1)+i for i in range(n-1,-1,-1)]+[j*(n+1) for j in range(n-1,0,-1)]
 for k,idx in enumerate(boundary):
  nxt=boundary[(k+1)%len(boundary)];faces.append((idx,nxt,nxt+off,idx+off))
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.materials.append(material);me.update()
 o=bpy.data.objects.new(name,me);s.collection.objects.link(o);o.location=loc;o.rotation_euler=rotation
 for p in me.polygons:p.use_smooth=True
 uv_project(o)
 # A fine welt follows the actual cushion edge, never a floating rectangle.
 cu=bpy.data.curves.new(name+' welt','CURVE');cu.dimensions='3D';cu.bevel_depth=.0018;cu.bevel_resolution=1
 sp=cu.splines.new('POLY');sp.points.add(len(boundary)-1);sp.use_cyclic_u=True
 for p,idx in zip(sp.points,boundary):
  xyz=list(verts[idx]);xyz[thin]=0;p.co=(*xyz,1)
 cu.materials.append(material);seam=bpy.data.objects.new(name+' welt',cu);s.collection.objects.link(seam);seam.location=loc;seam.rotation_euler=rotation
 return o
changed=[]
for o in list(s.objects):
 if o.type!='MESH':continue
 if o.name.startswith(('Sofa cushion','Sofa scatter cushion','Euro pillow','Bed cushion','Pillow')):
  # Use local bounds including object scale, preserving original orientation.
  coords=[v.co for v in o.data.vertices];dims=[(max(v[k] for v in coords)-min(v[k] for v in coords))*abs(o.scale[k]) for k in range(3)]
  thin=min(range(3),key=lambda i:dims[i]);name=o.name
  pillow(name,tuple(o.location),dims,o.data.materials[0],tuple(o.rotation_euler),thin)
  bpy.data.objects.remove(o,do_unlink=True);changed.append(name)
for i,x in enumerate([2.36,3.60,4.84]):
 pillow('Natural loose sofa back '+str(i),(x,4.40,.91),(1.14,.24,.48),bpy.data.materials['Boucle'],(math.radians(-7),0,math.radians([1,-1.2,.5][i])),1)
# Natural folds on existing duvet and throw meshes, within their original envelope.
for o in s.objects:
 if o.type=='MESH' and o.name.startswith(('Draped linen duvet','Caramel throw')):
  for v in o.data.vertices:
   x,y,z=v.co
   v.co.z+=.009*math.sin(x*16+y*5)+.005*math.sin(x*29-y*8)
# Restrained mineral variation on ceramics rather than perfect machined solids.
for name in ['Glazed ceramic','Dark ceramic']:
 m=bpy.data.materials.get(name)
 if m:pbr(m).inputs['Specular IOR Level'].default_value=.3
# Window daylight: neutral fill and a warm raking key instead of uniformly amber ambient.
for o in s.objects:
 if o.type=='LIGHT':
  if o.name=='Golden sun':
   o.data.energy=5.0;o.data.color=(1,.84,.66);o.data.angle=math.radians(2.2)
   o.rotation_euler=(math.radians(64),0,math.radians(-32))
  elif 'sky fill' in o.name:o.data.color=(.80,.88,1.0);o.data.energy*=1.35
  elif 'wash' in o.name.lower():o.data.energy*=.72
  elif 'Ceiling downlight' in o.name:o.data.energy*=.65
 if o.type=='MESH' and any(m and m.name=='Glass' for m in o.data.materials):o.visible_shadow=False
bg=next(n for n in s.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.78,.85,1,1);bg.inputs[1].default_value=.12
s.cycles.max_bounces=10;s.cycles.diffuse_bounces=5;s.cycles.glossy_bounces=4
for o in s.objects:
 if o.name.startswith('Sofa scatter cushion'):
  o.location.y-=.27
  o.location.z+=.025
exec(compile((F/'botanicals.py').read_text(),str(F/'botanicals.py'),'exec'))
# Correct an inherited 35 mm air gap beneath the dining centerpiece.
bpy.context.view_layer.update()
for o in s.objects:
 if o.name.startswith('Handmade stoneware'):
  coords=[o.matrix_world@v.co for v in o.data.vertices]
  center=sum(coords,Vector())/len(coords)
  if 9<center.x<10 and 2<center.y<3.5:
   o.location.z+=.779-min(v.z for v in coords)
# All images packed for an editable portable source.
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(F/'natural-interior.blend'))
(F/'changes.json').write_text(json.dumps({'scope':'3D interiors only','replacedCushions':changed,'source':'../premium-interior.blend','candidate':'natural-interior.blend','websiteFilesModified':[],'layoutAndCameras':'unchanged'},indent=2))
print('NATURAL_FINISH_SAVED',flush=True)
