# Model H-014 — the 3D house

These scripts build the house the website walks you through, and export it for
the web. Nothing here ships to the browser; the two build outputs do.

## What gets built

A single-storey linear pavilion. A south-facing circulation gallery runs the
length of a fully glazed elevation, and five spaces open off it to the north:

| stop | space   | x range (metres) |
| ---- | ------- | ---------------- |
| 1    | Living  | -16 to -8        |
| 2    | Dining  | -8 to -2         |
| 3    | Kitchen | -2 to 4          |
| 4    | Bedroom | 4 to 12          |
| 5    | Patio   | 12 to 20         |

The gallery band is y -5 to -2 and the rooms sit at y -2 to 5, with the ceiling
at 3.2m. Partitions are solid only across the room band, so the gallery reads as
one continuous enfilade and the camera can travel it without passing through
anything.

## Files

- `house_core.py` — materials, primitives, and the building shell
- `house_rooms.py` — furniture, joinery, lighting and props per space
- `house_site.py` — terrace, reflecting pool, lawn, planting, trees, roof soffit
- `post.py` — merge-by-material pass and the Eevee preview renderer
- `build_house.py` — the driver: builds, merges, exports, writes camera anchors

## Rebuilding

```bash
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup \
  -P build_house.py -- --out out/house.glb
```

Then copy the two outputs into the site:

```bash
cp out/house.glb            ../public/models/house.glb
cp out/house.anchors.json   ../src/data/houseAnchors.json
```

`houseAnchors.json` is the contract between this model and the website. It holds
one camera anchor per page section, in three.js space, and the site's section
order is read from it. If you rename or reorder a stop here, `src/data/rooms.js`
has to agree or the camera and the copy will drift apart.

## Preview renders

```bash
# 16:9 reference stills
... -P build_house.py -- --out out/house.glb --preview

# the browser's real aspect and vertical field of view
... -P build_house.py -- --out out/house.glb --preview --web

# one or two stops only
... --preview --web --only living,patio
```

Preview lighting lives in `post.py` and is never exported. The browser lights
the model itself, in `src/components/HouseJourney.jsx`.

## Things worth knowing

- **Coordinates.** Blender is Z-up, glTF and three.js are Y-up. `build_house.py`
  converts with `(x, y, z) -> (x, z, -y)` when it writes the anchors.
- **Field of view.** Blender measures the camera angle across the wider
  dimension; three.js `PerspectiveCamera.fov` is vertical. The anchors file
  carries the converted vertical value in `fov`, and the original in
  `fovBlender`.
- **Draw calls.** The build merges meshes per collection and material, taking
  roughly 1,100 objects down to about 130. Keep that step if you add geometry.
- **Size.** Draco compression is on, textures are off, and every material is a
  flat Principled colour. The export lands around 0.4 MB for ~75k triangles.
  The Draco decoder is vendored at `public/draco/` so nothing is fetched from a
  CDN at runtime.
- **Camera clearances.** The entry bay in the south glazing and the openings in
  each partition are what the camera flies through. If you move the glazing
  bays, the timber fins or the partitions, re-check the path between the
  `services` and `living` anchors first — that is the tightest gap.
