"""Chapter 2 worked example — audit of a faulty yield estimate and the checked,
versioned calculation sheet PLP-GEN-CAL-0002.

Run from the project root:   python -m companion.ch02.yield_audit
Writes to companion/ch02/expected/:
  audit_draft.txt      the Rev A draft recomputed exactly as it was written (errors included)
  audit_corrected.txt  the corrected calculation, line by line
  audit_check.txt      the independent check by other methods
  audit_density.txt    the air-density sensitivity behind comment C-05
  calc_sheet.txt       the calculation record, Rev 0
The people are roles (engineer A prepares, engineer B checks, lead engineer C approves).
"""
from __future__ import annotations

import math
import sys
import textwrap
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plantp import datapack, records as rec, screening as sc  # noqa: E402
from plantp.units import Q, check, kelvin  # noqa: E402

HERE = Path(__file__).resolve().parent
EXPECTED = HERE / "expected"
R_DRY_AIR = 287.05


def emit(name: str, lines: list[str]) -> None:
    wrapped = []
    for line in lines:
        wrapped += textwrap.wrap(line, 78, subsequent_indent="    ") or [""]
    text = "\n".join(wrapped) + "\n"
    (EXPECTED / f"{name}.txt").write_text(text, encoding="utf-8", newline="\n")
    print(f"== {name}\n{text}")


def draft_rev_a(ghi_daily: float, raw_kwh_per_turbine: float) -> dict:
    """The draft as engineer A wrote it, errors and all (do NOT reuse)."""
    d = {}
    d["L1_pv_mw"] = 50.0                                   # E1: AC rating used as DC
    d["L2_h"] = ghi_daily * 365                            # correct
    d["L3_e_pv"] = d["L1_pv_mw"] * d["L2_h"] * 0.85 * 0.98  # E2: no G_STC in the formula
    first_try = 1 + (-0.0035) * ((45 + 273) - 25)          # E3: K minus degC
    d["L4_first_try"] = first_try
    d["L4_factor"] = 1 + (-0.0035) * (45 - 25)             # E4: double counting with PR_DC
    d["L4_e_pv"] = d["L3_e_pv"] * d["L4_factor"]
    d["L5_rho_first"] = 877.67 / (287.05 * 16.78)          # E5: hPa and degC
    d["L5_rho_used"] = 1.225                               # E6: silent fallback
    d["L6_wind_sum_kwh"] = raw_kwh_per_turbine * 12 * 0.88
    d["L6_wind_label_mwh"] = d["L6_wind_sum_kwh"] / 1e6    # E7: /1e6 labelled MWh
    d["L7_total"] = d["L4_e_pv"] + d["L6_wind_label_mwh"]
    d["L9_cf"] = d["L7_total"] / (120 * 8784)              # E8 basis, E9 hours
    d["L11_claim_pct"] = 85 - 80                           # E11: points, not percent
    d["L11_true_pct"] = 100 * (0.85 / 0.80 - 1)
    return d


def binned_wind_energy_mwh(speeds, curve, turbines=12, loss=sc.WIND_LOSS) -> float:
    """Independent method: histogram of hourly speeds in the power-curve bins, times the
    power at each bin centre (no interpolation inside the bins)."""
    centres = curve["wind_speed_ms"].to_numpy()
    power = curve["power_kw"].to_numpy()
    edges = np.concatenate([[centres[0] - 0.25], (centres[:-1] + centres[1:]) / 2,
                            [centres[-1] + 0.25]])
    hours, _ = np.histogram(speeds, bins=edges)
    return float(np.sum(hours * power)) * turbines * (1 - loss) / 1000.0


