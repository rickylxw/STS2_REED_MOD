#!/usr/bin/env python3
"""
generate_all_svg.py
==================
Generates high-quality SVG art for the Reed character mod in Slay the Spire 2.
All SVGs share a fire/ember visual theme and are produced programmatically
with rich detail: radial-gradient backgrounds, multiple gradients, SVG
filters (feGaussianBlur glow), ember particles, and per-card visual elements.

Usage:
    python generate_all_svg.py [--force]
    --force  Overwrite existing SVG files (default: only generate missing ones).
"""

import os, sys, argparse, random, math

# =====================================================================
#  Colour palette  --  fire / ember theme
# =====================================================================

C_WHITE_HOT   = "#fff8e0"
C_WHITE_HOT2  = "#fff5cc"
C_YELLOW      = "#ffe060"
C_YELLOW2     = "#ffd24d"
C_YELLOW3     = "#ffcc40"
C_ORANGE      = "#ff8800"
C_ORANGE2     = "#ff6b1a"
C_ORANGE3     = "#ff6600"
C_ORANGE4     = "#ff7a1a"
C_DEEP_ORANGE = "#e6591a"
C_DEEP_ORANGE2= "#c41a05"
C_DEEP_ORANGE3= "#cc4400"
C_DARK_RED    = "#8a2a05"
C_DARK_RED2   = "#331100"
C_DARK_BG     = "#1a0d08"
C_DARK_BG2    = "#0d0604"
C_DARK_BG3    = "#0a0504"

EMBER_COLORS = [C_ORANGE, C_YELLOW3, C_DEEP_ORANGE, C_DEEP_ORANGE2,
                C_YELLOW, C_WHITE_HOT, C_ORANGE3, C_ORANGE4]
ASH_COLORS   = ["#5a5a5a", "#6a6a6a", "#7a7a7a", "#4a4a4a",
                "#888888", "#999999", "#555555"]

# =====================================================================
#  SVG builder
# =====================================================================

class SVG:
    """Accumulates <defs> and body content, then renders a complete SVG."""

    def __init__(self, width, height):
        self.w = width
        self.h = height
        self.defs = []
        self.body = []
        self._n = 0

    def nid(self):
        self._n += 1
        return self._n

    def def_(self, text):
        self.defs.append(text)

    def draw(self, text):
        self.body.append(text)

    def comment(self, text):
        self.body.append(f"  <!-- {text} -->")

    def build(self):
        defs_text = "\n".join(self.defs)
        body_text = "\n".join(self.body)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}">\n'
            f"  <defs>\n{defs_text}\n  </defs>\n\n{body_text}\n</svg>\n"
        )

# =====================================================================
#  Helper functions
# =====================================================================

def add_bg(s, cx="50%", cy="55%", r="70%", c0="#2a1815", c1=C_DARK_BG, c2=C_DARK_BG2):
    gid = f"bg{s.nid()}"
    s.def_(f'    <radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="{r}">\n'
           f'      <stop offset="0%" stop-color="{c0}"/>\n'
           f'      <stop offset="60%" stop-color="{c1}"/>\n'
           f'      <stop offset="100%" stop-color="{c2}"/>\n'
           f'    </radialGradient>')
    s.draw(f'  <rect width="{s.w}" height="{s.h}" fill="url(#{gid})" rx="8"/>')
    return gid

def add_glow(s, std=3):
    fid = f"glow{s.nid()}"
    s.def_(f'    <filter id="{fid}">\n'
           f'      <feGaussianBlur stdDeviation="{std}" result="blur"/>\n'
           f'      <feMerge>\n'
           f'        <feMergeNode in="blur"/>\n'
           f'        <feMergeNode in="SourceGraphic"/>\n'
           f'      </feMerge>\n'
           f'    </filter>')
    return fid

def add_soft_glow(s, std=5):
    fid = f"soft{s.nid()}"
    s.def_(f'    <filter id="{fid}">\n'
           f'      <feGaussianBlur stdDeviation="{std}" result="blur"/>\n'
           f'      <feMerge>\n'
           f'        <feMergeNode in="blur"/>\n'
           f'        <feMergeNode in="SourceGraphic"/>\n'
           f'      </feMerge>\n'
           f'    </filter>')
    return fid

def add_blur_only(s, std=2):
    fid = f"blur{s.nid()}"
    s.def_(f'    <filter id="{fid}"><feGaussianBlur stdDeviation="{std}"/></filter>')
    return fid

def lin_grad(s, stops, x1="0%", y1="0%", x2="100%", y2="100%"):
    gid = f"lin{s.nid()}"
    parts = []
    for st in stops:
        if len(st) == 3:
            parts.append(f'      <stop offset="{st[0]}" stop-color="{st[1]}" stop-opacity="{st[2]}"/>')
        else:
            parts.append(f'      <stop offset="{st[0]}" stop-color="{st[1]}"/>')
    s.def_(f'    <linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">\n'
           + "\n".join(parts) + "\n"
           f'    </linearGradient>')
    return gid

def rad_grad(s, stops, cx="50%", cy="50%", r="50%"):
    gid = f"rad{s.nid()}"
    parts = []
    for st in stops:
        if len(st) == 3:
            parts.append(f'      <stop offset="{st[0]}" stop-color="{st[1]}" stop-opacity="{st[2]}"/>')
        else:
            parts.append(f'      <stop offset="{st[0]}" stop-color="{st[1]}"/>')
    s.def_(f'    <radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="{r}">\n'
           + "\n".join(parts) + "\n"
           f'    </radialGradient>')
    return gid

def add_atmosphere(s, cx=None, cy=None, rx=None, ry=None, color=C_DEEP_ORANGE, opacity=0.04, filt=None):
    cx = cx or s.w / 2
    cy = cy or s.h / 2
    rx = rx or s.w * 0.48
    ry = ry or s.h * 0.42
    fref = f' filter="url(#{filt})"' if filt else ""
    s.draw(f'  <ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
           f'fill="{color}" opacity="{opacity}"{fref}/>')

def add_embers(s, count, seed, glow=None, colors=None, min_r=0.5, max_r=2.5,
               min_op=0.2, max_op=0.7, margin=8):
    rng = random.Random(seed)
    colors = colors or EMBER_COLORS
    for _ in range(count):
        x = rng.uniform(margin, s.w - margin)
        y = rng.uniform(margin, s.h - margin)
        r = rng.uniform(min_r, max_r)
        color = rng.choice(colors)
        op = rng.uniform(min_op, max_op)
        fref = f' filter="url(#{glow})"' if glow and rng.random() > 0.45 else ""
        s.draw(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" '
               f'fill="{color}" opacity="{op:.2f}"{fref}/>')

def add_ash_particles(s, count, seed, colors=None, min_r=0.5, max_r=2.0,
                      min_op=0.2, max_op=0.6, margin=8):
    rng = random.Random(seed)
    colors = colors or ASH_COLORS
    for _ in range(count):
        x = rng.uniform(margin, s.w - margin)
        y = rng.uniform(margin, s.h - margin)
        r = rng.uniform(min_r, max_r)
        color = rng.choice(colors)
        op = rng.uniform(min_op, max_op)
        s.draw(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" '
               f'fill="{color}" opacity="{op:.2f}"/>')

def add_motion_lines(s, lines_data, color=C_DEEP_ORANGE, opacity=0.2):
    for x1, y1, x2, y2, sw, op in lines_data:
        s.draw(f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
               f'stroke="{color}" stroke-width="{sw}" opacity="{op}"/>')

def add_spark_burst(s, cx, cy, count, seed, length=20, colors=None, glow=None):
    rng = random.Random(seed)
    colors = colors or [C_WHITE_HOT, C_YELLOW, C_ORANGE, C_YELLOW3]
    for _ in range(count):
        angle = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(length * 0.4, length)
        x2 = cx + r * math.cos(angle)
        y2 = cy + r * math.sin(angle)
        sw = rng.uniform(0.6, 1.8)
        op = rng.uniform(0.4, 0.9)
        color = rng.choice(colors)
        fref = f' filter="url(#{glow})"' if glow and rng.random() > 0.5 else ""
        s.draw(f'  <line x1="{cx:.1f}" y1="{cy:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
               f'stroke="{color}" stroke-width="{sw:.1f}" opacity="{op:.2f}"{fref}/>')

def flame_path(cx, base_y, height, width, jitter=0, seed=0):
    rng = random.Random(seed)
    j = jitter
    w, h = width, height
    top_x = cx + rng.uniform(-j, j)
    top_y = base_y - h
    lw = cx - w + rng.uniform(-j, j)
    rw = cx + w + rng.uniform(-j, j)
    mid_lx = cx - w * 0.4 + rng.uniform(-j, j)
    mid_rx = cx + w * 0.4 + rng.uniform(-j, j)
    return (
        f"M {cx:.1f} {base_y:.1f} "
        f"Q {lw:.1f} {base_y - h*0.25:.1f} {mid_lx:.1f} {base_y - h*0.45:.1f} "
        f"Q {cx - w*0.2:.1f} {base_y - h*0.65:.1f} {top_x:.1f} {top_y:.1f} "
        f"Q {cx + w*0.2:.1f} {base_y - h*0.7:.1f} {mid_rx:.1f} {base_y - h*0.55:.1f} "
        f"Q {rw:.1f} {base_y - h*0.3:.1f} {cx:.1f} {base_y:.1f} Z"
    )

def add_bottom_glow(s, cx, cy, rx, ry, color=C_DARK_RED, opacity=0.3, glow=None):
    fref = f' filter="url(#{glow})"' if glow else ""
    s.draw(f'  <ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
           f'fill="{color}" opacity="{opacity}"{fref}/>')

# Placeholder for card renderers -- filled in below
CARD_RENDERERS = {}

# =====================================================================
#  CARD RENDERERS  (56 cards, 250 x 190)
# =====================================================================

# ---- BASIC (2) ----

def render_strike(s):
    """Fire beam attack with trailing embers."""
    glow = add_glow(s, 3)
    add_bg(s)
    g_blade = lin_grad(s, [("0%", C_WHITE_HOT), ("20%", C_YELLOW), ("50%", C_ORANGE),
                            ("80%", C_DEEP_ORANGE), ("100%", C_DARK_RED)])
    g_trail = lin_grad(s, [("0%", C_DARK_RED, 0), ("30%", C_DEEP_ORANGE2, 0.3),
                            ("60%", C_DEEP_ORANGE, 0.6), ("90%", "#ffaa30", 0.8),
                            ("100%", C_WHITE_HOT, 0.9)], "100%", "100%", "0%", "0%")
    g_handle = lin_grad(s, [("0%", "#2a1815"), ("50%", "#4a2818"), ("100%", "#2a1815")])
    g_impact = rad_grad(s, [("0%", C_WHITE_HOT, 1), ("20%", C_YELLOW, 0.8),
                             ("50%", C_ORANGE, 0.5), ("100%", C_DARK_RED, 0)])
    add_atmosphere(s)
    add_embers(s, 10, 101, glow)
    add_motion_lines(s, [(10,170,60,120,1,0.2),(20,180,80,120,1.5,0.25),
        (5,155,50,110,0.8,0.15),(190,50,240,10,1,0.2),
        (200,60,245,15,1.2,0.2),(195,40,235,5,0.8,0.15)])
    s.comment("Fire trail")
    s.draw(f'  <path d="M 30 175 Q 60 160 90 135 Q 120 110 150 85 Q 170 65 180 55 '
            f'L 190 45 Q 165 60 140 85 Q 110 110 80 140 Q 50 165 30 175 Z" '
            f'fill="url(#{g_trail})" filter="url(#{glow})"/>')
    for x, y, w, h, c, o in [(40,170,15,20,C_ORANGE,0.5),(70,140,15,25,C_DEEP_ORANGE,0.4),
                              (105,105,15,25,C_ORANGE,0.4),(140,75,13,25,"#ffaa30",0.4)]:
        s.draw(f'  <path d="M {x} {y} Q {x+w} {y-h*0.3} {x+w*0.5} {y-h*0.5} '
                f'Q {x} {y-h*0.3} {x-w*0.2} {y} Z" fill="{c}" opacity="{o}"/>')
    s.draw(f'  <circle cx="195" cy="30" r="25" fill="url(#{g_impact})" filter="url(#{glow})"/>')
    s.comment("Sword")
    s.draw(f'  <rect x="18" y="168" width="20" height="8" fill="url(#{g_handle})" rx="2" '
            f'transform="rotate(-50 28 172)"/>')
    s.draw(f'  <rect x="22" y="162" width="14" height="5" fill="#4a2818" rx="1" '
            f'transform="rotate(-50 29 164.5)"/>')
    s.draw(f'  <path d="M 35 158 L 195 18 L 200 22 L 200 28 L 40 165 Z" '
            f'fill="url(#{g_blade})" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 195 18 L 200 22 L 200 28 L 190 15 Z" fill="{C_WHITE_HOT}" opacity="0.9"/>')
    s.draw(f'  <line x1="45" y1="152" x2="190" y2="22" stroke="{C_DEEP_ORANGE2}" '
            f'stroke-width="1" opacity="0.6"/>')
    for x, y, w, h, c, o in [(160,50,8,25,C_ORANGE,0.6),(130,82,8,27,"#ffaa30",0.5),
                              (100,112,8,27,C_ORANGE,0.5),(70,140,8,27,C_DEEP_ORANGE,0.4)]:
        s.draw(f'  <path d="M {x} {y} Q {x+w} {y-h*0.4} {x+w*0.5} {y-h} '
                f'Q {x} {y-h*0.4} {x-w*0.2} {y} Z" fill="{c}" opacity="{o}"/>')
    add_spark_burst(s, 195, 30, 6, 201, 25, glow=glow)
    for x, y, r, c, o in [(60,130,2,C_ORANGE,0.7),(95,95,1.5,"#ffaa30",0.6),
                           (130,60,2,C_ORANGE,0.6),(165,40,1.5,C_YELLOW,0.7)]:
        s.draw(f'  <circle cx="{x}" cy="{y}" r="{r}" fill="{c}" opacity="{o}" filter="url(#{glow})"/>')
    add_bottom_glow(s, 30, 175, 15, 5)

CARD_RENDERERS["Strike"] = render_strike


def render_defend(s):
    """Circular flame barrier."""
    glow = add_glow(s, 2.5)
    add_bg(s)
    g_face = rad_grad(s, [("0%", "#4a2818"), ("40%", "#3a1f15"),
                           ("80%", "#2a1815"), ("100%", C_DARK_BG)])
    g_sglow = rad_grad(s, [("80%", C_DEEP_ORANGE, 0), ("92%", C_ORANGE, 0.6),
                            ("100%", "#ffaa30", 0)])
    g_rim = lin_grad(s, [("0%", C_WHITE_HOT), ("15%", C_YELLOW), ("40%", C_ORANGE),
                          ("70%", C_DEEP_ORANGE), ("100%", C_DARK_RED)], "0%", "0%", "0%", "100%")
    g_ember = rad_grad(s, [("0%", C_WHITE_HOT, 0.9), ("30%", C_YELLOW, 0.6),
                            ("70%", C_ORANGE, 0.3), ("100%", C_DARK_RED, 0)])
    add_atmosphere(s)
    add_ash_particles(s, 10, 102)
    s.draw(f'  <ellipse cx="125" cy="95" rx="72" ry="78" fill="url(#{g_sglow})" filter="url(#{glow})"/>')
    s.comment("Shield body")
    s.draw(f'  <path d="M 125 18 L 190 35 L 190 95 Q 190 135 125 170 Q 60 135 60 95 L 60 35 Z" '
            f'fill="url(#{g_face})"/>')
    for pts in ["M 80 50 Q 95 55 88 65 Q 80 72 90 80",
                "M 170 55 Q 155 60 162 70 Q 170 78 160 85",
                "M 95 110 Q 110 115 105 125",
                "M 150 100 Q 140 108 145 118"]:
        s.draw(f'  <path d="{pts}" stroke="{C_DARK_BG}" stroke-width="1" fill="none" opacity="0.6"/>')
    for pts, sw, o in [("M 85 60 Q 90 70 87 80 Q 84 90 88 100",1.5,0.6),
                       ("M 165 60 Q 160 70 163 80 Q 166 90 162 100",1.5,0.6),
                       ("M 100 130 Q 110 140 105 150",1,0.5),
                       ("M 150 130 Q 140 140 145 150",1,0.5)]:
        s.draw(f'  <path d="{pts}" stroke="{C_ORANGE}" stroke-width="{sw}" '
                f'fill="none" opacity="{o}" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="90" r="28" fill="url(#{g_ember})" filter="url(#{glow})"/>')
    s.comment("Flame motif")
    s.draw(f'  <path d="M 125 70 Q 132 82 128 92 Q 135 85 133 75 Q 140 88 136 100 '
            f'Q 130 95 128 88 Q 125 96 122 88 Q 120 95 114 100 '
            f'Q 110 88 117 75 Q 115 85 122 92 Q 118 82 125 70 Z" '
            f'fill="{C_ORANGE}" opacity="0.7" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 125 78 Q 130 88 127 96 Q 130 90 132 82 Q 136 92 134 100 '
            f'Q 130 96 128 92 Q 126 98 124 92 Q 122 96 120 100 '
            f'Q 116 92 119 82 Q 121 90 123 96 Q 120 88 125 78 Z" '
            f'fill="{C_YELLOW}" opacity="0.8" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 125 84 Q 128 90 126 96 Q 128 92 130 88 Q 132 94 130 100 '
            f'Q 128 96 127 93 Q 125 97 123 93 Q 121 96 120 100 '
            f'Q 118 94 120 88 Q 122 92 123 96 Q 121 90 125 84 Z" '
            f'fill="{C_WHITE_HOT}" opacity="0.7"/>')
    s.comment("Rim")
    s.draw(f'  <path d="M 125 18 L 190 35 L 190 95 Q 190 135 125 170 Q 60 135 60 95 L 60 35 Z" '
            f'fill="none" stroke="url(#{g_rim})" stroke-width="3.5" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 125 22 L 186 37 L 186 95 Q 186 132 125 165 Q 64 132 64 95 L 64 37 Z" '
            f'fill="none" stroke="{C_WHITE_HOT}" stroke-width="0.8" opacity="0.4"/>')
    s.draw(f'  <path d="M 125 14 L 194 33 L 194 95 Q 194 138 125 174 Q 56 138 56 95 L 56 33 Z" '
            f'fill="none" stroke="{C_DARK_BG}" stroke-width="2" opacity="0.8"/>')
    for cx, cy in [(68,42),(182,42),(125,165)]:
        s.draw(f'  <circle cx="{cx}" cy="{cy}" r="3" fill="#4a2818"/>')
        s.draw(f'  <circle cx="{cx}" cy="{cy}" r="1.5" fill="{C_ORANGE}" opacity="0.5" '
                f'filter="url(#{glow})"/>')
    add_embers(s, 6, 103, glow)

CARD_RENDERERS["Defend"] = render_defend


# ---- COMMON (17) ----

def render_spearflame(s):
    """Flame jet igniting enemy."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    g_shaft = lin_grad(s, [("0%","#3a1f15"),("30%","#5a3828"),("50%","#6a4838"),
                            ("70%","#5a3828"),("100%","#3a1f15")], "0%","0%","100%","0%")
    g_blade = lin_grad(s, [("0%",C_WHITE_HOT),("20%",C_YELLOW),("50%",C_ORANGE),
                            ("80%",C_DEEP_ORANGE),("100%",C_DARK_RED)], "0%","0%","0%","100%")
    g_bglow = rad_grad(s, [("0%",C_WHITE_HOT,0.9),("30%",C_YELLOW,0.6),
                            ("60%",C_ORANGE,0.3),("100%",C_DEEP_ORANGE2,0)])
    g_spiral = lin_grad(s, [("0%",C_ORANGE,0.8),("50%","#ffaa30",0.6),
                              ("100%",C_YELLOW,0.3)], "0%","100%","0%","0%")
    add_atmosphere(s, opacity=0.04, filt=soft)
    for y in [40,70,120,150]:
        c = C_ORANGE if y < 100 else "#ffaa30"
        s.draw(f'  <path d="M 20 {y} Q 50 {y-5} 80 {y} Q 130 {y-5} 160 {y} '
                f'Q 190 {y-5} 220 {y} Q 240 {y-5} 250 {y}" stroke="{c}" '
                f'stroke-width="0.5" fill="none" opacity="0.12"/>')
    add_embers(s, 6, 301, glow)
    s.comment("Spear (tilted)")
    s.draw(f'  <g transform="rotate(5 125 95)">')
    s.draw(f'    <ellipse cx="125" cy="35" rx="35" ry="40" fill="url(#{g_bglow})" filter="url(#{glow})"/>')
    s.draw(f'    <path d="M 95 90 Q 100 75 110 65 Q 105 80 120 70 Q 115 85 125 75 Q 120 90 130 80" '
            f'stroke="url(#{g_spiral})" stroke-width="3" fill="none" opacity="0.5" filter="url(#{glow})"/>')
    s.draw(f'    <path d="M 155 90 Q 150 75 140 65 Q 145 80 130 70 Q 135 85 125 75 Q 130 90 120 80" '
            f'stroke="url(#{g_spiral})" stroke-width="3" fill="none" opacity="0.5" filter="url(#{glow})"/>')
    s.draw(f'    <rect x="120" y="50" width="10" height="120" fill="url(#{g_shaft})" rx="2"/>')
    for y in [120,130,140,150]:
        s.draw(f'    <rect x="119" y="{y}" width="12" height="3" fill="{C_DARK_BG}" opacity="0.7"/>')
    s.draw(f'    <line x1="122" y1="55" x2="122" y2="165" stroke="#8a6848" stroke-width="0.8" opacity="0.5"/>')
    s.draw(f'    <rect x="117" y="168" width="16" height="8" fill="#3a1f15" rx="2"/>')
    s.draw(f'    <circle cx="125" cy="172" r="3" fill="#4a2818"/>')
    s.draw(f'    <rect x="105" y="46" width="40" height="6" fill="#4a2818" rx="2"/>')
    s.draw(f'    <rect x="103" y="44" width="44" height="3" fill="#5a3828" rx="1"/>')
    s.draw(f'    <path d="M 125 10 L 115 30 Q 112 40 115 50 L 125 48 L 135 50 '
            f'Q 138 40 135 30 Z" fill="url(#{g_blade})" filter="url(#{glow})"/>')
    s.draw(f'    <line x1="125" y1="12" x2="125" y2="48" stroke="{C_DEEP_ORANGE2}" stroke-width="1" opacity="0.6"/>')
    s.draw(f'    <path d="M 125 10 L 115 30 Q 112 40 115 50 L 118 48 Q 116 38 118 28 Z" '
            f'fill="{C_WHITE_HOT}" opacity="0.3"/>')
    s.draw(f'    <circle cx="125" cy="12" r="5" fill="{C_WHITE_HOT}" opacity="0.8" filter="url(#{glow})"/>')
    s.draw(f'    <circle cx="125" cy="12" r="2" fill="#ffffff" opacity="0.9"/>')
    s.comment("Flames engulfing blade")
    for fx, fy, fw, fh, fc, fo in [
        (110,45,-10,45,C_ORANGE,0.7),(140,45,10,45,C_ORANGE,0.7),
        (112,42,-7,42,"#ffaa30",0.6),(138,42,7,42,"#ffaa30",0.6),
        (118,40,-3,40,C_YELLOW,0.5),(132,40,3,40,C_YELLOW,0.5)]:
        s.draw(f'    <path d="M {fx} {fy} Q {fx+fw} {fy-fh*0.4} {fx+fw*0.5} {fy-fh} '
                f'Q {fx} {fy-fh*0.4} {fx-fw*0.2} {fy} Z" fill="{fc}" opacity="{fo}" '
                f'filter="url(#{glow})"/>')
    s.draw(f'    <path d="M 120 40 Q 122 20 125 5 Q 128 20 130 40 Z" '
            f'fill="{C_WHITE_HOT}" opacity="0.4" filter="url(#{glow})"/>')
    for fx, fy, fw, fh, fc, fo in [
        (95,130,20,10,C_ORANGE,0.4),(155,110,-20,10,C_ORANGE,0.4),
        (100,95,20,10,"#ffaa30",0.35),(150,145,-20,10,C_DEEP_ORANGE,0.3)]:
        s.draw(f'    <path d="M {fx} {fy} Q {fx+fw*0.5} {fy-fh*0.5} {fx+fw} {fy} '
                f'Q {fx+fw*0.5} {fy+fh*0.3} {fx} {fy} Z" fill="{fc}" opacity="{fo}" '
                f'filter="url(#{glow})"/>')
    s.draw(f'  </g>')
    add_embers(s, 8, 302, glow)

CARD_RENDERERS["SpearFlame"] = render_spearflame


def render_swiftthrust(s):
    """Rapid fire streak with motion blur."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    g_streak = lin_grad(s, [("0%",C_DARK_RED,0),("20%",C_DEEP_ORANGE2,0.2),
                             ("50%",C_DEEP_ORANGE,0.5),("80%",C_ORANGE,0.8),
                             ("100%",C_WHITE_HOT,1)])
    g_after = lin_grad(s, [("0%",C_DARK_RED,0),("50%",C_DEEP_ORANGE,0.3),
                            ("100%",C_ORANGE,0.5)])
    add_atmosphere(s)
    add_embers(s, 6, 401, glow)
    for y, sw, op in [(40,1,0.15),(55,1.5,0.2),(70,1,0.12),(100,1.5,0.18),(130,1,0.15),(150,1.2,0.2)]:
        s.draw(f'  <line x1="5" y1="{y}" x2="245" y2="{y}" stroke="{C_ORANGE}" '
                f'stroke-width="{sw}" opacity="{op}"/>')
    for offset, op in [(20,0.15),(12,0.25),(6,0.35)]:
        s.draw(f'  <path d="M {15+offset} 95 Q {60+offset} 85 {120+offset} 92 '
                f'Q {180+offset} 98 {235+offset} 90" fill="none" '
                f'stroke="url(#{g_after})" stroke-width="6" opacity="{op}" filter="url(#{soft})"/>')
    s.draw(f'  <path d="M 15 95 Q 60 82 120 90 Q 180 96 235 85" fill="none" '
            f'stroke="url(#{g_streak})" stroke-width="10" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 15 95 Q 60 82 120 90 Q 180 96 235 85" fill="none" '
            f'stroke="{C_WHITE_HOT}" stroke-width="3" opacity="0.7"/>')
    g_imp = rad_grad(s, [("0%",C_WHITE_HOT,1),("30%",C_YELLOW,0.8),
                          ("60%",C_ORANGE,0.4),("100%",C_DARK_RED,0)])
    s.draw(f'  <circle cx="235" cy="85" r="15" fill="url(#{g_imp})" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="235" cy="85" r="5" fill="{C_WHITE_HOT}" opacity="0.9"/>')
    add_spark_burst(s, 235, 85, 8, 402, 30, glow=glow)
    for x, y, r, c, o in [(50,92,2,C_ORANGE,0.6),(90,88,1.5,"#ffaa30",0.5),
                           (150,93,2,C_ORANGE,0.5),(200,87,1.5,C_YELLOW,0.6)]:
        s.draw(f'  <circle cx="{x}" cy="{y}" r="{r}" fill="{c}" opacity="{o}" filter="url(#{glow})"/>')

