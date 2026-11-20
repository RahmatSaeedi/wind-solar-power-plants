"""Chapter 3 — numerical answers of the end-of-chapter problems (exr-ch03-N).

Run from the project root:   python -m companion.ch03.solutions
Writes companion/ch03/expected/solutions.txt (lines of at most 78 characters).
"""
from __future__ import annotations

import cmath
import math
import sys
import textwrap
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plantp import datapack, numerics as nm, phasors as ph, screening as sc  # noqa: E402
from plantp import solar, stats as st, uncertainty as un  # noqa: E402
from plantp import dispatch, geo, money, signals  # noqa: E402

OUT = Path(__file__).resolve().parent / "expected" / "solutions.txt"
LINES: list[str] = []


def p(num, *items) -> None:
    LINES.extend(textwrap.wrap(f"P{num:02d}: " + "; ".join(items), 78, subsequent_indent="     "))


def third_expansion(hourly, vs, pk) -> None:
    """Problems 53-69: series, money, signals, extremes, Markov, DP, Kelvin."""
    p(53, f"1 + ... + 60 = {60 * 61 // 2}",
      f"10 terms of 0.95^k: {money.geometric_sum(1, 0.95, 10):.3f}",
      f"infinite: {1 / (1 - 0.95):.0f}")
    amps = np.array([0, 100.0, 0, 0, 0, 6, 0, 4, 0, 0, 0, 3])
    p(54, f"RMS = sqrt(sum A^2 / 2) = {math.sqrt(np.sum(amps ** 2) / 2):.2f} A",
      f"THD = {100 * signals.thd(amps):.2f} %")
    p(55, f"20-year value in 20 years: {100 * st.prob_exceed_in_life(20, 20):.1f} %",
      "in any one year: 5.0 %")
    i_base = 100e6 / (math.sqrt(3) * 33e3)
    p(56, f"I = 1 / 0.10 = 10 pu; base {i_base:.1f} A; {10 * i_base / 1e3:.2f} kA")
    p(57, f"AF(8 %, 20) = {money.annuity_factor(0.08, 20):.3f}",
      f"CRF(8 %, 20) = {money.capital_recovery(0.08, 20):.4f}",
      f"50 million over 15 y at 6 %: {50 * money.capital_recovery(0.06, 15):.3f} million/yr")
    p(58, ", ".join(f"{h * 50} Hz -> {signals.alias_frequency(h * 50, 1000):.0f} Hz"
                    for h in (3, 13, 21, 39)), "50th harmonic needs fs > 5000 Hz")
    tau = 2.0
    p(59, f"f_c = 1/(2 pi 2) = {1 / (2 * math.pi * tau):.4f} Hz",
      *[f"{f} Hz: ratio {float(signals.first_order_gain(f, tau)):.3f}, "
        f"lag {float(signals.first_order_lag_deg(f, tau)):.1f} deg" for f in (0.05, 0.5)])
    lam, mu = 1 / 1000, 1 / 100
    pm = np.array([[1 - lam, lam], [mu, 1 - mu]])
    p(60, f"A = {100 * st.availability(1000, 100):.2f} %",
      f"still down after 24 h: {np.linalg.matrix_power(pm, 24)[1, 1]:.3f}",
      f"failures per year {8760 * st.availability(1000, 100) / 1000:.2f}")

    curve_pv = np.asarray(sc.pv_ac_power_mw(hourly["ghi_wm2"], 60, 50))
    wind = np.asarray(sc.wind_power_mw(hourly["ws_100m_ms"].to_numpy(), vs, pk, 12))
    pv_e, w_e = curve_pv.sum() / 1e3, wind.sum() / 1e3
    rate, yrs = 0.07, 25

    def lc(capex=100e6, opex=2.75e6, scale=1.0):
        e = scale * (money.discounted_energy(pv_e * 1e3, rate, yrs, 0.005)
                     + money.discounted_energy(w_e * 1e3, rate, yrs))
        return money.lcoe(capex, opex, e, rate, yrs)
    base = lc()
    p(61, f"base {base:.2f}", f"capex +10 %: {lc(capex=110e6):.2f}",
      f"opex +20 %: {lc(opex=3.3e6):.2f}", f"energy -5 %: {lc(scale=0.95):.2f} units/MWh")
    export = np.minimum(curve_pv + wind, 100.0)
    lost = np.maximum(export - 80.0, 0.0)
    p(62, f"cap 80 MW: {lost.sum() / 1e3:.2f} GWh curtailed in {int((lost > 0).sum())} h",
      f"{100 * lost.sum() / export.sum():.2f} % of export")
    price = np.array([30, 28, 27, 27, 28, 32, 40, 48, 45, 38, 33, 30,
                      29, 30, 34, 42, 55, 70, 78, 72, 60, 48, 40, 34], dtype=float)
    r = dispatch.dp_arbitrage(price, 20, 4, 36, 20, math.sqrt(0.86), 0.25, wear=5.0)
    p(63, f"DP with wear 5/MWh (0.25 MWh grid): net {r.revenue:.1f} units",
      f"discharged {r.power[r.power > 0].sum():.1f} MWh (LP of P47: 1288)")
    p(64, f"west sectors 240..300 hold {11.0 + 30.8 + 26.9:.1f} % of energy",
      f"farm loss 3 % x 0.687 = {3 * 0.687:.2f} %")
    k240 = 1057e3 * 240 * 2                 # PV of losses x area, doubled value
    a_star = math.sqrt(k240 / (5 * 300))
    tot = {a: 5 * (60e3 + 300 * a) + k240 / a for a in (400, 500, 630)}
    p(65, f"loss value 80/MWh: A* = {a_star:.0f} mm2",
      ", ".join(f"{a}: {t / 1e3:.0f} k" for a, t in tot.items()))
    ws_all = hourly["ws_100m_ms"].to_numpy()
    vpos = ws_all[ws_all > 0]
    lv = np.log(vpos)

    def nll(kk, cc):
        return float(-np.sum(np.log(kk / cc) + (kk - 1) * (lv - math.log(cc))
                             - (vpos / cc) ** kk)) / vpos.size

    def descend(step):
        x = np.array([1.5, 6.0])
        for it in range(3000):
            g = np.array([(nll(x[0] + 1e-6, x[1]) - nll(x[0] - 1e-6, x[1])) / 2e-6,
                          (nll(x[0], x[1] + 1e-6) - nll(x[0], x[1] - 1e-6)) / 2e-6])
            if not np.all(np.isfinite(g)):
                return f"step {step}: diverges after {it} steps"
            if np.linalg.norm(g) < 1e-4:
                return f"step {step}: {it} steps"
            x = x - step * g
            if x.min() <= 0:
                return f"step {step}: leaves the valid region after {it + 1} steps"
        return f"step {step}: no convergence in 3000 steps"
    hh = 1e-4
    k0, c0 = 1.5, 6.0
    f_kk = (nll(k0 + hh, c0) - 2 * nll(k0, c0) + nll(k0 - hh, c0)) / hh ** 2
    f_cc = (nll(k0, c0 + hh) - 2 * nll(k0, c0) + nll(k0, c0 - hh)) / hh ** 2
    f_kc = (nll(k0 + hh, c0 + hh) - nll(k0 + hh, c0 - hh) - nll(k0 - hh, c0 + hh)
            + nll(k0 - hh, c0 - hh)) / (4 * hh * hh)
    lmax0 = float(np.linalg.eigvalsh([[f_kk, f_kc], [f_kc, f_cc]])[-1])
    p(66, *[descend(s) for s in (1.0, 2.0, 4.0, 6.0)],
      f"largest curvature at the start {lmax0:.3f}: step limit there {2 / lmax0:.1f}")
    rng = np.random.default_rng(20260111)
    maxima = rng.gumbel(26.0, 2.5, 30)
    x10 = st.return_level(*st.gumbel_fit_moments(maxima[:10]), 50)
    x30 = st.return_level(*st.gumbel_fit_moments(maxima), 50)
    p(67, f"50-year value from the first 10 maxima {x10:.1f} m/s, from all 30 {x30:.1f} m/s")
    n_days = 73.5 ** 2 / (7.0 ** 2 - 6.0 ** 2 - 2.0 ** 2)
    p(68, f"sqrt((73.5/sqrt N)^2 + 6^2 + 2^2) < 7 needs N > {n_days:.0f} days "
      f"({n_days / 30.4:.0f} months)")

    p(70, f"1 arc-minute of latitude: {float(geo.haversine_m(34, 0, 34 + 1 / 60, 0)):.1f} m",
      f"1 deg of longitude at 60 N: {float(geo.haversine_m(60, 0, 60, 1)) / 1e3:.2f} km",
      f"0.001 deg each way at 34 N: {float(geo.haversine_m(34, 0, 34.001, 0.001)):.1f} m")
    p(71, f"prior 0.02, sensitivity 0.9, false alarms 0.01: "
      f"P(fault | alarm) = {st.bayes_posterior(0.02, 0.9, 0.01):.3f}")
    alpha, dz = 1e-6, 0.05
    p(72, f"dt_max = 0.5 dz^2 / alpha = {0.5 * dz ** 2 / alpha:.0f} s",
      f"daily damping depth sqrt(2 alpha / omega) = "
      f"{math.sqrt(2 * alpha / (2 * math.pi / 86400)):.3f} m",
      f"annual / daily = sqrt(365) = {math.sqrt(365):.1f}")
    p(73, f"bearing T3 -> T1 = {geo.bearing_deg(34.0061, 0.0040, 34.0, 0.0):.1f} deg",
      f"T1-T3 = {float(geo.haversine_m(34.0, 0.0, 34.0061, 0.0040)) / 150:.2f} D")
    from companion.ch03 import lab_spectrum as ls            # noqa: E402
    fs = 10_000.0
    t200 = np.arange(2000) / fs
    a_fix = ls.harmonic_peaks(ls.signal(t200, 50.2), fs, 50.0, (1, 5, 7))
    n_s = int(round(10 / 50.2 * fs))
    a_syn = ls.harmonic_peaks(ls.signal(np.arange(n_s) / fs, 50.2), fs, 50.2, (1, 5, 7))
    a9 = 0.9
    p(75, f"series 3 x 0.99: {st.series_availability([0.99] * 3):.4f}",
      f"parallel 2 x 0.9: {st.parallel_availability([0.9, 0.9]):.4f}",
      f"2-out-of-3 of 0.9: {3 * a9 ** 2 * (1 - a9) + a9 ** 3:.4f}")
    th_err = math.radians(-10.0)
    d0, q0 = math.cos(math.radians(-20)), math.sin(math.radians(-20))
    d1, q1 = ph.park(d0, q0, th_err)
    p(76, f"true d {d0:.3f}, q {q0:.3f}; frame 10 deg behind: d {float(d1):.3f}, "
      f"q {float(q1):.3f}")
    a_pair = st.parallel_availability([0.995, 0.995])
    for ccf in (0.0, 0.0005):
        a_p = st.series_availability([0.999, a_pair, 1 - ccf, 0.999, 0.997])
        p(77, f"common-cause unavailability {ccf}: path A {a_p:.5f}, "
          f"loss {(1 - a_p) * 289.8:.2f} GWh/yr")
    p(78, f"plain MC samples to match LHS n = 50 on the mean: 50 x (1.818 / 0.152)^2 = "
      f"{50 * (1.818 / 0.152) ** 2:.0f}")
    p(74, "grid 50.2 Hz, fixed 200 ms rectangular: A5 "
      f"{a_fix[1]:.4f}, A7 {a_fix[2]:.4f}",
      f"synchronised ({n_s} samples): A5 {a_syn[1]:.4f}, A7 {a_syn[2]:.4f}")


