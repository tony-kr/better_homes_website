"""Paint the golden-hour sky for each hero shot, in that camera's own view.

    python3 paint_hero_sky.py            # every shot in hero-shots.json
    python3 paint_hero_sky.py desktop

Each pixel's ray is traced from the camera in hero-shots.json. The sky colour
comes from the ray's elevation and its angle to the sun; the clouds come from
where the ray meets a flat cloud deck two kilometres up, so they shrink and
bunch toward the horizon the way real cloud does. render_hero.py maps the
result onto a dome through the same camera, which is what lets the reflecting
pool mirror the same sunset the camera sees.

Writes runtime/hero-sky-<shot>.png.
"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
CFG = json.loads((ROOT / 'hero-shots.json').read_text())
rng = np.random.default_rng(2026)


def fbm_tile(n=2048, octaves=((6, 1.0), (14, .5), (34, .26), (80, .12), (190, .05))):
    """Tileable fractal noise: FFT-filtered white noise, several bands."""
    f = np.fft.fftfreq(n) * n
    r = np.sqrt(f[:, None] ** 2 + f[None, :] ** 2)
    out = np.zeros((n, n))
    for freq, amp in octaves:
        white = np.fft.fft2(rng.normal(size=(n, n)))
        band = np.exp(-((r - freq) ** 2) / (2 * (freq * .35) ** 2))
        z = np.fft.ifft2(white * band).real
        out += amp * z / z.std()
    return out / out.std()


NOISE = fbm_tile()
NOISE2 = fbm_tile(octaves=((3, 1.0), (7, .5)))


def sample(tex, u, v):
    """Bilinear, wrapping lookup; u, v in tile units."""
    n = tex.shape[0]
    x = (u % 1.0) * n
    y = (v % 1.0) * n
    x0 = np.floor(x).astype(int)
    y0 = np.floor(y).astype(int)
    fx, fy = x - x0, y - y0
    x1, y1 = (x0 + 1) % n, (y0 + 1) % n
    x0, y0 = x0 % n, y0 % n
    a = tex[y0, x0] * (1 - fx) + tex[y0, x1] * fx
    b = tex[y1, x0] * (1 - fx) + tex[y1, x1] * fx
    return a * (1 - fy) + b * fy


def smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def mix(a, b, t):
    return a * (1 - t[..., None]) + b * t[..., None]


def rays(shot):
    W, H = shot['res']
    pos = np.array(shot['pos'], float)
    f = np.array(shot['target'], float) - pos
    f /= np.linalg.norm(f)
    r = np.cross(f, [0, 0, 1.0])
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    # Blender, sensor fit AUTO on a 36 mm sensor: the larger side gets it
    half = 18.0 / shot['lens']
    if W >= H:
        tx, ty = half, half * H / W
    else:
        tx, ty = half * W / H, half
    i = (np.arange(W) + .5) / W * 2 - 1
    j = 1 - (np.arange(H) + .5) / H * 2
    X, Y = np.meshgrid(i * tx, j * ty)
    d = X[..., None] * r + Y[..., None] * u + f
    return d / np.linalg.norm(d, axis=-1, keepdims=True)


def paint(key, shot):
    W, H = shot['res']
    d = rays(shot)
    el = np.arcsin(np.clip(d[..., 2], -1, 1))
    eld = np.degrees(el)
    az = np.radians(CFG['sun']['azimuthDeg'])
    se = np.radians(CFG['sun']['elevationDeg'])
    sun = np.array([np.cos(se) * np.sin(az), -np.cos(se) * np.cos(az), np.sin(se)])
    cos_sun = d @ sun

    # ------------------------------------------------------- sky gradient
    # Warm horizon under a rose band, cooling to dusk blue overhead. The sun
    # is behind the camera, so the glow is broad and soft, not a hot spot.
    stops = [(-2, (1.00, .80, .60)), (0, (1.00, .80, .60)), (3, (.99, .72, .56)),
             (9, (.93, .63, .56)), (18, (.70, .60, .66)), (30, (.45, .50, .66)), (55, (.26, .34, .52))]
    col = np.zeros((H, W, 3))
    for (e0, c0), (e1, c1) in zip(stops, stops[1:]):
        t = np.clip((eld - e0) / (e1 - e0), 0, 1)
        inside = (eld >= e0) & (eld < e1)
        col[inside] = (np.array(c0) * (1 - t[inside, None]) + np.array(c1) * t[inside, None])
    col[eld >= stops[-1][0]] = stops[-1][1]
    col[eld < stops[0][0]] = stops[0][1]
    # a little warmth leaks round from the sun side
    col += np.array([.05, .025, 0]) * smooth(-.6, .4, cos_sun)[..., None]

    # -------------------------------------------------------------- clouds
    # Where the ray meets the deck at 2 km, in km. Stretched along one axis
    # so the field reads as long evening stratocumulus, not cotton wool.
    h = 2.0
    up = np.maximum(d[..., 2], .004)
    px = d[..., 0] / up * h
    py = d[..., 1] / up * h
    rot = np.radians(24)
    cu = (px * np.cos(rot) - py * np.sin(rot)) / 38.0
    cv = (px * np.sin(rot) + py * np.cos(rot)) / 13.0
    warp = sample(NOISE2, cu * .5 + .3, cv * .5 + .7) * .08
    n = sample(NOISE, cu + warp, cv - warp)
    coverage = sample(NOISE2, cu * .35, cv * .35) * .5 + .15
    dens = smooth(.25 - coverage, 1.25 - coverage, n)
    # thickness toward the horizon, fade into haze right at it
    dens *= smooth(.4, 5.0, eld) * (1 - smooth(30, 62, eld) * .75)
    # light: sunlit undersides go peach and gold; thick cores go dusky rose
    lit = np.array([1.00, .74, .52])
    gold = np.array([1.00, .84, .58])
    core = np.array([.58, .45, .50])
    rim = sample(NOISE, cu * 2.1 + .5, cv * 2.1)
    cloud = mix(lit, gold, smooth(-.4, 1.2, rim))
    cloud = mix(cloud, core, smooth(.55, 1.0, dens) * .55)
    # higher clouds are further from the warm horizon light
    cloud = mix(cloud, np.array([.80, .66, .70]), smooth(12, 40, eld) * .45)
    col = mix(col, cloud, dens * .92)

    # -------------------------------------------------- horizon treeline
    # A low line of distant trees, hazed by the air between. It also hides
    # where the render's lawn stops.
    azv = np.arctan2(d[..., 0], d[..., 1])
    # rounded crowns, not spikes: sum of soft bumps at two scales
    ridge = .22 + .22 * sample(NOISE2, azv * 2.3, .2) + .18 * smooth(-.2, .9, sample(NOISE2, azv * 11.0, .6))
    ridge += .12 * smooth(-.4, 1.0, sample(NOISE2, azv * 31.0, .1))
    ridge += .35 * smooth(.6, 1.0, sample(NOISE2, azv * 5.0, .45))
    tree = smooth(ridge + .04, ridge - .04, eld)
    haze = np.array([.74, .60, .56])
    col = mix(col, haze, tree * .85)
    col = mix(col, np.array([.98, .78, .62]), smooth(1.4, -.1, eld) * (1 - tree) * .35)

    # dither so gradients survive 8-bit and the web encoder
    col += rng.normal(0, .004, col.shape)
    img = Image.fromarray((np.clip(col, 0, 1) ** (1 / 1.0) * 255).astype('uint8'), 'RGB')
    out = ROOT / 'runtime' / f'hero-sky-{key}.png'
    img.save(out)
    print('SKY', key, out)


only = sys.argv[1:] or list(CFG['shots'])
for key in only:
    paint(key, CFG['shots'][key])
