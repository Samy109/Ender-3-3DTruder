/*
 * =========================================================================================
 * 🛠️ 3DTruder All-In-One Recycler Firmware
 * 
 * Target Hardware: Arduino Uno R3 + Arduino CNC Shield V3
 * Runs:
 *   1. Closed-Loop PID Hotend Temperature Controller (up to 290 °C for PET)
 *   2. Thermal Runaway & Sensor Fault Safety Protection
 *   3. Constant-Speed Motorized Auger Feeder (Full Step, ~14.3 RPM)
 *   4. Cold-Extrusion Safety Interlock (Auger won't run until hotend is at temperature)
 *   5. Closed-Loop Diameter Puller Controller (1/16 microstepping, ~1.75 mm target)
 *   6. Interactive Serial Terminal & Live Telemetry UI (115200 baud)
 * 
 * Pinout on Arduino CNC Shield V3:
 *   - Puller Driver (X-Axis): Step = Pin 2, Dir = Pin 5 (1/16 microstep jumpered)
 *   - Auger Driver  (Y-Axis): Step = Pin 3, Dir = Pin 6 (Full-step, unjumpered)
 *   - Stepper Enable (All):   Pin 8 (Active LOW)
 *   - Diameter Sensor:        Analog Pin A0 (0 - 5 V analog input)
 *   - Auger Switch / Jumper:  Pin A2 ("Resume" header on CNC Shield; toggle to GND)
 *   - Hotend Thermistor:      Analog Pin A1 (100k NTC with 4.7k pull-up to 5V; standalone mode)
 *   - 25A MOSFET Control:     Digital Pin 12 (Labeled "SPN.DIR" on CNC Shield header; standalone mode)
 * =========================================================================================
 */

#include <Arduino.h>

// -----------------------------------------------------------------------------------------
// PIN DEFINITIONS
// -----------------------------------------------------------------------------------------
const int PULL_STEP_PIN   = 2;    // CNC Shield X.STEP
const int PULL_DIR_PIN    = 5;    // CNC Shield X.DIR
const int AUG_STEP_PIN    = 3;    // CNC Shield Y.STEP
const int AUG_DIR_PIN     = 6;    // CNC Shield Y.DIR
const int EN_PIN          = 8;    // CNC Shield Stepper Enable (Active LOW)

const int SENSOR_PIN      = A0;   // Filament diameter sensor (Analog 0-5V)
const int AUG_SWITCH_PIN  = A2;   // CNC Shield "Resume" header pin (toggle switch or jumper to GND)
const int THERMISTOR_PIN  = A1;   // 100K NTC thermistor (via 4.7k pullup to 5V)
const int HEATER_PIN      = 12;   // External 25A MOSFET control (SPN.DIR header)

// -----------------------------------------------------------------------------------------
// SYSTEM ARCHITECTURE MODE
// -----------------------------------------------------------------------------------------
// Set to 'true' (RECOMMENDED HYBRID SETUP):
//   - Ender 3 mainboard controls 80W heater & thermistor via custom Marlin + LCD.
//   - Arduino Uno + CNC Shield controls Auger motor, Puller motor, and Diameter sensor.
// Set to 'false' (ALL-IN-ONE ARDUINO SETUP):
//   - Arduino Uno controls heater, thermistor, auger, and puller all by itself.
const bool ENDER3_CONTROLS_HEAT = true;

// -----------------------------------------------------------------------------------------
// TEMPERATURE & THERMAL PROTECTION SETTINGS (Used when ENDER3_CONTROLS_HEAT is false)
// -----------------------------------------------------------------------------------------
const float SERIES_RESISTOR   = 4700.0;   // 4.7k ohm pullup resistor
const float THERMISTOR_NOM    = 100000.0; // 100k ohm at 25 C
const float TEMP_NOMINAL      = 25.0;     // 25 degrees C
const float B_COEFFICIENT     = 3950.0;   // Beta coefficient for 100k NTC B3950
const float MAX_SAFE_TEMP     = 295.0;    // Maximum safe temperature cutoff (C)
const float MIN_SAFE_TEMP     = 5.0;      // Sensor fault / disconnected cutoff (C)

