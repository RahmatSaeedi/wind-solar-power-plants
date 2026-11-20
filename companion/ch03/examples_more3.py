"""Chapter 3 (third expansion) — series and present value, Fourier series and harmonics,
sampling, frequency response, extreme winds, Markov availability, dynamic programming and
economic cable sizing.

Run from the project root:   python -m companion.ch03.examples_more3
Writes companion/ch03/expected/p_*.txt and diagrams/data/ch03-p-*.csv.
Values marked "assumed" are teaching values; money is in fictional units.
"""
from __future__ import annotations

import math
import sys
import textwrap
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plantp import datapack, dispatch, money, screening as sc  # noqa: E402
from plantp import signals, stats as st  # noqa: E402

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


def series_and_money(pv_gwh: float, wind_gwh: float) -> None:
    weeks = 12
    tw = sum(range(1, weeks + 1))
    q = 0.995
    g25 = money.geometric_sum(1.0, q, 25)
    af = money.annuity_factor(0.07, 25)
    emit("p_series", [
        "arithmetic series: 12 turbines energised one per week (assumed)",
        f"  turbine-weeks in the first 12 weeks: 1 + 2 + ... + 12 = 12 x 13 / 2 = {tw}",
        f"  share of full output during the ramp: {tw} / {weeks * weeks} = {tw / weeks ** 2:.3f}",
        "geometric series: output factor 0.995^t for t = 0..24 (0.5 %/yr degradation)",
        f"  sum = (1 - 0.995^25) / (1 - 0.995) = {g25:.3f}; mean factor {g25 / 25:.4f}",
        f"  infinite sum 1 / (1 - 0.995) = {1 / (1 - q):.0f} (only a bound: plants retire)",
        "present value of 1 unit per year for 25 years at 7 % (assumed):",
        f"  annuity factor (1 - 1.07^-25) / 0.07 = {af:.3f}",
        f"  capital recovery factor 1 / {af:.3f} = {1 / af:.4f} per year",
    ])
    rate, years = 0.07, 25
    capex, opex = 100e6, 2.75e6                     # fictional units (A-037)
    rows, lines = [], []
    for r in (0.05, 0.07, 0.09):
        e_pv = (money.discounted_energy(pv_gwh * 1e3, r, years, 0.005)
                + money.discounted_energy(wind_gwh * 1e3, r, years))
        lc = money.lcoe(capex, opex, e_pv, r, years)
        rows.append((r, e_pv, lc))
    e7 = rows[1][1]
    undiscounted = (capex + opex * years) / (
        sum(pv_gwh * 1e3 * 0.995 ** t for t in range(years)) + wind_gwh * 1e3 * years)
    lines += [
        f"Plant P, S0, data pack 1.0.0: PV {pv_gwh:.1f} GWh (0.5 %/yr degradation), "
        f"wind {wind_gwh:.1f} GWh (none)",
        "capex 100 million units at year 0, opex 2.75 million units/yr (A-037, fictional)",
        f"  discounted energy at 7 %, 25 years: {e7 / 1e6:.3f} TWh "
        f"(= {e7 / ((pv_gwh + wind_gwh) * 1e3):.2f} years of first-year output)",
        f"  PV of opex: 2.75 x {af:.3f} = {opex * af / 1e6:.1f} million units",
    ]
    for r, e_pv, lc in rows:
        lines.append(f"  rate {100 * r:.0f} %: LCOE = {lc:.2f} units/MWh")
    lines.append(f"  wrong (undiscounted) ratio: {undiscounted:.2f} units/MWh, "
                 "flatters the project")
    emit("p_lcoe", lines)
    t = np.arange(1, years + 1)
    e_year = pv_gwh * 0.995 ** (t - 1) + wind_gwh
    csv("ch03-p-discount.csv", "year,energy,discounted",
        [(int(y), f"{e:.2f}", f"{e / 1.07 ** y:.2f}") for y, e in zip(t, e_year)])


