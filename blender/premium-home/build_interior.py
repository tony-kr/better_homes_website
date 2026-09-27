"""Detailed native Blender interior. Form-review build; no runtime export."""
import bpy, math, json, random, sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
# Reuse the approved spatial layout, without running its concept exports/renders.
source=(ROOT/'build_concept.py').read_text().split('# Ground and physically lit review scene')[0]
source=source.replace('plant(6.3,.8)','plant(.7,-2.5)')
exec(compile(source,str(ROOT/'build_concept.py'),'exec'))
random.seed(27)

def remove_prefix(*prefixes):
 for o in list(bpy.context.scene.objects):
  if any(o.name.startswith(p) for p in prefixes):bpy.data.objects.remove(o,do_unlink=True)
def bsdf(m):return next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
def color(m,c):bsdf(m).inputs['Base Color'].default_value=(*c,1);m.diffuse_color=(*c,1)
def texture(name,stem,scale=1):
 m=M[name];p=bsdf(m);nodes=m.node_tree.nodes;links=m.node_tree.links
 for suffix,socket in [('color','Base Color'),('rough','Roughness'),('normal','Normal')]:
  image=bpy.data.images.load(str(ROOT/'textures'/f'{stem}-{suffix}.png'),check_existing=True)
  if suffix!='color':image.colorspace_settings.name='Non-Color'
  t=nodes.new('ShaderNodeTexImage');t.image=image;t.label=f'Original {stem} {suffix}'
  if suffix=='normal':
   n=nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.3 if stem in ('linen','rug') else .2;links.new(t.outputs['Color'],n.inputs['Color']);links.new(n.outputs[0],p.inputs[socket])
  else:links.new(t.outputs['Color'],p.inputs[socket])
 m['uv_meters']=scale
for name,stem,scale in [('Plaster','plaster',2),('Oak','oak',1.8),('Linen','linen',.55),('Paper','linen',.55),('Travertine','travertine',2),('Limestone','limestone',2),('Rug','rug',.8)]:texture(name,stem,scale)
mat('Graphite',(.018,.023,.025),.27,.4);mat('Terracotta',(.25,.1,.055),.8);mat('Oat velvet',(.42,.34,.24),.9);mat('Book cream',(.59,.53,.4));mat('Book dark',(.09,.105,.08));mat('Mirror',(.88,.9,.91),.035,1);mat('Water',(.68,.81,.83),.03)
bsdf(M['Water']).inputs['Transmission Weight'].default_value=1
color(M['Glass'],(.97,.99,1));bsdf(M['Glass']).inputs['Roughness'].default_value=.025;bsdf(M['Glass']).inputs['Transmission Weight'].default_value=1;bsdf(M['Glass']).inputs['IOR'].default_value=1.46
color(M['Porcelain'],(.86,.84,.79));color(M['Bronze'],(.2,.13,.065));bsdf(M['Bronze']).inputs['Roughness'].default_value=.31
bsdf(M['Light']).inputs['Emission Color'].default_value=(1,.75,.43,1);bsdf(M['Light']).inputs['Emission Strength'].default_value=3
# True floor contact and soft-edge finish.
for o in list(scene.objects):
 if o.name.startswith('Sofa oak plinth'):o.location.z=.1
 if o.name.startswith('Travertine coffee table'):o.location.z=.365
 if o.name.startswith('Dining pedestal'):o.dimensions.z=.725;o.location.z=.3625
 if o.name.startswith('Stool base'):o.dimensions.z=.60;o.location.z=.30
 if o.name.startswith('Pendant suspension'):o.location.z=2.745;o.dimensions.z=.665
 if o.name.startswith('Pendant canopy'):o.location.z=3.075
 if o.name.startswith('Continuous ceiling'):o.hide_render=False
