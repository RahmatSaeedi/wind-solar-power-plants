"""Chapter 37 - the operating year of Plant P (synthetic, teaching values
A-409 to A-416).

The expected hourly series come from the energy model 15.1 of chapter 15
(data pack year, scenario S0). The "actual" year is synthetic: the model's
output with hourly noise and four planted problems, one a month, for the
monitoring lessons to find:

  April     soiling builds up over the month, cleaned on the last day
  June      PV block B07 (a tenth of the PV) out for 9 days
  August    grid operator's export limit of 80 MW for 40 sunny hours
  October   the plane-of-array pyranometer reads 8 % low for 20 days

Nothing here is measured; the faults are planted so they can be found.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from companion.ch37 import common  # noqa: F401  (puts plantp on the path)
from companion.ch15 import sources as s15

P_DC_KWP = 60_060.0                 # PV DC rating (ch 10)
EXPORT_MW = 100.0
DAY_H = 24


@lru_cache(maxsize=2)
def operating_year(seed: int = 371) -> dict:
    """Hourly expected and synthetic actual series (MW, W/m2)."""
    py = s15.plant_year()
    rng = np.random.default_rng(seed)
    hours = np.arange(8760)
    day = hours // DAY_H
    month = py["month"]
    poa_true = py["pv_stc"] / 60.06 * 1000.0                 # W/m2 on the array
    pv_exp = py["pv_av"].copy()                               # MW expected at MV
    w_exp = py["w_av"].copy()
    noise = 1 + rng.normal(0, 0.02, 8760)
    pv_act = np.clip(pv_exp * noise, 0, None)
    w_act = np.clip(w_exp * (1 + rng.normal(0, 0.03, 8760)), 0, None)
    # April: soiling grows from 0 to 6 % over the month, cleaned at its end
    apr = month == 3
    d0 = day[apr].min()
    soil = np.zeros(8760)
    soil[apr] = 0.06 * (day[apr] - d0) / 29
    pv_act *= 1 - soil
    # June: block B07 (10 % of the PV) out for 9 days
    out = (day >= 160) & (day < 169)
    pv_act[out] *= 0.9
    # October: pyranometer reads 8 % low for 20 days (the plant is fine)
    poa_sensor = poa_true.copy()
    bad = (day >= 285) & (day < 305)
    poa_sensor[bad] *= 0.92
    # August: export limit of 80 MW in the 40 highest-output hours
    total = pv_act + w_act
    aug = np.where(month == 7)[0]
    top = aug[np.argsort(total[aug])[-40:]]
    limit = np.full(8760, EXPORT_MW)
    limit[top] = 80.0
    scale = np.minimum(1.0, limit / np.maximum(total, 1e-9))
    pv_del, w_del = pv_act * scale, w_act * scale
    curtailed = total - (pv_del + w_del)
    return dict(month=month, day=day, poa_true=poa_true, poa_sensor=poa_sensor,
                pv_exp=pv_exp, w_exp=w_exp, pv_act=pv_del, w_act=w_del,
                curtailed=curtailed, limit=limit, soil=soil, outage=out, sensor_bad=bad,
                t_air=s15.hourly_inputs()[4])


MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