def fourier() -> None:
    n = 3600
    th = (np.arange(n) + 0.5) / n * 2 * np.pi
    block = np.where(np.abs(np.sin(th)) > 0.5, np.sign(np.sin(th)), 0.0)
    a = signals.harmonic_amplitudes(block, 60)
    i_rms = signals.rms(block)
    i1 = a[1] / math.sqrt(2)
    lines = ["120-degree block current of a six-pulse diode rectifier, I_d = 1 (assumed)",
             f"  RMS of the block: sqrt(2/3) = {i_rms:.4f}",
             f"  fundamental peak 2 sqrt(3) / pi = {a[1]:.4f} (RMS {i1:.4f})",
             "  harmonic h:  1      3      5      7      9      11     13",
             "  A_h / A_1: " + " ".join(f"{a[h] / a[1]:6.3f}" for h in (1, 3, 5, 7, 9, 11, 13))]
    theory = math.sqrt(i_rms ** 2 - i1 ** 2) / i1
    for hmax in (13, 25, 49):
        lines.append(f"  THD from harmonics up to {hmax:2d}: "
                     f"{100 * signals.thd(a[: hmax + 1]):.1f} %")
    lines.append(f"  THD from the RMS values: sqrt(I^2 - I_1^2) / I_1 = {100 * theory:.1f} %")
    emit("p_fourier", lines)
    deg = np.arange(0, 361, 2)
    thr = np.radians(deg)

    def partial(hmax):
        hs = [h for h in range(1, hmax + 1) if h % 2 == 1 and h % 3 != 0]
        return sum((a[1] / h) * (1 if h % 12 in (1, 11) else -1) * np.sin(h * thr) for h in hs)

    blk = np.where(np.abs(np.sin(thr)) > 0.5 + 1e-9, np.sign(np.sin(thr)), 0.0)
    csv("ch03-p-fourier.csv", "deg,block,h1,h7,h25",
        [(int(d), f"{b:.4f}", f"{x1:.4f}", f"{x7:.4f}", f"{x25:.4f}")
         for d, b, x1, x7, x25 in zip(deg, blk, partial(1), partial(7), partial(25))])


def dft_and_aliasing() -> None:
    n = 64
    t = np.arange(n) / n
    x = (np.sin(2 * np.pi * t) + 0.04 * np.sin(2 * np.pi * 5 * t + 0.5)
         + 0.03 * np.sin(2 * np.pi * 7 * t - 0.8))
    a = signals.harmonic_amplitudes(x, 9)
    lines = ["inverter current: 1.0 pu at 50 Hz + 0.04 pu 5th + 0.03 pu 7th (A-040, assumed)",
             "  64 samples over one cycle (3.2 kHz); DFT peak amplitudes (pu):",
             "  h:  " + "  ".join(f"{h:5d}" for h in range(1, 10)),
             "  A:  " + "  ".join(f"{a[h]:5.3f}" for h in range(1, 10)),
             f"  THD = sqrt(0.04^2 + 0.03^2) / 1 = {100 * signals.thd(a):.1f} %"]
    m = 70                                           # 1.09 cycles: not a whole period
    xw = np.sin(2 * np.pi * np.arange(m) / n)
    spec = 2 * np.abs(np.fft.rfft(xw)) / m
    top = np.argsort(spec)[::-1][:3]
    lines.append("  window of 70 samples (1.09 cycles): bins are 45.7 Hz apart, 50 Hz falls")
    lines.append("    between bins; largest bins " + ", ".join(
        f"{k * 3200 / m:.0f} Hz: {spec[k]:.3f}" for k in sorted(top)) + " (leakage)")
    lines.append("aliasing: a sinusoid of f sampled at fs appears at |f - fs round(f/fs)|")
    for f, fs in ((50, 60), (50, 1000), (1250, 1000), (650, 1000)):
        lines.append(f"  f = {f:5d} Hz, fs = {fs:5d} Hz -> appears at "
                     f"{signals.alias_frequency(f, fs):5.0f} Hz")
    lines.append("  rule: fs > 2 f_max, and a low-pass filter before the converter")
    emit("p_dft", lines)


def frequency_response() -> None:
    d0, v = 3.0, 8.0                                 # distance constant m (assumed)
    tau_a = d0 / v
    lines = [f"cup anemometer as a first-order lag, distance constant {d0:.0f} m (assumed):",
             f"  at 8 m/s tau = 3 / 8 = {tau_a:.3f} s"]
    for f in (0.05, 0.2, 0.5, 1.0, 2.0):
        lines.append(f"  gust at {f:4.2f} Hz: amplitude ratio "
                     f"{float(signals.first_order_gain(f, tau_a)):.3f}, lag "
                     f"{float(signals.first_order_lag_deg(f, tau_a)):4.1f} deg")
    tau_c = 3.0
    f_day = 1 / 24
    g = float(signals.first_order_gain(f_day, tau_c))
    lag = float(signals.first_order_lag_deg(f_day, tau_c))
    lines += ["buried cable, tau = 3 h (A-033 variant), daily load cycle f = 1/24 per hour:",
              f"  amplitude ratio {g:.3f}; lag {lag:.1f} deg = {lag / 360 * 24:.2f} h",
              "  (the temperature swing is damped and the peak comes later than the load)"]
    emit("p_bode", lines)
    ft = np.logspace(-3, 1, 81)
    csv("ch03-p-bode.csv", "ftau,gain",
        [(f"{x:.5f}", f"{float(signals.first_order_gain(x, 1.0)):.5f}") for x in ft])


