"""
3DTruder heated barrel coupler (build123d + bd_warehouse). Matches shop_order.md and drawing BC-001.

    Barrel tube (12 mm OD, M12x1.0 external thread)
      -> this coupler (second heat zone: 24 V cartridge + thermistor)
      -> M6x1.0 male stub straight into the Super Volcano block (seals on the nozzle)

Made as a 316L metal print (SLM, JLC3D): +/-0.3 mm on sizes, +/-0.5 mm on holes, no machining.
So every fit is sized for that tolerance:
  - threads are printed and offset by FIT on diameter (external smaller, internal larger). A tight
    internal thread can be chased with a tap after printing; a loose one can't be fixed, so they
    stay at 0.3 rather than 0.5;
  - the cartridge holes are nominal + HOLE_FIT (a cartridge can't be forced into a tight hole; the
    set screw takes up a loose one); the wrench flats and the clamp round are nominal - 0.3.
All threads are modelled (ISO 60 deg profile, right hand, bd_warehouse IsoThread), M6 or larger.
Every wall is at least 2.0 mm except the stub (1.5 under the M6 root) and the thread teeth.
Body z runs from the shoulder (z = 0) up; the stub hangs below (z = -15 .. 0).

  Stub:        M6x1.0 printed full length, major 5.7, runs out at the shoulder (no relief)
  Bore:        Ø1.4 through the stub and 2 mm into the body (1.5 wall under the M6 root, and no thin
               neck at the shoulder), 90 deg cone up to Ø3.0 through the rest of the body
  Heater block (body z 0-26): 21.7 x 24.7, the 21.7 faces (normal to X) are the wrench flats
               (22 mm wrench at +0.3); both cross holes exit square through these faces.
               Corners chamfered 45 deg into the round above so they print without support.
    Cartridge: Ø6.5 cross hole, through, 6.8 mm off-axis, at z = 8   (24 V 40 W, 6 x 20 mm)
    Thermistor: Ø3.5 cross hole, 16 deep from +X, 6.8 mm off-axis (opposite side), at z = 15
    Set screws: M6x1.0 printed, up from the shoulder face into each hole
  Top (z 26-40): round Ø24.7 for an SK25 clamp; M12x1.0 printed internal thread, major 12.3,
               14 full thread; hole 18 deep with a 90 deg cone floor
Material: 316L stainless, metal 3D printed (SLM). Not aluminium.

Run:  python barrel_coupler.py   -> barrel_coupler.step / .stl
"""
from pathlib import Path

from build123d import Axis, GeomType, Plane, Polygon, RectangleRounded, chamfer, extrude, BuildLine, BuildPart, BuildSketch, Cylinder, Polyline, Pos, Rot, export_step, export_stl, make_face, revolve
from bd_warehouse.thread import IsoThread

FIT = 0.3                                        # print tolerance (+/-) on sizes, applied on diameter to every fit
HOLE_FIT = 0.5                                   # JLC3D's hole tolerance (+/-), applied to the cartridge holes
BODY_D, BODY_L = 25.0 - FIT, 40.0                # Ø24.7: an SK25 clamp still closes on it at +0.3
STUB_L = 15.0
M6_MAJOR = 6.0 - FIT                             # printed external M6x1.0
M12_MAJOR = 12.0 + FIT                           # printed internal M12x1.0
M12_DEPTH, M12_DRILL_DEPTH = 14.0, 18.0          # full thread, then 4 mm of plain hole above the cone floor
BORE, STUB_BORE = 3.0, 1.4                       # stub bore 1.4 = nozzle orifice; leaves 1.5 wall under the M6 root
STUB_BORE_TOP = 2.0                              # Ø1.4 runs 2 mm into the body before the cone to Ø3.0 (no neck)
FLATS, BLOCK_Z1, BLOCK_R = 22.0 - FIT, 26.0, 1.0  # heater block: 21.7 A/F (wrench flats) x BODY_D, z 0-26, R1 corners
HEATER_D, HEATER_OFFSET, HEATER_Z = 6.0 + HOLE_FIT, 6.8, 8.0   # 6.8 off-axis: 2.05 wall to the bore, 2.3 to the side
THERM_D, THERM_OFFSET, THERM_Z, THERM_DEPTH = 3.0 + HOLE_FIT, -6.8, 15.0, 16.0
SET_MAJOR, SET_PITCH = 6.0 + FIT, 1.0            # printed internal M6x1.0 for the set screws
THERM_SET_X = 3.0                                # thermistor set screw: X position along the thermistor hole
CH = 0.5

R, rb, rbs = BODY_D / 2, BORE / 2, STUB_BORE / 2
xf = FLATS / 2                                   # flat faces at X = +/-10.85
r_root6 = 0.5 * (M6_MAJOR - 1.2269 * 1.0)        # M6 external root radius (thread ridge overlaps into this core)
r_m12 = M12_MAJOR / 2                            # hole is bored to the major radius; thread teeth are fused inside
z_tip, z_top, z_m12 = -STUB_L, BODY_L, BODY_L - M12_DEPTH
z_floor = BODY_L - M12_DRILL_DEPTH


def revolved(profile):
    """Solid from a closed (radius, z) half-section revolved around Z."""
    with BuildPart() as bp:
        with BuildSketch(Plane.XZ):
            with BuildLine():
                Polyline(*profile, close=True)
            make_face()
        revolve(axis=Axis.Z)
    return bp.part


# Round top for the clamp (top chamfer), z 26-40
top = revolved([(0, BLOCK_Z1), (R, BLOCK_Z1), (R, z_top - CH), (R - CH, z_top), (0, z_top)])

