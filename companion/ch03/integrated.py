"""Chapter 3 — the three integrated Plant P examples.

Run from the project root:   python -m companion.ch03.integrated
  int_energy   annual wind energy four ways (functions, distributions, integrals)
  int_cable    a 33 kV cable through the summer subset day: phasors, losses and a
               thermal ODE solved with RK4 against the hour-by-hour steady state
  int_battery  battery arbitrage revenue when prices are uncertain: linear
               programming inside a Monte Carlo loop
Writes companion/ch03/expected/int_*.txt and diagrams/data/ch03-int-*.csv.
All prices, cable and thermal values are fictional teaching values (A-032, A-033, A-035).
"""
from __future__ import annotations

import math
import sys
import textwrap
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plantp import datapack, numerics as nm, screening as sc, stats as st  # noqa: E402

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


def arbitrage(price, pmax=20.0, emin=4.0, emax=36.0, e0=20.0, eta=math.sqrt(0.86)):
    """Daily price arbitrage as a linear program; returns (revenue, charge, discharge)."""
    n = len(price)
    tri = np.tril(np.ones((n, n)))
    a_soc = np.hstack([eta * tri, -tri / eta])
    res = linprog(np.concatenate([price, -price]),
                  A_ub=np.vstack([a_soc, -a_soc]),
                  b_ub=np.concatenate([np.full(n, emax - e0), np.full(n, e0 - emin)]),
                  A_eq=np.concatenate([eta * np.ones(n), -np.ones(n) / eta])[None, :],
                  b_eq=[0.0], bounds=[(0, pmax)] * (2 * n), method="highs")
    return -res.fun, res.x[:n], res.x[n:]


