"""Review-only Blender concept. Does not export or replace the website model."""
import bpy, math, json, os
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'
M={}
def mat(name,color,rough=.6,metal=0):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'); p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 M[name]=m;return m
mat('Limestone',(.63,.57,.46));mat('Plaster',(.82,.78,.69));mat('Oak',(.32,.19,.095));mat('Linen',(.74,.70,.60));mat('Bronze',(.13,.085,.045),.3,.75);mat('Travertine',(.63,.52,.37));mat('Sage',(.24,.29,.21));mat('Porcelain',(.84,.83,.78),.2);mat('Glass',(.25,.38,.4),.18);mat('Rug',(.47,.43,.36));mat('Soil',(.12,.1,.07));mat('Leaves',(.12,.19,.1));mat('Paper',(.85,.82,.72));mat('Light',(.98,.83,.57))
objects=[]; surfaces=[]; openings=[]; instances=[]; fixtures=[]
def box(name,loc,size,material='Plaster',bevel=0.025,tag='furniture'):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o.data.materials.append(M[material]);o['layer']=tag
 if bevel:
  mod=o.modifiers.new('Soft manufactured edge','BEVEL');mod.width=bevel;mod.segments=3
  mod=o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 objects.append(o);return o
def cyl(name,loc,r,depth,material='Oak',vertices=48):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc);o=bpy.context.object;o.name=name;o.data.materials.append(M[material]);o['layer']='furniture'
 b=o.modifiers.new('Edge','BEVEL');b.width=.015;b.segments=3
 for p in o.data.polygons:p.use_smooth=True
 objects.append(o);return o
def wall(name,loc,size):
 o=box(name,loc,size,bevel=0,tag='wall');surfaces.append(dict(id=name,location=list(loc),dimensions=list(size)));return o
def opening(w,name,loc,width,height,dest,axis='x',sill=0,kind='door'):
 size=(width,.6,height) if axis=='x' else (.6,width,height)
 cutter=box('Cutter '+name,(loc[0],loc[1],sill+height/2),size,bevel=0)
 mod=w.modifiers.new(name,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
 bpy.context.view_layer.objects.active=w;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True);objects.remove(cutter)
 openings.append(dict(id=name,kind=kind,wall=w.name,widthMeters=width,heightMeters=height,sillMeters=sill,thresholdMeters=0,depthMeters=.2,destination=dest,location=list(loc),axis=axis,approved=False,mask='masks/'+name+'.png',cutter='masks/'+name+'.json'))
 if kind=='window':
  glass=box('Glazing '+name,(loc[0],loc[1],sill+height/2),(width,.035,height) if axis=='x' else (.035,width,height),'Glass',.005,tag='glazing')
  for s in (-1,1):
   p=(loc[0]+s*width/2,loc[1],sill+height/2) if axis=='x' else (loc[0],loc[1]+s*width/2,sill+height/2)
   box('Bronze jamb '+name,p,(.04,.07,height),'Bronze',.005,tag='glazing')
def chair(x,y,rot=0):
 parts=[]
 parts.append(box('Chair seat',(x,y,.47),(.56,.54,.15),'Linen',.075))
 parts.append(box('Chair curved back',(x,y+.23,.78),(.57,.12,.5),'Linen',.06))
 for dx in (-.21,.21):
  for dy in (-.2,.2):parts.append(cyl('Chair leg',(x+dx,y+dy,.22),.025,.44,'Oak',16))
 for o in parts:
  d=o.location-Vector((x,y,0));o.location.x=x+d.x*math.cos(rot)-d.y*math.sin(rot);o.location.y=y+d.x*math.sin(rot)+d.y*math.cos(rot);o.rotation_euler.z=rot
 return parts
