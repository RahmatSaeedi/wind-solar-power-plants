# Chapter 49 plan: construction and installation (budget 60 pp, plan for ~70)

Handoff: 10 bullets (mobilisation to mechanical completion; site assembly vs factory manufacture,
receipt preservation and inspection, tolerances, torque/connection records, cable routing and
terminations, earthing continuity, protection from construction damage; social and labour plans
in construction; systemization and turnover packages; asset-data capture at receipt,
installation, test and turnover; collector/export substation and line construction; auxiliary
systems; fire-system construction QA; construction water; worked example: sequenced work plan for
one PV block with prerequisites and inspection records). Blueprint A-L (A readiness, B workface,
C quality and systemization, D work-package lab, E project controls, F auxiliary systems,
G fire-system QA, H construction water, I collector/export construction, J social-plan
implementation, K asset-data capture, L emergency and site-security readiness). Audit row 49.

Running products: PV block =PVF1-3 (ch 10 D-013: 21 combiners x 20 strings x 26 modules =
10,920 modules; tracker rows; one PV station skid of ch 40 with the 5.6 MVA unit transformer of
ch 39); turbine T05 foundation and erection (ch 30/31/47); the 33 kV collector WS1 and the
132 kV line (ch 24); the substation building's station service (ch 23); fire systems (ch 32);
construction water (ch 29: 87,460 m3, wells 30,300 m3); workforce (ch 22: peak 450, 4,534
worker-months over 18 months); social commitments (ch 33); a fictional EPC contractor with
fictional subcontractors.

Overlap rule: ch 22 has the development CPM, ch 29 the water balance and roads, ch 31 the
logistics and weather windows, ch 32 permits to work, JHA and emergency planning, ch 33 the
social plans and grievance workflow, ch 38 the MDR and earned value, ch 40 traveler and ITP,
ch 46/47 the factory and fabrication records. Ch 49 goes to the site: work packages and their
prerequisites, resource-levelled sequencing, hold points on site, installation records (torque,
continuity, terminations, as-laid), systemization and completion, project controls (look-ahead,
productivity, weather, recovery), the auxiliary, fire, water, export and social threads as
construction records, asset data captured and reconciled, and readiness checks before work.

Safeguards: no live-work procedures; no process recipes (torque values come from the maker's
instructions, concrete from the approved mix - the book checks records); no universal fire
prescriptions (layouts from the approved design); no tactical security detail; social
commitments only as approved and funded; teaching values only.

## Sections (files)
- `_49-a-readiness.qmd` A readiness, L emergency/security readiness (sections «الف», «ل»).
- `_49-b-workface.qmd` B workface execution.
- `_49-c-quality.qmd` C quality and systemization, K asset data.
- `_49-d-lab.qmd` D work-package lab (worked example).
- `_49-e-controls.qmd` E project controls.
- `_49-f-systems.qmd` F auxiliary systems, G fire QA, H water, I collector/export, J social.
- `_49-y-plantp.qmd`, `_49-z-assessment.qmd`.

## Companion
Module `plantp/construction.py` (serial schedule with crew limits, hold points, look-ahead
constraints, productivity, rules-of-credit progress, completion by subsystem, record checks);
chapter scripts `companion/ch49/`; tests `test_ch49_construction.py` (pure helpers only).

## Ledgers
D-053 construction and installation basis; assumptions A-506 onwards; unknown U-130
(contractor's method statements, permits and approved plans).
