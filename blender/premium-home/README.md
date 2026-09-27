# Premium home — detailed Blender interior

Layout and material direction were approved by the user on 2026-09-19 UTC ("proceeed with this"). Detailed Form review is the current stage; website export and runtime integration have not happened.

## Review

Serve this folder and open `interior-review.html` to switch between eleven rendered spaces. `review.html` preserves the original concept review. `premium-interior.blend` is the editable detailed source, with packed original texture maps. `concept.blend` preserves the initial layout.

Living, dining, kitchen, primary bedroom, guest bedroom, study, guest bathroom, ensuite, dressing, utility and garden terrace are modeled in one continuous home. The 20 × 14 m interior has a 2 m gallery and 19 Boolean wall apertures.

## Changes since approval

- Six original PBR material sets (18 albedo, roughness and normal maps), metre-scaled UVs, transparent glass and reflective mirrors.
- Detailed furniture, soft upholstery, modeled duvet folds, pleated curtains, framed openings, cabinet fronts and handles, kitchen equipment, shower fixtures, basins, books and wardrobe contents.
- An enclosed ceiling with mounted practical lights. Fixture manifest uses unique scene IDs.
- Kitchen entry kept clear by moving the cabinet run to the east wall.
- Guest shower moved away from its doorway. Ensuite vanity and its light fittings mounted on the east wall to preserve the north window.
- Geometry-derived navigation paths from the gallery into every space. These are a foundation for the website, not a claim that browser navigation is implemented.

## Reproduce

1. Run `make_materials.py` with Python, NumPy and Pillow.
2. Run Blender 5.0.1 in background mode with `--python build_interior.py`. The builder reads the approved concept builder but stops before the concept renderer, leaving approved records intact. Use `-- --only living,bedroom --draft` for limited drafts.
3. Run `audit_interior.py` and `audit_shell.py` through Blender for navigation, mesh and aperture evidence.
4. Run `render_final_review.py` through Blender for corrected hero views and ceiling/corner inspection renders.
5. Run `prepare_interior_review.py` with Python to assemble the review page.

The `fix_*.py` files are one-time repair history for the initial detailed build. Their changes are incorporated in `build_interior.py`; do not reapply them to a fresh build (the shower and plant repairs are positional).

## Validation and limits

`geometry-audit.json` records evaluated triangle count, UV coverage and room-route results. `shell-audit.json` records manifold walls and center ray checks through every scheduled aperture. Navigation uses a 0.19 m camera radius, exact evaluated wall BVHs and conservative furniture bounds. It does not replace runtime collision checks or certify every object-to-object contact.

Review images are Cycles renders. The browser will require texture tiers, merged/instanced meshes, fixture-matched lighting, tested camera transitions and mobile profiling to reproduce the design efficiently. No claim of completed lightmap baking or runtime parity is made.

The bundled skill validator hardcodes paid Meshy requirements. This project uses native Blender geometry and zero paid-generation credits; those unrelated checks are retained as reported failures rather than inventing paid task records. Human Form approval is still required before export. Runtime approval precedes deployment.

Existing website files and the original uncommitted user changes have been preserved.

## Web-facing rebuild (September 2026)

Three scripts own everything the website renders. Run them from this folder.

| script | makes | lands in |
| --- | --- | --- |
| `build_sky.py` | `sky/golden-sky.png` + `.exr` | `public/sky/golden-sky*.webp` |
| `build_exterior.py` | `runtime/exterior.glb` | `public/models/exterior.glb` |
| `rebake_lightmap.py` | clean baked atlas | `public/models/home-lightmap*.webp` |

**The sky** is painted rather than simulated. A physical atmosphere model kept
landing on pale blue; the gradient here is driven directly by the angle to the
sun, with a two-sample noise field for clouds that fakes self-shadowing by
sampling itself a second time offset toward the sun. `SKY_QUICK=1` renders at
1024x512 for iteration.

**The exterior** exists because the shipped model is interior-first: outside it
was a flat box on a dark plane. This adds a roof slab with overhang and fascia,
a timber soffit, glazing mullions over the front elevation, a stone plinth, the
terrace, a reflecting pool beyond the courtyard wall, planting, trees and lawn.
It is about 37 KB and carries no lightmap, since the sky lights it.

Coordinates matter here. three.js `(x, y, z)` is Blender `(x, -z, y)`. Measured
off the shipped mesh, in three.js space: the house mass is x 0..20, z -14..0
with the glazed front at z = 0, and a courtyard wall runs at z = -18, z = +8,
x = -9 and x = +29. Guessing these wrong puts the roof in the wrong place.

**The lightmap** was the cause of the graininess. It had been baked at 24-48
samples and then encoded as lossy WebP; path-tracer speckle is the worst
possible input for a lossy codec, so every wall came out mottled. Baking at 512
samples with OpenImageDenoise gives the encoder almost nothing to chew on, and
the q90 result is both sharper and smaller than the old q100 one.

| | old | new |
| --- | --- | --- |
| lightmap size | 2.74 MB | 1.39 MB |
| bits per pixel | 1.31 (of noise) | 0.66 (of clean) |
| bake samples | 24-48 | 512 + denoise |

