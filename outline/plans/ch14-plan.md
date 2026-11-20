# Chapter 14 plan: Site screening and wind-farm micro-siting (budget 80 pp; aim 100+)

Handoff: chapter 14 bullets (5) + worked example (compare two preliminary layouts using energy,
collection-cable length, access and environmental constraints); blueprint A-F; audit row 14
(theory: terrain, land tenure, wakes, shading, spatial, water, social, export-corridor constraints;
applied: compare site/layout and corridor alternatives with affected-use evidence; design:
preliminary wind/PV layout, access, water, export route, early consultation interfaces;
calculation: wake, spacing, shading, route, water and screening impacts where data support it;
manufacturing: N/A for factory manufacture, constructability and fabrication interfaces;
implementation: georeferenced layout, corridor options, land/user map, constraint register).

Safeguards: no invented country requirements (setbacks, noise limits, aviation rules are
"verify with the authority", chapters 55-57); noise and flicker as physics and teaching limits
labelled as such; land and social screening treated as participatory evidence, not cadastral
only; no tactical security detail; ecology as screening with specialist surveys.

## Built on
- ch 3 (geometry, GIS-like coordinates?), ch 5 (data), ch 10 (PV rows, GCR, shading, backtracking),
  ch 11 (Jensen wakes, layouts A/B/C, D-015, noise propagation, sum_levels), ch 12 (horizon,
  sun path), ch 13 (wind rose, spatial representativeness U-049, effective turbulence, hub study).

## Companion
- plantp/siting.py (new): a synthetic site grid (terrain height, slope, roughness classes,
  land-use and tenure polygons, water sources, dwellings, roads, ecology buffers), raster
  helpers (slope, aspect), point-in-polygon, buffer/setback masks, a simple linearised flow
  speed-up over a hill (teaching), Jensen farm energy reuse, Park/Frandsen effective turbulence
  (teaching form), shadow-flicker geometric hours (astronomical worst case and expected with
  sunshine/wind direction), noise at dwellings (ch 11 propagation), cable length by minimum
  spanning tree and by radial strings, road length and slope check, cut/fill volume estimate,
  PV block fit on usable land with row spacing, corridor least-cost path on a cost raster
  (Dijkstra), constraint register objects.
- companion/ch14: sources (synthetic site, seeded), examples_a (constraints and layers),
  examples_b (wind/PV layout principles), examples_c (buildability and impact: roads, cranes,
  drainage, noise, flicker, aviation, ecology), lab_d (two layouts compared: energy, cable,
  access, impacts, water, fatal flaws), examples_e (corridors: least-cost routes and
  alternatives), examples_f (land and social screening: users map, livelihood exposure,
  consultation plan), integrated, worked, solutions.

## Structure (labels)
A sec-ch14-a: a-why, a-layers (geospatial data, CRS, resolution), a-terrain (slope, ruggedness,
  flow), a-roughness, a-obstacles, a-land (rights, tenure), a-setbacks, a-water, a-grid,
  a-surveys, a-resolution.
B sec-ch14-b: b-wakes, b-spacing, b-effective-ti, b-pv-rows, b-shading, b-blocks, b-trackers,
  b-cables, b-shared.
C sec-ch14-c: c-roads, c-cranes, c-slope-drainage, c-grading, c-noise, c-flicker, c-aviation,
  c-ecology, c-community, c-permits.
D sec-ch14-d: d-alternatives, d-compare (worked example), d-fatal, d-log.
E sec-ch14-e: e-substation, e-corridors, e-crossings, e-route-uncertainty, e-alternatives.
F sec-ch14-f: f-users, f-livelihood, f-vulnerable, f-heritage, f-displacement, f-consultation.
Y: plantp (int-1 site constraints map, int-2 two layouts with wind+PV, int-3 corridor and
  constraint register), design, lab, mfg (N/A + constructability interfaces), std, deliverable.
Z: summary, vocab, assess (~140), solutions, examples-out.

## Numbering
Assumptions from A-259; unknowns from U-050; decision D-018 (preliminary layout and corridor);
documents PLP-GEN-DWG-0003 (georeferenced layout), PLP-GEN-REG-0003 (constraint register),
PLP-GEN-REP-0006 (site screening report). Check the register for free numbers first.
