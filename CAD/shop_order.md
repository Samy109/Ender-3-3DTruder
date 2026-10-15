# Shop Order: 3DTruder Extruder Parts

**Bringing:** stainless barrel tube (10 mm ID × 12 mm OD), M12×1.0 tap and die, auger bit (hex shank), 8 mm → 11 mm clamp-on shaft coupling.
**CAD (reference):** `barrel_coupler.step`  ·  Assembly is covered in the Master Manual, section 4.

How it all goes together:

```
motor → plate → thrust bearing → shaft coupling → auger
                                                    │ (runs inside the tube)
barrel tube ══ M12x1.0 ══► [ JOB 1 HEATED COUPLER ] ══ M6x1.0 ══► Super Volcano block ◄══ nozzle
```

---

## Job 1: Heated barrel coupler (main part)

```
        M12x1.0 FEMALE   ← barrel tube screws in here
      ┌───────────────┐
      │  14 mm deep   │   Ø25 round (SK25 clamp goes here)
      │               │
      ├┬─────────────┬┤   22 mm wrench flats, 6 mm tall
      ││  Ø3 bore    ││
      │  ○ Ø6 heater  │   heater zone, 20 mm tall:
      │               │     Ø6 cross hole (24 V cartridge)
      │  ○ Ø3 therm   │     Ø3 blind cross hole (thermistor)
      └──┐   ║   ┌──┘   ← shoulder
         │ M6x1 │
         │ MALE │       15 mm long, threaded full length
         └──────┘   ← flat, square end face (this is the seal)
```

| Feature | Spec |
|---|---|
| Material | **Brass** (C360 or similar). Stainless OK. **No aluminum** (runs at ~250 °C) |
| Body | Ø25 mm round, 40 mm long (not counting the stub) |
| Top | **M12×1.0 female**, 14 mm full-thread depth, light chamfer |
| Wrench flats | **22 mm across**, 6 mm tall, just below the M12 hole (body 20–26 mm up from the shoulder) |
| Heater hole | **Ø6.0 mm cross hole, through**, 6.5 mm off the centerline, 7 mm up from the shoulder. Fits a 24 V 40 W 6 × 20 mm cartridge. Ream or drill for a snug slide fit |
| Thermistor hole | **Ø3.0 mm blind cross hole, 16 mm deep**, 6.5 mm off-center on the **opposite** side, 15 mm up from the shoulder. Fits a 3 × 15 mm thermistor cartridge |
| Set screws | **M3 tapped hole** from the shoulder face up into each of the two cross holes, to lock the heater and thermistor |
| Bottom | **M6×1.0 male stub, 15 mm long, threaded the full length**, small thread relief at the shoulder |
| Stub end face | **Flat and square.** It seals against the top of the nozzle inside the heater block |
| Bore | **Ø3 mm** straight through, deburred. Must not break into either cross hole (2 mm wall to the heater hole) |
| Concentricity | Important: the tube threads into one end, the heater block onto the other |

## Job 2: Thread the barrel tube

| Feature | Spec |
|---|---|
| Thread | **M12×1.0 external**, 12 mm long (shorter than the coupler's 14 mm hole so no thinned thread is left exposed) |
| End | The end **without** the hopper window |
| Method | Lathe single-point preferred. **Wall is only 1 mm**, so support the inside with a 10 mm mandrel |
| Finish | Chamfer the tube end, deburr inside |

## Job 3 (optional): Sleeve for the auger shaft coupling

The auger shank is **hex, 9.0 mm across flats (~10.4 mm across corners)**. The motor coupling is an **8 mm → 11 mm clamp-on** (Ø32 × 45 mm aluminum), so there's ~0.3 mm per side of slop.

| Feature | Spec |
|---|---|
| Part | Sleeve, **11.0 mm OD**, bored to fit the hex across corners (~10.45 mm, measure it), ~20 mm long |
| Slit | One lengthwise slit so the clamp squeezes it onto the hex |
| Material | Brass or aluminum |
| Why | The auger has only ~0.25 mm per side of clearance in the barrel, so it must run dead-center |

*(Skip this if short on time: three wraps of soda-can aluminum around the hex does the same job.)*

---

## Fit check before leaving
- [ ] Tube threads fully into the coupler by hand
- [ ] An M6×1.0 nut spins freely along the whole stub
- [ ] Clear Ø3 path all the way through (look through it)
- [ ] A 6 mm drill shank slides through the heater hole; a 3 mm one into the thermistor hole
- [ ] Auger clamped in the shaft coupling spins true (no visible wobble at the tip)
