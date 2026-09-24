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
wide all along the aisle. The design is placed at its real **5.8 m × 2.4 m**,
bars repeating along the aisle like the old zebra. It is centred on the
band's aisle-side edge, so **half lies on the yellow paint and half on the
grey floor** (per Kevin). The rack-side edge ends just short of the bollards.

**Light, not paint.** The design brightens the surface under it, so floor
texture shows through; black text and outlines stay unlit. On the yellow
paint, the white bars stand out while the yellow bars blend in, as real
projected light would.
