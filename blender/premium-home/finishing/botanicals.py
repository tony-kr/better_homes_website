import bpy,math,random
from mathutils import Vector
random.seed(713)
s=bpy.context.scene
leafmat=bpy.data.materials['Olive leaf'];p=next(n for n in leafmat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
p.inputs['Base Color'].default_value=(.105,.15,.065,1);p.inputs['Roughness'].default_value=.72;p.inputs['Specular IOR Level'].default_value=.22
bark=bpy.data.materials['Bark']
def branch(points,r):
 cu=bpy.data.curves.new('Natural olive branch','CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=1
 sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
 for i,(p,xyz) in enumerate(zip(sp.points,points)):p.co=(*xyz,1);p.radius=1-.72*i/(len(points)-1)
 cu.materials.append(bark);o=bpy.data.objects.new('Natural olive branch',cu);s.collection.objects.link(o)
def leafmesh():
 v=[];f=[]
 for i in range(7):
  t=i/6;w=.013*math.sin(math.pi*t)**.75
  v.extend([(-w,t*.105,-.025*t*t+w*.3),(0,t*.105,-.025*t*t),(w,t*.105,-.025*t*t+w*.3)])
 for i in range(6):
  a=i*3;f.extend([(a,a+3,a+4,a+1),(a+1,a+4,a+5,a+2)])
 me=bpy.data.meshes.new('Natural olive leaflet');me.from_pydata(v,[],f);me.materials.append(leafmat)
 for p in me.polygons:p.use_smooth=True
 return me
leaf=leafmesh()
for x,y,h in [(.8,.85,1.9),(8.05,.62,1.7),(12.5,12,1.6)]:
 # Replace only the foliage and stems rooted in these existing planters.
 for o in list(s.objects):
  if o.name.startswith('Olive leaf') and math.hypot(o.location.x-x,o.location.y-y)<.85:bpy.data.objects.remove(o,do_unlink=True)
  elif o.name.startswith('Plant stem') and o.type=='CURVE':
   pt=o.matrix_world@Vector(o.data.splines[0].points[0].co[:3])
   if math.hypot(pt.x-x,pt.y-y)<.65:bpy.data.objects.remove(o,do_unlink=True)
 root=Vector((x,y,.57));fork=root+Vector((-.045,.018,h*.34))
 branch([root,root+Vector((.028,-.024,h*.16)),fork],.026)
 for j in range(9):
  angle=j*2.399+random.uniform(-.25,.25);r=random.uniform(.25,.49)*(h/1.9)
  end=Vector((x+math.cos(angle)*r,y+math.sin(angle)*r,.6+h*random.uniform(.65,.93)))
  mid=fork.lerp(end,.55)+Vector((.035,-.03,-.07))
  branch([fork,mid,end],.010)
  for k in range(4):
   start=mid.lerp(end,k/4)
   a=angle+random.uniform(-1.4,1.4)
   tip=start+Vector((math.cos(a)*.23,math.sin(a)*.23,random.uniform(.04,.16)))
   branch([start,start.lerp(tip,.5)+Vector((0,0,.025)),tip],.0026)
   for q in range(7):
    pos=start.lerp(tip,.18+q*.12)
    for side in [-1,1]:
     direction=Vector((math.cos(a+side*1.15),math.sin(a+side*1.15),random.uniform(-.35,.3)))
     o=bpy.data.objects.new('Natural olive leaf',leaf);s.collection.objects.link(o);o.location=pos;o.rotation_euler=direction.to_track_quat('Y','Z').to_euler();o.rotation_euler.rotate_axis('Y',random.uniform(-.8,.8));sc=random.uniform(.72,1.13);o.scale=(sc,sc,sc)
