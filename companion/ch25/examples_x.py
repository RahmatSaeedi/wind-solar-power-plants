"""Chapter 25 - tenth round: the plant's reactive balance at night
(cables against transformer magnetising), the life cost of the chosen
main transformer, the turbine transformer in the nacelle or at the tower
base, the loss statistics of a series of unit transformers, and the gas
pressure of a transformer shipped without oil.

Run from the project root:   python -m companion.ch25.examples_x
Writes companion/ch25/expected/x_*.txt and diagrams/data/ch25-nightq.csv.
Teaching values (A-326..A-330 extended).
"""
from __future__ import annotations

import math
import statistics

from companion.ch25 import sources as src
from companion.ch25.common import csv, emit

M = src.MAIN
W = 2 * math.pi * 50


def q_cable(c_uf_km: float, km: float, kv: float = 33.0) -> float:
    """Charging reactive power (Mvar) of a three-phase cable."""
    return (kv * 1e3) ** 2 * W * c_uf_km * 1e-6 * km / 1e6


def night_q() -> None:
    wind = 3 * (q_cable(0.30, 1.1) + q_cable(0.21, 3.3))
    rows = [("132 kV line charging (ch 24)", 0.30),
            ("wind feeders, 3 x 4.4 km", wind),
            ("PV feeders, 3 x 3.0 km (teaching)", 3 * q_cable(0.21, 3.0)),
            ("BESS feeders, 2 x 0.5 km", 2 * q_cable(0.21, 0.5)),
            ("main transformers, i0 0.20 %", -2 * M["s_mva"] * M["i0_pct"] / 100),
            ("PV units, 10 x 5.5 MVA, i0 0.8 %", -10 * 5.5 * 0.008),
            ("wind units, 12 x 5.6 MVA, i0 1.2 %", -12 * 5.6 * 0.012),
            ("BESS units, 4 x 5.5 MVA, i0 0.8 %", -4 * 5.5 * 0.008)]
    csv("ch25-nightq.csv", "k,q", [(k, f"{q:.3f}") for k, (_, q) in enumerate(rows)])
    lines = ["reactive balance at night, no output (+ produced, - absorbed):",
             "  element                                Mvar"]
    for name, q in rows:
        lines.append(f"  {name:36s} {q:+7.2f}")
    net = sum(q for _, q in rows)
    pv_off = net + 10 * 5.5 * 0.008
    lines += [f"  net at the POC {net:+.2f} Mvar (exported, leading)",
              f"  with the PV units switched off at night: {pv_off:+.2f} Mvar",
              "  the magnetising of 28 transformers nearly balances the",
              "  cables; switching the PV units off saves their no-load",
              "  loss (lesson units at night) but doubles the night export",
              "  of Mvar - if the grid asks for zero, the inverters' night",
              "  service or a small reactor absorbs it (ch 20, ch 28)"]
    emit("x_nightq", lines)


def life_cost() -> None:
    rate, years = 0.075, 25
    ann = (1 - (1 + rate) ** -years) / rate
    items = [("price (bid B)", 1_700.0),
             ("losses capitalised (A 6.84, B 0.88)", 6.84 * 42 + 0.88 * 290),
             ("routine maintenance 8 k u a year", 8 * ann),
             ("tap changer overhauls, years 10, 20", 40 / 1.075 ** 10 + 40 / 1.075 ** 20),
             ("online monitoring (DGA, bushings)", 60.0),
             ("end of life: removal 30, scrap +45", (30 - 45) / 1.075 ** 25)]
    tot = sum(v for _, v in items)
    lines = ["life cost of one main transformer, present value at 7.5 % (k u):",
             "  item                                    k u     share"]
    for name, v in items:
        lines.append(f"  {name:37s} {v:7.0f}   {v / tot:6.1%}")
    lines += [f"  total {tot:,.0f} k u: the price is {items[0][1] / tot:.0%} of it and the losses",
              f"  {items[1][1] / tot:.0%}; maintenance and monitoring together are small, and",
              "  a monitoring system that avoids one long outage (lesson",
              "  failure) repays itself many times"]
    emit("x_lifecost", lines)


