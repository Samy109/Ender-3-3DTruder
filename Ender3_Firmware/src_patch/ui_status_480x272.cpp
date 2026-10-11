/**
 * Marlin 3D Printer Firmware
 * Copyright (c) 2021 MarlinFirmware [https://github.com/MarlinFirmware/Marlin]
 *
 * Based on Sprinter and grbl.
 * Copyright (c) 2011 Camiel Gubbels / Erik van der Zalm
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 *
 */

#include "../../../inc/MarlinConfigPre.h"

#if IS_DWIN_MARLINUI

#include "marlinui_dwin.h"
#include "dwin_lcd.h"
#include "dwin_string.h"
#include "lcdprint_dwin.h"

#include "../../utf8.h"
#include "../../../libs/numtostr.h"
#include "../../marlinui.h"

#include "../../../sd/cardreader.h"
#include "../../../module/motion.h"
#include "../../../module/temperature.h"
#include "../../../module/printcounter.h"
#include "../../../module/planner.h"

#if HAS_MEDIA
  #include "../../../libs/duration_t.h"
#endif

#if ENABLED(LCD_SHOW_E_TOTAL)
  #include "../../../MarlinCore.h" // for printingIsActive
#endif

#if ENABLED(DWIN_MARLINUI_PORTRAIT)
  #define STATUS_HEATERS_X    15
  #define STATUS_HEATERS_Y    56
#else
  #define STATUS_HEATERS_X   154
  #define STATUS_HEATERS_Y    10
#endif
#define STATUS_HEATERS_XSPACE 64
#define STATUS_FAN_WIDTH      48
#define STATUS_FAN_HEIGHT     48
#define STATUS_FAN_Y          STATUS_HEATERS_Y + 22
#define STATUS_CHR_WIDTH      14
#define STATUS_CHR_HEIGHT     28

bool old_is_printing;

//
// Before homing, blink '123' <-> '???'.
// Homed but unknown... '123' <-> '   '.
// Homed and known, display constantly.
//
void _draw_axis_value(const AxisEnum axis, const char *value, const bool blink, const uint16_t x, const uint16_t y) {
  const bool x_redraw = !ui.did_first_redraw || old_is_printing != print_job_timer.isRunning();
  if (x_redraw) {
    dwin_string.set('X' + axis);
    DWIN_Draw_String(true, font16x32, Color_IconBlue, Color_Bg_Black,
      #if ENABLED(DWIN_MARLINUI_PORTRAIT)
        x + (utf8_strlen(value) * 14 - 14) / 2, y + 2
      #else
        x, y
      #endif
      , S(dwin_string.string())
    );
  }

  dwin_string.set();
  if (blink)
    dwin_string.add(value);
  else if (!TEST(axes_homed, axis))
    while (const char c = *value++) dwin_string.add(c <= '.' ? c : '?');
  else if (NONE(HOME_AFTER_DEACTIVATE, DISABLE_REDUCED_ACCURACY_WARNING) && !TEST(axes_trusted, axis))
    dwin_string.add(TERN1(DWIN_MARLINUI_PORTRAIT, axis == Z_AXIS) ? PSTR("       ") : PSTR("    "));
  else
    dwin_string.add(value);

  // For E_TOTAL there may be some characters to cover up
  if (TERN0(LCD_SHOW_E_TOTAL, x_redraw && axis == X_AXIS))
    dwin_string.add(F("   "));

  DWIN_Draw_String(true, font14x28, Color_White, Color_Bg_Black,
    #if ENABLED(DWIN_MARLINUI_PORTRAIT)
      x, y + 32
    #else
      x + 32, y + 4
    #endif
    , S(dwin_string.string())
  );
}

