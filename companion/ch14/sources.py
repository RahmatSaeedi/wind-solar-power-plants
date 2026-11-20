"""Chapter 14 - the synthetic Plant P site (A-259, seed 151), in a local
projected frame: x east and y north in metres from the south-west corner
of a 13 km by 7 km screening window; ground heights above sea level.

* terrain: a plain rising gently to the east, a north-south ridge in the
  west (about 70 m), a dry river bed (wadi) crossing in the south, small
  smoothed undulations;
* layers: the existing road and village track, an existing 20 kV line, the
  village and four isolated dwellings (one a seasonal herders' camp), a
  spring and its irrigation channel, a raptor nest on the ridge cliff, a
  seasonal wetland in the wadi, a cemetery and a caravanserai ruin;
* land use and tenure (as reported by the screening survey, to be verified
  with the users): state rangeland, two private farms, a customary seasonal
  grazing area, village lands, farmland strips along the export corridor;
* the 132 kV grid substation at the east edge of the window;
* two candidate wind layouts of twelve WT-5.0-150 (ridge, plain), a PV
  block and the on-site substation.

Every layer is fictional; none describes a real place, owner or community.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np
from scipy import ndimage

from companion.ch14 import common  # noqa: F401  (puts plantp on the path)
from plantp import siting as st

GRID = st.Grid(0.0, 0.0, 50.0, 260, 140)
HUB, RADIUS = 100.0, 75.0
TIP = HUB + RADIUS


@lru_cache(maxsize=1)
def terrain() -> np.ndarray:
    rng = np.random.default_rng(151)
    x, y = GRID.mesh()
    z = 1180.0 + 0.004 * x
    ridge = 70.0 * np.exp(-((x - 1800.0) / 420.0) ** 2)
    ridge *= 1 / (1 + np.exp(-(y - 1400.0) / 250.0)) * 1 / (1 + np.exp((y - 6600.0) / 250.0))
    wadi = -8.0 * np.exp(-((y - 1200.0 - 0.05 * (x - 4000.0)) / 90.0) ** 2)
    bumps = ndimage.gaussian_filter(rng.standard_normal(x.shape), 8) * 60.0
    return z + ridge + wadi + bumps


ROAD = [(0.0, 600.0), (13000.0, 600.0)]
TRACK = [(7600.0, 600.0), (7600.0, 6200.0)]
LINE_20KV = [(0.0, 700.0), (7600.0, 700.0), (7600.0, 6100.0)]
WADI = [(0.0, 1000.0), (13000.0, 1450.0)]
GRID_SUB = (12700.0, 3000.0)
SITE_SUB = (6500.0, 3500.0)
SITE_ENTRANCE = (6500.0, 600.0)

DWELLINGS = {
    "farmhouse A": (5600.0, 2200.0),
    "herders' camp B (seasonal)": (3200.0, 5200.0),
    "farmhouse C": (6800.0, 1500.0),
    "roadside house D": (2600.0, 750.0),
}

SPRING = (5600.0, 5400.0)
CHANNEL = [(5600.0, 5400.0), (5700.0, 4200.0), (5600.0, 3300.0), (5600.0, 2300.0)]
NEST = (1850.0, 5200.0)
WETLAND = (4200.0, 1250.0)
CEMETERY = (6000.0, 4800.0)
RUIN = (9800.0, 3500.0)

TENURE = {
    "private farm 1": [(4900, 1700), (6300, 1700), (6300, 2900), (4900, 2900)],
    "private farm 2": [(6400, 1000), (7400, 1000), (7400, 2000), (6400, 2000)],
    "customary grazing (Apr-Oct)": [(2400, 3800), (5000, 3800), (5000, 6800), (2400, 6800)],
    "village lands": [(6800, 5200), (9000, 5200), (9000, 7000), (6800, 7000)],
    "corridor farmland": [(9000, 2300), (12400, 2300), (12400, 3900), (9000, 3900)],
}
# everything else inside the window: state rangeland


@lru_cache(maxsize=1)
def village() -> np.ndarray:
    rng = np.random.default_rng(152)
    return np.array([7600.0, 6250.0]) + rng.normal(0, 150.0, (25, 2))


def all_dwellings() -> list[tuple[str, tuple[float, float]]]:
    out = [(k, v) for k, v in DWELLINGS.items()]
    out += [(f"village house {k + 1}", (float(a), float(b)))
            for k, (a, b) in enumerate(village())]
    return out


def layouts() -> dict[str, np.ndarray]:
    """Two candidate layouts of twelve turbines (A-259)."""
    ridge = np.array([[1800.0, 1900.0 + 420.0 * k] for k in range(12)])
    plain = np.array([[x, 2700.0 + 600.0 * k] for x in (3600.0, 4800.0)
                      for k in range(6)])
    return {"W1 ridge (1 row)": ridge, "W2 plain (2 rows)": plain}


PV_BLOCK = [(6900, 2300), (8300, 2300), (8300, 3150), (6900, 3150)]
