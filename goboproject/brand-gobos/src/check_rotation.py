#!/usr/bin/env python3
"""Prove the 'looks right from any angle' requirement.

1. Numerically: how closely the disc reproduces itself when turned. The
   rings, zebra, names and taglines are all 4-fold, so they repeat every
   90 degrees; the centre marks (the Syspex tile, the SysGuard helmets)
   are 180-degree marks, so the disc as a whole repeats every 180. Both
   figures are reported, and the 180 one is the design's real period.
2. Visually: a strip of the gobo at several projector rotations, so the
   worst case (45 degrees, the furthest any name can be from upright) can
   be judged by eye.
"""
import os
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "..", "artwork")
OUT = os.path.join(HERE, "..", "artwork")
NAMES = ("gobo-syspex", "gobo-sysguard")


def rot(img, deg):
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2 - .5, h / 2 - .5), deg, 1.0)
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC,
                          borderMode=cv2.BORDER_CONSTANT, borderValue=(10, 7, 5))


def main():
    for n in NAMES:
        img = cv2.imread(os.path.join(ART, n + "-2000.png"))
        # ignore the very edge, where rotation resampling clips the disc
        m = np.zeros(img.shape[:2], np.uint8)
        cv2.circle(m, (1000, 1000), 930, 255, -1)
        outside = np.zeros(img.shape[:2], np.uint8)
        cv2.circle(outside, (1000, 1000), 930, 255, -1)
        cv2.circle(outside, (1000, 1000), 400, 0, -1)     # frame only, centre mark excluded
        res = []
        for deg, mask, what in ((90, outside, "rings/type only"),
                                (90, m, "whole disc"), (180, m, "whole disc")):
            d = np.abs(rot(img, deg).astype(int) - img.astype(int))[mask > 0]
            res.append(f"{deg:>3}deg {what:<16} {d.mean():5.2f}/255")
        print(f"{n}:")
        for r in res:
            print("   ", r)

        tiles = []
        for deg in (0, 15, 30, 45):
            t = rot(img, deg)
            t = cv2.resize(t, (620, 620), interpolation=cv2.INTER_AREA)
            cv2.putText(t, f"{deg} deg", (18, 44), cv2.FONT_HERSHEY_SIMPLEX,
                        0.9, (255, 255, 255), 2, cv2.LINE_AA)
            tiles.append(t)
        strip = np.hstack(tiles)
        p = os.path.join(OUT, n + "-rotation-test.png")
        cv2.imwrite(p, strip)
        print("   wrote", p)


if __name__ == "__main__":
    main()
