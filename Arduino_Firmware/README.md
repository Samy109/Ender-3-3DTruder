# 🎛️ Arduino Uno Extruder & Puller Controller Firmware

This firmware runs on your **Arduino Uno R3 + CNC Shield V3** to drive the mechanical extrusion line and manage real-time diameter feedback.

---

## ⚡ How to Flash

### Method 1: Arduino IDE (Easiest)
1. Open [`Arduino_Firmware.ino`](Arduino_Firmware.ino) in the free [Arduino IDE](https://www.arduino.cc/en/software).
2. Select **Tools > Board > Arduino Uno** and select your COM port.
3. Click **Upload** (Arrow icon).

### Method 2: Direct Hex Flashing
* Use **[XLoader](http://www.hobbytronics.co.uk/arduino-xloader)** with the pre-compiled **`Arduino_Firmware.hex`** binary.
* Select device `Uno`, your COM port, baud rate `115200`, and click **Upload**.

---

## 🎛️ CNC Shield V3 Pinouts & Jumper Setup
* **Puller Driver (X Socket):**
  * Insert all 3 jumpers underneath the socket (**1/16 microstepping**).
  * Step = Pin 2, Dir = Pin 5.
* **Auger Driver (Y Socket):**
  * Leave jumpers uninserted (**Full Step mode** for ~14.3 RPM speed).
  * Step = Pin 3, Dir = Pin 6.
* **Stepper Enable:** Pin 8 (automatically driven active-low).
* **Diameter Sensor:** Analog Pin **`A0`** (0–5 V signal).
* **Headless Auger Run Switch (Optional):** Connect a toggle switch or jumper between **`Resume`** (Pin A2) and **`GND`** on the CNC Shield top header. When switched ON (closed to GND), the auger runs automatically without needing a computer attached!

---

## 📊 Live Telemetry & Serial Commands (115200 Baud)
Open Serial Monitor at 115200 baud to view real-time metrics:
```
[DIA: 1.748 mm] [PULL DELAY: 1980 us] [AUGER: RUNNING]
```
Commands you can type in Serial Monitor:
* `START` : Starts the motorized auger feed (software command).
* `STOP`  : Halts the auger feed.
* `OFF`   : Emergency stop (shuts off motor & heater).
* `HELP`  : Displays command menu.
