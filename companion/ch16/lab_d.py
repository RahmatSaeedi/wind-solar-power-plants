"""Chapter 16, lab D - the transparent uncertainty budget of Plant P (the
chapter's worked example), deterministic against Monte Carlo results,
the dominant drivers, the value of measuring better, and the yield
statement.

Run from the project root:   python -m companion.ch16.lab_d
Writes companion/ch16/expected/d_*.txt and diagrams/data/ch16-*.csv.
"""
from __future__ import annotations

import math
from dataclasses import replace

import numpy as np

from companion.ch16 import mc, sources as src
from companion.ch16.common import csv, emit
from plantp import yieldrisk as yr


# [start: budget]
def items(wind=None, pv=None):
    """(name, technology, sigma GWh at MV) for every part, plus the
    year-to-year term."""
    b = src.base()
    s = src.sigmas()
    mv = s["mv"]
    out = [(p.name, "wind", p.u * b["w"]) for p in (wind or src.WIND)]
    out += [(p.name, "PV", p.u * b["pv"]) for p in (pv or src.PV)]
    out += [(p.name, "plant", p.u * mv) for p in src.PLANT]
    out.append(("year-to-year (wind and PV, r 0.12)", "future", s["iav"]))
    return out


def total(it, years: int = 1) -> float:
    lt = [x[2] for x in it if x[1] != "future"]
    iav = [x[2] for x in it if x[1] == "future"][0]
    return math.sqrt(sum(v * v for v in lt) + iav ** 2 / years)
# [end: budget]


def budget() -> None:
    it = items()
    b = src.base()
    s = src.sigmas()
    tot = total(it)
    lines = ["uncertainty budget of Plant P, net energy (sigma in GWh at MV;",
             f"  P50 {b['net']:.2f} GWh at the POC, model 15.1, scenario S0):",
             "  component                            tech.   sigma   share"]
    rows = []
    for name, tech, sg in sorted(it, key=lambda x: -x[2]):
        lines.append(f"  {name:36s} {tech:6s} {sg:6.2f}  {100 * sg * sg / tot ** 2:5.1f} %")
        rows.append((name, sg))
    lt = total([x for x in it if x[1] != "future"] + [("", "future", 0.0)])
    r = s["ratio"]
    lines += [f"  long-term (all but the year-to-year)       {lt:6.2f}",
              f"  one year                                    {tot:6.2f}",
              f"  ten-year mean                               {total(it, 10):6.2f}",
              f"  at the POC (x {r:.3f}): one year {tot * r:.2f}, ten years {total(it, 10) * r:.2f} GWh",
              f"  P90 one year {b['net'] - 1.2816 * tot * r:.1f}, P99 one year"
              f" {b['net'] - 2.3263 * tot * r:.1f}, P90 ten years"
              f" {b['net'] - 1.2816 * total(it, 10) * r:.1f} GWh"]
    emit("d_budget", lines)
    top = sorted(it, key=lambda x: -x[2])[:10]
    csv("ch16-shares.csv", "k,share",
        [(i, f"{100 * sg * sg / tot ** 2:.2f}") for i, (_, _, sg) in enumerate(top)])


def montecarlo() -> None:
    b = src.base()
    s = src.sigmas()
    lines = ["Monte Carlo (20,000 draws, plant end of model 15.1) against the",
             "  analytic budget:",
             "  horizon     analytic P90   MC mean   MC P50   MC P90   MC P99"]
    for yrs in (1, 10):
        x = mc.net_draws(20_000, yrs, seed=166)
        an = b["net"] - 1.2816 * total(items(), yrs) * s["ratio"]
        lines.append(f"  {yrs:2d} year{'s' if yrs > 1 else ' '}       {an:7.2f}      {x.mean():7.2f}  "
                     f"{np.median(x):7.2f}  {yr.exceedance(x):7.2f}  {yr.exceedance(x, 0.99):7.2f}")
        if yrs == 1:
            hist, edges = np.histogram(x, bins=np.arange(230, 362, 4))
            csv("ch16-mchist.csv", "e,f",
                [(f"{0.5 * (a + c):.0f}", f"{h / len(x) / 4:.5f}")
                 for a, c, h in zip(edges[:-1], edges[1:], hist)])
    lines += ["  the two agree within the Monte Carlo noise: for this plant a",
              "  transparent root-sum-square budget is enough; the Monte Carlo",
              "  checks it and would catch strong non-linearity or skew"]
    emit("d_mc", lines)


