# Chapter 12 plan: Solar-resource assessment (budget 85 pp minimum; aim 95+)

Handoff: chapter 12 bullets (4), blueprint A-E, audit row 12 (theory: solar geometry, radiation,
sensor and soiling evidence; applied: compare measured/provider and soiling records; design:
measurement campaign and sensor-cleaning protocol; calculation: plane-of-array and cleaning/data
impacts; manufacturing: N/A for sensor production, evaluate supplier calibration/specification
evidence; implementation: quality-controlled dataset and cleaning-decision inputs). Worked example:
compare two sample irradiance sources and quantify how the choice changes an initial PV estimate.
Safeguards: no clause values of measurement standards; QC limits presented as teaching versions of
published test families; no work-at-height or electrical-work procedures for station maintenance.

Lesson learned from ch 11: a first pass of 9 section files gave 77 pp of 115. Plan 15-16 section
files and 120+ problems from the start.

## Built on (reference, do not repeat)
- ch 3: sun position, declination, equation of time, hour angle (sec-ch03-...), statistics.
- ch 5: data loading, QC flags of the pack (qc_flag), averaging effects (fig-ch05-averaging).
- ch 9: PV hourly model (pvyear), DC window.
- ch 10: Hay-Davies POA (pvcell.poa_hay_davies), IAM, Faiman, soiling station, D-014 cleaning
  basis, U-034.. soiling unknowns, PR and uncertainty of a sample mean.

## Companion
- plantp/irradiance.py (new): extraterrestrial normal irradiance, air mass, clearness index,
  Haurwitz clear-sky GHI, Erbs decomposition, isotropic and Hay-Davies transposition wrappers,
  closure test, teaching QC limits (physically possible / extremely rare families), sunrise
  symmetry time-shift test, cross-correlation lag, gap filling in clearness index, drift ratio,
  MBE/RMSE/KSI-like distribution distance, long-term ratio correction, P50/P90 with combined
  uncertainty. Tests: test_ch12_irradiance.py.
- companion/ch12: sources.py (synthetic "provider" hourly series from the pack: bias, noise,
  monthly bias pattern, seeded; synthetic 20-year long-term monthly series with interannual
  variability; synthetic one-minute days for QC), examples_a (geometry, time, k_t, clear sky,
  decomposition, transposition comparison, horizon), examples_b (sensor classes, response,
  cosine error, temperature, soiling of sensor, calibration drift), examples_c (QC flags,
  closure, time shift, gaps, drift, satellite comparison, long-term correction, uncertainty),
  lab_d (two-source comparison -> PV energy with the ch 10 chain; cleaning a faulty series;
  data-quality plan), lab_e (sensor cleaning vs module cleaning; soiling evidence to D-014),
  integrated, worked, solutions.

## Structure (labels)
A sec-ch12-a: a-why, a-time, a-sunpos, a-extra, a-components, a-clearsky, a-decomp,
  a-transposition, a-horizon, a-seasons.
B sec-ch12-b: b-sensors, b-classes, b-refcell, b-dni, b-mounting, b-calibration, b-cleaning,
  b-logging, b-maintenance, b-supplier (calibration certificates and specifications as evidence).
C sec-ch12-c: c-timestamps, c-qc, c-closure, c-gaps, c-drift, c-satellite, c-reanalysis,
  c-longterm, c-variability, c-uncertainty.
D sec-ch12-d: d-compare (handoff worked example), d-clean, d-energy, d-plan.
E sec-ch12-e: e-separate, e-sensorsoil, e-evidence, e-link.
Y: sec-ch12-plantp (int-1 one day QC; int-2 annual resource P50/P90; int-3 measurement and
  data-quality plan), design, lab, mfg (N/A: supplier evidence), std, deliverable.
Z: summary, vocab, assess (~120), solutions, examples-out.

## Numbering
Assumptions from A-240; unknowns from U-043; decision D-016 (solar resource basis: data-pack
ground year corrected to the long term by the provider ratio; QC rules; P50/P90 method).
Documents: PLP-GEN-REP-0004 (solar resource report), PLP-GEN-PRO-0001 (measurement and
data-quality plan), PLP-GEN-CAL-0004 (long-term correction and uncertainty).
Standards: ISO 9060:2018 (STD-014) and IEC 61724-1:2021 (STD-069) registered; verify before
citing: ISO 9847 (field calibration of pyranometers), IEC 60904-2 (reference devices),
ISO 9059 (pyrheliometer calibration) — cite only with verified title and edition.
