#!/usr/bin/env python3
"""Put the gobo artwork on the real entrance photo as projected light.

1. Remove the existing floor sticker completely, rebuilding the concrete:
   shading comes from the surrounding floor (inpainting), grain comes from
   a clean patch of the same concrete nearby, so the patch isn't a smudge.
2. Add the gobo as light only -- screen-blended over the floor, so the
   concrete shows through and the artwork's dark areas simply add nothing.
   No darkening anywhere: a dark disc under the projection reads as a
   sticker, which is exactly what this is meant to replace.

Input:  ../reference/nestle-entrance-current.webp, ../artwork/gobo-*.svg
Output: ../mockups/mockup-A-fullcolour.png, ../mockups/mockup-B-twocolour.png
"""
import io, os
import numpy as np
import cv2
import cairosvg

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PHOTO = os.path.join(ROOT, "reference", "nestle-entrance-current.webp")

PANEL = (18, 28, 762, 514)        # left photo panel of the reference image
K = 3                             # working upscale for the projection

# the existing sticker, measured off the photo (original pixels)
STICKER_C = (397.5, 442.5)
STICKER_AX = (158, 62)            # a touch past the printed edge, to catch its rim
# pillar bases the sticker nearly touches -- never paint over these
PILLARS = [(140, 0, 244, 441), (546, 0, 640, 441)]
# clean concrete to borrow grain from (either side, below the pillars)
GRAIN = [(60, 455, 240, 514), (556, 452, 640, 514)]
FLOOR_TOP = 374                   # bottom step ends here; above is not floor

# projection footprint: trapezoid the sticker's ellipse sits in (far edge
# slightly narrower -- the floor recedes toward the steps)
QUAD = [(247, 384), (548, 384), (559.5, 502), (235.5, 502)]


def _harmonic_fill(img, hole, wall):
    """Smoothest possible surface matching the real floor all round the
    hole's edge (Laplace equation). Wall pixels (the pillars) act as walls:
    nothing is taken from them, so their navy can't bleed in."""
    from scipy.sparse import lil_matrix
    from scipy.sparse.linalg import spsolve
    ys, xs = np.nonzero(hole)
    idx = -np.ones(hole.shape, np.int64); idx[ys, xs] = np.arange(len(ys))
    n = len(ys)
    A = lil_matrix((n, n)); B = np.zeros((n, 3))
    h, w = hole.shape
    for k, (y, x) in enumerate(zip(ys, xs)):
        deg = 0
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            qy, qx = y + dy, x + dx
            if not (0 <= qy < h and 0 <= qx < w) or wall[qy, qx]:
                continue
            deg += 1
            if hole[qy, qx]:
                A[k, idx[qy, qx]] = -1
            else:
                B[k] += img[qy, qx]
        A[k, k] = deg
    A = A.tocsr()
    out = img.astype(np.float32).copy()
    for ch in range(3):
        out[ys, xs, ch] = spsolve(A, B[:, ch])
    return out


def remove_sticker(img, seed=7):
    h, w = img.shape[:2]
    hole = np.zeros((h, w), np.uint8)
    cv2.ellipse(hole, (int(STICKER_C[0]), int(STICKER_C[1])), STICKER_AX, 0, 0, 360, 255, -1)
    wall = np.zeros((h, w), bool)
    for x0, y0, x1, y1 in PILLARS:
        wall[y0:y1, x0:x1] = True
    hole = (hole > 0) & ~wall

    smooth = _harmonic_fill(img, hole, wall)

    # texture: random overlapping patches of real concrete detail (stains,
    # blotches, grain) from clean floor nearby, laid over the smooth fill.
    # Large patches + no mirroring/tiling, so nothing visibly repeats.
    rng = np.random.default_rng(seed)
    srcs = []
    for x0, y0, x1, y1 in GRAIN:
        r = img[y0:y1, x0:x1].astype(np.float32)
        srcs.append(r - cv2.GaussianBlur(r, (0, 0), 9))
    P = 44
    win = np.outer(np.hanning(P), np.hanning(P))[..., None].astype(np.float32) + 1e-3
    acc = np.zeros((h, w, 3), np.float32); wsum = np.zeros((h, w, 1), np.float32)
    ys, xs = np.nonzero(hole)
    for yy in range(ys.min() - P, ys.max() + P, P // 3):
        for xx in range(xs.min() - P, xs.max() + P, P // 3):
            src = srcs[rng.integers(len(srcs))]
            sy = rng.integers(0, src.shape[0] - P); sx = rng.integers(0, src.shape[1] - P)
            patch = src[sy:sy + P, sx:sx + P]
            y0c, x0c, y1c, x1c = max(yy, 0), max(xx, 0), min(yy + P, h), min(xx + P, w)
            if y1c <= y0c or x1c <= x0c:
                continue
            py, px = y0c - yy, x0c - xx
            sl = (slice(py, py + y1c - y0c), slice(px, px + x1c - x0c))
            acc[y0c:y1c, x0c:x1c] += (patch * win)[sl]
            wsum[y0c:y1c, x0c:x1c] += win[sl]
    texture = acc / np.maximum(wsum, 1e-3)
    # the slab under the porch is smoother than the open concrete the
    # texture comes from, so use it at reduced strength
    filled = np.clip(smooth + texture * 0.8, 0, 255)

    soft = cv2.GaussianBlur(hole.astype(np.float32), (0, 0), 1.2)[..., None]
    soft *= (~wall)[..., None]
    return (img * (1 - soft) + filled * soft).astype(np.uint8)


def render(svg, size=1800):
    png = cairosvg.svg2png(url=svg, output_width=size, output_height=size)
    a = cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_COLOR)
    return a.astype(np.float32) / 255


def project(img, svg, strength=0.92, bloom=0.35):
    H, W = img.shape[:2]
    art = render(svg)
    s = art.shape[0]
    src = np.float32([[0, 0], [s, 0], [s, s], [0, s]])
    dst = np.float32([(x * K, y * K) for x, y in QUAD])
    M = cv2.getPerspectiveTransform(src, dst)
    beam = cv2.warpPerspective(art, M, (W, H), flags=cv2.INTER_AREA)
    glow = cv2.GaussianBlur(beam, (0, 0), 4 * K)
    light = np.clip(beam * strength + glow * bloom, 0, 1)
    base = img.astype(np.float32) / 255
    out = 1 - (1 - base) * (1 - light)                   # screen: light only adds
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)


def build(svg_name, out_name):
    photo = cv2.imread(PHOTO)
    clean = remove_sticker(photo)
    big = cv2.resize(clean, None, fx=K, fy=K, interpolation=cv2.INTER_LANCZOS4)
    done = project(big, os.path.join(ROOT, "artwork", svg_name))
    x0, y0, x1, y1 = (v * K for v in PANEL)
    done = done[y0:y1, x0:x1]
    done = cv2.resize(done, (1500, round(1500 * done.shape[0] / done.shape[1])),
                      interpolation=cv2.INTER_AREA)
    out = os.path.join(ROOT, "mockups", out_name)
    cv2.imwrite(out, done)
    return out, clean


if __name__ == "__main__":
    for svg, png in (("gobo-A-fullcolour.svg", "mockup-A-fullcolour.png"),
                     ("gobo-B-twocolour.svg", "mockup-B-twocolour.png")):
        out, clean = build(svg, png)
        print("wrote", out)
    x0, y0, x1, y1 = PANEL
    cv2.imwrite(os.path.join(HERE, "..", "reference", "entrance-sticker-removed.png"), clean[y0:y1, x0:x1])
