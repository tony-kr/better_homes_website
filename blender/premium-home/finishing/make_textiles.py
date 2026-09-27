from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent/'textures';R.mkdir(exist_ok=True)
N=2048;rng=np.random.default_rng(271);y,x=np.mgrid[:N,:N]/N
def save(name,base,h,rough):
 Image.fromarray(np.uint8(np.clip(base,0,1)*255)).save(R/(name+'-color.png'))
 Image.fromarray(np.uint8(np.clip(rough,0,1)*255)).save(R/(name+'-rough.png'))
 dx=(np.roll(h,-1,1)-np.roll(h,1,1))*1.8;dy=(np.roll(h,-1,0)-np.roll(h,1,0))*1.8
 n=np.stack([-dx,-dy,np.ones_like(h)],2);n/=np.linalg.norm(n,axis=2)[:,:,None]
 Image.fromarray(np.uint8((n*.5+.5)*255)).save(R/(name+'-normal.png'))
for name,base,count in [('boucle',[.78,.75,.69],110),('linen',[.77,.74,.68],160),('jute',[.51,.43,.32],75)]:
 warp=np.sin(x*np.pi*2*count+.25*np.sin(y*80));weft=np.sin(y*np.pi*2*count+.22*np.sin(x*95))
 grain=rng.normal(0,.012,(N,N));h=.16*warp*.6+.16*weft*.4+grain
 if name=='boucle':h+=.065*np.cos(x*count*9+y*count*8)
 variation=h*.15+grain*.6
 save(name,np.array(base)[None,None,:]+variation[:,:,None],h,.82+h*.14)
print('Natural textile maps ready')
