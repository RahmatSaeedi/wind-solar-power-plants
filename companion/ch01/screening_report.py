"""Chapter 1 — first-pass numbers for Plant P, scenarios S0 and S1.

Run from the project root:   python -m companion.ch01.screening_report
Writes companion/ch01/expected/*.txt (each line at most 78 characters, so the
book quotes them unchanged) and the plot data of the chapter's figures
(diagrams/data/ch01-*.csv).
"""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plantp import datapack, project as pj, screening as sc  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXPECTED = HERE / "expected"
DATA = ROOT / "diagrams" / "data"


def emit(name: str, lines: list[str]) -> str:
    wrapped = []
    for line in lines:
        wrapped += textwrap.wrap(line, 78, subsequent_indent="    ") or [""]
    text = "\n".join(wrapped) + "\n"
    (EXPECTED / f"{name}.txt").write_text(text, encoding="utf-8", newline="\n")
    print(f"== {name}\n{text}")
    return text


def plant_series(hourly, scenario, curve):
    pv = sc.pv_ac_power_mw(hourly["ghi_wm2"], scenario["pv"]["dc_mwp"], scenario["pv"]["ac_mw"])
    wind = sc.wind_power_mw(hourly["ws_100m_ms"], curve["wind_speed_ms"], curve["power_kw"],
                            scenario["wind"]["turbines"])
    export, cut = sc.export_and_curtailment_mw(pv + wind, scenario["export_limit_mw"])
    return np.asarray(pv), np.asarray(wind), np.asarray(export), np.asarray(cut)


