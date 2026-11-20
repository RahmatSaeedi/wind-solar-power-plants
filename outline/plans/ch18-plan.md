# Chapter 18 plan: Hybrid-plant architecture (budget 90 pp; core chapter)

Handoff: bullets (7) + worked examples (compare two architectures; decompose Plant P into equipment
and subassemblies; resolve a voltage/connector/thermal/communications mismatch before procurement);
blueprint A-F (operating concepts; architecture selection; interfaces and functional decomposition;
water-service architecture; architecture lab; collector and export architecture); audit row 18
(theory: architectures, energy flows, water services, export systems; applied: compare AC/DC/mixed
cases, service demands, export alternatives; design: decompose plant, collector, substation, route
and water-service interfaces; calculation: capacities, limits, losses, source/use balances;
manufacturing: product breakdown, make/buy, factory interfaces; implementation: architecture
diagrams, export basis, water-service basis, interface register).

Safeguards: selection conditional on grid data, permits, terrain, ownership (U-065..U-068); no
universal fire-water prescriptions (fire demands are placeholders for the authority and chapter 32);
teaching values labelled; no live-work content.

## Companion (sketch)
- plantp/architecture.py (new; check the name): coupling comparison (AC vs DC vs mixed for the
  S1 battery: conversion chains, round-trip and clipping recapture), capacity screening (PV/wind/
  BESS/export ratios with model 15.1's plant_end), collector options (radial strings, voltage
  33 vs 66 kV, losses, cable cost), export options (OHL vs cable, single vs double circuit,
  redundancy and expected unserved energy), product breakdown tree (plant > system > subsystem >
  equipment > LRU) with counts, interface register records and checks (voltage, connector,
  thermal, protocol), water balance (sources/uses/storage by month: cleaning from ch 15, dust,
  sanitation, cooling, fire reserve as held volume).
- companion/ch18: sources, examples_a (modes, coupling), examples_b (selection, ratios,
  expansion, curtailment/reserve), examples_c (decomposition, interface map, ICD, mismatch),
  lab_d (water-service basis), lab_e (architecture comparison worked example), examples_f
  (collector and export), integrated, worked, solutions.