def drivers() -> None:
    it = items()
    b = src.base()
    r = src.sigmas()["ratio"]
    base90 = b["net"] - 1.2816 * total(it) * r
    lines = [f"halving one component at a time: one-year P90 (now {base90:.2f} GWh):"]
    for name, tech, sg in sorted(it, key=lambda x: -x[2])[:6]:
        new = [(n, t, v / 2 if n == name and t == tech else v) for n, t, v in it]
        p90 = b["net"] - 1.2816 * total(new) * r
        lines.append(f"  {name:36s} {tech:6s} {p90 - base90:+5.2f} GWh")
    lines += ["  the year-to-year term cannot be halved (it is the future); of",
              "  the rest, the wind long-term correction and the measurement",
              "  chain pay most: better data, not a cleverer model"]
    emit("d_drivers", lines)


def measure() -> None:
    """Teaching effects of measuring better (A-280): a second mast year
    takes the MCP part from 2.0 to 1.5 % of speed; a lidar campaign at
    the turbines takes the cross-prediction from 1.35 to 0.8 %; weekly
    cleaning and calibration of the station takes the PV sensor
    maintenance part from 1.0 to 0.5 %."""
    b = src.base()
    r = src.sigmas()["ratio"]
    base90 = b["net"] - 1.2816 * total(items()) * r
    w = list(src.WIND)
    p = list(src.PV)
    S = src.SENS
    cases = {
        "second mast year (MCP 2.0 -> 1.5 %)":
            (_swap(w, "long-term correction and period",
                   S * math.hypot(0.015, 0.035 / math.sqrt(20))), p),
        "lidar at the turbines (1.35 -> 0.8 %)":
            (_swap(w, "cross-prediction to the turbines", S * 0.008), p),
        "station kept clean (1.0 -> 0.5 %)":
            (w, _swap(p, "irradiance sensor, maintenance", math.hypot(0.020, 0.005)))}
    lines = [f"measuring better (A-280), one-year P90 now {base90:.2f} GWh:"]
    for name, (ww, pp) in cases.items():
        p90 = b["net"] - 1.2816 * total(items(ww, pp)) * r
        lines.append(f"  {name:40s} {p90 - base90:+5.2f} GWh")
    ww = _swap(_swap(w, "long-term correction and period",
                     S * math.hypot(0.015, 0.035 / math.sqrt(20))),
               "cross-prediction to the turbines", S * 0.008)
    pp = _swap(p, "irradiance sensor, maintenance", math.hypot(0.020, 0.005))
    lines += [f"  all three                                {b['net'] - 1.2816 * total(items(ww, pp)) * r - base90:+5.2f} GWh",
              "  each GWh of P90 is debt capacity (lab E): measuring has a",
              "  value that can be set against its cost"]
    emit("d_measure", lines)


def _swap(parts, name, u):
    return [replace(x, u=u) if x.name == name else x for x in parts]


def statement() -> None:
    b = src.base()
    it = items()
    r = src.sigmas()["ratio"]
    t1, t10 = total(it) * r, total(it, 10) * r
    lines = ["yield statement, Plant P, scenario S0 (PLP-GEN-REP-0009, draft):",
             f"  P50 net at the POC, first year: {round(b['net']):.0f} GWh (model 15.1, D-019)",
             f"  one-year sigma {t1:.0f} GWh ({100 * t1 / b['net']:.1f} %); ten-year {t10:.0f} GWh",
             f"  P90 one year about {round(b['net'] - 1.2816 * t1):.0f} GWh; P99 one year about"
             f" {round(b['net'] - 2.3263 * t1):.0f} GWh;",
             f"    P90 ten years about {round(b['net'] - 1.2816 * t10):.0f} GWh",
             "  largest contributors: year-to-year wind, wind long-term",
             "    correction, wind measurement, cross-prediction, power curve",
             "  limits: synthetic data; teaching sigmas (A-277..A-279); no",
             "    climate trend; degradation and lifetime series in ch 15;",
             "    not a guarantee and not a complete risk assessment"]
    emit("d_statement", lines)


if __name__ == "__main__":
    budget()
    montecarlo()
    drivers()
    measure()
    statement()
