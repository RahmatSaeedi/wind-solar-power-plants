"""Synthetic operating records for chapter 51: the first operating year of
Plant P, run by a fictional operator under a fictional O&M contract.

ROSTER         roles by shift (A-522)
HANDOVER       one shift handover's checklist
LOG_WEEK       entries per hour in a week of operating logs
PERMITS_OP     permits to work in operation, by month (A-523)
EVENTS         reportable events and when they were reported
PROCEDURES     operating procedures and their review dates
LIMIT_EVENTS   operating-limit exceedances (1-minute data)
SETTLE         monthly metered, scheduled and validated energy (A-524)
AUX_OP         station battery and diesel records
FIRE_TESTS     fire-system inspection and test schedule (A-525)
WATER_MONTHS   metered water against ch 29's model (A-526)
LINE_PATROL    export line patrol and vegetation records (A-527)
OUTAGE_REQ     outage requests to the network owner
COMMIT         commitments register in operation (A-528)
TAG_CHANGES    SCADA tags against the asset register after changes (A-529)
WORK_ORDERS    work orders and their asset IDs
EXERCISES      emergency exercises and incidents (A-529)
Teaching values only; people, places and companies are fictional.
"""
from __future__ import annotations

from datetime import date

from companion.ch51 import common  # noqa: F401  (puts plantp on the path)

TODAY = date(2029, 6, 1)          # end of the first operating year

# ------------------------------------------------ A. organisation
ROSTER = {   # role: people qualified for it, by shift (4 shifts, 12 h)
    "control-room operator": {"A": 2, "B": 2, "C": 1, "D": 2},
    "shift lead": {"A": 1, "B": 1, "C": 1, "D": 1},
    "authorised person (HV)": {"A": 1, "B": 2, "C": 0, "D": 1},
    "first aider": {"A": 2, "B": 1, "C": 1, "D": 0},
}
NEED = {"control-room operator": 2, "shift lead": 1, "authorised person (HV)": 1,
        "first aider": 1}
HANDOVER = {"plant state and limits": True, "battery SOC and plan": True,
            "open permits and isolations": True, "active alarms and their owners": False,
            "grid operator instructions in force": True, "forecast version in use": False,
            "weather warnings": True, "people on site": True}
LOG_WEEK = [3, 2, 1, 1, 0, 1, 2, 4, 3, 2, 2, 3, 2, 1, 2, 3, 2, 2, 1, 0, 0, 1, 1, 2] * 7
DA_DEADLINE_H = 10                # day-ahead schedule due 10:00 (teaching)
FORECAST_READY_H = [8.5, 8.6, 9.8, 8.4, 10.4, 8.7, 8.5]    # a week, hours of day

# ------------------------------------------------ C. assurance
PERMITS_OP = {   # month: (issued, overran, isolation conflicts)
    1: (42, 2, 0), 2: (38, 1, 0), 3: (55, 6, 1), 4: (61, 4, 0), 5: (47, 3, 2), 6: (40, 1, 0),
}
EVENTS = [   # event, occurred day, reported day, class
    ("feeder WS2 trip", 12, 12, "grid"), ("inverter fire alarm (false)", 40, 41, "fire"),
    ("worker slipped on the PV access track", 77, 81, "safety"),
    ("oil leak at T5 base", 103, 103, "environment"), ("SCADA link lost 3 h", 150, 152, "OT"),
    ("near miss: crane boom near the 33 kV line", 201, 206, "safety"),
]
REPORT_DAYS = 1
PROCEDURES = {   # procedure: last review
    "OP-01 normal operation": date(2028, 9, 1), "OP-02 export restriction": date(2028, 9, 1),
    "OP-03 loss of SCADA": date(2027, 11, 1), "OP-04 battery limits": date(2028, 9, 1),
    "OP-05 restoration after a blackout": date(2027, 6, 1),
    "OP-06 fire alarm response": date(2029, 2, 1)}
REVIEW_DAYS = 365

