import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
variant=args[0] if args else 'before'
source=R/'premium-interior.blend' if variant.startswith('before') else R/'finishing/natural-interior.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
p=bpy.context.preferences.addons['cycles'].preferences;p.get_devices();g=[d for d in p.devices if d.type!='CPU']
if g:
 p.compute_device_type=g[0].type
 for d in p.devices:d.use=d.type!='CPU'
 s.cycles.device='GPU'
# Use the site's unchanged exterior as render-only context, never save it into the interior asset.
if variant in ('context','before-context'):
 for o in s.objects:
  if o.name.startswith('Landscape'):o.hide_render=True
 bpy.ops.import_scene.gltf(filepath=str(R/'runtime/exterior.glb'))
s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.use_denoising=True
s.render.resolution_x=1120;s.render.resolution_y=720;s.render.resolution_percentage=100
views={'living':([7.2,1.6,-.9],[.4,1.3,-3.2],48),'dining':([7.6,1.6,-4.8],[11.9,1.25,-1.7],50),'kitchen':([12.6,1.6,-5.4],[16,1.2,-1.8],52),'bedroom':([12.6,1.6,-9],[15.2,1,-12.8],52),'patio':([1.95,1.6,3.45],[9,1.1,1.2],48)}
def v(p):return Vector((p[0],-p[2],p[1]))
out=R/'finishing'/variant;out.mkdir(exist_ok=True)
for key in (args[1].split(',') if len(args)>1 else views):
 pos,target,fov=views[key];c=s.camera;c.location=v(pos);c.rotation_euler=(v(target)-v(pos)).to_track_quat('-Z','Y').to_euler();c.data.sensor_fit='VERTICAL';c.data.angle_y=math.radians(fov)
 s.render.filepath=str(out/(key+'.png'));bpy.ops.render.render(write_still=True);print('FINISHED',key,flush=True)
