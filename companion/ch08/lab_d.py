"""Chapter 8, section D - integration and condition-monitoring lab:
(1) a year of generator losses from the data pack, (2) a bearing fault in
a synthetic vibration record (spectrum and envelope), (3) cooling
degradation found in synthetic winding-temperature residuals.

Run from the project root:   python -m companion.ch08.lab_d
Writes companion/ch08/expected/d_*.txt and diagrams/data/ch08-*.csv.
Data pack 1.1.0 (hourly wind at 100 m, power curve at 1.225 kg/m3, S0);
A-111, A-116, A-119 (synthetic records, seeds 8 and 11). Not a design.
"""
from __future__ import annotations

import numpy as np

from companion.ch08.common import csv, emit
from plantp import datapack
from plantp import machines as m

P_GEN_R, ETA_R = 5.13e6, 0.970          # generator output at rating, A-111
ETA_CONV = 0.975                        # converter (chapter 4, A-047 chain)


# [start: annual]
def generator_year(fixed_share: float = 0.35):
    """Hourly generator output (W) and losses (W) of one turbine for the
    data-pack year; the turbine output follows the power curve."""
    hourly = datapack.load_hourly()
    curve = datapack.load_power_curve()
    p_turbine = 1e3 * np.interp(hourly["ws_100m_ms"].to_numpy(),
                                curve["wind_speed_ms"].to_numpy(),
                                curve["power_kw"].to_numpy())
    p_gen = p_turbine / ETA_CONV                  # generator terminals
    load = p_gen / P_GEN_R
    loss = np.where(p_gen > 0,
                    [m.loss_model(x, P_GEN_R, ETA_R, fixed_share)
                     for x in load], 0.0)         # stopped: no losses
    return p_gen, loss
# [end: annual]


def annual() -> None:
    lines = ["one turbine, data-pack year (1.1.0, S0; curve at 1.225 kg/m3;",
             "  gross: no wake or other losses), generator terminals:"]
    rows = None
    for share in (0.20, 0.35, 0.50):
        p_gen, loss = generator_year(share)
        e_out = p_gen.sum() / 1e6                     # MWh (1 h steps)
        e_loss = loss.sum() / 1e6
        run = (p_gen > 0).mean()
        lines.append(f"  fixed {100 * share:.0f} %: output {e_out:7.0f} MWh, "
                     f"losses {e_loss:5.1f} MWh, mean eff. "
                     f"{e_out / (e_out + e_loss):.4f}")
        if share == 0.35:
            load = p_gen / P_GEN_R
            hist, edges = np.histogram(load[p_gen > 0], bins=11,
                                       range=(0, 1.1))
            rows = [(f"{0.5 * (a + b):.2f}", f"{h}") for a, b, h in
                    zip(edges[:-1], edges[1:], hist)]
            e_by_bin = [p_gen[(load >= a) & (load < b)].sum() / 1e6
                        for a, b in zip(edges[:-1], edges[1:])]
            lines.append(f"    running {100 * run:.0f} % of hours; at rated "
                         "efficiency the losses would be")
            lines.append(f"    {e_out * (1 / ETA_R - 1):.1f} MWh")
            top = int(np.argmax(e_by_bin))
            lines.append(f"    most energy comes at {edges[top]:.1f}-"
                         f"{edges[top + 1]:.1f} pu load "
                         f"({100 * max(e_by_bin) / e_out:.0f} %)")
    lines += ["  12 turbines: about twelve times these losses each year;",
              "  part-load efficiency, not the rated value, sets the energy "
              "lost"]
    emit("d_annual", lines)
    csv("ch08-loadhist.csv", "load,hours", rows)


# [start: envelope]
def envelope_spectrum(x, fs, f_lo, f_hi):
    """Band-pass x by FFT masking, take the magnitude of the analytic signal
    (the envelope) and return its one-sided spectrum."""
    n = len(x)
    spec = np.fft.fft(x)
    f = np.fft.fftfreq(n, 1 / fs)
    band = (np.abs(f) >= f_lo) & (np.abs(f) <= f_hi)
    analytic = np.zeros(n, dtype=complex)
    analytic[(f > 0) & band] = 2 * spec[(f > 0) & band]
    env = np.abs(np.fft.ifft(analytic))
    env = env - env.mean()
    amp = np.abs(np.fft.rfft(env)) * 2 / n
    return np.fft.rfftfreq(n, 1 / fs), amp
# [end: envelope]


