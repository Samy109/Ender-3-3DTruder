"""
3DTruder heated barrel coupler (build123d + bd_warehouse). Matches shop_order.md, Job 1.

    Barrel tube (12 mm OD, M12x1.0 external thread)
      -> this coupler (second heat zone: 24 V cartridge + thermistor)
      -> M6x1.0 male stub straight into the Super Volcano block (seals on the nozzle)

All threads are modelled (ISO 60 deg profile, right hand, bd_warehouse IsoThread):
  M6x1.0 external stub, M12x1.0 internal top bore, M3x0.5 internal set-screw taps.
Body z runs from the shoulder (z = 0) up; the stub hangs below (z = -15 .. 0).

  Stub:        M6x1.0 full length (z -15 .. -1.5), Ø4.8 x 1.5 relief at the shoulder
  Bore:        Ø3.0 through the body, Ø2.0 through the stub (stub wall >= 1.39 mm)
  Heater zone (body z 0-20, solid except the bore):
    Cartridge: Ø6.0 cross hole, through, 6.5 mm off-axis, at z = 7   (24 V 40 W, 6 x 20 mm)
    Thermistor: Ø3.0 cross hole, 16 deep, 6.5 mm off-axis (opposite side), at z = 15
    Set screws: M3x0.5 tapped up from the shoulder face into each hole
  Flats:       22 mm across, body z 20-26
  Top:         M12x1.0 internal thread, 14 full thread (z 26-40), hole drilled 18 deep (floor z 22); round Ø25 here for an SK25 clamp
Material: 316L stainless, metal 3D printed (SLM). Not aluminium.

Run:  python barrel_coupler.py              -> barrel_coupler.step / .stl (all threads modelled)
      python barrel_coupler.py --no-threads -> barrel_coupler_nothreads.step / .stl (plain Ø6 stub, Ø11 and Ø2.5 tap-drill holes)
"""
import sys
from pathlib import Path

from build123d import Align, Axis, Box, GeomType, Plane, Polygon, chamfer, extrude, BuildLine, BuildPart, BuildSketch, Cylinder, Polyline, Pos, Rot, export_step, export_stl, make_face, revolve
from bd_warehouse.thread import IsoThread

THREADS = "--no-threads" not in sys.argv
BODY_D, BODY_L = 25.0, 40.0
STUB_D, STUB_L = 6.0, 15.0
RELIEF_D, RELIEF_L = 4.8, 1.5
M12_MAJOR, M12_DEPTH = 12.0, 14.0               # M12_DEPTH = full-thread length
M12_DRILL_DEPTH = 18.0                           # hole drilled 4 mm past the full thread so a taper/plug tap can reach full thread
BORE = 3.0
FLATS, FLATS_Z0, FLATS_Z1 = 22.0, 20.0, 26.0
HEATER_D, HEATER_OFFSET, HEATER_Z = 6.0, 6.5, 7.0
THERM_D, THERM_OFFSET, THERM_Z, THERM_DEPTH = 3.0, -6.5, 15.0, 16.0
SET_MAJOR = 3.0
CH = 0.5

R, rr, rb = BODY_D / 2, RELIEF_D / 2, BORE / 2
STUB_BORE = 2.0                                  # bore through the stub only: keeps >= 1.39 mm wall under the M6 thread root
rbs = STUB_BORE / 2
r_root6 = 0.5 * (STUB_D - 1.2269 * 1.0) if THREADS else STUB_D / 2          # M6x1.0 external root radius (thread ridge overlaps into this core)
r_m12 = M12_MAJOR / 2 if THREADS else 5.5                            # hole is bored to the major radius; thread teeth are fused inside
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

# M3 set-screw holes (bored to the major radius), up from the shoulder face into each hole
x_set = x_surface - 4
part = part - Pos(0, HEATER_OFFSET, HEATER_Z / 2) * Cylinder((SET_MAJOR if THREADS else 2.5) / 2, HEATER_Z)
part = part - Pos(x_set, THERM_OFFSET, THERM_Z / 2) * Cylinder((SET_MAJOR if THREADS else 2.5) / 2, THERM_Z)

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


if THREADS:
    # Internal M3x0.5 taps first (cleanest base for the fuse); only the part below each cross hole is threaded
    part = fuse_thread(part, IsoThread(major_diameter=SET_MAJOR, pitch=0.5, length=11.0, external=False,
                                       end_finishes=("fade", "fade")), Pos(x_set, THERM_OFFSET, 0))
    part = fuse_thread(part, IsoThread(major_diameter=SET_MAJOR, pitch=0.5, length=HEATER_Z - HEATER_D / 2 - 0.5, external=False,
                                       end_finishes=("fade", "fade")), Pos(0, HEATER_OFFSET, 0))
    # Internal M12x1.0 in the top bore (teeth fused inside the major-radius bore)
    part = fuse_thread(part, IsoThread(major_diameter=M12_MAJOR, pitch=1.0, length=M12_DEPTH, external=False,
                                       end_finishes=("fade", "fade")), Pos(0, 0, z_m12))
    # External M6x1.0 on the stub: chamfered at the tip, fades out at the relief
    part = fuse_thread(part, IsoThread(major_diameter=STUB_D, pitch=1.0, length=STUB_L - RELIEF_L, external=True,
                                       end_finishes=("chamfer", "fade")), Pos(0, 0, z_tip))


out = Path(__file__).with_suffix("")
if not THREADS:
    out = out.with_name(out.name + "_nothreads")
export_step(part, str(out) + ".step")
export_stl(part, str(out) + ".stl")
print("valid:", part.is_valid, " volume: %.1f mm3" % part.volume, " solids:", len(part.solids()))
print("wrote", str(out) + ".step", "and .stl")
