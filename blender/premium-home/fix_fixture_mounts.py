import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'premium-interior.blend'))
for o in bpy.context.scene.objects:
 if o.name.startswith('Vertical vanity light'):
  if o.location.x>15:
   side=-1 if o.location.x<18.5 else 1;o.location=(19.8875,13.2-side*.585,1.9);o.rotation_euler.z=1.57079632679
  else:o.location.y=13.8875
 if o.type=='LIGHT' and o.name.startswith('Vanity face light'):
  if o.location.x>15:
   side=-1 if o.location.x<18.5 else 1;o.location=(19.86,13.2-side*.585,1.9);target=(18.6,13.2,1.5)
  else:o.location.y=13.86;target=(10.5,12.5,1.5)
  o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
manifest=[]
for o in bpy.context.scene.objects:
 if o.type!='LIGHT':continue
 d=o.data;manifest.append(dict(id=o.name,type=d.type.lower(),position=list(o.location),rotationEuler=list(o.rotation_euler),watts=d.energy,color=list(d.color),size=getattr(d,'size',None)))
(R/'interior-fixtures.json').write_text(json.dumps(manifest,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'premium-interior.blend'))
print('Fixture mounts and unique IDs corrected')