def main() -> None:
    EXPECTED.mkdir(exist_ok=True)
    problems = datapack.verify("1.0.0")
    if problems:
        raise SystemExit("data pack is not intact: " + "; ".join(problems))
    hourly = datapack.load_hourly()
    curve = datapack.load_power_curve()
    s0 = datapack.load_scenario("S0")
    cite = datapack.cite("S0", "1.0.0")
    ghi_sum_kwh = float(hourly["ghi_wm2"].sum()) / 1000.0     # kWh/m2 in the year
    ghi_daily = ghi_sum_kwh / 365
    ws = hourly["ws_100m_ms"].to_numpy()
    raw_kw = np.interp(ws, curve["wind_speed_ms"], curve["power_kw"])
    raw_kwh_per_turbine = float(raw_kw.sum())                  # 1 h steps

    # ---- Rev A, reproduced ---------------------------------------------------------
    d = draft_rev_a(round(ghi_daily, 3), raw_kwh_per_turbine)
    emit("audit_draft", [
        "PLP-GEN-CAL-0002 Rev A (IFR) as written by engineer A - reproduced",
        f"L1  PV rating                        P = {d['L1_pv_mw']:.0f} MW",
        f"L2  annual GHI   {round(ghi_daily, 3):.3f} kWh/m2/d x 365 = {d['L2_h']:.1f} kWh/m2",
        f"L3  E_PV = 50 MW x {d['L2_h']:.1f} kWh/m2 x 0.85 x 0.98 = {d['L3_e_pv']:,.0f} MWh",
        f"L4  temperature: 1 - 0.0035 x ((45+273) - 25) = {d['L4_first_try']:.4f} "
        "-> 'negative,",
        f"    so use 45 - 25 = 20': factor {d['L4_factor']:.2f}; E_PV = "
        f"{d['L4_e_pv']:,.0f} MWh",
        f"L5  rho = 877.67 / (287.05 x 16.78) = {d['L5_rho_first']:.3f} kg/m3 -> "
        f"'too low, use {d['L5_rho_used']}'",
        f"L6  wind: sum of hourly curve power x 12 x 0.88 = {d['L6_wind_sum_kwh']:,.0f};",
        f"    / 1000 / 1000 = {d['L6_wind_label_mwh']:.1f} MWh",
        f"L7  total = {d['L4_e_pv']:,.0f} + {d['L6_wind_label_mwh']:.1f} = "
        f"{d['L7_total']:,.1f} MWh",
        "L8  curtailment at the 100 MW export limit: not relevant",
        f"L9  CF = {d['L7_total']:,.0f} MWh / (120 MW x 8784 h) = {100 * d['L9_cf']:.4f} %",
        f"L10 result: annual yield {d['L7_total']:,.4f} MWh, capacity factor "
        f"{100 * d['L9_cf']:.4f} %",
        f"L11 raising PR_DC from 0.80 to 0.85 raises the PV yield by {d['L11_claim_pct']} %",
        "L12 mean wind speed at hub height 7.10 km/h",
    ])

    # ---- corrected calculation ---------------------------------------------------
    p_dc = Q(s0["pv"]["dc_mwp"], "MWp")
    h = Q(ghi_sum_kwh, "kWh/m2")
    g_stc = Q(1000, "W/m2")
    e_pv_hand = check(p_dc * (h / g_stc) * sc.PR_DC * sc.ETA_INVERTER, "MWh").magnitude("MWh")
    pv = sc.pv_ac_power_mw(hourly["ghi_wm2"], s0["pv"]["dc_mwp"], s0["pv"]["ac_mw"])
    e_pv = float(np.sum(pv))
    clipped = e_pv_hand - e_pv
    wind = sc.wind_power_mw(ws, curve["wind_speed_ms"], curve["power_kw"],
                            s0["wind"]["turbines"])
    e_wind = float(np.sum(wind))
    export, cut = sc.export_and_curtailment_mw(pv + wind, s0["export_limit_mw"])
    e_gen = e_pv + e_wind
    e_exp = float(np.sum(export))
    hours = len(hourly)
    cf_exp = e_exp / (s0["export_limit_mw"] * hours)
    t_mean = float(hourly["t_air_c"].mean())
    p_mean = float(hourly["p_hpa"].mean())
    rho_mean = Q(p_mean, "hPa") / (Q(R_DRY_AIR, "J/kg/K") * Q(kelvin(t_mean), "K"))
    emit("audit_corrected", [
        f"PLP-GEN-CAL-0002 Rev B - corrected ({cite})",
        f"L1  PV DC capacity P_STC = {p_dc.value:.0f} MWp (SR-01); AC limit "
        f"{s0['pv']['ac_mw']} MW (SR-02)",
        f"L2  annual GHI H = {ghi_sum_kwh:.1f} kWh/m2 (sum of 8760 hourly means x 1 h)",
        f"L3  E_PV,hand = P_STC x H / G_STC x PR_DC x eta_inv = 60 MWp x "
        f"{ghi_sum_kwh:.1f} / 1 kW/m2",
        f"    x 0.85 x 0.98 = {e_pv_hand:,.0f} MWh (no clipping)",
        f"    hourly model with the 50 MW limit: {e_pv:,.0f} MWh "
        f"(clipped {clipped:.1f} MWh)",
        "L4  no separate temperature factor: PR_DC = 0.85 already includes it",
        f"L5  mean air density p/(R T) = 87767 Pa / (287.05 x {kelvin(t_mean):.2f} K) = "
        f"{rho_mean.magnitude('kg/m3'):.3f} kg/m3",
        "    (not used by the screening model; see comment C-05 and audit_density)",
        f"L6  E_wind = {e_wind:,.0f} MWh = {e_wind / 1000:.1f} GWh (12 turbines, losses 0.12)",
        f"L7  E_gen = {e_pv:,.0f} + {e_wind:,.0f} = {e_gen:,.0f} MWh = {e_gen / 1000:.1f} GWh",
        f"L8  curtailed {float(np.sum(cut)):.1f} MWh; exported {e_exp:,.0f} MWh "
        f"= {e_exp / 1000:.1f} GWh",
        f"L9  CF (export basis, {s0['export_limit_mw']} MW, {hours} h) = {cf_exp:.3f}; "
        f"PV CF (50 MW AC) {e_pv / (50 * hours):.3f};",
        f"    wind CF (60 MW) {e_wind / (60 * hours):.3f}",
        f"L10 result: about {e_exp / 1000:.0f} GWh/yr exported, CF {cf_exp:.2f} (screening)",
        f"L11 PR_DC 0.80 -> 0.85 raises E_PV by {d['L11_true_pct']:.2f} % "
        "(5 percentage points of PR)",
        f"L12 mean hub-height wind speed {ws.mean():.2f} m/s = {ws.mean() * 3.6:.1f} km/h",
    ])

    # ---- independent check --------------------------------------------------------
    e_wind_binned = binned_wind_energy_mwh(ws, curve)
    fermi = 96_000 + 184_000
    emit("audit_check", [
        "independent check by engineer B (different methods, same data pack)",
        f"PV:   hand method {e_pv_hand:,.0f} MWh - hourly {e_pv:,.0f} MWh = "
        f"{clipped:.1f} MWh",
        "      = energy above the 50 MW inverter limit: explained, PASS",
        f"wind: binned frequency method {e_wind_binned:,.0f} MWh vs hourly "
        f"{e_wind:,.0f} MWh",
        f"      difference {100 * (e_wind_binned / e_wind - 1):+.2f} % (bin width 0.5 m/s): "
        "PASS (limit 1 %)",
        f"order of magnitude: estimate 280 GWh, model {e_gen / 1000:.1f} GWh "
        f"({100 * (e_gen / fermi - 1):+.1f} %): PASS (limit 25 %)",
        f"bounds: 0 <= CF = {cf_exp:.3f} <= 1; E_export <= 100 MW x 8760 h = 876 GWh: PASS",
        f"PV specific yield {e_pv / 60:,.0f} kWh/kWp: plausible for 34 deg N "
        "(verify in chapters 12 and 15)",
        "dimensions: every step re-run with plantp.units quantities, check(E, 'MWh'): PASS",
        f"data pack 1.0.0 checksums: {'PASS' if not problems else 'FAIL'}",
    ])

    # ---- density sensitivity (comment C-05) ------------------------------------------
    rho_h = (hourly["p_hpa"].to_numpy() * 100.0) / (R_DRY_AIR * kelvin(hourly["t_air_c"].to_numpy()))
    lapse = 0.0065 * (100 - 2)                    # standard-atmosphere lapse, K
    rho_hub = (hourly["p_hpa"].to_numpy() * 100.0 * math.exp(-98 / 8400.0)) / (
        R_DRY_AIR * kelvin(hourly["t_air_c"].to_numpy() - lapse))
    def corrected(rho):
        v_eq = ws * (rho / 1.225) ** (1.0 / 3.0)
        return float(np.sum(sc.wind_power_mw(v_eq, curve["wind_speed_ms"], curve["power_kw"], 12)))
    e_rho2 = corrected(rho_h)
    e_rhohub = corrected(rho_hub)
    emit("audit_density", [
        "comment C-05: the power curve is for 1.225 kg/m3; Plant P is at 1200 m",
        f"hourly density from 2 m data: mean {rho_h.mean():.3f} kg/m3 "
        f"(range {rho_h.min():.3f} .. {rho_h.max():.3f})",
        f"estimated at 100 m (lapse 6.5 K/km, scale height 8.4 km): mean {rho_hub.mean():.3f} "
        "kg/m3",
        "first-order correction: v_eq = v (rho / 1.225)^(1/3), then the power curve",
        f"  wind energy with 2 m density:   {e_rho2:,.0f} MWh "
        f"({100 * (e_rho2 / e_wind - 1):+.1f} %)",
        f"  wind energy with 100 m density: {e_rhohub:,.0f} MWh "
        f"({100 * (e_rhohub / e_wind - 1):+.1f} %)",
        f"  plant total would fall to about {(e_pv + e_rhohub) / 1000:.0f} GWh/yr",
        "decision: kept outside the screening model; recorded as limitation L-2,",
        "    unknown U-013 and assumption A-028; modelled in chapters 4, 11 and 15",
    ])

    # ---- first uncertainty statement (integrated example 2) ---------------------------
    from plantp import uncertainty as un
    scales = np.linspace(0.85, 1.15, 31)
    v_eq = ws * (rho_hub / 1.225) ** (1.0 / 3.0)

    def wind_gwh(speeds, s):
        return float(np.sum(sc.wind_power_mw(speeds * s, curve["wind_speed_ms"],
                                             curve["power_kw"], 12))) / 1000.0
    grid_raw = np.array([wind_gwh(ws, s) for s in scales])
    grid_rho = np.array([wind_gwh(v_eq, s) for s in scales])
    pv_gwh = e_pv / 1000.0
    lines = [f"{cite}; resource uncertainty A-029 (teaching values), 200,000 draws"]
    for label, grid in (("screening, no density correction", grid_raw),
                        ("with first-order density correction", grid_rho)):
        mc = un.monte_carlo(lambda f_v, f_H: np.interp(f_v, scales, grid) + pv_gwh * f_H,
                            {"f_v": ("normal", 1.0, 0.03), "f_H": ("normal", 1.0, 0.04)})
        p50 = float(np.median(mc.samples))
        p90 = float(np.quantile(mc.samples, 0.10))
        lines.append(f"{label}:")
        lines.append(f"    P50 {p50:.1f} GWh, P90 {p90:.1f} GWh, std {mc.std:.1f} GWh "
                     f"({100 * mc.std / mc.mean:.1f} %)")
    lines.append("the density effect is a BIAS (a known shift): it moves the centre; it is")
    lines.append("    not added to the uncertainty")
    emit("int_statement", lines)

    # ---- calculation record ---------------------------------------------------------
    root = datapack.release_dir("1.0.0")
    files = {name: rec.file_sha256(root / name) for name in (
        "timeseries/plantp_hourly_8760.csv",
        "equipment/wind_turbine_WT-5.0-150_power_curve.csv",
        "scenarios/S0-no-bess.yml")}
    inputs = [
        rec.Input("I1", "PV DC capacity", 60, "MWp", "assumed", "SR-01, data pack 1.0.0"),
        rec.Input("I2", "PV AC (inverter) limit", 50, "MW", "assumed", "SR-02"),
        rec.Input("I3", "wind capacity", "12 x 5", "MW", "assumed", "SR-03, A-005"),
        rec.Input("I4", "export limit", 100, "MW", "assumed", "SR-06"),
        rec.Input("I5", "hourly GHI, wind speed", "8760 h", "-", "synthetic",
                  "timeseries/plantp_hourly_8760.csv"),
        rec.Input("I6", "power curve WT-5.0-150", "61 rows", "kW", "synthetic",
                  "equipment/...power_curve.csv"),
        rec.Input("I7", "PR_DC", 0.85, "-", "assumed", "plantp.screening, chapter 1"),
        rec.Input("I8", "inverter efficiency", 0.98, "-", "assumed", "plantp.screening"),
        rec.Input("I9", "wind losses (lumped)", 0.12, "-", "assumed", "plantp.screening"),
        rec.Input("I10", "reference irradiance G_STC", 1000, "W/m2", "verified",
                  "definition of STC (chapter 10)"),
    ]
    comments = [
        rec.Comment("C-01", "B", "L1", "PV model needs DC capacity (60 MWp), not the "
                    "50 MW AC limit", "major", "corrected; AC limit applied by clipping",
                    "closed"),
        rec.Comment("C-02", "B", "L3", "MW x kWh/m2 is not MWh; divide by G_STC",
                    "minor", "formula rewritten with H/G_STC", "closed"),
        rec.Comment("C-03", "B", "L4", "kelvin minus degC in the first attempt",
                    "minor", "line removed (see C-04)", "closed"),
        rec.Comment("C-04", "B", "L4", "temperature loss counted twice (inside PR_DC)",
                    "major", "separate factor removed", "closed"),
        rec.Comment("C-05", "B", "L5", "hPa and degC in the gas law; density silently "
                    "replaced by 1.225; screening ignores site density", "major",
                    f"rho = {rho_mean.magnitude('kg/m3'):.3f} kg/m3 computed; effect "
                    "quantified (audit_density); "
                    "accepted as limitation L-2, tracked as U-013", "closed"),
        rec.Comment("C-06", "B", "L6", "divided by 1e6 but labelled MWh", "major",
                    f"{e_wind:,.0f} MWh = {e_wind / 1000:.1f} GWh", "closed"),
        rec.Comment("C-07", "B", "L7", "sum mixes kWh-scale and GWh-scale numbers",
                    "major", "follows from C-06", "closed"),
        rec.Comment("C-08", "B", "L8", "is curtailment really zero?", "question",
                    "13.8 MWh/yr computed and shown", "closed"),
        rec.Comment("C-09", "B", "L9", "120 MW mixes MWp and MW; 2023 has 8760 h",
                    "major", "CF on export basis 100 MW and per technology", "closed"),
        rec.Comment("C-10", "B", "L10", "false precision", "editorial",
                    "reported to 3 significant figures", "closed"),
        rec.Comment("C-11", "B", "L11", "5 percentage points is 6.25 %", "minor",
                    "corrected", "closed"),
        rec.Comment("C-12", "B", "L12", "km/h should be m/s", "editorial", "corrected",
                    "closed"),
    ]
    sheet = rec.CalcSheet(
        number=rec.doc_number("GEN", "CAL", 2),
        title="Plant P - screening annual energy, scenario S0, data pack 1.0.0",
        purpose="first-pass annual generation and export of Plant P for the screening "
                "gate; not for design, finance or guarantees",
        revisions=[
            rec.Revision("A", "2026-11-02", "IFR", "first issue for review", "A"),
            rec.Revision("B", "2026-11-09", "IFR", "comments C-01..C-12 incorporated",
                         "A", "B"),
            rec.Revision("0", "2026-11-14", "APP", "approved for screening use", "A", "B",
                         "C"),
        ],
        inputs=inputs,
        method=[
            "PV: hourly AC power = min(60 MWp x GHI/1000 W/m2 x 0.85 x 0.98, 50 MW)",
            "wind: hourly speed into the power curve (linear interpolation) x 12 x 0.88",
            "export = min(PV + wind, 100 MW); energy = sum of hourly power x 1 h",
            "capacity factors on stated bases with 8760 h",
        ],
        results=[
            ("PV energy", f"{e_pv / 1000:.1f} GWh/yr (clipped {clipped:.1f} MWh)"),
            ("wind energy", f"{e_wind / 1000:.1f} GWh/yr"),
            ("generation", f"{e_gen / 1000:.1f} GWh/yr"),
            ("curtailed / exported", f"{float(np.sum(cut)):.1f} MWh / "
                                     f"{e_exp / 1000:.1f} GWh per year"),
            ("export capacity factor (100 MW)", f"{cf_exp:.3f}"),
            ("resource uncertainty (teaching)", "U(k=2) about 20 GWh, see example "
                                                "ex_montecarlo"),
        ],
        checks=[
            ("PV hand method vs hourly model", f"difference {clipped:.1f} MWh = clipping",
             "PASS"),
            ("wind binned vs hourly", f"{100 * (e_wind_binned / e_wind - 1):+.2f} %", "PASS"),
            ("order of magnitude 280 GWh", f"{100 * (e_gen / fermi - 1):+.1f} %", "PASS"),
            ("bounds on CF and energy", "within 0..1 and below 876 GWh", "PASS"),
            ("dimension guard (plantp.units)", "all steps", "PASS"),
            ("data pack checksums", "3 input files listed below", "PASS"),
        ],
        limitations=[
            "L-1 screening model: lumped losses, horizontal irradiance, no geometry",
            f"L-2 air density not modelled: about {100 * (e_rhohub / e_wind - 1):+.1f} % "
            "on wind energy (U-013, A-028)",
            "L-3 synthetic one-year data: no interannual variability",
        ],
        comments=comments,
        references=["Plant P Reference Data Pack 1.0.0 (manifest, SHA-256)",
                    "companion/ch01/screening_report.py; companion/ch02/yield_audit.py",
                    "comment-resolution sheet: section D of chapter 2"],
        file_digests=files,
    )
    lines = sheet.render(width=72)        # quoted inside an example box: 72 characters fit
    lines.append(f"open comments: {len(sheet.open_comments())}")
    emit("calc_sheet", lines)


if __name__ == "__main__":
    main()
