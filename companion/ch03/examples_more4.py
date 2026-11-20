"""Chapter 3 (fourth expansion) — geographic coordinates, Bayes' theorem for alarms, heat
diffusion in soil by finite differences, and Newton's method in two dimensions.

Run from the project root:   python -m companion.ch03.examples_more4
Writes companion/ch03/expected/q_*.txt and diagrams/data/ch03-q-*.csv.
Plant P is not geolocated (A-001): longitudes are offsets from a reference meridian.
Values marked "assumed" are teaching values.
"""
from __future__ import annotations

import math
import sys
import textwrap
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plantp import datapack, geo, numerics as nm, stats as st  # noqa: E402

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


def geodesy() -> None:
    lat0 = 34.0
    pts = {"T1": (34.0000, 0.0000), "T2": (34.0000, 0.0081), "T3": (34.0061, 0.0040),
           "mast": (33.9985, -0.0060), "substation": (33.9850, 0.0200)}    # A-041
    lines = ["points as (latitude deg N, longitude offset from the reference meridian, deg)",
             "  (fictional, A-041; Plant P is not geolocated)"]
    for name, (la, dl) in pts.items():
        e, n = geo.enu_offsets_m(lat0, 0.0, la, dl)
        lines.append(f"  {name:10s} {la:8.4f} N  lambda0 {dl:+.4f}  ->  east {float(e):7.1f} m, "
                     f"north {float(n):7.1f} m")
    lines.append("distances and bearings (haversine on a sphere, R = 6371.0 km):")
    for a, b in (("T1", "T2"), ("T1", "T3"), ("T1", "substation"), ("mast", "T1")):
        (la1, lo1), (la2, lo2) = pts[a], pts[b]
        d = float(geo.haversine_m(la1, lo1, la2, lo2))
        e1, n1 = geo.enu_offsets_m(lat0, 0.0, la1, lo1)
        e2, n2 = geo.enu_offsets_m(lat0, 0.0, la2, lo2)
        flat = math.hypot(float(e2 - e1), float(n2 - n1))
        lines.append(f"  {a}-{b}: {d:7.1f} m (flat patch {flat:7.1f} m), bearing "
                     f"{geo.bearing_deg(la1, lo1, la2, lo2):5.1f} deg, {d / 150:.2f} D")
    deg_lat = float(geo.haversine_m(lat0, 0, lat0 + 1, 0)) / 1e3
    deg_lon = float(geo.haversine_m(lat0, 0, lat0, 1)) / 1e3
    naive = 0.0081 * deg_lat * 1e3
    true = float(geo.haversine_m(34.0, 0.0, 34.0, 0.0081))
    lines += [f"one degree of latitude {deg_lat:.2f} km; one degree of longitude at 34 N "
              f"{deg_lon:.2f} km (x cos 34 = {math.cos(math.radians(34)):.4f})",
              f"  T1-T2 with 'degrees x 111 km': {naive:.0f} m instead of {true:.0f} m "
              f"({100 * (naive / true - 1):+.1f} %)",
              "  the T1-T2 row (bearing 90/270 deg) lies within 13 deg of the prevailing",
              "    wind axis (from 283 deg): T2 sits in the wake of T1 at about 5 D"]
    emit("q_geodesy", lines)


