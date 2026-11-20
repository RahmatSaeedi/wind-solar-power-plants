"""Chapter 16, further lessons - the uncertainty of a measure-correlate-
predict estimate against the length of concurrent data and the
correlation, a climate trend, degradation uncertainty over the life,
a skewed availability, narrowing the uncertainty with operating years,
and the ridge layout W1 against W2b in P-values and debt.

Run from the project root:   python -m companion.ch16.examples_f
Writes companion/ch16/expected/f_*.txt and diagrams/data/ch16-*.csv.
Teaching relations and values A-282.
"""
from __future__ import annotations

import math
from dataclasses import replace

import numpy as np

from companion.ch16 import lab_d, lab_e, sources as src
from companion.ch16.common import csv, emit
from plantp import yieldrisk as yr


# [start: mcp]
def u_mcp(months: int, r: float, sd_month: float = 0.10,
          years_ref: int = 20, sd_year: float = 0.035) -> float:
    """Teaching relation (A-282): uncertainty of the long-term mean speed
    from a regression on `months` concurrent months with correlation r
    (residual sd_month sqrt(1 - r^2), months taken as independent) plus
    the representativeness of a reference of `years_ref` years."""
    reg = sd_month * math.sqrt(1 - r * r) / math.sqrt(months)
    return math.hypot(reg, sd_year / math.sqrt(years_ref))
# [end: mcp]


def mcp() -> None:
    lines = ["uncertainty of the long-term mean wind speed by MCP (teaching",
             "  relation A-282; monthly sd 10 %, 20-year reference at 3.5 %):",
             "  months   r 0.70   r 0.80   r 0.90   r 0.95"]
    rows = []
    for m in (6, 12, 18, 24, 36):
        vals = [u_mcp(m, r) for r in (0.70, 0.80, 0.90, 0.95)]
        rows.append((m,) + tuple(f"{100 * v:.2f}" for v in vals))
        lines.append(f"  {m:5d}    " + "    ".join(f"{100 * v:4.2f} %" for v in vals))
    lines += ["  a longer concurrent period and a better-correlated reference",
              "  both help, and both stop at the reference's own limit (0.8 %);",
              "  12 months at r 0.7 to 0.8 give the 2.15 % (MCP and period) of",
              "  chapter 13"]
    emit("f_mcp", lines)
    csv("ch16-mcp.csv", "m,r70,r80,r90,r95", rows)


def trend() -> None:
    """A teaching trend of the wind speed (A-282): -0.5 % per decade,
    against a 20-year reference centred 10 years ago; the loan's
    15 years are centred 7.5 years ahead."""
    b = src.base()
    dt = 10 + 7.5                                         # years between centres
    dv = -0.005 * dt / 10
    de = dv * src.SENS
    lines = ["a slow change of the wind (teaching trend -0.5 % of speed a decade):",
             f"  reference centre to loan centre: {dt:.1f} years; speed {100 * dv:+.2f} %",
             f"  wind energy {100 * de:+.2f} % = {de * b['w']:+.2f} GWh a year at MV",
             f"  as a one-sigma part it would be {abs(de) * 100:.2f} %, beside the"
             f" {100 * src.u_group(src.WIND):.2f} % of the wind",
             "  a trend is not noise: if it is believed, the P50 moves; if it",
             "  is only possible, it becomes a scenario or a budget part, and",
             "  the statement says which (and on what evidence)"]
    emit("f_trend", lines)


def degradation() -> None:
    """PV degradation 0.5 +/- 0.2 % a year (one sigma, A-282), fully
    correlated over the years (one plant, one rate)."""
    b = src.base()
    lines = ["PV energy and its uncertainty from the degradation rate",
             "  (0.5 +/- 0.2 % a year, one rate for the whole life):",
             "  year   PV GWh at MV   sigma from rate   PV sigma all parts"]
    u_pv = src.u_group(src.PV)
    rows = []
    for y in (1, 5, 10, 15, 20, 25):
        f = (1 - 0.005 * y) / (1 - 0.005)
        e = b["pv"] * f
        s_rate = 0.002 * y * b["pv"] / (1 - 0.005)
        tot = math.hypot(u_pv * e, s_rate)
        rows.append((y, f"{s_rate:.2f}", f"{tot:.2f}"))
        lines.append(f"  {y:4d}     {e:8.2f}        {s_rate:6.2f} GWh        {tot:6.2f} GWh")
    lines += ["  the rate's uncertainty grows with every year: near year 15 it",
              "  equals all other PV parts together and then exceeds them;",
              "  long-term module data (chapter 41, field records) shrink it"]
    emit("f_degradation", lines)
    csv("ch16-degr.csv", "y,rate,total", rows)


