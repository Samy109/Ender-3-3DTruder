"""
Drawing BC-001 for the heated barrel coupler (matplotlib). Matches barrel_coupler.py and shop_order.md.

Run:  python make_drawing.py   -> barrel_coupler_drawing.pdf next to this file

Model axes as in barrel_coupler.py: Z is the part axis (shoulder z = 0, top z = 40, stub tip z = -15),
the heater hole runs along X at Y = +6.5, the thermistor hole along X at Y = -6.5.
Views are third-angle: section A-A and view C look from +X (+Y to the right), view B looks down
from +Z, view D looks up at the shoulder face from -Z.
"""
from math import cos, pi, sin, sqrt
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle, Polygon, Rectangle

# ---- geometry (mm), same numbers as barrel_coupler.py ----
BODY_R, BODY_L, CH = 12.5, 40.0, 0.5
STUB_R, STUB_L, STUB_MINOR_R = 3.0, 15.0, 0.5 * (6.0 - 1.2269)
RELIEF_R, RELIEF_L = 2.4, 1.5
BORE_R, STUB_BORE_R = 1.5, 1.0
M12_MAJOR_R, M12_DRILL_R, M12_THREAD, M12_DRILL_DEPTH = 6.0, 5.5, 14.0, 18.0
FLAT, FLAT_Z0, FLAT_Z1 = 11.0, 20.0, 26.0
HEATER_R, HEATER_Y, HEATER_Z = 3.0, 6.5, 7.0
THERM_R, THERM_Y, THERM_Z, THERM_DEPTH = 1.5, -6.5, 15.0, 16.0
SET_DRILL_R, SET_MAJOR_R = 1.25, 1.5
X_SURFACE = sqrt(BODY_R ** 2 - THERM_Y ** 2)
THERM_SET_X = X_SURFACE - 4                       # thermistor set screw sits 4 mm in from the +X surface
z_floor = BODY_L - M12_DRILL_DEPTH                # 22: end of the Ø11 wall
z_cone = z_floor - (M12_DRILL_R - BORE_R)         # 90° cone down to the bore
z_thread = BODY_L - M12_THREAD                    # 26

THICK, THIN, DIMW = 0.9, 0.35, 0.3
FS, FS_SMALL, FS_TITLE = 6.5, 5.5, 8.5
plt.rcParams.update({"font.family": "DejaVu Sans", "hatch.linewidth": 0.35, "pdf.fonttype": 42})

fig = plt.figure(figsize=(420 / 25.4, 297 / 25.4))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 420)
ax.set_ylim(0, 297)
ax.set_aspect("equal")
ax.axis("off")


# ---- drawing helpers ----
def view(x0, y0, s):
    return lambda u, v: (x0 + s * u, y0 + s * v)


def poly(pts, **kw):
    kw.setdefault("lw", THICK)
    kw.setdefault("fill", False)
    ax.add_patch(Polygon(pts, closed=True, joinstyle="miter", **kw))


def line(p, q, lw=THIN, ls="-", color="k", **kw):
    ax.plot([p[0], q[0]], [p[1], q[1]], color=color, lw=lw, ls=ls, solid_capstyle="butt", **kw)


def text(x, y, s, size=FS, ha="left", va="center", **kw):
    ax.text(x, y, s, fontsize=size, ha=ha, va=va, **kw)


def centerline(p, q):
    line(p, q, lw=THIN, ls=(0, (12, 3, 2, 3)))


def arrow(tip, tail):
    ax.annotate("", xy=tip, xytext=tail,
                arrowprops=dict(arrowstyle="-|>,head_length=0.7,head_width=0.22", lw=DIMW, color="k",
                                shrinkA=0, shrinkB=0))


def dim_v(x, y1, y2, label, ext_from=None, side="right"):
    """Vertical dimension at page x between page y1 and y2. ext_from = page x the extension lines start at."""
    if ext_from is not None:
        for y in (y1, y2):
            line((ext_from, y), (x + (1.5 if x > ext_from else -1.5), y), lw=DIMW)
    arrow((x, y1), ((x, (y1 + y2) / 2)))
    arrow((x, y2), ((x, (y1 + y2) / 2)))
    if side == "right":
        text(x + 1.2, (y1 + y2) / 2, label, ha="left")
    else:
        text(x - 1.2, (y1 + y2) / 2, label, ha="right")


