"""Helpers: GSHHS coastline parsing, orthographic projection, text-to-outline."""
import math, os, struct, base64
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

DATA = "/usr/local/lib/python3.11/dist-packages/mpl_toolkits/basemap_data"

# ---------------------------------------------------------------- coastlines
def load_land(res="l", min_area=12000.0):
    """Return list of polygons [(lon, lat), ...] for land, largest first."""
    meta = os.path.join(DATA, f"gshhsmeta_{res}.dat")
    dat = os.path.join(DATA, f"gshhs_{res}.dat")
    polys = []
    with open(dat, "rb") as fh:
        for line in open(meta):
            parts = line.split()
            typ = int(parts[0]); area = float(parts[1]); npts = int(parts[2])
            offset = int(parts[5]); nbytes = int(parts[6])
            if typ != 1 or area < min_area:      # 1 = land
                continue
            fh.seek(offset)
            raw = struct.unpack(f"<{npts*2}f", fh.read(npts * 8))
            polys.append(list(zip(raw[0::2], raw[1::2])))
    polys.sort(key=len, reverse=True)
    return polys


# ------------------------------------------------------------- projection
class Ortho:
    """Orthographic globe projection onto a circle of radius R at (cx, cy)."""

    def __init__(self, lon0, lat0, cx, cy, R):
        self.lon0 = math.radians(lon0); self.lat0 = math.radians(lat0)
        self.cx, self.cy, self.R = cx, cy, R

    def __call__(self, lon, lat):
        """-> (x, y, visible)"""
        lo = math.radians(lon) - self.lon0
        la = math.radians(lat)
        cosc = (math.sin(self.lat0) * math.sin(la)
                + math.cos(self.lat0) * math.cos(la) * math.cos(lo))
        x = math.cos(la) * math.sin(lo)
        y = math.cos(self.lat0) * math.sin(la) - math.sin(self.lat0) * math.cos(la) * math.cos(lo)
        if cosc < 0:                              # far side -> pin to the limb
            n = math.hypot(x, y) or 1.0
            x, y = x / n, y / n
        return self.cx + x * self.R, self.cy - y * self.R, cosc >= 0

    def poly_path(self, poly, step=1):
        """SVG path for one lon/lat polygon; None when fully hidden."""
        pts = [self(lo, la) for lo, la in poly[::step]]
        if not any(p[2] for p in pts):
            return None
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y, _ in pts) + " Z"
        return d

    def graticule(self, dlon=20, dlat=20):
        """SVG paths for meridians + parallels, visible arcs only."""
        out = []
        for lon in range(-180, 180, dlon):
            seg = []
            for i in range(-90, 91, 2):
                x, y, v = self(lon, i)
                if v:
                    seg.append((x, y))
                elif seg:
                    if len(seg) > 1:
                        out.append(seg)
                    seg = []
            if len(seg) > 1:
                out.append(seg)
        for lat in range(-80, 81, dlat):
            seg = []
            for i in range(-180, 181, 2):
                x, y, v = self(i, lat)
                if v:
                    seg.append((x, y))
                elif seg:
                    if len(seg) > 1:
                        out.append(seg)
                    seg = []
            if len(seg) > 1:
                out.append(seg)
        return ["M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in s) for s in out]


# ---------------------------------------------------------------- type
_FONTS = {}

def _font(path):
    if path not in _FONTS:
        f = TTFont(path)
        _FONTS[path] = (f, f.getGlyphSet(), f["cmap"].getBestCmap(),
                        f["head"].unitsPerEm, f["hmtx"])
    return _FONTS[path]


def text_path(text, font_path, size, x, y, anchor="middle", tracking=0.0):
    """Outline `text` as a single SVG path `d`. y = baseline. tracking in em."""
    font, gs, cmap, upem, hmtx = _font(font_path)
    scale = size / upem
    names, adv = [], 0.0
    for ch in text:
        gn = cmap.get(ord(ch))
        if gn is None:
            gn = cmap.get(ord(" "))
        names.append(gn)
        adv += hmtx[gn][0] * scale + tracking * size
    if tracking:
        adv -= tracking * size
    if anchor == "middle":
        pen_x = x - adv / 2
    elif anchor == "end":
        pen_x = x - adv
    else:
        pen_x = x
    d = []
    for gn in names:
        pen = SVGPathPen(gs)
        gs[gn].draw(pen)
        seg = pen.getCommands()
        if seg:
            d.append(f'<g transform="translate({pen_x:.2f},{y:.2f}) '
                     f'scale({scale:.5f},{-scale:.5f})"><path d="{seg}"/></g>')
        pen_x += hmtx[gn][0] * scale + tracking * size
    return "".join(d), adv


def text_width(text, font_path, size, tracking=0.0):
    font, gs, cmap, upem, hmtx = _font(font_path)
    scale = size / upem
    w = 0.0
    for ch in text:
        gn = cmap.get(ord(ch)) or cmap.get(ord(" "))
        w += hmtx[gn][0] * scale + tracking * size
    return w - (tracking * size if tracking else 0)


# ---------------------------------------------------------------- misc
def arc(cx, cy, r, a0, a1):
    """SVG arc path between two angles (degrees, 0 = east, clockwise on screen)."""
    x0 = cx + r * math.cos(math.radians(a0)); y0 = cy + r * math.sin(math.radians(a0))
    x1 = cx + r * math.cos(math.radians(a1)); y1 = cy + r * math.sin(math.radians(a1))
    large = 1 if abs(a1 - a0) > 180 else 0
    sweep = 1 if a1 > a0 else 0
    return f"M{x0:.2f},{y0:.2f} A{r},{r} 0 {large} {sweep} {x1:.2f},{y1:.2f}"


def data_uri(path):
    with open(path, "rb") as fh:
        return "data:image/png;base64," + base64.b64encode(fh.read()).decode()
