"""Chapter 2 — numerical answers of the end-of-chapter problems.

Run from the project root:   python -m companion.ch02.solutions
Writes companion/ch02/expected/solutions.txt (each line at most 78 characters).
Problem numbers match the exercises exr-ch02-N of the chapter.
"""
from __future__ import annotations

import math
import sys
import textwrap
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plantp import datapack, records as rec, screening as sc  # noqa: E402
from plantp import uncertainty as un  # noqa: E402
from plantp.units import Q, convert, format_sig, kelvin  # noqa: E402

OUT = Path(__file__).resolve().parent / "expected" / "solutions.txt"
LINES: list[str] = []


def p(num, *items) -> None:
    text = f"P{num:02d}: " + "; ".join(items)
    LINES.extend(textwrap.wrap(text, 78, subsequent_indent="     "))


def main() -> None:
    hourly = datapack.load_hourly()
    curve = datapack.load_power_curve()
    ws = hourly["ws_100m_ms"].to_numpy()

    p(2, f"3.6 MJ = {convert(3.6, 'MJ', 'kWh'):.3f} kWh",
      f"2 GWh = {convert(2, 'GWh', 'TJ'):.1f} TJ",
      f"132 kV = {convert(132, 'kV', 'V'):,.0f} V")
    p(4, f"3 x 5 MW x 4 h = {3 * 5 * 4} MWh = {convert(60, 'MWh', 'GJ'):,.0f} GJ")

    h_day = 6.2
    p(11, f"annual {h_day * 365:.0f} kWh/m2", f"mean irradiance "
      f"{h_day * 365 / 8760 * 1000:.1f} W/m2")
    six = [12, 12, 18, 18, 15, 15]
    p(12, f"energy = {sum(six)} x (1/6) h = {sum(six) / 6:.1f} MWh")
    p(13, f"Y_sp = 41,000 MWh / 25 MWp = {41000 / 25:,.0f} kWh/kWp",
      f"CF_DC = {41000 / (25 * 8760):.3f}")
    v = np.array([4.0, 6.0, 8.0, 10.0])
    p(14, f"mean {v.mean():.1f} m/s", f"mean of cubes {np.mean(v ** 3):.0f}",
      f"cube of mean {v.mean() ** 3:.0f}", f"K_e = {np.mean(v ** 3) / v.mean() ** 3:.3f}")
    wd = 225.0
    p(17, f"u = {-12 * math.sin(math.radians(wd)):+.3f} m/s",
      f"v_N = {-12 * math.cos(math.radians(wd)):+.3f} m/s (towards north-east)")
    dirs = np.radians([340.0, 20.0, 10.0])
    vm = math.degrees(math.atan2(np.mean(np.sin(dirs)), np.mean(np.cos(dirs)))) % 360
    p(18, f"vector mean {vm:.1f} deg", f"arithmetic mean {np.degrees(dirs).mean():.1f} deg")
    lim, u = un.from_reading_spec(1091.0, pct_of_reading=0.5, counts=2, count_size=0.1)
    p(19, f"limit +-{lim:.2f} V", f"u = {u:.2f} V")
    r = [41.92, 41.97, 41.95, 41.90, 41.99, 41.93]
    ta = un.type_a(r)
    p(20, f"mean {ta.mean:.3f} V", f"s = {ta.s:.4f} V", f"u(mean) = {ta.u_mean:.4f} V",
      f"t(95 %, 5) = {un.coverage_factor(0.95, 5):.3f}",
      f"U = {un.coverage_factor(0.95, 5) * ta.u_mean:.3f} V")
    p(21, f"u(P)/P = {100 * un.relative_power_law({'V': 1, 'I': 1}, {'V': 0.003, 'I': 0.004}):.2f} %")
    p(22, f"worst case +-{un.stack_worst_case([0.5] * 4):.1f} mm",
      f"RSS +-{un.stack_rss([0.5] * 4):.1f} mm")

    e_pv = float(np.sum(sc.pv_ac_power_mw(hourly["ghi_wm2"], 60, 50)))
    e_wind = float(np.sum(sc.wind_power_mw(ws, curve["wind_speed_ms"], curve["power_kw"], 12)))
    p(23, f"PV {e_pv / 1000:.1f} GWh: Y_sp {e_pv / 60:,.0f} kWh/kWp, CF_DC {e_pv / 525600:.3f}, "
      f"CF_AC {e_pv / 438000:.3f}", f"wind CF {e_wind / 525600:.3f}")
    i60 = 60e6 / (math.sqrt(3) * 33e3 * 0.95)
    p(24, f"S = {60 / 0.95:.2f} MVA", f"I = {i60:.1f} A",
      f"at 132 kV {60e6 / (math.sqrt(3) * 132e3 * 0.95):.1f} A")
    e80 = float(np.sum(sc.wind_power_mw(hourly["ws_80m_ms"], curve["wind_speed_ms"],
                                        curve["power_kw"], 12)))
    p(25, f"80 m speeds in the hub curve: {e80 / 1000:.1f} GWh vs {e_wind / 1000:.1f} GWh "
      f"({100 * (e80 / e_wind - 1):+.1f} %)")
    rho = (Q(845, "hPa") / (Q(287.05, "J/kg/K") * Q(kelvin(12.0), "K"))).magnitude("kg/m3")
    p(26, f"rho = {rho:.4f} kg/m3 ({100 * (rho / 1.225 - 1):+.1f} % from 1.225)")
    p(27, f"u(w)/w = {100 * un.relative_power_law({'r': 1, 'v': 3}, {'r': 0.005, 'v': 0.015}):.2f} %")
    rss = math.sqrt(3 * 0.5 ** 2)
    p(28, f"RSS {rss:.2f} %", f"worst case 1.5 %", f"RSS on 289.8 GWh = {289.8 * rss / 100:.2f} GWh")
    for eta, U in ((98.65, 0.20), (98.75, 0.20), (98.25, 0.20)):
        g = un.conformity(eta, U, lower=98.5)
        s_ = un.conformity(eta, U, lower=98.5, rule="simple")
        p(29, f"eta {eta} U {U}: guarded {g.verdict}, simple {s_.verdict}")
    p(30, "hour-ending 2023-12-31 20:00 UTC = 19:00-20:00 UTC = 23:00-24:00 at +04:00",
      "label 2023-12-31T23:00:00+04:00")
    for y, U in ((1947.23, 58.4), (0.18512, 0.00734), (97304.0, 3890.0)):
        ys, Us = un.round_result(y, U)
        p(31, f"y {y}, U {U} -> {ys} +- {Us}")
    p(33, rec.doc_number("CIV", "DWG", 7), f"after Z: {rec.next_revision('Z')}",
      f"approved: {rec.next_revision('Z', approve=True)}",
      f"3rd environmental report: {rec.doc_number('ENV', 'REP', 3)}")
    u_w5 = 1.62 * 0.05 * e_wind / 1000
    u_pv = 0.04 * e_pv / 1000
    p(34, f"wind {u_w5:.1f} GWh, PV {u_pv:.1f} GWh, combined "
      f"{math.hypot(u_w5, u_pv):.1f} GWh (first order, sensitivity 1.62)")

    t_max = (68 - 12 * 1 - 5 - 10) / 13
    p(40, f"13 t + 12 x 1 + 5 <= 68 - 10 -> t <= {t_max:.2f} mm (choose +-3 mm)")

    scales = np.linspace(0.85, 1.15, 31)
    grid = np.array([float(np.sum(sc.wind_power_mw(ws * s, curve["wind_speed_ms"],
                                                   curve["power_kw"], 12))) / 1000 for s in scales])
    pv_g = e_pv / 1000
    for uv, uh in ((0.03, 0.04), (0.05, 0.05)):
        mc = un.monte_carlo(lambda f_v, f_H: np.interp(f_v, scales, grid) + pv_g * f_H,
                            {"f_v": ("normal", 1.0, uv), "f_H": ("normal", 1.0, uh)})
        p(46, f"u(f_v) {100 * uv:.0f} %, u(f_H) {100 * uh:.0f} %: P50 "
          f"{np.median(mc.samples):.1f}, P90 {np.quantile(mc.samples, 0.10):.1f}, "
          f"std {mc.std:.1f} GWh")

    kw = lambda vv: np.interp(vv, curve["wind_speed_ms"], curve["power_kw"])  # noqa: E731
    lin = un.combine(lambda v_: float(kw(v_)), {"v_": 3.5}, {"v_": 0.5})
    mc = un.monte_carlo(lambda v_: kw(v_), {"v_": ("normal", 3.5, 0.5)})
    zero = float(np.mean(mc.samples == 0.0))
    p(51, f"at 3.5 m/s: linear {lin.y:.0f} +- {lin.u_c:.0f} kW", f"MC mean {mc.mean:.0f} kW, "
      f"std {mc.std:.0f} kW, 95 % {mc.low:.0f} .. {mc.high:.0f} kW",
      f"{100 * zero:.0f} % of draws give zero power (below cut-in)")

    fcf = 12 * 5 * 8760 * 0.45 / 1000
    p(45, f"draft: 12 x 5 MW x 8760 h x 0.45 = {fcf:.1f} GWh (CF assumed, not computed)",
      f"model: {e_wind / 1000:.1f} GWh, CF {e_wind / 525600:.3f}")
    p(44, "BESS 20 MW x 40 MWh is not an energy; 40 MWh is the energy",
      f"60 MW / 8760 h = {60 / 8760:.5f} MW/h is a meaningless quantity; "
      f"60 MW x 8760 h = {60 * 8760:,} MWh",
      f"1622 kWh/kWp / 8760 h = {1622 / 8760:.3f}; with 8784 h {1622 / 8784:.3f}")

    text = "\n".join(LINES) + "\n"
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(text)


if __name__ == "__main__":
    main()