# Genuine architraves and reveals around scheduled apertures.
for a in openings:
 x,y=a['location'];w=a['widthMeters'];h=a['heightMeters'];sill=a['sillMeters'];axis=a['axis'];material='Oak' if a['kind']=='door' else 'Bronze';depth=.23 if a['kind']=='door' else .12
 for side in (-1,1):
  pos=(x+side*(w/2-.018),y,sill+h/2) if axis=='x' else (x,y+side*(w/2-.018),sill+h/2)
  dims=(.036,depth,h) if axis=='x' else (depth,.036,h)
  box('Reveal '+a['id'],pos,dims,material,.005)
 box('Opening lintel '+a['id'],(x,y,sill+h-.018),(w,depth,.036) if axis=='x' else (depth,w,.036),material,.005)
 if a['kind']=='window':box('Stone sill '+a['id'],(x,y,sill-.02),(w+.12,.32,.04) if axis=='x' else (.32,w+.12,.04),'Travertine',.01)
 # Pocket door leaf is recessed laterally into a wall pocket, leaving passage clear.
 if a['kind']=='door' and a['id'] in ['guest-entry','study-entry','bath-entry','suite-entry','utility-entry']:
  leafx=x+w/2+.36;box('Retracted pocket door '+a['id'],(leafx,y-.015,h/2),(.65,.065,h-.04),'Oak',.012)
# Stone tile joints in common floor, timber plank flooring in private rooms.
for x in range(1,20):box('Stone floor joint',(x,3,.001),(.003,5.8,.002),'Travertine',0)
for y in range(1,6):box('Stone floor joint',(10,y,.001),(19.8,.003,.002),'Travertine',0)
for xmin,xmax in ((.11,4.89),(5.11,8.89),(12.11,16.89)):
 n=int((xmax-xmin)/.19)
 for i in range(n):
  xx=xmin+(i+.5)*(xmax-xmin)/n
  for j in range(3):
   box('Private wing oak plank',(xx,9.09+j*1.92,.009),((xmax-xmin)/n-.002,1.918,.018),'Oak',.001)
# Baseboards follow visible wall segments; skip door apertures.
for w in surfaces:
 if 'facade' not in w['id'] and 'gallery' not in w['id']:continue
 o=bpy.data.objects.get(w['id']);loc=w['location'];dims=w['dimensions'];axis='x' if dims[0]>dims[1] else 'y';idx=0 if axis=='x' else 1
 lo=loc[idx]-dims[idx]/2;hi=loc[idx]+dims[idx]/2
 cuts=sorted([(a['location'][idx]-a['widthMeters']/2,a['location'][idx]+a['widthMeters']/2) for a in openings if a['wall']==w['id'] and a['sillMeters']<.13])
 intervals=[];start=lo
 for l,r in cuts:
  if l>start:intervals.append((start,l))
  start=max(start,r)
 if start<hi:intervals.append((start,hi))
 for l,r in intervals:
  for s in (-1,1):
   xx=(l+r)/2 if axis=='x' else loc[0]+s*(dims[0]/2+.009)
   yy=loc[1]+s*(dims[1]/2+.009) if axis=='x' else (l+r)/2
   box('Recessed skirting',(xx,yy,.04),(r-l,.018,.08) if axis=='x' else (.018,r-l,.08),'Oak',.004)
# Real curtain fabric: pleated mesh with a visible track at the actual facade.
def curtain(x,y,width,height=2.87):
 verts=[];faces=[];nx=100;nz=20
 for j in range(nz+1):
  z=.06+height*j/nz
  for i in range(nx+1):
   u=i/nx;verts.append((x+width*(u-.5),y+.05*math.sin(u*math.pi*18)+.009*math.sin(j*.4+u*40),z))
 for j in range(nz):
  for i in range(nx):
   a=j*(nx+1)+i;faces.append((a,a+1,a+nx+2,a+nx+1))
 me=bpy.data.meshes.new('Pleated linen');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('Full-height linen curtain',me);scene.collection.objects.link(o);me.materials.append(M['Linen'])
 for p in me.polygons:p.use_smooth=True
 sol=o.modifiers.new('Fabric thickness','SOLIDIFY');sol.thickness=.0015
 box('Curtain track',(x,y,3.05),(width+.2,.06,.045),'Bronze',.01)
