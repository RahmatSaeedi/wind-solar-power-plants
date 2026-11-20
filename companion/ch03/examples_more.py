"""Chapter 3 (expansion) — numbers for the additional lessons of sections A to D.

Run from the project root:   python -m companion.ch03.examples_more
Writes companion/ch03/expected/m_*.txt and diagrams/data/ch03-m-*.csv.
Values marked "assumed" are teaching values; nothing here is a design value.
"""
from __future__ import annotations

import cmath
import math
import sys
import textwrap
from pathlib import Path

import numpy as np
from scipy import stats as sps
from scipy.interpolate import CubicSpline, RegularGridInterpolator
from scipy.optimize import linprog

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plantp import datapack, numerics as nm, phasors as ph, screening as sc  # noqa: E402
from plantp import solar, stats as st  # noqa: E402
from plantp.units import Q, check  # noqa: E402

HERE = Path(__file__).resolve().parent
EXPECTED = HERE / "expected"
DATA = HERE.parents[1] / "diagrams" / "data"


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


def golden_max(f, a: float, b: float, tol: float = 1e-4):
    """Golden-section search for the maximum of a unimodal function on [a, b]."""
    g = (math.sqrt(5) - 1) / 2
    c, d = b - g * (b - a), a + g * (b - a)
    fc, fd = f(c), f(d)
    steps = 0
    while b - a > tol:
        steps += 1
        if fc > fd:
            b, d, fd = d, c, fc
            c = b - g * (b - a)
            fc = f(c)
        else:
            a, c, fc = c, d, fd
            d = a + g * (b - a)
            fd = f(d)
    return (a + b) / 2, steps


