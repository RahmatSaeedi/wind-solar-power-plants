"""Chapter 54 sources: a FICTIONAL jurisdiction, "Country Z", with fictional
authorities, documents, editions and values. Nothing here states a real
country's requirement; chapters 55-57 research the real ones.
Teaching values (A-546 to A-550).
"""
from __future__ import annotations

from datetime import date

TODAY = date(2027, 3, 1)               # design stage of Plant P (teaching)
PROJECT = dict(voltage_kv=132, ownership="private", location="Province Q",
               technology="hybrid")

DOCS = {   # document: (source type, issuer, current edition, official source known?)
    "EA-Z": ("law", "Parliament of Z", "2021", True),
    "GLR": ("regulation", "Energy Regulator of Z (ERZ)", "2023", True),
    "EP-117": ("permit condition", "Environment Agency of Z", "2026", True),
    "GCZ": ("grid code", "Transmission System Operator of Z (TSOZ)", "2024", True),
    "TCR": ("utility rule", "TSOZ", "2022", True),
    "ZS-60076": ("national standard", "Standards Institute of Z", "2020", True),
    "CA-P": ("contract", "TSOZ and the project company", "draft 3", True),
    "PPA-P": ("contract", "offtaker and the project company", "signed", True),
    "OS-P": ("owner specification", "project company", "rev C", True),
    "DNR": ("regulation", "Distribution Network Rules of Z", "2019", False),
}

REQS = [   # the project's register (fictional); scope None = any
    dict(id="Z-001", document="GCZ", edition="2024", parameter="power factor at POC", kind="min",
         value=0.95, unit="-", status="verified", verified=date(2026, 11, 2), official_source=True,
         scope=dict(v_min=66), owner="grid engineer"),
    dict(id="Z-002", document="CA-P", edition="draft 3", parameter="power factor at POC", kind="min",
         value=0.93, unit="-", status="project-dependent", verified=date(2027, 1, 20),
         official_source=True, scope={}, owner="grid engineer"),
    dict(id="Z-003", document="OS-P", edition="rev C", parameter="power factor at POC", kind="min",
         value=0.95, unit="-", status="verified", verified=date(2027, 2, 1), official_source=True,
         scope={}, owner="owner's engineer"),
    dict(id="Z-004", document="GCZ", edition="2019", parameter="ramp rate", kind="max", value=10.0,
         unit="%/min", status="verified", verified=date(2025, 6, 1), official_source=True,
         scope=dict(v_min=66), owner="controls engineer"),
    dict(id="Z-005", document="TCR", edition="2022", parameter="ramp rate", kind="max", value=8.0,
         unit="%/min", status="verified", verified=date(2026, 12, 5), official_source=True,
         scope=dict(v_min=66), owner="controls engineer"),
    dict(id="Z-006", document="EP-117", edition="2026", parameter="night noise at dwellings",
         kind="max", value=40.0, unit="dB(A)", status="verified", verified=date(2026, 10, 1),
         official_source=True, scope={}, owner="environmental lead"),
    dict(id="Z-007", document="GLR", edition="2023", parameter="night noise at dwellings",
         kind="max", value=45.0, unit="dB(A)", status="verified", verified=date(2026, 9, 1),
         official_source=True, scope={}, owner="environmental lead"),
    dict(id="Z-008", document="PPA-P", edition="signed", parameter="night noise at dwellings",
         kind="max", value=48.0, unit="dB(A)", status="verified", verified=date(2026, 9, 1),
         official_source=True, scope={}, owner="commercial lead"),
    dict(id="Z-009", document="GCZ", edition="2024", parameter="ride-through at 0 pu",
         kind="min", value=150.0, unit="ms", status="verified", verified=date(2026, 11, 2),
         official_source=True, scope=dict(v_min=66), owner="grid engineer"),
    dict(id="Z-010", document="TCR", edition="2022", parameter="ride-through at 0 pu",
         kind="max", value=100.0, unit="ms", status="to-confirm", verified=date(2026, 12, 5),
         official_source=True, scope=dict(v_min=66), owner="grid engineer"),
    dict(id="Z-011", document="DNR", edition="2019", parameter="flicker at the connection",
         kind="max", value=0.35, unit="Pst", status="to-confirm", verified=None,
         official_source=False, scope=dict(v_max=33), owner="power-quality engineer"),
    dict(id="Z-012", document="ZS-60076", edition="2016", parameter="transformer standard",
         kind="equal", value=1, unit="-", status="verified", verified=date(2024, 2, 1),
         official_source=True, scope={}, owner="electrical lead"),
    dict(id="Z-013", document="EA-Z", edition="2021", parameter="generation licence",
         kind="equal", value=1, unit="-", status="verified", verified=date(2026, 8, 1),
         official_source=True, scope=dict(technology=["hybrid", "wind", "pv"]),
         owner="permitting lead"),
    dict(id="Z-014", document="GLR", edition="2023", parameter="licence above 50 MW",
         kind="equal", value=1, unit="-", status="project-dependent", verified=date(2026, 8, 1),
         official_source=True, scope={}, owner="permitting lead"),
]

