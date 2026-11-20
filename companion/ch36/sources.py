"""Chapter 36 - synthetic security data of Plant P (teaching values A-401 to
A-408). Everything is invented for teaching: no real addresses, products,
vulnerabilities or site details. Faults are planted so the review tools
have something to find; nothing here connects to any network.
"""
from __future__ import annotations

from companion.ch36 import common  # noqa: F401  (puts plantp on the path)

# Zones of the ch 35 logical diagram (A-401); target levels are teaching
# labels of the security-level concept (STD-158), not an assessment.
ZONES = {
    "field-ied": dict(devices=30, target="high", function="protection and measurement"),
    "field-wtg": dict(devices=24, target="high", function="turbine control"),
    "field-pv": dict(devices=40, target="medium", function="inverters"),
    "field-bes": dict(devices=24, target="high", function="battery control"),
    "control": dict(devices=12, target="high", function="SCADA servers, HMIs, PPC"),
    "dmz": dict(devices=3, target="medium", function="historian copy, patch store, jump host"),
    "business": dict(devices=200, target="low", function="office, CMMS, reports"),
    "remote": dict(devices=0, target="low", function="vendors and grid operator outside"),
}

# [start: conduits]
_C = [  # src zone, dst zone, service, business purpose (A-401)
    ("field-ied", "control", "telecontrol", "measurements, events"),
    ("field-wtg", "control", "turbine-data", "turbine data"),
    ("field-pv", "control", "inverter-data", "inverter data"),
    ("field-bes", "control", "battery-data", "battery data"),
    ("control", "dmz", "historian-copy", "one-way copy"),
    ("business", "dmz", "historian-read", "reports"),
    ("remote", "dmz", "remote-session", "vendor support"),
    ("dmz", "control", "jump-session", "supervised support")]
CONDUITS = [dict(src=a, dst=b, service=s, purpose=p) for a, b, s, p in _C]
# [end: conduits]

FLOW_LOG = [  # flows seen in a synthetic week: src, dst, service, count
    ("field-ied", "control", "telecontrol", 2_400_000),
    ("field-wtg", "control", "turbine-data", 7_200_000),
    ("field-pv", "control", "inverter-data", 6_500_000),
    ("field-bes", "control", "battery-data", 9_600_000),
    ("control", "dmz", "historian-copy", 600_000),
    ("business", "dmz", "historian-read", 4_200),
    ("remote", "dmz", "remote-session", 6),
    ("dmz", "control", "jump-session", 6),
    ("business", "control", "file-share", 14),          # planted: not in the conduits
    ("field-pv", "business", "cloud-telemetry", 50_400),  # planted: inverter to a cloud
]

RULES = [  # first-match firewall rules between zones (A-402), planted faults
    dict(id="R01", src="control", dst="dmz", service="historian-copy", action="allow",
         hits=600_000, purpose="one-way historian copy"),
    dict(id="R02", src="business", dst="dmz", service="historian-read", action="allow",
         hits=4_200, purpose="reports"),
    dict(id="R03", src="remote", dst="dmz", service="remote-session", action="allow",
         hits=6, purpose="vendor support, on request"),
    dict(id="R04", src="dmz", dst="control", service="jump-session", action="allow",
         hits=6, purpose="supervised support"),
    dict(id="R05", src="any", dst="any", service="any", action="allow",
         hits=50_414, purpose=""),                                   # planted: any-any
    dict(id="R06", src="business", dst="control", service="file-share", action="allow",
         hits=14, purpose="temporary, 2025 commissioning"),          # planted: shadowed
    dict(id="R07", src="remote", dst="control", service="remote-session", action="allow",
         hits=0, purpose="old vendor path"),                         # planted: shadowed, unused
    dict(id="R08", src="any", dst="any", service="any", action="deny",
         hits=0, purpose="default deny"),                            # shadowed by R05
]

