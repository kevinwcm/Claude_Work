#!/usr/bin/env python3
"""Nestle Digital Day — SysGuard gobo artwork generator.

Everything is drawn light-on-dark: in a gobo, black = no light = bare floor,
so only the bright elements actually appear in the projection.
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Ortho, load_land, text_path, text_width, arc, data_uri

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "assets")
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

BOLD_I = "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf"
BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

S = 2000                      # canvas
C = S / 2                     # centre
R_GLOBE = 742
LON0, LAT0 = -35, 12

CITIES = {
    "NYC": (-74.0, 40.7), "Chicago": (-87.6, 41.9), "Mexico": (-99.1, 19.4),
    "SaoPaulo": (-46.6, -23.5), "BuenosAires": (-58.4, -34.6),
    "London": (-0.1, 51.5), "Vevey": (6.8, 46.5), "Madrid": (-3.7, 40.4),
    "Casablanca": (-7.6, 33.6), "Lagos": (3.4, 6.5), "Cairo": (31.2, 30.0),
    "Joburg": (28.0, -26.2),
}
LINKS = [("Vevey", "London"), ("Vevey", "Cairo"), ("London", "NYC"),
         ("NYC", "Chicago"), ("NYC", "Mexico"), ("Mexico", "SaoPaulo"),
         ("SaoPaulo", "BuenosAires"), ("SaoPaulo", "Lagos"),
         ("Madrid", "Casablanca"), ("Casablanca", "Lagos"),
         ("Lagos", "Joburg"), ("Vevey", "Madrid")]


def fit(text, font, target_w, tracking=0.0):
    """Point size that makes `text` exactly target_w wide."""
    return target_w / text_width(text, font, 1.0, tracking)


def line(text, font, target_w, baseline, tracking=0.0):
    size = fit(text, font, target_w, tracking)
    d, _ = text_path(text, font, size, C, baseline, "middle", tracking)
    return d


# --------------------------------------------------------------- globe bits
def globe(proj, land, style):
    g = []
    if style == "colour":
        g.append(f'<circle cx="{C}" cy="{C}" r="{R_GLOBE}" fill="url(#ocean)"/>')
        g.append('<g stroke="#3FA9E8" stroke-opacity=".30" stroke-width="2.4" fill="none">')
        for d in proj.graticule(20, 20):
            g.append(f'<path d="{d}"/>')
        g.append("</g>")
        g.append('<g fill="url(#land)" fill-opacity=".97">')
        for p in land:
            d = proj.poly_path(p)
            if d:
                g.append(f'<path d="{d}"/>')
        g.append("</g>")
    else:                                            # two-colour line art
        g.append('<g stroke="#FFFFFF" stroke-opacity=".22" stroke-width="3" fill="none">')
        for d in proj.graticule(30, 30):
            g.append(f'<path d="{d}"/>')
        g.append("</g>")
        g.append('<g fill="#FFFFFF" fill-opacity=".14" stroke="#FFFFFF" '
                 'stroke-opacity=".98" stroke-width="6" stroke-linejoin="round">')
        for p in land[:26]:
            d = proj.poly_path(p)
            if d:
                g.append(f'<path d="{d}"/>')
        g.append("</g>")
    return "\n".join(g)


def network(proj, style):
    node = "#FFFFFF" if style == "colour" else "#FFD600"
    g = ['<g fill="none" stroke="%s" stroke-opacity=".55" stroke-width="3">'
         % ("#BFE9FF" if style == "colour" else "#FFD600")]
    pts = {k: proj(*v) for k, v in CITIES.items()}
    for a, b in LINKS:
        xa, ya, va = pts[a]; xb, yb, vb = pts[b]
        if not (va and vb):
            continue
        mx, my = (xa + xb) / 2, (ya + yb) / 2
        vx, vy = mx - C, my - C
        n = math.hypot(vx, vy) or 1
        bow = math.hypot(xb - xa, yb - ya) * 0.16
        g.append(f'<path d="M{xa:.1f},{ya:.1f} Q{mx + vx / n * bow:.1f},'
                 f'{my + vy / n * bow:.1f} {xb:.1f},{yb:.1f}"/>')
    g.append("</g>")
    g.append(f'<g fill="{node}">')
    for x, y, v in pts.values():
        if v:
            g.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7"/>')
            g.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="15" fill="none" '
                     f'stroke="{node}" stroke-opacity=".45" stroke-width="2.5"/>')
    g.append("</g>")
    return "\n".join(g)


def rings(style):
    cy_ = "#4FC8FF" if style == "colour" else "#FFFFFF"
    gold = "url(#goldarc)" if style == "colour" else "#FFD600"
    g = []
    # glow halo just outside the globe
    for w, o in ((30, .07), (16, .13), (7, .34)):
        g.append(f'<circle cx="{C}" cy="{C}" r="{R_GLOBE + 4}" fill="none" '
                 f'stroke="{cy_}" stroke-opacity="{o}" stroke-width="{w}"/>')
    g.append(f'<circle cx="{C}" cy="{C}" r="{R_GLOBE + 4}" fill="none" '
             f'stroke="{cy_}" stroke-opacity=".9" stroke-width="3.5"/>')
    g.append(f'<circle cx="{C}" cy="{C}" r="800" fill="none" stroke="{cy_}" '
             f'stroke-opacity=".40" stroke-width="2.5"/>')
    g.append(f'<circle cx="{C}" cy="{C}" r="828" fill="none" stroke="{cy_}" '
             f'stroke-opacity=".30" stroke-width="4" stroke-dasharray="5 26"/>')
    # four copper / yellow arc segments
    for a0 in (118, 208, 298, 28):
        g.append(f'<path d="{arc(C, C, 866, a0, a0 + 46)}" fill="none" '
                 f'stroke="{gold}" stroke-width="38" stroke-linecap="round"/>')
    # bright outer arcs with breaks at 3 and 9 o'clock
    for a0, a1 in ((100, 260), (280, 440)):
        for w, o in ((22, .10), (11, .20), (5, .85)):
            g.append(f'<path d="{arc(C, C, 908, a0, a1)}" fill="none" '
                     f'stroke="{cy_}" stroke-opacity="{o}" stroke-width="{w}" '
                     f'stroke-linecap="round"/>')
    g.append(f'<circle cx="{C}" cy="{C}" r="948" fill="none" stroke="{cy_}" '
             f'stroke-opacity=".26" stroke-width="2.5"/>')
    g.append(f'<circle cx="{C}" cy="{C}" r="975" fill="none" stroke="{cy_}" '
             f'stroke-opacity=".13" stroke-width="2"/>')
    return "\n".join(g)


def headline(style):
    g = ['<g fill="#FFFFFF">']
    g.append(line("WELCOME", BOLD_I, 1080, 855))
    g.append(line("to", BOLD_I, 150, 968))
    g.append(line("NESTLÉ DIGITAL", BOLD_I, 1290, 1118))
    g.append(line("SUPPLY CHAIN", BOLD_I, 1175, 1262))
    g.append("</g>")
    return "\n".join(g)


def cobrand(style, h_sg=76, h_sx=70):
    """Discreet Syspex / SysGuard credit at the foot of the disc."""
    w_sg, w_sx = h_sg * 5.714, h_sx * 5.517
    gap = 58
    x = C - (w_sg + gap + w_sx) / 2
    ymid = 1580
    g = []
    lbl = "PROJECTED BY"
    size = fit(lbl, BOLD, 300, 0.34)
    d, _ = text_path(lbl, BOLD, size, C, 1466, "middle", 0.34)
    g.append(f'<g fill="#FFFFFF" fill-opacity=".62">{d}</g>')
    for dx in (-1, 1):
        g.append(f'<rect x="{C + dx * 320 - (0 if dx < 0 else 170):.0f}" y="1454" '
                 f'width="170" height="2" fill="url(#rule)"/>')
    g.append(f'<image href="{data_uri(os.path.join(A, "sg-trim.png"))}" '
             f'x="{x:.1f}" y="{ymid - h_sg / 2:.1f}" width="{w_sg:.1f}" height="{h_sg}"/>')
    g.append(f'<rect x="{x + w_sg + gap / 2 - 1:.1f}" y="{ymid - 36}" width="2" '
             f'height="72" fill="#FFFFFF" fill-opacity=".40"/>')
    g.append(f'<image href="{data_uri(os.path.join(A, "sx-trim.png"))}" '
             f'x="{x + w_sg + gap:.1f}" y="{ymid - h_sx / 2:.1f}" '
             f'width="{w_sx:.1f}" height="{h_sx}"/>')
    return "\n".join(g)


DEFS = """
<defs>
  <radialGradient id="ocean" cx="42%%" cy="34%%" r="78%%">
    <stop offset="0%%"  stop-color="#0E3C63"/>
    <stop offset="62%%" stop-color="#06203A"/>
    <stop offset="100%%" stop-color="#010A15"/>
  </radialGradient>
  <linearGradient id="land" x1="0%%" y1="0%%" x2="100%%" y2="100%%">
    <stop offset="0%%"  stop-color="#F7DCAE"/>
    <stop offset="48%%" stop-color="#DFA764"/>
    <stop offset="100%%" stop-color="#B9762F"/>
  </linearGradient>
  <linearGradient id="goldarc" x1="0%%" y1="0%%" x2="100%%" y2="100%%">
    <stop offset="0%%"  stop-color="#FFE7BF"/>
    <stop offset="50%%" stop-color="#E4AE6E"/>
    <stop offset="100%%" stop-color="#A9702B"/>
  </linearGradient>
  <linearGradient id="rule" x1="0%%" y1="0%%" x2="100%%" y2="0%%">
    <stop offset="0%%"   stop-color="#FFFFFF" stop-opacity="0"/>
    <stop offset="50%%"  stop-color="#FFFFFF" stop-opacity=".55"/>
    <stop offset="100%%" stop-color="#FFFFFF" stop-opacity="0"/>
  </linearGradient>
  <radialGradient id="damp" cx="50%%" cy="50%%" r="50%%">
    <stop offset="0%%"   stop-color="#000000" stop-opacity=".93"/>
    <stop offset="52%%"  stop-color="#000000" stop-opacity=".84"/>
    <stop offset="78%%"  stop-color="#000000" stop-opacity=".46"/>
    <stop offset="100%%" stop-color="#000000" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="dampB" cx="50%%" cy="50%%" r="50%%">
    <stop offset="0%%"   stop-color="#000000" stop-opacity=".80"/>
    <stop offset="55%%"  stop-color="#000000" stop-opacity=".62"/>
    <stop offset="100%%" stop-color="#000000" stop-opacity="0"/>
  </radialGradient>
  <clipPath id="disc"><circle cx="%d" cy="%d" r="%d"/></clipPath>