def availability() -> None:
    """Twelve turbines; minor stops (uniform 1.0 % of time) plus major
    failures: 4 % chance per turbine-year of a 60-day stop (A-282).
    Annual energy-based availability over 100,000 simulated years."""
    rng = np.random.default_rng(170)
    n = 100_000
    minor = 0.010 + 0.002 * rng.standard_normal(n)
    major = rng.binomial(12, 0.04, n)
    days = major * 60 * rng.uniform(0.5, 1.5, n)
    a = 1 - minor - days / (12 * 365)
    mean, med = a.mean(), np.median(a)
    lines = ["annual availability with rare major failures (A-282):",
             f"  mean {100 * mean:.2f} %, median {100 * med:.2f} %, sd {100 * a.std():.2f} %",
             f"  P90 {100 * yr.exceedance(a):.2f} %, P99 {100 * yr.exceedance(a, 0.99):.2f} %",
             f"  normal with the same mean and sd: P90 {100 * (mean - 1.2816 * a.std()):.2f} %,"
             f" P99 {100 * (mean - 2.3263 * a.std()):.2f} %",
             f"  years with no major failure: {100 * (major == 0).mean():.0f} %",
             "  the distribution is one-sided: most years are a little better",
             "  than the mean, a few much worse; a normal part misplaces the",
             "  tail, and a long repair (spares, cranes, chapter 51) is the",
             "  real driver"]
    emit("f_availability", lines)
    hist, edges = np.histogram(100 * a, bins=np.arange(90.0, 99.6, 0.25))
    csv("ch16-avail.csv", "a,f", [(f"{0.5 * (x + y):.3f}", f"{h / n:.5f}")
                                  for x, y, h in zip(edges[:-1], edges[1:], hist)])


def update() -> None:
    """Operating years narrow the long-term part (A-282, teaching): each
    year measures the long-term mean with the year-to-year noise; the
    budget is the prior. Refinancing logic, not a forecast."""
    s = src.sigmas()
    r = s["ratio"]
    p50 = src.base()["net"]
    prior = s["lt"] * r
    iav = s["iav"] * r
    lines = ["narrowing the long-term part with operating years (teaching):",
             "  years   long-term sigma   one-year P90   ten-year P90   (GWh)"]
    rows = []
    for n in (0, 1, 2, 3, 5, 10):
        post = 1 / math.sqrt(1 / prior ** 2 + n / iav ** 2) if n else prior
        p1 = p50 - 1.2816 * math.hypot(post, iav)
        p10 = p50 - 1.2816 * math.hypot(post, iav / math.sqrt(10))
        rows.append((n, f"{post:.2f}", f"{p1:.2f}"))
        lines.append(f"  {n:5d}     {post:7.2f}         {p1:7.2f}       {p10:7.2f}")
    lines += ["  in this teaching model (exact meter, independent years) three",
              "  years take more than half off the long-term part; the",
              "  year-to-year part stays; this is why projects are often",
              "  refinanced after some years of operation (if the data are",
              "  clean and corrected to a long-term reference, chapter 52)"]
    emit("f_update", lines)
    csv("ch16-update.csv", "n,post,p90", rows)


def layouts() -> None:
    """W1 ridge against W2b (D-018): farm energy 236.9 and 196.9 GWh
    (chapter 14, long term before availability), cross-prediction 7.64
    and 1.35 % of speed; the same opex (teaching)."""
    b = src.base()
    r = src.sigmas()["ratio"]
    out = ["the ridge layout W1 against W2b, one year, teaching terms A-281:",
           "  layout             P50 net   sigma   P90 1y   P99 1y   debt k u   case"]
    for name, scale, xp in (("W2b plain", 1.0, 0.0135), ("W1 ridge", 236.9 / 196.9, 0.0764),
                            ("W1, ridge mast", 236.9 / 196.9, 0.0135)):
        wind = [replace(p, u=src.SENS * xp) if p.name.startswith("cross") else p
                for p in src.WIND]
        w = b["w"] * scale
        s_w = src.u_group(wind) * w
        s_p = src.u_group(src.PV) * b["pv"]
        s_pl = src.u_group(src.PLANT) * (w + b["pv"])
        i_w, i_p = b["iav_w"] * w, b["iav_p"] * b["pv"]
        iav = math.sqrt(i_w ** 2 + i_p ** 2 + 2 * b["r_iav"] * i_w * i_p)
        sig = math.sqrt(s_w ** 2 + s_p ** 2 + s_pl ** 2 + iav ** 2) * r
        p50 = b["net"] + (w - b["w"]) * r
        e = {"P50": p50, "P90 1y": p50 - 1.2816 * sig, "P99 1y": p50 - 2.3263 * sig}
        d, case = yr.debt_size({k: lab_e.cfads(v) for k, v in e.items()}, lab_e.DSCR,
                               lab_e.RATE, lab_e.YEARS)
        out.append(f"  {name:17s}  {p50:7.1f}   {sig:5.1f}   {e['P90 1y']:6.1f}   {e['P99 1y']:6.1f}"
                   f"   {d:8,.0f}   {case}")
    out += ["  the ridge gives a fifth more energy but carries it with an",
            "  uncertainty that the P99 case punishes: it supports less debt",
            "  than the plain until the ridge is measured, then 18 % more;",
            "  the bird survey (U-051) decides first (D-018)"]
    emit("f_layouts", out)


if __name__ == "__main__":
    mcp()
    trend()
    degradation()
    availability()
    update()
    layouts()