CARD_RENDERERS["SwiftThrust"] = render_swiftthrust


def render_ashenbulwark(s):
    """Wall of compressed ash."""
    glow = add_glow(s, 2.5)
    add_bg(s)
    g_ash = lin_grad(s, [("0%","#5a4a3a"),("30%","#3a2f25"),("60%","#2a2018"),("100%","#1a1410")])
    g_crack = lin_grad(s, [("0%",C_WHITE_HOT),("30%",C_YELLOW3),("70%",C_ORANGE3),("100%",C_DEEP_ORANGE)])
    add_atmosphere(s, color=C_DEEP_ORANGE, opacity=0.05)
    add_ash_particles(s, 12, 501)
    add_embers(s, 4, 502, glow, colors=[C_ORANGE, C_DEEP_ORANGE])
    blocks = [(20,60,50,35),(75,50,45,45),(125,55,50,40),(180,60,50,35),
              (20,100,55,40),(80,95,50,45),(135,100,55,40),(190,95,50,45),
              (20,145,60,35),(85,140,55,40),(145,145,55,35),(200,140,45,40)]
    for x, y, w, h in blocks:
        s.draw(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{g_ash})" '
                f'stroke="#1a0d08" stroke-width="1" opacity="0.9"/>')
    for x1, y1, x2, y2 in [(70,55,75,95),(120,50,125,100),(175,55,180,95),
                            (75,95,80,140),(135,95,140,140),(190,95,195,140)]:
        s.draw(f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="url(#{g_crack})" '
                f'stroke-width="2" opacity="0.7" filter="url(#{glow})"/>')
    for y in [95, 140]:
        s.draw(f'  <line x1="20" y1="{y}" x2="245" y2="{y}" stroke="url(#{g_crack})" '
                f'stroke-width="1.5" opacity="0.4" filter="url(#{glow})"/>')
    for x, y, r in [(45,78,2),(100,70,1.5),(150,75,2),(205,78,1.5),
                     (40,120,2),(105,115,1.5),(165,120,2),(210,115,1.5),
                     (50,160,1.5),(110,155,2),(170,160,1.5),(215,155,1.5)]:
        s.draw(f'  <circle cx="{x}" cy="{y}" r="{r}" fill="{C_ORANGE}" opacity="0.5" '
                f'filter="url(#{glow})"/>')

CARD_RENDERERS["AshenBulwark"] = render_ashenbulwark


def render_dragonbloodboiling(s):
    """Boiling blood energy."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    g_blood = rad_grad(s, [("0%",C_YELLOW),("30%",C_ORANGE),("60%",C_DEEP_ORANGE),
                            ("80%",C_DARK_RED),("100%",C_DARK_RED2)])
    g_bub = rad_grad(s, [("0%",C_WHITE_HOT,1),("40%",C_YELLOW,0.8),
                          ("80%",C_ORANGE,0.4),("100%",C_DEEP_ORANGE,0)])
    add_atmosphere(s, color=C_DARK_RED, opacity=0.06)
    add_embers(s, 8, 601, glow)
    s.draw(f'  <path d="M 40 100 Q 35 130 50 160 Q 80 180 125 180 Q 170 180 200 160 '
            f'Q 215 130 210 100 Z" fill="url(#{g_blood})" filter="url(#{glow})"/>')
    s.draw(f'  <ellipse cx="125" cy="100" rx="85" ry="12" fill="{C_ORANGE}" opacity="0.7" filter="url(#{glow})"/>')
    s.draw(f'  <ellipse cx="125" cy="98" rx="70" ry="8" fill="{C_YELLOW}" opacity="0.5" filter="url(#{glow})"/>')
    s.draw(f'  <ellipse cx="125" cy="96" rx="45" ry="5" fill="{C_WHITE_HOT}" opacity="0.3"/>')
    for cx, cy, r in [(70,95,8),(100,88,6),(140,92,7),(175,85,5),
                       (85,75,4),(155,78,5),(120,70,6),(190,95,4)]:
        s.draw(f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{g_bub})" opacity="0.6" filter="url(#{glow})"/>')
    for cx, base, h, w, c, o in [(70,95,50,12,C_ORANGE,0.5),(100,88,60,14,"#ffaa30",0.5),
                                  (140,92,55,13,C_ORANGE,0.5),(175,85,45,10,C_DEEP_ORANGE,0.4),
                                  (120,70,70,16,C_YELLOW,0.4)]:
        s.draw(f'  <path d="{flame_path(cx, base, h, w, 3, hash(str(cx))%100)}" '
                f'fill="{c}" opacity="{o}" filter="url(#{glow})"/>')
    for cx in [60, 110, 160, 200]:
        s.draw(f'  <path d="M {cx} 60 Q {cx+5} 40 {cx} 20 Q {cx-5} 10 {cx} 0" '
                f'stroke="#3a1f15" stroke-width="2" fill="none" opacity="0.2" filter="url(#{soft})"/>')

CARD_RENDERERS["DragonbloodBoiling"] = render_dragonbloodboiling


def render_emberignition(s):
    """Ember reigniting into blaze."""
    glow = add_glow(s, 3)
    add_bg(s)
    g_ember = rad_grad(s, [("0%",C_WHITE_HOT),("30%",C_YELLOW3),("60%",C_ORANGE),("100%",C_DARK_RED,0)])
    add_atmosphere(s, opacity=0.06)
    add_embers(s, 6, 701, glow)
    s.draw(f'  <circle cx="125" cy="160" r="12" fill="url(#{g_ember})" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="160" r="4" fill="{C_WHITE_HOT}" opacity="0.9"/>')
    for i in range(5):
        y = 155 - i * 25
        r = 8 - i * 1.2
        op = 0.4 + i * 0.1
        s.draw(f'  <circle cx="125" cy="{y}" r="{r}" fill="url(#{g_ember})" opacity="{op}" filter="url(#{glow})"/>')
    for cx, h, w, c, o in [(125,80,30,C_ORANGE,0.7),(110,60,20,"#ffaa30",0.6),
                            (140,65,22,C_DEEP_ORANGE,0.5),(125,50,15,C_YELLOW,0.6),
                            (125,35,8,C_WHITE_HOT,0.5)]:
        s.draw(f'  <path d="{flame_path(cx, 130, h, w, 3, hash(str(cx)+str(h))%100)}" '
                f'fill="{c}" opacity="{o}" filter="url(#{glow})"/>')
    add_spark_burst(s, 125, 130, 8, 702, 35, glow=glow)
    for x, y, r, c, o in [(100,100,1.5,C_ORANGE,0.6),(150,105,1.5,"#ffaa30",0.5),
                           (115,60,2,C_YELLOW,0.5),(135,50,1.5,C_WHITE_HOT,0.7),
                           (125,30,1,C_WHITE_HOT,0.4)]:
        s.draw(f'  <circle cx="{x}" cy="{y}" r="{r}" fill="{c}" opacity="{o}" filter="url(#{glow})"/>')

CARD_RENDERERS["EmberIgnition"] = render_emberignition


def render_cinderspear(s):
    """Cinder fire lance."""
    glow = add_glow(s, 3)
    add_bg(s)
    g_lance = lin_grad(s, [("0%",C_DARK_RED,0),("15%",C_DEEP_ORANGE2,0.6),
                           ("40%",C_DEEP_ORANGE,0.8),("60%",C_ORANGE,1),
                           ("85%",C_YELLOW,0.9),("100%",C_WHITE_HOT,1)])
    g_head = rad_grad(s, [("0%",C_WHITE_HOT,1),("20%",C_YELLOW,0.8),
                           ("50%",C_ORANGE,0.5),("100%",C_DARK_RED,0)])
    add_atmosphere(s)
    add_embers(s, 8, 801, glow)
    s.draw(f'  <path d="M 15 100 L 180 92 L 185 98 L 180 104 L 15 110 Z" '
            f'fill="url(#{g_lance})" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 15 103 L 180 96 L 185 98 L 180 100 L 15 107 Z" '
            f'fill="{C_WHITE_HOT}" opacity="0.3"/>')
    s.draw(f'  <path d="M 180 88 L 225 95 L 235 90 L 225 100 L 180 108 Z" '
            f'fill="url(#{g_lance})" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="235" cy="95" r="15" fill="url(#{g_head})" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="235" cy="95" r="5" fill="{C_WHITE_HOT}" opacity="0.9"/>')
    add_spark_burst(s, 235, 95, 8, 802, 30, glow=glow)
    for x, y, r, c, o in [(50,95,2,C_ORANGE,0.5),(100,92,1.5,"#ffaa30",0.4),
                           (150,95,2,C_ORANGE,0.4),(200,90,1.5,C_YELLOW,0.5)]:
        s.draw(f'  <circle cx="{x}" cy="{y}" r="{r}" fill="{c}" opacity="{o}" filter="url(#{glow})"/>')

CARD_RENDERERS["CinderSpear"] = render_cinderspear


def render_cinderspearcombo(s):
    """Triple fire streams converging."""
    glow = add_glow(s, 3)
    add_bg(s)
    g_s1 = lin_grad(s, [("0%",C_DARK_RED,0),("40%",C_DEEP_ORANGE,0.6),("100%",C_ORANGE,1)])
    g_s2 = lin_grad(s, [("0%",C_DARK_RED,0),("40%",C_DEEP_ORANGE2,0.6),("100%",C_YELLOW,1)])
    g_s3 = lin_grad(s, [("0%",C_DARK_RED,0),("40%",C_DEEP_ORANGE,0.6),("100%","#ffaa30",1)])
    g_imp = rad_grad(s, [("0%",C_WHITE_HOT,1),("30%",C_YELLOW,0.8),
                          ("60%",C_ORANGE,0.4),("100%",C_DARK_RED,0)])
    add_atmosphere(s)
    add_embers(s, 8, 901, glow)
    s.comment("Three converging streams")
    s.draw(f'  <path d="M 10 30 Q 80 50 125 90" fill="none" stroke="url(#{g_s1})" '
            f'stroke-width="8" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 10 95 Q 80 95 125 95" fill="none" stroke="url(#{g_s2})" '
            f'stroke-width="8" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 10 160 Q 80 140 125 100" fill="none" stroke="url(#{g_s3})" '
            f'stroke-width="8" filter="url(#{glow})"/>')
    s.comment("Convergence point")
    s.draw(f'  <circle cx="125" cy="95" r="25" fill="url(#{g_imp})" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="95" r="8" fill="{C_WHITE_HOT}" opacity="0.9"/>')
    add_spark_burst(s, 125, 95, 12, 902, 40, glow=glow)
    s.comment("Stream embers")
    for x, y, r, c, o in [(40,38,1.5,C_ORANGE,0.5),(70,48,1.5,"#ffaa30",0.4),
                           (40,95,1.5,C_YELLOW,0.5),(70,95,1.5,C_ORANGE,0.4),
                           (40,158,1.5,"#ffaa30",0.5),(70,142,1.5,C_DEEP_ORANGE,0.4)]:
        s.draw(f'  <circle cx="{x}" cy="{y}" r="{r}" fill="{c}" opacity="{o}" filter="url(#{glow})"/>')

CARD_RENDERERS["CinderSpearCombo"] = render_cinderspearcombo


def render_embershield(s):
    """Ember dome growing with scorch."""
    glow = add_glow(s, 3)
    add_bg(s)
    g_dome = rad_grad(s, [("0%",C_ORANGE,0.3),("60%",C_DEEP_ORANGE,0.15),("100%",C_DARK_RED,0)])
    g_ember = rad_grad(s, [("0%",C_WHITE_HOT,0.9),("30%",C_YELLOW,0.6),("100%",C_DARK_RED,0)])
    add_atmosphere(s, opacity=0.05)
    add_embers(s, 8, 1001, glow)
    for r, op in [(80,0.1),(65,0.15),(50,0.2),(35,0.25)]:
        s.draw(f'  <path d="M {125-r} 160 Q 125 {160-r*1.5} {125+r} 160" fill="none" '
                f'stroke="{C_ORANGE}" stroke-width="2" opacity="{op}" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 45 160 Q 125 20 205 160" fill="url(#{g_dome})" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 55 160 Q 125 30 195 160" fill="none" stroke="{C_ORANGE}" '
            f'stroke-width="2" opacity="0.4" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 65 160 Q 125 45 185 160" fill="none" stroke="{C_YELLOW3}" '
            f'stroke-width="1.5" opacity="0.3" filter="url(#{glow})"/>')
    for cx in [80, 125, 170]:
        s.draw(f'  <path d="{flame_path(cx, 160, 40, 10, 3, hash(str(cx))%100)}" '
                f'fill="{C_ORANGE}" opacity="0.5" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="120" r="15" fill="url(#{g_ember})" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="120" r="4" fill="{C_WHITE_HOT}" opacity="0.8"/>')
    s.comment("Scorch marks on ground")
    s.draw(f'  <ellipse cx="125" cy="165" rx="85" ry="8" fill="{C_DARK_RED}" opacity="0.4"/>')
    for x in [70, 100, 150, 180]:
        s.draw(f'  <circle cx="{x}" cy="164" r="3" fill="{C_ORANGE}" opacity="0.4" filter="url(#{glow})"/>')

CARD_RENDERERS["EmberShield"] = render_embershield


def render_emberconduit(s):
    """Vertical ember conduit."""
    glow = add_glow(s, 3)
    add_bg(s)
    g_flow = lin_grad(s, [("0%",C_DARK_RED,0),("20%",C_DEEP_ORANGE,0.8),
                          ("50%",C_ORANGE,1),("80%",C_YELLOW,0.9),("100%",C_WHITE_HOT,1)],
                         "0%","100%","0%","0%")
    g_tube = lin_grad(s, [("0%","#3a1f15"),("50%","#2a1815"),("100%","#3a1f15")],
                      "0%","0%","100%","0%")
    add_atmosphere(s, opacity=0.06)
    add_embers(s, 8, 1101, glow)
    s.comment("Conduit tube")
    s.draw(f'  <rect x="110" y="15" width="30" height="160" fill="url(#{g_tube})" rx="5"/>')
    s.draw(f'  <rect x="112" y="15" width="26" height="160" fill="url(#{g_flow})" rx="3" '
            f'filter="url(#{glow})"/>')
    s.comment("Flow streaks")
    for x in [116, 122, 128, 134]:
        s.draw(f'  <rect x="{x}" y="20" width="2" height="150" fill="{C_WHITE_HOT}" '
                f'opacity="0.2" rx="1"/>')
    s.comment("Energy nodes along conduit")
    for y in [40, 80, 120, 160]:
        s.draw(f'  <ellipse cx="125" cy="{y}" rx="20" ry="6" fill="{C_ORANGE}" '
                f'opacity="0.4" filter="url(#{glow})"/>')
        s.draw(f'  <ellipse cx="125" cy="{y}" rx="10" ry="3" fill="{C_YELLOW}" '
                f'opacity="0.5" filter="url(#{glow})"/>')
    s.comment("Top and bottom caps")
    s.draw(f'  <ellipse cx="125" cy="15" rx="18" ry="6" fill="{C_ORANGE}" opacity="0.6" '
            f'filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="15" r="5" fill="{C_WHITE_HOT}" opacity="0.9"/>')
    s.draw(f'  <ellipse cx="125" cy="175" rx="18" ry="6" fill="{C_DEEP_ORANGE}" opacity="0.5" '
            f'filter="url(#{glow})"/>')
    s.comment("Embers flowing up")
    for x, y, r in [(118,100,1.5),(132,70,1.5),(120,50,2),(130,30,1.5),
                     (115,120,1),(135,140,1)]:
        s.draw(f'  <circle cx="{x}" cy="{y}" r="{r}" fill="{C_YELLOW}" opacity="0.6" '
                f'filter="url(#{glow})"/>')

CARD_RENDERERS["EmberConduit"] = render_emberconduit


def render_embereye(s):
    """Glowing ember eye."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    g_iris = rad_grad(s, [("0%",C_WHITE_HOT),("20%",C_YELLOW),("50%",C_ORANGE),
                           ("80%",C_DEEP_ORANGE),("100%",C_DARK_RED)])
    g_pupil = rad_grad(s, [("0%",C_WHITE_HOT),("50%",C_YELLOW3),("100%",C_DEEP_ORANGE2)])
    g_eyelid = lin_grad(s, [("0%","#3a1f15"),("50%","#2a1815"),("100%","#3a1f15")])
    add_atmosphere(s, opacity=0.06, filt=soft)
    add_embers(s, 8, 1201, glow)
    s.comment("Eye socket glow")
    s.draw(f'  <ellipse cx="125" cy="95" rx="60" ry="35" fill="{C_DEEP_ORANGE}" '
            f'opacity="0.08" filter="url(#{soft})"/>')
    s.comment("Eye shape (almond)")
    s.draw(f'  <path d="M 50 95 Q 125 50 200 95 Q 125 140 50 95 Z" fill="{C_DARK_BG}" '
            f'stroke="url(#{g_eyelid})" stroke-width="3"/>')
    s.comment("Iris")
    s.draw(f'  <circle cx="125" cy="95" r="32" fill="url(#{g_iris})" filter="url(#{glow})"/>')
    s.comment("Iris texture rays")
    for i in range(12):
        a = i * 30
        x2 = 125 + 28 * math.cos(math.radians(a))
        y2 = 95 + 28 * math.sin(math.radians(a))
        s.draw(f'  <line x1="125" y1="95" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="{C_DEEP_ORANGE2}" stroke-width="1" opacity="0.3"/>')
    s.comment("Pupil")
    s.draw(f'  <circle cx="125" cy="95" r="12" fill="url(#{g_pupil})" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="95" r="5" fill="{C_WHITE_HOT}" opacity="0.9"/>')
    s.comment("Catchlight")
    s.draw(f'  <circle cx="118" cy="88" r="3" fill="#ffffff" opacity="0.8"/>')
    s.comment("Eyelid highlights")
    s.draw(f'  <path d="M 55 93 Q 125 52 195 93" fill="none" stroke="{C_ORANGE}" '
            f'stroke-width="1.5" opacity="0.5" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 55 97 Q 125 138 195 97" fill="none" stroke="{C_DEEP_ORANGE}" '
            f'stroke-width="1" opacity="0.3"/>')

CARD_RENDERERS["EmberEye"] = render_embereye


def render_ashenarmor(s):
    """Ash armor plating."""
    glow = add_glow(s, 2.5)
    add_bg(s)
    g_plate = lin_grad(s, [("0%","#5a4a3a"),("30%","#4a3a2a"),("60%","#3a2a20"),("100%","#2a1a10")])
    g_rim = lin_grad(s, [("0%",C_ORANGE,0.6),("50%",C_DEEP_ORANGE,0.4),("100%",C_DARK_RED,0.3)])
    add_atmosphere(s, color=C_DEEP_ORANGE, opacity=0.05)
    add_ash_particles(s, 10, 1301)
    add_embers(s, 4, 1302, glow, colors=[C_ORANGE, C_DEEP_ORANGE])
    plates = [
        (50,30,150,35),(50,70,150,35),(50,110,150,35),(50,150,150,35),
        (50,30,35,160),(115,30,35,160),(165,30,35,160),
    ]
    for x, y, w, h in plates:
        s.draw(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{g_plate})" '
                f'stroke="#1a0d08" stroke-width="1" rx="3"/>')
    s.comment("Glowing seams")
    for y in [65, 105, 145]:
        s.draw(f'  <line x1="50" y1="{y}" x2="200" y2="{y}" stroke="url(#{g_rim})" '
                f'stroke-width="1.5" opacity="0.6" filter="url(#{glow})"/>')
    for x in [110, 160]:
        s.draw(f'  <line x1="{x}" y1="30" x2="{x}" y2="190" stroke="url(#{g_rim})" '
                f'stroke-width="1" opacity="0.4" filter="url(#{glow})"/>')
    s.comment("Rivets")
    for x, y in [(55,35),(195,35),(55,75),(195,75),(55,115),(195,115),(55,155),(195,155)]:
        s.draw(f'  <circle cx="{x}" cy="{y}" r="2.5" fill="#3a2a20"/>')
        s.draw(f'  <circle cx="{x}" cy="{y}" r="1" fill="{C_ORANGE}" opacity="0.5" filter="url(#{glow})"/>')
    s.comment("Ember veins on plates")
    for x, y in [(80,50),(140,90),(90,130),(160,50),(120,170)]:
        s.draw(f'  <circle cx="{x}" cy="{y}" r="2" fill="{C_ORANGE}" opacity="0.4" filter="url(#{glow})"/>')

CARD_RENDERERS["AshenArmor"] = render_ashenarmor


def render_flamescale(s):
    """Scale patterns of flame."""
    glow = add_glow(s, 3)
    add_bg(s)
    g_scale = lin_grad(s, [("0%",C_DARK_RED),("30%",C_DEEP_ORANGE),("60%",C_ORANGE),("100%",C_YELLOW)])
    g_edge = lin_grad(s, [("0%",C_YELLOW3,0.8),("100%",C_DEEP_ORANGE,0.3)])
    add_atmosphere(s, opacity=0.05)
    add_embers(s, 6, 1401, glow)
    s.comment("Dragon scale pattern")
    for row in range(5):
        for col in range(7):
            x = 25 + col * 32 + (row % 2) * 16
            y = 25 + row * 32
            if x > 230 or y > 175:
                continue
            s.draw(f'  <path d="M {x} {y} Q {x-14} {y+10} {x} {y+22} Q {x+14} {y+10} {x} {y} Z" '
                    f'fill="url(#{g_scale})" stroke="url(#{g_edge})" stroke-width="0.5" '
                    f'opacity="0.7" filter="url(#{glow})"/>')
            s.draw(f'  <path d="M {x} {y+3} Q {x-8} {y+8} {x} {y+15} Q {x+8} {y+8} {x} {y+3} Z" '
                    f'fill="{C_YELLOW}" opacity="0.3"/>')
    s.comment("Glowing between scales")
    for x, y in [(40,50),(100,80),(160,50),(60,110),(130,140),(190,110)]:
        s.draw(f'  <circle cx="{x}" cy="{y}" r="2" fill="{C_ORANGE}" opacity="0.5" filter="url(#{glow})"/>')

CARD_RENDERERS["FlameScale"] = render_flamescale


def render_scorchbastion(s):
    """Massive scorching wall."""
    glow = add_glow(s, 2.5)
    add_bg(s)
    g_wall = lin_grad(s, [("0%","#4a3a2a"),("30%","#3a2a20"),("60%","#2a1a10"),("100%","#1a0d08")])
    g_scorch = lin_grad(s, [("0%",C_WHITE_HOT),("30%",C_YELLOW3),("70%",C_ORANGE3),("100%",C_DARK_RED)])
    add_atmosphere(s, color=C_DEEP_ORANGE, opacity=0.06)
    add_embers(s, 10, 1501, glow)
    s.comment("Fortress wall")
    s.draw(f'  <rect x="30" y="50" width="190" height="120" fill="url(#{g_wall})" rx="2"/>')
    s.comment("Battlements")
    for x in [30, 80, 130, 180]:
        s.draw(f'  <rect x="{x}" y="35" width="30" height="20" fill="url(#{g_wall})" rx="2"/>')
    s.comment("Scorch marks")
    for cx, cy, r in [(80,120,30),(160,100,25),(120,150,35)]:
        s.draw(f'  <ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r*0.7}" fill="url(#{g_scorch})" '
                f'opacity="0.3" filter="url(#{glow})"/>')
    s.comment("Glowing cracks")
    s.draw(f'  <path d="M 50 80 L 70 100 L 60 120 L 80 140 L 75 165" fill="none" '
            f'stroke="url(#{g_scorch})" stroke-width="2" opacity="0.7" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 200 80 L 180 100 L 190 120 L 170 140 L 175 165" fill="none" '
            f'stroke="url(#{g_scorch})" stroke-width="2" opacity="0.6" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 125 55 L 120 80 L 130 110 L 125 140 L 130 165" fill="none" '
            f'stroke="url(#{g_scorch})" stroke-width="1.5" opacity="0.5" filter="url(#{glow})"/>')
    s.comment("Ember spots")
    for x, y in [(60,90),(100,70),(150,80),(180,110),(70,130),(140,120),(190,140)]:
        s.draw(f'  <circle cx="{x}" cy="{y}" r="2" fill="{C_ORANGE}" opacity="0.5" filter="url(#{glow})"/>')

