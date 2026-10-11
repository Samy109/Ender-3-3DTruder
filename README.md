# 🛠️ Ender 3 3DTruder: High-Throughput Filament Recycler

A complete DIY conversion turning a **Creality Ender 3 / Ender 3 V2** into a high-throughput closed-loop filament extrusion line for recycling 3D prints and plastic waste into uniform 1.75 mm filament.

---

## ⚡ Quick Navigation

* 📖 **[Master Build & Operating Manual](ender_3_3dtruder_master_manual.md)**: Full engineering guide covering mechanics, melt physics, thermal protection, sifting, puller setup, calibration, and troubleshooting.
* 🛒 **[Bill of Materials / Amazon Parts List](amazon_parts_list.md)**: Categorized parts checklist with specifications and procurement links.
* 🖨️ **[Ender 3 V2 Melt Station Firmware](Ender3_Firmware/README.md)**: Pre-compiled Marlin binaries (`.bin`) with native DWIN color UI, 290 °C unlocked, and bed thermistor checks disabled.
* 🎛️ **[Arduino Closed-Loop Controller Firmware](Arduino_Firmware/README.md)**: Pre-compiled Arduino hex binary (`.hex`) and source sketch (`.ino`) for Uno + CNC Shield V3 motor control and inline diameter regulation.

---

## 🌟 System Architecture

```
                      [ Ender 3 24V 350W PSU ]
                                 │
           ┌─────────────────────┴─────────────────────┐
           ▼                                           ▼
 [ Ender 3 V2 Mainboard ]                     [ Arduino CNC Shield V3 ]
  - DWIN Color Graphical UI                    - X-Axis: 5:1 Puller Motor (1/16 Microstep)
  - 290 °C Hotend PID Control                  - Y-Axis: 14:1 Auger Motor (Full Step, ~14 RPM)
  - Bed Alarm Disabled (TEMP_SENSOR_BED 0)     - Pin A0: Inline Analog Diameter Sensor
  - Switches 25A External MOSFET               - Pin A2: Hardware Feed Toggle Switch
           │                                           │
           ▼                                           ▼
 [ Super Volcano Hotend ]                     [ Closed-Loop Filament Line ]
  - 80 W Heater Cartridge                      - Directional Dual 5010 Strand Blowers
  - 1.4 mm Brass Nozzle (Die Swell)            - BMG Dual-Drive Puller Extruder
  - Stainless Steel Solid Heatbreak            - Motorized Slip-Clutch Spooler
```

---

## 🚀 Key Engineering Highlights

1. **Viscoelastic Die Swell Compensation:**
   * Utilizes a **1.4 mm brass Super Volcano nozzle**. Extruding polymer expands to ~1.8–2.0 mm upon exit, allowing the motorized puller to draw down and tension the strand to a uniform **1.75 mm ± 0.02 mm**.
2. **Dedicated External MOSFET:**
   * An 80 W heater cartridge draws ~3.33 A at 24 V. Switching is offloaded from the mainboard to an opto-isolated 25 A external MOSFET module with inline fuse protection.
3. **Bed Alarm Elimination:**
   * Custom Marlin firmware sets `#define TEMP_SENSOR_BED 0`, allowing the heated bed and its wiring to be completely unplugged and removed from the chassis without triggering `MINTEMP` alarms.
4. **Autonomous Workshop Operation:**
   * The Arduino controller includes support for a physical toggle switch on CNC Shield header `Resume` (pin A2 to GND) so the machine can run headless without needing a PC attached, alongside full USB serial telemetry (115200 baud).

---

## 📦 Directory Structure

```
├── .gitignore
├── README.md
├── amazon_parts_list.md
├── ender_3_3dtruder_master_manual.md
├── Arduino_Firmware/
│   ├── Arduino_Firmware.ino
│   ├── Arduino_Firmware.hex
│   └── README.md
└── Ender3_Firmware/
    ├── Configuration.h
    ├── Configuration_adv.h
    ├── firmware_Ender3_V2_RC.bin
    ├── firmware_Ender3_V2_RE.bin
    └── README.md
```
