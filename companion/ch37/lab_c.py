"""Chapter 37, lab C (worked example): a year of monthly operating data of
Plant P, with four planted problems, read like an analyst - monthly PR
and energy against the model, then the daily signature of each suspect
month: soiling, an inverter outage, curtailment, a sensor fault.

Run from the project root:   python -m companion.ch37.lab_c
Writes companion/ch37/expected/c_*.txt and diagrams/data/ch37-*.csv.
Synthetic operating year (A-409); the model is ch 15's 15.1.
"""
from __future__ import annotations

import numpy as np

from companion.ch37 import sources as src
from companion.ch37.common import csv, emit
from plantp import performance as pf


def monthly() -> None:
    y = src.operating_year()
    lines = ["the operating year by month (synthetic; PV at MV, model 15.1)",
             "  month  POA kWh/m2  PV MWh   model MWh   ratio   PR     curtailed MWh"]
    rows = []
    for m in range(12):
        sel = y["month"] == m
        h = y["poa_sensor"][sel].sum() / 1000
        e = y["pv_act"][sel].sum()
        ex = y["pv_exp"][sel].sum()
        pr = pf.performance_ratio(e * 1000, src.P_DC_KWP, h)
        cur = y["curtailed"][sel].sum()
        rows.append((m + 1, round(pr, 4), round(e / ex, 4)))
        lines.append(f"  {src.MONTHS[m]:5s}  {h:10.1f}  {e:7.0f}   {ex:9.0f}   {e / ex:5.3f}"
                     f"   {pr:5.3f}  {cur:13.1f}")
    csv("ch37-monthly.csv", "m,pr,ratio", rows)
    lines += ["  four months stand out: April and June lose energy against",
              "  the model, August has the most curtailed energy - energy",
              "  the plant could have made - and October's PR is too good:",
              "  a plant does not suddenly beat its own model; its sensor",
              "  does. Curtailment by the 100 MW export limit appears in",
              "  most months (ch 15) and is not a fault"]
    emit("c_monthly", lines)


# [start: daily]
def daily_ratio(y, m):
    """Per day of month m: (day, actual/model, PR on the plant's sensor,
    PR on the reference sensor)."""
    days = np.unique(y["day"][y["month"] == m])
    out = []
    for d in days:
        s = y["day"] == d
        ex = y["pv_exp"][s].sum()
        e_kwh = y["pv_act"][s].sum() * 1000
        h_plant = max(y["poa_sensor"][s].sum() / 1000, 1e-6)
        h_ref = max(y["poa_true"][s].sum() / 1000, 1e-6)
        out.append((d, y["pv_act"][s].sum() / ex if ex > 1 else np.nan,
                    pf.performance_ratio(e_kwh, src.P_DC_KWP, h_plant),
                    pf.performance_ratio(e_kwh, src.P_DC_KWP, h_ref)))
    return np.array(out)
# [end: daily]


def signatures() -> None:
    y = src.operating_year()
    apr, jun, oct_ = daily_ratio(y, 3), daily_ratio(y, 5), daily_ratio(y, 9)
    slope = np.polyfit(np.arange(len(apr)), apr[:, 1], 1)[0] * 100
    j_in = jun[(jun[:, 0] >= 160) & (jun[:, 0] < 169), 1].mean()
    j_out = jun[(jun[:, 0] < 160) | (jun[:, 0] >= 169), 1].mean()
    o_bad = oct_[(oct_[:, 0] >= 285) & (oct_[:, 0] < 305)]
    aug = y["month"] == 7
    limited = aug & (y["limit"] < src.EXPORT_MW)
    at_limit = int(np.sum(limited))
    cur = y["curtailed"][limited].sum()

    csv("ch37-april.csv", "d,ratio", [(int(d), round(r, 4)) for d, r, *_ in apr])
    csv("ch37-june.csv", "d,ratio", [(int(d), round(r, 4)) for d, r, *_ in jun])
    csv("ch37-october.csv", "d,pr_sensor,pr_ref",
        [(int(d), round(a, 4), round(b, 4)) for d, _, a, b in oct_])
    lines = ["the daily signature of each suspect month (synthetic)",
             f"  April: actual/model falls {abs(slope):.2f} % a day, all month, all",
             "    blocks alike, back to normal after the cleaning: SOILING",
             f"  June: actual/model {j_in:.3f} for 9 days, {j_out:.3f} otherwise - a step",
             "    of a tenth, block B07 at zero in its own data: INVERTER OUTAGE",
             f"  August: {at_limit} hours held at the 80 MW limit, {cur:.0f} MWh not",
             "    taken; the set-point log shows the grid operator's limit:",
             "    CURTAILMENT - an external loss, excluded from availability",
             f"  October: PR on the plant's sensor {o_bad[:, 2].mean():.3f} against"
             f" {o_bad[:, 3].mean():.3f}",
             "    on the reference sensor for 20 days, energy unchanged:",
             "    SENSOR FAULT - the plant is fine, the pyranometer is not",
             "  each cause leaves a different shape: a slope, a step, a",
             "  flat top, a jump in PR without a jump in energy"]
    emit("c_signatures", lines)


if __name__ == "__main__":
    monthly()
    signatures()
