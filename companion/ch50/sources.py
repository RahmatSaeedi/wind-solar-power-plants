"""Synthetic commissioning records for chapter 50: Plant P commissioned by
the fictional EPC contractor's test team, witnessed by the owner and, at
the point of connection, by the network operator.

AUTHORITY, REQUESTS  energisation authority and requests (A-514)
PREREQ               pre-energisation prerequisites of =PVF1-3.MV
INSTRUMENTS          test instruments and calibration dates
STRINGS, IR          string records of combiner =PVF1-3-CB07 (A-515)
RELAYS               secondary-injection results of the 33 kV feeders
STEP, CAPABILITY     plant-controller step and reactive-capability tests (A-516)
FREQ_TEST            frequency-response test points
PR_DAYS              performance-ratio test days
PUNCH50, DEVIATIONS, TRAINING, SPARES   handover records (A-517)
TRANSFER, UPS_TEST, BATT_TEST, SHED, INTERLOCKS   auxiliary chains (A-518)
CANDE, TESTED, SUPERVISORY   fire cause-and-effect and its tests (A-519)
GRID_TESTS           results against ch 28's REQ-G01..G24 (A-520)
PHASING, SHEATH, INTERTRIP   export circuit records
HANDOVER_ROWS, DOCS, FLOCS   handover data for the owner's CMMS (A-521)
ROLES, CONTACTS, DRILLS      emergency readiness records
Teaching values only; places, people and companies are fictional.
"""
from __future__ import annotations

from datetime import date

from companion.ch50 import common  # noqa: F401  (puts plantp on the path)

TODAY = date(2028, 4, 1)          # construction month 16

# ------------------------------------------------ A. governance
AUTHORITY = {   # boundary: people authorised to energise it (owner's appointments)
    "=PVF1-3.MV": {"A. Hosseini", "N. Tehrani"},
    "=PVF1-3.INV": {"A. Hosseini", "N. Tehrani"},
    "substation 33 kV bus": {"N. Tehrani"},
    "bay E1 / 132 kV line": {"network operator control"},
}
REQUESTS = [   # (boundary, requested by, authorised by, permit)
    ("=PVF1-3.MV", "test team", "A. Hosseini", "SFT-031"),
    ("=PVF1-3.INV", "test team", "R. Kamali", "SFT-032"),
    ("substation 33 kV bus", "test team", "N. Tehrani", None),
    ("bay E1 / 132 kV line", "test team", "network operator control", "SFT-001"),
]
PREREQ = {   # prerequisite of energising =PVF1-3.MV: done?
    "mechanical completion certificate": True,
    "B check sheets complete": True,
    "protection settings applied and read back": False,
    "temporary earths removed and logged": True,
    "energisation notice issued to all crews": False,
    "area barriers and signs in place": True,
    "no open fire impairment in the area": True,
    "SCADA alarms of the subsystem tested": False,
}
INSTRUMENTS = {   # instrument: calibration due
    "IR tester IT-04": date(2028, 3, 10), "IR tester IT-07": date(2028, 9, 1),
    "secondary injection set SI-2": date(2028, 6, 30), "I-V tracer IV-1": date(2028, 5, 2),
    "phase rotation meter PR-3": None, "power analyser PA-1": date(2028, 12, 1),
}

# ------------------------------------------------ B. progressive tests
STRING_COND = dict(g=820.0, t_cell=45.0, n=26)
STRINGS = {   # string of CB07: (Voc V, Isc A) measured
    "S01": (1217, 11.55), "S02": (1214, 11.60), "S03": (1172, 11.57), "S04": (1219, 11.49),
    "S05": (-1216, 11.52), "S06": (1210, 11.56), "S07": (1215, 10.52), "S08": (1218, 11.61),
    "S09": (1221, 11.58), "S10": (1213, 11.54), "S11": (1125, 11.50), "S12": (1216, 11.59),
    "S13": (1212, 11.55), "S14": (1218, 11.57), "S15": (1214, 11.60), "S16": (1219, 11.62),
    "S17": (1211, 11.53), "S18": (1217, 11.58), "S19": (1215, 11.56), "S20": (1220, 11.60),
}
IR = {f"S{k:02d}": v for k, v in enumerate([   # insulation resistance, megohm (project limit)
    120, 140, 95, 160, 110, 3.1, 150, 130, 125, 145, 90, 135, None, 150, 140, 0.8, 120,
    130, 155, 140], 1)}
IR_LIMIT = 40.0                   # teaching: from the project's test specification
RELAYS = [   # feeder relay, test current A (secondary), pickup A, TMS, measured s
    ("WS1 51", 5.0, 1.0, 0.20, 0.86), ("WS2 51", 5.0, 1.0, 0.20, 0.84),
    ("WS3 51", 5.0, 1.0, 0.25, 1.30), ("PVF1 51", 4.0, 0.8, 0.15, 0.66),
    ("PVF2 51", 4.0, 0.8, 0.15, 0.63), ("PVF3 51", 4.0, 0.8, 0.15, None),
    ("BESS-A 51", 3.0, 0.6, 0.10, 0.44),
]
STEP = dict(p0=40.0, p1=70.0, delay=0.8, tau=2.2, rise_req=6.0, settle_req=15.0,
            band=0.05)        # teaching requirement of the plant-controller step test
