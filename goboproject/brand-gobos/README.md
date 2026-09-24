# Syspex & SysGuard round brand gobos

Two round gobos, one per brand, designed so the projection reads correctly
however the projector is rotated or aligned.

| File | What it is |
|---|---|
| `artwork/gobo-syspex.svg` | Syspex production master |
| `artwork/gobo-sysguard.svg` | SysGuard production master (hazard-tape band) |
| `artwork/gobo-sysguard-alt-chevron.svg` | Variant: chevron ring instead of tape |
| `artwork/gobo-sysguard-alt-zone.svg` | Variant: quiet zone ring instead of tape |
| `artwork/*-2000.png` | 2000 px flat previews |
| `artwork/*-rotation-test.png` | The same gobo at 0°, 15°, 30° and 45° |
| `artwork/*-floor-preview.jpg` | Shown as projected light on a real floor |
| `reference/logo-sysguard-2026.png` | Updated SysGuard logo — the helmet is traced from this |
| `reference/logo-*.png` | The other approved logo files everything is traced from |
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

## Any-angle requirement — where it stands

The **frame** of both gobos — rim rings, safety band, the four brand
names, taglines and dividers — is 4-fold: it repeats every 90 degrees.
Each brand name is set four times facing outward, so whichever side you
stand on the nearest name is at worst 45 degrees off upright.

The **centre marks** differ:

- **Syspex** uses the real Syspex tile, which reads the same either way up,
  so the whole disc repeats every 180 degrees.
- **SysGuard** uses a single upright helmet (Kevin's call). A hard hat has
  a definite "up", so the disc as a whole is not rotationally symmetric —
  the helmet reads upright from one side and upside down from the far side.
  Everything around it still looks identical at any rotation.

`check_rotation.py` turns each rendered disc and compares it with itself:

| Gobo | 90°, frame only | 180°, whole disc |
|---|---|---|
| Syspex | 0.31 / 255 | 0.38 / 255 |
| SysGuard | 0.10 / 255 | 5.23 / 255 (the upright helmet) |

The small residues are anti-aliasing from the rotation itself. SysGuard's
180° figure is the helmet, by design.

## The two designs

**Syspex — technological.** The real Syspex tile at the centre, ringed by a
twelve-node network mesh, radial spokes with inline nodes, and circuit
traces with end pads on the diagonals. Teal **#00BBB4**, white type.

**SysGuard — safety.** A band of industrial hazard tape wrapped into a
ring, around the SysGuard helmet from the updated logo. Four small cyan
sensor arcs keep a technical note without crowding it. Safety yellow
**#EED202**, white type, cyan only as an accent per the brand rules.

## The SysGuard safety band

A first attempt used a full radial zebra — a pedestrian crossing bent into
a circle. It was too heavy: at that width the bars dominate the disc and it
reads as a roulette wheel. Three calmer options were built and compared:

- **Hazard tape** *(chosen)* — diagonal stripes in a narrow band between two
  kerb lines. It is the strongest safety signal of the three while staying
  quiet, and it is SysGuard's own border motif, so it is on-brand rather
  than invented.
- **Chevron ring** — twelve outward chevrons. Clean and directional, but the
  safety read is milder and it looks more decorative than cautionary.
- **Zone ring** — containment rings, ticks and corner brackets. The quietest
  of the three, but it reads as a technical dial more than a safety marking.

Both alternatives are in `artwork/` if you'd rather swap.

## Before production

The tagline ring is fine detail: on a 2 m projection it is roughly 2–3 cm
tall. It reads standing over it but softens from across a room — drop it if
the gobo will mostly be seen from a distance.

## Gobo convention

Black = no light (the floor shows through); colour = open aperture. Same as
the other files in this project.
