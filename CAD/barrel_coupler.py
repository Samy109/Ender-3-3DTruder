"""
3DTruder heated barrel coupler (CadQuery). Matches shop_order.md, Job 1.

    Barrel tube (12 mm OD, M12x1.0 external thread)
      -> this coupler (second heat zone: 24 V cartridge + thermistor)
      -> M6x1.0 male stub straight into the Super Volcano block (seals on the nozzle)

Threads are not modelled. Features are at the sizes the machinist works from.
Body z runs from the shoulder (z = 0) up; the stub hangs below (z = -15 .. 0).

  Stub:        Ø6.0 x 15, thread M6x1.0 full length, Ø4.8 x 1.5 relief at the shoulder
  Bore:        Ø3.0 straight through
  Heater zone (body z 0-20, solid except the bore):
    Cartridge: Ø6.0 cross hole, through, 6.5 mm off-axis, at z = 7   (24 V 40 W, 6 x 20 mm)
    Thermistor: Ø3.0 cross hole, 16 deep, 6.5 mm off-axis (opposite side), at z = 15
    Set screws: M3 (Ø2.5 tap drill) up from the shoulder face into each hole
  Flats:       22 mm across, body z 20-26
  Top:         Ø11.0 x 14 deep (z 26-40) -> tap M12x1.0; round Ø25 here for an SK25 clamp
Material: brass (C360) preferred, stainless second choice. Not aluminium.

Run:  python barrel_coupler.py   -> writes barrel_coupler.step / .stl next to this file
"""
from pathlib import Path

import cadquery as cq

BODY_D, BODY_L = 25.0, 40.0
STUB_D, STUB_L = 6.0, 15.0
RELIEF_D, RELIEF_L = 4.8, 1.5
M12_DRILL, M12_DEPTH = 11.0, 14.0
BORE = 3.0
FLATS, FLATS_Z0, FLATS_Z1 = 22.0, 20.0, 26.0
HEATER_D, HEATER_OFFSET, HEATER_Z = 6.0, 6.5, 7.0
THERM_D, THERM_OFFSET, THERM_Z, THERM_DEPTH = 3.0, -6.5, 15.0, 16.0
SET_DRILL = 2.5
CH, STUB_CH = 0.5, 0.3

R, rs, rr, ra, rb = BODY_D / 2, STUB_D / 2, RELIEF_D / 2, M12_DRILL / 2, BORE / 2
z_tip, z_top, z_m12 = -STUB_L, BODY_L, BODY_L - M12_DEPTH

# Half cross-section (radius, z), revolved around Z.
profile = [
    (rb, z_tip), (rs - STUB_CH, z_tip), (rs, z_tip + STUB_CH),   # flat sealing face + tip chamfer
    (rs, -RELIEF_L), (rr, -RELIEF_L), (rr, 0),                   # threaded stub + relief
    (R - CH, 0), (R, CH),                                        # shoulder + chamfer
    (R, z_top - CH), (R - CH, z_top),                            # body wall + top chamfer
    (ra + CH, z_top), (ra, z_top - CH),                          # top face + M12 lead-in
    (ra, z_m12), (rb, z_m12),                                    # M12 hole wall + floor
]
part = cq.Workplane("XZ").polyline(profile).close().revolve(360, (0, 0, 0), (0, 1, 0))

# Wrench flats (normal to Y)
for side in (1, -1):
    part = part.cut(cq.Workplane("XY").box(40, 10, FLATS_Z1 - FLATS_Z0, centered=(True, False, False))
                    .translate((0, FLATS / 2 if side > 0 else -FLATS / 2 - 10, FLATS_Z0)))

# Cartridge heater: through cross hole along X, offset +Y
part = part.cut(cq.Workplane("YZ").center(HEATER_OFFSET, HEATER_Z).circle(HEATER_D / 2)
                .extrude(BODY_D, both=True))

# Thermistor: blind cross hole along X from the +X side, offset -Y
x_surface = (R ** 2 - THERM_OFFSET ** 2) ** 0.5
part = part.cut(cq.Workplane("YZ").workplane(offset=x_surface + 1).center(THERM_OFFSET, THERM_Z)
                .circle(THERM_D / 2).extrude(-(THERM_DEPTH + 1)))

# M3 set-screw tap drills, up from the shoulder face into each hole
part = part.cut(cq.Workplane("XY").center(0, HEATER_OFFSET).circle(SET_DRILL / 2).extrude(HEATER_Z))
part = part.cut(cq.Workplane("XY").center(x_surface - 4, THERM_OFFSET).circle(SET_DRILL / 2).extrude(THERM_Z))

out = Path(__file__).with_suffix("")
cq.exporters.export(part, str(out) + ".step")
cq.exporters.export(part, str(out) + ".stl")
print("wrote", str(out) + ".step", "and .stl")