CAPABILITY = [   # P MW, Q required +/- Mvar, Q reached lagging, leading (POC)
    (20, 33, 34.1, -33.6), (50, 33, 33.8, -34.0), (80, 33, 33.2, -33.4),
    (100, 33, 30.6, -33.1),
]
FREQ_TEST = dict(deadband=0.2, droop_req=4.0, tol=0.5,
                 df=[0.3, 0.4, 0.5, 0.6, -0.3, -0.4, -0.5, -0.6],
                 dp=[-0.047, -0.092, -0.141, -0.185, 0.046, 0.094, 0.139, 0.187])
PR_DAYS = [   # day: (POA kWh/m2, AC energy MWh, data availability)
    (1, 7.1, 353.0, 1.00), (2, 6.8, 338.0, 1.00), (3, 3.2, 158.0, 0.99), (4, 7.3, 361.0, 1.00),
    (5, 7.2, 356.0, 0.97), (6, 6.9, 331.0, 0.82), (7, 7.0, 347.0, 1.00), (8, 7.4, 366.0, 1.00),
    (9, 7.2, 357.0, 1.00), (10, 7.1, 352.0, 1.00),
]
PR_DC_KWP = 60_000.0
PR_GUARANTEE = 0.81
PR_U = 0.020                      # expanded uncertainty of the test PR (ch 37, ch 48)

# ------------------------------------------------ C. handover
PUNCH50 = {   # week: (opened, closed)
    10: (40, 18), 11: (35, 30), 12: (22, 34), 13: (15, 38), 14: (12, 31), 15: (9, 26),
}
PUNCH_OPEN_START = 120
DEVIATIONS = [   # id, item, accepted by owner?, conditions
    ("DEV-07", "PV station heater rated 2 kW, ordered 3 kW", True, "monitor winter RH"),
    ("DEV-11", "Q at 100 MW: 30.6 Mvar lagging vs 33", None, "network operator to decide"),
    ("DEV-14", "UPS-1 autonomy 26 min vs 30", False, "battery string to be replaced"),
]
TRAINING = {   # role: (people needed, trained, assessed)
    "control-room operator": (8, 8, 6), "authorised person (HV)": (4, 3, 3),
    "PV technician": (6, 6, 6), "wind technician": (10, 7, 5), "fire warden": (6, 6, 6),
}
SPARES = {"inverter power stack": (2, 2), "string fuses": (200, 200), "RMU spares kit": (1, 0),
          "SCADA switch RS-8": (2, 2), "anemometer": (3, 1), "UPS battery string": (1, 0)}

# ------------------------------------------------ E. auxiliary chains
TRANSFER = dict(measured_s=[4.2, 3.9, 9.6, 4.1], limit_s=6.0)
UPS_TEST = dict(load_kw=6.4, measured_min=26.0, required_min=30.0)
BATT_TEST = dict(load_a=42.0, measured_h=4.6, required_h=4.0, end_v=95.0, min_v=96.0)
SHED = [("HVAC 2", 1, 1), ("lighting non-essential", 2, 2), ("workshop", 3, 4),
        ("HVAC 1", 4, 3)]                       # (load, planned step, observed step)
INTERLOCKS = {"HVAC stops on smoke in control room": "pass",
              "pump stops on low tank level": "pass",
              "battery-room fan runs on charge": "fail",
              "UPS bypass on overload": "pass", "diesel starts on loss of both feeds": None}

# ------------------------------------------------ F. fire acceptance
CANDE = {   # cause: effects it must produce (approved cause-and-effect matrix)
    "smoke, control room": {"panel alarm", "HVAC stop", "damper close", "notify control room",
                            "gas release (delayed)"},
    "smoke, cable cellar": {"panel alarm", "notify control room", "notify fire service"},
    "smoke, battery container": {"panel alarm", "container HVAC stop", "notify control room",
                                 "notify fire service"},
    "manual call point": {"panel alarm", "notify control room", "notify fire service"},
    "transformer protection trip": {"panel alarm", "notify control room"},
}
TESTED = {
    ("smoke, control room", "panel alarm"), ("smoke, control room", "HVAC stop"),
    ("smoke, control room", "notify control room"),
    ("smoke, control room", "gas release (delayed)"),
    ("smoke, cable cellar", "panel alarm"), ("smoke, cable cellar", "notify control room"),
    ("smoke, battery container", "panel alarm"),
    ("smoke, battery container", "container HVAC stop"),
    ("smoke, battery container", "notify control room"),
    ("manual call point", "panel alarm"), ("manual call point", "notify control room"),
    ("manual call point", "notify fire service"),
    ("transformer protection trip", "panel alarm"),
    ("transformer protection trip", "notify control room"),
}
SUPERVISORY = {"mains failure": "pass", "battery failure": "pass",
               "loss of the link to the control room": "fail", "detector removed": "pass",
               "loop open circuit": "pass"}