LANGUAGE = {   # document: (official language consulted?, translation used, wording difference)
    "GCZ": (True, True, None),
    "TCR": (False, True, "translation 'should' where the official text says 'shall'"),
    "EP-117": (True, False, None),
    "GLR": (False, True, "translation omits a footnote on hybrid plants"),
    "CA-P": (True, False, None),
}

CLARIFICATIONS = [   # id, to, subject, sent, answered
    ("CQ-01", "TSOZ", "ride-through: GCZ 150 ms at 0 pu vs TCR trip after 100 ms",
     date(2027, 1, 10), None),
    ("CQ-02", "ERZ", "does the 50 MW licence threshold count export or installed MW?",
     date(2026, 12, 1), date(2027, 2, 10)),
    ("CQ-03", "Environment Agency", "noise limit: free field or at the facade?",
     date(2027, 2, 20), None),
    ("CQ-04", "TSOZ", "which edition of GCZ applies to an application filed in 2026?",
     date(2026, 11, 15), None),
]

CLAUSES = [   # one source text, classified (fictional GCZ 2024 extract)
    ("6.2", "The plant shall provide power factor 0.95 at the POC.", "normative"),
    ("6.2 Note 1", "Note: the operator may agree a different point of measurement.",
     "note"),
    ("6.3", "Reactive power should be shared between units in proportion.",
     "recommendation"),
    ("6.4", "The plant may use static compensation to meet 6.2.", "permission"),
    ("7.1", "Active power ramps shall not exceed 10 %/min of rated power.",
     "normative"),
    ("7.1 Example", "Example: a 100 MW plant ramps at most 10 MW a minute.",
     "example"),
    ("7.2", "Ramps shall be limited as appropriate during storms.", "normative"),
    ("8.4", "The plant shall stay connected for 150 ms at zero retained voltage.",
     "normative"),
    ("Annex C", "Informative: a method for model validation.", "informative annex"),
    ("Annex D", "Normative: data to submit with the application.", "normative annex"),
    ("9.1", "Telemetry shall be provided with adequate accuracy.", "normative"),
    ("9.2", "Telemetry will be received by the TSOZ control centre.", "statement"),
]
VAGUE = ("as appropriate", "adequate", "where practicable", "suitable", "sufficient")

AUTHORITIES = [   # topic, authority (fictional), level, status of identification
    ("generation licence", "ERZ", "national", "verified"),
    ("grid connection and studies", "TSOZ", "national", "verified"),
    ("environmental permit", "Environment Agency of Z", "national", "verified"),
    ("construction permit", "Province Q building office", "provincial", "verified"),
    ("land lease and access", "Province Q land office", "provincial", "verified"),
    ("water abstraction", "basin authority (which one?)", "regional", "to-confirm"),
    ("aviation obstacle", "Civil Aviation Authority of Z", "national", "verified"),
    ("cultural heritage", "Heritage Office of Z", "national", "project-dependent"),
    ("labour and safety", "Labour Inspectorate", "national", "verified"),
    ("fire and emergency", "Province Q fire service (or national?)", "provincial",
     "to-confirm"),
    ("transport of abnormal loads", "Roads Agency", "national", "verified"),
    ("telecommunications (radio links)", "", "national", "to-confirm"),
    ("tax registration and incentives", "Revenue Office of Z", "national",
     "project-dependent"),
    ("foreign exchange and repatriation", "Central Bank of Z", "national", "to-confirm"),
]