for x in (1.25,5.75,7.25,11.6,12.35,16.65):curtain(x,.24,.65)
for x in (1,4.2,12.65,16.45):curtain(x,13.76,.57)
# Proper contemporary lounge chairs replacing dining-scale proxies in the living room.
remove_prefix('Chair seat','Chair curved back','Chair leg')
def upholstered_chair(x,y,rotation=0,lounge=False):
 w=.78 if lounge else .54;depth=.75 if lounge else .51;z=.42 if lounge else .47;parts=[]
 parts.append(box('Tailored chair seat',(x,y,z),(w,depth,.16),'Linen',.075))
 parts.append(box('Tailored chair back',(x,y+depth/2-.04,z+.25),(w+.025,.13,.53),'Linen',.065))
 for dx in (-w/2+.07,w/2-.07):
  parts.append(box('Chair oak arm',(x+dx,y,z+.2),(.045,depth,.055),'Oak',.02))
  for dy in (-depth/2+.07,depth/2-.07):parts.append(cyl('Chair turned oak leg',(x+dx,y+dy,(z-.08)/2),.022,z-.08,'Oak',20))
 for o in parts:
  q=o.location-Vector((x,y,0));o.location.x=x+q.x*math.cos(rotation)-q.y*math.sin(rotation);o.location.y=y+q.x*math.sin(rotation)+q.y*math.cos(rotation);o.rotation_euler.z=rotation
upholstered_chair(1.5,2.05,1.15,True);upholstered_chair(5.6,2.05,-1.15,True)
for y in (1.85,2.8,3.75):upholstered_chair(8.4,y,math.pi/2);upholstered_chair(10.4,y,-math.pi/2)
upholstered_chair(7,11.8,math.pi)
for x in (6.2,7.8):upholstered_chair(x,-1);upholstered_chair(x,-3,math.pi)
# Soften upholstery using subdivided deformed surfaces, preserving silhouettes.
def soft_cushion(name,loc,size,material='Linen',seed=0):
 o=box(name,loc,size,material,min(size)*.35)
 bpy.context.view_layer.objects.active=o
 for mod in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
 sub=o.modifiers.new('Fabric subdivision','SUBSURF');sub.levels=2;sub.render_levels=2
 tex=bpy.data.textures.new(name+' wrinkles',type='CLOUDS');tex.noise_scale=.13
 dis=o.modifiers.new('Subtle fabric irregularity','DISPLACE');dis.texture=tex;dis.strength=.009;dis.texture_coords='GLOBAL'
 for p in o.data.polygons:p.use_smooth=True
 return o
for x,r in ((2.1,-.15),(4.95,.2)):
 o=soft_cushion('Sofa scatter cushion',(x,4.46,.86),(.58,.2,.51),'Oat velvet');o.rotation_euler=(.1,r,0)
# Duvets have actual draped folds and a hem, rather than hard slabs.
remove_prefix('Linen duvet')
def duvet(x,y,w):
 verts=[];faces=[];nx=64;ny=64
 for j in range(ny+1):
  v=j/ny;yy=y-1.09+v*1.85
  for i in range(nx+1):
   u=i/nx;xx=x+(u-.5)*(w+.17);drop=max(0,(abs(u-.5)-.43)/.07)*.22
   z=.71-drop+.018*math.sin(u*53+v*14)*math.sin(v*math.pi)+.01*math.sin(v*40+u*10)
   verts.append((xx,yy,z))
 for j in range(ny):
  for i in range(nx):a=j*(nx+1)+i;faces.append((a,a+1,a+nx+2,a+nx+1))
 me=bpy.data.meshes.new('Draped duvet');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('Draped linen duvet',me);scene.collection.objects.link(o);me.materials.append(M['Linen'])
 for p in me.polygons:p.use_smooth=True
 sol=o.modifiers.new('Duvet loft','SOLIDIFY');sol.thickness=.018
for x,y,w in ((2.5,11.5,1.6),(14.5,11.5,2)):duvet(x,y,w)
# Headboards meet a full-width wall of warm panels, giving beds a real backdrop.
for x,w in ((2.5,4.76),(14.5,4.76)):
 box('Headboard wall backing',(x,13.66,1.38),(w,.12,2.76),'Oak',.015)
 # Window is above bed; backing is kept below sill, with upper panels only at ends.
 backing=bpy.context.object;backing.dimensions.z=.86;backing.location.z=.43
 for side in (-1,1):box('Headboard side pier',(x+side*2.13,13.67,1.5),(.44,.12,3),'Oak',.008)
 # Move existing bed assembly toward its support wall, including linen and lamps.
 for o in list(scene.objects):
  if o.type=='MESH' and abs(o.location.x-x)<1.9 and 10.2<o.location.y<13 and not o.name.startswith(('Private wing','Full-height','Curtain','Primary rug','Guest rug')):
   if any(o.name.startswith(t) for t in ('Upholstered bed','Mattress','Oak headboard','Pillow','Bedside','Lamp shade')):o.location.y+=.83
 # Duvet mesh coordinates are world-space, so offset by transform.
 for o in scene.objects:
  if o.name.startswith('Draped linen'):
   center=sum(v.co.x for v in o.data.vertices)/len(o.data.vertices)
   if abs(center-x)<.1:o.location.y=.83
