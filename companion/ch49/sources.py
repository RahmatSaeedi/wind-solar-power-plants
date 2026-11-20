"""Synthetic site records for chapter 49: the construction of Plant P by a
fictional EPC contractor and its fictional subcontractors.

BLOCK         PV block =PVF1-3 (ch 10 D-013, ch 47 tables and posts)
PACKAGES      its work packages: days, predecessors, crew, hold days (A-506)
CREWS         crews available to the block
PERMITS       approvals register against the fronts that need them
METHODS       method statements by activity and their status
ROSTER        crew roles and certificate expiry
DRAWINGS      drawings each package needs and their status (ch 38 statuses)
FRONTS        work fronts, their distance by site road, the medical point
GATE, INDUCT  gate log and induction register
PILES, TORQUE, AS_LAID, TERMS, EARTH, STORE  installation records (A-507)
ITEMS, PUNCH  completion items of the block by subsystem (A-508)
ASSETS_*      asset records: design register and field capture (A-509)
LOOKAHEAD     packages of the next six weeks and their constraints (A-510)
WEEKS         installed modules and crew hours by week
AUX, SUBMIT, PEN, DETECT, IMPAIR   auxiliary and fire records (A-511)
WATER_*       construction water by month, sources and meters (A-512)
TOWERS, CROSS, SECTIONS            132 kV line and 33 kV collector WS1 (A-513)
GRIEV, HIRE, TRAFFIC, FIND         social-plan records (A-513)
Teaching values only; places, people and companies are fictional.
"""
from __future__ import annotations

from datetime import date

from companion.ch49 import common  # noqa: F401  (puts plantp on the path)

TODAY = date(2027, 9, 1)          # construction month 9 of 18 (ch 22 curve)

# ------------------------------------------------ PV block (ch 10, ch 47)
BLOCK = dict(tag="=PVF1-3", combiners=21, strings_per_cb=20, modules_per_string=26,
             tables=210, posts_per_table=12, modules=21 * 20 * 26)

# [start: packages]
# name: (days, [predecessors], crew, hold days after, inspection record)
PACKAGES = {
    "WP01 set-out": (2, [], "survey", 0, "set-out survey sheet"),
    "WP02 grading": (5, ["WP01 set-out"], "earthworks", 1, "level survey (hold)"),
    "WP03 piling": (6, ["WP02 grading"], "piling", 2, "post position and depth (hold)"),
    "WP04 tables": (8, ["WP03 piling"], "structure", 1, "torque and alignment (hold)"),
    "WP05 trenches": (4, ["WP02 grading"], "earthworks", 1, "trench before cables (hold)"),
    "WP06 cables in trench": (3, ["WP05 trenches"], "electrical", 1,
                              "cables and earth wire, open trench (hold)"),
    "WP07 backfill": (2, ["WP06 cables in trench"], "earthworks", 0, "compaction record"),
    "WP08 station base": (3, ["WP02 grading"], "civil", 7, "pour record; cure (hold)"),
    "WP09 station set": (1, ["WP08 station base"], "crane", 1, "anchoring (witness)"),
    "WP10 modules": (9, ["WP04 tables"], "modules", 0, "module serial capture"),
    "WP11 combiners": (3, ["WP04 tables"], "electrical", 0, "box install record"),
    "WP12 strings": (6, ["WP10 modules", "WP11 combiners"], "electrical", 1,
                     "connector sample (hold)"),
    "WP13 DC terminations": (3, ["WP12 strings", "WP07 backfill", "WP09 station set"],
                             "electrical", 1, "termination torque records (hold)"),
    "WP14 MV terminations": (2, ["WP09 station set", "WP07 backfill"], "jointer", 1,
                             "MV termination record (hold)"),
    "WP15 earthing": (1, ["WP13 DC terminations", "WP14 MV terminations"], "electrical", 0,
                      "continuity test sheet"),
    "WP16 walkdown": (2, ["WP15 earthing"], "QA", 0, "punch list; turnover package"),
}
CREWS = {"survey": 1, "earthworks": 1, "piling": 1, "structure": 1, "electrical": 1,
         "civil": 1, "crane": 1, "modules": 1, "jointer": 1, "QA": 1}
# [end: packages]