def bayes() -> None:
    prior, sens, fa = 0.02, 0.90, 0.05                 # A-042, assumed
    post = st.bayes_posterior(prior, sens, fa)
    sens2, fa2 = 0.80, 0.03
    post2 = st.bayes_posterior(post, sens2, fa2)
    n = 1000
    lines = ["gearbox condition monitoring, per turbine-month (A-042, assumed):",
             f"  prior P(fault) = {prior}; vibration alarm: sensitivity {sens}, "
             f"false alarms {fa}",
             f"  out of {n} turbine-months: {prior * n:.0f} with a fault -> "
             f"{prior * n * sens:.0f} alarms; {(1 - prior) * n:.0f} healthy -> "
             f"{(1 - prior) * n * fa:.0f} false alarms",
             f"  P(fault | alarm) = {prior * sens:.3f} / ({prior * sens:.3f} + "
             f"{(1 - prior) * fa:.3f}) = {post:.3f}",
             f"  P(no fault | no alarm) = {(1 - prior) * (1 - fa) / ((1 - prior) * (1 - fa) + prior * (1 - sens)):.4f}",
             f"a second, independent test (oil debris: sensitivity {sens2}, false alarms "
             f"{fa2}) after an alarm:",
             f"  prior is now {post:.3f}; P(fault | both positive) = {post2:.3f}",
             f"12 turbines: expected false alarms per month {12 * (1 - prior) * fa:.2f}, "
             f"per year {12 * 12 * (1 - prior) * fa:.1f}"]
    for p_ in (0.005, 0.02, 0.10):
        lines.append(f"  prior {p_:5.3f}: P(fault | alarm) = {st.bayes_posterior(p_, sens, fa):.3f}")
    emit("q_bayes", lines)


def soil_heat() -> None:
    alpha = 0.5e-6                                     # m2/s, soil (A-043, assumed)
    w_day = 2 * math.pi / 86400.0
    d_day = math.sqrt(2 * alpha / w_day)
    dz, dt = 0.02, 300.0
    r = alpha * dt / dz ** 2
    z = np.arange(0.0, 1.0 + dz / 2, dz)
    u = np.full(z.size, 20.0)
    steps_day = int(86400 / dt)
    record = {0.0: [], 0.1: [], 0.2: [], 0.4: []}
    idx = {k: int(round(k / dz)) for k in record}
    t_rec = []
    for k in range(1, 10 * steps_day + 1):
        t = k * dt
        u = nm.heat_explicit_step(u, r, 20.0 + 10.0 * math.sin(w_day * t))
        if k > 8 * steps_day:                          # keep the last two days
            t_rec.append(t / 3600.0 - 192.0)
            for key in record:
                record[key].append(u[idx[key]])
    lines = [f"soil diffusivity {alpha:.1e} m2/s (A-043, assumed); surface 20 C +- 10 K "
             "daily sine",
             f"  explicit scheme: dz = {dz} m, dt = {dt:.0f} s, r = alpha dt / dz^2 = {r:.3f} "
             "(stable if <= 0.5)",
             f"  damping depth of the daily wave d = sqrt(2 alpha / omega) = {d_day:.3f} m",
             "  depth   amplitude: numeric  analytic   lag (h): numeric  analytic"]
    for key in (0.1, 0.2, 0.4):
        ser = np.array(record[key])
        amp = (ser.max() - ser.min()) / 2
        t_peak = t_rec[int(np.argmax(ser))]
        surf = np.array(record[0.0])
        lag = (t_peak - t_rec[int(np.argmax(surf))]) % 24
        lines.append(f"  {key:4.1f} m {amp:16.2f} K {10 * math.exp(-key / d_day):8.2f} K "
                     f"{lag:14.1f} {key / d_day / w_day / 3600:9.1f}")
    w_yr = 2 * math.pi / (365 * 86400.0)
    d_yr = math.sqrt(2 * alpha / w_yr)
    lines += [f"annual wave (+- 12 K, assumed): damping depth {d_yr:.2f} m",
              f"  at 0.8 m (cable depth, A-043): amplitude {12 * math.exp(-0.8 / d_yr):.1f} K, "
              f"lag {0.8 / d_yr / w_yr / 86400:.0f} days; daily wave there "
              f"{10 * math.exp(-0.8 / d_day):.4f} K"]
    u_bad = np.full(11, 20.0)
    u_bad[5] = 21.0
    for _ in range(60):                                # r = 0.6 without the guard
        u_bad[1:-1] = u_bad[1:-1] + 0.6 * (u_bad[2:] - 2 * u_bad[1:-1] + u_bad[:-2])
    lines.append(f"  r = 0.6 (guard removed), 60 steps: max |u - 20| = "
                 f"{np.max(np.abs(u_bad - 20)):.1e} K (unstable)")
    emit("q_soil", lines)
    csv("ch03-q-soil.csv", "t,z0,z1,z2,z4",
        [(f"{t:.3f}", *(f"{record[k][i]:.3f}" for k in (0.0, 0.1, 0.2, 0.4)))
         for i, t in enumerate(t_rec) if i % 3 == 0])