# ------------------------------------------------ G, H. grid service and export
GRID_TESTS = {   # requirement: (procedure, result: pass / fail / None = not done)
    "REQ-G01": ("CP-G01 capability", "fail"), "REQ-G02": ("CP-G02 voltage control", "pass"),
    "REQ-G03": ("CP-G02 voltage control", "pass"), "REQ-G04": ("type test + model", "pass"),
    "REQ-G05": ("type test + model", "pass"), "REQ-G06": ("type test", "pass"),
    "REQ-G07": ("type test", "pass"), "REQ-G08": ("maker's declaration", "pass"),
    "REQ-G09": ("CP-G09 frequency", "pass"), "REQ-G10": ("CP-G10 frequency", None),
    "REQ-G12": ("CP-G12 intertrip", "pass"), "REQ-G13": ("CP-G13 reconnection", "pass"),
    "REQ-G14": ("CP-G14 ramp", "pass"), "REQ-G15": ("CP-G15 set-point", "pass"),
    "REQ-G16": ("CP-G16 export limit", "pass"), "REQ-G17": ("CP-G17 telemetry", "pass"),
    "REQ-G19": ("protection report", "pass"), "REQ-G20": ("PQ campaign 7 days", None),
    "REQ-G21": ("model validation", None), "REQ-G23": ("test programme", "pass"),
}
PHASING = {"E1-L1": ("A", "A"), "E1-L2": ("B", "B"), "E1-L3": ("C", "C"),
           "T1 HV": ("ABC", "ABC"), "T2 HV": ("ABC", "ACB")}
SHEATH = {"WS1 S1": "pass", "WS1 S2": "pass", "WS1 S3": "pass", "WS1 S4a": "fail",
          "WS1 S4b": "pass", "WS2 S1": None}
INTERTRIP = dict(measured_ms=[38, 41, 36, 120, 39], limit_ms=60)

# ------------------------------------------------ I, J. information and readiness
DOCS = {"PLP-ELE-DWG-0008": "C03", "PLP-ELE-DWG-0022": "C02", "PLP-CTL-DWG-0001": "C04",
        "PLP-ELE-SPC-0011": "C01", "PLP-ELE-REP-0016": "C01"}
FLOCS = {"PV-B03-ST", "PV-B03-CB", "SUB-AUX", "SUB-33"}
HANDOVER_ROWS = [
    dict(tag="=PVF1-3-T1", floc="PV-B03-ST", serial="TR-56-0311", doc="PLP-ELE-DWG-0008",
         doc_rev="C03", warranty="2028-06-01", maint="MP-T", class_="transformer"),
    dict(tag="=PVF1-3-INV1", floc="PV-B03-ST", serial="PCI-5500-0412", doc="PLP-ELE-DWG-0008",
         doc_rev="C02", warranty="2028-06-01", maint="MP-INV", class_="inverter"),
    dict(tag="=PVF1-3-Q1", floc="PV-B03-ST", serial="RMU-7781", doc="PLP-ELE-DWG-0008",
         doc_rev="C03", warranty="2028-06-01", maint="", class_="switchgear"),
    dict(tag="=PVF1-3-CB09", floc="PV-B03-CB", serial="CB-20-1188", doc="PLP-ELE-DWG-0022",
         doc_rev="C02", warranty="2028-06-01", maint="MP-CB", class_="combiner"),
    dict(tag="=PVF1-3-CB10", floc="PV-B03-CB", serial="CB-20-1190", doc="PLP-ELE-DWG-0022",
         doc_rev="C02", warranty="2028-06-01", maint="MP-CB", class_="combiner"),
    dict(tag="=PVF1-3-SW1", floc="PV-B3-ST", serial="RS8-30091", doc="PLP-CTL-DWG-0001",
         doc_rev="C04", warranty="2028-06-01", maint="MP-NW", class_="network"),
    dict(tag="=PVF1-3-UPS1", floc="PV-B03-ST", serial="UPS-3K-5520", doc="PLP-CTL-DWG-0009",
         doc_rev="C01", warranty="2028-06-01", maint="MP-UPS", class_="ups"),
    dict(tag="=PVF1-3-T1", floc="PV-B03-ST", serial="TR-56-0311", doc="PLP-ELE-DWG-0008",
         doc_rev="C03", warranty="2028-06-01", maint="MP-T", class_="transformer"),
]
RESTORE = dict(rto_h=8.0, measured_h=11.5, data_loss_h=0.0)
ROLES = {"incident controller (day)": "S. Bagheri", "incident controller (night)": None,
         "first-aid lead": "M. Kazemi", "fire warden lead": "A. Rad",
         "liaison with the fire service": "S. Bagheri", "community liaison": "L. Amini"}
CONTACTS = {   # contact: last verified
    "fire service": date(2028, 3, 20), "hospital": date(2027, 11, 2),
    "network operator control": date(2028, 3, 28), "police": date(2027, 12, 15),
    "village representative": date(2028, 2, 1)}
CONTACT_MAX_DAYS = 90
DRILLS = {   # drill: done before handover?
    "fire evacuation, substation": True, "rescue from a nacelle": True,
    "casualty at a PV block, night": False, "loss of communications": False,
    "responders' familiarisation visit": True}