# ------------------------------------------------ readiness (A, L)
# approval, front, needed by (construction day), granted day or None
PERMITS = [
    ("building permit, substation building", "substation", 40, 31),
    ("water abstraction, wells W-1/W-2", "water", 10, 12),
    ("road crossing, regional road (MV duct)", "collector WS2", 120, None),
    ("wadi works consent", "access road km 4", 60, 75),
    ("abnormal loads, turbine convoy", "wind erection", 150, 140),
    ("temporary diesel store", "laydown", 15, 9),
    ("ruin buffer works (ch 33)", "corridor", 90, None),
]
METHODS = {   # activity: (method statement, status)
    "piling": ("MS-07", "approved"), "table assembly": ("MS-08", "approved"),
    "module mounting": ("MS-09", "approved"), "trenching": ("MS-05", "approved"),
    "MV terminations": ("MS-14", "returned with comments"),
    "station placement (crane)": ("MS-12", "approved"),
    "DC terminations": ("MS-13", "approved"), "string wiring": (None, None),
    "earthing": ("MS-15", "submitted"),
}
ROSTER = {   # crew: [(role, person, certificate expiry)]
    "jointer": [("MV jointer (maker-trained)", "J. Rahimi", date(2027, 7, 30)),
                ("electrician", "S. Karimi", date(2028, 2, 1))],
    "crane": [("crane operator", "M. Ahmadi", date(2028, 5, 1)),
              ("slinger/signaller", "R. Nazari", date(2027, 12, 1)),
              ("lift supervisor", None, None)],
    "electrical": [("qualified electrician", "A. Moradi", date(2028, 1, 15)),
                   ("first aider", "A. Moradi", date(2027, 10, 1))],
    "modules": [("supervisor", "H. Rostami", None), ("first aider", None, None)],
}
DRAWINGS = {   # package: [(drawing, revision, status)]
    "WP03 piling": [("PLP-CIV-DWG-0011", "C02", "IFC")],
    "WP04 tables": [("PLP-CIV-DWG-0012", "C01", "IFC")],
    "WP06 cables in trench": [("PLP-ELE-DWG-0021", "B03", "IFA"),
                              ("PLP-ELE-LST-0012", "C01", "IFC")],
    "WP08 station base": [("PLP-CIV-DWG-0014", "C02", "IFC")],
    "WP13 DC terminations": [("PLP-ELE-DWG-0022", "C01", "IFC")],
    "WP14 MV terminations": [("PLP-ELE-DWG-0023", "B02", "IFR")],
}
FRONTS = {   # front: km by site road from the medical point
    "PV block PVF1-3": 2.1, "PV block PVF3-3": 4.6, "T01 erection": 6.8,
    "T12 erection": 9.4, "substation": 0.6, "132 kV line, tower 18": 14.5,
}
SITE_TEAM = dict(mobilise_min=6.0, road_kmh=25.0, target_min=30.0)   # ch 32 (A-370)
INDUCT = {"W-0101": date(2027, 3, 1), "W-0102": date(2027, 3, 1), "W-0145": date(2027, 4, 9),
          "W-0188": date(2026, 8, 20), "W-0210": date(2027, 8, 2), "W-0233": None}
INDUCT_VALID_DAYS = 365
GATE = ["W-0101", "W-0102", "W-0145", "W-0188", "W-0210", "W-0233", "W-0240"]

# ------------------------------------------------ installation records (B)
# post: (x error mm, y error mm, embedment m, design embedment m)
PILES = {f"P3-{k:03d}": v for k, v in enumerate([
    (5, -8, 2.05, 2.0), (12, 4, 2.02, 2.0), (-18, 10, 2.00, 2.0), (25, -3, 1.98, 2.0),
    (-6, 2, 2.10, 2.0), (41, 9, 2.03, 2.0), (3, -12, 1.71, 2.0), (-9, 15, 2.06, 2.0),
    (14, -22, 2.01, 2.0), (-27, 7, 2.04, 2.0), (8, 5, 2.08, 2.0), (-2, -36, 2.02, 2.0)], 1)}
