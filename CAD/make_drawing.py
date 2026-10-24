"""
Drawing BC-001 for the heated barrel coupler (matplotlib). Matches barrel_coupler.py and shop_order.md.

Run:  python make_drawing.py   -> barrel_coupler_drawing.pdf next to this file

Model axes as in barrel_coupler.py: Z is the part axis (shoulder z = 0, top z = 40, stub tip z = -15),
the heater hole runs along X at Y = +6.5, the thermistor hole along X at Y = -6.5, both exiting
through the heater block's wrench flats (normal to X).
Views are third-angle: section A-A and view C look from +X (+Y to the right), view B looks down
from +Z, view D looks up at the shoulder face from -Z.
"""
from math import asin, cos, pi, sin, sqrt
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle, Polygon, Rectangle

# ---- geometry (mm), same numbers as barrel_coupler.py (fits already offset for the ±0.3 print) ----
BODY_R, BODY_L, CH = 12.35, 40.0, 0.5
STUB_R, STUB_L = 2.85, 15.0
STUB_MINOR_R = STUB_R - 0.5 * 1.2269
BORE_R, STUB_BORE_R = 1.5, 0.7
M12_MAJOR_R, M12_THREAD, M12_HOLE_DEPTH = 6.15, 14.0, 18.0
M12_MINOR_R = M12_MAJOR_R - 0.5 * 1.0825
FLAT, BLOCK_Z1, BLOCK_R = 10.85, 26.0, 2.0       # heater block: flats at X = ±10.85, Y faces at ±BODY_R, R2 corners
HEATER_R, HEATER_Y, HEATER_Z = 3.15, 6.5, 7.0
THERM_R, THERM_Y, THERM_Z, THERM_DEPTH = 1.65, -6.5, 15.0, 16.0
SET_MAJOR_R = 3.15
SET_MINOR_R = SET_MAJOR_R - 0.5 * 1.0825
THERM_SET_X = 3.0
z_floor = BODY_L - M12_HOLE_DEPTH                 # 22: end of the plain hole below the thread
z_cone = z_floor - (M12_MAJOR_R - BORE_R)         # 90° cone down to the bore
z_thread = BODY_L - M12_THREAD                    # 26
y_round = sqrt(BODY_R ** 2 - FLAT ** 2)           # 5.9: where the flats meet the Ø24.7 round at z = 26


def corner_cone_edge(n=12):
    """Edge where the 45° corner cone (r = BODY_R + 26 - z) cuts the +X flat: (y, z) from the round to the R2 corner."""
    y_end = BODY_R - BLOCK_R
    return [(y, BLOCK_Z1 - (sqrt(FLAT ** 2 + y ** 2) - BODY_R))
            for y in (y_round + (y_end - y_round) * i / n for i in range(n + 1))]

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
    (STUB_BORE_R, -STUB_L), (STUB_R, -STUB_L), (STUB_R, 0),
    (BODY_R - CH, 0), (BODY_R, CH),
    (BODY_R, BODY_L - CH), (BODY_R - CH, BODY_L), (M12_MAJOR_R + CH, BODY_L),
    (M12_MINOR_R, BODY_L - CH - (M12_MAJOR_R - M12_MINOR_R)), (M12_MINOR_R, z_thread), (M12_MAJOR_R, z_thread),
    (M12_MAJOR_R, z_floor), (BORE_R, z_cone), (BORE_R, 0), (STUB_BORE_R, 0),
]
for sgn in (1, -1):
    pts = [P(sgn * y, z) for y, z in half]
    poly(pts, fill=False, hatch="////", lw=THICK)

# Holes cut by the section (white over the hatch)
poly(teardrop(HEATER_Y, HEATER_Z, HEATER_R, S, P), facecolor="white", fill=True, edgecolor="k", lw=THICK)
poly(teardrop(THERM_Y, THERM_Z, THERM_R, S, P), facecolor="white", fill=True, edgecolor="k", lw=THICK)
# Heater set screw (lies in the section plane): Ø2.5 tap drill from the shoulder up into the heater hole
set_top = HEATER_Z - HEATER_R * sqrt(2) + 0.6
ax.add_patch(Rectangle(P(HEATER_Y - SET_MINOR_R, 0), 2 * S * SET_MINOR_R, S * set_top,
                       facecolor="white", edgecolor="none", zorder=3))
for sgn in (1, -1):
    line(P(HEATER_Y + sgn * SET_MINOR_R, 0), P(HEATER_Y + sgn * SET_MINOR_R, HEATER_Z - HEATER_R * 1.2), lw=THICK, zorder=4)
    line(P(HEATER_Y + sgn * SET_MAJOR_R, 0), P(HEATER_Y + sgn * SET_MAJOR_R, HEATER_Z - HEATER_R * 1.3), lw=THIN, zorder=4)
