# Chapter 48 plan: instrumentation, metering, control-panel and plant-network hardware manufacture (budget 75 pp, plan for ~85)

Handoff: 6 bullets (measurement theory and product architecture; design and assembly; factory
process and quality; network-system physical build - defensive administration only; integration
and acceptance; worked examples and code - tag database validated for ranges/units, as-designed
vs as-built port/connection schedules, physical/logical network diagrams and a sensor-to-
historian data-flow model). Blueprint A-D (A measurement/control hardware; B panel and network
production; C configuration and test; D data/diagram lab). Audit row 48.

Running products: the met-station and turbine sensors of ch 12/13/34 (pyranometers, reference
cells, anemometers, vanes, Pt100s), the POC revenue meters and transducers of ch 34, the PLC/RTU
and I/O cabinets of ch 34, the SCADA rings, switches, gateways and time source of ch 35/36; a
fictional instrument maker, a fictional cabinet builder and a fictional network integrator.

Overlap rule: ch 34 has 4-20 mA scaling, loop length, ADC step, RSS, Pt100, lead error, clock
drift, calibration intervals, I/O list checker, panel heat, as-found/as-left, CT burden; ch 35
has fibre budget, sync budget, topology, ring recovery, point-list checks, int16 scaling,
register maps, failover timing; ch 36 has zones, rules, inventory, backups; ch 46 has panel
wiring, point-to-point, terminal plans, markers, fingerprints. Ch 48 goes to the hardware and
its records: a datasheet turned into a site error budget, calibration certificates read
(traceability, uncertainty, conformity statement), revenue-meter chain class and site tests as
records, enclosure IP and temperature derating, EMC as a test record, cabinet grounding and
shield earthing, port schedules and patch panels, fibre link test records against the budget,
copper certification records, dual power feeds, firmware/config baselines and backups, protocol
maps against the tag database, time offsets across devices, failover test records, a tag
database validator (ranges, units, limits order, deadbands), planned vs actual port schedules,
three views (physical, logical, sensor-to-historian).

Safeguards: defensive network administration only (no scanning, exploitation or evasion), no
live-work procedures, teaching values only.

## Sections (files)
- `_48-a-hardware.qmd` A. measurement and control hardware.
- `_48-b-production.qmd` B. panel and network production.
- `_48-c-config.qmd` C. configuration and test.
- `_48-d-lab.qmd` D. data and diagram lab.
- `_48-y-plantp.qmd`, `_48-z-assessment.qmd`.

## Companion
Module `plantp/hwmfg.py`; chapter scripts `companion/ch48/`; tests `test_ch48_hwmfg.py`.

## Ledgers
D-052 instrumentation, metering, panel and network hardware basis; assumptions from A-498;
unknown U-129 (makers' calibration and type-test records, integrator's as-built network files).
