# Chapter 13 plan: Wind measurement and assessment (budget see outline; aim 100+ pp)

Handoff: chapter 13 bullets (3), blueprint A-D, audit row 13 (theory: wind climate and measurement
physics; applied: diagnose inconsistent mast/remote-sensing data; design: campaign, sensor heights
and quality controls; calculation: shear, distributions, uncertainty; manufacturing: N/A for sensor
production, evaluate calibration and supplier controls; implementation: traceable wind dataset and
campaign acceptance report). Worked example: diagnose a likely sensor problem from inconsistent
measurements at two heights and document its effect on uncertainty.
Safeguards: no climbing, mast erection or rescue procedures; no clause values of the measurement
standards (IEC 61400-12-1:2022 and the remote-sensing/measurement parts are cited by title only);
icing and lightning as hazards described, not procedures.

Plan 15-16 section files and 110+ problems from the start (ch 11 lesson).

## Built on (reference, do not repeat)
- ch 2: shear exponent, roughness length; ch 3: statistics, Weibull, Gumbel, autocorrelation,
  wind rose; ch 4: wind power, density; ch 5: raw mast file cleaning (D1-D9 defects, flags),
  Weibull fits; ch 11: density-equivalent speed (D-008), power curve, Jensen wakes (D-015),
  turbulence 10 % assumption, U-039 (turbulence and extremes need 10-min data).
- ch 12: QC philosophy (flags, order of tests, gaps, drift, long-term ratio, P90).

## Companion
- plantp/windres.py (new): log and power-law profiles and fits from several heights, shear by
  sector and hour, veer, turbulence intensity and its representative value, gust factor, air
  density from p and T (reuse physics), cup overspeeding and tilt/cosine errors (teaching),
  anemometer transfer function, tower-shadow ratio test between two booms, icing detection
  (stuck/low-sd at freezing), data recovery, MCP: linear least squares, variance ratio, matrix
  (sectorwise ratio), concurrent-period correlation, extreme wind from Gumbel (annual maxima),
  uncertainty budget for the wind speed and energy (sensitivity dE/dv).
- companion/ch13: sources (a synthetic 10-min year at 60/80/100 m with diurnal stability,
  sectors, a reference long-term series of 20 years (reanalysis-like), lidar series with
  its own errors; seeded), examples_a/b/c, lab_d (two-height diagnosis = worked example,
  QC flags and plots, uncertainty, limitations), integrated, worked, solutions.

## Structure (labels)
A sec-ch13-a: a-why, a-climate, a-boundary (stability, diurnal), a-shear, a-veer, a-turbulence,
  a-density, a-instruments (cups, sonic, vanes), a-remote (lidar, sodar), a-mast (booms, tower
  shadow), a-calibration.
B sec-ch13-b: b-campaign (heights, hub height, configuration), b-redundancy, b-recovery,
  b-icing, b-faults, b-filtering, b-metadata, b-acceptance.
C sec-ch13-c: c-extrapolation, c-sectors, c-distributions, c-turbulence, c-extremes, c-mcp,
  c-uncertainty.
D sec-ch13-d: d-diagnose (worked example), d-flags, d-uncertainty, d-limitations.
Y: sec-ch13-plantp (int-1 one mast day; int-2 long-term hub-height wind with P90; int-3 campaign
  acceptance report), design, lab, mfg (N/A: calibration and supplier evidence), std, deliverable.
Z: summary, vocab, assess (~115), solutions, examples-out.

## Numbering
Assumptions from A-250; unknowns from U-047 (closes U-039 in part with synthetic 10-min data);
decision D-017 (wind resource basis: hub-height long-term speed by MCP with the reference series,
shear from the mast, turbulence representative value; replaces the pack speeds for later
chapters only when the real campaign exists). Documents: PLP-GEN-REP-0005 (wind resource and
campaign acceptance report), PLP-GEN-PRO-0002 (wind measurement plan), PLP-GEN-CAL-0005 (MCP and
uncertainty).