def newton_2d() -> None:
    ws = datapack.load_hourly()["ws_100m_ms"].to_numpy()
    v = ws[ws > 0]
    lv = np.log(v)

    def nll(x):
        k, c = x
        return float(-np.sum(np.log(k / c) + (k - 1) * (lv - math.log(c)) - (v / c) ** k)) / v.size

    x, it, hist = nm.newton_minimise(nll, [1.5, 6.0], h=1e-4, tol=1e-7)
    k_ref, c_ref = st.weibull_fit_mle(ws)
    lines = ["Newton's method on the Weibull negative log-likelihood",
             "  (start k 1.5, c 6.0 m/s; finite-difference gradient and Hessian)",
             "  iteration  |gradient|"]
    for i, g in enumerate(hist):
        lines.append(f"  {i:9d}  {g:.2e}")
    lines += [f"  result k = {x[0]:.4f}, c = {x[1]:.4f} m/s after {it} Newton steps",
              f"  closed-form MLE: k = {k_ref:.4f}, c = {c_ref:.4f}; gradient descent needed "
              "227 steps (step 0.5) to reach 1e-4",
              "  each Newton step costs a Hessian (here 2 x 2) and a linear solve"]
    emit("q_newton2d", lines)


def reliability() -> None:
    from plantp import screening as sc
    hourly = datapack.load_hourly()
    curve = datapack.load_power_curve()
    pv = np.asarray(sc.pv_ac_power_mw(hourly["ghi_wm2"], 60, 50))
    wind = np.asarray(sc.wind_power_mw(hourly["ws_100m_ms"].to_numpy(),
                                       curve["wind_speed_ms"].to_numpy(),
                                       curve["power_kw"].to_numpy(), 12))
    export = np.minimum(pv + wind, 100.0)
    e_total = export.sum() / 1e3                                     # GWh
    a_brk, a_tr, a_line = 0.999, 0.995, 0.997                        # A-044, assumed
    path = [a_brk, a_tr, a_brk, a_line]
    a_single = st.series_availability(path)
    a_tr2 = st.parallel_availability([a_tr, a_tr])
    a_dual = st.series_availability([a_brk, a_tr2, a_brk, a_line])
    above50 = np.maximum(export - 50.0, 0.0).sum() / 1e3
    p_one_down = 2 * a_tr * (1 - a_tr)
    p_both_down = (1 - a_tr) ** 2
    lost_half = (p_one_down * above50 + p_both_down * e_total) * a_brk ** 2 * a_line
    lost_half += (1 - a_brk ** 2 * a_line) * e_total
    lines = ["export path of Plant P: breaker - transformer - breaker - line, in series",
             f"  breaker {a_brk}, transformer {a_tr}, line {a_line} (A-044, assumed)",
             f"  one 100 MVA transformer: A = {a_single:.5f}; expected loss "
             f"{(1 - a_single) * e_total:.2f} GWh/yr of {e_total:.1f}",
             f"  two 100 % transformers in parallel: transformer pair A = {a_tr2:.6f}; path "
             f"A = {a_dual:.5f}; loss {(1 - a_dual) * e_total:.2f} GWh/yr",
             f"  two 50 % transformers: with one out, only export above 50 MW is lost "
             f"({above50:.1f} GWh/yr of {e_total:.1f})",
             f"    expected loss {lost_half:.2f} GWh/yr",
             "  assumes independent failures and losses independent of the weather"]
    emit("q_rbd", lines)


