# -*- coding: utf-8 -*-
"""
BETTER HOMES — Model H-014
A linear pavilion: a south-facing circulation gallery along full-height glazing,
with five spaces opening off it to the north.

   west                                                            east
   |  LIVING   |  DINING  |  KITCHEN |  BEDROOM  |     PATIO      |
   x -16..-8    -8..-2      -2..4       4..12        12..20
   rooms  y -2..5     |  gallery (camera path) y -5..-2
   floor z=0, ceiling z=3.2

Built in metres, Z-up. Exported to glTF (Y-up) for the web.
"""
import bpy, bmesh, json, math, os, sys
from mathutils import Vector

M = math.radians

# ---------------------------------------------------------------- scene reset
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    sc.unit_settings.length_unit = 'METERS'
    try:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    except Exception:
        pass

# ---------------------------------------------------------------- materials
_MATS = {}

def mat(name, base, rough=0.8, metal=0.0, emit=None, emit_str=0.0, alpha=1.0, ior=1.45):
    """Principled BSDF material, glTF friendly."""
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*base, 1.0)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metal
    if 'IOR' in bsdf.inputs:
        bsdf.inputs['IOR'].default_value = ior
    if emit is not None:
        if 'Emission Color' in bsdf.inputs:
            bsdf.inputs['Emission Color'].default_value = (*emit, 1.0)
            bsdf.inputs['Emission Strength'].default_value = emit_str
        elif 'Emission' in bsdf.inputs:
            bsdf.inputs['Emission'].default_value = (*emit, 1.0)
            bsdf.inputs['Emission Strength'].default_value = emit_str
    if alpha < 1.0:
        bsdf.inputs['Alpha'].default_value = alpha
        m.blend_method = 'BLEND'
        try:
            m.shadow_method = 'NONE'
        except Exception:
            pass
    _MATS[name] = m
    return m