PILE_TOL_MM = 30.0
TORQUE = [   # (joint, recorded Nm or None, tool, tool calibration due)
    ("T3-014 clamp 1", 24.8, "TW-11", date(2027, 11, 1)),
    ("T3-014 clamp 2", 25.3, "TW-11", date(2027, 11, 1)),
    ("T3-015 clamp 1", None, "TW-11", date(2027, 11, 1)),
    ("T3-021 clamp 1", 25.0, "TW-07", date(2027, 8, 15)),
    ("T3-021 clamp 2", 21.0, "TW-07", date(2027, 8, 15)),
    ("T3-022 clamp 1", 25.1, "TW-11", date(2027, 11, 1)),
]
TORQUE_SPEC = (25.0, 0.10)        # maker's value placeholder, +/- share
AS_LAID = {   # cable: (design m, as-laid m)
    "CB01-ST": (620, 641), "CB05-ST": (480, 486), "CB09-ST": (395, 452),
    "CB13-ST": (310, 318), "CB17-ST": (260, 262), "CB21-ST": (540, 548),
}
TERMS = [   # MV terminations: cable end, jointer, kit lot, screen earthed, photo
    ("WS1-PVF13 A-end", "J. Rahimi", "K-2207", True, True),
    ("WS1-PVF13 B-end", "J. Rahimi", "K-2207", True, False),
    ("PVF13-PVF12 A-end", "S. Karimi", None, True, True),
    ("PVF13-PVF12 B-end", "J. Rahimi", "K-2214", None, True),
]
EARTH = {   # bond: measured ohm (continuity, teaching limit below)
    "T3-001 to grid": 0.04, "T3-050 to grid": 0.06, "T3-101 to grid": 0.35,
    "T3-150 to grid": 0.05, "CB09 to grid": 0.03, "station skid to grid": 0.02,
    "fence corner NE": 0.08, "fence gate": None,
}
EARTH_LIMIT = 0.2
STORE = {   # stored item: (arrived day, last check days, heater on?)
    "station skid S-03": (180, [187, 194, 201, 215, 222], True),
    "station skid S-04": (185, [192, 199, 206, 213, 220], True),
    "RMU spares": (150, [160, 190, 222], None),
    "transformer T-PV3": (178, [185, 192, 199, 206, 213, 220], None),
}
STORE_DAY = 226
STORE_EVERY = 7

# ------------------------------------------------ completion (C, K)
# (subsystem, tag, ITR categories done)
ITEMS = [
    ("=PVF1-3.DC", "=PVF1-3-CB01", {"A": True, "B": True}),
    ("=PVF1-3.DC", "=PVF1-3-CB02", {"A": True, "B": False}),
    ("=PVF1-3.DC", "=PVF1-3-CB03", {"A": True, "B": True}),
    ("=PVF1-3.DC", "=PVF1-3-CB04", {"A": False, "B": False}),
    ("=PVF1-3.INV", "=PVF1-3-INV1", {"A": True, "B": False}),
    ("=PVF1-3.MV", "=PVF1-3-T1", {"A": True, "B": True}),
    ("=PVF1-3.MV", "=PVF1-3-Q1", {"A": True, "B": True}),
    ("=PVF1-3.AUX", "=PVF1-3-F1", {"A": True, "B": True}),
    ("=PVF1-3.AUX", "=PVF1-3-UPS1", {"A": False, "B": False}),
    ("=PVF1-3.CTL", "=PVF1-3-PLC1", {"A": True, "B": False}),
    ("=PVF1-3.CTL", "=PVF1-3-SW1", {"A": True, "B": True}),
]
PUNCH = [   # id, subsystem, category, open?
    ("PL-301", "=PVF1-3.DC", "A", True), ("PL-302", "=PVF1-3.DC", "B", True),
    ("PL-303", "=PVF1-3.INV", "B", True), ("PL-304", "=PVF1-3.MV", "A", False),
    ("PL-305", "=PVF1-3.MV", "B", True), ("PL-306", "=PVF1-3.CTL", "A", True),
    ("PL-307", "=PVF1-3.AUX", "B", False),
]
CREDIT = {"received and inspected": 0.05, "mounted": 0.55, "clamps torqued": 0.15,
          "serial captured": 0.05, "inspected": 0.20}

