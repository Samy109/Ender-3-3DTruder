"""
3DTruder heated barrel coupler (build123d + bd_warehouse). Matches shop_order.md and drawing BC-001.

    Barrel tube (12 mm OD, M12x1.0 external thread)
      -> this coupler (second heat zone: 24 V cartridge + thermistor)
      -> M6x1.0 male stub straight into the Super Volcano block (seals on the nozzle)

Made as a 316L metal print (SLM) held to +/-0.3 mm, with no machining or thread cutting afterwards.
So every fit is sized for that tolerance:
  - threads are printed and offset by FIT on diameter (external smaller, internal larger) so they
    still go together at the edge of the tolerance;
  - holes a part slides into are nominal + 0.3; the wrench flats and the clamp round are nominal - 0.3.
All threads are modelled (ISO 60 deg profile, right hand, bd_warehouse IsoThread).
Body z runs from the shoulder (z = 0) up; the stub hangs below (z = -15 .. 0).

  Stub:        M6x1.0 printed full length (z -15 .. -1.5), major 5.7; Ø4.4 x 1.5 relief at the shoulder
  Bore:        Ø3.0 through the body, Ø2.0 through the stub
  Heater zone (body z 0-20, solid except the bore):
    Cartridge: Ø6.3 cross hole, through, 6.5 mm off-axis, at z = 7   (24 V 40 W, 6 x 20 mm)
    Thermistor: Ø3.3 cross hole, 16 deep, 6.5 mm off-axis (opposite side), at z = 15
    Set screws: M5x0.8 printed, up from the shoulder face into each hole
  Flats:       21.7 mm across (fits a 22 mm wrench at +0.3), body z 20-26
  Top:         M12x1.0 printed internal thread, major 12.3, 14 full thread (z 26-40); hole 18 deep with
               a 90 deg cone floor; round Ø24.7 for an SK25 clamp
Material: 316L stainless, metal 3D printed (SLM). Not aluminium.

Run:  python barrel_coupler.py   -> barrel_coupler.step / .stl
"""
from pathlib import Path

from build123d import Align, Axis, Box, GeomType, Plane, Polygon, chamfer, extrude, BuildLine, BuildPart, BuildSketch, Cylinder, Polyline, Pos, Rot, export_step, export_stl, make_face, revolve
from bd_warehouse.thread import IsoThread

FIT = 0.3                                        # print tolerance (+/-), applied on diameter to every fit
BODY_D, BODY_L = 25.0 - FIT, 40.0                # Ø24.7: an SK25 clamp still closes on it at +0.3
STUB_L = 15.0
M6_MAJOR = 6.0 - FIT                             # printed external M6x1.0
RELIEF_D, RELIEF_L = 4.4, 1.5                    # just under the M6 root (4.47)
M12_MAJOR = 12.0 + FIT                           # printed internal M12x1.0
M12_DEPTH, M12_DRILL_DEPTH = 14.0, 18.0          # full thread, then 4 mm of plain hole above the cone floor
BORE, STUB_BORE = 3.0, 2.0
FLATS, FLATS_Z0, FLATS_Z1 = 22.0 - FIT, 20.0, 26.0
HEATER_D, HEATER_OFFSET, HEATER_Z = 6.0 + FIT, 6.5, 7.0
THERM_D, THERM_OFFSET, THERM_Z, THERM_DEPTH = 3.0 + FIT, -6.5, 15.0, 16.0
SET_MAJOR, SET_PITCH = 5.0 + FIT, 0.8            # printed internal M5x0.8 for the set screws
THERM_SET_X = 3.0                                # thermistor set screw: far enough in to keep wall to the OD
CH = 0.5

R, rr, rb, rbs = BODY_D / 2, RELIEF_D / 2, BORE / 2, STUB_BORE / 2
r_root6 = 0.5 * (M6_MAJOR - 1.2269 * 1.0)        # M6 external root radius (thread ridge overlaps into this core)
r_m12 = M12_MAJOR / 2                            # hole is bored to the major radius; thread teeth are fused inside
z_tip, z_top, z_m12 = -STUB_L, BODY_L, BODY_L - M12_DEPTH
z_floor = BODY_L - M12_DRILL_DEPTH

# Half cross-section (radius, z), revolved around Z.
profile = [
    (rbs, z_tip), (r_root6, z_tip),                             # flat sealing face
    (r_root6, -RELIEF_L), (rr, -RELIEF_L), (rr, 0),              # thread-root core + relief
    (R - CH, 0), (R, CH),                                        # shoulder + chamfer
    (R, z_top - CH), (R - CH, z_top),                            # body wall + top chamfer
    (r_m12 + CH, z_top), (r_m12, z_top - CH),                    # top face + M12 lead-in chamfer
    (r_m12, z_floor), (rb, z_floor - (r_m12 - rb)),               # M12 hole wall + 90 deg conical floor (self-supporting)
    (rb, 0), (rbs, 0),                                           # Ø3 body bore steps down to Ø2 stub bore
]
with BuildPart() as bp:
    with BuildSketch(Plane.XZ):
        with BuildLine():
            Polyline(*profile, close=True)
        make_face()
    revolve(axis=Axis.Z)
