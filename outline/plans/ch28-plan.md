# Chapter 28 plan: Grid studies and performance requirements (budget 90 pp; core chapter)

Handoff: 5 bullets + worked example (study-input checklist and compliance matrix for Plant P's
proposed POC); mastery gate (what each study proves, what data it needs, who approves it, what
evidence closes the requirement); blueprint A-G; audit row 28 (theory: power-system, dynamic,
export-system and grid-service study principles; applied: an interconnection, export circuit and a
conditional service requirement; design: study scope and models across plant, route and POC with
requirement-to-test traceability; calculation: bounded network, loss, fault and capability examples;
manufacturing: OEM/network model and configuration provenance, validated equipment and circuit data;
implementation: reviewed study inputs/results, export assumptions, service and test evidence).
Thread: weak-grid, islanded and black-start foundations (with ch 18, 20; evidence in ch 50-51) -
conditional, never implied as available or permitted by default (D-024: Plant P offers neither
grid-forming nor black start).

Safeguards: no country requirement invented - every requirement is a placeholder "REQ-G.."
for the operator's code (U-102); study results are teaching, not an approved study; the operator
and licensed engineers approve models and results; no energised test procedures (tests named by
purpose and evidence); standards cited only with verified titles (STD-102 IEEE 2800-2022, STD-105
IEC 61400-27-1:2020, STD-131 IEC 60909-0:2016, STD-132 IEC 61400-27-2:2020; STD-034 for
measurements).

## Network model (A-341..A-345)
Grid Thevenin at the POC: 1,500 MVA X/R 8 (maximum, ch 17), 900 MVA X/R 6 (minimum, A-341);
132 kV line 7.06 km r 0.12, x 0.40 ohm/km, c 9 nF/km; 2 x 63 MVA YNd11 uk 12 %, pk 250 kW,
taps +/-10 % in 1.25 % steps; split 33 kV bus MV-A / MV-B (D-027); eight feeders (WS1-3 4.4/4.8/5.2
km, PVF1-3 2.4/2.0/2.2 km, BESS-A/B 0.3 km) aggregated at half length; unit transformers aggregated
(uk 6 %, A-342); units 5 MW class with 5.6/5.5 MVA (wind/PV), BESS PCS 5 MVA (S1).

## Companion
- plantp/gridstudy.py (new): `Branch`, `ybus`, `load_flow` (Newton-Raphson, slack/PV/PQ),
  `flows`, `thevenin`, `zbus`, `fault_current` (equivalent source with c and converter current
  sources), `apparent_impedance`, `frt_sim`, `freq_event`, `ndz`, `escr`, `wscr`,
  `validation_errors`, `phase_jump_current`, `sync_power`. Tests test_ch28_gridstudy.py.
- companion/ch28: sources (network, cases, requirements REQ-G01..G24 placeholders, input register,
  model register), examples_a (data, Thevenin min/max, submission checks), examples_b (load flow
  cases, controller Q, losses, short circuit, infeed, validation), examples_c (FRT, frequency,
  voltage-control stability, NDZ with the hourly year, restoration, dispatch), lab_d (worked
  example: input checklist + compliance matrix), examples_e (SCR/ESCR/WSCR, phase jump, low fault
  current, resynchronisation), examples_f (envelopes, interactions, versions), examples_g (export
  line rating, N-1 with energy at risk, parameter sensitivity, data ownership), integrated, worked.

## Sections (about 45 lessons, 130+ problems, 15 figures)
A process, POC data, models, submission quality; B load flow, cases, reactive, losses, short
circuit, protection with infeed, model validation; C ride-through, frequency, voltage-control
stability, islanding, restoration/ramps/dispatch/telemetry, tests; D worked example + assumption
log + approval boundaries; E weak grid, grid-forming, low fault current, black start and
resynchronisation; F envelopes, interactions, versions and traceability; G export circuit,
contingencies, route/circuit data; K not applicable + OEM model interface; Y Plant P (D-032).

## Expansion after the first draft (2026-11-16)

First render 57 of 90 pages; thirteen rounds brought it to 90 (55 section files, 153 exercises,
19 figures): examples_h (P-V nose curves, bus sensitivities, tap limits), examples_k (earth fault
with the earthed stars, peak current, auto-reclose), examples_m (connection alternatives, harmonic
impedance locus, study programme as a critical path), examples_n (test predictions: P-Q points,
voltage step, frequency injection), examples_p (feeder aggregation checked turbine by turbine, Q at
night, line temperature), examples_q (battery shared between reserve and Q, coincident dip and
frequency event), examples_r (export limit in a gust, negative sequence, operating restrictions),
examples_s (firmware change, Gauss-Seidel check, re-study triggers), examples_t (Q(U) slope, fault
level growth, trips from a mis-set relay), examples_u (signal list, shallow/deep charges, report
completeness), examples_v (U-Q/Pmax profile, the plant as a grid contingency), examples_w (strength
at the unit terminals, S1 night import), examples_x (intertrip channel availability and timing).

Findings (D-032): losses 4.41 against model 15.1's 3.29 GWh (unit transformers and reactive current
missing in the energy model); Q capability +46/-63 Mvar at full output (ch 27's 56 was optimistic);
+33 Mvar not met on a 45 C day (29); the plant end of the line cannot see resistive faults (infeed x12)
- differential or intertrip; passive islanding relays blind ~1,760 h a year - intertrip on a
supervised channel; the line's rating did not bind in the data year (wind cools the line); N-1
numbers reconciled with ch 18 (line faults 17 MWh; the line's maintenance day 810 at random, 76 on a
calm day); the earthed YN stars carry ~3 kA of network earth faults; the export set-point needs a gust
margin (98-99 MW).

Terms aligned with the glossary: Thevenin equivalent «معادلِ تونن», firmware «میان‌افزار», headroom
«جای بالارو», intertrip «قطعِ متقابل».

IDs: D-032; A-341..A-348; U-102 (code and values), U-103 (operator's network model, minimum strength,
neighbours); documents PLP-ELE-REG-0004, REG-0005, CAL-0014, REP-0011, PLP-CTL-REG-0002; standards
STD-131 IEC 60909-0:2016, STD-132 IEC 61400-27-2:2020 (with STD-034, 102, 105).
