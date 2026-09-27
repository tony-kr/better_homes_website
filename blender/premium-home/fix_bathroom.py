import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'premium-interior.blend'))
for o in bpy.context.scene.objects:
 if o.name.startswith(('Shower stone tray','Frameless shower partition','Shower glass clamp','Rain shower disc')) and 9<o.location.x<12 and o.location.y<11:o.location.y+=1.5
 if o.name.startswith('Rain shower riser'):
  first=o.data.splines[0].points[0].co
  if 9<first.x<12:
   for sp in o.data.splines:
    for p in sp.points:p.co.y+=1.5
p=R/'interior-cameras.json';d=json.loads(p.read_text());d['bathroom'].update(position=[9.65,9.65,1.6],target=[10.55,12.8,1.45]);p.write_text(json.dumps(d,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'premium-interior.blend'))
print('Bathroom clearance corrected')