line(P(HEATER_Y - SET_MINOR_R, 0), P(HEATER_Y + SET_MINOR_R, 0), lw=THICK, color="white", zorder=4)

# Thread convention lines: M12 major (internal, thin), M6 minor (external, thin)
for sgn in (1, -1):
    line(P(sgn * M12_MAJOR_R, BODY_L - CH), P(sgn * M12_MAJOR_R, z_thread))
    line(P(sgn * STUB_MINOR_R, -STUB_L), P(sgn * STUB_MINOR_R, 0))
line(P(-M12_MAJOR_R, z_thread), P(M12_MAJOR_R, z_thread))          # end of full thread
centerline(P(0, -STUB_L - 3), P(0, BODY_L + 4))
centerline(P(HEATER_Y - HEATER_R - 2, HEATER_Z), P(HEATER_Y + HEATER_R + 2, HEATER_Z))
centerline(P(THERM_Y - THERM_R - 2, THERM_Z), P(THERM_Y + THERM_R + 2, THERM_Z))

text(SX, P(0, BODY_L)[1] + 26, "SECTION A-A", size=FS_TITLE, ha="center", weight="bold")
text(SX, P(0, BODY_L)[1] + 21.5, "PLANE X = 0, VIEWED FROM +X    SCALE 3:1", size=FS_SMALL, ha="center")

# Dimensions
top = P(0, BODY_L)[1]
dim_h(top + 10, P(-BODY_R, 0)[0], P(BODY_R, 0)[0], "Ø24.7", ext_from=top)
xl = P(-BODY_R, 0)[0]
dim_v(xl - 22, P(0, 0)[1], P(0, BODY_L)[1], "40", ext_from=xl, side="left")
dim_v(xl - 12, P(0, 0)[1], P(0, BLOCK_Z1)[1], "26", ext_from=xl, side="left")
dim_v(P(-STUB_R, 0)[0] - 14, P(0, -STUB_L)[1], P(0, 0)[1], "15", ext_from=P(-STUB_R, 0)[0], side="left")
xr = P(BODY_R, 0)[0]
dim_v(xr + 10, P(0, 0)[1], P(0, HEATER_Z)[1], "7", ext_from=xr)
dim_v(xr + 20, P(0, 0)[1], P(0, THERM_Z)[1], "15", ext_from=xr)
dim_v(xr + 10, P(0, z_thread)[1], P(0, BODY_L)[1], "14 FULL THREAD", ext_from=xr)
dim_v(xr + 34, P(0, z_floor)[1], P(0, BODY_L)[1], "18", ext_from=xr)

# Callouts, left
lx = 18
callout(P(-M12_MINOR_R, 34), (lx + 52, P(0, 34)[1]), ["M12x1.0 INTERNAL, PRINTED, x 14 FULL THREAD", "MODELLED +0.3 ON DIA (MAJOR 12.3)"], ha="right")
callout(P(-M12_MAJOR_R, 24), (lx + 52, P(0, 27.5)[1]), ["HOLE 18 DEEP, 90° CONE FLOOR"], ha="right")
callout(P(-(M12_MAJOR_R + 0.25), BODY_L - 0.25), (lx + 52, P(0, 43)[1]), ["0.5 x 45° CHAMFER"], ha="right")
callout(P(THERM_Y - THERM_R * 0.7, THERM_Z + THERM_R * 0.7), (lx + 52, P(0, 17)[1]),
        ["THERMISTOR Ø3.3 x 16 DEEP FROM +X", "Y -6.5, 15 FROM SHOULDER"], ha="right")
callout(P(-BORE_R, 9), (lx + 52, P(0, 8)[1]), ["Ø3.0 BODY BORE"], ha="right")
callout(P(-STUB_BORE_R, -9), (lx + 52, P(0, -8)[1]), ["Ø1.4 STUB BORE, THRU (1.5 WALL UNDER M6 ROOT)"], ha="right")

# Callouts, right
rx = xr + 46
callout(P(BODY_R, 23), (rx, P(0, 23)[1]), ["HEATER BLOCK 21.7 x 24.7, Z 0-26", "21.7 A/F FLATS NORMAL TO X (VIEWS C, D)"])
callout(P(HEATER_Y + HEATER_R * 0.7, HEATER_Z + HEATER_R * 0.7), (rx, P(0, 9.5)[1]),
        ["HEATER Ø6.3 THRU", "Y +6.5, 7 FROM SHOULDER"])
