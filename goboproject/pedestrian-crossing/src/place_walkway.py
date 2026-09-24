"""Project the Pedestrian Crossing gobo onto the warehouse floor photo in
true perspective, at the artwork's exact proportions, as projected light.

Input:  ../reference/warehouse-original.jpg, ../artwork/pedestrian-crossing.svg
Output: ../mockups/warehouse-walkway-mockup.jpg
Floor geometry comes from floor_model.py.
"""
import os
import numpy as np, cv2, cairosvg
from floor_model import to_img

HERE = os.path.dirname(os.path.abspath(__file__))
SVG = os.path.join(HERE, "..", "artwork", "pedestrian-crossing.svg")
PHOTO = os.path.join(HERE, "..", "reference", "warehouse-original.jpg")
OUT = os.path.join(HERE, "..", "mockups", "warehouse-walkway-mockup.jpg")
AX0, AX1 = 170.2, 2079.8                 # artwork aperture box (pt), same as build.py
AY0, AY1 = 731.2, 1518.8
RATIO = (AX1 - AX0) / (AY1 - AY0)

# footprint on the floor (metres): spans the cross-aisle from just in front
# of the right-hand rack end (u=1.9) to just short of the centre-block
# row-end bollards (u=6.1); width follows from the artwork's own ratio.
U0, U1, WC = 1.9, 6.1, 5.0
L = U1 - U0; W = L / RATIO
W0, W1 = WC - W/2, WC + W/2

SS = 2                                   # supersample factor
def render_art(scale=1.6):
    png = cairosvg.svg2png(url=SVG, scale=scale)
    a = cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_UNCHANGED)   # BGRA
    x0, x1 = int(round(AX0*scale)), int(round(AX1*scale))
    y0, y1 = int(round(AY0*scale)), int(round(AY1*scale))
    a = a[y0:y1, x0:x1].astype(np.float32) / 255.0
    b, g, r, al = a[...,0], a[...,1], a[...,2], a[...,3]
    lit = al * np.clip((g - b) / 0.95, 0, 1)   # yellow = lit, black text / empty = unlit
    return lit

def main(out_path=OUT, gain=1.9, light=(1.0, 0.92, 0.28)):
    img = cv2.imread(PHOTO).astype(np.float32)
    H, Wd = img.shape[:2]
    lit = render_art()
    ah, aw = lit.shape
    # orientation: artwork X -> +u (near->far), artwork Y -> -w, which is the
    # non-mirrored mapping; the normally-reading band ends up on the camera side
    src = np.float32([[0,0],[aw,0],[aw,ah],[0,ah]])
    dst = np.float32([to_img(U0,W1), to_img(U1,W1), to_img(U1,W0), to_img(U0,W0)]) * SS
    M = cv2.getPerspectiveTransform(src, dst)
    big = cv2.warpPerspective(lit, M, (Wd*SS, H*SS), flags=cv2.INTER_AREA)
    mask = cv2.resize(big, (Wd, H), interpolation=cv2.INTER_AREA)
    mask = cv2.GaussianBlur(mask, (0,0), 0.6)            # slight gobo softness

    # foreground occluders at the near end (bollard, worker, upright, railing):
    # everything right of the front bollard's left edge in that band
    occ = np.zeros((H, Wd), np.uint8)
    cv2.fillPoly(occ, [np.int32([[1483,840],[1760,840],[1760,1125],[1490,1125],[1489,1012]])], 255)
    occ = cv2.GaussianBlur(occ.astype(np.float32)/255, (0,0), 0.8)
    mask *= (1 - occ)

    col = np.array(light[::-1], np.float32)             # BGR
    lightmap = mask[...,None] * col
    out = img * (1 + gain * lightmap)                   # light reflected by the floor's own texture
    bloom = cv2.GaussianBlur(mask, (0,0), 6)[...,None] * col * 38
    out = out + bloom
    out = np.clip(out, 0, 255).astype(np.uint8)
    cv2.imwrite(out_path, out, [cv2.IMWRITE_JPEG_QUALITY, 93])
    return dst / SS

if __name__ == "__main__":
    print(f"walkway {L:.2f} m x {W:.2f} m (ratio {RATIO:.3f})")
    print(np.round(main(), 1))
