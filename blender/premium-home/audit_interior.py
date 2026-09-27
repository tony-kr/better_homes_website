"""Geometry-derived camera routes and honest form review evidence."""
import bpy,json,math,heapq,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'premium-interior.blend'))
scene=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
walls=[];obstacles=[];tris=0;meshcount=0;no_uv=[]
for o in scene.objects:
 if o.type not in ('MESH','CURVE') or o.hide_render:continue
 eo=o.evaluated_get(deps);me=eo.to_mesh();me.calc_loop_triangles();tris+=len(me.loop_triangles);meshcount+=1
 if o.type=='MESH' and not me.uv_layers:no_uv.append(o.name)
 vs=[o.matrix_world@v.co for v in me.vertices]
 if not vs:eo.to_mesh_clear();continue
 lo=[min(v[k] for v in vs) for k in range(3)];hi=[max(v[k] for v in vs) for k in range(3)]
 if o.get('layer')=='wall':
  tree=BVHTree.FromPolygons(vs,[list(p.vertices) for p in me.polygons]);walls.append((lo,hi,tree))
 elif hi[2]>.28 and lo[2]<1.82 and not any(o.name.startswith(p) for p in ('Landscape','Garden perimeter','South garden','North garden')):
  obstacles.append((lo,hi,o.name))
 eo.to_mesh_clear()
print('Geometry measured',meshcount,tris,flush=True)
# Camera capsule approximation: conservative furniture AABBs and exact evaluated
# Boolean wall surfaces, at three body heights. No flight through closed partitions.
radius=.19

def inside(tree,p):
 direction=Vector((1,.317,.073)).normalized();origin=p.copy();n=0
 for _ in range(30):
  hit,normal,index,dist=tree.ray_cast(origin,direction,80)
  if hit is None:break
  n+=1;origin=hit+direction*.0001
 return n%2==1

def free(x,y):
 if not (.25<x<19.75 and -3.75<y<13.75):return False
 for lo,hi,name in obstacles:
  if lo[0]-radius<x<hi[0]+radius and lo[1]-radius<y<hi[1]+radius:return False
 for lo,hi,tree in walls:
  if not(lo[0]-radius<x<hi[0]+radius and lo[1]-radius<y<hi[1]+radius):continue
  for z in (.5,1.2,1.7):
   p=Vector((x,y,z));nearest=tree.find_nearest(p)
   if nearest[0] is not None and nearest[3]<radius:return False
   if inside(tree,p):return False
 return True
step=.15
cache={}
def clear(n):
 if n not in cache:cache[n]=free(n[0]*step,n[1]*step)
 return cache[n]
def nearest(pos):
 n=(round(pos[0]/step),round(pos[1]/step))
 choices=sorted(((n[0]+dx,n[1]+dy) for dx in range(-1,2) for dy in range(-1,2)),key=lambda q:math.dist((q[0]*step,q[1]*step),pos[:2]))
 return next((q for q in choices if clear(q)),None)
def route(start,end):
 a=nearest(start);b=nearest(end)
 if a is None or b is None:return None
 q=[(0,a)];g={a:0};parent={};seen=set()
 while q:
  _,n=heapq.heappop(q)
  if n in seen:continue
  seen.add(n)
  if n==b:
   path=[n]
   while n!=a:n=parent[n];path.append(n)
   return [[p[0]*step,p[1]*step,1.6] for p in reversed(path)]
  for dx,dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
   v=(n[0]+dx,n[1]+dy)
   if not clear(v) or (dx and dy and (not clear((n[0]+dx,n[1])) or not clear((n[0],n[1]+dy)))):continue
   cost=g[n]+math.hypot(dx,dy)
   if cost<g.get(v,1e9):g[v]=cost;parent[v]=n;heapq.heappush(q,(cost+math.dist(v,b),v))
 return None
views=json.loads((R/'interior-cameras.json').read_text());routes={};failures=[]
for id,cam in views.items():
 path=route((1,7),cam['position'])
 if path is None:failures.append(id)
 routes[id]={'points':path,'requestedCamera':cam['position'],'endpointOffsetMeters':round(math.dist(path[-1],cam['position']),3) if path else None}
 print('Route',id,'OK' if path else 'FAILED',flush=True)
(R/'navigation-routes.json').write_text(json.dumps({'units':'meters','up':'Z','start':[1,7,1.6],'radiusMeters':radius,'gridStepMeters':step,'method':'A-star; evaluated Boolean wall BVH and conservative furniture bounds; not a runtime browser test','routes':routes,'failures':failures},indent=2))
(R/'geometry-audit.json').write_text(json.dumps({'meshAndCurveObjects':meshcount,'evaluatedTriangles':tris,'budgetTriangles':450000,'triangleBudgetPassed':tris<=450000,'meshesWithoutUV':no_uv,'pbrMapCount':len(list((R/'textures').glob('*.png'))),'routeFailures':failures,'notes':['Conservative furniture boxes can reject a physically feasible route.','This check does not replace visual review, full object-to-object BVH clearance, or browser verification.']},indent=2))
print('AUDIT COMPLETE',flush=True)