def main() -> None:
    EXPECTED.mkdir(exist_ok=True)
    hourly = datapack.load_hourly()
    curve = datapack.load_power_curve()
    vs, pk = curve["wind_speed_ms"].to_numpy(), curve["power_kw"].to_numpy()
    ws = hourly["ws_100m_ms"].to_numpy()

    # ---- A: geometry, rotation, motion, Taylor ---------------------------------------
    xt, yt = 1200.0, 800.0                       # turbine east/north of the substation (assumed)
    straight = math.hypot(xt, yt)
    rotor = math.pi * 75 ** 2
    found = math.pi * 10 ** 2 * 3.0
    emit("m_geometry", [
        f"cable from the substation to a turbine 1200 m east and 800 m north (assumed):",
        f"  straight line sqrt(1200^2 + 800^2) = {straight:.0f} m; along two roads "
        f"(east, then north) {xt + yt:.0f} m (+{100 * ((xt + yt) / straight - 1):.0f} %)",
        f"rotor swept area pi 75^2 = {rotor:,.0f} m2; a 120 deg sector of it = {rotor / 3:,.0f} m2",
        f"circular foundation 20 m diameter, 3 m deep: pi 10^2 x 3 = {found:,.0f} m3 of concrete",
    ])
    wd = 163.0                                   # prevailing direction FROM (the data-pack first hour)
    t_dir = math.radians(wd + 180)               # direction the wind blows TO
    ux, uy = math.sin(t_dir), math.cos(t_dir)    # unit vector downwind (east, north)
    d_east, d_north = 600.0, 1100.0              # second turbine relative to the first (assumed)
    downwind = d_east * ux + d_north * uy
    cross = d_east * uy - d_north * ux
    emit("m_rotation", [
        f"wind FROM {wd:.0f} deg blows TO {(wd + 180) % 360:.0f} deg: downwind unit vector "
        f"({ux:+.4f}, {uy:+.4f})",
        "second turbine 600 m east and 1100 m north of the first (assumed)",
        f"  rotated coordinates: downwind {downwind:.0f} m = {downwind / 150:.2f} D, crosswind "
        f"{cross:.0f} m = {cross / 150:.2f} D (D = 150 m)",
        f"  check: sqrt(downwind^2 + crosswind^2) = {math.hypot(downwind, cross):.0f} m = "
        f"{math.hypot(d_east, d_north):.0f} m (rotation keeps lengths)",
    ])
    omega = 10 * 2 * math.pi / 60
    tip = omega * 75
    emit("m_motion", [
        "rotor at 10 rpm (assumed), radius 75 m:",
        f"  omega = {omega:.4f} rad/s; tip speed v = omega r = {tip:.1f} m/s = {tip * 3.6:.0f} km/h",
        f"  centripetal acceleration of the tip omega^2 r = {omega ** 2 * 75:.1f} m/s2 = "
        f"{omega ** 2 * 75 / 9.80665:.1f} g",
        f"  rotation frequency 1P = {10 / 60:.4f} Hz; blade passing 3P = {3 * 10 / 60:.4f} Hz",
        f"  a point at mid-span (37.5 m) moves at {omega * 37.5:.1f} m/s: speed grows linearly with r",
    ])
    lines = ["small-angle approximations: sin x ~ x, cos x ~ 1 - x^2/2 (x in rad)"]
    for deg in (5, 10, 20, 30):
        x = math.radians(deg)
        lines.append(f"  {deg:2d} deg: sin x = {math.sin(x):.5f}, x = {x:.5f} "
                     f"({100 * (x / math.sin(x) - 1):+.2f} %); cos x = {math.cos(x):.5f}, "
                     f"1 - x^2/2 = {1 - x * x / 2:.5f}")
    v0 = 7.0
    for dv in (0.035, 0.07, 0.14):
        exact = (1 + dv) ** 3 - 1
        lin = 3 * dv
        lines.append(f"  v^3 near 7 m/s, change {100 * dv:.1f} %: exact {100 * exact:+.2f} %, "
                     f"linear 3 dv/v {100 * lin:+.2f} %, quadratic {100 * (lin + 3 * dv * dv):+.2f} %")
    emit("m_taylor", lines)

    # ---- A: optimal tilt by golden-section search ------------------------------------
    days = np.arange(1, 366, 2)
    times = np.arange(4.0, 20.0, 1 / 6)

    def annual_beam(tilt_deg):
        total = 0.0
        for n in days:
            el, az = solar.sun_position(34.0, n, times)
            el = np.asarray(el)
            up = el > 2.0
            am = 1.0 / np.sin(np.radians(el[up]))
            dni = 1353.0 * 0.7 ** (am ** 0.678)   # Meinel clear-sky beam model, W/m2
            cos_t = np.clip(solar.incidence_cos(el[up], np.asarray(az)[up], tilt_deg, 180.0), 0, None)
            total += float(np.sum(dni * cos_t)) / 6.0 * 2   # Wh/m2; every 2nd day
        return total / 1000.0                               # kWh/m2 per year
    tilts = np.arange(0, 61, 5)
    vals = [annual_beam(t) for t in tilts]
    best, steps = golden_max(annual_beam, 0.0, 60.0, tol=0.2)
    csv("ch03-m-tilt.csv", "tilt,beam", [(t, f"{v:.1f}") for t, v in zip(tilts, vals)])
    emit("m_tilt", [
        "annual clear-sky BEAM irradiation on a south-facing plane at 34 deg N",
        "    (Meinel model 1353 x 0.7^(AM^0.678) W/m2; every 2nd day, 10-min steps)",
        "  tilt (deg): " + " ".join(f"{t:5.0f}" for t in tilts),
        "  kWh/m2:     " + " ".join(f"{v:5.0f}" for v in vals),
        f"  golden-section search on [0, 60]: optimum {best:.1f} deg after {steps} steps; "
        f"{annual_beam(best):.0f} kWh/m2",
        f"  horizontal plane {vals[0]:.0f}; latitude tilt (34 deg) {annual_beam(34.0):.0f} kWh/m2",
        "  diffuse light, clouds and row shading are NOT in this model (chapters 10, 12, 15)",
    ])

    # ---- B: per unit and power-factor correction -------------------------------------
    s_base, v_base = 100e6, 33e3
    z_base = v_base ** 2 / s_base
    i_base = s_base / (math.sqrt(3) * v_base)
    z_pu = complex(0.625, 0.550) / z_base
    p, pf1, pf2 = 50e6, 0.90, 0.98
    qc = p * (math.tan(math.acos(pf1)) - math.tan(math.acos(pf2)))
    emit("m_perunit", [
        f"per-unit system, S_base = 100 MVA, V_base = 33 kV:",
        f"  Z_base = V^2/S = {z_base:.3f} ohm; I_base = S/(sqrt(3) V) = {i_base:.1f} A",
        f"  cable 0.625 + j0.550 ohm = {z_pu.real:.5f} + j{z_pu.imag:.5f} pu",
        f"  30 MW at pf 0.95 -> I = 552.5 A = {552.5 / i_base:.4f} pu",
        f"power-factor correction: 50 MW from pf 0.90 to 0.98 needs",
        f"  Qc = P (tan phi1 - tan phi2) = 50 ({math.tan(math.acos(pf1)):.4f} - "
        f"{math.tan(math.acos(pf2)):.4f}) = {qc / 1e6:.2f} Mvar",
        f"  apparent power falls from {p / pf1 / 1e6:.2f} to {p / pf2 / 1e6:.2f} MVA "
        f"(current -{100 * (1 - pf1 / pf2):.1f} %)",
    ])

    # ---- B: second-order system: tower vibration --------------------------------------
    m_top = 300e3                                 # kg equivalent top mass (assumed)
    f_n = 0.25                                    # Hz first tower mode (assumed)
    zeta = 0.01                                   # damping ratio (assumed)
    k = m_top * (2 * math.pi * f_n) ** 2
    c = 2 * zeta * math.sqrt(k * m_top)

    def rhs(t, y):
        return np.array([y[1], -(c * y[1] + k * y[0]) / m_top])
    t, y = nm.rk4(rhs, np.array([0.5, 0.0]), 0.0, 60.0, 0.01)
    peaks = [i for i in range(1, len(t) - 1) if y[i, 0] > y[i - 1, 0] and y[i, 0] > y[i + 1, 0]]
    logdec = math.log(y[peaks[0], 0] / y[peaks[1], 0])
    csv("ch03-m-tower.csv", "t,x,env", [(f"{a:.2f}", f"{b:.4f}",
                                          f"{0.5 * math.exp(-zeta * 2 * math.pi * f_n * a):.4f}")
                                         for a, b in zip(t[::20], y[::20, 0])])
    r = np.linspace(0, 3, 301)
    h = 1 / np.sqrt((1 - r ** 2) ** 2 + (2 * zeta * r) ** 2)
    csv("ch03-m-resonance.csv", "r,h", [(f"{a:.3f}", f"{min(b, 60):.3f}") for a, b in zip(r, h)])
    for name_, f_ex in (("1P", 10 / 60), ("3P", 0.5)):
        rr = f_ex / f_n
        hh = 1 / math.sqrt((1 - rr ** 2) ** 2 + (2 * zeta * rr) ** 2)
        if name_ == "1P":
            h1 = (rr, hh)
        else:
            h3 = (rr, hh)
    emit("m_tower", [
        "tower and nacelle as mass-spring-damper: m x'' + c x' + k x = F(t)",
        f"  m = 300 t, f_n = 0.25 Hz, damping ratio 1 % (all assumed): k = m (2 pi f_n)^2 = "
        f"{k / 1e3:.0f} kN/m",
        f"  free vibration from 0.5 m (RK4, dt 0.01 s): period {1 / f_n:.1f} s; log decrement "
        f"{logdec:.4f} (theory 2 pi zeta = {2 * math.pi * zeta:.4f})",
        f"  amplitude after 60 s: {0.5 * math.exp(-zeta * 2 * math.pi * f_n * 60):.3f} m",
        f"  dynamic amplification |H| = 1/sqrt((1-r^2)^2 + (2 zeta r)^2):",
        f"    1P at 10 rpm: r = {h1[0]:.3f}, |H| = {h1[1]:.2f};  3P: r = {h3[0]:.2f}, "
        f"|H| = {h3[1]:.2f};  at r = 1: {1 / (2 * zeta):.0f}",
    ])

    # ---- B: Newton-Raphson power flow on two buses ------------------------------------
    z_line = complex(0.01, 0.05)                  # pu (assumed)
    y_line = 1 / z_line
    g_, b_ = y_line.real, y_line.imag
    p_sp, q_sp = 0.50, 0.0                        # plant injects 50 MW at unity pf (100 MVA)

    def mismatch(x):
        th, v = x
        p_calc = v * v * g_ - v * (g_ * math.cos(th) + b_ * math.sin(th))
        q_calc = -v * v * b_ - v * (g_ * math.sin(th) - b_ * math.cos(th))
        return np.array([p_sp - p_calc, q_sp - q_calc])

    x = np.array([0.0, 1.0])
    hist = []
    for it in range(6):
        f0 = mismatch(x)
        hist.append((it, x[0], x[1], float(np.max(np.abs(f0)))))
        if np.max(np.abs(f0)) < 1e-12:
            break
        jac = np.zeros((2, 2))
        for j in range(2):
            dx = np.zeros(2)
            dx[j] = 1e-7
            jac[:, j] = (mismatch(x + dx) - f0) / 1e-7
        x = x - np.linalg.solve(jac, f0)
    v2 = cmath.rect(x[1], x[0])
    emit("m_newton_pf", [
        "two buses: bus 1 slack 1.0 /_ 0 pu; plant bus 2 injects P = 0.50, Q = 0 pu;",
        "    line z = 0.01 + j0.05 pu (assumed, 100 MVA base)",
        "  iteration  theta2 (deg)   V2 (pu)   largest mismatch (pu)",
        *[f"  {i:9d} {math.degrees(th):13.5f} {v:9.6f}   {mm:.2e}" for i, th, v, mm in hist],
        f"  solution V2 = {abs(v2):.5f} pu at {math.degrees(cmath.phase(v2)):.3f} deg; the plant "
        f"bus voltage rises {100 * (abs(v2) - 1):.2f} %",
        "  mismatch falls roughly as the square of the previous one: quadratic convergence",
    ])

    # ---- C: probability: availability ---------------------------------------------------
    a = 0.97
    k_av = np.arange(13)
    pmf = sps.binom.pmf(k_av, 12, a)
    csv("ch03-m-binom.csv", "k,p", [(i, f"{v:.6f}") for i, v in zip(k_av, pmf)])
    lam_m = 2.0 / 12                               # failures per turbine-month (assumed 2/yr)
    emit("m_binomial", [
        "12 turbines, each available with probability 0.97, independently (assumed)",
        f"  P(all 12) = 0.97^12 = {pmf[12]:.4f}; P(exactly 11) = {pmf[11]:.4f}; "
        f"P(at least 11) = {pmf[11:].sum():.4f}",
        f"  P(10 or fewer) = {pmf[:11].sum():.4f}; expected number available "
        f"{(k_av * pmf).sum():.2f} = 12 x 0.97",
        "failures as a Poisson process, 2 per turbine per year (assumed):",
        f"  one turbine, one month: P(0) = e^-{lam_m:.4f} = {math.exp(-lam_m):.4f}; "
        f"P(1 or more) = {1 - math.exp(-lam_m):.4f}",
        f"  whole farm, one month (rate {12 * lam_m:.0f}): P(0) = {math.exp(-12 * lam_m):.4f}; "
        f"P(3 or more) = {1 - sps.poisson.cdf(2, 12 * lam_m):.4f}",
        "  independence is an assumption: a grid outage or icing stops many turbines at once",
    ])
    sig = 10.1
    emit("m_exceedance", [
        "normal model of annual energy: mean 289.8 GWh, standard deviation 10.1 GWh",
        *[f"  P{q:<3d} = mean - z sigma, z = {sps.norm.ppf(q / 100):.4f}: "
          f"{289.8 - sps.norm.ppf(q / 100) * sig:.1f} GWh"
          for q in (50, 75, 90, 95, 99)],
        f"  probability that a year exceeds 300 GWh: {1 - sps.norm.cdf((300 - 289.8) / sig):.3f}",
        "  these numbers inherit every assumption of the 10.1 GWh (teaching values, chapter 2)",
    ])

    # ---- C: hypothesis test with autocorrelation --------------------------------------
    months = hourly.index.month
    first = ws[np.isin(months, [3, 4, 5])]
    second = ws[np.isin(months, [9, 10, 11])]
    diff = first.mean() - second.mean()
    se_naive = math.sqrt(first.var(ddof=1) / first.size + second.var(ddof=1) / second.size)
    n1, n2 = st.effective_n(first), st.effective_n(second)
    se_eff = math.sqrt(first.var(ddof=1) / n1 + second.var(ddof=1) / n2)
    emit("m_hypothesis", [
        "is the mean speed of spring (Mar-May) different from autumn (Sep-Nov)?",
        f"  means {first.mean():.3f} and {second.mean():.3f} m/s; difference {diff:+.3f} m/s",
        f"  naive t = diff / se, se from n = {first.size} and {second.size}: t = {diff / se_naive:.2f}, "
        f"p = {2 * (1 - sps.norm.cdf(abs(diff / se_naive))):.2g}",
        f"  with effective sizes {n1:.0f} and {n2:.0f}: t = {diff / se_eff:.2f}, "
        f"p = {2 * (1 - sps.t.cdf(abs(diff / se_eff), n1 + n2 - 2)):.2f}",
        "  the naive test calls the difference significant; the honest one does not",
    ])

    # ---- C: time-series basics and persistence forecast ---------------------------------
    hours_of_day = hourly.index.hour
    pv_p = np.asarray(sc.pv_ac_power_mw(hourly["ghi_wm2"], 60, 50))
    w_p = np.asarray(sc.wind_power_mw(ws, vs, pk, 12))
    diur = [(h_, f"{pv_p[hours_of_day == h_].mean():.3f}", f"{w_p[hours_of_day == h_].mean():.3f}")
            for h_ in range(24)]
    diur.append((24, diur[-1][1], diur[-1][2]))
    csv("ch03-m-diurnal.csv", "hour,pv,wind", diur)
    lines = ["persistence forecast of farm power: 'the next value equals the current one'"]
    rows = []
    for lead in (1, 3, 6, 12, 24):
        err = w_p[lead:] - w_p[:-lead]
        mae = float(np.mean(np.abs(err)))
        rmse = float(np.sqrt(np.mean(err ** 2)))
        rows.append((lead, f"{mae:.3f}", f"{rmse:.3f}"))
        lines.append(f"  lead {lead:2d} h: MAE {mae:5.2f} MW ({100 * mae / 60:4.1f} % of 60 MW), "
                     f"RMSE {rmse:5.2f} MW")
    clim = float(np.mean(np.abs(w_p - w_p.mean())))
    lines.append(f"  'climatology' (always the annual mean): MAE {clim:.2f} MW")
    csv("ch03-m-persist.csv", "lead,mae,rmse", rows)
    peak_pv = int(np.argmax([float(d[1]) for d in diur[:24]]))
    lines.append(f"mean daily cycle: PV peaks at hour {peak_pv}; wind mean ranges "
                 f"{min(float(d[2]) for d in diur):.1f}..{max(float(d[2]) for d in diur):.1f} MW")
    emit("m_timeseries", lines)

    # ---- D: numerical differentiation error -----------------------------------------
    f = math.exp
    hs = np.logspace(-15, -1, 57)
    rows = []
    for hh in hs:
        fwd = abs((f(1 + hh) - f(1)) / hh - math.e)
        cen = abs((f(1 + hh) - f(1 - hh)) / (2 * hh) - math.e)
        rows.append((f"{hh:.3e}", f"{max(fwd, 1e-17):.3e}", f"{max(cen, 1e-17):.3e}"))
    csv("ch03-m-numdiff.csv", "h,forward,central", rows)
    best_f = hs[int(np.argmin([float(r_[1]) for r_ in rows]))]
    best_c = hs[int(np.argmin([float(r_[2]) for r_ in rows]))]
    emit("m_numdiff", [
        "derivative of e^x at x = 1 (exact e) by finite differences:",
        f"  forward (f(x+h) - f(x))/h: smallest error near h = {best_f:.1e} "
        f"(theory sqrt(eps) = {math.sqrt(2.2e-16):.1e})",
        f"  central (f(x+h) - f(x-h))/2h: smallest error near h = {best_c:.1e} "
        f"(theory eps^(1/3) = {2.2e-16 ** (1 / 3):.1e})",
        "  smaller h is NOT always better: truncation error falls, round-off error grows",
    ])

    # ---- D: bilinear interpolation in an efficiency table ---------------------------
    p_frac = np.array([0.1, 0.25, 0.5, 0.75, 1.0])
    v_dc = np.array([900.0, 1100.0, 1300.0])
    eff = np.array([[96.2, 96.6, 96.0], [97.8, 98.1, 97.6], [98.3, 98.5, 98.1],
                    [98.2, 98.4, 98.0], [98.0, 98.2, 97.8]])   # percent (synthetic)
    interp = RegularGridInterpolator((p_frac, v_dc), eff)
    pt = (0.6, 1000.0)
    emit("m_bilinear", [
        "inverter efficiency table (synthetic), %",
        "  P/P_rated    900 V  1100 V  1300 V",
        *[f"  {pf_:9.2f}  " + "  ".join(f"{e_:6.1f}" for e_ in row) for pf_, row in zip(p_frac, eff)],
        f"  bilinear value at P = 0.6 P_rated, 1000 V: {float(interp(pt)):.3f} %",
        "  linear interpolation along one axis, then along the other; outside",
        "    the table the interpolator refuses (extrapolation policy)",
    ])

    # ---- D: LP shadow prices ------------------------------------------------------------
    e_pv = float(pv_p.sum()) / 1000
    e_w = float(w_p.sum()) / 1000
    yp, yw = e_pv / 60, e_w / 60
    res = linprog([0.55, 1.25], A_ub=[[-yp, -yw], [1, 0], [1 / 1.2, 1]], b_ub=[-290, 80, 120],
                  bounds=[(0, None), (0, None)], method="highs")
    duals = res.ineqlin.marginals
    res2 = linprog([0.55, 1.25], A_ub=[[-yp, -yw], [1, 0], [1 / 1.2, 1]], b_ub=[-290, 81, 120],
                   bounds=[(0, None), (0, None)], method="highs")
    emit("m_lp_dual", [
        "shadow prices (dual values) of the PV/wind mix linear program:",
        f"  energy constraint: {-duals[0]:.4f} cost units per extra GWh/yr required",
        f"  land constraint:   {-duals[1]:.4f} cost units saved per extra MWp of land",
        f"  AC capacity:       {-duals[2]:.4f} (not binding: zero)",
        f"  check: with 81 MWp of land the cost falls from {res.fun:.3f} to {res2.fun:.3f} "
        f"({res.fun - res2.fun:.4f})",
    ])

    # ---- D: unit-aware numerics -----------------------------------------------------
    h_t = Q(4.6, "m") * math.sin(math.radians(25))
    shadow = h_t / math.tan(math.radians(32.55))
    pitch = Q(4.6, "m") * math.cos(math.radians(25)) + shadow
    check(pitch, "m")
    g_stc = Q(1000, "W/m2")
    e_day = Q(60, "MW") * (Q(6.2, "kWh/m2") / g_stc) * 0.833
    emit("m_units", [
        f"row pitch computed with quantities: {pitch.to('m'):.4g} (dimension check passed)",
        f"PV energy of a day with H = 6.2 kWh/m2: {e_day.to('MWh'):.4g}",
        "  dividing by G_STC makes the dimension an energy; check(e, 'MWh') would refuse",
        "  the version without it (chapter 2)",
    ])


if __name__ == "__main__":
    main()
