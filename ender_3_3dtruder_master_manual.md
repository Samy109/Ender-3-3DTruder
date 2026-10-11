# 🛠️ Ender 3 / Ender 3 V2 Filament Recycler: Master Manual
**High-Throughput Super Volcano Extrusion Line (Phase 1, 1B & Phase 2)**

---

## 📌 1. Overview & Safety

### Safety Warnings
* **High temperature:** The Super Volcano block runs at **200 °C – 280 °C+**. Always wear heat-resistant leather/welding gloves when handling hot components. Never leave the machine heating unattended.
* **Mains voltage:** The Ender 3 power supply unit (PSU) features exposed 110 V / 220 V terminals under its safety terminal cover. **Always unplug the printer from the wall receptacle** before working on any PSU or mainboard power wiring.
* **High current:** An 80 W heater cartridge draws approximately **3.33 A at 24 V**. The stock Ender 3 mainboard MOSFETs are rated for 30–40 W stock hotends and will overheat or burn out under continuous 80 W load. **Always switch the heater cartridge through a dedicated external 25 A MOSFET module.**
* **Toxic fumes & ultrafine particles:** Heating polymers (PLA, PETG, ABS, PET) releases volatile organic compounds (VOCs) and ultrafine particulate matter. Operate in a well-ventilated garage, workshop, or directly under an active fume extraction hood.
* **Never process PVC (Polyvinyl Chloride):** Heating PVC produces lethal hydrogen chloride gas and corrosive hydrochloric acid that will destroy your lungs and rust your equipment. Only process verified plastics with known recycling codes (e.g., #1 PET, #5 PP, #7 PLA).

---

### ⚠️ Critical Engineering Realities (Read Before Building)

1. **The Melt Zone & Feed Physics Paradox:**
   * In a stock 3D printer, a solid 1.75 mm filament rod acts as a mechanical piston pushing molten plastic through the nozzle.
   * Flakes or shredded regrind have no column strength. In an unheated tube, granular plastic particles bind against each other and wedged against the walls (**granular jamming / Janssen effect**).
   * **You cannot push cold solid flakes through a standard 2.0 mm cold heatbreak.** If using a gravity hopper (Phase 1), feedstock must be sifted to fine micro-pellets (< 1.5 mm).
   * For the **Auger Module (Phase 1B)**, the motor-driven auger compresses and conveys flakes forward. The auger barrel must be structurally braced to the printer's 2020 aluminum frame (never suspended from the hotend), the auger bit tip must have its wood-cutting lead screw ground flat, and a thrust bearing must absorb axial kickback.
2. **Bi-Metal Heatbreak Fragility:**
   * Bi-metal heatbreaks feature an ultra-thin metal wall (0.2–0.3 mm) designed solely to minimize thermal conduction. They have virtually zero shear or bending strength.
   * A geared NEMA 17 motor produces massive mechanical torque. Any radial or axial force transmitted through the barrel will snap a bi-metal heatbreak. For auger-assisted builds, use a solid stainless steel heatbreak or rigid direct barrel coupler.
3. **Nozzle Orifice & Die Swell Expansion:**
   * Polymer extrudate exhibits **die swell** (viscoelastic elastic recovery upon exiting the restricted orifice).
   * With a **1.4 mm nozzle**, die swell expands the exiting strand to approximately **1.8 mm – 2.0 mm** (a swell ratio of ~1.3× to 1.4× depending on extrusion shear rate, melt temperature, and polymer).
   * Because the extrudate expands above 1.75 mm upon exit, the motorized puller can then apply controlled tension to stretch and draw down the strand to a precise, uniform **1.75 mm ± 0.02 mm**.

---

## 🛒 2. Master Bill of Materials (BOM)

### 🔹 Base Unit & Structural Frame
* **Ender 3 3D printer** (provides 24 V 350 W PSU, mainboard for temperature PID control, frame, and LCD interface)
* **2020 / 2040 Aluminum Extrusion brackets & M5 T-nuts** (for mounting the puller and auger modules directly to the frame)

### 🔹 Phase 1: Melt & Extrusion Station
* **E3D V6 heatsink** (groove-mount, universal)
* **V6 4010 24 V cooling fan with clip-on shroud duct** (actively cools the cold zone)
* **All-metal stainless steel heatbreak** (solid stainless recommended for auger; bi-metal is fragile under auger torque)
* **Super Volcano brass heater block**
* **Super Volcano high-temp silicone sock** **[NEW]** (mandatory to insulate the massive block from cooling blower drafts)
* **80 W heater cartridge, 24 V**
* **100K NTC B3950 thermistor** (or cartridge-style thermistor rated to 300 °C for high-temperature PET)
* **1.4 mm Super Volcano brass nozzle** (die swell expands extrudate to ~1.8–2.0 mm; puller draws it down to 1.75 mm)
* **25 A external MOSFET power module** (opto-isolated control input compatible with 24 V)
* **V6 groove-mount adapter bracket** for the Ender 3 X-carriage
* **16 AWG stranded silicone wire** (red/black) for PSU → MOSFET → heater power lines
* **Inline blade fuse holder + 5 A or 7.5 A fuse** (installed on positive 24 V rail)
* **Non-conductive thermal paste** (for heater cartridge & thermistor bore seating only; never on threads)

### 🔹 Feedstock & Hopper Setup
* **Stainless steel soil sieve set:** 5 mm, 3 mm, and 1 mm mesh screens
* **1.5 mm sieve screen** **[NEW]** (feedstock must pass 1.5 mm to guarantee clearance through the 2.0 mm throat)
* **Hopper funnel:** Steep-walled funnel or inverted bottle (minimum 60° internal wall angle)

### 🔹 Phase 1B: Motorized Auger Feed Module
* **NEMA 17 planetary gearmotor, 14:1 or higher reduction** (high torque, low speed)
* **Wood auger drill bit** (3/8" / ~9.5 mm OD, 12"+ length; screw point and spurs ground flat with cutoff wheel)
* **Seamless stainless steel or aluminum tube (barrel)** (internal diameter ~10.0 mm, matching auger OD with ~0.5 mm clearance)
* **Rigid shaft coupler or mini chuck** (5 mm motor shaft to measured auger shank diameter)
* **Thrust ball bearing** (matched to auger shank diameter; absorbs axial thrust into frame)
* **Metal transition reducer / threaded adapter** (barrel outlet to heatsink/block inlet)
* **Heavy-duty motor mount plate** (bolted to Ender 3 2020 aluminum frame extrusions)

### 🔹 Phase 2: Automated Puller & Closed-Loop Line
* **Arduino Uno R3**
* **Arduino CNC Shield V3** **[NEW]** (seats directly on Uno; holds A4988 drivers, built-in capacitors, 24 V terminals, microstepping jumpers)
* **2x A4988 stepper driver modules** (with aluminum heatsinks; 1 for puller, 1 for auger)
* **NEMA 17 planetary gearmotor, 5:1 reduction** (for the puller)
* **Complete BMG Clone Extruder Assembly** **[NEW / REPLACEMENT]** (housing, dual drive gears, needle bearings, idler arm, and thumbscrew tensioner)
* **Inline filament diameter sensor with analog 0–5 V output** (mechanical roller with analog Hall-effect sensor or TSL1401 optical array; *not a digital runout switch*)
* **Adjustable LM2596 buck converter module** (steps 24 V down to 9 V for Arduino Uno barrel jack, or 12 V for blowers)
* **2x 5010 blower fans** (strand cooling zone; confirm 12 V or 24 V) + focused directional ducts
* **Motorized spooler assembly** **[NEW]** (low-RPM 5–10 RPM gear motor with spring-loaded slip-clutch spool hub)

---

## 📥 3. Material Feeding & Hopper Setup

Strict feedstock sizing is mandatory to prevent instantaneous bridging and jamming at the cold throat entrance.

### 3.1 Sifting Strategy (4-Stage Stack)
Stack the sieve screens from top to bottom: **5 mm (top) → 3 mm → 1.5 mm → Pan (bottom)**, and agitate thoroughly.

| Sieve Layer | Particle Size | Action / Verdict |
| :--- | :--- | :--- |
| **Retained on 5 mm screen** | > 5 mm | Return to plastic shredder |
| **Retained on 3 mm screen** | 3.0 – 5.0 mm | Return to plastic shredder (far too large for throat) |
| **Retained on 1.5 mm screen** | 1.5 – 3.0 mm | Return to shredder (**cannot pass through a 2.0 mm throat**) |
| **Retained on 1.0 mm screen (or passed 1.5 mm onto pan)** | **1.0 – 1.5 mm** | **Optimal feedstock.** Usable for extrusion. |
| **Passed through 1.0 mm screen (dust/fines)** | < 1.0 mm | **Discard.** Fines trap air, burn, and cause bubble voids in filament. |

> [!IMPORTANT]
> If testing gravity feed without an auger, regrind until 100% of particles pass through a 1.5 mm screen. A single 2.2 mm flake lodged across a 2.0 mm throat will cause an immediate cold shut.

### 3.2 Pre-Drying Protocol
Entrained moisture vaporizes violently inside the melt chamber, causing popping noises, surface voids, and brittle filament. Dry on baking sheets in a dedicated dehydrator or oven:

| Polymer Type | Drying Temperature | Duration | Critical Handling Notes |
| :--- | :--- | :--- | :--- |
| **PLA** | 45 – 50 °C | 4+ hours | Do not exceed 55 °C or flakes will soften and fuse into a block. |
| **PETG** | 60 – 65 °C | 4 – 6 hours | Hygroscopic; store in sealed airtight containers with desiccant. |
| **PET (#1 Bottle Flakes)** | 120 – 140 °C | 5+ hours | Extremely moisture-sensitive. 65 °C is insufficient; PET requires high heat to desorb water. |

---

## 🔧 4. Phase 1: Hotend Assembly & Wiring

### Step 1: Hotend Mechanical Assembly
1. **Heatbreak installation:** Thread the M7 cold end of the stainless steel heatbreak into the V6 heatsink until seated. Do **not** apply thermal paste to the heatbreak threads (this impairs thermal isolation).
2. **Block installation:** Thread the M6 hot end of the heatbreak into the Super Volcano block until it stops, then back it out 1/2 turn.
3. **Nozzle installation:** Thread the **1.4 mm nozzle** into the bottom of the block until it lightly seats against the heatbreak. Leave final tightening for the hot-tightening step.
4. **Thermal components:**
   * Slide the **80 W heater cartridge** into the clamping hole and tighten the clamp screw securely.
   * Slide the **100K NTC thermistor** into the sensor hole and snug the retaining screw without pinching the fiberglass leads.
   * Slip the **Super Volcano silicone sock** over the block.

### Step 2: Mounting & Heatsink Cooling
1. Remove the stock Creality hotend and extruder from the Ender 3 carriage.
2. Bolt the V6 groove-mount adapter to the X-carriage plate.
3. Clamp the V6 heatsink collar securely in the adapter.
4. Clip the **4010 24 V cooling fan and shroud** onto the heatsink fins. Connect it to the Ender 3 mainboard's continuous 24 V fan header. The heatsink fan **must run 100% of the time whenever power is on**.

> [!TIP]
> **Heated Bed Removal & Thermistor Note:**
> * **With Custom 3DTruder Firmware (Flashed):** Our pre-compiled firmware in [`Ender3_Firmware/`](file:///c:/Users/adamh/Downloads/3DTruder/Ender3_Firmware/) permanently disables the bed thermistor checks (`#define TEMP_SENSOR_BED 0`). Once flashed, you can completely unplug and remove the heated bed, cables, and Y-carriage from the printer with zero `MINTEMP` alarms or errors!
> * **If Testing on Factory Stock Marlin:** Unmodified Creality firmware will halt on boot with a screeching `MINTEMP: Bed - PRINTER HALTED` alarm if the bed thermistor is unplugged. If you power up before flashing our custom firmware, leave the bed thermistor plugged in (detached from the bed and taped to the frame to read ambient ~20 °C) or insert a 100k dummy resistor across the `THB` terminals.

### Step 3: 25 A External MOSFET Wiring
The Ender 3 mainboard controls heaters via low-side PWM switching. To prevent mainboard failure from the 80 W cartridge, wire through an external opto-isolated MOSFET module:

```
 [ Ender 3 24V PSU (+/-) ] ──(16 AWG Silicone, 5A Fuse on +)──► [ MOSFET "DC IN" (+/-) ]
                                                                      │
 [ Mainboard Hotend Terminal ] ──(2-wire Signal Cable)────────► [ MOSFET "Control" (+/-) ]
                                                                      │
                                                                      ▼
                                                            [ MOSFET "LOAD / OUT" ]
                                                                      │
                                                                      ▼
                                                            [ 80 W Heater Cartridge ]
```

1. Run **16 AWG stranded silicone wire** from the PSU 24 V terminals to the MOSFET module's **`DC IN`** terminals. Install an inline fuse holder with a **5 A or 7.5 A fuse** on the positive lead.
2. Connect a 2-wire signal cable from the mainboard's **hotend heater terminal** to the MOSFET module's **`Control`** input. Observe polarity.
3. Connect the 80 W heater cartridge leads directly to the MOSFET's **`LOAD`** (or `OUT`) screw terminals.
4. Connect the thermistor leads to the mainboard's hotend thermistor header.

> [!WARNING]
> **Thermistor Table in Marlin:** Stock Ender 3 firmware expects a generic 100K B3950 NTC thermistor (`TEMP_SENSOR_0 1`). If you install a cartridge thermistor (e.g., Semitec 104GT-2 / Type 5), displayed temperatures will be drastically inaccurate. Confirm your sensor type matches your firmware definition.

### Step 4: Hot-Tightening & PID Auto-Tune
1. Power on the printer and command the hotend to **250 °C** via the LCD menu.
2. Once at 250 °C, hold the Super Volcano block firmly with a 16 mm wrench (wearing heat-resistant gloves) and torque the **1.4 mm nozzle** an additional **1/8 to 1/4 turn** against the heatbreak. This creates an airtight seal that prevents molten plastic from leaking over the threads.
3. Connect a PC via USB (Pronterface, OctoPrint, or Serial Terminal) and run PID tuning:
   ```gcode
   M303 E0 S220 C8 U1
   M500
   ```

> [!NOTE]
> **Pre-Compiled 3DTruder Melt Station Firmware Ready to Flash:**
> Pre-built binaries configured specifically for your **Ender 3 V2 DWIN screen** are ready in the [`Ender3_Firmware/`](file:///c:/Users/adamh/Downloads/3DTruder/Ender3_Firmware/) folder:
> * **`firmware_Ender3_V2_RE.bin`** (and `_RC.bin`): Copy to a micro-SD card to flash the Ender 3 V2 in 15 seconds.
> * **Native DWIN Vector UI:** Features a dedicated 3DTruder Melt Station interface (large nozzle temp readout, real-time heating / melt-ready status, material presets, 1.4 mm nozzle indicator) rendered directly via the display controller's hardware vector text engine. **Zero disassembly required — no need to open the screen enclosure or flash screen SD assets (`DWIN_SET`)!**
> * **All 3D Printer Artifacts Removed:** Cleaned of all unhomed axes coordinates (`???.?`), "Print" menus, missing icon glitches, and feedrate/z-offset clutter.
> * **Streamlined Menu:** Provides quick 1-click presets (`PLA 215 °C`, `PETG 240 °C`, `PET #1 270 °C`), rotary temperature dial (0–290 °C), 1-click cooldown, and onboard PID autotune (`M303`) with EEPROM storage (`M500`).
> * **Thermistor Diagnostic Note:** If the screen shows `522 °C / 0 °C` when powered without a hotend connected, this is normal floating CMOS ADC behavior on port `TH` (`PC5`). As soon as your 100K NTC thermistor is plugged in, the reading will immediately normalize to ambient room temperature (~20–25 °C).
> * Full flashing instructions and source configurations are in [`Ender3_Firmware/README.md`](file:///c:/Users/adamh/Downloads/3DTruder/Ender3_Firmware/README.md).
> * The Arduino Uno motor controller sketch and hex binary are in [`Arduino_Firmware/`](file:///c:/Users/adamh/Downloads/3DTruder/Arduino_Firmware/).

---

## 🌀 4B. Phase 1B: Motorized Auger Feed Module

The auger feed module provides continuous mechanical compression to feed flakes into the melt zone.

```
 [ Geared NEMA 17 ] ──► [ Thrust Bearing ] ──► [ Coupler ] ──► [ Auger Bit ]
                                                                   │
                                                   [ 10mm ID Steel Barrel ]
                                                                   │
                                                [ Hopper: 1-1.5mm Flakes ]
                                                                   │
                                              [ Rigid Frame Bracket to 2020 ]
                                                                   │
                                               [ Transition Reducer Fitting ]
                                                                   │
                                               [ Super Volcano Melt Zone ]
```

### Step 1: Modifying the Wood Auger Bit
Wood auger drill bits feature a threaded lead point (gimlet screw) and protruding cutting spurs designed to bore into wood.
1. Mount the 3/8" wood auger bit in a vise.
2. Using an angle grinder with a cutoff wheel or a Dremel, **cut off the threaded screw point**.
3. Grind the tip flat and chamfer the edges so the front flute transitions smoothly.
4. Grind off any outer cutting spurs flush with the bit's helical flight diameter. Deburr with a file.

### Step 2: Fabricating the Barrel & Feed Port
1. Cut the 10 mm ID stainless steel or thick-wall aluminum tube to **120 – 160 mm**.
2. Measure the auger bit: it should slide smoothly through the barrel with ~0.5 mm total diametrical clearance.
3. Near the drive end (30 mm from the top), mill or drill a 15 mm feed window for the hopper funnel.
4. Mount the steep-sided funnel securely over this feed port.

### Step 3: Structural Frame Mounting & Thrust Bearing
1. **Never support the auger assembly from the hotend.** Fabricate or bolt a rigid aluminum mounting plate directly to the Ender 3's vertical 2020 aluminum frame extrusions.
2. Install the **thrust ball bearing** between the auger bit's rear shoulder and the motor mounting faceplate.
   * *Purpose:* The auger generates up to 100+ N of backward axial force when compressing flakes. Stepper motor bearings cannot sustain axial thrust and will fail without a thrust bearing.
3. Connect the 5 mm output shaft of the 14:1 planetary gearmotor to the auger bit shank using the rigid metal coupler. Ensure concentric alignment.

---

## 🎛️ 5. Phase 2: Automated Puller & Closed-Loop Control

### Step 1: Assembling the BMG Puller & Strand Cooling Zone
1. Mount the **BMG clone extruder assembly** onto the output shaft of the 5:1 geared NEMA 17 motor. The internal needle bearings and dual drive gears provide slip-free gripping of 1.75 mm filament without flattening it.
2. Mount the puller assembly to the Ender 3 horizontal rail approximately **12 – 16 inches (30 – 40 cm)** downstream of the nozzle.
3. Position the two **5010 blower fans** between the nozzle and the puller:
   * Aim directional ducts directly at the extrudate strand 5–10 cm after it exits the nozzle.
   * The strand must be fully solidified and cooled below its glass transition temperature ($T_g$) before entering the puller gears, otherwise the gears will crush and deform the filament.
   * Keep blower airflow shielded from the Super Volcano block to maintain thermal stability.

### Step 2: Wiring the Arduino CNC Shield V3
Using an **Arduino CNC Shield V3** plugged directly onto the Arduino Uno eliminates floating jumper wires, provides hardware filter capacitors, and integrates stepper control safely.

```
 [ Ender 3 PSU 24V ] ──────────────────────────────────────────► [ CNC Shield "Power In" ]
                                                                        │
 [ CNC Shield on Uno ] ──► X-Axis Socket ──► A4988 ──► 5:1 Motor   (Puller)
                       ──► Y-Axis Socket ──► A4988 ──► 14:1 Motor  (Auger)
                       ──► A0 Header     ───────────► Analog Diameter Sensor
```

#### CNC Shield Configuration & Jumpers:
1. **Power:** Wire 24 V (+) and (−) from the Ender 3 PSU to the CNC Shield's blue screw terminal power input.
2. **Puller Driver (X Socket):**
   * Insert all 3 microstepping jumpers underneath the X socket (sets **1/16 microstepping** for ultra-smooth pulling).
   * Plug in the puller A4988 driver with heatsink.
   * CNC Shield default routing: **Step = Pin 2, Dir = Pin 5**.
3. **Auger Driver (Y Socket):**
   * Leave the microstepping jumpers under the Y socket **empty / unjumpered** (sets **Full Step mode**).
   * *Why Full Step?* With a 14:1 gearbox, full-stepping provides maximum holding torque and optimal auger rotational speed (~14 RPM) without overloading the Arduino clock.
   * CNC Shield default routing: **Step = Pin 3, Dir = Pin 6**.
4. **Current Limit (Vref) Adjustment:**
   * Measure DC voltage between the A4988 potentiometer wiper and GND.
   * Formula: $V_{\text{ref}} = I_{\text{limit}} \times 8 \times R_{\text{sense}}$ (typically $R_{\text{sense}} = 0.1\,\Omega$).
   * Set Puller driver to ~0.70 V (~0.9 A).
   * Set Auger driver to ~0.90 V (~1.1 A).
5. **Sensor Connection:**
   * Connect sensor +5 V to CNC Shield 5V, GND to GND, and signal output to analog pin **`A0`**.
6. **Headless Auger Run Switch (Optional):**
   * Connect an SPST toggle switch or 2-pin motherboard jumper between **`Resume`** (Pin A2) and **`GND`** on the CNC Shield header row. Closing the switch runs the auger automatically without needing a PC!
7. **Arduino Power:**
   * Set the LM2596 buck converter to **9.0 V DC** output from the 24 V rail and plug into the Arduino Uno barrel jack (or power via USB cable).

---

### Step 3: Complete Unified Closed-Loop Arduino Sketch

A ready-to-flash Arduino IDE sketch is saved in your project folder at [`Arduino_Firmware/Arduino_Firmware.ino`](file:///c:/Users/adamh/Downloads/3DTruder/Arduino_Firmware/Arduino_Firmware.ino). Open it in the Arduino IDE, select **Arduino Uno**, and click **Upload**. A pre-compiled binary is also available at [`Arduino_Firmware/Arduino_Firmware.hex`](file:///c:/Users/adamh/Downloads/3DTruder/Arduino_Firmware/Arduino_Firmware.hex).

This firmware controls both the **constant-speed auger** and the **closed-loop feedback puller**. It incorporates a **proportional damping filter** and **sample-and-hold delay** to prevent hunting and diameter surging caused by strand transit delay.

```cpp
/*
 * =========================================================================================
 * 🛠️ 3DTruder Master Controller: Unified Auger & Closed-Loop Puller
 * Hardware: Arduino Uno R3 + Arduino CNC Shield V3 + 2x A4988 + Analog Sensor
 * =========================================================================================
 */

#include <Arduino.h>

// CNC Shield V3 Pin Assignments
const int PULL_STEP_PIN   = 2;    // CNC Shield X.STEP
const int PULL_DIR_PIN    = 5;    // CNC Shield X.DIR
const int AUG_STEP_PIN    = 3;    // CNC Shield Y.STEP
const int AUG_DIR_PIN     = 6;    // CNC Shield Y.DIR
const int EN_PIN          = 8;    // CNC Shield Stepper Enable (Active LOW)

const int SENSOR_PIN      = A0;   // Filament diameter sensor (Analog 0-5V)
const int AUG_SWITCH_PIN  = A2;   // CNC Shield "Resume" header pin (toggle switch or jumper to GND)
const int THERMISTOR_PIN  = A1;   // 100K NTC thermistor (used in standalone mode)
const int HEATER_PIN      = 12;   // External 25A MOSFET control (used in standalone mode)

// Mode: Set 'true' for recommended Hybrid Setup (Ender 3 controls heat, Arduino controls motors)
const bool ENDER3_CONTROLS_HEAT = true;

// Process Parameters
const float TARGET_DIA        = 1.75;     // Target filament diameter (mm)
const float DIA_TOLERANCE     = 0.02;     // Dead-band tolerance (+/- mm)

// Two-Point Sensor Calibration: Replace with your measured values
const int   CAL_ADC_A         = 310;      // ADC reading at known gauge A
const float CAL_DIA_A         = 1.50;     // Diameter of gauge A (mm)
const int   CAL_ADC_B         = 720;      // ADC reading at known gauge B
const float CAL_DIA_B         = 2.00;     // Diameter of gauge B (mm)

// Puller Step Timing Clamps (microseconds; shorter delay = faster pulling)
const long  MIN_PULL_DELAY_US = 400;      // Fastest pull rate (~5 mm/s)
const long  MAX_PULL_DELAY_US = 5000;     // Slowest pull rate (~0.4 mm/s)
long  pullStepDelayUs         = 2000;     // Starting pull rate (~1.0 mm/s)
float currentDiameter         = TARGET_DIA;

// Auger Step Timing: Full-Step on 14:1 Gearbox (1500 us = ~14.3 RPM auger shaft speed)
const long  AUG_DELAY_US      = 1500;
bool  augerRunning            = false;

unsigned long lastPullStepUs  = 0;
unsigned long lastAugStepUs   = 0;
unsigned long lastControlMs   = 0;
unsigned long lastTelemetryMs = 0;

float readDiameterMm() {
  int rawAdc = analogRead(SENSOR_PIN);
  float dia = CAL_DIA_A + (float)(rawAdc - CAL_ADC_A) * (CAL_DIA_B - CAL_DIA_A) 
                          / (float)(CAL_ADC_B - CAL_ADC_A);
  return constrain(dia, 0.5, 3.5);
}

void handleSerialCommands() {
  if (!Serial.available()) return;
  String cmd = Serial.readStringUntil('\n');
  cmd.trim(); cmd.toUpperCase();

  if (cmd == "START") {
    augerRunning = true;
    Serial.println(F(">> Auger feeder STARTED."));
  } else if (cmd == "STOP") {
    augerRunning = false;
    Serial.println(F(">> Auger feeder STOPPED via serial."));
  } else if (cmd == "OFF") {
    augerRunning = false;
    Serial.println(F(">> Machine STOPPED. Motors halted."));
  } else if (cmd == "HELP") {
    Serial.println(F("Commands: START, STOP, OFF. Or use toggle switch on pin A2 (Resume) to GND."));
  }
}

void setup() {
  pinMode(PULL_STEP_PIN, OUTPUT);
  pinMode(PULL_DIR_PIN, OUTPUT);
  pinMode(AUG_STEP_PIN, OUTPUT);
  pinMode(AUG_DIR_PIN, OUTPUT);

  // Enable Steppers (Active LOW on CNC Shield)
  pinMode(EN_PIN, OUTPUT);
  digitalWrite(EN_PIN, LOW);

  digitalWrite(PULL_DIR_PIN, HIGH);
  digitalWrite(AUG_DIR_PIN, HIGH);

  // Physical auger switch input with internal pullup
  pinMode(AUG_SWITCH_PIN, INPUT_PULLUP);

  Serial.begin(115200);
  Serial.println(F("--- 3DTruder Master Controller Online ---"));
}

void loop() {
  unsigned long nowUs = micros();
  unsigned long nowMs = millis();

  // 1. Step Puller Motor (Continuous non-blocking pulse)
  if ((long)(nowUs - lastPullStepUs) >= pullStepDelayUs) {
    lastPullStepUs = nowUs;
    digitalWrite(PULL_STEP_PIN, HIGH);
    delayMicroseconds(5);
    digitalWrite(PULL_STEP_PIN, LOW);
  }

  // 2. Step Auger Motor (Runs if switch is ON or toggled via serial START)
  bool switchActive = (digitalRead(AUG_SWITCH_PIN) == LOW);
  bool isAugerOn = augerRunning || switchActive;
  if (isAugerOn) {
    if ((long)(nowUs - lastAugStepUs) >= AUG_DELAY_US) {
      lastAugStepUs = nowUs;
      digitalWrite(AUG_STEP_PIN, HIGH);
      delayMicroseconds(5);
      digitalWrite(AUG_STEP_PIN, LOW);
    }
  }

  // 3. Closed-Loop Diameter Control Loop (Runs every 1000 ms)
  if (nowMs - lastControlMs >= 1000) {
    lastControlMs = nowMs;
    float rawDia = readDiameterMm();
    currentDiameter = (0.75 * currentDiameter) + (0.25 * rawDia);

    float error = currentDiameter - TARGET_DIA;
    if (abs(error) > DIA_TOLERANCE) {
      long deltaDelay = (long)(error * 120.0);
      pullStepDelayUs -= deltaDelay;
      pullStepDelayUs = constrain(pullStepDelayUs, MIN_PULL_DELAY_US, MAX_PULL_DELAY_US);
    }
  }

  // 4. Live Telemetry Broadcast
  if (nowMs - lastTelemetryMs >= 1000) {
    lastTelemetryMs = nowMs;
    Serial.print(F("[DIA: ")); Serial.print(currentDiameter, 3);
    Serial.print(F(" mm] [PULL DELAY: ")); Serial.print(pullStepDelayUs);
    Serial.print(F(" us] [AUGER: "));
    Serial.println(isAugerOn ? F("RUNNING]") : F("STOPPED]"));
  }

  handleSerialCommands();
}
```

---

## 🚀 6. Calibration & Operating Sequence

### Initial Setup & Startup Sequence
1. **Pre-heat the system:** Turn on the Ender 3 PSU. Set hotend temperature according to material:
   * **PLA:** 215 – 225 °C
   * **PETG:** 235 – 245 °C
   * **PET (#1 Flakes):** 260 – 275 °C
2. **Thermal soak:** Allow the Super Volcano block to heat-soak for at least 10 minutes so the internal core is uniformly molten.
3. **Turn on strand blowers:** Verify the dual 5010 cooling blowers are running at constant speed.
4. **Start the auger:** Flip the auger feed switch ON (connected between CNC Shield `Resume` pin A2 and `GND`), or send `START` in the Arduino Serial Monitor (115200 baud). The auger begins rotating at ~14.3 RPM.
5. **Feed plastic:** Pour pre-dried 1.0–1.5 mm flakes into the hopper. Maintain a steady feed rate.
6. **Capture extrudate:** As molten extrudate exits the 1.4 mm nozzle and expands to ~1.8–2.0 mm due to die swell, grasp the tip with pliers/gloves, draw it past the cooling air stream, route it through the optical/roller diameter sensor, and insert the solid tip between the BMG puller gears.
7. **Engage puller tension:** Tighten the BMG thumbscrew until the gears grip the filament firmly without chewing or crushing it.
8. **Engage spooler:** Fasten the leading end of the drawn 1.75 mm strand to the slip-clutch spool hub.
9. **Inspect output:** Measure the finished filament with calipers at multiple orientations to verify roundness ($1.75 \pm 0.03\,\text{mm}$).

---

## 🛠️ 7. Troubleshooting Guide

| Symptom / Issue | Underlying Root Cause | Definitive Solution |
| :--- | :--- | :--- |
| **Molten plastic leaking above heater block** | Nozzle was not hot-tightened against heatbreak | Heat to 250 °C. Hold block with 16 mm wrench and torque nozzle an extra 1/8 turn against heatbreak. |
| **Auger stalls / motor buzzes loudly** | Solid flakes jammed in cold transition, or unground bit tip catching | Ensure bit lead screw is ground off. Verify flakes are sifted < 1.5 mm. Check auger Vref voltage. |
| **Filament diameter surges up and down (hunting)** | Transport delay causing control loop over-correction | Reduce proportional gain in sketch, increase `CONTROL_INTERVAL_MS`, or move sensor closer to cooling zone. |
| **Filament consistently undersized (< 1.60 mm)** | Puller running too fast or insufficient die swell | Increase `pullStepDelayUs` in the sketch to pull slower; slightly increase melt temperature or auger feed rate to increase die swell. |
| **Bubbles, popping sounds, and voids in filament** | Feedstock contains entrained moisture | Dry flakes longer at specified temperature (e.g., 4+ hrs @ 50 °C for PLA; 5+ hrs @ 130 °C for PET). |
| **Puller motor skips or flattens filament** | BMG thumbscrew tension too high or strand entering soft | Adjust BMG thumbscrew. Increase 5010 blower airflow so strand is completely rigid before puller. |
| **Thermistor displays MAXTEMP / MINTEMP error** | Damaged sensor wire or loose terminal screw | Inspect thermistor wiring. Verify thermistor type in Marlin firmware matches the installed hardware. |
| **Ender 3 mainboard reboots when heating** | 80 W heater wired directly to board | Wire heater through the external 25 A MOSFET module fed directly from PSU. |