// Temperature PID Constants
float targetTemp = 0.0;                   // Active target temperature (C), 0 = Off
float currentTemp = 0.0;
float pidIntegral = 0.0;
float pidLastError = 0.0;
const float Kp = 4.5;
const float Ki = 0.12;
const float Kd = 15.0;

// Thermal Runaway Watchdog
unsigned long lastTempCheckMs = 0;
unsigned long heatingWatchdogStartMs = 0;
bool thermalError = false;

// -----------------------------------------------------------------------------------------
// DIAMETER SENSOR & PULLER SETTINGS
// -----------------------------------------------------------------------------------------
const float TARGET_DIA        = 1.75;     // Target filament diameter (mm)
const float DIA_TOLERANCE     = 0.02;     // Dead-band tolerance (+/- mm)

// Two-Point Sensor Calibration: Gauge pin ADC calibration points
const int   CAL_ADC_A         = 310;      // ADC value for Gauge A
const float CAL_DIA_A         = 1.50;     // Diameter of Gauge A (mm)
const int   CAL_ADC_B         = 720;      // ADC value for Gauge B
const float CAL_DIA_B         = 2.00;     // Diameter of Gauge B (mm)

// Puller Step Timing Clamps (microseconds)
const long  MIN_PULL_DELAY_US = 400;      // Fastest pull rate (~5 mm/s)
const long  MAX_PULL_DELAY_US = 5000;     // Slowest pull rate (~0.4 mm/s)
long  pullStepDelayUs         = 2000;     // Starting pull rate (~1.0 mm/s)
float currentDiameter         = TARGET_DIA;

// -----------------------------------------------------------------------------------------
// AUGER FEEDER SETTINGS
// -----------------------------------------------------------------------------------------
// 1500 us step delay on full-step mode with 14:1 gearbox = ~14.3 RPM auger shaft speed
const long  AUG_DELAY_US      = 1500;
bool  augerRunning            = false;
bool  coldExtrusionPrevented  = true;     // Interlock: auger halts if temp < (target - 15)

// Non-blocking timing variables
unsigned long lastPullStepUs  = 0;
unsigned long lastAugStepUs   = 0;
unsigned long lastControlMs   = 0;
unsigned long lastTelemetryMs = 0;

// =========================================================================================
// HELPER FUNCTIONS
// =========================================================================================

// Read Thermistor temperature using Steinhart-Hart / Beta equation
float readTemperature() {
  int rawAdc = analogRead(THERMISTOR_PIN);
  if (rawAdc < 10 || rawAdc > 1015) {
    return (rawAdc < 10) ? 999.0 : -99.0; // Open circuit or short circuit
  }
  
  float resistance = SERIES_RESISTOR / (1023.0 / (float)rawAdc - 1.0);
  float steinhart;
  steinhart = resistance / THERMISTOR_NOM;            // (R / Ro)
  steinhart = log(steinhart);                         // ln(R / Ro)
  steinhart /= B_COEFFICIENT;                         // 1/B * ln(R / Ro)
  steinhart += 1.0 / (TEMP_NOMINAL + 273.15);         // + (1 / To)
  steinhart = 1.0 / steinhart;                        // Invert
  steinhart -= 273.15;                                // Convert Kelvin to Celsius
  return steinhart;
}

// Read and linearize filament diameter sensor
float readDiameterMm() {
  int rawAdc = analogRead(SENSOR_PIN);
  float dia = CAL_DIA_A + (float)(rawAdc - CAL_ADC_A) * (CAL_DIA_B - CAL_DIA_A) 
                          / (float)(CAL_ADC_B - CAL_ADC_A);
  return constrain(dia, 0.5, 3.5);
}

