"""Chapter 15, sections A-C - model architecture, conversion and gross-to-
net: time resolution (ten-minute against hourly wind), time alignment of
the two technologies, one clear PV day step by step, the wake loss of W2b
by direction, how wind and PV coincide, clipping against the DC/AC ratio,
the order of soiling and clipping, degradation over the life, a battery
on the curtailment, and when the grid outages fall.

Run from the project root:   python -m companion.ch15.examples_abc
Writes companion/ch15/expected/{a,b,c}_*.txt and diagrams/data/ch15-*.csv.
Model 15.1; A-267, A-275.
"""
from __future__ import annotations

import numpy as np

from companion.ch11 import lab_d as l11
from companion.ch13 import sources as s13
from companion.ch14 import examples_b as eb
from companion.ch15 import sources as src
from companion.ch15.common import csv, emit

MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


# ------------------------------------------------------------ A
def resolution() -> None:
    t = s13.mast_year()["true"]
    v10 = t["v100"]
    p10 = l11.pack_power(v10).mean() * 8760 / 1e3                 # MWh per turbine
    vh = v10.reshape(-1, 6).mean(axis=1)
    ph = l11.pack_power(vh).sum() / 1e3
    pv = src.plant_year()["pv_clip"]
    lines = ["time resolution of the inputs (one turbine, pack curve, mast year):",
             f"  ten-minute speeds {p10:8,.0f} MWh; hourly means {ph:8,.0f} MWh"
             f" ({100 * (ph / p10 - 1):+.2f} %)",
             "  the power curve is curved: averaging the speed first changes",
             "  the energy a little; clipping and curtailment, which act on",
             "  peaks, need the finest resolution the data allow",
             f"  PV clipping hours in the hourly model: {(pv >= 49.0 - 1e-6).sum()} h"]
    emit("a_resolution", lines)


def alignment() -> None:
    r = src.plant_year()
    w_, pv = r["w_av"], r["pv_av"]
    lines = ["time alignment: PV read one hour late (interval-end labels taken as",
             "  interval-start, chapter 5) against the right alignment:",
             "                             right     PV 1 h late"]
    for name, p in (("right", pv), ("late", np.r_[0.0, pv[:-1]])):
        mv = w_ + p
        cur = np.clip(mv - 100, 0, None).sum()
        both = int(((w_ > 30) & (p > 25)).sum())
        corr = float(np.corrcoef(w_, p)[0, 1])
        if name == "right":
            base = (cur, both, corr)
        else:
            late = (cur, both, corr)
    lines += [f"  curtailment at MV, MWh   {base[0]:8,.0f}    {late[0]:8,.0f}",
              f"  hours both above half     {base[1]:6d}      {late[1]:6d}",
              f"  correlation wind-PV       {base[2]:+.3f}      {late[2]:+.3f}",
              "  the annual energies do not change, but every hourly product",
              "  (curtailment, coincidence, storage, dispatch) does: check the",
              "  labels of every input before the first run"]
    emit("a_alignment", lines)


# ------------------------------------------------------------ B
def pv_day() -> None:
    r = src.plant_year()
    day = 173                                    # 23 June
    sl = slice(day * 24, day * 24 + 24)
    lines = ["one clear June day, PV chain, MW (model 15.1):",
             "  hour   STC    DC gross   DC     inverter  clipped  at MV"]
    for h in range(6, 20, 2):
        k = day * 24 + h
        lines.append(f"  {h:02d}   {r['pv_stc'][k]:6.2f}  {r['pv_dc_gross'][k]:7.2f}  {r['pv_dc'][k]:6.2f}"
                     f"   {r['pv_inv'][k]:6.2f}   {r['pv_clip'][k]:6.2f}   {r['pv_av'][k]:6.2f}")
    e = {k: float(r[k][sl].sum()) for k in ("pv_stc", "pv_inv", "pv_clip", "pv_av")}
    lines += [f"  day: STC {e['pv_stc']:.0f}, after inverter {e['pv_inv']:.0f}, clipped"
              f" {e['pv_inv'] - e['pv_clip']:.1f}, at MV {e['pv_av']:.0f} MWh",
              "  midday the temperature takes the most; clipping takes the top",
              "  of the noon hours only"]
    emit("b_pvday", lines)