def dim_h(y, x1, x2, label, ext_from=None):
    if ext_from is not None:
        for x in (x1, x2):
            line((x, ext_from), (x, y + (1.5 if y > ext_from else -1.5)), lw=DIMW)
    arrow((x1, y), ((x1 + x2) / 2, y))
    arrow((x2, y), ((x1 + x2) / 2, y))
    text((x1 + x2) / 2, y + 1.6, label, ha="center", va="bottom")


def callout(target, at, lines_, ha="left"):
    """Leader from text at `at` to a dot on `target`."""
    ax.plot([at[0], target[0]], [at[1], target[1]], color="k", lw=DIMW)
    ax.add_patch(Circle(target, 0.45, color="k"))
    text(at[0] + (1.0 if ha == "left" else -1.0), at[1], "\n".join(lines_), ha=ha, size=FS, linespacing=1.25)


def teardrop(cx, cy, r, s, P):
    """Circle of radius r with a 45° roof whose point aims toward -Z (the shoulder), in page coords via P."""
    pts = []
    for i in range(0, 61):                       # arc from -45° counter-clockwise round to 225°
        a = (-45 + 270 * i / 60) * pi / 180
        pts.append(P(cx + r * cos(a), cy + r * sin(a)))
    pts.append(P(cx, cy - r * sqrt(2)))
    return pts


def thread_arc(c, r, lw=THIN):
    """Three-quarter thin circle: end-view symbol for a thread."""
    ax.add_patch(Arc(c, 2 * r, 2 * r, theta1=100, theta2=370, lw=lw))


# =====================================================================================
# SECTION A-A (plane X = 0, viewed from +X), scale 3:1
# =====================================================================================
S = 3.0
SX, SY = 122.0, 68.0
P = view(SX, SY, S)

half = [
    (STUB_BORE_R, -STUB_L), (STUB_R, -STUB_L), (STUB_R, -RELIEF_L), (RELIEF_R, -RELIEF_L), (RELIEF_R, 0),
    (BODY_R - CH, 0), (BODY_R, CH), (BODY_R, FLAT_Z0), (FLAT, FLAT_Z0), (FLAT, FLAT_Z1), (BODY_R, FLAT_Z1),
    (BODY_R, BODY_L - CH), (BODY_R - CH, BODY_L), (M12_MAJOR_R + CH, BODY_L), (M12_DRILL_R, BODY_L - 1.0),
    (M12_DRILL_R, z_floor), (BORE_R, z_cone), (BORE_R, 0), (STUB_BORE_R, 0),
]
for sgn in (1, -1):
    pts = [P(sgn * y, z) for y, z in half]
    poly(pts, fill=False, hatch="////", lw=THICK)

# Holes cut by the section (white over the hatch)
poly(teardrop(HEATER_Y, HEATER_Z, HEATER_R, S, P), facecolor="white", fill=True, edgecolor="k", lw=THICK)
poly(teardrop(THERM_Y, THERM_Z, THERM_R, S, P), facecolor="white", fill=True, edgecolor="k", lw=THICK)
# Heater set screw (lies in the section plane): Ø2.5 tap drill from the shoulder up into the heater hole
set_top = HEATER_Z - HEATER_R * sqrt(2) + 0.6
ax.add_patch(Rectangle(P(HEATER_Y - SET_DRILL_R, 0), 2 * S * SET_DRILL_R, S * set_top,
                       facecolor="white", edgecolor="none", zorder=3))
for sgn in (1, -1):
    line(P(HEATER_Y + sgn * SET_DRILL_R, 0), P(HEATER_Y + sgn * SET_DRILL_R, HEATER_Z - HEATER_R * 1.2), lw=THICK, zorder=4)
    line(P(HEATER_Y + sgn * SET_MAJOR_R, 0), P(HEATER_Y + sgn * SET_MAJOR_R, HEATER_Z - HEATER_R * 1.25), lw=THIN, zorder=4)
line(P(HEATER_Y - SET_DRILL_R, 0), P(HEATER_Y + SET_DRILL_R, 0), lw=THICK, color="white", zorder=4)

# Thread convention lines: M12 major (internal, thin), M6 minor (external, thin)
for sgn in (1, -1):
    line(P(sgn * M12_MAJOR_R, BODY_L - CH), P(sgn * M12_MAJOR_R, z_thread))
    line(P(sgn * STUB_MINOR_R, -STUB_L), P(sgn * STUB_MINOR_R, -RELIEF_L))