def hx(s):
    """#rrggbb -> linear rgb tuple (glTF/Blender work in linear)."""
    s = s.lstrip('#')
    srgb = [int(s[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
    def lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(lin(c) for c in srgb)

def build_palette():
    P = {}
    # surfaces
    P['floor']     = mat('Oak Floor',      hx('#cba97f'), rough=0.5)
    P['floor_pat'] = mat('Patio Stone',    hx('#8f8b84'), rough=0.85)
    P['wall']      = mat('Plaster',        hx('#efe9e1'), rough=0.93)
    P['wall_warm'] = mat('Plaster Warm',   hx('#e3d9cc'), rough=0.93)
    P['accent']    = mat('Accent Charcoal',hx('#2b2f35'), rough=0.82)
    P['ceiling']   = mat('Ceiling',        hx('#f6f3ef'), rough=0.95)
    P['concrete']  = mat('Concrete',       hx('#a5a29c'), rough=0.88)
    P['ground']    = mat('Ground',         hx('#232a2f'), rough=1.0)
    # timber
    P['walnut']    = mat('Walnut',         hx('#5e4130'), rough=0.55)
    P['oak']       = mat('Oak',            hx('#c0966a'), rough=0.58)
    P['oak_pale']  = mat('Oak Pale',       hx('#d8bd97'), rough=0.6)
    # stone
    P['marble']    = mat('Marble',         hx('#e8e5e0'), rough=0.22)
    P['travertine']= mat('Travertine',     hx('#d6c9b4'), rough=0.7)
    # metal
    P['black_mtl'] = mat('Black Metal',    hx('#1b1d20'), rough=0.38, metal=0.92)
    P['brass']     = mat('Brass',          hx('#b08d57'), rough=0.28, metal=1.0)
    P['chrome']    = mat('Chrome',         hx('#cfd3d6'), rough=0.16, metal=1.0)
    # textile
    P['linen']     = mat('Linen',          hx('#cfc6b8'), rough=0.95)
    P['wool']      = mat('Wool Grey',      hx('#9a958c'), rough=0.97)
    P['rug']       = mat('Rug',            hx('#b8ab97'), rough=0.98)
    P['rug_deep']  = mat('Rug Deep',       hx('#7d6a58'), rough=0.98)
    P['boucle']    = mat('Boucle',         hx('#e0d8cb'), rough=0.98)
    P['rust']      = mat('Brand Red Textile', hx('#c41616'), rough=0.95)
    P['ink_fab']   = mat('Charcoal Textile', hx('#3b3a38'), rough=0.95)
    # nature
    P['leaf']      = mat('Leaf',           hx('#4c6b48'), rough=0.72)
    P['leaf_dk']   = mat('Leaf Deep',      hx('#38503a'), rough=0.72)
    P['soil']      = mat('Soil',           hx('#2e2822'), rough=1.0)
    P['clay']      = mat('Clay Pot',       hx('#9c8571'), rough=0.85)
    # glass + light
    P['glass']     = mat('Glass',          hx('#b9cddb'), rough=0.05, alpha=0.16, ior=1.5)
    P['lamp']      = mat('Lamplight',      hx('#3a2a17'), rough=0.4,
                         emit=hx('#ffd9a0'), emit_str=2.1)
    P['lamp_soft'] = mat('Lamplight Soft', hx('#2e2418'), rough=0.5,
                         emit=hx('#ffcf90'), emit_str=1.4)
    P['flame']     = mat('Flame',          hx('#40200a'), rough=0.6,
                         emit=hx('#ff7a22'), emit_str=2.0)
    P['ember']     = mat('Ember',          hx('#2a1206'), rough=0.8,
                         emit=hx('#e0480f'), emit_str=1.1)
    P['strip']     = mat('Cove Strip',     hx('#2b2418'), rough=0.6,
                         emit=hx('#ffdcae'), emit_str=0.8)
    P['screen']    = mat('Screen',         hx('#0e1116'), rough=0.25)
    P['art_a']     = mat('Art Ochre',      hx('#c08a4e'), rough=0.9)
    P['art_b']     = mat('Art Ink',        hx('#2f3a4a'), rough=0.9)
    P['art_c']     = mat('Art Bone',       hx('#ded5c6'), rough=0.9)
    P['book_a']    = mat('Book Red',       hx('#8d3a2e'), rough=0.9)
    P['book_b']    = mat('Book Blue',      hx('#3c4a5e'), rough=0.9)
    P['book_c']    = mat('Book Cream',     hx('#cfc3ae'), rough=0.9)
    return P

# ---------------------------------------------------------------- primitives
COLL = {}

def collection(name):
    if name in COLL:
        return COLL[name]
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    COLL[name] = c
    return c

_CUR = [None]

def into(name):
    _CUR[0] = collection(name)

def _link(o):
    for c in o.users_collection:
        c.objects.unlink(o)
    (_CUR[0] or bpy.context.scene.collection).objects.link(o)

def _finish(o, name, material, bevel=0.0, segs=2, smooth=False):
    o.name = name
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material is not None:
        o.data.materials.append(material)
    if bevel > 0:
        md = o.modifiers.new('bvl', 'BEVEL')
        md.width = bevel
        md.segments = segs
        md.limit_method = 'ANGLE'
        md.angle_limit = M(30)
        bpy.ops.object.modifier_apply(modifier=md.name)
    if smooth:
        try:
            bpy.ops.object.shade_auto_smooth(angle=M(35))
        except Exception:
            bpy.ops.object.shade_smooth()
    _link(o)
    return o

def box(name, size, loc, material=None, rot=(0, 0, 0), bevel=0.0, segs=2):
    bpy.ops.mesh.primitive_cube_add(size=2, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.scale = (size[0] / 2.0, size[1] / 2.0, size[2] / 2.0)
    return _finish(o, name, material, bevel, segs)

def cyl(name, r, h, loc, material=None, rot=(0, 0, 0), verts=20, smooth=True, bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc,
                                        rotation=rot, vertices=verts)
    o = bpy.context.active_object
    return _finish(o, name, material, bevel, 2, smooth)

def cone(name, r1, r2, h, loc, material=None, rot=(0, 0, 0), verts=20, smooth=True):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=h, location=loc,
                                    rotation=rot, vertices=verts)
    o = bpy.context.active_object
    return _finish(o, name, material, 0.0, 2, smooth)

def sphere(name, r, loc, material=None, segs=16, rings=10, scale=(1, 1, 1), rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, rotation=rot,
                                         segments=segs, ring_count=rings)
    o = bpy.context.active_object
    o.scale = scale
    return _finish(o, name, material, 0.0, 2, True)

def plane(name, size, loc, material=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.scale = (size[0], size[1], 1)
    return _finish(o, name, material)

def dup_row(obj, n, step, name):
    """Linear array without a modifier (keeps meshes independent and cheap)."""
    out = [obj]
    for i in range(1, n):
        c = obj.copy()
        c.data = obj.data          # share mesh data — cheap, and glTF re-uses it
        c.name = '%s_%02d' % (name, i)
        c.location = Vector(obj.location) + Vector(step) * i
        _link(c)
        out.append(c)
    return out

# ---------------------------------------------------------------- geometry
CEIL = 3.2
WALL_T = 0.18
GY0, GY1 = -5.0, -2.0        # gallery (circulation) band
RY0, RY1 = -2.0, 5.0         # room band
HX0, HX1 = -16.0, 12.0       # enclosed house
PX0, PX1 = 12.0, 20.0        # patio

ROOMS = [
    dict(id='living',  x=(-16.0, -8.0)),
    dict(id='dining',  x=(-8.0, -2.0)),
    dict(id='kitchen', x=(-2.0, 4.0)),
    dict(id='bedroom', x=(4.0, 12.0)),
    dict(id='patio',   x=(12.0, 20.0)),
]

def glazing(name, x0, x1, y, z0, z1, P, bay=2.4, post=0.07, gap=None):
    """Full-height glazing with black steel mullions. `gap` = (gx0, gx1) left open."""
    w = x1 - x0
    h = z1 - z0
    n = max(1, int(round(w / bay)))
    step = w / n
    # glass sheets
    for i in range(n):
        cx = x0 + step * (i + 0.5)
        if gap and cx > gap[0] and cx < gap[1]:
            continue
        box('%s_glass_%02d' % (name, i), (step - post, 0.02, h - post),
            (cx, y, (z0 + z1) / 2), P['glass'])
    # mullions
    for i in range(n + 1):
        px = x0 + step * i
        box('%s_mull_%02d' % (name, i), (post, 0.09, h), (px, y, (z0 + z1) / 2), P['black_mtl'])
    # head + sill
    box('%s_head' % name, (w, 0.1, post), (x0 + w / 2, y, z1 - post / 2), P['black_mtl'])
    box('%s_sill' % name, (w, 0.12, 0.05), (x0 + w / 2, y, z0 + 0.025), P['black_mtl'])


def glazing_y(name, y0, y1, x, z0, z1, P, bay=2.4, post=0.07, gap=None):
    """Full-height glazing running along Y at a fixed X."""
    w = y1 - y0
    h = z1 - z0
    n = max(1, int(round(w / bay)))
    step = w / n
    for i in range(n):
        cy = y0 + step * (i + 0.5)
        if gap and gap[0] < cy < gap[1]:
            continue
        box('%s_glass_%02d' % (name, i), (0.02, step - post, h - post),
            (x, cy, (z0 + z1) / 2), P['glass'])
    for i in range(n + 1):
        py = y0 + step * i
        box('%s_mull_%02d' % (name, i), (0.09, post, h), (x, py, (z0 + z1) / 2), P['black_mtl'])
    box('%s_head' % name, (0.1, w, post), (x, y0 + w / 2, z1 - post / 2), P['black_mtl'])
    box('%s_sill' % name, (0.12, w, 0.05), (x, y0 + w / 2, z0 + 0.025), P['black_mtl'])

def build_shell(P):
    into('Shell')
    # --- ground
    # ground, terrace, pool and planting are built by house_site.py

    # --- floors
    box('floor_house', (HX1 - HX0, GY1 - GY0 + (RY1 - RY0), 0.22),
        ((HX0 + HX1) / 2, (GY0 + RY1) / 2, -0.11), P['floor'])
    box('floor_patio', (PX1 - PX0, RY1 - GY0, 0.22),
        ((PX0 + PX1) / 2, (GY0 + RY1) / 2, -0.19), P['floor_pat'])
    box('patio_step', (0.4, RY1 - GY0, 0.1), (12.1, (GY0 + RY1) / 2, -0.13), P['concrete'])

    # --- ceiling plane, with a recessed cove band over the gallery
    box('ceiling_rooms', (HX1 - HX0, RY1 - RY0, 0.14),
        ((HX0 + HX1) / 2, (RY0 + RY1) / 2, CEIL + 0.07), P['ceiling'])
    box('ceiling_gallery', (HX1 - HX0, GY1 - GY0, 0.14),
        ((HX0 + HX1) / 2, (GY0 + GY1) / 2, CEIL + 0.21), P['ceiling'])
    # cove reveal + light strip
    box('cove_lip', (HX1 - HX0, 0.12, 0.28), ((HX0 + HX1) / 2, GY1 - 0.06, CEIL + 0.0), P['ceiling'])
    box('cove_strip', (HX1 - HX0 - 0.6, 0.06, 0.05), ((HX0 + HX1) / 2, GY1 - 0.16, CEIL + 0.06), P['strip'])

    # --- roof slab with overhang
    box('roof', (HX1 - HX0 + 1.6, (RY1 - GY0) + 1.6, 0.2),
        ((HX0 + HX1) / 2, (GY0 + RY1) / 2, CEIL + 0.42), P['concrete'])
    box('fascia', (HX1 - HX0 + 1.64, 0.1, 0.34), ((HX0 + HX1) / 2, GY0 - 0.82, CEIL + 0.4), P['accent'])

    # --- end walls
    box('wall_west', (WALL_T, RY1 - GY0, CEIL), (HX0 - WALL_T / 2, (GY0 + RY1) / 2, CEIL / 2), P['wall'])
    box('wall_west_slot', (0.06, 0.5, 2.3), (HX0 - WALL_T, 1.8, 1.5), P['glass'])

    # --- north wall: solid through dining + kitchen, glazed at living + bedroom
    box('wall_north_mid', (6.0, WALL_T, CEIL), (-5.0, RY1 + WALL_T / 2, CEIL / 2), P['wall'])
    box('wall_north_k', (6.0, WALL_T, CEIL), (1.0, RY1 + WALL_T / 2, CEIL / 2), P['wall_warm'])
    glazing('north_living', -15.4, -8.6, RY1 + 0.04, 0.0, CEIL, P, bay=2.26)
    box('wall_north_b', (4.4, WALL_T, CEIL), (6.2, RY1 + WALL_T / 2, CEIL / 2), P['wall'])
    glazing('north_bed', 8.5, 11.4, RY1 + 0.04, 0.0, CEIL, P, bay=1.45)

    # --- south wall: the long glazed elevation, open at the entry bay
    glazing('south', HX0, HX1, GY0 - 0.04, 0.0, CEIL, P, bay=2.33, gap=(-15.7, -13.1))
    # entry reveal
    box('entry_jamb_a', (0.12, 0.3, CEIL), (-15.7, GY0 - 0.04, CEIL / 2), P['black_mtl'])
    box('entry_jamb_b', (0.12, 0.3, CEIL), (-13.1, GY0 - 0.04, CEIL / 2), P['black_mtl'])
    # one sliding leaf parked open
    box('entry_leaf', (2.5, 0.05, CEIL - 0.14), (-12.0, GY0 - 0.22, (CEIL - 0.14) / 2), P['glass'])

    # --- partitions between rooms (solid in the room band, open to the gallery)
    for px, m_, tag in ((-8.0, P['wall'], 'a'), (-2.0, P['wall_warm'], 'b'), (4.0, P['wall'], 'c')):
        box('part_%s' % tag, (WALL_T, RY1 - RY0, CEIL), (px, (RY0 + RY1) / 2, CEIL / 2), m_)
        box('part_%s_fin' % tag, (WALL_T, 0.5, CEIL), (px, RY0 - 0.25, CEIL / 2), m_)
    # bedroom / patio: full-height sliding glass
    # bedroom -> patio: glazed in the room band, open where the gallery runs out
    glazing_y('east_slide', RY0, RY1, HX1, 0.0, CEIL, P, bay=2.33)
    box('east_pier_n', (0.5, 0.5, CEIL), (HX1, RY1 - 0.25, CEIL / 2), P['wall'])
    box('east_head', (0.4, GY1 - GY0, 0.5), (HX1, (GY0 + GY1) / 2, CEIL - 0.25), P['wall'])

    # --- patio pergola
    into('Patio')
    box('perg_beam_w', (0.16, RY1 - GY0, 0.4), (12.6, (GY0 + RY1) / 2, CEIL + 0.2), P['walnut'])
    box('perg_beam_e', (0.16, RY1 - GY0, 0.4), (19.4, (GY0 + RY1) / 2, CEIL + 0.2), P['walnut'])
    box('perg_col_a', (0.16, 0.16, CEIL + 0.4), (19.4, GY0 + 0.2, (CEIL + 0.4) / 2 - 0.2), P['walnut'])
    # set beside the seating rather than the far corner, so it does not
    # stand in the middle of the patio view; the beam cantilevers north
    box('perg_col_b', (0.16, 0.16, CEIL + 0.4), (19.4, 1.0, (CEIL + 0.4) / 2 - 0.2), P['walnut'])
    s = box('perg_slat_00', (7.0, 0.07, 0.24), (16.0, GY0 + 0.3, CEIL + 0.3), P['walnut'])
    dup_row(s, 22, (0, 0.44, 0), 'perg_slat')
