"""
System schematic for the 3DTruder extrusion line (matplotlib). Matches the master manual, amazon_parts_list.md,
Arduino_Firmware.ino, Ender3_Firmware/Configuration.h, barrel_coupler.py and shop_order.md.

Run:  python make_schematic.py   -> 3DTruder_schematic.pdf next to this file

Six A3 landscape sheets: 1 system overview, 2 assembled device, 3 power and heaters, 4 controller, 5 mechanical,
6 wire schedule and settings. Reference designators are the same on every sheet. Anything the build docs don't specify is dashed.
Page coordinates are mm, origin bottom left. Sheet 5's melt-path section is to scale, using barrel_coupler.py's numbers.
"""
from math import sqrt
from pathlib import Path
import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Circle, Polygon, Rectangle

W, H = 420, 297
SHEETS = 6
REV, DATE = "B", "2026-11-01"

FS, FS_SMALL, FS_TINY, FS_HEAD, FS_TITLE = 6.5, 5.6, 5.0, 8.0, 13
LW_WIRE, LW_BUS, LW_BOX = 0.8, 1.6, 0.8

C_24V, C_0V, C_SIG, C_TEMP = "#C62828", "#212121", "#1565C0", "#2E7D32"
C_MAINS, C_9V, C_MOTOR, C_FLOW = "#E65100", "#AD1457", "#6A1B9A", "#6D4C41"
F_POWER, F_ENDER, F_ARDUINO, F_MELT, F_LINE = "#FDECEA", "#FFF3E0", "#E3F2FD", "#FBE9D0", "#F1F3F4"

plt.rcParams.update({"font.family": "DejaVu Sans", "hatch.linewidth": 0.3, "pdf.fonttype": 42})


