"""Chapter 28, lesson G: the export system in the studies - the 132 kV
line's rating hour by hour against the plant's export, N-1 cases inside
the plant with the energy at risk, sensitivity to the line and grid
data, and who owns which piece of the export system's data.

Run from the project root:   python -m companion.ch28.examples_g
Writes companion/ch28/expected/g_*.txt and diagrams/data/ch28-*.csv.
Teaching values (A-345; heat balance as ch 24).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch28 import register as reg
from companion.ch28 import sources as src
from companion.ch28.common import csv, emit


# [start: rating]
def line_amps(t_air, v_wind, ghi, t_c: float = 75.0):
    """Rating (A) of the teaching 132 kV conductor from its heat balance
    (as ch 24) with the hour's air temperature, wind across the line
    and sunshine."""
    d, eps, alpha = 0.0245, 0.5, 0.5
    r_ac = 0.10e-3 * (1 + 0.00403 * (t_c - 20))
    t4 = (t_c + 273) ** 4 - (t_air + 273) ** 4
    p_rad = math.pi * d * eps * 5.67e-8 * t4
    h = 3.9 + 8.8 * v_wind ** 0.6 if v_wind > 0 else 3.0
    p_conv = math.pi * d * h * (t_c - t_air)
    return math.sqrt(max(p_conv + p_rad - alpha * d * ghi, 0) / r_ac)
# [end: rating]


def line_year() -> None:
    from companion.ch15 import sources as s15
    hdf, v100, _, _, t_air, _ = s15.hourly_inputs()
    ghi = hdf["ghi_wm2"].to_numpy(float)
    p = np.clip(s15.plant_year()["delivered"], 0, None)
    amps = p * 1e6 / (math.sqrt(3) * 132e3)
    static = line_amps(35.0, 0.6, 1000.0)
    lines = ["the 132 kV line's rating hour by hour against the plant's export (one year)",
             f"  static rating at 35 C, 0.6 m/s, full sun: {static:.0f} A; full export 437 A",
             "  wind across the line = factor x hub wind x (12/100)^0.2",
             "  factor   lowest rating A   hours < 437 A   hours over   least margin A"]
    keep = None
    for fac in (0.6, 0.25):
        v_line = fac * v100 * (12 / 100) ** 0.2
        rating = np.array([line_amps(a, b, c) for a, b, c in zip(t_air, v_line, ghi)])
        over = amps > rating
        k = int(np.argmin(rating - amps))
        lines.append(f"  {fac:6.2f}   {rating.min():15.0f}   {int((rating < 437).sum()):13d}"
                     f"   {int(over.sum()):10d}   {rating[k] - amps[k]:14.0f}")
        if keep is None:
            keep = (rating, k, v_line)
    rating, k, v_line = keep
    low = rating < np.percentile(rating, 5)
    lines += [f"  least margin (factor 0.6): {t_air[k]:.0f} C, {v_line[k]:.1f} m/s at the line,"
              f" sun {ghi[k]:.0f} W/m2,",
              f"  export {p[k]:.0f} MW = {amps[k]:.0f} A against {rating[k]:.0f} A",
              f"  the 5 % of hours with the lowest rating average {p[low].mean():.0f} MW of export",
              f"  (year: {p.mean():.0f} MW) and never reach 437 A: the wind that brings",
              "  full export also cools the line - the hot, still, sunny",
              "  hour of ch 24 comes with PV output only; even with wind",
              "  along the line (factor 0.25) no hour binds in this year,",
              "  but the least margin falls by a quarter: the study asks for",
              "  the line's real orientation and keeps a weather-based limit",
              "  in the controller as a fallback"]
    emit("g_line", lines)
    csv("ch28-line.csv", "p,rating",
        [(f"{a:.1f}", f"{c:.0f}") for a, c in zip(p[::9], rating[::9])])


def contingency() -> None:
    from companion.ch15 import sources as s15
    p = np.clip(s15.plant_year()["delivered"], 0, None)

    def limit_t2() -> float:
        lo, hi = 0.0, 1.0
        for _ in range(30):
            x = 0.5 * (lo + hi)
            r = src.solve({"wind": x, "pv": x}, 0.12, out=("T1",), coupler=True)
            s_t2 = abs(r["flows"][3]["s_ij"]) * src.S_BASE
            lo, hi = (x, hi) if s_t2 <= src.MAIN["s_mva"] else (lo, x)
        return src.solve({"wind": lo, "pv": lo}, 0.12, out=("T1",), coupler=True)["s_poc"].real

    lim_t = limit_t2()
    from companion.ch18 import sources as s18
    rel, ex = s18.REL, s18.EXPORT["overhead line, single circuit"]
    km = src.LINE["km"]
    day = p.reshape(365, 24).sum(axis=1)
    calm = day.min() / 24                       # mean MW on the calmest day
    cases = [   # name, export limit MW, unavailability (ch 18 A-288, A-286; A-345)
        ("main transformer out, no spare", lim_t, 2 * rel["trafo_fail"] * rel["trafo_repair_h"] / 8760),
        ("main transformer out, spare", lim_t, 2 * rel["trafo_fail"] * rel["trafo_spare_h"] / 8760),
        ("132 kV line fault", 0.0, ex["fail_per_km"] * km * ex["repair_h"] / 8760),
        ("line maintenance, any day", 0.0, 24 / 8760),
        ("wind feeder WS3 cable fault", 80.0, rel["cable_fail_per_km"] * 5.2 * rel["cable_repair_h"] / 8760),
    ]
    lines = ["N-1 inside the export system: limit, unavailability, energy at risk",
             "  case                             limit MW   unavail. %   MWh/yr   k u/yr"]
    rows = []
    for name, lim, u in cases:
        if name.startswith("wind feeder"):
            at_risk = 0.2 * np.sum(p)            # the feeder's share of output
        else:
            at_risk = np.sum(np.clip(p - lim, 0, None))
        mwh = u * at_risk
        lines.append(f"  {name:32s} {lim:8.1f}   {100 * u:10.3f}   {mwh:6.0f}   {mwh * 0.07:6.1f}")
        rows.append((len(rows), f"{mwh:.0f}"))
    lines.append(f"  line maintenance on the calmest day of the year: {24 * calm:6.0f} MWh")
    rows.append((len(rows), f"{24 * calm:.0f}"))
    csv("ch28-contingency.csv", "k,mwh", rows)
    lines += ["  (rates and repair times of ch 18, A-286/A-288; 70 u/MWh)",
              f"  with one transformer the second carries {lim_t:.0f} MW at the POC: the",
              "  coupler closes and the controller holds export below it -",
              "  an operating restriction the study writes down. The line's",
              "  faults cost what ch 18 found (17 MWh); its planned day,",
              "  taken at random, is the largest exposure - planned for the",
              "  calmest day it costs a tenth; a shared spare transformer",
              "  cuts that case from 156 to 26 MWh"]
    emit("g_contingency", lines)


def sensitivity() -> None:
    base = src.q_for_target({"wind": 1.0, "pv": 0.84}, 0.0)[1]
    lines = ["sensitivity of the full-export load flow to its data (Q = 0 at POC)",
             "  case                           V POC    V MV-A   loss MW   d loss %"]
    cases = [("base (7.06 km, grid max)", {}),
             ("line impedance +10 %", {"line_scale": 1.1}),
             ("line 7.60 km (sheet error)", {"line_scale": 7.60 / 7.06}),
             ("grid minimum (900 MVA)", {"grid": "min"})]
    for name, kw in cases:
        r = src.q_for_target({"wind": 1.0, "pv": 0.84}, 0.0, **kw)[1]
        lines.append(f"  {name:30s} {r['v'][1]:6.3f}   {r['v'][3]:6.3f}   {r['loss_mw']:7.2f}"
                     f"   {100 * (r['loss_mw'] / base['loss_mw'] - 1):+8.1f}")
    lines += ["  the line's data move losses by a few per cent and voltages",
              "  by a few thousandths: the result is robust to them; the",
              "  grid's strength moves the POC voltage more - which is why",
              "  the operator's minimum case matters more than the line's",
              "  exact length (still corrected before submission)"]
    emit("g_sensitivity", lines)


def ownership() -> None:
    items = [i for i in reg.INPUTS if "G" in i[5].split() or "B" in i[5].split()]
    lines = ["export system data: owner and gap (from the input register)",
             "  id     item                                 owner     status"]
    for iid, item, owner, status, _, _ in items:
        if status != "received":
            lines.append(f"  {iid}  {item:36s} {owner:9s} {status}")
    lines += ["  the plant owns the line to the POC and must measure its",
              "  impedance at commissioning; the operator owns the bay at",
              "  the grid substation, its protection and the network model -",
              "  each gap has an owner who closes it, and a date"]
    emit("g_ownership", lines)


if __name__ == "__main__":
    line_year()
    contingency()
    sensitivity()
    ownership()