def bed(x,y,w=2):
 box('Upholstered bed base',(x,y,.23),(w+.14,2.2,.4),'Linen',.12)
 box('Mattress',(x,y,.53),(w,2.08,.26),'Paper',.12)
 box('Linen duvet',(x,y-.23,.69),(w+.05,1.62,.16),'Linen',.13)
 box('Oak headboard',(x,y+1.2,.75),(w+1.5,.16,1.5),'Oak',.04)
 for dx in (-w/4,w/4):box('Pillow',(x+dx,y+.65,.75),(w*.44,.47,.18),'Paper',.12)
 for dx in (-w/2-.43,w/2+.43):
  box('Bedside drawer',(x+dx,y+.67,.3),(.6,.55,.58),'Oak',.035);cyl('Bedside lamp base',(x+dx,y+.67,.64),.11,.08,'Bronze');cyl('Lamp shade',(x+dx,y+.67,.88),.18,.28,'Linen')
def plant(x,y):
 cyl('Stone planter',(x,y,.25),.28,.5,'Travertine')
 for a in range(7):
  t=a*2.4;bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,location=(x+.18*math.cos(t),y+.18*math.sin(t),.7+a*.075));o=bpy.context.object;o.name='Foliage';o.scale=(.18,.09,.33);o.rotation_euler=(.3*math.cos(t),.4*math.sin(t),t);o.data.materials.append(M['Leaves']);o['layer']='furniture';objects.append(o)
def pendant(x,y):
 cyl('Pendant canopy',(x,y,3.07),.08,.05,'Bronze');cyl('Pendant suspension',(x,y,2.72),.009,.7,'Bronze',12);cyl('Pendant shade',(x,y,2.31),.32,.16,'Linen');fixtures.append(dict(id='pendant-'+str(len(fixtures)),position=[x,y,2.2],color='#ffe3b0',power=150))
 for o in objects[-3:]:o['layer']='ceiling'
