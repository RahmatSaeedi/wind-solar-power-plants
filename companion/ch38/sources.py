"""Chapter 38 - synthetic design registers of Plant P (teaching values
A-417 to A-424). Nothing here is a real project's record; the defects are
planted so the checks can find them.

DOCS        master document register (MDR) of 120 deliverables at the
            status date, week 40 of the detailed design
HISTORY     status changes of a few documents (two illegal ones planted)
REFS        cross-references between documents with the revision used
ONE_LINE, EQUIPMENT, CABLES, PROTECTION
            four registers that should agree on ratings and tags
REQS        requirements with design, verification and evidence links
ICD_INV     interface items of the PV inverter skid (inverter + unit
            transformer + MV switchgear)
DEPENDS     which documents use the data of which (change impact)
TQS         technical queries with days open
HANDOVER    handover package items with weight and share complete
"""
from __future__ import annotations

import numpy as np

from companion.ch38 import common  # noqa: F401  (puts plantp on the path)

STATUS_DATE_WEEK = 40
CREDIT = {"WIP": 0.10, "IFR": 0.30, "IFI": 0.30, "IFA": 0.60, "APP": 0.80,
          "IFC": 0.90, "ASB": 1.00, "SUP": 0.0}          # rules of credit (teaching)


def _docs(seed: int = 381):
    rng = np.random.default_rng(seed)
    mix = [("ELE", "DWG", 34), ("ELE", "CAL", 12), ("ELE", "LST", 8), ("ELE", "SPC", 6),
           ("CIV", "DWG", 18), ("CIV", "CAL", 6), ("MEC", "DWG", 6), ("CTL", "DWG", 10),
           ("CTL", "LST", 6), ("CTL", "SPC", 4), ("PRJ", "REG", 4), ("GEN", "PRO", 6)]
    docs, n = [], 0
    for dis, typ, count in mix:
        for k in range(count):
            n += 1
            planned_week = int(rng.integers(8, 60))
            hours = {"DWG": 60, "CAL": 80, "LST": 40, "SPC": 50, "REG": 30, "PRO": 30}[typ]
            hours = int(hours * rng.uniform(0.6, 1.6))
            # status at week 40 depends on how early it was planned
            if planned_week < 20:
                status = rng.choice(["IFC", "APP", "IFA"], p=[0.6, 0.2, 0.2])
            elif planned_week < 35:
                status = rng.choice(["IFA", "IFR", "IFC"], p=[0.4, 0.4, 0.2])
            elif planned_week < 45:
                status = rng.choice(["IFR", "WIP"], p=[0.5, 0.5])
            else:
                status = "WIP"
            rev = {"WIP": "A", "IFR": "A", "IFA": "B", "APP": "0", "IFC": "0"}[str(status)]
            docs.append(dict(id=f"PLP-{dis}-{typ}-{100 + k:04d}", title=f"{dis} {typ} {k + 1}",
                             rev=rev, status=str(status), planned_week=planned_week,
                             hours=hours, spent=int(hours * CREDIT[str(status)]
                                                    * rng.uniform(0.9, 1.5)),
                             owner="lead " + dis, asset="", approved_by=""))
    # planted defects (A-417)
    docs[3]["id"] = "PLP-ELX-DWG-0103"                  # unknown discipline
    docs[40]["id"] = "PLP-CIV-DWG-12"                   # short number
    docs[10]["rev"], docs[10]["status"] = "1", "IFR"     # number before approval
    docs[22]["rev"], docs[22]["status"] = "C", "IFC"     # letter after approval
    docs[55]["rev"], docs[55]["status"] = "B", "APP"
    for i in (5, 17, 29, 61, 77, 88, 95, 101, 116):
        docs[i]["owner"] = ""                           # metadata gaps
    for d in docs:                                      # approval for approved docs
        if d["status"] in ("APP", "IFC") and d["owner"]:
            d["approved_by"] = "checker " + d["id"][4:7]
        if d["id"][9:12] in ("DWG", "LST") and d["owner"]:
            d["asset"] = "=" + d["id"][4:7]
    docs[30]["approved_by"] = ""                        # approved without a checker
    return docs


