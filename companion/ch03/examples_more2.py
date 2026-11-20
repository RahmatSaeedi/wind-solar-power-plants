"""Chapter 3 (second expansion) — foundations, fault currents, wind-rose statistics, sampling,
gradient descent, integer choices and duration curves.

Run from the project root:   python -m companion.ch03.examples_more2
Writes companion/ch03/expected/n_*.txt and diagrams/data/ch03-n-*.csv.
Values marked "assumed" are teaching values.
"""
from __future__ import annotations

import math
import sys
import textwrap
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plantp import datapack, screening as sc, stats as st  # noqa: E402

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


def main() -> None:
    EXPECTED.mkdir(exist_ok=True)
    hourly = datapack.load_hourly()
    curve = datapack.load_power_curve()
    vs, pk = curve["wind_speed_ms"].to_numpy(), curve["power_kw"].to_numpy()
    ws = hourly["ws_100m_ms"].to_numpy()
    wd = hourly["wd_100m_deg"].to_numpy()

    # ---- foundations: rearranging, quadratic, compounding, decibels ------------------
    p_kw, rho, cp = 3000.0, 1.055, 0.45
    v_req = (2 * p_kw * 1e3 / (rho * math.pi * 75 ** 2 * cp)) ** (1 / 3)
    v_ocv, r_int, p_load = 800.0, 0.05, 1.0e6
    disc = v_ocv ** 2 - 4 * r_int * p_load
    i_small = (v_ocv - math.sqrt(disc)) / (2 * r_int)
    i_large = (v_ocv + math.sqrt(disc)) / (2 * r_int)
    emit("n_algebra", [
        "rearranging P = 1/2 rho A v^3 Cp for v:  v = (2 P / (rho A Cp))^(1/3)",
        f"  3 MW from a 150 m rotor at rho 1.055 kg/m3 and Cp 0.45 (assumed): v = {v_req:.2f} m/s",
        "a battery string: open-circuit 800 V, internal resistance 0.05 ohm (assumed)",
        "  delivering P = (V - I R) I = 1 MW  ->  R I^2 - V I + P = 0",
        f"  I = (V -+ sqrt(V^2 - 4 R P)) / (2 R): {i_small:.1f} A or {i_large:.1f} A",
        f"  the small root is the operating point: terminal voltage {v_ocv - i_small * r_int:.1f} V,"
        f" efficiency {100 * (1 - i_small * r_int / v_ocv):.1f} %",
        f"  no real root above P_max = V^2/(4R) = {v_ocv ** 2 / (4 * r_int) / 1e6:.1f} MW "
        "(the discriminant turns negative)",
    ])
    yrs = 25
    emit("n_growth", [
        "PV module degradation 0.5 % per year (assumed):",
        f"  compound: 0.995^25 = {0.995 ** yrs:.4f}; linear 1 - 25 x 0.005 = {1 - yrs * 0.005:.4f}",
        f"  mean output factor over 25 years (compound): "
        f"{np.mean([0.995 ** k for k in range(yrs)]):.4f}",
        f"  years to lose 10 % (compound): ln(0.9)/ln(0.995) = {math.log(0.9) / math.log(0.995):.1f}",
        "BESS capacity fade 2 % per year (A-011), linear vs compound after 10 years:",
        f"  linear {1 - 10 * 0.02:.3f}; compound 0.98^10 = {0.98 ** 10:.4f}",
        "cost escalation 3 % per year (assumed): price doubles in "
        f"ln 2 / ln 1.03 = {math.log(2) / math.log(1.03):.1f} years (rule of 72: {72 / 3:.0f})",
    ])
    lw = 105.0
    emit("n_decibel", [
        "decibels: L = 10 log10(W / W_ref); levels of independent sources add as powers",
        f"  two equal sources: +10 log10(2) = +{10 * math.log10(2):.2f} dB; twelve: "
        f"+{10 * math.log10(12):.2f} dB",
        f"  12 turbines of sound power level 105 dB (assumed): {lw + 10 * math.log10(12):.1f} dB",
        f"  85 dB + 85 dB = {10 * math.log10(2 * 10 ** 8.5):.1f} dB; 85 dB + 75 dB = "
        f"{10 * math.log10(10 ** 8.5 + 10 ** 7.5):.1f} dB (the quieter adds 0.4 dB)",
        f"  free-field spreading from a point source: -20 log10(r2/r1); from 100 to 500 m "
        f"{-20 * math.log10(5):.1f} dB",
        "  real noise assessment uses standardised methods and local limits (chapter 33)",
    ])

    # ---- fault currents from the bus impedance matrix --------------------------------
    z_line = {(0, 1): complex(0.010, 0.080), (0, 2): complex(0.012, 0.100), (1, 2): complex(0.006, 0.050)}
    z_grid = complex(0.0, 0.080)                   # grid source impedance at bus 1 (assumed, pu)
    y = np.zeros((3, 3), dtype=complex)
    for (i, j), z in z_line.items():
        y[i, i] += 1 / z
        y[j, j] += 1 / z
        y[i, j] -= 1 / z
        y[j, i] -= 1 / z
    y[0, 0] += 1 / z_grid
    zbus = np.linalg.inv(y)
    i_base = 100e6 / (math.sqrt(3) * 33e3)
    lines = ["three buses on a 33 kV, 100 MVA base; grid behind j0.080 pu at bus 1 (assumed)",
             "  bus  Z_kk (pu)              fault current |1/Z_kk| (pu)   (kA)"]
    for k in range(3):
        zk = zbus[k, k]
        lines.append(f"  {k + 1:3d}  {zk.real:.5f} + j{zk.imag:.5f}   {abs(1 / zk):10.2f}"
                     f"          {abs(1 / zk) * i_base / 1e3:6.1f}")
    lines.append("  three-phase bolted fault, prefault 1.0 pu, plant contribution neglected")
    lines.append("  the diagonal of Z_bus = Y_bus^-1 is the Thevenin impedance seen at each bus")
    emit("n_fault", lines)

    # ---- wind rose statistics -------------------------------------------------------
    edges = np.arange(-15, 360, 30)
    sector = ((wd + 15) // 30).astype(int) % 12
    p_turb = np.interp(ws, vs, pk)
    rows = []
    lines = ["12 sectors of 30 deg (centre, FROM direction): frequency, mean speed, energy share"]
    for s in range(12):
        m = sector == s
        rows.append((s * 30, f"{100 * m.mean():.2f}", f"{ws[m].mean() if m.any() else 0:.2f}",
                     f"{100 * p_turb[m].sum() / p_turb.sum():.2f}"))
        lines.append(f"  {s * 30:3d} deg: {100 * m.mean():5.1f} % of hours, mean "
                     f"{ws[m].mean() if m.any() else 0:5.2f} m/s, {100 * p_turb[m].sum() / p_turb.sum():5.1f} % "
                     "of energy")
    csv("ch03-n-rose.csv", "sector,freq,mean,energy", rows)
    top = max(rows, key=lambda r_: float(r_[3]))
    lines.append(f"  most energetic sector: {top[0]} deg ({top[3]} % of energy)")
    vx = np.mean(np.sin(np.radians(wd)) * ws)
    vy = np.mean(np.cos(np.radians(wd)) * ws)
    lines.append(f"  speed-weighted vector mean direction: {math.degrees(math.atan2(vx, vy)) % 360:.0f} deg")
    emit("n_rose", lines)

    # ---- sampling a Weibull distribution by inverse transform ---------------------------
    k, c = st.weibull_fit_mle(ws)
    rng = np.random.default_rng(20260109)
    u = rng.random(100_000)
    v_s = c * (-np.log(1 - u)) ** (1 / k)
    emit("n_inverse", [
        f"inverse-transform sampling of the fitted Weibull (k = {k:.3f}, c = {c:.3f} m/s):",
        "  U uniform on (0, 1)  ->  v = c (-ln(1 - U))^(1/k)",
        f"  100,000 samples: mean {v_s.mean():.3f} m/s (theory {st.weibull_mean(k, c):.3f}), "
        f"mean of v^3 {np.mean(v_s ** 3):.1f} (theory {st.weibull_mean_cube(k, c):.1f})",
        f"  energy from the samples: {np.interp(v_s, vs, pk).mean() * 8760 * 12 * 0.88 / 1e6:.1f} GWh/yr",
        "  independent samples have no autocorrelation: fine for annual sums, wrong for",
        "    anything that depends on the order of hours (batteries, ramps, curtailment)",
    ])

    # ---- gradient descent on the Weibull negative log-likelihood ----------------------
    vpos = ws[ws > 0]
    lv = np.log(vpos)

    def nll(kk, cc):
        return float(-np.sum(np.log(kk / cc) + (kk - 1) * (lv - math.log(cc)) - (vpos / cc) ** kk)) / vpos.size

    x = np.array([1.5, 6.0])
    step = 0.5
    hist = []
    for it in range(400):
        f0 = nll(*x)
        g = np.array([(nll(x[0] + 1e-6, x[1]) - nll(x[0] - 1e-6, x[1])) / 2e-6,
                      (nll(x[0], x[1] + 1e-6) - nll(x[0], x[1] - 1e-6)) / 2e-6])
        if it in (0, 1, 2, 5, 10, 25, 50, 100, 200, 399):
            hist.append((it, x[0], x[1], f0, float(np.linalg.norm(g))))
        x = x - step * g
    hs = 1e-4
    f_kk = (nll(k + hs, c) - 2 * nll(k, c) + nll(k - hs, c)) / hs ** 2
    f_cc = (nll(k, c + hs) - 2 * nll(k, c) + nll(k, c - hs)) / hs ** 2
    f_kc = (nll(k + hs, c + hs) - nll(k + hs, c - hs) - nll(k - hs, c + hs)
            + nll(k - hs, c - hs)) / (4 * hs * hs)
    lam_h = np.linalg.eigvalsh([[f_kk, f_kc], [f_kc, f_cc]])

    def steps_to(scale, tol=1e-4, nmax=3000):
        xs = np.array([1.5, 6.0 / scale])
        for it_ in range(nmax):
            def fs(a, b):
                return nll(a, b * scale)
            gs = np.array([(fs(xs[0] + 1e-6, xs[1]) - fs(xs[0] - 1e-6, xs[1])) / 2e-6,
                           (fs(xs[0], xs[1] + 1e-6) - fs(xs[0], xs[1] - 1e-6)) / 2e-6])
            if np.linalg.norm(gs) < tol:
                return f"{it_} steps"
            xs = xs - step * gs
        return "no convergence (oscillates)"
    emit("n_gradient", [
        "minimise the mean negative log-likelihood of a Weibull fit by gradient descent",
        "    (step 0.5, start k = 1.5, c = 6.0 m/s, numerical gradient)",
        "  iteration      k        c      NLL     |gradient|",
        *[f"  {i:9d} {a:7.4f} {b:8.4f} {f_:8.5f} {gn:10.2e}" for i, a, b, f_, gn in hist],
        f"  closed-form MLE (section C): k = {k:.4f}, c = {c:.4f}",
        f"  curvature at the optimum (Hessian eigenvalues): {lam_h[0]:.3f} and {lam_h[1]:.3f},"
        f" ratio {lam_h[1] / lam_h[0]:.1f}: a narrow valley",
        f"  stable only if step < 2 / {lam_h[1]:.3f} = {2 / lam_h[1]:.1f}",
        "  steps to |gradient| < 1e-4 with step 0.5: "
        + "; ".join(f"c/{s:g}: {steps_to(float(s))}" for s in (1, 3, 8)),
    ])

    # ---- integer choices ------------------------------------------------------------
    p_str = 26 * 550.0
    n_exact = 60e6 / p_str
    lines = [f"strings of 26 x 550 W = {p_str / 1e3:.1f} kWp; 60 MWp needs {n_exact:.2f} strings",
             "  combiner boxes take 24 strings each (A-014); options near 60 MWp:"]
    for boxes in (174, 175, 176):
        strings = boxes * 24
        lines.append(f"    {boxes} boxes x 24 = {strings} strings = {strings * p_str / 1e6:.3f} MWp")
    inv = 4.2                                       # MW per inverter (assumed)
    for n_inv in (11, 12, 13):
        lines.append(f"  {n_inv} inverters of 4.2 MW = {n_inv * inv:.1f} MW AC, DC/AC "
                     f"{175 * 24 * p_str / 1e6 / (n_inv * inv):.3f}")
    lines.append("  integers break the smooth optimum: round, then check every constraint again")
    emit("n_integer", lines)

    # ---- duration curve ---------------------------------------------------------------
    pv = np.asarray(sc.pv_ac_power_mw(hourly["ghi_wm2"], 60, 50))
    wind = np.asarray(sc.wind_power_mw(ws, vs, pk, 12))
    exp_ = np.minimum(pv + wind, 100.0)
    srt = np.sort(exp_)[::-1]
    emit("n_duration", [
        "duration curve: hourly export sorted from largest to smallest (data pack 1.0.0, S0)",
        f"  area under the curve = energy: {srt.sum() / 1000:.1f} GWh (same as the time series)",
        f"  hours above 50 MW: {int((exp_ > 50).sum())}; above 80 MW: {int((exp_ > 80).sum())}; "
        f"below 5 MW: {int((exp_ < 5).sum())}",
        f"  median hourly export {np.median(exp_):.1f} MW; 10 % of hours exceed "
        f"{np.quantile(exp_, 0.9):.1f} MW",
        f"  energy delivered in the top 1000 hours: {srt[:1000].sum() / 1000:.1f} GWh "
        f"({100 * srt[:1000].sum() / srt.sum():.0f} %)",
    ])


if __name__ == "__main__":
    main()