// Compute PID output and drive MOSFET
void updateHeaterPID() {
  currentTemp = readTemperature();

  // Safety check 1: Sensor disconnected / shorted
  if (currentTemp < MIN_SAFE_TEMP || currentTemp > MAX_SAFE_TEMP) {
    targetTemp = 0.0;
    analogWrite(HEATER_PIN, 0);
    thermalError = true;
    Serial.println(F("\n❌ [EMERGENCY] THERMISTOR OUT OF RANGE! HEATER SHUT DOWN!"));
    return;
  }

  // If heater is turned off
  if (targetTemp <= 0.0) {
    analogWrite(HEATER_PIN, 0);
    pidIntegral = 0.0;
    heatingWatchdogStartMs = 0;
    return;
  }

  float error = targetTemp - currentTemp;
  
  // Anti-windup clamping on integral
  pidIntegral += error * 0.2; // 200 ms interval
  pidIntegral = constrain(pidIntegral, -100.0, 100.0);

  float pidDerivative = (error - pidLastError) / 0.2;
  pidLastError = error;

  float output = (Kp * error) + (Ki * pidIntegral) + (Kd * pidDerivative);
  int pwmVal = constrain((int)output, 0, 255);

  // Safety check 2: Thermal runaway watchdog
  // If heater is at 100% PWM for 30s and temp does not rise, shut down.
  if (pwmVal >= 250 && error > 10.0) {
    if (heatingWatchdogStartMs == 0) {
      heatingWatchdogStartMs = millis();
    } else if (millis() - heatingWatchdogStartMs > 30000) {
      targetTemp = 0.0;
      analogWrite(HEATER_PIN, 0);
      thermalError = true;
      Serial.println(F("\n❌ [EMERGENCY] THERMAL RUNAWAY DETECTED! HEATER SHUT DOWN!"));
      return;
    }
  } else {
    heatingWatchdogStartMs = 0;
  }

  analogWrite(HEATER_PIN, pwmVal);
}

// Parse user serial commands
void handleSerialCommands() {
  if (!Serial.available()) return;
  String cmd = Serial.readStringUntil('\n');
  cmd.trim();
  cmd.toUpperCase();

  if (cmd.startsWith("T ")) {
    float newTarget = cmd.substring(2).toFloat();
    if (newTarget >= 0.0 && newTarget <= 285.0) {
      targetTemp = newTarget;
      thermalError = false;
      Serial.print(F(">> Set target temperature to: "));
      Serial.print(targetTemp);
      Serial.println(F(" °C"));
    } else {
      Serial.println(F(">> Invalid temperature. Range: 0 to 285 C"));
    }
  } else if (cmd == "OFF") {
    targetTemp = 0.0;
    augerRunning = false;
    analogWrite(HEATER_PIN, 0);
    Serial.println(F(">> Machine STOPPED. Heater & Auger turned OFF."));
    if (digitalRead(AUG_SWITCH_PIN) == LOW) {
      Serial.println(F(">> [NOTE] Physical switch on Pin A2 (Resume) is currently ON. Flip switch OFF for hardware stop."));
    }
  } else if (cmd == "START") {
    augerRunning = true;
    Serial.println(F(">> Auger feeder STARTED."));
  } else if (cmd == "STOP") {
    augerRunning = false;
    Serial.println(F(">> Auger feeder STOPPED via serial."));
    if (digitalRead(AUG_SWITCH_PIN) == LOW) {
      Serial.println(F(">> [NOTE] Physical switch on Pin A2 (Resume) is currently ON. Flip switch OFF to physically stop motor."));
    }
  } else if (cmd == "HELP") {
    Serial.println(F("\n--- 3DTruder Commands ---"));
    Serial.println(F("  START      : Start auger motor (serial override)"));
    Serial.println(F("  STOP       : Stop auger motor"));
    Serial.println(F("  OFF        : Complete shutdown (heater + auger off)"));
    Serial.println(F("  T <temp>   : Set hotend temperature (standalone mode)"));
    Serial.println(F("  [HARDWARE] : Toggle switch or jumper on CNC Shield 'Resume' (A2) to GND runs auger headless."));
    Serial.println(F("-------------------------\n"));
  }
}

// =========================================================================================
// SETUP
// =========================================================================================
void setup() {
  // Stepper output pins
  pinMode(PULL_STEP_PIN, OUTPUT);
  pinMode(PULL_DIR_PIN, OUTPUT);
  pinMode(AUG_STEP_PIN, OUTPUT);
  pinMode(AUG_DIR_PIN, OUTPUT);
  
  // Enable Steppers (Active LOW on CNC Shield)
  pinMode(EN_PIN, OUTPUT);
  digitalWrite(EN_PIN, LOW);

  // Set rotation directions
  digitalWrite(PULL_DIR_PIN, HIGH);
  digitalWrite(AUG_DIR_PIN, HIGH);

  // Physical auger switch input with internal pullup
  pinMode(AUG_SWITCH_PIN, INPUT_PULLUP);

  // Heater MOSFET control pin
  pinMode(HEATER_PIN, OUTPUT);
  analogWrite(HEATER_PIN, 0);

  // Sensor inputs
  pinMode(SENSOR_PIN, INPUT);
  pinMode(THERMISTOR_PIN, INPUT);

  Serial.begin(115200);
  Serial.println(F("=================================================="));
  Serial.println(F("   🛠️ 3DTruder Master Recycler Firmware"));
  Serial.println(F("   Type 'HELP' for serial command menu"));
  Serial.println(F("=================================================="));
}

