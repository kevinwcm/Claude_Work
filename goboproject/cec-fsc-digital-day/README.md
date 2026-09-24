# CEC FSC Digital Day — gobo projection

Replaces the printed floor sticker at the Nestlé entrance with a SysGuard gobo
projection, reusing the Digital Day theme artwork and adding a discreet
Syspex / SysGuard credit.

## The rule that shapes the whole design

A gobo is a stencil. Light passes through the clear parts and is blocked by the
dark parts. **Black in the artwork means no light, so the bare floor shows
through.** That is why this artwork is drawn light-on-dark, the opposite way
round to the sticker: the sticker's navy background becomes the concrete itself,
and only the globe, the type and the ring actually glow.

## What's here

| File | What it is |
|---|---|
| `artwork/gobo-A-fullcolour.svg` | Concept A, vector, production master |
| `artwork/gobo-A-fullcolour-2400.png` | Concept A, 2400 px preview |
| `artwork/gobo-B-twocolour.svg` | Concept B, vector, production master |
| `artwork/gobo-B-twocolour-2400.png` | Concept B, 2400 px preview |
| `mockups/mockup-A-fullcolour.png` | Concept A shown on the real entrance floor |
| `mockups/mockup-B-twocolour.png` | Concept B shown on the real entrance floor |
| `reference/entrance-sticker-removed.png` | The entrance photo with the existing floor sticker removed (the mockups' base) |
| `reference/` | Current entrance photo and the logo files used |
| `src/` | Scripts that generate the artwork and the mockups |

## How the mockups are made

`src/mockup.py` first removes the existing floor sticker completely. It
rebuilds the concrete with a smooth fill that matches the real floor all
round the sticker's edge (pillars treated as walls, so no navy bleeds in),
then adds real concrete texture sampled from clean floor nearby. The gobo is
then added as light only: screen-blended over the bare floor, so the
concrete shows through and the artwork's dark areas add nothing. There is
deliberately no darkening under the projection, because a dark disc reads
as a sticker.

## The two concepts

**A — Full colour.** Closest to the printed sticker: gold continents, deep blue
oceans, cyan ring glow, copper arc segments. Needs a full-colour glass gobo.
Richest look, lowest light output.

**B — Two colour (white + SysGuard yellow).** Line-art globe, bold white type,
yellow arcs. Noticeably brighter on the floor and far more tolerant of ambient
light. Also the more SysGuard-branded of the two.

## Branding

Nestlé's message stays dominant. Syspex and SysGuard appear once, small, at the
foot of the disc under a "PROJECTED BY" label — a credit, not a takeover.
Approved logo files were used as-is; neither has been redrawn or recoloured.

## Still needed before production

1. **Gobo glass size** from the Warton projector spec (outer diameter and image
   diameter). The artwork is square and scales to any size, but the maker needs
   the exact figures.
2. **Nestlé’s original sticker artwork** (AI/EPS/PDF). The headline here is set
   in Liberation Sans Bold Italic as a stand-in; the real event font should be
   dropped in and converted to outlines.
3. **Mono logo files** if Concept B goes ahead as a true two-colour gobo — the
   Syspex mark's teal square would otherwise be a third colour.
4. **Nestlé sign-off** on using their theme artwork in this form.

## Site note

The entrance in the photo is an open-sided walkway in daylight. A gobo competes
with ambient light, so in full sun the projection will look washed out no matter
how bright the projector. Best results come from the shaded section under the
roof, or from running the projection at dusk / indoors. Worth confirming where
and when Nestlé wants it before committing to a fixture.

## Production spec (draft, for the gobo maker)

- Headline copy, four lines: `WELCOME` / `to` / `CEC FSC` / `DIGITAL DAY`
  (lines 3 and 4 share one point size so the lockup stays even)
- Artwork: square, 1:1, image circle fills the full width
- Colour mode: A = full-colour glass gobo; B = two-colour (white + `#FFD600`)
- Minimum stroke weight in the artwork: 2 px at 2000 px square (~0.1% of
  diameter) — anything finer will not hold focus on the floor
- All type to be supplied as outlines, not live text
- Soft glows in the SVG are built from layered strokes, not filters, so they
  flatten cleanly
