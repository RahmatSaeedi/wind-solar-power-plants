# Chapter 17 plan: Load, grid, and project requirements (budget 60 pp; process chapter)

Handoff: bullets (4) + worked example (peak demand and annual energy from hourly data, then a
grid-information request list); blueprint A-E; audit row 17 (theory: load behaviour, grid
requirements, connection boundaries; applied: analyse customer/grid data and a proposed POC;
design: needs, ownership, export route and interface obligations into measurable requirements;
calculation: demand, energy, export limits, bounded connection checks; manufacturing: N/A, supplier
ratings and evidence requirements; implementation: requirements, grid-data request,
responsibility/interface registers).

Safeguards: no invented country rules (connection-cost allocation, grid codes, tariffs are
national: chapters 28, 55-57); grid data are synthetic teaching values (labelled); bounded checks
only (screening, not a grid study); no live-work content.

## Framing for Plant P
Plant P is an IPP exporting at 132 kV (chapter 1). Three loads are analysed: (1) the regional 132
kV substation area the plant feeds (town, farms with pumping, small industry; synthetic, A-284) for
grid context (minimum load, reverse flow, growth); (2) the plant's own loads (critical /
controllable / interruptible; from chapter 15 own use and chapter 18 preview); (3) an industrial
self-supply variant (chapter 1 business model) for the worked example.

## Companion
- plantp/demand.py (new; check the name is free): load metrics (energy, peak, load factor,
  duration curve, coincidence/diversity, peak by resolution, monthly/seasonal profiles), growth
  projection, resilience hours of critical load from a battery, net flow at a node, bounded
  connection checks (thermal, voltage rise on a line, short-circuit ratio), requirement records.
- companion/ch17: sources (synthetic loads A-284, network teaching data A-285), examples_a
  (demand metrics and use cases), examples_b (grid context and bounded checks), lab_d (requirements
  lab: worked example + register + grid data request), examples_e (boundary and responsibility
  matrix, cost allocation patterns), integrated, worked, solutions.

## Structure
A sec-ch17-a: a-why, a-interval, a-metrics, a-shape, a-growth, a-classes (critical/controllable/
  interruptible), a-resilience (islanding, critical hours).
B sec-ch17-b: b-poc, b-voltage, b-netflow (export/import, reverse flow), b-capacity (thermal,
  voltage rise, short-circuit ratio), b-data (data request), b-roles.
C sec-ch17-c: c-stakeholders, c-measurable, c-priorities, c-assumptions, c-acceptance,
  c-traceability, c-change.
D sec-ch17-d: worked example, register, request list.
E sec-ch17-e: e-boundary, e-assets, e-matrix (RACI), e-cost, e-tests, e-operating.
Y, Z (~90 problems).

## Numbering
Assumptions A-284..; unknowns U-065..; decision D-021 (requirements baseline and connection
boundary); documents PLP-PRJ-REG-0007 (requirements register), PLP-ELE-REQ-0001? (check the
register's type codes), PLP-PRJ-REG-0008 (responsibility/interface matrix).
