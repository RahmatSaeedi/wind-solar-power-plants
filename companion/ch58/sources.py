"""Chapter 58 sources. The register is the book's own
glossary/standards-register.csv (titles, editions, statuses - never the
text of a standard). The specification sentences, certificates, laboratory
scopes and evidence matrix are TEACHING records of Plant P written by the
book (A-567 to A-570); they quote no standard.
"""
from __future__ import annotations

from datetime import date

from companion.ch58 import common

REGISTER = common.HERE.parents[1] / "glossary" / "standards-register.csv"
TODAY = date(2026, 11, 18)

# [start: spec]
SPEC = [   # sentences of a teaching Plant P specification (book-written)
    "The revenue meter shall be class 0.5S at the ownership boundary.",
    "Cable joints shall not be placed inside road crossings.",
    "The inverter should be rated for the site's maximum ambient temperature.",
    "The supplier may offer an alternative earthing material with evidence.",
    "Site tests can be witnessed by the network company.",
    "Earthing shall be adequate for the fault level.",
    "Transformer bushings shall be suitable for the site.",
    "The average winding temperature rise shall not exceed 65 K.",
    "Corrosion protection shall follow good practice.",
    "The plant exports at the point of connection.",
    "Spare parts should be held where necessary.",
    "The contractor shall submit type-test reports with the bid.",
]
# [end: spec]

# [start: catalogue]
CATALOGUE = {   # from the register (STD-001, 119, 084, 173); one teaching placeholder
    "IEC 62548-1": [(2023, "IEC 62548-1:2023", "edition"),
                    (2025, "AMD1:2025", "amendment")],
    "IEC 60529": [(1989, "IEC 60529:1989", "edition"),
                  (1999, "AMD1:1999", "amendment"),
                  (2013, "AMD2:2013", "amendment")],
    "IEC 61400-24": [(2019, "IEC 61400-24:2019", "edition"),
                     (2024, "AMD1:2024", "amendment")],
    "IEC 60076-2": [(2011, "IEC 60076-2:2011", "edition")],
}
FUTURE = (9999, "IEC 60076-2 Ed. 4 (teaching placeholder: in development)", "edition")
# [end: catalogue]

# [start: certs]
# equipment -> (standard and edition the specification names, certificate
# standard and edition, laboratory's accredited scope)   (teaching)
CERTS = {
    "PV module": ("IEC 61215-2:2021", "IEC 61215-2:2021",
                  ["IEC 61215-2:2021", "IEC 61730-2:2023"]),
    "PV module safety": ("IEC 61730-2:2023", "IEC 61730-2:2016",
                         ["IEC 61215-2:2021", "IEC 61730-2:2016"]),
    "PV inverter safety": ("IEC 62109-1:2010", "IEC 62109-1:2010",
                           ["IEC 62109-1:2010", "IEC 62109-2:2011"]),
    "PV inverter anti-islanding": ("IEC 62116:2014", "IEC 62116:2014",
                                   ["IEC 62109-1:2010"]),
    "battery cells and system": ("IEC 62619:2022", "IEC 62619:2022",
                                 ["IEC 62619:2022"]),
    "MV switchgear": ("IEC 62271-200:2021", "IEC 62271-200:2011",
                      ["IEC 62271-200:2011"]),
    "revenue meter": ("IEC 62053-22:2020", "IEC 62053-22:2020",
                      ["IEC 62053-22:2020"]),
}
# [end: certs]

# [start: evidence]
# equipment -> evidence kinds Plant P asks for (chapters 40-50): T type test or
# certificate, R routine test on every unit, S sample test, F site test
EVIDENCE = {
    "PV modules (ch 41)": "TRSF", "PV inverters (ch 44)": "TR-F",
    "wind turbines (ch 42)": "T--F", "main transformers (ch 43)": "TR-F",
    "PV unit transformers (ch 39, 43)": "TRS-", "MV switchgear (ch 46)": "TR-F",
    "MV cables (ch 46)": "TRSF", "battery containers (ch 45)": "TRSF",
    "protection relays (ch 26, 46)": "TR-F", "revenue meters (ch 48)": "TR-F",
}
KINDS = {"T": "type test / certificate", "R": "routine test, every unit",
         "S": "sample test", "F": "site test"}
# [end: evidence]

# [start: trace]
TRACE = {   # the temperature-rise requirement of the main transformers
    "clause": "IEC 60076-2:2011 (STD-173): the temperature-rise test and its"
              " method, named by purpose; limits taken from the project",
    "decision": "D-029 transformer basis; D-047 design review and FAT basis",
    "procurement": "PLP-ELE-SPC-0010 clause C-2.5: top oil 60 K, winding 65 K",
    "inspection": "witness point at the heat run in the maker's test bay",
    "test": "heat run of T1, resistance read after shut-down (ch 43)",
    "approval": "acceptance of the test report by the owner's engineer",
    "register": "STD-173: edition 3.0 (2011); edition 4 reported - confirm",
    "trigger": "a new edition, an amendment, or a changed project limit",
}
LINKS = {   # requirement -> (document, records to re-check if it changes)
    "REQ-T1": ("STD-173", ["D-047 item on the heat run", "PLP-ELE-SPC-0010 C-2.5",
                           "ITP witness point (ch 43)", "T1 test report review",
                           "LossTempCalc settings (ch 43)"]),
    "REQ-T2": ("STD-120", ["PLP-ELE-SPC-0010 C-2.1 to C-2.4", "rating plate check",
                           "routine-test list (ch 43)"]),
    "REQ-T3": ("STD-173", ["hot-spot factor from fibre sensors (ch 43)",
                           "loading guide inputs (ch 25)"]),
    "REQ-M1": ("STD-013", ["meter specification (ch 48)", "metering trace (ch 57)"]),
}
# [end: trace]

REVIEW_MONTHS = {"open item": 1, "linked or hub": 6, "other": 12}
