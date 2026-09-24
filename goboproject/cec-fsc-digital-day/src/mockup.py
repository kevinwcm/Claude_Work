#!/usr/bin/env python3
"""Drop the gobo artwork onto the real entrance photo, as projected light."""
import io, os, sys, random
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import numpy as np
import cairosvg

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
PHOTO = os.path.join(os.path.dirname(HERE), "..", "images", "1.webp")
PHOTO = os.path.abspath(PHOTO)

K = 3                                   # upscale factor for the mockup
# sticker footprint in original-photo pixels
QUAD = [(258, 382), (511, 382), (525, 493), (243, 493)]
ELL = (244, 380, 525, 495)              # bbox of the existing sticker
PANEL = (18, 28, 762, 514)              # left photo panel


def find_coeffs(dst, src):
    """Coefficients mapping OUTPUT quad -> INPUT quad (what PIL wants)."""
    A, B = [], []
    for (xd, yd), (xs, ys) in zip(dst, src):
        A.append([xd, yd, 1, 0, 0, 0, -xs * xd, -xs * yd])
        A.append([0, 0, 0, xd, yd, 1, -ys * xd, -ys * yd])
        B += [xs, ys]
    res = np.linalg.solve(np.array(A, float), np.array(B, float))
    return res.tolist()


def erase_sticker(img):
    """Paint the old floor sticker out with plausible concrete."""
    x0, y0, x1, y1 = [v * K for v in ELL]
    pad = 26 * K
    ring = img.crop((x0 - pad, y0 - pad, x1 + pad, y1 + pad))
    base = tuple(int(c) for c in np.array(ring).reshape(-1, 3).mean(0))

    w, h = x1 - x0 + 2 * pad, y1 - y0 + 2 * pad
    noise = (np.random.normal(0, 7, (h, w, 1)).repeat(3, 2)
             + np.array(base, float))
    patch = Image.fromarray(np.clip(noise, 0, 255).astype("uint8"))
    # borrow the real floor's large-scale shading so it is not a flat disc
    patch = Image.blend(patch, ring.filter(ImageFilter.GaussianBlur(28 * K)), 0.55)

    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).ellipse((pad - 8 * K, pad - 8 * K, w - pad + 8 * K,
                                  h - pad + 8 * K), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(9 * K))
    img.paste(patch, (x0 - pad, y0 - pad), mask)
    return img


def project(img, svg_path, dim=0.42, gain=1.0):
    """Composite the gobo as added light, with the floor dimmed like an event."""
    W, H = img.size
    png = cairosvg.svg2png(url=svg_path, output_width=1800, output_height=1800)
    art = Image.open(io.BytesIO(png)).convert("RGB")

    dst = [(x * K, y * K) for x, y in QUAD]
    src = [(0, 0), (art.width, 0), (art.width, art.height), (0, art.height)]
    coeffs = find_coeffs(dst, src)
    beam = art.transform((W, H), Image.PERSPECTIVE, coeffs,
                         Image.BICUBIC, fillcolor=(0, 0, 0))

    # dim the floor inside a generous pool so the beam reads as light
    pool = Image.new("L", (W, H), 0)
    cx = sum(p[0] for p in dst) / 4; cy = sum(p[1] for p in dst) / 4
    rx = (dst[2][0] - dst[3][0]) * 0.95; ry = (dst[3][1] - dst[0][1]) * 1.45
    ImageDraw.Draw(pool).ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=255)
    pool = pool.filter(ImageFilter.GaussianBlur(40 * K))
    darker = Image.eval(img, lambda v: int(v * (1 - dim)))
    img = Image.composite(darker, img, pool)

    glow = beam.filter(ImageFilter.GaussianBlur(16 * K))
    img = ImageChops.add(img, Image.eval(glow, lambda v: int(v * 0.38)))
    img = ImageChops.add(img, Image.eval(beam, lambda v: min(255, int(v * gain))))
    return img


if __name__ == "__main__":
    random.seed(7); np.random.seed(7)
    base = Image.open(PHOTO).convert("RGB")
    base = base.resize((base.width * K, base.height * K), Image.LANCZOS)
    for name in ("gobo-A-fullcolour", "gobo-B-twocolour"):
        img = erase_sticker(base.copy())
        img = project(img, os.path.join(OUT, name + ".svg"))
        img = img.crop(tuple(v * K for v in PANEL))
        img = img.resize((1500, round(1500 * img.height / img.width)), Image.LANCZOS)
        p = os.path.join(OUT, f"mockup-{name[5:]}.png")
        img.save(p)
        print("wrote", p, img.size)