callout(P(HEATER_Y, HEATER_Z - HEATER_R * sqrt(2) + 0.2), (rx, P(0, 3.2)[1]),
        ["45° TEARDROP ROOFS ON BOTH", "CROSS HOLES (PRINT, NOTE 3)"])
callout(P(HEATER_Y + SET_MAJOR_R, 1.0), (rx, P(0, -3.0)[1]),
        ["M6x1.0 SET SCREW, PRINTED, 2 PL (VIEW D)", "MODELLED +0.3 ON DIA (MAJOR 6.3)"])
callout(P(STUB_R, -0.6), (rx, P(0, -8.5)[1]), ["THREAD RUNS OUT AT SHOULDER, NO RELIEF"])
callout(P(STUB_R, -10), (rx, P(0, -13.5)[1]), ["M6x1.0 EXTERNAL, PRINTED, FULL LENGTH", "MODELLED -0.3 ON DIA (MAJOR 5.7)"])
text(SX, P(0, -STUB_L)[1] - 5, "STUB END FACE: SEALING FACE, FLAT AS PRINTED (CUSTOMER LAPS IT)", size=FS_SMALL, ha="center")

# =====================================================================================
# VIEW C (from +X), scale 1.5:1
# =====================================================================================
s2 = 1.5
CX, CY = 300.0, 128.0
Q = view(CX, CY, s2)
outline = [
    (-STUB_R, -STUB_L), (STUB_R, -STUB_L), (STUB_R, 0),
    (BODY_R - CH, 0), (BODY_R, CH),
    (BODY_R, BODY_L - CH), (BODY_R - CH, BODY_L), (-(BODY_R - CH), BODY_L), (-BODY_R, BODY_L - CH),
    (-BODY_R, CH), (-(BODY_R - CH), 0), (-STUB_R, 0),
]
poly([Q(y, z) for y, z in outline])
for z in (CH, BODY_L - CH):
    line(Q(-BODY_R, z), Q(BODY_R, z))
line(Q(-y_round, BLOCK_Z1), Q(y_round, BLOCK_Z1), lw=THICK)                  # top of the flat, under the round
edge = corner_cone_edge()
for sgn in (1, -1):
    line(Q(sgn * STUB_MINOR_R, -STUB_L), Q(sgn * STUB_MINOR_R, 0))
    ax.plot(*zip(*[Q(sgn * y, z) for y, z in edge]), color="k", lw=THICK)     # 45° corner chamfers
    line(Q(sgn * (BODY_R - BLOCK_R), CH), Q(sgn * (BODY_R - BLOCK_R), edge[-1][1]))  # R2 corner tangent
poly(teardrop(HEATER_Y, HEATER_Z, HEATER_R, s2, Q))
poly(teardrop(THERM_Y, THERM_Z, THERM_R, s2, Q))
centerline(Q(0, -STUB_L - 2), Q(0, BODY_L + 2))
text(CX, Q(0, BODY_L)[1] + 9, "VIEW C (FROM +X)", size=FS_TITLE, ha="center", weight="bold")
text(CX, Q(0, BODY_L)[1] + 4.5, "SCALE 1.5:1", size=FS_SMALL, ha="center")
callout(Q(HEATER_Y + HEATER_R * 0.7, HEATER_Z + HEATER_R * 0.7), (CX + 27, Q(0, 10)[1]), ["HEATER Ø6.3 THRU", "Y +6.5, Z 7"])
callout(Q(THERM_Y + THERM_R * 0.7, THERM_Z + THERM_R * 0.7), (CX + 27, Q(0, 19)[1]), ["THERMISTOR Ø3.3 x 16", "Y -6.5, Z 15"])
callout(Q(BODY_R, 33), (CX + 27, Q(0, 33)[1]), ["Ø24.7 ROUND ABOVE FLATS", "FOR SK25 CLAMP"])
callout(Q(-2.0, 22.0), (CX - 27, Q(0, 22)[1]), ["21.7 A/F FLAT, Z 0-26", "(22 mm WRENCH), BOTH SIDES"], ha="right")
callout(Q(-edge[6][0], edge[6][1]), (CX - 27, Q(0, 30)[1]), ["45° CORNER CHAMFERS", "INTO THE ROUND"], ha="right")

