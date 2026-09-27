# Layering stays wholly inside the existing sofa envelope.
for o in s.objects:
 if o.name.startswith('Sofa scatter cushion'):
  o.location.y-=.27
  o.location.z+=.025
verts=[];faces=[];nx=48;ny=28
for j in range(ny+1):
 t=j/ny
 # Cloth runs down the back cushion, over the seat, then over the front edge.
 if t<.28:
  q=t/.28;yy=4.39-.12*q;zz=1.10-.39*q
 elif t<.72:
  q=(t-.28)/.44;yy=4.27-.46*q;zz=.71-.025*q
 else:
  q=(t-.72)/.28;yy=3.81-.065*math.sin(q*math.pi/2);zz=.685-.39*q
 for i in range(nx+1):
  u=i/nx;xx=4.18+(u-.5)*.62
  fold=.014*math.sin(u*math.pi*12+t*2)+.006*math.sin(u*math.pi*27-t*4)
  verts.append((xx,yy+.008*math.sin(u*10+t*5),zz+fold))
for j in range(ny):
 for i in range(nx):
  a=j*(nx+1)+i;faces.append((a,a+1,a+nx+2,a+nx+1))
me=bpy.data.meshes.new('Soft woven sofa throw');me.from_pydata(verts,[],faces);me.materials.append(bpy.data.materials['Oat velvet'])
o=bpy.data.objects.new('Soft woven sofa throw',me);s.collection.objects.link(o)
for f in me.polygons:f.use_smooth=True
o.modifiers.new('Cloth thickness','SOLIDIFY').thickness=.003
uv_project(o,.55)
