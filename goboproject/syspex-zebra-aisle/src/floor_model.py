"""Floor model for reference/old-zebra-mockup.webp (765x1137).

Vertical VP from the pillar and rack uprights; aisle VP from the painted
band edges and floor lines. Checks: the bollards measure 1.04 m and sit on
one line (w~2.5), and the painted band is a constant 0.72 m wide
(w 1.20-1.92) all along the aisle.
"""
import numpy as np
W_IMG, H_IMG = 765, 1137
c = np.array([W_IMG/2, H_IMG/2])
V = np.array([401.0, -2653.0])        # vertical VP (pillar + rack uprights)
A = np.array([572.0, 636.0])          # aisle VP (painted band edges, floor lines)
f = np.sqrt(-np.dot(V - c, A - c))
K = np.array([[f,0,c[0]],[0,f,c[1]],[0,0,1.0]]); Ki = np.linalg.inv(K)
ray = lambda p: (lambda v: v/np.linalg.norm(v))(Ki @ np.array([p[0], p[1], 1.0]))
up = ray(V);  up = -up if up[1] > 0 else up
r1 = ray(A); r1 -= up*np.dot(r1, up); r1 /= np.linalg.norm(r1)       # along the aisle, away
r2 = np.cross(up, r1); r2 /= np.linalg.norm(r2)                       # lateral (u x w = up)
LAT = (K @ r2)[:2] / (K @ r2)[2]
CAM_H = 1.5
X0 = -CAM_H * up
Hf = K @ np.c_[r1, r2, X0]; Hi = np.linalg.inv(Hf)
def to_img(u, w): p = Hf @ np.array([u, w, 1.0]); return p[:2]/p[2]
def to_floor(x, y): p = Hi @ np.array([x, y, 1.0]); return p[:2]/p[2]
if __name__ == "__main__":
    print(f"f={f:.0f}px  lateral VP=({LAT[0]:.0f},{LAT[1]:.0f})")
