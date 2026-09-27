# -*- coding: utf-8 -*-
"""The site — terrace, reflecting pool, lawn, planting, trees, path lighting."""
import math, random
random.seed(7)
M = math.radians

def site_palette(P):
    P['lawn']    = mat('Lawn',        hx('#2c3a2c'), rough=0.98)
    P['water']   = mat('Water',       hx('#0d1a24'), rough=0.06, metal=0.55)
    P['coping']  = mat('Coping',      hx('#b9b4ab'), rough=0.6)
    P['deck']    = mat('Deck Stone',  hx('#9d9890'), rough=0.72)
    P['hedge']   = mat('Hedge',       hx('#2b3b2e'), rough=0.95)
    P['bark']    = mat('Bark',        hx('#3a3129'), rough=0.9)
    P['canopy']  = mat('Canopy',      hx('#33452f'), rough=0.85)
    P['canopy2'] = mat('Canopy Warm', hx('#3f4f33'), rough=0.85)
    P['soffit']  = mat('Soffit Teak', hx('#6d4c33'), rough=0.62)
    P['bollard'] = mat('Bollard',     hx('#1a1c1f'), rough=0.4, metal=0.8)
    return P

def tree(n, loc, P, h=5.2, spread=2.1, tufts=6, lean=0.0):
    """Low-poly canopy tree — reads as a silhouette at dusk."""
    cyl('%s_trunk' % n, 0.16, h * 0.62, (loc[0], loc[1], loc[2] + h * 0.31), P['bark'],
        rot=(0, lean, 0), verts=8)
    for i in range(tufts):
        a = i * 2.399
        rad = spread * (0.28 + 0.52 * ((i % 3) / 3.0))
        zz = loc[2] + h * (0.58 + 0.34 * ((i % 4) / 4.0))
        sphere('%s_tuft_%d' % (n, i), spread * 0.56,
               (loc[0] + math.cos(a) * rad * 0.7, loc[1] + math.sin(a) * rad * 0.7, zz),
               P['canopy'] if i % 2 else P['canopy2'],
               segs=12, rings=7, scale=(1.0, 1.0, 0.66))

def hedge_run(n, x0, x1, y, P, h=0.95, d=0.85):
    box(n, (x1 - x0, d, h), ((x0 + x1) / 2, y, h / 2 - 0.3), P['hedge'], bevel=0.12, segs=2)

def bollard(n, loc, P, h=0.62):
    cyl('%s_post' % n, 0.045, h, (loc[0], loc[1], loc[2] + h / 2), P['bollard'], verts=10)
    cyl('%s_cap' % n, 0.055, 0.03, (loc[0], loc[1], loc[2] + h), P['bollard'], verts=10)
    cyl('%s_glow' % n, 0.042, 0.06, (loc[0], loc[1], loc[2] + h - 0.055), P['lamp'], verts=10)