# Functional island and east-wall kitchen: the gallery entrance remains clear.
remove_prefix('Oak kitchen cabinet','Stone worktop','Tall appliance bank')
for yy in (4.6,5.38):
 box('Kitchen drawer carcass',(16.54,yy,.45),(.72,.76,.9),'Oak',.012)
 for z in (.19,.49,.77):
  box('Kitchen drawer front',(16.164,yy,z),(.035,.724,.245),'Oak',.007)
  box('Integrated drawer pull',(16.135,yy,z+.1),(.025,.5,.018),'Bronze',.003)
box('Kitchen east counter',(16.5,4.98,.934),(.8,1.58,.068),'Travertine',.009)
for yy in (1,1.85,2.7):
 box('Tall kitchen unit',(16.55,yy,1.4),(.72,.815,2.8),'Oak',.016)
 for z in (.73,2.1):box('Tall cabinet door',(16.178,yy,z),(.025,.79,1.32),'Oak',.006)
 box('Cabinet slim handle',(16.145,yy-.25,1.4),(.03,.018,.45),'Bronze',.004)
# Oven on inward-facing surface of appliance bank.
box('Oven black glass',(16.14,1.86,1.25),(.04,.63,.58),'Graphite',.012);box('Oven brushed handle',(16.1,1.86,1.43),(.055,.45,.025),'Bronze',.008)
for y in (1.7,2.02):
 o=cyl('Oven control',(16.095,y,1.47),.025,.025,'Bronze');o.rotation_euler.y=math.pi/2
for yy in (1.365,4.135):box('Island stone end',(14.1,yy,.46),(1.34,.06,.92),'Travertine',.015)
box('Induction cooktop',(14.1,2.6,.989),(.8,.65,.018),'Graphite',.02)
for xx in (13.87,14.33):
 for yy in (2.44,2.77):cyl('Induction ring',(xx,yy,1.001),.125,.001,'Bronze')
# Recessed basin with visible bowl, rim and faucet.
def bowl(name,x,y,z,r=.23):
 verts=[];faces=[];rings=16;segments=64
 for j in range(rings+1):
  rr=.028+(r-.028)*j/rings;zz=z+.13*(j/rings)**2
  for i in range(segments):t=2*math.pi*i/segments;verts.append((x+rr*math.cos(t),y+rr*math.sin(t),zz))
 for j in range(rings):
  for i in range(segments):a=j*segments+i;b=j*segments+(i+1)%segments;faces.append((a,b,b+segments,a+segments))
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);scene.collection.objects.link(o);me.materials.append(M['Porcelain']);sol=o.modifiers.new('Ceramic thickness','SOLIDIFY');sol.thickness=.015
 for f in me.polygons:f.use_smooth=True
 cyl('Basin drain',(x,y,z),.026,.008,'Bronze')
