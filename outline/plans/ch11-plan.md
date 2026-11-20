# Chapter 11 plan: Wind turbines and wind-energy conversion (budget 115 pp minimum)

Handoff: chapter 11 bullets (8), blueprint A-D, audit row 11, worked examples (wind distribution and
power curve to gross energy; turbine subassembly/interface tree and a quality plan for a blade or
tower section). Mastery gate of Part II at the end of this chapter (trace each source's conversion,
explain interfaces, gross vs delivered output) -> Appendix X Part II test after the chapter.
Safeguards: no lifting, climbing or live-work procedures; manufacturing at process-flow level;
design classes and load cases described without quoting clause values (fictional teaching values).

## Built on (do not repeat, reference)
- ch 4: Betz (sec-ch04-a-betz), shear, tower natural frequency and soft-stiff window, blade root
  centrifugal/gravity loads, lift and drag (sec-ch04-a-aerofoil), fatigue basics (sec-ch04-b-fatigue),
  tower stress, air density at Plant P.
- ch 5: power-curve integration, series vs Weibull, density correction D-008 (mean 1.056 kg/m3),
  192.54 / 177.08 GWh.
- ch 8: DFIG, PMSG, D-011 geared drivetrain + full converter baseline, bearings life.
- ch 9: machine-side converter, brake chopper.
- U-013 (vendor curve for site density) stays open; ch 11 gives physical evidence for the method.

## Companion
- plantp/wind.py: polar, design_blade (Schmitz), bem (Prandtl tip/hub, Buhl), Turbine/operate
  (regions 2, 2.5, 3 with feathering branch), smooth_power_curve, density_equivalent_speed,
  jensen_deficit, farm_speeds, rainflow, miner_damage, damage_equivalent_load, tower_frequency,
  tube_inertia. Tests: test_ch11_wind.py.
- companion/ch11: examples_a (power, Betz recap, polar, BEM, Cp-lambda, regions, control law,
  density, yaw), examples_b (tree, drivetrain torque, loads, rainflow/DEL, Campbell, tower f),
  examples_c (blade mass/balance, tower sections, coating, lightning, icing, transport), lab_d
  (energy: Weibull vs series, density, wakes, condition spectrum), integrated, worked, solutions.

## Structure (labels)
A sec-ch11-a: a-why, a-power, a-momentum, a-aerofoil, a-bem, a-cplambda, a-regions, a-control,
  a-pitch, a-yaw, a-braking, a-thrust, a-density, a-curve (power curve as statistics).
B sec-ch11-b: b-tree, b-rotor, b-pitch, b-drivetrain, b-generator, b-yawbrake, b-nacelle,
  b-towerfound, b-sensors, b-controller, b-interfaces, b-loads, b-classes, b-fatigue, b-campbell,
  b-lubcool, b-cms.
C sec-ch11-c: c-blades, c-composites, c-castforge, c-gears, c-bearings, c-tower, c-nacelle,
  c-balancing, c-lightning, c-corrosion, c-icing, c-ndt, c-records, c-certification, c-transport,
  c-installation, c-service, c-qualityplan.
D sec-ch11-d: d-energy, d-density, d-wakes, d-condition, d-qualitymap, d-limits.
Y: sec-ch11-plantp (int-1 one turbine one hour; int-2 farm energy with density and wakes; int-3
  tree + tower-section quality plan), design, lab, mfg, std, deliverable.
Z: summary, vocab, assess (~130), solutions, examples-out.

## Numbering
Assumptions from A-211; unknowns from U-039; decision D-015 (wind energy basis: density-equivalent
power curve + wake model for estimates until vendor curve; layout spacing teaching basis).
Documents PLP-MEC-... (turbine tree, quality plan) and PLP-ELE/GEN for energy.
