# Syspex & SysGuard round brand gobos

Two round gobos, one per brand, designed so the projection reads correctly
however the projector is rotated or aligned.

| File | What it is |
|---|---|
| `artwork/gobo-syspex.svg` | Syspex production master |
| `artwork/gobo-sysguard.svg` | SysGuard production master (mirrored helmet pair) |
| `artwork/gobo-sysguard-alt-single-helmet.svg` | Variant: one upright helmet |
| `artwork/gobo-sysguard-alt-four-helmets.svg` | Variant: four helmets in a rosette |
| `artwork/*-2000.png` | 2000 px flat previews |
| `artwork/*-rotation-test.png` | The same gobo at 0°, 15°, 30° and 45° |
| `artwork/*-floor-preview.jpg` | Shown as projected light on a real floor |
| `reference/logo-*.png` | The approved logo files everything is traced from |
| `src/logo_trace.py` | Pulls the letterforms and marks out of the logo files |
| `src/build_gobos.py` | Generates all four files (layout values at the top) |
| `src/shapes.py` | Text-on-a-circle, sectors, and the other primitives |
| `src/check_rotation.py` | Verifies the rotation requirement |
| `src/floor_preview.py` | Builds the floor previews |

## Type and marks come from the logo files themselves

Rather than substitute a lookalike typeface, `logo_trace.py` takes the real
glyphs out of the approved logo artwork: it isolates each wordmark, splits
it at the gaps between letters, and traces every letter to an outline.
Letter widths and spacing come from the logo, so the word keeps its true
proportions when bent around the ring. The Syspex tile and the SysGuard
helmet are traced the same way. Counters and the grooves inside the Syspex
letters come through as holes, drawn `fill-rule="evenodd"`.

The only type still set in a substitute face is the small tagline ring.

*For production:* these outlines are traced from 1600 px PNGs, which is
about 1:1 with their size on the gobo, so they hold up. If you have the
vector logo (.ai/.eps) or the font itself, send it and the letterforms
become mathematically exact rather than traced.

## Any-angle requirement — how it's met, and how that's checked

The rim rings, the zebra band, the four brand names, the taglines and the
dividers are all **4-fold**: they repeat every 90°. The centre marks are
**180° marks** — the Syspex tile reads the same either way up, and the
SysGuard helmets are a mirrored pair — so the disc as a whole repeats
every 180°.

Each brand name is set four times facing outward, so whichever side you
stand on the nearest name is at worst 45° off upright.

`check_rotation.py` turns each rendered disc and compares it with itself:

| Gobo | 90°, rings and type only | 180°, whole disc |
|---|---|---|
| Syspex | 0.30 / 255 | 0.38 / 255 |
| SysGuard | 0.09 / 255 | 0.09 / 255 |

Those residues are anti-aliasing from the rotation, not design drift. In
short: the frame is identical every 90°, the whole disc every 180°, and
the centre mark reads either way up — so no projector orientation looks
wrong.

## The two designs

**Syspex — technological.** The real Syspex tile sits at the centre,
ringed by a twelve-node network mesh, radial spokes with inline nodes, and
circuit traces with end pads on the diagonals. Teal **#00BBB4**, white type.

**SysGuard — safety.** A pedestrian crossing bent into a circle: 24 radial
zebra bars between two kerb lines, wrapped around the SysGuard helmet.
Eight cyan sensor arcs keep the "technologically safe" note without
crowding it. Safety yellow **#EED202**, white type, cyan only as an accent
per the brand rules.

## The helmet, and why it's a mirrored pair

A hard hat has a definite "up", so it can't simply be dropped into an
any-angle design. Three options were built and compared:

- **Four helmets in a rosette** — keeps perfect 4-fold symmetry, but at
  that size the four brims interlock and the cluster reads as a gear, not
  as helmets. Rejected.
- **One upright helmet** — clearest and truest to the logo, but it is
  upside down from the far side, where it reads as a bowl.
- **A mirrored pair, 180° apart** *(chosen)* — the helmet stays
  unmistakable, the disc still repeats every 180°, and from a side view the
  pair is merely on its side, which still reads as helmets and looks
  deliberate.

Both alternatives are in `artwork/` if you'd rather have one of those.

## Before production

The tagline ring is fine detail: on a 2 m projection it is roughly 2–3 cm
tall. It reads standing over it but softens from across a room — drop it if
the gobo will mostly be seen from a distance.

## Gobo convention

Black = no light (the floor shows through); colour = open aperture. Same as
the other files in this project.
