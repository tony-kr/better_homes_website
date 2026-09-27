import bpy,math,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'premium-interior.blend'))
s=bpy.context.scene;c=s.camera;s.render.resolution_x=900;s.render.resolution_y=600;s.render.resolution_percentage=100;s.cycles.samples=24
out=R/'renders'/'checks';out.mkdir(exist_ok=True)
views={
 'corner-sw':((.5,.5,1.6),(3.5,3,1.4),120),
 'corner-se':((6.7,.5,1.6),(3.5,3,1.4),120),
 'corner-ne':((6.7,5.5,1.6),(3.5,3,1.4),120),
 'corner-nw':((.7,5.4,1.6),(3.5,3,1.4),120),
 'ceiling-up':((3.5,3,1.6),(3.5,3,3.1),100),
 'ceiling-oblique-a':((1,.7,1.2),(4,4,3.1),100),
 'ceiling-oblique-b':((6.7,5.4,1.2),(3,2,3.1),100),
 'kitchen-ceiling':((12.7,4.8,1.4),(14.4,2.8,3.1),100),
 'bedroom-ceiling':((12.7,9,1.4),(14.5,12,3.1),100),
}
for id,(p,t,fov) in views.items():
 c.location=p;c.rotation_euler=(Vector(t)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=36/(2*math.tan(math.radians(fov)/2));s.render.filepath=str(out/(id+'.png'));bpy.ops.render.render(write_still=True);print('CHECK_RENDER',id,flush=True)
