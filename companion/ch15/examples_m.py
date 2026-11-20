"""Chapter 15, sections C4 and D4 - environmental curtailment of the wind
farm (bat and night-noise rules), time-based against energy-based
availability, a battery behind an overbuilt PV block, a sensitivity
tornado of the net energy, and a monthly spreadsheet model against the
hourly model.

Run from the project root:   python -m companion.ch15.examples_m
Writes companion/ch15/expected/m_*.txt and diagrams/data/ch15-*.csv.
Model 15.1; teaching rules and ranges A-272.
"""
from __future__ import annotations

import math
from dataclasses import replace

import numpy as np

from companion.ch10 import pvyear10
from companion.ch11 import lab_d as l11
from companion.ch13 import sources as s13
from companion.ch15 import examples_k as ek, sources as src
from companion.ch15.common import csv, emit
from plantp import datapack, wind as w, yieldmodel as ym


def tail(w_av, pv_av, cfg, outage):
    """The plant end of the chain (MV to the POC) for given series."""
    return ym.plant_end(w_av, pv_av, cfg, outage)


# [start: environment]
def environmental() -> None:
    """Teaching rules (A-272): bats - April to October, from 20:00 to
    05:59, hub wind below 6 m/s and air above 10 C: all turbines stop;
    night noise - 22:00 to 05:59, hub wind 6 to 10 m/s: three turbines
    run a reduced mode at 8 % less power."""
    r = src.plant_year()
    _, v, _, _, t, month = src.hourly_inputs()
    hour = np.arange(8760) % 24
    night_b = (hour >= 20) | (hour < 6)
    bats = (month >= 3) & (month <= 9) & night_b & (v < 6.0) & (t > 10.0)
    night_n = (hour >= 22) | (hour < 6)
    noise = night_n & (v >= 6.0) & (v <= 10.0)
    lost_b = r["w_av"][bats].sum()
    lost_n = (3 / 12 * 0.08 * r["w_av"][noise]).sum()
# [end: environment]
    tot = r["w_av"].sum()
    season = (month >= 3) & (month <= 9) & night_b & (t > 10.0)
    thr = ", ".join(f"{x} m/s {r['w_av'][season & (v < x)].sum():,.0f}" for x in (5.5, 6.0, 6.5))
    lines = ["environmental curtailment of the wind farm (teaching rules, A-272):",
             f"  bats: {int(bats.sum())} h stopped, {lost_b:,.0f} MWh"
             f" ({100 * lost_b / tot:.2f} % of the wind energy)",
             f"    mean farm power in those hours {r['w_av'][bats].mean():.1f} MW"
             f" against {r['w_av'].mean():.1f} MW over the year",
             f"  night noise: {int(noise.sum())} h in reduced mode, {lost_n:,.0f} MWh"
             f" ({100 * lost_n / tot:.2f} %)",
             f"  bat threshold: {thr} MWh",
             f"  the bat rule takes {100 * bats.mean():.1f} % of the hours but"
             f" {100 * lost_b / tot:.1f} % of the energy:",
             "    it acts at low wind, where the power curve is low; it is still",
             "    the largest environmental loss here; the permit sets the rule",
             "    (chapter 33) and the model applies it hour by hour"]
    emit("m_environment", lines)


def availability() -> None:
    """Twelve turbines, failures at a mean rate that gives about 98 %
    time-based availability, repairs of 40 h on average; failures either
    uniform in time or more likely in strong wind (rate ~ (v/8)^2) (A-272)."""
    r = src.plant_year()
    _, v, *_ = src.hourly_inputs()
    p_t = r["w_lt"] / 12                                   # MW per turbine before availability
    rng = np.random.default_rng(200)
    rate0 = 1 / 1960                                       # per hour: MTBF ~1,960 h
    shape = (np.clip(v, 0, None) / 8.0) ** 2
    shape /= shape.mean()
    res = {}
    for name, scale in (("failures uniform in time", np.ones(8760)),
                        ("failures more likely in strong wind", shape)):
        tb, eb = [], []
        for _ in range(40):
            down = np.zeros((8760, 12), bool)
            for k in range(12):
                t0 = 0
                while t0 < 8760:
                    if rng.random() < rate0 * scale[t0]:
                        d = int(rng.exponential(40.0)) + 1
                        down[t0:t0 + d, k] = True
                        t0 += d
                    else:
                        t0 += 1
            tb.append(1 - down.mean())
            eb.append(1 - (p_t[:, None] * down).sum() / (p_t.sum() * 12))
        res[name] = (np.mean(tb), np.mean(eb))
    lines = ["time-based against energy-based availability (12 turbines, 40",
             "  simulated years each, repairs 40 h on average, A-272):"]
    for name, (a, b) in res.items():
        lines.append(f"  {name:36s} time {100 * a:5.2f} %, energy {100 * b:5.2f} %")
    lines += ["  contracts often guarantee time; the yield model needs energy;",
              "  when failures come with strong wind (loads, gusts) the energy",
              "  lost is larger than the hours suggest: state which one a",
              "  number is, and convert with the plant's own data (chapter 51)"]
    emit("m_availability", lines)


