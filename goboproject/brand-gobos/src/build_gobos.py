#!/usr/bin/env python3
"""Two round brand gobos: one for Syspex, one for SysGuard.

Design rule that drives everything: the projection must read from any
viewing angle, so nothing may have a single "up". Elements are stamped 4,
8, 12, 24 or 48 times around the centre, and each brand name is set four
times facing outward, so a viewer standing anywhere sees a name no more
than 45 degrees off upright. A projector that is rotated or misaligned
makes no visible difference.

Type and marks are the real thing: the letterforms, the Syspex tile and
the SysGuard helmet are traced straight out of the approved logo files
(see logo_trace.py), so the gobo carries the logo's own font rather than
a lookalike.

Gobo convention, as with the other files in this project:
  black   = no light (the floor shows through)
  colour  = open aperture (light passes)

Brand colours as supplied: Syspex teal #00BBB4, SysGuard yellow #EED202.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import logo_trace as LT
from shapes import (arc, arc_text, arc_text_width_deg, arc_wordmark, chevron,
                    dot, ngon, P, place, pol, ring, sector, sheared_sector,
                    ticks, poly_at)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "artwork")
BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

S, C, R = 2000, 1000.0, 950
BG = "#05070A"

# where each logo's parts sit in its PNG
SX_WORD = (20, 166, 150, 1600)
SG_WORD = (42, 154, 400, 1600)

SYSPEX = dict(name="SYSPEX", tagline="A HELPING BUSINESS",
              primary="#00BBB4", light="#5FD9D3", white="#FFFFFF",
              accent="#00BBB4", file="gobo-syspex")
SYSGUARD = dict(name="SYSGUARD", tagline="SMARTER PROTECTION  ·  SAFER WORKPLACE",
                primary="#EED202", light="#F8E96A", white="#FFFFFF",
                accent="#00C2FF", file="gobo-sysguard")


def fit_size(text, radius, target_deg, tracking):
    lo, hi = 10.0, 400.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if arc_text_width_deg(text, BOLD, mid, radius, tracking) < target_deg:
            lo = mid
        else:
            hi = mid
    return lo


def rim(b):
    return "\n".join([
        ring(C, C, 944, 7, b["primary"]),
        ring(C, C, 924, 2.5, b["primary"], .5),
        ring(C, C, 852, 2, b["primary"], .3),
        ring(C, C, 688, 3, b["primary"], .45),
    ])


def name_band(b, wm):
    """Brand name x4 in the logo's own letterforms, tagline x4 outside it,
    and a divider on each diagonal so the four labels read separately."""
    g = []
    tsize = min(fit_size(b["tagline"], 856, 80, 0.10), 56)
    for i in range(4):
        a = i * 90
        word, cap = arc_wordmark(wm, C, C, 700, a, 70, b["white"])
        g.append(word)
        g.append(arc_text(b["tagline"], BOLD, tsize, C, C, 856, a,
                          b["primary"], 0.10, opacity=1))
    for i in range(4):
        a = 45 + i * 90
        g.append(ticks(C, C, 700, 840, 1, b["primary"], 3, offset=a, opacity=.35))
        g.append(chevron(C, C, 790, a, 66, 42, 14, b["primary"], .95))
        g.append(chevron(C, C, 750, a, 50, 31, 11, b["primary"], .5))
    print(f"   name cap ~{cap:.0f}px, tagline {tsize:.0f}pt")
    return "\n".join(g)


def reticle(b, r=640):
    g = []
    for i in range(4):
        a = 45 + i * 90
        for da, sign in ((-7, 1), (7, -1)):
            g.append(arc(C, C, r, a + da - sign * 9, a + da, b["primary"], 6, "round", .8))
        g.append(dot(C, C, r, a, 7, b["primary"], .9))
    return "\n".join(g)


# --------------------------------------------------------------- emblems
def syspex_emblem(b):
    """A systems/network field around the real Syspex tile."""
    g = [ring(C, C, 600, 3.5, b["primary"], .6, dash="26 22"),
         ticks(C, C, 612, 632, 24, b["primary"], 3, offset=7.5, opacity=.4)]
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
    for i in range(12):
        a = i * 30 + 15
        x0, y0 = pol(C, C, 330, a)
        x1, y1 = pol(C, C, 470, a)
        g.append(f'<path d="M{P(x0,y0)} L{P(x1,y1)}" stroke="{b["primary"]}" '
                 f'stroke-opacity=".62" stroke-width="3.5"/>')
        g.append(dot(C, C, 470, a, 7, b["light"], .85))
    for i in range(4):
        a = 45 + i * 90
        for off, r0, r1 in ((-11, 545, 600), (0, 545, 615), (11, 545, 600)):
            xa, ya = pol(C, C, r0, a + off)
            xb, yb = pol(C, C, r1, a + off)
            g.append(f'<path d="M{P(xa,ya)} L{P(xb,yb)}" stroke="{b["primary"]}" '
                     f'stroke-opacity=".75" stroke-width="5" stroke-linecap="round"/>')
            g.append(dot(C, C, r1, a + off, 9, b["light"], .9))
    # the real Syspex mark at the centre. It reads the same either way up
    # (180-degree symmetric), so it is safe in the middle of an any-angle gobo.
    tile = LT.mark("logo-syspex-white.png", "teal", box=(0, 290, 0, 190))
    g.append(ring(C, C, 296, 5, b["primary"], .45))
    g.append(ticks(C, C, 300, 318, 8, b["primary"], 4, offset=22.5, opacity=.5))
    g.append(place(tile, C, C, 0, 0, 330, b["primary"], rotate=False))
    return "\n".join(g)


def _hazard_tape(b, r0=570, r1=655, n=24, shear=8.0):
    """Industrial hazard tape wrapped into a ring -- SysGuard's own border
    motif, and the calmest way to say 'safety' without shouting."""
    g = [ring(C, C, r1 + 7, 5, b["primary"], .9), ring(C, C, r0 - 7, 5, b["primary"], .9)]
    for i in range(n):
        g.append(sheared_sector(C, C, r0, r1, i * 360 / n, 360 / n * 0.5,
                                shear, b["primary"], .95))
    return g


def _chevron_ring(b, r=612, n=12):
    """A ring of outward chevrons: directional, open, plenty of black."""
    g = [ring(C, C, r + 58, 4, b["primary"], .55), ring(C, C, r - 58, 4, b["primary"], .55)]
    for i in range(n):
        g.append(chevron(C, C, r, i * 360 / n, 104, 66, 23, b["primary"], .95))
    return g


def _zone_ring(b):
    """The quietest option: containment rings, ticks and corner brackets."""
    g = [ring(C, C, 655, 6, b["primary"], .9),
         ring(C, C, 614, 4, b["primary"], .45, dash="30 26"),
         ring(C, C, 570, 6, b["primary"], .9),
         ticks(C, C, 632, 648, 48, b["primary"], 3, opacity=.45)]
    for i in range(4):
        a = 45 + i * 90
        for da, sign in ((-10, 1), (10, -1)):
            g.append(arc(C, C, 592, a + da - sign * 13, a + da, b["primary"], 9, "round", .95))
    return g


BANDS = dict(tape=_hazard_tape, chevron=_chevron_ring, zone=_zone_ring)


def sysguard_emblem(b, band="tape"):
    """A single upright SysGuard helmet inside one clean safety band."""
    g = list(BANDS[band](b))
    g.append(ring(C, C, 506, 3, b["primary"], .35))
    g.append(ticks(C, C, 486, 500, 24, b["primary"], 3, offset=7.5, opacity=.3))
    for i in range(4):                       # a restrained detection cue
        a = 45 + i * 90
        g.append(arc(C, C, 524, a - 8, a + 8, b["accent"], 5, "round", .85))
    helm = LT.mark("logo-sysguard-2026.png", "yellow", box=(0, 1250, 0, 2000))
    g.append(place(helm, C, C, 0, 0, 470, b["primary"], rotate=False))
    return "\n".join(g)


def build(b, emblem, wm, suffix="", ret_r=640, **kw):
    print(f" - {b['file']}{suffix}")
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{S}" height="{S}" '
        f'viewBox="0 0 {S} {S}">',
        f'<!-- {b["name"]} round gobo. 4-fold rotationally symmetric: the disc '
        f'is identical every 90 degrees, so projector rotation does not matter. '
        f'Type and marks traced from the approved logo files. '
        f'Black = no light, colour = open aperture. -->',
        f'<rect width="{S}" height="{S}" fill="{BG}"/>',
        rim(b), name_band(b, wm),
        reticle(b, ret_r) if ret_r else "", emblem(b, **kw),
        "</svg>",
    ]
    svg = "\n".join(parts)
    path = os.path.join(OUT, b["file"] + suffix + ".svg")
    open(path, "w").write(svg)
    return path, svg


if __name__ == "__main__":
    import cairosvg
    sx_wm = LT.wordmark("logo-syspex-white.png", SX_WORD, expect=6)
    sg_wm = LT.wordmark("logo-sysguard-white.png", SG_WORD, expect=8)
    jobs = [(SYSPEX, syspex_emblem, sx_wm, "", {}),
            # hazard tape is the recommended band -- see the README
            # no reticle on SysGuard: the tape band already occupies that ring
            (SYSGUARD, sysguard_emblem, sg_wm, "", dict(ret_r=None, band="tape")),
            (SYSGUARD, sysguard_emblem, sg_wm, "-alt-chevron", dict(ret_r=None, band="chevron")),
            (SYSGUARD, sysguard_emblem, sg_wm, "-alt-zone", dict(ret_r=None, band="zone"))]
    for b, em, wm, suffix, kw in jobs:
        path, svg = build(b, em, wm, suffix, **kw)
        # the masters also go out at 3000 px; the alternates stay at 2000
        sizes = (2000, 3000) if not suffix else (2000,)
        for px in sizes:
            cairosvg.svg2png(bytestring=svg.encode(), output_width=px, output_height=px,
                             write_to=os.path.join(OUT, f"{b['file']}{suffix}-{px}.png"))
        print("   wrote", path, "at", ", ".join(f"{p}px" for p in sizes))
