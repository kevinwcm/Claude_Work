# Green laser walkway line — corridor mockup

A single green laser line on the right-hand side of the corridor, near the
wall, shown on the original site photo.

| File | What it is |
|---|---|
| `mockups/corridor-green-laser-line.jpg` | The mockup |
| `reference/corridor-original.jpg` | Original corridor photo |
| `reference/earlier-two-line-mockup.webp` | Earlier two-line mockup, used only for the line's position |
| `src/laser_line.py` | Script that draws the line |

**Position.** Taken from the right-hand line of the earlier two-line mockup.
That mockup turned out to be this same photo, cropped and squashed
vertically by about 24%, so the line was mapped back onto the original by
feature matching. It passes within 1.5 px of the corridor's vanishing
point (found from the pipes, skirting and window lines), so it runs truly
parallel to the wall, and it clears the striped pillar's base.

**Rendering.** The line narrows with distance the way a real floor line
does (width scaled by distance below the horizon), with a solid laser-green
core, a green glow, and a faint scatter halo for the glossy epoxy floor.
Nothing else in the photo is altered.