def tube(name,pts,r=.013,material='Bronze'):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=3;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new(name,cu);scene.collection.objects.link(o);o.data.materials.append(M[material]);return o
bowl('Kitchen ceramic sink',16.47,5.15,.946,.23)
tube('Kitchen mixer',[(16.77,5.15,.97),(16.77,5.15,1.29),(16.66,5.15,1.35),(16.49,5.15,1.35),(16.46,5.15,1.29)])
# Bathrooms: replace floating concept boxes with supported vanity, shower and accessories.
remove_prefix('Floating vanity','Vanity slab','Basin','Shower tray','Shower glass','WC pedestal','WC seat')
for cx,front,back in ((10.5,8,14),(18.5,11,14)):
 existing=set(o.name for o in scene.objects)
 vy=back-.43
 box('Bathroom vanity',(cx,vy,.61),(1.82,.64,.5),'Oak',.025)
 for xx in (cx-.45,cx+.45):box('Vanity drawer',(xx,vy-.335,.64),(.87,.03,.38),'Oak',.012)
 box('Vanity stone',(cx,vy,.9),(1.87,.69,.06),'Travertine',.014);bowl('Bathroom ceramic bowl',cx,vy,.95,.24)
 tube('Wall mounted mixer',[(cx,back-.16,1.15),(cx,back-.43,1.15),(cx,back-.43,1.1)])
 box('Mirror backing',(cx,back-.14,1.92),(1.7,.05,1.5),'Bronze',.03)
 box('Vanity mirror',(cx,back-.171,1.92),(1.64,.014,1.44),'Mirror',.025)
 sy=front+(2.6 if cx==10.5 else 1.1)
 box('Shower stone tray',(cx+.6,sy,.03),(1.15,1.45,.06),'Travertine',.015)
 box('Frameless shower partition',(cx+.03,sy,1.17),(.018,1.46,2.28),'Glass',.005)
 for yy in (sy-.65,sy+.65):box('Shower glass clamp',(cx+.03,yy,.09),(.06,.06,.08),'Bronze',.004)
 tube('Rain shower riser',[(cx+1.26,sy,1),(cx+1.26,sy,2.36),(cx+.89,sy,2.36)])
 cyl('Rain shower disc',(cx+.89,sy,2.33),.14,.025,'Bronze')
 box('WC cistern wall',(cx-.9,front+.23,.55),(.8,.26,1.1),'Plaster',.02)
 box('WC ceramic body',(cx-.9,front+.6,.28),(.39,.6,.42),'Porcelain',.15)
 box('WC ceramic seat',(cx-.9,front+.64,.49),(.4,.59,.055),'Porcelain',.13)
 box('Flush plate',(cx-.9,front+.368,.88),(.2,.018,.12),'Bronze',.014)
 tube('Towel rail',[(cx-.75,back-.3,1.3),(cx-.75,back-.6,1.3),(cx-.45,back-.6,1.3),(cx-.45,back-.3,1.3)],.012)
 box('Folded hand towel',(cx-.6,back-.61,1.12),(.26,.055,.38),'Linen',.018)
# Rotate the ensuite vanity onto the east wall; keep the approved north window clear.
 if cx==18.5:
  prefixes=('Bathroom vanity','Vanity drawer','Vanity stone','Bathroom ceramic bowl','Basin drain','Wall mounted mixer','Mirror backing','Vanity mirror','Towel rail','Folded hand towel')
  from mathutils import Matrix
  transform=Matrix.Translation(Vector((20,13.2,0))) @ Matrix.Rotation(-math.pi/2,4,'Z') @ Matrix.Diagonal((.65,1,1,1)) @ Matrix.Translation(Vector((-cx,-back,0)))
  for ob in scene.objects:
   if ob.name not in existing and ob.name.startswith(prefixes):
    if ob.type=='MESH' and ob.location.length<.001:ob.data.transform(transform)
    elif ob.type=='CURVE':
     for sp in ob.data.splines:
      for p in sp.points:
       q=transform@Vector(p.co[:3]);p.co=(*q,1)
    else:ob.matrix_world=transform@ob.matrix_world
