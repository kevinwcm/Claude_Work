"""Remove the old white/yellow zebra from the mockup photo."""
import os
import numpy as np
import cv2
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "reference", "old-zebra-mockup.webp")
OLD = np.array([[332, 1003], [720, 1068], [628, 705], [540, 703]], np.int32)   # old zebra outline


def band_mask(img):
    """The orange-yellow painted walkway band (a wall for the fill). Told
    apart from the old zebra's lemon-yellow bars by hue: the paint's green
    is ~64% of its red, the old bars' ~90%."""
    b, g, r = [img[..., i].astype(np.float32) for i in range(3)]
    m = ((r > 150) & (b < 110) & (g > 70) & (g / (r + 1) < 0.78)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return m > 0


def harmonic_fill(img, hole, wall):
    ys, xs = np.nonzero(hole)
    idx = -np.ones(hole.shape, np.int64); idx[ys, xs] = np.arange(len(ys))
    A = lil_matrix((len(ys), len(ys))); B = np.zeros((len(ys), 3))
    h, w = hole.shape
    for k, (y, x) in enumerate(zip(ys, xs)):
        deg = 0
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            qy, qx = y + dy, x + dx
            if not (0 <= qy < h and 0 <= qx < w) or wall[qy, qx]:
                continue
            deg += 1
            if hole[qy, qx]: A[k, idx[qy, qx]] = -1
            else: B[k] += img[qy, qx]
        A[k, k] = max(deg, 1)
    A = A.tocsr(); out = img.astype(np.float32).copy()
    for ch in range(3):
        out[ys, xs, ch] = spsolve(A, B[:, ch])
    return out


def texture(img, hole, sources, seed=5, P=30, strength=0.55):
    """Random overlapping patches of real floor detail (no tiling)."""
    rng = np.random.default_rng(seed); h, w = hole.shape
    srcs = []
    for x0, y0, x1, y1 in sources:
        r = img[y0:y1, x0:x1].astype(np.float32); srcs.append(r - cv2.GaussianBlur(r, (0, 0), 6))
    win = np.outer(np.hanning(P), np.hanning(P))[..., None].astype(np.float32) + 1e-3
    acc = np.zeros((h, w, 3), np.float32); ws = np.zeros((h, w, 1), np.float32)
    ys, xs = np.nonzero(hole)
    for yy in range(ys.min() - P, ys.max() + P, P // 3):
        for xx in range(xs.min() - P, xs.max() + P, P // 3):
            yy_, xx_ = yy + int(rng.integers(-P // 4, P // 4)), xx + int(rng.integers(-P // 4, P // 4))
            yy, xx = yy_, xx_
            s = srcs[rng.integers(len(srcs))]
            sy = rng.integers(0, s.shape[0] - P); sx = rng.integers(0, s.shape[1] - P)
            p = s[sy:sy + P, sx:sx + P]
            if rng.random() < 0.5: p = p[:, ::-1]
            y0, x0, y1, x1 = max(yy, 0), max(xx, 0), min(yy + P, h), min(xx + P, w)
            if y1 <= y0 or x1 <= x0: continue
            sl = (slice(y0 - yy, y0 - yy + y1 - y0), slice(x0 - xx, x0 - xx + x1 - x0))
            acc[y0:y1, x0:x1] += (p * win)[sl]; ws[y0:y1, x0:x1] += win[sl]
    return acc / np.maximum(ws, 1e-3) * strength


def erase(img):
    hole = np.zeros(img.shape[:2], np.uint8)
    cv2.fillPoly(hole, [OLD], 255)
    hole = cv2.dilate(hole, np.ones((7, 7), np.uint8)) > 0
    wall = band_mask(img)
    hole &= ~wall
    smooth = harmonic_fill(img, hole, wall)
    # clean grey floor to borrow grain from: search for 40x40 blocks of plain
    # concrete that are clear of the old zebra, the painted band and anything
    # that isn't floor (low saturation, mid brightness)
    keep = hole | cv2.dilate(wall.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
    f = img.astype(int); sat = f.max(-1) - f.min(-1); lum = f.mean(-1)
    floorish = (sat < 60) & (lum > 60) & (lum < 200) & ~keep
    sources, S = [], 40
    for y0 in range(700, 1100 - S, 12):
        for x0 in range(180, 725 - S, 12):
            if floorish[y0:y0 + S, x0:x0 + S].all():
                box = (x0, y0, x0 + S, y0 + S)
                if all(abs(box[0] - b[0]) >= S or abs(box[1] - b[1]) >= S for b in sources):
                    sources.append(box)
    print(len(sources), "texture sources found")
    tex = texture(img, hole, sources)
    filled = np.clip(smooth + tex, 0, 255)
    soft = cv2.GaussianBlur(hole.astype(np.float32), (0, 0), 1.0)[..., None]
    return (img * (1 - soft) + filled * soft).astype(np.uint8), hole


if __name__ == "__main__":
    img = cv2.imread(SRC)
    clean, hole = erase(img)
    cv2.imwrite(os.path.join(HERE, "..", "reference", "aisle-old-zebra-removed.png"), clean)
    print("hole px", int(hole.sum()))
