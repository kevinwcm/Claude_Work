"""Floor-plane camera model for reference/warehouse-original.jpg (2000x1125).

Vanishing points were found by RANSAC over detected line segments; the
lateral one is derived (not measured) because the ultra-wide lens bends the
ceiling lines it would otherwise come from. Checked against the scene: the
four row-end bollards land at the same depth (6.3 m +/- 0.2), the painted
dashes fall on one line, and both workers measure 1.73-1.75 m.
World floor coords (u, w) in metres: u along the building's long axis
(VP H1, rack-row direction), w lateral (VP H2). Camera height CAM_H."""
import numpy as np
W_IMG, H_IMG = 2000, 1125
c = np.array([W_IMG/2, H_IMG/2])
V  = np.array([884.0, -4378.0])      # vertical VP (RANSAC on uprights)
H1 = np.array([453.0, 700.0])        # long-axis VP (RANSAC, 161 segments)
# focal length from V _|_ H1 with principal point at centre
f = np.sqrt(-np.dot(V - c, H1 - c))
K = np.array([[f,0,c[0]],[0,f,c[1]],[0,0,1]])
Ki = np.linalg.inv(K)
def ray(p): v = Ki @ np.array([p[0],p[1],1.0]); return v/np.linalg.norm(v)
up = ray(V)                          # points to the upward vanishing direction
if up[1] > 0: up = -up               # image y grows downward; up has negative y
r1 = ray(H1); r1 -= up*np.dot(r1,up); r1 /= np.linalg.norm(r1)
r2 = np.cross(up, r1); r2 /= np.linalg.norm(r2)
if np.dot(K @ r2, [0,0,1]) < 0: r2 = -r2
H2 = (K @ r2)[:2] / (K @ r2)[2]
CAM_H = 1.50
X0 = -CAM_H * up                     # floor point directly below the camera
Hfloor = K @ np.c_[r1, r2, X0]       # (u,w,1) -> image
Hinv = np.linalg.inv(Hfloor)
def to_img(u, w):
    p = Hfloor @ np.array([u, w, 1.0]); return p[:2]/p[2]
def to_floor(x, y):
    p = Hinv @ np.array([x, y, 1.0]); return p[:2]/p[2]
if __name__ == "__main__":
    print(f"f={f:.1f}px  H2(derived)=({H2[0]:.0f},{H2[1]:.0f})  r1.r2={np.dot(r1,r2):.4f}")
