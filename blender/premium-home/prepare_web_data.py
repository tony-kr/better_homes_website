from pathlib import Path
import json,math
R=Path(__file__).resolve().parent;PROJECT=R.parent.parent
routes=json.loads((R/'navigation-routes.json').read_text());cams=json.loads((R/'interior-cameras.json').read_text())
assert not routes['failures']
to3=lambda p:[round(p[0],4),round(p[2],4),round(-p[1],4)]
paths={id:[to3(p) for p in r['points']] for id,r in routes['routes'].items()}
hub=paths['living'][0]
paths['exterior']=[hub,to3([-.5,7,1.6]),to3([-3,7,1.6]),to3([-3,-7,3]),to3([26,-14,8])]
data={'model':'/models/premium-home.glb','lightmap':'/models/home-lightmap.webp','mobileLightmap':'/models/home-lightmap-mobile.webp','units':'meters','paths':paths,'views':{}}
for id,c in cams.items():data['views'][id]={'position':paths[id][-1],'target':to3(c['target']),'fov':round(math.degrees(2*math.atan(36/(2*c['lens']*(1400/900)))),2)}
data['views']['exterior']={'position':paths['exterior'][-1],'target':to3([9,3,1.4]),'fov':42}
(PROJECT/'src/data/premiumHome.json').write_text(json.dumps(data,separators=(',',':')))
print('Wrote runtime route graph and camera contract')
