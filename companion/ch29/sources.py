"""Chapter 29 - the site of Plant P for civil works (teaching values
A-349 to A-355; the site and layout of chapter 14, decision D-018).

Fictional ground investigation (ten boreholes, two seismic lines), a
synthetic 30-year record of rainfall and heat extremes, wells, and the
water demands of construction and operation. Everything here is
teaching data for a fictional site; a real project's values come from
its own investigation, its permits and its fire strategy.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np

from companion.ch29 import common  # noqa: F401  (puts plantp on the path)
from companion.ch14 import sources as s14

TURBINES = [(3600.0, 1500.0), (3600.0, 2100.0), (3600.0, 2700.0), (3600.0, 3300.0),
            (3600.0, 3900.0), (3600.0, 4500.0), (4800.0, 2700.0), (4800.0, 3300.0),
            (4800.0, 3900.0), (4800.0, 4500.0), (4800.0, 5100.0), (4800.0, 5700.0)]
SITE_SUB, GRID_SUB, ENTRANCE = s14.SITE_SUB, s14.GRID_SUB, s14.SITE_ENTRANCE
PV_BLOCK, WADI, SPRING = s14.PV_BLOCK, s14.WADI, s14.SPRING


# [start: borehole]
@dataclass
class Layer:
    top: float           # m below ground
    bottom: float
    soil: str
    spt_n: int | None    # blows / 300 mm, uncorrected (None: not tested)


@dataclass
class Borehole:
    name: str
    xy: tuple[float, float]
    layers: list[Layer]
    water_m: float | None            # groundwater depth, None: not recorded
    lab: set = field(default_factory=set)   # lab tests done
# [end: borehole]


BOREHOLES = [   # A-349 (fictional; deliberately incomplete for lesson D)
    Borehole("BH-01 (T01)", TURBINES[0], [Layer(0, 1.5, "silty sand, loose", 8),
             Layer(1.5, 7.0, "sand and gravel, dense", 34), Layer(7.0, 15.0, "weathered sandstone", 50)],
             6.5, {"grading", "moisture", "sulphate"}),
    Borehole("BH-02 (T03)", TURBINES[2], [Layer(0, 2.0, "silty sand, loose", 9),
             Layer(2.0, 8.0, "sand and gravel, dense", 31), Layer(8.0, 15.0, "weathered sandstone", 50)],
             7.0, {"grading", "moisture"}),
    Borehole("BH-03 (T05)", TURBINES[4], [Layer(0, 1.0, "silty sand", 10),
             Layer(1.0, 6.0, "sand and gravel, dense", 36)], None, {"grading"}),
    Borehole("BH-04 (T07)", TURBINES[6], [Layer(0, 2.5, "silty clay, soft", 4),
             Layer(2.5, 9.0, "sand, medium dense", 18), Layer(9.0, 15.0, "weathered sandstone", 50)],
             3.0, {"grading", "moisture", "Atterberg"}),
    Borehole("BH-05 (T09)", TURBINES[8], [Layer(0, 1.5, "silty sand", 11),
             Layer(1.5, 10.0, "sand and gravel, dense", 33), Layer(10.0, 15.0, "weathered sandstone", 50)],
             8.0, {"grading", "moisture", "sulphate", "chloride"}),
    Borehole("BH-06 (T11)", TURBINES[10], [Layer(0, 2.0, "silty sand", 9),
             Layer(2.0, 12.0, "sand and gravel, dense", 30), Layer(12.0, 15.0, "weathered sandstone", 50)],
             9.5, {"grading"}),
    Borehole("BH-07 (T12)", TURBINES[11], [Layer(0, 3.0, "silty sand with gypsum", 12),
             Layer(3.0, 15.0, "sand and gravel, dense", 35)], None, {"grading", "moisture"}),
    Borehole("BH-08 (substation)", SITE_SUB, [Layer(0, 1.0, "silty sand", 10),
             Layer(1.0, 10.0, "sand and gravel, dense", 32)], 7.5, {"grading", "moisture", "sulphate"}),
    Borehole("BH-09 (PV north)", (7600.0, 3000.0), [Layer(0, 0.8, "silty sand", 7),
             Layer(0.8, 6.0, "sand and gravel, dense", 29)], 6.0, {"grading", "corrosivity"}),
    Borehole("BH-10 (PV south)", (7600.0, 2400.0), [Layer(0, 1.2, "silty sand", 6),
             Layer(1.2, 6.0, "sand and gravel, dense", 27)], 5.5, {"grading"}),
]

SEISMIC = [   # two refraction lines: (name, crossover m, v1 m/s, v2 m/s), A-349
    ("SL-1 along the turbine rows", 34.0, 450.0, 2100.0),
    ("SL-2 across the wadi", 18.0, 380.0, 1600.0),
]

FOUNDATION_DEPTH = 3.5        # m, a typical gravity foundation (ch 30 decides)
NEEDED_LAB = {"grading", "moisture", "sulphate", "chloride"}     # concrete and design screening


@lru_cache(maxsize=1)
def extremes(seed: int = 291) -> dict:
    """Synthetic 30-year annual maxima (A-350): 1-hour and 24-hour
    rainfall (mm), daily maximum temperature (C), 3-s gust at 10 m (m/s)."""
    rng = np.random.default_rng(seed)
    g = lambda mu, beta: mu - beta * np.log(-np.log(rng.random(30)))  # noqa: E731
    return {"rain_1h": g(16.0, 6.0), "rain_24h": g(34.0, 12.0),
            "t_max": g(41.0, 1.2) + 0.03 * np.arange(30),          # warming trend
            "gust": g(27.0, 3.0)}


WELLS = {   # A-351 (teaching; a pumping test gives the real values)
    "W-1": dict(t_m2_s=1.5e-4, s=2e-4, safe_l_s=0.40, summer_factor=0.75),
    "W-2": dict(t_m2_s=6.0e-5, s=1e-4, safe_l_s=0.25, summer_factor=0.6),
}

DEMAND = {   # A-352: m3 a month (operations) and totals (construction)
    "module_area_m2": 280_000.0,          # 60 MWp of modules
    "modules": 4200 * 26,                  # ch 10 (D-013)
    "wash_l_module": 1.0,                  # truck washing, ch 10 (A-196, D-014)
    "washes": [0, 1, 1, 1, 2, 2, 2, 2, 1, 1, 1, 0],   # 14 a year = ch 10's 4 % trigger
    "staff": 20, "staff_l_day": 60.0,
    "construction_concrete_m3": 12 * 620.0 + 900.0,
    "water_per_m3_concrete": 0.18, "curing_per_m3": 0.10,
    "dust_l_m2_day": 1.5, "road_area_m2": 28_000 * 6.0, "dust_days": 300,
    "workers_peak": 450, "worker_months": 4534,   # ch 22's 18-month curve
    "worker_l_day": 70.0, "construction_months": 18,
}

def channel_invert(x: float, reach: float = 400.0) -> float:
    """Lowest ground within `reach` m (north-south) of the chapter 14 wadi
    line at east coordinate x: the channel bed. The line itself may sit on
    a bank - the 50 m terrain puts the channel up to 175 m beside it."""
    yw = float(np.interp(x, [WADI[0][0], WADI[1][0]], [WADI[0][1], WADI[1][1]]))
    ys = np.arange(yw - reach, yw + reach + 1, 25.0)
    return float(s14.GRID.interp(s14.terrain(), np.full_like(ys, x), ys).min())


WASH_M3 = DEMAND["modules"] * DEMAND["wash_l_module"] / 1000    # treated water a wash

FIRE = dict(reserve_m3=None, note="from the fire strategy and the authority (U-105)")
SOIL = dict(r_factor=300.0, k_factor=0.30)    # A-353, MJ mm/(ha h yr), t ha h/(ha MJ mm)
