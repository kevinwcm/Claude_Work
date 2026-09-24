# Syspex & SysGuard round brand gobos

Two new round gobos, one per brand, designed so the projection reads
correctly however the projector is rotated or aligned.

| File | What it is |
|---|---|
| `artwork/gobo-syspex.svg` / `gobo-sysguard.svg` | Production masters (vector) |
| `artwork/*-2000.png` | 2000 px flat previews |
| `artwork/*-rotation-test.png` | The same gobo at 0°, 15°, 30° and 45° |
| `artwork/*-floor-preview.jpg` | Shown as projected light on a real floor |
| `reference/logo-*.png` | The approved logo files the design was built against |
| `src/build_gobos.py` | Generates both gobos (all layout values at the top) |
| `src/shapes.py` | Text-on-a-circle and the geometric primitives |
| `src/check_rotation.py` | Verifies the rotation requirement |
| `src/floor_preview.py` | Builds the floor previews |

## Any-angle requirement — how it's met, and how that's checked

Nothing in either design has a single "up". Every element is stamped 4,
12, 24 or 48 times around the centre, which gives the whole disc **4-fold
rotational symmetry**: turn it 90° and it is the same disc.

The brand name is set **four times** around the ring, each facing outward.
Whichever side you stand on, the nearest name is at worst 45° off upright
— comfortably readable, and the same is true for a projector that is
mounted crooked.

Checked, not assumed. `check_rotation.py` rotates each rendered disc by
90° and compares it with the original:

| Gobo | Mean difference after a 90° turn |
|---|---|
| Syspex | 0.26 / 255 |
| SysGuard | 1.21 / 255 |

That residue is anti-aliasing from the rotation itself, not design drift.
The rotation-test strips show the worst case (45°) by eye.

## The two designs

**Syspex — technological.** A systems core: four bars stamped at 90°
interlock into a pinwheel square (systems fitting together, echoing the
angular interlock in the Syspex mark without copying it), inside nested
diamonds. Around it, a twelve-node network mesh, radial spokes with inline
nodes, and circuit traces with end pads on the diagonals. Teal **#00BBB4**
with white type.

**SysGuard — technologically safe.** A protective sensing field: an
octagon shield core held in a cyan targeting reticle, ringed by twelve hex
"protected cells", bold outward hazard chevrons, sensor nodes, and three
broken detection-sweep arcs that get heavier as they go out. Safety yellow
**#EED202** with white type, cyan used only as a small detection accent per
the SysGuard brand rules.

Both share the same skeleton — rim, name band, tagline band, diagonal
dividers, emblem — so they read as a pair.

## Colours

Official values as supplied: Syspex teal `#00BBB4`, SysGuard safety yellow
`#EED202`. (Sampling the approved logo PNGs gives `#19BCB9` and `#FFF200`
— close, but the official values are used.)

## Before production — two things to settle

1. **Type.** Neither brand face is installed here, so the type is set in
   Liberation Sans Bold as a stand-in. The wordmarks use a squared techno
   face; swap that in and convert to outlines before the gobo is cut.
2. **The tagline ring is fine detail.** On a 2 m projection the tagline is
   roughly 3 cm tall (Syspex) and 2 cm (SysGuard, whose tagline is twice as
   long). It will read standing over it, but softens at a distance. Drop it
   if the gobo will be seen mainly from across a room.

Also worth knowing: these use the brand *names as set type*, not the logo
lockups. Four copies at four rotations is what the any-angle requirement
needs, and rotating an approved logo is not allowed under the SysGuard
brand rules. If a literal logo is wanted, it would have to sit once in the
centre, upright — which gives up the any-angle property.

## Gobo convention

Black = no light (the floor shows through); colour = open aperture. Same
as the other files in this project.
