/*
 * =========================================================================================
 * 3DTruder Puller & Auger Controller Firmware (V4)
 *
 * Target Hardware: Arduino Uno R3 (ATmega328P) + Arduino CNC Shield V3
 *   - Puller (X socket, 1/16 microstep): Step = Pin 2 (PD2), Dir = Pin 5
 *   - Auger  (Y socket, full step):      Step = Pin 3 (PD3), Dir = Pin 6
 *   - Stepper Enable:                    Pin 8 (active LOW, shared)
 *   - Diameter sensor (0-5 V analog):    A0 ("Abort" header)
 *   - Headless run switch to GND:        A2 ("Resume" header)
 *
 * Heater / thermistor are controlled by the Ender 3 V2 mainboard (Marlin), NOT this board.
 * This board has no idea whether the melt zone is hot -- never start the auger cold.
 *
 * Architecture:
 *   1. Timer1 ISR steps the puller (0.5 us resolution, independent of loop()).
 *   2. Timer2 ISR (20 kHz) steps the auger (50 us resolution, independent of loop()).
 *   3. Non-blocking ADC, 16-sample averaging on the diameter sensor.
 *   4. Dead-time-aware diameter control: after each speed correction the controller waits
 *      until the strand has travelled from the nozzle to the sensor before correcting again,
 *      so it never reacts to filament that was drawn before its last change.
 *   5. Corrections are made in mm/s using mass conservation (speed ~ diameter^2).
 *   6. Non-blocking serial command parser (115200 baud, Newline line ending).
 * =========================================================================================
 */

#include <Arduino.h>
#include <util/atomic.h>

// -----------------------------------------------------------------------------------------
// PINS (Arduino CNC Shield V3). Step pins are hard-wired to PD2 / PD3 inside the ISRs.
// -----------------------------------------------------------------------------------------
const uint8_t PULL_DIR_PIN    = 5;
const uint8_t AUG_DIR_PIN     = 6;
const uint8_t PULL_STEP_PIN   = 2;    // PD2
const uint8_t AUG_STEP_PIN    = 3;    // PD3
const uint8_t EN_PIN          = 8;    // Active LOW
const uint8_t SENSOR_PIN      = A0;   // ADC channel 0
const uint8_t RUN_SWITCH_PIN  = A2;   // Close to GND = run auger + puller headless

// Flip these if a motor turns the wrong way (or swap one coil pair on its connector).
// The auger must turn so the flights carry flakes TOWARD the nozzle (clockwise viewed from
// the motor for a standard right-hand wood auger bit).
const bool PULL_DIR_INVERT    = false;
const bool AUG_DIR_INVERT     = false;

// -----------------------------------------------------------------------------------------
// PULLER MECHANICS -- CALIBRATE PULL_STEPS_PER_MM!
// -----------------------------------------------------------------------------------------
// BMG clone (~415 steps/mm at 1/16 microstepping) x 5.18:1 planetary gearbox = ~2150 steps/mm.
// To calibrate: thread filament, send "SPEED 1", "PULL ON", time 60 s, measure how far the
// strand moved (L mm), then set PULL_STEPS_PER_MM = 2150 * 60 / L.
const float PULL_STEPS_PER_MM = 2150.0;
const float PULL_NOMINAL_MM_S = 1.0;    // Starting line speed after power-up
const float PULL_MIN_MM_S     = 0.1;
const float PULL_MAX_MM_S     = 6.0;    // ~12.9k steps/s at 2150 steps/mm

// -----------------------------------------------------------------------------------------
// AUGER
// -----------------------------------------------------------------------------------------
const float AUG_STEPS_PER_REV = 200.0 * 14.0;   // Full step x 14:1 gearbox
const float AUG_DEFAULT_RPM   = 14.0;
const float AUG_START_RPM     = 4.0;            // Soft-start begins here
const float AUG_MIN_RPM       = 1.0;
const float AUG_MAX_RPM       = 20.0;
const float AUG_RAMP_RPM_S    = 7.0;            // 4 -> 14 RPM in ~1.5 s

