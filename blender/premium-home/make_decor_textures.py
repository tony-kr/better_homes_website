"""Original texture sets for the wall-dressing pass. No third-party images.

    python3 make_decor_textures.py

Writes PBR sets (color / rough / normal) for fluted oak, book-matched marble,
walnut and glazed ceramic, plus six framed artworks, into textures/.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

R = Path(__file__).resolve().parent / 'textures'
R.mkdir(exist_ok=True)
rng = np.random.default_rng(91)
N = 1024
y, x = np.mgrid[0:N, 0:N] / N


def noise(scale, n=N):
    a = rng.normal(size=(n, n))
    f = np.fft.fftfreq(n) * n
    filt = np.exp(-(f[:, None] ** 2 + f[None, :] ** 2) / (2 * scale ** 2))
    z = np.fft.ifft2(np.fft.fft2(a) * filt).real
    return z / (z.std() * 6)


def write(name, base, height, rough, strength):
    base = np.clip(base, 0, 1)
    Image.fromarray((base * 255).astype('uint8'), 'RGB').save(R / f'{name}-color.png')
    Image.fromarray((np.clip(rough, 0, 1) * 255).astype('uint8'), 'L').save(R / f'{name}-rough.png')
    dx = (np.roll(height, -1, 1) - np.roll(height, 1, 1)) * strength
    dy = (np.roll(height, -1, 0) - np.roll(height, 1, 0)) * strength
    n = np.stack((-dx, -dy, np.ones_like(dx)), 2)
    n /= np.linalg.norm(n, axis=2)[:, :, None]
    Image.fromarray(((n * .5 + .5) * 255).astype('uint8'), 'RGB').save(R / f'{name}-normal.png')


def rgb(c, f):
    return np.array(c)[None, None, :] + f[:, :, None]


# ------------------------------------------------------------ fluted oak
# One tile = 0.6 m, 16 flutes of 37.5 mm. The groove shading is painted into
# the albedo because the web lightmap is far too coarse to resolve it.
flutes = 16
u = (x * flutes) % 1.0
profile = np.sqrt(np.clip(1 - (2 * u - 1) ** 2, 0, 1))          # rounded reed
groove = np.exp(-((u - 0) ** 2) / .0012) + np.exp(-((u - 1) ** 2) / .0012)
warp = .1 * np.sin(x * 2 * np.pi * 3) + .08 * noise(5)
grain = np.sin(2 * np.pi * (y * 70 + warp * 5)) * .012 + np.sin(2 * np.pi * (y * 210 + warp * 11)) * .006
tone = .045 * noise(4) + grain + .012 * noise(300)
shade = .80 + .20 * profile - .30 * groove
base = rgb([.66, .50, .34], tone) * shade[:, :, None]
write('fluted-oak', base, profile * .6 + tone, .55 + noise(20) * .08, 3.2)

# ---------------------------------------------------------- walnut
warp = .14 * np.sin(y * 2 * np.pi) + .06 * np.sin(y * 9 * np.pi) + .1 * noise(5)
grain = np.sin(2 * np.pi * (x * 70 + warp * 7)) * .018 + np.sin(2 * np.pi * (x * 240 + warp * 16)) * .007
f = .05 * noise(6) + grain + .012 * noise(320)
write('walnut', rgb([.27, .17, .11], f), f, .42 + noise(12) * .08, 2)

# --------------------------------------------------------- marble slab
# Warm Calacatta: cream ground, soft grey-gold veins, mirrored down the
# centre line so a slab reads as book-matched.
half = N // 2
yy, xx = np.mgrid[0:N, 0:half] / N
# Distance along a diagonal, warped by fractal noise, gives long veins that
# wander without closing into loops.
warp = noise(2)[:, :half] * .45 + noise(7)[:, :half] * .14 + noise(40)[:, :half] * .035
d = (xx * .8 + yy * 1.6 + warp) * 2.2
v1 = np.abs(((d + .5) % 1.0) - .5)
d2 = (xx * 2.0 - yy * .7 + warp * 1.4) * 3.1
v2 = np.abs(((d2 + .5) % 1.0) - .5)
vein = np.exp(-(v1 / .012) ** 2) * .8 + np.exp(-(v1 / .06) ** 2) * .18 + np.exp(-(v2 / .006) ** 2) * .35
ground = rgb([.90, .87, .81], .03 * noise(5)[:, :half] + .01 * noise(200)[:, :half])
vc = np.array([.52, .47, .40])[None, None, :]
gold = np.array([.70, .58, .40])[None, None, :]
mix = np.clip(noise(4)[:, :half] * 4 + .5, 0, 1)[:, :, None]
vein_col = vc * (1 - mix) + gold * mix
left = ground * (1 - vein[:, :, None]) + vein_col * vein[:, :, None]
slab = np.concatenate([left, left[:, ::-1]], 1)
h = np.concatenate([vein, vein[:, ::-1]], 1) * -.05
write('marble', slab, h, .18 + np.concatenate([vein, vein[:, ::-1]], 1) * .08, 1)

# ------------------------------------------------------- glazed ceramic
speck = (rng.random((N, N)) > .996).astype(float)
speck = np.array(Image.fromarray((speck * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.1))) / 255
f = .03 * noise(8) + .015 * noise(60) - speck * .18
col = rgb([.80, .76, .68], f)
write('ceramic', col, f, .28 + noise(30) * .06 + speck * .5, 1.5)
f = .04 * noise(8) + .02 * noise(80) - speck * .1
write('ceramic-dark', rgb([.16, .14, .12], f), f, .38 + noise(30) * .06, 1.5)


# ------------------------------------------------------------ artworks
def paper(w, h, tint=(236, 229, 216), seed=0):
    g = np.random.default_rng(seed)
    base = np.ones((h, w, 3)) * np.array(tint)[None, None, :]
    n = g.normal(0, 3.2, (h, w))[:, :, None]
    im = Image.fromarray(np.clip(base + n, 0, 255).astype('uint8'), 'RGB')
    return im


def brushy(im, seed):
    """Break flat fills with a faint pigment texture so shapes read as painted."""
    g = np.random.default_rng(seed)
    a = np.asarray(im).astype(float)
    t = g.normal(0, 1, a.shape[:2])
    t = np.asarray(Image.fromarray(((t * 20) + 128).clip(0, 255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.6))).astype(float) - 128
    a += t[:, :, None] * .35
    return Image.fromarray(a.clip(0, 255).astype('uint8'))


W, H = 1200, 1500

# 1. Arches: terracotta arch, sand disc, charcoal line on warm paper
im = paper(W, H, seed=1)
d = ImageDraw.Draw(im)
d.rectangle([220, 520, 760, 1300], fill=(176, 92, 58))
d.ellipse([220, 250, 760, 790], fill=(176, 92, 58))
d.ellipse([560, 330, 980, 750], fill=(214, 186, 140))
d.rectangle([640, 900, 980, 1300], fill=(92, 104, 86))
d.line([(140, 1300), (1060, 1300)], fill=(40, 36, 32), width=6)
brushy(im, 1).save(R / 'art-arches.png')

# 2. Enso: a single gestural charcoal ring on off-white
im = paper(W, H, tint=(240, 236, 228), seed=2)
a = np.asarray(im).astype(float)
yy, xx = np.mgrid[0:H, 0:W]
cx, cy, rr = W / 2, H / 2 - 40, 360
ang = np.arctan2(yy - cy, xx - cx)
dist = np.hypot(xx - cx, yy - cy)
t = ((ang + np.pi * .72) % (2 * np.pi)) / (2 * np.pi)
width = 70 * (1 - t) ** .6 + 6
dry = np.random.default_rng(3).random((H, W)) < (.25 + t * .6)
ink = (np.abs(dist - rr - 12 * np.sin(ang * 3)) < width / 2) & (t < .93) & ~(dry & (np.random.default_rng(4).random((H, W)) < t * .7))
a[ink] = a[ink] * .1 + np.array([28, 26, 24]) * .9
im = Image.fromarray(a.clip(0, 255).astype('uint8')).filter(ImageFilter.GaussianBlur(.8))
d = ImageDraw.Draw(im)
d.rectangle([W - 190, H - 220, W - 150, H - 180], fill=(170, 40, 30))
im.save(R / 'art-enso.png')

# 3. Colour field in ochre and rust, soft edges
im = paper(W, H, tint=(222, 206, 180), seed=5)
layer = Image.new('RGB', (W, H), (0, 0, 0))
mask = Image.new('L', (W, H), 0)
for box, col in (((130, 150, 1070, 760), (196, 132, 64)), ((130, 820, 1070, 1350), (122, 58, 38))):
    m = Image.new('L', (W, H), 0)
    ImageDraw.Draw(m).rectangle(box, fill=235)
    m = m.filter(ImageFilter.GaussianBlur(18))
    im = Image.composite(Image.new('RGB', (W, H), col), im, m)
brushy(im, 6).save(R / 'art-field.png')

# 4. Horizon: sage ground, sand sky, low sun
im = paper(W, H, tint=(230, 219, 198), seed=7)
d = ImageDraw.Draw(im)
d.ellipse([430, 520, 770, 860], fill=(206, 146, 96))
d.rectangle([0, 820, W, H], fill=(128, 138, 112))
d.rectangle([0, 1080, W, H], fill=(86, 98, 78))
for i in range(9):
    yv = 870 + i * 22
    d.line([(90 + i * 14, yv), (W - 90 - i * 30, yv)], fill=(146, 154, 128), width=2)
brushy(im, 8).save(R / 'art-horizon.png')

# 5. Botanical: olive leaf silhouettes on cream
im = paper(W, H, tint=(238, 232, 220), seed=9)
d = ImageDraw.Draw(im)
g = np.random.default_rng(10)
stem = [(600 + 60 * np.sin(t / 180), 1350 - t) for t in range(0, 1100, 10)]
d.line(stem, fill=(70, 78, 56), width=7)
for i in range(22):
    px, py = stem[int(i * 4.8) + 4]
    side = 1 if i % 2 else -1
    L = 170 - i * 3
    ang = np.radians(35 + g.random() * 20) * side
    tip = (px + np.sin(ang) * L, py - np.cos(ang) * L)
    nx, ny = -(tip[1] - py) / L * 26, (tip[0] - px) / L * 26
    mid = ((px + tip[0]) / 2, (py + tip[1]) / 2)
    d.polygon([(px, py), (mid[0] + nx, mid[1] + ny), tip, (mid[0] - nx, mid[1] - ny)],
              fill=(78 + int(g.random() * 30), 92 + int(g.random() * 26), 62))
brushy(im, 11).save(R / 'art-botanical.png')

# 6. Stacked forms: stone-balance composition, landscape format
W2, H2 = 1600, 1100
im = paper(W2, H2, tint=(226, 214, 196), seed=12)
d = ImageDraw.Draw(im)
d.rectangle([0, 0, W2 // 2, H2], fill=(212, 196, 172))
d.ellipse([520, 640, 1080, 900], fill=(58, 54, 50))
d.ellipse([610, 430, 990, 660], fill=(176, 108, 70))
d.ellipse([690, 270, 910, 450], fill=(236, 226, 208))
d.line([(200, 900), (1400, 900)], fill=(58, 54, 50), width=4)
brushy(im, 13).save(R / 'art-stones.png')

print('decor textures written to', R)


# =================================================== reference redesign
# Client round 4 (September 2026): the rooms are redesigned after the
# client's interior references: walnut slat walls, jute, boucle, travertine,
# and collage artwork in sand, umber and black.
rng = np.random.default_rng(404)

# Walnut slats: 16 slats per 0.6 m tile (37.5 mm), each slat a flat face with
# softened arrises and a deep dark gap, grain running up the slat.
u = (x * 16) % 1.0
gap = (u < 0.16).astype(float)
edge = np.exp(-((u - 0.16) ** 2) / 0.0009) + np.exp(-((u - 1.0) ** 2) / 0.0009)
slat_id = np.floor(x * 16)
tint = (np.sin(slat_id * 12.9898) * 43758.5453) % 1.0  # per-slat tone variation
warp = .06 * noise(5) + .03 * np.sin(x * 2 * np.pi * 16)
grain = np.sin(2 * np.pi * (y * 55 + warp * 5)) * .02 + np.sin(2 * np.pi * (y * 160 + warp * 13)) * .01
tone = .03 * noise(6) + grain + (tint[:, :] - .5) * .05
col = rgb([.36, .22, .13], tone)
col = col * (1 - gap[:, :, None] * .78) * (1 - edge[:, :, None] * .18)
height = (1 - gap) * .8 - edge * .2 + tone * .3
write('walnut-slat', col, height, .5 + noise(20) * .06 + gap * .4, 3.5)

# Jute: a chunky basket weave in warm straw
n = N
wx = np.sin(x * np.pi * 2 * 40)
wy = np.sin(y * np.pi * 2 * 40)
cell = ((np.floor(x * 40) + np.floor(y * 40)) % 2).astype(float)
weave = np.where(cell > .5, np.abs(wx), np.abs(wy)) * .5 + .5 * np.abs(np.sin(y * np.pi * 2 * 192) * np.sin(x * np.pi * 2 * 192))
fiber = .05 * noise(250) + .03 * noise(40)
col = rgb([.7, .6, .45], (weave - .5) * .22 + fiber * 1.4)
write('jute', col, weave * .6 + fiber, .95 + fiber * .1, 6)

# Boucle: small loops, soft cream
loops = noise(420) * 2.2 + noise(160) * 1.2
loops = np.clip(loops, -1, 1)
col = rgb([.86, .82, .75], loops * .05)
write('boucle', col, loops * .5, np.full((N, N), .96), 7)

# Stone planter: coarse travertine, pitted
pits = (rng.random((N, N)) > .993).astype(float)
pits = np.array(Image.fromarray((pits * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.6))) / 255
f = .05 * noise(5) + .03 * noise(60) + .015 * noise(300) - pits * .25
write('stone', rgb([.78, .72, .62], f), f, .88 + noise(30) * .05, 2)

# Artwork, after the references: torn-paper collage in sand, umber, black
def collage(W, H, blocks, seed, tint=(236, 226, 208)):
    g = np.random.default_rng(seed)
    im = paper(W, H, tint=tint, seed=seed)
    for (x0, y0, x1, y1), c in blocks:
        m = Image.new('L', (W, H), 0)
        d = ImageDraw.Draw(m)
        # ragged torn edges: jitter each side
        pts = []
        for t in np.linspace(0, 1, 40): pts.append((x0 + (x1 - x0) * t, y0 + g.normal(0, 4)))
        for t in np.linspace(0, 1, 40): pts.append((x1 + g.normal(0, 4), y0 + (y1 - y0) * t))
        for t in np.linspace(1, 0, 40): pts.append((x0 + (x1 - x0) * t, y1 + g.normal(0, 4)))
        for t in np.linspace(1, 0, 40): pts.append((x0 + g.normal(0, 4), y0 + (y1 - y0) * t))
        d.polygon(pts, fill=255)
        m = m.filter(ImageFilter.GaussianBlur(1.2))
        layer = Image.new('RGB', (W, H), c)
        im = Image.composite(layer, im, m)
    return brushy(im, seed + 1)

collage(1400, 1400, [((260, 200, 700, 620), (214, 196, 168)), ((700, 200, 1140, 620), (196, 170, 132)),
                     ((260, 620, 620, 1180), (30, 28, 26)), ((620, 620, 1140, 1180), (226, 214, 192)),
                     ((820, 700, 1080, 900), (180, 150, 112))], 41).save(R / 'art-collage.png')
collage(1200, 1500, [((300, 260, 900, 1240), (221, 205, 180)), ((420, 700, 820, 1240), (122, 74, 44)),
                     ((520, 380, 880, 700), (200, 176, 140))], 43).save(R / 'art-organic.png')
collage(1500, 1200, [((200, 180, 760, 600), (214, 200, 176)), ((760, 180, 1300, 600), (176, 140, 100)),
                     ((200, 600, 760, 1020), (150, 70, 40)), ((760, 600, 1300, 1020), (226, 214, 192))], 47).save(R / 'art-blocks.png')
print('reference redesign textures written')
