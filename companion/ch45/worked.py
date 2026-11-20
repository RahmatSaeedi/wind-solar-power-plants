"""Chapter 45 - small worked examples (E-lines) and the numerical answers
of the exercises (P-lines), each computed here.

Run from the project root:   python -m companion.ch45.worked
Writes companion/ch45/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch45 import examples_a as ea
from companion.ch45 import examples_b as eb
from companion.ch45 import examples_c as ec
from companion.ch45 import integrated as it
from companion.ch45 import lab_d
from companion.ch45 import sources as src
from companion.ch45.common import emit
from plantp import cellmfg as cf


def worked() -> None:
    lines = [f"E01 areal capacity 40 mg/cm2 x 0.95 x 155 mAh/g: "
             f"{cf.areal_capacity(40, 0.95, 155):.2f} mAh/cm2",
             f"E02 N/P of 6.17 over 5.89: {cf.np_ratio(6.17, 5.89):.3f}",
             f"E03 K-value of 3.3150 -> 3.3143 V in 14 days: "
             f"{cf.k_value(3.3150, 3.3143, 14):.3f} mV/day",
             f"E04 string of 316, 317, 314.5 Ah: "
             f"{cf.string_capacity([316, 317, 314.5]):.1f} Ah",
             f"E05 rack of 416 cells, 2.5-3.65 V: "
             f"{416 * 2.5:.0f}-{416 * 3.65:.0f} V",
             f"E06 module energy 52 x 314 Ah x 3.2 V: {52 * 314 * 3.2 / 1000:.1f} kWh",
             f"E07 weld heat at 157 A, 60 uohm: {157 ** 2 * 60e-6:.2f} W",
             f"E08 water at a -40 C dew point: {cf.abs_humidity_g_m3(-40):.3f} g/m3",
             f"E09 sample of 50 from 2000 with 5 bad, at least one: "
             f"{1 - math.comb(1995, 50) / math.comb(2000, 50):.1%}",
             f"E10 balancing 63 Ah at 0.1 A: {63 / 0.1:,.0f} h"]
    emit("worked", lines)


def solutions() -> None:
    bal = ea.balance()
    lev = ea.levels()
    win = ea.windows()
    nif = ea.interfaces()
    coat = eb.coating()
    dry = eb.dry_room()
    gr = eb.grading()
    mt = eb.matching()
    wl = eb.welds()
    bm = eb.bms()
    out = [f"P01 N/P as designed and at the worst spot: {bal['np']:.3f}, "
           f"{bal['worst']:.3f}",
           f"P02 facing area of one cell: {bal['area'] / 1e4:.2f} m2",
           f"P03 system cells and MWh: {lev['total']:,}, {lev['mwh']:.2f}",
           f"P04 rack BMS window: {win['rack'][0]:.0f}-{win['rack'][1]:.0f} V",
           f"P05 interfaces cell to plant: {nif}",
           f"P06 Cpk of coating lines A and B: {coat['A'][3]:.2f}, {coat['B'][3]:.2f}",
           f"P07 dry-room water share of a hall: "
           f"{dry['dry room (teaching)'] / dry['ordinary factory hall']:.1%}",
           f"P08 flags K / capacity / resistance: {len(gr['f_k'])}, "
           f"{len(gr['f_c'])}, {len(gr['f_r'])}",
           f"P09 module capacity gain by sorting: "
           f"{mt['sorted'][1] - mt['arrival order'][1]:.2f} Ah",
           f"P10 cold welds and worst heat: {len(wl['bad'])}, {wl['worst_w']:.2f} W",
           f"P11 BMS limits wrong: {', '.join(bm['bad'])}"]
    out += more()
    emit("solutions", out)


def more() -> list[str]:
    dv = ec.divided()
    sh = ec.shipping()
    rp = ec.replacement()
    eo = ec.end_of_life()
    sd = lab_d.soc_day()
    rc = lab_d.receiving()
    rt = lab_d.rest_test()
    bl = lab_d.balancing()
    tr = lab_d.trail()
    hb = it.by_hand()
    mod = dv["module"]
    return [f"P12 module volts and kWh: {mod[0]:.0f} V, {mod[1]:.1f} kWh",
            f"P13 container MWh at 30 % SOC: {sh[0.3]:.2f}",
            f"P14 string Ah after a new module; days to balance: "
            f"{rp['string']:.0f}, {rp['hours'] / 24:.0f}",
            f"P15 container cells recovered: {eo['recovered'] / 1000:.1f} of "
            f"{eo['total'] / 1000:.1f} t",
            f"P16 SOC range and cut steps (charge/discharge): {sd['lo']:.2f}-"
            f"{sd['hi']:.2f}, {sd['cut_c']}/{sd['cut_d']}",
            f"P17 chance a 50-cell sample finds a leaker; cells for 90 %: "
            f"{rc['p50']:.1%}, {rc['need']}",
            f"P18 leakers caught at 14 / 7 days: {rt[14][1]:.1f}, {rt[7][1]:.1f}",
            f"P19 extra leak current and balancing duty: {bl['extra']:.1f} mA, "
            f"{bl['duty']:.0%}",
            f"P20 trail deviations and gaps: {tr.get('deviation', 0)}, "
            f"{tr.get('gap', 0)}",
            f"P21 S1 nominal and usable MWh, C-rate: {hb['e_nom']:.2f}, "
            f"{hb['usable']:.2f}, {hb['c_rate']:.2f}",
            f"P22 usable MWh in year 10 (linear fade): {hb['out'][10]:.2f}"]


if __name__ == "__main__":
    worked()
    solutions()
    _ = src