line(P(-M12_MAJOR_R, z_thread), P(M12_MAJOR_R, z_thread))          # end of full thread
line(P(-STUB_R, -RELIEF_L), P(STUB_R, -RELIEF_L))                   # end of stub thread
centerline(P(0, -STUB_L - 3), P(0, BODY_L + 4))
centerline(P(HEATER_Y - HEATER_R - 2, HEATER_Z), P(HEATER_Y + HEATER_R + 2, HEATER_Z))
centerline(P(THERM_Y - THERM_R - 2, THERM_Z), P(THERM_Y + THERM_R + 2, THERM_Z))

text(SX, P(0, BODY_L)[1] + 26, "SECTION A-A", size=FS_TITLE, ha="center", weight="bold")
text(SX, P(0, BODY_L)[1] + 21.5, "PLANE X = 0, VIEWED FROM +X    SCALE 3:1", size=FS_SMALL, ha="center")

# Dimensions
top = P(0, BODY_L)[1]
dim_h(top + 10, P(-BODY_R, 0)[0], P(BODY_R, 0)[0], "Ø25", ext_from=top)
xl = P(-BODY_R, 0)[0]
dim_v(xl - 22, P(0, 0)[1], P(0, BODY_L)[1], "40", ext_from=xl, side="left")
dim_v(xl - 12, P(0, FLAT_Z0)[1], P(0, FLAT_Z1)[1], "6", ext_from=P(-FLAT, 0)[0], side="left")
dim_v(P(-STUB_R, 0)[0] - 14, P(0, -STUB_L)[1], P(0, 0)[1], "15", ext_from=P(-STUB_R, 0)[0], side="left")
xr = P(BODY_R, 0)[0]
dim_v(xr + 10, P(0, 0)[1], P(0, HEATER_Z)[1], "7", ext_from=xr)
dim_v(xr + 20, P(0, 0)[1], P(0, THERM_Z)[1], "15", ext_from=xr)
dim_v(xr + 10, P(0, z_thread)[1], P(0, BODY_L)[1], "14 FULL THREAD", ext_from=xr)
dim_v(xr + 34, P(0, z_floor)[1], P(0, BODY_L)[1], "18", ext_from=xr)

# Callouts, left
lx = 18
callout(P(-M12_DRILL_R, 34), (lx + 52, P(0, 34)[1]), ["M12x1.0-6H x 14 FULL THREAD", "Ø11.0 x 18 DEEP, 90° CONE FLOOR"], ha="right")
callout(P(-(M12_MAJOR_R + 0.25), BODY_L - 0.25), (lx + 52, P(0, 43)[1]), ["0.5 x 45° CHAMFER"], ha="right")
callout(P(THERM_Y - THERM_R * 0.7, THERM_Z + THERM_R * 0.7), (lx + 52, P(0, 17)[1]),
        ["THERMISTOR Ø3.0 +0.05/0 x 16 DEEP FROM +X", "Y -6.5, 15 FROM SHOULDER"], ha="right")
callout(P(-BORE_R, 9), (lx + 52, P(0, 8)[1]), ["Ø3.0 +0.1/0 BODY BORE"], ha="right")
callout(P(-STUB_BORE_R, -9), (lx + 52, P(0, -8)[1]), ["Ø2.0 +0.1/0 STUB BORE, THRU"], ha="right")

# Callouts, right
rx = xr + 46
callout(P(FLAT, 23), (rx, P(0, 23)[1]), ["22 A/F FLATS, Z 20-26 (VIEW B)"])
callout(P(HEATER_Y + HEATER_R * 0.7, HEATER_Z + HEATER_R * 0.7), (rx, P(0, 9.5)[1]),
        ["HEATER Ø6.0 +0.05/+0.02 THRU", "Y +6.5, 7 FROM SHOULDER"])
callout(P(HEATER_Y, HEATER_Z - HEATER_R * sqrt(2) + 0.2), (rx, P(0, 3.2)[1]),
        ["45° TEARDROP ROOFS ON BOTH", "CROSS HOLES (PRINT, NOTE 3)"])
callout(P(HEATER_Y + SET_MAJOR_R, 1.0), (rx, P(0, -3.0)[1]),
        ["M3x0.5 SET SCREW, 2 PL (VIEW D)", "PRINT Ø2.5, TAP AFTER PRINT"])