DOCS = _docs()

HISTORY = {   # status changes recorded in the CDE (two illegal ones planted)
    "PLP-ELE-DWG-0105": ["WIP", "IFR", "IFA", "APP", "IFC"],
    "PLP-ELE-CAL-0101": ["WIP", "IFR", "IFC"],          # skipped the approval
    "PLP-CIV-DWG-0102": ["WIP", "IFR", "WIP", "IFR", "IFA", "APP"],
    "PLP-CTL-DWG-0103": ["WIP", "IFI", "IFC"],          # issued for information, then built
    "PLP-MEC-DWG-0100": ["WIP", "IFR", "IFA", "APP", "IFC", "ASB"],
}

# current revision of the documents the cross-references point to
CURRENT = {"PLP-ELE-DWG-0005": "2", "PLP-ELE-LST-0004": "1", "PLP-ELE-LST-0005": "1",
           "PLP-ELE-CAL-0011": "1", "PLP-CTL-LST-0001": "2", "PLP-CIV-DWG-0101": "0",
           "PLP-ELE-SPC-0007": "1", "PLP-CTL-DWG-0001": "1"}
REFS = [  # (from, to, revision used)
    ("PLP-ELE-LST-0005", "PLP-ELE-DWG-0005", "2"),   # cable schedule -> one-line
    ("PLP-ELE-CAL-0011", "PLP-ELE-DWG-0005", "1"),   # protection study used rev 1
    ("PLP-ELE-SPC-0007", "PLP-ELE-CAL-0011", "1"),
    ("PLP-CTL-LST-0001", "PLP-ELE-DWG-0005", "2"),
    ("PLP-CTL-DWG-0001", "PLP-CTL-LST-0001", "1"),   # network drawing used I/O list rev 1
    ("PLP-CIV-DWG-0101", "PLP-ELE-LST-0004", "1"),
    ("PLP-CIV-DWG-0101", "PLP-ELE-DWG-0009", "0"),   # points to a drawing not registered
]

# four registers that should agree (A-418); planted disagreements
ONE_LINE = {   # PLP-ELE-DWG-0005 rev 2 (after ch 26: incomers 1,600 A)
    "=T1-Q2": dict(a=1600, ka=25), "=T2-Q2": dict(a=1600, ka=25),
    "=WS1-Q1": dict(a=630, ka=25), "=PVF2-Q1": dict(a=630, ka=25),
    "=PVF2-3-T1": dict(mva=5.5, vector="Dyn11"), "=WS1-2-T1": dict(mva=5.6, vector="Dyn11"),
    "=PVF2-W1": dict(mm2=240, km=0.6),
}
EQUIPMENT = {   # PLP-ELE-LST-0004 rev 1
    "=T1-Q2": dict(a=1250, ka=25), "=T2-Q2": dict(a=1600, ka=25),
    "=WS1-Q1": dict(a=630, ka=25), "=PVF2-Q1": dict(a=630, ka=25),
    "=PVF2-3-T1": dict(mva=5.0, vector="Dyn11"), "=WS1-2-T1": dict(mva=5.6, vector="Dyn5"),
}
CABLES = {   # PLP-ELE-LST-0005 rev 1
    "=PVF2-W1": dict(mm2=240, km=0.9),
}
PROTECTION = {   # PLP-ELE-SPC-0007 rev 1, CT ratios used in the settings
    "=WS1-Q1": dict(ct=600), "=PVF2-Q1": dict(ct=800),
}
CT_LIST = {   # CT ratios on the switchgear data sheets
    "=WS1-Q1": dict(ct=600), "=PVF2-Q1": dict(ct=600),
}