def nacelle() -> None:
    p, l_m, pf = 5.0e6, 110.0, 1.0
    i_lv = p / (math.sqrt(3) * 690 * pf)
    r_lv = 0.095 * l_m / 1e3 / 12                 # 12 x 240 mm2 Cu per phase
    loss_lv = 3 * i_lv ** 2 * r_lv
    i_mv = p / (math.sqrt(3) * 33e3 * pf)
    r_mv = 0.32 * l_m / 1e3                        # one 3 x 95 mm2 Al MV cable
    loss_mv = 3 * i_mv ** 2 * r_mv
    e_ratio = 0.30                                 # loss load factor, wind unit
    lines = ["turbine transformer at the tower base or in the nacelle (teaching):",
             f"  5 MW, 110 m of cable down the tower; LV 690 V: {i_lv:,.0f} A,",
             "  12 x 240 mm2 copper per phase; MV 33 kV: one 3 x 95 mm2 cable",
             f"  LV cable loss at full power {loss_lv / 1e3:5.1f} kW ({loss_lv / p:.2%})",
             f"  MV cable loss at full power {loss_mv / 1e3:5.2f} kW",
             f"  a year (loss load factor {e_ratio}): {(loss_lv - loss_mv) * e_ratio * 8760 / 1e6:.0f} MWh"
             " saved per turbine",
             "  in the nacelle: lower losses, 36 LV cables fewer down the",
             "  tower; but some 10 t more at the tower top (160 t nacelle,",
             "  ch 11), heat and fire inside the nacelle, and access for",
             "  maintenance at height - Plant P's base keeps it in the tower",
             "  base (A-328); the turbine maker's design decides"]
    emit("x_nacelle", lines)


def series_stats() -> None:
    p0 = [4.42, 4.51, 4.47, 4.60, 4.38, 4.55, 4.49, 4.63, 4.44, 4.58]
    pk = [44.1, 45.6, 44.9, 46.2, 43.8, 45.1, 44.7, 46.8, 44.0, 45.9]
    lines = ["routine-test losses of the ten PV unit transformers (after the",
             "  design fix of lesson D), guarantee 4.5 / 45.0 kW; individual",
             "  limit +15 %; teaching clause: the series average is priced",
             "  quantity      mean    s.d.   max    individual ok   average over"]
    pen = 0.0
    for name, vals, g, factor in (("no-load kW", p0, 4.5, 6.84), ("load kW", pk, 45.0, 0.88)):
        mu, sd = statistics.mean(vals), statistics.stdev(vals)
        over = max(0.0, mu - g)
        pen += over * factor * len(vals)
        ok = all(v <= 1.15 * g for v in vals)
        lines.append(f"  {name:12s} {mu:6.2f}  {sd:6.2f}  {max(vals):5.2f}    {'yes' if ok else 'no':>12s}"
                     f"   {over:+.2f}")
    lines += [f"  every unit is inside its own limit; the averages are slightly",
              f"  over the guarantee - priced over ten units: {pen:.1f} k u",
              "  a tolerance per unit protects against a bad unit; a clause",
              "  on the series average protects against a design that is a",
              "  little worse every time"]
    emit("x_series", lines)


def gas_pressure() -> None:
    p_atm = 1.013
    lines = ["a tank shipped without oil, filled with dry air (teaching):",
             "  departure 0.25 bar(g) at 30 C; readings on arrival:",
             "  arrival     expected bar(g)   measured bar(g)   lost   verdict"]
    for t_c, meas in ((10.0, 0.16), (10.0, 0.12), (-5.0, 0.11)):
        exp = (p_atm + 0.25) * (t_c + 273.15) / (30 + 273.15) - p_atm
        lost = 1 - (p_atm + meas) / (p_atm + exp)
        verdict = "tight" if lost < 0.01 else "leak: check dew point"
        lines.append(f"  {t_c:5.0f} C   {exp:15.3f}   {meas:15.2f}   {lost:5.1%}   {verdict}")
    lines += ["  a pressure that falls because the tank cooled is not a leak;",
              "  only the drop beyond the gas law says air left - and moist",
              "  air may have come in: the dew point of the gas and the",
              "  maker's assessment decide whether extra drying is needed",
              "  before oil filling (evidence for the arrival record)"]
    emit("x_gas", lines)


if __name__ == "__main__":
    night_q()
    life_cost()
    nacelle()
    series_stats()
    gas_pressure()
