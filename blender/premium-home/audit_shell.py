import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'premium-interior.blend'))
deps=bpy.context.evaluated_depsgraph_get();results=[];trees={}
for o in bpy.context.scene.objects:
 if o.get('layer')!='wall':continue
 eo=o.evaluated_get(deps);me=eo.to_mesh();bm=bmesh.new();bm.from_mesh(me)
 results.append(dict(wall=o.name,nonManifoldEdges=sum(not e.is_manifold for e in bm.edges),volumeCubicMeters=bm.calc_volume(signed=True)))
 trees[o.name]=BVHTree.FromPolygons([o.matrix_world@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons]);bm.free();eo.to_mesh_clear()
openings=[]
for a in json.loads((R/'openings.json').read_text())['openings']:
 x,y=a['location'];z=a['sillMeters']+a['heightMeters']/2;axis=Vector((0,1,0)) if a['axis']=='x' else Vector((1,0,0));center=Vector((x,y,z));hit=trees[a['wall']].ray_cast(center-axis*.5,axis,1)
 openings.append(dict(id=a['id'],centerApertureClear=hit[0] is None))
(R/'shell-audit.json').write_text(json.dumps(dict(walls=results,apertures=openings,allWallsManifold=all(r['nonManifoldEdges']==0 for r in results),allApertureCentersClear=all(r['centerApertureClear'] for r in openings),limitations='Checks wall meshes and aperture centers; not an exhaustive whole-shell leak or prop-intersection proof.'),indent=2))
print('Shell audit complete')
