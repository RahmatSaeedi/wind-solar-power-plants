# Chapter 29 plan: Site investigation and civil works (budget 95 pp; core chapter)

Handoff: 7 bullets + two worked examples (water-stewardship case: wet/dry/robotic/no cleaning against
soiling loss, water, cost, energy, safety and environment, with a source-to-use balance, uncertainty
register and monitoring plan; review a sample geotechnical summary and prepare design questions
without presuming a foundation solution); blueprint A-I; audit row 29.

Safeguards: no foundation solution presumed - questions for qualified civil/geotechnical engineers;
correlations (SPT to friction angle, CBR) are screening tools; no universal fire-system
prescriptions - firewater rates, durations and separations come from the fire strategy, the
authority and product tests (placeholders, U-105); water rights and permits are project-specific
(U-104); climate evidence is teaching (synthetic series), not a hazard study; fictional site.

## Data (A-349..A-355)
Site: the ch 14 synthetic 13 x 7 km grid (D-018 layout W2b, east PV block, middle substation);
boreholes BH-01..BH-10 (fictional: layers, SPT N, groundwater, lab results) and two seismic lines;
synthetic 30-year rainfall record (annual maximum hourly and daily), temperatures and gusts from the
data pack plus a warming scenario; wells (transmissivity, storage, seasonal yield); demands
(cleaning from ch 10 / D-014, construction concrete and dust, staff); soils (USLE K), land cover.

## Companion
- plantp/civil.py (new): refraction_depth, bearing_factors, bearing_square, elastic_settlement,
  spread_pressure, rational_peak, kirpich_tc, manning_q, pipe_full_q, usle, ls_factor, lot_accept,
  characteristic, cooper_jacob, trench_inflow, gumbel_return. Tests test_ch29_civil.py (8).
- companion/ch29: sources, examples_a (survey control, DEM, boreholes, refraction, ground model,
  interpolation limits), examples_b (roads: grades and curves; crane pads; trenches; drainage by
  rational method; culverts; erosion; cut/fill), examples_c (compaction lots, concrete strength,
  NCRs, records), lab_d (geotechnical summary review - worked example), examples_e (climate
  extremes and design values, warming scenario, heat/dust/flood links), examples_f (fire access,
  turning, firewater volume from placeholders, runoff containment), examples_g (water sources and
  monthly balance with reserve, drought), lab_h (cleaning strategies - worked water case,
  infrastructure sizing, metering), examples_i (corridor constraints, crossings, reinstatement),
  integrated, worked.

## Sections (about 50 lessons, 140+ problems, 16 figures)
A survey and ground model; B civil design basis; C construction quality and environment; D
investigation review exercise; E climate resilience; F fire-service site infrastructure; G water
resources and balance; H water infrastructure and optimisation lab; I connection corridor and
substation site; K manufacturing (precast, aggregates, concrete supply as interfaces to ch 47);
Y Plant P (D-033).

## As built (2026-11-16)
- Companion scripts: sources, examples_a/b/c/e/f/g/i/k/m/n/p/q, lab_d, lab_h, integrated, worked
  (E01-E08, P01-P20); module plantp.civil (refraction, bearing, drainage, acceptance, water, gumbel
  blocks quoted); 18 figures; 21 section files; 151 problems; 64 worked examples; 33 equations.
- D-033 civil and water basis (int_basis). Assumptions A-349..A-355; unknowns U-104 (water right),
  U-105 (fire strategy values), U-106 (transport limits), U-107 (wadi flood levels and paths).
- Documents: PLP-CIV-REP-0001 (ground model, review, questions), PLP-CIV-SPC-0001 (civil design
  basis), PLP-CIV-CAL-0001 (drainage, earthworks, water balance), PLP-CIV-PRO-0001 (ITPs and
  acceptance rules), PLP-CIV-REP-0002 (water management plan), PLP-CIV-REG-0001 (corridor and
  substation-site register), PLP-GEN-REG-0006 (climate hazard and adaptation register).
- Standards registered: STD-133 ISO 22476-3:2005, STD-134 EN 1997-2:2024, STD-135 ISO 14688-1:2017,
  STD-136 ISO 46001:2019 (with STD-076, STD-083, STD-108).
- Findings caught by reading outputs against physics or other chapters:
  * the wadi "bed" was read on the ch 14 wadi line, which sits on a bank: the channel invert is up
    to 175 m beside it; the substation is +1.8 m above the channel bed, not -3.8 m (channel_invert);
  * a grade line smoothed over 450 m crossed the wadi on 4.2 m of fill (a dam): fill capped at the
    culvert crest;
  * wash water must follow ch 10 (1.0 L per module = 109.2 m3 a wash, 14 washes on the 4 % trigger),
    not 0.5 L/m2 and 11 washes;
  * the Gumbel CSV held NaN (reduced variate transformed twice);
  * the corridor register listed a wadi and a public-road crossing the computed route does not make.
