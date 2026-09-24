"""Pull the real letterforms and marks out of the approved logo PNGs.

Kevin asked the gobo type to follow the logo's own font. Rather than hunt
for a lookalike typeface, this takes the actual glyphs straight out of the
approved logo artwork: isolate the wordmark, split it at the gaps between
letters, and trace each letter's outline to an SVG path. Letter widths and
the spaces between them come from the logo itself, so the word keeps its
real proportions when it is bent around the gobo's ring.

Counters (the holes in P, R, A, D and the grooves inside the Syspex
letters) come back as separate contours and are drawn with
fill-rule="evenodd", so they stay open.
"""
import os
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "..", "reference")


def _load(path):
    im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if im.shape[2] == 4:
        bgr, a = im[..., :3].astype(float), im[..., 3].astype(float) / 255
    else:
        bgr, a = im.astype(float), np.ones(im.shape[:2])
    return bgr, a


def trace(mask, scale=4, eps_src=0.28):
    """Trace a boolean mask to SVG path data, in the mask's own pixel coords.

    The mask is upscaled smoothly before thresholding so the traced edge
    follows the artwork's anti-aliased edge rather than its pixel stairs.
    """
    m = cv2.GaussianBlur(mask.astype(np.float32), (0, 0), 0.6)
    up = cv2.resize(m, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    up = (up > 0.5).astype(np.uint8) * 255
    cnts, _ = cv2.findContours(up, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in cnts:
        if cv2.contourArea(c) < (3 * scale) ** 2:
            continue
        c = cv2.approxPolyDP(c, eps_src * scale, True)
        if len(c) < 3:
            continue
        pts = c.reshape(-1, 2) / scale
        out.append("M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts) + " Z")
    return " ".join(out)


def split_letters(mask, min_gap=2):
    """Column ranges of each letter, from the gaps in the vertical profile."""
    cols = mask.any(0)
    spans, start = [], None
    for x, on in enumerate(cols):
        if on and start is None:
            start = x
        elif not on and start is not None:
            spans.append((start, x))
            start = None
    if start is not None:
        spans.append((start, len(cols)))
    # merge spans separated by less than min_gap (e.g. a split serif)
    merged = [spans[0]]
    for s, e in spans[1:]:
        if s - merged[-1][1] < min_gap:
            merged[-1] = (merged[-1][0], e)
        else:
            merged.append((s, e))
    return merged


def wordmark(png, row, white_only=True, expect=None):
    """Trace a wordmark, letter by letter.

    Returns dict with per-letter path data plus the metrics needed to set
    the word on an arc: each letter's x-centre, and the word's overall
    width and baseline, all in the source artwork's pixels.
    """
    bgr, a = _load(os.path.join(REF, png))
    b, g, r = bgr[..., 0], bgr[..., 1], bgr[..., 2]
    if white_only:
        m = (a > .5) & (b > 150) & (g > 150) & (r > 150)
    else:
        m = a > .5
    y0, y1, x0, x1 = row
    box = np.zeros_like(m); box[y0:y1, x0:x1] = True
    m = m & box
    spans = split_letters(m)
    if expect and len(spans) != expect:
        raise SystemExit(f"{png}: found {len(spans)} letters, expected {expect}: {spans}")
    ys = np.nonzero(m.any(1))[0]
    baseline, top = ys.max() + 1, ys.min()
    letters = []
    for s, e in spans:
        sub = np.zeros_like(m); sub[:, s:e] = m[:, s:e]
        letters.append(dict(path=trace(sub), x0=s, x1=e, cx=(s + e) / 2))
    return dict(letters=letters, baseline=float(baseline), top=float(top),
                width=float(spans[-1][1] - spans[0][0]),
                left=float(spans[0][0]), right=float(spans[-1][1]),
                cap=float(baseline - top))


def mark(png, colour, box=None):
    """Trace a coloured mark (the Syspex tile, the SysGuard helmet)."""
    bgr, a = _load(os.path.join(REF, png))
    b, g, r = bgr[..., 0], bgr[..., 1], bgr[..., 2]
    if colour == "teal":
        m = (a > .5) & (g > 90) & (b > 90) & (g - r > 40)
    elif colour == "yellow":
        m = (a > .5) & (r > 120) & (g > 120) & (b < 120) & (g - b > 60)
    if box:
        y0, y1, x0, x1 = box
        k = np.zeros_like(m); k[y0:y1, x0:x1] = True
        m &= k
    ys, xs = np.nonzero(m)
    return dict(path=trace(m), x0=float(xs.min()), x1=float(xs.max() + 1),
                y0=float(ys.min()), y1=float(ys.max() + 1))


def solid_mark(png, box):
    """Trace a mark as its silhouette, ignoring internal colour splits."""
    bgr, a = _load(os.path.join(REF, png))
    y0, y1, x0, x1 = box
    m = np.zeros(a.shape, bool)
    m[y0:y1, x0:x1] = a[y0:y1, x0:x1] > .5
    ys, xs = np.nonzero(m)
    return dict(path=trace(m), x0=float(xs.min()), x1=float(xs.max() + 1),
                y0=float(ys.min()), y1=float(ys.max() + 1))


if __name__ == "__main__":
    for png in ("logo-syspex-white.png", "logo-sysguard-white.png"):
        bgr, a = _load(os.path.join(REF, png))
        print(png, "size", a.shape)
        b, g, r = bgr[..., 0], bgr[..., 1], bgr[..., 2]
        w = (a > .5) & (b > 150) & (g > 150) & (r > 150)
        rows = np.nonzero(w.any(1))[0]
        print("  white rows", rows.min(), rows.max())
        prof = w.any(1).astype(int)
        runs, st = [], None
        for y, on in enumerate(prof):
            if on and st is None: st = y
            elif not on and st is not None: runs.append((st, y)); st = None
        if st is not None: runs.append((st, len(prof)))
        print("  white row bands", runs)
        cols = np.nonzero(w.any(0))[0]
        print("  white cols", cols.min(), cols.max())
