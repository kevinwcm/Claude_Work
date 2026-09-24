#!/usr/bin/env python3
"""Replace the blue LED zebra-crossing fixture in a warehouse photo with our
Pedestrian Crossing gobo, projected onto the same patch of floor as
projected light (floor dimmed, artwork added back as a glow).

Input:  ../reference/warehouse-aisle-original.png
Output: ../mockups/warehouse-aisle-mockup.png
"""
import io, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import cairosvg

HERE = os.path.dirname(os.path.abspath(__file__))
SVG = os.path.join(HERE, "..", "artwork", "pedestrian-crossing.svg")
SRC_PHOTO = os.path.join(HERE, "..", "reference", "warehouse-aisle-original.png")
OUT_PHOTO = os.path.join(HERE, "..", "mockups", "warehouse-aisle-mockup.png")

# quad corners of the existing crossing in img3.png (pixel space), matched so
# that moving artwork-TL->TR (its WIDTH axis, where the 7 stripes repeat)
# tracks the photo's long/receding axis (the walking direction), and
# artwork-TL->BL (its HEIGHT axis) tracks the photo's short axis (crossing
# width) at the far end.

# The blue LED end-caps mark the crossing's two short ends, but the white
# zebra stripes actually run a bit wider than those accent strips -- expand
# 20% outward along each end's own axis so the new artwork's edges land on
# the true stripe extent rather than the narrower LED bar.
def _expand(a, b, factor=0.20):
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    hx, hy = (b[0] - a[0]) / 2 * (1 + factor), (b[1] - a[1]) / 2 * (1 + factor)
    return (mx - hx, my - hy), (mx + hx, my + hy)


FAR_LEFT, FAR_RIGHT = _expand((137.0, 943.0), (270.0, 924.0))
NEAR_LEFT, NEAR_RIGHT = _expand((505.0, 1096.0), (655.0, 1059.0))

DST = [FAR_LEFT, NEAR_LEFT, NEAR_RIGHT, FAR_RIGHT]   # artwork TL, TR, BR, BL in that order


def find_coeffs(dst, src):
    A, B = [], []
    for (xd, yd), (xs, ys) in zip(dst, src):
        A.append([xd, yd, 1, 0, 0, 0, -xs * xd, -xs * yd])
        A.append([0, 0, 0, xd, yd, 1, -ys * xd, -ys * yd])
        B += [xs, ys]
    res = np.linalg.solve(np.array(A, float), np.array(B, float))
    return res.tolist()


def erase_crossing(img, K):
    """Paint out the old blue/white crossing with plausible bare concrete,
    borrowing texture from the floor just to the left of it (same lighting,
    same material, no crossing)."""
    xs = [p[0] * K for p in DST]; ys = [p[1] * K for p in DST]
    x0, x1 = min(xs), max(xs); y0, y1 = min(ys), max(ys)
    pad = 26 * K
    bx0, by0, bx1, by1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
    w, h = int(bx1 - bx0), int(by1 - by0)

    # source patch: same size, shifted DOWN onto clean open floor just in
    # front of the crossing (shifting left would clip the rack leg and
    # bollard base visible to that side)
    shift = h + 20 * K
    src_box = (int(bx0), int(by0 + shift), int(bx0) + w, int(by0 + shift) + h)
    img_w, img_h = img.size
    if src_box[3] > img_h:
        off = src_box[3] - img_h
        src_box = (src_box[0], src_box[1] - off, src_box[2], img_h)
    src_box = tuple(max(0, v) for v in src_box)
    patch = img.crop(src_box).resize((w, h))
    patch = patch.filter(ImageFilter.GaussianBlur(1.2 * K))

    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    poly = [(x - bx0, y - by0) for x, y in zip(xs, ys)]
    infl = []
    cx = sum(p[0] for p in poly) / 4; cy = sum(p[1] for p in poly) / 4
    for x, y in poly:
        infl.append((x + (x - cx) * 0.28, y + (y - cy) * 0.28))
    d.polygon(infl, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(6 * K))

    out = img.copy()
    out.paste(patch, (int(bx0), int(by0)), mask)
    return out


def project(img, K, dim=0.30, gain=1.0):
    W, H = img.size
    png = cairosvg.svg2png(url=SVG, output_width=1800, output_height=1800)
    art = Image.open(io.BytesIO(png)).convert("RGB")

    dst = [(x * K, y * K) for x, y in DST]
    src = [(0, 0), (art.width, 0), (art.width, art.height), (0, art.height)]
    coeffs = find_coeffs(dst, src)
    beam = art.transform((W, H), Image.PERSPECTIVE, coeffs, Image.BICUBIC, fillcolor=(0, 0, 0))

    pool = Image.new("L", (W, H), 0)
    cx = sum(p[0] for p in dst) / 4; cy = sum(p[1] for p in dst) / 4
    rx = max(abs(p[0] - cx) for p in dst) * 1.35
    ry = max(abs(p[1] - cy) for p in dst) * 1.35
    ImageDraw.Draw(pool).ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=255)
    pool = pool.filter(ImageFilter.GaussianBlur(22 * K))
    darker = Image.eval(img, lambda v: int(v * (1 - dim)))
    img = Image.composite(darker, img, pool)

    glow = beam.filter(ImageFilter.GaussianBlur(7 * K))
    img = ImageChops.add(img, Image.eval(glow, lambda v: int(v * 0.35)))
    img = ImageChops.add(img, Image.eval(beam, lambda v: min(255, int(v * gain))))
    return img


if __name__ == "__main__":
    K = 3
    base = Image.open(SRC_PHOTO).convert("RGB")
    big = base.resize((base.width * K, base.height * K), Image.LANCZOS)

    cleaned = erase_crossing(big, K)
    done = project(cleaned, K)
    done = done.resize(base.size, Image.LANCZOS)

    # keep the red arrow / ceiling / racking above the floor line untouched
    # -- restore rows above the crossing's topmost point straight from the
    # source (numpy slice, not a per-pixel loop).
    top_guard = int(min(FAR_LEFT[1], FAR_RIGHT[1]) - 30)
    if top_guard > 0:
        a_done = np.array(done); a_src = np.array(base)
        a_done[:top_guard, :, :] = a_src[:top_guard, :, :]
        done = Image.fromarray(a_done)

    done.save(OUT_PHOTO)
    print("saved", OUT_PHOTO, done.size)
