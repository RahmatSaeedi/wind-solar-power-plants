# Chapter 10 plan: Solar PV modules and array design (budget 120 pp minimum)

Handoff: chapter 10 bullets (10), blueprint A-E, audit row 10, worked examples (string limits at
temperature extremes; module BOM -> failure modes and incoming-inspection evidence; cell-process
flow at a non-proprietary educational level). Safeguard: process flow conceptual only (no recipes,
no concentrations or furnace settings).

## Promises from chapters 1-9 to honour
- POA (plane-of-array) transposition with the data pack's DNI/DHI; DC/AC ratio and clipping
  "precisely" (ch 1); optimum tilt with diffuse/albedo (ch 3); row spacing and inter-row shading,
  U-016 (ch 3); combiner/inverter integer layout (ch 3: 175 not divisible by 12; ch 6 A-014 = 24
  strings per combiner, A-015 = 26 modules per string, D-002).
- Physical single-diode model with Rs, Rsh fitted to the PVM-550 data sheet (ch 3, ch 6: simple
  model gave 13.56 vs 14.30 kW); semiconductor model of the cell (ch 6 a3); dP/dT < 0 (ch 3).
- Module temperature models with wind and mounting (ch 4, ch 6 NOCT).
- Mismatch of parallel strings (ch 6); bypass diodes and hot spots (ch 6, ch 9 shading lab).
- Qualification tests: "passing is not a guaranteed life" (ch 4); thermal cycling (ch 4).
- Flash-test / STC-conversion uncertainty (ch 2).
- Cable derating in sun (ch 4).
- Functional earthing / PID decision with modules (ch 9, A-172).
- U-032 (ch 9): rerun the DC window (D-012) and annual energy with POA irradiance and a better cell
  temperature model.

## Structure (section labels)
A sec-ch10-a: a-why, a-light (photons, bandgap, limit), a-junction (pn, diode, equivalent circuit),
  a-iv (Isc, Voc, FF, eta), a-sdm (5-parameter fit, Lambert W), a-temperature, a-technologies
  (PERC, TOPCon, HJT, IBC, bifacial, thin film, tandem), a-datasheet (STC, NMOT, tolerance, binning,
  coefficients, max voltage, fuse rating, bifaciality), a-celltemp (NOCT, Faiman with wind),
  a-bifacial, a-spectrum/angle (IAM) optional.
B sec-ch10-b: b-chain (polysilicon -> ingot -> wafer -> cell -> test/sort, conceptual), b-arch
  (cell architectures compared at process-step level), b-module (BOM table), b-line (module factory
  stages and quality gates), b-defects (cracks, delamination, corrosion, hot spots, moisture, PID,
  LID/LeTID), b-bommap (worked example 2), b-hotspot (reverse bias of a shaded cell, bypass),
  b-qualification (IEC 61215 / 61730 family, what certificates do and do not establish), b-roles
  (cell factory vs module assembly vs site installation), b-degradation (rates, warranty).
C sec-ch10-c: c-strings (cold Voc vs 1500 V, hot Vmp vs 933 V window, currents), c-layout (strings
  per combiner, combiners per inverter, integer layout), c-poa (transposition, tilt sweep), c-rows
  (row spacing, GCR, shading), c-mismatch (Monte Carlo of tolerance), c-shading (bypass,
  portrait/landscape), c-soiling, c-snow, c-cabling (DC losses, sun derating), c-isolation
  (combiners, fuses, SPD, earthing/PID), c-dcac (DC/AC ratio and clipping with POA), c-inverter
  (window revisited, U-032), c-cleaninterface.
D sec-ch10-d: d-soiling (physics, soiling ratio station), d-methods (none, dry, robotic, wet;
  water quality, abrasion, safety, runoff), d-optimize (T* = sqrt(2C/(p E r))), d-decision
  (matrix, D-014).
E sec-ch10-e: e-flash (sample flash data, tolerance, uncertainty, conformity), e-soildata
  (soiling-station data -> rate), e-stringscript (string sizing with boundary tests), e-inspection
  (module + cleaning-system inspection plan), e-certs (certificates vs project acceptance),
  e-limits.
Y: sec-ch10-plantp (int-1 module at one hour SDM vs data sheet; int-2 array design; int-3 cleaning
  and acceptance basis), sec-ch10-design, sec-ch10-lab, sec-ch10-mfg, sec-ch10-std,
  sec-ch10-deliverable. Z: summary, vocab, assess (~130 problems), solutions, examples-out.

## Numbering
Assumptions from A-183; unknowns from U-033; decisions D-013 (array layout), D-014 (cleaning).
Documents: PLP-PV-... or PLP-ELE-...; check tbl-ch02-register for discipline codes.
Companion: companion/ch10/, module plantp/pvcell.py (SDM, Lambert W), plantp/solar.py (exists:
check for POA functions), tests test_ch10_pv.py.
