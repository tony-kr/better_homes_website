import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'premium-interior.blend'))
result={'materials':[],'objects':[],'lights':[],'world':[]}
for m in bpy.data.materials:
 if not m.use_nodes:continue
 p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
 result['materials'].append({'name':m.name,'textures':[n.image.filepath for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image],'color':list(p.inputs['Base Color'].default_value) if p else None})
for o in bpy.context.scene.objects:
 if o.type=='LIGHT':result['lights'].append({'name':o.name,'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'rotation':list(o.rotation_euler),'location':list(o.location)})
 elif o.type=='MESH':result['objects'].append({'name':o.name,'loc':list(o.location),'dims':list(o.dimensions),'verts':len(o.data.vertices),'mats':[m.name for m in o.data.materials if m]})
for n in bpy.context.scene.world.node_tree.nodes:
 result['world'].append({'name':n.name,'type':n.type})
(R/'finishing/scene-inventory.json').write_text(json.dumps(result,indent=2))
