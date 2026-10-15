# 🛠️ Ender 3 3DTruder: High-Throughput Filament Recycler

A complete DIY conversion turning a **Creality Ender 3 / Ender 3 V2** into a high-throughput closed-loop filament extrusion line for recycling 3D prints and plastic waste into uniform 1.75 mm filament.

---

## ⚡ Quick Navigation

* 📖 **[Master Build & Operating Manual](ender_3_3dtruder_master_manual.md)**: Full build and operating guide covering assembly, wiring, sifting, puller setup, calibration, and troubleshooting. Also exported as [HTML](Ender_3_3DTruder_Master_Manual.html) and [PDF](Ender_3_3DTruder_Master_Manual.pdf).
* 🔩 **[Shop Order & CAD](CAD/shop_order.md)**: Machinist spec for the heated brass barrel coupler, barrel thread and auger sleeve.
* 🛒 **[Bill of Materials / Amazon Parts List](amazon_parts_list.md)**: Categorized parts checklist with specifications and procurement links.
* 🖨️ **[Ender 3 V2 Melt Station Firmware](Ender3_Firmware/README.md)**: Pre-compiled Marlin binaries (`.bin`) with native DWIN color UI, 290 °C unlocked, and a second heat zone for the barrel coupler on the bed channel.
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
  - Bed Output -> 40 W Coupler Heat Zone       - Pin A0: Inline Analog Diameter Sensor
  - Switches 25A External MOSFET               - Pin A2: Hardware Feed Toggle Switch
           │                                           │
           ▼                                           ▼
 [ Melt Zone ]                                [ Closed-Loop Filament Line ]
  - 10x12 mm Barrel, M12x1.0 Thread            - Directional Dual 5010 Strand Blowers
  - Heated Brass Coupler -> M6 Stub            - Diameter Sensor 10-20 cm From Nozzle
  - Super Volcano Block, 80 W Cartridge        - BMG Dual-Drive Puller Extruder
  - 1.4 mm Brass Nozzle (Die Swell)            - Motorized Slip-Clutch Spooler
```

---

## 🚀 Key Engineering Highlights

1. **Viscoelastic Die Swell Compensation:**
   * Utilizes a **1.4 mm brass Super Volcano nozzle**. Extruding polymer swells as it exits, and the motorized puller draws the strand down to a uniform **1.75 mm ± 0.02 mm**. (A 2.0 mm nozzle is the fallback if swell falls short.)
2. **Heatbreak-Free Melt Path:**
   * The barrel threads into a shop-made **brass coupler** whose M6 stub screws straight into the Super Volcano block and seals on the nozzle. No heatsink or heatbreak for flakes to jam in. The coupler carries its own 40 W heater and thermistor as a second heat zone. See [`CAD/shop_order.md`](CAD/shop_order.md).
3. **Dedicated External MOSFET:**
   * An 80 W heater cartridge draws ~3.33 A at 24 V. Switching is offloaded from the mainboard to an opto-isolated 25 A external MOSFET module with inline fuse protection.
4. **Two-Zone Heating & Melt Soak Timer:**
   * The removed heated bed's output and thermistor input now drive the coupler heater, with PID and thermal-runaway protection. Menus call it **Coupler**; presets set both zones.
   * The status screen shows both zones and counts down a 10-minute soak after both reach temperature and only then shows `MELT READY` / `AUGER: OK TO START`.
5. **Interrupt-Driven Motor Firmware (V4):**
   * Puller and auger are stepped from hardware timer interrupts, so serial traffic never stalls the motors.
   * 1.5-second soft-start ramp on the 14:1 auger; auger RPM and puller speed adjustable live over serial.
   * Dead-time-aware diameter control that waits for fresh strand to reach the sensor between corrections, and holds speed when the sensor is empty.
6. **Autonomous Workshop Operation or Raspberry Pi Host:**
   * Runs headless via CNC Shield toggle switch on `Resume` (A2 to GND).
   * Supports an optional Raspberry Pi connected via USB for webcam monitoring, live diameter plotting, and remote telemetry logging.

---

## 📦 Directory Structure

```
├── .gitignore
├── README.md
├── amazon_parts_list.md
├── ender_3_3dtruder_master_manual.md   (source; HTML/PDF built by tools/build_manual.py)
├── Ender_3_3DTruder_Master_Manual.html
├── Ender_3_3DTruder_Master_Manual.pdf
├── CAD/
│   ├── barrel_coupler.py      (CadQuery source)
│   ├── barrel_coupler.step
│   ├── barrel_coupler.stl
│   └── shop_order.md
├── tools/
│   └── build_manual.py
├── Arduino_Firmware/
│   ├── Arduino_Firmware.ino
│   ├── Arduino_Firmware.hex
│   └── README.md
└── Ender3_Firmware/
    ├── Configuration.h
    ├── Configuration_adv.h
    ├── firmware_Ender3_V2_RC.bin
    ├── firmware_Ender3_V2_RE.bin
    ├── README.md
    └── src_patch/
        ├── menu_main.cpp
        └── ui_status_480x272.cpp
```
