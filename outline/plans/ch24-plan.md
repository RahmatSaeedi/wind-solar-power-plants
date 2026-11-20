# Chapter 24 plan: Cables, switchgear and electrical installation (budget 105 pp; core chapter)

Handoff: 9 bullets + worked examples (preliminary cable by current, drop, installation and fault duty;
switchboard one-line mapped to compartments and FAT/SAT evidence); blueprint A-F; audit row 24 (theory:
cable, OHL and switchgear electrical/thermal behaviour; applied: main, auxiliary, collector or export
constraints; design: circuit type, conductor, protection, route, installation interfaces; calculation:
ampacity inputs, drop, losses, thermal and fault duty; manufacturing: cable/line hardware and
switchgear production, tolerances, tests, installation QA; implementation: circuit basis, procurement
schedule, route/install QA, acceptance records).

Safeguards: laying, jointing, voltage tests and switching only within approved training and maker's
instructions (named by purpose and evidence); OHL final design by qualified engineers and approved
standards; no universal OHL/cable choice; teaching values for cables, factors, gear and conductor.

## Companion
- plantp/cables.py (new): r_at, rating (factors), drop_pct, loss_kw, annual_loss_mwh, adiabatic_mm2,
  withstand_ka, peak_ka, short_time_ok, charging_a, sheath_v, conductor_temp, economic_section,
  sag_m. Tests test_ch24_cables.py (5).
- companion/ch24: sources (33 kV Al XLPE 240/400/630, factors, LV Cu table, teaching OHL conductor,
  gear ratings), examples_a (temps, ratings, losses from ch 15 hourly wind, fault, select = worked
  example 1), examples_b (layers, pulling with capstan, drums, gear duties, busbar force),
  lab_d (schedule check with 3 planted errors, switchboard panels = worked example 2, ITP),
  examples_e (LV schedule from ch 23 loads, DC trip coil, segregation), examples_f (graded string
  economics, sheath bonding, charging, sag, OHL vs cable), examples_g (PV string DC cable and fuse,
  IP code, factory eccentricity and resistance, interlock truth table, contact resistance),
  integrated, worked, figdata.

## Expansion after the first draft (2026-11-16)

First render: 47 of 105 pages (a leading "+" in an LTR span also broke the render until
theme/ltr.lua put an empty group in front). Nine rounds of computed lessons brought it to 105:
examples_h (thermal circuit and factors, cyclic, skin, dielectric, overload, DTS), examples_k
(busbar, DC at separation, internal arc, SF6, contact wear), examples_m (loop impedance, motor
start, battery cable, string options with losses, line rating, creepage, duct), examples_p
(stranding, eccentricity and Cpk, drums, test families), examples_q (fuses, UPS, generator, DC
isolator, AIS/GIS, hot sag, wind, OPGW, route, repair), examples_s (bonding, back-flashover,
overload class, mechanism, terminals, joints, hold log), examples_t (trefoil, ageing, inverter
link, ventilation, tray, neutral), examples_u (SF6 density, chopping, capacitive switching, drum
allocation, earth bar), examples_v (soil survey, cross-country, PV cable), examples_w (heater,
torque, thermography, markers, forms), examples_x (corona), examples_y (reflection, depth),
examples_z (sun); 20 new section files; 211 exercises; 13 new figures.
Findings fed back: the 132 kV line limits export on hot still days; screens and the feeder relay
are checked together; incomers 1,600 A (ch 26); D-028's basis output lists the additions.
