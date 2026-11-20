# Chapter 41 plan: PV cells and module manufacturing engineering (budget 95 pp, plan for ~105)

Handoff: 9 bullets (semiconductor and materials foundation; upstream materials and cell-process
map at textbook level, no recipes; module product architecture with compatibility and repair
limits; module-line design; design for manufacture; quality and reliability defects, sampling,
traceability, failure analysis; testing and qualification - purposes, qualification vs every-unit
inspection; plant integration - connectors, strings, mounting, grounding, mismatch, monitoring,
acceptance sampling; worked examples: cell mismatch in a string, parse module test data and flag
outliers, module BOM + process flow + control plan + incoming-inspection checklist). Blueprint A-D
(checked by tools/check_coverage.py). Audit row 41.

Running product: Plant P's fictional module PVM-550 (data pack 1.1.0: 144 half-cut mono cells,
550 W, Voc 49.9 V, Isc 13.98 A, tolerance 0/+5 W); about 109,000 modules for 60 MWp. The factory
and its lots are fictional; ch 40's system (route, ITP, FMEA, control plan, sampling, genealogy)
is applied, not re-taught; ch 10's single-diode model (`plantp.pvcell`) and ch 15's mismatch and
bypass functions (`plantp.mppt`) are reused.

Safeguards: no cell-fabrication recipes - each process step by purpose, control variable and the
defect it can cause, never by settings; no proprietary data; qualification standards named only
when registered (check IEC 61215 / IEC 61730 / IEC 62941 = STD-074 in the register before citing);
teaching values labelled.

## Sections (files)
- `_41-a-device.qmd` A. Device principles: band gap and absorption, doping and the junction,
  carriers and recombination (lifetime, diffusion length), contacts and series resistance,
  optical and electrical losses budget, cell architectures (concept), process variation -> Voc,
  FF, Isc spread (computed with the single-diode model).
- `_41-b-route.qmd` B. Material-to-cell route: feedstock purity and wafer routes (concepts),
  wafer inspection, texturing, junction, passivation, coatings, metallisation, firing, edge
  isolation, sorting/binning and metrology - purpose, control variable, defect; cell binning by
  current and its effect on module mismatch; traceability of cell lots.
- `_41-c-module.qmd` C. Module assembly and reliability: BOM of PVM-550; stringing, lay-up,
  lamination (gel content concept), trimming, framing, junction box, curing, labelling; line
  layout and takt; DfM (current paths, half-cut, thermal, mechanical, sealing, insulation);
  defects (cracks, solder, voids, delamination, moisture, corrosion, hot spots, diodes,
  insulation) with detection; tests (EL, flash, insulation, wet leakage concept) and
  qualification vs production; transport damage; failure analysis.
- `_41-d-lab.qmd` D. Production/data lab: flash-test data of a lot parsed and outliers flagged
  (robust z, Pmax binning, EL grade); cell mismatch in a string by simulation; module BOM,
  process flow, control plan, incoming-inspection checklist and acceptance sampling for Plant P.
- `_41-e-plant.qmd` plant integration: connector compatibility (mixed connectors), string
  sizing check with tolerance, mounting/clamping zones, grounding/bonding, cable routing,
  mismatch from binning and soiling, monitoring, acceptance sampling at site (EL of a sample).
- `_41-y-plantp.qmd`, `_41-z-assessment.qmd`.

## Companion
- `plantp/pvfab.py` (new): absorption depth, diffusion length, Voc from J0 and Jsc, loss budget,
  binning, mismatch loss of a string from a current distribution, robust outlier flags (median/
  MAD), lamination void and gel-content checks as data rules, sampling reuse from `quality`.
- `companion/ch41/`: sources (cell lots, flash data of a 3,000-module lot with planted
  outliers, EL grades, BOM, line route), examples_a/b/c, lab_d, examples_e, integrated (D-045),
  worked.

## Ledgers
D-045 module manufacturing and acceptance basis; A-442..A-449; U-122 (the chosen maker's
actual qualification evidence for the exact BOM); standards to verify first.
