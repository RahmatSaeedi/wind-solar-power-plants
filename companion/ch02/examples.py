"""Chapter 2 — numbers for the worked examples of sections A, B and C.

Run from the project root:   python -m companion.ch02.examples
Writes one text file per example group to companion/ch02/expected/ (each line at
most 78 characters, so the book can quote it unchanged) and the plot data of the
chapter's figures to diagrams/data/ch02-*.csv.

Values marked "assumed" or "synthetic" are teaching values stated in the chapter.
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
from plantp.units import Q, DimensionError, check, convert, format_sig, kelvin  # noqa: E402

HERE = Path(__file__).resolve().parent
EXPECTED = HERE / "expected"
DATA = HERE.parents[1] / "diagrams" / "data"
R_DRY_AIR = 287.05          # J/(kg K), specific gas constant of dry air (textbook value)


def emit(name: str, lines: list[str]) -> None:
    wrapped = []
    for line in lines:
        wrapped += textwrap.wrap(line, 78, subsequent_indent="    ") or [""]
    text = "\n".join(wrapped) + "\n"
    (EXPECTED / f"{name}.txt").write_text(text, encoding="utf-8", newline="\n")
    print(f"== {name}\n{text}")


def csv(name: str, header: str, rows) -> None:
    with open(DATA / name, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(header + "\n")
        for row in rows:
            fh.write(",".join(str(x) for x in row) + "\n")


def wind_energy_gwh(hourly, curve, scale: float = 1.0) -> float:
    p = sc.wind_power_mw(hourly["ws_100m_ms"].to_numpy() * scale, curve["wind_speed_ms"],
                         curve["power_kw"], 12)
    return float(p.sum()) / 1000.0


def main() -> None:
    EXPECTED.mkdir(exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    if datapack.verify("1.0.0"):
        raise SystemExit("data pack is not intact")
    hourly = datapack.load_hourly()
    curve = datapack.load_power_curve()
    s0 = datapack.load_scenario("S0")
    cite = datapack.cite("S0", "1.0.0")

    # ================================================================ A. units ======
    v = Q(hourly["ws_100m_ms"].mean(), "m/s")
    h_year = Q(hourly["ghi_wm2"].sum(), "W h/m2")
    p_air = Q(hourly["p_hpa"].mean(), "hPa")
    emit("ex_conversions", [
        f"data: {cite}",
        f"mean wind speed at 100 m: {v.value:.3f} m/s = {v.magnitude('km/h'):.2f} km/h "
        f"= {v.magnitude('kn'):.2f} kn = {v.magnitude('mph'):.2f} mph",
        f"annual GHI: {h_year.magnitude('kWh/m2'):.1f} kWh/m2 = "
        f"{h_year.magnitude('MJ/m2'):.0f} MJ/m2",
        f"  as a mean irradiance over 8760 h: "
        f"{(h_year / Q(8760, 'h')).magnitude('W/m2'):.1f} W/m2",
        f"  as a daily mean: {h_year.magnitude('kWh/m2') / 365:.3f} kWh/m2 per day",
        f"mean station pressure: {p_air.value:.2f} hPa = {p_air.magnitude('kPa'):.3f} kPa "
        f"= {p_air.magnitude('Pa'):.0f} Pa = {p_air.magnitude('bar'):.4f} bar "
        f"= {p_air.magnitude('psi'):.2f} psi",
    ])

    e_total = Q(289.8, "GWh")
    emit("ex_energy_units", [
        f"289.8 GWh = {e_total.magnitude('MWh'):,.0f} MWh = {e_total.magnitude('TWh'):.4f} TWh",
        f"          = {e_total.magnitude('TJ'):,.0f} TJ = {e_total.magnitude('PJ'):.3f} PJ",
        f"          = {e_total.magnitude('toe'):,.0f} toe (1 toe = 41.868 GJ)",
        f"one module, 550 W for 1 h = {Q(550, 'W h').magnitude('kJ'):,.0f} kJ "
        f"= {Q(550, 'W h').magnitude('kWh'):.2f} kWh",
    ])

    p_rated = Q(5, "MW")
    n_rpm = 10.0                                     # assumed rotor speed
    omega = Q(n_rpm * 2 * math.pi / 60, "rad/s")
    torque = p_rated / omega
    emit("ex_torque", [
        "WT-5.0-150 at rated power 5 MW (synthetic) and 10 rpm (assumed rotor speed)",
        f"omega = 10 x 2 pi / 60 = {omega.value:.4f} rad/s",
        f"torque = P / omega = {torque.magnitude('MN m'):.2f} MN m "
        f"= {torque.magnitude('kN m'):,.0f} kN m",
        f"check: {check(torque * omega, 'W').magnitude('MW'):.3f} MW",
    ])

    # energy versus power on the summer day of the data pack
    day = datapack.load_hourly("day_summer")
    pv_day = sc.pv_ac_power_mw(day["ghi_wm2"], 60, 50)
    wind_day = sc.wind_power_mw(day["ws_100m_ms"], curve["wind_speed_ms"], curve["power_kw"], 12)
    tot_day = pv_day + wind_day
    rows = [(i, f"{a:.3f}", f"{b:.3f}", f"{a + b:.3f}") for i, (a, b) in
            enumerate(zip(pv_day, wind_day))]
    rows.append((24,) + rows[-1][1:])        # end point so the last hour is drawn as a step
    csv("ch02-day-power.csv", "hour,pv,wind,total", rows)
    e_pv_day, e_wind_day = float(np.sum(pv_day)), float(np.sum(wind_day))
    emit("ex_day_energy", [
        f"day {day.index[0].date()} (data pack 1.0.0, summer subset), hourly means",
        f"PV:   peak {np.max(pv_day):5.1f} MW, energy {e_pv_day:6.1f} MWh, "
        f"mean power {e_pv_day / 24:5.1f} MW",
        f"wind: peak {np.max(wind_day):5.1f} MW, energy {e_wind_day:6.1f} MWh, "
        f"mean power {e_wind_day / 24:5.1f} MW",
        f"sum:  peak {np.max(tot_day):5.1f} MW, energy {e_pv_day + e_wind_day:6.1f} MWh",
        f"full-load hours of the day: PV {e_pv_day / 50:.2f} h (on 50 MW AC), "
        f"wind {e_wind_day / 60:.2f} h (on 60 MW)",
    ])

    pv_year = sc.pv_ac_power_mw(hourly["ghi_wm2"], 60, 50)
    wind_year = sc.wind_power_mw(hourly["ws_100m_ms"], curve["wind_speed_ms"],
                                 curve["power_kw"], 12)
    e_pv = float(np.sum(pv_year))
    e_wind = float(np.sum(wind_year))
    emit("ex_bases", [
        f"PV energy {e_pv / 1000:.1f} GWh/yr ({cite})",
        f"specific yield = {e_pv:,.0f} MWh / 60 MWp = {e_pv / 60:,.0f} kWh/kWp",
        f"full-load hours on AC = {e_pv:,.0f} MWh / 50 MW = {e_pv / 50:,.0f} h",
        f"capacity factor on DC basis = {e_pv / (60 * 8760):.3f}; "
        f"on AC basis = {e_pv / (50 * 8760):.3f}",
        f"wind: {e_wind / 1000:.1f} GWh/yr, {e_wind / 60:,.0f} full-load hours, "
        f"CF {e_wind / (60 * 8760):.3f}",
        "BESS (S1): 40 MWh / 20 MW = 2.0 h duration; 20 MW / 40 MWh = 0.5 C;",
        "    usable 10-90 % window: 0.8 x 40 MWh = 32 MWh",
    ])

    p15 = [80.0, 84.0, 90.0, 86.0]
    emit("ex_intervals", [
        "four 15-minute mean powers: " + ", ".join(f"{p:.0f} MW" for p in p15),
        f"energy = sum(P x 0.25 h) = {sum(p * 0.25 for p in p15):.0f} MWh",
        f"wrong: sum(P) = {sum(p15):.0f} 'MWh' (four times too much)",
        f"mean power of the hour = {np.mean(p15):.0f} MW -> energy of the hour "
        f"{np.mean(p15):.0f} MWh",
        "ten-minute data: E = sum(P) x (1/6) h; hourly data: E = sum(P) x 1 h",
    ])

    v_ll = Q(33, "kV")
    v_ph = v_ll / math.sqrt(3)
    p_ac, pf = 50e6, 0.95
    i_line = p_ac / (math.sqrt(3) * 33e3 * pf)
    s_va = p_ac / pf
    q_var = math.sqrt(s_va ** 2 - p_ac ** 2)
    emit("ex_ac_quantities", [
        f"230 V rms -> peak {230 * math.sqrt(2):.0f} V; 33 kV line-to-line -> "
        f"{v_ph.magnitude('kV'):.2f} kV line-to-neutral",
        f"50 MW at power factor 0.95: S = {s_va / 1e6:.2f} MVA, Q = {q_var / 1e6:.2f} Mvar",
        f"line current at 33 kV: I = P / (sqrt(3) V_LL pf) = {i_line:.1f} A",
        f"same power at 132 kV: {p_ac / (math.sqrt(3) * 132e3 * pf):.1f} A",
    ])

    ws = hourly["ws_100m_ms"].to_numpy()
    mean_v = float(ws.mean())
    mean_v3 = float(np.mean(ws ** 3))
    epf = mean_v3 / mean_v ** 3
    rho0 = 1.225
    area = math.pi * 75 ** 2
    pd_wrong = 0.5 * rho0 * mean_v ** 3
    pd_right = 0.5 * rho0 * mean_v3
    p_at_mean = float(np.interp(mean_v, curve["wind_speed_ms"], curve["power_kw"]))
    e_curve_mean = p_at_mean * 12 * 8760 * (1 - sc.WIND_LOSS) / 1e6
    e_curve_hourly = e_wind / 1000
    csv("ch02-cube-trap.csv", "case,label,value",
        [(1, "mean speed in the power curve", f"{e_curve_mean:.1f}"),
         (2, "hourly speeds in the power curve", f"{e_curve_hourly:.1f}")])
    w60 = sc.wind_power_mw(hourly["ws_60m_ms"], curve["wind_speed_ms"], curve["power_kw"], 12)
    e60 = float(np.sum(w60)) / 1000
    pv_series = np.asarray(pv_year)
    shifted = np.roll(pv_series, 1)                 # hour-ending data read as hour-beginning
    mad = float(np.mean(np.abs(shifted - pv_series)[pv_series > 0]))
    corr = float(np.corrcoef(pv_series[1:], shifted[1:])[0, 1])
    emit("ex_height_time", [
        f"mean speed: 60 m {hourly['ws_60m_ms'].mean():.3f} m/s, 100 m {mean_v:.3f} m/s "
        f"(ratio {mean_v / hourly['ws_60m_ms'].mean():.3f})",
        f"farm energy with 60 m speeds in the hub-height curve: {e60:.1f} GWh vs "
        f"{e_wind / 1000:.1f} GWh ({100 * (e60 / (e_wind / 1000) - 1):+.0f} %)",
        f"PV hourly series shifted by one hour: correlation {corr:.3f}; mean absolute "
        f"difference {mad:.1f} MW in daylight hours (annual energy unchanged)",
        "8760 h in 2023; 8784 h in a leap year (2024): CF with the wrong hours is "
        f"{100 * (8760 / 8784 - 1):+.2f} % off",
    ])

    emit("ex_cube_trap", [
        f"hub-height speeds of {cite}",
        f"mean speed {mean_v:.3f} m/s; (mean speed)^3 = {mean_v ** 3:.1f} m3/s3; "
        f"mean of cubes = {mean_v3:.1f} m3/s3",
        f"energy pattern factor = mean(v^3) / mean(v)^3 = {epf:.3f}",
        f"power density at 1.225 kg/m3: from the mean speed {pd_wrong:.0f} W/m2; "
        f"correct {pd_right:.0f} W/m2",
        f"  through the rotor (A = {area:,.0f} m2): {pd_wrong * area / 1e6:.2f} MW vs "
        f"{pd_right * area / 1e6:.2f} MW of wind power",
        f"power curve at the mean speed: {p_at_mean:.0f} kW per turbine -> "
        f"{e_curve_mean:.1f} GWh/yr for the farm",
        f"power curve hour by hour: {e_curve_hourly:.1f} GWh/yr "
        f"(the mean-speed shortcut is {100 * (e_curve_mean / e_curve_hourly - 1):+.0f} %)",
    ])

    # ============================================================ B. dimensions =====
    rho, a_rot, v10 = Q(1.225, "kg/m3"), Q(area, "m2"), Q(10, "m/s")
    lines = []
    for label, expr in (("1/2 rho A v^3", lambda: 0.5 * rho * a_rot * v10 ** 3),
                        ("1/2 rho A v^2", lambda: 0.5 * rho * a_rot * v10 ** 2)):
        q = expr()
        try:
            check(q, "W")
            lines.append(f"{label:14s} -> [{q.dimension()}] = power: "
                         f"{q.magnitude('MW'):.2f} MW")
        except DimensionError:
            ok_force = True
            try:
                check(q, "N")
            except DimensionError:
                ok_force = False
            lines.append(f"{label:14s} -> [{q.dimension()}] is NOT a power"
                         + (" (it is a force)" if ok_force else ""))
    t_heat = Q(28, "kg") * Q(900, "J/kg/K") * Q(40, "K")
    lines.append(f"m c dT for a 28 kg module, c = 900 J/(kg K), 40 K: "
                 f"{t_heat.magnitude('MJ'):.2f} MJ [{t_heat.dimension()}]")
    rho_site = Q(877.67, "hPa") / (Q(R_DRY_AIR, "J/kg/K") * Q(kelvin(16.78), "K"))
    lines.append(f"p / (R T) = {rho_site.magnitude('kg/m3'):.4f} kg/m3 "
                 f"[{rho_site.dimension()}]")
    emit("ex_dimension_checks", lines)

    # Rayleigh's method: P = k rho^a A^b v^c ; dimensions of P = L^2 M T^-3
    # rows: L, M, T ; columns: a, b, c
    m_wind = np.array([[-3.0, 2.0, 1.0], [1.0, 0.0, 0.0], [0.0, 0.0, -1.0]])
    a, b, c = np.linalg.solve(m_wind, np.array([2.0, 1.0, -3.0]))
    # drag F = k rho^a v^b L^c ; F = L M T^-2
    m_drag = np.array([[-3.0, 1.0, 1.0], [1.0, 0.0, 0.0], [0.0, -1.0, 0.0]])
    a2, b2, c2 = np.linalg.solve(m_drag, np.array([1.0, 1.0, -2.0]))
    emit("ex_rayleigh", [
        "wind power P = k rho^a A^b v^c; match L, M, T:",
        "  L: -3a + 2b + c = 2;  M: a = 1;  T: -c = -3",
        f"  solution a = {a:.0f}, b = {b:.0f}, c = {c:.0f}  ->  P = k rho A v^3",
        "drag force F = k rho^a v^b D^c:",
        f"  solution a = {a2:.0f}, b = {b2:.0f}, c = {c2:.0f}  ->  F = k rho v^2 D^2",
    ])

    lam = (n_rpm * 2 * math.pi / 60) * 75.0 / 10.0
    v60, v100 = float(hourly["ws_60m_ms"].mean()), mean_v
    alpha = math.log(v100 / v60) / math.log(100 / 60)
    ratio_log = math.log(100 / 0.03) / math.log(60 / 0.03)
    # roughness length that reproduces the data-pack ratio: ln(100/z0) = r ln(60/z0)
    r = v100 / v60
    z0 = math.exp((math.log(100) - r * math.log(60)) / (1 - r))
    emit("ex_profile", [
        f"tip-speed ratio at 10 rpm, R = 75 m, v = 10 m/s: lambda = omega R / v = {lam:.2f}",
        "    units: (rad/s) m / (m/s) = rad = 1, dimensionless",
        f"log profile with z0 = 0.03 m: v(100)/v(60) = ln(100/0.03)/ln(60/0.03) = "
        f"{ratio_log:.4f}",
        f"data pack means: v(100)/v(60) = {v100:.3f}/{v60:.3f} = {r:.4f}",
        f"  power-law exponent alpha = ln({r:.4f})/ln(100/60) = {alpha:.3f}",
        f"  log-law roughness length that fits the ratio: z0 = {z0:.3f} m",
    ])

    emit("ex_sigfigs", [
        f"289812.4371 MWh to 4 s.f.: {format_sig(289812.4371, 4)} MWh; "
        f"to 3 s.f.: {format_sig(289812.4371, 3)} MWh",
        f"0.0500 has 3 s.f.: {format_sig(0.05, 3)}; 9.996 to 3 s.f.: {format_sig(9.996, 3)}",
        f"0.1 + 0.2 in binary floating point = {0.1 + 0.2!r}",
        f"round(2.5) = {round(2.5)}, round(3.5) = {round(3.5)} (Python rounds half to even)",
        f"round(2.675, 2) = {round(2.675, 2)} (2.675 is stored as {2.675:.20f})",
    ])

    # tolerance stack-up along one PV table: 13 modules side by side and 12 clamp gaps
    n_mod, w_mod, t_mod = 13, 1134.0, 2.0          # width synthetic; tolerance assumed
    n_gap, w_gap, t_gap = 12, 20.0, 1.0            # assumed clamp gap
    nominal = n_mod * w_mod + n_gap * w_gap
    tols = [t_mod] * n_mod + [t_gap] * n_gap
    worst = un.stack_worst_case(tols)
    rss = un.stack_rss(tols)
    rng = np.random.default_rng(20260101)
    dev = (rng.uniform(-t_mod, t_mod, (200_000, n_mod)).sum(axis=1)
           + rng.uniform(-t_gap, t_gap, (200_000, n_gap)).sum(axis=1))
    q_lo, q_hi = np.quantile(dev, [0.00135, 0.99865])
    rail, rail_tol = 15050.0, 5.0
    clear_nom = rail - nominal
    hist, edges = np.histogram(dev, bins=40, range=(-20, 20), density=True)
    csv("ch02-tolerance.csv", "dev_mm,density",      # left bin edges, for ybar interval
        [(f"{edges[i]:.1f}", f"{hist[i]:.5f}") for i in range(len(hist))]
        + [(f"{edges[-1]:.1f}", "0")])
    emit("ex_tolerance", [
        f"table length = 13 x 1134 mm + 12 x 20 mm = {nominal:,.0f} mm",
        f"tolerances: module width +-{t_mod:.0f} mm (assumed), gap +-{t_gap:.0f} mm (assumed)",
        f"worst case: +-{worst:.0f} mm; root-sum-square: +-{rss:.1f} mm",
        f"Monte Carlo, uniform parts, 200,000 tables: std {dev.std():.2f} mm; "
        f"99.73 % of tables within {q_lo:+.1f} .. {q_hi:+.1f} mm",
        f"rail 15,050 +-{rail_tol:.0f} mm: nominal end clearance {clear_nom:.0f} mm in total, "
        f"worst case {clear_nom - worst - rail_tol:.0f} mm",
    ])

    first = hourly.iloc[0]
    sp, wd = float(first["ws_100m_ms"]), float(first["wd_100m_deg"])
    u_c = -sp * math.sin(math.radians(wd))
    v_c = -sp * math.cos(math.radians(wd))
    dirs = np.array([350.0, 10.0])
    vec = math.degrees(math.atan2(np.mean(np.sin(np.radians(dirs))),
                                  np.mean(np.cos(np.radians(dirs)))))
    vec = round(vec, 6) % 360
    emit("ex_wind_direction", [
        f"first hour of the data pack: {sp:.2f} m/s from {wd:.0f} deg (FROM, clockwise "
        f"from north)",
        f"blows towards {(wd + 180) % 360:.0f} deg; components u (east) = {u_c:+.3f} m/s, "
        f"v (north) = {v_c:+.3f} m/s",
        f"check: sqrt(u^2 + v^2) = {math.hypot(u_c, v_c):.2f} m/s",
        f"directions 350 and 10 deg: arithmetic mean {dirs.mean():.0f} deg (wrong); "
        f"vector mean {vec:.0f} deg",
    ])

    emit("ex_fermi", [
        "order-of-magnitude estimate before any model:",
        "  PV:   60 MWp x 1600 kWh/kWp       = 96 GWh",
        "  wind: 60 MW x 8760 h x 0.35       = 184 GWh",
        "  sum                               ~ 280 GWh",
        "  upper bound: 100 MW x 8760 h      = 876 GWh (export limit all year)",
        f"screening model of chapter 1: {(e_pv + e_wind) / 1000:.1f} GWh "
        f"({100 * ((e_pv + e_wind) / 1000 / 280 - 1):+.0f} % from the estimate)",
    ])

    # =========================================================== C. measurement =====
    readings = [600.0, 343.0, 100.0, 34.3, 10.0, 3.0]
    lines = ["clamp meter, 600.0 A range, +-(1.5 % of reading + 5 digits), digit 0.1 A "
             "(assumed spec)"]
    rows = []
    for r in readings:
        lim, u = un.from_reading_spec(r, pct_of_reading=1.5, counts=5, count_size=0.1)
        lines.append(f"  reading {r:6.1f} A: limit +-{lim:5.2f} A = +-{100 * lim / r:5.2f} % "
                     f"of reading; u = {u:.2f} A")
    for r in np.geomspace(2.0, 600.0, 60):
        lim, _ = un.from_reading_spec(r, pct_of_reading=1.5, counts=5, count_size=0.1)
        rows.append((f"{r:.3f}", f"{100 * lim / r:.3f}"))
    csv("ch02-meter-error.csv", "reading_a,limit_pct", rows)
    emit("ex_meter_spec", lines)

    def ma_to_c(ma, lo=-40.0, hi=60.0):
        return lo + (ma - 4.0) / 16.0 * (hi - lo)
    emit("ex_loop", [
        "temperature transmitter, 4-20 mA = -40..+60 degC (assumed)",
        f"  12.00 mA -> {ma_to_c(12.0):.1f} degC; 4.00 mA -> {ma_to_c(4.0):.1f} degC; "
        f"20.00 mA -> {ma_to_c(20.0):.1f} degC",
        f"  sensitivity {100 / 16:.2f} degC per mA; 0.01 mA resolution = "
        f"{0.01 * 100 / 16:.4f} degC",
        "  0 mA is outside 4-20 mA: a broken wire is detected (live zero)",
        "16-bit converter over 0..2000 W/m2: step = 2000 / 65536 = "
        f"{2000 / 65536:.4f} W/m2",
        f"12-bit converter over the same range: step = {2000 / 4096:.3f} W/m2",
    ])

    rng = np.random.default_rng(20260102)
    i_obs = np.round(10.42 + rng.normal(0, 0.035, 10), 2)
    ta = un.type_a(i_obs)
    k_t = un.coverage_factor(0.95, ta.dof)
    emit("ex_type_a", [
        "ten readings of one string current, same conditions (synthetic), A:",
        "  " + ", ".join(f"{x:.2f}" for x in i_obs),
        f"mean {ta.mean:.3f} A; s = {ta.s:.4f} A; u(mean) = s / sqrt(10) = {ta.u_mean:.4f} A",
        f"degrees of freedom {ta.dof}; t-factor for 95 % = {k_t:.3f}; "
        f"U = {k_t * ta.u_mean:.3f} A",
    ])

    u_res = un.resolution(0.1)
    u_spec = un.rectangular(0.3)
    u_t = math.hypot(u_res, u_spec)
    emit("ex_type_b", [
        "thermometer: resolution 0.1 degC, data-sheet limit +-0.3 degC (assumed)",
        f"  resolution: 0.05 / sqrt(3) = {u_res:.4f} K",
        f"  data sheet: 0.3 / sqrt(3)  = {u_spec:.4f} K",
        f"  combined:   sqrt(sum of squares) = {u_t:.3f} K; U(k=2) = {2 * u_t:.2f} K",
    ])

    t_k = kelvin(16.78)
    dens = lambda p, T, R: p / (R * T)            # noqa: E731
    vals = {"p": 87767.0, "T": t_k, "R": R_DRY_AIR}
    inst = un.combine(dens, vals, {"p": un.rectangular(50.0), "T": un.rectangular(0.3),
                                   "R": 0.0})
    repr_ = un.combine(dens, vals, {"p": un.rectangular(50.0),
                                    "T": math.hypot(un.rectangular(0.3), 2.0), "R": 0.0})
    emit("ex_density_budget", [
        "air density rho = p / (R T) at Plant P annual means (data pack 1.0.0)",
        "instrument only: p +-0.5 hPa, T +-0.3 K (assumed limits, rectangular)",
        *inst.report("kg/m3"),
        "plus representativeness: 2 m temperature used for 100 m air, u = 2 K (assumed)",
        *repr_.report("kg/m3"),
    ])

    wpd = lambda rho, v: 0.5 * rho * v ** 3       # noqa: E731
    w_res = un.combine(wpd, {"rho": 1.0546, "v": 7.10},
                       {"rho": repr_.u_c, "v": 0.02 * 7.10})
    rel_pl = un.relative_power_law({"rho": 1, "v": 3},
                                   {"rho": repr_.u_c / 1.0546, "v": 0.02})
    emit("ex_power_density_budget", [
        "wind power density 0.5 rho v^3 with u(v)/v = 2 % (assumed) and u(rho) from above",
        *w_res.report("W/m2"),
        f"power-law shortcut: sqrt((1 x {100 * repr_.u_c / 1.0546:.2f} %)^2 + "
        f"(3 x 2 %)^2) = {100 * rel_pl:.2f} %",
    ])

    # anemometer calibration (synthetic wind-tunnel points)
    f_hz = np.array([80.0, 105.0, 130.0, 155.0, 180.0, 205.0, 230.0, 255.0, 280.0, 305.0, 330.0])
    rng = np.random.default_rng(20260103)
    v_ref = np.round(0.04620 * f_hz + 0.240 + rng.normal(0, 0.018, f_hz.size), 3)
    slope, offset = np.polyfit(f_hz, v_ref, 1)
    fit = slope * f_hz + offset
    resid = v_ref - fit
    s_fit = float(np.sqrt(np.sum(resid ** 2) / (f_hz.size - 2)))
    v_use = slope * 152.0 + offset
    v_generic = 0.0480 * 152.0 + 0.0
    csv("ch02-calibration.csv", "f_hz,v_ref,v_fit,resid_mms",
        [(f"{a:.0f}", f"{b:.3f}", f"{c:.4f}", f"{1000 * d:.1f}")
         for a, b, c, d in zip(f_hz, v_ref, fit, resid)])
    u_cert = un.from_expanded(0.05, 2)
    u_v = math.sqrt(u_cert ** 2 + s_fit ** 2)
    emit("ex_calibration", [
        "cup anemometer, wind-tunnel calibration (synthetic points)",
        "  f (Hz):    " + " ".join(f"{x:.0f}" for x in f_hz),
        "  v_ref (m/s): " + " ".join(f"{x:.2f}" for x in v_ref),
        f"least-squares line: v = {slope:.5f} f + {offset:.4f} m/s",
        f"residual standard deviation {1000 * s_fit:.1f} mm/s; largest residual "
        f"{1000 * np.max(np.abs(resid)):.1f} mm/s",
        f"reading 152.0 Hz -> {v_use:.3f} m/s with this calibration",
        f"  generic transfer function v = 0.0480 f (assumed): {v_generic:.3f} m/s "
        f"({100 * (v_generic / v_use - 1):+.1f} %, {300 * (v_generic / v_use - 1):+.0f} % "
        "in v^3)",
        f"u(v) = sqrt(certificate {u_cert:.3f}^2 + fit {s_fit:.3f}^2) = {u_v:.3f} m/s "
        f"(field effects not included)",
    ])

    s_true, s_nominal, mv = 8.62, 9.00, 7.10
    emit("ex_pyranometer", [
        "pyranometer output 7.10 mV; individual sensitivity 8.62 uV per W/m2 (certificate)",
        f"  G = 7100 uV / 8.62 = {1000 * mv / s_true:.1f} W/m2",
        f"  with the nominal 9.00 uV per W/m2 instead: {1000 * mv / s_nominal:.1f} W/m2 "
        f"({100 * (s_true / s_nominal - 1):+.1f} %)",
    ])

    eff = lambda p_ac, p_dc: 100.0 * p_ac / p_dc   # noqa: E731
    u_rel = 0.0010                                  # 0.10 % standard uncertainty each (assumed)
    cases = []
    lines = ["inverter efficiency acceptance: guaranteed eta >= 98.5 % at the test point",
             "power analyser: u = 0.10 % of reading on each channel (assumed, uncorrelated)"]
    for name, p_dc, p_ac in (("T1", 1250.0, 1230.0), ("T2", 1250.0, 1235.0),
                             ("T3", 1250.0, 1226.25)):
        res = un.combine(eff, {"p_ac": p_ac, "p_dc": p_dc},
                         {"p_ac": u_rel * p_ac, "p_dc": u_rel * p_dc})
        U = res.expanded(2)
        guarded = un.conformity(res.y, U, lower=98.5)
        simple = un.conformity(res.y, U, lower=98.5, rule="simple")
        cases.append((name, res.y, U, guarded.verdict))
        lines.append(f"{name}: eta = {res.y:.2f} %, U(k=2) = {U:.2f} points -> guarded "
                     f"{guarded.verdict}, simple {simple.verdict}")
    corr = un.combine(eff, {"p_ac": 1230.0, "p_dc": 1250.0},
                      {"p_ac": u_rel * 1230.0, "p_dc": u_rel * 1250.0},
                      {("p_ac", "p_dc"): 0.8})
    lines.append(f"acceptance limit with guard band w = U: {98.5 + cases[0][2]:.2f} %")
    Uc = corr.expanded()
    dc_ = un.conformity(corr.y, Uc, lower=98.5)
    lines.append(f"T1 with correlation r = 0.8 between channels: U = {Uc:.3f} points,")
    lines.append(f"    interval {corr.y - Uc:.2f} .. {corr.y + Uc:.2f} % -> guarded {dc_.verdict}; "
                 f"acceptance limit now {98.5 + Uc:.2f} %")
    csv("ch02-conformity.csv", "case,eta,U,verdict",
        [(n, f"{y:.3f}", f"{u:.3f}", d) for n, y, u, d in cases])
    emit("ex_conformity", lines)

    # Monte Carlo on annual energy: wind speed scale and irradiation scale
    scales = np.linspace(0.85, 1.15, 31)
    e_grid = np.array([wind_energy_gwh(hourly, curve, s) for s in scales])
    e1 = wind_energy_gwh(hourly, curve, 1.0)
    csv("ch02-sensitivity.csv", "scale,energy_rel,cube_rel",
        [(f"{s:.3f}", f"{e / e1:.4f}", f"{s ** 3:.4f}") for s, e in zip(scales, e_grid)])
    k_lo = (wind_energy_gwh(hourly, curve, 0.99) )
    k_hi = (wind_energy_gwh(hourly, curve, 1.01))
    sens = (k_hi - k_lo) / (0.02 * e1)
    pv_gwh = e_pv / 1000
    u_v_rel, u_h_rel = 0.03, 0.04                   # assumed teaching values
    f_tot = lambda f_v, f_H: np.interp(f_v, scales, e_grid) + pv_gwh * f_H   # noqa: E731
    mc = un.monte_carlo(f_tot, {"f_v": ("normal", 1.0, u_v_rel),
                                "f_H": ("normal", 1.0, u_h_rel)})
    lin = un.combine(lambda f_v, f_H: float(np.interp(f_v, scales, e_grid)) + pv_gwh * f_H,
                     {"f_v": 1.0, "f_H": 1.0}, {"f_v": u_v_rel, "f_H": u_h_rel})
    counts, edges = np.histogram(mc.samples, bins=50, range=(240, 340))
    hist = counts / (mc.samples.size * (edges[1] - edges[0]))   # density of ALL draws
    csv("ch02-mc-hist.csv", "energy_gwh,density",          # left bin edges, ybar interval
        [(f"{e:.1f}", f"{h:.5f}") for e, h in zip(edges[:-1], hist)] + [(f"{edges[-1]:.1f}", "0")])
    grid = np.linspace(240, 340, 101)
    normal = np.exp(-0.5 * ((grid - lin.y) / lin.u_c) ** 2) / (lin.u_c * math.sqrt(2 * math.pi))
    csv("ch02-mc-normal.csv", "energy_gwh,density",
        [(f"{g:.1f}", f"{n:.5f}") for g, n in zip(grid, normal)])
    p90 = float(np.quantile(mc.samples, 0.10))
    y_r, U_r = un.round_result(mc.mean, 2 * mc.std)
    emit("ex_montecarlo", [
        f"annual energy of {cite}, uncertainty of the resource only",
        f"wind: speed scale f_v, u(f_v) = {100 * u_v_rel:.0f} % (assumed); "
        f"PV: irradiation scale f_H, u(f_H) = {100 * u_h_rel:.0f} % (assumed)",
        f"sensitivity of wind energy to speed: dE/E = {sens:.2f} x dv/v (not 3: rated "
        "region and cut-in)",
        "first-order (GUM) budget:",
        *lin.report("GWh"),
        f"Monte Carlo, 200,000 draws: mean {mc.mean:.1f} GWh, std {mc.std:.1f} GWh, "
        f"95 % interval {mc.low:.1f} .. {mc.high:.1f} GWh",
        f"value exceeded with 90 % probability (P90): {p90:.1f} GWh",
        f"reported: E = {y_r} GWh, U(k=2) = {U_r} GWh (resource only; teaching values)",
    ])

    cases_r = [("annual energy, GWh", lin.y, lin.expanded(2)),
               ("air density, kg/m3", repr_.y, repr_.expanded(2)),
               ("string current, A", ta.mean, k_t * ta.u_mean),
               ("power density, W/m2", w_res.y, w_res.expanded(2))]
    lines = ["round U to two significant figures, the result to the same decimal place"]
    for label, y, U in cases_r:
        y_s, U_s = un.round_result(y, U)
        lines.append(f"  {label:22s} y = {y:<10.5g} U = {U:<8.3g} -> {y_s} +- {U_s}")
    emit("ex_report", lines)

    ct = vt = meter = 0.2                          # class indices used as limits, percent
    rss = math.sqrt(ct ** 2 + vt ** 2 + meter ** 2)
    emit("ex_metering_chain", [
        "revenue metering chain: CT 0.2 %, VT 0.2 %, meter 0.2 % (teaching limits)",
        f"  worst case {ct + vt + meter:.1f} %; root-sum-square {rss:.2f} %",
        f"  on 289.8 GWh/yr: worst case {289.8 * (ct + vt + meter) / 100:.2f} GWh, "
        f"RSS {289.8 * rss / 100:.2f} GWh per year",
        f"  at 45 currency units per MWh (fictional): {289.8e3 * rss / 100 * 45:,.0f} "
        "units per year",
    ])

    x = np.linspace(-1.6, 1.6, 161)
    rect = np.where(np.abs(x) <= 1, 0.5, 0.0)
    tri = np.clip(1 - np.abs(x), 0, None)
    sig = 1 / math.sqrt(3)
    norm = np.exp(-0.5 * (x / sig) ** 2) / (sig * math.sqrt(2 * math.pi))
    csv("ch02-distributions.csv", "x,rect,tri,normal",
        [(f"{a:.3f}", f"{b:.4f}", f"{c:.4f}", f"{d:.4f}") for a, b, c, d in zip(x, rect, tri, norm)])

    # data-pack check: units, time stamps and conventions of the hourly file
    import json
    idx = hourly.index
    offsets = sorted({str(t.utcoffset()) for t in idx})
    steps = sorted({int(s.total_seconds()) for s in (idx[1:] - idx[:-1])})
    expected = json.loads((datapack.release_dir("1.0.0") / "expected_results.json").read_text())
    ghi_kwh = float(hourly["ghi_wm2"].sum()) * 1.0 / 1000.0      # W/m2 x 1 h -> kWh/m2
    dd =(datapack.release_dir("1.0.0") / "data_dictionary.csv").read_text(encoding="utf-8")
    emit("ex_datapack_check", [
        f"hourly file: {len(hourly)} rows; first {idx[0].isoformat()}; last {idx[-1].isoformat()}",
        f"UTC offsets present: {offsets}; steps between rows (s): {steps}",
        f"duplicated time stamps: {int(idx.duplicated().sum())}; "
        f"quality flags present: {sorted(hourly['qc_flag'].unique().tolist())}",
        f"wind direction range {hourly['wd_100m_deg'].min()} .. {hourly['wd_100m_deg'].max()} deg "
        f"(dictionary: FROM, 0 = north, clockwise: {'FROM' in dd})",
        f"annual GHI = sum(W/m2) x 1 h / 1000 = {ghi_kwh:.1f} kWh/m2; expected_results.json "
        f"{expected['annual_ghi_kwh_m2']} -> {'PASS' if abs(ghi_kwh - expected['annual_ghi_kwh_m2']) < 0.05 else 'FAIL'}",
        f"mean wind 100 m = {hourly['ws_100m_ms'].mean():.3f} m/s; expected "
        f"{expected['mean_ws_100m_ms']} -> "
        f"{'PASS' if abs(hourly['ws_100m_ms'].mean() - expected['mean_ws_100m_ms']) < 0.0005 else 'FAIL'}",
        f"pressure unit hPa: range {hourly['p_hpa'].min():.1f} .. {hourly['p_hpa'].max():.1f} "
        "(Pa would be 100 times larger)",
    ])

    manifest = datapack.load_manifest("1.0.0")
    rel = "timeseries/plantp_hourly_8760.csv"
    actual = rec.file_sha256(datapack.release_dir("1.0.0") / rel)
    emit("ex_provenance", [
        f"file {rel} of data pack {manifest.get('release', '1.0.0')}",
        f"  SHA-256 in manifest: {manifest['files'][rel]['sha256'][:32]}...",
        f"  SHA-256 computed:    {actual[:32]}...",
        f"  identical: {actual == manifest['files'][rel]['sha256']}",
        "change one character in the file and the digest changes completely:",
        f"  digest('7.10') = {rec.digest('7.10')[:24]}...",
        f"  digest('7.11') = {rec.digest('7.11')[:24]}...",
    ])


if __name__ == "__main__":
    main()