callout(P(RELIEF_R, -0.8), (rx, P(0, -8.5)[1]), ["RELIEF Ø4.8 x 1.5"])
callout(P(STUB_R, -10), (rx, P(0, -13.5)[1]), ["M6x1.0-6g x 15, FULL LENGTH"])
text(SX, P(0, -STUB_L)[1] - 5, "STUB END FACE: FLAT, PERPENDICULAR TO AXIS 0.02 (SEALING FACE)", size=FS_SMALL, ha="center")

# =====================================================================================
# VIEW C (from +X), scale 1.5:1
# =====================================================================================
s2 = 1.5
CX, CY = 300.0, 128.0
Q = view(CX, CY, s2)
outline = [
    (-STUB_R, -STUB_L), (STUB_R, -STUB_L), (STUB_R, -RELIEF_L), (RELIEF_R, -RELIEF_L), (RELIEF_R, 0),
    (BODY_R - CH, 0), (BODY_R, CH), (BODY_R, FLAT_Z0), (FLAT, FLAT_Z0), (FLAT, FLAT_Z1), (BODY_R, FLAT_Z1),
    (BODY_R, BODY_L - CH), (BODY_R - CH, BODY_L), (-(BODY_R - CH), BODY_L), (-BODY_R, BODY_L - CH),
    (-BODY_R, FLAT_Z1), (-FLAT, FLAT_Z1), (-FLAT, FLAT_Z0), (-BODY_R, FLAT_Z0), (-BODY_R, CH),
    (-(BODY_R - CH), 0), (-RELIEF_R, 0), (-RELIEF_R, -RELIEF_L), (-STUB_R, -RELIEF_L),
]
poly([Q(y, z) for y, z in outline])
for z in (CH, BODY_L - CH):
    line(Q(-BODY_R, z), Q(BODY_R, z))
line(Q(-STUB_R, -RELIEF_L), Q(STUB_R, -RELIEF_L))
for sgn in (1, -1):
    line(Q(sgn * STUB_MINOR_R, -STUB_L), Q(sgn * STUB_MINOR_R, -RELIEF_L))
poly(teardrop(HEATER_Y, HEATER_Z, HEATER_R, s2, Q))
poly(teardrop(THERM_Y, THERM_Z, THERM_R, s2, Q))
centerline(Q(0, -STUB_L - 2), Q(0, BODY_L + 2))
text(CX, Q(0, BODY_L)[1] + 9, "VIEW C (FROM +X)", size=FS_TITLE, ha="center", weight="bold")
text(CX, Q(0, BODY_L)[1] + 4.5, "SCALE 1.5:1", size=FS_SMALL, ha="center")
callout(Q(HEATER_Y + HEATER_R * 0.7, HEATER_Z + HEATER_R * 0.7), (CX + 27, Q(0, 10)[1]), ["HEATER Ø6 THRU", "Y +6.5, Z 7"])
callout(Q(THERM_Y + THERM_R * 0.7, THERM_Z + THERM_R * 0.7), (CX + 27, Q(0, 19)[1]), ["THERMISTOR Ø3 x 16", "Y -6.5, Z 15"])
callout(Q(BODY_R, 33), (CX + 27, Q(0, 33)[1]), ["Ø25 ROUND ABOVE FLATS", "FOR SK25 CLAMP"])

# =====================================================================================
# VIEW B (top, from +Z), scale 1.5:1. Page right = +Y, page up = -X (third angle, above view C)
# =====================================================================================
BX, BY = 300.0, 238.0
c = (BX, BY)
ax.add_patch(Circle(c, s2 * BODY_R, fill=False, lw=THICK))
ax.add_patch(Circle(c, s2 * (BODY_R - CH), fill=False, lw=THIN))
ax.add_patch(Circle(c, s2 * (M12_MAJOR_R + CH), fill=False, lw=THIN))
ax.add_patch(Circle(c, s2 * M12_DRILL_R, fill=False, lw=THICK))
thread_arc(c, s2 * M12_MAJOR_R)
ax.add_patch(Circle(c, s2 * BORE_R, fill=False, lw=THICK))
for sgn in (1, -1):                                              # flats are below the round: hidden
    h = sqrt(BODY_R ** 2 - FLAT ** 2)
    line((BX + sgn * s2 * FLAT, BY - s2 * h), (BX + sgn * s2 * FLAT, BY + s2 * h), ls=(0, (3, 1.5)))