CARD_RENDERERS["ScorchBastion"] = render_scorchbastion


def render_scorchingcharge(s):
    """Surging scorch flames."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    g_charge = lin_grad(s, [("0%",C_DARK_RED,0),("20%",C_DEEP_ORANGE2,0.6),
                              ("50%",C_DEEP_ORANGE,0.8),("80%",C_ORANGE,1),
                              ("100%",C_WHITE_HOT,1)])
    add_atmosphere(s, opacity=0.06)
    add_embers(s, 8, 1601, glow)
    s.comment("Charge cone (rightward)")
    pts = "M 20 70 L 220 50 L 235 85 L 220 120 L 20 110 Z"
    s.draw(f'  <path d="{pts}" fill="url(#{g_charge})" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 20 85 L 220 75 L 235 85 L 220 95 L 20 95 Z" '
            f'fill="{C_WHITE_HOT}" opacity="0.3"/>')
    s.comment("Flame tongues at front")
    for cx, cy, h, w, c, o in [(220,55,30,8,C_ORANGE,0.6),(225,70,40,10,C_YELLOW,0.5),
                                (235,85,50,12,C_WHITE_HOT,0.4),(225,100,40,10,C_YELLOW,0.5),
                                (220,115,30,8,C_ORANGE,0.6)]:
        s.draw(f'  <path d="{flame_path(cx, cy, h, w, 3, hash(str(cx)+str(cy))%100)}" '
                f'fill="{c}" opacity="{o}" filter="url(#{glow})"/>')
    s.comment("Trailing streaks")
    for y in [75, 85, 95]:
        s.draw(f'  <line x1="15" y1="{y}" x2="200" y2="{y}" stroke="{C_ORANGE}" '
                f'stroke-width="1" opacity="0.2"/>')
    add_spark_burst(s, 235, 85, 8, 1602, 25, glow=glow)

CARD_RENDERERS["ScorchingCharge"] = render_scorchingcharge


def render_spontaneouscombustion(s):
    """Explosive self-immolation."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    g_expl = rad_grad(s, [("0%",C_WHITE_HOT,1),("15%",C_YELLOW,0.9),
                           ("35%",C_ORANGE,0.7),("60%",C_DEEP_ORANGE,0.4),
                           ("100%",C_DARK_RED,0)])
    add_atmosphere(s, opacity=0.06)
    add_embers(s, 10, 1701, glow)
    s.comment("Explosion core")
    s.draw(f'  <circle cx="125" cy="95" r="60" fill="url(#{g_expl})" filter="url(#{soft})"/>')
    s.draw(f'  <circle cx="125" cy="95" r="35" fill="url(#{g_expl})" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="95" r="12" fill="{C_WHITE_HOT}" opacity="0.9"/>')
    s.comment("Shockwave rings")
    for r, op in [(75,0.15),(90,0.1),(105,0.05)]:
        s.draw(f'  <circle cx="125" cy="95" r="{r}" fill="none" stroke="{C_ORANGE}" '
                f'stroke-width="2" opacity="{op}" filter="url(#{glow})"/>')
    s.comment("Explosion spikes")
    for i in range(16):
        a = i * 22.5
        x1 = 125 + 35 * math.cos(math.radians(a))
        y1 = 95 + 35 * math.sin(math.radians(a))
        x2 = 125 + 70 * math.cos(math.radians(a))
        y2 = 95 + 70 * math.sin(math.radians(a))
        s.draw(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="{C_YELLOW}" stroke-width="2" opacity="0.5" filter="url(#{glow})"/>')
    add_spark_burst(s, 125, 95, 16, 1702, 50, glow=glow)

CARD_RENDERERS["SpontaneousCombustion"] = render_spontaneouscombustion


def render_cindershield(s):
    """Solidified cinder dome."""
    glow = add_glow(s, 2.5)
    add_bg(s)
    g_dome = lin_grad(s, [("0%","#4a3a2a"),("30%","#3a2a20"),("60%","#2a1a10"),("100%","#1a0d08")],
                      "0%","0%","0%","100%")
    g_crystal = lin_grad(s, [("0%",C_ORANGE,0.8),("50%",C_DEEP_ORANGE,0.5),("100%",C_DARK_RED,0.2)])
    g_crack = lin_grad(s, [("0%",C_WHITE_HOT),("50%",C_YELLOW3),("100%",C_ORANGE3)])
    add_atmosphere(s, opacity=0.05)
    add_embers(s, 8, 1801, glow)
    s.comment("Dome base")
    s.draw(f'  <path d="M 40 160 Q 125 40 210 160 Z" fill="url(#{g_dome})" '
            f'stroke="#1a0d08" stroke-width="1"/>')
    s.comment("Crystal facets")
    facets = [(125,55,40,100),(80,90,30,70),(170,90,30,70),(60,130,25,30),(190,130,25,30)]
    for cx, cy, w, h in facets:
        s.draw(f'  <path d="M {cx-w} {cy+h*0.3} L {cx} {cy-h} L {cx+w} {cy+h*0.3} Z" '
                f'fill="url(#{g_crystal})" opacity="0.3" filter="url(#{glow})"/>')
    s.comment("Glowing cracks between facets")
    s.draw(f'  <path d="M 40 160 L 80 100 L 125 55 L 170 100 L 210 160" fill="none" '
            f'stroke="url(#{g_crack})" stroke-width="1.5" opacity="0.7" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 80 100 L 80 160 M 125 55 L 125 160 M 170 100 L 170 160" fill="none" '
            f'stroke="url(#{g_crack})" stroke-width="1" opacity="0.5" filter="url(#{glow})"/>')
    s.comment("Central core")
    s.draw(f'  <circle cx="125" cy="110" r="10" fill="{C_ORANGE}" opacity="0.6" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="110" r="3" fill="{C_WHITE_HOT}" opacity="0.9"/>')

CARD_RENDERERS["CinderShield"] = render_cindershield


def render_ashgathering(s):
    """Ash vortex converging."""
    glow = add_glow(s, 2.5)
    soft = add_soft_glow(s, 4)
    add_bg(s)
    g_vortex = rad_grad(s, [("0%",C_ORANGE,0.5),("30%",C_DEEP_ORANGE,0.3),("100%",C_DARK_RED,0)])
    add_atmosphere(s, opacity=0.05)
    add_ash_particles(s, 15, 1901)
    add_embers(s, 6, 1902, glow, colors=[C_ORANGE, C_DEEP_ORANGE])
    s.comment("Spiral arms")
    for start_a in [0, 90, 180, 270]:
        pts = []
        for t in range(0, 100, 5):
            a = math.radians(start_a + t * 3.6)
            r = 80 - t * 0.7
            if r < 5:
                break
            x = 125 + r * math.cos(a)
            y = 95 + r * math.sin(a)
            pts.append(f"{x:.1f} {y:.1f}")
        path = "M " + " L ".join(pts)
        s.draw(f'  <path d="{path}" fill="none" stroke="{ASH_COLORS[2]}" '
                f'stroke-width="2" opacity="0.3" filter="url(#{soft})"/>')
    s.comment("Convergence point")
    s.draw(f'  <circle cx="125" cy="95" r="15" fill="url(#{g_vortex})" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="95" r="5" fill="{C_ORANGE}" opacity="0.8" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="95" r="2" fill="{C_WHITE_HOT}" opacity="0.9"/>')

CARD_RENDERERS["AshGathering"] = render_ashgathering


# ---- UNCOMMON (26) ----

def render_ashbath(s):
    """Falling ash rain."""
    glow = add_glow(s, 2)
    add_bg(s)
    g_ash = lin_grad(s, [("0%",ASH_COLORS[0],0),("50%",ASH_COLORS[2],0.5),("100%",ASH_COLORS[3],0.8)])
    add_atmosphere(s, color="#3a2a20", opacity=0.08)
    s.comment("Falling ash streaks")
    rng = random.Random(2001)
    for _ in range(40):
        x = rng.uniform(10, 240)
        y = rng.uniform(0, 190)
        length = rng.uniform(8, 25)
        sw = rng.uniform(0.5, 1.5)
        op = rng.uniform(0.2, 0.5)
        c = rng.choice(["#7a7a7a", "#6a6a6a", "#8a8a8a", "#5a5a5a"])
        s.draw(f'  <line x1="{x:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{y+length:.1f}" '
                f'stroke="{c}" stroke-width="{sw:.1f}" opacity="{op:.2f}"/>')
    s.comment("Glowing embers mixed in")
    for _ in range(12):
        x = rng.uniform(10, 240)
        y = rng.uniform(0, 190)
        r = rng.uniform(0.8, 2)
        s.draw(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{C_ORANGE}" '
                f'opacity="0.4" filter="url(#{glow})"/>')
    s.comment("Ash accumulation at bottom")
    s.draw(f'  <ellipse cx="125" cy="185" rx="100" ry="10" fill="{ASH_COLORS[3]}" opacity="0.4"/>')
    s.draw(f'  <ellipse cx="125" cy="182" rx="70" ry="6" fill="{ASH_COLORS[2]}" opacity="0.3"/>')

CARD_RENDERERS["AshBath"] = render_ashbath


def render_ashignition(s):
    """Ash exploding into fire."""
    glow = add_glow(s, 3)
    add_bg(s)
    g_ign = rad_grad(s, [("0%",C_WHITE_HOT,1),("20%",C_YELLOW,0.8),
                          ("50%",C_ORANGE,0.5),("100%",C_DARK_RED,0)])
    add_atmosphere(s, opacity=0.06)
    add_ash_particles(s, 10, 2101)
    s.comment("Igniting ash particles")
    rng = random.Random(2102)
    for _ in range(20):
        x = rng.uniform(20, 230)
        y = rng.uniform(20, 170)
        r = rng.uniform(2, 5)
        c = rng.choice([C_ORANGE, C_YELLOW3, C_DEEP_ORANGE, "#ffaa30"])
        s.draw(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{c}" '
                f'opacity="0.5" filter="url(#{glow})"/>')
    s.comment("Central explosion")
    s.draw(f'  <circle cx="125" cy="95" r="30" fill="url(#{g_ign})" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="95" r="10" fill="{C_WHITE_HOT}" opacity="0.9"/>')
    add_spark_burst(s, 125, 95, 12, 2103, 35, glow=glow)

CARD_RENDERERS["AshIgnition"] = render_ashignition


def render_ashresonance(s):
    """Resonating ash rings."""
    glow = add_glow(s, 2.5)
    soft = add_soft_glow(s, 4)
    add_bg(s)
    add_atmosphere(s, opacity=0.05)
    add_ash_particles(s, 8, 2201)
    s.comment("Concentric resonating rings")
    for r, op, sw in [(20,0.8,2),(35,0.6,2),(50,0.4,1.5),(65,0.3,1.5),(80,0.2,1),(95,0.15,1)]:
        s.draw(f'  <circle cx="125" cy="95" r="{r}" fill="none" stroke="{ASH_COLORS[1]}" '
                f'stroke-width="{sw}" opacity="{op}" filter="url(#{soft})"/>')
    s.comment("Glowing resonance core")
    s.draw(f'  <circle cx="125" cy="95" r="12" fill="{C_ORANGE}" opacity="0.6" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="95" r="4" fill="{C_WHITE_HOT}" opacity="0.9"/>')
    s.comment("Vibration lines")
    for i in range(8):
        a = i * 45
        x1 = 125 + 25 * math.cos(math.radians(a))
        y1 = 95 + 25 * math.sin(math.radians(a))
        x2 = 125 + 90 * math.cos(math.radians(a))
        y2 = 95 + 90 * math.sin(math.radians(a))
        s.draw(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="{ASH_COLORS[1]}" stroke-width="0.5" opacity="0.2"/>')

CARD_RENDERERS["AshResonance"] = render_ashresonance


def render_burnaway(s):
    """Flames burning away."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    g_flame = lin_grad(s, [("0%",C_DARK_RED,0.1),("30%",C_DEEP_ORANGE,0.5),
                           ("60%",C_ORANGE,0.7),("100%",C_YELLOW,0.4)],
                      "0%","100%","0%","0%")
    add_atmosphere(s, opacity=0.05)
    add_embers(s, 10, 2301, glow)
    s.comment("Dissolving flame (bottom solid, top wisps)")
    s.draw(f'  <path d="M 70 170 Q 80 120 85 80 Q 90 50 95 20 Q 100 50 105 80 '
            f'Q 110 120 115 170 Z" fill="url(#{g_flame})" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 110 170 Q 115 130 120 90 Q 125 50 130 15 Q 135 50 140 90 '
            f'Q 145 130 150 170 Z" fill="url(#{g_flame})" opacity="0.8" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 145 170 Q 150 140 155 100 Q 160 60 165 25 Q 170 60 175 100 '
            f'Q 180 140 180 170 Z" fill="url(#{g_flame})" opacity="0.6" filter="url(#{glow})"/>')
    s.comment("Wisps dissipating at top")
    for cx in [95, 130, 165]:
        s.draw(f'  <path d="M {cx} 20 Q {cx+5} 10 {cx} 0" stroke="{C_DEEP_ORANGE}" '
                f'stroke-width="1" fill="none" opacity="0.2" filter="url(#{soft})"/>')
    s.comment("Ash falling")
    for x in [85, 110, 140, 170]:
        s.draw(f'  <circle cx="{x}" cy="{x%50+100}" r="1" fill="{ASH_COLORS[2]}" opacity="0.4"/>')

CARD_RENDERERS["BurnAway"] = render_burnaway


def render_burnout(s):
    """Final fire burst consuming scorch."""
    glow = add_glow(s, 3)
    add_bg(s)
    g_burst = rad_grad(s, [("0%",C_WHITE_HOT,0.8),("20%",C_YELLOW,0.6),
                            ("50%",C_ORANGE,0.3),("100%",C_DARK_RED,0)])
    add_atmosphere(s, color=C_DARK_RED, opacity=0.06)
    add_embers(s, 12, 2401, glow, colors=[C_DEEP_ORANGE, C_DARK_RED, "#ffaa30"])
    s.comment("Dim central burst")
    s.draw(f'  <circle cx="125" cy="95" r="40" fill="url(#{g_burst})" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="95" r="15" fill="{C_DEEP_ORANGE}" opacity="0.5" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="95" r="5" fill="{C_YELLOW3}" opacity="0.6"/>')
    s.comment("Scorch marks around")
    for cx, cy, r in [(60,60,25),(190,50,20),(70,140,22),(180,130,28)]:
        s.draw(f'  <ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r*0.7}" fill="{C_DARK_RED}" opacity="0.3"/>')
    s.comment("Dying embers")
    for x, y, r in [(80,70,1.5),(170,60,1),(60,100,1.5),(190,100,1),
                     (90,140,1),(170,130,1.5),(125,50,1),(125,150,1)]:
        s.draw(f'  <circle cx="{x}" cy="{y}" r="{r}" fill="{C_DEEP_ORANGE}" opacity="0.4" '
                f'filter="url(#{glow})"/>')

CARD_RENDERERS["BurnOut"] = render_burnout


def render_cremation(s):
    """Cremation funeral pyre."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    g_wood = lin_grad(s, [("0%","#3a2a1a"),("50%","#5a3a2a"),("100%","#3a2a1a")])
    g_flame = lin_grad(s, [("0%",C_DARK_RED,0.3),("30%",C_DEEP_ORANGE,0.7),
                            ("60%",C_ORANGE,0.9),("100%",C_YELLOW,0.6)],
                      "0%","100%","0%","0%")
    add_atmosphere(s, opacity=0.06)
    add_embers(s, 10, 2501, glow)
    s.comment("Pyre logs")
    for angle in [-15, 0, 15]:
        s.draw(f'  <rect x="60" y="140" width="130" height="12" fill="url(#{g_wood})" '
                f'rx="3" transform="rotate({angle} 125 145)"/>')
    s.comment("Flames rising from pyre")
    for cx, h, w, c, o in [(80,80,15,C_ORANGE,0.7),(100,100,18,C_YELLOW,0.6),
                            (125,120,22,C_ORANGE,0.8),(150,100,18,C_DEEP_ORANGE,0.6),
                            (170,80,15,C_ORANGE,0.7)]:
        s.draw(f'  <path d="{flame_path(cx, 145, h, w, 4, hash(str(cx))%100)}" '
                f'fill="{c}" opacity="{o}" filter="url(#{glow})"/>')
    s.comment("White-hot core")
    s.draw(f'  <path d="{flame_path(125, 145, 80, 10, 2, 99)}" fill="{C_WHITE_HOT}" '
            f'opacity="0.5" filter="url(#{glow})"/>')
    s.comment("Smoke rising")
    for cx in [90, 125, 160]:
        s.draw(f'  <path d="M {cx} 60 Q {cx+8} 40 {cx} 20 Q {cx-8} 10 {cx} 0" '
                f'stroke="#3a1f15" stroke-width="2" fill="none" opacity="0.2" filter="url(#{soft})"/>')
    s.comment("Ground scorch")
    s.draw(f'  <ellipse cx="125" cy="155" rx="80" ry="6" fill="{C_DARK_RED}" opacity="0.4"/>')

CARD_RENDERERS["Cremation"] = render_cremation


def render_dragonbreath(s):
    """Massive fire cone."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    g_cone = lin_grad(s, [("0%",C_WHITE_HOT,0.9),("20%",C_YELLOW,0.7),
                           ("50%",C_ORANGE,0.5),("80%",C_DEEP_ORANGE,0.3),
                           ("100%",C_DARK_RED,0)])
    add_atmosphere(s, opacity=0.06)
    add_embers(s, 10, 2601, glow)
    s.comment("Fire cone from left")
    s.draw(f'  <path d="M 15 95 L 80 55 L 245 30 L 245 160 L 80 135 Z" '
            f'fill="url(#{g_cone})" filter="url(#{glow})"/>')
    s.comment("Cone interior detail")
    s.draw(f'  <path d="M 15 95 L 90 70 L 240 45 L 240 145 L 90 120 Z" '
            f'fill="{C_ORANGE}" opacity="0.2" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 15 95 L 100 85 L 235 70 L 235 120 L 100 105 Z" '
            f'fill="{C_YELLOW}" opacity="0.15" filter="url(#{glow})"/>')
    s.comment("Breath source")
    s.draw(f'  <circle cx="15" cy="95" r="12" fill="{C_WHITE_HOT}" opacity="0.8" filter="url(#{glow})"/>')
    s.comment("Flame tongues at edge")
    for cy, h, w, c, o in [(40,30,10,C_ORANGE,0.5),(80,35,12,C_YELLOW,0.4),
                            (120,35,12,C_ORANGE,0.4),(150,30,10,C_DEEP_ORANGE,0.5)]:
        s.draw(f'  <path d="{flame_path(240, cy, h, w, 3, hash(str(cy))%100)}" '
                f'fill="{c}" opacity="{o}" filter="url(#{glow})"/>')
    add_spark_burst(s, 240, 95, 10, 2602, 35, glow=glow)

CARD_RENDERERS["DragonBreath"] = render_dragonbreath


def render_emberblade(s):
    """Solidified ember edge."""
    glow = add_glow(s, 3)
    add_bg(s)
    g_blade = lin_grad(s, [("0%",C_DARK_RED),("20%",C_DEEP_ORANGE),
                            ("50%",C_ORANGE),("80%",C_YELLOW),("100%",C_WHITE_HOT)])
    g_edge = lin_grad(s, [("0%",C_WHITE_HOT,0.9),("50%",C_YELLOW,0.5),("100%",C_ORANGE,0.2)])
    add_atmosphere(s, opacity=0.05)
    add_embers(s, 8, 2701, glow)
    s.comment("Blade (vertical, curved)")
    s.draw(f'  <path d="M 120 20 Q 110 60 115 100 Q 120 140 125 170 '
            f'L 135 170 Q 130 140 135 100 Q 140 60 130 20 Z" '
            f'fill="url(#{g_blade})" filter="url(#{glow})"/>')
    s.comment("Blade edge highlight")
    s.draw(f'  <path d="M 125 25 Q 118 60 122 100 Q 127 140 128 168" '
            f'fill="none" stroke="url(#{g_edge})" stroke-width="2" opacity="0.7"/>')
    s.comment("Center groove")
    s.draw(f'  <line x1="125" y1="30" x2="128" y2="165" stroke="{C_DEEP_ORANGE2}" '
            f'stroke-width="1" opacity="0.5"/>')
    s.comment("Handle")
    s.draw(f'  <rect x="115" y="168" width="20" height="8" fill="#3a1f15" rx="2"/>')
    s.draw(f'  <rect x="110" y="174" width="30" height="4" fill="#4a2818" rx="1"/>')
    s.comment("Ember particles embedded in blade")
    for y in [40, 70, 100, 130]:
        s.draw(f'  <circle cx="125" cy="{y}" r="2" fill="{C_WHITE_HOT}" opacity="0.6" '
                f'filter="url(#{glow})"/>')
    s.comment("Tip glow")
    s.draw(f'  <circle cx="125" cy="20" r="6" fill="{C_WHITE_HOT}" opacity="0.8" filter="url(#{glow})"/>')

CARD_RENDERERS["EmberBlade"] = render_emberblade


def render_embers(s):
    """Floating ember cloud."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    g_cloud = rad_grad(s, [("0%",C_ORANGE,0.15),("50%",C_DEEP_ORANGE,0.08),("100%",C_DARK_RED,0)])
    add_atmosphere(s, opacity=0.04, filt=soft)
    s.comment("Diffuse ember cloud")
    s.draw(f'  <ellipse cx="125" cy="95" rx="90" ry="60" fill="url(#{g_cloud})" filter="url(#{soft})"/>')
    s.comment("Dense ember cluster")
    rng = random.Random(2801)
    for _ in range(35):
        x = rng.uniform(40, 210)
        y = rng.uniform(40, 150)
        r = rng.uniform(1, 3.5)
        c = rng.choice([C_ORANGE, C_YELLOW3, C_YELLOW, C_DEEP_ORANGE, "#ffaa30", C_WHITE_HOT])
        op = rng.uniform(0.3, 0.9)
        s.draw(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{c}" '
                f'opacity="{op:.2f}" filter="url(#{glow})"/>')
    s.comment("Bright cores")
    for x, y in [(90,80),(140,90),(110,110),(160,70),(80,120),(170,130)]:
        s.draw(f'  <circle cx="{x}" cy="{y}" r="1.5" fill="{C_WHITE_HOT}" opacity="0.8" '
                f'filter="url(#{glow})"/>')

CARD_RENDERERS["Embers"] = render_embers


def render_flameburst(s):
    """Flame burst with sparks."""
    glow = add_glow(s, 3)
    add_bg(s)
    g_burst = rad_grad(s, [("0%",C_WHITE_HOT,1),("15%",C_YELLOW,0.8),
                            ("40%",C_ORANGE,0.5),("70%",C_DEEP_ORANGE,0.2),
                            ("100%",C_DARK_RED,0)])
    add_atmosphere(s, opacity=0.06)
    add_embers(s, 8, 2901, glow)
    s.comment("Burst center")
    s.draw(f'  <circle cx="125" cy="95" r="40" fill="url(#{g_burst})" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="95" r="15" fill="{C_WHITE_HOT}" opacity="0.9"/>')
    s.comment("Flame tongues radiating")
    for i in range(8):
        a = i * 45
        cx = 125 + 35 * math.cos(math.radians(a))
        cy = 95 + 35 * math.sin(math.radians(a))
        h = 30
        w = 8
        s.draw(f'  <path d="{flame_path(cx, cy + 15, h, w, 3, i*7)}" '
                f'fill="{C_ORANGE}" opacity="0.5" filter="url(#{glow})" '
                f'transform="rotate({a+90} {cx:.1f} {cy+15:.1f})"/>')
    add_spark_burst(s, 125, 95, 14, 2902, 45, glow=glow)

CARD_RENDERERS["FlameBurst"] = render_flameburst


def render_flameinheritance(s):
    """Flames spreading."""
    glow = add_glow(s, 3)
    add_bg(s)
    g_flame = lin_grad(s, [("0%",C_DARK_RED,0.3),("40%",C_DEEP_ORANGE,0.7),
                            ("70%",C_ORANGE,0.9),("100%",C_YELLOW,0.5)],
                      "0%","100%","0%","0%")
    add_atmosphere(s, opacity=0.05)
    add_embers(s, 8, 3001, glow)
    s.comment("Chain of spreading flames")
    positions = [(50,150,50,12),(90,120,55,13),(130,90,50,12),(170,60,45,10),(200,30,35,8)]
    for cx, base, h, w in positions:
        s.draw(f'  <path d="{flame_path(cx, base, h, w, 4, hash(str(cx))%100)}" '
                f'fill="url(#{g_flame})" opacity="0.7" filter="url(#{glow})"/>')
    s.comment("Connecting ember trails")
    for i in range(len(positions)-1):
        x1 = positions[i][0]
        y1 = positions[i][1] - positions[i][2]
        x2 = positions[i+1][0]
        y2 = positions[i+1][1] - positions[i+1][2]
        s.draw(f'  <path d="M {x1} {y1} Q {(x1+x2)/2} {min(y1,y2)-15} {x2} {y2}" '
                f'fill="none" stroke="{C_ORANGE}" stroke-width="1.5" opacity="0.4" '
                f'filter="url(#{glow})"/>')
    s.comment("Spreading embers")
    for x, y, r in [(30,160,1.5),(65,130,1),(105,100,1.5),(145,70,1),
                     (185,40,1.5),(215,20,1)]:
        s.draw(f'  <circle cx="{x}" cy="{y}" r="{r}" fill="{C_YELLOW}" opacity="0.5" '
                f'filter="url(#{glow})"/>')

CARD_RENDERERS["FlameInheritance"] = render_flameinheritance


def render_flameshadowart(s):
    """Shadowy dark flames."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    g_dark = lin_grad(s, [("0%",C_DARK_RED2,0.8),("30%",C_DARK_RED,0.5),
                           ("60%","#3a1010",0.3),("100%",C_DARK_BG,0)],
                      "0%","100%","0%","0%")
    g_edge = lin_grad(s, [("0%",C_DEEP_ORANGE2,0.4),("50%",C_DARK_RED,0.2),("100%",C_DARK_BG,0)])
    add_atmosphere(s, color=C_DARK_RED2, opacity=0.08)
    add_embers(s, 6, 3101, glow, colors=[C_DEEP_ORANGE2, C_DARK_RED])
    s.comment("Shadowy flame silhouettes")
    for cx, h, w, o in [(60,120,18,0.7),(95,140,20,0.6),(125,150,22,0.8),
                         (155,140,20,0.6),(190,120,18,0.7)]:
        s.draw(f'  <path d="{flame_path(cx, 170, h, w, 5, hash(str(cx))%100)}" '
                f'fill="url(#{g_dark})" opacity="{o}" filter="url(#{glow})"/>')
    s.comment("Dark flame edges")
    for cx, h, w in [(60,120,18),(125,150,22),(190,120,18)]:
        s.draw(f'  <path d="{flame_path(cx, 170, h, w, 5, hash(str(cx)+'e')%100)}" '
                f'fill="none" stroke="url(#{g_edge})" stroke-width="1.5" opacity="0.5"/>')
    s.comment("Dark ember wisps")
    rng = random.Random(3102)
    for _ in range(12):
        x = rng.uniform(40, 210)
        y = rng.uniform(20, 160)
        r = rng.uniform(1, 2.5)
        s.draw(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{C_DARK_RED}" '
                f'opacity="0.4" filter="url(#{glow})"/>')
    s.comment("Glowing core")
    s.draw(f'  <circle cx="125" cy="100" r="8" fill="{C_DEEP_ORANGE2}" opacity="0.4" '
            f'filter="url(#{glow})"/>')

CARD_RENDERERS["FlameShadowArt"] = render_flameshadowart


def render_flamewhirl(s):
    """Flame whirlwind."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    g_flame = lin_grad(s, [("0%",C_DARK_RED,0.2),("40%",C_DEEP_ORANGE,0.6),
                            ("70%",C_ORANGE,0.8),("100%",C_YELLOW,0.5)],
                      "0%","100%","0%","0%")
    add_atmosphere(s, opacity=0.06)
    add_embers(s, 10, 3201, glow)
    s.comment("Spiral flame arms")
    for start_a in [0, 120, 240]:
        pts = []
        for t in range(0, 120, 4):
            a = math.radians(start_a + t * 4)
            r = 10 + t * 0.8
            x = 125 + r * math.cos(a) * 0.7
            y = 95 + r * math.sin(a) * 0.5 - t * 0.3
            if y < 10 or y > 180:
                break
            pts.append(f"{x:.1f} {y:.1f}")
        if len(pts) > 2:
            path = "M " + " L ".join(pts)
            s.draw(f'  <path d="{path}" fill="none" stroke="url(#{g_flame})" '
                    f'stroke-width="5" opacity="0.5" filter="url(#{glow})"/>')
    s.comment("Whirlwind core")
    s.draw(f'  <ellipse cx="125" cy="140" rx="25" ry="10" fill="{C_ORANGE}" '
            f'opacity="0.5" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="140" r="8" fill="{C_YELLOW}" opacity="0.6" filter="url(#{glow})"/>')

