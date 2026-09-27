import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'finishing/natural-interior.blend'))
s=bpy.context.scene;c=s.camera
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.get_devices();gpus=[d for d in prefs.devices if d.type!='CPU']
if gpus:
 prefs.compute_device_type=gpus[0].type
 for d in prefs.devices:d.use=d.type!='CPU'
 s.cycles.device='GPU'
# Four 120-degree corners and three distinct ceiling views, plus kitchen / bedroom ceiling.
s.render.resolution_x=640;s.render.resolution_y=440;s.cycles.samples=16
out=R/'finishing/checks';out.mkdir(exist_ok=True)
checks={
 'corner-sw':((.5,.5,1.6),(3.5,3,1.4),120),
 'corner-se':((6.7,.5,1.6),(3.5,3,1.4),120),
 'corner-ne':((6.7,5.5,1.6),(3.5,3,1.4),120),
 'corner-nw':((.7,5.4,1.6),(3.5,3,1.4),120),
 'ceiling-up':((3.5,3,1.6),(3.5,3,3.1),100),
 'ceiling-oblique-a':((1,.7,1.2),(4,4,3.1),100),
 'ceiling-oblique-b':((6.7,5.4,1.2),(3,2,3.1),100),
 'kitchen-ceiling':((12.7,4.8,1.4),(14.4,2.8,3.1),100),
 'bedroom-ceiling':((12.7,9,1.4),(14.5,12,3.1),100)}
for id,(p,t,fov) in checks.items():
 c.location=p;c.rotation_euler=(Vector(t)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=36/(2*math.tan(math.radians(fov)/2));s.render.filepath=str(out/(id+'.png'));bpy.ops.render.render(write_still=True);print('CHECK_RENDER',id,flush=True)
print('FINAL REVIEW RENDERS COMPLETE',flush=True)
