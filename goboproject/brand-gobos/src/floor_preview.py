#!/usr/bin/env python3
"""Show each gobo as projected light on a real floor, for scale and feel.

Uses the cleaned entrance plate from the CEC FSC project (same photo with
its floor sticker already removed) purely as a convenient real surface --
the gobos themselves are not tied to that location.
"""
import io
import os
import numpy as np
import cv2
import cairosvg

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "..", "artwork")
PLATE = os.path.join(HERE, "..", "..", "cec-fsc-digital-day", "reference",
                     "entrance-sticker-removed.png")
QUAD = [(247 - 18, 384 - 28), (548 - 18, 384 - 28),
        (559.5 - 18, 502 - 28), (235.5 - 18, 502 - 28)]   # plate is the cropped panel
K = 3


def project(plate, svg, strength=0.95, bloom=0.4):
    H, W = plate.shape[:2]
    png = cairosvg.svg2png(url=svg, output_width=1600, output_height=1600)
    art = cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_COLOR).astype(np.float32) / 255
    s = art.shape[0]
    src = np.float32([[0, 0], [s, 0], [s, s], [0, s]])
    dst = np.float32([(x * K, y * K) for x, y in QUAD])
    M = cv2.getPerspectiveTransform(src, dst)
    big = cv2.resize(plate, None, fx=K, fy=K, interpolation=cv2.INTER_LANCZOS4)
    beam = cv2.warpPerspective(art, M, (W * K, H * K), flags=cv2.INTER_AREA)
    beam = cv2.resize(beam, (W, H), interpolation=cv2.INTER_AREA)
    glow = cv2.GaussianBlur(beam, (0, 0), 5)
    light = np.clip(beam * strength + glow * bloom, 0, 1)
    base = plate.astype(np.float32) / 255
    return (np.clip(1 - (1 - base) * (1 - light), 0, 1) * 255).astype(np.uint8)


if __name__ == "__main__":
    plate = cv2.imread(PLATE)
    for n in ("gobo-syspex", "gobo-sysguard"):
        out = project(plate, os.path.join(ART, n + ".svg"))
        out = out[300:486, 120:640]      # crop to the floor, not the venue
        out = cv2.resize(out, (1400, round(1400 * out.shape[0] / out.shape[1])),
                         interpolation=cv2.INTER_LANCZOS4)
        p = os.path.join(ART, n + "-floor-preview.jpg")
        cv2.imwrite(p, out, [cv2.IMWRITE_JPEG_QUALITY, 93])
        print("wrote", p)
