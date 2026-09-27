from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parent
load=lambda n:json.loads((R/n).read_text())
def save(n,d):(R/n).write_text(json.dumps(d,indent=2)+'\n')
g=load('geometry-audit.json');s=load('shell-audit.json')
f=load('final-report.json')
f['gates'].update(function=True,form=False,runtime=False)
f['formChecks'].update(manifold=s['allWallsManifold'],booleans=s['allApertureCentersClear'],camera=not g['routeFailures'],ceilingCoverage=True,provenance=True)
f['reviewRenders']['corners']=[f'renders/checks/corner-{x}.png' for x in ['sw','se','ne','nw']]
f['reviewRenders']['ceiling']=[f'renders/checks/{x}.png' for x in ['ceiling-up','ceiling-oblique-a','ceiling-oblique-b']]
f['postmortem']['corrections']=['Moved kitchen cabinets clear of entry.','Moved guest shower farther from doorway.','Moved ensuite vanity to east wall and remounted vanity lighting.','Removed visible daylight emitters from glass reflections.','Moved plant out of living camera foreground.','Added terrace table pedestals and corrected shelf intersections.','Replaced block garment placeholders with draped shirt silhouettes.']
f['postmortem']['remainingRisks']=['Human Form approval pending.','Exhaustive prop contact/intersection and full-shell light-leak audits are not certified by these focused checks.','GLB export, draw-call optimization, texture tiers, baked lighting and browser runtime parity remain.','The bundled validator assumes paid Meshy assets; this native Blender workflow uses none.']
f['nativeBlenderEvidence']={'source':'premium-interior.blend','sha256':hashlib.sha256((R/'premium-interior.blend').read_bytes()).hexdigest(),'geometryAudit':'geometry-audit.json','shellAudit':'shell-audit.json','navigationRoutes':'navigation-routes.json','materials':'textures','review':'interior-review.html'}
save('final-report.json',f)
v=load('milestone-reviews.json');v['form'].update(status='pending',approvedBy='',approvedAt='',evidence=['interior-review.html','premium-interior.blend','geometry-audit.json','shell-audit.json']+f['reviewRenders']['corners']+f['reviewRenders']['ceiling'],strangestElement='Sparse planting and some procedural furnishing still read as CGI; the actual website must preserve texture and lighting quality rather than revert to flat materials.',notes='Detailed native Blender interior rendered and inspected. Awaiting user visual approval before runtime export.');save('milestone-reviews.json',v)
manifest=[]
for p in sorted((R/'textures').glob('*.png')):manifest.append(dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),provenance='Original deterministic map from make_materials.py; no external assets'))
save('material-provenance.json',{'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'maps':manifest})
print('Updated pending Form review with measured evidence; runtime remains incomplete.')
