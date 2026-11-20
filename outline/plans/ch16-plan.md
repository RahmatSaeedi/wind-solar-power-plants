# Chapter 16 plan: Uncertainty and yield assessment (budget 75 pp; aim 80+)

Handoff: bullets (4) + worked example (simplified probabilistic yield range, largest contributors);
blueprint A-E; audit row 16 (theory: probability, uncertainty, yield-to-finance; applied: evaluate
yield uncertainty and finance downside cases; design: uncertainty budget and scenario set;
calculation: sensitivities, correlations, exceedance metrics, selected financial impacts;
manufacturing: N/A, carry factory quality/degradation evidence into uncertainty; implementation:
auditable probabilistic yield statement with explicit financing interface and limits).
Mastery gate: explain source, loss assumptions, uncertainty and limitations of a production estimate.

Safeguards: P90 never a guarantee or a full risk assessment; lender/project assumptions are theirs;
forecast skill (ch 15) kept apart from long-term uncertainty; teaching sigmas labelled (A-277..);
standards only STD-007 (JCGM 100:2008), STD-008 (JCGM 101:2008), IEC 61400-12-1:2022,
IEC 61724-1:2021 by title; no clause values; no data-pack licence text.

## Built on
ch 3 probability, normal distribution, Monte Carlo, tornado; ch 5 money (annuity, NPV);
ch 12 GHI budget 2.8 % (A-245) and P90; ch 13 wind speed budget 2.6 %, sensitivity 1.60 (A-254),
IAV; ch 14 cross-prediction W2b 1.35 % (A-265); ch 15 model 15.1 (net 295.14 GWh, D-019),
`plant_end`, IAV wind 4.5 % / PV 2.7 % / hybrid 3.2 %, r +0.12, tornado, bridge, wake k range,
model choices, availability time vs energy, lifetime series.

## Companion
- plantp/yieldrisk.py (new; plantp.uncertainty holds the ch 2/3 GUM tools): z of exceedance, p_value (normal), p_value_lognormal, combine
  (RSS with correlation matrix), variance shares, n-year IAV, sensitivity ratio, sample (normal,
  lognormal, uniform, triangular), mc_quantiles, convergence, annuity debt sizing (DSCR).
- companion/ch16: sources (budget of Plant P: wind, PV, plant components, teaching sigmas,
  correlations), examples_a (taxonomy numbers, variability vs uncertainty, sensitivity ratio,
  n-year), examples_b (RSS, correlation sweep, hybrid P90 not additive, distributions, MC
  convergence, nonlinear MC through plant_end, scenarios), examples_c (exceedance table, horizons,
  lognormal/skew, confidence on P90, forecast vs long-term), lab_d (budget, deterministic vs MC,
  drivers, value of another measurement year), lab_e (finance: cases, DSCR debt sizing, value of
  less uncertainty, what P90 is not), integrated, worked, solutions.

## Structure
A sec-ch16-a: a-why, a-variability, a-taxonomy, a-wind, a-pv, a-plant, a-sensitivity, a-evidence.
B sec-ch16-b: b-distributions, b-rss, b-correlation, b-hybrid, b-montecarlo, b-convergence,
  b-nonlinear, b-scenarios, b-falseprecision.
C sec-ch16-c: c-pxx, c-horizon, c-skew, c-confidence, c-uses, c-forecast, c-communication.
D sec-ch16-d: d-budget (worked example), d-mc, d-drivers, d-measure, d-statement.
E sec-ch16-e: e-cases, e-dscr, e-value, e-notguarantee, e-portfolio.
Y, Z (~140 problems).

## Numbering
Assumptions A-277..; unknowns U-061..; decision D-020 (uncertainty basis and financing cases);
documents PLP-GEN-REP-0009 (probabilistic yield statement), PLP-GEN-CAL-0007 (uncertainty model).
