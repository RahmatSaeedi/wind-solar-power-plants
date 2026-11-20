# Chapter 37 plan: Performance monitoring and analytics (budget 85 pp, plan for ~95)

Handoff: 9 bullets (availability, yield, loss and performance indicators; SCADA data validation,
baselines, expected vs actual, alarm quality, fault detection, root cause, evidence, limits of
predictive maintenance; RAM vs performance vs data availability, event taxonomy, failure/downtime
boundaries, planned/forced/external, reporting windows; reliability-data practice - hierarchy,
failure codes, exposure, censored records, fleet comparability, uncertainty, quality, feedback;
forecast quality by horizon and use - bias, MAE/RMSE, probabilistic scores, ramps, skill,
calibration, completeness, drift, impact, no training-data scoring, no single score as a dispatch
guarantee; grid-service performance - response availability, tracking error, response/recovery
time, delivered power/energy, telemetry quality, exclusions, settlement evidence; worked example
monthly data distinguishing soiling, inverter outage, curtailment and sensor fault; reliability lab
on synthetic event logs with missing timestamps, duplicates, inconsistent definitions; forecast and
service analytics lab on held-out forecasts and a service trace against a supplied spec), blueprint
A-G, audit row 37 (manufacturing N/A: factory failure/quality data as inputs).

Overlaps to respect: ch 15 (yield model 15.1, forecasts, scores, skill, pinball, CRPS, ramps,
reliability diagrams - reference, do not repeat; ch 37 scores held-out operating forecasts and
monitors drift), ch 16 (uncertainty, P-values), ch 20 (service REQ-S01, controller), ch 27 (service
verification tests, droop fit), ch 34 (telemetry accuracy, quality), ch 35 (historian, data
completeness per tag, report with gaps, alarm floods, CMMS IDs, functional location vs equipment),
ch 36 (indicators). Chapter 37 adds: KPI definitions with time windows, expected-energy baselines
from the yield model, loss classification, IEC 61724-type PR concepts (verify edition), IEC 61400-26
availability (verify), event taxonomy, reliability statistics (MTBF with censoring, Weibull,
Crow-AMSAA trend), fleet comparability, forecast monitoring in operation, service-performance
scoring and settlement evidence.

Safeguards: synthetic data only; predictive maintenance limits stated; no guarantee from a score;
contractual availability definitions are the contract's (concepts only).

## Data (A-409..A-416)
Data pack hourly year S0/S1 and model 15.1 as baseline; synthetic monthly operating data with
planted soiling, an inverter outage, curtailment and a sensor fault; synthetic event logs with
missing timestamps, duplicates and two outage definitions; turbine component failure records with
censoring; held-out forecast archive (ch 15 A-267 extension); service response trace and a supplied
acceptance spec (REQ-S01 placeholder).

## Companion
- plantp/performance.py (new): PR and temperature-corrected PR, energy-based and time-based
  availability with exclusions, loss waterfall by class, expected-vs-actual residual tests,
  CUSUM drift, event merge/deduplicate/clip to window, MTBF/MTTR with censored data (exponential
  MLE), Weibull fit, Crow-AMSAA beta, confidence interval for a failure rate (chi-square),
  forecast scores by horizon (bias, MAE, RMSE, skill vs persistence), PIT/coverage, service
  tracking error and response/settling time against a spec.
- companion/ch37: sources, examples_a (indicators), b (data to diagnosis), lab_c (monthly
  worked example), examples_d (taxonomy), lab_e (reliability), examples_f (reliability practice),
  lab_g (forecast and service), integrated (D-041), worked.

## Sections (~55 lessons, 150+ problems, 18+ figures)
A metrics and baselines; B data-to-diagnosis; C analytics and limits (with the monthly worked
example); D diagnostic lab; E reliability-data discipline; F quantitative monitoring lab; G forecast
monitoring; plus service-performance monitoring; K note (manufacturing N/A, factory data as input);
Y Plant P (D-041); Z assessment.
