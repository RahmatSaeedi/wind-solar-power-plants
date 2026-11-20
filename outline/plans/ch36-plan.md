# Chapter 36 plan: IT and industrial cybersecurity (budget 75 pp, plan for ~90)

Handoff: 8 bullets (OT vs IT priorities; network models and diagrams; segmentation, least
privilege, identity, remote access, logging, time, backups, patch/change/supplier, inventory,
incident response, continuity; coordination with physical access without replacing a site
physical-security assessment; engineering/asset-data lifecycle governance; reviewing a vendor
network design without exposing site details; software/network labs on an isolated synthetic
model; worked example of Plant P diagrams, zones/conduits, business purposes of paths, recovery
dependencies and single points of failure), blueprint A-E, audit row 36 (review synthetic topology
and information flow; design zones, access, custody, retention, backup and response with physical
interfaces; calculate recovery objectives and assess data/availability risks; secure procurement,
provenance, supplier lifecycle; deliver defensive configuration, data-lifecycle, recovery review
and tabletop record).

Overlaps to respect: ch 35 (subnets, logical diagram as a table of allowed paths, priority classes,
roles and least privilege, backups RPO, configuration baselines, asset-data boundary), ch 34
(configuration fingerprints, watchdog/fallback), ch 32 (physical security screen, emergency plan),
ch 20 (comms loss fallback), ch 5 (data handling). Chapter 36 adds the security view: risk,
zones/conduits with security levels as concepts, rule review, identity and remote access, logging
and monitoring, patching and change, supplier and provenance, data lifecycle and custody, backups
and restore tests, incident response and tabletop, continuity.

Safeguards: defensive only; no exploit, scanning-of-live-targets or evasion content; all labs on
an isolated synthetic model in one process; no tactical physical-security detail (interfaces and
escalation only); no site-sensitive details in examples; standards cited only with verified
editions (IEC 62443 parts, NIST SP 800-82, ISO/IEC 27001, IEC 62351 - verify before citing).

## Data (A-401..A-408)
Zones and conduits from the ch 35 logical diagram; synthetic asset inventory (devices, firmware,
owners) with planted gaps; synthetic firewall rule set with planted faults (any-any, shadowed,
unused, undocumented); access matrix with planted excess rights; backup/restore records;
teaching likelihood/consequence scales; recovery time/point objectives; patch cadence; supplier
list with provenance attributes; log volumes; tabletop scenario timeline.

## Companion
- plantp/ot_security.py (new): risk score and band, zone/conduit model with allowed-path check,
  rule-set review (shadowed, any-any, unused, undocumented), access-matrix least-privilege check,
  inventory completeness, patch exposure window, log volume and retention, RTO/RPO arithmetic,
  restore-test scheduling, availability with single points of failure, password/key entropy
  (defensive sizing only), supplier scorecard.
- companion/ch36: sources, examples_a (priorities, risk), b (architecture), c (resilience),
  lab_d (design review of synthetic diagrams = worked example), e (data lifecycle), k (supply
  chain), integrated (D-040), worked.

## Sections (~45 lessons, 140+ problems, 15+ figures)
A OT security foundations; B defensive architecture; C resilience and response; D defensive
design exercise (lab); E asset-data lifecycle controls; K procurement/provenance/supplier; Y
Plant P (D-040); Z assessment.