GCZ_CLAUSES = {   # clause -> versions (in force from, issue, text) - fictional
    "6.2": [(date(2024, 7, 1), "2024", "pf 0.95 at the POC from 20 to 100 % of rated P"),
            (date(2025, 7, 1), "A1", "pf 0.95 at the POC from 10 to 100 % of rated P")],
    "7.1": [(date(2024, 7, 1), "2024", "ramp at most 10 %/min of rated P"),
            (date(2026, 9, 1), "A2", "ramp at most 8 %/min above 50 MW")],
    "8.4": [(date(2024, 7, 1), "2024", "stay connected 150 ms at 0 pu retained voltage")],
    "9.3": [(date(2026, 9, 1), "A2", "4-second telemetry of P, Q, U at the POC")],
}
FILED = date(2026, 5, 10)          # Plant P's connection application (teaching)
CONNECT = date(2028, 3, 1)         # planned first energisation (teaching)

RESEARCH = {   # requirement -> fields of its research record (planted gaps)
    "Z-001": dict(official_ref="GCZ 2024 cl 6.2, TSOZ website", accessed="2026-11-02",
                  verifier="grid engineer", second_check="owner's engineer"),
    "Z-004": dict(official_ref="GCZ 2019 cl 7.1", accessed="2025-06-01",
                  verifier="controls engineer", second_check=""),
    "Z-006": dict(official_ref="EP-117 condition 14", accessed="2026-10-01",
                  verifier="environmental lead", second_check="permitting lead"),
    "Z-009": dict(official_ref="GCZ 2024 cl 8.4", accessed="2026-11-02",
                  verifier="grid engineer", second_check="owner's engineer"),
    "Z-010": dict(official_ref="TCR 2022 sec 5", accessed="2026-12-05",
                  verifier="grid engineer", second_check=""),
    "Z-011": dict(official_ref="", accessed="", verifier="consultant slide deck",
                  second_check=""),
    "Z-013": dict(official_ref="EA-Z art 12, official gazette 2021/44",
                  accessed="2026-08-01", verifier="permitting lead",
                  second_check="local counsel"),
    "Z-014": dict(official_ref="GLR 2023 art 3", accessed="2026-08-01",
                  verifier="permitting lead", second_check=""),
}

OWNERSHIP = {   # scenario: who builds and owns the 132 kV line (fictional)
    "O1 utility builds and owns the line": [],
    "O2 plant builds, transfers at COD": ["line design to TSOZ standard",
                                          "TSOZ witness of line tests",
                                          "transfer deed and as-built records",
                                          "defects period on the line"],
    "O3 plant builds and owns for life": ["line design to TSOZ standard",
                                          "TSOZ witness of line tests",
                                          "right-of-way under the transmission law",
                                          "transmission licence or exemption",
                                          "line maintenance and patrol obligations",
                                          "third-party connection to the line",
                                          "line decommissioning at the end"],
}

OWNERSHIP_BASE = "O1 utility builds and owns the line"   # decided 2026-06 (teaching)

FIELDS = ("clause", "edition", "status", "applicability", "consequence",
          "evidence", "owner", "approver", "verified", "revision")
RECORDS = {   # the register's columns per requirement (planted gaps)
    "Z-001": dict(clause="6.2", edition="2024", status="verified",
                  applicability="132 kV transmission", consequence="Q 32.9 Mvar at 100 MW",
                  evidence="ch 50 Q test", owner="grid engineer", approver="TSOZ",
                  verified="2026-11-02", revision="R3"),
    "Z-004": dict(clause="7.1", edition="2019", status="verified",
                  applicability="above 66 kV", consequence="PPC ramp 10 %/min",
                  evidence="", owner="controls engineer", approver="TSOZ",
                  verified="2025-06-01", revision="R1"),
    "Z-006": dict(clause="cond 14", edition="2026", status="verified",
                  applicability="all dwellings", consequence="noise model to 40 dB(A)",
                  evidence="ch 51 noise monitoring", owner="environmental lead",
                  approver="Environment Agency", verified="2026-10-01", revision="R3"),
    "Z-009": dict(clause="8.4", edition="2024", status="verified",
                  applicability="above 66 kV", consequence="unit FRT 150 ms",
                  evidence="ch 44 type test", owner="grid engineer", approver="",
                  verified="2026-11-02", revision="R3"),
    "Z-011": dict(clause="", edition="2019", status="to-confirm",
                  applicability="", consequence="", evidence="", owner="",
                  approver="", verified="", revision="R2"),
    "Z-013": dict(clause="art 12", edition="2021", status="verified",
                  applicability="all generation", consequence="licence before COD",
                  evidence="licence application", owner="permitting lead",
                  approver="ERZ", verified="2026-08-01", revision="R3"),
}

