"""Chapter 39 - synthetic procurement data of Plant P (teaching values
A-425 to A-432). The suppliers, offers, audits and screenings are
fictional; nothing here describes a real company, country or product.

PACKAGE     the 33/0.6 kV PV unit transformers, 10 x 5.6 MVA Dyn11
            (after change C-017 of ch 38)
REQS        technical requirements, the critical ones marked
OFFERS      three offers U-A, U-B, U-C with price, losses, delivery,
            currency share, warranty, answers and priced deviations
AUDITS      factory capability audit scores of the three suppliers
DATA_ITEMS  supplier information deliverables and what each offer commits
LABOUR      labour due-diligence screen of suppliers and sub-suppliers
CONTRACTS   what each contract of the project relies on and what it covers
"""
from __future__ import annotations

from companion.ch39 import common  # noqa: F401  (puts plantp on the path)

PACKAGE = dict(units=10, s_mva=5.6, hv_kv=33.0, lv_kv=0.6, vector="Dyn11",
               uk_pct=7.0, need_week=34)
FINANCE = dict(energy_price=70.0, years=25, rate=0.075, load_loss_factor=0.20,
               ld_per_week=0.005, ld_cap=0.10, fx_allowance=0.08)   # (A-425)

REQS = {   # id -> (text, critical?)
    "T01": ("rating 5.6 MVA ONAN, 45 C ambient", True),
    "T02": ("vector group Dyn11", True),
    "T03": ("impedance 7.0 % +/- 10 %", True),
    "T04": ("guaranteed losses with tolerance", True),
    "T05": ("temperature rise within the class", True),
    "T06": ("routine tests on every unit, type test on one", True),
    "T07": ("witness: heat run, losses, insulation", True),
    "T08": ("sound power level at the limit", False),
    "T09": ("ester fluid, fire point above 300 C", False),
    "T10": ("off-circuit taps +/- 2 x 2.5 %", False),
    "T11": ("LV busbar for 8 cables per phase", False),
    "T12": ("tank and cooler coating class C4", False),
    "T13": ("monitoring relay, defined data link", False),
    "T14": ("data schedule per item I01-I14", True),
    "T15": ("spares: one set of bushings and gaskets", False),
    "T16": ("warranty at least 3 years", False),
    "T17": ("design calculations for short-circuit withstand", True),
    "T18": ("transport within 2.4 m width", False),
}

OFFERS = {   # price k u for 10 units; losses per unit kW; delivery week
    "U-A": dict(price=1_160.0, p0_kw=4.1, pk_kw=41.0, week=30, foreign=0.70,
                warranty_y=5, deviations=6.0,
                answers={r: "comply" for r in REQS} | {"T09": "deviate", "T13": "deviate"}),
    "U-B": dict(price=1_010.0, p0_kw=5.2, pk_kw=52.0, week=38, foreign=0.20,
                warranty_y=2, deviations=28.0,
                answers={r: "comply" for r in REQS} | {"T07": "deviate", "T14": "no",
                                                        "T16": "no", "T11": "deviate"}),
    "U-C": dict(price=1_080.0, p0_kw=4.5, pk_kw=45.0, week=33, foreign=0.90,
                warranty_y=3, deviations=12.0,
                answers={r: "comply" for r in REQS} | {"T12": "deviate", "T08": "deviate"}),
}

AUDIT_WEIGHTS = {"quality system": 2, "process control": 3, "test laboratory": 3,
                 "capacity": 2, "sub-supplier control": 2, "traceability": 2,
                 "labour and HSE": 2, "delivery record": 1}
AUDIT_FLOORS = {"process control": 3.0, "test laboratory": 3.0, "labour and HSE": 3.0}
AUDITS = {   # 0-5 (A-426)
    "U-A": {"quality system": 4, "process control": 4, "test laboratory": 4, "capacity": 3,
            "sub-supplier control": 3, "traceability": 4, "labour and HSE": 4,
            "delivery record": 4},
    "U-B": {"quality system": 3, "process control": 2, "test laboratory": 3, "capacity": 4,
            "sub-supplier control": 2, "traceability": 2, "labour and HSE": 3,
            "delivery record": 3},
    "U-C": {"quality system": 4, "process control": 4, "test laboratory": 3, "capacity": 2,
            "sub-supplier control": 3, "traceability": 4, "labour and HSE": 3,
            "delivery record": 2},
}

DATA_ITEMS = ["I01 unique ID and serial", "I02 data sheet as built", "I03 bill of materials",
              "I04 approved drawings and 3D model", "I05 routine test reports",
              "I06 type test report", "I07 calibration of test instruments",
              "I08 warranty certificate", "I09 maintenance plan", "I10 spares list with codes",
              "I11 fluid safety and environmental data", "I12 data in the owner's schema",
              "I13 update obligation for 10 years", "I14 right to use the data"]
DATA_COMMIT = {   # what each offer commits to deliver (True = committed and valid)
    "U-A": {k: True for k in DATA_ITEMS} | {"I13 update obligation for 10 years": False},
    "U-B": {k: True for k in DATA_ITEMS[:8]},
    "U-C": {k: True for k in DATA_ITEMS} | {"I12 data in the owner's schema": False,
                                            "I14 right to use the data": False},
}

LABOUR = [   # supplier or sub-supplier, tier, risk indicators (0-2 each), evidence kind
    ("U-A factory", 1, dict(sector=1, region=0, opacity=0, migrant=0), "audit + interviews"),
    ("U-A core steel", 2, dict(sector=1, region=1, opacity=1, migrant=0), "declaration"),
    ("U-B factory", 1, dict(sector=1, region=1, opacity=1, migrant=1), "declaration"),
    ("U-B copper winding wire", 2, dict(sector=2, region=2, opacity=2, migrant=1), "none"),
    ("U-C factory", 1, dict(sector=1, region=0, opacity=0, migrant=1), "audit"),
    ("U-C bushings", 2, dict(sector=1, region=1, opacity=1, migrant=0), "declaration"),
    ("site contractor", 1, dict(sector=2, region=0, opacity=0, migrant=2), "audit + interviews"),
]

CONTRACTS = {   # contract -> (topics it relies on others for, topics it covers) (A-431)
    "EPC": ({"OEM turbine power curve test", "grid compliance tests", "O&M spares at handover"},
            {"plant completion", "delay damages", "performance test of the plant",
             "grid compliance tests"}),
    "turbine OEM": ({"site access roads", "grid availability during tests"},
                    {"OEM turbine power curve test", "turbine availability guarantee",
                     "turbine warranty"}),
    "O&M": ({"O&M spares at handover", "as-built data", "turbine warranty"},
            {"plant availability guarantee", "spares holding", "service response"}),
    "PPA": ({"plant availability guarantee", "metering data"},
            {"price", "curtailment compensation"}),
    "grid connection": ({"protection settings of the plant"},
                        {"grid availability during tests", "metering data",
                         "connection date"}),
    "lenders": ({"lender-named insurance", "performance test of the plant",
                 "independent engineer access"}, {"loan conditions"}),
}
