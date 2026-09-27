# Interior finishing candidate — 27 September 2026

Scope: refine the current interior source using the five images in sample_target, without editing website source, camera paths, layout, typography, palette or behavior.

The editable candidate is natural-interior.blend. The original ../premium-interior.blend and all public/model assets remain unchanged. review.html compares the five reference images with candidate Cycles renders from the website's camera positions. These renders are authoring previews, not evidence of runtime parity.

Run make_textiles.py with Python/NumPy/Pillow, then refine.py in Blender 5.0.1. refine.py always starts from the current original, making this pass repeatable and non-stacking. It calls botanicals.py. soft_details.py is a rejected drape experiment and is not used: the fabric intersected the sofa, so it was excluded.

Changes:
- Fine 2K textile albedo, roughness and normal maps; restrained sheen and specular.
- Sculpted cushion bulges, seam welts, loose sofa backs, subtle duvet folds.
- Three indoor olives rebuilt with connected branches and irregular leaves.
- Neutral sky fill balanced against warm directional sun and practical lights.
- Dining centerpiece lowered 35 mm onto the tabletop.

Validation: audit.py verifies hashes of 54 website files and geometry/transforms of 176 protected walls, cameras and chairs. Candidate 546,576 evaluated triangles versus source 542,900; the old 450k budget was already exceeded by the user's current source. No new performance claim is made. Browser assets remain untouched; actual performance and baked-lighting parity must be measured after export.

Existing generic form validator still fails the old evidence package's unset checks, including paid-Meshy provenance assumptions. This native finishing pass does not fabricate those records or claim the generic validator passes. New Form approval is pending; no export or deployment is performed.

Observations: the references have more mature landscape context and materially richer asset silhouettes than the current procedural home. This is a constrained finishing improvement, not a claim of pixel-level photographic equivalence. Runtime will need a fresh lightmap using explicit LightmapUV, with foliage excluded from its atlas as in the existing exporter.