# Shell: a 20 x 14 m compact home, plus garden terrace. Review cutaway has its ceiling hidden.
box('Continuous floor',(10,7,-.12),(20.3,14.3,.24),'Limestone',.02,tag='floor')
box('Garden terrace',(9,-2,-.13),(18,4,.26),'Travertine',.03,tag='floor')
box('Arrival apron',(-1.5,7,-.12),(3,3,.24),'Limestone',.02,tag='floor')
S=wall('South facade',(10,0,1.55),(20.2,.2,3.1));N=wall('North facade',(10,14,1.55),(20.2,.2,3.1));W=wall('West facade',(0,7,1.55),(.2,14,3.1));E=wall('East facade',(20,7,1.55),(.2,14,3.1))
lo=wall('South gallery partition',(10,6,1.55),(20,.18,3.1));hi=wall('North gallery partition',(10,8,1.55),(20,.18,3.1))
opening(W,'arrival',(0,7),2.4,2.8,'Entry gallery','y')
for name,x,width,dest in [('living-entry',3.7,2.8,'Living'),('dining-entry',9.5,2.5,'Dining'),('kitchen-entry',14.4,2.2,'Kitchen'),('utility-entry',18.5,.95,'Utility')]:opening(lo,name,(x,6),width,2.8,dest)
for name,x,width,dest in [('guest-entry',3.5,1.1,'Guest bedroom'),('study-entry',7,1.2,'Study'),('bath-entry',10.5,1,'Guest bathroom'),('suite-entry',14.2,1.4,'Primary suite')]:opening(hi,name,(x,8),width,2.7,dest)
for x in (5,9,12):wall('North dividing wall '+str(x),(x,11,1.55),(.18,6,3.1))
sep=wall('Kitchen screen',(12,3,1.55),(.18,6,3.1));opening(sep,'dining-kitchen',(12,4.3),2.6,2.8,'Kitchen','y')
wall('Utility partition',(17,3,1.55),(.18,6,3.1))
ens=wall('Suite service wall',(17,11,1.55),(.18,6,3.1));opening(ens,'dressing-entry',(17,9.5),1.2,2.7,'Dressing','y');opening(ens,'ensuite-entry',(17,12.4),1,2.7,'Ensuite','y')
wall('Ensuite partition',(18.5,11,1.55),(3,.18,3.1))
opening(S,'terrace-passage',(3.5,0),3.6,2.8,'Garden terrace')
for x,w in ((9.5,3.6),(14.5,3.7)):opening(S,'garden-'+str(x),(x,0),w,2.7,'Garden terrace',sill=.1,kind='window')
for x,w in ((2.5,3.2),(7,2.8),(14.5,3.3),(18.5,1.4)):opening(N,'north-'+str(x),(x,14),w,1.8,'Planted garden',sill=1,kind='window')
ceiling=box('Continuous ceiling',(10,7,3.2),(20.2,14.2,.2),'Plaster',.01,tag='ceiling');ceiling.hide_render=True
# Living conversation group
box('Living wool rug',(3.5,2.9,.015),(5,3.6,.03),'Rug',.07)
box('Sofa oak plinth',(3.6,4.25,.13),(3.6,1,.2),'Oak',.08)
box('Sofa soft base',(3.6,4.25,.35),(3.8,1.05,.35),'Linen',.17)
box('Sofa back',(3.6,4.66,.75),(3.8,.3,.76),'Linen',.15)
for x in (2.36,3.6,4.84):box('Sofa cushion',(x,4.18,.59),(1.18,.84,.22),'Linen',.12)
for x in (1.68,5.52):box('Sofa arm',(x,4.23,.64),(.25,1.06,.55),'Linen',.12)
cyl('Travertine coffee table',(3.4,2.64,.34),.7,.09,'Travertine');cyl('Coffee pedestal',(3.4,2.64,.16),.32,.32,'Travertine')
chair(1.5,2.15,math.pi*.55);chair(5.6,2.15,-math.pi*.55)
box('Media joinery',(.36,3,.36),(.5,3.4,.7),'Oak',.025)
plant(.7,.7);plant(6.3,.8)
# Dining
box('Dining rug',(9.4,2.8,.016),(4,4.2,.032),'Rug',.04)
box('Oval dining top',(9.4,2.8,.77),(1.25,2.85,.09),'Oak',.3)
for y in (1.9,3.7):cyl('Dining pedestal',(9.4,y,.35),.24,.7,'Oak')
for y in (1.85,2.8,3.75):chair(8.4,y,-math.pi/2);chair(10.4,y,math.pi/2)
for y in (2,3.6):pendant(9.4,y)
# Kitchen perimeter and island
for x in (12.6,13.4,14.2,15,15.8,16.6):
 box('Oak kitchen cabinet',(x,5.5,.44),(.77,.65,.88),'Oak',.012);box('Stone worktop',(x,5.5,.91),(.8,.69,.06),'Travertine',.01)
box('Tall appliance bank',(16.5,2,.0+1.35),(.75,2.8,2.7),'Oak',.03)
box('Kitchen island',(14.1,2.75,.45),(1.2,2.7,.9),'Oak',.025);box('Waterfall stone island',(14.1,2.75,.94),(1.34,2.85,.08),'Travertine',.018)
for y in (1.9,2.75,3.6):cyl('Stool seat',(12.95,y,.66),.24,.12,'Linen');cyl('Stool base',(12.95,y,.3),.06,.6,'Bronze')
pendant(14.1,2);pendant(14.1,3.5)
# Utility
box('Laundry cabinets',(19.5,3,1.2),(.7,4,2.4),'Plaster',.025)
for y in (1.8,2.8):box('Laundry appliance',(19, y,.45),(.65,.8,.9),'Porcelain',.04)
# Sleeping and work spaces
box('Guest rug',(2.5,11,.014),(3.7,3.8,.028),'Rug',.03);bed(2.5,11.5,1.6)
box('Guest wardrobe',(.5,9.5,1.35),(.65,2,2.7),'Oak',.025)
box('Study desk',(7,12.8,.75),(2.5,.8,.08),'Oak',.025)
for x in (5.9,8.1):box('Desk legs',(x,12.8,.36),(.09,.65,.72),'Bronze',.01)
chair(7,11.8,math.pi)
box('Study bookcase',(8.65,10.9,1.2),(.45,2.7,2.4),'Oak',.02)
box('Primary rug',(14.5,11.3,.015),(4.6,4.1,.03),'Rug',.05);bed(14.5,11.5,2)
for y in (8.6,9.4,10.2):box('Dressing wardrobe',(19.5,y,1.35),(.7,.77,2.7),'Oak',.015)
# Bathrooms
for x,y in ((10.5,11),(18.5,12.5)):
 box('Floating vanity',(x,y+.9,.64),(1.8,.55,.48),'Oak',.02);box('Vanity slab',(x,y+.9,.91),(1.85,.6,.07),'Travertine',.02)
 cyl('Basin',(x,y+.9,1.02),.22,.18,'Porcelain')
 box('Shower tray',(x+.4,y-.9,.045),(1.15,1.2,.09),'Travertine',.015)
 box('Shower glass',(x-.2,y-.9,1.1),(.025,1.2,2.2),'Glass',.005)
 cyl('WC pedestal',(x-.6,y-.9,.2),.19,.4,'Porcelain');box('WC seat',(x-.6,y-.9,.44),(.4,.57,.13),'Porcelain',.15)
