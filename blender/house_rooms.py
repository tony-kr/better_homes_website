# -*- coding: utf-8 -*-
"""Interiors for Model H-014 — furniture, joinery, lighting, props."""
import math, random
from mathutils import Vector

M = math.radians
random.seed(14)

# ------------------------------------------------------------------ props
def cushion(n, loc, P, m=None, w=0.46, rot=0.0):
    box(n, (w, 0.16, w * 0.86), loc, m or P['linen'], rot=(0, 0, rot), bevel=0.055, segs=3)

def throw(n, loc, P, m=None, size=(0.9, 1.1)):
    box(n, (size[0], size[1], 0.045), loc, m or P['wool'], bevel=0.02, segs=2)

def books(n, loc, P, count=3, w=0.22, d=0.3, rot=0.0):
    cols = [P['book_a'], P['book_b'], P['book_c'], P['walnut']]
    z = loc[2]
    for i in range(count):
        t = 0.035 + (i % 3) * 0.012
        box('%s_%d' % (n, i), (w - i * 0.012, d - i * 0.014, t),
            (loc[0], loc[1], z + t / 2), cols[i % 4], rot=(0, 0, rot + i * 0.06))
        z += t

def vase(n, loc, P, h=0.34, r=0.09, m=None, stems=True):
    cyl('%s_body' % n, r, h, (loc[0], loc[1], loc[2] + h / 2), m or P['clay'], verts=16)
    cyl('%s_neck' % n, r * 0.52, h * 0.22, (loc[0], loc[1], loc[2] + h + h * 0.08),
        m or P['clay'], verts=14)
    if stems:
        for i in range(7):
            a = i * 2.399
            tilt = 0.26 + (i % 3) * 0.12
            L = 0.34 + (i % 4) * 0.07
            cyl('%s_stem_%d' % (n, i), 0.006, L,
                (loc[0] + math.cos(a) * L * 0.18, loc[1] + math.sin(a) * L * 0.18,
                 loc[2] + h + L * 0.45),
                P['leaf_dk'], rot=(math.sin(a) * tilt, -math.cos(a) * tilt, 0), verts=5)
            sphere('%s_leaf_%d' % (n, i), 0.055,
                   (loc[0] + math.cos(a) * L * 0.42, loc[1] + math.sin(a) * L * 0.42,
                    loc[2] + h + L * 0.88),
                   P['leaf'] if i % 3 else P['leaf_dk'],
                   segs=10, rings=6, scale=(1.45, 0.62, 0.1), rot=(0.1, 0.22, a))

def bowl(n, loc, P, r=0.15, m=None):
    sphere('%s' % n, r, (loc[0], loc[1], loc[2] + r * 0.4), m or P['marble'],
           segs=18, rings=8, scale=(1, 1, 0.42))

def plant(n, loc, P, h=1.35, pot_r=0.26, leaves=13):
    """A sculptural indoor tree in a matte pot."""
    cyl('%s_pot' % n, pot_r, 0.42, (loc[0], loc[1], loc[2] + 0.21), P['clay'], verts=20)
    cyl('%s_pot_lip' % n, pot_r * 1.04, 0.05, (loc[0], loc[1], loc[2] + 0.42), P['clay'], verts=20)
    cyl('%s_soil' % n, pot_r * 0.9, 0.04, (loc[0], loc[1], loc[2] + 0.42), P['soil'], verts=16)
    cyl('%s_trunk' % n, 0.035, h, (loc[0], loc[1], loc[2] + 0.42 + h / 2), P['walnut'], verts=8)
    for i in range(leaves):
        a = i * 2.399
        rad = 0.14 + (i % 5) * 0.11
        zz = loc[2] + 0.42 + h * (0.34 + 0.66 * ((i % 6) / 6.0))
        droop = 0.22 + (i % 3) * 0.16
        sphere('%s_leaf_%02d' % (n, i), 0.14,
               (loc[0] + math.cos(a) * rad, loc[1] + math.sin(a) * rad, zz),
               P['leaf'] if i % 3 else P['leaf_dk'],
               segs=10, rings=6, scale=(1.75, 0.95, 0.1), rot=(math.sin(a) * droop, -math.cos(a) * droop, a))
        cyl('%s_twig_%02d' % (n, i), 0.008, rad * 1.5,
            (loc[0] + math.cos(a) * rad * 0.42, loc[1] + math.sin(a) * rad * 0.42, zz + 0.012),
            P['leaf_dk'], rot=(math.sin(a) * 1.35, -math.cos(a) * 1.35, 0), verts=5)

def grass_pot(n, loc, P, h=0.85, r=0.3):
    """A clipped shrub in a trough — reads as mass, not wires."""
    box('%s_pot' % n, (r * 2, r * 2, 0.5), (loc[0], loc[1], loc[2] + 0.25), P['concrete'], bevel=0.02)
    cyl('%s_soil' % n, r * 0.82, 0.04, (loc[0], loc[1], loc[2] + 0.5), P['soil'], verts=14)
    for i in range(5):
        a = i * 2.399
        rad = r * 0.42 * ((i % 3) / 3.0 + 0.35)
        zz = loc[2] + 0.5 + h * (0.34 + 0.46 * ((i % 3) / 3.0))
        sphere('%s_mass_%d' % (n, i), h * 0.42,
               (loc[0] + math.cos(a) * rad, loc[1] + math.sin(a) * rad, zz),
               P['leaf_dk'] if i % 2 else P['leaf'],
               segs=10, rings=6, scale=(1.0, 1.0, 0.8))


