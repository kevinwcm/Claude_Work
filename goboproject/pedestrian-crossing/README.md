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
| `reference/warehouse-original.jpg` | Original warehouse site photo (clean, no mockup) |
| `reference/warehouse-aisle-original.png` | Kevin's annotated crop of that photo, with an earlier mockup crossing and the projector-aim arrow — used only to locate where the crossing goes |
| `mockups/warehouse-walkway-mockup.jpg` | The original photo with this design projected onto the floor at true proportions |
| `src/build.py` | Script that generates the SVG (edit the constants at the top to amend it) |
| `src/floor_model.py` | Camera/floor model of the warehouse photo (real-world metres on the floor) |
| `src/place_walkway.py` | Builds the warehouse mockup from the SVG and the floor model |

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

`mockups/warehouse-walkway-mockup.jpg` places this design on the floor of
`reference/warehouse-original.jpg`, at the spot Kevin's annotated crop
marked: across the forklift cross-aisle, from the centre rack block's row
end out to the right-hand rack end.

**How it's placed.** Rather than stretching the artwork into a hand-picked
four-corner shape, `floor_model.py` rebuilds the camera from the photo
(vanishing points of the racking and uprights), giving real-world metres on
the floor. The walkway is then laid down as a true rectangle with the
artwork's own proportions, so width and length can't drift out of ratio.
The model checks out against the scene: the four row-end bollards all land
at the same depth (6.3 m ± 0.2), the painted yellow dashes fall on one
straight line, and both workers measure 1.73–1.75 m tall.

**Size.** The clear cross-aisle there is only about 4.6 m, so the full
5.8 m design would run under the pallets. The mockup keeps the design's
exact proportions and sizes it to span the aisle: **4.2 m × 1.73 m**. That
is a lens/throw choice on the projector, not a change to the artwork.

**Light, not paint.** The pattern is added as light reflected by the floor
(the concrete texture shows through), the black text cut-outs stay unlit,
and the near end sits behind the bollard, the worker and the railing
rather than being painted over them.

**Worth knowing.** At this size the "PEDESTRIAN CROSSING" bands are only
~11 cm deep on the floor, which is hard to read from a forklift seat. For a
floor crossing, thicker text bands would help.

The earlier attempt at this mockup (hand-picked corners, whole square
canvas stretched onto the floor) came out far too thin and was replaced.

## Fix log

- The first version anchored the diagonal stripes to the bottom edge,
  leaving a blocked (dark) corner top-left instead of the small bright
  sliver in the photo. Re-anchored to the top edge instead.
- That fix then clipped a stripe short at the top-right corner. The shear
  is bigger than one stripe period, so the band that "wraps round" to
  cover the bottom-right corner starts off-canvas — the loop now walks a
  few extra periods either side and lets the clip crop whatever falls
  outside the box, instead of assuming one band per corner.
