# "Powered by Syspex" zebra — aisle mockup

Kevin's earlier aisle mockup used an old white/yellow zebra. This replaces it
with the "Powered by Syspex / Secured by SysGuard" design.

| File | What it is |
|---|---|
| `mockups/aisle-syspex-zebra-mockup.jpg` | The new mockup |
| `reference/old-zebra-mockup.webp` | Earlier mockup with the old zebra (no clean photo exists) |
| `reference/aisle-old-zebra-removed.png` | Same image with the old zebra removed |
| `reference/powered-by-syspex.pdf` / `.webp` | The design |
| `src/erase_old_zebra.py` | Removes the old zebra |
| `src/floor_model.py` | Floor/camera model in metres |
| `src/place_zebra.py` | Projects the design onto the floor |

**Removing the old zebra.** There's no clean photo of this aisle, so the old
pattern is painted out: a smooth fill matched to the floor around it, plus
real concrete grain from clean floor blocks found automatically nearby. The
painted walkway band is kept intact. It's told apart from the old zebra's
yellow bars by hue (the paint is orange-yellow, the old bars lemon-yellow).

**Size and position.** The floor model is rebuilt from the photo's
vanishing points and checked against the scene: the bollards measure
1.04 m and stand on one line, and the painted band is a constant 0.72 m
wide all along the aisle. The projection is 2.4 m wide, with its rack-side
edge flush with the band's outer edge, so it covers the whole painted band
without spilling toward the racking. It runs 10 m along the aisle, from the
bottom of the frame to just before the band curves at the end of the
racking. Bars repeat along the aisle like the old zebra.

At 10 m × 2.4 m the design is stretched lengthwise compared with its
native 5.8 m × 2.4 m. That's what happens when a gobo projector is aimed
down an aisle at a shallow angle. For true proportions over that length
you'd need two projectors end to end.

(An earlier version centred the width on the band's inner edge. Since the
band is only 0.72 m wide, that pushed 0.5 m onto the strip in front of the
bollards, too close to the racking.)

**Light, not paint.** Kept deliberately modest: in a lit warehouse a gobo
lifts the floor rather than glowing. It brightens the surface under it
(texture shows through), slightly desaturated, fading a little with throw
distance; black text and outlines stay unlit. On the yellow
paint, the white bars stand out while the yellow bars blend in, as real
projected light would.