CARD_RENDERERS["FlameWhirl"] = render_flamewhirl


def render_passingthetorch(s):
    """Flame passing fire."""
    glow = add_glow(s, 3)
    add_bg(s)
    g_torch = lin_grad(s, [("0%","#3a2a1a"),("50%","#5a3a2a"),("100%","#3a2a1a")])
    g_flame = lin_grad(s, [("0%",C_DARK_RED,0.3),("40%",C_DEEP_ORANGE,0.7),
                            ("70%",C_ORANGE,0.9),("100%",C_YELLOW,0.5)],
                      "0%","100%","0%","0%")
    g_transfer = lin_grad(s, [("0%",C_DARK_RED,0),("50%",C_ORANGE,0.5),("100%",C_YELLOW,0.8)])
    add_atmosphere(s, opacity=0.05)
    add_embers(s, 8, 3301, glow)
    s.comment("Left torch")
    s.draw(f'  <rect x="35" y="100" width="10" height="70" fill="url(#{g_torch})" rx="2"/>')
    s.draw(f'  <rect x="33" y="95" width="14" height="8" fill="#4a2818" rx="1"/>')
    s.draw(f'  <path d="{flame_path(40, 95, 55, 12, 3, 1)}" fill="url(#{g_flame})" '
            f'opacity="0.8" filter="url(#{glow})"/>')
    s.comment("Right torch")
    s.draw(f'  <rect x="205" y="100" width="10" height="70" fill="url(#{g_torch})" rx="2"/>')
    s.draw(f'  <rect x="203" y="95" width="14" height="8" fill="#4a2818" rx="1"/>')
    s.comment("Flame transfer arc")
    s.draw(f'  <path d="M 40 75 Q 125 30 210 75" fill="none" '
            f'stroke="url(#{g_transfer})" stroke-width="4" opacity="0.6" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 40 75 Q 125 40 210 75" fill="none" '
            f'stroke="{C_YELLOW}" stroke-width="2" opacity="0.5" filter="url(#{glow})"/>')
    s.comment("Transferred flame at right")
    s.draw(f'  <circle cx="210" cy="75" r="8" fill="{C_ORANGE}" opacity="0.7" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="210" cy="75" r="3" fill="{C_WHITE_HOT}" opacity="0.9"/>')
    add_spark_burst(s, 125, 40, 8, 3302, 20, glow=glow)

CARD_RENDERERS["PassingTheTorch"] = render_passingthetorch


def render_reedsspear(s):
    """Massive fire lance."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    g_shaft = lin_grad(s, [("0%","#3a1f15"),("30%","#5a3828"),("50%","#6a4838"),
                            ("70%","#5a3828"),("100%","#3a1f15")])
    g_blade = lin_grad(s, [("0%",C_WHITE_HOT),("20%",C_YELLOW),("50%",C_ORANGE),
                            ("80%",C_DEEP_ORANGE),("100%",C_DARK_RED)])
    g_blade_glow = rad_grad(s, [("0%",C_WHITE_HOT,0.9),("30%",C_YELLOW,0.6),
                                 ("60%",C_ORANGE,0.3),("100%",C_DEEP_ORANGE2,0)])
    add_atmosphere(s, opacity=0.06, filt=soft)
    add_embers(s, 12, 3401, glow)
    s.comment("Massive spear (diagonal)")
    s.draw(f'  <g transform="rotate(-30 125 95)">')
    s.draw(f'    <ellipse cx="125" cy="50" rx="40" ry="50" fill="url(#{g_blade_glow})" '
            f'filter="url(#{glow})"/>')
    s.draw(f'    <rect x="115" y="45" width="20" height="140" fill="url(#{g_shaft})" rx="3"/>')
    for y in [80, 100, 120, 140, 160]:
        s.draw(f'    <rect x="113" y="{y}" width="24" height="4" fill="{C_DARK_BG}" opacity="0.6"/>')
    s.draw(f'    <rect x="100" y="40" width="50" height="8" fill="#4a2818" rx="2"/>')
    s.draw(f'    <path d="M 125 5 L 105 35 Q 100 48 105 55 L 125 52 L 145 55 '
            f'Q 150 48 145 35 Z" fill="url(#{g_blade})" filter="url(#{glow})"/>')
    s.draw(f'    <line x1="125" y1="8" x2="125" y2="52" stroke="{C_DEEP_ORANGE2}" '
            f'stroke-width="1.5" opacity="0.6"/>')
    s.draw(f'    <circle cx="125" cy="5" r="8" fill="{C_WHITE_HOT}" opacity="0.9" '
            f'filter="url(#{glow})"/>')
    s.draw(f'    <circle cx="125" cy="5" r="3" fill="#ffffff" opacity="0.95"/>')
    s.comment("Flames around blade")
    for fx, fy, fw, fh, fc, fo in [
        (100,50,-15,50,C_ORANGE,0.6),(150,50,15,50,C_ORANGE,0.6),
        (105,45,-10,45,"#ffaa30",0.5),(145,45,10,45,"#ffaa30",0.5)]:
        s.draw(f'    <path d="M {fx} {fy} Q {fx+fw} {fy-fh*0.4} {fx+fw*0.5} {fy-fh} '
                f'Q {fx} {fy-fh*0.4} {fx-fw*0.2} {fy} Z" fill="{fc}" opacity="{fo}" '
                f'filter="url(#{glow})"/>')
    s.draw(f'    <path d="M 115 45 Q 120 20 125 0 Q 130 20 135 45 Z" '
            f'fill="{C_WHITE_HOT}" opacity="0.4" filter="url(#{glow})"/>')
    s.draw(f'  </g>')
    add_embers(s, 8, 3402, glow)

CARD_RENDERERS["ReedsSpear"] = render_reedsspear


def render_scorchawakening(s):
    """Flames to raw energy."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    g_energy = rad_grad(s, [("0%",C_WHITE_HOT,0.9),("20%",C_YELLOW,0.7),
                             ("50%",C_ORANGE,0.4),("100%",C_DARK_RED,0)])
    add_atmosphere(s, opacity=0.06)
    add_embers(s, 10, 3501, glow)
    s.comment("Ground eruption")
    s.draw(f'  <path d="M 60 170 L 70 120 L 80 140 L 90 100 L 100 130 L 110 90 '
            f'L 125 110 L 140 90 L 150 130 L 160 100 L 170 140 L 180 120 L 190 170 Z" '
            f'fill="url(#{g_energy})" opacity="0.5" filter="url(#{glow})"/>')
    s.comment("Energy column")
    s.draw(f'  <ellipse cx="125" cy="95" rx="30" ry="70" fill="url(#{g_energy})" '
            f'filter="url(#{soft})"/>')
    s.draw(f'  <ellipse cx="125" cy="80" rx="15" ry="50" fill="{C_YELLOW}" '
            f'opacity="0.3" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="60" r="10" fill="{C_WHITE_HOT}" opacity="0.8" '
            f'filter="url(#{glow})"/>')
    s.comment("Energy arcs")
    for i in range(6):
        a = math.radians(i * 60)
        x1 = 125 + 15 * math.cos(a)
        y1 = 95 + 15 * math.sin(a)
        x2 = 125 + 45 * math.cos(a)
        y2 = 95 + 45 * math.sin(a)
        s.draw(f'  <path d="M {x1:.1f} {y1:.1f} Q {125+30*math.cos(a+0.3):.1f} '
                f'{95+30*math.sin(a+0.3):.1f} {x2:.1f} {y2:.1f}" '
                f'stroke="{C_YELLOW}" stroke-width="1.5" fill="none" '
                f'opacity="0.6" filter="url(#{glow})"/>')
    add_spark_burst(s, 125, 60, 10, 3502, 30, glow=glow)
    for x, y, r, c, o in [(90,120,2,C_ORANGE,0.5),(160,120,2,C_ORANGE,0.5),
                           (100,50,1.5,C_YELLOW,0.7),(150,50,1.5,C_YELLOW,0.7)]:
        s.draw(f'  <circle cx="{x}" cy="{y}" r="{r}" fill="{c}" opacity="{o}" '
                f'filter="url(#{glow})"/>')
    add_bottom_glow(s, 125, 170, 50, 8, color=C_DEEP_ORANGE, opacity=0.3, glow=soft)

CARD_RENDERERS["ScorchAwakening"] = render_scorchawakening


# ---- RARE (21) ----

