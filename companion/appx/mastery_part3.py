"""Appendix X - answers of the Part III diagnostic mastery test (chapters
12-16): explain the source, the loss assumptions, the uncertainty and the
limitations behind a production estimate of Plant P.

Run from the project root:   python -m companion.appx.mastery_part3
Writes companion/appx/expected/mastery_part3.txt.
Data pack 1.1.0 (synthetic), S0; model 15.1 (D-019) and the budget of
chapter 16 (D-020). Test values marked (test) are used only here.
"""
from __future__ import annotations

import math

from companion.appx.common import emit
from companion.ch16 import lab_d, sources as s16
from companion.ch16.examples_f import u_mcp
from plantp import yieldrisk as yr

OUT: list[str] = []


def p(pid: str, text: str) -> None:
    OUT.append(f"{pid}: {text}")


def source() -> None:
    ghi = 1920.0                                    # ch 12, long-term P50 (kWh/m2)
    u_lt, iav = 0.028, 0.027
    p("M30", f"GHI P90 one year: 1,920 x (1 - 1.2816 x {100 * math.hypot(u_lt, iav):.1f} %)"
             f" = {ghi * (1 - 1.2816 * math.hypot(u_lt, iav)):,.0f} kWh/m2")
    p("M31", f"wind long term against the mast year: 191.87 / 186.69 ="
             f" {191.87 / 186.69:.4f} ({100 * (191.87 / 186.69 - 1):+.2f} %)")
    u = u_mcp(12, 0.80)
    p("M32", f"MCP 12 months, r 0.80: speed {100 * u:.2f} %; energy x 1.82 ="
             f" {100 * 1.82 * u:.2f} %")
    p("M33", f"cross-prediction W2b 1.35 % and W1 7.64 % of speed: energy"
             f" {1.82 * 1.35:.2f} % and {1.82 * 7.64:.2f} %")
    p("M34", "Part II test against model 15.1 at MV: wind 184.58 -> 193.14 GWh"
             f" ({193.14 - 184.58:+.2f}), PV 110.23 -> 108.36 GWh ({108.36 - 110.23:+.2f})")


def losses() -> None:
    w = [218.79, 200.12, 199.56, 191.56, 196.88, 193.14]
    steps = [100 * (b / a - 1) for a, b in zip(w[:-1], w[1:])]
    p("M35", "wind steps %: " + ", ".join(f"{x:+.2f}" for x in steps)
          + f"; total {100 * (w[-1] / w[0] - 1):+.2f} %")
    pv = [129.15, 108.36]
    p("M36", f"PV from STC to MV: {100 * (pv[1] / pv[0] - 1):+.2f} %; of it availability"
             " -1.00 % and degradation -0.50 % (A-275)")
    p("M37", f"plant MV 301.49 -> POC 295.14 GWh: {100 * (295.14 / 301.49 - 1):+.2f} %"
             f" ({301.49 - 295.14:.2f} GWh)")
    p("M38", f"losses 2 % and 3 % in a row: {100 * (1 - 0.98 * 0.97):.2f} % (not 5 %)")


def uncertainty() -> None:
    parts = [3.0, 2.0, 2.5, 1.0, 1.5]                # % (test)
    u = yr.combine(parts)
    p("M39", f"RSS of 3, 2, 2.5, 1, 1.5 %: {u:.2f} %; P90 of 200 GWh:"
             f" {yr.p_value(200, u / 100):.2f} GWh")
    p("M40", f"same parts fully correlated: {sum(parts):.1f} %; P90"
             f" {yr.p_value(200, sum(parts) / 100):.2f} GWh")
    s = s16.sigmas()
    r = s["ratio"]
    b = s16.base()
    lt, iav = s["lt"] * r, s["iav"] * r
    p("M41", f"Plant P at the POC: long-term {lt:.2f}, year-to-year {iav:.2f} GWh;"
             f" P90 1y {b['net'] - 1.2816 * math.hypot(lt, iav):.1f},"
             f" P90 10y {b['net'] - 1.2816 * yr.n_year(lt, iav, 10):.1f} GWh")
    p("M42", "hybrid P90 one year at MV 281.93 GWh against wind + PV P90s"
             " 174.84 + 102.20 = 277.04 GWh")
    it = lab_d.items()
    top = sorted(it, key=lambda x: -x[2])[:3]
    tot = lab_d.total(it)
    p("M43", "largest shares: " + "; ".join(f"{n} {100 * v * v / tot ** 2:.1f} %"
                                           for n, _, v in top))


def limits() -> None:
    p("M44", "one-year P90 exceeded in 9 of 10 years; at least one year below it"
             f" in 15 years: {1 - 0.9 ** 15:.2f}")
    p("M45", "forecast RMSE 10.72 MW (31 % of mean power, hourly) against the"
             " one-year yield sigma 14.99 GWh (5.1 %)")


if __name__ == "__main__":
    source()
    losses()
    uncertainty()
    limits()
    emit("mastery_part3", OUT)
