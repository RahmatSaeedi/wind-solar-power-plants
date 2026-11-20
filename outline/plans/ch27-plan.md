# Chapter 27 plan: Power quality and plant behaviour (budget 80 pp; core chapter)

Handoff: chapter bullets on power-quality quantities and their measurement, the plant as a source
and a sink of disturbances, investigation of complaints with evidence, labs on measured data, and the
plant's grid services with acceptance evidence; blueprint A-E; audit row 27 (theory: harmonics,
interharmonics, flicker, unbalance, dips, transients, reactive power and frequency behaviour; applied:
a week of measurements at the POC and an investigation; design: filter and resonance, reactive
capability at the POC, monitoring plan; calculation: summation, scans, allocation, voltage changes,
step and droop metrics; manufacturing: filter capacitors and reactors, meters and transducers;
implementation: acceptance matrix, compliance statement, records).

Safeguards: limits and allocations are the operator's (teaching placeholders, U-100); background
levels at the POC unknown (U-101); no energised test procedures (tests named by purpose and evidence);
standards cited only with verified titles (STD-034, STD-035, STD-053, STD-128..130); service prices
and markets not assumed (teaching values only).

## Companion
- plantp/pq.py: thd, tdd, spectrum, aggregate, percentile, summation, scan, tuned_filter,
  voltage_change, step_metrics, droop_fit, ramp_exceedance, completeness. Tests
  test_ch27_pq.py (7).
- companion/ch27: sources (EMISSION, UNITS, NET, FILTER; week(), voltage_step(),
  frequency_event()), examples_a/b/e/k, lab_c (investigation), lab_d (week statistics, regression),
  examples_m/n/p (first expansions), integrated (by hand, monitoring, basis D-031), worked (E01-E05,
  P01-P22; solutions2 P23-P44).

## Expansion after the first draft (2026-11-16)

First render 36 of 80 pages; fourteen rounds of computed lessons brought it to 81 (38 section
files, 119 exercises, 16 figures, 76 worked examples): examples_r (current split, flicker
coefficient, Plt, voltage THD, recovery, causes), examples_s (converter as harmonic sink, Q at the
band edges, flagged intervals, before/after acceptance), examples_t (compliance summary, meter
reconciliation, frequency statistics, ringdown damping, data volume), examples_u (3p modulation,
CVT gain at harmonics, Q(U) spread, on-site instrument check), examples_w (service value against
losses, control point, pf signs under D-010), examples_x (supraharmonics, DC injection, line
unbalance, ripple-control signal), examples_y (dip through YNd11/Dyn, reactive current boost, area
of vulnerability), examples_z (resonance against units online, auxiliary board THD), examples_ab
(remedies at the worst unit count and order, alarm thresholds), examples_ac (the plant's own events
as RVC, power oscillation damping), examples_ad (filter tuning as a statistical budget).

Findings (in D-031): the 33 kV resonance moves with the units online (11th with about 8, 13th with
about 3, amplification ~45) - scans and remedies judged at the worst unit count and order (a damped
11th filter leaves 4.5 at the 7th; active damping helps least with few units); the 5th filter seen
from 132 kV resonates at 4.29, near a teaching 216.7 Hz ripple signal; the reactor tap is set on
site after measuring the capacitors (factory tolerances alone put 4.8 % of filters above 4.85);
units give 43 Mvar at 0.9 pu instead of 68; the controller at the plant bus reads up to 1 % away
from the POC; a whole-plant trip while giving 33 Mvar is a 3.0 % step at the POC; 6-pulse HVAC
drives give 13 % voltage THD on the 400 V board at 160 kW.

Terms aligned with the glossary after the expansion: flicker «سوسو» (فلیکر once in parentheses),
power filter «صافی», resonance «تشدید», active front end «یکسوسازِ فعال», damping ratio
«ضریبِ میرایی»; «فرورفتِ ولتاژ» recorded as the short form of «افتِ کوتاه‌مدتِ ولتاژ»; symbols
$S_\text{sc}$ and $h_\text{r}$ as in chapter 7.

IDs: D-031; A-336..A-340; U-100, U-101; documents PLP-ELE-CAL-0013, PLP-ELE-REP-0010,
PLP-ELE-PRO-0005, PLP-CTL-REP-0001.
