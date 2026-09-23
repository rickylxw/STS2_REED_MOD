#!/usr/bin/env python3
"""
generate_new_cards.py
=====================
Registers renderers for the 2026-09 batch of new Reed cards/powers and
generates their SVGs, reusing the helpers from generate_all_svg.py.
"""

import generate_all_svg as g
from generate_all_svg import (
    SVG, add_bg, add_glow, add_soft_glow, add_blur_only, lin_grad, rad_grad,
    add_atmosphere, add_embers, add_ash_particles, add_motion_lines,
    add_spark_burst, flame_path, add_bottom_glow,
    C_WHITE_HOT, C_YELLOW, C_YELLOW3, C_ORANGE, C_ORANGE2, C_ORANGE3,
    C_ORANGE4, C_DEEP_ORANGE, C_DEEP_ORANGE2, C_DEEP_ORANGE3,
    C_DARK_RED, C_DARK_RED2, C_DARK_BG, C_DARK_BG2, ASH_COLORS,
)


# =====================================================================
#  CARD RENDERERS (250 x 190)
# =====================================================================

def render_emberscales(s):
    """Scales of overlapping ember plates."""
    glow = add_glow(s, 2.5)
    add_bg(s)
    g_plate = lin_grad(s, [("0%", C_DEEP_ORANGE), ("50%", C_DARK_RED), ("100%", C_DARK_BG)])
    g_edge = lin_grad(s, [("0%", C_YELLOW3), ("100%", C_ORANGE3)])
    add_atmosphere(s, color=C_DEEP_ORANGE, opacity=0.06)
    add_ash_particles(s, 8, 9101)
    add_embers(s, 6, 9102, glow)
    rows = [(30, 40), (80, 40), (130, 40), (55, 85), (105, 85), (155, 85), (30, 130), (80, 130), (130, 130), (180, 130)]
    for i, (cx, cy) in enumerate(rows):
        s.draw(f'  <path d="M {cx-28} {cy+22} Q {cx} {cy-26} {cx+28} {cy+22} '
               f'Q {cx} {cy+6} {cx-28} {cy+22} Z" fill="url(#{g_plate})" '
               f'stroke="url(#{g_edge})" stroke-width="1.5" opacity="0.85" filter="url(#{glow})"/>')
    add_bottom_glow(s, 125, 175, 70, 10, glow=glow)


def render_ashembrace(s):
    """Arms of grey ash embracing a warm core."""
    glow = add_glow(s, 2.5)
    soft = add_soft_glow(s, 4)
    add_bg(s)
    g_core = rad_grad(s, [("0%", C_WHITE_HOT), ("40%", C_YELLOW), ("100%", C_ORANGE)])
    g_ash = lin_grad(s, [("0%", ASH_COLORS[2]), ("100%", ASH_COLORS[0])])
    add_atmosphere(s, color=C_DEEP_ORANGE, opacity=0.07)
    add_ash_particles(s, 16, 9111)
    add_embers(s, 5, 9112, glow)
    s.draw(f'  <circle cx="125" cy="95" r="34" fill="url(#{g_core})" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="95" r="12" fill="{C_WHITE_HOT}" opacity="0.85"/>')
    for dx, dy, r in [(-52, -18, 34), (52, -18, 34), (-60, 22, 30), (60, 22, 30)]:
        s.draw(f'  <path d="M {125+dx} {95+dy} a {r} {r*0.7} 0 0 1 { -dx*1.2 } { -dy }" '
               f'stroke="url(#{g_ash})" stroke-width="14" fill="none" opacity="0.75" '
               f'stroke-linecap="round" filter="url(#{soft})"/>')
    add_spark_burst(s, 125, 95, 8, 9113, 22, glow=glow)


def render_scorchdetonation(s):
    """Target ring detonating a scorch mark."""
    glow = add_glow(s, 3)
    add_bg(s)
    g_blast = rad_grad(s, [("0%", C_WHITE_HOT), ("30%", C_YELLOW), ("60%", C_ORANGE), ("100%", C_DEEP_ORANGE2, 0.0)])
    add_atmosphere(s, color=C_DEEP_ORANGE, opacity=0.08)
    add_embers(s, 12, 9121, glow)
    add_motion_lines(s, [(20, 40, 70, 70, 2, 0.35), (230, 40, 180, 70, 2, 0.35),
                         (20, 150, 70, 120, 2, 0.35), (230, 150, 180, 120, 2, 0.35)])
    s.draw(f'  <circle cx="125" cy="95" r="55" fill="url(#{g_blast})" filter="url(#{glow})"/>')
    for r, sw, op in [(70, 3, 0.7), (82, 1.5, 0.45)]:
        s.draw(f'  <circle cx="125" cy="95" r="{r}" fill="none" stroke="{C_ORANGE3}" '
               f'stroke-width="{sw}" opacity="{op}" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="95" r="10" fill="{C_WHITE_HOT}" opacity="0.9"/>')
    add_spark_burst(s, 125, 95, 14, 9122, 40, glow=glow)