def lhs() -> None:
    from scipy.stats import norm
    from plantp import uncertainty as un

    def energy(dv, dl, dg, dp):
        return 192.5 * (1 + dv) ** 2.0 * (1 + dl) + 97.3 * (1 + dg) * (1 + dp)

    sig = np.array([0.03, 0.02, 0.04, 0.02])                         # A-045, assumed
    rng = np.random.default_rng(20260113)
    big = rng.standard_normal((400_000, 4)) * sig
    ref = energy(*big.T)
    ref_mean, ref_p90 = ref.mean(), np.quantile(ref, 0.10)
    lines = ["annual energy with four uncertain factors (A-045, assumed):",
             "  E = 192.5 (1 + dv)^2 (1 + dl) + 97.3 (1 + dg)(1 + dp) GWh",
             "  std: wind speed 3 %, wind losses 2 %, irradiance 4 %, PV losses 2 %",
             f"  reference (400 000 samples): mean {ref_mean:.2f} GWh, P90 {ref_p90:.2f} GWh",
             f"  200 repeated studies of n samples: spread (std) of the estimates",
             "      n   mean: plain MC   LHS     P90: plain MC   LHS"]
    for n in (50, 200, 1000):
        m_mc, m_lh, p_mc, p_lh = [], [], [], []
        for _ in range(200):
            x = rng.standard_normal((n, 4)) * sig
            e = energy(*x.T)
            m_mc.append(e.mean())
            p_mc.append(np.quantile(e, 0.10))
            u = un.latin_hypercube(n, 4, rng)
            e2 = energy(*(norm.ppf(u) * sig).T)
            m_lh.append(e2.mean())
            p_lh.append(np.quantile(e2, 0.10))
        lines.append(f"  {n:5d} {np.std(m_mc):13.3f} {np.std(m_lh):7.3f} "
                     f"{np.std(p_mc):14.3f} {np.std(p_lh):7.3f}")
    lines.append("  (GWh) LHS shrinks the spread of the mean most; tails gain less")
    emit("q_lhs", lines)


def park_frame() -> None:
    from plantp import phasors as ph
    w = 2 * math.pi * 50.0
    t = np.arange(0, 0.04 + 1e-9, 0.04 / 400)
    phi = math.radians(-20.0)                          # current lags by 20 deg (assumed)

    def three(amp, f_hz, ph0, seq=1):
        wt = 2 * math.pi * f_hz * t + ph0
        return (amp * np.cos(wt), amp * np.cos(wt - seq * 2 * math.pi / 3),
                amp * np.cos(wt + seq * 2 * math.pi / 3))

    cases = []
    a, b, c = three(1.0, 50.0, phi)
    cases.append(("balanced", a, b, c))
    a2, b2, c2 = three(0.1, 50.0, 0.0, seq=-1)
    cases.append(("10 % negative seq.", a + a2, b + b2, c + c2))
    a3, b3, c3 = three(1.0, 50.2, phi)
    cases.append(("grid at 50.2 Hz", a3, b3, c3))
    lines = ["Park transform of a 1.0 pu current lagging 20 deg; frame angle 2 pi 50 t",
             "  case                 d mean  q mean   d range       q range"]
    keep = None
    for name, xa, xb, xc in cases:
        al, be, _ = ph.clarke(xa, xb, xc)
        d, q = ph.park(al, be, w * t)
        lines.append(f"  {name:19s} {d.mean():6.3f} {q.mean():7.3f}   "
                     f"{d.min():5.3f}..{d.max():5.3f}  {q.min():6.3f}..{q.max():6.3f}")
        if name.startswith("10 %"):
            keep = (d, q)
    lines += ["  balanced: d = cos(-20 deg) = 0.940, q = sin(-20 deg) = -0.342, constant",
              "  negative sequence: a 100 Hz ripple of amplitude 0.1 rides on d and q",
              "  frequency error: d and q drift slowly (0.2 Hz) instead of staying put",
              "  (40 ms shown); a phase-locked loop makes theta follow the grid (ch. 9)"]
    emit("q_park", lines)
    csv("ch03-q-park.csv", "ms,d,q",
        [(f"{1000 * tt:.2f}", f"{dd:.4f}", f"{qq:.4f}")
         for tt, dd, qq in zip(t, *keep)])


def main() -> None:
    EXPECTED.mkdir(exist_ok=True)
    park_frame()
    geodesy()
    bayes()
    soil_heat()
    newton_2d()
    reliability()
    lhs()


if __name__ == "__main__":
    main()
