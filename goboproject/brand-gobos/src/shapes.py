"""Drawing helpers for the round brand gobos: text set on a circle, plus
the geometric primitives the emblems are built from.

Everything here is built so a shape can be stamped N times around the
centre, which is what makes the finished gobo read the same from any
viewing angle.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import text_path, text_width, _font

P = lambda x, y: f"{x:.2f},{y:.2f}"


# --------------------------------------------------------------- geometry
def pol(cx, cy, r, deg):
    """Point at radius r, angle deg measured clockwise from 12 o'clock."""
    a = math.radians(deg)
    return cx + r * math.sin(a), cy - r * math.cos(a)


def ring(cx, cy, r, w, colour, opacity=1.0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<circle cx="{cx}" cy="{cy}" r="{r:.2f}" fill="none" stroke="{colour}" '
            f'stroke-opacity="{opacity}" stroke-width="{w}"{d}/>')


def arc(cx, cy, r, a0, a1, colour, w, cap="butt", opacity=1.0):
    """Arc from a0 to a1 (degrees clockwise from 12 o'clock)."""
    x0, y0 = pol(cx, cy, r, a0)
    x1, y1 = pol(cx, cy, r, a1)
    large = 1 if abs(a1 - a0) > 180 else 0
    sweep = 1 if a1 > a0 else 0
    return (f'<path d="M{P(x0,y0)} A{r:.2f},{r:.2f} 0 {large} {sweep} {P(x1,y1)}" '
            f'fill="none" stroke="{colour}" stroke-opacity="{opacity}" '
            f'stroke-width="{w}" stroke-linecap="{cap}"/>')


def ticks(cx, cy, r0, r1, n, colour, w, offset=0.0, opacity=1.0):
    out = []
    for i in range(n):
        a = offset + i * 360 / n
        x0, y0 = pol(cx, cy, r0, a)
        x1, y1 = pol(cx, cy, r1, a)
        out.append(f'<path d="M{P(x0,y0)} L{P(x1,y1)}" stroke="{colour}" '
                   f'stroke-opacity="{opacity}" stroke-width="{w}" stroke-linecap="round"/>')
    return "".join(out)


def poly_at(cx, cy, r, deg, pts, colour, rotate=True, opacity=1.0):
    """Stamp a local-coordinate polygon at radius r / angle deg.

    Local +y points outward from the centre, +x is tangential, so a shape
    drawn once can be repeated around the ring and always face outward.
    """
    x, y = pol(cx, cy, r, deg)
    rot = f" rotate({deg})" if rotate else ""
    body = " ".join(P(*p) for p in pts)
    return (f'<g transform="translate({x:.2f},{y:.2f}){rot}">'
            f'<polygon points="{body}" fill="{colour}" fill-opacity="{opacity}"/></g>')


def chevron(cx, cy, r, deg, w, h, t, colour, opacity=1.0):
    """A single outward-pointing chevron (hazard/direction language)."""
    pts = [(-w / 2, h / 2), (0, -h / 2), (w / 2, h / 2),
           (w / 2 - t, h / 2), (0, -h / 2 + t * 1.6), (-w / 2 + t, h / 2)]
    pts = [(x, -y) for x, y in pts]          # local +y outward
    return poly_at(cx, cy, r, deg, pts, colour, opacity=opacity)


def ngon(cx, cy, r, n, colour, w=0, fill="none", rot=0.0, opacity=1.0):
    pts = [pol(cx, cy, r, rot + i * 360 / n) for i in range(n)]
    d = "M" + " L".join(P(*p) for p in pts) + " Z"
    stroke = f' stroke="{colour}" stroke-width="{w}" stroke-linejoin="round"' if w else ""
    return f'<path d="{d}" fill="{fill}" fill-opacity="{opacity}"{stroke}/>'


def dot(cx, cy, r, deg, rad, colour, opacity=1.0):
    x, y = pol(cx, cy, r, deg)
    return f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{rad}" fill="{colour}" fill-opacity="{opacity}"/>'


# ------------------------------------------------------------------- type
def arc_text(text, font, size, cx, cy, radius, centre_deg, colour,
             tracking=0.0, inward=False, opacity=1.0):
    """Set `text` along a circle, centred on centre_deg.

    Letters stand upright to a viewer looking at that part of the ring from
    outside the circle -- which is what lets the same word, repeated a few
    times around the gobo, always be readable from somewhere.
    """
    _, gs, cmap, upem, hmtx = _font(font)
    scale = size / upem
    advances = []
    for ch in text:
        gn = cmap.get(ord(ch)) or cmap.get(ord(" "))
        advances.append(hmtx[gn][0] * scale + tracking * size)
    total = sum(advances)
    out = []
    # walk from the start of the string, placing each glyph at its own angle
    s = -total / 2
    for ch, adv in zip(text, advances):
        mid = s + adv / 2
        deg = centre_deg + math.degrees(mid / radius) * (-1 if inward else 1)
        glyph, w = text_path(ch, font, size, 0, 0, "middle")
        flip = 180 if inward else 0
        x, y = pol(cx, cy, radius, deg)
        out.append(f'<g transform="translate({x:.2f},{y:.2f}) rotate({deg + flip:.3f})">'
                   f'<g transform="translate(0,{-0 if inward else 0})">{glyph}</g></g>')
        s += adv
    return f'<g fill="{colour}" fill-opacity="{opacity}">' + "".join(out) + "</g>"


def arc_text_width_deg(text, font, size, radius, tracking=0.0):
    return math.degrees(text_width(text, font, size, tracking) / radius)
