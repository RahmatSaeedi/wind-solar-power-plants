"""Chapter 3 — numbers for sections C (data and uncertainty mathematics) and D
(numerical methods, optimisation and sensitivity).

Run from the project root:   python -m companion.ch03.examples_cd
Writes companion/ch03/expected/*.txt and diagrams/data/ch03-*.csv.
All prices, costs and limits are fictional teaching values.
"""
from __future__ import annotations

import math
import sys
import textwrap
from pathlib import Path

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.optimize import linprog

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plantp import datapack, numerics as nm, screening as sc  # noqa: E402
from plantp import stats as st, uncertainty as un  # noqa: E402

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


def farm_energy_gwh(speeds, curve, loss=sc.WIND_LOSS) -> float:
    return float(np.sum(sc.wind_power_mw(speeds, curve["wind_speed_ms"], curve["power_kw"],
                                         12, loss))) / 1000.0


def main() -> None:
    EXPECTED.mkdir(exist_ok=True)
    hourly = datapack.load_hourly()
    curve = datapack.load_power_curve()
    vs, pk = curve["wind_speed_ms"].to_numpy(), curve["power_kw"].to_numpy()
    ws = hourly["ws_100m_ms"].to_numpy()
    ghi = hourly["ghi_wm2"].to_numpy()
    cite = datapack.cite("S0", "1.0.0")

    # ======================================================== C1 description =========
    s = st.describe(ws)
    day = ghi[ghi > 0]
    sg = st.describe(day)
    skew = float(np.mean(((ws - ws.mean()) / ws.std()) ** 3))
    emit("c_describe", [
        f"hourly wind speed at 100 m, {cite}:",
        f"  n {s.n}, mean {s.mean:.3f}, std {s.std:.3f}, min {s.minimum:.2f}, "
        f"Q1 {s.q1:.2f}, median {s.median:.2f}, Q3 {s.q3:.2f}, max {s.maximum:.2f} m/s",
        f"  skewness {skew:.3f} (> 0: long tail of strong winds; median < mean)",
        f"GHI in daylight hours (> 0): n {sg.n}, mean {sg.mean:.1f}, median {sg.median:.1f}, "
        f"max {sg.maximum:.1f} W/m2",
    ])

    # ======================================================== C2 Weibull ===============
    fits = {"moments": st.weibull_fit_moments(ws), "max. likelihood": st.weibull_fit_mle(ws),
            "least squares": st.weibull_fit_lsq(ws)}
    vgrid = np.linspace(0, 30, 3001)
    p_turb = np.interp(vgrid, vs, pk, right=0.0)
    lines = [f"Weibull fits to the 8760 hourly speeds at 100 m ({cite})",
             f"{'method':16s} {'k':>6s} {'c (m/s)':>8s} {'mean':>7s} {'mean v^3':>9s} "
             f"{'farm GWh':>9s}"]
    for name, (k, c) in fits.items():
        e = float(np.trapezoid(p_turb * st.weibull_pdf(vgrid, k, c), vgrid)) * 8760 * 12 \
            * (1 - sc.WIND_LOSS) / 1e6
        lines.append(f"{name:16s} {k:6.3f} {c:8.3f} {st.weibull_mean(k, c):7.3f} "
                     f"{st.weibull_mean_cube(k, c):9.1f} {e:9.1f}")
    lines.append(f"{'data (hourly)':16s} {'':6s} {'':8s} {ws.mean():7.3f} {np.mean(ws ** 3):9.1f} "
                 f"{farm_energy_gwh(ws, curve):9.1f}")
    emit("c_weibull", lines)
    edges = np.arange(0, 26, 1.0)
    hist, _ = np.histogram(ws, bins=edges, density=True)
    k_ml, c_ml = fits["max. likelihood"]
    k_m, c_m = fits["moments"]
    k_l, c_l = fits["least squares"]
    csv("ch03-hist.csv", "v,density", [(f"{a:.1f}", f"{b:.5f}") for a, b in zip(edges[:-1], hist)]
        + [(f"{edges[-1]:.1f}", "0")])
    vv = np.linspace(0, 25, 251)
    csv("ch03-weibull.csv", "v,mle,mom,lsq",
        [(f"{v:.2f}", f"{st.weibull_pdf(v, k_ml, c_ml):.5f}", f"{st.weibull_pdf(v, k_m, c_m):.5f}",
          f"{st.weibull_pdf(v, k_l, c_l):.5f}") for v in vv])

    # ======================================================== C3 sampling ==============
    month = hourly.index.month
    mmeans = np.array([ws[month == m].mean() for m in range(1, 13)])
    r1 = st.lag1_autocorrelation(ws)
    neff = st.effective_n(ws)
    m_naive = st.mean_ci(ws)
    m_eff = st.mean_ci(ws, n_eff=neff)
    # block bootstrap by day: resample whole days to keep the hour-to-hour memory
    rng = np.random.default_rng(20260101)
    days = ws.reshape(365, 24)
    boot_mean, boot_e = [], []
    for _ in range(400):
        pick = days[rng.integers(0, 365, 365)].ravel()
        boot_mean.append(pick.mean())
        boot_e.append(farm_energy_gwh(pick, curve))
    emit("c_sampling", [
        "monthly mean speeds (m/s): " + " ".join(f"{x:.2f}" for x in mmeans),
        f"  spread of monthly means (std) {mmeans.std(ddof=1):.3f} m/s",
        f"lag-1 autocorrelation of hourly speeds r1 = {r1:.3f}",
        f"effective number of independent hours n_eff = n (1 - r1)/(1 + r1) = {neff:.0f} "
        f"of {ws.size}",
        f"95 % CI of the annual mean: naive (n = 8760) {m_naive[1]:.3f} .. {m_naive[2]:.3f}; "
        f"with n_eff {m_eff[1]:.3f} .. {m_eff[2]:.3f} m/s",
        f"block bootstrap by day (400 resamples): std of the mean {np.std(boot_mean, ddof=1):.3f} "
        f"m/s, std of farm energy {np.std(boot_e, ddof=1):.2f} GWh "
        f"({100 * np.std(boot_e, ddof=1) / farm_energy_gwh(ws, curve):.1f} %)",
        "    (sampling within ONE synthetic year only; year-to-year variability is extra)",
    ])

    # ======================================================== C4 regression ============
    w80 = hourly["ws_80m_ms"].to_numpy()
    fit = st.linear_fit(w80, ws)
    lo, hi = fit.slope_ci()
    csv("ch03-regression.csv", "v80,v100", [(f"{a:.2f}", f"{b:.2f}") for a, b in zip(w80[::25], ws[::25])])
    emit("c_regression", [
        "v100 = a v80 + b, least squares on 8760 hours",
        f"  a = {fit.slope:.4f} (95 % CI {lo:.4f} .. {hi:.4f}), b = {fit.intercept:.4f} m/s",
        f"  r^2 = {fit.r2:.4f}, residual std {fit.s_resid:.3f} m/s",
        f"  predicted mean at 100 m from the 80 m mean: {fit.predict(w80.mean()):.3f} m/s "
        f"(data {ws.mean():.3f})",
        "  warning: the CI assumes independent residuals; hourly residuals are not",
    ])

    pv = np.asarray(sc.pv_ac_power_mw(ghi, 60, 50))
    wind = np.asarray(sc.wind_power_mw(ws, vs, pk, 12))
    r_hour = st.pearson(pv, wind)
    pv_d, wind_d = pv.reshape(365, 24).sum(1), wind.reshape(365, 24).sum(1)
    r_day = st.pearson(pv_d, wind_d)
    pv_m = np.array([pv[month == m].sum() for m in range(1, 13)])
    wind_m = np.array([wind[month == m].sum() for m in range(1, 13)])
    r_month = st.pearson(pv_m, wind_m)
    csv("ch03-daily.csv", "pv_mwh,wind_mwh", [(f"{a:.1f}", f"{b:.1f}") for a, b in zip(pv_d, wind_d)])
    emit("c_correlation", [
        f"Pearson correlation of PV and wind output ({cite}):",
        f"  hourly {r_hour:+.3f}; daily energies {r_day:+.3f}; monthly energies {r_month:+.3f}",
        "  negative = complementary; the sign and size depend on the time scale",
        "  correlation measures LINEAR association only; it is not causation",
    ])

    # ======================================================== C5 outliers ==============
    bad = ws.copy()
    rng = np.random.default_rng(5)
    spikes = rng.choice(ws.size, 5, replace=False)
    bad[spikes] = [38.0, 41.5, 0.0, 36.2, 44.0]
    bad[4000:4012] = bad[4000]                  # stuck sensor for 12 hours
    iqr_mask = st.iqr_outliers(bad, k=3.0)
    z = (bad - bad.mean()) / bad.std()
    z_mask = np.abs(z) > 4
    stuck = np.zeros(bad.size, bool)
    run = 1
    for i in range(1, bad.size):
        run = run + 1 if bad[i] == bad[i - 1] else 1
        if run >= 6:
            stuck[i - run + 1:i + 1] = True
    step = np.abs(np.diff(bad, prepend=bad[0])) > 12
    emit("c_outliers", [
        "five spikes injected (38.0, 41.5, 0.0, 36.2, 44.0 m/s) and a 12-hour stuck sensor",
        f"  IQR fences (k = 3): {int(iqr_mask.sum())} flagged; spikes found "
        f"{int(iqr_mask[spikes].sum())} of 5",
        f"  |z| > 4: {int(z_mask.sum())} flagged; spikes found {int(z_mask[spikes].sum())} of 5",
        f"  step > 12 m/s in one hour: {int(step.sum())} flagged (each spike gives 2 steps)",
        f"  same value 6 or more hours in a row: {int(stuck.sum())} flagged "
        f"(the stuck run: {int(stuck[4000:4012].sum())} of 12)",
        "  the 0.0 m/s spike is inside the normal range: only the step test sees it",
    ])

    # ======================================================== C6 correlated inputs =====
    e_w = farm_energy_gwh(ws, curve)
    e_pv = float(pv.sum()) / 1000
    sens = 1.62
    f_tot = lambda f_v, f_H: e_w * (1 + sens * (f_v - 1)) + e_pv * f_H   # noqa: E731
    lines = ["total energy E = E_w (1 + 1.62 (f_v - 1)) + E_pv f_H, u(f_v) 3 %, u(f_H) 4 %"]
    for r in (0.0, 0.5, -0.5):
        res = un.combine(f_tot, {"f_v": 1.0, "f_H": 1.0}, {"f_v": 0.03, "f_H": 0.04},
                         {("f_v", "f_H"): r} if r else None)
        lines.append(f"  correlation r = {r:+.1f}: u_c = {res.u_c:.2f} GWh")
    jac = np.array([e_w * sens, e_pv])
    cov = np.array([[0.03 ** 2, 0.5 * 0.03 * 0.04], [0.5 * 0.03 * 0.04, 0.04 ** 2]])
    lines.append(f"  matrix form u^2 = J S J^T with r = 0.5: u_c = {math.sqrt(jac @ cov @ jac):.2f} "
                 "GWh (same)")
    emit("c_correlated", lines)

    # ======================================================== D1 root finding ==========
    target_kw = 30e3 / 12 / (1 - sc.WIND_LOSS)
    spline = CubicSpline(vs, pk)
    f = lambda v: float(np.interp(v, vs, pk)) - target_kw           # noqa: E731
    fs = lambda v: float(spline(v)) - target_kw                     # noqa: E731
    dfs = lambda v: float(spline(v, 1))                             # noqa: E731
    rb = nm.bisection(f, 3.0, 13.0, tol=1e-6)
    rs = nm.secant(f, 6.0, 10.0, tol=1e-10)
    rn = nm.newton(fs, dfs, 10.0, tol=1e-12)
    # independent references: a very tight bisection for the table, and Newton run to the
    # end for the spline; errors below 1e-15 (machine precision) are left out of the plot
    ref_table = nm.bisection(f, 3.0, 13.0, tol=1e-15).root
    ref_spline = rn.history[-1]

    def err(x, ref):
        e = abs(x - ref)
        return "" if e < 1e-15 else f"{e:.3e}"
    rows = []
    for k in range(1, 25):
        eb = err(rb.history[k - 1], ref_table) if k <= len(rb.history) else ""
        es = err(rs.history[k + 1], ref_table) if k + 1 < len(rs.history) else ""
        en = err(rn.history[k], ref_spline) if k < len(rn.history) else ""
        rows.append((k, eb, es, en))
    csv("ch03-roots.csv", "k,bisection,secant,newton", rows)
    emit("d_roots", [
        f"farm output 30 MW -> each turbine {target_kw:.1f} kW before 12 % losses",
        f"  bisection on [3, 13] (table): v = {rb.root:.6f} m/s after {rb.iterations} halvings",
        f"  secant from 6 and 10 (table): v = {rs.root:.6f} m/s after {rs.iterations} steps",
        f"  Newton on a cubic spline:     v = {rn.root:.6f} m/s after {rn.iterations} steps",
        "  Newton iterates: " + ", ".join(f"{x:.6f}" for x in rn.history[:6]),
        "  error per step: bisection halves it; secant and Newton square it (roughly)",
    ])

    k_hist = []
    v_cv2 = (ws.std(ddof=1) / ws.mean()) ** 2
    g = lambda k: math.gamma(1 + 2 / k) / math.gamma(1 + 1 / k) ** 2 - 1 - v_cv2  # noqa: E731
    r = nm.bisection(g, 0.5, 20.0, tol=1e-8)
    emit("d_weibull_k", [
        f"method of moments: Gamma(1+2/k)/Gamma(1+1/k)^2 - 1 = (s/mean)^2 = {v_cv2:.5f}",
        f"  bisection on [0.5, 20]: k = {r.root:.6f} after {r.iterations} steps",
        "  first iterates: " + ", ".join(f"{x:.3f}" for x in r.history[:8]),
    ])
    del k_hist

    # ======================================================== D2 interpolation =========
    nodes = np.arange(3.0, 24.0, 2.0)
    pnodes = np.interp(nodes, vs, pk)
    xs = np.linspace(3, 23, 201)
    lag = np.array([nm.lagrange(x, nodes, pnodes) for x in xs])
    lin = np.interp(xs, nodes, pnodes)
    ref = np.interp(xs, vs, pk)
    csv("ch03-runge.csv", "v,table,linear,lagrange",
        [(f"{a:.2f}", f"{b:.1f}", f"{c:.1f}", f"{d:.1f}") for a, b, c, d in zip(xs, ref, lin, lag)])
    emit("d_interp", [
        "11 nodes of the power curve, 3..23 m/s every 2 m/s",
        f"  linear interpolation: worst error {np.max(np.abs(lin - ref)):.0f} kW",
        f"  degree-10 polynomial (Lagrange): worst error {np.max(np.abs(lag - ref)):.0f} kW "
        f"(at {xs[np.argmax(np.abs(lag - ref))]:.1f} m/s)",
        f"  polynomial value at 22 m/s: {nm.lagrange(22.0, nodes, pnodes):.0f} kW "
        f"(true 5000 kW)",
        "  high-degree polynomials oscillate between nodes (Runge); piecewise methods do not",
    ])

    # ======================================================== D3 quadrature ============
    # half-sine over the daylight interval: exact integral 2 peak L / pi
    peak, length_min = 58.0, 864.0                      # MW, minutes (14.4 h, synthetic)
    exact_e = 2 * peak * (length_min / 60) / math.pi
    prof = lambda t_m: peak * np.sin(np.pi * t_m / length_min)   # noqa: E731
    rows = []
    lines = [f"half-sine day, peak 58 MW, 14.4 h: exact energy 2 Pmax L / pi = {exact_e:.4f} MWh",
             f"{'h (min)':>8s} {'trapezoid':>11s} {'error':>10s} {'Simpson':>11s} {'error':>10s}"]
    prev = None
    for hmin in (144, 72, 36, 18, 9):
        y = prof(np.arange(0, length_min + 0.5, hmin))
        tr = nm.trapezoid(y, hmin / 60)
        si = nm.simpson(y, hmin / 60)
        rows.append((hmin, f"{abs(tr - exact_e):.3e}", f"{abs(si - exact_e):.3e}"))
        lines.append(f"{hmin:8d} {tr:11.4f} {tr - exact_e:+10.2e} {si:11.4f} {si - exact_e:+10.2e}")
        prev = (hmin, tr) if prev is None else prev
    t72 = nm.trapezoid(prof(np.arange(0, length_min + 0.5, 72)), 72 / 60)
    t36 = nm.trapezoid(prof(np.arange(0, length_min + 0.5, 36)), 36 / 60)
    rich = nm.richardson(t72, t36, 2)
    lines.append(f"halving h divides the trapezoid error by about 4 and Simpson's by about 16")
    lines.append(f"Richardson from h = 72 and 36 min: {rich:.4f} MWh (error {rich - exact_e:+.2e})")
    csv("ch03-quad.csv", "h_min,trap_err,simp_err", rows)
    emit("d_quad", lines)

    tmin = np.arange(0, 24 * 60 + 1)                    # minutes of a clear day
    t_r, t_s = 5.0 * 60, 19.5 * 60
    phase = np.clip((tmin - t_r) / (t_s - t_r), 0.0, 1.0)
    smooth = peak * np.sin(np.pi * phase) ** 1.3

    # discretisation error: clipping seen with 1-minute and with hourly data
    rng = np.random.default_rng(11)
    noise = np.convolve(rng.normal(0, 1, tmin.size), np.ones(9) / 9, mode="same")
    cloudy = np.clip(smooth * (1 + 0.10 * noise / noise.std()), 0, None)
    limit = 50.0
    clip_1 = float(np.sum(np.maximum(cloudy[:-1] - limit, 0)) / 60)
    hour_means = cloudy[:-1].reshape(24, 60).mean(axis=1)
    clip_h = float(np.sum(np.maximum(hour_means - limit, 0)))
    csv("ch03-clip.csv", "minute,p_1min", [(m_, f"{x:.3f}") for m_, x in zip(tmin[600:840], cloudy[600:840])])
    csv("ch03-clip-hourly.csv", "minute,p_hour",
        [(60 * h, f"{hour_means[h]:.3f}") for h in range(10, 14)] + [(840, f"{hour_means[13]:.3f}")])
    emit("d_clip", [
        "synthetic day with 10 % minute-to-minute fluctuations, 50 MW inverter limit",
        f"  energy above the limit from 1-minute data: {clip_1:.3f} MWh",
        f"  energy above the limit from hourly means:  {clip_h:.3f} MWh",
        f"  hourly averaging hides {100 * (1 - clip_h / clip_1):.0f} % of the clipped energy",
    ])

    # ======================================================== D4 conditioning ===========
    th = 1e-8
    naive = 1 - math.cos(th)
    stable = 2 * math.sin(th / 2) ** 2
    s64 = float(np.sum(pv.astype(np.float64)))
    s32 = float(np.sum(pv.astype(np.float32), dtype=np.float32))
    acc32 = np.float32(0.0)
    for x in pv.astype(np.float32):
        acc32 = np.float32(acc32 + x)
    vmat = lambda deg: np.vander(np.linspace(0, 25, 26), deg + 1)   # noqa: E731
    emit("d_condition", [
        f"1 - cos(1e-8): naive {naive:.3e}; stable 2 sin^2(x/2) {stable:.3e} (true 5.0e-17)",
        f"sum of 8760 hourly PV values: float64 {s64:.4f} MWh; numpy float32 {s32:.4f};",
        f"    running float32 sum {float(acc32):.4f} (error {float(acc32) - s64:+.4f} MWh)",
        "condition number of polynomial-fit matrices on 0..25 m/s:",
        *[f"  degree {d:2d}: {nm.condition_number(vmat(d)):.2e}" for d in (1, 3, 6, 10)],
    ])

    # ======================================================== D5 linear programming =====
    price = np.array([30, 28, 27, 27, 28, 32, 40, 48, 45, 38, 33, 30,
                      29, 30, 34, 42, 55, 70, 78, 72, 60, 48, 40, 34], dtype=float)
    n = 24
    eta = math.sqrt(0.86)
    pmax, emin, emax, e0 = 20.0, 4.0, 36.0, 20.0
    # variables: charge c_t (MW, >= 0), discharge d_t (MW, >= 0); SOC_t = e0 + sum(eta c - d/eta)
    cost = np.concatenate([price, -price])              # minimise cost of charging - revenue
    tri = np.tril(np.ones((n, n)))
    a_soc = np.hstack([eta * tri, -tri / eta])
    a_ub = np.vstack([a_soc, -a_soc])
    b_ub = np.concatenate([np.full(n, emax - e0), np.full(n, e0 - emin)])
    a_eq = np.concatenate([eta * np.ones(n), -np.ones(n) / eta])[None, :]
    res = linprog(cost, A_ub=a_ub, b_ub=b_ub, A_eq=a_eq, b_eq=[0.0],
                  bounds=[(0, pmax)] * (2 * n), method="highs")
    c_t, d_t = res.x[:n], res.x[n:]
    soc = e0 + np.cumsum(eta * c_t - d_t / eta)
    revenue = float(price @ (d_t - c_t))
    csv("ch03-lp-battery.csv", "hour,price,charge,discharge,soc",
        [(h, f"{price[h]:.0f}", f"{c_t[h]:.3f}", f"{d_t[h]:.3f}", f"{soc[h]:.3f}") for h in range(n)])
    # plot files: price held over each hour (24 is the end point); stored energy at the
    # hour boundaries (it changes linearly inside an hour at constant power)
    csv("ch03-lp-price.csv", "t,price", [(h, f"{price[min(h, n - 1)]:.0f}") for h in range(n + 1)])
    csv("ch03-lp-soc.csv", "t,soc", [(0, f"{e0:.3f}")] + [(h + 1, f"{soc[h]:.3f}") for h in range(n)])
    emit("d_lp_battery", [
        "one day of price arbitrage, battery 20 MW, usable 4..36 MWh, one-way efficiency 0.927",
        "  prices (fictional units/MWh): " + " ".join(f"{p:.0f}" for p in price),
        f"  linear program: {2 * n} variables, {a_ub.shape[0]} inequality and 1 equality "
        "constraints",
        f"  optimum revenue {revenue:.0f} units; charge hours "
        + ", ".join(str(h) for h in range(n) if c_t[h] > 1e-6)
        + "; discharge hours " + ", ".join(str(h) for h in range(n) if d_t[h] > 1e-6),
        f"  energy charged {c_t.sum():.1f} MWh, discharged {d_t.sum():.1f} MWh; SOC range "
        f"{soc.min():.1f}..{soc.max():.1f} MWh",
    ])

    # two-variable LP: how much PV (x, MWp) and wind (y, MW) to meet an energy target
    yld_pv, yld_w = e_pv / 60, e_w / 60                 # GWh per MW (Plant P yields)
    c = np.array([0.55, 1.25])                          # fictional cost units per MW
    a_ub2 = np.array([[-yld_pv, -yld_w], [1.0, 0.0], [1 / 1.2, 1.0]])
    b_ub2 = np.array([-290.0, 80.0, 120.0])
    r2 = linprog(c, A_ub=a_ub2, b_ub=b_ub2, bounds=[(0, None), (0, None)], method="highs")
    x_opt, y_opt = r2.x
    csv("ch03-lp2.csv", "name,x,y", [("opt", f"{x_opt:.3f}", f"{y_opt:.3f}")])
    emit("d_lp_mix", [
        f"yields: PV {yld_pv:.4f} GWh per MWp, wind {yld_w:.4f} GWh per MW ({cite})",
        "minimise 0.55 x + 1.25 y (fictional cost units) subject to",
        f"  {yld_pv:.3f} x + {yld_w:.3f} y >= 290 GWh;  x <= 80 MWp (land);  x/1.2 + y <= 120 MW",
        f"  optimum x = {x_opt:.1f} MWp, y = {y_opt:.1f} MW, cost {r2.fun:.1f} units",
        f"  cost per GWh: PV {0.55 / yld_pv:.3f}, wind {1.25 / yld_w:.3f} units -> PV first, "
        "up to the land limit",
    ])

    # ======================================================== D6 sensitivity (tornado) ===
    def plant(pr=sc.PR_DC, wl=sc.WIND_LOSS, fv=1.0, fh=1.0, eta_i=sc.ETA_INVERTER):
        p_ = np.asarray(sc.pv_ac_power_mw(ghi * fh, 60, 50, pr, eta_i))
        w_ = np.asarray(sc.wind_power_mw(ws * fv, vs, pk, 12, wl))
        return float(np.minimum(p_ + w_, 100).sum()) / 1000
    base = plant()
    cases = [("wind speed scale +-3 %", plant(fv=0.97), plant(fv=1.03)),
             ("irradiation +-4 %", plant(fh=0.96), plant(fh=1.04)),
             ("wind losses 15 / 9 %", plant(wl=0.15), plant(wl=0.09)),
             ("PR_DC +-5 %", plant(pr=0.85 * 0.95), plant(pr=0.85 * 1.05)),
             ("inverter efficiency 97 / 99 %", plant(eta_i=0.97), plant(eta_i=0.99))]
    cases.sort(key=lambda c_: -(c_[2] - c_[1]))
    # no label column: a "%" in a CSV line starts a comment for pgfplots
    csv("ch03-tornado.csv", "rank,low,high",
        [(i, f"{lo - base:.2f}", f"{hi - base:.2f}") for i, (lab, lo, hi) in enumerate(cases)])
    emit("d_tornado", [f"one-at-a-time sensitivity of exported energy, base {base:.1f} GWh"]
         + [f"  {lab:30s} {lo - base:+6.1f} .. {hi - base:+6.1f} GWh" for lab, lo, hi in cases])


if __name__ == "__main__":
    main()