</defs>
""" % (C, C, R_GLOBE)


def build(style):
    proj = Ortho(LON0, LAT0, C, C, R_GLOBE)
    land = load_land("l", 9000)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" '
             f'xmlns:xlink="http://www.w3.org/1999/xlink" '
             f'width="{S}" height="{S}" viewBox="0 0 {S} {S}">',
             DEFS,
             f'<rect width="{S}" height="{S}" fill="#04060A"/>',
             f'<g clip-path="url(#disc)">',
             globe(proj, land, style),
             network(proj, style),
             "</g>",
             rings(style),
             (f'<ellipse cx="{C}" cy="1020" rx="820" ry="430" fill="url(#damp)"/>'
              if style == "colour" else
              f'<ellipse cx="{C}" cy="1020" rx="860" ry="470" fill="url(#dampB)"/>'),
             headline(style),
             cobrand(style),
             "</svg>"]
    return "\n".join(parts)


if __name__ == "__main__":
    import cairosvg
    for style, name in (("colour", "gobo-A-fullcolour"), ("mono", "gobo-B-twocolour")):
        svg = build(style)
        p = os.path.join(OUT, name + ".svg")
        open(p, "w").write(svg)
        cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(OUT, name + ".png"),
                         output_width=1400, output_height=1400)
        print("built", p, len(svg) // 1024, "KB")
