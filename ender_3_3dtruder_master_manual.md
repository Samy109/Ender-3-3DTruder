# 🛠️ Ender 3 / Ender 3 V2 Filament Recycler: Master Manual
**Auger-Fed Super Volcano Extrusion Line with Closed-Loop Diameter Control**

---

## 📌 1. Overview & Safety

### How it works
1. Dried, sieved plastic flakes drop from a bottle hopper into a window in a horizontal **10 mm ID × 12 mm OD stainless barrel**.
2. A **14:1 geared NEMA 17** turns a modified **3/8" wood auger** inside the barrel and pushes the flakes forward.
3. The barrel screws into a **316L stainless barrel coupler** (M12×1.0 → M6×1.0 stub), which screws straight into a **Super Volcano heater block**. The plastic melts in the coupler and block and leaves through a **1.4 mm nozzle**.
4. The strand is cooled by two **5010 blowers**, measured by an **inline diameter sensor**, and drawn down to **1.75 mm** by a **BMG puller** on a 5:1 geared motor. An Arduino adjusts the puller speed to hold diameter.
5. The Ender 3 V2 mainboard runs **two heat zones**: the Super Volcano block (80 W, through an **external 25 A MOSFET**) and the heated coupler (40 W, on the board's former heated-bed output). Its screen shows both temperatures and a **10-minute melt soak timer** before the auger may start.

### Safety Warnings
* **High temperature:** The heater block, nozzle and barrel coupler run at **200 °C – 280 °C**. Wear heat-resistant gloves when handling hot parts. Never leave the machine heating unattended.
* **Mains voltage:** The Ender 3 PSU has exposed 110 V / 220 V terminals under its cover. **Unplug the printer from the wall** before working on any PSU or mainboard wiring.
* **High current:** The 80 W heater cartridge draws about **3.33 A at 24 V**, more than the stock mainboard MOSFET is meant to carry continuously. **Always switch the heater through the external 25 A MOSFET module.**
* **Fumes:** Melting plastic releases VOCs and ultrafine particles. Run in a ventilated space or under a fume extractor.
* **Never process PVC (#3):** Heating PVC releases hydrogen chloride gas. Only process known plastics (#1 PET, #5 PP, #7 PLA / PETG).
* **Never run the auger cold:** Solid plastic jammed against the nozzle can generate enough pressure to split the thin barrel thread. Wait for `AUGER: OK TO START` on the screen.

### Design notes
* **Melt zone:** The barrel is heated only by conduction from the coupler, so just its last 1–2 cm gets hot enough to melt plastic. Flakes stay solid along the rest of the barrel and melt in the coupler and heater block. The coupler is 316L stainless, which conducts heat poorly, so it carries its own heater rather than relying on heat from the block, and the soak timer exists because the coupler and barrel end lag the block by several minutes.
* **No heatbreak:** There is no V6 heatsink or heatbreak in the melt path. A heatbreak is designed to keep its top end cold, which is exactly where flakes would jam.
* **Thin barrel thread:** The barrel's M12×1.0 thread leaves about 0.4 mm of wall at the thread root. Three rules keep it safe: the thread is fully hidden inside the coupler, the coupler (not the tube) is clamped to the frame, and the auger driver's current is limited so a jam makes the motor skip instead of building pressure.
* **Two heat zones:** The coupler carries its own 24 V 40 W cartridge and thermistor, driven by the Ender's heated-bed output (the bed itself is removed). Marlin controls it with full PID and thermal-runaway protection, and the menus call it **Coupler**. It roughly doubles the heat available for melting and pushes the melt zone up into the barrel end. Presets run the coupler about 10 °C below the nozzle.
* **Die swell:** Plastic swells as it leaves the 1.4 mm nozzle (to roughly 1.6–2.0 mm depending on material and temperature). The puller can only draw the strand *thinner*. If it comes out under 1.75 mm before pulling, a larger nozzle is needed (keep a 2.0 mm on hand, or drill out the 1.4 mm). The coupler's stub bore stays 1.4 mm (that keeps its wall printable), which adds only a little back-pressure at these flow rates.

---

## 🛒 2. Bill of Materials

Full list with specs and links: [`amazon_parts_list.md`](amazon_parts_list.md). Shop-made parts: [`CAD/shop_order.md`](CAD/shop_order.md).

### 🔹 Base Unit
* **Ender 3 V2** (24 V 350 W PSU, 4.2.2 mainboard, DWIN screen, 2020 frame). Heated bed removed.
* **2020 brackets & M5 T-nuts** for mounting the auger, coupler clamp and puller.

### 🔹 Melt Zone
* **Super Volcano heater block** + **1.4 mm Super Volcano brass nozzle** + **silicone sock**
* **80 W 24 V heater cartridge** + **100K NTC B3950 thermistor cartridge**
* **25 A external MOSFET module** + 16 AWG silicone wire + 5 A inline fuse
* **Heated barrel coupler (316L stainless, metal 3D printed at ±0.3 mm, threads printed):** 40 mm long: a 21.7 × 24.7 mm heater block (its 21.7 mm faces are the wrench flats) under a Ø24.7 mm round for the clamp. M12×1.0 female top, M6×1.0 male stub (15 mm, full thread), Ø3 mm bore (Ø1.4 through the stub), flats for a 22 mm wrench, cross holes for a 6 mm heater cartridge and a 3 mm thermistor, M6 set screws. No machining or thread cutting needed. See [`CAD/shop_order.md`](CAD/shop_order.md) and [`CAD/barrel_coupler.step`](CAD/barrel_coupler.step).
* **SK25 shaft support:** clamps the coupler's round top section to the frame.
* **M6 stainless set screws:** one 6 mm (heater) and one 16 mm (thermistor), plus a 3 mm hex key.
* **Coupler heat zone:** 24 V 40 W 6 × 20 mm cartridge heater + 100K B3950 thermistor cartridge (3 × 15 mm), wired to the mainboard's bed terminals and `TB` thermistor header.
* **PTFE thread tape** for the barrel thread.

### 🔹 Auger Feed
* **Stainless barrel tube, 10 mm ID × 12 mm OD, 150 mm**, with a 15 × 12 mm hopper window near one end. The other end needs an M12×1.0 external thread, 12 mm long. Best done by a machine shop (see 4.3).
* **3/8" wood auger bit, 12"**, hex shank 9.0 mm across flats. Screw point cut off, tip ground to a cone.
* **NEMA 17 planetary gearmotor, 14:1**, 8 mm output shaft (needs at least 25 mm of exposed shaft).
* **8 mm → 11 mm clamp-on shaft coupling**, Ø32 × 45 mm aluminum, plus a soda-can aluminum shim to center the hex shank (see 4.2).
* **51100 thrust ball bearing**, 10 × 24 × 9 mm.
* **NEMA 17 motor mount plate** bolted to the 2020 frame.
* **24 V 4010 fan** over the barrel at the hopper window.
* **A4988 driver**, full step, current limited to ~0.7 A.

### 🔹 Hopper & Feedstock
* **Clear PET jug** (half-gallon), inverted over the barrel window.
* **Sieve set:** 5 mm, 3 mm, 1 mm.

### 🔹 Puller & Control
* **Arduino Uno R3** + **CNC Shield V3** (capacitors must be rated **35 V or 50 V** for 24 V).
* **A4988 driver** for the puller, 1/16 microstepping.
* **NEMA 17 planetary gearmotor, 5:1** + **complete BMG clone extruder** (puller).
* **Analog (0–5 V) filament diameter sensor** on `A0`.
* **LM2596 buck converter**, 24 V → 9 V for the Uno.
* **2× 5010 blowers + ducts** for strand cooling.
* **Motorized spooler** with slip-clutch hub.

### 🔹 Tools
* Only if you cut the barrel thread yourself: **M12×1.0 die** + **38 mm die handle**, bench vise, cutting oil, and a Ø10 mm rod about 50 mm long
* Sheet of glass + 400-grit wet-and-dry paper (lapping the stub end)
* M12×1.0 and M6×1.0 taps + 1.4 mm drill bit, only if the printed coupler's threads or bore come out tight
* Angle grinder / cutoff discs, needle files, 240-grit cloth
* Digital caliper, multimeter (for A4988 Vref)
* 22 mm wrench (coupler flats), nozzle wrench

---

## 📥 3. Feedstock & Hopper

### 3.1 Sifting (3-Stage Stack)
Stack screens top to bottom: **5 mm → 3 mm → 1 mm → catch pan**, and shake well.

| Sieve Layer | Particle Size | Action |
| :--- | :--- | :--- |
| **Retained on 5 mm** | > 5 mm | Return to shredder |
| **Retained on 3 mm** | 3.0 – 5.0 mm | Return to shredder |
| **Retained on 1 mm** | **1.0 – 3.0 mm** | **Feedstock** |
| **Catch pan** | < 1.0 mm | **Discard.** Fines trap air, burn, and cause bubbles |

> [!NOTE]
> Measure the depth of the auger's flights (the groove between the spiral and the core). Flakes should be smaller than that depth or they wedge instead of feeding. If 3 mm flakes jam, sieve down to 1–2 mm.

### 3.2 Pre-Drying
Moisture boils in the melt zone and causes popping, voids and brittle filament.

| Plastic | Temperature | Time | Notes |
| :--- | :--- | :--- | :--- |
| **PLA** | 45 – 50 °C | 4+ h | Stay below 55 °C or flakes clump |
| **PETG** | 60 – 65 °C | 4 – 6 h | Store sealed with desiccant |
| **PET (#1 bottles)** | 120 – 140 °C | 5+ h | Needs high heat to dry |

### 3.3 Bottle Hopper
The barrel is horizontal, so the hopper sits upside-down on top of the window.

1. Cut the bottom off the jug. It becomes the open top of the hopper.
2. Cut a **15 × 12 mm slot** in the top of the cap, matching the barrel window, and file the cap's top into a curved saddle that sits on the 12 mm barrel.
3. Screw the cap onto the jug, set it on the barrel with the slot over the window, and strap it down with a hose clamp or zip ties.
4. The jug is PET and softens around 70 °C, so it must sit at the cold end of the barrel, over the 4010 fan zone, never near the coupler.
5. If flakes bridge in the jug's shoulder, tap the jug or add a small vibration motor.

---

## 🔧 4. Phase 1: Auger, Barrel & Melt Zone Assembly

### 4.1 Modifying the Auger Bit
1. Clamp the auger bit in a vise.
2. **Cut off the threaded screw point** with an angle grinder or cutoff disc.
3. Grind the cutting spurs into a **smooth cone (about 60°)**.
4. Polish the tip with 240-grit cloth so there are no burrs.
5. Cut the bit to length so that, when installed, its tip stops **1.5 – 2.0 mm short of the barrel's threaded end**. It must never touch the coupler.

### 4.2 Motor, Thrust Bearing & Shaft Coupling
Melt pressure pushes the auger back **toward the motor**, so the thrust bearing goes between the mount plate and the coupling:

```
 [ 14:1 motor ] ─ [ mount plate ] ─ [ 51100 bearing ] ─ [ shaft coupling ] ─ auger ─►
```

1. Bolt the motor to the mount plate and the plate to the 2020 frame.
2. Slide the 51100 bearing over the 8 mm motor shaft against the plate.
3. Center the hex shank in the 11 mm side of the clamp-on coupling: wrap the hex in **three layers of soda-can aluminum** (about 0.1 mm each) where the clamp grips it.
4. Push the coupling down onto the bearing with **no gap**, then tighten the 8 mm clamp. The load path is now coupling → bearing → plate → frame, not the gearbox.
5. **Spin test:** turn the motor by hand and watch the auger tip. Any visible wobble will rub the barrel (only ~0.25 mm clearance per side). Fix the shim before going further.

### 4.3 Barrel Prep
1. **Deburr the window:** file all inside edges of the window smooth with a needle file and 240-grit. Burrs left by the cutting disc catch flakes and scrape the auger.
2. **Thread the outlet end** (the end without the window) **M12×1.0, 12 mm long.** The tube wall is only 1 mm, so this is fiddly with a hand die. The easy route is a machine shop or anyone with a lathe: it's a few minutes' work. Ask for **M12×1.0 external, 12 mm long, on 12 × 1 mm stainless tube, support the bore while threading.** To cut it yourself:
    * File a small 45° chamfer on the outside edge of the tube end so the die starts square.
    * Slide the Ø10 mm rod into the tube so the 1 mm wall can't crush, and clamp the tube in the vise on a rag or soft jaws, well away from the window.
    * Start the die square with plenty of cutting oil. Turn half a turn forward, a quarter turn back to break the chip, and repeat.
    * Stop at **12 mm**. The coupler's thread is 14 mm deep, so the whole cut thread ends up hidden inside it.
    * Back the die off, deburr the inside edge, and test-fit the coupler by hand. If the thread tears, cut 15 mm off the tube and start again.
3. Slide the barrel over the auger. The window end goes toward the motor.

### 4.4 Melt Zone Assembly
First, check the printed coupler (it's printed at ±0.3 mm on sizes and ±0.5 mm on holes, threads and all):
* Run the M6 stub into the block, the threaded barrel into the M12 end, and both M6 set screws in by hand. A printed thread may feel rough the first time; run it in and out a few times. Don't force it: if an internal thread is tight, chase it with the M12×1.0 or M6×1.0 tap (by hand, cutting oil, back off every half turn).
* **Check the bore:** you should see light straight through. If the Ø1.4 stub bore printed small or holds powder, run a 1.4 mm drill through it by hand.
* **Lap the stub end:** lay 400-grit paper on the glass, hold the coupler upright by its body, and rub the stub end in figure-eights until the whole face is evenly matte. It's the sealing face.

```
 barrel ══ M12×1.0 ══ [ 316L coupler ] ══ M6 stub  ══ [ Super Volcano block ] ══ nozzle
                       ▲ SK25 clamp                         ▲ zone 1: 80 W + thermistor
                       ▲ zone 2: 40 W + thermistor
```

1. **Barrel → coupler:** wrap the barrel thread in PTFE tape and screw it into the coupler's M12×1.0 end until snug. The whole thread should be hidden inside the coupler.
2. **Coupler → block:** screw the coupler's M6 stub into the **top** of the Super Volcano block about 6–8 mm deep. Leave a gap between the coupler shoulder and the block.
3. **Nozzle:** screw the 1.4 mm nozzle **up** into the bottom of the block until it meets the end of the stub. There should be a small gap (0.5–1 mm) between the nozzle's hex and the block. If the hex touches the block first, screw the stub in deeper and repeat.
   *The seal is the flat end of the stub pressing on the top of the nozzle, not the threads.*
4. **Clamp:** mount an **SK25 shaft support** to the frame and clamp the round top section of the coupler (above the flats, away from the heater zone). It's printed slightly under 25 mm; if the clamp doesn't grip, add one wrap of soda-can aluminum. The motor plate and the coupler are now both tied to the frame, so melt pressure goes through the frame instead of pulling on the thin barrel thread.
5. **Heater & sensor:** install the 80 W cartridge and the thermistor in the block and fit the silicone sock.
6. **Coupler heater:** slide the 24 V 40 W cartridge into the coupler's heater hole and the thermistor into its hole, and lock each with its M6 set screw from the shoulder face (6 mm screw for the heater, 16 mm for the thermistor; snug, not tight). Route the leads away from the nozzle.
7. **Barrel fan:** mount a 24 V 4010 or 4020 fan over the barrel at the window (blowing across it) to keep the feed end cold. Zip-tie it directly: loop two zip-ties through the fan corner holes and around the 12 mm barrel or hopper neck. Wire it to an always-on 24 V supply so it runs continuously.

### 4.5 Heater Wiring
**Zone 1, Super Volcano block (80 W), through the external MOSFET:**

```
[ Ender 3 24V PSU (+/-) ] ──(16 AWG, 5A fuse on +)──► [ MOSFET "DC IN" (+/-) ]
[ Mainboard hotend terminal ] ──(signal cable)──────► [ MOSFET "Control" (+/-) ]
                                                      [ MOSFET "LOAD / OUT" ] ──► [ 80 W heater ]
[ Block thermistor ] ─────────────────────────────────► [ Mainboard "TH" header ]
```

**Zone 2, coupler (40 W), straight to the board:**

```
[ 40 W coupler cartridge ] ──► [ Mainboard "BED" screw terminals ]  (well within the bed MOSFET's rating)
[ Coupler thermistor ]     ──► [ Mainboard "TB" header ]
```

> [!WARNING]
> Connect **both** thermistors before heating. If a zone's thermistor is unplugged when that zone is given a target (for example by a preset), Marlin halts with `MINTEMP`. That's the safety working, not a firmware fault.

### 4.6 First Boot, First Heat, Hot-Tighten & PID
1. Flash the Ender 3 V2 firmware (see [`Ender3_Firmware/README.md`](Ender3_Firmware/README.md)): `firmware_Ender3_V2_RE.bin` or `_RC.bin` to match the chip on your board. If the board has been flashed before, rename the file to something new so the bootloader picks it up.
2. **First boot, cold:** both thermistors plugged in (nozzle on `TH`, coupler on `TB`). The nozzle readout and the `COUPLER:` line should both show room temperature (about 20–25 °C). A reading near or below 0 °C, or an error, means a thermistor isn't connected.
3. Set the hotend to **250 °C** and wait a few minutes.
4. Hold the coupler's **flats with a 22 mm wrench** (on the upper part of the flats, clear of the heater and thermistor leads) and tighten the nozzle a further **⅛ turn** against the stub.
5. Run PID autotune on **both zones** and save, either from the screen (**Configuration → Advanced Settings → PID Autotune** for the nozzle and the Coupler, then **Store Settings**) or over USB:

```gcode
M303 E0 S220 C8 U1    ; nozzle (zone 1)
M303 E-1 S205 C8 U1   ; coupler (zone 2, the "bed" channel)
M500
```

The coupler ships with rough starting PID values, so tune it before the first real run.

**Then watch one full soak:** pick a preset and check the screen counts `SOAKING: 10:00` down to `>>> MELT READY <<<` and `AUGER: OK TO START`.

---

## 🎛️ 5. Phase 2: Puller, Sensor & Controller

### 5.1 Strand Line Layout
```
 nozzle ─► [ 5010 blowers ] ─► [ diameter sensor ] ─► [ BMG puller ] ─► [ spooler ]
           5–10 cm after exit   10–20 cm from nozzle
```

1. Mount the **BMG** on the 5:1 geared motor and fix it to the frame after the sensor.
2. Aim both **5010 blowers** at the strand 5–10 cm after the nozzle. It must be solid before it reaches the puller gears. Mount them directly into the 2020 frame slots using M4/M5 bolts and drop-in T-nuts (loosening lets you slide them along the extrusion to tune strand cooling distance), or mount via flexible clamp arms.
3. Put the **diameter sensor 10–20 cm from the nozzle**, right after the cooling zone. Every extra 10 cm adds about 100 s between diameter corrections at 1 mm/s. Enter the measured distance as `SENSOR_DISTANCE_MM` in the firmware.

### 5.2 CNC Shield V3 Wiring
```
 [ Ender 3 PSU 24V ] ──────────────────────────────► [ CNC Shield "Power In" ]
 [ CNC Shield on Uno ] ─► X socket (Pin 2 / 5) ─► A4988 ─► 5:1 motor  (puller, 1/16 step)
                       ─► Y socket (Pin 3 / 6) ─► A4988 ─► 14:1 motor (auger, full step)
                       ─► A0 ("Abort")    ─────────────► diameter sensor signal
                       ─► A2 ("Resume")   ─────────────► headless run switch to GND
```

> [!CAUTION]
> **Check the CNC Shield capacitors before connecting 24 V.** Budget shields often ship with 16 V or 25 V capacitors. Replace them with 35 V parts or run the shield from 12 V.

### 5.3 Driver Current (Vref)
* **Auger (Y):** set for about **0.7 A**. This is a torque limit: if the nozzle clogs, the motor skips steps (a buzzing noise) instead of building enough pressure to split the barrel thread. Raise it only in small steps if the auger skips during normal feeding.
* **Puller (X):** set to the motor's comfortable running current; it carries very little load.
* Measure Vref with a multimeter and check your A4988's sense resistor (R100 / R050) to convert.

### 5.4 Controller Firmware
Flash [`Arduino_Firmware.ino`](Arduino_Firmware/Arduino_Firmware.ino) to the Uno from the Arduino IDE (**Tools → Board → Arduino Uno**, pick the port, **Upload**), or with `arduino-cli` (use your own COM port):

```bash
arduino-cli compile -b arduino:avr:uno -u -p COM7 Arduino_Firmware
```

Open a serial monitor at **115200 baud** (line ending `Newline`). You should see the `3DTruder Puller & Auger Controller V4` banner, the command list, and a status line every second. Details in [`Arduino_Firmware/README.md`](Arduino_Firmware/README.md).

* Interrupt-driven stepping for both motors, so serial traffic never stutters them.
* Soft-start auger ramp; auger speed adjustable live with `RPM <x>`.
* Diameter control that waits for fresh strand to reach the sensor between corrections, and holds speed when the sensor is empty.

### 5.5 Commissioning & Calibration
Do these in order, with the **heaters off and the barrel empty**. The calibration values are at the top of the sketch. Re-upload after changing them.

> [!WARNING]
> With nothing plugged into A0, the `DIA:` reading drifts at random (the unconnected pin picks up noise) and can look like a real diameter. **Don't run the puller in auto mode until the sensor is connected and calibrated**, or it will chase that noise. Use `AUTO OFF` for any testing before then.

1. **Motor directions:** send `RPM 4`, then `AUG ON`, watch for a second, then `AUG OFF`. The auger must turn so its flights carry flakes **toward the nozzle**. Then `SPEED 1` and `PULL ON` / `PULL OFF`: the BMG must pull the strand **away from the nozzle**. If either is backwards, flip `AUG_DIR_INVERT` or `PULL_DIR_INVERT` (or swap one coil pair on that motor's plug).
2. **Diameter sensor:** connect it to A0 (plus 5 V and GND). Insert a **1.50 mm** gauge pin (a drill blank works) and note the `RAW:` value, then a **2.00 mm** pin and note it again. Enter them as `CAL_ADC_A` and `CAL_ADC_B`. Afterwards the `DIA:` reading should match each pin within about 0.01 mm.
3. **Puller steps/mm:** thread a piece of filament through the BMG, mark it at the inlet, send `AUTO OFF`, `SPEED 1`, `PULL ON`, and stop it after exactly 60 s. Measure how far the mark moved (L, in mm) and set `PULL_STEPS_PER_MM = 2150 × 60 / L`.
4. **Sensor distance:** measure from the nozzle tip to the sensor's measuring point and enter it as `SENSOR_DISTANCE_MM`.
5. **Re-upload** the sketch and send `AUTO ON`. Commissioning is done; the line is ready for the operating procedure below.

---

## 🚀 6. Operating Procedure

### 6.1 Startup
Screen presets (each sets both heat zones):

| Preset | Nozzle | Coupler |
| :--- | :--- | :--- |
| PLA | 215 °C | 205 °C |
| PETG | 240 °C | 230 °C |
| PET | 270 °C | 260 °C |

1. **Pre-flight:** barrel fan running; feedstock sieved (1–3 mm) and dried; CNC shield on 24 V only with 35 V+ capacitors.
2. **Preheat:** pick a preset on the screen (table above). It sets both zones.
3. **Soak:** once **both zones** are at temperature the screen counts down `SOAKING: 10:00`. Wait for **`>>> MELT READY <<<`** and **`AUGER: OK TO START`**.
4. **Blowers on.**
5. **Start the auger slow:** send `RPM 5`, then `AUG ON`. Fill the hopper. (The A2 switch starts the auger **and** the puller at the sketch defaults, 14 RPM and 1 mm/s, so save it for headless runs once the line is threaded.)
6. **Capture the strand:** as plastic leaves the nozzle, draw it past the blowers with pliers.
7. **Thread the line:** through the diameter sensor, into the BMG, tighten the thumbscrew.
8. **Pull:** send `PULL ON`. Use `SPEED <x>` to get near 1.75 mm by hand, then let auto-regulation trim it. Attach the filament to the spooler.
9. **Throughput:** raise the auger with `RPM <x>` a step at a time. If the puller pins at its maximum speed, or Marlin reports thermal runaway, the auger is too fast.

### 6.2 Shutdown
1. `AUG OFF`, let the puller clear the strand, then `STOP`. If the A2 switch is closed, open it first: serial commands can't stop the motors while it's closed.
2. Cooldown on the screen (turns off both zones). Leave the barrel fan running until the block is below 60 °C.

### 6.3 Troubleshooting

| Symptom | Likely Cause | Fix |
| :--- | :--- | :--- |
| **Auger motor buzzes / skips** | Plastic not melted, or nozzle clogged. (Skipping is the torque limit working.) | Stop the auger. Wait for `MELT READY`. Clear the nozzle. Don't raise Vref to push through. |
| **`Thermal Runaway` mid-run** (nozzle or coupler) | Auger feeding cold flakes faster than the heaters can melt them | Lower `RPM`. Don't loosen the thermal protection. |
| **`MINTEMP` / `MAXTEMP`** | Thermistor unplugged or broken | Check the nozzle thermistor on `TH` and the coupler thermistor on `TB`, and their wires |
| **Coupler never reaches temperature** | Cartridge loose in its hole, or PID not tuned | Tighten the M6 set screw; run `M303 E-1 S205 C8 U1` then `M500` |
| **Plastic leaks around the block top** | Stub end not seated on the nozzle | Heat to 250 °C, hold the coupler flats, tighten the nozzle ⅛ turn. Check the nozzle hex isn't touching the block. |
| **Plastic leaks at the barrel thread** | Thread not sealed or not snug | Cool down, re-tape and re-tighten. Check the thread is fully inside the coupler. |
| **Squealing / auger rubbing** | Auger off-center in the shaft coupling | Redo the shim; spin-test for wobble |
| **Flakes not feeding** | Bridging in the jug, or flakes too big for the flights | Tap the jug; sieve to 1–2 mm |
| **Diameter hunts up and down** | Sensor too far from the nozzle, or wrong `SENSOR_DISTANCE_MM` | Move the sensor closer; measure and update the setting |
| **Filament undersized before pulling** | Not enough die swell | Raise temperature 5–10 °C, slow the puller; if still thin, switch to a 2.0 mm nozzle |
| **Bubbles / popping** | Wet feedstock | Dry longer (PET: 5+ h at 130 °C) |
| **Puller flattens the filament** | Strand still soft at the puller | More blower airflow; loosen the BMG thumbscrew slightly |
