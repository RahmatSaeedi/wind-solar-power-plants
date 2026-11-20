"""Chapter 3 — numbers for sections A (algebra to calculus) and B (linear and dynamic
models).

Run from the project root:   python -m companion.ch03.examples_ab
Writes companion/ch03/expected/*.txt (lines of at most 78 characters) and the plot
data diagrams/data/ch03-*.csv. Values marked "assumed" are teaching values.
"""
from __future__ import annotations

import math
import sys
import textwrap
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plantp import datapack, dc, numerics as nm, phasors as ph  # noqa: E402
from plantp import screening as sc, solar  # noqa: E402

HERE = Path(__file__).resolve().parent
EXPECTED = HERE / "expected"
DATA = HERE.parents[1] / "diagrams" / "data"


def emit(name: str, lines: list[str]) -> None:
    wrapped = []
    for line in lines:
        wrapped += textwrap.wrap(line, 78, subsequent_indent="    ",
                                 drop_whitespace=False) or [""]
    wrapped = [w.rstrip() for w in wrapped]
    text = "\n".join(wrapped) + "\n"
    (EXPECTED / f"{name}.txt").write_text(text, encoding="utf-8", newline="\n")
    print(f"== {name}\n{text}")


def csv(name: str, header: str, rows) -> None:
    with open(DATA / name, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(header + "\n")
        for row in rows:
            fh.write(",".join(str(x) for x in row) + "\n")


def main() -> None:
    EXPECTED.mkdir(exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    curve = datapack.load_power_curve()
    vs, pk = curve["wind_speed_ms"].to_numpy(), curve["power_kw"].to_numpy()

    # ======================================================== A1 algebra, powers =====
    d1, d2 = 150.0, 170.0
    emit("a_scaling", [
        "rotor diameter 150 m -> 170 m: area ratio (170/150)^2 = "
        f"{(d2 / d1) ** 2:.4f} (+{100 * ((d2 / d1) ** 2 - 1):.1f} %)",
        f"wind 7.0 -> 7.7 m/s (+10 %): power ratio 1.1^3 = {1.1 ** 3:.3f} "
        f"(+{100 * (1.1 ** 3 - 1):.1f} %)",
        f"speed for twice the power: 2^(1/3) = {2 ** (1 / 3):.4f} -> "
        f"+{100 * (2 ** (1 / 3) - 1):.1f} % speed",
        f"log10(5e6 W / 1e-3 W) = {math.log10(5e6 / 1e-3):.1f} orders of magnitude",
        f"time for an exponential decay to 1 %: t = tau ln(100) = {math.log(100):.3f} tau",
    ])

    # ======================================================== A2 trigonometry ========
    days = {"winter solstice (355)": 355, "equinox (81)": 81, "summer solstice (172)": 172}
    rows = []
    lines = ["sun at 34 deg N, solar time (Cooper declination)"]
    for label, n in days.items():
        d = float(solar.declination(n))
        noon_el = 90 - 34 + d
        ws = float(solar.sunrise_hour_angle(34.0, n))
        lines.append(f"{label:22s} declination {d:+6.2f} deg, noon elevation "
                     f"{noon_el:5.2f} deg, day {2 * abs(ws) / 15:5.2f} h")
        for t in np.arange(4.0, 20.01, 0.25):
            el, az = solar.sun_position(34.0, n, t)
            if float(el) > 0:
                rows.append((n, f"{t:.2f}", f"{float(az):.2f}", f"{float(el):.2f}"))
    for n in days.values():
        csv(f"ch03-sunpath-{n}.csv", "solar_time,azimuth,elevation",
            [r_[1:] for r_ in rows if r_[0] == n])
    emit("a_sun", lines)

    # row spacing for no noon shading at the winter solstice
    slope_len, tilt = 4.6, 25.0              # two modules in portrait (assumed)
    el_w = 90 - 34 + float(solar.declination(355))
    h = slope_len * math.sin(math.radians(tilt))
    proj = slope_len * math.cos(math.radians(tilt))
    shadow = h / math.tan(math.radians(el_w))
    pitch = proj + shadow
    emit("a_rows", [
        f"table slope length 4.6 m (assumed), tilt 25 deg (assumed)",
        f"height h = 4.6 sin 25 = {h:.3f} m; ground projection 4.6 cos 25 = {proj:.3f} m",
        f"winter-solstice noon elevation {el_w:.2f} deg: shadow h / tan(el) = {shadow:.3f} m",
        f"row pitch = {pitch:.3f} m; ground cover ratio 4.6 / pitch = {slope_len / pitch:.3f}",
        f"at 10:00 solar time the sun is lower: elevation "
        f"{float(solar.sun_position(34.0, 355, 10.0)[0]):.2f} deg",
    ])

    el, az = solar.sun_position(34.0, 172, 10.0)
    s = solar.sun_vector(el, az)
    nrm = solar.surface_normal(25.0, 180.0)
    cos_t = float(s @ nrm)
    emit("a_vectors", [
        f"21 June, 10:00 solar time: elevation {float(el):.2f} deg, azimuth "
        f"{float(az):.2f} deg",
        f"sun vector (E, N, U) = ({s[0]:+.4f}, {s[1]:+.4f}, {s[2]:+.4f}), |s| = "
        f"{np.linalg.norm(s):.4f}",
        f"panel normal, tilt 25 deg facing south = ({nrm[0]:+.4f}, {nrm[1]:+.4f}, "
        f"{nrm[2]:+.4f})",
        f"cos(theta) = s . n = {cos_t:.4f}; angle of incidence {math.degrees(math.acos(cos_t)):.2f} "
        "deg",
        f"beam of 850 W/m2 normal to the sun -> {850 * cos_t:.1f} W/m2 on the panel, "
        f"{850 * max(float(np.sin(np.radians(el))), 0):.1f} W/m2 on the ground",
    ])

    # ======================================================== A3 functions ===========
    g = np.linspace(0, 1100, 111)
    p_pv = sc.pv_ac_power_mw(g, 60, 50)
    csv("ch03-pv-function.csv", "ghi,p_mw", [(f"{a:.0f}", f"{b:.3f}") for a, b in zip(g, p_pv)])
    g_knee = 50.0 / (60 * 0.85 * 0.98) * 1000
    emit("a_functions", [
        "PV screening model P(G) = min(60 x G/1000 x 0.85 x 0.98, 50) MW: piecewise linear",
        f"  slope below the knee: {60 * 0.85 * 0.98 / 1000 * 1000:.3f} MW per 1000 W/m2",
        f"  knee at G = 50 / (60 x 0.833) x 1000 = {g_knee:.1f} W/m2",
        f"wind power curve: cut-in {vs[np.argmax(pk > 0)]:.1f} m/s, rated from "
        f"{vs[np.argmax(pk >= 5000)]:.1f} m/s, table ends at {vs[-1]:.1f} m/s",
        f"  P(8.25 m/s) by linear interpolation = {np.interp(8.25, vs, pk):.1f} kW",
        f"  P(26 m/s) is outside the table: lerp_table(..., outside='zero') -> "
        f"{nm.lerp_table(26.0, vs, pk, outside='zero'):.0f} kW (cut-out)",
    ])

    # ======================================================== A4 derivatives ==========
    v_ci, v_r, p_r = 3.0, 13.0, 5000.0
    model = lambda v: p_r * (v ** 3 - v_ci ** 3) / (v_r ** 3 - v_ci ** 3)   # noqa: E731
    dmodel = lambda v: p_r * 3 * v ** 2 / (v_r ** 3 - v_ci ** 3)              # noqa: E731
    h_ = 0.25
    fd_c = (np.interp(8.0 + h_, vs, pk) - np.interp(8.0 - h_, vs, pk)) / (2 * h_)
    rows = [(f"{v:.2f}", f"{np.interp(v, vs, pk):.1f}",
             f"{model(v) if v_ci <= v <= v_r else (p_r if v > v_r else 0):.1f}")
            for v in np.arange(0, 25.01, 0.25)]
    csv("ch03-powercurve.csv", "v,table_kw,cubic_kw", rows)
    from scipy.interpolate import CubicSpline
    spline = CubicSpline(vs, pk)
    fd_rows = [(hh, (np.interp(8.0 + hh, vs, pk) - np.interp(8.0 - hh, vs, pk)) / (2 * hh))
               for hh in (1.0, 0.5, 0.25)]
    emit("a_derivative", [
        "candidate model: ideal cubic law between cut-in 3 m/s and rated 13 m/s,",
        "    P = 5000 (v^3 - 27) / (2197 - 27) kW",
        f"  P(8) = {model(8.0):.0f} kW, but the table gives {np.interp(8.0, vs, pk):.0f} kW: "
        f"{100 * (model(8.0) / np.interp(8.0, vs, pk) - 1):+.0f} % -> model REJECTED",
        "slope of the table at 8 m/s:",
        *[f"  central difference, h = {hh:.2f} m/s: {d:.1f} kW/(m/s)" for hh, d in fd_rows],
        f"  cubic spline through the table, exact derivative: {float(spline(8.0, 1)):.1f} "
        "kW/(m/s)",
        f"  relative sensitivity (dP/P)/(dv/v) at 8 m/s: "
        f"{float(spline(8.0, 1)) * 8 / float(spline(8.0)):.2f}",
    ])

    # maximum power point of one PVM-550 module (simplified one-diode model)
    m = dc.PVM_550
    vt = 1.380649e-23 * 298.15 / 1.602176634e-19
    nvt = m.n_cells * vt
    i0 = m.i_sc / math.expm1(m.v_oc / nvt)
    g_ = lambda v: m.i_sc + i0 - i0 * math.exp(v / nvt) * (1 + v / nvt)    # dP/dV  # noqa: E731
    dg = lambda v: -i0 * math.exp(v / nvt) * (2 + v / nvt) / nvt             # noqa: E731
    res = nm.newton(g_, dg, 40.0)
    v_mpp = res.root
    i_mpp = float(dc.pv_iv_curve(m, 1, v_mpp))
    vv = np.linspace(0, m.v_oc, 200)
    ii = dc.pv_iv_curve(m, 1, vv)
    csv("ch03-mpp.csv", "v,i,p", [(f"{a:.3f}", f"{b:.4f}", f"{a * b:.2f}") for a, b in zip(vv, ii)])
    emit("a_mpp", [
        "P(V) = V I(V), simplified one-diode model of PVM-550 (no series resistance)",
        f"dP/dV = 0 solved with Newton from 40 V: {res.iterations} iterations",
        "  iterates: " + ", ".join(f"{x:.4f}" for x in res.history[:6]),
        f"V_mpp = {v_mpp:.3f} V, I_mpp = {i_mpp:.3f} A, P_max = {v_mpp * i_mpp:.1f} W",
        f"datasheet: 41.96 V, 13.11 A, 550 W -> the model's V_mpp is "
        f"{100 * (v_mpp / 41.96 - 1):+.1f} % (no series resistance; chapter 10)",
    ])

    # partial derivatives of P_PV(G, T)
    p_stc, gam = 550.0, -0.0035
    p = lambda G, T: p_stc * G / 1000 * (1 + gam * (T - 25))   # noqa: E731
    G0, T0 = 800.0, 45.0
    dPdG = p_stc / 1000 * (1 + gam * (T0 - 25))
    dPdT = p_stc * G0 / 1000 * gam
    lin = p(G0, T0) + dPdG * 50 + dPdT * 5
    emit("a_partial", [
        f"P(G, T) = 550 x G/1000 x (1 - 0.0035 (T - 25)); at G = 800 W/m2, T = 45 C: "
        f"P = {p(G0, T0):.2f} W",
        f"  dP/dG = {dPdG:.4f} W per W/m2; dP/dT = {dPdT:.3f} W per K",
        f"  linear estimate at (850, 50): {lin:.2f} W; exact {p(850, 50):.2f} W",
    ])

    # constrained optimisation: share a fixed volume of copper between two feeders
    i1, i2, l1, l2 = 300.0, 150.0, 180.0, 180.0
    vol = (240 + 240) * 180.0                # mm2 x m, same copper as two 240 mm2 cables
    rho = 1.72e-8
    loss = lambda a1: rho * 2 * (l1 * i1 ** 2 / (a1 * 1e-6) +                # noqa: E731
                                 l2 * i2 ** 2 / ((vol - a1 * l1) / l2 * 1e-6))
    a1_opt = vol / (l1 + l2 * i2 / i1)       # Lagrange: A proportional to I
    a2_opt = (vol - a1_opt * l1) / l2
    emit("a_lagrange", [
        "two DC feeders, 180 m each, 300 A and 150 A; copper volume fixed at two 240 mm2",
        f"  equal areas 240/240 mm2: loss {loss(240.0) / 1000:.2f} kW",
        f"  Lagrange optimum A1/A2 = I1/I2: {a1_opt:.0f} / {a2_opt:.0f} mm2, loss "
        f"{loss(a1_opt) / 1000:.2f} kW ({100 * (loss(a1_opt) / loss(240.0) - 1):+.1f} %)",
        f"  current densities at the optimum: {i1 / a1_opt:.3f} and {i2 / a2_opt:.3f} A/mm2 "
        "(equal)",
    ])

    # ======================================================== A5 integrals ============
    day = datapack.load_hourly("day_summer")
    pv_day = np.asarray(sc.pv_ac_power_mw(day["ghi_wm2"], 60, 50))
    unclipped = np.asarray(sc.pv_dc_power_mw(day["ghi_wm2"], 60)) * sc.ETA_INVERTER
    on = np.nonzero(unclipped > 0)[0]
    t_rise, t_set = on[0], on[-1] + 1
    length = t_set - t_rise
    pmax = unclipped.max()
    e_sine = 2 * pmax * length / math.pi
    t = np.linspace(0, 24, 241)
    sine = np.where((t >= t_rise) & (t <= t_set),
                    pmax * np.sin(np.pi * (t - t_rise) / length), 0.0)
    csv("ch03-halfsine.csv", "t,sine,hourly_unclipped",
        [(f"{a:.2f}", f"{b:.3f}", f"{unclipped[min(int(a), 23)]:.3f}") for a, b in zip(t, sine)])
    emit("a_integral", [
        f"summer day: PV (unclipped AC) from hour {t_rise} to {t_set}, peak {pmax:.2f} MW",
        f"half-sine model: E = integral of Pmax sin(pi (t - t_r)/L) dt = 2 Pmax L / pi "
        f"= {e_sine:.1f} MWh",
        f"hourly data, unclipped: {unclipped.sum():.1f} MWh "
        f"({100 * (e_sine / unclipped.sum() - 1):+.1f} %)",
        f"hourly data, with the 50 MW inverter limit: {pv_day.sum():.1f} MWh",
    ])

    # heat from a current ramp: integral of I^2 R dt
    r = 0.0123                                # ohm, a feeder (assumed)
    i_end, t_end = 315.0, 3600.0
    q_exact = r * i_end ** 2 * t_end / 3
    tt = np.linspace(0, t_end, 7)
    q_trap = nm.trapezoid(r * (i_end * tt / t_end) ** 2, tt[1] - tt[0])
    emit("a_heat", [
        "current rising linearly from 0 to 315 A in one hour through 0.0123 ohm (assumed)",
        f"  Q = integral R (I t/T)^2 dt = R I^2 T / 3 = {q_exact / 1e3:.1f} kJ "
        f"= {q_exact / 3.6e6:.3f} kWh",
        f"  trapezoid with 6 intervals: {q_trap / 1e3:.1f} kJ "
        f"({100 * (q_trap / q_exact - 1):+.2f} %)",
        f"  using the mean current (157.5 A) instead: {r * 157.5 ** 2 * t_end / 1e3:.1f} kJ "
        f"({100 * (157.5 ** 2 * t_end * r / q_exact - 1):+.0f} %)",
    ])

    # ======================================================== B1 linear systems ======
    # four-node DC collector: three combiner boxes (current sources) to an inverter bus
    # node 1..3 combiner boxes, node 4 inverter input held by an ideal source at 1100 V
    g = 1 / np.array([0.020, 0.025, 0.015, 0.010, 0.012])  # branch conductances (assumed)
    # branches: 1-4 (0.020), 2-4 (0.025), 3-4 (0.015), 1-2 (0.010), 2-3 (0.012) ohm
    inj = np.array([314.6, 314.6, 288.4])        # A from each combiner box
    v4 = 1100.0
    gmat = np.array([[g[0] + g[3], -g[3], 0.0],
                     [-g[3], g[1] + g[3] + g[4], -g[4]],
                     [0.0, -g[4], g[2] + g[4]]])
    rhs = inj + np.array([g[0], g[1], g[2]]) * v4
    v_gauss = nm.solve_gauss(gmat, rhs)
    v_np = np.linalg.solve(gmat, rhs)
    emit("b_network", [
        "nodal equations G v = i for three combiner boxes feeding a 1100 V bus",
        "G (S) =",
        *["    " + " ".join(f"{x:9.2f}" for x in row) for row in gmat],
        "i (A) = " + " ".join(f"{x:.1f}" for x in rhs),
        "node voltages, Gaussian elimination: " + ", ".join(f"{x:.3f}" for x in v_gauss) + " V",
        "node voltages, numpy.linalg.solve:   " + ", ".join(f"{x:.3f}" for x in v_np) + " V",
        f"condition number of G: {nm.condition_number(gmat):.2f}",
    ])

    # DC power flow on three buses: 1 = point of connection (slack), 2 = PV, 3 = wind
    x12, x13, x23 = 0.08, 0.10, 0.05          # per-unit reactances (assumed, 100 MVA base)
    b = np.array([[1 / x12 + 1 / x23, -1 / x23], [-1 / x23, 1 / x13 + 1 / x23]])
    p_inj = np.array([0.45, 0.55])            # 45 MW PV, 55 MW wind on 100 MVA
    theta = np.linalg.solve(b, p_inj)
    th = np.array([0.0, *theta])
    f12, f13, f23 = (th[1] - th[0]) / x12, (th[2] - th[0]) / x13, (th[1] - th[2]) / x23
    emit("b_dcflow", [
        "DC power flow, 100 MVA base: P = B theta; bus 1 slack (theta = 0)",
        f"  injections: bus 2 (PV) 45 MW, bus 3 (wind) 55 MW; x12 {x12}, x13 {x13}, x23 {x23} pu",
        f"  theta2 = {math.degrees(theta[0]):.3f} deg, theta3 = {math.degrees(theta[1]):.3f} deg",
        f"  flows (MW): 2->1 {100 * f12:.1f}, 3->1 {100 * f13:.1f}, 2->3 {100 * f23:.1f}",
        f"  check at the slack: {100 * (f12 + f13):.1f} MW arrives = 100 MW injected",
    ])

    # least squares: temperature coefficient of P_max from module test points
    rng = np.random.default_rng(31)
    temps = np.array([15.0, 25.0, 35.0, 45.0, 55.0, 65.0])
    pmeas = np.round(550 * (1 - 0.0035 * (temps - 25)) + rng.normal(0, 1.2, temps.size), 1)
    a_mat = np.column_stack([np.ones_like(temps), temps - 25])
    coef_ne = np.linalg.solve(a_mat.T @ a_mat, a_mat.T @ pmeas)
    coef_ls, *_ = np.linalg.lstsq(a_mat, pmeas, rcond=None)
    resid = pmeas - a_mat @ coef_ls
    csv("ch03-lsq.csv", "t,p,fit,resid", [(f"{a:.0f}", f"{b:.1f}", f"{c:.2f}", f"{d:.2f}")
                                          for a, b, c, d in zip(temps, pmeas, a_mat @ coef_ls, resid)])
    emit("b_lsq", [
        "P_max of one module at six cell temperatures (synthetic test points), W:",
        "  T (C): " + " ".join(f"{x:.0f}" for x in temps),
        "  P (W): " + " ".join(f"{x:.1f}" for x in pmeas),
        "model P = p0 + p1 (T - 25); A = [1, T - 25]; normal equations A^T A c = A^T y",
        f"  normal equations: p0 = {coef_ne[0]:.2f} W, p1 = {coef_ne[1]:.4f} W/K",
        f"  numpy lstsq:      p0 = {coef_ls[0]:.2f} W, p1 = {coef_ls[1]:.4f} W/K",
        f"  gamma = p1 / p0 = {100 * coef_ls[1] / coef_ls[0]:.4f} %/K (true -0.35 %/K)",
        f"  residuals (W): " + " ".join(f"{x:+.2f}" for x in resid),
    ])

    # coupled thermal model: winding and oil of a transformer (two states)
    c_w, c_o = 2.0e5, 4.0e6                  # J/K (assumed)
    g_wo, g_oa = 4000.0, 2500.0               # W/K (assumed)
    a_th = np.array([[-g_wo / c_w, g_wo / c_w],
                     [g_wo / c_o, -(g_wo + g_oa) / c_o]])
    lam = np.linalg.eigvals(a_th)
    taus = sorted(-1 / lam.real)
    lam_pi, _, it = nm.power_iteration(a_th)
    emit("b_eigen", [
        "transformer winding (w) and oil (o): dT/dt = A T + b P, A in 1/s:",
        f"  A = [[{a_th[0, 0]:.5f}, {a_th[0, 1]:.5f}], [{a_th[1, 0]:.6f}, {a_th[1, 1]:.6f}]]",
        f"  eigenvalues {lam[0].real:.6f} and {lam[1].real:.6f} 1/s, both negative: stable",
        f"  time constants -1/lambda: {taus[0]:.0f} s ({taus[0] / 60:.1f} min) and {taus[1]:.0f} s "
        f"({taus[1] / 3600:.2f} h)",
        f"  power iteration finds the dominant |lambda| {lam_pi:.6f} 1/s in {it} steps",
    ])

    # ======================================================== B2 complex numbers ======
    r_km, x_km, km = 0.125, 0.110, 5.0        # 33 kV cable per phase (assumed)
    z = complex(r_km * km, x_km * km)
    v_ph = ph.polar(33e3 / math.sqrt(3), 0)
    p_w, pf = 30e6, 0.95
    i_mag = p_w / (math.sqrt(3) * 33e3 * pf)
    i = ph.polar(i_mag, -math.degrees(math.acos(pf)))
    v_send = v_ph + z * i
    s3 = ph.three_phase_power(v_ph, i)
    drop_exact = (abs(v_send) - abs(v_ph)) * math.sqrt(3)
    drop_apx = ph.voltage_drop_approx(p_w, s3.imag, z.real, z.imag, 33e3)
    loss = 3 * abs(i) ** 2 * z.real
    vm, va = ph.to_polar(v_send)
    emit("b_phasor", [
        "5 km of 33 kV cable, z = 0.125 + j0.110 ohm/km (assumed): Z = "
        f"{z.real:.3f} + j{z.imag:.3f} ohm",
        f"receiving end 33 kV, 30 MW at pf 0.95 lagging: I = {i_mag:.1f} A at "
        f"{-math.degrees(math.acos(pf)):.2f} deg",
        f"S = 3 V I* = {s3.real / 1e6:.2f} MW + j{s3.imag / 1e6:.2f} Mvar",
        f"sending phase voltage V_s = V_r + Z I = {vm:.1f} V at {va:.3f} deg",
        f"line-to-line drop: exact {drop_exact:.1f} V ({100 * drop_exact / 33e3:.2f} %); "
        f"approx (RP + XQ)/V = {drop_apx:.1f} V",
        f"cable loss 3 I^2 R = {loss / 1e3:.1f} kW ({100 * loss / p_w:.2f} % of 30 MW)",
    ])
    csv("ch03-phasor.csv", "name,re,im", [
        ("V_r", f"{v_ph.real:.1f}", f"{v_ph.imag:.1f}"),
        ("ZI", f"{(z * i).real:.1f}", f"{(z * i).imag:.1f}"),
        ("V_s", f"{v_send.real:.1f}", f"{v_send.imag:.1f}"),
        ("I", f"{i.real:.2f}", f"{i.imag:.2f}")])

    ia, ib, ic = ph.polar(100, 0), ph.polar(80, -125), ph.polar(95, 118)
    i0, i1, i2 = ph.symmetrical_components(ia, ib, ic)
    emit("b_sequence", [
        "unbalanced currents: Ia 100 /_0, Ib 80 /_-125, Ic 95 /_118 (A)",
        f"  zero     I0 = {abs(i0):6.2f} A /_ {math.degrees(np.angle(i0)):7.2f} deg",
        f"  positive I1 = {abs(i1):6.2f} A /_ {math.degrees(np.angle(i1)):7.2f} deg",
        f"  negative I2 = {abs(i2):6.2f} A /_ {math.degrees(np.angle(i2)):7.2f} deg",
        f"  unbalance |I2|/|I1| = {100 * abs(i2) / abs(i1):.1f} %",
        "  check: rebuilding Ia from the sequences gives "
        f"{abs(ph.from_sequences(i0, i1, i2)[0]):.2f} A",
    ])

    # ======================================================== B3 differential eq. ====
    tau, theta_ss = 1800.0, 40.0             # s, K rise (assumed cable)
    f = lambda t, y: (theta_ss - y) / tau    # noqa: E731
    exact = lambda t: theta_ss * (1 - np.exp(-t / tau))   # noqa: E731
    rows = []
    lines = ["cable temperature rise after a load step: tau = 1800 s, final rise 40 K",
             f"{'dt (s)':>8s} {'Euler err (K)':>14s} {'RK4 err (K)':>13s}  at t = 3600 s"]
    for dt in (900.0, 600.0, 300.0, 60.0):
        _, ye = nm.euler(f, 0.0, 0, 3600, dt)
        _, yr = nm.rk4(f, 0.0, 0, 3600, dt)
        lines.append(f"{dt:8.0f} {ye[-1] - exact(3600):14.4f} {yr[-1] - exact(3600):13.2e}")
    lines.append(f"exact rise at 3600 s: {exact(3600):.4f} K (1 - e^-2 of the final value)")
    t_e, y_e = nm.euler(f, 0.0, 0, 7200, 600)
    t_r, y_r = nm.rk4(f, 0.0, 0, 7200, 600)
    tt = np.linspace(0, 7200, 145)
    for k, tv in enumerate(tt):
        rows.append((f"{tv:.0f}", f"{exact(tv):.3f}",
                     f"{np.interp(tv, t_e, y_e):.3f}" if tv in t_e else "",
                     f"{np.interp(tv, t_r, y_r):.3f}" if tv in t_r else ""))
    csv("ch03-ode.csv", "t,exact,euler,rk4", rows)
    csv("ch03-ode-steps.csv", "t,euler,rk4",
        [(f"{a:.0f}", f"{b:.3f}", f"{c:.3f}") for a, b, c in zip(t_e, y_e, y_r)])
    _, y_bad = nm.euler(f, 0.0, 0, 36000, 4500)
    lines.append("Euler with dt = 4500 s (> 2 tau): " + ", ".join(f"{x:.0f}" for x in y_bad[:7])
                 + " ... (oscillates and grows)")
    csv("ch03-euler-unstable.csv", "t,euler", [(f"{4500 * k}", f"{x:.2f}") for k, x in enumerate(y_bad)])
    emit("b_ode", lines)

    # battery state of charge as a state variable over one day (S1, assumed schedule)
    hours = np.arange(25)
    p_bat = np.zeros(24)
    p_bat[9:15] = -5.0                        # charge 5 MW from 09 to 15 (negative)
    p_bat[18:22] = 6.0                        # discharge 6 MW from 18 to 22 (positive)
    eta = math.sqrt(0.86)
    soc = [4.0]                               # MWh at 00:00: the 10 % floor (assumed)
    for p in p_bat:
        de = -p * eta if p < 0 else -p / eta
        soc.append(soc[-1] + de)
    e_in = float(-p_bat[p_bat < 0].sum())
    e_out = float(p_bat[p_bat > 0].sum())
    csv("ch03-soc.csv", "hour,soc_mwh,p_mw", [(h_i, f"{s_i:.3f}", f"{(p_bat[h_i] if h_i < 24 else 0):.1f}")
                                              for h_i, s_i in zip(hours, soc)])
    emit("b_soc", [
        "dE/dt = -P eta_c (charging, P < 0) or -P / eta_d (discharging, P > 0);",
        "    one-way efficiency sqrt(0.86) = 0.927 (scenario S1)",
        "start 4.0 MWh; charge 5 MW from 09 to 15; discharge 6 MW from 18 to 22",
        f"  after charging (15:00): {soc[15]:.2f} MWh; after discharging (22:00): "
        f"{soc[22]:.2f} MWh",
        f"  window 4..36 MWh (10..90 % of 40 MWh): min {min(soc):.2f}, max {max(soc):.2f} -> "
        f"{'inside' if 4 - 1e-9 <= min(soc) and max(soc) <= 36 else 'OUTSIDE'}",
        f"  energy in {e_in:.0f} MWh, out {e_out:.0f} MWh, stored change "
        f"{soc[-1] - soc[0]:+.2f} MWh -> losses {e_in - e_out - (soc[-1] - soc[0]):.2f} MWh",
    ])


if __name__ == "__main__":
    main()
