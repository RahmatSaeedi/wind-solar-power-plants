"""Chapter 16, sections A and B - variability against uncertainty, the
energy sensitivity to wind speed, the wind and PV budgets by group,
combination with and without correlation, the hybrid P90 that is not the
sum of P90s, distribution shapes, Monte Carlo convergence, non-linear
effects through the plant end, scenarios and false precision.

Run from the project root:   python -m companion.ch16.examples_ab
Writes companion/ch16/expected/a_*.txt, b_*.txt and diagrams/data/ch16-*.csv.
Budget A-277..A-279 (sources); model 15.1.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch15 import forecast as fc, sources as s15
from companion.ch16 import mc, sources as src
from companion.ch16.common import csv, emit
from plantp import yieldmodel as ym, yieldrisk as yr


def variability() -> None:
    b = src.base()
    wy, py = b["years_w"], b["years_p"]
    lines = ["variability (how much a year moves) against uncertainty of the",
             "  mean (how well 20 years fix the long-term mean):",
             "  resource   sd of one year   uncertainty of the 20-year mean"]
    for name, y in (("wind", wy), ("PV", py), ("hybrid", wy + py)):
        sd = float(np.std(y, ddof=1) / np.mean(y))
        lines.append(f"  {name:8s}       {100 * sd:4.1f} %                  {100 * sd / math.sqrt(20):4.1f} %")
    lines += ["  the year-to-year spread does not shrink with more data: it is",
              "  how the future varies; the mean becomes better known with",
              "  more years: that part is uncertainty"]
    emit("a_variability", lines)


def sensitivity() -> None:
    _, v, *_ = s15.hourly_inputs()
    *_, curve = fc.truth()
    cv = 0.5 * np.arange(len(curve))
    lines = ["sensitivity of the farm energy (model 15.1 farm curve) to the",
             "  wind speed of every hour:"]
    for st in (0.01, 0.03, 0.05, -0.03, -0.05):
        e0 = float(np.interp(v, cv, curve).sum())
        e1 = float(np.interp(v * (1 + st), cv, curve).sum())
        lines.append(f"  speed {100 * st:+3.0f} %: energy {100 * (e1 / e0 - 1):+6.2f} %"
                     f"  (ratio {(e1 / e0 - 1) / st:.2f})")
    lines += ["  the ratio is about 1.8 for the farm, less than the cube (3)",
              "  because much energy comes near and above rated power, but more",
              "  than the 1.60 of one turbine without wakes (chapter 13): wakes",
              "  take more at moderate speeds; a shortfall of speed costs a",
              "  little more than the same surplus gains"]
    emit("a_sensitivity", lines)


def budgets() -> None:
    b = src.base()
    lines = []
    for title, parts, e in (("wind", src.WIND, b["w"]), ("PV", src.PV, b["pv"])):
        u = np.array([p.u for p in parts])
        sh = yr.shares(u)
        lines.append(f"{title} ({e:.2f} GWh at MV), one sigma:")
        for p, s_ in zip(parts, sh):
            lines.append(f"  {p.name:38s} {100 * p.u:4.2f} %  share {100 * s_:4.1f} %")
        tot = yr.combine(u)
        lines.append(f"  combined {100 * tot:4.2f} % = {tot * e:5.2f} GWh;"
                     f" fully correlated {100 * u.sum():4.2f} %")
    emit("a_budgets", lines)
    groups = {}
    for p in src.WIND:
        groups.setdefault(p.group, [0.0, 0.0])[0] += (p.u * b["w"]) ** 2
    for p in src.PV:
        groups.setdefault(p.group, [0.0, 0.0])[1] += (p.u * b["pv"]) ** 2
    csv("ch16-groups.csv", "k,group,wind,pv",
        [(i, g, f"{math.sqrt(w):.2f}", f"{math.sqrt(q):.2f}")
         for i, (g, (w, q)) in enumerate(groups.items())])


def correlation() -> None:
    s = src.sigmas()
    lines = ["hybrid long-term sigma against the correlation of the wind and",
             f"  PV long-term errors (wind {s['s_w']:.2f}, PV {s['s_p']:.2f} GWh):",
             "  r       sigma GWh   P90 (long-term, at MV) GWh"]
    rows = []
    for r in (-0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0):
        sg = math.sqrt(s["s_w"] ** 2 + s["s_p"] ** 2 + 2 * r * s["s_w"] * s["s_p"])
        rows.append((r, f"{sg:.2f}"))
        lines.append(f"  {r:+5.2f}    {sg:6.2f}      {s['mv'] - 1.2816 * sg:7.2f}")
    lines += ["  shared inputs (one long-term reference used for both, one",
              "  modeller's habits) make r positive; treat r as an assumption",
              "  with its own evidence (A-279 sets 0)"]
    emit("b_correlation", lines)
    csv("ch16-corr.csv", "r,sigma", rows)


def hybrid_p90() -> None:
    s = src.sigmas()
    b = src.base()
    w1 = math.hypot(s["s_w"], s["i_w"])
    p1 = math.hypot(s["s_p"], s["i_p"])
    h1 = math.sqrt(w1 ** 2 + p1 ** 2 + 2 * b["r_iav"] * s["i_w"] * s["i_p"])
    lines = ["P90 of the hybrid against the sum of the P90s (one year, at MV):",
             f"  wind   P50 {b['w']:7.2f}  sigma {w1:5.2f}  P90 {b['w'] - 1.2816 * w1:7.2f} GWh",
             f"  PV     P50 {b['pv']:7.2f}  sigma {p1:5.2f}  P90 {b['pv'] - 1.2816 * p1:7.2f} GWh",
             f"  sum of the two P90s           {b['w'] + b['pv'] - 1.2816 * (w1 + p1):7.2f} GWh",
             f"  hybrid P50 {s['mv']:7.2f}  sigma {h1:5.2f}  P90 {s['mv'] - 1.2816 * h1:7.2f} GWh",
             f"  the hybrid P90 is {1.2816 * (w1 + p1 - h1):.2f} GWh higher than the sum:",
             "  a P90 is not additive, because both sources are unlikely to be",
             "  at their P90 in the same year; adding P90s double-counts the",
             "  downside"]
    emit("b_hybridp90", lines)


def shapes() -> None:
    rng = np.random.default_rng(161)
    lines = ["P90 and P99 factors for a 5 % spread, by distribution shape",
             "  (one million samples):",
             "  shape        P90 factor   P99 factor"]
    for k in ("normal", "lognormal", "uniform", "triangular"):
        x = yr.sample(k, 0.05, 1_000_000, rng)
        lines.append(f"  {k:11s}   {yr.exceedance(x, 0.9):.4f}      {yr.exceedance(x, 0.99):.4f}")
    lines += ["  the P90 hardly depends on the shape; the P99 does: the tail is",
              "  where the assumption of a distribution matters"]
    emit("b_shapes", lines)


def convergence() -> None:
    s = src.sigmas()
    sig = math.hypot(s["lt"], s["iav"]) * s["ratio"]
    p50 = src.base()["net"]

    def draw(n, rng):
        return p50 + sig * rng.standard_normal(n)
    res = yr.convergence(draw, (100, 1_000, 10_000, 100_000), 200, 162)
    lines = [f"Monte Carlo P90 of a normal net energy (P50 {p50:.2f}, sigma {sig:.2f} GWh),",
             "  200 repeats per sample size:",
             "  draws      mean P90   spread of the P90 estimate"]
    rows = []
    for n, m, sd in res:
        rows.append((n, f"{sd:.3f}"))
        lines.append(f"  {n:7,d}    {m:7.2f}        {sd:6.3f} GWh")
    lines += [f"  exact P90 {p50 - 1.2816 * sig:.2f} GWh; the spread falls with the square root",
              "  of the draws: 10,000 draws give the P90 to about 0.2 GWh"]
    emit("b_convergence", lines)
    csv("ch16-converge.csv", "n,sd", rows)


def nonlinear() -> None:
    s = src.sigmas()
    lines = ["Monte Carlo through the plant end (losses, limit) against the",
             "  linear sum, one year, 6,000 draws:",
             "  PV block   deterministic   MC mean   MC P50   MC P90   linear P90"]
    for scale in (1.0, 1.6):
        x = mc.net_draws(6000, 1, seed=163, pv_scale=scale)
        r = src.base()["r"]
        _, net0 = ym.plant_end(r["w_av"], r["pv_av"] * scale, s15.ModelConfig(), r["outage"])
        d = net0.sum() / 1e3
        lin = d - 1.2816 * float(np.std(x))
        lines.append(f"  {50 * scale:4.0f} MW    {d:9.2f}     {x.mean():8.2f}  {np.median(x):7.2f}"
                     f"  {yr.exceedance(x):7.2f}   {lin:8.2f}")
    lines += ["  linear P90 = MC mean - 1.2816 x sd of the draws; even with the",
              "  80 MW block the limit changes the spread little here: the",
              "  differences are about the Monte Carlo noise (0.2 GWh on the",
              "  mean); the median lies below the mean (products of factors",
              "  skew to the right); a plant with heavy clipping or curtailment",
              "  is still checked this way, not assumed linear"]
    emit("b_nonlinear", lines)


def scenarios() -> None:
    b = src.base()
    r = b["r"]
    cfg = s15.ModelConfig()
    s = src.sigmas()

    def run(w, p, c=cfg, out=r["outage"]):
        return ym.plant_end(w, p, c, out)[1].sum() / 1e3

    hour = np.arange(8760) % 24
    month = r["month"]
    rng = np.random.default_rng(164)
    extra = r["outage"].copy()
    extra[rng.choice(np.flatnonzero(~extra), 36, replace=False)] = True
    days = (month >= 2) & (month <= 4) & (hour >= 10) & (hour < 15)
    pick = np.isin(np.arange(8760) // 24, rng.choice(np.unique(np.arange(8760)[days] // 24), 18,
                                                      replace=False)) & days
    base = run(r["w_av"], r["pv_av"])
    cases = [
        ("low wind year (one year -1.28 sd)", run(r["w_av"] * (1 - 1.2816 * b["iav_w"]), r["pv_av"])),
        ("dusty year (soiling x 3)", run(r["w_av"], r["pv_av"] * (1 - 2 * 0.0143))),
        ("grid: 48 h outage + spring limit", base - (base - run(r["w_av"], r["pv_av"], out=extra))
         - np.clip(ym.plant_end(r["w_av"], r["pv_av"], cfg, r["outage"])[1][pick] - 70, 0, None).sum() / 1e3),
        ("availability 95 % wind", run(r["w_av"] * 0.95 / 0.981, r["pv_av"])),
    ]
    lines = [f"scenarios against the P50 of {base:.2f} GWh (one year, teaching):"]
    for name, val in cases:
        lines.append(f"  {name:36s} {val:7.2f} GWh ({val - base:+6.2f})")
    allc = run(r["w_av"] * (1 - 1.2816 * b["iav_w"]) * 0.95 / 0.981,
               r["pv_av"] * (1 - 2 * 0.0143), out=extra)
    lines += [f"  all four together (spring limit left out)     {allc:7.2f} GWh",
              f"  one-year P90 from the budget                  "
              f"{base - 1.2816 * math.hypot(s['lt'], s['iav']) * s['ratio']:7.2f} GWh",
              "  a scenario has no probability: it answers 'what if', and the",
              "  lender may ask for named scenarios besides the P-values"]
    emit("b_scenarios", lines)


def precision() -> None:
    s = src.sigmas()
    sig = math.hypot(s["lt"], s["iav"]) * s["ratio"]
    p50 = src.base()["net"]
    lines = ["how precise is a P90? (one year):",
             f"  P50 {p50:.2f}, sigma {sig:.2f} GWh, P90 {p50 - 1.2816 * sig:.2f} GWh"]
    for f in (0.8, 1.2):
        lines.append(f"  sigma itself {100 * (f - 1):+.0f} %: P90 {p50 - 1.2816 * sig * f:.2f} GWh")
    lines += ["  an uncertainty known to about a fifth moves the P90 by about",
              f"  {1.2816 * sig * 0.2:.1f} GWh; report it as about {round(p50 - 1.2816 * sig):.0f} GWh,"
              " not to two decimals"]
    emit("b_precision", lines)


if __name__ == "__main__":
    variability()
    sensitivity()
    budgets()
    correlation()
    hybrid_p90()
    shapes()
    convergence()
    nonlinear()
    scenarios()
    precision()
