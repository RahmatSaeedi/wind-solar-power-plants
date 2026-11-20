# Chapter 40 plan: Manufacturing systems, quality engineering and factory tests (budget 85 pp, plan for ~95)

Handoff: 10 bullets (production engineering: process maps, BOM, work instructions, tooling,
capability, qualifications, calibration, traceability, change control, yield/scrap, continuous
improvement; quality planning: QMP, ITP, hold/witness/review points, incoming/in-process/final
inspection, acceptance sampling, nonconformity, root cause, corrective action, concession,
records; production-system design (PBS, routing, takt/throughput, competency) - overlaps bullet 1,
covered once; quality engineering (design/process FMEA, MSA) - overlaps bullet 2, covered once;
FMEA and control plans tied to reliability (criticality, mechanisms, prevention/detection,
reliability growth, supplier corrective action, serial/lot genealogy, factory defect -> field
failure and repair); prototype, pilot, serial, contract manufacturing, certified supplier
production, site assembly, field repair, make/buy, proprietary process knowledge; product
life-cycle documentation (baseline, approved materials, traveler, genealogy, inspection records,
test dossier, deviations, packaging, transport, preservation, receipt inspection, warranty
traceability); design verification vs type qualification vs routine tests vs FAT vs SAT vs
integrated plant tests; factory EHS (energy isolation, lifting, hot work, chemicals,
pressure/vacuum, thermal processes, ergonomics, emissions, waste, emergency planning); worked
examples: manufacturing route and ITP, audit of a fictional test dossier, defect traced from
cause to plant consequence). Blueprint A-E (checked by tools/check_coverage.py). Audit row 40.
Thread: quantitative reliability (ch 37 failure data, ch 39 supplier requirements, ch 40 growth,
ch 52 RAM, ch 53, ch 59).

Running product (fictional): the **PV station skid** of Plant P - one per PV block, ten in all
(ch 23 tags =PVF2-n): steel base frame, the 5.6 MVA unit transformer bought in ch 39 (U-A), a
central inverter, an RMU, LV busbar and cables, auxiliary/control panel, earthing. Built by a
fictional skid integrator; components from tier-1 suppliers. Chapters 41-48 go inside each
product's own factory; ch 40 teaches the system that every one of those factories uses.

Overlaps, reused not repeated: ch 4 (materials, tolerances, measurement), ch 5 (testing, records),
ch 32 (risk matrix, lifting index, permits), ch 37 (Weibull, CUSUM, failure data, warranty), ch 38
(document status, RVTM, ICD, release for manufacture), ch 39 (capability audit, witness points,
concessions, supplier data schedule, transformer offers). Chapter 40 adds: route and takt, line
balance, yield and RTY, capability Cp/Cpk and ppm, Shewhart charts, gauge R&R by ANOVA, OC curves
for sampling plans, FMEA ranking and control plan, genealogy queries, test-dossier audit,
reliability growth (Crow-AMSAA), burn-in trade-off, defect escape chain and plant consequence,
factory EHS numbers (sling angle, solvent mass balance).

Safeguards: fictional factory and suppliers; no proprietary recipes; HV/FAT tests by purpose,
roles and acceptance only (no energised procedure); lifting and hot work as planning concepts with
competent-person boundary; no standard table copied; teaching values labelled.

## Sections (files)
- `_40-a-production.qmd` A. Production system: PBS and BOM explosion for ten skids, routing and
  process map (OP10-OP90), work instructions and tooling, takt and line balance, yield/RTY and
  scrap cost, competency coverage, calibration and TUR, traceability levels.
- `_40-a2-stages.qmd` prototype -> pilot -> serial; contract manufacturing, certified supplier
  production, site assembly, field repair; make/buy and proprietary process knowledge; change
  control (first-article inspection after a change).
- `_40-b-quality.qmd` B. Quality planning: QMP, DFMEA/PFMEA ranking, control plan, ITP with
  H/W/R points, MSA (gauge R&R), capability, SPC, sampling OC curves, acceptance criteria.
- `_40-c-evidence.qmd` C. Nonconformity and evidence: containment by genealogy, root cause
  (5 whys + cause categories as data), corrective action effectiveness, concession, test
  dossier, packaging/preservation/transport, receipt inspection, supplier change control,
  warranty traceability.
- `_40-c2-tests.qmd` the test ladder: design verification, type qualification, routine, FAT, SAT,
  integrated plant tests - what each proves and what it cannot.
- `_40-d-lab.qmd` D. Factory-quality lab: traveler + ITP for the skid; audit of a fictional test
  dossier (planted defects); the torque defect traced from cause to plant consequence and closure.
- `_40-e-reliability.qmd` E. Reliability in production: FMEA -> critical characteristics ->
  controls; reliability growth on the pilot run (Crow-AMSAA); infant mortality and burn-in
  trade-off (Weibull beta < 1, ch 37); field returns and escapes; supplier corrective action.
- `_40-f-ehs.qmd` factory EHS: energy isolation in the test bay (roles), lifting (sling angle),
  hot work, chemicals and solvent mass balance, pressure/vacuum and thermal processes, ergonomics,
  waste streams, emergency planning.
- `_40-y-plantp.qmd`, `_40-z-assessment.qmd` (generated).

## Companion
- `plantp/quality.py` (new): cp_cpk, ppm_out, xbar_r_limits, rty, takt/line balance, oc_accept,
  find_plan, grr_anova, rpn and ranking, crow_amsaa, escape chain, tur, sling tension.
- `companion/ch40/`: sources (skid BOM, route, cycle times, measurements, FMEA, dossier, pilot
  failures, genealogy), examples_a, examples_b, examples_c, lab_d, examples_e, examples_f,
  integrated (D-044), worked.

## Ledgers
D-044 manufacturing quality basis of the PV station skids; A-434..A-441; U-121 (integrator's
actual process capability data, before award); standards STD-167..STD-172 (ISO 9001:2026,
IEC 60812:2018, IEC 61014:2003, IEC 61164:2004, ISO 10012:2026, ISO 7870-2:2023), with STD-011,
STD-076, STD-137, STD-144, STD-166 reused.