// -----------------------------------------------------------------------------------------
// DIAMETER SENSOR & CONTROL LOOP
// -----------------------------------------------------------------------------------------
const float TARGET_DIA        = 1.75;     // mm
const float DIA_TOLERANCE     = 0.02;     // Dead band (+/- mm)
const float MIN_VALID_DIA     = 1.10;     // Below = empty sensor
const float MAX_VALID_DIA     = 2.40;     // Above = sensor unseated / lump / foreign object

// Two-point calibration: insert gauge pins (drill blanks) and note the ADC value from the
// "RAW" field of the telemetry line.
const int   CAL_ADC_A         = 300;
const float CAL_DIA_A         = 1.50;
const int   CAL_ADC_B         = 700;
const float CAL_DIA_B         = 2.00;

// Distance from the nozzle tip to the diameter sensor. Keep this SHORT (10-20 cm): the
// controller can only correct once per this much strand, so at 1 mm/s a 150 mm gap means
// one correction every 2.5 minutes.
const float SENSOR_DISTANCE_MM          = 150.0;
const float CONTROL_GAIN                = 0.5;    // Fraction of computed correction applied
const float MAX_CORRECTION              = 0.10;   // Max +/-10 % speed change per correction
const unsigned long MIN_CORRECTION_MS   = 2000;
const unsigned long EMPTY_TIMEOUT_MS    = 1500;   // Invalid this long = filament absent

// -----------------------------------------------------------------------------------------
// STATE
// -----------------------------------------------------------------------------------------
// Shared with ISRs
volatile bool     pullIsrActive   = false;
volatile uint16_t pullTimerTop    = 4000;
volatile uint32_t pullStepCount   = 0;
volatile bool     augIsrActive    = false;
volatile uint16_t augPeriodTicks  = 100;

// Operator state
bool  augerRunning    = false;
bool  pullerRunning   = false;
bool  autoMode        = true;
float pullSpeedMmS    = PULL_NOMINAL_MM_S;
float augTargetRpm    = AUG_DEFAULT_RPM;
float augCurrentRpm   = AUG_START_RPM;

// Sensor state
float    currentDiameter   = TARGET_DIA;
int      lastRawAdc        = 0;
bool     filamentPresent   = false;
bool     adcPending        = false;
uint32_t adcSum            = 0;
uint8_t  adcCount          = 0;
const uint8_t ADC_SAMPLES  = 16;

// Control state
uint32_t correctionStartSteps = 0;
unsigned long lastCorrectionMs = 0;
unsigned long lastValidMs      = 0;

// Run switch debounce
bool switchActive = false;
bool switchRaw    = false;
unsigned long switchChangedMs = 0;

// Timing
unsigned long lastRampMs      = 0;
unsigned long lastAdcMs       = 0;
unsigned long lastTelemetryMs = 0;

char    serialRxBuf[32];
uint8_t serialRxIdx = 0;

// =========================================================================================
// INTERRUPTS
// =========================================================================================
// Puller: Timer1 CTC, 2 MHz tick. Fires once per step.
ISR(TIMER1_COMPA_vect) {
  OCR1A = pullTimerTop;
  if (pullIsrActive) {
    PORTD |= (1 << PD2);
    pullStepCount++;
    delayMicroseconds(2);
    PORTD &= ~(1 << PD2);
  }
}

// Auger: Timer2 CTC at 20 kHz. Step pulse is held high for one tick (50 us).
ISR(TIMER2_COMPA_vect) {
  static uint16_t countdown = 1;
  PORTD &= ~(1 << PD3);
  if (augIsrActive && --countdown == 0) {
    countdown = augPeriodTicks;
    PORTD |= (1 << PD3);
  }
}

