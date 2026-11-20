"""Chapter 5, section D - applied computing laboratories on Plant P.

    D1 validate the raw sample data against its defect key
    D2 PV temperature/irradiance model, hand check, comparison with SCADA
    D3 wind power-curve integration: time series, Weibull, air density
    D4 battery state of charge and a rule-based dispatch (S1)
    D5 collector-cable and export-transformer losses
    D6 auditable cash flow, DSCR, NPV, IRR and sensitivity
Run from the project root:   python -m companion.ch05.lab_d
Data pack 1.1.0 (synthetic); money in fictional units u; assumptions A-089..A-097.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch05 import step2_reader, step3_model as m
from companion.ch05.common import csv, emit
from companion.ch05.resource_tool import rawdata
from plantp import datapack, dispatch, losses, money, screening as sc, stats

CURVE = datapack.load_power_curve()
VS, PK = CURVE["wind_speed_ms"].to_numpy(), CURVE["power_kw"].to_numpy()


def hourly_s0():
    h = datapack.load_hourly()
    pv = m.pv_ac_mw(h["ghi_wm2"], h["t_air_c"])
    rho = m.air_density(h["p_hpa"], h["t_air_c"])
    wind = m.wind_farm_mw(h["ws_100m_ms"], rho, VS, PK)
    return h, np.asarray(pv), np.asarray(wind), np.asarray(rho)


def d1_validate() -> None:
    import csv as c
    key = list(c.DictReader(datapack.raw_path("met_mast_defects_key.csv")
                            .read_text(encoding="utf-8").splitlines()))
    _, s = rawdata.validate(datapack.raw_path("met_mast_10min_raw.csv"))
    f = s["flags"]
    found = {"D1": s["duplicates"] == 1, "D2": bool(s["gaps"]),
             "D3": "ws60_avg: out of range" in f, "D4": "ws80_avg: stuck" in f,
             "D5": "t_air: sentinel" in f, "D6": "p_air: kPa -> hPa" in f,
             "D7": s["out_of_order"] == 1, "D8": "ghi: night offset -> 0" in f,
             "D9": "wd100_avg: out of range" in f}
    lines = ["defect key of the data pack versus what the validator reported:"]
    for k in key:
        lines.append(f"  {k['id']} {k['defect']:32s} {'found' if found[k['id']] else 'MISSED'}")
    planted = {"ws60_avg: out of range": 1, "ws80_avg: stuck": 12, "t_air: sentinel": 1,
               "p_air: kPa -> hPa": 6, "ghi: night offset -> 0": 6,
               "wd100_avg: out of range": 1}
    extra = {k: n for k, n in f.items() if n != planted.get(k)}
    lines.append(f"detected {sum(found.values())} of {len(key)}; flagged values "
                 f"{sum(f.values())}, planted {sum(planted.values())}; "
                 f"false alarms: {extra or 'none'}")
    emit("d_validate", lines)


def d2_pv() -> None:
    h, pv, _, _ = hourly_s0()
    noon = h.loc["2023-06-23 12:00"]
    g, ta = float(noon["ghi_wm2"]), float(noon["t_air_c"])
    tc = ta + 25 / 800 * g
    p_hand = min(60 * g / 1000 * (1 - 0.0035 * (tc - 25)) * 0.90 * 0.98, 50)
    p_code = float(m.pv_ac_mw(g, ta))
    pv_ch1 = np.asarray(sc.pv_ac_power_mw(h["ghi_wm2"], 60, 50))
    tcell = np.asarray(m.cell_temperature(h["ghi_wm2"], h["t_air_c"]))
    day = h["ghi_wm2"].to_numpy() > 0
    w = h["ghi_wm2"].to_numpy()[day]
    t_weighted = float(np.sum(tcell[day] * w) / np.sum(w))
    emit("d_pv", [
        "hand check, 23 June 12:00 (data pack 1.1.0, S0):",
        f"  G = {g} W/m2, T_air = {ta} C -> T_cell = {ta} + 25/800 x {g} = {tc:.2f} C",
        f"  P = 60 x {g / 1000:.4f} x (1 - 0.0035 x {tc - 25:.2f}) x 0.90 x 0.98 = "
        f"{p_hand:.3f} MW; code {p_code:.3f} MW",
        f"annual PV with the temperature model {pv.sum() / 1000:.2f} GWh; chapter 1 lumped "
        f"model {pv_ch1.sum() / 1000:.2f} GWh",
        f"irradiance-weighted cell temperature {t_weighted:.1f} C -> mean temperature factor "
        f"{1 - 0.0035 * (t_weighted - 25):.3f}",
        f"hottest cell {tcell.max():.1f} C; coldest daylight cell {tcell[day].min():.1f} C",
    ])
    rows, _ = step2_reader.read_scada(datapack.raw_path("pv_scada_export.csv"))
    import pandas as pd
    idx = [pd.Timestamp(r["start"]).tz_convert("+04:00") for r in rows]
    scada = np.array([r["energy_mwh"] for r in rows])
    model = np.asarray(m.pv_ac_mw(h.loc[idx, "ghi_wm2"], h.loc[idx, "t_air_c"]))
    bias = 100 * (model.sum() - scada.sum()) / scada.sum()
    emit("d_pv_scada", [
        f"71 SCADA hours (3-5 April, one hour missing) vs the chapter 5 model:",
        f"  SCADA {scada.sum():.1f} MWh, model {model.sum():.1f} MWh, difference {bias:+.1f} %",
        f"  hourly RMS difference {math.sqrt(np.mean((model - scada) ** 2)):.2f} MW",
        "  the synthetic 'SCADA' was made with the chapter 1 model: on cool April days",
        "  the explicit temperature factor exceeds the lumped one; a real comparison",
        "  would also separate availability, soiling and meter error (chapters 15, 37)",
    ])
    sub = h.loc["2023-06-23"]
    p5 = np.asarray(m.pv_ac_mw(sub["ghi_wm2"], sub["t_air_c"]))
    p1 = np.asarray(sc.pv_ac_power_mw(sub["ghi_wm2"], 60, 50))
    tc = np.asarray(m.cell_temperature(sub["ghi_wm2"], sub["t_air_c"]))
    csv("ch05-pvday.csv", "hour,p5,p1,tcell",
        [(k + 0.5, f"{p5[k]:.3f}", f"{p1[k]:.3f}", f"{tc[k]:.2f}") for k in range(24)])


def d3_wind() -> None:
    h, _, wind, rho = hourly_s0()
    v = h["ws_100m_ms"].to_numpy()
    e_ts = wind.sum() / 1000
    e_ref = float(np.sum(np.interp(v, VS, PK)) * 12 / 1000 * 0.88) / 1000
    k, c = 2.11, 8.02
    grid = np.linspace(0, 30, 3001)
    f = stats.weibull_pdf(grid, k, c)
    p_mean = float(np.trapezoid(np.interp(grid, VS, PK) * f, grid))
    e_wb = p_mean * 8760 * 12 * 0.88 / 1e6
    rho_m = float(rho.mean())
    v_eq8 = 8 * (rho_m / 1.225) ** (1 / 3)
    emit("d_wind", [
        f"time series, power curve at 1.225 kg/m3:   {e_ref:7.2f} GWh",
        f"time series, hourly site density (D-008):  {e_ts:7.2f} GWh "
        f"({100 * (e_ts - e_ref) / e_ref:+.1f} %)",
        f"Weibull k {k}, c {c} m/s at 1.225 kg/m3:   {e_wb:7.2f} GWh "
        f"(mean power {p_mean:,.0f} kW per turbine)",
        f"hand check: mean density {rho_m:.4f} kg/m3; at 8 m/s v_eq = 8 x ({rho_m:.4f}/1.225)^(1/3)"
        f" = {v_eq8:.3f} m/s",
        f"  P(8.000) = {np.interp(8, VS, PK):.0f} kW, P({v_eq8:.3f}) = {np.interp(v_eq8, VS, PK):.0f}"
        f" kW ({100 * (np.interp(v_eq8, VS, PK) / np.interp(8, VS, PK) - 1):+.1f} %)",
        "Weibull and series differ because the fit smooths the real distribution;",
        "  the series keeps the joint timing with PV that export limits depend on",
    ])
    csv("ch05-weibull.csv", "v,pdf,p,density",
        [(f"{x:.1f}", f"{stats.weibull_pdf(x, k, c):.5f}", f"{np.interp(x, VS, PK) / 1000:.3f}",
          f"{np.interp(x, VS, PK) * stats.weibull_pdf(x, k, c):.2f}") for x in np.arange(0, 26.01, 0.5)])


def d4_battery() -> None:
    h, pv, wind, _ = hourly_s0()
    gen = pv + wind
    hour = h.index.hour.to_numpy()
    price = np.where((hour >= 18) & (hour < 22), 90.0, 40.0)       # chapter 1 fictional
    s0 = np.minimum(gen, 100.0)
    r = dispatch.rule_based_shift(gen, range(9, 15), range(18, 22), 20.0, 32.0, 0.86, 100.0)
    rev0, rev1 = float(np.sum(s0 * price)), float(np.sum(r.export_mw * price))
    ch, dis = r.charge_mw.sum(), r.discharge_mw.sum()
    eta = math.sqrt(0.86)
    lines = ["S1 rule: charge from on-site generation 09-15 h, discharge 18-22 h;",
             "  20 MW, 32 MWh usable, round trip 86 %, no grid charging (A-009..A-012)",
             f"energy charged {ch / 1000:.2f} GWh, delivered {dis / 1000:.2f} GWh, lost "
             f"{(ch - dis) / 1000:.2f} GWh ({100 * (1 - dis / ch):.1f} %)",
             f"equivalent full cycles {dis / (32 * eta):.0f} per year (energy leaving the cells,"
             f" {dis / eta / 1000:.2f} GWh, / 32 MWh usable)",
             f"export S0 {s0.sum() / 1000:.2f} GWh, S1 {r.export_mw.sum() / 1000:.2f} GWh",
             f"revenue at the fictional tariff: S0 {rev0 / 1e6:.3f}, S1 {rev1 / 1e6:.3f} million u "
             f"({100 * (rev1 - rev0) / rev0:+.2f} %)",
             f"gain per MWh delivered {(rev1 - rev0) / dis:.1f} u = 90 - 40 / 0.86 "
             f"({90 - 40 / 0.86:.1f}): the spread less the round-trip loss"]
    checks = [("SOC within 0..32 MWh", bool((r.soc_mwh >= -1e-9).all() and (r.soc_mwh <= 32 + 1e-9).all())),
              ("never charges more than generation", bool((r.charge_mw <= gen + 1e-9).all())),
              ("export never above 100 MW", bool((r.export_mw <= 100 + 1e-9).all())),
              ("energy balance closes", abs(ch * eta - dis / eta - r.soc_mwh[-1]) < 1e-6)]
    lines += ["invariant checks: " + "; ".join(f"{t} {'PASS' if ok else 'FAIL'}" for t, ok in checks)]
    lines += ["capacity fade 2 %/yr (A-011) is not modelled in this one-year run"]
    emit("d_battery", lines)
    week = slice(92 * 24, 99 * 24)
    csv("ch05-soc.csv", "k,soc,gen,exp",
        [(k, f"{r.soc_mwh[week][k]:.2f}", f"{gen[week][k]:.2f}", f"{r.export_mw[week][k]:.2f}")
         for k in range(168)])


def d5_losses() -> None:
    h, pv, wind, _ = hourly_s0()
    gen = pv + wind
    per_feeder = gen / 4
    cable = 4 * losses.cable_loss_mw(per_feeder, 33.0, 0.95, 0.10, 6.0, 0.00403, 70.0)
    trafo = losses.transformer_loss_mw(np.minimum(gen, 120), 0.95, 120.0, 0.060, 0.400)
    s = losses.annual_losses(gen, cable, trafo)
    i = float(losses.current_a(25.0, 33.0, 0.95))
    r70 = 0.10 * 6.0 * (1 + 0.00403 * 50)
    emit("d_losses", [
        "hand check at 100 MW: 25 MW per feeder, I = 25e6 / (sqrt3 x 33e3 x 0.95) = "
        f"{i:.1f} A",
        f"  R(70 C) = 0.10 x 6 x (1 + 0.00403 x 50) = {r70:.4f} ohm; loss 3 I^2 R = "
        f"{3 * i ** 2 * r70 / 1e3:.1f} kW per feeder, {4 * 3 * i ** 2 * r70 / 1e6:.3f} MW in all",
        f"  transformer: 60 kW + 400 kW x ({100 / 0.95:.1f} / 120)^2 = "
        f"{float(losses.transformer_loss_mw(100, 0.95, 120, 0.060, 0.400)) * 1e3:.0f} kW",
        f"annual (S0, data pack 1.1.0): energy {s['energy_mwh'] / 1000:.2f} GWh;",
        f"  cables {s['cable_mwh']:,.0f} MWh ({s['cable_pct']:.2f} %), transformer "
        f"{s['trafo_mwh']:,.0f} MWh ({s['trafo_pct']:.2f} %)",
        f"  of which no-load loss {0.060 * 8760:,.0f} MWh: it runs every hour, even at night",
        "teaching model (A-091, A-092): constant 70 C conductor, equal feeders, no",
        "  reactive power flow or harmonics; chapters 24 and 25 replace it",
    ])


def d6_finance() -> None:
    e1, price, capex, opex = 273_520.0, 50.0, 100e6, 2.75e6        # A-093, A-037
    cf = money.project_cash_flow(e1, price, capex, opex, 25, 0.005, 0.70, 0.06, 15)
    dscr = [x for x in cf["dscr"][1:] if not math.isnan(x)]
    project = [-capex] + cf["cfads"][1:]
    npv_p, irr_p = money.npv(0.07, project), money.irr(project)
    npv_e, irr_e = money.npv(0.10, cf["equity_cash"]), money.irr(cf["equity_cash"])
    lines = ["year  revenue    opex   CFADS  debt serv.  DSCR  equity cash  (million u)"]
    for y in (0, 1, 2, 15, 16, 25):
        d = cf["dscr"][y]
        lines.append(f"{y:4d} {cf['revenue'][y] / 1e6:8.3f} {cf['opex'][y] / 1e6:7.3f} "
                     f"{cf['cfads'][y] / 1e6:7.3f} {cf['debt_service'][y] / 1e6:10.3f} "
                     f"{'   -' if math.isnan(d) else f'{d:5.2f}'} {cf['equity_cash'][y] / 1e6:11.3f}")
    lines += [f"DSCR minimum {min(dscr):.2f} (year {cf['dscr'].index(min(dscr))}), average "
              f"{sum(dscr) / len(dscr):.2f}",
              f"project: NPV at 7 % {npv_p / 1e6:+.2f} million u, IRR {100 * irr_p:.2f} %",
              f"equity:  NPV at 10 % {npv_e / 1e6:+.2f} million u, IRR {100 * irr_e:.2f} %",
              "audit: every year uses the same formulas; totals: revenue "
              f"{sum(cf['revenue']) / 1e6:.1f}, debt service {sum(cf['debt_service']) / 1e6:.2f} "
              f"= {0.70 * capex / 1e6:.0f} principal + interest"]
    emit("d_finance", lines)
    base = npv_p

    def npv_with(**kw):
        p = dict(e1=e1, price=price, capex=capex, opex=opex, rate=0.07)
        p.update(kw)
        c = money.project_cash_flow(p["e1"], p["price"], p["capex"], p["opex"], 25, 0.005,
                                    0.70, 0.06, 15)
        return money.npv(p["rate"], [-p["capex"]] + c["cfads"][1:])
    cases = [("energy -/+10 %", npv_with(e1=e1 * 0.9), npv_with(e1=e1 * 1.1)),
             ("price -/+10 %", npv_with(price=price * 0.9), npv_with(price=price * 1.1)),
             ("capex +/-10 %", npv_with(capex=capex * 1.1), npv_with(capex=capex * 0.9)),
             ("opex +/-20 %", npv_with(opex=opex * 1.2), npv_with(opex=opex * 0.8)),
             ("discount rate +/-1 pt", npv_with(rate=0.08), npv_with(rate=0.06))]
    cases.sort(key=lambda c: -(c[2] - c[1]))
    lines = [f"project NPV {base / 1e6:+.2f} million u; one input changed at a time:"]
    for name, lo, hi in cases:
        lines.append(f"  {name:22s} {lo / 1e6:+7.2f} .. {hi / 1e6:+7.2f}  (swing {(hi - lo) / 1e6:5.2f})")
    be = money_break_even(npv_with, price)
    lines.append(f"break-even price (NPV = 0): {be:.2f} u/MWh")
    emit("d_sensitivity", lines)
    csv("ch05-tornado.csv", "k,lo,hi,name",
        [(k, f"{(lo - base) / 1e6:.3f}", f"{(hi - base) / 1e6:.3f}", name.split()[0])
         for k, (name, lo, hi) in enumerate(reversed(cases))])
    csv("ch05-dscr.csv", "year,dscr", [(y, f"{cf['dscr'][y]:.4f}") for y in range(1, 16)])


def money_break_even(npv_with, price) -> float:
    lo, hi = 0.0, price * 2
    for _ in range(80):
        mid = (lo + hi) / 2
        if npv_with(price=mid) > 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


if __name__ == "__main__":
    d1_validate()
    d2_pv()
    d3_wind()
    d4_battery()
    d5_losses()
    d6_finance()
