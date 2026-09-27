import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];F=R/'finishing'
def fingerprint(o):
 data={'matrix':[list(row) for row in o.matrix_world]}
 if o.type=='MESH':data['verts']=[list(v.co) for v in o.data.vertices];data['faces']=[list(p.vertices) for p in o.data.polygons]
 if o.type=='CAMERA':data['lens']=o.data.lens
 return hashlib.sha256(json.dumps(data).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(R/'premium-interior.blend'))
sourceTris=0
deps=bpy.context.evaluated_depsgraph_get()
for o in bpy.context.scene.objects:
 if o.type not in ('MESH','CURVE') or o.hide_render:continue
 e=o.evaluated_get(deps);m=e.to_mesh();m.calc_loop_triangles();sourceTris+=len(m.loop_triangles);e.to_mesh_clear()
original={o.name:fingerprint(o) for o in bpy.context.scene.objects if o.get('layer')=='wall' or o.type=='CAMERA' or o.name.startswith(('Tailored chair','Chair oak','Chair turned','Reveal','Opening lintel','Continuous ceiling'))}
bpy.ops.wm.open_mainfile(filepath=str(F/'natural-interior.blend'))
changed=[n for n,h in original.items() if n not in bpy.data.objects or fingerprint(bpy.data.objects[n])!=h]
deps=bpy.context.evaluated_depsgraph_get();tris=0
for o in bpy.context.scene.objects:
 if o.type not in ('MESH','CURVE') or o.hide_render:continue
 e=o.evaluated_get(deps);m=e.to_mesh();m.calc_loop_triangles();tris+=len(m.loop_triangles);e.to_mesh_clear()
base=json.loads((F/'website-baseline.json').read_text())
websiteChanged=[p for p,h in base.items() if hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h]
report={'protectedObjectsChecked':len(original),'changedWallsCamerasDiningChairs':changed,'websiteFilesChecked':len(base),'changedWebsiteFiles':websiteChanged,'sourceTriangles':sourceTris,'evaluatedTriangles':tris,'triangleDelta':tris-sourceTris,'sourceSha256':hashlib.sha256((R/'premium-interior.blend').read_bytes()).hexdigest(),'candidateSha256':hashlib.sha256((F/'natural-interior.blend').read_bytes()).hexdigest(),'scope':'Blender finishing candidate, not exported or installed','formApproval':'pending'}
(F/'audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
assert not changed and not websiteChanged
