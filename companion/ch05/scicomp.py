"""Chapter 5, section B - the scientific-computing workflow: arrays, tables,
time series, solvers, plots, configuration and recorded versions.

Run from the project root:   python -m companion.ch05.scicomp
Data: Plant P Reference Data Pack 1.1.0, scenario S0 (synthetic).
"""
from __future__ import annotations

import sys

from companion.ch05.basics import capture
from companion.ch05.common import HERE, emit


# [start: numpy]
def numpy_demo():
    import numpy as np
    from plantp import datapack
    ghi = datapack.load_hourly()["ghi_wm2"].to_numpy()   # 8760 values
    p_dc = 60.0 * ghi / 1000.0 * 0.85                    # whole year at once
    p_ac = np.minimum(p_dc * 0.98, 50.0)                 # element by element
    print("shape", ghi.shape, " dtype", ghi.dtype)
    print(f"energy {p_ac.sum():,.0f} MWh;  hours at the limit",
          int((p_ac >= 50.0).sum()))
    total = 0.0
    for g in ghi:                                        # the same, slowly
        total += min(60.0 * g / 1000.0 * 0.85 * 0.98, 50.0)
    print("loop and array agree:", bool(np.isclose(total, p_ac.sum())))
    day = p_ac.reshape(365, 24)                          # days x hours
    print("best hour of the mean day:", int(day.mean(axis=0).argmax()))
# [end: numpy]


# [start: pandas]
def pandas_demo():
    from plantp import datapack
    h = datapack.load_hourly()
    print("index:", h.index[0], "...", h.index[-1], "| tz:", h.index.tz)
    monthly = h["ghi_wm2"].resample("MS").sum() / 1000     # kWh/m2
    print("June GHI", round(monthly.iloc[5], 1), "kWh/m2;",
          "December", round(monthly.iloc[11], 1))
    profile = h.groupby(h.index.hour)["ws_100m_ms"].mean()
    print(f"windiest hour {profile.idxmax()}:00 ({profile.max():.2f} m/s),",
          f"calmest {profile.idxmin()}:00 ({profile.min():.2f} m/s)")
    print(h[["t_air_c", "p_hpa"]].describe().loc[["mean", "min", "max"]]
          .round(1).to_string())
# [end: pandas]


# [start: datetime]
def datetime_demo():
    import pandas as pd
    t = pd.Timestamp("2023-04-03 14:10")               # naive: no zone
    local = t.tz_localize("+04:00")                    # we SAY which zone
    start = local - pd.Timedelta(minutes=10)           # end label -> start
    print("label", t, "-> interval start", start)
    print("in UTC:", start.tz_convert("UTC"))
    utc = pd.date_range("2023-03-25 23:00", periods=4, freq="h", tz="UTC")
    berlin = utc.tz_convert("Europe/Berlin")           # a zone with DST
    print("four UTC hours seen in Berlin:",
          [x.strftime("%H:%M%z") for x in berlin])
# [end: datetime]


# [start: solver]
def solver_demo():
    import numpy as np
    from scipy import integrate, optimize
    from plantp import datapack, stats
    curve = datapack.load_power_curve()
    v, p = curve["wind_speed_ms"].to_numpy(), curve["power_kw"].to_numpy()

    def power(x):
        return float(np.interp(x, v, p))
    v_half = optimize.brentq(lambda x: power(x) - 2500.0, 3.0, 13.0)
    print(f"speed for 2.5 MW: {v_half:.3f} m/s")
    k, c = 2.11, 8.02                                  # chapter 3 fit
    mean_kw, err = integrate.quad(
        lambda x: power(x) * stats.weibull_pdf(x, k, c), 0, 30,
        points=list(v[(v > 2) & (v < 26)]), limit=200)
    print(f"Weibull mean power {mean_kw:,.0f} kW (error estimate {err:.1e})")
    print(f"capacity factor {mean_kw / 5000:.3f}")
# [end: solver]


# [start: plot]
def plot_demo(folder):
    import matplotlib
    matplotlib.use("Agg")                              # no screen needed
    import matplotlib.pyplot as plt
    from plantp import datapack
    h = datapack.load_hourly("week_spring")
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.plot(h.index, h["ws_100m_ms"], label="100 m")
    ax.plot(h.index, h["ws_60m_ms"], "--", label="60 m")
    ax.set_ylabel("wind speed (m/s)")
    ax.set_title("Plant P, 3-9 April (data pack 1.1.0)")
    ax.legend()
    fig.tight_layout()
    out = f"{folder}/week_wind.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print("wrote", out.rsplit("/", 1)[-1], "with", len(h), "points per line")
# [end: plot]


# [start: config]
def config_demo():
    import yaml
    text = """
    run: S0
    data_release: 1.1.0
    pv: {dc_mwp: 60, ac_mw: 50, pr_dc: 0.85}
    wind: {turbines: 12, loss: 0.12}
    export_limit_mw: 100
    """
    cfg = yaml.safe_load(text)
    print(cfg["pv"], "| limit", cfg["export_limit_mw"], "MW")
    print("release read as", repr(cfg["data_release"]),
          "-> keep versions as text")
    print("yaml '1.10' is", repr(yaml.safe_load("v: 1.10")["v"]),
          "but '\"1.10\"' is", repr(yaml.safe_load('v: "1.10"')["v"]))
# [end: config]


# [start: versions]
def versions_demo():
    import platform
    import numpy
    import pandas
    import scipy
    import plantp
    print("python", platform.python_version(), "| numpy", numpy.__version__,
          "| pandas", pandas.__version__, "| scipy", scipy.__version__)
    print("plantp", plantp.__version__, "| data pack", plantp.DATA_RELEASE)
# [end: versions]


def main() -> None:
    out = HERE / "output"
    out.mkdir(exist_ok=True)
    for name, func in (("numpy", numpy_demo), ("pandas", pandas_demo),
                       ("datetime", datetime_demo), ("solver", solver_demo),
                       ("config", config_demo), ("versions", versions_demo)):
        emit(f"b_{name}", capture(func))
    emit("b_plot", capture(plot_demo, out.as_posix()))


if __name__ == "__main__":
    sys.exit(main())