def art(n, loc, P, w=0.9, h=1.2, face='y', m=None, frame=True):
    """Canvas on a wall. face 'y' faces -Y/+Y, 'x' faces -X/+X."""
    m = m or P['art_a']
    if face == 'y':
        size, fsize = (w, 0.04, h), (w + 0.06, 0.06, h + 0.06)
    else:
        size, fsize = (0.04, w, h), (0.06, w + 0.06, h + 0.06)
    if frame:
        box('%s_frame' % n, fsize, loc, P['black_mtl'])
    off = 0.035
    l2 = list(loc)
    l2[1 if face == 'y' else 0] += off * (-1 if loc[1] > 0 or face == 'x' else 1)
    box('%s_canvas' % n, size, tuple(l2), m)

def pendant(n, loc, P, r=0.16, drop=1.5, shade='dome'):
    top = loc[2] + drop
    cyl('%s_cord' % n, 0.008, drop, (loc[0], loc[1], loc[2] + drop / 2), P['black_mtl'], verts=6)
    cyl('%s_canopy' % n, 0.05, 0.04, (loc[0], loc[1], top), P['black_mtl'], verts=12)
    if shade == 'dome':
        sphere('%s_shade' % n, r, (loc[0], loc[1], loc[2]), P['black_mtl'],
               segs=20, rings=10, scale=(1, 1, 0.62))
        sphere('%s_glow' % n, r * 0.7, (loc[0], loc[1], loc[2] - r * 0.22), P['lamp'],
               segs=16, rings=8, scale=(1, 1, 0.42))
    else:
        cone('%s_shade' % n, r, r * 0.34, r * 1.15, (loc[0], loc[1], loc[2]), P['black_mtl'], verts=20)
        cyl('%s_glow' % n, r * 0.82, 0.04, (loc[0], loc[1], loc[2] - r * 0.55), P['lamp'], verts=18)

def downlights(n, x0, x1, y, z, P, count=6, r=0.055):
    step = (x1 - x0) / max(1, count - 1) if count > 1 else 0
    for i in range(count):
        cx = x0 + step * i
        cyl('%s_%02d' % (n, i), r, 0.03, (cx, y, z - 0.015), P['lamp_soft'], verts=12)

def table_lamp(n, loc, P, h=0.46):
    cyl('%s_base' % n, 0.09, 0.02, (loc[0], loc[1], loc[2] + 0.01), P['brass'], verts=16)
    cyl('%s_stem' % n, 0.016, h * 0.62, (loc[0], loc[1], loc[2] + h * 0.33), P['brass'], verts=10)
    cone('%s_shade' % n, 0.14, 0.1, 0.19, (loc[0], loc[1], loc[2] + h * 0.82), P['linen'], verts=20)
    cyl('%s_glow' % n, 0.095, 0.02, (loc[0], loc[1], loc[2] + h * 0.82 - 0.095), P['lamp'], verts=16)

def floor_lamp(n, loc, P, h=1.62):
    cyl('%s_base' % n, 0.16, 0.025, (loc[0], loc[1], loc[2] + 0.012), P['black_mtl'], verts=22)
    cyl('%s_stem' % n, 0.018, h, (loc[0], loc[1], loc[2] + h / 2), P['black_mtl'], verts=10)
    cyl('%s_arm' % n, 0.016, 0.6, (loc[0] + 0.3, loc[1], loc[2] + h), P['black_mtl'],
        rot=(0, M(90), 0), verts=10)
    cone('%s_shade' % n, 0.17, 0.12, 0.2, (loc[0] + 0.6, loc[1], loc[2] + h - 0.1), P['black_mtl'], verts=20)
    cyl('%s_glow' % n, 0.11, 0.02, (loc[0] + 0.6, loc[1], loc[2] + h - 0.2), P['lamp'], verts=16)

def rug(n, loc, size, P, m=None, z=0.0):
    box(n, (size[0], size[1], 0.024), (loc[0], loc[1], z + 0.012), m or P['rug'], bevel=0.01)

