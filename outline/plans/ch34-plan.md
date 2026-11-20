# Chapter 34 plan: Instrumentation and control (budget 95 pp, plan for ~105)

Handoff: 7 bullets + three worked items (Plant P I/O list; trace of a measured grid voltage from
instrument to operator display; test case for a simulated sensor failure); blueprint A-G; audit
row 34 (scaling, loop response, autonomy, response limits; link sensor/panel/controller
production and calibration to ch 48; tested cause/effect, interface, service-mode and
failure-state records).

Overlaps to respect (reference, do not repeat): ch 2-3 uncertainty and signals (GUM, RMS,
aliasing), ch 12-13 instruments (pyranometers, anemometers, QC), ch 20 control (PI with
anti-windup, priorities, comms hold and fallback, D-024), ch 23 auxiliary and DC supplies
(battery Ah, UPS, D-027), ch 26 protection settings and checksums, ch 32 fire C&E matrix and
evidence ladder (lab C). Chapter 34 adds the I&C view: the measurement chain, the controller as a
sampled machine, I/O, panels, FAT, loop checks, control power per load, and the interfaces.

Safeguards: no live-work or energised test steps (loop checks named by purpose and evidence; all
tests on de-energised or simulated signals); fire-system interface keeps life-safety control
separate from dispatch and gives no universal fire prescription; grid services only where
required or permitted (REQ-S01 hypothetical, ch 20); standards cited only verified.

## Data (A-385..A-392)
ch 23 one-line and AUX/DC_DUTY; ch 20 LIMITS, SERVICE, PI gains; ch 26 VT/CT; ch 28 POC voltage
band; ch 19 BESS containers (8); ch 32 fire areas; teaching instrument specs (accuracy classes,
drifts, ranges), panel losses, PLC scan times, MTBF/MTTR (teaching).

## Companion
- plantp/instrumentation.py (new): ma_to_eng/eng_to_ma, loop length, ADC resolution, combine
  uncertainty, Pt100 Callendar-Van Dusen and lead error, thermocouple CJC, clock drift,
  calibration interval, first-order filter, scan response, PI discrete (Euler/Tustin), panel
  temperature rise, I/O with spares, autonomy per load, availability with redundancy, quality
  flag rules, setpoint validation.
- companion/ch34: sources, examples_a (measurement chain), b (architecture), c (design/FAT),
  lab_d (grid-voltage trace + I/O list + failure test = worked examples 1-3), e (control
  power), f (fire interfaces), g (grid-service interfaces), more rounds as needed, integrated
  (D-038), worked.

## Sections (~60 lessons, 140+ problems, 18+ figures)
A measurement chain; B architecture; C design and factory realization; D functional lab;
E control-power resilience; F fire-system interfaces; G grid-service interfaces; K manufacturing
(link to ch 48); Y Plant P (D-038); Z assessment.
