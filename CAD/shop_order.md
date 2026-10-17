# Work Order: Heated Barrel Coupler

| | |
|---|---|
| **Customer** | Adam Humphries |
| **Part** | Heated barrel coupler, qty 1 |
| **Reference CAD** | `barrel_coupler.step` (all threads modelled). `barrel_coupler_nothreads.step` has plain Ø6 stub, Ø11 and Ø2.5 holes for threading after the print |
| **Drawing** | `barrel_coupler_drawing.pdf` (BC-001 Rev A). Where the drawing and this order differ, this order governs |
| **Material** | 316L stainless steel, metal 3D printed (SLM). Aluminum not acceptable (service temperature 280 °C) |
| **Units** | mm |
| **General tolerance** | ±0.1 unless noted. Break sharp edges 0.3–0.5 |
| **Customer-supplied** | M12×1.0 tap (if needed) |

---

| Feature | Specification |
|---|---|
| Body | Ø25 × 40, excluding stub |
| Top bore | M12×1.0-6H, 14 full thread from the top face; hole Ø11.0 × 18 deep with a 90° cone floor; 0.5 × 45° chamfer |
| Stub | M6×1.0-6g × 15, threaded full length; relief Ø4.8 × 1.5 at shoulder |
| Stub end face | Flat, perpendicular to axis within 0.02 (sealing face) |
| Through bore | Ø3.0 +0.1/0 in the body (z > 0); Ø2.0 +0.1/0 through the stub (z -15 to 0); deburred both ends |
| Wrench flats | 22 A/F, 20–26 from shoulder |
| Heater hole | Ø6.0 +0.05/+0.02, through; perpendicular to axis, 6.5 off-center, 7 from shoulder; 45° teardrop roof per CAD |
| Thermistor hole | Ø3.0 +0.05/0 × 16 deep; parallel to heater hole, 6.5 off-center opposite side, 15 from shoulder; 45° teardrop roof per CAD |
| Set screws | M3×0.5 from shoulder face into heater and thermistor holes, per CAD. Print as Ø2.5 and tap after printing |
| Concentricity | M12 bore to M6 stub, 0.05 TIR |

**Notes**
1. Print orientation: axis vertical, top (M12) face on the plate, stub up.
2. As-printed SLM will not hold the stub end face (0.02) or the 0.05 TIR. After stress relief and support removal, face the stub end square to the axis and chase the M6 (die) and M12 (tap) threads.
3. Ream the heater hole to Ø6.0 +0.05/+0.02 if the print comes out undersize.
4. Through bore must not break into either cross hole (2.0 min wall to heater hole).
5. Leave Ø25 round above the flats for an SK25 shaft clamp.

**Inspection**
- [ ] M6×1.0 nut runs full length of stub
- [ ] M12×1.0 tap or plug gauge runs 14 deep
- [ ] 6 mm heater cartridge slides into its hole
- [ ] Clear sight line through the bore