# Real open shelves and objects give the study its purpose.
remove_prefix('Study bookcase')
box('Study shelf backing',(8.78,11.2,1.45),(.08,3.6,2.8),'Oak',.008)
for yy in (9.42,11.2,12.98):box('Study upright',(8.57,yy,1.45),(.45,.055,2.8),'Oak',.008)
for z in (.08,.65,1.23,1.81,2.4,2.82):box('Study shelf',(8.57,11.2,z),(.45,3.6,.045),'Oak',.008)
for i in range(32):
 yy=9.6+(i%8)*.12;z=.68+(i//8)*.58;h=random.uniform(.19,.33)
 box('Library volume',(8.52,yy,z+h/2),(.26,.07,h),'Book cream' if i%3 else 'Book dark',.003)
box('Desk leather mat',(7,12.73,.798),(1.1,.5,.007),'Oat velvet',.015)
box('Laptop base',(7,12.8,.815),(.38,.27,.018),'Graphite',.008)
o=box('Laptop screen',(7,12.93,.95),(.38,.015,.25),'Graphite',.008);o.rotation_euler.x=math.radians(-12)
# Dressing room: separate panels, rail and hanging garments.
remove_prefix('Dressing wardrobe')
box('Dressing back',(19.83,9.5,1.4),(.08,2.78,2.8),'Oak',.008)
for yy in (8.11,9.04,9.96,10.89):box('Wardrobe divider',(19.47,yy,1.4),(.78,.045,2.8),'Oak',.006)
for z in (.1,2.23,2.78):box('Wardrobe shelf',(19.47,9.5,z),(.78,2.8,.045),'Oak',.006)
for a,b in ((8.17,8.98),(9.1,9.9),(10.02,10.82)):
 tube('Clothes rail',[(19.45,a,2.05),(19.45,b,2.05)],.016)
 for j in range(5):
  yy=a+.1+j*.14;tube('Wood hanger',[(19.45,yy,2.05),(19.15,yy,1.88),(19.73,yy,1.88),(19.45,yy,2.05)],.008,'Oak')
  box('Hanging linen garment',(19.44,yy,1.45),(.53,.055,.82),'Linen' if j%2 else 'Oat velvet',.055)
# Utility cabinet divisions, real washer fronts and sink/worktop.
for yy in (1.8,2.8):
 o=cyl('Washer glass door',(18.658,yy,.44),.23,.035,'Graphite');o.rotation_euler.y=math.pi/2
 o=cyl('Washer steel rim',(18.682,yy,.44),.265,.035,'Bronze');o.rotation_euler.y=math.pi/2
 box('Washer controls',(18.657,yy,.8),(.015,.64,.08),'Graphite',.007)
box('Utility counter',(18.98,2.3,.945),(.8,2,.08),'Travertine',.012)
# Restrained art and everyday objects.
def book(x,y,z,w=.28,d=.2,material='Book cream'):
 box('Coffee table book',(x,y,z+.025),(w,d,.05),material,.005)
def vase(x,y,z,r=.11,h=.25):
 # Lathed stoneware profile, with an open mouth.
 profile=[(.7*r,0),(r,.08*h),(r,.45*h),(.62*r,.85*h),(.55*r,h),(.43*r,h),(.48*r,.86*h),(.75*r,.4*h),(.5*r,.12*h)]
 verts=[];faces=[];n=48
 for rr,zz in profile:
  for i in range(n):a=i*2*math.pi/n;verts.append((x+rr*math.cos(a),y+rr*math.sin(a),z+zz))
 for j in range(len(profile)-1):
  for i in range(n):a=j*n+i;b=j*n+(i+1)%n;faces.append((a,b,b+n,a+n))
 me=bpy.data.meshes.new('Stoneware profile');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('Handmade stoneware',me);scene.collection.objects.link(o);me.materials.append(M['Travertine'])
 for p in me.polygons:p.use_smooth=True
vase(3.55,2.75,.41,.09,.22);book(3.16,2.5,.41);book(3.18,2.5,.46,.24,.18,'Book dark');vase(9.4,2.8,.815,.13,.32)
for yy in (1.8,3.7):
 for xx in (9.04,9.76):
  cyl('Dining stoneware plate',(xx,yy,.826),.16,.02,'Porcelain');cyl('Linen napkin ring',(xx,yy,.854),.035,.025,'Bronze')
# Minimal art on living west wall, on a real support.
box('Art frame',(.126,3,1.8),(.035,2.1,1.2),'Bronze',.008)
box('Art canvas',(.148,3,1.8),(.012,2.04,1.14),'Paper',.005)
for yy,z,w,h,material in ((2.65,1.85,.63,.75,'Oat velvet'),(3.35,1.65,.65,.43,'Sage'),(3.45,2.1,.33,.26,'Terracotta')):box('Abstract relief art',(.159,yy,z),(.007,w,h),material,.04)
# Organic leaves with thin stems, instead of clustered primitive spheres.
remove_prefix('Foliage')
def leafy_plant(x,y):
 for stem in range(5):
  ang=stem*2.4;h=random.uniform(1,1.7);ex=x+.16*math.cos(ang);ey=y+.16*math.sin(ang)
  tube('Plant stem',[(x,y,.38),(ex,ey,h)],.008,'Oak')
  for k in range(5):
   a=ang+k*2.2;z=.63+k*(h-.55)/5;cx=ex+.14*math.cos(a);cy=ey+.14*math.sin(a)
   verts=[(ex,ey,z),(cx-.08*math.sin(a),cy+.08*math.cos(a),z+.12),(ex+.4*math.cos(a),ey+.4*math.sin(a),z+.15),(cx+.08*math.sin(a),cy-.08*math.cos(a),z+.12),(cx,cy,z+.16)]
   me=bpy.data.meshes.new('Leaf');me.from_pydata(verts,[],[(0,1,4),(1,2,4),(2,3,4),(3,0,4)]);me.update();o=bpy.data.objects.new('Botanical leaf',me);scene.collection.objects.link(o);me.materials.append(M['Leaves'])
for o in list(scene.objects):
 if o.name.startswith('Stone planter'):leafy_plant(o.location.x,o.location.y)
# Exterior garden context visible through glazing; no unrelated HDRI.
box('Landscape',(10,5,-.34),(64,55,.4),'Sage',.02,tag='site')
for y in (-5.4,15.8):
 box('Garden perimeter planter',(10,y,.2),(29,1.4,.4),'Travertine',.06)
 for x in range(-3,25,2):leafy_plant(x,y)
box('South garden boundary',(10,-8,1),(38,.24,2.4),'Plaster',.03)
box('North garden boundary',(10,18,1),(38,.24,2.4),'Plaster',.03)
# Sealed ceiling, restrained lowered perimeter trim and warm built-in light.
for x0,x1,y0,y1 in ((.1,11.9,.1,5.9),(12.1,16.9,.1,5.9),(.1,4.9,8.1,13.9),(5.1,8.9,8.1,13.9),(12.1,16.9,8.1,13.9)):
 for y in (y0+.12,y1-.12):box('Ceiling perimeter reveal',((x0+x1)/2,y,3.015),(x1-x0,.19,.17),'Plaster',.014)
 for x in (x0+.12,x1-.12):box('Ceiling perimeter reveal',(x,(y0+y1)/2,3.015),(.19,y1-y0-.38,.17),'Plaster',.014)
# Shared fixture manifest is the source for all actual lights.
fixtures=[]
def area(name,pos,power,size=1,color=(1,.82,.62),target=None):
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.color=color;data.shape='DISK';data.size=size
 o=bpy.data.objects.new(name,data);scene.collection.objects.link(o);o.location=pos
 o.visible_camera=False;o.visible_glossy=False;o.visible_transmission=False
 if target is not None:o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
 fixtures.append(dict(id=o.name,type='area',position=list(pos),target=list(target) if target else [pos[0],pos[1],0],watts=power,size=size,color=list(color)))
 return o
for x,y in ((9.4,2),(9.4,3.6),(14.1,2),(14.1,3.5)):
 cyl('Pendant diffuser',(x,y,2.215),.28,.015,'Light');area('Pendant light',(x,y,2.2),45,.5)
for x,y in ((2,2),(5,2),(2,5.25),(7,5.25),(11,5.25),(15.5,5),(18.5,3),(2.5,9.5),(7,10),(10.5,10.5),(14.5,9.5),(18.2,9.5),(18.5,12)):
 cyl('Recessed downlight trim',(x,y,3.086),.058,.025,'Bronze');cyl('Downlight lens',(x,y,3.068),.043,.009,'Light');area('Ceiling downlight',(x,y,3.058),35,.16)
for x in (2,5,8,11,14,17):area('Gallery practical',(x,7,3.02),45,.9)
for x,y in ((1.27,13),(3.73,13),(13.07,13),(15.93,13)):area('Bedside warm light',(x,y,1.1),12,.2,target=(x,y,.45))
for x in (10.5,18.5):
 for dx in (-.9,.9):
  if x==18.5:
   yy=13.2-dx*.65
   box('Vertical vanity light',(19.8875,yy,1.9),(.025,.025,1.2),'Light',.01);area('Vanity face light',(19.86,yy,1.9),20,.5,target=(18.6,13.2,1.5))
  else:
   box('Vertical vanity light',(x+dx,13.8875,1.9),(.025,.025,1.2),'Light',.01);area('Vanity face light',(x+dx,13.86,1.9),20,.5,target=(x,12.5,1.5))
exec(compile((ROOT/'finish_details.py').read_text(),str(ROOT/'finish_details.py'),'exec'))
bpy.context.view_layer.update()
# UVs are authored at material-specific metre scales and will survive GLB export.
for o in scene.objects:
 if o.type!='MESH' or not o.data.materials:continue
 me=o.data;uv=me.uv_layers.active or me.uv_layers.new(name='UVMap');scale=o.data.materials[0].get('uv_meters',1)
 for p in me.polygons:
  axis=max(range(3),key=lambda k:abs(p.normal[k]));axes=[k for k in range(3) if k!=axis]
  for li in p.loop_indices:
   co=o.matrix_world@me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]/scale,co[axes[1]]/scale)
