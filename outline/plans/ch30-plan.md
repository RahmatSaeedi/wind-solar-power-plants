# Chapter 30 plan: Structures, turbine foundations and mechanical loads (budget 95 pp; core chapter)

Handoff: 7 bullets + worked examples (compare conceptual foundation schemes under alternative soil
assumptions; fabrication traveler and inspection plan for a tower section with checks that need
qualified structural engineers and inspectors); blueprint A-E; audit row 30 (structural mechanics,
fatigue and line/substation structures; compare foundation, support and line-structure concepts;
load paths, materials, clearances and verification basis; illustrative loads/stress/deflection with
limits; trace steel/concrete/tower/gantry fabrication, welding, coatings and QA; checked design-review
package and erection/inspection evidence).

Forward references to honour: ch 4 v_foundation (overturning, B/6, buoyancy -> "geotechnical and
structural check (chapter 30)"), ch 4 a_tower/t_tower (soft-stiff, drag), ch 11 k_tower (local
buckling, weld/flange fatigue, door opening are "the real sizing checks (chapter 30)"), ch 11
k_flange (flatness, preload), ch 11 c_tower (sections, welds, coating), ch 29 (ground model, T07 soft
clay, T12 gypsum, groundwater range, Q1-Q10), ch 24 (line sag, wind on conductors), ch 25 (IF-009
transformer foundation 95 t), ch 10 (2P x 26 tables, D-013).

Safeguards: teaching loads and factors only, never a design; no code clause or partial factor quoted
as a requirement (the project's codes and the type certificate govern); independent verification and
licensed structural engineers decide; weld/NDT by qualified inspectors; lifting by competent persons
(ch 31); fictional site.

## Data (A-356..A-362)
Turbine loads from ch 11 (thrust 923 kN, top mass, tower sections), extreme and fatigue teaching
loads; site wind and seismic teaching spectrum; ch 29 soils (dense sand, T07 soft clay, groundwater
range); PV table geometry (ch 10); line/gantry geometry (ch 24, 28); transformer 95 t (ch 25).

## Companion
- plantp/structures.py (new): wind_profile, dynamic_pressure, peak_speed, drag_force,
  vortex_speed, shell_buckling, sn_life (bilinear detail category), effective_area_circle,
  foundation_pressure, rotational_stiffness, frequency_with_foundation (Dunkerley), pile_uplift,
  broms_lateral, zinc_life, thermal_expansion, base_shear, bolt_slip, rebar_area.
- companion/ch30: sources, examples_a (load paths, wind, gust, seismic, snow, thermal, construction
  loads, combinations), examples_b (fatigue, resonance and foundation stiffness, buckling, deflection),
  examples_c (PV tables and piles, corrosion, purlins, bolts, welds), lab_d (foundation schemes under
  alternative soils = worked example 1), lab_e (fabrication traveler and inspection plan = worked
  example 2), examples_f (line towers, gantries, equipment supports, clearances), examples_g..
  (expansion), integrated (D-034), worked.

## Sections (about 50 lessons, 140+ problems, 16+ figures)
A loads and structural response; B structural products and materials; C manufacture and field
erection; D engineering review exercise; E line and substation structures; K manufacturing (ch 41-48
interfaces); Y Plant P (D-034).
