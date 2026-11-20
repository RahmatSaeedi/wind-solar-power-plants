# Chapter 51 plan: operating the plant (budget 90 pp, plan for ~100)

Handoff: 10 bullets (control-room roles to restoration; community and workforce commitments in
operation; authoritative asset and configuration records; collector/export assets with the
network owner; auxiliary systems routine and abnormal; fire-system readiness; operational water
plan; forecast-to-schedule-to-dispatch; grid services within approved capability; worked example:
an operating shift with a forecast change, an export restriction and a battery near an operating
limit). Blueprint A-N (A operating organization, B normal/abnormal operation, C operational
assurance, D shift simulation, E commercial operations, F auxiliary systems, G fire readiness,
H water stewardship, I forecast-informed operations, J grid-service operations, K export assets,
L community/workforce commitments, M asset information and configuration control, N emergency
and physical-security operations). Audit row 51. Persian letters A-N = الف ب پ ت ث ج چ ح خ د ذ
ر ز ژ.

Running data: the operating year of ch 37 (`operating_year()`, model 15.1 + noise + planted
problems), ch 15/20 forecasts at the POC through `plant_end`, the ch 20 `Controller` (priorities,
SOC limits, export cap, comms fallback), ch 19/20 prices and imbalance terms, ch 29 water demand,
ch 32 emergency plan, ch 33 commitments, ch 35 tags, ch 50 handover records and deviations.

Overlap rule: ch 20 designed the controller and its priorities, ch 15/37 the forecasts and their
scores, ch 29 the water balance, ch 32 the emergency plan, ch 33 the commitments, ch 35/36 the
SCADA and OT security, ch 37 performance monitoring, ch 50 the handover. Ch 51 runs them as an
operator: shift logs and handover, the day's schedule and its updates, curtailment and imbalance
records by cause, abnormal events and restoration, permits and authority in operation, the
service's availability and settlement inputs, auxiliary autonomy in a real outage, fire
impairments in operation, water metered against the model, commitments kept, asset records
reconciled as the plant changes, emergency exercises and incident learning.

Safeguards: no live-work or switching procedures (authority, records and decisions only);
defensive OT only; no tactical security detail; commitments only as approved; a forecast is never
a guarantee; teaching values only; market rules only as local-verification items.

## Sections (files)
- `_51-a-organization.qmd` A; `_51-b-operation.qmd` B; `_51-c-assurance.qmd` C;
  `_51-d-shift.qmd` D (worked example); `_51-e-commercial.qmd` E, I, J;
  `_51-f-systems.qmd` F, G, H, K; `_51-l-people.qmd` L, M, N; y, z.

## Companion
Module `plantp/operations.py`; chapter scripts `companion/ch51/`; tests
`test_ch51_operations.py`.

## Ledgers
D-055 operating basis; assumptions A-522 onwards; unknown U-132 (operator's procedures and the
grid operator's operating instructions, market or contract rules where they apply).