class Sheet:
    def __init__(self, number, title, subtitle):
        self.fig = plt.figure(figsize=(W / 25.4, H / 25.4))
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, W)
        self.ax.set_ylim(0, H)
        self.ax.set_aspect("equal")
        self.ax.axis("off")
        ax = self.ax
        ax.add_patch(Rectangle((8, 8), W - 16, H - 16, fill=False, lw=1.2))
        self.text(14, 282, title, size=FS_TITLE, weight="bold")
        self.text(14, 275, subtitle, size=FS, color="#444444")
        self.title_block(number, title)

    def title_block(self, number, title):
        x, y, w, h = 272, 8, 140, 24
        self.ax.add_patch(Rectangle((x, y), w, h, fc="white", ec="k", lw=0.8, zorder=5))
        for a, b in (((x, y + 16), (x + w, y + 16)), ((x, y + 8), (x + w, y + 8)), ((x + 88, y), (x + 88, y + 8)),
                     ((x + 112, y), (x + 112, y + 8))):
            self.line(a, b, lw=0.4, zorder=6)
        self.text(x + 3, y + 20, "3DTruder auger-fed filament extrusion line", size=FS_SMALL + 1, weight="bold", zorder=6)
        self.text(x + 3, y + 12, title, size=FS_SMALL, zorder=6)
        self.text(x + 3, y + 4, "Drawn from the build docs and firmware in this repo", size=FS_TINY, zorder=6)
        self.text(x + 91, y + 4, "Rev %s  %s" % (REV, DATE[:7]), size=FS_TINY, zorder=6)
        self.text(x + 115, y + 4, "Sheet %d of %d" % (number, SHEETS), size=FS_TINY, weight="bold", zorder=6)

    # ---- primitives ----
    def line(self, p, q, lw=0.5, color="k", ls="-", zorder=2):
        self.ax.plot([p[0], q[0]], [p[1], q[1]], color=color, lw=lw, ls=ls, solid_capstyle="round", zorder=zorder)

    def wire(self, pts, color=C_0V, lw=LW_WIRE, ls="-", zorder=2):
        self.ax.plot([p[0] for p in pts], [p[1] for p in pts], color=color, lw=lw, ls=ls, zorder=zorder,
                     solid_joinstyle="miter", solid_capstyle="butt")

    def dot(self, x, y, color=C_0V, r=0.75):
        self.ax.add_patch(Circle((x, y), r, fc=color, ec=color, lw=0, zorder=4))

    def text(self, x, y, s, size=FS, ha="left", va="center", **kw):
        return self.ax.text(x, y, s, fontsize=size, ha=ha, va=va, **kw)

    def label(self, x, y, s, size=FS_SMALL, ha="left", va="center", color="k", **kw):
        """Text on a white patch so it stays readable over wires."""
        kw.setdefault("zorder", 7)
        return self.text(x, y, s, size=size, ha=ha, va=va, color=color,
                         bbox=dict(fc="white", ec="none", pad=0.5), **kw)

    def box(self, x, y, w, h, s=None, fc="white", ec="k", lw=LW_BOX, size=FS, ls="-", weight=None, valign="center", zorder=3):
        self.ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, ls=ls, zorder=zorder))
        if s:
            ty = {"center": y + h / 2, "top": y + h - 2.5}[valign]
            self.text(x + w / 2, ty, s, size=size, ha="center", va={"center": "center", "top": "top"}[valign],
                      weight=weight, zorder=zorder + 1, linespacing=1.25)

    def flag(self, x, y, s, w=30, h=9, direction="right", color=C_0V):
        """Off-sheet connector: a pentagon pointing the way the connection leaves."""
        n = 2.5
        pts = {"right": [(x, y), (x + w - n, y), (x + w, y + h / 2), (x + w - n, y + h), (x, y + h)],
               "left": [(x + w, y), (x + n, y), (x, y + h / 2), (x + n, y + h), (x + w, y + h)]}[direction]
        self.ax.add_patch(Polygon(pts, closed=True, fc="white", ec=color, lw=0.7, zorder=3))
        self.text(x + w / 2, y + h / 2, s, size=FS_TINY, ha="center", zorder=4, color=color)

    def callout(self, tip, at, s, ha="left", color="k", size=FS_SMALL, rel=None):
        """Leader from tip to the text. rel = where on the text box it attaches, (0, 0) lower left to (1, 1) upper right."""
        rel = rel or ((0, 0.5) if ha == "left" else (1, 0.5))
        self.ax.annotate(s, xy=tip, xytext=at, fontsize=size, ha=ha, va="center", color=color, zorder=8, linespacing=1.2,
                         arrowprops=dict(arrowstyle="-", lw=0.35, color="#555555", shrinkA=1, shrinkB=0, relpos=rel))

    def arrow(self, tail, tip, color=C_0V, lw=LW_WIRE, ls="-", head=0.45):
        self.ax.annotate("", xy=tip, xytext=tail, zorder=4,
                         arrowprops=dict(arrowstyle="-|>,head_length=%g,head_width=%g" % (head, head * 0.45), lw=lw,
                                         color=color, ls=ls, shrinkA=0, shrinkB=0))

    # ---- schematic symbols ----
    def zigzag(self, x, y, length, vertical=True, color=C_24V, teeth=4, amp=1.8, lw=LW_WIRE):
        """Resistive element starting at (x, y), running down (vertical) or right, with a straight lead each end."""
        lead = length * 0.15
        run = length - 2 * lead
        n = teeth * 2
        off = []
        for i in range(n):
            off.append((lead + run * (i + 0.5) / n, amp if i % 2 else -amp))
        off.append((length - lead, 0))
        off.append((length, 0))
        pts = [(0, 0), (lead, 0)] + off
        if vertical:
            self.wire([(x + a, y - p) for p, a in pts], color=color, lw=lw)
        else:
            self.wire([(x + p, y + a) for p, a in pts], color=color, lw=lw)

    def thermistor(self, x, ytop, length, color=C_TEMP):
        """NTC thermistor, leads along a vertical line."""
        b = length * 0.6
        y0 = ytop - (length - b) / 2
        self.wire([(x, ytop), (x, y0)], color=color)
        self.wire([(x, y0 - b), (x, ytop - length)], color=color)
        self.ax.add_patch(Rectangle((x - 1.7, y0 - b), 3.4, b, fc="white", ec=color, lw=LW_WIRE, zorder=3))
        self.line((x - 3.2, y0 - b - 0.6), (x + 3.2, y0 + 0.6), lw=0.5, color=color, zorder=4)

    def fuse(self, x, ytop, length, color=C_24V):
        y0 = ytop - length
        self.ax.add_patch(Rectangle((x - 1.6, y0), 3.2, length, fc="white", ec=color, lw=LW_WIRE, zorder=3))
        self.line((x, ytop), (x, y0), lw=LW_WIRE, color=color, zorder=4)

    def switch(self, x, ytop, ybot, color=C_0V, ls="-"):
        """Vertical open switch between (x, ytop) and (x, ybot)."""
        self.ax.add_patch(Circle((x, ytop - 1), 0.7, fc="white", ec=color, lw=0.6, zorder=4))
        self.ax.add_patch(Circle((x, ybot + 1), 0.7, fc="white", ec=color, lw=0.6, zorder=4))
        self.line((x, ybot + 1.6), (x + 3.2, ytop - 2.0), lw=LW_WIRE, color=color, zorder=4, ls=ls)

    def fan(self, x, y, r=4.5, color=C_24V, ls="-"):
        self.ax.add_patch(Circle((x, y), r, fc="white", ec=color, lw=LW_WIRE, ls=ls, zorder=3))
        self.line((x - r * 0.65, y - r * 0.4), (x + r * 0.65, y + r * 0.4), lw=0.6, color=color, zorder=4)
        self.line((x - r * 0.65, y + r * 0.4), (x + r * 0.65, y - r * 0.4), lw=0.6, color=color, zorder=4)

    def motor(self, x, y, r=7, color=C_MOTOR, ls="-", s="M"):
        self.ax.add_patch(Circle((x, y), r, fc="white", ec=color, lw=1.0, ls=ls, zorder=3))
        self.text(x, y, s, size=FS + 1, ha="center", weight="bold", color=color, zorder=4)

    def legend(self, x, y, entries, cols=3, dx=64, dy=5.5):
        """Line-style key. entries = (label, color, lw, ls)."""
        for i, (s, color, lw, ls) in enumerate(entries):
            cx, cy = x + (i % cols) * dx, y - (i // cols) * dy
            self.wire([(cx, cy), (cx + 9, cy)], color=color, lw=lw, ls=ls)
            self.text(cx + 11, cy, s, size=FS_TINY + 0.3)

    def notes(self, x, ytop, items, width, size=FS_SMALL, dy=3.6, title=None):
        y = ytop
        if title:
            self.text(x, y, title, size=size + 0.6, weight="bold")
            y -= dy + 0.6
        chars = int(width / (size * 0.196))
        for i, item in enumerate(items, 1):
            lines = textwrap.wrap(item, chars)
            self.text(x, y, "%d." % i, size=size)
            for ln in lines:
                self.text(x + 4, y, ln, size=size)
                y -= dy
            y -= 0.5
        return y

    def table(self, x, ytop, widths, rows, size=FS_TINY + 0.9, dy=4.3, pad=1.3, title=None):
        """Grid table; first row is the header. Cells wrap to their column. Returns the page y of the bottom edge."""
        y = ytop
        if title:
            self.text(x, y + 3, title, size=FS + 0.5, weight="bold")
        total = sum(widths)
        char_w = size * 0.189
        for r, row in enumerate(rows):
            cells = [textwrap.wrap(str(c), max(1, int((w - 2 * pad) / char_w))) or [""] for c, w in zip(row, widths)]
            h = max(len(c) for c in cells) * dy + 1.3
            self.ax.add_patch(Rectangle((x, y - h), total, h, fc="#ECEFF1" if r == 0 else "white", ec="#777777", lw=0.3, zorder=1))
            cx = x
            for c, w in zip(cells, widths):
                self.line((cx, y), (cx, y - h), lw=0.3, color="#777777")
                for i, ln in enumerate(c):
                    self.text(cx + pad, y - 0.65 - dy * (i + 0.5), ln, size=size, weight="bold" if r == 0 else None, zorder=3)
                cx += w
            self.line((cx, y), (cx, y - h), lw=0.3, color="#777777")
            y -= h
        return y


# =========================================================================================================
# Sheet 1: system overview
# =========================================================================================================
def sheet_overview():
    s = Sheet(1, "System overview", "Plastic runs left to right along the top. Two independent controllers run the line: "
              "the Ender mainboard owns heat, the Arduino owns motion.")
    # Material path
    s.text(16, 262, "MATERIAL PATH", size=FS + 0.5, weight="bold", color=C_FLOW)
    stages = [("Feedstock\n1-3 mm flakes\nsieved, dried", F_LINE), ("Hopper\nPET jug over\n15 × 12 window", F_LINE),
              ("Barrel + auger\n10 ID × 12 OD\n3/8 in auger", F_LINE), ("Heated coupler\n316L, ZONE 2\nM12 to M6 stub", F_MELT),
              ("Super Volcano\nblock\nZONE 1", F_MELT), ("Nozzle\n1.4 mm brass", F_MELT), ("Strand cooling\n5-10 cm after\nnozzle", F_LINE),
              ("Diameter\nsensor\n10-20 cm out", F_LINE), ("BMG puller\ndraws down\nto 1.75 mm", F_LINE), ("Spooler\nslip-clutch\nhub", F_LINE)]
    bw, gap, x0, by, bh = 33.0, 6.0, 18.0, 233.0, 24.0
    centers = []
    for i, (t, fc) in enumerate(stages):
        x = x0 + i * (bw + gap)
        s.box(x, by, bw, bh, t, fc=fc, size=FS_SMALL)
        centers.append(x + bw / 2)
        if i:
            s.arrow((x - gap, by + bh / 2), (x, by + bh / 2), color=C_FLOW, lw=1.6, head=0.5)

    bot = by
    # Loads hanging under the material path
    ly = 196
    # FAN1 on the barrel feed end
    s.fan(centers[1] + 8, ly + 6, color=C_24V)
    s.label(centers[1] + 8, ly - 3.5, "FAN1 4010 / 4020\nalways on", ha="center", size=FS_TINY + 0.3)
    s.arrow((centers[1] + 8, ly + 10.5), (centers[1] + 8, bot), color="#777777", lw=0.5)
    # M1 auger
    m1x = centers[2]
    s.motor(m1x, ly + 8)
    s.label(m1x + 9, ly + 8, "M1 14:1\nNEMA 17", size=FS_TINY + 0.3)
    s.wire([(m1x - 0.7, ly + 15), (m1x - 0.7, bot)], color=C_MOTOR, lw=0.6)
    s.wire([(m1x + 0.7, ly + 15), (m1x + 0.7, bot)], color=C_MOTOR, lw=0.6)
    # Heaters and thermistors
    h2x, h1x = centers[3], centers[4]
    s.box(h2x - 15, ly + 1, 30, 14, "H2 40 W\nRT2 100K", fc="white", size=FS_SMALL)
    s.box(h1x - 15, ly + 1, 30, 14, "H1 80 W\nRT1 100K", fc="white", size=FS_SMALL)
    s.arrow((h2x, ly + 15), (h2x, bot), color=C_24V, lw=1.0)
    s.arrow((h1x, ly + 15), (h1x, bot), color=C_24V, lw=1.0)
    # Blowers, sensor, puller, spooler
    s.fan(centers[6] - 6, ly + 8, color=C_24V, ls=":")
    s.fan(centers[6] + 6, ly + 8, color=C_24V, ls=":")
    s.label(centers[6], ly - 1, "FAN2, FAN3\n2 × 5010", ha="center", size=FS_TINY + 0.3)
    s.arrow((centers[6], ly + 13), (centers[6], bot), color="#777777", lw=0.5)
    s.box(centers[7] - 12, ly + 1, 24, 14, "S1 analog\n0-5 V", fc="white", size=FS_SMALL)
    s.wire([(centers[7] - 3, bot), (centers[7] - 3, ly + 15)], color="#777777", lw=0.5)
    s.wire([(centers[7] + 3, bot), (centers[7] + 3, ly + 15)], color="#777777", lw=0.5)
    s.motor(centers[8], ly + 8)
    s.label(centers[8], ly - 3, "M2 5:1 NEMA 17", ha="center", size=FS_TINY + 0.3)
    s.wire([(centers[8] - 0.7, ly + 15), (centers[8] - 0.7, bot)], color=C_MOTOR, lw=0.6)
    s.wire([(centers[8] + 0.7, ly + 15), (centers[8] + 0.7, bot)], color=C_MOTOR, lw=0.6)
    s.motor(centers[9], ly + 8, ls=":")
    s.label(centers[9], ly - 3, "M3 gear motor\n(not bought yet)", ha="center", size=FS_TINY + 0.3)
    s.wire([(centers[9] - 0.7, ly + 15), (centers[9] - 0.7, bot)], color=C_MOTOR, lw=0.6)
    s.wire([(centers[9] + 0.7, ly + 15), (centers[9] + 0.7, bot)], color=C_MOTOR, lw=0.6)

    # Controllers
    cy, ch = 112, 44
    mbx, mbw = 138, 90
    s.box(mbx, cy, mbw, ch, "U2 Ender 3 V2 mainboard (Creality 4.2.2)\nMarlin 2.1.2.4, two PID heat zones\n"
          "Zone 1 hotend channel, 290 °C max\nZone 2 bed channel relabelled Coupler\n10 min melt soak timer, thermal runaway on both", fc=F_ENDER, size=FS)
    s.box(84, cy + 8, 42, 28, "U3 DWIN screen\nand encoder\nMELT READY\nAUGER: OK TO START", fc=F_ENDER, size=FS_TINY + 0.4)
    s.wire([(126, cy + 22), (mbx, cy + 22)], color=C_SIG)
    s.box(278, cy, 124, ch, "U5 Arduino Uno R3 + U6 CNC Shield V3\nFirmware V4, interrupt-driven stepping\n"
          "U7 A4988 on X: puller, 1/16 step\nU8 A4988 on Y: auger, full step, ~0.7 A\n"
          "Closed loop: diameter sets puller speed,\nwaiting out the strand dead time", fc=F_ARDUINO, size=FS)

    # Ender to its heaters. Q1 sits between U2 and H1; its fused feed comes up the right of U2.
    q1x = h1x
    q1y, q1h = 164, 15
    s.box(q1x - 17, q1y, 34, q1h, "Q1 25 A MOSFET\nopto-isolated", fc=F_POWER, size=FS_SMALL)
    s.arrow((q1x, q1y + q1h), (q1x, ly + 1), color=C_24V, lw=1.0)
    s.arrow((q1x, cy + ch), (q1x, q1y), color=C_SIG)
    s.label(q1x + 1.5, cy + ch + 4, "HOTEND output", size=FS_TINY + 0.3, color=C_SIG)
    s.arrow((h2x - 6, cy + ch), (h2x - 6, ly + 1), color=C_24V, lw=1.0)
    s.label(h2x - 7, cy + ch + 4, "BED output", ha="right", size=FS_TINY + 0.3, color=C_24V)
    s.arrow((h2x + 6, ly + 1), (h2x + 6, cy + ch), color=C_TEMP)
    s.label(h2x + 7, cy + ch + 13, "TB", size=FS_TINY + 0.3, color=C_TEMP)
    s.wire([(h1x - 15, ly + 5), (170.5, ly + 5), (170.5, cy + ch + 3)], color=C_TEMP)
    s.arrow((170.5, cy + ch + 3), (170.5, cy + ch), color=C_TEMP)
    s.label(169.5, cy + ch + 13, "TH", ha="right", size=FS_TINY + 0.3, color=C_TEMP)

    # Arduino to its loads
    s.arrow((centers[7], ly + 1), (centers[7], cy + ch), color=C_TEMP)
    s.label(centers[7] + 1, cy + ch + 13, "A0", size=FS_TINY + 0.3, color=C_TEMP)
    s.arrow((centers[8], cy + ch), (centers[8], ly - 5), color=C_MOTOR)
    s.label(centers[8] + 1, cy + ch + 13, "X socket", size=FS_TINY + 0.3, color=C_MOTOR)
    # Auger motor is far left: its cable runs under the mainboard
    ax_ = 300
    route_y = 104
    s.wire([(ax_, cy), (ax_, route_y), (70, route_y), (70, 186), (m1x, 186)], color=C_MOTOR)
    s.arrow((m1x, 186), (m1x, ly + 1), color=C_MOTOR)
    s.label(120, route_y + 3, "Y socket: auger motor cable", size=FS_TINY + 0.3, color=C_MOTOR)

    # No link between the controllers
    s.text(253, cy + 22, "NO DATA\nLINK", size=FS_SMALL, ha="center", weight="bold", color="#B71C1C", zorder=8)
    s.line((233, cy + 22), (243, cy + 22), lw=0.7, color="#B71C1C", ls=(0, (2, 2)))
    s.line((263, cy + 22), (273, cy + 22), lw=0.7, color="#B71C1C", ls=(0, (2, 2)))

    # Power
    s.box(18, 44, 52, 34, "U1 Ender PSU\n24 V, 350 W\n(14.6 A)", fc=F_POWER, size=FS, weight="bold")
    s.box(18, 86, 52, 10, "Mains in, 110 / 220 V", fc=F_POWER, size=FS_SMALL)
    s.arrow((44, 86), (44, 78), color=C_MAINS, lw=1.2)
    bus = 61
    s.wire([(70, bus), (398, bus)], color=C_24V, lw=LW_BUS)
    s.label(74, bus + 3.5, "24 V bus (all loads return to PSU V−, so both controllers share ground)", size=FS_SMALL, color=C_24V)
    for x in (mbx + 12,):
        s.dot(x, bus, C_24V)
        s.arrow((x, bus), (x, cy), color=C_24V, lw=1.0)
    # Q1 feed, fused, clear of U2
    fx = 238
    s.dot(fx, bus, C_24V)
    s.wire([(fx, bus), (fx, q1y + q1h / 2), (q1x + 17, q1y + q1h / 2)], color=C_24V, lw=1.0)
    s.fuse(fx, 92, 8)
    s.label(fx + 3, 88, "F1 5 A", size=FS_TINY + 0.3, color=C_24V)
    # Arduino side
    s.dot(330, bus, C_24V)
    s.box(317, 72, 26, 12, "U4 LM2596\n24 to 9 V", fc=F_POWER, size=FS_TINY + 0.3)
    s.wire([(330, bus), (330, 72)], color=C_24V, lw=1.0)
    s.arrow((330, 84), (330, cy), color=C_9V, lw=1.0)
    s.label(332, 98, "9 V to Uno jack", size=FS_TINY + 0.3, color=C_9V)
    s.dot(382, bus, C_24V)
    s.arrow((382, bus), (382, cy), color=C_24V, lw=1.0)
    s.label(384, 98, "24 V\nPower In", size=FS_TINY + 0.3, color=C_24V)
    # Fans, spooler
    s.dot(394, bus, C_24V)
    s.wire([(394, bus), (394, 50)], color=C_24V, lw=1.0, ls=":")
    s.label(392, 50, "to fans and spooler, sheet 3", ha="right", size=FS_TINY + 0.3, color=C_24V)
    # USB host
    s.box(346, 72, 26, 12, "USB host\nPC or Pi", size=FS_TINY + 0.3, ls=":")
    s.arrow((359, 84), (359, cy), color=C_SIG)
    s.label(361, 98, "USB", size=FS_TINY + 0.3, color=C_SIG)
    # Key
    s.legend(16, 31, [("Heater and motor power", C_24V, 1.0, "-"), ("Control signal", C_SIG, LW_WIRE, "-"),
                      ("Temperature / diameter sense", C_TEMP, LW_WIRE, "-"), ("Stepper drive", C_MOTOR, LW_WIRE, "-"),
                      ("Material flow", C_FLOW, 1.6, "-"), ("Not specified in the docs", C_24V, 1.0, ":")], cols=3, dx=82)
    s.text(16, 17, "The Arduino cannot see temperature. Starting the auger only after AUGER: OK TO START is an operator step, "
           "not an electrical interlock.", size=FS_SMALL, color="#B71C1C", weight="bold")
    s.text(16, 12.5, "Details: sheet 2 assembled device, sheet 3 power and heaters, sheet 4 controller, sheet 5 mechanical, sheet 6 wire schedule.", size=FS_SMALL)
    return s


# =========================================================================================================
# Sheet 2: assembled device
# =========================================================================================================
def sheet_assembled():
    s = Sheet(2, "Fully assembled device", "Every part in its built position at one common scale (about 1:2.25 at A3), "
              "with the electronics and cable runs. Heights and lengths of bought parts are typical values.")
    k, X0, AY, PY = 1 / 2.25, 20.0, 166.0, 76.0
    E = lambda x, h: (X0 + x * k, AY + h * k)        # elevation: x mm from the back of M1, h mm above the strand axis
    N = lambda x, y: (X0 + x * k, PY + y * k)        # plan: same x, y mm across the axis

    def rect(pt, x0, x1, y0, y1, text=None, **kw):
        a = pt(x0, y0)
        kw.setdefault("size", FS_TINY)
        s.box(a[0], a[1], (x1 - x0) * k, (y1 - y0) * k, text, **kw)

    # Stations along the axis, mm. Coupler to nozzle match sheet 5: coupler top face 278, shoulder 318, nozzle tip 364.
    m0, m1, g1, p1, b1, c1 = 0, 48, 95, 99, 108, 138       # motor, gearbox, plate, 51100, shaft coupling
    br0, br1 = 140, 290                                    # barrel, its outlet end inside the coupler
    win = 150                                              # hopper window, 15 long
    cp0, cp1, stub, bl0, bl1, tip = 278, 318, 333, 326, 350, 364
    fan0, fan1 = 178, 218
    blow0, blow1, sens, pull0, pull1, sp, sp_r = 425, 475, 514, 545, 590, 690, 100   # blowers 50-100 and sensor 150 past the tip
    rail_top, rail_bot = -40, -60
    frame_end, rail_end = 470, 720

    # ---- elevation ----
    s.text(16, 266, "ELEVATION", size=FS + 0.5, weight="bold")
    rect(E, 0, frame_end, rail_bot, rail_top, "Ender 3 V2 2020 frame", fc="#D7DBDD")
    rect(E, frame_end, rail_end, rail_bot, rail_top, "Extra rail? See note 1", fc="white", ls=":")
    rect(E, m0, m1, -21, 21, "M1", fc="#90A4AE", size=FS_TINY + 0.3)
    rect(E, m1, g1, -18, 18, "14:1", fc="#B0BEC5", size=FS_TINY + 0.3)
    rect(E, g1, p1, rail_top, 30, fc="#9E9E9E")
    rect(E, p1, b1, -12, 12, fc="#F2D675")
    rect(E, b1, c1, -12, 12, fc="#D1C4E9")
    rect(E, br0 - 2, br1, -6, 6, fc="#ECEFF1")
    flights(s, E(c1, 0)[0], E(cp0 - 4, 0)[0], AY, 1.9, 7)
    # Hopper: inverted jug on a saddled cap over the window
    h = E(win + 7.5, 0)[0]
    jug = [(-19, 6), (-19, 30), (-57, 80), (-57, 236), (57, 236), (57, 80), (19, 30), (19, 6)]
    s.ax.add_patch(Polygon([(h + a * k, AY + b * k) for a, b in jug], closed=True, fc="#E1F5FE", ec="k", lw=0.7, zorder=3))
    rect(E, win, win + 15, 5, 7, fc="white", size=None)
    s.text(h, AY + 150 * k, "PET jug\nhopper\n1-3 mm flakes", size=FS_TINY + 0.3, ha="center", zorder=4, linespacing=1.2)
    s.text(h, AY + 232 * k, "open top", size=FS_TINY, ha="center", va="top", zorder=4)
    rect(E, fan0, fan1, 8, 18, fc="#C8E6C9")
    rect(E, 276, 284, rail_top, -18, fc="#616161")
    rect(E, cp0 - 10, cp0 + 14, -18, 18, fc="#616161")
    rect(E, cp0, cp1, -12.35, 12.35, fc="#F0C26B", zorder=4)
    rect(E, cp1, stub, -3, 3, fc="#F0C26B")
    rect(E, bl0, bl1, -10, 10, fc="#E8A04A", zorder=4)
    s.ax.add_patch(Polygon([E(bl1, 5), E(bl1 + 2, 5), E(bl1 + 2, 2), E(tip, 0.5), E(tip, -0.5), E(bl1 + 2, -2), E(bl1 + 2, -5), E(bl1, -5)],
                           closed=True, fc="#C9A227", ec="k", lw=0.6, zorder=4))
    s.wire([E(tip, 0), E(sp, 0)], color="#2E7D32", lw=1.0, zorder=5)
    rect(E, blow0, blow1, rail_top, -14, fc="#BBDEFB")
    s.arrow(E((blow0 + blow1) / 2, -14), E((blow0 + blow1) / 2, -1), color="#1565C0", lw=0.6)
    rect(E, sens - 12, sens + 12, -15, 15, fc="#BDBDBD")
    rect(E, sens - 4, sens + 4, rail_top, -15, fc="#9E9E9E")
    rect(E, pull0, pull1, -21, 21, "BMG", fc="#9FB4CC", size=FS_TINY + 0.3, zorder=6)
    rect(E, pull0 + 15, pull0 + 30, rail_top, -21, fc="#9E9E9E")
    # Spool hangs from a post; the strand runs onto its underside
    s.ax.add_patch(Circle(E(sp, sp_r), sp_r * k, fc="white", ec="k", lw=0.8, ls=":", zorder=3))
    s.ax.add_patch(Circle(E(sp, sp_r), 25 * k, fc=F_LINE, ec="k", lw=0.6, ls=":", zorder=4))
    s.text(E(sp, sp_r)[0], E(sp, sp_r)[1], "M3", size=FS_TINY + 0.3, ha="center", zorder=5)
    s.text(E(sp, sp_r + 55)[0], E(sp, sp_r + 55)[1], "Spooler, slip-clutch hub", size=FS_TINY + 0.3, ha="center", zorder=5)
    rect(E, sp - 4, sp + 4, rail_top, sp_r - 25, fc="none", ls=":", zorder=2)

    def tag(x, y, s_, ha="left"):
        s.text(x, y, s_, size=FS_TINY + 0.3, ha=ha, zorder=8, linespacing=1.2)

    s.callout(E(97, 30), (16, 210), "Mount plate")
    s.callout(E(123, 12), (16, 201), "Shaft coupling")
    s.callout(E(103, 12), (16, 192), "51100 thrust bearing")
    s.callout(E(198, 18), (113, 197), "FAN1 at the window, always on")
    s.callout(E(240, 6), (113, 185), "Barrel, 150 long, auger inside", rel=(0.4, 0))
    s.callout(E(278, 18), (130, 209), "SK25 clamp, shimmed to line up with M1")
    s.callout(E(298, 12.35), (165, 197), "Heated coupler, ZONE 2\nH2 40 W + RT2", rel=(0, 0))
    s.callout(E(338, 10), (178, 184), "Super Volcano block in sock\nZONE 1, H1 80 W + RT1")
    s.callout(E(tip, 0.5), (188, 174), "1.4 mm nozzle")
    s.callout(E(sens, 15), (232, 184), "S1 sensor, 150 from nozzle\n(firmware default)", rel=(0.5, 0))
    s.callout(E(567, 21), (250, 197), "BMG puller on M2\n(motor runs back from the page)", rel=(0.5, 0))
    tag(E(blow1, 0)[0] + 1, 159, "FAN2, FAN3")

    # ---- electronics row, placement diagrammatic ----
    ey, eh = 116, 17
    s.box(20, ey, 38, eh, "U1 PSU 24 V 350 W", fc=F_POWER, size=FS_TINY + 0.3)
    s.box(62, ey, 14, eh, "U4\nbuck", fc=F_POWER, size=FS_TINY)
    s.box(80, ey, 42, eh, "U5 Uno + U6 shield\nU7 X, U8 Y\nUSB (W18) to PC or Pi", fc=F_ARDUINO, size=FS_TINY)
    s.box(126, ey, 42, eh, "U2 mainboard, U3 screen\nin the Ender base", fc=F_ENDER, size=FS_TINY)
    s.box(170, ey, 24, eh, "Q1 MOSFET\nF1 5 A", fc=F_POWER, size=FS_TINY)
    def run(pts, color, lab=None, at=None, ls="-", ha="left"):
        s.wire(pts, color=color, lw=0.7, ls=ls, zorder=2)
        if lab:
            s.label(at[0], at[1], lab, size=FS_TINY - 0.2, color=color, ha=ha)
    bus = 113.5
    s.wire([(39, ey), (39, bus), (322, bus)], color=C_24V, lw=1.1, zorder=2)
    for x in (69, 100, 147, 182):
        s.dot(x, bus, C_24V, r=0.55)
        s.wire([(x, bus), (x, ey)], color=C_24V, lw=0.7)
    s.label(205, bus + 0.1, "24 V, all loads", size=FS_TINY - 0.2, color=C_24V)
    run([(76, 124), (80, 124)], C_9V)
    run([(168, 124), (170, 124)], C_SIG)
    # Motion cables leave U6 along the channel under the rail
    run([(84, ey + eh), (84, 136), (30, 136), (30, E(0, -21)[1])], C_MOTOR, "W15 auger", (55, 136))
    run([(110, ey + eh), (110, 135), (272, 135), (272, E(0, -21)[1])], C_MOTOR, "W14 puller", (262, 135))
    run([(100, ey + eh), (100, 137), (E(sens, 0)[0] - 1, 137), (E(sens, 0)[0] - 1, E(0, -15)[1])], C_TEMP, "W16", (236, 137))
    # Heaters and thermistors go straight up to the melt zone
    y_c, y_b = E(0, -12.35)[1], E(0, -10)[1]
    run([(148, ey + eh), (148, y_c)], C_24V, "W8", (147.3, 143.5), ha="right")
    run([(156, ey + eh), (156, y_c)], C_TEMP, "W9", (155.3, 143.5), ha="right")
    run([(166, ey + eh), (166, y_b)], C_TEMP, "W7", (165.3, 143.5), ha="right")
    run([(172, ey + eh), (172, y_b)], C_24V, "W6", (172.7, 143.5))
    # Always-on fan, then the two unspecified supplies
    fx = E(fan1, 13)
    run([(124, bus), (124, fx[1]), fx], C_24V, "W19", (124.7, 128))
    s.dot(124, bus, C_24V, r=0.55)
    bx = E(blow0 + 12, 0)[0]
    run([(bx, bus), (bx, E(0, rail_top)[1])], C_24V, "W20", (bx + 0.7, 128), ls=":")
    s.dot(bx, bus, C_24V, r=0.55)
    run([(322, bus), (322, E(0, sp_r - 25)[1])], C_24V, "W21", (322.7, 128), ls=":")
    s.text(236, 125, "Electronics are shown where it keeps the cable runs clear. Only U1 and\nU2 have a stated home, the Ender base. "
           "W numbers match the wire schedule.", size=FS_TINY, va="center", linespacing=1.3)

    # ---- plan ----
    s.text(16, 107, "PLAN", size=FS + 0.5, weight="bold")
    rect(N, 0, frame_end, -4.5 / k, 4.5 / k, fc="#E8EAEB", lw=0.4, zorder=1)
    rect(N, frame_end, rail_end, -4.5 / k, 4.5 / k, fc="white", lw=0.4, ls=":", zorder=1)
    rect(N, m0, m1, -21, 21, "M1", fc="#90A4AE", size=FS_TINY + 0.3)
    rect(N, m1, g1, -18, 18, "14:1", fc="#B0BEC5", size=FS_TINY + 0.3)
    rect(N, g1, p1, -25, 25, fc="#9E9E9E")
    rect(N, p1, b1, -12, 12, fc="#F2D675")
    rect(N, b1, c1, -12, 12, fc="#D1C4E9")
    rect(N, br0 - 2, cp0, -6, 6, fc="#ECEFF1")
    hc = N(win + 7.5, 0)
    s.ax.add_patch(Circle(hc, 57 * k, fc="#E1F5FE", ec="k", lw=0.6, ls=":", alpha=0.75, zorder=3.2))
    s.ax.add_patch(Circle(hc, 19 * k, fc="none", ec="k", lw=0.5, zorder=3.3))
    rect(N, win, win + 15, -6, 6, fc="white", zorder=3.4, size=None)
    rect(N, fan0, fan1, -20, 20, "FAN1", fc="#C8E6C9", zorder=3.4)
    s.text(hc[0], hc[1] + 17, "Hopper over window", size=FS_TINY, ha="center", zorder=5)
    rect(N, cp0 - 10, cp0 + 14, -35, 35, fc="#616161")
    s.text(N(cp0 + 2, 0)[0], PY, "SK25", size=FS_TINY, ha="center", rotation=90, color="white", zorder=5)
    rect(N, cp0 + 14, cp1, -12.35, 12.35, fc="#F0C26B", zorder=4)
    rect(N, cp1, stub, -3, 3, fc="#F0C26B")
    rect(N, bl0, bl1, -10, 10, fc="#E8A04A", zorder=4)
    s.ax.add_patch(Polygon([N(bl1, 5), N(bl1 + 2, 5), N(bl1 + 2, 2), N(tip, 0.5), N(tip, -0.5), N(bl1 + 2, -2), N(bl1 + 2, -5), N(bl1, -5)],
                           closed=True, fc="#C9A227", ec="k", lw=0.6, zorder=4))
    s.wire([N(tip, 0), N(sp, 0)], color="#2E7D32", lw=1.0, zorder=5)
    for sign in (1, -1):
        rect(N, blow0, blow1, sign * 22, sign * 42, "FAN2" if sign > 0 else "FAN3", fc="#BBDEFB")
        s.arrow(N((blow0 + blow1) / 2, sign * 22), N((blow0 + blow1) / 2, sign * 3), color="#1565C0", lw=0.6)
    rect(N, sens - 12, sens + 12, -15, 15, "S1", fc="#BDBDBD", zorder=6)
    s.callout(N(304, 12.35), (168, 96), "Coupler", rel=(0, 0.5))
    s.callout(N(338, 10), (178, 90), "Block + nozzle", rel=(0, 0.5))
    rect(N, pull0, pull1, -21, 21, "BMG", fc="#9FB4CC", size=FS_TINY + 0.3, zorder=6)
    rect(N, pull0 + 3, pull1 - 3, -85, -21, "M2\n5:1", fc="#B0BEC5", size=FS_TINY + 0.3)
    rect(N, sp - sp_r, sp + sp_r, -35, 35, fc="white", ls=":")
    s.text(N(sp, 0)[0], PY + 8, "Spool, shown edge on", size=FS_TINY + 0.3, ha="center", zorder=6)

    def dim(x1, x2, y, label):
        p, q = N(x1, 0)[0], N(x2, 0)[0]
        s.ax.annotate("", xy=(p, y), xytext=(q, y), zorder=8,
                      arrowprops=dict(arrowstyle="<|-|>,head_length=0.3,head_width=0.1", lw=0.3, color="k", shrinkA=0, shrinkB=0))
        s.label((p + q) / 2, y, label, size=FS_TINY, ha="center")

    dim(br0, br1, 54, "Barrel 150")
    dim(tip, tip + 150, 54, "Nozzle to sensor 150 (100-200)")
    dim(tip + 50, tip + 100, 49, "Blowers 50-100")
    dim(0, tip, 44, "About 365, back of M1 to nozzle tip")
    dim(0, pull0, 39.5, "About 545, back of M1 to puller")

    s.notes(14, 30, [
        "The docs say the line bolts to the 2020 frame but not to which rail. Back of M1 to puller is about 545 mm and the Ender's footprint is roughly 470 mm, so check the "
        "fit. The puller and spooler may need an extra rail or their own stand. Dotted frame is that open question.",
        "M1, M2, FAN, BMG, SK25 and spool sizes are typical, not from the repo. Coupler, barrel, thrust bearing and spacings are from the docs. Ender gantry, motors and belts are not drawn.",
    ], 254, size=FS_TINY + 0.3, dy=3.0)
    return s


# =========================================================================================================
# Sheet 3: power and heaters
# =========================================================================================================
def sheet_power():
    s = Sheet(3, "Power distribution and heaters", "Ladder layout: the 24 V bus runs along the top, the 0 V bus along the bottom, "
              "and every load is a rung between them.")
    top, bot = 250, 72
    # Mains and PSU
    s.box(16, 216, 42, 22, "J1 mains inlet\nand power switch\n110 / 220 V", fc=F_POWER, size=FS_SMALL)
    s.box(16, 132, 42, 72, "U1\nEnder 3 V2 PSU\n24 V DC\n350 W\n14.6 A", fc=F_POWER, size=FS, weight="bold")
    for x, n in ((24, "L"), (37, "N"), (50, "PE")):
        s.wire([(x, 216), (x, 204)], color=C_MAINS, lw=1.0)
        s.label(x + 1, 210, n, size=FS_TINY, color=C_MAINS)
    s.label(37, 126, "Mains terminals are exposed\nunder the PSU cover", ha="center", size=FS_TINY + 0.3, color=C_MAINS)
    s.text(56.5, 190, "V+", size=FS_SMALL, ha="right", color=C_24V, weight="bold", zorder=5)
    s.text(56.5, 146, "V−", size=FS_SMALL, ha="right", weight="bold", zorder=5)
    s.wire([(58, 190), (66, 190), (66, top)], color=C_24V, lw=LW_BUS)
    s.wire([(58, 146), (66, 146), (66, bot)], color=C_0V, lw=LW_BUS)
    s.wire([(66, top), (398, top)], color=C_24V, lw=LW_BUS)
    s.wire([(66, bot), (398, bot)], color=C_0V, lw=LW_BUS)
    s.label(72, top + 3.5, "+24 V BUS", size=FS_SMALL, color=C_24V, weight="bold")
    s.label(72, bot - 3.5, "0 V BUS (PSU V−, common ground for the whole machine)", size=FS_SMALL, weight="bold")

    # Mainboard
    mx, mw, my, mh = 80, 58, 92, 142
    s.box(mx, my, mw, mh, "U2\nCreality 4.2.2\nmainboard\n\nMarlin 2.1.2.4", fc=F_ENDER, size=FS, valign="top")
    pw = mx + 12
    s.wire([(pw, top), (pw, my + mh)], color=C_24V, lw=1.2)
    s.wire([(pw, my), (pw, bot)], color=C_0V, lw=1.2)
    s.dot(pw, top, C_24V)
    s.dot(pw, bot)
    s.label(pw + 2, top - 8, "stock\ncable", size=FS_TINY)
    s.text(pw, my + mh - 1.5, "POWER", size=FS_TINY, ha="center", va="top", zorder=5)
    tx = mx + mw
    terms = [("HOTEND +", 216), ("HOTEND −", 204), ("BED +", 182), ("BED −", 162), ("TH", 142), ("", 130), ("TB", 116), ("", 104)]
    for n, y in terms:
        s.ax.add_patch(Rectangle((tx - 1.2, y - 1.2), 2.4, 2.4, fc="white", ec="k", lw=0.5, zorder=5))
        if n:
            s.text(tx - 2.5, y if n[0] != "T" else y - 6, n, size=FS_TINY + 0.3, ha="right", zorder=5, weight="bold")
    # U3 screen
    s.box(mx + 22, 76, 36, 11, "U3 DWIN screen", fc=F_ENDER, size=FS_TINY + 0.3)
    s.wire([(mx + 40, 87), (mx + 40, my)], color=C_SIG)

    # H2 straight off BED
    hx = 160
    s.wire([(tx, 182), (hx, 182)], color=C_24V)
    s.wire([(tx, 162), (hx, 162)], color=C_0V)
    s.zigzag(hx, 182, 20)
    s.text(hx + 4, 172, "H2 coupler heater (zone 2)\n24 V 40 W, 6 × 20 mm, 1.67 A", size=FS_TINY + 0.3, linespacing=1.3)
    # RT1, RT2
    s.wire([(tx, 142), (hx, 142)], color=C_TEMP)
    s.wire([(tx, 130), (hx, 130)], color=C_TEMP)
    s.thermistor(hx, 142, 12)
    s.text(hx + 5, 136, "RT1 block thermistor\n100K NTC B3950", size=FS_TINY + 0.3, linespacing=1.3)
    s.wire([(tx, 116), (hx, 116)], color=C_TEMP)
    s.wire([(tx, 104), (hx, 104)], color=C_TEMP)
    s.thermistor(hx, 116, 12)
    s.text(hx + 5, 110, "RT2 coupler thermistor\n100K NTC B3950, 3 × 15 mm", size=FS_TINY + 0.3, linespacing=1.3)

    # Q1 + F1 + H1
    qx, qw, qy, qh = 208, 46, 188, 36
    s.box(qx, qy, qw, qh, "Q1\n25 A MOSFET module\nopto-isolated", fc=F_POWER, size=FS_SMALL)
    s.wire([(tx, 216), (qx, 216)], color=C_SIG)
    s.wire([(tx, 204), (qx, 204)], color=C_SIG)
    s.label(170, 219, "control signal, not heater power", size=FS_TINY + 0.3, color=C_SIG)
    s.text(qx + 1, 216, "CTRL +", size=FS_TINY, zorder=5)
    s.text(qx + 1, 204, "CTRL −", size=FS_TINY, zorder=5)
    fx = qx + 34
    s.wire([(fx, top), (fx, 240)], color=C_24V, lw=1.2)
    s.fuse(fx, 240, 8)
    s.wire([(fx, 232), (fx, qy + qh)], color=C_24V, lw=1.2)
    s.dot(fx, top, C_24V)
    s.label(fx + 3.5, 236, "F1 5 A\ninline blade", size=FS_TINY + 0.3, color=C_24V)
    s.text(fx, qy + qh - 1.2, "DC IN +", size=FS_TINY, ha="center", va="top", zorder=5)
    s.label(fx - 4, 228, "16 AWG", ha="right", size=FS_TINY + 0.3, color=C_24V)
    gx = qx + 12
    s.wire([(gx, qy), (gx, bot)], color=C_0V, lw=1.2)
    s.dot(gx, bot)
    s.text(gx, qy + 1.3, "DC IN −", size=FS_TINY, ha="center", va="bottom", zorder=5)
    s.label(gx + 1.5, 150, "16 AWG", size=FS_TINY + 0.3)
    lx = qx + 36
    s.text(lx, qy + 1.3, "LOAD", size=FS_TINY, ha="center", va="bottom", zorder=5)
    h1x = 268
    s.wire([(lx - 3, qy), (lx - 3, 176), (h1x, 176)], color=C_24V, lw=1.2)
    s.wire([(lx + 3, qy), (lx + 3, 182), (h1x + 8, 182), (h1x + 8, 150), (h1x, 150)], color=C_0V, lw=1.2)
    s.zigzag(h1x, 176, 26, lw=1.0)
    s.text(238, 143, "H1 block heater (zone 1)\n24 V 80 W, 6 × 20 mm, 3.33 A", size=FS_TINY + 0.3, linespacing=1.3)

    # U4 buck
    bx = 288
    s.box(bx, 158, 26, 32, "U4\nLM2596\nbuck\n24 to 9 V", fc=F_POWER, size=FS_SMALL)
    s.wire([(bx + 6, top), (bx + 6, 190)], color=C_24V)
    s.wire([(bx + 6, 158), (bx + 6, bot)], color=C_0V)
    s.dot(bx + 6, top, C_24V)
    s.dot(bx + 6, bot)
    s.text(bx + 7, 192, "IN+", size=FS_TINY, color=C_24V)
    s.text(bx + 7, 156, "IN−", size=FS_TINY)
    s.wire([(bx + 15, 158), (bx + 15, 122)], color=C_9V)
    s.wire([(bx + 21, 158), (bx + 21, 122)], color=C_0V)
    s.text(bx + 14, 152, "9 V", size=FS_TINY, ha="right", color=C_9V)
    s.flag(bx + 9, 104, "U5 barrel\njack, sh. 4", w=24, h=18, direction="right", color=C_9V)

    # U6 shield power
    x6 = 324
    s.box(x6, 158, 28, 32, "U6 CNC\nShield V3\nPower In\ncaps ≥ 35 V", fc=F_ARDUINO, size=FS_TINY + 0.3)
    s.wire([(x6 + 14, top), (x6 + 14, 190)], color=C_24V)
    s.wire([(x6 + 14, 158), (x6 + 14, bot)], color=C_0V)
    s.dot(x6 + 14, top, C_24V)
    s.dot(x6 + 14, bot)

    # FAN1 always on
    x = 362
    s.wire([(x, top), (x, 179)], color=C_24V)
    s.fan(x, 174.5)
    s.wire([(x, 170), (x, bot)], color=C_0V)
    s.dot(x, top, C_24V)
    s.dot(x, bot)
    s.text(x + 1.6, 212, "FAN1 barrel fan, always on", size=FS_TINY + 0.3, rotation=90, ha="left", va="bottom")
    # FAN2/3: switch and supply not in the docs
    x = 378
    s.wire([(x, top), (x, 226)], color=C_24V, ls=":")
    s.switch(x, 226, 214, color=C_24V)
    s.wire([(x, 214), (x, 186)], color=C_24V, ls=":")
    s.fan(x, 181.5, ls=":")
    s.wire([(x, 177), (x, 172)], color=C_24V, ls=":")
    s.fan(x, 167.5, ls=":")
    s.wire([(x, 163), (x, bot)], color=C_0V, ls=":")
    s.dot(x, top, C_24V)
    s.dot(x, bot)
    s.text(x - 1.5, 125, "SW2?  FAN2, FAN3 blowers", size=FS_TINY + 0.3, rotation=90, ha="right", va="bottom")
    # M3 spooler
    x = 394
    s.wire([(x, top), (x, 182)], color=C_24V, ls=":")
    s.motor(x, 175, r=6, ls=":")
    s.wire([(x, 169), (x, bot)], color=C_0V, ls=":")
    s.dot(x, top, C_24V)
    s.dot(x, bot)
    s.text(x - 1.5, 94, "M3 spooler, not bought yet", size=FS_TINY + 0.3, rotation=90, ha="right", va="bottom")

    # Physical grouping
    s.notes(16, 62, [
        "Unplug from the wall before touching PSU or mainboard wiring.",
        "H1 must go through Q1. Its 3.33 A is more than the mainboard MOSFET should carry continuously. H2's 1.67 A is within the bed MOSFET's rating.",
        "Connect both thermistors before heating. An unplugged one halts that zone with MINTEMP (5 °C). Limits: nozzle MAXTEMP 305 °C (290 °C settable), coupler 290 °C (280 °C settable).",
    ], 250, title="Notes")
    s.notes(272, 62, [
        "Dotted rungs: the docs do not say how FAN2, FAN3 or M3 are powered. The bus feed and SW2 are the obvious way to do it, not a documented design. A 12 V spooler needs its own buck.",
    ], 136, title="Open wiring")
    s.legend(16, 31, [("Mains", C_MAINS, 1.0, "-"), ("+24 V", C_24V, 1.2, "-"), ("0 V", C_0V, 1.2, "-"), ("Control signal", C_SIG, LW_WIRE, "-"),
                      ("Thermistor", C_TEMP, LW_WIRE, "-"), ("9 V", C_9V, LW_WIRE, "-"), ("Not specified in the docs", C_24V, 1.0, ":")], cols=4, dx=60)
    return s


# =========================================================================================================
# Sheet 4: controller
# =========================================================================================================
def sheet_controller():
    s = Sheet(4, "Motion controller: Arduino Uno and CNC Shield V3", "U6 plugs straight onto U5, so the links between them are header pins, not "
              "loose wires. Only the connections at the far left and right are wired by hand.")
    ux, uw, uy, uh = 58, 58, 60, 196
    s.box(ux, uy, uw, uh, "U5\nArduino Uno R3\nATmega328P\n\nFirmware V4", fc=F_ARDUINO, size=FS, valign="top")
    s.text(ux + uw / 2, 140, "Timer1 ISR: puller\nTimer2 ISR: auger\nA0 16-sample average\n"
           "Diameter loop\nTelemetry every 1 s", size=FS_TINY + 0.3, ha="center", zorder=5, linespacing=1.3)
    sx, sw, sy, sh = 148, 142, 54, 206
    s.box(sx, sy, sw, sh, fc="#F5FAFE", ec="#1565C0", lw=1.0, zorder=1)
    s.text(sx + 3, sy + sh - 4, "U6 CNC Shield V3", size=FS + 0.5, weight="bold", color=C_SIG, zorder=4)

    # External: USB and 9 V
    s.box(14, 214, 30, 18, "USB host\nPC or Pi\n115200 baud", fc="white", size=FS_TINY + 0.3, ls=":")
    s.wire([(44, 223), (ux, 223)], color=C_SIG)
    s.text(51, 226, "USB", size=FS_TINY, ha="center", color=C_SIG)
    s.flag(14, 150, "U4 buck, 9 V\n(sheet 3)", w=30, h=14, direction="left", color=C_9V)
    s.wire([(44, 160), (ux, 160)], color=C_9V)
    s.wire([(44, 154), (ux, 154)], color=C_0V)
    s.text(46, 163, "barrel jack", size=FS_TINY, color=C_9V)

    # Uno pins
    pins = [("D2", 240), ("D5", 228), ("D8", 204), ("D3", 170), ("D6", 158), ("A0", 110), ("5V", 96), ("GND", 82), ("A2", 68)]
    tx = ux + uw
    for n, y in pins:
        s.ax.add_patch(Rectangle((tx - 1.2, y - 1.2), 2.4, 2.4, fc="white", ec="k", lw=0.5, zorder=5))
        s.text(tx - 2.5, y, n, size=FS_TINY + 0.5, ha="right", weight="bold", zorder=5, family="DejaVu Sans Mono")

    # Drivers
    dx, dw = 178, 66
    def driver(ref, name, ytop, step_y, dir_y, en_y, jumpers, mode):
        dh = ytop - (en_y - 16)
        s.box(dx, en_y - 16, dw, dh, fc="white", lw=0.9)
        s.text(dx + dw / 2, ytop - 3.5, "%s A4988 on %s socket" % (ref, name), size=FS_SMALL, ha="center", weight="bold", zorder=5)
        for lbl, y in (("STEP", step_y), ("DIR", dir_y), ("EN", en_y)):
            s.text(dx + 1.5, y, lbl, size=FS_TINY + 0.3, zorder=5, family="DejaVu Sans Mono")
        for i, on in enumerate(jumpers):
            jx = dx + 6 + i * 10
            s.ax.add_patch(Rectangle((jx - 2.2, en_y - 11), 4.4, 3.2, fc="#37474F" if on else "white", ec="#37474F", lw=0.5, zorder=5))
            s.text(jx, en_y - 13.5, "MS%d" % (i + 1), size=FS_TINY - 0.6, ha="center", zorder=5)
        s.text(dx + 36, en_y - 11, mode, size=FS_TINY + 0.3, zorder=5, va="center", linespacing=1.25)

    driver("U7", "X", 252, 240, 228, 216, (True, True, True), "1/16 step\nall 3 jumpers fitted")
    driver("U8", "Y", 182, 170, 158, 146, (False, False, False), "Full step\nno jumpers, ~0.7 A")

    # Header-pin links
    ex = 158
    s.wire([(tx, 240), (dx, 240)], color=C_SIG)
    s.wire([(tx, 228), (dx, 228)], color=C_SIG)
    s.wire([(tx, 170), (dx, 170)], color=C_SIG)
    s.wire([(tx, 158), (dx, 158)], color=C_SIG)
    s.wire([(tx, 204), (ex, 204)], color=C_SIG)
    s.wire([(ex, 216), (ex, 146)], color=C_SIG)
    s.wire([(ex, 216), (dx, 216)], color=C_SIG)
    s.wire([(ex, 146), (dx, 146)], color=C_SIG)
    s.dot(ex, 204, C_SIG)
    s.label(ex + 2, 208, "shared EN, active LOW", size=FS_TINY, color=C_SIG)

    # 24 V in: terminal on the shield, then a VMOT rail to both sockets
    tb = dx + 24
    s.flag(tb - 7, 263, "+24 V and 0 V from U1 (sheet 3)", w=46, h=7, direction="left", color=C_24V)
    s.wire([(tb, 263), (tb, 258)], color=C_24V, lw=1.2)
    s.box(tb - 11, 254.5, 22, 3.5, "Power In", fc="white", ec=C_24V, size=FS_TINY - 0.4, zorder=4)
    rail, drop = sx + sw - 5, dx + 58
    s.wire([(tb + 11, 256), (rail, 256), (rail, 186), (drop, 186), (drop, 182)], color=C_24V, lw=0.7)
    s.wire([(drop, 256), (drop, 252)], color=C_24V, lw=0.7)
    s.dot(drop, 256, C_24V)
    s.text(rail - 2, 200, "VMOT to both drivers", size=FS_TINY, rotation=90, ha="center", color=C_24V, zorder=5)

    # Control header
    hx, hw = dx, dw
    s.box(hx, 62, hw, 56, fc="white", lw=0.9)
    s.text(hx + hw / 2, 114.5, "Control header", size=FS_SMALL, ha="center", weight="bold", zorder=5)
    for lbl, y, color, on_right in (("Abort = A0", 110, C_TEMP, True), ("5V", 96, C_24V, True), ("GND", 82, C_0V, True), ("Resume = A2", 68, C_SIG, True)):
        s.wire([(tx, y), (hx, y)], color=color)
        s.text(hx + 1.5, y + 2.6, lbl, size=FS_TINY + 0.3, zorder=5)
        s.wire([(hx, y), (hx + hw, y)], color=color)
        s.wire([(hx + hw, y), (sx + sw, y)], color=color)

    # Motors
    gx = 348
    for ref, name, y1, y2, cy, ratio, what in (("M2", "puller", 238, 216, 227, "5.18:1", "drives BMG\n1 mm/s start\n0.1-6 mm/s"), ("M1", "auger", 168, 146, 157, "14:1", "drives auger\n14 RPM default\n1-20 RPM")):
        s.motor(gx - 26, cy, r=11)
        s.text(gx - 26, cy - 14.5, "%s NEMA 17" % ref, size=FS_SMALL, ha="center", weight="bold")
        for y, c in ((y1, "coil A"), (y2, "coil B")):
            s.wire([(dx + dw, y + 1.4), (gx - 42, y + 1.4), (gx - 34, cy + (y - cy) * 0.3 + 1)], color=C_MOTOR)
            s.wire([(dx + dw, y - 1.4), (gx - 42, y - 1.4), (gx - 34, cy + (y - cy) * 0.3 - 1)], color=C_MOTOR)
            s.label(dx + dw + 3, y + 3.8, c, size=FS_TINY, color=C_MOTOR)
        s.box(gx - 13, cy - 9, 18, 18, ratio + "\ngearbox", fc=F_LINE, size=FS_TINY + 0.3)
        s.wire([(gx - 15, cy), (gx - 13, cy)], color="k", lw=1.6)
        s.wire([(gx + 5, cy), (gx + 11, cy)], color="k", lw=1.6)
        s.text(gx + 12, cy, what, size=FS_TINY + 0.3, linespacing=1.25)

    # Sensor and run switch
    bx = 330
    s.box(bx, 74, 62, 44, "S1 filament\nwidth sensor\nAnalog 0-5 V", fc="white", size=FS_SMALL)
    x_end = sx + sw
    s.wire([(x_end, 110), (bx, 110)], color=C_TEMP)
    s.wire([(x_end, 96), (bx, 96)], color=C_24V)
    s.wire([(x_end, 82), (bx, 82)], color=C_0V)
    s.label(bx - 2, 112.8, "SIG", ha="right", size=FS_TINY + 0.3, color=C_TEMP)
    s.label(bx - 2, 98.8, "5 V", ha="right", size=FS_TINY + 0.3, color=C_24V)
    s.label(bx - 2, 84.8, "GND", ha="right", size=FS_TINY + 0.3)
    swx = 306
    s.wire([(x_end, 68), (swx, 68)], color=C_SIG)
    s.switch(swx, 82, 68, color=C_0V)
    s.dot(swx, 82)
    s.text(swx + 5, 68, "SW1 headless run\nclosed = auger + puller run,\nserial can't stop them", size=FS_TINY + 0.3, linespacing=1.25, va="center")

    s.notes(14, 50, [
        "Check the shield's capacitors before applying 24 V: 35 V or 50 V only. Budget shields often ship with 16 V or 25 V parts. Otherwise replace them or run the shield from 12 V.",
        "Set U4's output to 9 V with a multimeter before connecting it to the Uno. These modules are adjustable and can arrive set well above 9 V.",
        "Auger current is the torque limit: a jam must make M1 skip, not build pressure against the thin barrel thread. Don't raise it to push through a jam.",
    ], 254, size=FS_TINY + 0.4, dy=3.2)
    s.legend(14, 30.5, [("Step / dir / enable", C_SIG, LW_WIRE, "-"), ("Stepper coils", C_MOTOR, LW_WIRE, "-"), ("Sensor signal", C_TEMP, LW_WIRE, "-"), ("Supply", C_24V, LW_WIRE, "-")], cols=4, dx=48)
    return s


# =========================================================================================================
# Sheet 5: mechanical
# =========================================================================================================
def flights(s, u0, u1, v0, r, pitch, color="#90A4AE"):
    """Side view of an auger: slanted flights on a core. Page coordinates; runs from u0 right to u1."""
    u = u0
    while u < u1 - pitch * 0.2:
        s.ax.add_patch(Polygon([(u, v0 - r), (min(u + pitch * 0.25, u1), v0 - r), (min(u + pitch * 0.55, u1), v0 + r), (min(u + pitch * 0.3, u1), v0 + r)],
                               closed=True, fc=color, ec="#546E7A", lw=0.3, zorder=3))
        u += pitch


def sheet_mechanical():
    s = Sheet(5, "Mechanical layout and melt path", "View A is a side view of the whole line, not to scale. View B is a section through the melt path at 2.5:1, "
              "with coupler and barrel to scale.")
    # ---- View A ----
    s.text(16, 266, "VIEW A   Full line, side view (not to scale)", size=FS + 0.5, weight="bold")
    ay, rail = 225, 186
    s.box(16, rail - 8, 388, 8, "Ender 3 V2 frame, 2020 aluminium extrusion. Heated bed removed.", fc="#D7DBDD", size=FS_SMALL)
    # Motor stack
    s.box(16, ay - 14, 10, 28, "M1", fc="#90A4AE", size=FS_TINY + 0.3)
    s.box(26, ay - 11, 10, 22, "14:1", fc="#B0BEC5", size=FS_TINY + 0.3)
    s.box(36, rail, 3.5, ay + 22 - rail, fc="#9E9E9E")
    s.box(39.5, ay - 7, 4, 14, fc="#F2D675")
    s.box(43.5, ay - 8, 15, 16, "shaft\ncoupl.", fc="#D1C4E9", size=FS_TINY)
    s.callout((36.5, ay + 22), (16, ay + 28), "Mount plate")
    s.callout((41.5, ay - 7), (46, ay - 22), "51100 thrust\nbearing", ha="left")
    # Barrel, auger
    bx0, bx1 = 58.5, 182
    s.box(bx0, ay - 5, bx1 - bx0, 10, fc="#ECEFF1")
    s.wire([(bx0, ay - 3.5), (bx1, ay - 3.5)], color="#90A4AE", lw=0.3)
    s.wire([(bx0, ay + 3.5), (bx1, ay + 3.5)], color="#90A4AE", lw=0.3)
    flights(s, bx0 + 1, bx1 - 4, ay, 3.2, 8)
    s.text(135, ay - 9, "Barrel 10 ID × 12 OD × 150, auger inside", size=FS_TINY + 0.3, ha="center", color="#37474F")
    # Hopper and fan
    s.ax.add_patch(Polygon([(84, ay + 5), (96, ay + 5), (112, ay + 36), (68, ay + 36)], closed=True, fc="#E1F5FE", ec="k", lw=0.7, zorder=3))
    s.text(90, ay + 23, "PET jug hopper\n1-3 mm flakes", size=FS_TINY + 0.3, ha="center", zorder=4, linespacing=1.2)
    s.box(84, ay + 4.2, 12, 1.6, fc="white", lw=0.5)
    s.box(116, ay + 10, 16, 5, fc="#C8E6C9")
    s.arrow((117, ay + 10), (108, ay + 6.5), color="#2E7D32", lw=0.6)
    s.text(134, ay + 12.5, "FAN1 blows across barrel at the window", size=FS_TINY + 0.3)
    # SK25, coupler, block, nozzle
    cx0, cx1 = 182, 215
    s.box(cx0 - 8, ay - 15, 19, 30, fc="#616161", zorder=3)
    s.box(cx0 + 2, rail, 6, ay - 15 - rail, fc="#616161", zorder=3)
    s.box(cx0, ay - 13, cx1 - cx0, 26, fc="#F0C26B", zorder=4)
    s.text(cx0 + 18.5, ay, "Heated\ncoupler", size=FS_TINY + 0.3, ha="center", zorder=5)
    s.box(cx1, ay - 2.5, 12, 5, fc="#F0C26B", zorder=3)
    s.box(cx1 + 8, ay - 11, 22, 22, "Super\nVolcano\nblock", fc="#E8A04A", size=FS_TINY + 0.3, zorder=4)
    nz = cx1 + 30
    s.ax.add_patch(Polygon([(nz, ay - 5), (nz + 5, ay - 5), (nz + 14, ay - 1.2), (nz + 14, ay + 1.2), (nz + 5, ay + 5), (nz, ay + 5)], closed=True, fc="#C9A227", ec="k", lw=0.7, zorder=4))
    s.callout((cx0 + 2, ay + 15), (152, ay + 29), "SK25 clamp grips the coupler round,\noverhangs the barrel", ha="left")
    s.label(cx0 + 18.5, ay + 18.5, "ZONE 2\n40 W + RT2", size=FS_TINY + 0.3, ha="center", color=C_24V)
    s.label(cx1 + 19, ay + 18.5, "ZONE 1\n80 W + RT1", size=FS_TINY + 0.3, ha="center", color=C_24V)
    # Strand
    sx1 = 386
    s.wire([(nz + 14, ay), (sx1, ay)], color="#2E7D32", lw=1.6)
    s.label(nz + 18, ay + 3.5, "strand", size=FS_TINY + 0.3, color="#2E7D32")
    for x in (272, 288):
        s.box(x - 5, rail, 10, 8, fc="#BBDEFB")
        s.arrow((x, rail + 8), (x, ay - 1), color="#1565C0", lw=0.7)
    s.label(280, rail + 18, "FAN2, FAN3\n5010 blowers", size=FS_TINY + 0.3, ha="center")
    s.box(310, ay - 7, 7, 14, fc="#BDBDBD")
    s.text(313.5, ay + 11, "S1 sensor\n10-20 cm\nfrom nozzle", size=FS_TINY + 0.3, ha="center", linespacing=1.2)
    s.box(330, ay - 9, 18, 18, "BMG", fc="#9FB4CC", size=FS_TINY + 1)
    s.box(331, rail, 16, ay - 9 - rail, "M2\n5:1", fc="#B0BEC5", size=FS_TINY + 0.3)
    s.ax.add_patch(Circle((385, ay), 18, fc="white", ec="k", lw=0.8, ls=":", zorder=3))
    s.ax.add_patch(Circle((385, ay), 5, fc=F_LINE, ec="k", lw=0.6, ls=":", zorder=4))
    s.text(385, ay + 10, "Spooler", size=FS_TINY + 0.3, ha="center", zorder=5)
    s.text(385, ay - 10, "M3", size=FS_TINY + 0.3, ha="center", zorder=5)
    # Load path
    s.text(16, 172, "Load paths:  melt pressure on the auger goes coupling → 51100 → plate → frame, not through the gearbox.  "
           "Pressure on the coupler goes SK25 → frame, not through the thin barrel thread.", size=FS_SMALL, weight="bold", color="#37474F")

    # ---- View B: BC-001 section A-A (the plane through both cross holes) laid on its side, motor end to the left ----
    s.text(16, 165, "VIEW B   Melt path section, 2.5:1", size=FS + 0.5, weight="bold")
    k, X0, Y0 = 2.5, 88, 102
    P = lambda z, y: (X0 + (40 - z) * k, Y0 + y * k)
    R, CH = 12.35, 0.5
    r12, rb, rs, rstub = 6.15, 1.5, 0.7, 2.85
    z_floor, z_cone = 22.0, 22.0 - (6.15 - 1.5)
    half = [(40, r12 + CH), (40 - CH, r12), (z_floor, r12), (z_cone, rb), (2.8, rb), (2.0, rs), (-15, rs), (-15, rstub), (0, rstub),
            (0, R - CH), (CH, R), (40 - CH, R), (40, R - CH)]
    for sign in (1, -1):
        s.ax.add_patch(Polygon([P(z, sign * y) for z, y in half], closed=True, fc="#F4D79B", ec="k", lw=0.9, hatch="////", zorder=2))
    # M12 thread teeth line in the coupler
    r_min = 6.15 - 0.54
    for sign in (1, -1):
        s.line(P(40, sign * r_min), P(26, sign * r_min), lw=0.3, zorder=3)
    # M6 stub thread line
    r_root = rstub - 0.61
    for sign in (1, -1):
        s.line(P(0, sign * r_root), P(-15, sign * r_root), lw=0.3, zorder=3)
    # Barrel, breaks at z = 68, end at z = 28 (12 of thread fully engaged)
    z_end, z_break = 28.0, 68.0
    for sign in (1, -1):
        s.ax.add_patch(Polygon([P(z_end, sign * 5), P(z_end, sign * 6), P(z_break, sign * 6), P(z_break - 0.8, sign * 5.5), P(z_break, sign * 5)],
                               closed=True, fc="#CFD8DC", ec="k", lw=0.8, hatch="\\\\\\\\", zorder=3))
    # Auger (tip stops 1.75 short of the barrel end), 60° cone
    z_tip = z_end + 1.75
    r_aug = 4.75
    z_flight = z_tip + r_aug / 0.577
    u0, u1 = P(z_break, 0)[0], P(z_flight, 0)[0]
    flights(s, u0, u1, Y0, r_aug * k, 22)
    s.ax.add_patch(Polygon([P(z_flight, 1.8), P(z_tip + 0.1, 0.25), P(z_tip + 0.1, -0.25), P(z_flight, -1.8)], closed=True, fc="#90A4AE", ec="#546E7A", lw=0.4, zorder=3))
    s.ax.add_patch(Polygon([P(z_break, 1.8), P(z_flight, 1.8), P(z_flight, -1.8), P(z_break, -1.8)], closed=True, fc="#B0BEC5", ec="#546E7A", lw=0.4, zorder=2.5))
    # Heater, thermistor cross holes and set screws
    hy, hz, hr = 6.8, 8.0, 3.25
    ty, tz, tr = -6.8, 15.0, 1.75
    s.ax.add_patch(Polygon([P(hz - hr * sqrt(2), hy), P(hz - hr / sqrt(2), hy + hr / sqrt(2)), P(hz - hr / sqrt(2), hy - hr / sqrt(2))], closed=True, fc="white", ec="k", lw=0.5, zorder=3))
    s.ax.add_patch(Circle(P(hz, hy), hr * k, fc="white", ec="k", lw=0.6, zorder=3))
    s.ax.add_patch(Circle(P(hz, hy), 3.0 * k, fc="#E57373", ec="#B71C1C", lw=0.6, zorder=4))
    s.ax.add_patch(Polygon([P(tz - tr * sqrt(2), ty), P(tz - tr / sqrt(2), ty + tr / sqrt(2)), P(tz - tr / sqrt(2), ty - tr / sqrt(2))], closed=True, fc="white", ec="k", lw=0.5, zorder=3))
    s.ax.add_patch(Circle(P(tz, ty), tr * k, fc="white", ec="k", lw=0.6, zorder=3))
    s.ax.add_patch(Circle(P(tz, ty), 1.5 * k, fc="#81C784", ec="#1B5E20", lw=0.6, zorder=4))
    # Heater set screw M6 × 6: seated on the cartridge, 1 proud of the shoulder
    a = P(5.0, hy + 3.0)
    s.ax.add_patch(Rectangle(a, 6 * k, -6 * k, fc="#78909C", ec="k", lw=0.5, zorder=4))
    # Thermistor set screw M6 × 16 sits 3 mm off the section plane, so it's hidden: 2 proud
    s.ax.add_patch(Rectangle(P(13.5, ty + 3.0), 16 * k, -6 * k, fc="none", ec="#37474F", lw=0.5, ls=(0, (3, 2)), zorder=4))
    # Block (outline illustrative) + nozzle: stub 7 into the block, nozzle meets the stub tip
    z_face, z_back = -8.0, -32.0
    b = 10.0
    s.ax.add_patch(Polygon([P(z_face, b), P(z_back, b), P(z_back, 3.0), P(z_face, 3.0)], closed=True, fc="#E8B26A", ec="k", lw=0.9, hatch="xx", zorder=1.5))
    s.ax.add_patch(Polygon([P(z_face, -b), P(z_back, -b), P(z_back, -3.0), P(z_face, -3.0)], closed=True, fc="#E8B26A", ec="k", lw=0.9, hatch="xx", zorder=1.5))
    z_hex = z_back - 0.75
    noz_top = [(-15, 0.7), (-15, 2.85), (z_back, 2.85), (z_back, 2.85), (z_hex, 2.85), (z_hex, 4.5), (z_hex - 5, 4.5), (z_hex - 5, 3.0), (z_hex - 13, 1.0), (z_hex - 13, 0.7)]
    for sign in (1, -1):
        s.ax.add_patch(Polygon([P(z, sign * y) for z, y in noz_top], closed=True, fc="#E6C65C", ec="k", lw=0.8, hatch="....", zorder=2))
    s.line(P(z_break + 3, 0), P(z_hex - 18, 0), lw=0.3, ls=(0, (12, 3, 2, 3)), color="#444444", zorder=6)
    # SK25 around the coupler round, overhanging the barrel: 24 wide
    for y0, y1 in ((12.6, 16.5), (-12.6, -18.5)):
        s.ax.add_patch(Polygon([P(26, y0), P(50, y0), P(50, y1), P(26, y1)], closed=True, fc="#9E9E9E", ec="k", lw=0.8, hatch="////", zorder=2))
    # Dimensions + callouts
    def dimh(z1, z2, y, label):
        p, q = P(z1, y), P(z2, y)
        s.ax.annotate("", xy=p, xytext=q, arrowprops=dict(arrowstyle="<|-|>,head_length=0.35,head_width=0.12", lw=0.3, color="k", shrinkA=0, shrinkB=0), zorder=8)
        s.label((p[0] + q[0]) / 2, p[1], label, size=FS_TINY, ha="center")
    dimh(40, 0, 19.5, "Body 40")
    dimh(0, -15, 19.5, "Stub 15")
    s.line(P(40, 16.7), P(40, 20.5), lw=0.25)
    s.line(P(0, 12.4), P(0, 20.5), lw=0.25)
    s.line(P(-15, 10.1), P(-15, 20.5), lw=0.25)
    s.text(P(z_break, 0)[0] + 1, Y0 + 19, "Barrel\n10 ID × 12 OD", size=FS_TINY + 0.3)
    top, low = 158.5, 46
    s.callout(P(46, 16.5), (70, top), "SK25 clamp: about 24 wide,\ngrips the 14 long round", rel=(0.2, 0))
    s.callout(P(hz, hy + 3), (118, top), "H2 40 W cartridge, Ø6 in Ø6.5 hole\n8 from shoulder, 6.8 off axis", rel=(0.2, 0))
    s.callout(P(2, hy + 3), (176, top), "M6 × 6 set screw\nfor H2", rel=(0.3, 0))
    s.callout(P(-15, 2.2), (206, top), "SEAL: stub end face presses on\ntop of the nozzle, not the threads", rel=(0.2, 0))
    s.callout(P(58, -3), (16, 74), "3/8 in auger, 9.5 mm\n~0.25 clearance\nper side", rel=(0.4, 1))
    s.callout(P(34, -5.6), (16, low), "M12×1.0 barrel thread, 12 long, ~0.4 wall\nat root, fully hidden in the coupler", rel=(0.8, 1))
    s.callout(P(z_tip, -0.2), (74, low), "Auger tip stops 1.5-2 mm\nshort of the barrel end", rel=(0.5, 1))
    s.callout(P(10, -1.4), (110, low), "Ø3 bore, Ø1.4 through\nthe stub", rel=(0.5, 1))
    s.callout(P(tz, ty - 1.5), (142, low), "RT2 Ø3 in Ø3.5 × 16 blind\nhole, 15 from shoulder", rel=(0.5, 1))
    s.callout(P(3, ty - 3), (178, low), "M6 × 16 set screw, RT2\n(hidden, 3 off the plane)", rel=(0.5, 1))
    s.callout(P(-4, -2.8), (214, low), "M6 stub 6-8 deep in block,\nkeep ≥ 3 shoulder to block", rel=(0.3, 1))
    s.callout(P(-20, -10), (250, low), "Super Volcano block, H1, RT1\n(outline illustrative)", rel=(0.3, 1))
    s.callout(P(z_hex - 2.5, -4.5), (300, 72), "Nozzle hex: leave 0.5-1 gap\nto the block")
    s.callout(P(z_hex - 13, 0.8), (305, 118), "1.4 mm brass nozzle\nDie swell 1.6-2.0 mm before draw")
    s.notes(322, 58, ["Rotation about the axis is set by the barrel thread, then the whole assembly is turned until the hopper window faces up. Drawn with H2 on top for clarity.",
                      "Barrel end at about z 28, assuming the 12 mm thread is fully run in."], 86, size=FS_TINY + 0.3, dy=2.9, title="View B notes")
    return s


# =========================================================================================================
# Sheet 6: wire schedule + settings
# =========================================================================================================
def sheet_schedule():
    s = Sheet(6, "Wire schedule and settings", "Every connection and every value you need at the bench. Source for each is the manual, the sketch or Configuration.h.")
    rows = [("Wire", "From", "To", "Carries", "Cable / note"),
            ("W1", "J1 mains inlet", "U1 PSU L, N, PE", "110 / 220 V AC", "Stock. Unplug before touching"),
            ("W2", "U1 V+, V−", "U2 POWER", "24 V", "Stock cable"),
            ("W3", "U1 V+", "F1, then Q1 DC IN +", "24 V, 3.33 A", "16 AWG red, 5 A fuse on +"),
            ("W4", "U1 V−", "Q1 DC IN −", "0 V", "16 AWG black"),
            ("W5", "U2 HOTEND +, −", "Q1 CONTROL +, −", "PWM control", "Signal cable, mind polarity"),
            ("W6", "Q1 LOAD", "H1 80 W block heater", "24 V, 3.33 A", "Heater leads"),
            ("W7", "RT1 block thermistor", "U2 TH", "Temp sense", "Marlin sensor type 1"),
            ("W8", "H2 40 W coupler heater", "U2 BED screw terminals", "24 V, 1.67 A", "Route away from nozzle"),
            ("W9", "RT2 coupler thermistor", "U2 TB", "Temp sense", "Marlin sensor type 1"),
            ("W10", "U2", "U3 DWIN screen", "Serial UI", "Stock cable"),
            ("W11", "U1 V+, V−", "U6 Power In", "24 V motor power", "Check caps first"),
            ("W12", "U1 V+, V−", "U4 IN", "24 V", ""),
            ("W13", "U4 OUT", "U5 barrel jack", "9 V", "Set 9 V before connecting"),
            ("W14", "U6 X motor header", "M2 puller, 5:1", "Stepper coils", "Swap a coil pair to reverse"),
            ("W15", "U6 Y motor header", "M1 auger, 14:1", "Stepper coils", "Swap a coil pair to reverse"),
            ("W16", "U6 Abort (A0), 5V, GND", "S1 SIG, VCC, GND", "0-5 V analog", "Not a digital runout switch"),
            ("W17", "U6 Resume (A2), GND", "SW1 run switch", "Closed = run", "Optional, headless only"),
            ("W18", "U5 USB", "PC or Pi", "115200 baud", "Commands and telemetry"),
            ("W19", "U1 V+, V−", "FAN1 4010 / 4020", "24 V", "Always on, no switch"),
            ("W20", "Not specified", "FAN2, FAN3 5010", "24 V assumed", "OPEN: docs give no supply or switch"),
            ("W21", "Not specified", "M3 spooler", "24 V or 12 V", "OPEN: not bought. 12 V needs a buck")]
    s.table(14, 262, (12, 40, 40, 28, 56), rows, title="Wire schedule")

    x2 = 196
    y = s.table(x2, 262, (34, 34, 34, 34), [
        ("Stepper driver", "Socket / jumpers", "Step mode", "Current"),
        ("U7 puller (M2)", "X, 3 jumpers fitted", "1/16", "Motor's comfortable running current"),
        ("U8 auger (M1)", "Y, no jumpers", "Full, 2800 steps/rev", "~0.7 A, torque limit"),
    ], title="Drivers")
    s.text(x2, y - 3, "Vref = 8 × Rs × I.  At 0.7 A: R100 sense resistor 0.56 V, R050 sense resistor 0.28 V.", size=FS_TINY + 0.4)
    x3 = x2 + 142
    s.table(x3, 262, (24, 21, 21), [("Preset", "Nozzle", "Coupler"), ("PLA", "215 °C", "205 °C"), ("PETG", "240 °C", "230 °C"), ("PET #1", "270 °C", "260 °C")], title="Presets")

    s.table(x2, 226, (42, 26, 40), [
        ("Arduino pin", "Shield label", "Function"),
        ("D2 (PD2) / D5", "X STEP / DIR", "Puller, Timer1 ISR"),
        ("D3 (PD3) / D6", "Y STEP / DIR", "Auger, Timer2 ISR"),
        ("D8", "EN", "Active LOW, both drivers"),
        ("A0", "Abort", "Diameter sensor"),
        ("A2", "Resume", "Run switch to GND, pull-up"),
    ], title="Arduino pin map")
    s.table(x2 + 114, 226, (46, 50), [
        ("Marlin setting", "Value"),
        ("Soak timer", "10 min, within 3 °C, resets past 5 °C"),
        ("MINTEMP both zones", "5 °C"),
        ("MAXTEMP nozzle / coupler", "305 / 290 °C"),
        ("Settable max", "290 / 280 °C"),
        ("Thermal runaway", "60 s, 4 °C, both zones"),
    ], title="Thermal protection")

    s.table(x2, 178, (44, 22, 42), [
        ("Controller value", "Default", "Set at commissioning"),
        ("PULL_STEPS_PER_MM", "2150", "2150 × 60 / L"),
        ("SENSOR_DISTANCE_MM", "150", "Measure nozzle to sensor"),
        ("CAL_ADC_A at 1.50 mm", "300", "Read RAW with gauge pin"),
        ("CAL_ADC_B at 2.00 mm", "700", "Read RAW with gauge pin"),
        ("TARGET_DIA / dead band", "1.75 / ±0.02", "Fixed"),
        ("Correction", "Gain 0.5", "Capped ±10 %, min 2 s apart"),
    ], title="Calibration")
    s.table(x2 + 114, 178, (30, 66), [
        ("Serial command", "Action"),
        ("START / STOP, OFF", "Auger + puller on / off"),
        ("PULL ON / OFF", "Puller only, for threading"),
        ("AUG ON / OFF", "Auger only, 1.5 s soft start"),
        ("SPEED <x>", "Puller, 0.1-6 mm/s"),
        ("RPM <x>", "Auger, 1-20 RPM"),
        ("AUTO ON / OFF", "Diameter regulation on / frozen"),
        ("HELP", "List commands"),
    ], title="Serial, 115200 baud, Newline")

    band = 128
    s.notes(14, band, [
        "FAN2, FAN3 supply and switching (W20). The procedure says \"Blowers on\" but gives no wiring, and the screen menu has no fan item.",
        "M3 spooler (W21) is still to buy, so its voltage is not settled.",
        "F1 protects only the heater branch. U4, U6, FAN1 and the blower and spooler rungs have no fuse of their own in the docs.",
        "The barrel's M12×1.0 thread is listed as still to do in the parts list.",
    ], 172, size=FS_SMALL + 0.3, dy=3.9, title="Open items at Rev B")
    s.notes(196, 122, [
        "U1 PSU, U2 mainboard, U3 screen, U4 buck, U5 Uno, U6 shield, U7 U8 A4988, Q1 MOSFET, F1 fuse, H1 H2 heaters, RT1 RT2 thermistors, "
        "M1 auger, M2 puller, M3 spooler, FAN1 barrel fan, FAN2 FAN3 blowers, S1 diameter sensor, SW1 run switch, SW2 blower switch (assumed), J1 mains inlet.",
    ], 100, size=FS_SMALL + 0.3, dy=3.9, title="Reference designators")
    s.notes(306, 122, [
        "Known heater load is 120 W, or 5.0 A of the PSU's 14.6 A. Motors and fans aren't rated in the docs, but that leaves plenty of margin.",
        "Ender X, Y, Z and E motor outputs and endstops are not used by this build.",
    ], 100, size=FS_SMALL + 0.3, dy=3.9, title="Power and unused hardware")
    s.notes(14, 88, [
        "Before any power: check the shield's capacitors are 35 V or 50 V, and set U4 to 9 V on a multimeter with the Uno disconnected.",
        "Flash Marlin to U2 and the sketch to U5. Set Vref on U7 and U8 and fit the jumpers.",
        "First boot, cold, both thermistors plugged in: the nozzle and COUPLER readouts should both show 20-25 °C.",
        "Heat to 250 °C, hold the coupler flats with a 22 mm wrench and tighten the nozzle a further 1/8 turn against the stub.",
        "PID tune both zones and save: M303 E0 S220 C8 U1, then M303 E-1 S205 C8 U1, then M500.",
        "Heaters off, barrel empty: check both motor directions, calibrate S1 with gauge pins, then puller steps/mm and sensor distance. Re-upload the sketch.",
        "Watch one full soak on a preset, through SOAKING: 10:00 to AUGER: OK TO START, before the first run.",
    ], 390, size=FS_SMALL + 0.3, dy=3.9, title="Bring-up order")
    return s


SHEET_BUILDERS = (sheet_overview, sheet_assembled, sheet_power, sheet_controller, sheet_mechanical, sheet_schedule)


def build():
    return [make() for make in SHEET_BUILDERS]


if __name__ == "__main__":
    out = Path(__file__).with_name("3DTruder_schematic.pdf")
    with PdfPages(out, metadata={"Title": "3DTruder System Schematic", "Creator": "make_schematic.py"}) as pdf:
        for sheet in build():
            pdf.savefig(sheet.fig)
            plt.close(sheet.fig)
    print("wrote", out)
