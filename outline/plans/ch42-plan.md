# Chapter 42 plan: wind-turbine component design and manufacturing (budget 100 pp, plan for ~110)

Handoff: 8 bullets (architecture and load paths; blade design and production; hub, pitch and
bearings; drivetrain and generator; nacelle and yaw/brake; tower and foundation interfaces;
manufacturing engineering; worked examples: simplified blade loading and drivetrain loss,
subassembly/interface tree, vibration data, tower-section traveler and blade inspection/quality
plan). Blueprint A-D (checked by tools/check_coverage.py). Audit row 42.

Running product: Plant P's fictional WT-5.0-150 (A-211: rotor 150 m, hub 100 m, 5 MW, geared
D-011, 11.5 rpm rated, 4.42 MN m main-shaft torque), its fictional blade (22 t, plantp.wind
`design_blade`), the tower of ch 30 and the logistics of ch 31. The factories are fictional.

Overlap rule: ch 11 has aerodynamics, BEM, loads, gearbox frequencies, envelope analysis, balance,
bearing life, tower frequency; ch 30 has the tower structure, welds, coating, bolting and the
tower-section traveler (lab E); ch 31 has transport. Ch 42 reuses those numbers and goes to the
factory: process qualification, control plans, inspection and test evidence, nonconformity
disposition and repair limits. Every lesson cites its ch 11/30/31 counterpart.

Safeguards: no process recipes (cure schedules, weld parameters, heat treatment cycles) - purpose,
control variable and defect only; cure on a normalised axis; no proprietary designs; no live work
or rotating-equipment procedures; certification evidence named by type only, standards cited only
when registered (check IEC 61400-1, -5, -22/IECRE, ISO 1940/21940, ISO 10816/20816 before citing).

## Sections (files)
- `_42-a-requirements.qmd` A. requirements and load paths: subassembly/interface tree with
  load path, operating envelope, simplified blade loading (root moment from thrust, gravity
  bending, edgewise), drivetrain loss chain, reliability allocation, service strategy, evidence.
- `_42-b-blade.qmd` B. blade/hub/pitch: rule of mixtures, fibre volume fraction and void content,
  laminate stiffness, spar-cap strain, normalised cure window, bond-line thickness, root insert
  pull-out, lightning receptor resistance, balancing (mass moments), NDT detection, casting
  porosity and UT, bearing fits (interference, shrink temperature as a concept), bolt preload.
- `_42-c-drivetrain.qmd` C. drivetrain/nacelle/tower: gear accuracy and transmission error,
  lubrication and oil cleanliness, cooling, generator insulation thermal life (10 K rule),
  winding hipot as purpose only, rotor balance grades as concept, alignment, frame weld fatigue,
  yaw brake torque, tower interface (reference ch 30), traceability tree.
- `_42-d-lab.qmd` D. lab: synthetic vibration of a factory run-in (order spectra, sidebands,
  severity trend), blade inspection/quality plan, NCR escalation and disposition, transport and
  installation interface map.
- `_42-y-plantp.qmd`, `_42-z-assessment.qmd`.

## Ledgers
D-046 turbine component quality and acceptance basis; A-450..A-457; U-123 (maker's certification
and component test evidence); standards to verify first.