#if ENABLED(LCD_SHOW_E_TOTAL)

  void _draw_e_value(const_float_t value, const uint16_t x, const uint16_t y) {
    const uint8_t scale = value >= 100000.0f ? 10 : 1; // show cm after 99,999mm
    const bool e_redraw = !ui.did_first_redraw || old_is_printing != print_job_timer.isRunning();

    #if ENABLED(DWIN_MARLINUI_PORTRAIT)

      if (e_redraw) {
        // Extra spaces to erase previous value
        dwin_string.set(F("E         "));
        DWIN_Draw_String(true, font16x32, Color_IconBlue, Color_Bg_Black, x + (4 * 14 / 2) - 7, y + 2, S(dwin_string.string()));
      }

      dwin_string.set(ui16tostr5rj(value / scale));
      DWIN_Draw_String(true, font14x28, Color_White, Color_Bg_Black, x, y + 32, S(dwin_string.string()));

      // Extra spaces to erase previous value
      DWIN_Draw_String(true, font14x28, Color_IconBlue, Color_Bg_Black, x + (5 * 14), y + 32, S(scale == 1 ? "mm      " : "cm      "));

    #else // !DWIN_MARLINUI_PORTRAIT

      if (e_redraw) {
        dwin_string.set(F("E "));
        DWIN_Draw_String(true, font16x32, Color_IconBlue, Color_Bg_Black, x, y, S(dwin_string.string()));
      }

      dwin_string.set(ui16tostr5rj(value / scale));
      DWIN_Draw_String(true, font14x28, Color_White, Color_Bg_Black, x + 32, y + 4, S(dwin_string.string()));

      DWIN_Draw_String(true, font14x28, Color_IconBlue, Color_Bg_Black, x + (32 + 70), y + 4, S(scale == 1 ? "mm      " : "cm      "));

    #endif // !DWIN_MARLINUI_PORTRAIT
  }

#endif // LCD_SHOW_E_TOTAL

#if HAS_FAN
  //
  // Fan Icon and Percentage
  //
  FORCE_INLINE void _draw_fan_status(const uint16_t x, const uint16_t y) {
    const uint16_t fanx = (4 * STATUS_CHR_WIDTH - STATUS_FAN_WIDTH) / 2;
    const bool fan_on = !!thermalManager.scaledFanSpeed(0);
    if (fan_on) {
      DWIN_ICON_Animation(0, fan_on, ICON, ICON_Fan0, ICON_Fan3, x + fanx, y, 25);
      dwin_string.set(i8tostr3rj(thermalManager.scaledFanSpeedPercent(0)));
      dwin_string.add('%');
      DWIN_Draw_String(true, font14x28, Color_White, Color_Bg_Black, x, y + STATUS_FAN_HEIGHT, S(dwin_string.string()));
    }
    else {
      DWIN_ICON_AnimationControl(0x0000); // disable all icon animations (this is the only one)
      DWIN_ICON_Show(ICON, ICON_Fan0, x + fanx, y);
      dwin_string.set(F("    "));
      DWIN_Draw_String(true, font14x28, Color_White, Color_Bg_Black, x, y + STATUS_FAN_HEIGHT, S(dwin_string.string()));
    }
  }
#endif

/**
 * Draw a single heater icon with current and target temperature, at the given XY
 */
