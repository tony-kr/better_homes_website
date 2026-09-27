import bpy,math,ast
from pathlib import Path
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'premium-interior.blend'))
scene=bpy.context.scene;M={m.name:m for m in bpy.data.materials};objects=[]
for filename,names in [('build_concept.py',{'box'}),('build_interior.py',{'remove_prefix'})]:
 tree=ast.parse((R/filename).read_text());tree.body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names];exec(compile(tree,filename,'exec'))
exec(compile((R/'finish_details.py').read_text(),'finish_details.py','exec'))
bpy.context.view_layer.update()
for o in scene.objects:
 if o.type!='MESH' or not o.data.materials:continue
 me=o.data;uv=me.uv_layers.active or me.uv_layers.new(name='UVMap');scale=o.data.materials[0].get('uv_meters',1)
 for p in me.polygons:
  axis=max(range(3),key=lambda k:abs(p.normal[k]));axes=[k for k in range(3) if k!=axis]
  for li in p.loop_indices:
   co=o.matrix_world@me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]/scale,co[axes[1]]/scale)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'premium-interior.blend'))
print('Final furniture details applied')