def extremes() -> None:
    rng = np.random.default_rng(20260111)
    maxima = rng.gumbel(26.0, 2.5, 30)               # synthetic, A-036
    mu_m, be_m = st.gumbel_fit_moments(maxima)
    mu_l, be_l = st.gumbel_fit_lsq(maxima)
    lines = ["30 annual maxima of the 10-minute mean wind at hub height (synthetic, A-036)",
             f"  mean {maxima.mean():.2f} m/s, std {maxima.std(ddof=1):.2f} m/s, "
             f"largest {maxima.max():.2f} m/s",
             f"  Gumbel by moments: mu = {mu_m:.2f}, beta = {be_m:.2f} m/s",
             f"  Gumbel by line on the Gumbel plot: mu = {mu_l:.2f}, beta = {be_l:.2f} m/s"]
    for t in (10, 50, 100):
        lines.append(f"  {t:3d}-year value: moments {st.return_level(mu_m, be_m, t):.1f} m/s, "
                     f"plot {st.return_level(mu_l, be_l, t):.1f} m/s")
    lines.append(f"  chance the 50-year value is exceeded in a 25-year life: "
                 f"{100 * st.prob_exceed_in_life(50, 25):.1f} %")
    for size in (10, 30):
        boot = []
        for _ in range(2000):
            s = rng.choice(maxima, size)
            boot.append(st.return_level(*st.gumbel_fit_moments(s), 50))
        lo, hi = np.percentile(boot, [5, 95])
        lines.append(f"  50-year value from {size} years: 90 % bootstrap range "
                     f"{lo:.1f} .. {hi:.1f} m/s")
    emit("p_gumbel", lines)
    xs, y = st.gumbel_plot_positions(maxima)
    csv("ch03-p-gumbel.csv", "y,x", [(f"{a:.4f}", f"{b:.3f}") for a, b in zip(y, xs)])
    yl = np.array([-1.5, 5.0])
    csv("ch03-p-gumbel-fit.csv", "y,x", [(f"{a:.2f}", f"{mu_l + be_l * a:.3f}") for a in yl])


def markov() -> None:
    mtbf, mttr = 2000.0, 60.0                        # hours (A-039, assumed)
    lam, mu = 1 / mtbf, 1 / mttr
    p = np.array([[1 - lam, lam], [mu, 1 - mu]])
    pi = st.markov_stationary(p)
    rng = np.random.default_rng(20260112)
    n_t, n_h = 12, 10 * 8760
    up = np.ones(n_t, dtype=bool)
    count = np.empty(n_h, dtype=int)
    for h in range(n_h):
        r = rng.random(n_t)
        up = np.where(up, r >= lam, r < mu)
        count[h] = up.sum()
    a_sim = count.mean() / n_t
    a = st.availability(mtbf, mttr)
    binom2 = 1 - a ** 12 - 12 * a ** 11 * (1 - a)
    stay24 = np.linalg.matrix_power(p, 24)[1, 1]
    lines = [f"one turbine: MTBF {mtbf:.0f} h, MTTR {mttr:.0f} h (A-039, assumed)",
             f"  transition matrix per hour: [[{1 - lam:.4f} {lam:.4f}] [{mu:.4f} {1 - mu:.4f}]]",
             f"  stationary distribution (pi P = pi): up {pi[0]:.4f}, down {pi[1]:.4f}",
             f"  MTBF / (MTBF + MTTR) = {a:.4f}",
             f"12 turbines simulated for 10 years, hourly: availability {a_sim:.4f}",
             f"  hours with 2 or more down: simulated {100 * np.mean(count <= 10):.1f} %, "
             f"binomial {100 * binom2:.1f} %",
             f"  a turbine down now is still down 24 h later with probability {stay24:.3f}",
             f"    (an independent hourly draw would give {1 - a:.3f})"]
    emit("p_markov", lines)


def dynamic_programming(price) -> None:
    eta = math.sqrt(0.86)
    lines = ["battery 20 MW, usable 4..36 MWh, one-way efficiency 0.927, start/end 20 MWh",
             "  same fictional prices as the linear program of section D (LP: 1584.4 units)",
             "  grid step (MWh)  states  revenue (units)  transitions per hour"]
    paths = {}
    for step in (4.0, 2.0, 1.0, 0.5, 0.25):
        r = dispatch.dp_arbitrage(price, 20.0, 4.0, 36.0, 20.0, eta, step)
        paths[step] = r.energy
        lines.append(f"  {step:15.2f} {r.states:7d} {r.revenue:16.1f} {r.states ** 2:21d}")
    r = dispatch.dp_arbitrage(price, 20.0, 4.0, 36.0, 20.0, eta, 0.25)
    ch = [h for h in range(24) if r.power[h] < -1e-9]
    dis = [h for h in range(24) if r.power[h] > 1e-9]
    lines += [f"  step 0.25: charge hours {', '.join(map(str, ch))}; "
              f"discharge hours {', '.join(map(str, dis))}",
              f"  two batteries on the 0.25 grid: {129 ** 2} states, "
              f"{129 ** 4:.1e} transitions per hour"]
    emit("p_dp", lines)
    csv("ch03-p-dp.csv", "t,dp4,dp05",
        [(t, f"{paths[4.0][t]:.3f}", f"{paths[0.5][t]:.3f}") for t in range(25)])