def render_backdraft(s):
    """Reverse flame wave blasting outward."""
    glow = add_glow(s, 3)
    add_bg(s)
    g_wave = lin_grad(s, [("0%", C_YELLOW3), ("50%", C_ORANGE), ("100%", C_DEEP_ORANGE2)])
    add_atmosphere(s, color=C_ORANGE, opacity=0.07)
    add_embers(s, 10, 9131, glow)
    cx, cy = 125, 95
    for i, (r, op) in enumerate([(30, 0.85), (55, 0.55), (80, 0.3)]):
        s.draw(f'  <path d="M {cx-r} {cy+30} Q {cx} {cy-r*1.1} {cx+r} {cy+30} '
               f'Q {cx} {cy-r*0.5} {cx-r} {cy+30} Z" fill="none" stroke="url(#{g_wave})" '
               f'stroke-width="{5-i}" opacity="{op}" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="{cx}" cy="{cy}" r="14" fill="url(#{g_wave})" filter="url(#{glow})"/>')
    add_spark_burst(s, cx, cy, 12, 9132, 35, glow=glow)


def render_emberafterglow(s):
    """Fading embers trailing light."""
    glow = add_glow(s, 2.5)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    g_trail = lin_grad(s, [("0%", C_WHITE_HOT), ("40%", C_YELLOW), ("100%", C_DARK_RED, 0.0)])
    add_atmosphere(s, color=C_DEEP_ORANGE, opacity=0.06)
    add_ash_particles(s, 10, 9141)
    add_embers(s, 9, 9142, glow)
    s.draw(f'  <path d="M 40 150 Q 90 110 130 80 Q 170 55 210 40" stroke="url(#{g_trail})" '
           f'stroke-width="10" fill="none" opacity="0.7" stroke-linecap="round" filter="url(#{soft})"/>')
    for cx, cy, r in [(40, 150, 9), (90, 115, 6), (140, 78, 4.5), (185, 50, 3), (215, 38, 2)]:
        s.draw(f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="{C_ORANGE}" opacity="0.8" filter="url(#{glow})"/>')
        s.draw(f'  <circle cx="{cx}" cy="{cy}" r="{r*0.4:.1f}" fill="{C_WHITE_HOT}" opacity="0.9"/>')
    add_spark_burst(s, 40, 150, 7, 9143, 18, glow=glow)


def render_residualwarmth(s):
    """Warm hand cupping the last ember."""
    glow = add_glow(s, 2.5)
    soft = add_soft_glow(s, 4)
    add_bg(s)
    g_ember = rad_grad(s, [("0%", C_WHITE_HOT), ("45%", C_YELLOW), ("100%", C_ORANGE2)])
    add_atmosphere(s, color=C_DEEP_ORANGE, opacity=0.06)
    add_embers(s, 6, 9151, glow)
    s.draw(f'  <path d="M 60 150 Q 85 120 120 118 L 175 118 Q 195 120 192 132 '
           f'Q 190 142 172 142 L 150 142 L 190 150 Q 200 156 190 162 L 120 162 '
           f'Q 85 165 60 150 Z" fill="#3a2418" stroke="{C_DEEP_ORANGE3}" '
           f'stroke-width="2" opacity="0.9" filter="url(#{soft})"/>')
    s.draw(f'  <circle cx="150" cy="95" r="24" fill="url(#{g_ember})" filter="url(#{glow})"/>')
    s.draw(f'  <path d="{flame_path(150, 82, 42, 13, 3, 9152)}" fill="{C_ORANGE}" '
           f'opacity="0.85" filter="url(#{glow})"/>')
    s.draw(f'  <path d="{flame_path(150, 80, 26, 7, 2, 9153)}" fill="{C_YELLOW3}" opacity="0.9"/>')
    add_bottom_glow(s, 150, 170, 60, 9, glow=glow)


def render_martyrflame(s):
    """A falling figure dissolving into flame."""
    glow = add_glow(s, 2.5)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    g_body = lin_grad(s, [("0%", C_YELLOW3), ("60%", C_ORANGE), ("100%", C_DEEP_ORANGE2)])
    add_atmosphere(s, color=C_DEEP_ORANGE, opacity=0.07)
    add_ash_particles(s, 8, 9161)
    add_embers(s, 10, 9162, glow)
    cx, cy = 125, 85
    s.draw(f'  <circle cx="{cx}" cy="{cy-32}" r="11" fill="url(#{g_body})" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M {cx} {cy-20} L {cx-16} {cy+16} L {cx-6} {cy+52} L {cx+6} {cy+52} '
           f'L {cx+16} {cy+16} Z" fill="url(#{g_body})" opacity="0.85" filter="url(#{soft})"/>')
    s.draw(f'  <path d="M {cx-14} {cy-8} L {cx-40} {cy+24}" stroke="{C_ORANGE}" '
           f'stroke-width="7" stroke-linecap="round" opacity="0.8" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M {cx+14} {cy-8} L {cx+44} {cy-30}" stroke="{C_ORANGE}" '
           f'stroke-width="7" stroke-linecap="round" opacity="0.8" filter="url(#{glow})"/>')
    for i, (fx, fy, fh, fw) in enumerate([(cx-10, cy+62, 36, 10), (cx+10, cy+62, 44, 12), (cx, cy+70, 56, 14)]):
        s.draw(f'  <path d="{flame_path(fx, fy, fh, fw, 3, 9163+i)}" fill="{C_ORANGE3}" '
               f'opacity="0.7" filter="url(#{glow})"/>')
    add_bottom_glow(s, cx, 175, 60, 10, glow=glow)


def render_dragonsmajesty(s):
    """Dragon head silhouette looming with a commanding gaze."""
    glow = add_glow(s, 2.5)
    soft = add_soft_glow(s, 4)
    add_bg(s)
    g_head = lin_grad(s, [("0%", C_DEEP_ORANGE), ("55%", C_DARK_RED), ("100%", C_DARK_BG)])
    g_eye = rad_grad(s, [("0%", C_WHITE_HOT), ("60%", C_YELLOW), ("100%", C_ORANGE)])
    add_atmosphere(s, color=C_DEEP_ORANGE, opacity=0.06)
    add_ash_particles(s, 7, 9171)
    add_embers(s, 5, 9172, glow)
    cx, cy = 125, 80
    s.draw(f'  <path d="M {cx-55} {cy+28} Q {cx-50} {cy-30} {cx} {cy-38} '
           f'Q {cx+50} {cy-30} {cx+55} {cy+28} Q {cx+30} {cy+8} {cx+70} {cy+44} '
           f'Q {cx+20} {cy+52} {cx} {cy+30} Q {cx-20} {cy+52} {cx-70} {cy+44} '
           f'Q {cx-30} {cy+8} {cx-55} {cy+28} Z" fill="url(#{g_head})" '
           f'stroke="{C_ORANGE3}" stroke-width="1.5" opacity="0.9" filter="url(#{soft})"/>')
    for ex in (cx-24, cx+24):
        s.draw(f'  <ellipse cx="{ex}" cy="{cy+2}" rx="9" ry="5" fill="url(#{g_eye})" filter="url(#{glow})"/>')
        s.draw(f'  <line x1="{ex}" y1="{cy-4}" x2="{ex}" y2="{cy+8}" stroke="{C_DARK_BG}" stroke-width="2"/>')
    for hx, hy in [(cx-40, cy-26), (cx-20, cy-34), (cx+20, cy-34), (cx+40, cy-26)]:
        s.draw(f'  <path d="M {hx} {hy} L {hx+6} {hy-22} L {hx+12} {hy+2} Z" '
               f'fill="{C_ORANGE4}" opacity="0.8" filter="url(#{glow})"/>')
    add_bottom_glow(s, cx, 172, 60, 10, glow=glow)


# ---- legacy entry kept for theme dict parity ----
def render_ashstorm(s):
    """Violent ash storm vortex."""
    glow = add_glow(s, 2.5)
    soft = add_soft_glow(s, 4)
    add_bg(s)
    g_storm = rad_grad(s, [("0%", ASH_COLORS[1], 0.8), ("70%", ASH_COLORS[3], 0.6), ("100%", C_DARK_BG, 0.0)])
    add_atmosphere(s, color=C_DEEP_ORANGE, opacity=0.05)
    add_ash_particles(s, 26, 9181)
    add_embers(s, 6, 9182, glow)
    for i, (rx, ry, op) in enumerate([(90, 30, 0.7), (65, 22, 0.55), (42, 15, 0.4)]):
        s.draw(f'  <ellipse cx="125" cy="95" rx="{rx}" ry="{ry}" fill="none" '
               f'stroke="url(#{g_storm})" stroke-width="{7-i*2}" opacity="{op}" '
               f'filter="url(#{soft})" transform="rotate({-20+i*8} 125 95)"/>')
    s.draw(f'  <circle cx="125" cy="95" r="10" fill="{C_ORANGE}" opacity="0.6" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="95" r="4" fill="{C_WHITE_HOT}" opacity="0.8"/>')
    add_spark_burst(s, 125, 95, 6, 9183, 20, glow=glow)


# =====================================================================
#  POWER RENDERERS (64 x 64)
# =====================================================================

def render_ashembracepower(s):
    """Ashen Embrace — ash arms around a core."""
    glow = add_glow(s, 1.5)
    soft = add_soft_glow(s, 3)
    add_bg(s, cx="50%", cy="50%", r="60%")
    g_core = rad_grad(s, [("0%", C_WHITE_HOT), ("40%", C_YELLOW), ("100%", C_ORANGE)])
    g_ash = lin_grad(s, [("0%", ASH_COLORS[2]), ("100%", ASH_COLORS[0])])
    add_ash_particles(s, 8, 9201)
    add_embers(s, 3, 9202, glow)
    s.draw(f'  <circle cx="32" cy="32" r="13" fill="url(#{g_core})" filter="url(#{glow})"/>')
    for sx in (-1, 1):
        s.draw(f'  <path d="M {32+sx*22} 20 Q {32+sx*30} 32 {32+sx*22} 46" '
               f'stroke="url(#{g_ash})" stroke-width="6" fill="none" opacity="0.75" '
               f'stroke-linecap="round" filter="url(#{soft})"/>')
    s.draw(f'  <circle cx="32" cy="32" r="4" fill="{C_WHITE_HOT}" opacity="0.9"/>')


def render_emberafterglowpower(s):
    """Ember Afterglow — fading ember trail."""
    glow = add_glow(s, 1.5)
    soft = add_soft_glow(s, 3)
    add_bg(s, cx="50%", cy="50%", r="60%")
    g_trail = lin_grad(s, [("0%", C_WHITE_HOT), ("50%", C_YELLOW), ("100%", C_DARK_RED, 0.0)])
    add_embers(s, 5, 9211, glow)
    s.draw(f'  <path d="M 12 48 Q 26 36 38 26 Q 48 18 56 12" stroke="url(#{g_trail})" '
           f'stroke-width="5" fill="none" opacity="0.8" stroke-linecap="round" filter="url(#{soft})"/>')
    for cx, cy, r in [(12, 48, 3.5), (28, 36, 2.5), (42, 24, 1.8), (54, 14, 1.2)]:
        s.draw(f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="{C_ORANGE}" opacity="0.85" filter="url(#{glow})"/>')


def render_dragonsmajestypower(s):
    """Dragonborn Majesty — commanding dragon eye."""
    glow = add_glow(s, 1.5)
    add_bg(s, cx="50%", cy="50%", r="60%")
    g_eye = rad_grad(s, [("0%", C_WHITE_HOT), ("60%", C_YELLOW), ("100%", C_ORANGE)])
    g_head = lin_grad(s, [("0%", C_DEEP_ORANGE), ("100%", C_DARK_RED)])
    add_embers(s, 3, 9221, glow)
    s.draw(f'  <path d="M 8 40 Q 14 16 32 14 Q 50 16 56 40 Q 40 32 32 40 Q 24 32 8 40 Z" '
           f'fill="url(#{g_head})" stroke="{C_ORANGE3}" stroke-width="1" opacity="0.9" filter="url(#{glow})"/>')
    s.draw(f'  <ellipse cx="32" cy="30" rx="12" ry="7" fill="url(#{g_eye})" filter="url(#{glow})"/>')
    s.draw(f'  <line x1="32" y1="23" x2="32" y2="37" stroke="{C_DARK_BG}" stroke-width="2.5"/>')


# =====================================================================
#  GAP-FILL BATCH (2026-09): 5 cards + 1 power
# =====================================================================

def render_stokeflame(s):
    """Fan fanning a small flame into counters."""
    glow = add_glow(s, 2.5)
    add_bg(s)
    g_fan = lin_grad(s, [("0%", C_ORANGE), ("100%", C_DARK_RED)])
    add_atmosphere(s, color=C_DEEP_ORANGE, opacity=0.06)
    add_embers(s, 7, 9301, glow)
    s.draw(f'  <path d="M 150 30 L 175 130 L 135 118 Z" fill="url(#{g_fan})" opacity="0.85" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 165 34 L 205 118 L 162 112 Z" fill="url(#{g_fan})" opacity="0.6" filter="url(#{glow})"/>')
    s.draw(f'  <path d="{flame_path(115, 150, 80, 26, 4, 9302)}" fill="{C_ORANGE}" opacity="0.9" filter="url(#{glow})"/>')
    s.draw(f'  <path d="{flame_path(115, 148, 52, 15, 3, 9303)}" fill="{C_YELLOW3}" opacity="0.9"/>')
    s.draw(f'  <path d="{flame_path(115, 146, 28, 8, 2, 9304)}" fill="{C_WHITE_HOT}" opacity="0.9"/>')
    add_bottom_glow(s, 120, 172, 55, 9, glow=glow)


def render_dragonlance(s):
    """A lance piercing through a blazing sun."""
    glow = add_glow(s, 3)
    add_bg(s)
    g_sun = rad_grad(s, [("0%", C_WHITE_HOT), ("40%", C_YELLOW), ("100%", C_DEEP_ORANGE2, 0.0)])
    g_lance = lin_grad(s, [("0%", C_YELLOW3), ("100%", C_DEEP_ORANGE)])
    add_atmosphere(s, color=C_DEEP_ORANGE, opacity=0.07)
    add_embers(s, 8, 9311, glow)
    s.draw(f'  <circle cx="150" cy="80" r="52" fill="url(#{g_sun})" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 20 165 L 185 60 L 215 42 L 196 76 L 178 74 Z" fill="url(#{g_lance})" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 20 165 L 40 158 L 52 170 Z" fill="{C_DARK_RED}" opacity="0.9"/>')
    add_spark_burst(s, 150, 80, 10, 9312, 30, glow=glow)


def render_flameparity(s):
    """Two mirrored flames in perfect balance."""
    glow = add_glow(s, 2.5)
    soft = add_soft_glow(s, 4)
    add_bg(s)
    g_l = lin_grad(s, [("0%", C_YELLOW3), ("100%", C_ORANGE)])
    g_r = lin_grad(s, [("0%", C_ORANGE), ("100%", C_DEEP_ORANGE2)])
    add_atmosphere(s, color=C_DEEP_ORANGE, opacity=0.06)
    add_embers(s, 6, 9321, glow)
    for dx, grad in [(-42, g_l), (42, g_r)]:
        s.draw(f'  <path d="{flame_path(125+dx, 150, 95, 24, 3, 9322+dx)}" fill="url(#{grad})" '
               f'opacity="0.85" filter="url(#{soft})"/>')
        s.draw(f'  <path d="{flame_path(125+dx, 148, 60, 13, 2, 9323+dx)}" fill="{C_WHITE_HOT}" opacity="0.75"/>')
    s.draw(f'  <line x1="125" y1="35" x2="125" y2="165" stroke="{C_ORANGE3}" '
           f'stroke-width="2" opacity="0.5" filter="url(#{glow})"/>')
    add_bottom_glow(s, 125, 172, 70, 10, glow=glow)


def render_everburning(s):
    """An eternal flame ring that never fades."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    g_ring = lin_grad(s, [("0%", C_YELLOW), ("50%", C_ORANGE), ("100%", C_DEEP_ORANGE2)])
    add_atmosphere(s, color=C_DEEP_ORANGE, opacity=0.08)
    add_embers(s, 10, 9331, glow)
    cx, cy = 125, 95
    s.draw(f'  <circle cx="{cx}" cy="{cy}" r="52" fill="none" stroke="url(#{g_ring})" '
           f'stroke-width="9" opacity="0.85" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="{cx}" cy="{cy}" r="66" fill="none" stroke="url(#{g_ring})" '
           f'stroke-width="3" opacity="0.5" filter="url(#{soft})"/>')
    s.draw(f'  <path d="{flame_path(cx, cy+30, 70, 20, 4, 9332)}" fill="{C_ORANGE}" opacity="0.9" filter="url(#{glow})"/>')
    s.draw(f'  <path d="{flame_path(cx, cy+28, 45, 11, 3, 9333)}" fill="{C_WHITE_HOT}" opacity="0.9"/>')
    add_spark_burst(s, cx, cy, 8, 9334, 26, glow=glow)


def render_draconiccrush(s):
    """A massive dragon fist slamming down."""
    glow = add_glow(s, 3)
    add_bg(s)
    g_fist = lin_grad(s, [("0%", C_DEEP_ORANGE), ("60%", C_DARK_RED), ("100%", C_DARK_BG)])
    add_atmosphere(s, color=C_DEEP_ORANGE, opacity=0.07)
    add_embers(s, 9, 9341, glow)
    cx, cy = 125, 70
    s.draw(f'  <path d="M {cx-55} {cy} Q {cx-60} {cy-42} {cx-10} {cy-46} '
           f'Q {cx+45} {cy-50} {cx+58} {cy-8} Q {cx+62} {cy+28} {cx+20} {cy+40} '
           f'Q {cx-30} {cy+52} {cx-55} {cy} Z" fill="url(#{g_fist})" opacity="0.92" filter="url(#{glow})"/>')
    for kx in (cx-34, cx-10, cx+14, cx+38):
        s.draw(f'  <path d="M {kx} {cy-40} Q {kx+4} {cy-58} {kx+16} {cy-44} Q {kx+10} {cy-34} {kx} {cy-40} Z" '
               f'fill="{C_ORANGE4}" opacity="0.85" filter="url(#{glow})"/>')
    for i, (bx, br) in enumerate([(60, 14), (105, 18), (150, 16), (190, 12)]):
        s.draw(f'  <path d="M {bx-20} 190 Q {bx} {150-bx%30} {bx+20} 190 Z" fill="{C_ORANGE3}" '
               f'opacity="0.4" filter="url(#{glow})"/>')
    add_bottom_glow(s, cx, 182, 90, 12, color=C_DEEP_ORANGE2, opacity=0.45, glow=glow)


def render_everburningpower(s):
    """Everburning marker — unbroken flame ring."""
    glow = add_glow(s, 1.5)
    add_bg(s, cx="50%", cy="50%", r="60%")
    g_ring = lin_grad(s, [("0%", C_YELLOW), ("100%", C_DEEP_ORANGE2)])
    add_embers(s, 3, 9351, glow)
    s.draw(f'  <circle cx="32" cy="32" r="20" fill="none" stroke="url(#{g_ring})" '
           f'stroke-width="4" opacity="0.9" filter="url(#{glow})"/>')
    s.draw(f'  <path d="{flame_path(32, 42, 24, 8, 2, 9352)}" fill="{C_ORANGE}" opacity="0.9" filter="url(#{glow})"/>')
    s.draw(f'  <path d="{flame_path(32, 41, 14, 4, 1, 9353)}" fill="{C_WHITE_HOT}" opacity="0.9"/>')


# =====================================================================
#  DEATH/STRENGTH/RULES BATCH (2026-09): 6 cards + 3 powers
# =====================================================================

def render_heatwave(s):
    """Rolling heat waves sweeping across the field."""
    glow = add_glow(s, 2.5)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    g_wave = lin_grad(s, [("0%", C_YELLOW3), ("100%", C_DEEP_ORANGE2, 0.0)])
    add_atmosphere(s, color=C_ORANGE, opacity=0.08)
    add_embers(s, 12, 9401, glow)
    for i, (y, sw, op) in enumerate([(140, 12, 0.6), (105, 10, 0.5), (70, 8, 0.4), (38, 6, 0.3)]):
        s.draw(f'  <path d="M 10 {y+18} Q 65 {y-14} 125 {y} Q 185 {y+14} 240 {y-10}" '
               f'stroke="url(#{g_wave})" stroke-width="{sw}" fill="none" opacity="{op}" '
               f'stroke-linecap="round" filter="url(#{soft})"/>')
    add_spark_burst(s, 125, 95, 8, 9402, 30, glow=glow)


def render_dragondominance(s):
    """A dragon claw gripping a burning crown."""
    glow = add_glow(s, 2.5)
    add_bg(s)
    g_claw = lin_grad(s, [("0%", C_DEEP_ORANGE), ("100%", C_DARK_RED)])
    g_crown = rad_grad(s, [("0%", C_WHITE_HOT), ("50%", C_YELLOW), ("100%", C_ORANGE)])
    add_atmosphere(s, color=C_DEEP_ORANGE, opacity=0.07)
    add_embers(s, 7, 9411, glow)
    cx, cy = 125, 105
    s.draw(f'  <circle cx="{cx}" cy="62" r="24" fill="url(#{g_crown})" filter="url(#{glow})"/>')
    for hx in (-18, 0, 18):
        s.draw(f'  <path d="M {cx+hx-6} 48 L {cx+hx} 26 L {cx+hx+6} 48 Z" fill="{C_YELLOW3}" filter="url(#{glow})"/>')
    for ang in [(-30, -60), (-10, -40), (10, -40), (30, -60)]:
        s.draw(f'  <path d="M {cx+ang[0]*0.4} {cy-10} Q {cx+ang[0]} {cy+30} {cx+ang[0]*1.5} {cy+55}" '
               f'stroke="url(#{g_claw})" stroke-width="11" stroke-linecap="round" opacity="0.9" filter="url(#{glow})"/>')
    add_bottom_glow(s, cx, 178, 65, 10, glow=glow)


def render_pyre(s):
    """A funeral pyre with rising smoke and flame."""
    glow = add_glow(s, 2.5)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    add_atmosphere(s, color=C_DEEP_ORANGE, opacity=0.07)
    add_ash_particles(s, 10, 9421)
    add_embers(s, 9, 9422, glow)
    for x, y in [(70, 130), (95, 140), (120, 128), (145, 140), (170, 130), (82, 148), (110, 148), (138, 148), (160, 148)]:
        s.draw(f'  <line x1="{x-16}" y1="{y+10}" x2="{x+16}" y2="{y-6}" stroke="#4a2c18" '
               f'stroke-width="6" stroke-linecap="round" opacity="0.85"/>')
    s.draw(f'  <path d="{flame_path(120, 132, 95, 30, 5, 9423)}" fill="{C_ORANGE}" opacity="0.85" filter="url(#{glow})"/>')
    s.draw(f'  <path d="{flame_path(120, 130, 62, 18, 4, 9424)}" fill="{C_YELLOW3}" opacity="0.9"/>')
    s.draw(f'  <path d="{flame_path(120, 128, 32, 9, 2, 9425)}" fill="{C_WHITE_HOT}" opacity="0.9"/>')
    add_bottom_glow(s, 120, 170, 70, 11, color=C_DEEP_ORANGE2, opacity=0.4, glow=glow)


def render_emberreaper(s):
    """A scythe harvesting embers."""
    glow = add_glow(s, 2.5)
    add_bg(s)
    g_blade = lin_grad(s, [("0%", C_WHITE_HOT), ("50%", C_YELLOW3), ("100%", C_ORANGE)])
    add_atmosphere(s, color=C_DEEP_ORANGE, opacity=0.06)
    add_embers(s, 10, 9431, glow)
    s.draw(f'  <line x1="80" y1="165" x2="160" y2="35" stroke="#3a2418" stroke-width="7" stroke-linecap="round"/>')
    s.draw(f'  <path d="M 160 35 Q 215 45 205 95 Q 200 60 155 52 Z" fill="url(#{g_blade})" filter="url(#{glow})"/>')
    for cx, cy, r in [(90, 130, 5), (110, 100, 4), (130, 72, 3.5), (150, 50, 3)]:
        s.draw(f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="{C_ORANGE}" opacity="0.85" filter="url(#{glow})"/>')
        s.draw(f'  <circle cx="{cx}" cy="{cy}" r="{r*0.4:.1f}" fill="{C_WHITE_HOT}"/>')
    add_spark_burst(s, 180, 80, 7, 9432, 22, glow=glow)


def render_windblaze(s):
    """Wind streaks fanning flames sideways."""
    glow = add_glow(s, 2.5)
    soft = add_soft_glow(s, 4)
    add_bg(s)
    g_wind = lin_grad(s, [("0%", C_WHITE_HOT, 0.0), ("100%", C_YELLOW3)])
    add_atmosphere(s, color=C_ORANGE, opacity=0.07)
    add_embers(s, 11, 9441, glow)
    for i, (y, op) in enumerate([(55, 0.5), (95, 0.65), (135, 0.5)]):
        s.draw(f'  <path d="M 15 {y+14} Q 80 {y-10} 150 {y+4} Q 200 {y+12} 238 {y-6}" '
               f'stroke="url(#{g_wind})" stroke-width="3" fill="none" opacity="{op}" stroke-linecap="round" filter="url(#{soft})"/>')
    for fx, fy, fh, fw in [(95, 150, 75, 20), (160, 150, 55, 15), (45, 150, 48, 13)]:
        s.draw(f'  <path d="{flame_path(fx, fy, fh, fw, 4, 9442+fx)}" fill="{C_ORANGE}" '
               f'opacity="0.85" filter="url(#{glow})"/>')
        s.draw(f'  <path d="{flame_path(fx+6, fy-2, fh*0.6, fw*0.5, 3, 9443+fx)}" fill="{C_YELLOW3}" opacity="0.9"/>')
    add_bottom_glow(s, 120, 172, 75, 10, glow=glow)


def render_infernalpact(s):
    """A burning contract scroll sealed with a sigil."""
    glow = add_glow(s, 2.5)
    soft = add_soft_glow(s, 4)
    add_bg(s)
    g_scroll = lin_grad(s, [("0%", "#e8d5b0"), ("100%", "#b09468")])
    add_atmosphere(s, color=C_DEEP_ORANGE, opacity=0.06)
    add_embers(s, 7, 9451, glow)
    s.draw(f'  <path d="M 55 55 L 185 45 L 195 140 L 65 150 Z" fill="url(#{g_scroll})" '
           f'stroke="#5a3a20" stroke-width="2" opacity="0.92" filter="url(#{soft})"/>')
    for y in (72, 90, 108):
        s.draw(f'  <line x1="80" y1="{y}" x2="172" y2="{y-6}" stroke="#5a3a20" stroke-width="2.5" opacity="0.55"/>')
    s.draw(f'  <circle cx="150" cy="122" r="14" fill="none" stroke="{C_DEEP_ORANGE2}" stroke-width="3" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 143 122 L 157 122 M 150 115 L 150 129" stroke="{C_DEEP_ORANGE2}" '
           f'stroke-width="2.5" filter="url(#{glow})"/>')
    s.draw(f'  <path d="{flame_path(88, 140, 55, 14, 3, 9452)}" fill="{C_ORANGE}" opacity="0.8" filter="url(#{glow})"/>')
    add_bottom_glow(s, 125, 172, 65, 10, glow=glow)


def render_dragondominancepower(s):
    """Dragon Dominance — claw gripping crown, mini."""
    glow = add_glow(s, 1.5)
    add_bg(s, cx="50%", cy="50%", r="60%")
    g_crown = rad_grad(s, [("0%", C_WHITE_HOT), ("60%", C_YELLOW), ("100%", C_ORANGE)])
    add_embers(s, 3, 9461, glow)
    s.draw(f'  <circle cx="32" cy="22" r="10" fill="url(#{g_crown})" filter="url(#{glow})"/>')
    for hx in (-7, 0, 7):
        s.draw(f'  <path d="M {32+hx-2.5} 16 L {32+hx} 6 L {32+hx+2.5} 16 Z" fill="{C_YELLOW3}"/>')
    for ang in (-10, 6, 22):
        s.draw(f'  <path d="M {32+ang*0.5} 30 Q {32+ang} 40 {32+ang*1.3} 54" '
               f'stroke="{C_DEEP_ORANGE}" stroke-width="5" stroke-linecap="round" opacity="0.9" filter="url(#{glow})"/>')


def render_windblazepower(s):
    """Windblaze — wind lines fanning a flame."""
    glow = add_glow(s, 1.5)
    add_bg(s, cx="50%", cy="50%", r="60%")
    add_embers(s, 4, 9471, glow)
    for y, op in [(20, 0.5), (30, 0.6), (40, 0.5)]:
        s.draw(f'  <path d="M 6 {y+5} Q 18 {y-4} 30 {y} Q 42 {y+4} 58 {y-4}" '
               f'stroke="{C_YELLOW3}" stroke-width="2" fill="none" opacity="{op}" stroke-linecap="round" filter="url(#{glow})"/>')
    s.draw(f'  <path d="{flame_path(36, 54, 26, 9, 2, 9472)}" fill="{C_ORANGE}" opacity="0.9" filter="url(#{glow})"/>')
    s.draw(f'  <path d="{flame_path(38, 52, 15, 5, 1, 9473)}" fill="{C_WHITE_HOT}" opacity="0.9"/>')


def render_infernalpactpower(s):
    """Infernal Pact — burning sigil ring."""
    glow = add_glow(s, 1.5)
    add_bg(s, cx="50%", cy="50%", r="60%")
    g_ring = lin_grad(s, [("0%", C_DEEP_ORANGE2), ("100%", C_ORANGE)])
    add_embers(s, 3, 9481, glow)
    s.draw(f'  <circle cx="32" cy="32" r="17" fill="none" stroke="url(#{g_ring})" '
           f'stroke-width="4" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 32 22 L 32 42 M 24 27 L 40 37 M 40 27 L 24 37" '
           f'stroke="{C_YELLOW3}" stroke-width="2.5" filter="url(#{glow})"/>')


# =====================================================================
#  Register + generate
# =====================================================================

NEW_CARDS = ["EmberScales", "AshEmbrace", "ScorchDetonation", "Backdraft",
             "EmberAfterglow", "ResidualWarmth", "MartyrFlame", "DragonsMajesty",
             "StokeFlame", "Dragonlance", "FlameParity", "Everburning", "DraconicCrush",
             "Heatwave", "DragonDominance", "Pyre", "EmberReaper", "Windblaze", "InfernalPact"]
NEW_POWERS = ["AshEmbracePower", "EmberAfterglowPower", "DragonsMajestyPower",
              "EverburningPower", "DragonDominancePower", "WindblazePower", "InfernalPactPower"]

CARD_FNS = {
    "EmberScales": render_emberscales,
    "AshEmbrace": render_ashembrace,
    "ScorchDetonation": render_scorchdetonation,
    "Backdraft": render_backdraft,
    "EmberAfterglow": render_emberafterglow,
    "ResidualWarmth": render_residualwarmth,
    "MartyrFlame": render_martyrflame,
    "DragonsMajesty": render_dragonsmajesty,
    "StokeFlame": render_stokeflame,
    "Dragonlance": render_dragonlance,
    "FlameParity": render_flameparity,
    "Everburning": render_everburning,
    "DraconicCrush": render_draconiccrush,
    "Heatwave": render_heatwave,
    "DragonDominance": render_dragondominance,
    "Pyre": render_pyre,
    "EmberReaper": render_emberreaper,
    "Windblaze": render_windblaze,
    "InfernalPact": render_infernalpact,
    "AshStorm": render_ashstorm,
}
POWER_FNS = {
    "AshEmbracePower": render_ashembracepower,
    "EmberAfterglowPower": render_emberafterglowpower,
    "DragonsMajestyPower": render_dragonsmajestypower,
    "EverburningPower": render_everburningpower,
    "DragonDominancePower": render_dragondominancepower,
    "WindblazePower": render_windblazepower,
    "InfernalPactPower": render_infernalpactpower,
}


def main(force=False):
    g._FORCE = force
    for name, fn in CARD_FNS.items():
        g.CARD_RENDERERS[name] = fn
    for name, fn in POWER_FNS.items():
        g.POWER_RENDERERS[name] = fn

    written = total = 0
    print("[cards]")
    for name in NEW_CARDS:
        total += 1
        if g.generate_card(name):
            written += 1
    print("[powers]")
    for name in NEW_POWERS:
        total += 1
        if g.generate_power(name):
            written += 1
    print(f"=== done: {written}/{total} files written ===")


if __name__ == "__main__":
    import sys
    main(force="--force" in sys.argv)