def battery_overbuild() -> None:
    """PV block 80 MW AC (scale 1.6) behind the 100 MW limit; batteries
    charge only from power above the limit and discharge below it."""
    r = src.plant_year()
    cfg = src.ModelConfig()
    poc, _ = tail(r["w_av"], 1.6 * r["pv_av"], cfg, np.zeros(8760, bool))
    cut0 = np.clip(poc - 100, 0, None).sum()
    lines = ["PV 80 MW AC behind 100 MW: a battery that stores what the limit",
             f"  cuts (round trip 86 %); curtailed without battery {cut0:,.0f} MWh",
             "  battery          stored MWh   returned MWh   share   cycles"]
    eta = math.sqrt(0.86)
    rows = []
    for pb, eb in ((20, 40), (20, 80), (40, 80), (40, 160)):
        soc, st, ret = 0.0, 0.0, 0.0
        for x in poc:
            if x > 100:
                ch = min(x - 100, pb, (eb - soc) / eta)
                soc += ch * eta
                st += ch
            elif soc > 0:
                dis = min(100 - x, pb, soc * eta)
                soc -= dis / eta
                ret += dis
        rows.append((f"{pb}/{eb}", f"{100 * ret / cut0:.1f}"))
        lines.append(f"  {pb:3d} MW {eb:4d} MWh   {st:9,.0f}     {ret:9,.0f}     {100 * ret / cut0:5.1f} %"
                     f"   {ret / eb:5.0f}")
    lines += ["  energy alone rarely pays for a battery: the cycles are few;",
              "  its value comes from timing, reserve and shortfalls as well",
              "  (chapters 17-19); the model counts each use apart"]
    emit("m_batteryoverbuild", lines)


def allocation() -> None:
    """Who is curtailed when the limit binds: PV first, wind first or in
    proportion to output; teaching tariffs wind 55, PV 45 u/MWh (A-272)."""
    r = src.plant_year()
    cfg = src.ModelConfig()
    lines = ["sharing the curtailment between wind and PV (teaching tariffs",
             "  wind 55, PV 45 u/MWh, A-272):",
             "  PV block  rule            wind cut MWh   PV cut MWh   lost value k u"]
    for f in (1.0, 1.6):
        pv = f * r["pv_av"]
        poc, _ = tail(r["w_av"], pv, cfg, np.zeros(8760, bool))
        cut = np.clip(poc - cfg.export_mw, 0, None)
        share_pv = np.where(r["w_av"] + pv > 0, pv / np.maximum(r["w_av"] + pv, 1e-9), 0)
        rules = {"PV first": (cut - np.minimum(cut, pv), np.minimum(cut, pv)),
                 "wind first": (np.minimum(cut, r["w_av"]), cut - np.minimum(cut, r["w_av"])),
                 "pro rata": (cut * (1 - share_pv), cut * share_pv)}
        for name, (cw, cp) in rules.items():
            val = (55 * cw.sum() + 45 * cp.sum()) / 1e3
            lines.append(f"  {50 * f:5.0f} MW  {name:12s}   {cw.sum():10,.0f}   {cp.sum():10,.0f}"
                         f"     {val:8.1f}")
    lines += ["  the energy lost is the same; who loses it changes the money when",
              "  tariffs or owners differ; the rule belongs in the contracts and",
              "  the controller (chapters 19 and 34), and the model must use it"]
    emit("m_allocation", lines)


