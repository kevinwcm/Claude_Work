# Green laser walkway line — corridor mockup

A single green laser line on the right-hand side of the corridor, near the
wall, shown on the original site photo.

| File | What it is |
|---|---|
| `mockups/corridor-green-laser-line.jpg` | The mockup |
| `reference/corridor-original.jpg` | Original corridor photo |
| `reference/earlier-two-line-mockup.webp` | Earlier two-line mockup, used only for the line's position |
| `src/laser_line.py` | Script that draws the line |

**Position.** On the walkway between the bollard/chain line and the
right-hand wall, 35% of the walkway's width out from the wall, running
from the bottom of the frame to the far end of the walkway where the
bollard chain finishes. The wall base and the bollard line both run into
the corridor's vanishing point (found from the pipes, skirting and window
lines), so holding a fixed fraction between them keeps the laser truly
parallel to the wall all the way down. (A first version copied the
earlier mockup's line, which sat only ~20% out from the wall and stopped
short; that was too close to the wall.)

**Rendering.** The line narrows with distance the way a real floor line
does (width scaled by distance below the horizon), with a solid laser-green
core, a green glow, and a faint scatter halo for the glossy epoxy floor.
Nothing else in the photo is altered.