# ------------------------------------------------------------------ LIVING
def build_living(P):
    into('Living')
    cx, cy = -12.0, 1.4
    rug('living_rug', (cx, cy - 0.1), (4.6, 3.4), P)

    # L-sofa: long run facing the glass, return along the west
    box('sofa_base', (3.5, 1.02, 0.30), (cx - 0.2, cy + 1.25, 0.15), P['wool'], bevel=0.035)
    box('sofa_back', (3.5, 0.24, 0.52), (cx - 0.2, cy + 1.64, 0.56), P['wool'], bevel=0.05)
    box('sofa_arm_r', (0.26, 1.02, 0.28), (cx + 1.62, cy + 1.25, 0.44), P['wool'], bevel=0.06)
    box('sofa_ret_base', (1.06, 1.7, 0.30), (cx - 2.42, cy + 0.36, 0.15), P['wool'], bevel=0.035)
    box('sofa_ret_back', (0.24, 1.7, 0.52), (cx - 2.83, cy + 0.36, 0.56), P['wool'], bevel=0.05)
    for i, (sx, sy) in enumerate([(cx - 1.35, cy + 1.2), (cx - 0.2, cy + 1.2), (cx + 0.95, cy + 1.2)]):
        box('sofa_seat_%d' % i, (1.1, 0.96, 0.15), (sx, sy, 0.375), P['linen'], bevel=0.05, segs=3)
    box('sofa_seat_ret', (1.0, 1.1, 0.15), (cx - 2.42, cy + 0.0, 0.375), P['linen'], bevel=0.05, segs=3)
    cushion('cush_a', (cx - 1.5, cy + 1.52, 0.56), P, m=P['boucle'], rot=0.08)
    cushion('cush_b', (cx + 1.05, cy + 1.52, 0.56), P, m=P['rust'], rot=-0.1)
    cushion('cush_c', (cx - 2.62, cy + 0.8, 0.56), P, m=P['ink_fab'], rot=0.6, w=0.4)
    box('sofa_throw', (0.52, 0.72, 0.03), (cx + 1.16, cy + 1.06, 0.462), P['rust'],
        bevel=0.03, segs=2)
    box('sofa_throw_fall', (0.48, 0.16, 0.2), (cx + 1.16, cy + 0.74, 0.38), P['rust'],
        bevel=0.04, segs=2)
    for i, lx in enumerate((cx - 3.0, cx + 1.72)):
        box('sofa_leg_%d' % i, (0.06, 0.9, 0.06), (lx, cy + 1.2, 0.03), P['black_mtl'])

    # travertine coffee table + styling
    box('cof_top', (1.5, 0.78, 0.09), (cx, cy - 0.5, 0.36), P['travertine'], bevel=0.02)
    box('cof_leg_a', (0.16, 0.66, 0.32), (cx - 0.6, cy - 0.5, 0.16), P['travertine'])
    box('cof_leg_b', (0.16, 0.66, 0.32), (cx + 0.6, cy - 0.5, 0.16), P['travertine'])
    books('cof_books', (cx - 0.3, cy - 0.5, 0.405), P, count=3, w=0.3, d=0.36, rot=0.12)
    cyl('cof_bowl', 0.17, 0.075, (cx + 0.38, cy - 0.46, 0.443), P['marble'], verts=24, bevel=0.018)
    cyl('cof_bowl_in', 0.14, 0.02, (cx + 0.38, cy - 0.46, 0.472), P['soil'], verts=22)
    cyl('cof_candle_a', 0.03, 0.14, (cx + 0.08, cy - 0.72, 0.475), P['boucle'], verts=12)
    cyl('cof_candle_b', 0.03, 0.2, (cx + 0.17, cy - 0.68, 0.505), P['boucle'], verts=12)

    # two boucle lounge chairs, angled aside so the gallery view stays open
    for i, (chx, chy, yaw) in enumerate(((cx - 2.05, cy - 1.35, M(34)), (cx + 1.45, cy - 1.5, M(-30)))):
        ca, sa = math.cos(yaw), math.sin(yaw)
        def off(dx, dy):
            return (chx + dx * ca - dy * sa, chy + dx * sa + dy * ca)
        box('lchair_%d_seat' % i, (0.76, 0.74, 0.15), (*off(0, 0), 0.34), P['boucle'],
            rot=(0, 0, yaw), bevel=0.07, segs=3)
        box('lchair_%d_back' % i, (0.76, 0.18, 0.44), (*off(0, -0.34), 0.58), P['boucle'],
            rot=(M(-8), 0, yaw), bevel=0.07, segs=3)
        box('lchair_%d_arm_a' % i, (0.12, 0.7, 0.12), (*off(-0.37, 0.02), 0.46), P['boucle'],
            rot=(0, 0, yaw), bevel=0.045)
        box('lchair_%d_arm_b' % i, (0.12, 0.7, 0.12), (*off(0.37, 0.02), 0.46), P['boucle'],
            rot=(0, 0, yaw), bevel=0.045)
        for j, (lx, ly) in enumerate([(-0.29, -0.27), (0.29, -0.27), (-0.29, 0.29), (0.29, 0.29)]):
            cyl('lchair_%d_leg_%d' % (i, j), 0.022, 0.26, (*off(lx, ly), 0.13),
                P['black_mtl'], verts=8)

    # west-wall console + art + objects
    box('console_body', (0.5, 2.6, 0.46), (-15.6, 2.2, 0.36), P['walnut'], bevel=0.015)
    box('console_top', (0.56, 2.68, 0.04), (-15.6, 2.2, 0.61), P['walnut'], bevel=0.01)
    for i in range(3):
        box('console_leg_%d' % i, (0.04, 0.04, 0.14), (-15.6, 1.1 + i * 1.1, 0.07), P['black_mtl'])
    vase('console_vase', (-15.58, 1.35, 0.63), P, h=0.36, r=0.1)
    books('console_books', (-15.58, 2.5, 0.63), P, count=4, w=0.26, d=0.32, rot=-0.08)
    bowl('console_bowl', (-15.58, 3.1, 0.63), P, r=0.13, m=P['brass'])
    art('living_art_a', (-15.86, 1.6, 1.78), P, w=1.0, h=1.3, face='x', m=P['art_c'])
    art('living_art_b', (-15.86, 2.9, 1.66), P, w=0.72, h=0.95, face='x', m=P['art_b'])

    # partition wall (x=-8) reads as a joinery niche from the living side
    box('niche_back', (0.06, 2.6, 2.3), (-8.14, 2.4, 1.35), P['accent'])
    for i in range(4):
        box('niche_shelf_%d' % i, (0.3, 2.5, 0.04), (-8.3, 2.4, 0.5 + i * 0.6), P['walnut'])
        books('niche_books_%d' % i, (-8.3, 1.55 + (i % 2) * 0.5, 0.52 + i * 0.6), P,
              count=3, w=0.2, d=0.26, rot=0.0)
    for i in range(4):
        box('niche_strip_%d' % i, (0.04, 2.3, 0.025), (-8.44, 2.4, 0.56 + i * 0.6), P['strip'])
    bowl('niche_bowl', (-8.3, 3.3, 1.72), P, r=0.12, m=P['clay'])
    vase('niche_vase', (-8.3, 3.25, 2.32), P, h=0.26, r=0.075, stems=False)

    floor_lamp('living_lamp', (cx - 3.3, cy + 2.15, 0.0), P)
    plant('living_plant', (-8.9, -1.2, 0.0), P, h=1.5, leaves=15)
    plant('living_plant_b', (-15.4, 4.15, 0.0), P, h=1.15, pot_r=0.22, leaves=11)
    pendant('living_pend', (cx + 2.7, cy - 1.9, 1.95), P, r=0.2, drop=1.25, shade='dome')
    downlights('living_dl', -15.0, -9.0, 3.2, CEIL, P, count=5)

    # side table by the return
    cyl('living_side_top', 0.26, 0.05, (cx - 2.4, cy - 1.25, 0.5), P['marble'], verts=22)
    cyl('living_side_stem', 0.05, 0.48, (cx - 2.4, cy - 1.25, 0.24), P['black_mtl'], verts=12)
    cyl('living_side_base', 0.21, 0.02, (cx - 2.4, cy - 1.25, 0.01), P['black_mtl'], verts=22)
    table_lamp('living_tl', (cx - 2.4, cy - 1.25, 0.525), P, h=0.42)

