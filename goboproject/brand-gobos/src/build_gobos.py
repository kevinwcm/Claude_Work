#!/usr/bin/env python3
"""Two round brand gobos: one for Syspex, one for SysGuard.

Design rule that drives everything: the projection must read from any
viewing angle, so nothing may have a single "up". Every element is
stamped 4, 12, 24 or 48 times around the centre, giving the whole disc
4-fold rotational symmetry -- turn it 90 degrees and it is identical.
The brand name is set four times around the ring, each facing outward,
so a viewer standing anywhere sees a name no more than 45 degrees off
upright, and a projector that is rotated or misaligned makes no visible
difference.

Gobo convention, as with the other files in this project:
  black   = no light (the floor shows through)
  colour  = open aperture (light passes)

Brand colours are the official ones Kevin supplied: Syspex teal #00BBB4,
SysGuard safety yellow #EED202. (Sampling the approved logo PNGs gives
#19BCB9 and #FFF200 -- close, but the official values win.)
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapes import (arc, arc_text, arc_text_width_deg, chevron, dot, ngon,
                    P, pol, ring, ticks, poly_at)
from lib import text_path

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "artwork")

BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
# NOTE: the brands' own faces (Poppins / the logo's squared techno face)
# are not installed here. Type is set in Liberation Sans Bold as a
# stand-in and must be swapped before production -- see the README.

S = 2000
C = S / 2
R = 950                       # outer edge of the artwork
BG = "#05070A"

SYSPEX = dict(
    name="SYSPEX", tagline="A HELPING BUSINESS",
    primary="#00BBB4", light="#5FD9D3", white="#FFFFFF", accent="#00BBB4",
    file="gobo-syspex",
)
SYSGUARD = dict(
    name="SYSGUARD", tagline="SMARTER PROTECTION  ·  SAFER WORKPLACE",
    primary="#EED202", light="#F8E96A", white="#FFFFFF", accent="#00C2FF",
    file="gobo-sysguard",
)


def fit_size(text, radius, target_deg, tracking):
    """Point size that makes `text` span target_deg of arc at `radius`."""
    lo, hi = 10.0, 400.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if arc_text_width_deg(text, BOLD, mid, radius, tracking) < target_deg:
            lo = mid
        else:
            hi = mid
    return lo


# ------------------------------------------------------------ shared rings
def rim(b):
    return "\n".join([
        ring(C, C, 944, 7, b["primary"]),
        ring(C, C, 924, 2.5, b["primary"], .5),
        ring(C, C, 852, 2, b["primary"], .3),
        ring(C, C, 688, 3, b["primary"], .45),
        ticks(C, C, 655, 672, 24, b["primary"], 3, offset=7.5, opacity=.5),
    ])


def name_band(b):
    """Name x4 on the main band, tagline x4 on the outer band, and a divider
    on each diagonal so the four segments read as four separate labels."""
    g = []
    size = min(fit_size(b["name"], 700, 58, 0.14), 152)
    tsize = min(fit_size(b["tagline"], 856, 80, 0.10), 72)
    for i in range(4):
        a = i * 90
        g.append(arc_text(b["name"], BOLD, size, C, C, 700, a, b["white"], 0.14))
        g.append(arc_text(b["tagline"], BOLD, tsize, C, C, 856, a, b["primary"],
                          0.10, opacity=1))
    for i in range(4):
        a = 45 + i * 90
        g.append(ticks(C, C, 700, 840, 1, b["primary"], 3, offset=a, opacity=.35))
        g.append(chevron(C, C, 790, a, 66, 42, 14, b["primary"], .95))
        g.append(chevron(C, C, 750, a, 50, 31, 11, b["primary"], .5))
    print(f"   name {size:.0f}pt (cap ~{size*.72:.0f}px), tagline {tsize:.0f}pt")
    return "\n".join(g)


def reticle(b, r=640):
    """Four corner brackets -- a 'system watching' cue, 4-fold by design."""
    g = []
    for i in range(4):
        a = 45 + i * 90
        for da, sign in ((-7, 1), (7, -1)):
            g.append(arc(C, C, r, a + da - sign * 9, a + da, b["primary"], 6, "round", .8))
        x, y = pol(C, C, r, a)
        g.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{b["primary"]}" fill-opacity=".9"/>')
    return "\n".join(g)


# --------------------------------------------------------------- emblems
def syspex_emblem(b):
    """A systems/network core: nodes, mesh and circuit traces."""
    g = [ring(C, C, 600, 3.5, b["primary"], .6, dash="26 22"),
         ticks(C, C, 612, 632, 24, b["primary"], 3, offset=7.5, opacity=.4)]
    # network mesh across twelve nodes
    nodes = [pol(C, C, 520, i * 30) for i in range(12)]
    for step, op, w in ((5, .3, 3.0), (3, .62, 5.0)):
        for i in range(12):
            x0, y0 = nodes[i]
            x1, y1 = nodes[(i + step) % 12]
            g.append(f'<path d="M{P(x0,y0)} L{P(x1,y1)}" stroke="{b["primary"]}" '
                     f'stroke-opacity="{op}" stroke-width="{w}"/>')
    for i in range(12):
        g.append(dot(C, C, 520, i * 30, 21, b["primary"], .28))
        g.append(dot(C, C, 520, i * 30, 11, b["white"], .95))
    # radial spokes with inline nodes
    for i in range(12):
        a = i * 30 + 15
        x0, y0 = pol(C, C, 270, a)
        x1, y1 = pol(C, C, 470, a)
        g.append(f'<path d="M{P(x0,y0)} L{P(x1,y1)}" stroke="{b["primary"]}" '
                 f'stroke-opacity=".62" stroke-width="3.5"/>')
        g.append(dot(C, C, 470, a, 7, b["light"], .85))
    # circuit traces on the diagonals
    for i in range(4):
        a = 45 + i * 90
        for off, r0, r1 in ((-11, 545, 600), (0, 545, 615), (11, 545, 600)):
            xa, ya = pol(C, C, r0, a + off)
            xb, yb = pol(C, C, r1, a + off)
            g.append(f'<path d="M{P(xa,ya)} L{P(xb,yb)}" stroke="{b["primary"]}" '
                     f'stroke-opacity=".75" stroke-width="5" stroke-linecap="round"/>')
            g.append(dot(C, C, r1, a + off, 9, b["light"], .9))
    # core: a four-way data diamond -- four arms out along the axes, inside
    # nested diamonds. Four-fold by construction, so it never looks "upside
    # down"; the angular, interlocking feel nods to the Syspex mark without
    # copying it.
    g.append(ngon(C, C, 282, 4, b["primary"], w=7, rot=45, opacity=.5))
    g.append(ngon(C, C, 238, 4, b["primary"], w=3, rot=45, opacity=.28))
    # four offset bars stamped at 90 degrees interlock into a pinwheel
    # square -- the "systems fitting together" idea, and 4-fold by design
    for i in range(4):
        bar = [(-168, -122), (44, -122), (44, -58), (-168, -58)]
        g.append(poly_at(C, C, 0, i * 90, bar, b["primary"], opacity=.95))
    g.append(ngon(C, C, 66, 4, b["light"], fill=b["light"], rot=45, opacity=.95))
    g.append(f'<circle cx="{C}" cy="{C}" r="30" fill="{BG}"/>')
    g.append(f'<circle cx="{C}" cy="{C}" r="16" fill="{b["white"]}"/>')
    return "\n".join(g)


def sysguard_emblem(b):
    """A protective sensing field around a shielded core: detection sweeps,
    sensor nodes, hazard chevrons, a hex cell ring, and an octagon shield."""
    g = []
    # three broken 'detection sweep' rings, heavier as they go out
    for r, w, seg, op in ((600, 10, 21, .95), (556, 5.5, 17, .6), (512, 4, 13, .4)):
        for i in range(12):
            a = i * 30
            g.append(arc(C, C, r, a - seg / 2, a + seg / 2, b["primary"], w, "round", op))
    # sensor nodes with a small cyan detection tick (cyan stays an accent)
    for i in range(12):
        a = i * 30 + 15
        g.append(dot(C, C, 556, a, 22, b["primary"], .25))
        g.append(dot(C, C, 556, a, 10, b["primary"], .95))
        g.append(arc(C, C, 578, a - 6, a + 6, b["accent"], 4.5, "round", .9))
    # bold outward hazard chevrons
    for i in range(12):
        g.append(chevron(C, C, 470, i * 30, 94, 60, 21, b["primary"], .95))
    # a ring of hex cells -- 'protected cells', and the brand's hex texture
    for i in range(12):
        x, y = pol(C, C, 392, i * 30 + 15)
        g.append(ngon(x, y, 48, 6, b["primary"], w=5.5, opacity=.55))
        g.append(ngon(x, y, 20, 6, b["primary"], fill=b["primary"], opacity=.35))
    g.append(ring(C, C, 336, 3, b["primary"], .4))
    g.append(ticks(C, C, 318, 332, 24, b["primary"], 3, offset=7.5, opacity=.35))
    # core: an octagon shield, held in a cyan reticle
    g.append(ngon(C, C, 292, 8, b["primary"], w=9, rot=22.5, opacity=.8))
    g.append(ngon(C, C, 244, 8, b["primary"], w=4, rot=22.5, opacity=.38))
    for i in range(4):
        a = 45 + i * 90
        for da in (-1, 1):
            xa, ya = pol(C, C, 196, a + da * 11)
            xb, yb = pol(C, C, 268, a + da * 11)
            g.append(f'<path d="M{P(xa,ya)} L{P(xb,yb)}" stroke="{b["accent"]}" '
                     f'stroke-opacity=".85" stroke-width="6" stroke-linecap="round"/>')
    g.append(ngon(C, C, 152, 8, b["primary"], fill=b["primary"], rot=22.5, opacity=.95))
    g.append(f'<circle cx="{C}" cy="{C}" r="58" fill="{BG}"/>')
    g.append(ngon(C, C, 40, 8, b["white"], fill=b["white"], rot=22.5))
    return "\n".join(g)


def build(b, emblem):
    print(f" - {b['file']}")
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{S}" height="{S}" '
        f'viewBox="0 0 {S} {S}">',
        f'<!-- {b["name"]} round gobo. 4-fold rotationally symmetric: the disc is '
        f'identical every 90 degrees, so projector rotation does not matter. '
        f'Black = no light, colour = open aperture. -->',
        f'<rect width="{S}" height="{S}" fill="{BG}"/>',
        rim(b), name_band(b), reticle(b), emblem(b),
        "</svg>",
    ]
    svg = "\n".join(parts)
    path = os.path.join(OUT, b["file"] + ".svg")
    open(path, "w").write(svg)
    return path, svg


if __name__ == "__main__":
    import cairosvg
    for b, em in ((SYSPEX, syspex_emblem), (SYSGUARD, sysguard_emblem)):
        path, svg = build(b, em)
        cairosvg.svg2png(bytestring=svg.encode(), output_width=2000, output_height=2000,
                         write_to=os.path.join(OUT, b["file"] + "-2000.png"))
        print("   wrote", path)