# ------------------------------------------------ E. commercial
SETTLE = {   # month: (scheduled MWh, metered MWh, intervals missing in the meter data)
    1: (21_400, 20_950, 0), 2: (22_800, 23_310, 12), 3: (27_100, 26_420, 0),
    4: (24_000, 22_900, 4), 5: (30_200, 30_850, 0), 6: (19_800, 19_100, 30),
}

# ------------------------------------------------ F, G, H, K
AUX_OP = dict(battery_kwh=110 * 400 / 1000 * 1.0, load_kw=4.6,
              diesel_runs=[(18, 2.5), (77, 0.6), (150, 6.0), (212, 1.2)],
              fuel_l_h=24.0, tank_l=1200.0)
FIRE_TESTS = {   # system: (interval days, last done day, today day)
    "detection loops": (90, 120, 365), "control-room gas extinguishing": (180, 210, 365),
    "fire pumps (weekly run)": (7, 361, 365), "hydrants": (365, 30, 365),
    "battery container detection": (90, 250, 365), "emergency lighting": (30, 300, 365),
}
WATER_MONTHS = {   # month: (metered m3, modelled m3)
    1: (190, 180), 2: (205, 180), 3: (360, 330), 4: (420, 330), 5: (380, 360), 6: (395, 360),
}
LINE_PATROL = {   # span group: (last patrol day, vegetation found m to conductor)
    "T01-T04": (300, 7.5), "T05-T08": (120, 4.2), "T09-T12": (330, 6.8),
    "T13-T18": (90, 3.1), "T19-T24": (310, 8.0)}
PATROL_DAYS = 180
CLEARANCE_M = 5.0                 # teaching minimum vegetation clearance
OUTAGE_REQ = [   # work, requested day, needed day, notice needed days
    ("bay E1 relay test", 30, 60, 20), ("line T05-T08 vegetation", 140, 150, 20),
    ("T1 tap-changer service", 200, 260, 45), ("CT replacement at the POC", 280, 300, 45),
]

# ------------------------------------------------ L, M, N
COMMIT = {   # commitment: (status, due day, done day or None)
    "grievance line open 24/7": ("ongoing", None, None),
    "herders' track kept open": ("ongoing", None, None),
    "local hiring 40 % of O&M staff": ("due", 365, None),
    "dust monitoring report to the village": ("due", 180, 175),
    "school road safety briefing": ("due", 90, 140),
    "restoration of the laydown area": ("due", 300, None),
}
OM_STAFF = (46, 15)               # O&M staff, of whom local
TAG_CHANGES = {   # tag in SCADA: in the asset register?
    "=PVF1-3-INV1": True, "=PVF1-3-INV1-PS3": False, "=WS2-Q1": True, "=T05-CONV": True,
    "=T05-CONV-NEW": False, "=BESS-A-PCS2": True, "=SUB-RTU-2": False}
WORK_ORDERS = [   # work order, asset ID, failure code, closed with test record
    ("WO-1021", "=T05-CONV", "F-ELEC", True), ("WO-1022", "", "F-MECH", True),
    ("WO-1023", "=PVF1-3-CB07", "", False), ("WO-1024", "=WS2-Q1", "F-PROT", True),
    ("WO-1025", "", "", False), ("WO-1026", "=BESS-A-PCS2", "F-ELEC", True),
    ("WO-1027", "=PVF2-1-INV1", "F-COOL", False), ("WO-1028", "=T09-PITCH", "F-HYD", True)]
EXERCISES = {   # exercise: (required a year, done)
    "fire evacuation": (2, 2), "rescue from a nacelle": (2, 1), "casualty at night": (1, 0),
    "loss of SCADA (with the OT team)": (1, 1), "responders' site visit": (1, 1)}
INCIDENTS = {1: (0, 3), 2: (1, 2), 3: (0, 4), 4: (0, 1), 5: (1, 5), 6: (0, 6)}   # (incidents, near misses)