ASSETS_DESIGN = {   # tag: design record
    "=PVF1-3-T1": dict(type="5.6 MVA unit transformer", x=7600.0, y=2720.0, doc="PLP-ELE-DWG-0008"),
    "=PVF1-3-INV1": dict(type="PCI-5500", x=7605.0, y=2730.0, doc="PLP-ELE-DWG-0008"),
    "=PVF1-3-Q1": dict(type="RMU 36 kV", x=7598.0, y=2712.0, doc="PLP-ELE-DWG-0008"),
    "=PVF1-3-CB09": dict(type="combiner 20 in", x=7380.0, y=2890.0, doc="PLP-ELE-DWG-0022"),
    "=PVF1-3-UPS1": dict(type="UPS 3 kVA", x=7605.0, y=2731.0, doc="PLP-CTL-DWG-0001"),
    "=PVF1-3-SW1": dict(type="RS-8 switch", x=7605.0, y=2731.0, doc="PLP-CTL-DWG-0001"),
}
# tag: captured record (stage fields: receipt, install, test, turnover)
ASSETS_FIELD = {
    "=PVF1-3-T1": dict(type="5.6 MVA unit transformer", serial="TR-56-0311", x=7600.4,
                       y=2719.6, doc="PLP-ELE-DWG-0008", firmware=None, test="FAT-T1-311",
                       warranty="2027-08-20", spares="SP-T1", maint="MP-T"),
    "=PVF1-3-INV1": dict(type="PCI-5500", serial="PCI-5500-0412", x=7605.2, y=2729.8,
                         doc="PLP-ELE-DWG-0008", firmware="4.2.1", test="FAT-0412",
                         warranty=None, spares="SP-INV", maint="MP-INV"),
    "=PVF1-3-Q1": dict(type="RMU 36 kV", serial="RMU-7781", x=7598.2, y=2711.7,
                       doc="PLP-ELE-DWG-0008", firmware=None, test="FAT-7781",
                       warranty="2027-08-20", spares="SP-RMU", maint=None),
    "=PVF1-3-CB09": dict(type="combiner 20 in", serial="CB-20-1188", x=7391.0, y=2890.5,
                         doc="PLP-ELE-DWG-0022", firmware=None, test=None,
                         warranty="2027-08-28", spares="SP-CB", maint="MP-CB"),
    "=PVF1-3-UPS1": dict(type="UPS 3 kVA", serial="UPS-3K-5520", x=7605.0, y=2731.0,
                         doc="PLP-CTL-DWG-0001", firmware="2.0", test="SAT-pending",
                         warranty="2027-08-28", spares=None, maint="MP-UPS"),
    "=PVF1-3-SW2": dict(type="RS-8 switch", serial="RS8-30091", x=7605.0, y=2731.0,
                        doc="PLP-CTL-DWG-0001", firmware="6.2.1", test="FAT-NW-14",
                        warranty="2027-08-28", spares="SP-NW", maint="MP-NW"),
    "=PVF1-3-CB10": dict(type="combiner 20 in", serial="CB-20-1188", x=7420.0, y=2890.0,
                         doc="PLP-ELE-DWG-0022", firmware=None, test=None,
                         warranty="2027-08-28", spares="SP-CB", maint="MP-CB"),
}
STAGES = {"receipt": ["type", "serial"], "installation": ["x", "y", "doc"],
          "test": ["test"], "turnover": ["warranty", "spares", "maint"]}
GIS_TOL_M = 2.0

# ------------------------------------------------ project controls (E)
# package: ([constraints], planned start day)
LOOKAHEAD = {
    "PVF2-1 piling": (["drawings", "permit", "crew", "materials"], 250),
    "PVF2-1 tables": (["materials", "predecessor"], 262),
    "PVF2-2 trenches": (["drawings", "access"], 248),
    "WS2 road crossing": (["permit", "drawings", "traffic plan"], 255),
    "T07 foundation": (["geotech report", "drawings", "concrete supply"], 270),
    "substation GIS": (["materials", "maker's engineer", "building handover"], 280),
}
CLEARED = {   # constraint of a package (package|constraint): day cleared or None
    "PVF2-1 piling|drawings": 230, "PVF2-1 piling|permit": 240, "PVF2-1 piling|crew": 245,
    "PVF2-1 piling|materials": 252,
    "PVF2-1 tables|materials": 255, "PVF2-1 tables|predecessor": 258,
    "PVF2-2 trenches|drawings": 244, "PVF2-2 trenches|access": 246,
    "WS2 road crossing|permit": None, "WS2 road crossing|drawings": 250,
    "WS2 road crossing|traffic plan": 253,
    "T07 foundation|geotech report": None, "T07 foundation|drawings": 260,
    "T07 foundation|concrete supply": 262,
    "substation GIS|materials": 268, "substation GIS|maker's engineer": 285,
    "substation GIS|building handover": 275,
}
LOOK_TODAY = 244
WEEKS = [   # week: modules installed, crew hours, crews
    (31, 3800, 900, 3), (32, 4300, 920, 3), (33, 4700, 950, 3), (34, 3100, 960, 3),
    (35, 5200, 1220, 4), (36, 5400, 1260, 4), (37, 4100, 1280, 4), (38, 5600, 1250, 4),
]
PLAN_RATE = 4.6                   # modules a crew-hour (A-510)