def tornado() -> None:
    """Net energy for low and high values of each input (A-272)."""
    r = src.plant_year()
    cfg = src.ModelConfig()
    out = r["outage"]
    _, base = tail(r["w_av"], r["pv_av"], cfg, out)
    b = base.sum() / 1e3
    w0, p0 = r["w_av"], r["pv_av"]
    wake = lambda x: (1 - x) / (1 - 0.0400)                 # noqa: E731
    cases = [
        ("wind long-term factor -/+ 3 %", (w0 * 0.97, p0, cfg), (w0 * 1.03, p0, cfg)),
        ("wake decay k 0.04 / 0.075", (w0 * wake(0.0435), p0, cfg), (w0 * wake(0.0346), p0, cfg)),
        ("wind availability 97 / 99 %", (w0 * 0.97 / 0.981, p0, cfg), (w0 * 0.99 / 0.981, p0, cfg)),
        ("PV long-term factor -/+ 2 %", (w0, p0 * 0.98, cfg), (w0, p0 * 1.02, cfg)),
        ("PV temperature model -/+ 2 %", (w0, p0 * 0.98, cfg), (w0, p0 * 1.02, cfg)),
        ("soiling 2.0 / 1.0 %", (w0, p0 * 0.980 / (1 - 0.0143), cfg),
         (w0, p0 * 0.990 / (1 - 0.0143), cfg)),
        ("PV availability 98 / 99.5 %", (w0, p0 * 0.98 / 0.99, cfg), (w0, p0 * 0.995 / 0.99, cfg)),
        ("load losses 2.0 / 1.0 %", (w0, p0, replace(cfg, loadloss=0.02)),
         (w0, p0, replace(cfg, loadloss=0.01))),
        ("export limit 95 / 105 MW", (w0, p0, replace(cfg, export_mw=95.0)),
         (w0, p0, replace(cfg, export_mw=105.0)))]
    res = []
    for name, lo, hi in cases:
        a = tail(lo[0], lo[1], lo[2], out)[1].sum() / 1e3 - b
        c = tail(hi[0], hi[1], hi[2], out)[1].sum() / 1e3 - b
        res.append((name, a, c))
    res.sort(key=lambda x: -(abs(x[2] - x[1])))
    lines = [f"net energy {b:.2f} GWh; change for the low and high value of each",
             "  input, one at a time (teaching ranges, A-272):",
             "  input                              low GWh   high GWh"]
    for name, a, c in res:
        lines.append(f"  {name:34s} {a:+7.2f}   {c:+7.2f}")
    lines += ["  the wind resource leads by far; the PV resource, the PV",
              "  temperature model and wind availability follow at about 4 GWh",
              "  each from low to high; every other input moves less than 2 GWh;",
              "  the order depends on the ranges, so the ranges are evidence too",
              "  (chapter 16); it tells the owner what to measure better first"]
    emit("m_tornado", lines)
    csv("ch15-tornado.csv", "rank,lo,hi",
        [(i, f"{a:.2f}", f"{c:.2f}") for i, (_, a, c) in enumerate(res)])


def monthly_model() -> None:
    """A spreadsheet model: PV = H_poa x P_STC x annual PR; wind = 12 x
    Weibull (k from each month) energy x the annual factor from the
    hourly chain; plant = sum x (1 - 1.09 % electrical) - own use."""
    r = src.plant_year()
    h = datapack.load_hourly()
    v = h["ws_100m_ms"].to_numpy(float)
    rho = s13.hub_density(h["p_hpa"].to_numpy(float), h["t_air_c"].to_numpy(float))
    veq = w.density_equivalent_speed(v, rho)
    poa = np.asarray(pvyear10.poa()["poa"])
    month = r["month"]
    pr = r["pv_av"].sum() / ek.P_STC / (poa.sum() / 1e3)
    w_factor = r["w_av"].sum() / r["w_dens"].sum()
    el = r["el_loss"].sum() / r["mv"].sum()
    lines = ["a monthly spreadsheet model against the hourly model (GWh):",
             "  month   PV monthly  PV hourly   wind monthly  wind hourly"]
    tm = th = 0.0
    sw_m = 0.0
    for k in range(12):
        m = month == k
        pv_m = poa[m].sum() / 1e3 * ek.P_STC * pr / 1e3
        km, cm = ek.moments_fit(veq[m])
        wm = 12 * ek.weibull_energy(km, cm) * m.mean() / 1e3 * w_factor
        tm += pv_m + wm
        sw_m += wm
        th += r["pv_av"][m].sum() / 1e3 + r["w_av"][m].sum() / 1e3
        lines.append(f"  {k + 1:5d}   {pv_m:8.2f}   {r['pv_av'][m].sum() / 1e3:8.2f}"
                     f"     {wm:8.2f}     {r['w_av'][m].sum() / 1e3:8.2f}")
    net_m = tm * (1 - el) - (src.ModelConfig().aux_wind_mw * 8760 / 1e3
                             + 0.003 * r["pv_av"].sum() / 1e3)
    sw_h = r["w_av"].sum() / 1e3
    lines += [f"  wind: monthly {sw_m:.2f}, hourly {sw_h:.2f} GWh ({100 * (sw_m / sw_h - 1):+.1f} %);"
              " PV: equal sums",
              f"  MV total: monthly {tm:.2f}, hourly {th:.2f} GWh",
              f"  net: monthly {net_m:.2f} GWh (no limit, no import, no outage),"
              f" hourly {r['net'].sum() / 1e3:.2f} GWh",
              "  with one annual PR the monthly PV runs about 4 % high in summer",
              "  and 5 % low in winter while the year agrees by construction;",
              "  the wind is low only because of the monthly Weibull fits (the",
              "  hourly speeds with the same annual factor give the hourly sum);",
              "  and a monthly model cannot see clipping, the limit, import or",
              "  storage"]
    emit("m_monthly", lines)


if __name__ == "__main__":
    environmental()
    availability()
    battery_overbuild()
    allocation()
    tornado()
    monthly_model()