FORCE_INLINE void _draw_heater_status(const heater_id_t heater, const uint16_t x, const uint16_t y) {

  #if HAS_HOTEND
    #if HOTENDS > 2
      #define HOTEND_STATS 3
    #elif HOTENDS > 1
      #define HOTEND_STATS 2
    #else
      #define HOTEND_STATS 1
    #endif
    static celsius_t old_temp[HOTEND_STATS] = { 0 },
                   old_target[HOTEND_STATS] = { 0 };
    static bool old_on[HOTEND_STATS] = { false };
  #endif

  #if HAS_HEATED_BED
    static celsius_t old_bed_temp = 0, old_bed_target = 0;
    static bool old_bed_on = false;
    #if HAS_LEVELING
      static bool old_leveling_on = false;
    #endif
  #endif

  celsius_float_t tc = 0, tt = 0;
  bool isBed = (DISABLED(HAS_HOTEND) && ENABLED(HAS_HEATED_BED)) || (ALL(HAS_HOTEND, HAS_HEATED_BED) && heater < 0),
       ta = false, c_draw, t_draw, i_draw;
  c_draw = t_draw = i_draw = !ui.did_first_redraw;
  if (isBed) {
    #if HAS_HEATED_BED
      tc = thermalManager.degBed();
      tt = thermalManager.degTargetBed();
      ta = thermalManager.isHeatingBed();
      c_draw |= tc != old_bed_temp;
      t_draw |= tt != old_bed_target;
      i_draw |= ta != old_bed_on;
      old_bed_temp = tc;
      old_bed_target = tt;
      old_bed_on = ta;
      #if HAS_LEVELING
        i_draw |= planner.leveling_active != old_leveling_on;
        old_leveling_on = planner.leveling_active;
      #endif
    #endif
  }
  else {
    #if HAS_HOTEND
      tc = thermalManager.degHotend(heater);
      tt = thermalManager.degTargetHotend(heater);
      ta = thermalManager.isHeatingHotend(heater);
      c_draw |= tc != old_temp[heater];
      t_draw |= tt != old_target[heater];
      i_draw |= ta != old_on[heater];
      old_temp[heater] = tc;
      old_target[heater] = tt;
      old_on[heater] = ta;
    #endif
  }

  // Draw target temperature, if needed
  if (t_draw) {
    dwin_string.set(i16tostr3rj(tt + 0.5));
    dwin_string.add(LCD_STR_DEGREE);
    DWIN_Draw_String(true, font14x28, Color_White, Color_Bg_Black, x, y, S(dwin_string.string()));
  }

  // Draw heater icon with on / off / leveled states
  if (i_draw) {
    const uint8_t ico = isBed ? (TERN0(HAS_LEVELING, planner.leveling_active) ? ICON_BedLevelOff : ICON_BedOff) : ICON_HotendOff;
    DWIN_ICON_Show(ICON, ico + ta, x, y + STATUS_CHR_HEIGHT + 2);
  }

  // Draw current temperature, if needed
  if (c_draw) {
    dwin_string.set(i16tostr3rj(tc + 0.5));
    dwin_string.add(LCD_STR_DEGREE);
    DWIN_Draw_String(true, font14x28, Color_White, Color_Bg_Black, x, y + 70, S(dwin_string.string()));
  }
}

/**
 * Draw the current "feed rate" percentage preceded by the >> character
 */
FORCE_INLINE void _draw_feedrate_status(const char *value, uint16_t x, uint16_t y) {
  if (!ui.did_first_redraw) {
    dwin_string.set(LCD_STR_FEEDRATE);
    DWIN_Draw_String(true, font14x28, Color_IconBlue, Color_Bg_Black, x, y, S(dwin_string.string()));
  }

  dwin_string.set(value);
  dwin_string.add('%');
  DWIN_Draw_String(true, font14x28, Color_White, Color_Bg_Black, x + 14, y, S(dwin_string.string()));
}

