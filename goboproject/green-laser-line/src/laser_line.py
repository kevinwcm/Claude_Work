#!/usr/bin/env python3
"""Add one green laser walkway line to the corridor photo.

Position: on the walkway between the bollard/chain line and the right-hand
wall, 35% of the walkway's width out from the wall. Both edges are lines
through the corridor's vanishing point (616, 1003), found from the pipes,
skirting and window lines, so a fixed fraction between them is a line
truly parallel to the wall. It runs from the bottom of the frame to the
far end of the walkway, where the bollard chain ends.

Rendering: on a floor, image distance below the horizon is proportional to
1/depth, so the line's width is scaled by (y - horizon). A bright core, a
green glow, and a faint wide scatter halo for the glossy epoxy floor are
added as light over the photo.

Input:  ../reference/corridor-original.jpg
Output: ../mockups/corridor-green-laser-line.jpg
"""
import os
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
PHOTO = os.path.join(HERE, "..", "reference", "corridor-original.jpg")
OUT = os.path.join(HERE, "..", "mockups", "corridor-green-laser-line.jpg")

VP = np.array([616.3, 1003.4])       # corridor vanishing point (= horizon height)
WALL_ANGLE = 1.04323                 # wall base (skirting/floor edge) from VP, radians
BOLLARD_ANGLE = 2.17958              # bollard/chain line from VP, radians
FROM_WALL = 0.35                      # fraction of walkway width, measured from the wall
FAR_Y = 1042.0                        # far end of the walkway (end of the bollard chain)
CORE_HALF_W_AT_BOTTOM = 5.5          # px at the bottom edge of the photo


def _x_on(angle, y):
    return VP[0] + (y - VP[1]) / np.tan(angle)


# the laser line: a point near the bottom, FROM_WALL of the way in from the wall
_Y = 1950.0
NEAR = np.array([(1 - FROM_WALL) * _x_on(WALL_ANGLE, _Y) + FROM_WALL * _x_on(BOLLARD_ANGLE, _Y), _Y])
SS = 2                                # supersampling


def main():
    img = cv2.imread(PHOTO).astype(np.float32)
    H, W = img.shape[:2]
    ys, xs = np.mgrid[0:H*SS, 0:W*SS].astype(np.float32) / SS + 0.5 / SS
    d = (NEAR - VP) / np.linalg.norm(NEAR - VP)
    n = np.array([-d[1], d[0]])
    dist = np.abs((xs - VP[0]) * n[0] + (ys - VP[1]) * n[1])      # px from the line's axis
    depth_scale = np.clip((ys - VP[1]) / (H - VP[1]), 0, None)    # 1 at bottom, 0 at horizon
    hw = CORE_HALF_W_AT_BOTTOM * depth_scale + 0.5
    core = np.clip(1.5 - dist / hw, 0, 1) ** 1.2                  # anti-aliased solid core
    glow = np.exp(-(dist / (hw * 2.2 + 1.2)) ** 2)
    halo = np.exp(-(dist / (hw * 7 + 4)) ** 2)
    # soft start at the far end, running off the bottom of the frame
    extent = np.clip((ys - FAR_Y) / 6.0, 0, 1)
    core, glow, halo = (a * extent for a in (core, glow, halo))
    down = lambda a: cv2.resize(a, (W, H), interpolation=cv2.INTER_AREA)
    core, glow, halo = down(core), down(glow), down(halo)

    # a laser is intense enough to read as clean green even on red epoxy, so
    # the core *replaces* the floor colour; glow and scatter add light around it
    green_core = np.array([150, 255, 130], np.float32)   # BGR: bright centre, slightly whitened
    green = np.array([60, 255, 25], np.float32)          # BGR: laser green
    c = core[..., None]
    base = img * (1 - c) + green_core * c
    add = glow[..., None] * green * 0.55 * (1 - c) + halo[..., None] * green * 0.14
    add = add - (glow[..., None] * 0.35 * (1 - c)) * img * np.array([0.2, 0, 1.0])   # glow eats a little red
    lit = base + add
    add = add + (base - img)
    # keep the core from clipping to a flat block: roll off highlights, but
    # only where the laser adds light -- the rest of the photo is untouched
    T = 205.0
    roll = np.where(lit > T, T + (255 - T) * (1 - np.exp(-(lit - T) / (255 - T))), lit)
    wgt = np.clip(add.sum(-1, keepdims=True) / 30.0, 0, 1)
    out = img * (1 - wgt) + roll * wgt
    cv2.imwrite(OUT, np.clip(out, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 93])
    print("wrote", OUT)


if __name__ == "__main__":
    main()
