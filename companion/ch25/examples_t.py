"""Chapter 25 - sixth round: a second test dossier (a PV unit
transformer), N-1 emergency loading of the remaining main transformer,
the hot-spot factor's weight in ageing, the reactive power the
transformers consume and the plant must supply, staging the export
substation with the second transformer late, and the noise of all the
site's transformers at the boundary.

Run from the project root:   python -m companion.ch25.examples_t
Writes companion/ch25/expected/t_*.txt. Teaching values (A-326..A-330
extended).
"""
from __future__ import annotations

import math

from companion.ch25 import sources as src
from companion.ch25.common import emit
from companion.ch25.examples_c import review_item
from plantp import transformer as tr

M = src.MAIN

PV_DOSSIER = [   # PV unit transformer 5.5 MVA (teaching contract tolerances)
    ("no-load loss kW", 4.5, 5.4, ("max", 0.15)),
    ("load loss kW at 75 C", 45.0, 46.8, ("max", 0.15)),
    ("total loss kW", 49.5, 52.2, ("max", 0.10)),
    ("impedance % (principal tap)", 6.0, 6.2, ("band", 0.10)),
    ("ratio error % (principal tap)", 0.0, 0.2, ("abs", 0.5)),
    ("top-oil rise K", 60.0, 61.5, ("limit", 0.0)),
    ("sound power dB(A)", 72.0, 73.5, ("limit", 0.0)),
]


def pv_dossier() -> None:
    lines = ["second dossier: a PV unit transformer, 5.5 MVA (teaching)",
             "  quantity                       declared  measured  accept       result"]
    fails = []
    for name, d, m, tol in PV_DOSSIER:
        ok, how = review_item(name, d, m, tol)
        lines.append(f"  {name:30s} {d:8.3g}  {m:8.3g}  {how:12s} {'ok' if ok else 'NOT OK'}")
        if not ok:
            fails.append(name)
    pen = (5.4 - 4.5) * 6.84 + (46.8 - 45.0) * 0.88
    lines += [f"  not accepted: {', '.join(fails)}",
              f"  loss overrun priced: {pen:.1f} k u per unit, {pen * 10:.0f} k u for ten units",
              "  the no-load loss is 20 % over (a core-steel or joint",
              "  problem in this design), the oil rise and the sound exceed",
              "  their limits: one design, ten units - the maker explains",
              "  and corrects before the series ships; a type fault is",
              "  cheapest found on the first unit"]
    emit("t_pvdossier", lines)


def n_minus_1() -> None:
    d_or, d_hr, r, x, y = 52.0, 26.0, 6.0, 0.8, 1.6
    tau_o, tau_w, amb = 180.0, 7.0, 35.0
    lines = ["N-1: one main transformer out, the other takes the section's export",
             "  (start at 0.7 pu, air 35 C; teaching emergency limit 140 C hot spot)",
             "  load pu   minutes to 140 C   hot spot after 4 h C"]
    for k in (1.1, 1.2, 1.3, 1.5):
        d_o = d_or * ((1 + r * 0.49) / (1 + r)) ** x
        d_h = d_hr * 0.7 ** y
        t_lim, hs4 = None, None
        for minute in range(1, 24 * 60):
            d_o += (d_or * ((1 + r * k * k) / (1 + r)) ** x - d_o) / tau_o
            d_h += (d_hr * k ** y - d_h) / tau_w
            hs = amb + d_o + d_h
            if t_lim is None and hs >= 140:
                t_lim = minute
            if minute == 240:
                hs4 = hs
        lines.append(f"  {k:7.1f}   {('never' if t_lim is None else str(t_lim)):>16s}   {hs4:20.0f}")
    lines += ["  the oil's slow time constant buys time: the remaining unit",
              "  carries a short overload while the plant controller limits",
              "  export (ch 20) - the limit, the time and the ageing spent",
              "  come from the loading guide and the maker's emergency",
              "  rating, written into the operating rules"]
    emit("t_nminus1", lines)


