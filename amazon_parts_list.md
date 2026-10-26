# 🛒 Parts List: 3DTruder Extrusion Line
*Assumes your Ender 3 V2 and its 24 V 350 W power supply are already on hand. Assembly is in the [Master Manual](ender_3_3dtruder_master_manual.md).*

> **Key:**
> * ✅ = Owned
> * ☐ = Still to get

---

## 🔥 Melt Zone
| ☐ | Qty | Part | Spec / Notes | Link |
| :-: | :-: | :--- | :--- | :--- |
| ✅ | 1 | Super Volcano heater block | Brass block, M6×1.0 bore, 6 mm heater cartridge and thermistor cartridge holes. | [Search](https://www.amazon.com/s?k=super+volcano+heater+block+brass) |
| ✅ | 1 | Super Volcano brass nozzle | **1.4 mm**, M6 thread. Screws up into the block until it meets the coupler stub. | [Search](https://www.amazon.com/s?k=super+volcano+nozzle+1.4mm+brass) |
| ✅ | 1 | Super Volcano brass nozzle (spare, optional) | **2.0 mm**, in case 1.4 mm doesn't swell enough to reach 1.75 mm. | [Search](https://www.amazon.com/s?k=super+volcano+nozzle+2.0mm+brass) |
| ✅ | 1 | Super Volcano silicone sock | Shields the block from the 5010 blower drafts. | [Search](https://www.amazon.com/s?k=super+volcano+silicone+sock) |
| ✅ | 1 | Heater cartridge | 24 V, 80 W, 6 mm × 20 mm. | [Search](https://www.amazon.com/s?k=24v+80w+heater+cartridge+6mm) |
| ✅ | 1 | Thermistor cartridge | 100K NTC B3950, rated to 300 °C for PET. | [Search](https://www.amazon.com/s?k=100k+b3950+thermistor+cartridge+3d+printer) |
| ✅ | 1 | 25 A external MOSFET module | Opto-isolated control input, works with the mainboard's 24 V heater output. | [Search](https://www.amazon.com/s?k=3d+printer+mosfet+module+25a+24v) |
| ✅ | 1 | **Heated barrel coupler (metal 3D printed)** | **JLC3D SLM print, 316L stainless, ±0.3 mm on sizes / ±0.5 mm on holes, all threads printed. 40 mm long: a 21.7 × 24.7 mm heater block (its 21.7 mm faces are the wrench flats) under a Ø24.7 mm round for the clamp. M12×1.0 female top (14 mm deep), M6×1.0 male stub (15 mm, full thread), Ø1.4 mm bore through the stub and 2 mm into the body, Ø3 mm above, flats for a 22 mm wrench, cross holes for a 6 mm heater cartridge and 3 mm thermistor, M6 set screws.** Replaces any adapter or heatbreak. | [Shop order](CAD/shop_order.md) · [CAD](CAD/barrel_coupler.step) |
| ✅ | 1 | SK25 shaft support | 25 mm bore. Clamps the coupler's top section to the 2020 frame so melt pressure doesn't pull on the barrel thread. Goes onto the barrel before the coupler (manual 4.4). | [Search](https://www.amazon.com/s?k=sk25+shaft+support+25mm) |
| ✅ | 1 | Coupler heater cartridge | 24 V, 40 W, 6 × 20 mm. Second heat zone in the coupler, wired to the mainboard's bed terminals. | [Search](https://www.amazon.com/s?k=24v+40w+heater+cartridge+6x20mm) |
| ✅ | 1 | Coupler thermistor | 100K NTC B3950 cartridge, 3 × 15 mm, rated to 300 °C. Plugs into the mainboard's `TB` header. | [Search](https://www.amazon.com/s?k=100k+b3950+thermistor+cartridge+3x15mm) |
| ✅ | 1 | PTFE thread tape | For the barrel → coupler thread. | [Search](https://www.amazon.com/s?k=ptfe+thread+seal+tape) |
| ✅ | 2 | M6 stainless set screws | Hex socket: one **M6 × 6** (heater), one **M6 × 16** (thermistor). Lock the coupler's cartridges. | [Search](https://www.amazon.com/s?k=m6+stainless+set+screw+assortment) |
| ✅ | 1 | 24 V 4010 / 4020 axial fan (replacement) | Over the barrel at the hopper window, keeps the feed end cold. Zip-tied directly to barrel/hopper neck. Always on. | [Search](https://www.amazon.com/s?k=24v+4020+cooling+fan) |

---

## 🌀 Auger Feed
| ☐ | Qty | Part | Spec / Notes | Link |
| :-: | :-: | :--- | :--- | :--- |
| ✅ | 1 | Stainless barrel tube | **10 mm ID × 12 mm OD**, 150 mm. Hopper window cut. **M12×1.0 external thread, 12 mm long, on the other end: still to do, best by a machine shop (manual 4.3).** | [Search](https://www.amazon.com/s?k=stainless+steel+tube+10mm+id+12mm+od) |
| ✅ | 1 | Wood auger drill bit | **3/8" (~9.5 mm), 12"**, **hex shank 9.0 mm across flats**. Screw point cut off, tip ground to a cone. | [Search](https://www.amazon.com/s?k=3%2F8+auger+drill+bit+12+inch) |
| ✅ | 1 | NEMA 17 planetary gearmotor | **14:1**, 8 mm output shaft (needs ≥ 25 mm exposed for the bearing + coupling). | [Search](https://www.amazon.com/s?k=nema+17+planetary+gearbox+stepper+motor+14%3A1) |
| ✅ | 1 | Shaft coupling | **8 mm motor shaft → 9 mm hex auger shank**, fits both directly, no shim. | — |
| ✅ | 1 | 51100 thrust ball bearing | **10 × 24 × 9 mm.** Sits on the motor shaft between the mount plate and the coupling. | [Search](https://www.amazon.com/s?k=51100+thrust+ball+bearing+10mm) |
| ✅ | 1 | Motor mount plate & fasteners | NEMA 17 bracket, bolts to the 2020 frame. | [Search](https://www.amazon.com/s?k=nema+17+motor+mount+bracket) |
| ✅ | 1 | A4988 stepper driver | With heatsink. Full step, **current limited to ~0.7 A** (torque limit). | [Search](https://www.amazon.com/s?k=a4988+stepper+driver+heatsink) |

---

## ⚡ Wiring & Safety
| ☐ | Qty | Part | Spec / Notes | Link |
| :-: | :-: | :--- | :--- | :--- |
| ✅ | 1 | Silicone wire | 16 AWG, red and black. | [Search](https://www.amazon.com/s?k=16+awg+silicone+wire+red+black) |
| ✅ | 1 | Inline fuse holder + fuses | Blade fuse holder + 5 A fuses. | [Search](https://www.amazon.com/s?k=inline+blade+fuse+holder+5a+fuse) |
| ✅ | 1 | Terminals, heat-shrink, jumpers | Crimp terminals, ferrules, heat-shrink. | [Search](https://www.amazon.com/s?k=dupont+jumper+wires+heat+shrink+tubing+kit) |

---

## 📥 Feedstock & Hopper
| ☐ | Qty | Part | Spec / Notes | Link |
| :-: | :-: | :--- | :--- | :--- |
| ✅ | 1 | Sieve set | 1 mm, 3 mm, 5 mm, stainless. Keep 1–3 mm flakes. | [Search](https://www.amazon.com/s?k=stainless+steel+soil+sieve+set+mesh) |
| ✅ | 1 | Clear PET jug (hopper) | Half-gallon. Bottom cut off, inverted, cap slotted and saddled onto the barrel window. | — |

---

## 🎛️ Puller & Control
| ☐ | Qty | Part | Spec / Notes | Link |
| :-: | :-: | :--- | :--- | :--- |
| ✅ | 1 | Arduino Uno R3 | With USB cable. | [Search](https://www.amazon.com/s?k=arduino+uno+r3) |
| ✅ | 1 | Arduino CNC Shield V3 | **Capacitors must be 35 V or 50 V** for 24 V. | [Search](https://www.amazon.com/s?k=cnc+shield+v3+arduino+uno) |
| ✅ | 1 | A4988 stepper driver (puller) | With heatsink, 1/16 microstepping. | [Search](https://www.amazon.com/s?k=a4988+stepper+driver+heatsink) |
| ✅ | 1 | NEMA 17 planetary gearmotor | **5:1** (puller). | [Search](https://www.amazon.com/s?k=nema+17+planetary+gearbox+stepper+motor+5%3A1) |
| ✅ | 1 | Complete BMG clone extruder | Housing, idler arm, spring, dual drive gears. | [Search](https://www.amazon.com/s?k=bmg+extruder+clone+dual+drive+1.75mm) |
| ✅ | 1 | Filament width sensor | **Analog 0–5 V output** on A0 (not a digital runout switch). | [Search](https://www.amazon.com/s?k=filament+width+diameter+sensor+1.75mm) |
| ✅ | 1 | Buck converter | 24 V → 9 V for the Uno barrel jack. | [Search](https://www.amazon.com/s?k=24v+to+9v+buck+converter) |
| ✅ | 2 | 5010 blowers + shrouds | Strand cooling between nozzle and sensor. | [Search](https://www.amazon.com/s?k=5010+blower+fan+24v) |
| ☐ | 1 | Motorized spooler | Low-RPM gear motor with slip-clutch hub. A 24 V motor runs straight off the PSU; a 12 V one needs a second buck converter. | [Search](https://www.amazon.com/s?k=24v+dc+gear+motor+10rpm+high+torque) |

---

## 🔧 Tools
| ☐ | Qty | Part | Spec / Notes | Link |
| :-: | :-: | :--- | :--- | :--- |
| ✅ | 1 | M12×1.0 tap & die set | Die: only needed if you cut the barrel thread yourself. Tap: chases the coupler's printed M12 if it comes out tight. | [Search](https://www.amazon.com/s?k=m12x1+tap+and+die+set) |
| ✅ | 1 | M6×1.0 tap + 1.4 mm drill bit | Cleanup only: chase the coupler's printed M6 set-screw holes if tight, and run the drill through the Ø1.4 stub bore if it printed small or holds powder. | [Search](https://www.amazon.com/s?k=m6x1.0+hand+tap) |
| ✅ | 1 | Die handle (die stock) | **38 mm (1.5") round die**, to fit the M12 die. Skip it if a shop cuts the barrel thread. | [Search](https://www.amazon.com/s?k=38mm+die+handle+round+die+stock) |
| ✅ | 1 | Angle grinder / cutoff discs | Cutting the auger tip and barrel window. | [Search](https://www.amazon.com/s?k=rotary+tool+cutoff+wheels+metal) |
| ✅ | 1 | Needle files + 240-grit cloth | Deburring the window and auger tip. | — |
| ✅ | 1 | Digital caliper | 0.01 mm resolution. | [Search](https://www.amazon.com/s?k=digital+caliper+150mm) |
| ✅ | 1 | Multimeter | Vref and continuity checks. | [Search](https://www.amazon.com/s?k=digital+multimeter) |
| ✅ | 1 | Wrenches | 22 mm (coupler flats) + nozzle wrench + 3 mm hex key (M6 set screws). | [Search](https://www.amazon.com/s?k=mini+wrench+set+metric) |
| ✅ | 1 | Fume extractor | Carbon filter fan. | [Search](https://www.amazon.com/s?k=solder+fume+extractor+fan+carbon+filter) |