def main() -> None:
    hourly = datapack.load_hourly()
    curve = datapack.load_power_curve()
    vs, pk = curve["wind_speed_ms"].to_numpy(), curve["power_kw"].to_numpy()
    ws = hourly["ws_100m_ms"].to_numpy()

    p(1, f"(2.5e3)^3 = {2.5e3 ** 3:.4e}", f"log10(2.5e3) = {math.log10(2.5e3):.4f}")
    p(2, f"45 deg = {math.radians(45):.4f} rad", f"sin = cos = {math.sin(math.radians(45)):.4f}")
    z = (2 + 3j) * (1 - 1j)
    p(6, f"(2+3j)(1-j) = {z.real:.0f}{z.imag:+.0f}j", f"|z| = {abs(z):.4f}",
      f"angle {math.degrees(cmath.phase(z)):.2f} deg")
    d = np.array([5.0, 7, 7, 9, 12])
    p(8, f"mean {d.mean():.2f}", f"median {np.median(d):.0f}", f"s = {d.std(ddof=1):.4f}")

    for dec in (10.0, -15.0):
        p(11, f"declination {dec:+.0f}: noon elevation {90 - 34 + dec:.0f} deg")
    p(12, f"shadow of 2 m at 30 deg: 2 / tan 30 = {2 / math.tan(math.radians(30)):.4f} m")
    a, b = np.array([1.0, 1, 0]), np.array([0.0, 1, 1])
    p(13, f"cos theta = {a @ b / (np.linalg.norm(a) * np.linalg.norm(b)):.4f}",
      f"theta = {math.degrees(math.acos(a @ b / 2)):.1f} deg")
    p(15, "f = x e^-x: f' = (1 - x) e^-x = 0 at x = 1", f"f(1) = {math.exp(-1):.4f} (maximum)")
    A = [[2, 1, -1], [-3, -1, 2], [-2, 1, 2]]
    bvec = [8, -11, -3]
    p(16, "solution " + ", ".join(f"{x:.4f}" for x in nm.solve_gauss(A, bvec)))
    fit = st.linear_fit([0, 1, 2, 3], [1, 2, 2, 4])
    p(17, f"slope {fit.slope:.2f}", f"intercept {fit.intercept:.2f}")
    ev = np.linalg.eigvalsh([[-2.0, 1.0], [1.0, -2.0]])
    p(18, "eigenvalues " + ", ".join(f"{x:.0f}" for x in ev),
      "time constants " + ", ".join(f"{-1 / x:.4f}" for x in ev))
    s = ph.complex_power(ph.polar(230, 0), ph.polar(10, -36.87))
    p(19, f"S = {s.real:.1f} + j{s.imag:.1f} VA", f"|S| = {abs(s):.0f} VA")
    _, y = nm.euler(lambda t, y_: -y_, 1.0, 0, 1.0, 0.5)
    p(20, f"Euler: {y[1]:.4f}, {y[2]:.4f}", f"exact e^-1 = {math.exp(-1):.4f}")
    p(21, f"mean 8 Gamma(1.5) = {st.weibull_mean(2, 8):.3f} m/s",
      f"P(v < 4) = {float(st.weibull_cdf(4, 2, 8)):.4f}")
    p(22, f"n_eff = 1000 x 0.1/1.9 = {1000 * 0.1 / 1.9:.1f}")

    el_w = 90 - 34 + float(solar.declination(355))
    for tilt in (30.0,):
        h = 4.6 * math.sin(math.radians(tilt))
        pitch = 4.6 * math.cos(math.radians(tilt)) + h / math.tan(math.radians(el_w))
        p(23, f"tilt {tilt:.0f}: h {h:.3f} m, pitch {pitch:.3f} m, GCR {4.6 / pitch:.3f}")
    p(24, "equinox noon: theta = latitude - tilt = 34 - 25 = 9 deg",
      f"cos 9 = {math.cos(math.radians(9)):.4f}")
    target = 45e3 / 12 / (1 - sc.WIND_LOSS)
    r = nm.bisection(lambda v: float(np.interp(v, vs, pk)) - target, 3, 13, tol=1e-8)
    p(25, f"per turbine {target:.1f} kW", f"v = {r.root:.4f} m/s ({r.iterations} halvings)")
    zc = complex(1.25, 1.10)
    i_mag = 30e6 / (math.sqrt(3) * 33e3 * 0.95)
    i = ph.polar(i_mag, -math.degrees(math.acos(0.95)))
    vs_ = ph.polar(33e3 / math.sqrt(3), 0) + zc * i
    drop = (abs(vs_) - 33e3 / math.sqrt(3)) * math.sqrt(3)
    p(26, f"10 km: drop {drop:.0f} V ({100 * drop / 33e3:.2f} %)",
      f"loss {3 * i_mag ** 2 * 1.25 / 1e3:.0f} kW ({100 * 3 * i_mag ** 2 * 1.25 / 30e6:.2f} %)")
    i0, i1, i2 = ph.symmetrical_components(ph.polar(100, 0), ph.polar(100, -120), ph.polar(80, 120))
    p(27, f"|I0| = {abs(i0):.2f}, |I1| = {abs(i1):.2f}, |I2| = {abs(i2):.2f} A",
      f"unbalance {100 * abs(i2) / abs(i1):.1f} %")
    p(28, f"40 (1 - e^(-1/3)) = {40 * (1 - math.exp(-1 / 3)):.2f} K")
    p(29, f"(20 - 4) x 0.927 / 5 = {(20 - 4) * math.sqrt(0.86) / 5:.3f} h at 5 MW")
    vg = np.linspace(0, 30, 3001)
    e_w = float(np.trapezoid(np.interp(vg, vs, pk, right=0) * st.weibull_pdf(vg, 2.0, 8.0), vg)) \
        * 8760 * 12 * 0.88 / 1e6
    p(30, f"Weibull k 2.0, c 8.0: {e_w:.1f} GWh (fit k 2.11: 191.4 GWh)")
    p(31, f"1.0403 x 9 - 0.0089 = {1.0403 * 9 - 0.0089:.3f} m/s")
    p(32, f"z = (24.28 - 7.103) / 3.529 = {(24.28 - 7.103) / 3.529:.2f} -> flagged, but real")
    p(33, f"3.04 / 4^2 = {3.04 / 16:.2f} MWh (table: 0.19)")
    p(34, "range roughly halves: about -4.7 .. +4.6 GWh")

    vals = 1e9 + np.array([4.0, 7.0, 13.0, 16.0])
    naive = float(np.mean(vals ** 2) - np.mean(vals) ** 2)
    two_pass = float(np.mean((vals - vals.mean()) ** 2))
    p(44, f"variance of 1e9 + [4, 7, 13, 16]: naive E[x^2] - E[x]^2 = {naive:.1f}",
      f"two-pass {two_pass:.2f} (true 22.50)")

    def wind_energy(k, c):
        return float(np.trapezoid(np.interp(vg, vs, pk, right=0) * st.weibull_pdf(vg, k, c), vg)) \
            * 8760 * 12 * 0.88 / 1e6
    kk = np.linspace(1.4, 2.9, 31)          # wide enough for +-5 standard deviations
    cc = np.linspace(6.8, 9.2, 25)
    grid = np.array([[wind_energy(a_, b_) for b_ in cc] for a_ in kk])
    from scipy.interpolate import RegularGridInterpolator
    interp = RegularGridInterpolator((kk, cc), grid)
    mc = un.monte_carlo(lambda k_, c_: interp(np.column_stack([k_, c_])),
                        {"k_": ("normal", 2.114, 0.10), "c_": ("normal", 8.017, 0.20)}, n=50_000)
    p(46, f"k 2.114 +- 0.10, c 8.017 +- 0.20: mean {mc.mean:.1f} GWh, std {mc.std:.1f} GWh",
      f"P90 {np.quantile(mc.samples, 0.10):.1f} GWh")

    price = np.array([30, 28, 27, 27, 28, 32, 40, 48, 45, 38, 33, 30,
                      29, 30, 34, 42, 55, 70, 78, 72, 60, 48, 40, 34], dtype=float)
    eta = math.sqrt(0.86)
    n = 24
    tri = np.tril(np.ones((n, n)))
    a_soc = np.hstack([eta * tri, -tri / eta])
    for wear in (0.0, 5.0):
        res = linprog(np.concatenate([price, -price + wear]), A_ub=np.vstack([a_soc, -a_soc]),
                      b_ub=np.concatenate([np.full(n, 16.0), np.full(n, 16.0)]),
                      A_eq=np.concatenate([eta * np.ones(n), -np.ones(n) / eta])[None, :],
                      b_eq=[0.0], bounds=[(0, 20)] * (2 * n), method="highs")
        dis = res.x[n:].sum()
        p(47, f"wear cost {wear:.0f}/MWh: net {-res.fun:.0f} units, discharged {dis:.1f} MWh")

    day = datapack.load_hourly("day_summer")
    pv = np.asarray(sc.pv_ac_power_mw(day["ghi_wm2"], 60, 50))
    wind = np.asarray(sc.wind_power_mw(day["ws_100m_ms"], vs, pk, 12))
    i_a = 0.5 * np.minimum(pv + wind, 100) * 1e6 / (math.sqrt(3) * 33e3 * 0.95)
    kth = 40.0 / 552.5 ** 2

    def rhs(t, y_):
        return (kth * i_a[min(int(t // 3600), 23)] ** 2 - y_) / 21600.0
    _, y6 = nm.rk4(rhs, 0.0, 0.0, 86400.0, 60.0)
    p(48, f"tau 6 h: maximum rise {y6.max():.1f} K (steady state 42.9 K)")

    pv_y = np.asarray(sc.pv_ac_power_mw(hourly["ghi_wm2"], 60, 50)).reshape(365, 24).sum(1)
    w_y = np.asarray(sc.wind_power_mw(ws, vs, pk, 12)).reshape(365, 24).sum(1)
    rng = np.random.default_rng(3)
    rs = []
    for _ in range(1000):
        idx = rng.integers(0, 365, 365)
        rs.append(st.pearson(pv_y[idx], w_y[idx]))
    lo, hi = np.quantile(rs, [0.025, 0.975])
    p(49, f"daily r = {st.pearson(pv_y, w_y):+.3f}", f"bootstrap 95 % interval {lo:+.3f} .. {hi:+.3f}")

    x = np.linspace(0, 25, 60)
    yv = np.interp(x, vs, pk)
    v6 = np.vander(x, 7)
    c_ne = np.linalg.solve(v6.T @ v6, v6.T @ yv)
    c_ls, *_ = np.linalg.lstsq(v6, yv, rcond=None)
    p(51, f"degree-6 fit: cond(A) {np.linalg.cond(v6):.2e}, cond(A^T A) {np.linalg.cond(v6.T @ v6):.2e}",
      f"rms residual normal eqs {np.sqrt(np.mean((v6 @ c_ne - yv) ** 2)):.1f} kW, "
      f"lstsq {np.sqrt(np.mean((v6 @ c_ls - yv) ** 2)):.1f} kW")

    third_expansion(hourly, vs, pk)

    text = "\n".join(LINES) + "\n"
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(text)


if __name__ == "__main__":
    main()