def build_site(P):
    site_palette(P)
    into('Site')

    # --- lawn + far grade
    plane('lawn', (190, 190), (0, -6, -0.36), P['lawn'])

    # --- stone terrace along the glazed elevation (flush with the floor)
    box('terrace', (39.0, 5.6, 0.34), (1.0, -7.7, -0.17), P['deck'])
    box('terrace_edge', (39.0, 0.12, 0.1), (1.0, -10.44, -0.05), P['coping'])

    # --- reflecting pool: the facade doubles in it
    px0, px1, py0, py1 = -13.5, 6.5, -15.6, -11.2
    box('pool_basin', (px1 - px0 + 0.7, py1 - py0 + 0.7, 0.5),
        ((px0 + px1) / 2, (py0 + py1) / 2, -0.58), P['coping'])
    box('site_pool', (px1 - px0, py1 - py0, 0.06),
        ((px0 + px1) / 2, (py0 + py1) / 2, -0.28), P['water'])
    for tag, sz, loc in (
        ('n', (px1 - px0 + 0.7, 0.36, 0.1), ((px0 + px1) / 2, py1 + 0.17, -0.26)),
        ('s', (px1 - px0 + 0.7, 0.36, 0.1), ((px0 + px1) / 2, py0 - 0.17, -0.26)),
        ('w', (0.36, py1 - py0 + 0.7, 0.1), (px0 - 0.17, (py0 + py1) / 2, -0.26)),
        ('e', (0.36, py1 - py0 + 0.7, 0.1), (px1 + 0.17, (py0 + py1) / 2, -0.26))):
        box('pool_cope_%s' % tag, sz, loc, P['coping'])
    # stepping stones crossing to the terrace
    for i in range(4):
        box('step_%d' % i, (1.5, 0.9, 0.12), (8.9, -11.0 - i * 1.35, -0.28), P['coping'])

    # --- planting: beds either side of the entry, hedges framing the lawn
    for i in range(6):
        hedge_run('hedge_n_%d' % i, -20.0 + i * 5.7, -15.1 + i * 5.7, 8.6 + (i % 3) * 0.55,
                  P, h=0.85 + (i % 3) * 0.32, d=1.0 + (i % 2) * 0.35)
    hedge_run('hedge_pool_w', -20.5, -15.5, -13.4, P, h=0.8, d=1.0)
    hedge_run('hedge_pool_e', 8.5, 14.0, -13.4, P, h=0.8, d=1.0)
    for i in range(7):
        grass_pot('site_grass_%d' % i, (-17.4 + i * 0.0, -9.6 + i * 1.6, -0.3), P, h=0.8, r=0.26)
    for i in range(5):
        grass_pot('site_grass_e_%d' % i, (13.6, -9.0 + i * 1.7, -0.36), P, h=0.75, r=0.24)

    # --- trees: a loose grove, clear of the approach sightline
    tree('tree_w1', (-25.5, 1.0, -0.34), P, h=6.4, spread=2.6, tufts=7)
    tree('tree_w2', (-21.5, 6.5, -0.34), P, h=5.2, spread=2.1, tufts=6, lean=0.06)
    tree('tree_w3', (-30.0, -4.0, -0.34), P, h=5.6, spread=2.3, tufts=6)
    tree('tree_e1', (25.5, -1.0, -0.34), P, h=6.0, spread=2.5, tufts=7)
    tree('tree_e2', (22.5, 7.0, -0.34), P, h=5.0, spread=2.0, tufts=6, lean=-0.05)
    tree('tree_n1', (-7.0, 14.5, -0.34), P, h=6.8, spread=2.8, tufts=7)
    tree('tree_n2', (5.0, 16.5, -0.34), P, h=5.4, spread=2.2, tufts=6)
    tree('tree_n3', (-18.0, 13.0, -0.34), P, h=6.0, spread=2.4, tufts=6)
    tree('tree_s1', (-30.0, -20.0, -0.34), P, h=6.2, spread=2.5, tufts=7)
    tree('tree_s2', (24.0, -18.0, -0.34), P, h=5.8, spread=2.4, tufts=6)


    # --- path lighting along the walk and the pool edge
    for i in range(6):
        bollard('boll_w_%d' % i, (-17.6, -10.5 - i * 2.2, -0.3), P)
    for i in range(5):
        bollard('boll_e_%d' % i, (10.2, -11.4 - i * 2.2, -0.34), P)

def refine_roof(P):
    """Warm timber soffit under the overhang so the elevation reads as architecture."""
    into('Shell')
    ov = 0.8
    box('soffit_south', (HX1 - HX0 + 1.6, ov, 0.05),
        ((HX0 + HX1) / 2, GY0 - ov / 2, CEIL + 0.27), P['soffit'])
    box('soffit_north', (HX1 - HX0 + 1.6, ov, 0.05),
        ((HX0 + HX1) / 2, RY1 + ov / 2, CEIL + 0.27), P['soffit'])
    box('soffit_west', (ov, (RY1 - GY0) + 1.6, 0.05),
        (HX0 - ov / 2, (GY0 + RY1) / 2, CEIL + 0.27), P['soffit'])
    # Vertical timber fins screening part of the elevation. They start east of
    # the entry bay so the approach — and the camera — walks straight in.
    for i in range(9):
        box('fin_%02d' % i, (0.09, 0.3, CEIL + 0.1),
            (-12.9 + i * 0.62, GY0 - 0.62, (CEIL + 0.1) / 2), P['soffit'])
    # a chimney-like service volume breaking the roofline
    box('flue', (0.9, 0.9, 1.5), (-9.4, 3.2, CEIL + 1.05), P['accent'])