def bearing() -> None:
    fs, dur = 10240.0, 2.0
    t = np.arange(0, dur, 1 / fs)
    rng = np.random.default_rng(8)                                  # A-116
    b = m.bearing_freqs(1155, 14, 0.040, 0.220)
    x = 0.20 * np.sin(2 * np.pi * b["fr"] * t)                      # 1x
    x += 0.05 * np.sin(2 * np.pi * 2 * b["fr"] * t)                 # 2x
    for t0 in np.arange(0, dur, 1 / b["bpfo"]):                     # impacts
        k = t >= t0
        tau = t[k] - t0
        x[k] += 0.6 * np.exp(-tau / 0.002) * np.sin(2 * np.pi * 3000 * tau)
    x += 0.5 * rng.standard_normal(len(t))
    f = np.fft.rfftfreq(len(t), 1 / fs)
    raw = np.abs(np.fft.rfft(x)) * 2 / len(t)
    fe, env = envelope_spectrum(x, fs, 2000, 4000)
    low = (f > 5) & (f < 500)
    top_raw = f[low][np.argsort(raw[low])[-3:][::-1]]
    lowe = (fe > 5) & (fe < 500)
    top_env = fe[lowe][np.argsort(env[lowe])[-3:][::-1]]
    emit("d_bearing", [
        f"synthetic acceleration, fs {fs:.0f} Hz, 2 s, outer-race defect "
        "(A-116):",
        f"  expected outer-race frequency {b['bpfo']:.1f} Hz; shaft "
        f"{b['fr']:.2f} Hz",
        "  largest raw-spectrum peaks below 500 Hz: "
        + ", ".join(f"{x:.1f}" for x in top_raw) + " Hz",
        "  largest envelope-spectrum peaks (band 2-4 kHz): "
        + ", ".join(f"{x:.1f}" for x in top_env) + " Hz",
        "  the raw spectrum shows the shaft; the envelope shows the defect",
        "  at the outer-race frequency and its harmonics",
    ])
    sel = fe <= 500
    csv("ch08-envelope.csv", "f,env", [(f"{a:.2f}", f"{v:.5f}")
                                       for a, v in zip(fe[sel], env[sel])])


# [start: residual]
def temperature_record(seed: int = 11):
    """Hourly winding temperature of one generator for the data-pack year:
    air temperature + k x losses + noise; the cooling fouls from day 200
    (k grows 15 %, A-119)."""
    rng = np.random.default_rng(seed)
    hourly = datapack.load_hourly()
    t_air = hourly["t_air_c"].to_numpy()
    _, loss = generator_year()
    k = np.where(np.arange(len(loss)) < 200 * 24, 0.30, 0.345)   # K per kW
    temp = t_air + 15.0 + k * loss / 1e3 + rng.normal(0, 1.5, len(loss))
    return t_air, loss / 1e3, temp
# [end: residual]


def residual() -> None:
    t_air, loss_kw, temp = temperature_record()
    train = np.arange(len(temp)) < 60 * 24
    a = np.column_stack([np.ones(train.sum()), t_air[train], loss_kw[train]])
    coef, *_ = np.linalg.lstsq(a, temp[train], rcond=None)
    pred = coef[0] + coef[1] * t_air + coef[2] * loss_kw
    res = temp - pred
    loaded = loss_kw > 50                        # only hours with load
    days = np.arange(365)
    daily = np.array([res[d * 24:(d + 1) * 24][loaded[d * 24:(d + 1) * 24]]
                      .mean() if loaded[d * 24:(d + 1) * 24].any() else 0.0
                      for d in days])
    cusum, alarm = 0.0, None
    for d in days[60:]:
        cusum = max(0.0, cusum + daily[d] - 0.5)
        if cusum > 5.0 and alarm is None:
            alarm = d
    before = res[(np.arange(len(res)) < 200 * 24) & loaded].mean()
    after = res[(np.arange(len(res)) >= 200 * 24) & loaded].mean()
    emit("d_temperature", [
        "winding temperature model fitted on days 0-59 (A-119, synthetic):",
        f"  T = {coef[0]:.1f} + {coef[1]:.2f} T_air + {coef[2]:.3f} x losses "
        "(kW)",
        f"  mean residual on loaded hours: before day 200 {before:+.2f} K, "
        f"after {after:+.2f} K",
        f"  CUSUM of daily residuals (slack 0.5 K, limit 5 K): alarm on day "
        f"{alarm}",
        "  the cooling fouled on day 200 (planted); the alarm comes days "
        "later,",
        "  long before the absolute temperature looks unusual",
    ])
    csv("ch08-residual.csv", "day,res", [(d, f"{v:.3f}") for d, v in
                                         zip(days, daily)])


if __name__ == "__main__":
    annual()
    bearing()
    residual()