def wake_sectors() -> None:
    flat, terr, wake = src.wind_tables()
    tab = eb.wind_table()
    sec_t, sec_w = np.zeros(12), np.zeros(12)
    for (a, b), n in tab.items():
        s = int(((2 * a + 1) % 360) // 30)
        sec_t[s] += n * terr[(a, b)]
        sec_w[s] += n * wake[(a, b)]
    lines = ["wake loss of W2b by direction sector (data year):",
             "  sector     energy share   wake loss"]
    rows = []
    for k in range(12):
        share = sec_t[k] / sec_t.sum()
        loss = 1 - sec_w[k] / sec_t[k] if sec_t[k] > 0 else 0.0
        lines.append(f"  {30 * k:3d}-{30 * k + 30:3d}      {100 * share:5.1f} %       {100 * loss:5.1f} %")
        rows.append((30 * k + 15, f"{100 * loss:.2f}", f"{100 * share:.2f}"))
    csv("ch15-wakesector.csv", "dir,loss,share", rows)
    lines += ["  the rows stand across the prevailing sectors: small losses",
              "  where the energy is; large losses only in rare sectors along",
              "  the rows (north and south)"]
    emit("b_wakesectors", lines)


def coincidence() -> None:
    r = src.plant_year()
    w_, pv, m = r["w_av"], r["pv_av"], r["month"]
    hour = np.arange(8760) % 24
    rows = [(h, f"{w_[hour == h].mean():.2f}", f"{pv[hour == h].mean():.2f}") for h in range(24)]
    csv("ch15-diurnal.csv", "hour,wind,pv", rows)
    lines = ["how wind and PV coincide at Plant P (model 15.1):",
             f"  hourly correlation {np.corrcoef(w_, pv)[0, 1]:+.3f}",
             f"  hours with both above half their rating: {int(((w_ > 30) & (pv > 25)).sum())}",
             f"  hours with neither above a tenth: {int(((w_ < 6) & (pv < 5)).sum())}",
             "  month   wind GWh   PV GWh   sum"]
    for k in range(12):
        a, b = w_[m == k].sum() / 1e3, pv[m == k].sum() / 1e3
        lines.append(f"  {MONTHS[k]}     {a:6.2f}     {b:5.2f}   {a + b:6.2f}")
    lines += ["  the negative correlation and the night-heavy wind (chapter 13)",
              "  make the sum steadier than either part: few hours exceed the",
              "  export limit, and quiet hours are fewer than for each alone"]
    emit("b_coincidence", lines)


# ------------------------------------------------------------ C
def clipping() -> None:
    from companion.ch10.integrated import EFF_POINTS
    from plantp import pe
    c0, c1, c2 = pe.fit_loss_coeffs(EFF_POINTS)
    r = src.plant_year()
    lines = ["clipping against the DC/AC ratio (AC fixed at 50 MW, DC scaled):",
             "  DC/AC   DC MWp   AC energy GWh   clipped GWh   clipped %"]
    for ratio in (1.1, 1.2, 1.3, 1.4):
        dc = r["pv_dc"] * ratio / 1.2
        x = dc / 50.0
        y = np.where(x > c0, (-(1 + c1) + np.sqrt((1 + c1) ** 2 - 4 * c2 * (c0 - x))) / (2 * c2), 0.0)
        inv = y * 50.0
        clip = np.minimum(inv, 49.0)
        lost = inv.sum() - clip.sum()
        lines.append(f"  {ratio:.1f}    {60.06 * ratio / 1.2:6.1f}      {clip.sum() / 1e3:7.2f}"
                     f"         {lost / 1e3:5.2f}       {100 * lost / inv.sum():5.2f}")
    lines += ["  more DC per AC fills the inverter in more hours and loses a",
              "  growing share at the top; the optimum is an economic one",
              "  (chapter 10 c_dcac, chapter 20)"]
    emit("c_clipping", lines)


def order() -> None:
    r = src.plant_year()
    cfg = src.ModelConfig()
    from companion.ch10.integrated import EFF_POINTS
    from plantp import pe
    c0, c1, c2 = pe.fit_loss_coeffs(EFF_POINTS)
    dc_soiled = r["pv_dc"] * (1 - cfg.soiling)
    x = dc_soiled / 50.0
    y = np.where(x > c0, (-(1 + c1) + np.sqrt((1 + c1) ** 2 - 4 * c2 * (c0 - x))) / (2 * c2), 0.0)
    before = np.minimum(y * 50.0, 49.0).sum()
    after = (r["pv_clip"] * (1 - cfg.soiling)).sum()
    lines = ["order of two losses: soiling before the inverter (physical) or",
             "  after clipping (a factor on AC energy):",
             f"  soiling on DC, then inverter and clipping   {before / 1e3:7.2f} GWh",
             f"  clipping first, soiling factor on AC         {after / 1e3:7.2f} GWh",
             f"  difference {(before - after) / 1e3:+.2f} GWh ({100 * (before / after - 1):+.2f} %)",
             "  in clipped hours dirt removes energy that would have been",
             "  clipped anyway: soiling on DC loses less; a factor on AC",
             "  counts it twice (double counting in a small way)"]
    emit("c_order", lines)


def degradation() -> None:
    r = src.plant_year()
    pv1 = r["pv_av"].sum() / 1e3 / (1 - 0.005)
    lines = ["PV energy over the life with 0.5 %/yr degradation (A-275):",
             "  year   energy GWh   against year 0"]
    tot = 0.0
    for y in range(1, 26):
        e = pv1 * (1 - 0.005 * y)
        tot += e
        if y in (1, 5, 10, 15, 20, 25):
            lines.append(f"  {y:3d}     {e:7.2f}      {100 * (e / pv1 - 1):+5.1f} %")
    lines += [f"  25-year mean {tot / 25:.2f} GWh ({100 * (tot / 25 / pv1 - 1):+.1f} % against year 0)",
              "  a year-1 report and a life-mean report differ by about 6 %:",
              "  each states which it is (chapter 16 and the finance model)"]
    emit("c_degradation", lines)


def storage() -> None:
    """S1: 20 MW / 40 MWh, usable 32 MWh, round trip 86 % (A-009, A-010):
    store curtailed energy, release it in the next hours with headroom."""
    r = src.plant_year()
    poc = r["poc"]
    soc, stored, released = 0.0, 0.0, 0.0
    eta = 0.86 ** 0.5
    for k in range(8760):
        if poc[k] > 100:
            ch = min(poc[k] - 100, 20.0, (32.0 - soc) / eta)
            soc += ch * eta
            stored += ch
        elif soc > 0:
            dis = min(100 - poc[k], 20.0, soc * eta)
            soc -= dis / eta
            released += dis
    lines = ["the S1 battery on the curtailment (20 MW, 32 MWh usable, 86 %):",
             f"  curtailed without storage {r['curtailed'].sum():,.0f} MWh",
             f"  stored {stored:,.0f} MWh, released {released:,.0f} MWh"
             f" (losses {stored - released:,.0f} MWh)",
             "  the curtailment of this plant is small, so a battery sized",
             "  for it would sit idle: its value lies elsewhere (shifting,",
             "  reserve, firm delivery, chapters 17-19)"]
    emit("c_storage", lines)


def outages() -> None:
    r = src.plant_year()
    rng = np.random.default_rng(153)
    lost = []
    for _ in range(500):
        h = rng.choice(8760, 12, replace=False)
        lost.append(r["delivered"][h].sum())
    lost = np.array(lost)
    lines = ["12 grid-outage hours a year: energy lost depends on when they fall",
             f"  model run (seed 151): {(r['delivered'] - r['net']).sum():.0f} MWh",
             f"  500 random years: mean {lost.mean():.0f} MWh, 10-90 % {np.quantile(lost, 0.1):.0f}"
             f" .. {np.quantile(lost, 0.9):.0f} MWh",
             "  outages in storms (windy hours) cost more than the mean: a",
             "  grid-availability figure needs its timing as well (chapter 27)"]
    emit("c_outages", lines)


if __name__ == "__main__":
    resolution()
    alignment()
    pv_day()
    wake_sectors()
    coincidence()
    clipping()
    order()
    degradation()
    storage()
    outages()
