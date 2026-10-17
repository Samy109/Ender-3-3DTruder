# 🖨️ Ender 3 V2 3DTruder Melt Station Firmware (Native DWIN Vector UI)

This dedicated firmware turns your **Ender 3 V2** (Creality 4.2.2 32-bit mainboard) into a two-zone filament extrusion melt station: **zone 1** is the Super Volcano block (hotend channel), **zone 2** is the heated 316L barrel coupler (the former heated-bed channel). It features a **custom, vector UI powered directly by the V2 DWIN screen library** (`DWIN_MARLINUI_PORTRAIT`).

> [!TIP]
> **Zero Hardware Disassembly Required:**
> This UI renders via the DWIN display controller's native vector engine and onboard hardware fonts. **You do NOT need to open the screen enclosure or flash internal screen SD card assets (`DWIN_SET`).** Simply flash the `.bin` firmware file from the front motherboard SD slot.

---

## 🖥️ Screen Layout & Features

The status screen has been overhauled specifically for 3DTruder bottle-to-filament recycling:

```
+-----------------------------------+
|         3DTRUDER STATION          | <- High-contrast header banner
+-----------------------------------+
| NOZZLE TEMPERATURE:               |
|            270 C / 270 C          | <- Large live readout
|         SOAKING:  07:42           | <- 10-min countdown once both zones at temp
|         >>> MELT READY <<<        | <- Green only after the soak finishes
|      COUPLER: 260 / 260 C         | <- Zone 2 readout (yellow until at temp)
+-----------------------------------+
| EXTRUSION PROCESS:                |
| PRESET: PET (270 C)               | <- Dynamic material target
| THERMAL GUARD: ACTIVE             | <- Runaway protection on both zones
| COOLING: CHECK FAN ON             | <- Reminder (barrel fan is wired to 24 V)
| AUGER: OK TO START                | <- Green after soak; "DO NOT START" before
+-----------------------------------+
|      [ PRESS FOR CONTROLS ]       | <- Encoder prompt
+-----------------------------------+
```

### Melt Soak Timer
The heaters reach temperature long before the barrel end does. Once the nozzle **and** the coupler (if it has a target) are within 3 °C of target, the screen counts down **10 minutes** before showing `MELT READY` / `AUGER: OK TO START`. The countdown restarts if either target changes or either zone drifts more than 5 °C. A coupler target of 0 is ignored, so the line can still run on the nozzle alone. The Arduino can't see the temperature, so this screen is your go / no-go for starting the auger.

### Eliminated 3D Printer Glitches:
- ❌ **No "Print" or SD media menu** (station operates as a pure melt extruder).
- ❌ **No missing icon squares / artifacts** (stock Creality icon dependencies removed).
- ❌ **No unhomed axes coordinates (`???.?   ???.?   ???.?`)**.
- ❌ **No Z-offset (`0.00`) or feedrate (`100%`) clutter**.
- ❌ **No heated-bed clutter**: the bed channel is relabelled **Coupler** in every menu and message.

---

## 🎛️ Streamlined Melt Control Menu

Clicking the rotary encoder knob opens a clean, focused control menu:

1. **Preheat Presets (set both zones):**
   - `Preheat PLA`: nozzle 215 °C, coupler 205 °C
   - `Preheat PETG`: nozzle 240 °C, coupler 230 °C
   - `Preheat PET #1`: nozzle 270 °C, coupler 260 °C
2. **Temperature Control:**
   - Nozzle dial up to 290 °C, Coupler dial up to 280 °C
3. **Cooldown:**
   - 1-click shutdown of both heaters
4. **Configuration & EEPROM:**
   - **PID Autotune** for the nozzle (`M303 E0`) and the Coupler (`M303 E-1`), run from the screen
   - **Store Settings** (`M500` saves PID parameters to onboard EEPROM)
   - **Load Settings** (`M501`)
   - **Restore Defaults** (`M502`)

---

## 🔌 Coupler Zone Wiring
- **Heater:** 24 V 40 W cartridge → mainboard **BED** screw terminals (no external MOSFET needed at 40 W).
- **Thermistor:** 100K B3950 → mainboard **TB** header (`TEMP_SENSOR_BED 1`).
- **Limits:** `BED_MAXTEMP 290` (settable to 280 °C), thermal runaway 60 s / 4 °C, same as the nozzle.
- **PID:** ships with rough starting values. Tune it: `M303 E-1 S205 C8 U1`, then `M500`.

## ⚠️ Thermistor Errors

Both zones use a 5 °C `MINTEMP`, so an unplugged or broken thermistor halts that heater with a `MINTEMP` error instead of heating blind. Plug in **both** thermistors before using a preset. If you see `MINTEMP` or `MAXTEMP`, check the nozzle thermistor on `TH` and the coupler thermistor on `TB`.

If you get `Thermal Runaway` (nozzle or coupler) mid-run, the auger is feeding cold flakes faster than the heaters can keep up. Lower the auger speed (`RPM <x>` on the Arduino) rather than loosening the protection.

---

## 💾 Flashing Guide (30 Seconds)

1. Format a micro-SD card (8 GB to 32 GB) as **FAT32** with **4096-byte allocation**.
2. Select your firmware binary based on the MCU printed on your Creality 4.2.2 board:
   - For **STM32F103RET6 / 512K** chips: use `firmware_Ender3_V2_RE.bin`
   - For **STM32F103RCT6 / GD32F303** chips: use `firmware_Ender3_V2_RC.bin`
3. Copy the `.bin` file to the root of the micro-SD card.
   *(Tip: Creality's bootloader remembers the last flashed filename. If updating again later, rename the file to something unique like `firmware_3dtruder_v1.bin`).*
4. Ensure the printer power is **OFF**.
5. Insert the micro-SD card into the mainboard's front slot.
6. Power **ON** the printer. The screen will remain black for ~10 seconds while flashing, then launch straight into the 3DTruder vector UI!

---

## 📁 Source & Configuration Files
- [`Configuration.h`](Configuration.h): Full Marlin 2.1.2.4 configuration with thermal limits and presets. Build envs: `STM32F103RE_creality` and `STM32F103RC_creality`.
- [`Configuration_adv.h`](Configuration_adv.h): Thermal runaway protection and menu shortcut configuration.
- [`src_patch/`](src_patch/): Custom DWIN vector status screen (`ui_status_480x272.cpp` → `Marlin/src/lcd/e3v2/marlinui/`), menu layout (`menu_main.cpp` → `Marlin/src/lcd/menu/`), and "Bed" → "Coupler" labels (`language_en.h` → `Marlin/src/lcd/language/`).
