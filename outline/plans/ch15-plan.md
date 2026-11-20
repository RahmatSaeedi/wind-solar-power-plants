# Chapter 15 plan: Energy-yield modeling and losses (budget 105 pp; aim 115+)

Handoff: bullets (7) + worked example (monthly energy balance, each loss separate, gross to net
reconciled) + forecast lab (persistence vs weather-driven on a held-out synthetic PV/wind series,
error by horizon, ramp misses, intervals, pass the distribution to a dispatch exercise); blueprint
A-G; audit row 15 (theory: conversion models, losses, forecast validation; applied: reconcile
hybrid yield and score forecasts by horizon; design: traceable yield/forecast methods and
uncertainty; calculation: gross-to-net, forecast error, calibration, ramp skill; manufacturing:
N/A, model equipment tolerances and degradation inputs; implementation: reproducible model,
synthetic data provenance, validation report).

Safeguards: no clause values; machine learning not oversold (baselines first, leakage, drift);
cleaning not assumed beneficial (chapter 10 D-014 basis, water-aware); no data-pack licence text.

## Built on
- ch 5 hourly pack and losses.py (cable, transformer); ch 9 inverter efficiency and clipping;
  ch 10 PV chain (i_chain: 111.3 GWh before availability and degradation), soiling station and
  D-014 cleaning; ch 11 wind farm (D-015 wakes, layout A); ch 12 D-016 solar resource
  (long-term x 0.9859, P90); ch 13 D-017 wind basis (farm 191.87 GWh, hub density); ch 14 D-018
  layout W2b (196.9 GWh with terrain speed-up); Part II mastery hybrid chain to the POC.

## Companion
- plantp/yieldmodel.py (new): ModelConfig (versioned settings), hourly PV chain (POA from pack
  or ch 12 functions, temperature, IAM, DC losses, inverter curve, clipping), wind chain (power
  curve at hub density, farm wake factor by direction sector, availability), collection and
  transformer losses (losses.py), export limit, BESS conversion (S1), degradation, soiling with
  cleaning, loss waterfall with ordered application and interaction check (sum of losses vs
  product), monthly energy balance, unit/energy-balance checks; forecast tools: persistence,
  smart persistence (clear-sky / diurnal), synthetic NWP-like forecast with horizon-dependent
  error, quantile intervals, MAE/RMSE/bias, skill vs persistence, pinball loss and coverage,
  ramp detection and hit/miss, leakage demonstration (random split vs time split).
- companion/ch15: sources (pack hourly, long-term bases, synthetic forecast archive, seeded),
  examples_a (architecture: resolution, time alignment, versions), examples_b (PV and wind
  conversion steps), examples_c (gross-to-net and interactions), lab_d (monthly energy balance =
  worked example; waterfall; two assumptions), examples_e (forecast methods and metrics),
  lab_f (soiling/cleaning alternatives incl. no cleaning, water, cost), lab_g (forecast to
  dispatch: reserve from quantiles), integrated, worked, solutions.

## Structure
A sec-ch15-a: a-why, a-inputs, a-resolution, a-boundary, a-chain, a-settings (version control).
B sec-ch15-b: b-pv (irradiance to DC/AC, temperature, inverter), b-wind (curve, density, wakes,
  availability), b-hybrid (time alignment, coincidence, complementarity).
C sec-ch15-c: c-clipping, c-electrical, c-availability, c-soiling, c-degradation, c-curtailment,
  c-outages, c-storage, c-interaction (double counting), c-water.
D sec-ch15-d: monthly balance worked example, waterfall, two assumptions, unit checks.
E sec-ch15-e: e-horizons, e-baselines, e-nwp, e-imagery, e-ensembles, e-metrics, e-probabilistic,
  e-ramps, e-leakage, e-drift.
F sec-ch15-f: soiling lab (no-cleaning baseline, intervals, methods, water, cost, uncertainty).
G sec-ch15-g: forecast-to-dispatch lab.
Y, Z as usual (~130 problems).

## Numbering
Assumptions from A-264; unknowns from U-056; decision D-019 (energy model basis and loss
register); documents PLP-GEN-CAL-0006 (energy model), PLP-GEN-REP-0007 (yield and loss report),
PLP-OPS-PRO-0001? (forecast validation procedure) - check the register.
