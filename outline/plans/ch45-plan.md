# Chapter 45 plan: battery cells, packs, BMS and storage-container manufacturing (budget 95 pp, plan for ~105)

Handoff: 7 bullets (electrochemical foundations; cell architecture/materials; cell manufacturing map
without a fabrication recipe; pack and container design; manufacturing and quality; safety and
lifecycle; worked examples - usable energy, C-rate, round-trip efficiency, degradation scenarios, a
Python SOC simulator with invariant and boundary tests, outlier analysis of synthetic cell data).
Blueprint A-D (A cell and pack architecture; B production and quality; C safety and lifecycle
engineering; D evidence-chain exercise following a fictional cell defect from receiving to
lifecycle records). Audit row 45.

Running product: the S1 battery of ch 19 (LFP 314 Ah cells, 52 s modules, 8 modules a rack, 12 racks
a container, 8 containers, 4 PCS of 5 MW; 39,936 cells, 40.13 MWh), its cells from a fictional cell
maker and its containers from a fictional integrator.

Overlap rule: ch 19 already has electrochemistry, OCV, ECM, C-rate, efficiency, window, SOC/SOH,
fade, Faraday, CC-CV, heat, hierarchy, protection, BMS functions, HVAC, process sequence, hazards,
formation, grading, inspection, lots, trace, runaway, warranty, EOL, screening, DCIR, SOH, FAT.
Ch 45 reuses those numbers (plantp.storage) and goes to the factory and the evidence: electrode
balance (N/P) and loading as design-for-manufacture, coating weight and thickness control as SPC,
dry-room dew point and moisture budget as a control (no process values beyond teaching),
formation/aging data analysis (K-value self-discharge by OCV drop, outliers by robust z), cell
matching into modules (binning vs sorting), tab/busbar weld resistance as process evidence, module
and rack insulation and isolation, BMS configuration identity (limits table checked against the cell
data sheet, fingerprint), SOC estimator as software with invariants and boundary tests, container
FAT evidence, transport classification as an interface (UN 38.3 already registered), propagation
concept and containment as interfaces, reuse/recycling material accounting, and the evidence chain.

Safeguards: no cell-fabrication recipe (no slurry formulations, drying temperatures, formation
currents/voltages for practice, electrolyte handling steps); purpose, control and evidence only;
no fire prescriptions; no live work; synthetic data.

## Sections (files)
- `_45-a-architecture.qmd` A. cell and pack architecture: materials concept, formats, N/P balance,
  energy density from the build, module/rack/container interfaces, pack limits.
- `_45-b-production.qmd` B. production and quality: process map with controls and evidence, coating
  SPC, dry room, formation/aging data, grading and matching, welds, pack assembly, BMS configuration,
  thermal system, test evidence.
- `_45-c-safety.qmd` C. safety and lifecycle engineering: process hazards and containment concepts,
  propagation concept, detection interfaces, transport, installation, service isolation, warranty,
  replacement, reuse and recycling.
- `_45-d-lab.qmd` D. evidence chain: SOC simulator with invariants and boundary tests, outlier
  analysis of a synthetic formation lot, a fictional cell defect followed through receiving,
  assembly, BMS limits, acceptance, incident and records.
- `_45-y-plantp.qmd`, `_45-z-assessment.qmd`.

## Companion
Module `plantp/cellmfg.py`; chapter scripts `companion/ch45/`; tests `test_ch45_cellmfg.py`.

## Ledgers
D-049 battery manufacturing and evidence basis; assumptions from A-474; unknown U-126 (cell maker's
qualification and lot data, integrator's BMS configuration records); documents (check the register).