centerline((BX - s2 * BODY_R - 4, BY), (BX + s2 * BODY_R + 4, BY))
centerline((BX, BY - s2 * BODY_R - 4), (BX, BY + s2 * BODY_R + 4))
dim_h(BY - s2 * BODY_R - 7, BX - s2 * FLAT, BX + s2 * FLAT, "22 A/F", ext_from=BY - s2 * 4)
# Section A-A cut line (plane X = 0 is the horizontal centre line here; arrows look toward -X = page up)
for sgn in (1, -1):
    xe = BX + sgn * (s2 * BODY_R + 9)
    line((xe - sgn * 4, BY), (xe, BY), lw=THICK)
    arrow((xe, BY + 5), (xe, BY))
    text(xe + sgn * 1.5, BY + 6.5, "A", size=FS, ha="left" if sgn > 0 else "right", weight="bold")
text(BX, BY + s2 * BODY_R + 11, "VIEW B (TOP, FROM +Z)", size=FS_TITLE, ha="center", weight="bold")
text(BX, BY + s2 * BODY_R + 6.5, "SCALE 1.5:1", size=FS_SMALL, ha="center")
callout((BX + s2 * M12_DRILL_R * 0.71, BY + s2 * M12_DRILL_R * 0.71), (BX + 32, BY + 12), ["M12x1.0-6H x 14", "Ø11.0 x 18 DEEP"])
callout((BX + s2 * BORE_R * 0.71, BY - s2 * BORE_R * 0.71), (BX + 32, BY - 2), ["Ø3.0 BORE"])
text(BX + 33, BY - 11, "FLATS HIDDEN (BELOW Ø25 ROUND)", size=FS_SMALL)

# =====================================================================================
# VIEW D (shoulder face, from -Z), scale 1.5:1. Page right = +Y, page up = +X (below view C)
# =====================================================================================
DX, DY = 300.0, 70.0
d = (DX, DY)
R = lambda x, y: (DX + s2 * y, DY + s2 * x)
ax.add_patch(Circle(d, s2 * BODY_R, fill=False, lw=THICK))
ax.add_patch(Circle(d, s2 * (BODY_R - CH), fill=False, lw=THIN))
ax.add_patch(Circle(d, s2 * STUB_R, fill=False, lw=THICK))
thread_arc(d, s2 * STUB_MINOR_R)
ax.add_patch(Circle(d, s2 * STUB_BORE_R, fill=False, lw=THICK))
for (x, y) in ((0.0, HEATER_Y), (THERM_SET_X, THERM_Y)):
    ax.add_patch(Circle(R(x, y), s2 * SET_DRILL_R, fill=False, lw=THICK))
    thread_arc(R(x, y), s2 * SET_MAJOR_R)
    centerline((R(x, y)[0] - 4, R(x, y)[1]), (R(x, y)[0] + 4, R(x, y)[1]))
    centerline((R(x, y)[0], R(x, y)[1] - 4), (R(x, y)[0], R(x, y)[1] + 4))
centerline((DX - s2 * BODY_R - 4, DY), (DX + s2 * BODY_R + 4, DY))
centerline((DX, DY - s2 * BODY_R - 4), (DX, DY + s2 * BODY_R + 4))
text(DX, DY + s2 * BODY_R + 11, "VIEW D (SHOULDER FACE, FROM -Z)", size=FS_TITLE, ha="center", weight="bold")
text(DX, DY + s2 * BODY_R + 6.5, "SCALE 1.5:1    +X UP", size=FS_SMALL, ha="center")
callout(R(0.0, HEATER_Y + SET_MAJOR_R * 0.7), (DX + 32, DY + 6),
        ["M3x0.5 TO HEATER HOLE", "X 0, Y +6.5, 7 DEEP"])
callout(R(THERM_SET_X + SET_MAJOR_R * 0.7, THERM_Y), (DX - 32, DY + 14),
        ["M3x0.5 TO THERMISTOR HOLE", "X +%.2f, Y -6.5, 15 DEEP" % THERM_SET_X], ha="right")
callout(R(-STUB_R * 0.71, STUB_R * 0.71), (DX + 32, DY - 8), ["M6 STUB END (SEALING FACE)", "Ø2.0 BORE"])

