# Chapter 43 plan: power-transformer theory, design and factory manufacture (budget 100 pp, plan for ~110)

Handoff: 10 bullets (first principles; requirements and architecture; preliminary design logic;
materials and subassemblies; factory route; process control and failure modes; testing and
evidence; plant integration; worked examples and code - turns ratio, flux, current, loss and
efficiency, a loss/temperature sensitivity calculator with tests, a fictional traveler and test
report with unresolved evidence; safety boundary). Blueprint A-D (checked by
tools/check_coverage.py). Audit row 43.

Running products: Plant P's main transformer as bought (ch 25, D-029: bid B, 63 MVA ONAN/ONAF
50/63, 132/33 kV YNd11, uk 12 %, OLTC +-10 % in 17 positions, guaranteed P0 42 kW and Pk 290 kW
at 75 C, transport within 72 t) and the PV unit transformer of ch 39 (U-A: 5.6 MVA 33/0.6 kV
Dyn11 ONAN 45 C, P0 4.1 kW, Pk 41 kW). The factories are fictional.

Overlap rule: ch 25 already has Faraday/turns, equivalent circuit from tests, regulation and
efficiency, loss capitalisation (A/B), hot spot and ageing, sharing, short-circuit current and
force ratio, sound sums, bund, design sequence, parts, factory gates, winding forces and eddy
loss (concept), conservator, dry type in the tower, tests and their purpose, transport, refloss,
dossier review, DGA, health index, spares, fire interfaces. Ch 43 reuses those numbers and goes
deeper and quantitative on DESIGN (core and winding sizing, leakage impedance from geometry,
loss build-up, cooling surface, dielectric stress, short-circuit stress and buckling, design
sensitivities and the cost optimum with the A/B factors) and on the FACTORY (core cutting and
stacking, winding tolerances and axial balance, drying as a moisture budget, oil processing,
tests read and corrected, traveler and test report). Every lesson cites its ch 25 counterpart.

Safeguards: high voltage, vacuum, pressure, hot oil, dielectric tests and heavy lifts for
understanding and quality oversight only - no shop procedures, no drying or oil-processing
schedules (temperature/time/vacuum recipes), no test procedures with voltages to apply; standards
only when registered (IEC 60076 parts registered in ch 25: STD-120..123 - check before citing);
loss tolerances and test limits as contract/teaching values unless the registered standard's text
is checked.

## Sections (files)
- `_43-a-theory.qmd` A. theory and requirement translation: flux density choice (no-load loss,
  sound, over-excitation at Vmax/f), volts per turn and turns of the main unit, magnetising
  current and inrush factor (link ch 25), leakage reactance from winding geometry (Rogowski),
  impedance vs short-circuit current and regulation trade, loss build-up (I2R, eddy, stray),
  efficiency map, harmonic eddy-loss factor from the converter spectrum (ch 27), dielectric
  stress in oil-pressboard gaps, temperature rise (oil and gradient), requirement-to-clause
  table (rating, vector, impedance, taps, cooling, losses, sound, transport, grid study).
- `_43-b-design.qmd` B. materials and preliminary design: electrical-steel grades and building
  factor, stepped core cross-section (fill factor by steps), core mass and no-load loss, window
  and winding arrangement, conductor (CTC, strand eddy vs thickness), current density vs load
  loss and copper mass, cost optimum with A and B (ch 25 factors), radiators/fans surface,
  tank and oil volume, OLTC step voltage and contact wear, bushings and creepage at altitude
  (link ch 25 altitude), sensitivity tornado, OEM design boundary.
- `_43-c-factory.qmd` C. factory route and test evidence: core cutting burr and loss increase,
  stacking and joint gaps, winding dimensions and axial ampere-turn balance (axial force),
  clamping pressure, moisture budget of paper and pressboard (water to remove), oil quality
  (water ppm vs breakdown concept), routine tests read and corrected (ratio tolerance, resistance
  to 75 C, no-load loss waveform correction, load loss and impedance at reference temperature),
  temperature-rise test (cooling-curve extrapolation), sound power from pressure, FRA baseline
  (correlation of traces), DGA before/after heat run, impulse records by comparison, preservation
  and transport (impact recorder, gas pressure - link ch 25 arrival).
- `_43-d-lab.qmd` D. specification and dossier lab: requirement -> purchase clause -> test trace
  matrix; fictional traveler with planted gaps; fictional routine-test report with corrections
  and tolerance decisions; loss/temperature sensitivity calculator (module + tests); unresolved
  OEM/utility decisions list.
- `_43-e-integration.qmd` plant integration (handoff bullet 8): foundation and bund (link ch 25),
  CT/differential interface (vector group compensation, ch 26), grounding, monitoring signals,
  cooling control, commissioning checks (non-live, purpose only).
- `_43-y-plantp.qmd`, `_43-z-assessment.qmd`.

## Companion
Module `plantp/xfmrdesign.py` (new name; `plantp/transformer.py` stays): core_area, turns,
leakage_pct (Rogowski), stacked_fill, core_mass, no_load_loss, eddy_factor, load_loss_build,
cooling_surface, oil_rise, gradient, field_in_gap, hoop_stress, axial_force, moisture_budget,
resistance_to_ref, waveform_correction, cooling_curve_extrapolate, sound_power, fra_correlation,
plus a `LossTempCalc` (the handoff's calculator). Tests `test_ch43_xfmrdesign.py` with hand values.
Chapter scripts `companion/ch43/`: sources (MAIN_B, PVU, materials, traveler, test report with
planted defects), examples_a/b/c/e, lab_d, integrated, worked. ~16 figures.

## Ledgers
D-047 transformer design review and factory acceptance basis; assumptions from A-458; unknown
U-124 (maker's design data and type-test evidence, short-circuit proof); documents (check the
register before numbering).
