import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {buildTourGraph,shortestRoute,measureRoute,sampleRoute,redirectRoute} from '../src/lib/tourRoutes.js';
const home=JSON.parse(fs.readFileSync(new URL('../src/data/premiumHome.json',import.meta.url)));
const graph=buildTourGraph(home.paths);
test('every room pair follows connected audited edges',()=>{
 for(const a of Object.values(home.views)) for(const b of Object.values(home.views)){
  const points=shortestRoute(graph,a.position,b.position);
  assert.deepEqual(points[0],a.position);assert.deepEqual(points.at(-1),b.position);
  for(let i=1;i<points.length;i++) assert.ok(graph.nodes.get(graph.key(points[i-1])).edges.has(graph.key(points[i])));
 }
});
test('repeated travel interruptions preserve current position and arrive at target',()=>{
 let route=measureRoute(shortestRoute(graph,home.views.exterior.position,home.views.living.position));
 for(let i=0;i<120;i++){
  const target=Object.values(home.views)[i%12].position;
  const d=route.total*.37;const current=sampleRoute(route,d).point;
  route=redirectRoute(graph,route,d,target);
  assert.deepEqual(route.points[0],current);
  assert.deepEqual(sampleRoute(route,route.total).point,target);
  assert.ok(Number.isFinite(route.total));
 }
});
test('stationary route remains stable',()=>{
 const p=home.views.living.position;
 assert.deepEqual(sampleRoute(measureRoute([p]),999).point,p);
});
