"""Chapter 16 - three integrated Plant P examples: the PV block alone
(introductory), a wind-only plant against the hybrid under the same
financing rules (intermediate), and the financing memo of the hybrid
(integrated).

Run from the project root:   python -m companion.ch16.integrated
Writes companion/ch16/expected/i_*.txt.
"""
from __future__ import annotations

import math

from companion.ch16 import lab_d, lab_e, sources as src
from companion.ch16.common import emit
from plantp import yieldrisk as yr


def pv_alone() -> None:
    b = src.base()
    u_lt = src.u_group(src.PV)
    u1 = math.hypot(u_lt, b["iav_p"])
    lines = ["the PV block alone (at MV, before the plant end):",
             f"  P50 {b['pv']:.2f} GWh; long-term {100 * u_lt:.2f} %, year-to-year"
             f" {100 * b['iav_p']:.2f} %",
             f"  one year {100 * u1:.2f} %: P90 {yr.p_value(b['pv'], u1):.2f} GWh,"
             f" P99 {yr.p_value(b['pv'], u1, 0.99):.2f} GWh",
             f"  chapter 12 gave the irradiance alone 2.8 % long-term; the PV",
             "  energy adds the conversion and loss parts on top"]
    emit("i_pvalone", lines)


def wind_vs_hybrid() -> None:
    """Same rules for both: opex in proportion to P50 energy (13.55 k u
    per GWh, as for the hybrid), price and ratios of lab E."""
    b = src.base()
    s = src.sigmas()
    opex_per = lab_e.OPEX / b["net"]
    lines = ["a wind-only plant against the hybrid, same financing rules:",
             "  plant       P50 GWh   sigma 1y %   P90 1y GWh   debt k u   debt per GWh"]
    plants = {"wind only": (b["w"] * s["ratio"],
                            math.hypot(src.u_group(src.WIND), b["iav_w"])),
              "hybrid": (b["net"], lab_e.sig_one_year() / b["net"])}
    for name, (p50, u) in plants.items():
        e = {"P50": p50, "P90 1y": p50 * (1 - 1.2816 * u), "P99 1y": p50 * (1 - 2.3263 * u)}
        cf = {k: v * lab_e.PRICE - opex_per * p50 for k, v in e.items()}
        d, bind = yr.debt_size(cf, lab_e.DSCR, lab_e.RATE, lab_e.YEARS)
        lines.append(f"  {name:10s}  {p50:7.2f}    {100 * u:6.2f}      {e['P90 1y']:7.2f}"
                     f"     {d:8,.0f}   {d / p50:7.1f} ({bind})")
    lines += ["  the hybrid's smaller relative spread lets each GWh carry more",
              "  debt: part of the value of combining wind and PV is financial"]
    emit("i_windhybrid", lines)


def memo() -> None:
    b = src.base()
    sig = lab_e.sig_one_year()
    e = lab_e.energies(sig)
    cf = {k: lab_e.cfads(v) for k, v in e.items()}
    d, bind = yr.debt_size(cf, lab_e.DSCR, lab_e.RATE, lab_e.YEARS)
    lines = ["financing memo, Plant P (S0), teaching terms A-281:",
             f"  yield: P50 {b['net']:.0f} GWh; one-year sigma {sig:.0f} GWh;"
             f" P90 1y {e['P90 1y']:.0f}; P99 1y {e['P99 1y']:.0f} GWh",
             f"  ten-year P90 {b['net'] - 1.2816 * lab_d.total(lab_d.items(), 10) * src.sigmas()['ratio']:.0f}"
             " GWh (for the average over a loan)",
             f"  debt sized {d:,.0f} k u by the {bind} case; P50 cover"
             f" {cf['P50'] / (d / yr.annuity(lab_e.RATE, lab_e.YEARS)):.2f}",
             "  separate downside cases: price, cost, availability guarantee",
             "  (lab E); a P90 delivery guarantee costs about 71 k u a year",
             "  open items: U-061 lender's cases and ratios, U-062 a second",
             "    year of measurement, U-063 correlation of the long-term",
             "    errors of wind and PV"]
    emit("i_memo", lines)


if __name__ == "__main__":
    pv_alone()
    wind_vs_hybrid()
    memo()