# Terrace seating
box('Terrace table',(7,-2,.72),(2.2,1,.09),'Oak',.15)
for x in (6.2,7.8):chair(x,-1);chair(x,-3,math.pi)
for x in (1,11,17):plant(x,-3)
# Discrete hall ceiling rails / lights, separated as reflected ceiling plan.
for x in (2,5,8,11,14,17):
 o=box('Gallery light',(x,7,3.06),(1.2,.06,.04),'Light',.01,tag='ceiling');fixtures.append(dict(id='gallery-'+str(x),position=[x,7,3],power=50,color='#ffe3b0'))
# Human-height proposed camera routes, each entering via a doorway and returning to gallery.
rooms=[('living','Living room',(0,0,7,6),(3.7,6),(5.8,5.1,1.6),(3.2,2.8,1.1)),('dining','Dining',(7,0,12,6),(9.5,6),(11.1,4.9,1.6),(9.4,2.7,1.1)),('kitchen','Kitchen',(12,0,17,6),(14.4,6),(12.8,4.65,1.6),(14.8,2.4,1.1)),('utility','Utility',(17,0,20,6),(18.5,6),(18,4.8,1.6),(19.2,2.8,1.2)),('guest','Guest bedroom',(0,8,5,14),(3.5,8),(3.5,9,1.6),(2.5,11.5,.9)),('study','Study',(5,8,9,14),(7,8),(6.2,9.1,1.6),(7.2,12.3,1.1)),('bathroom','Guest bathroom',(9,8,12,14),(10.5,8),(10.4,9.1,1.6),(10.5,11.5,1.1)),('bedroom','Primary bedroom',(12,8,17,14),(14.2,8),(13.2,9.1,1.6),(14.5,11.5,1)),('dressing','Dressing',(17,8,20,11),(17,9.5),(18,9.5,1.6),(19.5,9.5,1.3)),('ensuite','Ensuite',(17,11,20,14),(17,12.4),(17.6,12.4,1.6),(18.6,12.8,1)),('patio','Garden terrace',(0,-4,18,0),(3.5,0),(4,-1,1.6),(8,-2,1))]
metadata=[]
for id,label,bounds,entry,pos,target in rooms:
 metadata.append(dict(id=id,label=label,bounds=list(bounds),entry=list(entry),camera=list(pos),target=list(target)))