def render_scorchburst(s):
    """Explosive scorch nova."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 6)
    add_bg(s)
    g_nova = rad_grad(s, [("0%",C_WHITE_HOT,1),("15%",C_YELLOW,0.9),
                          ("40%",C_ORANGE,0.6),("70%",C_DEEP_ORANGE,0.3),
                          ("100%",C_DARK_RED,0)])
    g_ray = lin_grad(s, [("0%",C_WHITE_HOT,0.9),("50%",C_ORANGE,0.5),("100%",C_DARK_RED,0)])
    add_atmosphere(s, opacity=0.06)
    add_embers(s, 12, 3601, glow)
    s.comment("Explosion core")
    s.draw(f'  <circle cx="125" cy="95" r="50" fill="url(#{g_nova})" filter="url(#{soft})"/>')
    s.draw(f'  <circle cx="125" cy="95" r="25" fill="{C_WHITE_HOT}" opacity="0.5" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="95" r="10" fill="#ffffff" opacity="0.8"/>')
    s.comment("Shockwave rays")
    for i in range(12):
        a = math.radians(i * 30)
        x1 = 125 + 30 * math.cos(a)
        y1 = 95 + 30 * math.sin(a)
        x2 = 125 + 80 * math.cos(a)
        y2 = 95 + 80 * math.sin(a)
        s.draw(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="url(#{g_ray})" stroke-width="3" opacity="0.5" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="95" r="60" fill="none" stroke="{C_ORANGE}" '
            f'stroke-width="2" opacity="0.3" filter="url(#{soft})"/>')
    s.draw(f'  <circle cx="125" cy="95" r="75" fill="none" stroke="{C_DEEP_ORANGE}" '
            f'stroke-width="1" opacity="0.2"/>')
    add_spark_burst(s, 125, 95, 16, 3602, 40, glow=glow)
    for cx, cy, r, c, o in [(60,70,2,C_ORANGE,0.5),(190,70,2,C_ORANGE,0.5),
                             (60,120,2,C_DEEP_ORANGE,0.4),(190,120,2,C_DEEP_ORANGE,0.4),
                             (125,40,2,C_YELLOW,0.6),(125,150,2,C_YELLOW,0.6)]:
        s.draw(f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}" opacity="{o}" filter="url(#{glow})"/>')

CARD_RENDERERS["ScorchBurst"] = render_scorchburst


def render_scorchedearth(s):
    """Cracked earth with lava seeping."""
    glow = add_glow(s, 2.5)
    add_bg(s)
    g_earth = lin_grad(s, [("0%","#3a2a18"),("40%","#2a1f15"),("100%","#1a120a")],"0%","0%","0%","100%")
    g_lava = lin_grad(s, [("0%",C_WHITE_HOT),("30%",C_YELLOW),("60%",C_ORANGE),("100%",C_DEEP_ORANGE2)])
    add_atmosphere(s, color=C_DEEP_ORANGE, opacity=0.05)
    add_ash_particles(s, 10, 3701)
    add_embers(s, 6, 3702, glow)
    s.draw(f'  <path d="M 0 110 Q 50 105 100 112 Q 150 108 200 115 Q 230 110 250 112 '
            f'L 250 190 L 0 190 Z" fill="url(#{g_earth})"/>')
    for pts in ["M 20 120 L 40 140 L 35 160 L 50 175",
                "M 80 115 L 95 135 L 85 155 L 100 170",
                "M 130 118 L 145 138 L 135 158 L 150 172",
                "M 180 120 L 195 140 L 185 160 L 200 175",
                "M 220 115 L 230 135 L 225 155 L 235 170"]:
        s.draw(f'  <path d="{pts}" stroke="url(#{g_lava})" stroke-width="2.5" '
                f'fill="none" opacity="0.7" filter="url(#{glow})"/>')
    for cx, cy, rx, ry in [(35,165,18,6),(100,160,22,7),(150,165,20,6),(215,158,15,5)]:
        s.draw(f'  <ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" '
                f'fill="url(#{g_lava})" opacity="0.6" filter="url(#{glow})"/>')
    for cx, base, h, w, c, o in [(40,140,25,8,C_ORANGE,0.5),(90,135,30,10,C_ORANGE,0.5),
                                  (145,138,28,9,C_DEEP_ORANGE,0.4),(195,140,22,8,C_ORANGE,0.4)]:
        s.draw(f'  <path d="{flame_path(cx, base, h, w, 2, int(cx*7+h))}" '
                f'fill="{c}" opacity="{o}" filter="url(#{glow})"/>')
    for y in [50, 65, 80]:
        s.draw(f'  <path d="M 10 {y} Q 60 {y-3} 125 {y} Q 190 {y+3} 240 {y}" '
                f'stroke="{C_DEEP_ORANGE}" stroke-width="0.5" fill="none" opacity="0.1"/>')
    add_bottom_glow(s, 125, 180, 80, 8, color=C_DARK_RED, opacity=0.3, glow=glow)

CARD_RENDERERS["ScorchedEarth"] = render_scorchedearth


def render_scorchedearthprotocol(s):
    """Earth-protocol fire wall barrier."""
    glow = add_glow(s, 2.5)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    g_wall = lin_grad(s, [("0%",C_DARK_RED),("30%",C_DEEP_ORANGE),("60%",C_ORANGE),("100%",C_YELLOW3)],
                      "0%","100%","0%","0%")
    g_rune = rad_grad(s, [("0%",C_WHITE_HOT,0.9),("40%",C_YELLOW,0.6),("100%",C_DARK_RED,0)])
    add_atmosphere(s, opacity=0.05)
    add_embers(s, 10, 3801, glow)
    s.draw(f'  <path d="M 10 100 Q 30 50 60 80 Q 80 40 110 70 Q 125 30 140 70 '
            f'Q 170 40 190 80 Q 220 50 240 100 L 240 190 L 10 190 Z" '
            f'fill="url(#{g_wall})" opacity="0.6" filter="url(#{soft})"/>')
    for cx, cy in [(50,120),(100,115),(150,120),(200,115)]:
        s.draw(f'  <circle cx="{cx}" cy="{cy}" r="8" fill="url(#{g_rune})" '
                f'opacity="0.6" filter="url(#{glow})"/>')
        s.draw(f'  <rect x="{cx-4}" y="{cy-4}" width="8" height="8" fill="none" '
                f'stroke="{C_YELLOW}" stroke-width="0.8" opacity="0.5" '
                f'transform="rotate(45 {cx} {cy})"/>')
    for x1, y1, x2, y2 in [(50,120,100,115),(100,115,150,120),(150,120,200,115)]:
        s.draw(f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                f'stroke="{C_YELLOW}" stroke-width="1" opacity="0.4" filter="url(#{glow})"/>')
    for cx, base, h, w, c, o in [(30,100,40,10,C_ORANGE,0.5),(80,80,50,12,C_ORANGE,0.5),
                                  (125,70,55,14,C_YELLOW,0.4),(170,80,50,12,C_ORANGE,0.5),
                                  (220,100,40,10,C_DEEP_ORANGE,0.4)]:
        s.draw(f'  <path d="{flame_path(cx, base, h, w, 3, int(cx*5+base))}" '
                f'fill="{c}" opacity="{o}" filter="url(#{glow})"/>')
    add_bottom_glow(s, 125, 185, 100, 8, color=C_DARK_RED, opacity=0.4, glow=soft)

CARD_RENDERERS["ScorchedEarthProtocol"] = render_scorchedearthprotocol


def render_scorchingheart(s):
    """Burning heart core."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 6)
    add_bg(s)
    g_heart = rad_grad(s, [("0%",C_WHITE_HOT),("20%",C_YELLOW),("50%",C_ORANGE),
                           ("80%",C_DEEP_ORANGE),("100%",C_DARK_RED)])
    g_aura = rad_grad(s, [("0%",C_ORANGE,0.4),("50%",C_DEEP_ORANGE,0.2),("100%",C_DARK_RED,0)])
    add_atmosphere(s, color=C_DARK_RED, opacity=0.06)
    add_embers(s, 12, 3901, glow)
    s.draw(f'  <ellipse cx="125" cy="95" rx="70" ry="65" fill="url(#{g_aura})" filter="url(#{soft})"/>')
    s.draw(f'  <path d="M 125 140 C 90 110 70 90 70 70 C 70 50 90 45 100 55 '
            f'C 110 65 120 70 125 80 C 130 70 140 65 150 55 '
            f'C 160 45 180 50 180 70 C 180 90 160 110 125 140 Z" '
            f'fill="url(#{g_heart})" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 100 60 C 95 65 90 70 92 78 C 95 72 100 68 105 65 Z" '
            f'fill="{C_WHITE_HOT}" opacity="0.5"/>')
    for pts in ["M 125 80 Q 120 100 115 120","M 125 80 Q 130 100 135 120",
                "M 125 80 Q 125 110 125 130"]:
        s.draw(f'  <path d="{pts}" stroke="{C_DEEP_ORANGE2}" stroke-width="1" '
                f'fill="none" opacity="0.4"/>')
    s.draw(f'  <circle cx="125" cy="85" r="12" fill="{C_WHITE_HOT}" opacity="0.6" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="85" r="5" fill="#ffffff" opacity="0.9"/>')
    add_spark_burst(s, 125, 85, 10, 3902, 35, glow=glow)
    for cx, cy, r, c, o in [(90,60,2,C_ORANGE,0.5),(160,60,2,C_ORANGE,0.5),
                             (80,100,1.5,C_YELLOW,0.4),(170,100,1.5,C_YELLOW,0.4)]:
        s.draw(f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}" opacity="{o}" filter="url(#{glow})"/>')

CARD_RENDERERS["ScorchingHeart"] = render_scorchingheart


def render_searingpierce(s):
    """Piercing fire lance."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    g_lance = lin_grad(s, [("0%",C_DARK_RED,0),("20%",C_DEEP_ORANGE,0.3),
                           ("50%",C_ORANGE,0.7),("80%",C_YELLOW,0.9),
                           ("100%",C_WHITE_HOT,1)], "0%","100%","0%","0%")
    g_trail = lin_grad(s, [("0%",C_DARK_RED,0),("40%",C_DEEP_ORANGE,0.2),
                           ("70%",C_ORANGE,0.4),("100%",C_YELLOW,0.6)], "0%","100%","0%","0%")
    g_tip = rad_grad(s, [("0%",C_WHITE_HOT,1),("30%",C_YELLOW,0.8),("70%",C_ORANGE,0.4),("100%",C_DARK_RED,0)])
    add_atmosphere(s, opacity=0.05)
    add_embers(s, 8, 4001, glow)
    for y, sw, op in [(50,1,0.12),(65,1.5,0.15),(125,1,0.12),(140,1.5,0.15)]:
        s.draw(f'  <line x1="5" y1="{y}" x2="245" y2="{y}" stroke="{C_ORANGE}" '
                f'stroke-width="{sw}" opacity="{op}"/>')
    s.draw(f'  <path d="M 10 100 Q 60 90 110 95 Q 160 100 210 90 L 210 110 '
            f'Q 160 120 110 115 Q 60 110 10 120 Z" fill="url(#{g_trail})" '
            f'opacity="0.5" filter="url(#{soft})"/>')
    s.draw(f'  <path d="M 15 95 L 220 90 L 225 100 L 220 110 L 15 105 Z" '
            f'fill="url(#{g_lance})" filter="url(#{glow})"/>')
    s.draw(f'  <line x1="15" y1="100" x2="220" y2="100" stroke="{C_WHITE_HOT}" '
            f'stroke-width="1.5" opacity="0.6"/>')
    s.draw(f'  <circle cx="225" cy="100" r="12" fill="url(#{g_tip})" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="225" cy="100" r="4" fill="{C_WHITE_HOT}" opacity="0.9"/>')
    for x, y, w, h, c, o in [(40,100,10,20,C_ORANGE,0.4),(80,98,10,22,"#ffaa30",0.4),
                              (120,100,10,20,C_ORANGE,0.4),(160,98,10,22,C_DEEP_ORANGE,0.3)]:
        s.draw(f'  <path d="M {x} {y} Q {x+w} {y-h*0.4} {x+w*0.5} {y-h} '
                f'Q {x} {y-h*0.4} {x-w*0.2} {y} Z" fill="{c}" opacity="{o}" filter="url(#{glow})"/>')
    add_spark_burst(s, 225, 100, 10, 4002, 30, glow=glow)

CARD_RENDERERS["SearingPierce"] = render_searingpierce


def render_shadowflameprowl(s):
    """Shadow flame stalking."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 5)
    add_bg(s, c0="#1a0a08", c1="#0a0404", c2="#050202")
    g_shadow = rad_grad(s, [("0%",C_DEEP_ORANGE,0.4),("40%",C_DARK_RED,0.2),("100%",C_DARK_BG2,0)])
    g_eye = rad_grad(s, [("0%",C_WHITE_HOT,1),("40%",C_YELLOW,0.8),("100%",C_ORANGE,0)])
    add_atmosphere(s, color=C_DARK_RED, opacity=0.08)
    add_embers(s, 10, 4101, glow, colors=[C_DEEP_ORANGE, C_DARK_RED, C_ORANGE])
    s.draw(f'  <path d="M 30 140 C 30 100 50 80 80 75 C 100 70 120 75 140 80 '
            f'C 170 85 200 90 220 110 C 225 120 220 130 215 140 '
            f'C 210 145 200 142 190 145 L 190 155 L 180 145 '
            f'C 170 148 160 145 150 148 L 150 155 L 140 148 '
            f'C 100 150 60 148 30 140 Z" fill="url(#{g_shadow})" '
            f'opacity="0.7" filter="url(#{soft})"/>')
    for cx, base, h, w, c, o in [(60,75,30,8,C_DEEP_ORANGE,0.5),(100,70,35,10,C_ORANGE,0.4),
                                  (150,75,30,8,C_DEEP_ORANGE,0.4),(190,85,25,7,C_DARK_RED,0.3)]:
        s.draw(f'  <path d="{flame_path(cx, base, h, w, 4, int(cx*3+h))}" '
                f'fill="{c}" opacity="{o}" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="90" cy="100" r="5" fill="url(#{g_eye})" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="160" cy="105" r="5" fill="url(#{g_eye})" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="90" cy="100" r="2" fill="{C_WHITE_HOT}" opacity="0.9"/>')
    s.draw(f'  <circle cx="160" cy="105" r="2" fill="{C_WHITE_HOT}" opacity="0.9"/>')
    for pts in ["M 30 140 Q 10 120 5 100","M 220 110 Q 240 100 245 80",
                "M 125 150 Q 120 170 115 185","M 100 148 Q 90 165 85 180"]:
        s.draw(f'  <path d="{pts}" stroke="{C_DARK_RED}" stroke-width="2" '
                f'fill="none" opacity="0.3" filter="url(#{soft})"/>')
    add_bottom_glow(s, 125, 155, 60, 6, color=C_DARK_RED, opacity=0.3, glow=soft)

CARD_RENDERERS["ShadowflameProwl"] = render_shadowflameprowl


def render_witheredrevival(s):
    """Withered plant reviving with fire."""
    glow = add_glow(s, 2.5)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    g_stem = lin_grad(s, [("0%","#4a3020"),("50%","#6a4830"),("100%","#3a2010")])
    g_bloom = rad_grad(s, [("0%",C_WHITE_HOT,0.9),("30%",C_YELLOW,0.7),
                           ("60%",C_ORANGE,0.4),("100%",C_DEEP_ORANGE,0)])
    add_atmosphere(s, color=C_DEEP_ORANGE, opacity=0.05)
    add_ash_particles(s, 8, 4201)
    add_embers(s, 6, 4202, glow)
    s.comment("Withered roots")
    for pts in ["M 125 170 Q 100 175 80 180","M 125 170 Q 150 175 170 180",
                "M 125 170 Q 115 180 105 185","M 125 170 Q 135 180 145 185"]:
        s.draw(f'  <path d="{pts}" stroke="#3a2010" stroke-width="2" fill="none" opacity="0.6"/>')
    s.draw(f'  <path d="M 122 170 Q 120 130 123 90 Q 121 60 125 40" '
            f'stroke="url(#{g_stem})" stroke-width="4" fill="none"/>')
    for cx, cy, w, h in [(110,120,15,8),(140,100,15,8),(115,70,12,6),(135,55,12,6)]:
        s.draw(f'  <ellipse cx="{cx}" cy="{cy}" rx="{w}" ry="{h}" fill="#4a3020" opacity="0.5"/>')
    s.draw(f'  <circle cx="125" cy="35" r="25" fill="url(#{g_bloom})" filter="url(#{soft})"/>')
    s.draw(f'  <path d="{flame_path(125, 45, 30, 12, 3, 4210)}" '
            f'fill="{C_ORANGE}" opacity="0.6" filter="url(#{glow})"/>')
    s.draw(f'  <path d="{flame_path(120, 45, 25, 8, 2, 4211)}" '
            f'fill="{C_YELLOW}" opacity="0.5" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="35" r="8" fill="{C_WHITE_HOT}" opacity="0.7" filter="url(#{glow})"/>')
    for cx, cy, r, c, o in [(110,120,2,C_ORANGE,0.5),(140,100,2,C_ORANGE,0.5),
                             (115,70,1.5,C_YELLOW,0.5),(135,55,1.5,C_YELLOW,0.5)]:
        s.draw(f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}" opacity="{o}" filter="url(#{glow})"/>')
    add_spark_burst(s, 125, 35, 8, 4203, 25, glow=glow)

CARD_RENDERERS["WitheredRevival"] = render_witheredrevival


def render_ashrecovery(s):
    """Ash reforming into shape."""
    glow = add_glow(s, 2.5)
    soft = add_soft_glow(s, 4)
    add_bg(s)
    g_form = rad_grad(s, [("0%",C_ORANGE,0.5),("40%",C_DEEP_ORANGE,0.3),("100%",C_DARK_RED,0)])
    add_atmosphere(s, color=C_DEEP_ORANGE, opacity=0.05)
    add_ash_particles(s, 20, 4301)
    add_embers(s, 8, 4302, glow)
    s.draw(f'  <path d="M 90 170 Q 85 140 95 110 Q 100 80 110 60 '
            f'Q 115 45 125 40 Q 135 45 140 60 Q 150 80 155 110 '
            f'Q 165 140 160 170 Z" fill="url(#{g_form})" opacity="0.5" '
            f'filter="url(#{soft})"/>')
    rng = random.Random(4303)
    for _ in range(15):
        x = rng.uniform(20, 230)
        y = rng.uniform(0, 40)
        x2 = 125 + rng.uniform(-20, 20)
        y2 = 95 + rng.uniform(-30, 30)
        s.draw(f'  <line x1="{x:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="{ASH_COLORS[2]}" stroke-width="0.8" opacity="0.3"/>')
    s.draw(f'  <circle cx="125" cy="95" r="15" fill="{C_ORANGE}" opacity="0.5" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="95" r="6" fill="{C_YELLOW}" opacity="0.7" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="95" r="2" fill="{C_WHITE_HOT}" opacity="0.9"/>')
    for cx, cy, r, c, o in [(100,80,2,C_ORANGE,0.5),(150,80,2,C_ORANGE,0.5),
                             (110,120,1.5,C_YELLOW,0.4),(140,120,1.5,C_YELLOW,0.4)]:
        s.draw(f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}" opacity="{o}" filter="url(#{glow})"/>')

CARD_RENDERERS["AshRecovery"] = render_ashrecovery


def render_emberpact(s):
    """Ember pact — glowing hand with fire."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    g_palm = rad_grad(s, [("0%",C_WHITE_HOT,0.8),("30%",C_YELLOW,0.5),
                           ("70%",C_ORANGE,0.3),("100%",C_DARK_RED,0)])
    g_pact = rad_grad(s, [("0%",C_WHITE_HOT,1),("30%",C_YELLOW,0.8),
                          ("60%",C_ORANGE,0.5),("100%",C_DARK_RED,0)])
    add_atmosphere(s, opacity=0.06)
    add_embers(s, 10, 4401, glow)
    s.draw(f'  <path d="M 80 170 L 85 120 Q 80 100 85 85 Q 90 75 95 85 '
            f'Q 93 100 98 110 L 100 80 Q 105 70 110 80 L 108 115 '
            f'Q 115 75 120 80 Q 125 75 125 85 L 122 115 '
            f'Q 130 80 135 85 Q 140 80 138 95 L 140 130 '
            f'Q 145 140 140 155 Q 130 170 110 170 Z" '
            f'fill="url(#{g_palm})" opacity="0.5" filter="url(#{soft})"/>')
    s.draw(f'  <circle cx="115" cy="140" r="20" fill="url(#{g_pact})" filter="url(#{glow})"/>')
    s.draw(f'  <path d="{flame_path(115, 145, 35, 12, 3, 4410)}" '
            f'fill="{C_ORANGE}" opacity="0.6" filter="url(#{glow})"/>')
    s.draw(f'  <path d="{flame_path(115, 145, 25, 8, 2, 4411)}" '
            f'fill="{C_YELLOW}" opacity="0.5" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="115" cy="140" r="6" fill="{C_WHITE_HOT}" opacity="0.8"/>')
    for pts in ["M 85 140 Q 90 135 95 140","M 135 140 Q 140 135 145 140"]:
        s.draw(f'  <path d="{pts}" stroke="{C_YELLOW}" stroke-width="1" fill="none" '
                f'opacity="0.5" filter="url(#{glow})"/>')
    add_spark_burst(s, 115, 140, 10, 4402, 30, glow=glow)

CARD_RENDERERS["EmberPact"] = render_emberpact


def render_scorchingbond(s):
    """Two flames linked by bond."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    g_flame1 = rad_grad(s, [("0%",C_WHITE_HOT,0.9),("30%",C_YELLOW,0.7),
                             ("60%",C_ORANGE,0.4),("100%",C_DARK_RED,0)])
    g_flame2 = rad_grad(s, [("0%",C_WHITE_HOT,0.9),("30%",C_YELLOW,0.7),
                             ("60%",C_DEEP_ORANGE,0.4),("100%",C_DARK_RED,0)])
    g_bond = lin_grad(s, [("0%",C_ORANGE,0.6),("50%",C_WHITE_HOT,0.8),("100%",C_DEEP_ORANGE,0.6)])
    add_atmosphere(s, opacity=0.05)
    add_embers(s, 10, 4501, glow)
    s.draw(f'  <circle cx="70" cy="95" r="30" fill="url(#{g_flame1})" filter="url(#{soft})"/>')
    s.draw(f'  <path d="{flame_path(70, 110, 50, 15, 3, 4510)}" '
            f'fill="{C_ORANGE}" opacity="0.6" filter="url(#{glow})"/>')
    s.draw(f'  <path d="{flame_path(70, 110, 35, 10, 2, 4511)}" '
            f'fill="{C_YELLOW}" opacity="0.5" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="180" cy="95" r="30" fill="url(#{g_flame2})" filter="url(#{soft})"/>')
    s.draw(f'  <path d="{flame_path(180, 110, 50, 15, 3, 4512)}" '
            f'fill="{C_DEEP_ORANGE}" opacity="0.6" filter="url(#{glow})"/>')
    s.draw(f'  <path d="{flame_path(180, 110, 35, 10, 2, 4513)}" '
            f'fill="{C_YELLOW}" opacity="0.5" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 100 95 Q 125 75 150 95" stroke="url(#{g_bond})" '
            f'stroke-width="4" fill="none" opacity="0.7" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 100 95 Q 125 115 150 95" stroke="url(#{g_bond})" '
            f'stroke-width="2" fill="none" opacity="0.5" filter="url(#{glow})"/>')
    for cx, cy, r, c, o in [(110,85,2,C_YELLOW,0.6),(140,85,2,C_YELLOW,0.6),
                             (125,75,2.5,C_WHITE_HOT,0.7),(125,100,2,C_ORANGE,0.5)]:
        s.draw(f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}" opacity="{o}" filter="url(#{glow})"/>')
    add_spark_burst(s, 125, 95, 8, 4502, 25, glow=glow)

CARD_RENDERERS["ScorchingBond"] = render_scorchingbond


def render_breathofcalamity(s):
    """Devastating dragon breath."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 6)
    add_bg(s)
    g_breath = lin_grad(s, [("0%",C_WHITE_HOT,1),("20%",C_YELLOW,0.9),
                            ("50%",C_ORANGE,0.7),("80%",C_DEEP_ORANGE,0.4),
                            ("100%",C_DARK_RED,0)], "0%","0%","100%","0%")
    add_atmosphere(s, color=C_DARK_RED, opacity=0.08)
    add_embers(s, 15, 4601, glow)
    s.draw(f'  <circle cx="30" cy="95" r="20" fill="{C_WHITE_HOT}" opacity="0.5" filter="url(#{soft})"/>')
    s.draw(f'  <path d="M 30 95 L 20 60 Q 100 40 200 50 Q 240 55 245 70 '
            f'L 245 120 Q 240 135 200 140 Q 100 150 20 130 Z" '
            f'fill="url(#{g_breath})" opacity="0.6" filter="url(#{soft})"/>')
    s.draw(f'  <path d="M 30 95 L 40 80 Q 120 70 200 80 Q 230 85 240 90 '
            f'L 240 100 Q 230 105 200 110 Q 120 120 40 110 Z" '
            f'fill="{C_YELLOW}" opacity="0.4" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 30 95 L 50 90 Q 120 85 200 90 L 200 100 '
            f'Q 120 105 50 100 Z" fill="{C_WHITE_HOT}" opacity="0.4"/>')
    s.draw(f'  <path d="M 5 85 Q 10 75 20 78 Q 15 85 25 88 Q 20 95 30 95 '
            f'L 30 100 Q 20 102 25 108 Q 15 105 20 112 Q 10 115 5 105 Z" '
            f'fill="{C_DARK_BG}" opacity="0.7"/>')
    for cx, base, h, w, c, o in [(100,50,30,10,C_ORANGE,0.5),(150,55,35,12,C_DEEP_ORANGE,0.4),
                                  (200,50,30,10,C_ORANGE,0.5),(100,140,30,10,C_ORANGE,0.4),
                                  (150,135,35,12,C_DEEP_ORANGE,0.4),(200,140,30,10,C_ORANGE,0.4)]:
        s.draw(f'  <path d="{flame_path(cx, base, h, w, 4, int(cx*3+h))}" '
                f'fill="{c}" opacity="{o}" filter="url(#{glow})"/>')
    add_spark_burst(s, 30, 95, 12, 4602, 40, glow=glow)
    add_spark_burst(s, 200, 95, 10, 4603, 30, glow=glow)

CARD_RENDERERS["BreathOfCalamity"] = render_breathofcalamity


def render_dragonslegacy(s):
    """Ancient dragon legacy aura."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 6)
    add_bg(s)
    g_aura = rad_grad(s, [("0%",C_WHITE_HOT,0.6),("20%",C_YELLOW,0.4),
                          ("50%",C_ORANGE,0.2),("100%",C_DARK_RED,0)])
    g_scale = lin_grad(s, [("0%",C_YELLOW3),("50%",C_ORANGE),("100%",C_DEEP_ORANGE)])
    add_atmosphere(s, color=C_DARK_RED, opacity=0.06)
    add_embers(s, 12, 4701, glow)
    s.draw(f'  <ellipse cx="125" cy="95" rx="90" ry="80" fill="url(#{g_aura})" filter="url(#{soft})"/>')
    s.draw(f'  <path d="M 60 130 Q 50 100 70 80 Q 90 60 120 55 Q 150 60 170 80 '
            f'Q 185 95 180 120 Q 170 135 140 130 Q 125 135 110 130 '
            f'Q 90 135 80 130 Q 70 132 60 130 Z" fill="{C_DARK_BG2}" '
            f'opacity="0.6" filter="url(#{soft})"/>')
    s.draw(f'  <ellipse cx="100" cy="90" rx="6" ry="4" fill="{C_YELLOW}" opacity="0.8" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="100" cy="90" r="2" fill="{C_WHITE_HOT}" opacity="0.9"/>')
    for cx, cy, r in [(70,110,5),(85,100,4),(100,115,5),(115,105,4),
                      (130,110,5),(145,100,4),(160,115,5),(175,105,4)]:
        s.draw(f'  <path d="M {cx-r} {cy} Q {cx} {cy-r*0.8} {cx+r} {cy} '
                f'Q {cx} {cy+r*0.8} {cx-r} {cy} Z" fill="url(#{g_scale})" '
                f'opacity="0.5" filter="url(#{glow})"/>')
    for cx, base, h, w, c, o in [(90,55,30,10,C_ORANGE,0.5),(125,50,35,12,C_YELLOW,0.4),
                                  (160,55,30,10,C_ORANGE,0.5)]:
        s.draw(f'  <path d="{flame_path(cx, base, h, w, 3, int(cx*4+h))}" '
                f'fill="{c}" opacity="{o}" filter="url(#{glow})"/>')
    add_spark_burst(s, 125, 80, 10, 4702, 30, glow=glow)

CARD_RENDERERS["DragonsLegacy"] = render_dragonslegacy


def render_everflame(s):
    """Eternal undying flame."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 6)
    add_bg(s)
    g_flame = rad_grad(s, [("0%",C_WHITE_HOT,1),("20%",C_YELLOW,0.8),
                           ("50%",C_ORANGE,0.5),("80%",C_DEEP_ORANGE,0.2),
                           ("100%",C_DARK_RED,0)])
    g_ring = lin_grad(s, [("0%",C_YELLOW),("50%",C_ORANGE),("100%",C_DEEP_ORANGE)])
    add_atmosphere(s, opacity=0.06)
    add_embers(s, 14, 4801, glow)
    s.draw(f'  <circle cx="125" cy="95" r="70" fill="none" stroke="url(#{g_ring})" '
            f'stroke-width="2" opacity="0.3" filter="url(#{soft})"/>')
    s.draw(f'  <circle cx="125" cy="95" r="65" fill="none" stroke="{C_YELLOW}" '
            f'stroke-width="1" opacity="0.2"/>')
    s.draw(f'  <ellipse cx="125" cy="100" rx="40" ry="60" fill="url(#{g_flame})" filter="url(#{soft})"/>')
    s.draw(f'  <path d="{flame_path(125, 160, 80, 20, 4, 4810)}" '
            f'fill="{C_ORANGE}" opacity="0.6" filter="url(#{glow})"/>')
    s.draw(f'  <path d="{flame_path(125, 160, 60, 14, 3, 4811)}" '
            f'fill="{C_YELLOW}" opacity="0.5" filter="url(#{glow})"/>')
    s.draw(f'  <path d="{flame_path(125, 160, 40, 10, 2, 4812)}" '
            f'fill="{C_WHITE_HOT}" opacity="0.4" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="85" r="15" fill="{C_WHITE_HOT}" opacity="0.6" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="85" r="6" fill="#ffffff" opacity="0.9"/>')
    for i in range(8):
        a = math.radians(i * 45)
        x = 125 + 68 * math.cos(a)
        y = 95 + 68 * math.sin(a)
        s.draw(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="2" fill="{C_YELLOW}" '
                f'opacity="0.5" filter="url(#{glow})"/>')
    add_spark_burst(s, 125, 85, 10, 4802, 35, glow=glow)

CARD_RENDERERS["Everflame"] = render_everflame


def render_flameshadowreed(s):
    """Reed's flame-shadow form."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 5)
    add_bg(s, c0="#1a0a08", c1="#0d0504", c2="#050202")
    g_reed = rad_grad(s, [("0%",C_ORANGE,0.4),("40%",C_DEEP_ORANGE,0.2),("100%",C_DARK_BG2,0)])
    g_flame = rad_grad(s, [("0%",C_WHITE_HOT,0.8),("30%",C_YELLOW,0.6),
                           ("60%",C_ORANGE,0.3),("100%",C_DARK_RED,0)])
    add_atmosphere(s, color=C_DARK_RED, opacity=0.08)
    add_embers(s, 12, 4901, glow, colors=[C_DEEP_ORANGE, C_ORANGE, C_DARK_RED])
    s.draw(f'  <path d="M 115 170 L 113 120 Q 110 90 115 60 Q 120 40 125 35 '
            f'Q 130 40 135 60 Q 140 90 137 120 L 135 170 Z" '
            f'fill="url(#{g_reed})" opacity="0.6" filter="url(#{soft})"/>')
    s.draw(f'  <circle cx="125" cy="35" r="20" fill="url(#{g_flame})" filter="url(#{soft})"/>')
    s.draw(f'  <path d="{flame_path(125, 45, 40, 14, 3, 4910)}" '
            f'fill="{C_ORANGE}" opacity="0.6" filter="url(#{glow})"/>')
    s.draw(f'  <path d="{flame_path(125, 45, 30, 10, 2, 4911)}" '
            f'fill="{C_YELLOW}" opacity="0.5" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="35" r="6" fill="{C_WHITE_HOT}" opacity="0.8"/>')
    for pts in ["M 115 120 Q 90 130 70 120","M 135 120 Q 160 130 180 120",
                "M 113 90 Q 85 80 60 85","M 137 90 Q 165 80 190 85"]:
        s.draw(f'  <path d="{pts}" stroke="{C_DARK_RED}" stroke-width="2" '
                f'fill="none" opacity="0.3" filter="url(#{soft})"/>')
    for cx, base, h, w, c, o in [(70,120,20,7,C_DEEP_ORANGE,0.4),(180,120,20,7,C_DEEP_ORANGE,0.4),
                                  (60,85,20,7,C_DARK_RED,0.3),(190,85,20,7,C_DARK_RED,0.3)]:
        s.draw(f'  <path d="{flame_path(cx, base, h, w, 3, int(cx*2+h))}" '
                f'fill="{c}" opacity="{o}" filter="url(#{glow})"/>')
    add_spark_burst(s, 125, 35, 10, 4902, 30, glow=glow)

CARD_RENDERERS["FlameShadowReed"] = render_flameshadowreed


def render_infernostorm(s):
    """Fire storm inferno."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 6)
    add_bg(s)
    g_storm = rad_grad(s, [("0%",C_WHITE_HOT,0.5),("20%",C_YELLOW,0.3),
                           ("50%",C_ORANGE,0.2),("100%",C_DARK_RED,0)])
    g_vortex = lin_grad(s, [("0%",C_ORANGE,0.6),("50%",C_YELLOW3,0.4),("100%",C_WHITE_HOT,0.2)],
                        "0%","100%","0%","0%")
    add_atmosphere(s, color=C_DARK_RED, opacity=0.08)
    add_embers(s, 20, 5001, glow)
    s.draw(f'  <ellipse cx="125" cy="95" rx="85" ry="75" fill="url(#{g_storm})" filter="url(#{soft})"/>')
    for start_a in [0, 72, 144, 216, 288]:
        pts = []
        for t in range(0, 80, 4):
            a = math.radians(start_a + t * 4.5)
            r = 75 - t * 0.8
            if r < 8:
                break
            x = 125 + r * math.cos(a)
            y = 95 + r * math.sin(a)
            pts.append(f"{x:.1f} {y:.1f}")
        if len(pts) > 1:
            path = "M " + " L ".join(pts)
            s.draw(f'  <path d="{path}" fill="none" stroke="url(#{g_vortex})" '
                    f'stroke-width="3" opacity="0.4" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="95" r="15" fill="{C_WHITE_HOT}" opacity="0.7" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="95" r="6" fill="#ffffff" opacity="0.9"/>')
    rng = random.Random(5002)
    for _ in range(15):
        x = rng.uniform(10, 240)
        y = rng.uniform(0, 60)
        length = rng.uniform(15, 35)
        s.draw(f'  <line x1="{x:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{y+length:.1f}" '
                f'stroke="{rng.choice([C_ORANGE,C_YELLOW,C_DEEP_ORANGE])}" '
                f'stroke-width="1.5" opacity="0.4" filter="url(#{glow})"/>')
    add_spark_burst(s, 125, 95, 14, 5003, 40, glow=glow)

CARD_RENDERERS["InfernoStorm"] = render_infernostorm


def render_unitedfront(s):
    """United flame front — wall of fire."""
    glow = add_glow(s, 2.5)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    g_wall = lin_grad(s, [("0%",C_DARK_RED),("30%",C_DEEP_ORANGE),("60%",C_ORANGE),
                          ("100%",C_YELLOW3)], "0%","100%","0%","0%")
    g_shield = rad_grad(s, [("0%",C_WHITE_HOT,0.6),("40%",C_YELLOW,0.3),("100%",C_DARK_RED,0)])
    add_atmosphere(s, opacity=0.05)
    add_embers(s, 12, 5101, glow)
    s.draw(f'  <path d="M 10 170 L 10 100 Q 20 70 40 80 Q 50 60 70 70 '
            f'Q 80 50 100 65 Q 110 45 125 55 Q 140 45 150 65 '
            f'Q 170 50 180 70 Q 200 60 210 80 Q 230 70 240 100 '
            f'L 240 170 Z" fill="url(#{g_wall})" opacity="0.6" filter="url(#{soft})"/>')
    for cx, base, h, w, c, o in [(30,100,40,10,C_ORANGE,0.5),(60,80,50,12,C_YELLOW,0.4),
                                  (90,70,55,14,C_ORANGE,0.5),(125,55,60,16,C_WHITE_HOT,0.3),
                                  (160,70,55,14,C_ORANGE,0.5),(190,80,50,12,C_YELLOW,0.4),
                                  (220,100,40,10,C_DEEP_ORANGE,0.4)]:
        s.draw(f'  <path d="{flame_path(cx, base, h, w, 3, int(cx*3+h))}" '
                f'fill="{c}" opacity="{o}" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="110" r="15" fill="url(#{g_shield})" opacity="0.6" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="110" r="5" fill="{C_WHITE_HOT}" opacity="0.8"/>')
    for x1, y1, x2, y2 in [(40,80,70,70),(70,70,100,65),(100,65,125,55),
                            (125,55,150,65),(150,65,180,70),(180,70,210,80)]:
        s.draw(f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                f'stroke="{C_YELLOW}" stroke-width="1" opacity="0.3" filter="url(#{glow})"/>')
    add_bottom_glow(s, 125, 170, 100, 8, color=C_DARK_RED, opacity=0.4, glow=soft)

CARD_RENDERERS["UnitedFront"] = render_unitedfront


def render_victoriasvow(s):
    """Victoria's flame vow."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    g_vow = rad_grad(s, [("0%",C_WHITE_HOT,0.9),("30%",C_YELLOW,0.7),
                          ("60%",C_ORANGE,0.4),("100%",C_DARK_RED,0)])
    g_ring = lin_grad(s, [("0%",C_YELLOW3),("50%",C_ORANGE),("100%",C_DEEP_ORANGE)])
    add_atmosphere(s, opacity=0.06)
    add_embers(s, 10, 5201, glow)
    s.draw(f'  <circle cx="125" cy="90" r="35" fill="url(#{g_vow})" filter="url(#{soft})"/>')
    s.draw(f'  <path d="{flame_path(125, 120, 70, 18, 3, 5210)}" '
            f'fill="{C_ORANGE}" opacity="0.6" filter="url(#{glow})"/>')
    s.draw(f'  <path d="{flame_path(125, 120, 50, 12, 2, 5211)}" '
            f'fill="{C_YELLOW}" opacity="0.5" filter="url(#{glow})"/>')
    s.draw(f'  <path d="{flame_path(125, 120, 30, 8, 2, 5212)}" '
            f'fill="{C_WHITE_HOT}" opacity="0.4" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="90" r="50" fill="none" stroke="url(#{g_ring})" '
            f'stroke-width="2" opacity="0.4" filter="url(#{glow})"/>')
    for i in range(6):
        a = math.radians(i * 60 - 90)
        x = 125 + 50 * math.cos(a)
        y = 90 + 50 * math.sin(a)
        s.draw(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="{C_YELLOW}" '
                f'opacity="0.6" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="80" r="12" fill="{C_WHITE_HOT}" opacity="0.6" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="80" r="4" fill="#ffffff" opacity="0.9"/>')
    for i in range(8):
        a = math.radians(i * 45)
        x1 = 125 + 40 * math.cos(a)
        y1 = 90 + 40 * math.sin(a)
        x2 = 125 + 60 * math.cos(a)
        y2 = 90 + 60 * math.sin(a)
        s.draw(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="{C_YELLOW}" stroke-width="1" opacity="0.3" filter="url(#{glow})"/>')
    add_spark_burst(s, 125, 80, 10, 5202, 30, glow=glow)

CARD_RENDERERS["VictoriasVow"] = render_victoriasvow


def render_wildfire(s):
    """Rampaging wildfire."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 6)
    add_bg(s)
    g_fire = lin_grad(s, [("0%",C_DARK_RED),("30%",C_DEEP_ORANGE),("60%",C_ORANGE),
                          ("100%",C_YELLOW)], "0%","100%","0%","0%")
    add_atmosphere(s, color=C_DARK_RED, opacity=0.08)
    add_embers(s, 20, 5301, glow)
    s.draw(f'  <path d="M 0 170 L 0 130 Q 30 100 50 120 Q 70 90 90 110 '
            f'Q 110 80 125 100 Q 140 80 160 110 Q 180 90 200 120 '
            f'Q 220 100 250 130 L 250 170 Z" fill="url(#{g_fire})" '
            f'opacity="0.6" filter="url(#{soft})"/>')
    for cx, base, h, w, c, o in [(20,130,50,12,C_ORANGE,0.5),(50,120,55,14,C_YELLOW,0.4),
                                  (80,110,60,16,C_ORANGE,0.5),(110,100,65,18,C_YELLOW,0.4),
                                  (125,100,70,20,C_WHITE_HOT,0.3),(140,100,65,18,C_YELLOW,0.4),
                                  (170,110,60,16,C_ORANGE,0.5),(200,120,55,14,C_DEEP_ORANGE,0.4),
                                  (230,130,50,12,C_ORANGE,0.5)]:
        s.draw(f'  <path d="{flame_path(cx, base, h, w, 5, int(cx*2+h))}" '
                f'fill="{c}" opacity="{o}" filter="url(#{glow})"/>')
    for cx, cy, r, o in [(40,80,15,0.2),(80,65,18,0.15),(125,55,20,0.2),
                         (170,65,18,0.15),(210,80,15,0.2)]:
        s.draw(f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="{C_DARK_BG}" '
                f'opacity="{o}" filter="url(#{soft})"/>')
    rng = random.Random(5302)
    for _ in range(15):
        x = rng.uniform(10, 240)
        y = rng.uniform(20, 120)
        r = rng.uniform(1, 2.5)
        s.draw(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" '
                f'fill="{rng.choice([C_ORANGE,C_YELLOW,C_DEEP_ORANGE])}" '
                f'opacity="0.5" filter="url(#{glow})"/>')
    add_bottom_glow(s, 125, 170, 100, 8, color=C_DARK_RED, opacity=0.4, glow=soft)

CARD_RENDERERS["Wildfire"] = render_wildfire


# ---- SPECIAL (2) ----

def render_spark(s):
    """Single bright spark."""
    glow = add_glow(s, 4)
    soft = add_soft_glow(s, 8)
    add_bg(s)
    g_spark = rad_grad(s, [("0%",C_WHITE_HOT,1),("20%",C_YELLOW,0.8),
                           ("50%",C_ORANGE,0.5),("100%",C_DARK_RED,0)])
    add_atmosphere(s, opacity=0.04)
    add_embers(s, 6, 5401, glow)
    s.draw(f'  <circle cx="125" cy="95" r="40" fill="url(#{g_spark})" opacity="0.5" filter="url(#{soft})"/>')
    s.draw(f'  <circle cx="125" cy="95" r="15" fill="{C_WHITE_HOT}" opacity="0.8" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="95" r="6" fill="#ffffff" opacity="0.95"/>')
    for i in range(8):
        a = math.radians(i * 45)
        x1 = 125 + 18 * math.cos(a)
        y1 = 95 + 18 * math.sin(a)
        x2 = 125 + 45 * math.cos(a)
        y2 = 95 + 45 * math.sin(a)
        s.draw(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="{C_YELLOW}" stroke-width="1.5" opacity="0.5" filter="url(#{glow})"/>')
    add_spark_burst(s, 125, 95, 12, 5402, 35, glow=glow)

CARD_RENDERERS["Spark"] = render_spark


def render_ashstorm(s):
    """Devastating ash storm."""
    glow = add_glow(s, 2.5)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    g_storm = rad_grad(s, [("0%",C_DEEP_ORANGE,0.3),("40%",C_DARK_RED,0.15),
                           ("100%",C_DARK_BG,0)])
    add_atmosphere(s, color=C_DARK_RED, opacity=0.08)
    add_ash_particles(s, 30, 5501)
    add_embers(s, 10, 5502, glow, colors=[C_DEEP_ORANGE, C_DARK_RED])
    s.draw(f'  <ellipse cx="125" cy="95" rx="85" ry="75" fill="url(#{g_storm})" '
            f'opacity="0.5" filter="url(#{soft})"/>')
    for start_a in [0, 90, 180, 270]:
        pts = []
        for t in range(0, 90, 5):
            a = math.radians(start_a + t * 4)
            r = 80 - t * 0.8
            if r < 5:
                break
            x = 125 + r * math.cos(a)
            y = 95 + r * math.sin(a)
            pts.append(f"{x:.1f} {y:.1f}")
        if len(pts) > 1:
            path = "M " + " L ".join(pts)
            s.draw(f'  <path d="{path}" fill="none" stroke="{ASH_COLORS[2]}" '
                    f'stroke-width="2" opacity="0.3" filter="url(#{soft})"/>')
    s.draw(f'  <circle cx="125" cy="95" r="12" fill="{C_DEEP_ORANGE}" opacity="0.5" '
            f'filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="95" r="4" fill="{C_WHITE_HOT}" opacity="0.7"/>')
    add_spark_burst(s, 125, 95, 8, 5503, 25, glow=glow)

CARD_RENDERERS["AshStorm"] = render_ashstorm


def render_eternalember(s):
    """Eternal undying ember."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 6)
    add_bg(s)
    g_ember = rad_grad(s, [("0%",C_WHITE_HOT,1),("20%",C_YELLOW,0.8),
                           ("50%",C_ORANGE,0.5),("80%",C_DEEP_ORANGE,0.2),
                           ("100%",C_DARK_RED,0)])
    g_ring = lin_grad(s, [("0%",C_YELLOW),("50%",C_ORANGE),("100%",C_DEEP_ORANGE)])
    add_atmosphere(s, opacity=0.05)
    add_embers(s, 12, 5601, glow)
    s.draw(f'  <circle cx="125" cy="95" r="60" fill="none" stroke="url(#{g_ring})" '
            f'stroke-width="1.5" opacity="0.25" filter="url(#{soft})"/>')
    s.draw(f'  <circle cx="125" cy="95" r="30" fill="url(#{g_ember})" filter="url(#{soft})"/>')
    s.draw(f'  <path d="{flame_path(125, 130, 55, 16, 3, 5610)}" '
            f'fill="{C_ORANGE}" opacity="0.6" filter="url(#{glow})"/>')
    s.draw(f'  <path d="{flame_path(125, 130, 40, 12, 2, 5611)}" '
            f'fill="{C_YELLOW}" opacity="0.5" filter="url(#{glow})"/>')
    s.draw(f'  <path d="{flame_path(125, 130, 25, 8, 2, 5612)}" '
            f'fill="{C_WHITE_HOT}" opacity="0.4" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="85" r="10" fill="{C_WHITE_HOT}" opacity="0.7" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="85" r="4" fill="#ffffff" opacity="0.95"/>')
    for i in range(6):
        a = math.radians(i * 60)
        x = 125 + 55 * math.cos(a)
        y = 95 + 55 * math.sin(a)
        s.draw(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="2" fill="{C_YELLOW}" '
                f'opacity="0.5" filter="url(#{glow})"/>')
    add_spark_burst(s, 125, 85, 10, 5602, 30, glow=glow)

CARD_RENDERERS["EternalEmber"] = render_eternalember


# =====================================================================
#  RELIC RENDERERS  (6 relics, 128 x 128)
# =====================================================================

RELIC_RENDERERS = {}

def render_scaleflamecharm(s):
    """Dragon scale amulet with fire."""
    glow = add_glow(s, 2)
    soft = add_soft_glow(s, 4)
    add_bg(s, cx="50%", cy="50%", r="65%")
    g_scale = lin_grad(s, [("0%",C_YELLOW3),("40%",C_ORANGE),("80%",C_DEEP_ORANGE),("100%",C_DARK_RED)])
    g_rim = rad_grad(s, [("0%",C_WHITE_HOT,0.6),("50%",C_YELLOW,0.3),("100%",C_DARK_RED,0)])
    add_atmosphere(s, opacity=0.06)
    add_embers(s, 8, 6101, glow)
    s.comment("Chain")
    s.draw(f'  <path d="M 64 12 Q 60 20 64 28 Q 60 36 64 44" stroke="#4a3020" '
            f'stroke-width="2" fill="none" opacity="0.6"/>')
    s.draw(f'  <path d="M 64 12 Q 68 20 64 28 Q 68 36 64 44" stroke="#3a2010" '
            f'stroke-width="1" fill="none" opacity="0.5"/>')
    s.comment("Amulet body")
    s.draw(f'  <path d="M 64 50 Q 35 55 30 75 Q 28 95 40 105 Q 55 115 64 110 '
            f'Q 73 115 88 105 Q 100 95 98 75 Q 93 55 64 50 Z" '
            f'fill="url(#{g_scale})" opacity="0.7" filter="url(#{soft})"/>')
    s.comment("Scale texture")
    for cx, cy, r in [(48,70,6),(64,65,7),(80,70,6),(52,88,5),(64,85,6),(76,88,5),(58,100,4),(70,100,4)]:
        s.draw(f'  <path d="M {cx-r} {cy} Q {cx} {cy-r*0.7} {cx+r} {cy} '
                f'Q {cx} {cy+r*0.7} {cx-r} {cy} Z" fill="{C_DEEP_ORANGE}" '
                f'opacity="0.4" filter="url(#{glow})"/>')
    s.comment("Center gem")
    s.draw(f'  <circle cx="64" cy="80" r="10" fill="url(#{g_rim})" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="64" cy="80" r="5" fill="{C_WHITE_HOT}" opacity="0.7"/>')
    s.draw(f'  <circle cx="62" cy="78" r="2" fill="#ffffff" opacity="0.9"/>')
    add_spark_burst(s, 64, 80, 6, 6102, 15, glow=glow)

RELIC_RENDERERS["ScaleFlameCharm"] = render_scaleflamecharm


def render_relicofthedragon(s):
    """Dragon-shaped relic with fire aura."""
    glow = add_glow(s, 2)
    soft = add_soft_glow(s, 4)
    add_bg(s, cx="50%", cy="50%", r="65%")
    g_aura = rad_grad(s, [("0%",C_ORANGE,0.4),("40%",C_DEEP_ORANGE,0.2),("100%",C_DARK_RED,0)])
    g_body = lin_grad(s, [("0%",C_YELLOW3),("40%",C_ORANGE),("80%",C_DEEP_ORANGE),("100%",C_DARK_RED)])
    add_atmosphere(s, opacity=0.06)
    add_embers(s, 8, 6201, glow)
    s.draw(f'  <ellipse cx="64" cy="64" rx="45" ry="42" fill="url(#{g_aura})" filter="url(#{soft})"/>')
    s.comment("Dragon silhouette")
    s.draw(f'  <path d="M 30 70 Q 25 50 35 40 Q 45 30 55 28 Q 65 25 70 30 '
            f'Q 80 25 90 30 Q 100 35 100 50 Q 105 55 100 65 Q 95 75 85 72 '
            f'Q 75 78 65 75 Q 55 78 45 75 Q 35 78 30 70 Z" '
            f'fill="url(#{g_body})" opacity="0.7" filter="url(#{soft})"/>')
    s.comment("Dragon eye")
    s.draw(f'  <circle cx="50" cy="48" r="3" fill="{C_YELLOW}" opacity="0.8" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="50" cy="48" r="1.5" fill="{C_WHITE_HOT}" opacity="0.9"/>')
    s.comment("Dragon horns")
    s.draw(f'  <path d="M 35 40 Q 30 30 25 25" stroke="{C_DEEP_ORANGE}" '
            f'stroke-width="2" fill="none" opacity="0.5"/>')
    s.draw(f'  <path d="M 90 30 Q 95 20 100 15" stroke="{C_DEEP_ORANGE}" '
            f'stroke-width="2" fill="none" opacity="0.5"/>')
    s.comment("Flame breath")
    s.draw(f'  <path d="{flame_path(100, 55, 25, 8, 3, 6210)}" '
            f'fill="{C_ORANGE}" opacity="0.5" filter="url(#{glow})"/>')
    s.draw(f'  <path d="{flame_path(100, 55, 18, 5, 2, 6211)}" '
            f'fill="{C_YELLOW}" opacity="0.4" filter="url(#{glow})"/>')
    add_spark_burst(s, 64, 50, 6, 6202, 15, glow=glow)

RELIC_RENDERERS["RelicOfTheDragon"] = render_relicofthedragon


def render_reedsspearhead(s):
    """Reed's spearhead relic."""
    glow = add_glow(s, 2)
    soft = add_soft_glow(s, 4)
    add_bg(s, cx="50%", cy="50%", r="65%")
    g_blade = lin_grad(s, [("0%",C_WHITE_HOT),("30%",C_YELLOW),("60%",C_ORANGE),("100%",C_DARK_RED)],
                      "0%","0%","0%","100%")
    g_aura = rad_grad(s, [("0%",C_ORANGE,0.3),("50%",C_DEEP_ORANGE,0.15),("100%",C_DARK_RED,0)])
    add_atmosphere(s, opacity=0.06)
    add_embers(s, 8, 6301, glow)
    s.draw(f'  <ellipse cx="64" cy="64" rx="40" ry="40" fill="url(#{g_aura})" filter="url(#{soft})"/>')
    s.comment("Spearhead")
    s.draw(f'  <path d="M 64 20 L 50 50 Q 48 70 52 85 L 64 100 L 76 85 Q 80 70 78 50 Z" '
            f'fill="url(#{g_blade})" filter="url(#{glow})"/>')
    s.comment("Spear midrib")
    s.draw(f'  <line x1="64" y1="24" x2="64" y2="96" stroke="{C_DEEP_ORANGE2}" '
            f'stroke-width="1" opacity="0.5"/>')
    s.comment("Spear highlight")
    s.draw(f'  <path d="M 64 20 L 57 50 Q 55 70 58 85 L 64 100 L 61 85 Q 58 70 60 50 Z" '
            f'fill="{C_WHITE_HOT}" opacity="0.3"/>')
    s.comment("Socket")
    s.draw(f'  <rect x="56" y="95" width="16" height="10" fill="#3a2010" rx="2"/>')
    s.draw(f'  <rect x="54" y="103" width="20" height="4" fill="#4a3020" rx="1"/>')
    s.comment("Glowing tip")
    s.draw(f'  <circle cx="64" cy="22" r="5" fill="{C_WHITE_HOT}" opacity="0.8" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="64" cy="22" r="2" fill="#ffffff" opacity="0.9"/>')
    add_spark_burst(s, 64, 22, 6, 6302, 12, glow=glow)

RELIC_RENDERERS["ReedsSpearhead"] = render_reedsspearhead


def render_heartofembers(s):
    """Heart of embers relic."""
    glow = add_glow(s, 2)
    soft = add_soft_glow(s, 5)
    add_bg(s, cx="50%", cy="50%", r="65%")
    g_heart = rad_grad(s, [("0%",C_WHITE_HOT),("20%",C_YELLOW),("50%",C_ORANGE),
                           ("80%",C_DEEP_ORANGE),("100%",C_DARK_RED)])
    g_aura = rad_grad(s, [("0%",C_ORANGE,0.3),("50%",C_DARK_RED,0.1),("100%",C_DARK_BG,0)])
    add_atmosphere(s, color=C_DARK_RED, opacity=0.06)
    add_embers(s, 10, 6401, glow)
    s.draw(f'  <ellipse cx="64" cy="64" rx="45" ry="42" fill="url(#{g_aura})" filter="url(#{soft})"/>')
    s.comment("Heart shape")
    s.draw(f'  <path d="M 64 100 C 40 80 25 60 25 45 C 25 32 38 25 48 32 '
            f'C 56 38 62 42 64 50 C 66 42 72 38 80 32 '
            f'C 90 25 103 32 103 45 C 103 60 88 80 64 100 Z" '
            f'fill="url(#{g_heart})" filter="url(#{glow})"/>')
    s.comment("Lava cracks")
    for pts in ["M 64 50 Q 58 65 55 80","M 64 50 Q 70 65 73 80","M 64 50 Q 64 70 64 90"]:
        s.draw(f'  <path d="{pts}" stroke="{C_WHITE_HOT}" stroke-width="1" '
                f'fill="none" opacity="0.4" filter="url(#{glow})"/>')
    s.comment("Glowing core")
    s.draw(f'  <circle cx="64" cy="55" r="8" fill="{C_WHITE_HOT}" opacity="0.7" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="64" cy="55" r="3" fill="#ffffff" opacity="0.95"/>')
    add_spark_burst(s, 64, 55, 8, 6402, 15, glow=glow)

RELIC_RENDERERS["HeartOfEmbers"] = render_heartofembers


def render_flameofvictoria(s):
    """Victoria's flame relic."""
    glow = add_glow(s, 2)
    soft = add_soft_glow(s, 5)
    add_bg(s, cx="50%", cy="50%", r="65%")
    g_flame = rad_grad(s, [("0%",C_WHITE_HOT,0.9),("30%",C_YELLOW,0.7),
                           ("60%",C_ORANGE,0.4),("100%",C_DARK_RED,0)])
    g_ring = lin_grad(s, [("0%",C_YELLOW),("50%",C_ORANGE),("100%",C_DEEP_ORANGE)])
    add_atmosphere(s, opacity=0.06)
    add_embers(s, 8, 6501, glow)
    s.comment("Flame body")
    s.draw(f'  <ellipse cx="64" cy="65" rx="22" ry="35" fill="url(#{g_flame})" filter="url(#{soft})"/>')
    s.draw(f'  <path d="{flame_path(64, 95, 50, 14, 3, 6510)}" '
            f'fill="{C_ORANGE}" opacity="0.6" filter="url(#{glow})"/>')
    s.draw(f'  <path d="{flame_path(64, 95, 35, 10, 2, 6511)}" '
            f'fill="{C_YELLOW}" opacity="0.5" filter="url(#{glow})"/>')
    s.draw(f'  <path d="{flame_path(64, 95, 20, 7, 2, 6512)}" '
            f'fill="{C_WHITE_HOT}" opacity="0.4" filter="url(#{glow})"/>')
    s.comment("Protective ring")
    s.draw(f'  <circle cx="64" cy="64" r="35" fill="none" stroke="url(#{g_ring})" '
            f'stroke-width="1.5" opacity="0.3" filter="url(#{soft})"/>')
    s.comment("Ring marks")
    for i in range(6):
        a = math.radians(i * 60)
        x = 64 + 35 * math.cos(a)
        y = 64 + 35 * math.sin(a)
        s.draw(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="1.5" fill="{C_YELLOW}" '
                f'opacity="0.6" filter="url(#{glow})"/>')
    s.comment("Core")
    s.draw(f'  <circle cx="64" cy="55" r="8" fill="{C_WHITE_HOT}" opacity="0.7" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="64" cy="55" r="3" fill="#ffffff" opacity="0.95"/>')
    add_spark_burst(s, 64, 55, 6, 6502, 12, glow=glow)

RELIC_RENDERERS["FlameOfVictoria"] = render_flameofvictoria


def render_ashencore(s):
    """Ashen core relic."""
    glow = add_glow(s, 2)
    soft = add_soft_glow(s, 4)
    add_bg(s, cx="50%", cy="50%", r="65%")
    g_core = rad_grad(s, [("0%",C_WHITE_HOT,0.8),("20%",C_YELLOW,0.6),
                          ("50%",C_ORANGE,0.3),("80%",C_DEEP_ORANGE,0.1),("100%",C_DARK_BG,0)])
    g_shell = lin_grad(s, [("0%","#4a3a30"),("50%","#3a2a20"),("100%","#1a120a")])
    add_atmosphere(s, color=C_DEEP_ORANGE, opacity=0.06)
    add_ash_particles(s, 12, 6601)
    add_embers(s, 6, 6602, glow)
    s.comment("Outer shell")
    s.draw(f'  <path d="M 64 20 Q 30 25 25 55 Q 22 85 40 100 Q 55 110 64 108 '
            f'Q 73 110 88 100 Q 106 85 103 55 Q 98 25 64 20 Z" '
            f'fill="url(#{g_shell})" opacity="0.7" filter="url(#{soft})"/>')
    s.comment("Cracks revealing core")
    for pts in ["M 40 40 Q 45 50 42 65","M 88 40 Q 83 50 86 65",
                "M 64 25 Q 60 40 62 60","M 35 70 Q 45 80 40 95",
                "M 93 70 Q 83 80 88 95"]:
        s.draw(f'  <path d="{pts}" stroke="{C_ORANGE}" stroke-width="1.5" '
                f'fill="none" opacity="0.5" filter="url(#{glow})"/>')
    s.comment("Glowing core")
    s.draw(f'  <circle cx="64" cy="64" r="18" fill="url(#{g_core})" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="64" cy="64" r="8" fill="{C_YELLOW}" opacity="0.6" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="64" cy="64" r="3" fill="{C_WHITE_HOT}" opacity="0.9"/>')
    add_spark_burst(s, 64, 64, 8, 6603, 15, glow=glow)

RELIC_RENDERERS["AshenCore"] = render_ashencore


# =====================================================================
#  POWER RENDERERS  (12 powers, 64 x 64)
# =====================================================================

POWER_RENDERERS = {}

def render_ash(s):
    """Ash power — grey ash cloud."""
    glow = add_glow(s, 1.5)
    soft = add_soft_glow(s, 3)
    add_bg(s, cx="50%", cy="50%", r="60%")
    g_ash = rad_grad(s, [("0%",C_DEEP_ORANGE,0.3),("40%",ASH_COLORS[2],0.5),("100%",ASH_COLORS[3],0.7)])
    add_atmosphere(s, color=C_DEEP_ORANGE, opacity=0.08)
    add_ash_particles(s, 12, 7101)
    add_embers(s, 4, 7102, glow)
    s.draw(f'  <ellipse cx="32" cy="32" rx="22" ry="20" fill="url(#{g_ash})" filter="url(#{soft})"/>')
    s.draw(f'  <ellipse cx="28" cy="28" rx="12" ry="10" fill="{ASH_COLORS[2]}" opacity="0.4"/>')
    s.draw(f'  <circle cx="32" cy="32" r="6" fill="{C_ORANGE}" opacity="0.4" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="32" cy="32" r="2" fill="{C_WHITE_HOT}" opacity="0.6"/>')

POWER_RENDERERS["Ash"] = render_ash


def render_ashrecoverypower(s):
    """Ash recovery power."""
    glow = add_glow(s, 1.5)
    soft = add_soft_glow(s, 3)
    add_bg(s, cx="50%", cy="50%", r="60%")
    g_form = rad_grad(s, [("0%",C_ORANGE,0.4),("50%",C_DEEP_ORANGE,0.2),("100%",C_DARK_BG,0)])
    add_atmosphere(s, opacity=0.06)
    add_ash_particles(s, 10, 7201)
    add_embers(s, 4, 7202, glow)
    s.draw(f'  <path d="M 20 48 Q 18 35 22 25 Q 28 18 32 15 Q 36 18 42 25 '
            f'Q 46 35 44 48 Z" fill="url(#{g_form})" opacity="0.5" filter="url(#{soft})"/>')
    s.draw(f'  <circle cx="32" cy="30" r="6" fill="{C_ORANGE}" opacity="0.5" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="32" cy="30" r="2" fill="{C_WHITE_HOT}" opacity="0.8"/>')
    rng = random.Random(7203)
    for _ in range(8):
        x = rng.uniform(8, 56)
        y = rng.uniform(8, 56)
        s.draw(f'  <line x1="{x:.1f}" y1="{y:.1f}" x2="{32+rng.uniform(-5,5):.1f}" '
                f'y2="{30+rng.uniform(-5,5):.1f}" stroke="{ASH_COLORS[2]}" '
                f'stroke-width="0.5" opacity="0.3"/>')

POWER_RENDERERS["AshRecoveryPower"] = render_ashrecoverypower


def render_calamitybreath(s):
    """Calamity breath power."""
    glow = add_glow(s, 1.5)
    soft = add_soft_glow(s, 3)
    add_bg(s, cx="50%", cy="50%", r="60%")
    g_breath = lin_grad(s, [("0%",C_WHITE_HOT),("30%",C_YELLOW),("60%",C_ORANGE),("100%",C_DARK_RED)],
                       "0%","0%","100%","0%")
    add_atmosphere(s, color=C_DARK_RED, opacity=0.08)
    add_embers(s, 6, 7301, glow)
    s.draw(f'  <path d="M 8 32 Q 20 20 40 24 Q 52 28 56 32 Q 52 36 40 40 '
            f'Q 20 44 8 32 Z" fill="url(#{g_breath})" opacity="0.6" filter="url(#{soft})"/>')
    s.draw(f'  <path d="M 8 32 Q 20 28 40 30 Q 52 32 56 32 Q 52 32 40 34 '
            f'Q 20 36 8 32 Z" fill="{C_WHITE_HOT}" opacity="0.4"/>')
    s.draw(f'  <circle cx="56" cy="32" r="4" fill="{C_WHITE_HOT}" opacity="0.7" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="56" cy="32" r="1.5" fill="#ffffff" opacity="0.9"/>')
    add_spark_burst(s, 56, 32, 6, 7302, 10, glow=glow)

POWER_RENDERERS["CalamityBreath"] = render_calamitybreath


def render_dragonslegacypower(s):
    """Dragon legacy power."""
    glow = add_glow(s, 1.5)
    soft = add_soft_glow(s, 3)
    add_bg(s, cx="50%", cy="50%", r="60%")
    g_aura = rad_grad(s, [("0%",C_YELLOW,0.3),("50%",C_ORANGE,0.15),("100%",C_DARK_RED,0)])
    add_atmosphere(s, opacity=0.06)
    add_embers(s, 6, 7401, glow)
    s.draw(f'  <ellipse cx="32" cy="32" rx="25" ry="22" fill="url(#{g_aura})" filter="url(#{soft})"/>')
    s.draw(f'  <path d="M 16 40 Q 14 28 20 22 Q 26 18 32 16 Q 38 18 44 22 '
            f'Q 50 28 48 40 Q 40 42 32 40 Q 24 42 16 40 Z" '
            f'fill="{C_DARK_BG2}" opacity="0.5" filter="url(#{soft})"/>')
    s.draw(f'  <circle cx="22" cy="28" r="2" fill="{C_YELLOW}" opacity="0.8" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="22" cy="28" r="1" fill="{C_WHITE_HOT}" opacity="0.9"/>')
    for cx, cy in [(24,36,),(32,34),(40,36)]:
        s.draw(f'  <path d="M {cx-3} {cy} Q {cx} {cy-2} {cx+3} {cy} Q {cx} {cy+2} {cx-3} {cy} Z" '
                f'fill="{C_ORANGE}" opacity="0.4" filter="url(#{glow})"/>')

POWER_RENDERERS["DragonsLegacyPower"] = render_dragonslegacypower


def render_emberspread(s):
    """Ember spread power."""
    glow = add_glow(s, 1.5)
    soft = add_soft_glow(s, 3)
    add_bg(s, cx="50%", cy="50%", r="60%")
    add_atmosphere(s, opacity=0.06)
    add_embers(s, 8, 7501, glow)
    s.draw(f'  <circle cx="32" cy="32" r="15" fill="{C_ORANGE}" opacity="0.3" filter="url(#{soft})"/>')
    for cx, cy, r, c, o in [(20,20,3,C_YELLOW,0.6),(44,20,3,C_ORANGE,0.5),
                             (20,44,3,C_DEEP_ORANGE,0.4),(44,44,3,C_YELLOW,0.5),
                             (32,18,2.5,C_ORANGE,0.5),(32,46,2.5,C_ORANGE,0.5),
                             (18,32,2.5,C_YELLOW,0.4),(46,32,2.5,C_YELLOW,0.4)]:
        s.draw(f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}" opacity="{o}" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="32" cy="32" r="4" fill="{C_WHITE_HOT}" opacity="0.7" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="32" cy="32" r="1.5" fill="#ffffff" opacity="0.9"/>')

POWER_RENDERERS["EmberSpread"] = render_emberspread


def render_eternalemberpower(s):
    """Eternal ember power."""
    glow = add_glow(s, 1.5)
    soft = add_soft_glow(s, 4)
    add_bg(s, cx="50%", cy="50%", r="60%")
    g_ember = rad_grad(s, [("0%",C_WHITE_HOT,0.8),("30%",C_YELLOW,0.6),
                           ("60%",C_ORANGE,0.3),("100%",C_DARK_RED,0)])
    g_ring = lin_grad(s, [("0%",C_YELLOW),("50%",C_ORANGE),("100%",C_DEEP_ORANGE)])
    add_atmosphere(s, opacity=0.05)
    add_embers(s, 6, 7601, glow)
    s.draw(f'  <circle cx="32" cy="32" r="22" fill="none" stroke="url(#{g_ring})" '
            f'stroke-width="1" opacity="0.2" filter="url(#{soft})"/>')
    s.draw(f'  <circle cx="32" cy="32" r="10" fill="url(#{g_ember})" filter="url(#{soft})"/>')
    s.draw(f'  <circle cx="32" cy="32" r="4" fill="{C_WHITE_HOT}" opacity="0.7" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="32" cy="32" r="1.5" fill="#ffffff" opacity="0.9"/>')
    for i in range(4):
        a = math.radians(i * 90)
        x = 32 + 20 * math.cos(a)
        y = 32 + 20 * math.sin(a)
        s.draw(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="1.5" fill="{C_YELLOW}" '
                f'opacity="0.5" filter="url(#{glow})"/>')

POWER_RENDERERS["EternalEmberPower"] = render_eternalemberpower


def render_everflamepower(s):
    """Everflame power — eternal flame with protective ring."""
    glow = add_glow(s, 1.5)
    soft = add_soft_glow(s, 3)
    add_bg(s, cx="50%", cy="50%", r="60%")
    g_flame = rad_grad(s, [("0%",C_WHITE_HOT,0.9),("30%",C_YELLOW,0.6),
                           ("60%",C_ORANGE,0.3),("100%",C_DARK_RED,0)])
    g_ring = lin_grad(s, [("0%",C_YELLOW),("50%",C_ORANGE),("100%",C_DEEP_ORANGE)])
    add_atmosphere(s, opacity=0.06)
    add_embers(s, 6, 7701, glow)
    s.draw(f'  <circle cx="32" cy="32" r="24" fill="none" stroke="url(#{g_ring})" '
            f'stroke-width="1" opacity="0.25" filter="url(#{soft})"/>')
    s.draw(f'  <ellipse cx="32" cy="35" rx="10" ry="18" fill="url(#{g_flame})" filter="url(#{soft})"/>')
    s.draw(f'  <path d="{flame_path(32, 45, 25, 7, 2, 7710)}" '
            f'fill="{C_ORANGE}" opacity="0.5" filter="url(#{glow})"/>')
    s.draw(f'  <path d="{flame_path(32, 45, 15, 5, 1, 7711)}" '
            f'fill="{C_YELLOW}" opacity="0.4" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="32" cy="28" r="4" fill="{C_WHITE_HOT}" opacity="0.7" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="32" cy="28" r="1.5" fill="#ffffff" opacity="0.9"/>')

POWER_RENDERERS["EverflamePower"] = render_everflamepower


def render_flameshadowform(s):
    """Flame shadow form power."""
    glow = add_glow(s, 1.5)
    soft = add_soft_glow(s, 3)
    add_bg(s, c0="#1a0a08", c1="#0d0504", c2="#050202")
    g_shadow = rad_grad(s, [("0%",C_DEEP_ORANGE,0.3),("40%",C_DARK_RED,0.15),("100%",C_DARK_BG2,0)])
    g_flame = rad_grad(s, [("0%",C_WHITE_HOT,0.7),("30%",C_YELLOW,0.5),("100%",C_DARK_RED,0)])
    add_atmosphere(s, color=C_DARK_RED, opacity=0.08)
    add_embers(s, 5, 7801, glow, colors=[C_DEEP_ORANGE, C_DARK_RED])
    s.draw(f'  <ellipse cx="32" cy="32" rx="22" ry="22" fill="url(#{g_shadow})" filter="url(#{soft})"/>')
    s.draw(f'  <path d="M 28 48 Q 27 35 29 20 Q 31 12 32 10 Q 33 12 35 20 '
            f'Q 37 35 36 48 Z" fill="url(#{g_flame})" opacity="0.5" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="32" cy="14" r="5" fill="{C_ORANGE}" opacity="0.5" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="32" cy="14" r="2" fill="{C_WHITE_HOT}" opacity="0.8"/>')
    for pts in ["M 28 30 Q 18 28 12 30","M 36 30 Q 46 28 52 30"]:
        s.draw(f'  <path d="{pts}" stroke="{C_DARK_RED}" stroke-width="1.5" '
                f'fill="none" opacity="0.3"/>')

POWER_RENDERERS["FlameShadowForm"] = render_flameshadowform


def render_scorch(s):
    """Scorch power — flame shape."""
    glow = add_glow(s, 1.5)
    soft = add_soft_glow(s, 3)
    add_bg(s, cx="50%", cy="50%", r="60%")
    g_flame = rad_grad(s, [("0%",C_WHITE_HOT,0.9),("30%",C_YELLOW,0.7),
                           ("60%",C_ORANGE,0.4),("100%",C_DARK_RED,0)])
    add_atmosphere(s, opacity=0.06)
    add_embers(s, 5, 7901, glow)
    s.draw(f'  <path d="{flame_path(32, 50, 35, 12, 2, 7910)}" '
            f'fill="url(#{g_flame})" filter="url(#{soft})"/>')
    s.draw(f'  <path d="{flame_path(32, 50, 22, 8, 1, 7911)}" '
            f'fill="{C_ORANGE}" opacity="0.5" filter="url(#{glow})"/>')
    s.draw(f'  <path d="{flame_path(32, 50, 12, 5, 1, 7912)}" '
            f'fill="{C_YELLOW}" opacity="0.4" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="32" cy="25" r="3" fill="{C_WHITE_HOT}" opacity="0.7" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="32" cy="25" r="1" fill="#ffffff" opacity="0.9"/>')

POWER_RENDERERS["Scorch"] = render_scorch


def render_scorchcounter(s):
    """Scorch counter power."""
    glow = add_glow(s, 1.5)
    soft = add_soft_glow(s, 3)
    add_bg(s, cx="50%", cy="50%", r="60%")
    g_count = rad_grad(s, [("0%",C_WHITE_HOT,0.8),("30%",C_ORANGE,0.5),("100%",C_DARK_RED,0)])
    add_atmosphere(s, opacity=0.06)
    add_embers(s, 4, 8001, glow)
    s.draw(f'  <circle cx="32" cy="32" r="18" fill="url(#{g_count})" opacity="0.4" filter="url(#{soft})"/>')
    s.draw(f'  <circle cx="32" cy="32" r="12" fill="none" stroke="{C_ORANGE}" '
            f'stroke-width="1.5" opacity="0.5" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="32" cy="32" r="6" fill="{C_ORANGE}" opacity="0.5" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="32" cy="32" r="2.5" fill="{C_WHITE_HOT}" opacity="0.8"/>')
    for i in range(4):
        a = math.radians(i * 90 + 45)
        x = 32 + 14 * math.cos(a)
        y = 32 + 14 * math.sin(a)
        s.draw(f'  <line x1="{32:.1f}" y1="{32:.1f}" x2="{x:.1f}" y2="{y:.1f}" '
                f'stroke="{C_YELLOW}" stroke-width="1" opacity="0.4"/>')

POWER_RENDERERS["ScorchCounter"] = render_scorchcounter


def render_scorchimmunity(s):
    """Scorch immunity power."""
    glow = add_glow(s, 1.5)
    soft = add_soft_glow(s, 3)
    add_bg(s, cx="50%", cy="50%", r="60%")
    g_shield = rad_grad(s, [("0%",C_WHITE_HOT,0.6),("40%",C_YELLOW,0.3),("100%",C_DARK_RED,0)])
    g_ring = lin_grad(s, [("0%",C_YELLOW),("50%",C_ORANGE),("100%",C_DEEP_ORANGE)])
    add_atmosphere(s, opacity=0.06)
    add_embers(s, 4, 8101, glow)
    s.draw(f'  <circle cx="32" cy="32" r="20" fill="none" stroke="url(#{g_ring})" '
            f'stroke-width="1.5" opacity="0.3" filter="url(#{soft})"/>')
    s.draw(f'  <path d="M 32 16 L 42 22 L 42 32 Q 42 40 32 46 Q 22 40 22 32 L 22 22 Z" '
            f'fill="url(#{g_shield})" opacity="0.5" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 32 16 L 42 22 L 42 32 Q 42 40 32 46 Q 22 40 22 32 L 22 22 Z" '
            f'fill="none" stroke="{C_YELLOW}" stroke-width="0.8" opacity="0.4"/>')
    s.draw(f'  <circle cx="32" cy="30" r="4" fill="{C_ORANGE}" opacity="0.5" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="32" cy="30" r="1.5" fill="{C_WHITE_HOT}" opacity="0.8"/>')

POWER_RENDERERS["ScorchImmunity"] = render_scorchimmunity


def render_unitedfrontpower(s):
    """United front power."""
    glow = add_glow(s, 1.5)
    soft = add_soft_glow(s, 3)
    add_bg(s, cx="50%", cy="50%", r="60%")
    g_wall = lin_grad(s, [("0%",C_DARK_RED),("50%",C_ORANGE),("100%",C_YELLOW3)],
                     "0%","100%","0%","0%")
    add_atmosphere(s, opacity=0.06)
    add_embers(s, 6, 8201, glow)
    s.draw(f'  <path d="M 8 50 L 8 35 Q 14 25 20 30 Q 26 20 32 25 Q 38 20 44 30 '
            f'Q 50 25 56 35 L 56 50 Z" fill="url(#{g_wall})" opacity="0.5" '
            f'filter="url(#{soft})"/>')
    for cx, base, h, w, c, o in [(14,35,12,4,C_ORANGE,0.4),(24,30,15,5,C_YELLOW,0.3),
                                  (32,25,18,6,C_ORANGE,0.4),(40,30,15,5,C_YELLOW,0.3),
                                  (50,35,12,4,C_DEEP_ORANGE,0.3)]:
        s.draw(f'  <path d="{flame_path(cx, base, h, w, 1, int(cx+h))}" '
                f'fill="{c}" opacity="{o}" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="32" cy="35" r="4" fill="{C_WHITE_HOT}" opacity="0.6" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="32" cy="35" r="1.5" fill="#ffffff" opacity="0.9"/>')

POWER_RENDERERS["UnitedFrontPower"] = render_unitedfrontpower


# =====================================================================
#  POTION RENDERERS  (1 potion, 128 x 128)
# =====================================================================

POTION_RENDERERS = {}

def render_dragonflamepotion(s):
    """Dragon flame potion — potion bottle with fire liquid and swirling dragon flame."""
    glow = add_glow(s, 2)
    soft = add_soft_glow(s, 4)
    add_bg(s, cx="50%", cy="55%", r="65%")
    g_glass = lin_grad(s, [("0%","#5a4838",0.6),("40%","#3a2c20",0.5),
                           ("100%","#1a1410",0.7)], "0%","0%","0%","100%")
    g_liquid = lin_grad(s, [("0%",C_YELLOW),("30%",C_ORANGE),("70%",C_DEEP_ORANGE),
                            ("100%",C_DEEP_ORANGE2)], "0%","0%","0%","100%")
    g_flame = lin_grad(s, [("0%",C_WHITE_HOT),("20%",C_YELLOW),("50%",C_ORANGE),
                           ("80%",C_DEEP_ORANGE2),("100%",C_DARK_RED,0)],
                       "0%","100%","0%","0%")
    g_aura = rad_grad(s, [("0%",C_ORANGE,0.4),("50%",C_DEEP_ORANGE,0.15),
                          ("100%",C_DARK_RED,0)], cx="50%", cy="55%", r="50%")
    g_ember = rad_grad(s, [("0%",C_WHITE_HOT,0.9),("40%",C_YELLOW3,0.7),
                           ("80%",C_DEEP_ORANGE,0.4),("100%",C_DARK_RED,0)])
    add_atmosphere(s, color=C_DEEP_ORANGE, opacity=0.06)
    add_embers(s, 12, 9101, glow)
    s.comment("Aura")
    s.draw(f'  <ellipse cx="64" cy="68" rx="48" ry="56" fill="url(#{g_aura})" filter="url(#{soft})"/>')
    s.comment("Cork / stopper")
    s.draw(f'  <rect x="54" y="16" width="20" height="12" fill="#3a2c20" '
            f'stroke="#1a0d08" stroke-width="0.5" rx="2"/>')
    s.draw(f'  <rect x="56" y="18" width="16" height="4" fill="#5a4838" '
            f'opacity="0.5" rx="2"/>')
    s.comment("Neck")
    s.draw(f'  <rect x="58" y="26" width="12" height="12" fill="url(#{g_glass})" '
            f'stroke="#1a0d08" stroke-width="0.5"/>')
    s.draw(f'  <rect x="54" y="26" width="20" height="4" fill="#3a2c20" rx="2"/>')
    s.comment("Bottle body (flask shape)")
    s.draw(f'  <path d="M 40,38 Q 32,44 32,60 L 32,96 Q 32,112 48,114 '
            f'L 80,114 Q 96,112 96,96 L 96,60 Q 96,44 88,38 Z" '
            f'fill="url(#{g_glass})" stroke="#1a0d08" stroke-width="1"/>')
    s.comment("Glass highlight")
    s.draw(f'  <path d="M 40,44 Q 36,52 36,64 L 36,92 Q 36,100 40,104" '
            f'fill="none" stroke="#7a6a5a" stroke-width="2" opacity="0.3"/>')
    s.comment("Liquid inside (orange flame potion)")
    s.draw(f'  <path d="M 36,60 Q 34,70 36,84 L 36,94 Q 36,108 48,110 '
            f'L 80,110 Q 92,108 92,94 L 92,84 Q 94,70 92,60 Z" '
            f'fill="url(#{g_liquid})" opacity="0.9"/>')
    s.comment("Liquid surface (meniscus)")
    s.draw(f'  <ellipse cx="64" cy="62" rx="26" ry="5" fill="{C_YELLOW}" opacity="0.6"/>')
    s.draw(f'  <ellipse cx="64" cy="60" rx="20" ry="3" fill="{C_WHITE_HOT}" opacity="0.3"/>')
    s.comment("Dragon flame inside liquid (swirling)")
    s.draw(f'  <path d="M 64,100 C 56,90 68,84 60,76 C 56,70 66,66 62,60" '
            f'fill="none" stroke="{C_YELLOW}" stroke-width="2" opacity="0.7" '
            f'filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 56,96 C 52,86 60,80 54,72 C 50,66 58,62 54,56" '
            f'fill="none" stroke="{C_ORANGE}" stroke-width="1.5" opacity="0.5"/>')
    s.draw(f'  <path d="M 72,96 C 76,86 68,80 74,72 C 78,66 70,62 74,56" '
            f'fill="none" stroke="#ffaa00" stroke-width="1.5" opacity="0.5"/>')
    s.comment("Flame bursting from bottle neck")
    s.draw(f'  <path d="M 58,28 Q 54,16 60,8 Q 62,16 60,26 Z" '
            f'fill="url(#{g_flame})" opacity="0.8" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 64,28 Q 60,12 66,4 Q 68,12 66,26 Z" '
            f'fill="url(#{g_flame})" opacity="0.85" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 70,28 Q 74,16 68,8 Q 66,16 68,26 Z" '
            f'fill="url(#{g_flame})" opacity="0.75" filter="url(#{glow})"/>')
    s.comment("Bright flame core from neck")
    s.draw(f'  <ellipse cx="64" cy="28" rx="8" ry="6" fill="url(#{g_ember})" '
            f'opacity="0.8" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="64" cy="26" r="3" fill="{C_WHITE_HOT}" opacity="0.9"/>')
    s.comment("Embers inside liquid")
    for cx, cy, r, c, o in [(56,90,2,C_YELLOW,0.6),(72,86,1.6,"#ffaa00",0.55),
                             (48,80,1.2,C_ORANGE,0.4),(80,76,1.2,C_ORANGE,0.4),
                             (64,84,2,C_YELLOW,0.5)]:
        s.draw(f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}" opacity="{o}" '
                f'filter="url(#{glow})"/>')
    add_spark_burst(s, 64, 26, 8, 9102, 18, glow=glow)
    s.comment("Floating embers escaping")
    for cx, cy, r, c, o in [(48,12,1.6,C_ORANGE,0.4),(80,10,1.6,"#ffaa00",0.4),
                             (56,4,1.2,C_YELLOW,0.35),(72,6,1.2,C_ORANGE,0.3),
                             (44,20,1,C_DEEP_ORANGE,0.3),(84,18,1,C_YELLOW,0.3)]:
        s.draw(f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}" opacity="{o}" '
                f'filter="url(#{glow})"/>')
    add_bottom_glow(s, 64, 114, 24, 6, color=C_DARK_RED, opacity=0.3, glow=soft)

