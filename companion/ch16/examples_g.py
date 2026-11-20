"""Chapter 16, more lessons - variance shares read from the Monte Carlo
draws, monthly variability and a liquidity reserve, the spread of two
models as evidence for the model parts, and parts that are systematic
or independent across the twelve turbines.

Run from the project root:   python -m companion.ch16.examples_g
Writes companion/ch16/expected/g_*.txt and diagrams/data/ch16-*.csv.
Teaching values A-283.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch12 import sources as s12
from companion.ch13 import sources as s13
from companion.ch15 import forecast as fc, sources as s15
from companion.ch16 import lab_d, lab_e, sources as src
from companion.ch16.common import csv, emit
from plantp import yieldmodel as ym, yieldrisk as yr


def mc_shares() -> None:
    """Draw each part's factor, run the plant end, and read the share of
    the output variance that each factor explains (squared correlation;
    nearly additive for independent, nearly linear parts)."""
    rng = np.random.default_rng(171)
    n = 6000
    b = src.base()
    r = b["r"]
    cfg = s15.ModelConfig()
    parts = [("wind", p) for p in src.WIND] + [("PV", p) for p in src.PV]
    f = {(t, p.name): yr.sample(p.kind, p.u, n, rng) for t, p in parts}
    from companion.ch16 import mc
    iw, ip = mc.iav_pair(n, 1, rng)
    fw = np.prod([f[(t, p.name)] for t, p in parts if t == "wind"], axis=0) * iw
    fp = np.prod([f[(t, p.name)] for t, p in parts if t == "PV"], axis=0) * ip
    out = np.empty(n)
    for k in range(n):
        out[k] = ym.plant_end(r["w_av"] * fw[k], r["pv_av"] * fp[k], cfg, r["outage"])[1].sum() / 1e3
    rows = []
    for (t, name), x in f.items():
        rows.append((f"{t}: {name}", float(np.corrcoef(x, out)[0, 1]) ** 2))
    rows.append(("year-to-year wind", float(np.corrcoef(iw, out)[0, 1]) ** 2))
    rows.append(("year-to-year PV", float(np.corrcoef(ip, out)[0, 1]) ** 2))
    rows.sort(key=lambda x: -x[1])
    lines = ["variance shares read from 6,000 Monte Carlo draws (squared",
             "  correlation of each factor with the net energy):"]
    for name, s_ in rows[:7]:
        lines.append(f"  {name:44s} {100 * s_:5.1f} %")
    lines += [f"  sum of all shares {100 * sum(s_ for _, s_ in rows):.1f} %"
              " (near 100 %: the model is almost linear here)",
              "  the same order as the budget (lab D), found without writing",
              "  any formula: useful when the model is too complex for one"]
    emit("g_mcshares", lines)


def monthly() -> None:
    """Monthly energy at MV over 20 years: wind from the reference series
    through the farm curve, PV from the 20-year monthly GHI ratios."""
    ref = s13.reference()
    r = src.base()["r"]
    month = r["month"]
    wy = np.array([[fc.farm_curve(np.clip(0.012 + 1.0862 * ref["long"][y][month == m], 0, None)).sum()
                    for m in range(12)] for y in range(20)]) / 1e3
    wy *= r["w_av"].sum() / 1e3 / wy.sum(axis=1).mean()
    sums = np.asarray(s12.long_term()["monthly"])
    pv_m = np.array([r["pv_av"][month == m].sum() for m in range(12)]) / 1e3
    py = sums / sums.mean(axis=0)[None, :] * pv_m[None, :]
    h = wy + py
    mean = h.mean(axis=0)
    sd = h.std(axis=0, ddof=1)
    lines = ["monthly energy at MV over 20 years (GWh):",
             "  month   mean    sd     sd %   P90 (normal)"]
    rows = []
    for m in range(12):
        rows.append((m + 1, f"{mean[m]:.2f}", f"{mean[m] - 1.2816 * sd[m]:.2f}"))
        lines.append(f"  {m + 1:5d}   {mean[m]:5.2f}  {sd[m]:5.2f}   {100 * sd[m] / mean[m]:4.1f}"
                     f"   {mean[m] - 1.2816 * sd[m]:6.2f}")
    ann = h.sum(axis=1)
    sum_p90 = float((mean - 1.2816 * sd).sum())
    lines += [f"  year: mean {ann.mean():.2f}, sd {ann.std(ddof=1):.2f} GWh"
              f" ({100 * ann.std(ddof=1) / ann.mean():.1f} %); sum of monthly P90s {sum_p90:.2f},",
              f"    year-to-year P90 {ann.mean() - 1.2816 * ann.std(ddof=1):.2f} GWh",
              "  in this synthetic record the months move with their year, so",
              "  a month varies about as much as the year in per cent; measured",
              "  monthly records usually vary more and the gap between the sum",
              "  of monthly P90s and the annual P90 grows; the method stays"]
    emit("g_monthly", lines)
    csv("ch16-monthly.csv", "m,mean,p90", rows)
    # liquidity: six months of debt service as a reserve (A-283)
    ds = lab_e.energies(lab_e.sig_one_year())
    d, _ = yr.debt_size({k: lab_e.cfads(v) for k, v in ds.items()}, lab_e.DSCR,
                        lab_e.RATE, lab_e.YEARS)
    service = d / yr.annuity(lab_e.RATE, lab_e.YEARS)
    cf_month = (h * lab_e.PRICE - lab_e.OPEX / 12)       # k u per month, 20 x 12
    short = np.clip(service / 12 - cf_month, 0, None)
    worst = short.sum(axis=1).max()
    lines2 = ["liquidity: monthly cash against level monthly debt service",
              f"  (service {service:,.0f} k u a year, {service / 12:,.0f} k u a month):",
              f"  months short of the service in 20 years: {int((short > 0).sum())} of 240",
              f"  largest shortfall in one year {worst:,.0f} k u;"
              f" a six-month reserve holds {service / 2:,.0f} k u",
              "  seasonal shortfalls are normal and the reserve absorbs them;",
              "  a reserve is sized on monthly data, not on the annual P90"]
    emit("g_liquidity", lines2)


def model_spread() -> None:
    """The bridge of chapter 15 (5.91 GWh from five model choices)
    against the model parts of the budget."""
    b = src.base()
    names = {"wake model": b["w"], "hub density": b["w"],
             "transposition model": b["pv"], "PV model (temperature, angle, light)": b["pv"]}
    parts = [p.u * names[p.name] for p in src.WIND + src.PV if p.name in names]
    parts.append(src.PLANT[0].u * (b["w"] + b["pv"]))
    s = math.sqrt(sum(x * x for x in parts))
    lines = ["the spread of two models as evidence for the model parts:",
             f"  model parts of the budget (wake, density, transposition, PV",
             f"    model, electrical): sigma {s:.2f} GWh at MV",
             "  chapter 15 bridge, reviewer's model B against model A:"
             " 5.91 GWh (2.0 %)",
             f"  that is {5.91 / s:.1f} sigma of the model parts (or {5.91 / (s * math.sqrt(2)):.1f}"
             " sigma of",
             "    the difference of two independent models)",
             "  two models differing by about one to two sigma is ordinary;",
             "  a much larger gap would say the model parts are too small,",
             "  and the bridge says which part to look at first"]
    emit("g_modelspread", lines)


def units() -> None:
    """Twelve turbines: a part with a systematic share (same type, same
    test) and an independent share per unit (A-283: power curve 2.0 %
    systematic, 3.0 % per unit)."""
    lines = ["parts shared by all turbines against parts of each unit",
             "  (power curve, teaching: 2.0 % systematic, 3.0 % per unit):",
             "  turbines   farm sigma %"]
    for n in (1, 3, 12, 50):
        lines.append(f"  {n:8d}    {math.hypot(2.0, 3.0 / math.sqrt(n)):6.2f}")
    lines += ["  the per-unit part averages out over many turbines, the",
              "  systematic part never does: the budget lists the farm-level",
              "  (systematic) sigma, not one turbine's"]
    emit("g_units", lines)


def autocorrelation() -> None:
    """Lag-1 autocorrelation of the 20 annual wind energies and the
    effective number of independent years in a 10-year mean."""
    b = src.base()
    w = b["years_w"]
    x = w - w.mean()
    r1 = float((x[1:] * x[:-1]).sum() / (x * x).sum())
    lines = [f"lag-1 autocorrelation of the 20 annual wind energies: {r1:+.2f}",
             "  effective years in a 10-year mean, n (1 - r1) / (1 + r1):"]
    for r in (r1, 0.2, 0.4):
        n_eff = 10 * (1 - r) / (1 + r)
        lines.append(f"    r1 {r:+.2f}: {n_eff:5.2f} years; year-to-year part of the mean"
                     f" {100 * b['iav_w'] / math.sqrt(n_eff):.2f} % (not {100 * b['iav_w'] / math.sqrt(10):.2f} %)")
    lines += ["  20 values give a very rough r1; if good and bad years come in",
              "  runs (r1 > 0), averaging helps less than the square root of n;",
              "  a long reference series is the evidence"]
    emit("g_autocorr", lines)


def two_estimates() -> None:
    """Two independent yield estimates combined by inverse variance
    (teaching numbers A-283): ours 295 +/- 12 GWh long-term, a second
    consultant's 288 +/- 15 GWh; correlation of their errors 0 or 0.5."""
    a, sa, b_, sb = 295.0, 12.0, 288.0, 15.0
    lines = ["two estimates of the long-term P50 (sigma, teaching A-283):",
             f"  ours {a:.0f} +/- {sa:.0f} GWh, second consultant {b_:.0f} +/- {sb:.0f} GWh"]
    for r in (0.0, 0.5):
        # weights for correlated estimates
        v = np.array([[sa * sa, r * sa * sb], [r * sa * sb, sb * sb]])
        w = np.linalg.solve(v, np.ones(2))
        w /= w.sum()
        m = w @ np.array([a, b_])
        s = math.sqrt(float(w @ v @ w))
        lines.append(f"  r {r:.1f}: weights {w[0]:.2f} / {w[1]:.2f}, combined {m:.1f} +/- {s:.1f} GWh")
    z = (a - b_) / math.hypot(sa, sb)
    lines += [f"  difference {a - b_:.0f} GWh is {z:.2f} sigma of the difference: consistent",
              "  combining helps only if the errors are independent; two",
              "  consultants with the same data and methods are not"]
    emit("g_twoestimates", lines)


if __name__ == "__main__":
    autocorrelation()
    two_estimates()
    mc_shares()
    monthly()
    model_spread()
    units()
