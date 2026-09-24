# Pedestrian Crossing — gobo, rebuilt as an editable SVG

Kevin's existing gobo light is currently running this "Pedestrian Crossing"
hazard-stripe pattern, but only a projected photo of it existed — no source
file to edit. This reconstructs it as a clean, editable vector so amendments
(wording, stripe count, icon, sizing) don't mean re-tracing a photo again.

## Files

| File | What it is |
|---|---|
| `artwork/pedestrian-crossing.svg` | Editable vector, production master |
| `artwork/pedestrian-crossing.pdf` | Same artwork as a 2250×2250pt PDF, for importing into Canva |
| `artwork/pedestrian-crossing-2400.png` | 2400 px flat preview |
| `artwork/glow-simulation.png` | The SVG rendered as projected light, for comparing against the real thing |
| `reference/pedestrian-crossing-current-photo.jpg` | The photo this was reconstructed from |
| `reference/powered-by-syspex-reference.pdf` | Kevin's other gobo file for this fixture, used to match canvas size and drawing conventions |
| `reference/warehouse-aisle-original.png` | Site photo of a different aisle, still showing the old blue LED floor-strip crossing it's meant to replace |
| `mockups/warehouse-aisle-mockup.png` | That same photo with the LED strip removed and this design composited in as projected light |
| `src/build.py` | Script that generates the SVG (edit the constants at the top to amend it) |
| `src/compose.py` | Script that builds the warehouse mockup (erases the old fixture, warps the new artwork onto the same floor quad) |

## Sizing

Same canvas and aperture envelope as `powered-by-syspex-reference.pdf`, so
this drops into the same fixture: 2250×2250pt canvas, aperture
~1909.6 × 816.9pt, which that file's own dimension callouts put at
**5.8m × 2.4m**.

## How it reads

Matching the convention in the reference PDF: unfilled canvas = opaque
(blocked), yellow fill = open aperture (light passes), black = a cut-out
inside an open area (the text and icons). No border/outline stroke on
the open shapes — edges are just the fill boundary, at Kevin's request.

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

## Editing in Canva

Canva's "import a PDF as a design" only works from a file already on your
own device, not from a link, so: download `artwork/pedestrian-crossing.pdf`,
then in Canva use **Create a design → Import file** (or drag the PDF into
your Projects) and let it convert the PDF's shapes and text into editable
Canva elements. The SVG is there too if you'd rather start from that.

## The warehouse mockup

`reference/warehouse-aisle-original.png` is a site photo (with a red dotted
annotation showing the proposed ceiling-mounted projector's aim) of an aisle
that currently has a physical blue LED zebra-crossing strip set into the
floor. `mockups/warehouse-aisle-mockup.png` shows that same aisle with the
LED strip erased and this gobo pattern warped onto the same patch of floor
as projected light, so it can stand in for "what a gobo would look like
here instead of the LED fixture."

The floor quad was measured directly off the photo (the blue LED end-caps
mark the crossing's two short ends), then eased outward by 20% because the
white zebra stripes themselves run a little wider than those accent strips.
The old fixture is removed by cloning nearby clean floor over it, not by
guesswork — same technique as the Nestlé entrance mockup earlier in this
project.

## Fix log

- The first version anchored the diagonal stripes to the bottom edge,
  leaving a blocked (dark) corner top-left instead of the small bright
  sliver in the photo. Re-anchored to the top edge instead.
- That fix then clipped a stripe short at the top-right corner. The shear
  is bigger than one stripe period, so the band that "wraps round" to
  cover the bottom-right corner starts off-canvas — the loop now walks a
  few extra periods either side and lets the clip crop whatever falls
  outside the box, instead of assuming one band per corner.