# =====================================================================================
# VIEW B (top, from +Z), scale 1.5:1. Page right = +Y, page up = -X (third angle, above view C)
# =====================================================================================
BX, BY = 300.0, 238.0
c = (BX, BY)
ax.add_patch(Circle(c, s2 * BODY_R, fill=False, lw=THICK))
ax.add_patch(Circle(c, s2 * (BODY_R - CH), fill=False, lw=THIN))
ax.add_patch(Circle(c, s2 * (M12_MAJOR_R + CH), fill=False, lw=THIN))
ax.add_patch(Circle(c, s2 * M12_MINOR_R, fill=False, lw=THICK))
thread_arc(c, s2 * M12_MAJOR_R)
ax.add_patch(Circle(c, s2 * BORE_R, fill=False, lw=THICK))


def block_outline(inset=0.0, n=8):
    """Heater block footprint (x, y): 21.7 x 24.7, R2 corners, counter-clockwise; optionally inset."""
    pts, r = [], BLOCK_R - inset
    for cx, cy, a0 in ((FLAT - BLOCK_R, BODY_R - BLOCK_R, 0), (-(FLAT - BLOCK_R), BODY_R - BLOCK_R, 90),
                       (-(FLAT - BLOCK_R), -(BODY_R - BLOCK_R), 180), (FLAT - BLOCK_R, -(BODY_R - BLOCK_R), 270)):
        pts += [(cx + r * cos((a0 + 90 * i / n) * pi / 180), cy + r * sin((a0 + 90 * i / n) * pi / 180))
                for i in range(n + 1)]
    return pts + pts[:1]


# Block below the round: the corners outside Ø24.7 are seen (on the 45° chamfers), the rest is hidden.
# Page right = +Y, page up = -X.
blk = block_outline()
for (x0, y0), (x1, y1) in zip(blk, blk[1:]):
    hidden = sqrt(((x0 + x1) / 2) ** 2 + ((y0 + y1) / 2) ** 2) < BODY_R - 0.05
    line((BX + s2 * y0, BY - s2 * x0), (BX + s2 * y1, BY - s2 * x1),
         lw=THIN if hidden else THICK, ls=(0, (3, 1.5)) if hidden else "-")
centerline((BX - s2 * BODY_R - 4, BY), (BX + s2 * BODY_R + 4, BY))
centerline((BX, BY - s2 * BODY_R - 4), (BX, BY + s2 * BODY_R + 4))
dim_h(BY - s2 * BODY_R - 7, BX - s2 * BODY_R, BX + s2 * BODY_R, "24.7", ext_from=BY - s2 * 4)
dim_v(BX - s2 * BODY_R - 18, BY - s2 * FLAT, BY + s2 * FLAT, "21.7 A/F", ext_from=BX - s2 * 4, side="left")
# Section A-A cut line (plane X = 0 is the horizontal centre line here; arrows look toward -X = page up)
for sgn in (1, -1):
    xe = BX + sgn * (s2 * BODY_R + 9)
    line((xe - sgn * 4, BY), (xe, BY), lw=THICK)
    arrow((xe, BY + 5), (xe, BY))
    text(xe + sgn * 1.5, BY + 6.5, "A", size=FS, ha="left" if sgn > 0 else "right", weight="bold")
text(BX, BY + s2 * BODY_R + 11, "VIEW B (TOP, FROM +Z)", size=FS_TITLE, ha="center", weight="bold")
text(BX, BY + s2 * BODY_R + 6.5, "SCALE 1.5:1", size=FS_SMALL, ha="center")
callout((BX + s2 * M12_MINOR_R * 0.71, BY + s2 * M12_MINOR_R * 0.71), (BX + 32, BY + 12), ["M12x1.0 PRINTED x 14", "HOLE 18 DEEP"])
callout((BX + s2 * BORE_R * 0.71, BY - s2 * BORE_R * 0.71), (BX + 32, BY - 2), ["Ø3.0 BORE"])
text(BX + 33, BY - 11, "HEATER BLOCK BELOW Ø24.7 ROUND", size=FS_SMALL)

# =====================================================================================
# VIEW D (shoulder face, from -Z), scale 1.5:1. Page right = +Y, page up = +X (below view C)
# =====================================================================================
DX, DY = 300.0, 70.0
d = (DX, DY)
R = lambda x, y: (DX + s2 * y, DY + s2 * x)
poly([R(x, y) for x, y in blk], lw=THICK)                       # shoulder face (block footprint)
poly([R(x, y) for x, y in block_outline(inset=CH)], lw=THIN)    # inner edge of the 0.5 shoulder chamfer
a_flat = 180 / pi * asin(FLAT / BODY_R)
for a0 in (a_flat, 180 + a_flat):                                # Ø24.7 round showing past the flats (+X up)
    ax.add_patch(Arc(d, 2 * s2 * BODY_R, 2 * s2 * BODY_R, theta1=a0, theta2=a0 + 180 - 2 * a_flat, lw=THICK))
