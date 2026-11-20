"""Chapter 17 - synthetic loads and network data for Plant P (teaching
values; A-284 loads, A-285 network). Nothing here describes a real grid.

Loads, MW, hourly for the data-pack year (Jan 1 taken as a Monday):
  regional: the area fed by the 132/33 kV grid substation (town with
    cooling and heating, daytime irrigation pumping April-September,
    small industry on weekdays), with 3 % random variation;
  plant:    Plant P's own loads in three classes;
  factory:  an industrial customer for the self-supply variant.
Network: the 7.06 km export line of chapter 14 to the grid substation.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from companion.ch17 import common  # noqa: F401  (puts plantp on the path)
from companion.ch13 import sources as s13
from plantp import datapack

# [start: network]
NETWORK = {                            # teaching values (A-285)
    "line_km": 7.06,                   # chapter 14 least-cost route
    "r_ohm_km": 0.12, "x_ohm_km": 0.40,
    "line_rating_mva": 140.0,
    "v_kv": 132.0,
    "s_sc_mva": 1500.0,                # short-circuit power at the POC
    "upstream_mw": 90.0,               # export the 132 kV network beyond
                                       # the grid substation can take
    "trafo_mva": 2 * 63.0,             # grid substation 132/33 kV
}
# [end: network]

# plant's own loads, kW (A-284): (name, class, kW, hours a day)
PLANT_LOADS = [
    ("protection, control, telecom (UPS)", "critical", 45, 24),
    ("SCADA servers and network", "critical", 20, 24),
    ("battery container cooling (S1)", "critical", 120, 24),
    ("substation lighting and security", "critical", 15, 12),
    ("turbine auxiliaries (12 WTGs, mean)", "controllable", 230, 24),
    ("cleaning robots charging", "controllable", 60, 8),
    ("water pumping and treatment", "controllable", 40, 10),
    ("buildings cooling and heating", "controllable", 50, 14),
    ("workshop and stores", "interruptible", 35, 9),
    ("staff housing", "interruptible", 25, 16),
]


@lru_cache(maxsize=1)
def calendar():
    h = datapack.load_hourly()
    hour = np.arange(8760) % 24
    day = np.arange(8760) // 24
    dow = day % 7                                      # 0 = Monday
    month = h.index.month.to_numpy() - 1
    t = h["t_air_c"].to_numpy(float)
    return hour, dow, month, t


def _bump(hour, centre, width):
    d = np.minimum(np.abs(hour - centre), 24 - np.abs(hour - centre))
    return np.exp(-0.5 * (d / width) ** 2)


# [start: regional]
@lru_cache(maxsize=1)
def regional(seed: int = 173) -> dict:
    """Components and total of the regional load (MW)."""
    hour, dow, month, t = calendar()
    rng = np.random.default_rng(seed)
    town = (14.0 + 5.0 * _bump(hour, 8, 1.5) + 9.0 * _bump(hour, 20, 2.0)
            + 0.9 * np.clip(t - 24.0, 0, None)
            + 0.5 * np.clip(12.0 - t, 0, None))
    season = (month >= 3) & (month <= 8)
    pump = np.where(season & (hour >= 6) & (hour < 18), 8.0, 0.0)
    work = (dow < 5) & (hour >= 7) & (hour < 19)
    industry = np.where(work, 12.0, 4.0)
    noise = 1 + 0.03 * s13.ar1(8760, 3.0, rng)
    total = (town + pump + industry) * noise
    return {"town": town * noise, "pump": pump * noise,
            "industry": industry * noise, "total": total}
# [end: regional]


@lru_cache(maxsize=1)
def regional_15min(seed: int = 174) -> np.ndarray:
    """Quarter-hour values: the hourly load with intra-hour variation of
    4 % (A-284) that keeps each hour's mean."""
    rng = np.random.default_rng(seed)
    p = np.repeat(regional()["total"], 4)
    e = 0.04 * rng.standard_normal(len(p))
    e = e - np.repeat(e.reshape(-1, 4).mean(axis=1), 4)
    return p * (1 + e)


@lru_cache(maxsize=1)
def factory(seed: int = 175) -> np.ndarray:
    """A cement-like factory: 22 MW running, 6 MW on Fridays (weekly
    stop), 3 MW during a two-week overhaul in March (A-284)."""
    hour, dow, month, _ = calendar()
    rng = np.random.default_rng(seed)
    p = np.where(dow == 4, 6.0, 22.0)
    day = np.arange(8760) // 24
    p = np.where((day >= 66) & (day < 80), 3.0, p)
    return p * (1 + 0.04 * rng.standard_normal(8760))


def plant_loads_hourly() -> dict:
    """The plant's own loads by class, MW, hourly (simple daily windows:
    lights at night, cleaning at night, pumping and workshop by day)."""
    hour, *_ = calendar()
    windows = {"substation lighting and security": (hour >= 18) | (hour < 6),
               "cleaning robots charging": (hour >= 22) | (hour < 6),
               "water pumping and treatment": (hour >= 7) & (hour < 17),
               "buildings cooling and heating": (hour >= 7) & (hour < 21),
               "workshop and stores": (hour >= 8) & (hour < 17),
               "staff housing": (hour >= 6) & (hour < 22)}
    out = {"critical": np.zeros(8760), "controllable": np.zeros(8760),
           "interruptible": np.zeros(8760)}
    for name, cls, kw, _ in PLANT_LOADS:
        on = windows.get(name, np.ones(8760, bool))
        out[cls] += np.where(on, kw / 1000.0, 0.0)
    return out