def kelvin(hourly) -> None:
    curve = datapack.load_power_curve()
    vs, pk = curve["wind_speed_ms"].to_numpy(), curve["power_kw"].to_numpy()
    pv = np.asarray(sc.pv_ac_power_mw(hourly["ghi_wm2"], 60, 50))
    wind = np.asarray(sc.wind_power_mw(hourly["ws_100m_ms"].to_numpy(), vs, pk, 12))
    p_feeder = np.minimum(pv + wind, 100.0) / 2               # MW, half the plant
    i = p_feeder * 1e6 / (math.sqrt(3) * 33e3 * 0.95)          # A
    length = 5.0                                               # km
    r240 = 0.125                                               # ohm/km (A-032)
    c0, c1, value, rate, years = 60e3, 300.0, 40.0, 0.07, 25   # A-038 (fictional)
    af = money.annuity_factor(rate, years)
    s_i2 = float(np.sum(i ** 2))
    e_feeder = float(p_feeder.sum())

    def loss_mwh(area):
        return 3 * s_i2 * (r240 * 240 / area * length) / 1e6

    lines = ["one 33 kV feeder, 5 km, half the plant output, pf 0.95, data pack 1.0.0, S0",
             "  R = 0.125 ohm/km at 240 mm2 (A-032), scaled as 1/area (assumption)",
             "  cable cost 5 km x (60 000 + 300 A) units; losses valued 40 units/MWh;",
             f"  25 years at 7 % (annuity factor {af:.3f}); all money fictional (A-038)",
             "  area   capex     loss    loss    PV of losses   total",
             "  (mm2)  (k)      (MWh/y) (%)     (k)            (k)"]
    best = None
    rows = []
    for area in (240, 300, 400, 500, 630):
        cap = length * (c0 + c1 * area)
        lm = loss_mwh(area)
        pvl = lm * value * af
        tot = cap + pvl
        rows.append((area, cap, pvl, tot))
        if best is None or tot < best[1]:
            best = (area, tot)
        lines.append(f"  {area:5d} {cap / 1e3:7.0f} {lm:9.0f} {100 * lm / e_feeder:6.2f}"
                     f" {pvl / 1e3:12.0f} {tot / 1e3:9.0f}")
    par = 2 * length * (c0 + c1 * 150)
    lines.append(f"  2 x 150 mm2 in parallel: capex {par / 1e3:.0f} k, losses as 300 mm2 "
                 "-> dominated")
    k_loss = loss_mwh(240) * 240 * value * af              # PV of losses = k_loss / A
    a_star = math.sqrt(k_loss / (length * c1))
    lines.append(f"  Kelvin optimum (d total / dA = 0): A* = sqrt(k / (L c1)) = {a_star:.0f} mm2")
    lines.append(f"  cheapest standard size: {best[0]} mm2; thermal minimum stays 240 mm2")
    emit("p_kelvin", lines)
    areas = np.arange(150, 801, 10)
    csv("ch03-p-kelvin.csv", "area,capex,losses,total",
        [(int(a_), f"{length * (c0 + c1 * a_) / 1e6:.4f}", f"{k_loss / a_ / 1e6:.4f}",
          f"{(length * (c0 + c1 * a_) + k_loss / a_) / 1e6:.4f}") for a_ in areas])
    csv("ch03-p-kelvin-pts.csv", "area,total",
        [(a_, f"{tot / 1e6:.4f}") for a_, _, _, tot in rows])


def main() -> None:
    EXPECTED.mkdir(exist_ok=True)
    hourly = datapack.load_hourly()
    curve = datapack.load_power_curve()
    vs, pk = curve["wind_speed_ms"].to_numpy(), curve["power_kw"].to_numpy()
    pv = np.asarray(sc.pv_ac_power_mw(hourly["ghi_wm2"], 60, 50))
    wind = np.asarray(sc.wind_power_mw(hourly["ws_100m_ms"].to_numpy(), vs, pk, 12))
    series_and_money(pv.sum() / 1e3, wind.sum() / 1e3)
    fourier()
    dft_and_aliasing()
    frequency_response()
    extremes()
    markov()
    price = np.array([30, 28, 27, 27, 28, 32, 40, 48, 45, 38, 33, 30,
                      29, 30, 34, 42, 55, 70, 78, 72, 60, 48, 40, 34], dtype=float)
    dynamic_programming(price)
    kelvin(hourly)


if __name__ == "__main__":
    main()