// Draw 3DTruder Melt Station Status Screen
void MarlinUI::draw_status_screen() {
  if (!ui.did_first_redraw) {
    // Clear screen to black
    DWIN_Frame_Clear(Color_Bg_Black);

    // Top Header Banner
    DWIN_Draw_Rectangle(1, Color_Bg_Blue, 0, 0, DWIN_WIDTH, 42);
    DWIN_Draw_String(false, font14x28, Color_White, Color_Bg_Blue, 24, 7, F("3DTRUDER STATION"));

    // Box 1: Nozzle Temperature Box (Y: 50 to 222)
    DWIN_Draw_Rectangle(0, Select_Color, 6, 50, DWIN_WIDTH - 7, 222);
    DWIN_Draw_String(false, font10x20, Color_IconBlue, Color_Bg_Black, 41, 58, F("NOZZLE TEMPERATURE:"));

    // Box 2: Extrusion Process Box (Y: 230 to 418)
    DWIN_Draw_Rectangle(0, Select_Color, 6, 230, DWIN_WIDTH - 7, 418);
    DWIN_Draw_String(false, font10x20, Color_IconBlue, Color_Bg_Black, 46, 238, F("EXTRUSION PROCESS:"));

    // Bottom Prompt Bar (Y: 428 to 478)
    DWIN_Draw_Rectangle(1, Color_Bg_Blue, 0, 428, DWIN_WIDTH, 478);
    DWIN_Draw_String(false, font10x20, Color_White, Color_Bg_Blue, 21, 444, F("[ PRESS FOR CONTROLS ]"));
  }

  // Live Nozzle Temperature update: Current / Target
  celsius_t cur = thermalManager.wholeDegHotend(0);
  celsius_t tgt = thermalManager.degTargetHotend(0);

  static celsius_t last_cur = -999, last_tgt = -999;
  if (!ui.did_first_redraw || cur != last_cur || tgt != last_tgt) {
    last_cur = cur;
    last_tgt = tgt;

    // Line 1: Big Nozzle Readout (Centered)
    dwin_string.set(i16tostr3rj(cur));
    dwin_string.add(F(" C / "));
    dwin_string.add(i16tostr3rj(tgt));
    dwin_string.add(F(" C"));
    DWIN_Draw_String(true, font16x32, Color_White, Color_Bg_Black, 16, 92, S(dwin_string.string()));

    // Line 2: Heating Status
    dwin_string.set();
    uint16_t stateColor = Color_White;
    if (tgt == 0) {
      dwin_string.set(F("  HEATER: OFF       "));
      stateColor = Color_White;
    }
    else if (abs(cur - tgt) <= 3) {
      dwin_string.set(F(" >>> MELT READY <<< "));
      stateColor = RGB(0x00,0x3F,0x00); // Bright Green
    }
    else if (cur < tgt) {
      dwin_string.set(F(" STATUS: HEATING... "));
      stateColor = Color_Yellow;
    }
    else {
      dwin_string.set(F(" STATUS: COOLING... "));
      stateColor = Color_Yellow;
    }
    DWIN_Draw_String(true, font14x28, stateColor, Color_Bg_Black, 0, 140, S(dwin_string.string()));

    // Line 3: Thermal Guard state
    dwin_string.set(F("THERMAL GUARD: ACTIVE "));
    DWIN_Draw_String(true, font10x20, Color_White, Color_Bg_Black, 26, 182, S(dwin_string.string()));

    // Box 2 - Line 1: Preset
    dwin_string.set(F("PRESET: "));
    if (tgt == 215)      dwin_string.add(F("PLA (215 C)     "));
    else if (tgt == 240) dwin_string.add(F("PETG (240 C)    "));
    else if (tgt == 270) dwin_string.add(F("PET BOTTLE (270)"));
    else if (tgt == 0)   dwin_string.add(F("STANDBY (OFF)   "));
    else {
      dwin_string.add(F("CUSTOM ("));
      dwin_string.add(i16tostr3rj(tgt));
      dwin_string.add(F(" C) "));
    }
    DWIN_Draw_String(true, font12x24, Color_White, Color_Bg_Black, 16, 268, S(dwin_string.string()));

    // Box 2 - Line 2: Nozzle Spec
    DWIN_Draw_String(false, font10x20, Color_White, Color_Bg_Black, 16, 305, F("NOZZLE : 1.4 mm BRASS"));

    // Box 2 - Line 3: Hotend Fan
    DWIN_Draw_String(false, font10x20, Color_White, Color_Bg_Black, 16, 338, F("COOLING: 24V ACTIVE  "));

    // Box 2 - Line 4: Pull Rate Guide
    if (tgt > 0 && abs(cur - tgt) <= 3) {
      DWIN_Draw_String(true, font10x20, RGB(0x00,0x3F,0x00), Color_Bg_Black, 16, 372, F("PULL: ~250-400 mm/min"));
    }
    else {
      DWIN_Draw_String(true, font10x20, Color_White, Color_Bg_Black, 16, 372, F("PULL: STANDBY / WAIT "));
    }
  }

  ui.did_first_redraw = true;
}

#endif // IS_DWIN_MARLINUI
