"""Chapter 47 - teaching data for the manufacture of Plant P's tower,
foundations, PV tables, tracker variant and balance-of-plant steel by a
fictional tower fabricator, a fictional tracker maker and a fictional
ready-mix supplier. Values are illustrative, not makers' data and not a
standard's limits (A-490 to A-497).

ORDER       steel purchase order for the tower plates (A-490)
CERTS       mill certificates of the plates, with planted faults (A-490)
PLATES      plate -> heat -> cans -> section genealogy (A-490)
WELDERS     welder qualifications and the weld log of section 1 (A-491)
NDT         planned and done NDT coverage by weld category (A-491)
TRACKER     torque-tube survey and drive end-of-line records (A-492)
ZINC        galvanizing thickness of PV posts by lot (A-492)
BBS         bar bending schedule of one foundation, with faults (A-493)
TICKETS     batching tickets of one foundation pour (A-494)
CUBES       strength results by pour (A-494)
NCRS        nonconformance register of the fabricator (A-495)
DOSSIER     documents required and present for tower section 1 (A-496)
"""
from __future__ import annotations

from datetime import date

from companion.ch47 import common  # noqa: F401  (puts plantp on the path)
from companion.ch30 import sources as s30

TOWER = s30.TOWER                      # (section, D base, D top, t mm, length)
STEEL_RHO = s30.STEEL["rho"]
BASE_D = 24.0                          # m, D-034 (ch 30)
BASE_CONCRETE = 893.0                  # m3 a turbine, D-034
TURBINES = 12

# [start: order]
ORDER = dict(grade="S355", t_range=(20, 50), impact_c=-20, impact_j=27,
             cev_max=0.43)
# [end: order]

CERTS = [   # plate, heat, grade, t mm, impact test C, impact J (3), chemistry
    dict(plate="P101", heat="H5521", grade="S355", t_mm=46, impact_c=-20,
         impact_j=(62, 71, 58), chem=dict(c=0.16, mn=1.45, cu=0.05)),
    dict(plate="P102", heat="H5521", grade="S355", t_mm=46, impact_c=-20,
         impact_j=(66, 54, 70), chem=dict(c=0.16, mn=1.45, cu=0.05)),
    dict(plate="P103", heat="H5523", grade="S355", t_mm=46, impact_c=0,
         impact_j=(48, 52, 45), chem=dict(c=0.17, mn=1.40, cu=0.04)),
    dict(plate="P104", heat="H5524", grade="S355", t_mm=40, impact_c=-20,
         impact_j=(41, 22, 39), chem=dict(c=0.15, mn=1.38, cu=0.04)),
    dict(plate="P105", heat="H5530", grade="S355", t_mm=40, impact_c=-20,
         impact_j=(55, 60, 57), chem=dict(c=0.20, mn=1.55, cr=0.10, cu=0.10)),
    dict(plate="P106", heat="H5531", grade="S275", t_mm=32, impact_c=-20,
         impact_j=(50, 48, 52), chem=dict(c=0.14, mn=1.20, cu=0.03)),
    dict(plate="P107", heat="H5532", grade="S355", t_mm=32, impact_c=-20,
         impact_j=(64, 61, 66), chem=dict(c=0.15, mn=1.42, cu=0.04)),
    dict(plate="P108", heat="H5533", grade="S355", t_mm=26, impact_c=-20,
         impact_j=(70, 68, 73), chem=dict(c=0.14, mn=1.40, cu=0.03)),
]

PLATES = {   # plate -> cans cut from it (section-can)
    "P101": ["1-01", "1-02", "1-03"], "P102": ["1-04", "1-05", "1-06"],
    "P103": ["1-07", "1-08", "1-09", "1-10"], "P104": ["2-01", "2-02", "2-03"],
    "P105": ["2-04", "2-05", "2-06", "2-07"], "P106": ["3-01", "3-02"],
    "P107": ["3-03", "3-04", "3-05"], "P108": ["4-01", "4-02", "4-03"],
}

TODAY = date(2027, 3, 15)
WELDERS = {
    "W-11": dict(quals={"SAW": dict(positions={"PA", "PB"}, expires=date(2027, 9, 1)),
                        "FCAW": dict(positions={"PA", "PB", "PF"},
                                     expires=date(2027, 6, 1))}),
    "W-12": dict(quals={"SAW": dict(positions={"PA"}, expires=date(2027, 2, 28))}),
    "W-13": dict(quals={"FCAW": dict(positions={"PA", "PB"},
                                     expires=date(2028, 1, 1))}),
    "W-14": dict(quals={"SAW": dict(positions={"PA", "PB"}, expires=date(2027, 12, 1)),
                        "FCAW": dict(positions={"PA", "PB", "PF", "PC"},
                                     expires=date(2027, 12, 1))}),
}
WELD_LOG = [   # joint, welder, process, position, date
    ("C1-01", "W-11", "SAW", "PA", date(2027, 2, 10)),
    ("C1-02", "W-12", "SAW", "PA", date(2027, 3, 2)),
    ("C1-03", "W-14", "SAW", "PA", date(2027, 3, 3)),
    ("L1-01", "W-11", "SAW", "PA", date(2027, 2, 12)),
    ("F1-01", "W-13", "FCAW", "PF", date(2027, 3, 5)),
    ("F1-02", "W-14", "FCAW", "PB", date(2027, 3, 6)),
    ("D1-01", "W-12", "FCAW", "PB", date(2027, 2, 20)),
    ("A1-01", "W-14", "FCAW", "PC", date(2027, 3, 8)),
]

