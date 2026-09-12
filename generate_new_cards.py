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
#  Register + generate
# =====================================================================

NEW_CARDS = ["EmberScales", "AshEmbrace", "ScorchDetonation", "Backdraft",
             "EmberAfterglow", "ResidualWarmth", "MartyrFlame", "DragonsMajesty"]
NEW_POWERS = ["AshEmbracePower", "EmberAfterglowPower", "DragonsMajestyPower"]

CARD_FNS = {
    "EmberScales": render_emberscales,
    "AshEmbrace": render_ashembrace,
    "ScorchDetonation": render_scorchdetonation,
    "Backdraft": render_backdraft,
    "EmberAfterglow": render_emberafterglow,
    "ResidualWarmth": render_residualwarmth,
    "MartyrFlame": render_martyrflame,
    "DragonsMajesty": render_dragonsmajesty,
    "AshStorm": render_ashstorm,
}
POWER_FNS = {
    "AshEmbracePower": render_ashembracepower,
    "EmberAfterglowPower": render_emberafterglowpower,
    "DragonsMajestyPower": render_dragonsmajestypower,
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