part = bp.part

# Wrench flats (normal to Y)
flat_box = Box(40, 10, FLATS_Z1 - FLATS_Z0, align=(Align.CENTER, Align.MIN, Align.MIN))
part = part - Pos(0, FLATS / 2, FLATS_Z0) * flat_box
part = part - Pos(0, -FLATS / 2 - 10, FLATS_Z0) * flat_box

def teardrop_peak(r, length, y, z):
    """Wedge on the -Z (build-up) side of a hole along X so the hole prints without support (45 deg roof)."""
    k = r * 2 ** 0.5
    tri = Polygon((r / 2 ** 0.5, r / 2 ** 0.5), (r / 2 ** 0.5, -r / 2 ** 0.5), (k, 0), align=None)
    return Pos(0, y, z) * Rot(0, 90, 0) * extrude(Plane.XY * tri, amount=length / 2, both=True)


# Cartridge heater: through cross hole along X, offset +Y (teardrop roof on the build-up side)
part = part - Pos(0, HEATER_OFFSET, HEATER_Z) * Rot(0, 90, 0) * Cylinder(HEATER_D / 2, 2 * BODY_D)

# Thermistor: blind cross hole along X from the +X side, offset -Y
x_surface = (R ** 2 - THERM_OFFSET ** 2) ** 0.5
therm_len = THERM_DEPTH + 1
part = part - Pos(x_surface + 1 - therm_len / 2, THERM_OFFSET, THERM_Z) * Rot(0, 90, 0) * Cylinder(THERM_D / 2, therm_len)

# M5 set-screw holes (bored to the major radius), up from the shoulder face into each hole
part = part - Pos(0, HEATER_OFFSET, HEATER_Z / 2) * Cylinder(SET_MAJOR / 2, HEATER_Z)
part = part - Pos(THERM_SET_X, THERM_OFFSET, THERM_Z / 2) * Cylinder(SET_MAJOR / 2, THERM_Z)

# 0.3 x 45 deg chamfer on the heater (both ends) and thermistor hole entries
cross_edges = [e for e in part.edges() if e.geom_type == GeomType.BSPLINE and abs(e.center().X) > 9 and e.length > 8]
part = chamfer(cross_edges, 0.3)

# Teardrop roofs (45 deg) on the build-up side of both cross holes so they print without support
part = part - teardrop_peak(HEATER_D / 2, 2 * BODY_D, HEATER_OFFSET, HEATER_Z)
part = part - Pos(x_surface + 1 - therm_len / 2, 0, 0) * teardrop_peak(THERM_D / 2, therm_len, THERM_OFFSET, THERM_Z)

# ---- threads ----
def fuse_thread(base, thread, loc):
    """OCC booleans on helical solids are touchy about exact coincidences; retry with tiny angle/position nudges (<=0.03 mm)."""
    for ang in (0, 37, 111, 200, 290):
        for dz in (0.0, 0.013, 0.027):
            out = base + loc * Pos(0, 0, dz) * Rot(0, 0, ang) * thread
            if out.volume > base.volume:
                return out
    raise RuntimeError("thread fuse failed")


# Internal M5x0.8 set-screw threads first (cleanest base for the fuse); only the part below each cross hole
heater_set_len = HEATER_Z - HEATER_D / 2 * 2 ** 0.5 - 0.3      # stops short of the heater teardrop point
therm_set_len = THERM_Z - THERM_D / 2 * 2 ** 0.5 - 0.3
part = fuse_thread(part, IsoThread(major_diameter=SET_MAJOR, pitch=SET_PITCH, length=therm_set_len, external=False,
                                   end_finishes=("fade", "fade")), Pos(THERM_SET_X, THERM_OFFSET, 0))
part = fuse_thread(part, IsoThread(major_diameter=SET_MAJOR, pitch=SET_PITCH, length=heater_set_len - 0.3, external=False,
                                   end_finishes=("fade", "fade")), Pos(0, HEATER_OFFSET, 0.3))
# Internal M12x1.0 in the top bore (teeth fused inside the major-radius bore)
part = fuse_thread(part, IsoThread(major_diameter=M12_MAJOR, pitch=1.0, length=M12_DEPTH, external=False,
                                   end_finishes=("fade", "fade")), Pos(0, 0, z_m12))
# External M6x1.0 on the stub: chamfered at the tip, fades out at the relief
part = fuse_thread(part, IsoThread(major_diameter=M6_MAJOR, pitch=1.0, length=STUB_L - RELIEF_L, external=True,
                                   end_finishes=("chamfer", "fade")), Pos(0, 0, z_tip))


out = Path(__file__).with_suffix("")
export_step(part, str(out) + ".step")
export_stl(part, str(out) + ".stl")
print("valid:", part.is_valid, " volume: %.1f mm3" % part.volume, " solids:", len(part.solids()))
print("wrote", str(out) + ".step", "and .stl")