# =====================================================================================
# Notes, title block, border
# =====================================================================================
notes = [
    "1. MATERIAL: 316L STAINLESS STEEL, METAL 3D PRINTED (SLM). NO ALUMINIUM (280 °C SERVICE).",
    "2. GENERAL TOLERANCE ±0.1 UNLESS NOTED. BREAK SHARP EDGES 0.3-0.5. 0.3 x 45° CHAMFER ON HEATER AND THERMISTOR HOLE ENTRIES.",
    "3. PRINT AXIS VERTICAL, TOP (M12) FACE ON THE PLATE, STUB UP. CROSS HOLES HAVE 45° TEARDROP ROOFS POINTING TO THE SHOULDER; M12 HOLE FLOOR IS A 90° CONE.",
    "4. CAD: barrel_coupler.step HAS ALL THREADS MODELLED; barrel_coupler_nothreads.step HAS A PLAIN Ø6 STUB AND Ø11 / Ø2.5 HOLES.",
    "5. AFTER STRESS RELIEF AND SUPPORT REMOVAL: FACE THE STUB END SQUARE, CHASE M6 (DIE) AND M12 (TAP), TAP BOTH M3x0.5 FROM Ø2.5, REAM HEATER HOLE IF UNDERSIZE.",
    "6. CONCENTRICITY M12 BORE TO M6 STUB: 0.05 TIR.",
    "7. BORE MUST NOT BREAK INTO EITHER CROSS HOLE (2.0 MIN WALL TO HEATER HOLE). STUB WALL 1.39 MIN AT THE M6 ROOT.",
    "8. HEATER AND THERMISTOR HOLES RUN PARALLEL TO X, PERPENDICULAR TO THE AXIS, ON OPPOSITE SIDES OF IT.",
    "9. DEBURR THE BORE BOTH ENDS. LEAVE Ø25 ROUND ABOVE THE FLATS FOR AN SK25 SHAFT CLAMP. CUSTOMER SUPPLIES M12x1.0 TAP IF NEEDED.",
    "10. INSPECT: M6x1.0 NUT RUNS FULL STUB; M12x1.0 TAP OR GAUGE RUNS 14 DEEP; 6 mm CARTRIDGE SLIDES IN; CLEAR SIGHT LINE THROUGH THE BORE.",
    "11. THREADS SHOWN BY CONVENTION. THIRD-ANGLE PROJECTION. WHERE THIS DRAWING AND shop_order.md DIFFER, THE SHOP ORDER GOVERNS.",
]
text(16, 280, "NOTES (UNITS: mm)", size=FS_TITLE, weight="bold")
for i, n in enumerate(notes):
    text(16, 274 - i * 4.6, n, size=FS)

ax.add_patch(Rectangle((8, 8), 404, 281, fill=False, lw=1.4))
tb_x, tb_y, tb_w = 292, 12, 116
ax.add_patch(Rectangle((tb_x, tb_y), tb_w, 32, fill=False, lw=1.0))
line((tb_x, tb_y + 20), (tb_x + tb_w, tb_y + 20), lw=0.6)
line((tb_x, tb_y + 11), (tb_x + tb_w, tb_y + 11), lw=0.6)
line((tb_x + 64, tb_y), (tb_x + 64, tb_y + 11), lw=0.6)
text(tb_x + 3, tb_y + 26, "HEATED BARREL COUPLER", size=10, weight="bold")
text(tb_x + 3, tb_y + 15.5, "316L STAINLESS (SLM)    UNITS mm    QTY 1", size=FS)
text(tb_x + 3, tb_y + 7.3, "CUSTOMER: ADAM HUMPHRIES", size=FS_SMALL)
text(tb_x + 3, tb_y + 3.3, "REF: barrel_coupler.step", size=FS_SMALL)
text(tb_x + 67, tb_y + 7.3, "DWG: BC-001    REV B", size=FS_SMALL)
text(tb_x + 67, tb_y + 3.3, "SCALE: AS NOTED  SHEET 1/1", size=FS_SMALL)

out = Path(__file__).with_name("barrel_coupler_drawing.pdf")
fig.savefig(out, metadata={"Title": "BC-001 Heated Barrel Coupler", "Creator": "make_drawing.py"})
print("wrote", out)
