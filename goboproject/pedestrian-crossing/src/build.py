#!/usr/bin/env python3
"""Rebuild the 'Pedestrian Crossing' gobo as an editable SVG.

Reconstructed from a photo of the pattern as currently projected, on the
same 2250x2250pt canvas / ~5.8m x 2.4m aperture envelope as Kevin's
existing "Powered by Syspex" reference PDF, so it drops into the same
fixture. Convention (matched to that reference file):

  - unfilled canvas  = opaque / blocked (no light)
  - yellow fill      = open aperture (light passes)
  - black fill       = a cut-out INSIDE an open area (text, icon) -- still
                        blocked, drawn on top of the yellow
  - thin black stroke = cut/kerf outline around every open shape

Top band is rotated 180 degrees about its own centre (not just flipped),
matching the "Secured by SysGuard" band in the reference file -- so each
band reads right-way-up to someone approaching from that end of the
walkway.
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import text_path, text_width

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
YELLOW = "#FFF200"
BLACK = "#000000"
STROKE = 6.0

CANVAS = 2250
# same outer envelope as the "Powered by Syspex" reference (~5.8m x 2.4m)
X0, X1 = 170.2, 2079.8
Y0, Y1 = 701.9, 1518.8           # top hairline to bottom of bottom band
BAND_H = 51.9
GAP = 18.4                       # band -> stripe-field clearance
TOP_BAND = (731.2, 731.2 + BAND_H)
BOT_BAND = (Y1 - BAND_H, Y1)
FIELD = (TOP_BAND[1] + GAP, BOT_BAND[0] - GAP)   # stripe field y-range

SCALE_PT_PER_M = (X1 - X0) / 5.8   # ~329.3 pt/m, confirmed against the 2.4m callout


def pedestrian_icon(cx, cy, h):
    """A simple walking-figure pictogram, h tall, centred at (cx, cy)."""
    s = h / 100.0
    # path drawn in a 100-unit-tall local box, feet near y=96, head near y=8
    d = (
        "M 6,8 a 9,9 0 1,0 18,0 a 9,9 0 1,0 -18,0 Z "                  # head
        "M 10,24 "
        "C 4,26 -2,34 0,44 "                                            # trailing arm sweep
        "L 9,42 "
        "C 8,36 12,31 17,29 "
        "L 34,34 "
        "C 40,36 42,44 40,54 "
        "L 33,86 L 41,96 L 33,98 L 22,70 L 13,96 L 4,94 L 15,58 "
        "C 12,50 8,42 10,24 Z "
        "M 22,34 C 30,30 40,32 44,24 L 52,28 C 47,40 34,42 24,44 Z"     # forward arm
    )
    return f'<g transform="translate({cx - 27 * s:.2f},{cy - 55 * s:.2f}) scale({s:.4f})"><path d="{d}"/></g>'


def label_group(cx, cy, band_top, band_bot):
    """PEDESTRIAN CROSSING flanked by pedestrian icons, black, centred."""
    text = "PEDESTRIAN CROSSING"
    icon_h = (band_bot - band_top) * 0.62
    size = 40.0
    tw = text_width(text, BOLD, size, tracking=0.02)
    pad = 30.0
    total = icon_h + pad + tw + pad + icon_h
    left = cx - total / 2
    g = ['<g fill="#000000">']
    g.append(pedestrian_icon(left + icon_h / 2, cy, icon_h))
    tx0 = left + icon_h + pad
    d, _ = text_path(text, BOLD, size, tx0 + tw / 2, cy + size * 0.36, "middle", 0.02)
    g.append(d)
    g.append(pedestrian_icon(left + icon_h + pad + tw + pad + icon_h / 2, cy, icon_h))
    g.append("</g>")
    return "".join(g)


def band(y0, y1, mirrored):
    cx, cy = (X0 + X1) / 2, (y0 + y1) / 2
    g = [f'<rect x="{X0:.1f}" y="{y0:.1f}" width="{X1 - X0:.1f}" height="{y1 - y0:.1f}" '
         f'fill="{YELLOW}" stroke="{BLACK}" stroke-width="{STROKE}"/>']
    inner = label_group(cx, cy, y0, y1)
    if mirrored:
        g.append(f'<g transform="rotate(180 {cx:.1f} {cy:.1f})">{inner}</g>')
    else:
        g.append(inner)
    return "\n".join(g)


def stripe_field():
    y0, y1 = FIELD
    h = y1 - y0
    shear = h * math.tan(math.radians(30))      # ~30 deg off vertical, from the photo
    n_half = 13                                  # 7 bright + 6 dark half-bands
    period = (X1 - X0) / n_half
    g = [f'<clipPath id="field-clip"><rect x="{X0:.1f}" y="{y0:.1f}" '
         f'width="{X1 - X0:.1f}" height="{h:.1f}"/></clipPath>']
    g.append(f'<rect x="{X0:.1f}" y="{y0:.1f}" width="{X1 - X0:.1f}" height="{h:.1f}" '
             f'fill="none" stroke="{BLACK}" stroke-width="{STROKE}"/>')
    g.append('<g clip-path="url(#field-clip)">')
    for i in range(0, n_half, 2):                # even indices = bright stripes
        xb0 = X0 + i * period
        xb1 = xb0 + period
        xt0, xt1 = xb0 + shear, xb1 + shear
        pts = f"{xt0:.1f},{y0:.1f} {xt1:.1f},{y0:.1f} {xb1:.1f},{y1:.1f} {xb0:.1f},{y1:.1f}"
        g.append(f'<polygon points="{pts}" fill="{YELLOW}" stroke="{BLACK}" '
                 f'stroke-width="{STROKE}" stroke-linejoin="round"/>')
    g.append("</g>")
    return "\n".join(g)


def build():
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS}" height="{CANVAS}" '
        f'viewBox="0 0 {CANVAS} {CANVAS}">',
        f'<!-- Pedestrian Crossing gobo. Aperture {X1 - X0:.0f} x {Y1 - Y0:.0f} pt '
        f'(~5.8m x 2.4m at {SCALE_PT_PER_M:.1f} pt/m), same envelope as the '
        f'"Powered by Syspex" reference file. Unfilled = opaque, yellow = open, '
        f'black = cut-out on an open area. -->',
        f'<rect x="{X0:.1f}" y="{Y0:.1f}" width="{X1 - X0:.1f}" height="3.0" fill="{BLACK}"/>',
        band(*TOP_BAND, mirrored=True),
        stripe_field(),
        band(*BOT_BAND, mirrored=False),
        "</svg>",
    ]
    return "\n".join(parts)


if __name__ == "__main__":
    import cairosvg
    svg = build()
    p = os.path.join(OUT, "pedestrian-crossing.svg")
    open(p, "w").write(svg)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(OUT, "pedestrian-crossing-2400.png"),
                     output_width=2400, output_height=2400, background_color="white")
    print("built", p, len(svg) // 1024, "KB")