REQS = {   # requirement -> (text, design links, verification method, evidence)
    "REQ-001": ("export cap 100 MW at POC", ["PLP-CTL-SPC-0001"], "test", []),
    "REQ-004": ("reactive capability at POC", ["PLP-ELE-CAL-0014"], "analysis", []),
    "REQ-G03": ("fault ride-through", ["PLP-ELE-REP-0011"], "test", []),
    "REQ-G07": ("power quality emissions", ["PLP-ELE-CAL-0013"], "measurement", []),
    "REQ-S01": ("frequency service", ["PLP-CTL-SPC-0001"], "test", []),
    "REQ-007": ("auxiliary autonomy 4 h", ["PLP-ELE-CAL-0008"], "test", []),
    "REQ-009": ("SCADA retention 10 years", ["PLP-CTL-SPC-0003"], "inspection", []),
    "REQ-010": ("fire detection, BESS area", [], "inspection", []),
    "REQ-011": ("noise at the camp", ["PLP-GEN-REP-0011"], "", []),
    "REQ-012": ("water use within permit", [], "", []),
    "REQ-003": ("time stamps to 1 ms", ["PLP-CTL-SPC-0003"], "test",
                ["FAT record F-112"]),
    "REQ-002": ("protection clearing time", ["PLP-ELE-CAL-0011"], "test",
                ["FAT record F-087"]),
}

ICD_INV = [   # interface items of the PV inverter skid (A-419); owner A = inverter maker,
              # B = EPC; value None = open
    ("mechanical", "skid footprint and bolt pattern", "A", "6.1 x 2.4 m, 8 x M24"),
    ("mechanical", "MV cable entry from below", "B", "3 x 240 mm2 Al"),
    ("electrical", "AC rating at 0.6 kV", "A", "5.0 MVA"),
    ("electrical", "unit transformer rating", "B", "5.5 MVA Dyn11"),
    ("electrical", "short-circuit level at the RMU", "B", None),
    ("protection", "boundary: inverter / LV breaker / MV RMU", "B", "settings file"),
    ("thermal", "heat rejected at full load, 45 C", "A", None),
    ("thermal", "air inlet and outlet clearances", "A", "1.5 m"),
    ("controls", "set points and limits over the plant network", "A", "point list rev 2"),
    ("controls", "time synchronisation", "B", "PTP from the plant clock"),
    ("civil", "foundation load and drainage", "B", "28 t, falls 1 %"),
    ("grid", "fault ride-through and reactive capability", "A", None),
]

DEPENDS = {   # data of the key -> documents that use it (change impact, A-420)
    "unit transformer rating": ["equipment list", "transformer data sheet",
                                "one-line diagram"],
    "equipment list": ["skid foundation drawing", "LV cable schedule"],
    "transformer data sheet": ["protection study", "losses calculation"],
    "one-line diagram": ["SCADA point list", "protection study"],
    "protection study": ["relay settings file"],
    "relay settings file": ["FAT procedure"],
    "SCADA point list": ["HMI displays", "FAT procedure"],
    "skid foundation drawing": ["civil bill of quantities"],
    "LV cable schedule": ["cable pulling plan"],
    "losses calculation": [], "HMI displays": [], "FAT procedure": [],
    "civil bill of quantities": [], "cable pulling plan": [],
}
REWORK_H = {"equipment list": 4, "transformer data sheet": 6, "one-line diagram": 6,
            "skid foundation drawing": 16, "LV cable schedule": 8, "protection study": 24,
            "losses calculation": 6, "SCADA point list": 4, "relay settings file": 8,
            "FAT procedure": 6, "HMI displays": 4, "civil bill of quantities": 6,
            "cable pulling plan": 4}


def _tqs(seed: int = 382):
    rng = np.random.default_rng(seed)
    return [int(x) for x in np.round(rng.gamma(1.6, 9.0, 42))]


TQS = _tqs()

HANDOVER = {   # item -> (weight, share complete, critical?) (A-421)
    "as-built drawings": (3, 0.92, True),
    "asset register attributes": (3, 0.85, True),
    "O&M manuals": (2, 0.70, False),
    "test and commissioning records": (3, 1.00, True),
    "spare parts lists": (1, 0.60, False),
    "software and settings backups": (2, 0.95, True),
    "warranties and certificates": (1, 0.80, False),
}