POTION_RENDERERS["DragonFlamePotion"] = render_dragonflamepotion


# =====================================================================
#  Output directories (relative to this script's location)
# =====================================================================

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARDS_DIR   = os.path.join(_BASE_DIR, "Reed", "Reed", "images", "cards")
RELICS_DIR  = os.path.join(_BASE_DIR, "Reed", "Reed", "images", "relics")
POWERS_DIR  = os.path.join(_BASE_DIR, "Reed", "Reed", "images", "powers")
POTIONS_DIR = os.path.join(_BASE_DIR, "Reed", "Reed", "images", "potions")


# =====================================================================
#  Generate functions
# =====================================================================

def _write_svg(path, svg_text, force):
    """Write SVG text to *path*, honouring the --force flag."""
    if os.path.exists(path) and not force:
        print(f"  skip  {os.path.relpath(path, _BASE_DIR)} (exists)")
        return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(svg_text)
    print(f"  wrote {os.path.relpath(path, _BASE_DIR)}")
    return True


def generate_card(name, theme_desc=""):
    """Generate a single card SVG (250x190). Returns True on write."""
    renderer = CARD_RENDERERS.get(name)
    if renderer is None:
        print(f"  !! no renderer for card '{name}'")
        return False
    s = SVG(250, 190)
    renderer(s)
    path = os.path.join(CARDS_DIR, f"{name}.svg")
    return _write_svg(path, s.build(), _FORCE)