ROLES = {  # rights allowed for each role (ch 35 lesson C)
    "viewer": {"view"},
    "operator": {"view", "ack", "operate"},
    "maintenance": {"view", "ack", "operate"},
    "control engineer": {"view", "ack", "operate", "settings", "software"},
    "vendor": {"view"},
}
USERS = {  # user: (role, rights held) - planted excess rights (A-403)
    "op-1": ("operator", {"view", "ack", "operate"}),
    "op-2": ("operator", {"view", "ack", "operate", "settings"}),
    "mnt-1": ("maintenance", {"view", "ack", "operate"}),
    "eng-1": ("control engineer", {"view", "ack", "operate", "settings", "software"}),
    "ven-1": ("vendor", {"view", "software"}),
    "shared-hmi": ("operator", {"view", "ack", "operate"}),
}
LAST_USE_DAYS = {"op-1": 1, "op-2": 3, "mnt-1": 12, "eng-1": 40, "ven-1": 210,
                 "shared-hmi": 0}

INVENTORY = [  # synthetic asset inventory rows (A-404), planted gaps
    dict(tag="FW-1", kind="firewall", zone="dmz", owner="OT lead", firmware="7.2", support_end=2031),
    dict(tag="FW-2", kind="firewall", zone="dmz", owner="OT lead", firmware="7.2", support_end=2031),
    dict(tag="SW-R01", kind="ring switch", zone="field-wtg", owner="control eng", firmware="4.2.1",
         support_end=2030),
    dict(tag="SW-R02", kind="ring switch", zone="field-wtg", owner="", firmware="4.1.9",
         support_end=2030),
    dict(tag="SRV-1", kind="SCADA server", zone="control", owner="control eng", firmware="",
         support_end=2029),
    dict(tag="SRV-2", kind="SCADA server", zone="control", owner="control eng", firmware="3.4",
         support_end=2029),
    dict(tag="HIS-1", kind="historian", zone="control", owner="control eng", firmware="5.0",
         support_end=None),
    dict(tag="PPC-A", kind="plant controller", zone="control", owner="control eng",
         firmware="2.8", support_end=2035),
    dict(tag="GPS-1", kind="time server", zone="control", owner="", firmware="1.3",
         support_end=2028),
    dict(tag="JMP-1", kind="jump host", zone="dmz", owner="OT lead", firmware="2024.1",
         support_end=2027),
]

RECOVERY = {  # restore steps of each system, hours (A-405, teaching)
    "plant controller": dict(detect=0.5, spare=0.5, load_config=0.5, verify=2.0, target=4.0),
    "SCADA server": dict(detect=0.2, spare=1.0, load_config=1.0, restore_data=2.0, verify=2.0,
                         target=8.0),
    "historian": dict(detect=1.0, spare=4.0, load_config=1.0, restore_data=12.0, verify=4.0,
                      target=24.0),
    "protection relay settings": dict(detect=0.5, spare=2.0, load_config=0.5, verify=3.0,
                                      target=8.0),
    "firewall": dict(detect=0.2, spare=0.5, load_config=0.5, verify=1.0, target=2.0),
}

SUPPLIERS = {  # scorecards 0-5 (A-406, teaching)
    "S-A": dict(secure_dev=4, patch_support=4, notice=3, provenance=4, local_service=2),
    "S-B": dict(secure_dev=2, patch_support=3, notice=2, provenance=3, local_service=5),
    "S-C": dict(secure_dev=5, patch_support=2, notice=4, provenance=5, local_service=3),
}
SUPPLIER_WEIGHTS = dict(secure_dev=3, patch_support=3, notice=2, provenance=2, local_service=1)

# Topology of the logical diagram as a graph for single points of failure (A-407)
LINKS = [("field-ied", "SW-CORE-A"), ("field-wtg", "SW-CORE-A"), ("field-pv", "SW-CORE-A"),
         ("field-bes", "SW-CORE-A"), ("field-ied", "SW-CORE-B"), ("field-wtg", "SW-CORE-B"),
         ("SW-CORE-A", "control"), ("SW-CORE-B", "control"),
         ("control", "FW-PAIR"), ("FW-PAIR", "dmz"), ("dmz", "business")]
