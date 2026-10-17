# 🎛️ Arduino Uno Extruder & Puller Controller Firmware (V4)

This firmware runs on your **Arduino Uno R3 + CNC Shield V3** to drive the mechanical extrusion line, manage soft-start stepper acceleration, and regulate real-time filament diameter feedback.

---

## ⚡ How to Flash (Recommended)

### Method 1: Arduino IDE (Recommended)
1. Download and install the free [Arduino IDE](https://www.arduino.cc/en/software).
2. Open [`Arduino_Firmware.ino`](Arduino_Firmware.ino) in the Arduino IDE.
3. Edit the settings block at the top of the sketch for your hardware:
   * `CAL_ADC_A` / `CAL_ADC_B`: insert 1.50 mm and 2.00 mm gauge pins (drill blanks) into the sensor and copy the `RAW` value from the telemetry line.
   * `PULL_STEPS_PER_MM`: default 2150 = BMG (~415 steps/mm) x 5.18:1 gearbox at 1/16 microstepping. Calibrate it (instructions in the sketch).
   * `SENSOR_DISTANCE_MM`: measured distance from the nozzle tip to the diameter sensor.
   * `AUG_DIR_INVERT` / `PULL_DIR_INVERT`: flip if a motor runs backwards.
4. Go to **Tools > Board > Arduino AVR Boards > Arduino Uno**.
5. Select your Arduino's serial port under **Tools > Port**.
6. Click **Upload** (Arrow icon).

> [!IMPORTANT]
> `Arduino_Firmware.hex` is built from the current sketch with the **default** calibration values. It is fine for a first bench test, but upload from source once you have your own calibration numbers.

---

## ⚠️ Electrical Pre-Flight Check: CNC Shield V3 Capacitors

> [!CAUTION]
> **Check Capacitor Voltage Ratings Before Connecting 24 V!**
> Budget Arduino CNC Shield V3 clone boards sold on Amazon often ship with **16 V electrolytic capacitors** installed across the motor power rails. Connecting 24 V from the Ender 3 PSU to a 16 V capacitor will cause it to **burst and destroy your A4988 drivers**!
> 
> * **Action:** Look at the small cylinder capacitors next to each stepper socket.
> * If marked **35V or 50V**: Safe to connect directly to the 24 V PSU.
> * If marked **16V or 25V**: Either solder in replacement 35 V 100 µF capacitors, OR power the CNC Shield with 12 V from a buck converter / 12 V power supply (A4988 and NEMA 17 motors run quietly and with high torque on 12 V for low-RPM recycling).

---

## 🎛️ CNC Shield V3 Pinouts & Jumper Setup

* **Puller Driver (X Socket):**
  * Insert all 3 jumpers underneath the socket (**1/16 microstepping** for smooth tensioning).
  * Shield pin routing: Step = Pin 2, Dir = Pin 5.
* **Auger Driver (Y Socket):**
  * Leave jumpers uninserted (**Full Step mode** for maximum torque at ~14 RPM).
  * Set the A4988 current limit to about **0.7 A**. This is the torque limit that keeps a jam from splitting the barrel thread (see the Master Manual, section 5.3).
  * Shield pin routing: Step = Pin 3, Dir = Pin 6.
* **Stepper Enable:** Pin 8 (driven active-low automatically).
* **Diameter Sensor:** Analog Pin **`A0`** (0–5 V analog signal; requires 5V, GND, Signal).
* **Headless Line Run Switch (Optional):** Connect a toggle switch or jumper between **`Resume`** (Pin A2) and **`GND`** on the CNC Shield top header. When closed to GND, both the auger and puller run automatically without needing a PC attached. While it is closed, `STOP` / `AUG OFF` / `PULL OFF` can't stop the motors; open the switch to stop.

---

## 📊 Live Telemetry & Serial Commands (115200 Baud)

Open the Arduino Serial Monitor at **115200 baud** (set line ending to `Newline` or `Both NL & CR`):

```text
[DIA: 1.748mm] [RAW: 498] [PULL: 1.02A] [AUG: 14.0]
```
* `PULL` is the line speed in mm/s; `A` = auto diameter regulation, `M` = manual (frozen).
* `AUG` is the auger shaft speed in RPM.
* With no filament in the sensor it reports `[DIA: EMPTY]` and **holds the current puller speed** (it stops regulating; it does not speed up or slow down).

### How the diameter loop works
The sensor sees filament that was drawn down near the nozzle some time ago (the strand has to travel `SENSOR_DISTANCE_MM` to reach it). After every speed correction the controller waits until that much strand has passed the sensor before it corrects again, so it never chases its own old corrections. Each correction uses mass conservation (speed ∝ diameter²), applies half of the computed change, and is capped at ±10 %.

**Keep the sensor close to the nozzle (10–20 cm, right after the cooling blowers).** At 1 mm/s, every 10 cm of gap adds 100 s between corrections.

### Serial Commands:
* `START`       : Starts auger (soft-start ramp) + puller.
* `STOP` / `OFF`: Stops both motors (unless the A2 run switch is closed). Drivers are de-energized whenever nothing is running.
* `PULL ON` / `PULL OFF` : Puller only (strand threading).
* `AUG ON` / `AUG OFF`   : Auger only.
* `SPEED <x>`   : Set puller speed in mm/s (e.g. `SPEED 1.5`).
* `RPM <x>`     : Set auger speed in RPM, 1–20 (e.g. `RPM 8`). Ramps smoothly.
* `AUTO ON` / `AUTO OFF` : Enable / freeze diameter regulation.
* `HELP`        : Displays the command menu.

> [!WARNING]
> This board does **not** control or monitor the heater — the Ender 3 does. `OFF` stops motors only. Cut heat from the Ender screen (Cooldown).