def main() -> None:
    EXPECTED.mkdir(exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    problems = datapack.verify("1.0.0")
    if problems:
        raise SystemExit("data pack is not intact: " + "; ".join(problems))
    hourly = datapack.load_hourly()
    curve = datapack.load_power_curve()
    s0, s1 = datapack.load_scenario("S0"), datapack.load_scenario("S1")
    pv, wind, export, cut = plant_series(hourly, s0, curve)
    e_pv, e_wind = pv.sum(), wind.sum()

    # ---- S0 screening ---------------------------------------------------------------
    p_dc = np.asarray(sc.pv_dc_power_mw(hourly["ghi_wm2"], s0["pv"]["dc_mwp"]))
    unclipped = p_dc * sc.ETA_INVERTER
    clipped = np.maximum(unclipped - s0["pv"]["ac_mw"], 0.0)
    emit("screening_s0", [
        "Plant P - first-pass (screening) numbers",
        f"data: {datapack.cite('S0', '1.0.0')}",
        f"assumptions: PR_dc = {sc.PR_DC}, inverter efficiency = {sc.ETA_INVERTER}, "
        f"wind losses = {sc.WIND_LOSS}; horizontal irradiance used for the PV array",
        "",
        f"PV   energy  {e_pv / 1000:6.1f} GWh/yr, capacity factor (50 MW AC) "
        f"{sc.capacity_factor(e_pv, s0['pv']['ac_mw']):.3f}",
        f"wind energy  {e_wind / 1000:6.1f} GWh/yr, capacity factor (60 MW)    "
        f"{sc.capacity_factor(e_wind, s0['wind']['ac_mw']):.3f}",
        f"sum          {(e_pv + e_wind) / 1000:6.1f} GWh/yr",
        f"PV DC/AC ratio {s0['pv']['dc_mwp'] / s0['pv']['ac_mw']:.2f}: {int((clipped > 0).sum())} h at "
        f"the inverter limit, {clipped.sum():.1f} MWh clipped "
        f"({100 * clipped.sum() / unclipped.sum():.2f} % of unclipped AC)",
        f"highest hourly PV + wind {float((pv + wind).max()):.1f} MW "
        f"(export limit {s0['export_limit_mw']} MW)",
        f"hours above the export limit: {int((cut > 0).sum())}",
        f"S0 curtailed {cut.sum():.1f} MWh/yr "
        f"({100 * cut.sum() / (e_pv + e_wind):.3f} % of generation)",
        f"S0 exported {export.sum() / 1000:.1f} GWh/yr, capacity factor (100 MW) "
        f"{sc.capacity_factor(export.sum(), s0['export_limit_mw']):.3f}",
    ])

    # ---- S1 battery used only to store curtailed energy --------------------------------
    bess = s1["bess"]
    headroom = s1["export_limit_mw"] - export
    r = sc.shift_surplus_with_battery(cut, headroom, bess["power_mw"],
                                      bess["usable_energy_mwh_bol"],
                                      bess["roundtrip_efficiency_ac_pct"] / 100)
    emit("screening_s1", [
        f"data: {datapack.cite('S1', '1.0.0')}",
        "battery role in this test: store curtailed energy only, deliver it later",
        f"energy charged          {r.charged_mwh:8.1f} MWh/yr",
        f"energy delivered later  {r.delivered_mwh:8.1f} MWh/yr",
        f"full-cycle equivalents  {r.charged_mwh / bess['usable_energy_mwh_bol']:8.2f} per year",
        f"exported                {(export.sum() + r.delivered_mwh) / 1000:8.1f} GWh/yr",
        f"duration at rated power: {bess['energy_mwh_nominal_bol'] / bess['power_mw']:.1f} h "
        f"nominal, {bess['usable_energy_mwh_bol'] / bess['power_mw']:.1f} h usable",
    ])

    # ---- complementarity -----------------------------------------------------------------
    total = pv + wind
    month = hourly.index.month.to_numpy()
    hour = hourly.index.hour.to_numpy()
    corr = float(np.corrcoef(pv, wind)[0, 1])
    corr_day = float(np.corrcoef(pv[(hour >= 7) & (hour <= 17)], wind[(hour >= 7) & (hour <= 17)])[0, 1])
    lines = [f"correlation of hourly PV and wind power: {corr:+.3f} "
             f"(daylight hours 07-17 only: {corr_day:+.3f})"]
    for thr in (0.1, 10, 50, 80, 100):
        lines.append(f"hours with PV + wind above {thr:5.1f} MW: {int((total > thr).sum()):5d} "
                     f"({100 * (total > thr).mean():5.1f} %)")
    lines.append(f"hours below 10 MW: PV alone {int((pv < 10).sum())}, wind alone "
                 f"{int((wind < 10).sum())}, together {int((total < 10).sum())}")
    lines.append(f"export capacity factor: PV only {sc.capacity_factor(e_pv, 100):.3f}, "
                 f"wind only {sc.capacity_factor(e_wind, 100):.3f}, hybrid "
                 f"{sc.capacity_factor(export.sum(), 100):.3f} of the 100 MW connection")
    emit("complementarity", lines)

    # ---- revenue under two fictional tariffs ------------------------------------------------
    flat = 50.0
    peak = (hour >= 18) & (hour < 22)
    tou = np.where(peak, 90.0, 40.0)
    rev_flat = export.sum() * flat / 1e6
    rev_tou = float((export * tou).sum()) / 1e6
    pv_share = np.divide(pv, total, out=np.zeros_like(pv), where=total > 0)
    val_pv = float((export * pv_share * tou).sum() / (export * pv_share).sum())
    val_wind = float((export * (1 - pv_share) * tou).sum() / (export * (1 - pv_share)).sum())
    emit("revenue", [
        "tariffs are FICTIONAL teaching values in an imaginary currency unit (u)",
        f"flat tariff {flat:.0f} u/MWh: revenue {rev_flat:.2f} million u/yr",
        f"time-of-use: 90 u/MWh from 18:00 to 22:00, 40 u/MWh otherwise "
        f"(time-weighted mean {tou.mean():.1f} u/MWh)",
        f"revenue {rev_tou:.2f} million u/yr; average value "
        f"{rev_tou * 1e6 / export.sum():.1f} u/MWh",
        f"average value of PV energy {val_pv:.1f} u/MWh, of wind energy {val_wind:.1f} u/MWh",
        f"energy exported 18:00-22:00: {export[peak].sum() / 1000:.1f} GWh "
        f"({100 * export[peak].sum() / export.sum():.1f} % of the year's export)",
    ])

    # ---- development schedule (critical path) ------------------------------------------------
    dev = [
        pj.Activity("A", 3), pj.Activity("B", 14, ("A",)), pj.Activity("C", 12, ("A",)),
        pj.Activity("D", 8, ("A",)), pj.Activity("E", 12, ("A",)), pj.Activity("F", 6, ("D", "E")),
        pj.Activity("G", 2, ("B",)), pj.Activity("H", 6, ("G", "C")), pj.Activity("I", 4, ("F", "H")),
    ]
    res = pj.critical_path(dev)
    lines = ["act  dur   ES   EF   LS   LF  float"]
    for a in dev:
        n = a.name
        lines.append(f"  {n}  {a.duration:3.0f}  {res.early_start[n]:3.0f}  {res.early_finish[n]:3.0f}  "
                     f"{res.late_start[n]:3.0f}  {res.late_finish[n]:3.0f}  {res.total_float[n]:4.0f}")
    lines.append(f"project duration {res.project_duration:.0f} months; critical path "
                 f"{' - '.join(res.critical_path)}")
    emit("schedule", lines)
    with open(DATA / "ch01-gantt.csv", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("row,name,es,ef,float\n")
        for k, a in enumerate(dev):
            fh.write(f"{k},{a.name},{res.early_start[a.name]:.0f},{res.early_finish[a.name]:.0f},"
                     f"{res.total_float[a.name]:.0f}\n")

    # ---- lifecycle spending S-curve (fictional shares) -----------------------------------------
    with open(DATA / "ch01-scurve.csv", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("month,cumulative_pct\n")
        for mth in range(0, 61):
            dev_share = 0.03 * pj.s_curve(mth, 0, 30, 6)
            build_share = 0.97 * pj.s_curve(mth, 30, 26, 8)
            fh.write(f"{mth},{100 * (dev_share + build_share):.2f}\n")
    emit("scurve", [
        "fictional spend profile: 3 % of capital over months 0-30 (development),",
        "97 % over months 30-56 (procurement and construction)",
        f"spent by month 24: {100 * 0.03 * pj.s_curve(24, 0, 30, 6):.1f} %; by month 30: "
        f"{100 * 0.03:.1f} %; by month 43: "
        f"{100 * (0.03 + 0.97 * pj.s_curve(43, 30, 26, 8)):.1f} %",
    ])

    # ---- risk register (first look) -------------------------------------------------------------
    risks = [("R1", 3, 5), ("R2", 3, 4), ("R3", 4, 3), ("R4", 2, 4),
             ("R5", 3, 3), ("R6", 2, 3), ("R7", 3, 4), ("R8", 2, 5)]
    with open(DATA / "ch01-risks.csv", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("id,likelihood,impact,score\n")
        for rid, lk, im in risks:
            fh.write(f"{rid},{lk},{im},{pj.risk_score(lk, im)}\n")
    emit("risks", [f"{rid}: L{lk} x I{im} = {pj.risk_score(lk, im):2d} "
                   f"({pj.risk_band(pj.risk_score(lk, im))})" for rid, lk, im in risks])

    # ---- plot data ----------------------------------------------------------------------------
    day = datapack.load_hourly("day_summer")
    d_pv, d_wind, _, _ = plant_series(day, s0, curve)
    with open(DATA / "ch01-summer-day.csv", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("hour,pv_mw,wind_mw,total_mw\n")
        for h, a, b in zip(day.index.hour, d_pv, d_wind):
            fh.write(f"{h + 0.5:.1f},{a:.2f},{b:.2f},{a + b:.2f}\n")
    with open(DATA / "ch01-monthly.csv", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("month,pv_gwh,wind_gwh\n")
        for m in range(1, 13):
            fh.write(f"{m},{pv[month == m].sum() / 1000:.2f},{wind[month == m].sum() / 1000:.2f}\n")
    with open(DATA / "ch01-hour-of-day.csv", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("hour,pv_mw,wind_mw\n")
        for h in range(24):
            fh.write(f"{h + 0.5:.1f},{pv[hour == h].mean():.2f},{wind[hour == h].mean():.2f}\n")
    week = datapack.load_hourly("week_spring")
    w_pv, w_wind, _, _ = plant_series(week, s0, curve)
    with open(DATA / "ch01-week.csv", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("h,pv_mw,wind_mw,total_mw\n")
        for k, (a, b) in enumerate(zip(w_pv, w_wind)):
            fh.write(f"{k + 0.5:.1f},{a:.2f},{b:.2f},{a + b:.2f}\n")
    with open(DATA / "ch01-duration.csv", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("hours,pv_mw,wind_mw,total_mw\n")
        sp, sw, st = np.sort(pv)[::-1], np.sort(wind)[::-1], np.sort(total)[::-1]
        for k in range(0, 8760, 20):
            fh.write(f"{k},{sp[k]:.2f},{sw[k]:.2f},{st[k]:.2f}\n")
        fh.write(f"8759,{sp[-1]:.2f},{sw[-1]:.2f},{st[-1]:.2f}\n")


if __name__ == "__main__":
    main()
