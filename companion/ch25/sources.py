"""Chapter 25 - teaching data for Plant P's transformers and export
substation (A-326 to A-330): the two 63 MVA 132/33 kV main transformers,
two bids with different losses, the unit transformers, test results for
the dossier review, and failure data for the bus arrangements.

Values are illustrative of their kind, not a maker's data or a
standard's tolerance.
"""
from __future__ import annotations

from companion.ch25 import common  # noqa: F401  (puts plantp on the path)

# [start: main]
MAIN = dict(   # one main transformer (A-326)
    s_mva=63.0, hv_kv=132.0, lv_kv=33.0, vector="YNd11", cooling="ONAN/ONAF",
    s_onan_mva=50.0, uk_pct=12.0, p0_kw=35.0, pk_kw=250.0, i0_pct=0.20,
    taps=(-10.0, 10.0, 1.25), oil_m3=22.0, mass_t=95.0, transport_t=72.0)
BIDS = {   # two offers for the same rating (A-327), price in k u
    "bid A (low loss)": dict(price=1_950.0, p0_kw=28.0, pk_kw=215.0),
    "bid B (low price)": dict(price=1_700.0, p0_kw=42.0, pk_kw=290.0),
}
# [end: main]

UNIT = {   # 33 kV unit transformers (A-328)
    "PV block, oil, outdoor skid": dict(s_mva=5.5, p0_kw=4.5, pk_kw=45.0, oil_m3=2.6),
    "turbine, dry type, in tower": dict(s_mva=5.6, p0_kw=7.0, pk_kw=50.0, oil_m3=0.0),
}

# [start: dossier]
DOSSIER = [   # quantity, guaranteed or declared, measured, tolerance (A-329)
    ("no-load loss kW", 35.0, 36.1, ("max", 0.15)),
    ("load loss kW at 75 C", 250.0, 262.0, ("max", 0.15)),
    ("total loss kW", 285.0, 298.1, ("max", 0.10)),
    ("impedance % (principal tap)", 12.0, 13.4, ("band", 0.075)),
    ("ratio error % (principal tap)", 0.0, 0.3, ("abs", 0.5)),
    ("no-load current %", 0.20, 0.24, ("max", 0.30)),
    ("top-oil rise K", 60.0, 57.0, ("limit", 0.0)),
    ("winding rise K", 65.0, 68.0, ("limit", 0.0)),
]
# [end: dossier]

BUS = {   # failure data for bus arrangements (A-330): per year, repair hours
    "breaker": (0.01, 72.0), "busbar section": (0.005, 24.0),
    "line": (0.042, 12.0), "transformer": (0.015, 4_380.0),
}