# Ground and physically lit review scene
box('Site',(10,5,-.4),(60,55,.25),'Sage',.02,tag='site')
world=bpy.data.worlds.new('Daylight');world.use_nodes=True;scene.world=world
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.74,.81,.94,1);bg.inputs[1].default_value=.5
ld=bpy.data.lights.new('Sun','SUN');ld.energy=2;ld.angle=.15;sun=bpy.data.objects.new('Sun',ld);scene.collection.objects.link(sun);sun.rotation_euler=(.4,-.5,-.5)
bpy.ops.object.camera_add(location=(30,-27,29));cam=bpy.context.object;cam.name='Review camera';scene.camera=cam
try:scene.render.engine='CYCLES'
except TypeError:pass
scene.cycles.samples=16;scene.cycles.use_denoising=True
scene.render.resolution_x=1600;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
def aim(loc,target,ortho=None):
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO' if ortho else 'PERSP';cam.data.ortho_scale=ortho or 30;cam.data.lens=26

def render(path):
 scene.render.filepath=str(ROOT/path);bpy.ops.render.render(write_still=True)
# Save immutable review stage separately from existing build.
aim((29,-26,29),(9,5,0),33)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'concept.blend'))
render('renders/layout-axon.png')
# Exact mesh orthographic plans; grayscale clay, no substitute rectangles.
original={o.name:list(o.data.materials) for o in scene.objects if o.type=='MESH'}
clay=mat('Plan white',(.86,.86,.86));wallmat=mat('Plan wall',(.06,.06,.06))
for o in scene.objects:
 if o.type=='MESH':
  o.data.materials.clear();o.data.materials.append(wallmat if o.get('layer')=='wall' else clay)
  o.hide_render=o.get('layer') in ('ceiling','site')
plan_cut=box('Plan cut above 1.2m',(10,7,3.2),(24,18,4),bevel=0,tag='plan-helper');plan_cut.hide_render=True
for o in scene.objects:
 if o.get('layer')=='wall':
  mod=o.modifiers.new('Plan section only','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=plan_cut
aim((10,5,35),(10,5,0),26);scene.render.resolution_x=1500;scene.render.resolution_y=1200
render('plans/lower-room.png')
for o in scene.objects:
 if o.type=='MESH':o.hide_render=o.get('layer') not in ('wall','ceiling') or o.name=='Continuous ceiling'
render('plans/reflected-ceiling.png')
# Restore full-height walls after engineering section renders.
for o in scene.objects:
 if o.modifiers.get('Plan section only'):o.modifiers.remove(o.modifiers.get('Plan section only'))
bpy.data.objects.remove(plan_cut,do_unlink=True)
# Restore palette and render shell elevation.
for o in scene.objects:
 if o.type=='MESH':
  o.data.materials.clear()
  for m in original.get(o.name,[]):o.data.materials.append(m)
  o.hide_render=o.name=='Continuous ceiling'
aim((10,-30,1.55),(10,0,1.55),23);scene.render.resolution_x=1600;scene.render.resolution_y=400;render('plans/south-elevation.png')
# Review furniture silhouettes drawn from the same modeled objects.
for o in scene.objects:
 if o.type=='MESH':o.hide_render=o.get('layer') in ('wall','glazing','ceiling','site')
aim((27,-26,30),(9,5,0),31);scene.render.resolution_y=1200;render('images/furniture-reference.png')
# Persist machine-readable proposed layout.
(ROOT/'concept-rooms.json').write_text(json.dumps(metadata,indent=2))
(ROOT/'fixture-manifest.json').write_text(json.dumps(fixtures,indent=2))
layout=json.loads((ROOT/'room-layout.json').read_text());layout['surfaces']=surfaces;layout['productionCamera']={'location':[5.8,5.1,1.6],'target':[3.2,2.8,1.1],'verticalFovDegrees':55};layout['conceptObjects']=[dict(id=o.name,location=list(o.location),dimensions=list(o.dimensions),layer=o.get('layer')) for o in scene.objects if o.type=='MESH'];(ROOT/'room-layout.json').write_text(json.dumps(layout,indent=2))
schedule=json.loads((ROOT/'openings.json').read_text());schedule['primaryArrival']={'openingId':'arrival','exception':''};schedule['openings']=openings;(ROOT/'openings.json').write_text(json.dumps(schedule,indent=2))
print('CONCEPT COMPLETE')
