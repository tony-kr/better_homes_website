from pathlib import Path
import json,struct,io,hashlib
from PIL import Image
R=Path(__file__).resolve().parent;P=R.parent.parent/'public/models';P.mkdir(exist_ok=True)
raw=(R/'runtime/premium-home.glb').read_bytes();jl,jt=struct.unpack_from('<II',raw,12);doc=json.loads(raw[20:20+jl]);off=20+jl;bl,bt=struct.unpack_from('<II',raw,off);binary=raw[off+8:off+8+bl]
assert all('TEXCOORD_1' in p['attributes'] for m in doc['meshes'] if m['name']=='PremiumHome_Opaque' for p in m['primitives'])
normal_ids={doc['textures'][m['normalTexture']['index']]['source'] for m in doc['materials'] if 'normalTexture' in m}
replace={}
for i,im in enumerate(doc.get('images',[])):
 bv=doc['bufferViews'][im['bufferView']];start=bv.get('byteOffset',0);pic=Image.open(io.BytesIO(binary[start:start+bv['byteLength']]));out=io.BytesIO()
 pic.save(out,format='WEBP',lossless=i in normal_ids,quality=93,method=6);replace[im['bufferView']]=out.getvalue();im['mimeType']='image/webp'
for t in doc.get('textures',[]):
 t.setdefault('extensions',{})['EXT_texture_webp']={'source':t.pop('source')}
for field in ('extensionsUsed','extensionsRequired'):
 doc.setdefault(field,[])
 if 'EXT_texture_webp' not in doc[field]:doc[field].append('EXT_texture_webp')
chunks=[];offset=0
for i,bv in enumerate(doc['bufferViews']):
 start=bv.get('byteOffset',0);data=replace.get(i,binary[start:start+bv['byteLength']]);bv['byteOffset']=offset;bv['byteLength']=len(data);data+=b'\x00'*((-len(data))%4);chunks.append(data);offset+=len(data)
binary=b''.join(chunks);doc['buffers'][0]['byteLength']=len(binary);j=json.dumps(doc,separators=(',',':')).encode();j+=b' '*((-len(j))%4)
result=struct.pack('<III',0x46546c67,2,12+8+len(j)+8+len(binary))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(binary),0x004e4942)+binary
(P/'premium-home.glb').write_bytes(result)
light=Image.open(R/'runtime/home-lightmap.png').convert('RGB')
light.save(P/'home-lightmap.webp',format='WEBP',quality=96,method=6)
light.resize((2048,2048),Image.Resampling.LANCZOS).save(P/'home-lightmap-mobile.webp',format='WEBP',quality=94,method=6)
for name in ('living','dining','kitchen','bedroom','guest','study','bathroom','ensuite','dressing','utility','patio'):
 Image.open(R/'renders/interiors'/f'{name}.png').resize((1120,720)).save(P/f'{name}-preview.webp',quality=88,method=6)
report={'modelBytes':len(result),'meshCount':len(doc['meshes']),'primitiveCount':sum(len(m['primitives']) for m in doc['meshes']),'materialCount':len(doc['materials']),'textureImages':len(doc.get('images',[])),'uv1Verified':True,'lightmapPixels':list(light.size),'modelSha256':hashlib.sha256(result).hexdigest(),'sourceSha256':hashlib.sha256((R/'premium-interior.blend').read_bytes()).hexdigest(),'lightmapSha256':hashlib.sha256((P/'home-lightmap.webp').read_bytes()).hexdigest()}
(R/'runtime/export-report.json').write_text(json.dumps(report,indent=2));print(report)