# Broad daylight, physical sun, carefully restrained exposure.
world=bpy.data.worlds.new('Architectural daylight');world.use_nodes=True;scene.world=world
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.78,.86,1,1);bg.inputs[1].default_value=.4
ld=bpy.data.lights.new('Afternoon sun','SUN');ld.energy=2;ld.angle=.12;sun=bpy.data.objects.new('Afternoon sun',ld);scene.collection.objects.link(sun);sun.rotation_euler=(math.radians(31),math.radians(-22),math.radians(-35))
# Window daylight area emitters are outside the shell, aligned through real openings.
for x,w in ((3.5,3.6),(9.5,3.6),(14.5,3.7)):area('South sky fill',(x,-.3,2),230,w,(.82,.9,1),target=(x,4,1))
for x,w in ((2.5,3.2),(7,2.8),(14.5,3.3),(18.5,1.4)):area('North sky fill',(x,14.3,2.2),180,w,(.85,.92,1),target=(x,10,1))
area('Entry sky fill',(-.3,7,2),150,2.4,(.9,.95,1),target=(4,7,1.5))
scene.render.engine='CYCLES'
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.get_devices()
gpus=[d for d in prefs.devices if d.type!='CPU']
if gpus:
 try:
  prefs.compute_device_type=gpus[0].type
  for d in prefs.devices:d.use=d.type!='CPU'
  scene.cycles.device='GPU';print('GPU RENDER DEVICE',gpus[0].name,flush=True)
 except (TypeError,RuntimeError) as e:print('Using CPU:',e,flush=True)