// =========================================================================================
// MAIN LOOP
// =========================================================================================
void loop() {
  unsigned long nowUs = micros();
  unsigned long nowMs = millis();

  // 1. Step the Puller Motor (Continuous non-blocking pulse)
  if ((long)(nowUs - lastPullStepUs) >= pullStepDelayUs) {
    lastPullStepUs = nowUs;
    digitalWrite(PULL_STEP_PIN, HIGH);
    delayMicroseconds(5);
    digitalWrite(PULL_STEP_PIN, LOW);
  }

  // 2. Step the Auger Motor
  // In Hybrid Mode (ENDER3_CONTROLS_HEAT), auger runs if switch is closed to GND (LOW) OR toggled via Serial START.
  // In Standalone Mode, auger also requires hotend to reach target temperature first.
  bool switchActive = (digitalRead(AUG_SWITCH_PIN) == LOW);
  bool isAugerOn = augerRunning || switchActive;
  bool augerAllowed = ENDER3_CONTROLS_HEAT ? isAugerOn : (isAugerOn && (targetTemp > 100.0) && (currentTemp >= (targetTemp - 15.0)) && !thermalError);
  if (augerAllowed) {
    if ((long)(nowUs - lastAugStepUs) >= AUG_DELAY_US) {
      lastAugStepUs = nowUs;
      digitalWrite(AUG_STEP_PIN, HIGH);
      delayMicroseconds(5);
      digitalWrite(AUG_STEP_PIN, LOW);
    }
  }

  // 3. Update Heater PID Loop (Only active if Arduino controls heat)
  if (!ENDER3_CONTROLS_HEAT) {
    if (nowMs - lastTempCheckMs >= 200) {
      lastTempCheckMs = nowMs;
      if (!thermalError) {
        updateHeaterPID();
      }
    }
  }

  // 4. Closed-Loop Diameter Puller Control (Runs every 1000 ms)
  if (nowMs - lastControlMs >= 1000) {
    lastControlMs = nowMs;

    // Filter sensor readings
    float rawDia = readDiameterMm();
    currentDiameter = (0.75 * currentDiameter) + (0.25 * rawDia);

    float diaError = currentDiameter - TARGET_DIA;
    if (abs(diaError) > DIA_TOLERANCE) {
      // Proportional speed adjustment with transport-delay damping
      long deltaDelay = (long)(diaError * 120.0);
      pullStepDelayUs -= deltaDelay;
      pullStepDelayUs = constrain(pullStepDelayUs, MIN_PULL_DELAY_US, MAX_PULL_DELAY_US);
    }
  }

  // 5. Serial Live Telemetry Output (Runs every 1000 ms)
  if (nowMs - lastTelemetryMs >= 1000) {
    lastTelemetryMs = nowMs;

    if (!ENDER3_CONTROLS_HEAT) {
      Serial.print(F("[TEMP: "));
      Serial.print(currentTemp, 1);
      Serial.print(F(" / "));
      Serial.print(targetTemp, 0);
      Serial.print(F(" °C] "));
    }

    Serial.print(F("[DIA: "));
    Serial.print(currentDiameter, 3);
    Serial.print(F(" mm] "));

    Serial.print(F("[PULL DELAY: "));
    Serial.print(pullStepDelayUs);
    Serial.print(F(" us] "));

    Serial.print(F("[AUGER: "));
    if (isAugerOn) {
      Serial.print(F("RUNNING"));
    } else {
      Serial.print(F("STOPPED"));
    }
    Serial.println(F("]"));
  }

  // 6. Check incoming Serial Terminal commands
  handleSerialCommands();
}
