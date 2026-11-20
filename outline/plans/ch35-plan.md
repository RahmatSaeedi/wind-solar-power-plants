# Chapter 35 plan: SCADA and communications (budget 95 pp, plan for ~105)

Handoff: 9 bullets (network fundamentals; protocols and interoperability; SCADA architecture;
diagram types; data and operations; operational/asset data boundary with CMMS/EAM; fire-alarm/SCADA
boundary; software implementation lab with synthetic data only; acceptance), blueprint A-F, audit
row 35 (diagnose synthetic telemetry/asset-ID mismatch; design governed real-time and CMMS/EAM flows;
calculate sampling, bandwidth, latency, quality, retention; link hardware build/test to ch 48 and
control software/configuration; deliver tested synthetic interfaces and a source-of-truth map
without bypassing life-safety systems).

Overlaps to respect: ch 34 (time stamps, quality, historian deadband, watchdog, telemetry budget,
fire interface from the control side), ch 20 (comms hold and fallback), ch 5 (data handling,
schemas), ch 23 (one-line, metering), STD-092/093 (IEC 60870-5-104, IEC 61850). Chapter 35 adds the
network and data view: media, addressing, bandwidth, latency, redundancy, protocols as data models,
gateways, tag schemas, SCADA operations, diagrams, the asset-data boundary and acceptance.

Safeguards: defensive and benign only - the lab is a simulated producer/consumer on synthetic
data, never connected to live controls; no exploitation detail (security is ch 36); protocol names
never presented as guaranteeing interoperability; fire system authority stays with the fire panel.

## Data (A-393..A-400)
ch 34 I/O list and points, ch 23 one-line, ch 14 site distances (fibre lengths), ch 19 BESS
containers, ch 11 turbines; teaching link rates, latencies, packet sizes, MTBF/MTTR, tag counts,
asset register extract with planted mismatches.

## Companion
- plantp/scada.py (new): serialisation delay, link utilisation, polling cycle, report-by-
  exception load, ring/star availability, fibre loss budget, time-sync error budget, tag-name
  validator, scaling check, staleness detector, alarm rule engine (benign), retention sizing.
- companion/ch35: sources, examples_a (networks), b (data and interoperability), c (operations),
  lab_d (synthetic telemetry producer/consumer, schema, logger, alarms, diagnosis), e (fire
  boundary), f (asset-data boundary, CMMS/EAM IDs), k (manufacturing/config), integrated (D-039),
  worked.

## Sections (~60 lessons, 140+ problems, 18+ figures)
A networks; B data and interoperability; C operations and design (diagram types, HMI, historian,
alarms, access, retention, loss of comms, FAT/SAT); D synthetic-data lab; E fire-alarm boundary;
F operational/asset-data boundary; K manufacturing/config; Y Plant P (D-039); Z assessment.