# Heater block z 0-26, shoulder edges chamfered; its corners stick out past the round, so they are cut
# back by a 45 deg cone into the round (r <= R + (26 - z)) and print without support stub-up
block = extrude(Plane.XY * RectangleRounded(FLATS, BODY_D, BLOCK_R), amount=BLOCK_Z1)
block = chamfer(block.edges().group_by(Axis.Z)[0], CH)
r_big = 20.0
block = block & revolved([(0, -1), (r_big, -1), (r_big, BLOCK_Z1 - (r_big - R)), (R, BLOCK_Z1), (0, BLOCK_Z1)])

# Stub core at the M6 root radius (the thread ridge is fused on below), overlapping into the block
stub = revolved([(0, z_tip), (r_root6, z_tip), (r_root6, 0.5), (0, 0.5)])

part = top + block + stub

# Bore (Ø1.4 up to z 2, 90 deg cone to Ø3.0), M12 hole with lead-in chamfer and 90 deg cone floor (self-supporting)
part = part - revolved([
    (0, z_tip - 1), (rbs, z_tip - 1), (rbs, STUB_BORE_TOP), (rb, STUB_BORE_TOP + (rb - rbs)),
    (rb, z_floor - (r_m12 - rb)), (r_m12, z_floor),
    (r_m12, z_top - CH), (r_m12 + CH, z_top), (r_m12 + CH, z_top + 1), (0, z_top + 1),
])


def teardrop_peak(r, length, y, z):
    """Wedge on the -Z (build-up) side of a hole along X so the hole prints without support (45 deg roof)."""
    k = r * 2 ** 0.5
    tri = Polygon((r / 2 ** 0.5, r / 2 ** 0.5), (r / 2 ** 0.5, -r / 2 ** 0.5), (k, 0), align=None)
    return Pos(0, y, z) * Rot(0, 90, 0) * extrude(Plane.XY * tri, amount=length / 2, both=True)


# Cartridge heater: through cross hole along X, offset +Y, flat face to flat face
part = part - Pos(0, HEATER_OFFSET, HEATER_Z) * Rot(0, 90, 0) * Cylinder(HEATER_D / 2, 2 * BODY_D)

# Thermistor: blind cross hole along X from the +X flat, offset -Y
therm_len = THERM_DEPTH + 1
therm_x = xf + 1 - therm_len / 2
part = part - Pos(therm_x, THERM_OFFSET, THERM_Z) * Rot(0, 90, 0) * Cylinder(THERM_D / 2, therm_len)

# M6 set-screw holes (bored to the major radius), up from the shoulder face into each hole
part = part - Pos(0, HEATER_OFFSET, HEATER_Z / 2) * Cylinder(SET_MAJOR / 2, HEATER_Z)
part = part - Pos(THERM_SET_X, THERM_OFFSET, THERM_Z / 2) * Cylinder(SET_MAJOR / 2, THERM_Z)

# 0.3 x 45 deg chamfer on the heater (both ends) and thermistor hole entries on the flats
cross_edges = [e for e in part.edges() if e.geom_type == GeomType.CIRCLE and abs(abs(e.center().X) - xf) < 0.01]
part = chamfer(cross_edges, 0.3)

# Teardrop roofs (45 deg) on the build-up side of both cross holes so they print without support
part = part - teardrop_peak(HEATER_D / 2, 2 * BODY_D, HEATER_OFFSET, HEATER_Z)
part = part - Pos(therm_x, 0, 0) * teardrop_peak(THERM_D / 2, therm_len, THERM_OFFSET, THERM_Z)

# ---- threads ----
def fuse_thread(base, thread, loc):
    """OCC booleans on helical solids are touchy about exact coincidences; retry with tiny angle/position nudges (<=0.03 mm)."""
    for ang in (0, 37, 111, 200, 290):
        for dz in (0.0, 0.013, 0.027):
            out = base + loc * Pos(0, 0, dz) * Rot(0, 0, ang) * thread
            if out.volume > base.volume:
                return out
    raise RuntimeError("thread fuse failed")


# Internal M6x1.0 set-screw threads first (cleanest base for the fuse); only the part below each cross hole
heater_set_len = HEATER_Z - HEATER_D / 2 * 2 ** 0.5 - 0.3      # stops short of the heater teardrop point
therm_set_len = THERM_Z - THERM_D / 2 * 2 ** 0.5 - 0.3
part = fuse_thread(part, IsoThread(major_diameter=SET_MAJOR, pitch=SET_PITCH, length=therm_set_len, external=False,
                                   end_finishes=("fade", "fade")), Pos(THERM_SET_X, THERM_OFFSET, 0))
part = fuse_thread(part, IsoThread(major_diameter=SET_MAJOR, pitch=SET_PITCH, length=heater_set_len - 0.3, external=False,
                                   end_finishes=("fade", "fade")), Pos(0, HEATER_OFFSET, 0.3))
# Internal M12x1.0 in the top bore (teeth fused inside the major-radius bore)
part = fuse_thread(part, IsoThread(major_diameter=M12_MAJOR, pitch=1.0, length=M12_DEPTH, external=False,
                                   end_finishes=("fade", "fade")), Pos(0, 0, z_m12))
# External M6x1.0 on the stub: chamfered at the tip, fades out just below the shoulder
part = fuse_thread(part, IsoThread(major_diameter=M6_MAJOR, pitch=1.0, length=STUB_L - 0.5, external=True,
                                   end_finishes=("chamfer", "fade")), Pos(0, 0, z_tip))


out = Path(__file__).with_suffix("")
export_step(part, str(out) + ".step")
export_stl(part, str(out) + ".stl")
print("valid:", part.is_valid, " volume: %.1f mm3" % part.volume, " solids:", len(part.solids()))
print("wrote", str(out) + ".step", "and .stl")