void initTimers() {
  noInterrupts();
  // Timer1: CTC, prescaler 8 -> 2 MHz
  TCCR1A = 0;
  TCCR1B = (1 << WGM12) | (1 << CS11);
  TCNT1  = 0;
  OCR1A  = pullTimerTop;
  TIMSK1 = (1 << OCIE1A);
  // Timer2: CTC, prescaler 8, OCR2A 99 -> 20 kHz
  TCCR2A = (1 << WGM21);
  TCCR2B = (1 << CS21);
  TCNT2  = 0;
  OCR2A  = 99;
  TIMSK2 = (1 << OCIE2A);
  interrupts();
}

void applyPullSpeed() {
  pullSpeedMmS = constrain(pullSpeedMmS, PULL_MIN_MM_S, PULL_MAX_MM_S);
  uint16_t top = (uint16_t)(2000000.0 / (pullSpeedMmS * PULL_STEPS_PER_MM)) - 1;
  ATOMIC_BLOCK(ATOMIC_RESTORESTATE) { pullTimerTop = top; }
}

void applyAugerRpm() {
  uint16_t ticks = (uint16_t)(1200000.0 / (augCurrentRpm * AUG_STEPS_PER_REV) + 0.5);
  if (ticks < 2) ticks = 2;
  ATOMIC_BLOCK(ATOMIC_RESTORESTATE) { augPeriodTicks = ticks; }
}

uint32_t readPullSteps() {
  uint32_t s;
  ATOMIC_BLOCK(ATOMIC_RESTORESTATE) { s = pullStepCount; }
  return s;
}

// =========================================================================================
// NON-BLOCKING ADC
// =========================================================================================
void initADC() {
  ADMUX  = (1 << REFS0);                                        // AVcc ref, channel A0
  ADCSRA = (1 << ADEN) | (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0); // 125 kHz ADC clock
}

float adcToDiameter(float raw) {
  return CAL_DIA_A + (raw - CAL_ADC_A) * (CAL_DIA_B - CAL_DIA_A) / (float)(CAL_ADC_B - CAL_ADC_A);
}

// =========================================================================================
// COMMANDS
// =========================================================================================
void printHelp() {
  Serial.println(F("\n--- 3DTruder Controller Commands ---"));
  Serial.println(F("  START       : Start auger + puller"));
  Serial.println(F("  STOP        : Stop auger + puller"));
  Serial.println(F("  PULL ON/OFF : Puller only (threading)"));
  Serial.println(F("  AUG ON/OFF  : Auger only"));
  Serial.println(F("  SPEED <x>   : Set puller speed, mm/s"));
  Serial.println(F("  RPM <x>     : Set auger speed, RPM"));
  Serial.println(F("  AUTO ON/OFF : Diameter auto-regulation"));
  Serial.println(F("  OFF         : Stop all + de-energize motors"));
  Serial.println(F("  Switch A2->GND runs auger + puller headless"));
  Serial.println(F("------------------------------------\n"));
}

