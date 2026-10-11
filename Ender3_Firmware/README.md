# 🖨️ Ender 3 V2 Melt Station Firmware (Color DWIN UI)

This firmware turns your **Ender 3 V2** into a dedicated high-temperature melt station while preserving the full color graphical screen interface.

---

## 💾 Quick Flashing (30 Seconds)

1. Format a standard MicroSD card as **FAT32** (4096-byte allocation).
2. Copy **`firmware_Ender3_V2_RE.bin`** onto the root of the MicroSD card.
   *(Note: If your board has the GD32/RC processor, use `firmware_Ender3_V2_RC.bin` instead).*
3. Ensure the Ender 3 V2 is **powered OFF**.
4. Insert the MicroSD card into the printer's front card slot.
5. Turn **ON** the power switch.
6. The V2 color screen will remain black for ~10–15 seconds while the bootloader flashes the chip, then boot into the custom **3DTruder V2** color graphical interface!

---

## ⚡ What Is Configured:
* **V2 DWIN Color Screen Active:** Beautiful color icons, live temperature graphs, and rotary dial control.
* **Bed Thermistor Disabled (`TEMP_SENSOR_BED 0`):** No screeching `MINTEMP: Bed` halts when the print bed is removed.
* **Max Temperature Raised to 290 °C:** Unlocked to 305 °C limit (`HEATER_0_MAXTEMP 305`), allowing you to dial up to 290 °C for #1 PET bottle flakes.
* **Super Volcano Watchdog (`THERMAL_PROTECTION_PERIOD 60`):** Adjusted to handle the thermal mass of the 80 W heater and brass block.
* **Cold Extrusion Lock Removed:** No blocking print checks.

---

## 📁 Source Configuration Files Included
* [`Configuration.h`](Configuration.h): Complete Marlin V2 DWIN configuration.
* [`Configuration_adv.h`](Configuration_adv.h): Advanced thermal protection and buffer configuration.
