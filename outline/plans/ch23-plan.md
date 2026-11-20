# Chapter 23 plan: Electrical one-line and system boundaries (budget 100 pp; core chapter)

Handoff: 11 bullets + worked examples (draft Plant P's one-line with provisional parameters; trace one
PV block from module terminals through inverter, transformer, protection and grid meter with every
interface and verification record); blueprint A-G; audit row 23 (theory: topology, ownership,
boundaries; applied: trace a source to the delivery point; design: plant/export one-lines,
ownership/isolation boundaries, auxiliary architecture; calculation: loads, distribution,
control-power autonomy, bounded circuit quantities; manufacturing: link transformers, panels, UPS,
batteries, HVAC, pumps, export equipment to supplier/FAT evidence; implementation: plant/export
one-lines, responsibility matrix, test boundaries, restoration case). Part V mastery gate: say what
each study proves, what data it needs, who approves it, what evidence closes the requirement.

Safeguards: tests named by purpose and evidence only; no switching, earthing or live-work steps; fire
design left to fire engineers and authorities (interfaces recorded); teaching values; the POC owner
and meter place stay open (U-065).

## Companion
- plantp/oneline.py (new): Bus, Branch (owner, zone, status per parameter, isolation, meter, test),
  OneLine with path (BFS), crossings (voltage, owner, zone, isolation, meter, test), checks
  (undefined bus, windings vs buses, voltage join, missing zone, owner boundary without isolation),
  schedule. plantp/auxpower.py (new): Load with duty by state, demand with diversity, next_size,
  sc_current_ka, start_dip, battery_ah (simplified duty cycle), charger_a, ups, hvac_kw, shed,
  timeline. Tests test_ch23_oneline.py (8).
- companion/ch23: sources (plant network: split 33 kV bus, feeders WS1-3, PVF1-3, BESS-A/B, incomers,
  SST A1/A2, line bay E1, open line, grid bay G1; PV block DC detail; AUX register; DC duty),
  examples_a (levels, inventory, boundaries, transformer schedule, interface matrix, sections,
  feeders), examples_c (review with 8 planted errors, revision log), lab_d (provisional one-line,
  PV trace with records = worked example 2, unresolved list, circuit schedule), examples_e
  (register, classes, sizing, DC, rooms, shed, cause-and-effect, restoration, standby), lab_g
  (turbine trace, MVA method, responsibility, meter losses, unresolved), examples_m (phases, 33 kV
  earthing, designations, lighting/drainage, LV drop, battery life, connection alternatives),
  examples_n (meter error, string voltage rise, battery-aux boundary, isolation boundary and RMU
  omission, cable quantities, LV distribution, DC window, night import), integrated, worked.

## Expansion after the first draft (2026-11-16)

First render: 68 of 100 pages. Six rounds of computed lessons brought it to 100:
examples_p (per unit, fault level along the path, LV faults, phase shift, energisation
stages, interlocks, register status, mimic, fibre ring), examples_q (title blocks,
cross-references, legend, tag pattern, phase balance, shared line with a third party),
examples_r (starting method vs diesel, K-factor, auxiliary sources), examples_s (full
schedule, battery trace, document register), examples_t (temporary maintenance load,
receiving network), examples_u (floating DC and two earth faults, zones from the model,
NER sizing); new sections a5, c2, c3, d2, e5, e6, f4, f5, g4, g5; 223 exercises.
A radial-vs-ring lesson was dropped: chapter 18 already decides it with its own values.
