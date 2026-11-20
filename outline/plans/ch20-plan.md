# Chapter 20 plan: Plant control and energy management (budget 105 pp; core chapter)

Handoff: 6 bullets + worked example (hourly dispatch table for changing renewables, export limits
and SOC) + integrated dispatch/service lab (bounded controller simulation with forecast uncertainty
and a verified hypothetical service requirement; infeasible requests, comms loss, SOC limits,
priority/override); blueprint A-F; audit row 20 (theory: control theory, forecast-informed dispatch,
conditional service modes; applied: simulate forecast/export/storage changes and service conflicts;
design: hierarchy, modes, capability envelopes, limits, fail-safe; calculation: dispatch, ramp,
reserve, service headroom, SOC schedules; manufacturing: controller hardware/firmware build and
configuration -> ch 44/48; implementation: verify only sourced/project-applicable requirements by
simulation and commissioning tests).

Safeguards: grid services only where equipment, contract, grid rules and operator permit; no
invented grid-code values (all limits teaching, labelled); operator authority stated; no live-work
test procedures (commissioning tests named by purpose and evidence); defensive cyber only (ch 36).

## Companion
- plantp/control.py (new name, checked): first-order plant with PI loop and rate limiter, droop
  (frequency-power, voltage-reactive), P-Q capability, headroom/footroom, SOC headroom for a
  service, DP schedule with time-varying charge and export caps, hourly Controller with priorities,
  fallback on comms loss and alarms, imbalance settlement. Tests test_ch20_control.py.
- companion/ch20: sources (limits, services, prices, imbalance prices, forecasts from ch 15 nwp),
  examples_a (hierarchy timescales, PI/rate, droop), examples_b (export allocation, ramp smoothing on
  minute data, P-Q envelope, SOC headroom, priorities, degraded modes), lab_c (requirements -> test
  cases, settings hash, state machine), lab_d (worked example hourly table + controller tests),
  examples_e (DA/ID/RT schedules, forecast error -> reserve and SOC positioning, imbalance), lab_e
  (integrated service lab), examples_f (islanded load shedding, black-start energy, sync windows),
  integrated, worked.

## Sections
A a-hierarchy, a2-loops; B b-export, b2-ramp, b3-reactive, b4-soc, b5-priority; C c-design,
c2-verify; D d-lab; E e-forecast, e2-service; F f-island; y; z. D-024 control basis; A-299..;
U-077..; documents PLP-CTL-SPC-0001 (control narrative), PLP-CTL-PRO-0001 (test plan),
PLP-CTL-CAL-0001 (dispatch model).