void executeCommand(char* cmd) {
  while (*cmd == ' ' || *cmd == '\t') cmd++;

  if (strcmp(cmd, "START") == 0) {
    augerRunning = pullerRunning = true;
    Serial.println(F(">> Line STARTED"));
  } else if (strcmp(cmd, "STOP") == 0 || strcmp(cmd, "OFF") == 0) {
    augerRunning = pullerRunning = false;
    Serial.println(F(">> Line STOPPED"));
  } else if (strcmp(cmd, "PULL ON") == 0) {
    pullerRunning = true;
    Serial.println(F(">> Puller ON"));
  } else if (strcmp(cmd, "PULL OFF") == 0) {
    pullerRunning = false;
    Serial.println(F(">> Puller OFF"));
  } else if (strcmp(cmd, "AUG ON") == 0) {
    augerRunning = true;
    Serial.println(F(">> Auger ON"));
  } else if (strcmp(cmd, "AUG OFF") == 0) {
    augerRunning = false;
    Serial.println(F(">> Auger OFF"));
  } else if (strcmp(cmd, "AUTO ON") == 0) {
    autoMode = true;
    Serial.println(F(">> Auto diameter control ON"));
  } else if (strcmp(cmd, "AUTO OFF") == 0) {
    autoMode = false;
    Serial.println(F(">> Auto diameter control OFF (speed frozen)"));
  } else if (strncmp(cmd, "SPEED ", 6) == 0) {
    pullSpeedMmS = atof(cmd + 6);
    applyPullSpeed();
    correctionStartSteps = readPullSteps();
    Serial.print(F(">> Puller speed = "));
    Serial.print(pullSpeedMmS, 2);
    Serial.println(F(" mm/s"));
  } else if (strncmp(cmd, "RPM ", 4) == 0) {
    augTargetRpm = constrain(atof(cmd + 4), AUG_MIN_RPM, AUG_MAX_RPM);
    Serial.print(F(">> Auger target = "));
    Serial.print(augTargetRpm, 1);
    Serial.println(F(" RPM"));
  } else if (strcmp(cmd, "HELP") == 0) {
    printHelp();
  } else {
    Serial.print(F(">> Unknown command: "));
    Serial.println(cmd);
  }
}

void pollSerialCommands() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\r') continue;
    if (c == '\n') {
      if (serialRxIdx > 0) {
        serialRxBuf[serialRxIdx] = '\0';
        executeCommand(serialRxBuf);
        serialRxIdx = 0;
      }
    } else if (serialRxIdx < sizeof(serialRxBuf) - 1) {
      if (c >= 'a' && c <= 'z') c -= 32;
      serialRxBuf[serialRxIdx++] = c;
    }
  }
}

// =========================================================================================
// SETUP
// =========================================================================================
void setup() {
  pinMode(PULL_STEP_PIN, OUTPUT);
  pinMode(PULL_DIR_PIN, OUTPUT);
  pinMode(AUG_STEP_PIN, OUTPUT);
  pinMode(AUG_DIR_PIN, OUTPUT);
  pinMode(EN_PIN, OUTPUT);
  digitalWrite(EN_PIN, HIGH);   // Drivers off until something runs

  digitalWrite(PULL_DIR_PIN, PULL_DIR_INVERT ? LOW : HIGH);
  digitalWrite(AUG_DIR_PIN, AUG_DIR_INVERT ? LOW : HIGH);

  pinMode(RUN_SWITCH_PIN, INPUT_PULLUP);
  pinMode(SENSOR_PIN, INPUT);

  initADC();
  applyPullSpeed();
  applyAugerRpm();
  initTimers();

  Serial.begin(115200);
  Serial.println(F("=================================================="));
  Serial.println(F("   3DTruder Puller & Auger Controller V4"));
  Serial.println(F("   Heater is controlled by the Ender 3 - preheat"));
  Serial.println(F("   and soak BEFORE starting the auger."));
  Serial.println(F("=================================================="));
  printHelp();
}

