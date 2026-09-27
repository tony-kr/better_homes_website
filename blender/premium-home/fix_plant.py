import bpy
from pathlib import Path
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'premium-interior.blend'))
for o in bpy.context.scene.objects:
 if o.name.startswith('Stone planter') and abs(o.location.x-6.3)<.01 and abs(o.location.y-.8)<.01:o.location.y-=1.6
 if o.name.startswith('Plant stem'):
  p=o.data.splines[0].points[0].co
  if abs(p.x-6.3)<.01 and abs(p.y-.8)<.01:
   for sp in o.data.splines:
    for q in sp.points:q.co.y-=1.6
 if o.name.startswith('Botanical leaf'):
  p=o.data.vertices[0].co
  if abs(p.x-6.3)<.3 and abs(p.y-.8)<.3:
   for v in o.data.vertices:v.co.y-=1.6
bpy.ops.wm.save_as_mainfile(filepath=str(R/'premium-interior.blend'))
print('Plant moved outside camera foreground')