# ------------------------------------------------ auxiliary and fire (F, G)
AUX = {   # item: (received day, installed, labelled, connected, inspected, preserved)
    "SST 250 kVA": (150, True, True, True, True, True),
    "LV board MB-A": (160, True, True, True, False, True),
    "110 V DC board": (161, True, False, True, False, True),
    "station battery 110 V": (40, False, False, False, False, None),
    "UPS 10 kVA": (162, True, True, False, False, True),
    "HVAC units (2)": (170, True, True, True, True, True),
    "fire pump set": (175, True, False, True, False, True),
    "lighting": (180, True, True, True, False, True),
}
AUX_DAY = 226
BATTERY_STORE_MAX = 180           # maker's storage limit before a refresh, days (teaching)
SUBMIT = {   # fire component: (submittal, certificate or listing reference, approved)
    "smoke detectors": ("SUB-F01", "CERT-DET-224", True),
    "aspirating detector": ("SUB-F02", "CERT-ASD-77", True),
    "fire-stopping system": ("SUB-F03", None, False),
    "fire pump set": ("SUB-F04", "CERT-PMP-12", True),
    "hydrant valves": ("SUB-F05", "CERT-HV-03", False),
    "gas extinguishing (control room)": ("SUB-F06", "CERT-GX-19", True),
}
PEN = {f"PEN-{k:02d}": v for k, v in enumerate([   # inspected, photo, label
    (True, True, True), (True, True, True), (True, False, True), (False, False, False),
    (True, True, False), (True, True, True), (False, False, False), (True, True, True),
    (True, True, True), (True, False, True), (True, True, True), (True, True, True)], 1)}
DETECT = {   # detector: (approved x, y), (installed x, y), metres
    "SD-01": ((2.0, 2.0), (2.1, 2.0)), "SD-02": ((6.0, 2.0), (6.0, 2.2)),
    "SD-03": ((10.0, 2.0), (10.0, 3.4)), "SD-04": ((2.0, 6.0), (2.0, 6.1)),
    "SD-05": ((6.0, 6.0), (6.3, 6.0)), "SD-06": ((10.0, 6.0), None),
}
DETECT_TOL = 0.5
IMPAIR = [   # system, start day, end day or None, compensating measure
    ("fire main loop B", 200, 203, "fire watch, extinguishers"),
    ("detection zone 3", 210, None, "fire watch"),
    ("fire pump (testing)", 215, 215, "standby pump, responders told"),
    ("hydrant H-04", 205, None, None),
]

# ------------------------------------------------ water (H)
WATER_WELLS_M3 = 30_300.0         # ch 29: safe yield over the build
TICKETS = {   # month: (trucked tickets m3, trucked meter at tank m3)
    7: (5200, 5170), 8: (5600, 5050), 9: (5400, 5390),
}

# ------------------------------------------------ export and collector (I)
TOWERS = {   # tower: (landowner, access agreed, foundation done)
    "T01": ("L-01", True, True), "T02": ("L-01", True, True), "T03": ("L-02", True, True),
    "T04": ("L-02", True, False), "T05": ("L-03", False, False), "T06": ("L-03", False, False),
    "T07": ("L-04", True, False), "T08": ("L-05", True, False),
}
CROSS = [   # crossing, kind, approval, method
    ("X1", "regional road", "road authority", "duct under, traffic plan"),
    ("X2", "wadi", "water authority", "deep duct, outside flood season"),
    ("X3", "33 kV distribution line", "network owner", "outage window"),
    ("X4", "herders' track", "community (ch 33)", "kept open, crossing plate"),
]
SECTIONS = {   # WS1 section: (length m, drum m, joint bays)
    "S1": (1450, 1500, 0), "S2": (1620, 1500, 1), "S3": (980, 1500, 0), "S4": (3100, 1500, 1),
}

# ------------------------------------------------ social plan (J)
GRIEV = [   # id, received day, category, acknowledged day, closed day or None
    ("G-21", 150, "dust", 151, 160), ("G-22", 155, "traffic", 157, 171),
    ("G-23", 162, "wages (subcontractor)", 170, None), ("G-24", 170, "grazing access", 171, 179),
    ("G-25", 181, "noise at night", 182, 184), ("G-26", 190, "wages (subcontractor)", 198, None),
    ("G-27", 201, "dust", 202, 206), ("G-28", 214, "hiring", 215, None),
]
GRIEV_ACK_DAYS = 3
GRIEV_CLOSE_DAYS = 30
HIRE = {   # month: (workers, local)
    3: (120, 60), 4: (190, 85), 5: (260, 105), 6: (330, 122), 7: (390, 130), 8: (430, 140),
}
HIRE_TARGET = 0.40                # ch 32/33 commitment (approved plan)
TRAFFIC = {   # hour: heavy vehicles through the village (one week, mean a day)
    6: 3, 7: 9, 8: 6, 9: 5, 10: 6, 11: 5, 12: 4, 13: 8, 14: 6, 15: 5, 16: 4, 17: 3,
}
QUIET_HOURS = (7, 13)             # school arrival and return (ch 32 school traffic)
FIND = dict(day=219, found="09:40", stop="09:55", notified="next day 11:00",
            radius_m=50, procedure_hours=24)