// =========================================================================================
// MAIN LOOP (only bookkeeping -- all stepping happens in the ISRs)
// =========================================================================================
void loop() {
  unsigned long nowMs = millis();

  // 1. Debounced headless run switch
  bool raw = (digitalRead(RUN_SWITCH_PIN) == LOW);
  if (raw != switchRaw) {
    switchRaw = raw;
    switchChangedMs = nowMs;
  } else if (nowMs - switchChangedMs >= 50) {
    switchActive = switchRaw;
  }

  bool augerActive  = augerRunning || switchActive;
  bool pullerActive = pullerRunning || switchActive;

  digitalWrite(EN_PIN, (augerActive || pullerActive) ? LOW : HIGH);
  if (pullerActive && !pullIsrActive) correctionStartSteps = readPullSteps();
  pullIsrActive = pullerActive;
  augIsrActive  = augerActive;

  // 2. Auger soft-start ramp (every 10 ms)
  if (nowMs - lastRampMs >= 10) {
    lastRampMs = nowMs;
    if (!augerActive) {
      augCurrentRpm = min(AUG_START_RPM, augTargetRpm);
    } else if (augCurrentRpm != augTargetRpm) {
      float stepRpm = AUG_RAMP_RPM_S * 0.01;
      if (augCurrentRpm < augTargetRpm) augCurrentRpm = min(augCurrentRpm + stepRpm, augTargetRpm);
      else                              augCurrentRpm = max(augCurrentRpm - stepRpm, augTargetRpm);
    }
    applyAugerRpm();
  }

  // 3. Non-blocking ADC: one conversion every 25 ms, averaged over 16 samples (400 ms)
  if (!adcPending && nowMs - lastAdcMs >= 25) {
    lastAdcMs = nowMs;
    ADCSRA |= (1 << ADSC);
    adcPending = true;
  }
  if (adcPending && !(ADCSRA & (1 << ADSC))) {
    adcPending = false;
    adcSum += ADC;
    if (++adcCount >= ADC_SAMPLES) {
      float avgRaw = adcSum / (float)ADC_SAMPLES;
      adcSum = 0;
      adcCount = 0;
      lastRawAdc = (int)(avgRaw + 0.5);

      float dia = adcToDiameter(avgRaw);
      if (dia >= MIN_VALID_DIA && dia <= MAX_VALID_DIA) {
        if (!filamentPresent) currentDiameter = dia;   // Don't average against stale data
        filamentPresent = true;
        lastValidMs = nowMs;
        currentDiameter = 0.7 * currentDiameter + 0.3 * dia;
      } else if (nowMs - lastValidMs >= EMPTY_TIMEOUT_MS) {
        // Hold the current speed; just stop regulating until a valid strand returns.
        filamentPresent = false;
      }
    }
  }

  // 4. Dead-time-aware diameter regulation
  if (pullerActive && autoMode && filamentPresent) {
    uint32_t stepsSince = readPullSteps() - correctionStartSteps;
    bool strandRefreshed = stepsSince >= (uint32_t)(SENSOR_DISTANCE_MM * PULL_STEPS_PER_MM);
    float diaError = currentDiameter - TARGET_DIA;

    if (strandRefreshed && nowMs - lastCorrectionMs >= MIN_CORRECTION_MS &&
        fabs(diaError) > DIA_TOLERANCE) {
      // Constant output Q: v ~ 1/d^2, so the speed that would give TARGET_DIA is
      // v * (d / target)^2. Apply only part of it, and limit the step size.
      float ratio  = sq(currentDiameter / TARGET_DIA);
      float factor = 1.0 + CONTROL_GAIN * (ratio - 1.0);
      factor = constrain(factor, 1.0 - MAX_CORRECTION, 1.0 + MAX_CORRECTION);
      pullSpeedMmS *= factor;
      applyPullSpeed();
      correctionStartSteps = readPullSteps();
      lastCorrectionMs = nowMs;
    }
  }

  // 5. Telemetry (every 1000 ms, kept under the 64-byte TX buffer so it never blocks)
  if (nowMs - lastTelemetryMs >= 1000) {
    lastTelemetryMs = nowMs;
    Serial.print(F("[DIA: "));
    if (filamentPresent) {
      Serial.print(currentDiameter, 3);
      Serial.print(F("mm] "));
    } else {
      Serial.print(F("EMPTY] "));
    }
    Serial.print(F("[RAW: "));
    Serial.print(lastRawAdc);
    Serial.print(F("] [PULL: "));
    if (pullerActive) Serial.print(pullSpeedMmS, 2);
    else              Serial.print(F("OFF "));
    Serial.print(autoMode ? F("A] [AUG: ") : F("M] [AUG: "));
    if (augerActive) Serial.print(augCurrentRpm, 1);
    else             Serial.print(F("OFF"));
    Serial.println(F("]"));
  }

  // 6. Serial commands
  pollSerialCommands();
}
