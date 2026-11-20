# Chapter 46 plan: cable, connector, switchgear and protection-panel manufacture (budget 85 pp, plan for ~95)

Handoff: 8 bullets (cable theory/design; cable process; connectors and terminations; switchgear
architecture; protection/control-panel manufacture; quality and acceptance - type vs routine vs site
and why neither substitutes; plant integration; worked examples - cable loss/voltage drop, a script
that checks a cable schedule for missing fields and unit inconsistencies, map a one-line circuit to
compartments, terminal drawings and tests). Blueprint A-D (A cable/connector product design; B
switchgear product architecture; C panel manufacture and acceptance; D plant traceability lab:
validate cable schedules, map one-line to compartments/terminals, inspection/test matrix with
qualified-person boundaries). Audit row 46.

Running products: the 33 kV collector cables of ch 24 (240/400/630 mm2 Al XLPE), the 33 kV
switchgear of ch 23-26 (incomers 1,600 A, feeders WS1-3, PVF1-3, BESS-A/B), the protection and
control panels of ch 26/34, and the LV/DC cables of the PV blocks; a fictional cable maker, a
fictional switchgear maker and a fictional panel builder.

Overlap rule: ch 24 has cable sizing, construction layers, factory process control and tests,
drums, eccentricity and Cpk, joints, switchgear parts, duties, interlocks, mechanism, SF6, fuses;
ch 26 has protection, settings register with checksum, CT/VT, testing; ch 40 crimp Cpk. Ch 46 goes to
the factory and the records: conductor resistance by length and temperature, insulation minimum
point and sampling by drum, routine test reports read (PD, conductor, sheath), crimp qualification
and pull tests, contact resistance and mechanism timing spread, interlock truth table checked by
code, panel wiring list point-to-point check, terminal-plan consistency, relay configuration
fingerprints, FAT/SAT matrix (type/routine/site), cable-schedule validator, one-line to compartment
and terminal mapping.

Safeguards: no test voltages or test procedures to apply, no live work, no extrusion or curing
values; qualified-person boundaries named.

## Sections (files)
- `_46-a-cable.qmd` A. cable and connector product design and process.
- `_46-b-switchgear.qmd` B. switchgear product architecture.
- `_46-c-panels.qmd` C. panel manufacture and acceptance.
- `_46-d-lab.qmd` D. plant traceability lab.
- `_46-y-plantp.qmd`, `_46-z-assessment.qmd`.

## Companion
Module `plantp/cablemfg.py`; chapter scripts `companion/ch46/`; tests `test_ch46_cablemfg.py`.

## Ledgers
D-050 cable, switchgear and panel manufacturing and acceptance basis; assumptions from A-482;
unknown U-127 (makers' type-test reports for the exact designs, panel builder's records).