NDT_PLAN = {"circumferential": 1.0, "longitudinal": 1.0, "flange-to-shell": 1.0,
            "door frame": 1.0, "attachments": 0.10}
NDT_DONE = {"circumferential": (104.0, 104.0), "longitudinal": (25.0, 25.0),
            "flange-to-shell": (28.3, 28.3), "door frame": (9.6, 9.6),
            "attachments": (1.2, 30.0)}

TUBE = dict(x=[0, 6, 12, 18, 24, 30, 36, 42, 48, 54, 60],
            y=[0.0, 3.1, 5.8, 9.4, 14.2, 18.9, 16.0, 13.1, 9.0, 4.4, 0.4])  # mm
DRIVES = [   # serial, backlash deg, holding test result, lubricant lot
    ("SD-301", 0.08, "pass", "L-7"), ("SD-302", 0.09, "pass", "L-7"),
    ("SD-303", 0.21, "pass", "L-8"), ("SD-304", 0.07, "pass", "L-7"),
    ("SD-305", 0.08, "", "L-8"), ("SD-306", 0.10, "pass", "L-8"),
]

ZINC = {   # lot: (steel thickness mm, readings um)
    "Z-01": (4.0, [92, 98, 105, 88, 101, 96, 110, 94]),
    "Z-02": (4.0, [72, 69, 80, 75, 66, 78, 71, 70]),
    "Z-03": (6.0, [104, 112, 98, 120, 108, 101, 115, 99]),
}
ZINC_MIN = {4.0: (85, 70), 6.0: (85, 70)}      # teaching: (mean, each) um

# [start: bbs]
BBS = [   # one turbine foundation (excerpt)
    dict(mark="B01", dia=32, shape="00", length_mm=11800, number=180),
    dict(mark="B02", dia=32, shape="00", length_mm=11800, number=180),
    dict(mark="B03", dia=25, shape="21", length_mm=3600, number=240),
    dict(mark="B04", dia=25, shape="21", length_mm=3.6, number=240),
    dict(mark="B05", dia=20, shape="51", length_mm=2400, number=320),
    dict(mark="B05", dia=20, shape="51", length_mm=2400, number=160),
    dict(mark="B07", dia=22, shape="00", length_mm=6000, number=96),
    dict(mark="B08", dia=16, shape="99", length_mm=1800, number=400),
    dict(mark="B09", dia=16, shape="", length_mm=1500, number=200),
]
DIAS = {10, 12, 16, 20, 25, 32, 40}
SHAPES = {"00", "11", "21", "51"}
# [end: bbs]

TICKETS = [   # truck, minutes batching -> end of discharge, temp C, water L
    dict(truck=k + 1, discharged_min=m, temp_c=t, water_added_l=w)
    for k, (m, t, w) in enumerate([
        (52, 27, 0), (58, 28, 0), (61, 28, 0), (55, 29, 0), (63, 29, 0),
        (70, 30, 0), (96, 31, 0), (66, 31, 40), (72, 32, 0), (65, 33, 0),
        (59, 32, 0), (64, 31, 0), (88, 31, 0), (61, 30, 0), (57, 30, 0)])]

CUBES = {   # pour: three 28-day results, MPa (class 35 teaching)
    "F01": [41.2, 40.1, 42.3], "F02": [43.7, 41.8, 44.0], "F03": [38.0, 36.5, 37.9],
    "F04": [40.8, 30.2, 41.5], "F05": [42.6, 43.1, 41.0], "F06": [39.9, 40.4, 41.2],
}

NCRS = [   # id, raised, closed?, subject
    dict(id="NCR-201", raised=date(2026, 11, 20), closed=True, subject="ovality can 2-03"),
    dict(id="NCR-202", raised=date(2026, 12, 5), closed=False, subject="flange F2 flatness"),
    dict(id="NCR-203", raised=date(2027, 1, 18), closed=False, subject="DFT low section 3"),
    dict(id="NCR-204", raised=date(2027, 2, 2), closed=True, subject="UT repair C1-07"),
    dict(id="NCR-205", raised=date(2027, 2, 25), closed=False, subject="plate P103 impact"),
    dict(id="NCR-206", raised=date(2027, 3, 9), closed=False, subject="welder W-12 expired"),
    dict(id="NCR-207", raised=date(2026, 10, 30), closed=False, subject="door frame MT"),
]

DOSSIER = {   # document: present?
    "purchase order and drawings at revision": True,
    "mill certificates of every plate": True,
    "plate-to-can genealogy": True,
    "WPS and PQR for each weld type": True,
    "welder qualifications on the weld dates": False,
    "weld map with welder per joint": True,
    "NDT reports to the plan": False,
    "repair records and re-tests": True,
    "dimensional survey (ovality, flange flatness)": True,
    "coating DFT records": True,
    "NCR register with closures": False,
    "release note signed by the buyer's inspector": False,
}
