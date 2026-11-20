"""Chapter 21 - economic and financial data of Plant P (all teaching
values, A-304 to A-310): capital costs from chapter 18's screening costs
(A-287) plus development, owner's costs and contingency; operating
costs including water and cleaning; replacements; decommissioning; the
power purchase agreement; finance and tax terms; scenarios.

No value here is a market price, a tax rule of any country or a lender's
requirement: each is a labelled teaching assumption that a real project
replaces with quotes, law and term sheets (chapters 38-39, 55-57).
Money in k u (thousand units) unless stated.
"""
from __future__ import annotations

import numpy as np

from companion.ch21 import common  # noqa: F401  (puts plantp on the path)
from companion.ch18 import sources as s18

C18 = s18.COST

# [start: capex]
CAPEX = {                                    # k u, S1 (A-304)
    "wind 60 MW": 60 * C18["wind_per_mw"],
    "PV 50 MW AC": 50 * C18["pv_per_mw_ac"],
    "substation and line": C18["connection"],
    "battery 20 MW / 40 MWh": (20 * C18["bess_per_mw"]
                               + 40 * C18["bess_per_mwh"]),
    "development and permits": 3_000.0,
    "owner's engineering": 4_000.0,
}
CONTINGENCY = 0.05                           # of the items above
# [end: capex]

# [start: opex]
OPEX = {                                     # k u a year, year-1 money (A-305)
    "wind O&M (30 k u/MW)": 1_800.0,
    "PV O&M (10 k u/MW)": 500.0,
    "battery O&M": 160.0,
    "substation and line": 250.0,
    "land lease": 450.0,
    "insurance": 520.0,
    "water and cleaning": 140.0,
    "asset management, admin": 450.0,
}
REPLACE = {                           # k u, year-1 money, by year (A-306)
    8: ("battery augmentation 4 MWh", 600.0),
    12: ("PV inverter refurbishment", 1_500.0),
    13: ("battery augmentation 4 MWh", 600.0),
    15: ("wind main components reserve", 1_800.0),
}
DECOM = {"cost": 4_000.0, "salvage": 1_500.0}    # k u, year-1 money (A-306)
# [end: opex]

# [start: terms]
TERMS = {                                    # teaching finance terms (A-307..A-309)
    "years": 25, "construction": (0.4, 0.6),     # two years before COD
    "inflation": 0.025,
    "tariff": 70.0, "tariff_index": 0.02, "ppa_years": 20,   # u/MWh, nominal
    "merchant_real": 45.0,                   # u/MWh after the PPA, year-1 money
    "curtail_uncomp": 0.01,                  # share of energy curtailed unpaid
    "tax": 0.25, "dep_years": 20,
    "receivable_days": 45, "payable_days": 30,
    "rate": 0.06, "fee": 0.015, "tenor": 15,
    "dscr_p50": 1.30, "dscr_p90": 1.20, "max_gearing": 0.75,
    "dsra_months": 6, "lockup": 1.10, "default": 1.05,
    "wacc": 0.075, "cost_of_equity": 0.10,
}
P90_1Y = 276.0 / 295.14                      # D-020: P90 one year / P50
SHIFT_VALUE = 469.0                          # k u a year, ch 20 (prices ~50 u)
# [end: terms]


def capex_total(with_battery: bool = True) -> float:
    items = {k: v for k, v in CAPEX.items()
             if with_battery or not k.startswith("battery")}
    return sum(items.values()) * (1 + CONTINGENCY)


def energy_series(years: int = 25, scale: float = 1.0) -> np.ndarray:
    """Net energy at the POC (GWh) by operating year, S0, model 15.1 with
    PV degradation 0.5 %/yr (chapter 15 lifetime lesson, A-275)."""
    y = np.arange(1, years + 1)
    f = (1 - 0.005 * y) / (1 - 0.005)
    return scale * (295.14 - 0.962 * 108.36 * (1 - f))
