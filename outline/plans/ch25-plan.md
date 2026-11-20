# Chapter 25 plan: Transformers and substations (budget 115 pp; core chapter)

Handoff: 11 bullets (transformer theory and specification, design sequence and parts, loading and
losses, factory route and quality gates, routine/type/special tests, transport and installation,
monitoring and the test dossier, station service, fire and sound interfaces, bus arrangements and
the export bay); blueprint A-G; audit row 25 (theory: electromagnetic, thermal, substation and fire
scenarios; applied: main/station-service and export-terminal cases; design: transformer,
export-bay, metering, protection, ownership interface basis; calculation: ratio/loss/loading/
auxiliary checks; manufacturing: core/winding/tank and substation process controls and factory
tests; implementation: specification, interface/fire review, test dossier, commissioning).

Safeguards: factory drying, vacuum, oil filling, high-voltage tests, energising and switching are
named by purpose and evidence only (maker's equipment, procedures and qualified staff); no universal
fire-system or oil-containment prescription (fire design and authority decide); seismic values,
insulation levels and clearances come from the site studies and the standards' own figures;
commercial terms are sketches, not legal advice; all values teaching assumptions (A-326..A-330).

## Companion
- plantp/transformer.py: volts_per_turn, turns, conductor_mm2, from_tests, regulation_pct,
  efficiency, loss_cost, ab_factors, hot_spot, ageing_rate, share, sc_current_ka, force_ratio,
  sound_sum, sound_at, bund_m3. Tests test_ch25_transformer.py (6).
- companion/ch25: sources (MAIN 63 MVA 132/33 kV YNd11 ONAN/ONAF 50/63, uk 12 %, P0 35, Pk 250,
  taps +/-10 % by 1.25, oil 22 m3, 95 t / 72 t; BIDS A and B; UNIT; DOSSIER; BUS), examples_a
  (Faraday, circuit, vector, taps, parallel, fault and inrush), examples_b (bids with A 6.84 and
  B 0.88, thermal year, cooling, design), examples_c (dossier = worked example, penalty, transport,
  containment, sound, buses, bays), examples_d (core, route, gates, oil vs dry), integrated
  (by hand, bid record, basis D-029), worked (E-lines, P01-P24; solutions2 P25-P62 check every
  short answer added later).

## Expansion after the first draft (2026-11-16)

Twelve rounds of computed lessons brought the chapter to 115 pages (54 section files, 206
exercises, 20 figures): examples_h (inrush, over-excitation, harmonics, impulse, forces,
impedance, eddy), examples_k (hot day, dynamic model, moisture, key gas, DGA, OLTC, expansion,
radiators, night, spare), examples_n (sizing, correlation, trace, FRA, impact, earthing unit, I/O
list, take-off, footprint, energising, bushings), examples_p (impedance choice, HV neutral, tap
range, transport mass, oil tests, ester, heat flux, drain, control cables, trip matrix),
examples_s (circulating current, PV unit with Q, tower air, loss-measurement uncertainty, heat
run fit, amorphous, units at night), examples_t (second dossier, N-1, H factor, reactive, staging,
site noise), examples_u (copper, drying, vacuum, metering, spares, annual loss budget), examples_v
(three-winding star, harmonic cancellation, off-circuit tap corners, furans/DP, health index,
repair or replace, carbon), examples_w (residual cooling alarm, payment milestones, energising
dip, seismic, tubular busbar), examples_x (night reactive balance, life cost, nacelle vs tower
base, series statistics, shipping gas pressure), examples_y (altitude, room for the battery,
battery cycle, load noise, arc energy), examples_z (loss at reference temperature, impedance by
tap, breather, failure risk vs pool fee, sun on the tank); integrated example: technical schedule
of the PV unit transformer (tbl-ch25-pvschedule).

Findings fed back: the PV unit transformer is 1 % short for full Q at full power (5.6 MVA or a
written Q limit); no fixed tap covers all four operating corners once the 33 kV bus band is added;
switching the PV units off at night doubles the night Mvar export; the 26 unit transformers lose
3.3 times as much energy as the two main units (A and B set per group); the battery adds about
320 kW of HVAC, more than the 250 kVA station transformer (S1 needs its own auxiliary supply); the
site noise lesson now uses chapter 19's eight containers.