ax.add_patch(Circle(d, s2 * STUB_R, fill=False, lw=THICK))
thread_arc(d, s2 * STUB_MINOR_R)
ax.add_patch(Circle(d, s2 * STUB_BORE_R, fill=False, lw=THICK))
for (x, y) in ((0.0, HEATER_Y), (THERM_SET_X, THERM_Y)):
    ax.add_patch(Circle(R(x, y), s2 * SET_MINOR_R, fill=False, lw=THICK))
    thread_arc(R(x, y), s2 * SET_MAJOR_R)
    centerline((R(x, y)[0] - 4, R(x, y)[1]), (R(x, y)[0] + 4, R(x, y)[1]))
    centerline((R(x, y)[0], R(x, y)[1] - 4), (R(x, y)[0], R(x, y)[1] + 4))
centerline((DX - s2 * BODY_R - 4, DY), (DX + s2 * BODY_R + 4, DY))
centerline((DX, DY - s2 * BODY_R - 4), (DX, DY + s2 * BODY_R + 4))
text(DX, DY + s2 * BODY_R + 11, "VIEW D (SHOULDER FACE, FROM -Z)", size=FS_TITLE, ha="center", weight="bold")
text(DX, DY + s2 * BODY_R + 6.5, "SCALE 1.5:1    +X UP", size=FS_SMALL, ha="center")
callout(R(0.0, HEATER_Y + SET_MAJOR_R * 0.7), (DX + 32, DY + 6),
        ["M6x1.0 TO HEATER HOLE", "X 0, Y +6.5"])
callout(R(THERM_SET_X + SET_MAJOR_R * 0.7, THERM_Y), (DX - 32, DY + 14),
        ["M6x1.0 TO THERMISTOR HOLE", "X +%.1f, Y -6.5" % THERM_SET_X], ha="right")
callout(R(-STUB_R * 0.71, STUB_R * 0.71), (DX + 32, DY - 8), ["M6 STUB END (SEALING FACE)", "Ø1.4 BORE"])

# =====================================================================================
# Notes, title block, border
# =====================================================================================
notes = [  # what JLC3D is asked to hold: print as modelled, ±0.3, nothing finer
    "1. MATERIAL: 316L STAINLESS STEEL, METAL 3D PRINTED (SLM). NO ALUMINIUM (280 °C SERVICE).",
    "2. ALL DIMENSIONS ±0.3 (STANDARD SLM TOLERANCE). NO TIGHTER TOLERANCE APPLIES ANYWHERE ON THIS PART. NO MACHINING REQUIRED.",
    "3. PRINT EXACTLY AS MODELLED IN barrel_coupler.step. ALL FOUR THREADS (M6 STUB, M12, 2x M6 SET SCREW) ARE PRINTED; THEIR FIT IS ALREADY OFFSET IN THE MODEL.",
    "4. PRINT AXIS VERTICAL, TOP (M12) FACE ON THE PLATE, STUB UP. CROSS HOLES HAVE 45° TEARDROP ROOFS; M12 HOLE FLOOR IS A 90° CONE; BLOCK CORNERS 45°. NO INTERNAL SUPPORTS.",
    "5. STRESS RELIEVE, REMOVE FROM PLATE, REMOVE SUPPORTS, BEAD BLAST. KEEP THE BORE, THREADS AND CROSS HOLES CLEAR OF POWDER.",
    "6. HEATER AND THERMISTOR HOLES RUN PARALLEL TO X, ON OPPOSITE SIDES OF THE AXIS, EXITING SQUARE THROUGH THE 21.7 FLATS. 0.3 x 45° CHAMFER ON THEIR ENTRIES.",
    "7. MINIMUM WALL 1.5 EVERYWHERE EXCEPT THREAD TEETH (STUB 1.5 UNDER THE M6 ROOT; 1.85 BORE TO HEATER HOLE).",
    "8. THREADS SHOWN BY CONVENTION. THIRD-ANGLE PROJECTION.",
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
text(tb_x + 67, tb_y + 7.3, "DWG: BC-001    REV D", size=FS_SMALL)
text(tb_x + 67, tb_y + 3.3, "SCALE: AS NOTED  SHEET 1/1", size=FS_SMALL)

out = Path(__file__).with_name("barrel_coupler_drawing.pdf")
fig.savefig(out, metadata={"Title": "BC-001 Heated Barrel Coupler", "Creator": "make_drawing.py"})
print("wrote", out)
