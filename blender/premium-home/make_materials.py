"""Deterministic, original tileable PBR maps. No third-party textures."""
from pathlib import Path
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parent/'textures';R.mkdir(exist_ok=True)
rng=np.random.default_rng(37);N=1024
y,x=np.mgrid[0:N,0:N]/N

def noise(scale):
 a=rng.normal(size=(N,N));freq=np.fft.fftfreq(N)*N
 filt=np.exp(-(freq[:,None]**2+freq[None,:]**2)/(2*scale**2))
 z=np.fft.ifft2(np.fft.fft2(a)*filt).real
 return z/(z.std()*6)

def write(name,base,height,rough,strength):
 base=np.clip(base,0,1);Image.fromarray((base*255).astype('uint8'),'RGB').save(R/(name+'-color.png'))
 Image.fromarray((np.clip(rough,0,1)*255).astype('uint8'),'L').save(R/(name+'-rough.png'))
 dx=(np.roll(height,-1,1)-np.roll(height,1,1))*strength;dy=(np.roll(height,-1,0)-np.roll(height,1,0))*strength
 normals=np.stack((-dx,-dy,np.ones_like(dx)),2);normals/=np.linalg.norm(normals,axis=2)[:,:,None]
 Image.fromarray(((normals*.5+.5)*255).astype('uint8'),'RGB').save(R/(name+'-normal.png'))

def rgb(color,f):return np.array(color)[None,None,:]+f[:,:,None]
f=.035*noise(6)+.018*noise(75)+.01*noise(600)
write('plaster',rgb([.82,.8,.75],f),f,.78+noise(40)*.07,2)
warp=.13*np.sin(y*2*np.pi)+.05*np.sin(y*12*np.pi)+.09*noise(5)
grain=np.sin(2*np.pi*(x*90+warp*6))*.007+np.sin(2*np.pi*(x*260+warp*15))*.004
f=.055*noise(6)+grain+.016*noise(320)
write('oak',rgb([.49,.35,.22],f),f,.52+noise(12)*.12,2)
f=.05*noise(5)+.02*noise(40)+.015*noise(400)
vein=np.exp(-np.abs(np.sin((y*5+x*.6+noise(7)*.14)*np.pi))*38)
f-=vein*.07
write('travertine',rgb([.72,.66,.55],f),f,.58+noise(30)*.06,1.3)
f=.04*noise(6)+.015*noise(130)
write('limestone',rgb([.73,.7,.63],f),f,.64+noise(40)*.1,1.5)
weave=.014*(np.cos(x*np.pi*512)+np.cos(y*np.pi*512))+.012*noise(512)
write('linen',rgb([.8,.77,.7],weave),weave,.92+noise(150)*.04,8)
f=.035*noise(170)+.025*noise(500)
write('rug',rgb([.6,.55,.46],f),f,.98+f*.05,12)
print('Created six original PBR material sets, 18 maps.')
