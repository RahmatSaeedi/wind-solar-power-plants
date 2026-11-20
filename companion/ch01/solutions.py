"""Chapter 1 — numerical answers of the end-of-chapter problems.

Run from the project root:   python -m companion.ch01.solutions
Writes companion/ch01/expected/solutions.txt. Every number printed in the
chapter's answer key is taken from this output.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plantp import datapack, screening as sc  # noqa: E402

HERE = Path(__file__).resolve().parent


def main() -> None:
    s0 = datapack.load_scenario("S0")
    s1 = datapack.load_scenario("S1")
    hourly = datapack.load_hourly()
    curve = datapack.load_power_curve()
    L = []

    # L2-1  energy at an assumed capacity factor
    for name, mw, cf in (("PV (50 MW AC)", 50, 0.18), ("wind (60 MW)", 60, 0.40)):
        e = mw * 8760 * cf
        L.append(f"L2-1 {name}: {mw} MW x 8760 h x {cf} = {e:,.0f} MWh = {e / 1000:.1f} GWh")

    # L2-2  capacity factor from an energy figure
    L.append(f"L2-2 CF = 97,300 MWh / (50 MW x 8760 h) = {sc.capacity_factor(97_300, 50):.3f}")

    # L2-3  DC/AC ratio and clipping threshold
    ratio = s0["pv"]["dc_mwp"] / s0["pv"]["ac_mw"]
    g_clip = 1000 * s0["pv"]["ac_mw"] / (s0["pv"]["dc_mwp"] * sc.PR_DC * sc.ETA_INVERTER)
    L.append(f"L2-3 DC/AC = {ratio:.2f}; inverters reach 50 MW at GHI = "
             f"1000 x 50 / (60 x {sc.PR_DC} x {sc.ETA_INVERTER}) = {g_clip:.0f} W/m2")

    # L2-4  land screening
    L.append(f"L2-4 PV land 60 MWp x 1.5..2.5 ha/MWp = {sc.pv_land_area_ha(60, 1.5):.0f}..{sc.pv_land_area_ha(60, 2.5):.0f} ha; "
             f"wind envelope 12 x (7x150 m)(4x150 m) = {sc.wind_envelope_km2(12, 150):.2f} km2 = "
             f"{100 * sc.wind_envelope_km2(12, 150):.0f} ha")

    # L2-5  battery usable energy and duration
    b = s1["bess"]
    usable = b["energy_mwh_nominal_bol"] * (b["soc_window_pct"][1] - b["soc_window_pct"][0]) / 100
    L.append(f"L2-5 usable = 40 MWh x (90-10)/100 = {usable:.0f} MWh; duration = {usable} / 20 MW = "
             f"{usable / b['power_mw']:.1f} h; one-way efficiency = sqrt(0.86) = {0.86 ** 0.5:.4f}; "
             f"energy out of 32 MWh of AC input (AC in -> AC out) = 32 x 0.86 = "
             f"{32 * 0.86:.2f} MWh")

    # L2-6  development budget
    capex = 120.0          # illustrative, in 'million units' (fictional currency unit)
    for pct in (2.0, 3.0, 5.0):
        L.append(f"L2-6 development spend at {pct:.0f} % of {capex:.0f} M units = {capex * pct / 100:.1f} M units")

    # L3-2  one winter day from the data pack (hand calculation data)
    day = datapack.load_hourly("day_winter")
    pv = sc.pv_ac_power_mw(day["ghi_wm2"], s0["pv"]["dc_mwp"], s0["pv"]["ac_mw"])
    wind = sc.wind_power_mw(day["ws_100m_ms"], curve["wind_speed_ms"], curve["power_kw"],
                            s0["wind"]["turbines"])
    L.append(f"L3-2 winter day {day.index[0].date()}: PV {pv.sum():.1f} MWh, wind {wind.sum():.1f} MWh, "
             f"peak PV {pv.max():.1f} MW at {int(pv.argmax()):02d}:00, peak total {(pv + wind).max():.1f} MW")
    L.append("L3-2 hourly GHI (W/m2) and wind (m/s) of that day:")
    for ts, g, w, p, q in zip(day.index, day["ghi_wm2"], day["ws_100m_ms"], pv, wind):
        L.append(f"      {ts.hour:02d}:00  GHI {g:6.1f}  ws {w:5.2f}  -> PV {p:5.2f} MW  wind {q:5.2f} MW")

    # L3-3  what the whole year says about the export limit
    pv_y = sc.pv_ac_power_mw(hourly["ghi_wm2"], s0["pv"]["dc_mwp"], s0["pv"]["ac_mw"])
    wind_y = sc.wind_power_mw(hourly["ws_100m_ms"], curve["wind_speed_ms"], curve["power_kw"],
                              s0["wind"]["turbines"])
    export, cut = sc.export_and_curtailment_mw(pv_y + wind_y, s0["export_limit_mw"])
    for limit in (100, 90, 80):
        e, c = sc.export_and_curtailment_mw(pv_y + wind_y, limit)
        L.append(f"L3-3 export limit {limit} MW: curtailed {c.sum():8.1f} MWh/year "
                 f"({100 * c.sum() / (pv_y + wind_y).sum():.2f} %), hours {int((c > 0).sum())}")

    # ---- problems 23-38 (expanded edition) -----------------------------------------------
    from plantp import project as pj
    base = {"A": (3, ()), "B": (14, ("A",)), "C": (12, ("A",)), "D": (8, ("A",)),
            "E": (12, ("A",)), "F": (6, ("D", "E")), "G": (2, ("B",)), "H": (6, ("G", "C")),
            "I": (4, ("F", "H"))}

    def run(changes):
        net = dict(base)
        net.update(changes)
        return pj.critical_path([pj.Activity(k, d, p) for k, (d, p) in net.items()])

    r27 = run({"C": (18, ("A",))})
    L.append(f"P27 C = 18 months: duration {r27.project_duration:.0f}, critical path "
             f"{'-'.join(r27.critical_path)}; float of B {r27.total_float['B']:.0f}")
    r35 = run({"E": (12, ("D",))})
    L.append(f"P35 E after D: duration {r35.project_duration:.0f}, critical path "
             f"{'-'.join(r35.critical_path)}")
    m40 = 100 * (0.03 + 0.97 * pj.s_curve(40, 30, 26, 8))
    m50 = 100 * (0.03 + 0.97 * pj.s_curve(50, 30, 26, 8))
    L.append(f"P28 S-curve: spent by month 40 = {m40:.1f} %, by month 50 = {m50:.1f} %")
    for rid, lk, im in (("R9", 4, 4), ("R10", 1, 5), ("R11", 5, 2)):
        L.append(f"P29 {rid}: {lk} x {im} = {pj.risk_score(lk, im)} -> "
                 f"{pj.risk_band(pj.risk_score(lk, im))}")
    L.append(f"P30 flat 60 u/MWh: {export.sum() * 60 / 1e6:.2f} million u/yr")
    L.append(f"P31 hybrid export CF = {export.sum() / 1000:.1f} GWh / (100 MW x 8760 h) = "
             f"{export.sum() / (100 * 8760):.3f}")
    import numpy as _np
    tot = _np.asarray(pv_y) + _np.asarray(wind_y)
    L.append(f"P32 hours above 50 MW: wind alone {int((_np.asarray(wind_y) > 50).sum())}, "
             f"PV alone {int((_np.asarray(pv_y) > 50).sum())}, total {int((tot > 50).sum())}")

    import textwrap
    wrapped = []
    for line in L:
        wrapped += textwrap.wrap(line, 78, subsequent_indent="    ") or [""]
    text = "\n".join(wrapped) + "\n"
    (HERE / "expected").mkdir(exist_ok=True)
    (HERE / "expected" / "solutions.txt").write_text(text, encoding="utf-8", newline="\n")
    print(text)


if __name__ == "__main__":
    main()
