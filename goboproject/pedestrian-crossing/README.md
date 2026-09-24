# Pedestrian Crossing — gobo, rebuilt as an editable SVG

Kevin's existing gobo light is currently running this "Pedestrian Crossing"
hazard-stripe pattern, but only a projected photo of it existed — no source
file to edit. This reconstructs it as a clean, editable vector so amendments
(wording, stripe count, icon, sizing) don't mean re-tracing a photo again.

## Files

| File | What it is |
|---|---|
| `artwork/pedestrian-crossing.svg` | Editable vector, production master |
| `artwork/pedestrian-crossing-2400.png` | 2400 px flat preview |
| `artwork/glow-simulation.png` | The SVG rendered as projected light, for comparing against the real thing |
| `reference/pedestrian-crossing-current-photo.jpg` | The photo this was reconstructed from |
| `reference/powered-by-syspex-reference.pdf` | Kevin's other gobo file for this fixture, used to match canvas size and drawing conventions |
| `src/build.py` | Script that generates the SVG (edit the constants at the top to amend it) |

## Sizing

Same canvas and aperture envelope as `powered-by-syspex-reference.pdf`, so
this drops into the same fixture: 2250×2250pt canvas, aperture
~1909.6 × 816.9pt, which that file's own dimension callouts put at
**5.8m × 2.4m**.

## How it reads

Matching the convention in the reference PDF: unfilled canvas = opaque
(blocked), yellow fill = open aperture (light passes), black = a cut-out
inside an open area (the text and icons), thin black stroke = the cut
line around every open shape.

The top band is rotated a full 180° about its own centre — not just flipped
— exactly as "Secured by SysGuard" is in the reference file. That's what
makes the text read upside-down in the photo: each band is meant to read
right-way-up to someone approaching from that end of the walkway.

## What's a faithful reconstruction vs. a redraw

- **Stripe count, angle, spacing, band proportions, mirroring** — measured
  directly off the photo (7 bright diagonal stripes, ~30° off vertical,
  clipped at both ends) and cross-checked against the reference PDF's own
  measurements for the band heights and margins.
- **Pedestrian icon** — the one in the photo is too small in the source
  photo to trace accurately, so this is a clean redraw of a generic walking
  figure, not a pixel copy. Swap in Syspex's own pictogram file here if one
  exists.
- **Font** — set in Liberation Sans Bold as a close stand-in. Swap for the
  house font before this goes to production.

## To amend

Everything that defines the layout is at the top of `src/build.py`
(band heights, stripe angle, stripe count, wording, colours). Change a
value and re-run `python3 build.py` to regenerate the SVG — no need to
hand-edit paths.