RACI = {   # requirement -> (prepares evidence, reviews, approves)
    "Z-001": ("EPC grid engineer", "owner's engineer", "TSOZ"),
    "Z-004": ("EPC controls engineer", "EPC controls engineer", "TSOZ"),
    "Z-006": ("env. consultant", "owner's env. lead", "Environment Agency"),
    "Z-009": ("converter maker", "owner's engineer", ""),
    "Z-012": ("transformer maker", "owner's engineer", "owner's engineer"),
    "Z-013": ("permitting lead", "local counsel", "ERZ"),
}

REV_R2 = {   # register revision R2 (2026-09) and R3 (2027-02): value, status
    "Z-001": dict(value=0.95, status="verified", edition="2024"),
    "Z-002": dict(value=0.90, status="project-dependent", edition="draft 2"),
    "Z-004": dict(value=10.0, status="verified", edition="2019"),
    "Z-006": dict(value=42.0, status="project-dependent", edition="draft"),
    "Z-011": dict(value=0.35, status="to-confirm", edition="2019"),
    "Z-015": dict(value=1, status="to-confirm", edition="-"),
}
REV_R3 = {
    "Z-001": dict(value=0.95, status="verified", edition="2024"),
    "Z-002": dict(value=0.93, status="project-dependent", edition="draft 3"),
    "Z-004": dict(value=10.0, status="verified", edition="2019"),
    "Z-006": dict(value=40.0, status="verified", edition="2026"),
    "Z-009": dict(value=150.0, status="verified", edition="2024"),
    "Z-010": dict(value=100.0, status="to-confirm", edition="2022"),
    "Z-011": dict(value=0.35, status="to-confirm", edition="2019"),
}
REV_NOTES = {"Z-015": "withdrawn: a bird-radar condition dropped from the final permit"}

INTERPRETATIONS = [   # id, requirement, reading, basis, agreed by, in writing?
    ("INT-01", "Z-001", "pf 0.95 at the POC = Q of 32.9 Mvar at 100 MW, both signs",
     "GCZ 6.2 + Note 1", "TSOZ", True),
    ("INT-02", "Z-006", "40 dB(A) at the facade, 22:00-06:00", "EP-117 cond 14",
     "phone call with the agency", False),
    ("INT-03", "Z-014", "50 MW threshold = export capacity 100 MW, so licence applies",
     "CQ-02 answer", "ERZ letter", True),
    ("INT-04", "Z-004", "ramp limit applies to the plant, not to each unit",
     "GCZ 7.1 wording", "meeting minutes, unsigned", False),
    ("INT-05", "Z-009", "150 ms counted from fault start to clearing", "GCZ 8.4",
     "", False),
]

FINANCE = [   # item, source type, status, who reviews (fictional Country Z)
    ("corporate income tax rate", "law", "verified", "local tax advisor"),
    ("tax depreciation of plant", "regulation", "to-confirm", "local tax advisor"),
    ("import duty on modules and turbines", "regulation", "project-dependent",
     "customs broker + local tax advisor"),
    ("production premium 5 u/MWh", "draft regulation", "to-confirm", "local counsel"),
    ("PPA tariff and indexation", "contract", "verified", "commercial lead + local counsel"),
    ("currency of payment and convertibility", "central-bank rule", "to-confirm",
     "local bank + local counsel"),
    ("repatriation of dividends", "law + central-bank rule", "to-confirm", "local counsel"),
    ("foreign ownership limit", "law", "verified", "local counsel"),
    ("security over land lease", "law", "project-dependent", "lenders' counsel"),
    ("compulsory insurances", "regulation", "verified", "insurance broker"),
    ("settlement of imbalance", "grid code", "verified", "commercial lead"),
    ("withholding tax on interest", "law", "to-confirm", "local tax advisor"),
]

LINKS = {   # requirement -> (document, records that use it)
    "Z-001": ("GCZ", ["ch 28 load-flow PLP-ELE-CAL-0014", "ch 27 Q budget", "ch 50 Q test"]),
    "Z-004": ("GCZ", ["ch 20 PPC ramp setting", "ch 50 ramp test"]),
    "Z-009": ("GCZ", ["ch 28 FRT study", "ch 44 converter type test", "ch 50 FRT record"]),
    "Z-006": ("EP-117", ["ch 33 noise model", "ch 51 noise monitoring"]),
}
