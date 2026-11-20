"""Chapter 16 - the uncertainty budget of Plant P: standard uncertainties
(one sigma) of the long-term energy at MV, by component, built on the
budgets of chapters 12-14 and the model of chapter 15 (D-019). Values
not taken from an earlier chapter are teaching values (A-277 wind,
A-278 PV and plant, A-279 correlations); they are not a recommendation.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache

import numpy as np

from companion.ch16 import common  # noqa: F401  (puts plantp on the path)
from companion.ch15 import examples_h as eh, sources as s15

SENS = 1.82                            # energy per speed: farm curve of
                                       # model 15.1 (examples_ab); ch 13 had
                                       # 1.60 for one turbine without wakes


@dataclass(frozen=True)
class Part:
    name: str
    group: str        # measurement, long-term, extrapolation, model, ...
    u: float          # relative standard uncertainty of the energy
    kind: str         # sampling distribution
    source: str


# [start: budget]
N, LN = "normal", "lognormal"
WIND = [
    Part("anemometer calibration, mounting", "measurement",
         SENS * math.hypot(0.010, 0.010), N, "ch 13, A-254"),
    Part("long-term correction and period", "long-term",
         SENS * math.hypot(0.020, 0.035 / math.sqrt(20)), N, "ch 13, A-254"),
    Part("cross-prediction to the turbines", "extrapolation",
         SENS * 0.0135, N, "ch 14, A-265"),
    Part("wake model", "model", 0.010, N, "A-277"),
    Part("hub density", "model", 0.003, N, "A-277"),
    Part("power curve", "equipment", 0.020, N, "A-277"),
    Part("availability (energy-based)", "operation", 0.010, N, "A-277"),
    Part("icing and environmental stops", "operation", 0.005, N, "A-277"),
]
PV = [
    Part("irradiance sensor, maintenance", "measurement",
         math.hypot(0.020, 0.010), N, "ch 12, A-245"),
    Part("long-term correction and period", "long-term",
         math.hypot(0.015, 0.006), N, "ch 12, A-245"),
    Part("transposition model", "model", 0.010, N, "A-278"),
    Part("PV model (temperature, angle, light)", "model", 0.015, N, "A-278"),
    Part("module power (flash-test sample)", "equipment", 0.010, N,
         "A-278"),
    Part("inverter efficiency", "equipment", 0.003, N, "A-278"),
    Part("degradation, first year", "equipment", 0.003, N, "A-278"),
    Part("soiling and cleaning", "operation", 0.005, N, "A-278"),
    Part("availability", "operation", 0.005, N, "A-278"),
]
PLANT = [
    Part("electrical losses", "model", 0.003, N, "A-278"),
    Part("grid outages, ordered curtailment", "operation", 0.003, LN,
         "A-278"),
]
R_WIND_PV = 0.0                        # long-term parts (A-279)
# [end: budget]


@lru_cache(maxsize=1)
def base() -> dict:
    """P50 series and year-to-year terms from chapter 15."""
    r = s15.plant_year()
    _, wy, py = eh.iav_years()
    iav_w = float(np.std(wy, ddof=1) / np.mean(wy))
    iav_p = float(np.std(py, ddof=1) / np.mean(py))
    r_iav = float(np.corrcoef(wy, py)[0, 1])
    return {"r": r, "w": float(r["w_av"].sum()) / 1e3,
            "pv": float(r["pv_av"].sum()) / 1e3,
            "net": float(r["net"].sum()) / 1e3, "iav_w": iav_w, "iav_p": iav_p,
            "r_iav": r_iav, "years_w": wy, "years_p": py}


def u_group(parts) -> float:
    return math.sqrt(sum(p.u ** 2 for p in parts))


def sigmas() -> dict:
    """Long-term and year-to-year standard uncertainties in GWh at MV."""
    b = base()
    mv = b["w"] + b["pv"]
    s_w = u_group(WIND) * b["w"]
    s_p = u_group(PV) * b["pv"]
    s_pl = u_group(PLANT) * mv
    lt = math.sqrt(s_w ** 2 + s_p ** 2 + 2 * R_WIND_PV * s_w * s_p
                   + s_pl ** 2)
    i_w, i_p = b["iav_w"] * b["w"], b["iav_p"] * b["pv"]
    iav = math.sqrt(i_w ** 2 + i_p ** 2 + 2 * b["r_iav"] * i_w * i_p)
    return {"s_w": s_w, "s_p": s_p, "s_pl": s_pl, "lt": lt, "i_w": i_w,
            "i_p": i_p, "iav": iav, "mv": mv, "ratio": b["net"] / mv}