## Client round 3 (September 2026)

The client found the walls plain and the landing not premium enough, with a
reference of a real-estate hero at golden hour. Everything below runs from this
folder, in this order. `BAKE_SAMPLES` overrides the bake quality in both
`export_web.py` (4 is enough there: `rebake_lightmap.py` replaces its bake) and
`rebake_lightmap.py` (1024 for release; the bedroom is lamp-lit and shows
denoiser blotches at 256).

| step | command | makes |
| --- | --- | --- |
| textures | `python3 make_decor_textures.py` | fluted oak, marble, walnut, ceramic, six artworks |
| dressing | `blender -b -P add_decor.py` | dresses `premium-interior.blend` (clean copy kept as `.pre-decor.blend`) |
| exterior | `blender -b -P build_exterior.py` | `runtime/exterior.glb`, now without the sphere trees |
| export | `BAKE_SAMPLES=4 blender -b -P export_web.py` | `runtime/premium-home.glb`, `web-bake.blend` |
| bake | `BAKE_SAMPLES=1024 blender -b -P rebake_lightmap.py` | the lightmap atlas |
| posters | `blender -b -P render_walk_previews.py` | walk-room stills from the site's camera views |
| package | `python3 package_web.py` | `public/models/*` |
| hero sky | `python3 paint_hero_sky.py` | `runtime/hero-sky-*.png` |
| hero | `blender -b -P render_hero.py` | `runtime/hero-{desktop,mobile}.png` |

The hero PNGs are encoded by hand to `public/hero/hero-desktop.webp` (2880),
`hero-desktop-1920.webp` and `hero-mobile.webp`.

**Dressing** (`add_decor.py`) covers the five rooms the site walks through,
plus the gallery. Living: fluted oak either side of a book-matched marble slab,
framed art, a fig, a side table. Dining: fluted oak behind a walnut sideboard
with a marble top, a large colour-field piece. Kitchen: fluted oak with an
ensō, marble splashback, a floating shelf. Bedroom: oak dado and panelling,
framed prints, a bench. Terrace and garden beds: olive trees and sansevieria.
The dining camera stands at (7.6, 4.8) in Blender space, so nothing may be
placed there; the old dining plant was moved off it.

**The hero** is a Cycles still, not the live scene. The sky is painted per
shot in the camera's own view (`paint_hero_sky.py`: clouds are sampled where
each ray meets a deck 2 km up) and mapped onto a dome UV'd through the same
camera, so the reflecting pool mirrors the painted sunset. Shots and the sun
live in `hero-shots.json`. Blender 5 renamed the Nishita sky to
`MULTIPLE_SCATTERING`.

## Client round 4 (September 2026)

The client sent five room references (`interiors/` in the site repo) and asked
for the rooms to be redesigned in Blender to match them. The "reference
redesign" section of `add_decor.py` does that on top of the round-3 dressing:
walnut slat walls with warm LED washes, a travertine plinth table and stone
dome pendants in the dining room, walnut kitchen joinery with a marble
waterfall island, a limewash feature wall with a channel headboard, draped
throw and mushroom lamps in the bedroom, jute rugs, boucle upholstery, olive
trees in stone pots, and collage artwork (`make_decor_textures.py`).

Lighting was reworked for golden hour: a low warm sun from the south-west,
warmer and dimmer window fills, and a warm world. Cycles casts no light
through refractive glass, so the glazing is made shadow-free for the bake;
without that the sun never reaches the floors.

Preview the walk views in Cycles before exporting:

    blender -b -P add_decor.py -- --preview living,dining --views walk-views.json

`walk-views.json` is the website's WALK_VIEWS converted to Blender space.

The exterior fascia now sits 2 cm proud of the roof slab (`build_exterior.py`);
sharing its edge plane made the two z-fight into a black and white shimmer.

## Client round 5 (September 2026): the way in

After Services the walk now stands in the gallery before the living room's
doors, slides them apart and walks through, instead of flying in from outside.

`build_door.py` builds the two walnut pocket-door leaves for the 2.8 m opening
off the gallery and bakes each leaf's full diffuse look (albedo and light) into
its own texture, then exports `runtime/door.glb`:

    BAKE_SAMPLES=384 blender -b -P build_door.py
    cp runtime/door.glb ../../public/models/door.glb

The leaves are deliberately not in `premium-interior.blend`: the house's
lightmap is baked with the doorway open, and the leaves move at runtime, so
they cannot share its atlas. The browser draws them unlit and slides them
apart with the camera's progress (`Door` in `src/components/HouseJourney.jsx`);
the camera's path through the doorway is `ENTRY_LINK` in `src/data/journey.js`.

Round 6: the plain slab leaves read as wall panels. Each leaf is now a
stile-and-rail walnut door with a recessed slat panel, reeded glass framed in
black, and a long bronze pull, in a black steel casing with a marble
threshold (`DoorCasing`). Frames, panels and casing are baked; the glass
(`DoorGlass`) and pulls (`DoorPull`) keep placeholder materials that the
browser replaces with live reeded glass and reflective bronze.
