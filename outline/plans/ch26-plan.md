# Chapter 26 plan: Protection, grounding and lightning (budget 110 pp; core chapter)

Handoff: 6 bullets + worked example (trace a hypothetical fault from network data through a
coordination report to acceptance testing; final design and settings need project studies and
approval); blueprint A-E; audit row 26 (theory: fault protection, grounding, lightning and circuit
protection; applied: trace a collector/export fault; design: line/cable/bus/transformer zones,
coordination and communications interfaces; calculation: conceptual fault, coordination and grounding
quantities; manufacturing: relay, instrument transformer, panel and breaker manufacture and tests;
implementation: approved-setting boundary, end-to-end test evidence, maintenance record).

Safeguards: no live-work or energised procedures; tests named by purpose and evidence only;
arc-flash boundaries and labels by qualified engineers with an accepted method; settings from the
approved network model and the operator's requirements; earthing and lightning values teaching
(soil survey U-098, flash density U-099); standards cited only with verified titles (STD-038,
STD-093, STD-124..127).

## Companion
- plantp/protection.py: fault_currents, CURVES, trip_time, grading_ok, ct_knee_ok, diff_trips,
  distance_zones, grid_resistance, gpr, collection_area, strikes_per_year, sequence, phasor,
  pickup_window, tms_for, hemisphere_v, foot_resistance, body_current, rolling_sphere_r,
  loop_voltage, at_equipment, fuse_needed, p_fail_to_clear. Tests test_ch26_protection.py (6).
- companion/ch26: sources (RELAYS feeder 480 A TMS 0.10, incomer 1,600 A 0.11, T1 HV 400 A 0.18;
  EARTH; NETWORK; feeder sections; GRID; LIGHTNING), examples_a/b/c/f/g/h/k, lab_d (trace = worked
  example, setting file with checksum, maintenance), lab_e (sequence of events, clocks), integrated
  (by hand, boundary, settings register, basis D-030), worked (P01-P44; solutions2 P45-P75).

## Expansion after the first draft (2026-11-16)

First render 69 of 110 pages; thirteen rounds of computed lessons brought it to 110 (38 section
files, 157 exercises, 21 figures): examples_m (differential spill and slope, REF, sympathetic
tripping, auto-reclose drift, synchrocheck), examples_n (Wenner, fall of potential and 61.8 %,
down-conductor heating, arc-flash boundary, bus blocking), examples_p (channel asymmetry, charging
current, VT supervision, hidden failures, dependability and security), examples_r (voltage and
frequency bands, thermal replica, high-impedance bus differential, cable damage curve), examples_s
(lightning risk structure, SPD leads, setting-file comparison, fault locator), examples_t
(acceptance band, CT polarity, wiring errors), examples_u (second-harmonic restraint from
waveforms, screens against the earthing choice), examples_w (PV string loop, BF timer, plant
fault contribution), examples_x (lightning current sharing, protection per energisation stage),
examples_y (three-step grading in the turbine, diesel-fed board), examples_z (fuse or breaker,
test-record completeness), examples_ab (four steps case by case), examples_ac (cold-load inrush
with the relay as an integrator).

Findings: incomers 1,600 A (ch 23/24 keep 1,250 A as provisional); PV string fuse rule aligned with
ch 24 (1.5 Isc); the unit-transformer stage has no window with 0.3 s margins on both sides - 0.25 s
margins with a 0.35 s definite-time stage (a coordination-report decision); PV unit transformers
need breakers too (inrush rules out fuses in the teaching range); the coil-2 link missing at FAT was
wrongly classed B (lab E shows the cost).
