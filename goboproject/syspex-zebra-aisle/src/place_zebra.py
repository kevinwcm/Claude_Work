#!/usr/bin/env python3
"""Project the "Powered by Syspex / Secured by SysGuard" zebra onto the aisle
floor, in true perspective at its real 5.8 m x 2.4 m size.

Placement: bars repeat along the aisle (like the old zebra), and the 2.4 m
width is centred on the painted band's aisle-side edge (w = 1.20 m), so
half the projection lies on the yellow paint and half on the grey floor.

Input:  ../reference/aisle-old-zebra-removed.png  (from erase_old_zebra.py)
        ../reference/powered-by-syspex.pdf        (page 1 = the design)
Output: ../mockups/aisle-syspex-zebra-mockup.jpg
"""
import os
import numpy as np
import cv2
import fitz
from floor_model import to_img

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..", "reference", "aisle-old-zebra-removed.png")
PDF = os.path.join(HERE, "..", "reference", "powered-by-syspex.pdf")
OUT = os.path.join(HERE, "..", "mockups", "aisle-syspex-zebra-mockup.jpg")

BOX = (170.2, 731.2, 2079.8, 1518.8)       # design extent in the PDF (pt)
LEN, WID = 5.8, 2.4                          # metres, from the PDF's dimension callouts
U0 = 2.0                                     # near end, metres along the aisle
W_CENTRE = 1.20                              # painted band's aisle-side edge
SS = 3


def design(scale=2.0):
    page = fitz.open(PDF)[0]
    x0, y0, x1, y1 = BOX
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale),
                          clip=fitz.Rect(x0, y0, x1, y1), alpha=False)
    a = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w, 3)[..., ::-1].astype(np.float32) / 255
    # the PDF page is white where nothing is drawn; only the bars and bands
    # are light. Build a light mask from the drawn shapes: anything inside
    # the bars/bands that isn't the black text or outlines.
    lum = a.mean(-1)
    shapes = np.zeros(lum.shape, np.uint8)
    for d in page.get_drawings():
        f = d.get("fill")
        if f in ((1.0, 0.9490000009536743, 0.0), (1.0, 1.0, 1.0)) and d["rect"].width < 2000:
            r = d["rect"]
            cv2.rectangle(shapes, (int((r.x0 - x0) * scale), int((r.y0 - y0) * scale)),
                          (int((r.x1 - x0) * scale), int((r.y1 - y0) * scale)), 255, -1)
    light = (shapes > 0) & (lum > 0.35)                 # excludes black text and outlines
    col = a * light[..., None]
    return col


def main():
    img = cv2.imread(BASE).astype(np.float32)
    H, W = img.shape[:2]
    art = design()
    ah, aw = art.shape[:2]
    w0, w1 = W_CENTRE - WID / 2, W_CENTRE + WID / 2
    # design x -> along the aisle (u), design y -> lateral (-w): not mirrored
    dst = np.float32([to_img(U0, w1), to_img(U0 + LEN, w1),
                      to_img(U0 + LEN, w0), to_img(U0, w0)]) * SS
    src = np.float32([[0, 0], [aw, 0], [aw, ah], [0, ah]])
    M = cv2.getPerspectiveTransform(src, dst)
    beam = cv2.warpPerspective(art, M, (W * SS, H * SS), flags=cv2.INTER_AREA)
    beam = cv2.resize(beam, (W, H), interpolation=cv2.INTER_AREA)
    beam = cv2.GaussianBlur(beam, (0, 0), 0.6)

    # projected light: brightens what's under it (floor texture shows
    # through), plus a little direct light and a soft bloom
    lit = img * (1 + 1.25 * beam) + 95 * beam
    lit += cv2.GaussianBlur(beam, (0, 0), 5) * 30
    T = 215.0
    lit = np.where(lit > T, T + (255 - T) * (1 - np.exp(-(lit - T) / (255 - T))), lit)
    # keep the photo's feathered white frame on top
    frame = cv2.imread(os.path.join(HERE, "..", "reference", "old-zebra-mockup.webp")).astype(np.float32)
    whiteness = np.clip((frame.min(-1) - 225) / 25, 0, 1)
    edge = np.zeros((H, W), np.float32); edge[:] = 1
    edge[45:H - 45, 45:W - 45] = 0                  # only the feathered border, never the floor
    whiteness = (whiteness * cv2.GaussianBlur(edge, (0, 0), 15))[..., None]
    out = lit * (1 - whiteness) + frame * whiteness
    cv2.imwrite(OUT, np.clip(out, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 94])
    print("wrote", OUT)


if __name__ == "__main__":
    main()