def generate_relic(name, theme_desc=""):
    """Generate a single relic SVG (128x128). Returns True on write."""
    renderer = RELIC_RENDERERS.get(name)
    if renderer is None:
        print(f"  !! no renderer for relic '{name}'")
        return False
    s = SVG(128, 128)
    renderer(s)
    path = os.path.join(RELICS_DIR, f"{name}.svg")
    return _write_svg(path, s.build(), _FORCE)


def generate_power(name, theme_desc=""):
    """Generate a single power SVG (64x64). Returns True on write."""
    renderer = POWER_RENDERERS.get(name)
    if renderer is None:
        print(f"  !! no renderer for power '{name}'")
        return False
    s = SVG(64, 64)
    renderer(s)
    path = os.path.join(POWERS_DIR, f"{name}.svg")
    return _write_svg(path, s.build(), _FORCE)


def generate_potion(name, theme_desc=""):
    """Generate a single potion SVG (128x128). Returns True on write."""
    renderer = POTION_RENDERERS.get(name)
    if renderer is None:
        print(f"  !! no renderer for potion '{name}'")
        return False
    s = SVG(128, 128)
    renderer(s)
    path = os.path.join(POTIONS_DIR, f"{name}.svg")
    return _write_svg(path, s.build(), _FORCE)


# =====================================================================
#  Full card / relic / power / potion name lists with themes
# =====================================================================

CARD_THEMES = {
    # ---- BASIC (2) ----
    "Strike":              "Fire beam attack with trailing embers",
    "Defend":              "Circular flame barrier",
    # ---- COMMON (17) ----
    "SpearFlame":          "Vertical spear with flame-engulfed blade",
    "SwiftThrust":         "Rapid spear thrust with motion blur",
    "AshenBulwark":        "Reinforced ash wall shield",
    "DragonbloodBoiling":  "Boiling dragon-blood potion burst",
    "EmberIgnition":       "Igniting a cluster of embers",
    "CinderSpear":         "Spear wreathed in cinder flames",
    "CinderSpearCombo":    "Two-hit cinder spear combo",
    "EmberShield":         "Shield of swirling embers",
    "EmberConduit":        "Channeling embers through conduit",
    "EmberEye":            "Giant ember eye staring",
    "AshenArmor":          "Plate armor of hardened ash",
    "FlameScale":          "Dragon-scale flame barrier",
    "ScorchBastion":       "Fortress of scorched earth",
    "ScorchingCharge":     "Flaming charge forward",
    "SpontaneousCombustion": "Sudden explosive ignition",
    "CinderShield":        "Shield of compacted cinders",
    "AshGathering":        "Swirling gathering of ash",
    # ---- UNCOMMON (16) ----
    "AshBath":             "Cleansing bath of ash",
    "AshIgnition":         "Igniting ash into flame",
    "AshResonance":        "Resonating ash shockwave",
    "BurnAway":            "Burning away weakness",
    "BurnOut":             "Flare burning out to embers",
    "Cremation":           "Funeral pyre cremation",
    "DragonBreath":        "Dragon's breath fire cone",
    "EmberBlade":          "Blade of pure ember",
    "Embers":              "Scattered ember swarm",
    "FlameBurst":          "Explosive flame burst",
    "FlameInheritance":    "Inheriting ancestral flame",
    "FlameShadowArt":      "Shadow-flame martial art",
    "FlameWhirl":          "Whirling vortex of flame",
    "PassingTheTorch":     "Passing a flaming torch",
    "ReedsSpear":          "Reed's signature spear",
    "ScorchAwakening":     "Flames to raw energy",
    # ---- RARE (18) ----
    "ScorchBurst":         "Massive scorch detonation",
    "ScorchedEarth":       "Scorched-earth landscape",
    "ScorchedEarthProtocol":"Systematic scorched-earth protocol",
    "ScorchingHeart":      "Burning heart of the dragon",
    "SearingPierce":       "Searing spear pierce",
    "ShadowflameProwl":    "Prowling in shadow-flame",
    "WitheredRevival":     "Revival of withered reeds",
    "AshRecovery":         "Recovery from ash",
    "EmberPact":           "Pact of eternal embers",
    "ScorchingBond":       "Bond forged in scorch-fire",
    "BreathOfCalamity":    "Calamity dragon's breath",
    "DragonsLegacy":       "Legacy of the dragon bloodline",
    "Everflame":           "Eternal undying flame",
    "FlameShadowReed":     "Reed transformed by shadow-flame",
    "InfernoStorm":        "Storm of inferno fire",
    "UnitedFront":         "United wall of flame warriors",
    "VictoriasVow":        "Victoria's vow of fire",
    "Wildfire":            "Spreading wildfire",
    # ---- SPECIAL (3) ----
    "Spark":               "Single spark of ignition",
    "AshStorm":            "Violent ash storm",
    "EternalEmber":        "Eternal glowing ember",
    # ---- NEW BATCH (8) ----
    "AshEmbrace":          "Ash arms embracing a protected core",
    "Backdraft":           "Hollow reversed blast ring",
    "DragonsMajesty":      "Draconic crest with pressure rings",
    "EmberAfterglow":      "Fading embers drifting upward",
    "EmberScales":         "Overlapping glowing scale shield",
    "MartyrFlame":         "Self-consuming offering flame",
    "ResidualWarmth":      "Warm glow in cold ash bed",
    "ScorchDetonation":    "Shattering scorch detonation",
}