def hotspot_factor() -> None:
    lines = ["the hot-spot factor H (ratio of hot-spot gradient to mean gradient):",
             "  H     hot spot at 1.0 pu, 30 C C   relative ageing"]
    base = None
    for h in (1.1, 1.2, 1.3, 1.4):
        hs = 30 + 52 + 26 * h / 1.3
        age = tr.ageing_rate(hs)
        base = base or age
        lines.append(f"  {h:3.1f}   {hs:29.1f}   {age / base:15.2f}")
    lines += ["  the hot spot is a design property: winding layout, oil",
              "  ducts and leakage flux set H; a higher H means more ageing",
              "  at the same load - fibre-optic sensors in the windings",
              "  measure it directly, the heat run confirms the design value"]
    emit("t_hfactor", lines)


def reactive() -> None:
    lines = ["reactive power the transformers consume (I^2 X), and the line:",
             "  export MW   each T (half) Mvar   both T Mvar   line Mvar   total"]
    x_line = 7.06 * 0.40
    for p in (25, 50, 75, 100):
        s_each = p / 0.95 / 2
        q_t = M["uk_pct"] / 100 * s_each ** 2 / M["s_mva"]
        i = p / 0.95 * 1e6 / (math.sqrt(3) * 132e3)
        q_l = 3 * i ** 2 * x_line / 1e6
        lines.append(f"  {p:9d}   {q_t:18.2f}   {2 * q_t:11.2f}   {q_l:9.2f}   {2 * q_t + q_l:5.2f}")
    lines += ["  at full export the transformers take about 10 Mvar: the",
              "  plant's reactive capability at the POC is what the units",
              "  produce minus this - the requirement is met at the POC, so",
              "  the PQ study (ch 20, ch 28) carries the transformers in it"]
    emit("t_reactive", lines)


def staging() -> None:
    share_above = 0.18
    energy = 295e3
    lines = ["staging: the second main transformer arrives late (teaching)",
             "  months late   energy above one unit's rating lost MWh   k u at 70"]
    for months in (1, 3, 6):
        lost = energy * share_above * months / 12
        lines.append(f"  {months:11d}   {lost:39.0f}   {lost * 0.07:9.0f}")
    lines += ["  with one transformer the plant exports up to its rating and",
              "  curtails the rest: energising stage by stage (ch 23 lesson",
              "  C) with one unit first is possible, and the late unit's",
              "  cost is the energy above 63 MVA - a number for the",
              "  delivery contract's delay damages (ch 39)"]
    emit("t_staging", lines)


def site_noise() -> None:
    sources = [("main transformers (2)", 2, 72.0, 120.0), ("PV unit transformers (10)", 10, 62.0, 300.0),
               ("PV inverters (10)", 10, 70.0, 300.0), ("BESS containers HVAC (8)", 8, 75.0, 250.0)]
    lines = ["noise of the site's sources at the nearest home (free field, teaching):",
             "  group                         each dB(A) at 2 m   distance m   at home"]
    at_home = []
    for name, n, lw2, r in sources:
        single = tr.sound_at(lw2, 2.0, r)
        group = tr.sound_sum([single] * n)
        at_home.append(group)
        lines.append(f"  {name:29s} {lw2:17.0f}   {r:10.0f}   {group:7.1f}")
    night = tr.sound_sum([at_home[0], at_home[1], at_home[3]])
    lines += [f"  all together by day: {tr.sound_sum(at_home):.1f} dB(A); at night the PV",
              f"  inverters stop and {night:.1f} dB(A) remains - the main",
              "  transformers and the battery HVAC set the night level, so",
              "  both are in the noise specification; the noise study (ch 14,",
              "  33) uses real data, ground and screening, and the",
              "  authority's limit and method"]
    emit("t_noise", lines)


if __name__ == "__main__":
    pv_dossier()
    n_minus_1()
    hotspot_factor()
    reactive()
    staging()
    site_noise()
