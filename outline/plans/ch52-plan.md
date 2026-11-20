# Chapter 52 plan: maintenance, troubleshooting and RAM (budget 95 pp, plan for ~105)

Handoff: 9 bullets (preventive/predictive/corrective; hierarchy and condition/failure data into
CMMS/EAM work orders; subsystem maintenance PV to batteries with safe fault isolation, RCA,
downtime, spares, contractors, permits, recurrence; export substations, circuits, line structures
or cable routes, terminations, protection/telecom, corridors, owner vs utility assets; soiling
measurement and cleaning-system maintenance; quantitative RAM: rates and distributions, MTBF/MTTR
limits, inherent/achieved/operational availability, series/parallel RBDs, fault trees, common
cause, redundancy, maintainability, repair logistics, spares; methods and assumptions:
exponential vs Weibull, repairable vs non-repairable, exposure, planned/forced classes,
dependencies, uncertainty, data sufficiency, why independence/constant rates mislead;
requirements-to-lifecycle: allocation, critical equipment, FMEA/FMECA and fault-tree reviews,
design for access/diagnostics/repair, PM tasks, supplier claims, commissioning baselines, field
data to corrective action; Plant P reliability case across PV, turbines, converters,
transformers, BESS, auxiliaries, grid outages and shared systems - equipment reliability vs plant
availability vs energy-based performance; worked example: an output loss traced from SCADA alarm
through safe diagnostic evidence, root cause, corrective work and verification; RAM mastery
exercise: bounded RBD and failure-mode register, scenario availability/downtime and sensitivity
to repair time, spares, common cause and planned maintenance, data limits and verification).
Blueprint A-I (A strategy, B subsystem maintenance, C fault diagnosis and restoration, D
troubleshooting case, E RAM models and assumptions, F quantitative Plant P exercise, G
water-dependent maintenance, H collector/export asset maintenance, I CMMS/EAM workflow). Audit
row 52. Persian letters A-I = الف ب پ ت ث ج چ ح خ.

Running data: ch 51's first operating year (outages with waiting, inverter trips, spares count,
work orders, criticality ranking, thermography, filters, UPS life, battery trend, line faults),
ch 37 `operating_year()` and its reliability helpers (censored MTBF, chi-square interval, Weibull
MLE, Crow-AMSAA), ch 18/19 REL data and Poisson spares, ch 26 protection, ch 24 cables and line,
ch 25 transformers (DGA), ch 10/29 cleaning and water, ch 35 SCADA events, ch 41-48 factory
records and baselines, ch 50 commissioning baselines.

Overlap rule: ch 37 measured performance and fitted failure data, ch 18 introduced N-1 and spares,
ch 19 battery spares, ch 40 FMEA and reliability growth in the factory, ch 51 ran the plant and
found the gaps. Ch 52 builds the maintenance system and the RAM case: strategy by criticality,
task plans per subsystem, the CMMS data model and its checks, RBD/fault-tree/common-cause models,
availability types, Monte Carlo of the plant with repair logistics and spares, PM interval
optimisation (age replacement, P-F interval), and the troubleshooting case end to end.

Safeguards: no live-work or energised diagnostic procedures (evidence, isolation authority and
records only; tests by qualified persons under permits); no universal fire prescriptions;
defensive OT only; teaching values only; supplier claims treated as claims until verified.

## Sections (files)
- `_52-a-strategy.qmd` A; `_52-b-subsystems.qmd` B; `_52-c-diagnosis.qmd` C;
  `_52-d-case.qmd` D (worked example); `_52-e-ram.qmd` E; `_52-f-plantp.qmd` F (mastery
  exercise); `_52-g-water.qmd` G; `_52-h-export.qmd` H; `_52-i-cmms.qmd` I; y, z.

## Companion
Module `plantp/ram.py` (availability types, series/parallel/k-of-n, RBD evaluation, fault tree
with minimal cut sets, beta-factor common cause, Weibull reliability and hazard, age-replacement
cost rate, P-F inspection interval, Monte Carlo of repairable blocks with spares and logistics
delay); chapter scripts `companion/ch52/`; tests `test_ch52_ram.py`.

## Ledgers
D-056 maintenance and RAM basis; assumptions A-530 onwards; unknown U-133 (makers' maintenance
manuals, failure data and service-agreement terms; network owner's maintenance boundaries).