# ------------------------------------------------------------------ DINING
def build_dining(P):
    into('Dining')
    cx, cy = -5.0, 1.5
    rug('dining_rug', (cx, cy), (3.6, 2.6), P, m=P['rug_deep'])

    # solid walnut table
    box('dine_top', (2.9, 1.12, 0.07), (cx, cy, 0.735), P['walnut'], bevel=0.012)
    box('dine_leg_a', (0.1, 0.96, 0.7), (cx - 1.22, cy, 0.35), P['walnut'], bevel=0.012)
    box('dine_leg_b', (0.1, 0.96, 0.7), (cx + 1.22, cy, 0.35), P['walnut'], bevel=0.012)
    box('dine_rail', (2.3, 0.08, 0.1), (cx, cy, 0.62), P['walnut'])

    # six chairs — three a side
    def chair(n, x, y, flip):
        s = -1 if flip else 1
        box('%s_seat' % n, (0.47, 0.46, 0.055), (x, y, 0.445), P['oak'], bevel=0.014)
        box('%s_pad' % n, (0.43, 0.42, 0.04), (x, y, 0.492), P['ink_fab'], bevel=0.016)
        # two stiles carry the back, so it reads as one piece
        for k, sx in enumerate((-0.2, 0.2)):
            box('%s_stile_%d' % (n, k), (0.05, 0.05, 0.42), (x + sx, y + 0.2 * s, 0.63),
                P['oak'], rot=(M(7) * s, 0, 0), bevel=0.008)
        box('%s_back' % n, (0.45, 0.045, 0.24), (x, y + 0.235 * s, 0.76), P['oak'],
            rot=(M(7) * s, 0, 0), bevel=0.014)
        for j, (lx, ly) in enumerate([(-0.19, -0.19), (0.19, -0.19), (-0.19, 0.19), (0.19, 0.19)]):
            cyl('%s_leg_%d' % (n, j), 0.018, 0.44, (x + lx, y + ly, 0.22), P['black_mtl'], verts=8)
    for i in range(3):
        chair('dchair_s%d' % i, cx - 0.95 + i * 0.95, cy - 0.86, False)
        chair('dchair_n%d' % i, cx - 0.95 + i * 0.95, cy + 0.86, True)

    # a row of three pendants
    for i in range(3):
        pendant('dine_pend_%d' % i, (cx - 0.9 + i * 0.9, cy, 2.06), P, r=0.15, drop=1.14, shade='cone')

    # table styling
    vase('dine_vase', (cx, cy, 0.77), P, h=0.3, r=0.085)
    for i in range(2):
        cyl('dine_candle_%d' % i, 0.026, 0.22 + i * 0.07,
            (cx - 0.55 + i * 1.1, cy + 0.08, 0.77 + (0.22 + i * 0.07) / 2), P['boucle'], verts=12)
    for i, (px, py) in enumerate([(cx - 0.95, cy - 0.5), (cx, cy - 0.5), (cx + 0.95, cy - 0.5),
                                  (cx - 0.95, cy + 0.5), (cx, cy + 0.5), (cx + 0.95, cy + 0.5)]):
        cyl('dine_plate_%d' % i, 0.13, 0.015, (px, py, 0.778), P['marble'], verts=20)

    # sideboard on the north wall + art
    box('side_body', (2.4, 0.46, 0.62), (cx, 4.62, 0.58), P['oak_pale'], bevel=0.014)
    box('side_top', (2.48, 0.5, 0.04), (cx, 4.62, 0.91), P['oak_pale'], bevel=0.01)
    for i in range(2):
        box('side_door_%d' % i, (1.14, 0.03, 0.54), (cx - 0.6 + i * 1.2, 4.38, 0.58), P['walnut'])
        cyl('side_pull_%d' % i, 0.012, 0.3, (cx - 0.6 + i * 1.2, 4.35, 0.58), P['brass'],
            rot=(M(90), 0, 0), verts=8)
    for i in range(4):
        box('side_leg_%d' % i, (0.05, 0.05, 0.26), (cx - 1.05 + (i % 2) * 2.1, 4.45 + (i // 2) * 0.34, 0.13),
            P['black_mtl'])
    vase('side_vase', (cx - 0.8, 4.6, 0.93), P, h=0.42, r=0.11)
    books('side_books', (cx + 0.75, 4.6, 0.93), P, count=3, w=0.26, d=0.3, rot=0.1)
    bowl('side_bowl', (cx + 0.15, 4.6, 0.93), P, r=0.14, m=P['clay'])
    art('dine_art', (cx - 0.25, 4.86, 2.0), P, w=1.5, h=1.05, face='y', m=P['art_a'])
    downlights('dine_dl', -7.2, -2.8, 3.2, CEIL, P, count=4)
    plant('dine_plant', (-2.85, -1.2, 0.0), P, h=1.2, pot_r=0.22, leaves=11)

# ------------------------------------------------------------------ KITCHEN
def build_kitchen(P):
    into('Kitchen')
    cx = 1.0
    ny = 4.9   # north wall face

    # tall run + base run against the north wall
    box('k_tall', (2.2, 0.66, 2.42), (cx + 1.7, ny - 0.33, 1.21), P['walnut'], bevel=0.01)
    for i in range(3):
        box('k_tall_door_%d' % i, (0.7, 0.03, 2.34), (cx + 0.98 + i * 0.72, ny - 0.68, 1.21), P['walnut'])
    box('k_base', (3.4, 0.66, 0.88), (cx - 1.1, ny - 0.33, 0.44), P['walnut'], bevel=0.01)
    box('k_counter', (3.5, 0.7, 0.05), (cx - 1.1, ny - 0.33, 0.905), P['marble'], bevel=0.008)
    box('k_splash', (3.5, 0.03, 0.62), (cx - 1.1, ny - 0.01, 1.24), P['marble'])
    for i in range(4):
        box('k_base_door_%d' % i, (0.8, 0.03, 0.8), (cx - 2.4 + i * 0.85, ny - 0.68, 0.44), P['walnut'])
        cyl('k_pull_%d' % i, 0.01, 0.42, (cx - 2.4 + i * 0.85, ny - 0.71, 0.72), P['brass'],
            rot=(0, M(90), 0), verts=8)
    # floating shelf + strip light under the tall run
    box('k_shelf', (1.9, 0.26, 0.05), (cx - 1.5, ny - 0.13, 1.62), P['oak'], bevel=0.008)
    box('k_strip', (3.2, 0.05, 0.035), (cx - 1.1, ny - 0.6, 1.45), P['strip'])
    for i in range(5):
        cyl('k_jar_%d' % i, 0.055, 0.16 + (i % 3) * 0.04,
            (cx - 2.2 + i * 0.36, ny - 0.13, 1.645 + (0.16 + (i % 3) * 0.04) / 2),
            P['marble'] if i % 2 else P['clay'], verts=14)
    # sink + tap
    box('k_sink', (0.66, 0.42, 0.03), (cx - 1.6, ny - 0.35, 0.9), P['chrome'])
    cyl('k_tap', 0.018, 0.34, (cx - 1.6, ny - 0.12, 1.09), P['black_mtl'], verts=10)
    cyl('k_tap_arm', 0.016, 0.24, (cx - 1.6, ny - 0.24, 1.25), P['black_mtl'], rot=(M(90), 0, 0), verts=10)
    # hob
    box('k_hob', (0.62, 0.42, 0.015), (cx - 0.35, ny - 0.35, 0.935), P['screen'])

    # island with waterfall ends
    ix, iy = cx, 1.55
    box('isl_body', (2.7, 1.0, 0.86), (ix, iy, 0.43), P['oak_pale'], bevel=0.01)
    box('isl_top', (2.96, 1.12, 0.06), (ix, iy, 0.89), P['marble'], bevel=0.008)
    box('isl_fall_a', (0.06, 1.12, 0.92), (ix - 1.45, iy, 0.46), P['marble'])
    box('isl_fall_b', (0.06, 1.12, 0.92), (ix + 1.45, iy, 0.46), P['marble'])
    box('isl_reveal', (2.7, 0.03, 0.1), (ix, iy - 0.51, 0.1), P['screen'])
    for i in range(2):
        box('isl_door_%d' % i, (1.2, 0.03, 0.72), (ix - 0.65 + i * 1.3, iy + 0.51, 0.47), P['walnut'])
    # island styling
    cyl('isl_bowl', 0.2, 0.09, (ix - 0.85, iy, 0.965), P['clay'], verts=24, bevel=0.02)
    cyl('isl_bowl_in', 0.165, 0.02, (ix - 0.85, iy, 1.0), P['soil'], verts=22)
    for i in range(5):
        a = i * 2.399
        sphere('isl_fruit_%d' % i, 0.052,
               (ix - 0.85 + math.cos(a) * 0.075, iy + math.sin(a) * 0.075, 1.045),
               P['art_a'] if i % 2 else P['leaf'], segs=10, rings=6)
    box('isl_board', (0.46, 0.3, 0.025), (ix + 0.75, iy - 0.08, 0.933), P['walnut'], bevel=0.008)
    cyl('isl_kettle', 0.08, 0.2, (ix + 0.2, iy + 0.2, 1.02), P['black_mtl'], verts=16)
    vase('isl_sprig', (ix + 1.15, iy + 0.26, 0.92), P, h=0.2, r=0.055)

    # three stools on the gallery side
    for i in range(3):
        sx = ix - 0.9 + i * 0.9
        sy = iy - 0.85
        cyl('stool_%d_seat' % i, 0.18, 0.05, (sx, sy, 0.66), P['ink_fab'], verts=20, bevel=0.012)
        cyl('stool_%d_stem' % i, 0.022, 0.64, (sx, sy, 0.32), P['black_mtl'], verts=10)
        cyl('stool_%d_base' % i, 0.17, 0.02, (sx, sy, 0.01), P['black_mtl'], verts=20)
        cyl('stool_%d_ring' % i, 0.13, 0.015, (sx, sy, 0.2), P['black_mtl'], verts=16)

    pendant('k_pend_a', (ix - 0.66, iy, 1.96), P, r=0.17, drop=1.24, shade='cone')
    pendant('k_pend_b', (ix + 0.66, iy, 1.96), P, r=0.17, drop=1.24, shade='cone')
    downlights('k_dl', -1.2, 3.2, 4.3, CEIL, P, count=5)
    art('k_art_a', (3.95, 2.35, 1.72), P, w=0.95, h=1.25, face='x', m=P['art_b'])
    art('k_art_b', (3.95, 3.55, 1.58), P, w=0.62, h=0.85, face='x', m=P['art_c'])
    plant('k_plant', (3.3, 3.5, 0.0), P, h=1.35, pot_r=0.24, leaves=12)
    grass_pot('k_grass', (3.4, -1.3, 0.0), P, h=0.7, r=0.24)

# ------------------------------------------------------------------ BEDROOM
def build_bedroom(P):
    into('Bedroom')
    bx, by = 6.2, 3.35      # bed centre; head against the solid north wall
    ny = 4.9

    rug('bed_rug', (bx + 0.15, by - 0.95), (3.6, 3.2), P, m=P['rug'])

    # full-height oak headboard panel with an upholstered inset
    box('bed_head', (2.9, 0.12, 1.25), (bx, ny - 0.06, 0.74), P['oak'], bevel=0.02)
    box('bed_head_pad', (2.55, 0.11, 0.9), (bx, ny - 0.16, 0.8), P['linen'], bevel=0.06, segs=3)
    box('bed_head_rail', (3.1, 0.07, 0.06), (bx, ny - 0.08, 1.4), P['walnut'], bevel=0.012)

    # platform bed, foot toward the gallery
    box('bed_plat', (2.08, 2.18, 0.24), (bx, by, 0.12), P['walnut'], bevel=0.015)
    box('bed_mat', (1.94, 2.0, 0.38), (bx, by - 0.04, 0.43), P['boucle'], bevel=0.08, segs=3)
    box('bed_sheet', (1.98, 1.5, 0.42), (bx, by - 0.36, 0.45), P['linen'], bevel=0.09, segs=3)
    box('bed_sheet_fall', (1.98, 0.18, 0.3), (bx, by - 1.08, 0.36), P['linen'], bevel=0.07, segs=3)
    box('bed_fold', (1.96, 0.66, 0.11), (bx, by - 0.74, 0.655), P['wool'], bevel=0.045, segs=3)
    for i, px in enumerate((bx - 0.46, bx + 0.46)):
        box('pillow_%d' % i, (0.66, 0.4, 0.17), (px, by + 0.78, 0.6), P['linen'], bevel=0.07, segs=3)
        box('pillow_b_%d' % i, (0.58, 0.34, 0.14), (px, by + 0.5, 0.6), P['boucle'], bevel=0.06, segs=3)
    cushion('bed_cush', (bx, by + 0.28, 0.6), P, m=P['rust'], w=0.4)

    # nightstands + lamps, flanking the head
    for i, px in enumerate((bx - 1.62, bx + 1.62)):
        py = ny - 0.42
        box('ns_%d' % i, (0.46, 0.4, 0.32), (px, py, 0.35), P['walnut'], bevel=0.012)
        box('ns_top_%d' % i, (0.5, 0.44, 0.03), (px, py, 0.525), P['walnut'], bevel=0.008)
        cyl('ns_pull_%d' % i, 0.01, 0.16, (px, py - 0.21, 0.35), P['brass'], rot=(0, M(90), 0), verts=8)
        for j in range(4):
            cyl('ns_leg_%d_%d' % (i, j), 0.014, 0.19,
                (px - 0.14 + (j % 2) * 0.28, py - 0.14 + (j // 2) * 0.28, 0.095),
                P['black_mtl'], verts=6)
        table_lamp('bed_lamp_%d' % i, (px, py, 0.54), P, h=0.44)
    books('ns_books', (bx + 1.62, ny - 0.5, 0.54), P, count=2, w=0.18, d=0.24, rot=0.2)

    # bench at the foot
    box('bench_top', (1.7, 0.44, 0.13), (bx, by - 1.86, 0.44), P['boucle'], bevel=0.055, segs=3)
    for i in range(2):
        box('bench_leg_%d' % i, (0.06, 0.06, 0.38), (bx - 0.7 + i * 1.4, by - 1.86, 0.19), P['black_mtl'])
    box('bench_rail', (1.5, 0.05, 0.05), (bx, by - 1.86, 0.33), P['black_mtl'])
    throw('bench_throw', (bx + 0.5, by - 1.86, 0.52), P, m=P['wool'], size=(0.55, 0.38))

    # low dressing joinery on the gallery edge, facing the bed
    box('dress_body', (3.0, 0.5, 0.68), (8.6, -1.45, 0.4), P['oak_pale'], bevel=0.012)
    box('dress_top', (3.1, 0.54, 0.04), (8.6, -1.45, 0.76), P['oak_pale'], bevel=0.008)
    for i in range(3):
        box('dress_dr_%d' % i, (0.92, 0.03, 0.58), (7.6 + i * 1.0, -1.21, 0.4), P['walnut'])
        cyl('dress_pull_%d' % i, 0.01, 0.34, (7.6 + i * 1.0, -1.18, 0.4), P['brass'],
            rot=(0, M(90), 0), verts=8)
    vase('dress_vase', (7.7, -1.45, 0.78), P, h=0.32, r=0.09)
    bowl('dress_tray', (9.5, -1.45, 0.78), P, r=0.16, m=P['brass'])
    art('bed_art_a', (8.0, -1.73, 1.8), P, w=0.95, h=1.25, face='y', m=P['art_c'])
    art('bed_art_b', (9.35, -1.73, 1.68), P, w=0.7, h=0.92, face='y', m=P['art_b'])

    # reading corner at the north-east glass
    chx, chy = 10.5, 3.4
    box('read_seat', (0.8, 0.78, 0.15), (chx, chy, 0.35), P['ink_fab'], bevel=0.07, segs=3)
    box('read_back', (0.8, 0.18, 0.5), (chx, chy + 0.36, 0.62), P['ink_fab'],
        rot=(M(-8), 0, 0), bevel=0.07, segs=3)
    box('read_arm_a', (0.13, 0.74, 0.12), (chx - 0.38, chy, 0.47), P['ink_fab'], bevel=0.045)
    box('read_arm_b', (0.13, 0.74, 0.12), (chx + 0.38, chy, 0.47), P['ink_fab'], bevel=0.045)
    for j, (lx, ly) in enumerate([(-0.3, -0.28), (0.3, -0.28), (-0.3, 0.3), (0.3, 0.3)]):
        cyl('read_leg_%d' % j, 0.022, 0.26, (chx + lx, chy + ly, 0.13), P['black_mtl'], verts=8)
    cyl('read_side', 0.22, 0.04, (chx - 0.82, chy - 0.42, 0.48), P['marble'], verts=20)
    cyl('read_side_stem', 0.04, 0.46, (chx - 0.82, chy - 0.42, 0.23), P['black_mtl'], verts=10)
    books('read_books', (chx - 0.82, chy - 0.42, 0.5), P, count=2, w=0.2, d=0.24, rot=0.3)

    # the west face of the partition carries art and a tall plant
    art('bed_art_w_a', (4.2, 1.6, 1.75), P, w=0.85, h=1.15, face='x', m=P['art_b'])
    art('bed_art_w_b', (4.2, 2.75, 1.62), P, w=0.62, h=0.82, face='x', m=P['art_a'])
    plant('bed_plant_w', (4.72, 0.15, 0.0), P, h=1.2, pot_r=0.23, leaves=12)
    floor_lamp('bed_floor_lamp', (11.3, 2.1, 0.0), P, h=1.55)
    plant('bed_plant', (11.2, -0.9, 0.0), P, h=1.3, leaves=13)
    downlights('bed_dl', 5.0, 10.6, 3.4, CEIL, P, count=5)
    pendant('bed_pend_a', (bx - 1.62, ny - 0.42, 2.15), P, r=0.12, drop=1.05, shade='dome')
    pendant('bed_pend_b', (bx + 1.62, ny - 0.42, 2.15), P, r=0.12, drop=1.05, shade='dome')

# ------------------------------------------------------------------ PATIO
def build_patio(P):
    into('Patio')
    cx, cy = 16.4, 0.9
    box('patio_rug', (3.8, 3.0, 0.02), (cx, cy, -0.07), P['rug_deep'], bevel=0.008)

    # low modular lounge, L-shaped, opening back toward the house
    box('pl_base', (1.0, 3.2, 0.24), (cx + 1.7, cy + 0.2, 0.05), P['concrete'], bevel=0.02)
    box('pl_seat', (0.94, 3.1, 0.16), (cx + 1.7, cy + 0.2, 0.25), P['linen'], bevel=0.06, segs=3)
    box('pl_back', (0.22, 3.1, 0.46), (cx + 2.08, cy + 0.2, 0.5), P['linen'], bevel=0.06, segs=3)
    box('pl_base_b', (2.4, 0.95, 0.24), (cx + 0.1, cy + 1.85, 0.05), P['concrete'], bevel=0.02)
    box('pl_seat_b', (2.34, 0.9, 0.16), (cx + 0.1, cy + 1.85, 0.25), P['linen'], bevel=0.06, segs=3)
    box('pl_back_b', (2.34, 0.22, 0.46), (cx + 0.1, cy + 2.2, 0.5), P['linen'], bevel=0.06, segs=3)
    cushion('p_cush_a', (cx + 1.9, cy + 1.2, 0.47), P, m=P['rust'], rot=0.1)
    cushion('p_cush_b', (cx + 1.9, cy - 0.8, 0.47), P, m=P['ink_fab'], rot=-0.12)
    cushion('p_cush_c', (cx - 0.6, cy + 2.0, 0.47), P, m=P['boucle'], rot=1.6)
    throw('p_throw', (cx + 1.62, cy - 1.0, 0.34), P, m=P['wool'], size=(0.7, 0.8))

    # fire table as the focal point
    cyl('fire_base', 0.6, 0.32, (cx, cy - 0.35, 0.16), P['concrete'], verts=26, bevel=0.02)
    cyl('fire_rim', 0.63, 0.06, (cx, cy - 0.35, 0.33), P['travertine'], verts=26)
    cyl('fire_bed', 0.47, 0.05, (cx, cy - 0.35, 0.345), P['screen'], verts=24)
    for i in range(11):
        a = i * 2.399
        r = 0.31 * ((i % 3) / 3.0 + 0.32)
        sphere('fire_stone_%d' % i, 0.062,
               (cx + math.cos(a) * r, cy - 0.35 + math.sin(a) * r, 0.375),
               P['screen'], segs=8, rings=5, scale=(1, 1, 0.65))
    # flame: a cluster of tapered cones so it reads as fire, not a lit disc
    for i in range(7):
        a = i * 0.897 + 0.3
        r = 0.06 + (i % 4) * 0.055
        hgt = 0.09 + (i % 4) * 0.045
        cone('fire_flame_%d' % i, 0.032 + (i % 2) * 0.012, 0.003, hgt,
             (cx + math.cos(a) * r, cy - 0.35 + math.sin(a) * r, 0.365 + hgt / 2),
             P['flame'], verts=8)
    cyl('fire_embers', 0.42, 0.012, (cx, cy - 0.35, 0.358), P['ember'], verts=22)

    # drinks table
    cyl('p_side_top', 0.27, 0.05, (cx + 0.75, cy - 1.75, 0.41), P['travertine'], verts=22)
    cyl('p_side_base', 0.23, 0.38, (cx + 0.75, cy - 1.75, 0.19), P['travertine'], verts=22)
    for i in range(2):
        cyl('p_glass_%d' % i, 0.035, 0.12, (cx + 0.66 + i * 0.18, cy - 1.7, 0.5), P['glass'], verts=12)

    # two low sling chairs, set wide so they frame rather than block
    for i, (px, py, yaw) in enumerate(((cx - 1.85, cy - 0.5, M(-58)), (cx - 1.25, cy - 2.25, M(-24)))):
        ca, sa = math.cos(yaw), math.sin(yaw)
        def po(dx, dy):
            return (px + dx * ca - dy * sa, py + dx * sa + dy * ca)
        box('sling_%d_seat' % i, (0.7, 0.68, 0.11), (*po(0, 0), 0.32), P['ink_fab'],
            rot=(0, 0, yaw), bevel=0.04, segs=3)
        box('sling_%d_back' % i, (0.7, 0.14, 0.42), (*po(0, -0.31), 0.53), P['ink_fab'],
            rot=(M(16), 0, yaw), bevel=0.04, segs=3)
        for j, (lx, ly) in enumerate([(-0.29, -0.26), (0.29, -0.26), (-0.29, 0.28), (0.29, 0.28)]):
            cyl('sling_%d_leg_%d' % (i, j), 0.02, 0.26, (*po(lx, ly), 0.13), P['walnut'], verts=8)

    # planting along the open edge + festoon lighting
    for i in range(4):
        grass_pot('p_grass_%d' % i, (19.3, -3.4 + i * 2.4, -0.1), P, h=0.9, r=0.3)
    plant('p_plant', (12.9, 4.1, -0.1), P, h=1.6, pot_r=0.3, leaves=15)
    plant('p_plant_b', (18.4, -4.5, -0.1), P, h=1.3, pot_r=0.26, leaves=12)
    for row, yy in enumerate((-4.1, 4.5)):
        for i in range(14):
            t = i / 13.0
            sag = math.sin(t * math.pi) * 0.26
            sphere('p_bulb_%d_%02d' % (row, i), 0.045,
                   (12.9 + t * 6.4, yy, CEIL + 0.12 - sag), P['lamp'], segs=10, rings=6)

