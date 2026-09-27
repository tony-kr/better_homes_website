import bpy,json,math,datetime
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'premium-interior.blend'))
centers=[(x,y) for x in (8.4,10.4) for y in (1.85,2.8,3.75)]
seat_prefix=('Tailored chair seat','Tailored chair back','Chair oak arm','Chair turned oak leg')
for o in bpy.context.scene.objects:
 if not o.name.startswith(seat_prefix):continue
 nearest=min(centers,key=lambda c:math.hypot(o.location.x-c[0],o.location.y-c[1]))
 if math.hypot(o.location.x-nearest[0],o.location.y-nearest[1])>.44:continue
 pivot=Vector((*nearest,0));o.matrix_world=Matrix.Translation(pivot)@Matrix.Rotation(math.pi,4,'Z')@Matrix.Translation(-pivot)@o.matrix_world
checks=[]
for o in bpy.context.scene.objects:
 if o.name.startswith('Tailored chair seat') and 8<o.location.x<11 and 1.5<o.location.y<4:
  front=o.matrix_world.to_3x3()@Vector((0,-1,0));toward=Vector((9.4-o.location.x,0,0)).normalized();dot=front.normalized().dot(toward);assert dot>.99,(o.name,dot)
  checks.append(dict(chair=o.name,facingTableDot=round(dot,5)))
assert len(checks)==6
(R/'dining-seating-audit.json').write_text(json.dumps({'chairs':checks,'passed':True},indent=2))
bpy.context.scene['stage']='Form approved by user, with dining chair correction verified; runtime integration in progress'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'premium-interior.blend'))
p=R/'milestone-reviews.json';d=json.loads(p.read_text());d['form'].update(status='approved',approvedBy='user',approvedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),notes='User: "continue... only thing to notice is in dining room chairs are faced opposite to table which is wrong". All six chairs corrected toward table and orientation numerically verified.');p.write_text(json.dumps(d,indent=2))
print('All six dining chairs face the table.')
