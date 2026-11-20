# Chapter 19 plan: Battery energy storage (budget 115 pp; core chapter)

Handoff: 8 bullets + 2 worked examples (size a preliminary battery and test its power/energy
limits; cell-to-container interface tree and a hypothetical cell defect traced from receiving
inspection to containment by system controls); blueprint A-E; audit row 19 (theory:
electrochemistry, storage, degradation, thermal propagation; applied: analyse a failure/propagation
case; design: cell-to-plant, detection, separation, emergency interfaces; calculation: power,
usable energy, SOC, sourced safety-design checks; manufacturing: trace cell, pack, BMS, container
production and QC; implementation: safety-bounded design basis, fire-interface evidence, dispatch
model).

Safeguards: no small-scale cell-fabrication recipes (process purpose and controls only); no
universal fire-system prescriptions (spacing, volumes, suppression come from the authority, the
hazard mitigation analysis and product test evidence); no live-work or energized procedures;
standards cited by verified title/edition only (STD-096..101); teaching values labelled.

Plant P S1 battery (data pack): 20 MW, 40 MWh nominal BOL, window 10-90 % (32 MWh usable),
round trip 86 % AC, fade 2 %/yr linear (teaching), charging from PV and wind only.
Teaching build-up (A-290): LFP prismatic cell 314 Ah, 3.2 V nominal, 2.5-3.6 V; module 1P52S;
rack 8 modules (416 cells, 1,331 V nominal, 1,498 V at 3.6 V); container 12 racks (5.02 MWh);
8 containers (40.1 MWh); 4 PCS of 5 MW (two containers each) - matches the ch 18 breakdown.

## Companion
- plantp/storage.py (new name, checked): OCV curves (LFP, NMC teaching), Thevenin cell
  (R0 + one RC), discharge at C-rates, I^2R efficiency, pack build-up, coulomb counting with
  bias and OCV reset, calendar fade (Arrhenius, sqrt t, SOC factor) and cycle fade (DoD power
  law, rainflow from plantp.wind), lumped container thermal model, self-discharge voltage drift
  (k-value), propagation chain (teaching abstraction), sizing with window/RT/fade/EOL,
  augmentation schedule, warranty check. Tests test_ch19_storage.py.
- companion/ch19: sources (cell, build-up, chemistries, prices from ch 15, costs), examples_a
  (cell, OCV, Thevenin, C-rates, efficiency, SOC estimation, degradation), examples_b
  (hierarchy, electrical protection, thermal/HVAC, formats/architectures), lab_b (sizing worked
  example + limits), examples_c (process, grading/binning, AQL, traceability, defect trace
  worked example, runaway chain, warranty/augmentation, recycling), lab_d (year of dispatch,
  rainflow, 20-year fade, warranty, edge cases, evidence map), examples_e (fire interfaces,
  propagation case timeline), integrated, worked.

## Sections (files)
A a-cell, a2-model, a3-soc, a4-degradation; B b-hierarchy, b2-electrical, b3-thermal,
b4-sizing (worked 1), b5-formats; C c-process, c2-quality, c3-defect (worked 2), c4-runaway,
c5-life; D d-lab, d2-map; E e-fire, e2-case; y, z.
Decision D-023 battery basis; assumptions A-290..; unknowns U-073..; documents
PLP-ELE-SPC-0004? (check), PLP-ELE-REP-0006, PLP-GEN-REG-0005.
