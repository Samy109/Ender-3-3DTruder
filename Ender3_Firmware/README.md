# 🖨️ Ender 3 V2 3DTruder Melt Station Firmware (Native DWIN Vector UI)

This dedicated firmware turns your **Ender 3 V2** (Creality 4.2.2 32-bit mainboard) into a high-temperature filament extrusion melt station. It features a **custom, vector UI powered directly by the V2 DWIN screen library** (`DWIN_MARLINUI_PORTRAIT`).

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
|            270 C / 270 C          | <- Large, crisp live readout
|         >>> MELT READY <<<        | <- Green when at target; Yellow when heating
|       THERMAL GUARD: ACTIVE       | <- Watchdog loop armed
+-----------------------------------+
| EXTRUSION PROCESS:                |
| PRESET: PET BOTTLE (270 C)        | <- Dynamic material target
| NOZZLE: 1.4 mm BRASS              | <- Calibrated extrusion orifice
| COOLING: 24V ACTIVE               | <- Heatsink fan status
| PULL: ~250-400 mm/min             | <- Dynamic pull rate speed guide
+-----------------------------------+
|      [ PRESS FOR CONTROLS ]       | <- Encoder prompt
+-----------------------------------+
```

### Eliminated 3D Printer Glitches:
- ❌ **No "Print" or SD media menu** (station operates as a pure melt extruder).
- ❌ **No missing icon squares / artifacts** (stock Creality icon dependencies removed).
- ❌ **No unhomed axes coordinates (`???.?   ???.?   ???.?`)**.
- ❌ **No Z-offset (`0.00`) or feedrate (`100%`) clutter**.
- ❌ **No heated bed readouts or screeching `MINTEMP: Bed` halts**.

---

## 🎛️ Streamlined Melt Control Menu

Clicking the rotary encoder knob opens a clean, focused control menu:

1. **Preheat Presets (1-Click Hotend Priming):**
   - `Preheat PLA` (215 °C)
   - `Preheat PETG` (240 °C)
   - `Preheat PET #1` (270 °C — bottle strip extrusion)
2. **Temperature Control:**
   - Smooth manual dial (0 °C to 290 °C in 1 °C steps)
3. **Cooldown:**
   - 1-click instant hotend heater shutdown (`0 °C`)
4. **Configuration & EEPROM:**
   - **PID Autotune Hotend** (`M303` cycle run directly from screen)
   - **Store Settings** (`M500` saves PID parameters to onboard EEPROM)
   - **Load Settings** (`M501`)
   - **Restore Defaults** (`M502`)
5. **About Station:**
   - Hardware & version info (`3DTruder V2`, `Creality 4.2.2`, `1.4 mm Nozzle`)

---

## ⚠️ Important Hardware Note: `522 °C` Reading

> [!WARNING]
> If your screen displays `522 C / 0 C` on initial boot:
> This occurs when the hotend thermistor is **unplugged or disconnected** from port `TH` (`PC5`) on the Creality mainboard.
> A floating CMOS analog-to-digital converter (ADC) input sits at mid-rail (~1.65 V), which Marlin's 100K NTC thermistor table translates to ~522 °C.
> **As soon as your 100K NTC thermistor is connected to the hotend and plugged into `TH`, the readout will immediately normalize to ambient room temperature (~20 °C – 25 °C).**

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
- [`Configuration.h`](Configuration.h): Full Marlin 2.1.2.4 configuration with thermal limits and presets.
- [`Configuration_adv.h`](Configuration_adv.h): Thermal runaway protection and menu shortcut configuration.
- [`src_patch/`](src_patch/): Custom DWIN vector status screen (`ui_status_480x272.cpp`) and menu layout (`menu_main.cpp`).