scene.cycles.samples=48;scene.cycles.use_denoising=True;scene.cycles.max_bounces=10;scene.cycles.transmission_bounces=8
scene.render.resolution_x=1400;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
scene.view_settings.exposure=.35
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Interior production camera';scene.camera=cam;cam.data.lens=23;cam.data.clip_start=.05

def aim(pos,target,lens=23):
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
views={
 'living':((7.2,.85,1.65),(3.2,3.7,1.15),26),
 'dining':((11.45,5.28,1.6),(8.9,2.55,1.2),25),
 'kitchen':((12.63,5.38,1.6),(14.75,2.7,1.3),23),
 'bedroom':((12.65,9.05,1.6),(14.5,12.35,1.18),23),
 'guest':((4.45,8.7,1.6),(2.5,12.05,1.1),23),
 'study':((5.55,8.7,1.6),(7.25,12.1,1.3),24),
 'bathroom':((9.65,9.65,1.6),(10.55,12.8,1.45),22),
 'ensuite':((17.45,12.2,1.6),(19.2,13.1,1.4),18),
 'dressing':((17.45,8.5,1.6),(19.35,9.65,1.5),21),
 'utility':((17.5,5.3,1.6),(19.1,2.2,1.2),22),
 'patio':((2,-3.5,1.7),(8,-1,1.2),26),
}
(ROOT/'interior-fixtures.json').write_text(json.dumps(fixtures,indent=2))
(ROOT/'interior-cameras.json').write_text(json.dumps({k:dict(position=p,target=t,lens=l) for k,(p,t,l) in views.items()},indent=2))
# Record provenance and counts, save native editable source with packed PBR maps.
for image in bpy.data.images:
 if image.source=='FILE':image.pack()
aim(*views['living'])
scene['stage']='Form review; layout approved by user; not yet exported'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'premium-interior.blend'))
(ROOT/'renders'/'interiors').mkdir(exist_ok=True)
only=sys.argv[sys.argv.index('--only')+1].split(',') if '--only' in sys.argv else list(views)
if '--draft' in sys.argv:scene.render.resolution_percentage=60;scene.cycles.samples=24
for id in only:
 aim(*views[id]);scene.render.filepath=str(ROOT/'renders'/'interiors'/f'{id}.png');bpy.ops.render.render(write_still=True);print('REVIEW_RENDER_COMPLETE',id,flush=True)
print('DETAILED INTERIOR BUILD COMPLETE',flush=True)