def main() -> None:
    EXPECTED.mkdir(exist_ok=True)
    hourly = datapack.load_hourly()
    curve = datapack.load_power_curve()
    vs, pk = curve["wind_speed_ms"].to_numpy(), curve["power_kw"].to_numpy()
    ws = hourly["ws_100m_ms"].to_numpy()
    factor = 12 * (1 - sc.WIND_LOSS) / 1e6       # kW per turbine -> GWh per hour of the farm

    # ---- 1. annual wind energy four ways -------------------------------------------
    e_mean = float(np.interp(ws.mean(), vs, pk)) * 8760 * factor
    k, c = st.weibull_fit_mle(ws)
    vg = np.linspace(0, 30, 3001)
    e_weib = float(np.trapezoid(np.interp(vg, vs, pk, right=0) * st.weibull_pdf(vg, k, c), vg)) \
        * 8760 * factor
    e_hour = float(np.interp(ws, vs, pk).sum()) * factor
    edges = np.concatenate([[vs[0] - 0.25], (vs[:-1] + vs[1:]) / 2, [vs[-1] + 0.25]])
    hours, _ = np.histogram(ws, bins=edges)
    e_bin = float(np.sum(hours * pk)) * factor
    emit("int_energy", [
        "annual energy of the wind farm (data pack 1.0.0, S0), four mathematical routes:",
        f"  1 mean speed into the power curve           {e_mean:7.1f} GWh  (function of a mean)",
        f"  2 Weibull k = {k:.3f}, c = {c:.3f}: 8760 x integral  {e_weib:7.1f} GWh  (expectation)",
        f"  3 binned frequency x power at bin centres  {e_bin:7.1f} GWh  (quadrature on bins)",
        f"  4 hour by hour (time series)                {e_hour:7.1f} GWh  (sum = integral)",
        f"  routes 2-4 agree within {100 * (max(e_weib, e_bin, e_hour) / min(e_weib, e_bin, e_hour) - 1):.1f} %; "
        f"route 1 is {100 * (e_mean / e_hour - 1):+.0f} % (mean of a nonlinear function)",
    ])

    # ---- 2. a 33 kV cable through one day ------------------------------------------
    day = datapack.load_hourly("day_summer")
    pv = np.asarray(sc.pv_ac_power_mw(day["ghi_wm2"], 60, 50))
    wind = np.asarray(sc.wind_power_mw(day["ws_100m_ms"], vs, pk, 12))
    p_mw = 0.5 * np.minimum(pv + wind, 100.0)    # one of two feeders, half the output each
    r_ph, pf = 0.625, 0.95                       # ohm per phase for 5 km (A-032)
    i_a = p_mw * 1e6 / (math.sqrt(3) * 33e3 * pf)
    loss_kw = 3 * i_a ** 2 * r_ph / 1e3
    i_ref, rise_ref = 552.5, 40.0                # A, K at steady state (A-033)
    kth = rise_ref / i_ref ** 2                  # K per A^2 at steady state
    steady = kth * i_a ** 2

    def simulate(tau):
        def rhs(t, y):
            h = min(int(t // 3600), 23)
            return (kth * i_a[h] ** 2 - y) / tau
        return nm.rk4(rhs, 0.0, 0.0, 24 * 3600.0, 60.0)
    t, y_air = simulate(1800.0)                  # cable in air (A-033)
    _, y_buried = simulate(10800.0)              # buried cable, slower (assumed)
    with open(DATA / "ch03-int-cable.csv", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("t_h,rise_air,rise_buried,rise_steady\n")
        for tk, ya, yb in zip(t[::10], y_air[::10], y_buried[::10]):
            h = min(int(tk // 3600), 23)
            fh.write(f"{tk / 3600:.3f},{ya:.3f},{yb:.3f},{steady[h]:.3f}\n")
    i_peak = int(np.argmax(i_a))
    emit("int_cable", [
        "one of two 33 kV collector feeders (half the plant output each, assumed), 5 km,",
        "    Z = 0.625 + j0.550 ohm per phase (A-032), summer subset day, pf 0.95",
        f"  peak hour {i_peak}: {p_mw[i_peak]:.1f} MW, I = {i_a[i_peak]:.0f} A, loss "
        f"{loss_kw[i_peak]:.0f} kW",
        f"  daily loss = sum of 3 I^2 R x 1 h = {loss_kw.sum() / 1000:.2f} MWh "
        f"({100 * loss_kw.sum() / 1000 / p_mw.sum():.2f} % of {p_mw.sum():.0f} MWh)",
        f"  with the daily MEAN current instead: "
        f"{24 * 3 * i_a.mean() ** 2 * r_ph / 1e6:.2f} MWh (too low: mean of a square)",
        "  temperature rise, thermal ODE with 40 K at 552.5 A (A-033), RK4, dt 60 s:",
        f"    hour-by-hour steady state: maximum {steady.max():.1f} K",
        f"    tau 0.5 h (in air): maximum {y_air.max():.1f} K at {t[np.argmax(y_air)] / 3600:.1f} h",
        f"    tau 3 h (buried):   maximum {y_buried.max():.1f} K at "
        f"{t[np.argmax(y_buried)] / 3600:.1f} h",
    ])

    # ---- 3. arbitrage revenue with uncertain prices ----------------------------------
    base = np.array([30, 28, 27, 27, 28, 32, 40, 48, 45, 38, 33, 30,
                     29, 30, 34, 42, 55, 70, 78, 72, 60, 48, 40, 34], dtype=float)
    r0, *_ = arbitrage(base)
    rng = np.random.default_rng(20260107)
    revenues = []
    for _ in range(300):
        level = math.exp(rng.normal(0, 0.15))                     # day-to-day level
        shape = np.exp(rng.normal(0, 0.10, 24))                   # hour-to-hour noise
        revenues.append(arbitrage(base * level * shape)[0])
    rev = np.array(revenues)
    with open(DATA / "ch03-int-revenue.csv", "w", encoding="utf-8", newline="\n") as fh:
        cnt, edg = np.histogram(rev, bins=24)
        fh.write("revenue,density\n")
        for e_, c_ in zip(edg[:-1], cnt / (rev.size * (edg[1] - edg[0]))):
            fh.write(f"{e_:.1f},{c_:.6f}\n")
        fh.write(f"{edg[-1]:.1f},0\n")
    emit("int_battery", [
        "daily arbitrage of the 20 MW / 4..36 MWh battery (fictional prices, A-035)",
        f"  base price profile: revenue {r0:.0f} units (perfect foresight)",
        "  300 random days: level x exp(N(0, 0.15)), each hour x exp(N(0, 0.10))",
        f"  revenue: mean {rev.mean():.0f}, std {rev.std(ddof=1):.0f}, P10 {np.quantile(rev, 0.10):.0f}, "
        f"P90 {np.quantile(rev, 0.90):.0f} units",
        f"  mean of the random-day revenues is {100 * (rev.mean() / r0 - 1):+.0f} % from the "
        "base-day revenue:",
        "    noisier prices give a battery more to exploit (convexity of the optimum)",
        "  every value assumes perfect foresight: an UPPER bound, not a forecast",
    ])


if __name__ == "__main__":
    main()