RELIC_THEMES = {
    "ScaleFlameCharm":    "Dragon scale amulet with flame core",
    "RelicOfTheDragon":   "Ancient dragon relic",
    "ReedsSpearhead":     "Reed's spearhead tip",
    "HeartOfEmbers":      "Heart of living embers",
    "FlameOfVictoria":    "Victoria's eternal flame",
    "AshenCore":          "Ashen core with glowing heart",
}

POWER_THEMES = {
    "Ash":                "Grey ash cloud",
    "AshRecoveryPower":   "Ash recovery",
    "CalamityBreath":     "Calamity breath",
    "DragonsLegacyPower": "Dragon legacy",
    "EmberSpread":        "Ember spread",
    "EternalEmberPower":  "Eternal ember",
    "EverflamePower":     "Everflame eternal flame",
    "FlameShadowForm":    "Flame shadow form",
    "Scorch":             "Scorch flame",
    "ScorchCounter":      "Scorch counter",
    "ScorchImmunity":     "Scorch immunity",
    "UnitedFrontPower":   "United front",
}

POTION_THEMES = {
    "DragonFlamePotion":  "Potion of dragon flame",
}


# =====================================================================
#  Main entry point
# =====================================================================

_FORCE = False


def main():
    global _FORCE
    parser = argparse.ArgumentParser(
        description="Generate high-quality SVG art for the Reed character mod.")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite existing SVG files (default: skip existing).")
    args = parser.parse_args()
    _FORCE = args.force

    print("=== Reed SVG generator ===")
    print(f"  force={_FORCE}")
    print()

    total = 0
    written = 0

    # ---- cards ----
    print(f"[cards] {len(CARD_THEMES)} items -> {os.path.relpath(CARDS_DIR, _BASE_DIR)}")
    for name, theme in CARD_THEMES.items():
        total += 1
        if generate_card(name, theme):
            written += 1

    # ---- relics ----
    print(f"[relics] {len(RELIC_THEMES)} items -> {os.path.relpath(RELICS_DIR, _BASE_DIR)}")
    for name, theme in RELIC_THEMES.items():
        total += 1
        if generate_relic(name, theme):
            written += 1

    # ---- powers ----
    print(f"[powers] {len(POWER_THEMES)} items -> {os.path.relpath(POWERS_DIR, _BASE_DIR)}")
    for name, theme in POWER_THEMES.items():
        total += 1
        if generate_power(name, theme):
            written += 1

    # ---- potions ----
    print(f"[potions] {len(POTION_THEMES)} items -> {os.path.relpath(POTIONS_DIR, _BASE_DIR)}")
    for name, theme in POTION_THEMES.items():
        total += 1
        if generate_potion(name, theme):
            written += 1

    print()
    print(f"=== done: {written}/{total} files written ===")


# =====================================================================
#  New cards (added batch): AshEmbrace / Backdraft / DragonsMajesty /
#  EmberAfterglow / EmberScales / MartyrFlame / ResidualWarmth /
#  ScorchDetonation
# =====================================================================

def render_ashembrace(s):
    """Ash arms embracing a protected core."""
    glow = add_glow(s, 2.5)
    soft = add_soft_glow(s, 4)
    add_bg(s)
    g_core = rad_grad(s, [("0%",C_WHITE_HOT,0.9),("30%",C_ORANGE,0.6),
                          ("70%",C_DEEP_ORANGE,0.25),("100%",C_DARK_RED,0)])
    add_atmosphere(s, opacity=0.05)
    add_ash_particles(s, 16, 3001)
    add_embers(s, 6, 3002, glow, colors=[C_ORANGE, C_YELLOW3])
    s.comment("Two ash arms curving around the core")
    for side, flip in [(-1, 1), (1, -1)]:
        cx0 = 125 + side * 20
        s.draw(f'  <path d="M {cx0 + side*40},170 '
               f'C {cx0 + side*55},130 {cx0 + side*45},80 {cx0 + side*8},62 '
               f'C {cx0 + side*20},85 {cx0 + side*18},125 {cx0 + flip*6},150 Z" '
               f'fill="{ASH_COLORS[2]}" opacity="0.55" filter="url(#{soft})"/>')
        s.draw(f'  <path d="M {cx0 + side*44},166 '
               f'C {cx0 + side*58},128 {cx0 + side*48},82 {cx0 + side*10},66" '
               f'fill="none" stroke="{C_ORANGE}" stroke-width="1.5" '
               f'opacity="0.5" filter="url(#{glow})"/>')
    s.comment("Glowing core held within")
    s.draw(f'  <circle cx="125" cy="100" r="26" fill="url(#{g_core})" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="125" cy="100" r="8" fill="{C_WHITE_HOT}" opacity="0.85"/>')
    add_spark_burst(s, 125, 100, 8, 3003, 22, glow=glow)
    s.comment("Embrace aura ring")
    s.draw(f'  <ellipse cx="125" cy="105" rx="58" ry="42" fill="none" '
           f'stroke="{ASH_COLORS[1]}" stroke-width="1.5" opacity="0.35"/>')
    add_bottom_glow(s, 125, 175, 60, 8, color=C_DARK_RED, opacity=0.25, glow=soft)

CARD_RENDERERS["AshEmbrace"] = render_ashembrace


def render_backdraft(s):
    """Reversed flame -- ring shockwave blowing outward."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    g_ring = rad_grad(s, [("0%",C_DARK_BG2,0),("55%",C_DARK_BG2,0),
                          ("70%",C_ORANGE,0.5),("85%",C_DEEP_ORANGE2,0.4),
                          ("100%",C_DARK_RED,0)])
    add_atmosphere(s, opacity=0.05)
    s.comment("Expanding hollow blast ring")
    s.draw(f'  <circle cx="125" cy="95" r="62" fill="url(#{g_ring})" filter="url(#{glow})"/>')
    for r, op, sw, c in [(46,0.7,3,C_ORANGE),(58,0.5,2.5,C_DEEP_ORANGE),
                          (70,0.3,2,C_DEEP_ORANGE2),(82,0.18,1.5,C_DARK_RED)]:
        s.draw(f'  <circle cx="125" cy="95" r="{r}" fill="none" stroke="{c}" '
               f'stroke-width="{sw}" opacity="{op}" filter="url(#{glow})"/>')
    s.comment("Outward streaks: force blowing away from center")
    rng = random.Random(3101)
    for _ in range(16):
        a = rng.uniform(0, 360)
        r0 = rng.uniform(50, 60)
        r1 = r0 + rng.uniform(18, 34)
        x1 = 125 + r0 * math.cos(math.radians(a))
        y1 = 95 + r0 * math.sin(math.radians(a))
        x2 = 125 + r1 * math.cos(math.radians(a))
        y2 = 95 + r1 * math.sin(math.radians(a))
        s.draw(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
               f'stroke="{C_DEEP_ORANGE}" stroke-width="{rng.uniform(1,2.5):.1f}" '
               f'opacity="{rng.uniform(0.3,0.6):.2f}" filter="url(#{glow})"/>')
    s.comment("Hollow dark center (the counter being consumed)")
    s.draw(f'  <circle cx="125" cy="95" r="34" fill="{C_DARK_BG2}" opacity="0.85"/>')
    s.draw(f'  <circle cx="125" cy="95" r="30" fill="{C_DARK_BG}" opacity="0.9"/>')
    s.comment("Faint inward-sucked embers at rim")
    for _ in range(10):
        a = rng.uniform(0, 360)
        r = rng.uniform(38, 46)
        x = 125 + r * math.cos(math.radians(a))
        y = 95 + r * math.sin(math.radians(a))
        s.draw(f'  <circle cx="{x:.1f}" y="{y:.1f}"'.replace(' y=',' cy=') +
               f' r="{rng.uniform(1,2):.1f}" fill="{C_YELLOW3}" '
               f'opacity="0.6" filter="url(#{glow})"/>')
    add_bottom_glow(s, 125, 178, 55, 8, color=C_DARK_RED, opacity=0.2, glow=soft)

CARD_RENDERERS["Backdraft"] = render_backdraft


def render_dragonsmajesty(s):
    """Regal draconic pressure -- flame crown and pressure rings."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 4)
    add_bg(s, cx="50%", cy="60%")
    g_crown = lin_grad(s, [("0%",C_YELLOW,0.9),("50%",C_ORANGE,0.7),
                           ("100%",C_DEEP_ORANGE2,0.5)])
    add_atmosphere(s, cy=105, opacity=0.06)
    add_embers(s, 8, 3201, glow, colors=[C_ORANGE, C_YELLOW, C_DEEP_ORANGE])
    s.comment("Stylized horned dragon crest")
    cx, cy = 125, 92
    s.draw(f'  <path d="M {cx},118 C {cx-30},112 {cx-38},90 {cx-26},70 '
           f'C {cx-20},58 {cx-8},52 {cx},50 '
           f'C {cx+8},52 {cx+20},58 {cx+26},70 '
           f'C {cx+38},90 {cx+30},112 {cx},118 Z" '
           f'fill="{C_DARK_RED2}" opacity="0.85"/>')
    s.draw(f'  <path d="M {cx},118 C {cx-30},112 {cx-38},90 {cx-26},70 '
           f'C {cx-20},58 {cx-8},52 {cx},50 '
           f'C {cx+8},52 {cx+20},58 {cx+26},70 '
           f'C {cx+38},90 {cx+30},112 {cx},118 Z" '
           f'fill="none" stroke="{C_ORANGE}" stroke-width="2" opacity="0.7" filter="url(#{glow})"/>')
    s.comment("Horns")
    s.draw(f'  <path d="M {cx-20},62 Q {cx-40},50 {cx-44},30 Q {cx-30},44 {cx-14},54 Z" '
           f'fill="url(#{g_crown})" opacity="0.85" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M {cx+20},62 Q {cx+40},50 {cx+44},30 Q {cx+30},44 {cx+14},54 Z" '
           f'fill="url(#{g_crown})" opacity="0.85" filter="url(#{glow})"/>')
    s.comment("Burning eyes")
    for dx in (-9, 9):
        s.draw(f'  <path d="M {cx+dx-5},86 Q {cx+dx},82 {cx+dx+5},86 '
               f'Q {cx+dx},92 {cx+dx-5},86 Z" fill="{C_WHITE_HOT}" opacity="0.95" filter="url(#{glow})"/>')
    s.comment("Pressure rings descending outward")
    for r, op in [(70,0.35),(90,0.22),(110,0.12)]:
        s.draw(f'  <ellipse cx="{cx}" cy="{cy+30}" rx="{r}" ry="{r*0.35}" fill="none" '
               f'stroke="{C_DEEP_ORANGE}" stroke-width="1.5" opacity="{op}" filter="url(#{soft})"/>')
    s.comment("Flame crown above")
    for i, (dx, h) in enumerate([(-14,20),(0,30),(14,20)]):
        s.draw(f'  <path d="M {cx+dx-4},48 Q {cx+dx-2},{48-h*0.6} {cx+dx},{48-h} '
               f'Q {cx+dx+2},{48-h*0.6} {cx+dx+4},48 Z" '
               f'fill="url(#{g_crown})" opacity="0.8" filter="url(#{glow})"/>')
    add_bottom_glow(s, 125, 178, 60, 8, color=C_DARK_RED, opacity=0.28, glow=soft)

CARD_RENDERERS["DragonsMajesty"] = render_dragonsmajesty


def render_emberafterglow(s):
    """Fading embers drifting up, leaving glowing trails."""
    glow = add_glow(s, 2.5)
    soft = add_soft_glow(s, 4)
    add_bg(s)
    g_glow = rad_grad(s, [("0%",C_YELLOW,0.7),("40%",C_ORANGE,0.4),
                          ("100%",C_DARK_RED,0)])
    add_atmosphere(s, opacity=0.05)
    add_ash_particles(s, 8, 3301)
    s.comment("Rising ember trails fading upward")
    rng = random.Random(3401)
    for _ in range(7):
        x = rng.uniform(45, 205)
        y0 = rng.uniform(120, 165)
        h = rng.uniform(45, 85)
        drift = rng.uniform(-14, 14)
        s.draw(f'  <path d="M {x:.1f},{y0:.1f} Q {x+drift*0.5:.1f},{y0-h*0.5:.1f} '
               f'{x+drift:.1f},{y0-h:.1f}" fill="none" stroke="{C_ORANGE}" '
               f'stroke-width="{rng.uniform(1,2):.1f}" '
               f'opacity="{rng.uniform(0.25,0.5):.2f}" filter="url(#{soft})"/>')
        s.draw(f'  <circle cx="{x+drift:.1f}" cy="{y0-h:.1f}" r="{rng.uniform(2,3.5):.1f}" '
               f'fill="{C_YELLOW3}" opacity="0.7" filter="url(#{glow})"/>')
        s.draw(f'  <circle cx="{x:.1f}" cy="{y0:.1f}" r="{rng.uniform(1.5,2.5):.1f}" '
               f'fill="{C_DEEP_ORANGE}" opacity="0.6" filter="url(#{glow})"/>')
    s.comment("Dying ember bed at the bottom")
    s.draw(f'  <ellipse cx="125" cy="172" rx="85" ry="12" fill="{ASH_COLORS[3]}" opacity="0.5"/>')
    s.draw(f'  <ellipse cx="125" cy="168" rx="60" ry="8" fill="url(#{g_glow})" opacity="0.6" filter="url(#{glow})"/>')
    for x in (85, 110, 140, 165):
        s.draw(f'  <circle cx="{x}" cy="168" r="2" fill="{C_WHITE_HOT}" opacity="0.7" filter="url(#{glow})"/>')
    s.comment("Faint card-like wisps (drawn power)")
    for dx in (-40, 0, 40):
        s.draw(f'  <path d="M {125+dx-8},96 Q {125+dx},88 {125+dx+8},96 '
               f'Q {125+dx},104 {125+dx-8},96 Z" fill="none" stroke="{C_YELLOW3}" '
               f'stroke-width="1" opacity="0.35" filter="url(#{glow})"/>')
    add_bottom_glow(s, 125, 182, 55, 6, color=C_DARK_RED, opacity=0.2, glow=soft)

CARD_RENDERERS["EmberAfterglow"] = render_emberafterglow


def render_emberscales(s):
    """Overlapping scale plates forming a shield, glowing seams."""
    glow = add_glow(s, 2.5)
    soft = add_soft_glow(s, 4)
    add_bg(s)
    g_scale = lin_grad(s, [("0%",C_DARK_RED2,0.9),("60%","#4a1a08",0.7),
                           ("100%",C_DARK_RED,0.5)])
    g_seam = lin_grad(s, [("0%",C_WHITE_HOT,0.9),("50%",C_ORANGE,0.7),
                          ("100%",C_DEEP_ORANGE2,0.4)])
    add_atmosphere(s, opacity=0.05)
    add_ash_particles(s, 6, 3501)
    s.comment("Curved shield of overlapping scales")
    cx, cy = 125, 100
    for row in range(4):
        ry = cy - 28 + row * 18
        n = 5 + row
        for i in range(n):
            x = cx - (n - 1) * 11 + i * 22
            s.draw(f'  <path d="M {x-11},{ry} Q {x},{ry-14} {x+11},{ry} '
                   f'Q {x},{ry+8} {x-11},{ry} Z" '
                   f'fill="url(#{g_scale})" opacity="0.92"/>')
            s.draw(f'  <path d="M {x-11},{ry} Q {x},{ry-14} {x+11},{ry}" '
                   f'fill="none" stroke="url(#{g_seam})" stroke-width="1.5" '
                   f'opacity="0.8" filter="url(#{glow})"/>')
    s.comment("Heat bleeding through seams")
    rng = random.Random(3601)
    for _ in range(10):
        x = rng.uniform(cx-45, cx+45)
        y = rng.uniform(cy-40, cy+30)
        s.draw(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{rng.uniform(0.8,1.8):.1f}" '
               f'fill="{C_YELLOW3}" opacity="0.5" filter="url(#{glow})"/>')
    s.comment("Outer aura arc")
    s.draw(f'  <path d="M {cx-62},{cy+38} A 70 70 0 0 1 {cx+62},{cy+38}" '
           f'fill="none" stroke="{C_ORANGE}" stroke-width="2" opacity="0.35" filter="url(#{soft})"/>')
    add_bottom_glow(s, cx, 178, 55, 7, color=C_DARK_RED, opacity=0.22, glow=soft)

CARD_RENDERERS["EmberScales"] = render_emberscales


def render_martyrflame(s):
    """Self-consuming offering flame on a pyre, embers spreading."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    g_flame = lin_grad(s, [("0%",C_WHITE_HOT,1),("35%",C_YELLOW,0.9),
                           ("70%",C_ORANGE,0.7),("100%",C_DEEP_ORANGE2,0.4)])
    add_atmosphere(s, opacity=0.06)
    add_embers(s, 7, 3701, glow, colors=[C_ORANGE, C_YELLOW, C_DEEP_ORANGE2])
    s.comment("Pyre base")
    s.draw(f'  <path d="M 75,160 L 95,138 L 155,138 L 175,160 Z" '
           f'fill="{C_DARK_RED2}" opacity="0.9"/>')
    s.draw(f'  <path d="M 85,160 L 100,145 L 150,145 L 165,160" '
           f'fill="none" stroke="{C_DARK_RED}" stroke-width="2" opacity="0.7"/>')
    s.comment("Tall self-consuming flame")
    s.draw(f'  <path d="M 125,138 C 100,120 108,92 125,58 '
           f'C 142,92 150,120 125,138 Z" '
           f'fill="url(#{g_flame})" opacity="0.9" filter="url(#{glow})"/>')
    s.draw(f'  <path d="M 125,132 C 112,118 116,100 125,80 '
           f'C 134,100 138,118 125,132 Z" fill="{C_WHITE_HOT}" opacity="0.75"/>')
    s.comment("Side flame tongues leaning outward (spreading)")
    for side in (-1, 1):
        s.draw(f'  <path d="M {125+side*14},134 Q {125+side*38},120 {125+side*52},98 '
               f'Q {125+side*34},116 {125+side*10},126 Z" '
               f'fill="url(#{g_flame})" opacity="0.5" filter="url(#{glow})"/>')
    s.comment("Rising sparks transferring away")
    rng = random.Random(3801)
    for _ in range(9):
        x = rng.uniform(60, 190)
        y = rng.uniform(25, 90)
        s.draw(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{rng.uniform(1,2.2):.1f}" '
               f'fill="{C_YELLOW3}" opacity="{rng.uniform(0.4,0.7):.2f}" filter="url(#{glow})"/>')
    add_bottom_glow(s, 125, 172, 60, 8, color=C_DARK_RED, opacity=0.3, glow=soft)

CARD_RENDERERS["MartyrFlame"] = render_martyrflame


def render_residualwarmth(s):
    """Faint warm glow from a bed of cold ash."""
    glow = add_glow(s, 2)
    soft = add_soft_glow(s, 4)
    add_bg(s, cx="50%", cy="70%")
    g_warm = rad_grad(s, [("0%",C_YELLOW,0.55),("35%",C_ORANGE,0.3),
                          ("100%",C_DARK_RED,0)])
    add_atmosphere(s, cy=130, color="#3a2a20", opacity=0.07)
    add_ash_particles(s, 14, 3901)
    s.comment("Cold ash bed")
    s.draw(f'  <ellipse cx="125" cy="160" rx="95" ry="22" fill="{ASH_COLORS[3]}" opacity="0.55"/>')
    s.draw(f'  <ellipse cx="125" cy="155" rx="70" ry="15" fill="{ASH_COLORS[2]}" opacity="0.45"/>')
    s.comment("Residual warm glow breathing in the ash")
    s.draw(f'  <ellipse cx="125" cy="150" rx="34" ry="14" fill="url(#{g_warm})" '
           f'opacity="0.7" filter="url(#{glow})"/>')
    s.draw(f'  <ellipse cx="125" cy="150" rx="14" ry="6" fill="{C_WHITE_HOT}" '
           f'opacity="0.55" filter="url(#{glow})"/>')
    s.comment("Faint heat wisps rising")
    for dx in (-18, 0, 18):
        s.draw(f'  <path d="M {125+dx},142 Q {125+dx-5},128 {125+dx},116 '
               f'Q {125+dx+5},104 {125+dx},92" fill="none" stroke="{C_ORANGE}" '
               f'stroke-width="1.2" opacity="0.3" filter="url(#{soft})"/>')
    s.comment("Half-buried embers")
    for x, y in [(92,152),(148,156),(115,160),(160,148)]:
        s.draw(f'  <circle cx="{x}" cy="{y}" r="2" fill="{C_DEEP_ORANGE}" '
               f'opacity="0.6" filter="url(#{glow})"/>')
    s.comment("Faint cards of warmth above")
    for dx in (-30, 30):
        s.draw(f'  <circle cx="{125+dx}" cy="{88}" r="1.8" fill="{C_YELLOW3}" '
               f'opacity="0.4" filter="url(#{glow})"/>')
    add_bottom_glow(s, 125, 180, 60, 7, color=C_DARK_RED, opacity=0.2, glow=soft)

CARD_RENDERERS["ResidualWarmth"] = render_residualwarmth


def render_scorchdetonation(s):
    """Contained scorch circle shattering in a detonation."""
    glow = add_glow(s, 3)
    soft = add_soft_glow(s, 5)
    add_bg(s)
    g_boom = rad_grad(s, [("0%",C_WHITE_HOT,1),("25%",C_YELLOW,0.85),
                          ("55%",C_ORANGE,0.5),("100%",C_DARK_RED,0)])
    add_atmosphere(s, opacity=0.06)
    add_ash_particles(s, 8, 4001)
    cx, cy = 125, 95
    s.comment("Detonation core")
    s.draw(f'  <circle cx="{cx}" cy="{cy}" r="34" fill="url(#{g_boom})" filter="url(#{glow})"/>')
    s.draw(f'  <circle cx="{cx}" cy="{cy}" r="12" fill="{C_WHITE_HOT}" opacity="0.95"/>')
    add_spark_burst(s, cx, cy, 14, 4002, 42, glow=glow)
    s.comment("Shattered containment ring fragments")
    rng = random.Random(4003)
    for _ in range(12):
        a = rng.uniform(0, 360)
        r0 = rng.uniform(42, 50)
        span = rng.uniform(14, 26)
        x0 = cx + r0 * math.cos(math.radians(a))
        y0 = cy + r0 * math.sin(math.radians(a))
        x1 = cx + (r0+span) * math.cos(math.radians(a + rng.uniform(-4,4)))
        y1 = cy + (r0+span) * math.sin(math.radians(a + rng.uniform(-4,4)))
        s.draw(f'  <line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" '
               f'stroke="{C_DEEP_ORANGE2}" stroke-width="{rng.uniform(2,4):.1f}" '
               f'opacity="{rng.uniform(0.5,0.8):.2f}" filter="url(#{glow})"/>')
    s.comment("Broken scorch runes flung outward")
    for _ in range(8):
        a = rng.uniform(0, 360)
        r = rng.uniform(58, 84)
        x = cx + r * math.cos(math.radians(a))
        y = cy + r * math.sin(math.radians(a))
        size = rng.uniform(2.5, 5)
        s.draw(f'  <path d="M {x-size:.1f},{y:.1f} L {x:.1f},{y-size:.1f} '
               f'L {x+size:.1f},{y:.1f} L {x:.1f},{y+size:.1f} Z" '
               f'fill="none" stroke="{C_DEEP_ORANGE}" stroke-width="1.2" '
               f'opacity="{rng.uniform(0.3,0.6):.2f}" filter="url(#{soft})"/>')
    add_bottom_glow(s, cx, 178, 60, 8, color=C_DARK_RED, opacity=0.25, glow=soft)

CARD_RENDERERS["ScorchDetonation"] = render_scorchdetonation


if __name__ == "__main__":
    main()