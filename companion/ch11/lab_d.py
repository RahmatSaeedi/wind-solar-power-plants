"""Chapter 11, section D - yield and design lab: gross energy from the wind
distribution and the power curve (bins, Weibull, time series), the density
correction, wake losses of three layouts of the twelve turbines with the
Jensen model, and a bearing fault found in a synthetic vibration signal.

Run from the project root:   python -m companion.ch11.lab_d
Writes companion/ch11/expected/d_*.txt and diagrams/data/ch11-*.csv.
Teaching values A-221 .. A-223 (fictional); data pack 1.1.0 (S0).
"""
from __future__ import annotations

import math

import numpy as np
from scipy.signal import hilbert

from companion.ch11 import rotor
from companion.ch11.common import csv, emit
from plantp import datapack, physics, stats, wind as w

N_T = 12
D = 2 * rotor.RADIUS


def hourly():
    h = datapack.load_hourly()
    v = h["ws_100m_ms"].to_numpy(float)
    wd = h["wd_100m_deg"].to_numpy(float)
    rho = np.asarray(physics.air_density(h["p_hpa"].to_numpy(float),
                                         h["t_air_c"].to_numpy(float)))
    return v, wd, rho


def pack_power(v):
    pc = datapack.load_power_curve()
    return np.interp(v, pc.wind_speed_ms, pc.power_kw, right=0.0)


# [start: bins]
def energy_by_bins(v, power_kw, width: float = 1.0):
    """Hours in each wind-speed bin times the power at the bin centre."""
    edges = np.arange(0.0, 26.0 + width, width)
    hours, _ = np.histogram(v, edges)
    centre = 0.5 * (edges[1:] + edges[:-1])
    energy = hours * power_kw(centre) / 1e3                   # MWh
    return centre, hours, energy
# [end: bins]


def energy() -> None:
    v, wd, rho = hourly()
    c, hrs, e = energy_by_bins(v, pack_power)
    series = pack_power(v).sum() / 1e3
    k, cw = stats.weibull_fit_mle(v)
    vv = np.linspace(0, 30, 3001)
    mean_p = np.trapezoid(pack_power(vv) * stats.weibull_pdf(vv, k, cw), vv)
    lines = ["worked example 1: one turbine, data-pack year, 1.225 kg/m3:",
             "  bin m/s   hours   P kW    MWh    share %"]
    for ci, hi, ei in zip(c, hrs, e):
        if hi > 0 and ci <= 18:
            lines.append(f"  {ci:7.1f}   {hi:5d}   {float(pack_power(ci)):4.0f}"
                         f"   {ei:6.0f}   {100 * ei / e.sum():6.1f}")
    lines += [f"  sum of bins {e.sum():,.0f} MWh; hour by hour {series:,.0f} MWh",
              f"  Weibull k {k:.2f}, c {cw:.2f} m/s: mean power {mean_p:,.0f} kW"
              f" -> {mean_p * 8.76:,.0f} MWh",
              f"  twelve turbines: {12 * series / 1e3:.2f} GWh gross; chapter 5's"
              " 192.54 GWh",
              f"    is this gross after its 12 % lumped loss"
              f" (x 0.88 = {12 * series / 1e3 * 0.88:.2f})",
              "  most energy comes from 7 .. 13 m/s, where the curve is steep:",
              "  the curve's uncertainty there matters most"]
    emit("d_energy", lines)
    csv("ch11-energybins.csv", "v,hours,mwh",
        [(f"{ci:.1f}", int(hi), f"{ei:.1f}") for ci, hi, ei in zip(c, hrs, e)
         if ci <= 22])


def density() -> None:
    v, wd, rho = hourly()
    p_ref = pack_power(v).sum() / 1e3
    v_eq = w.density_equivalent_speed(v, rho)
    p_hour = pack_power(v_eq).sum() / 1e3
    v_mean = w.density_equivalent_speed(v, rho.mean())
    p_mean = pack_power(v_mean).sum() / 1e3
    _, _, s1, _ = rotor.curve_arrays(rotor.RHO_SITE)
    vg = np.arange(0.0, 30.01, 0.5)
    p_bem = np.interp(v, vg, s1, right=0.0).sum() / 1e3
    emit("d_density", [
        "one turbine, four ways to treat air density (A-221):",
        f"  power curve at 1.225 kg/m3, no correction   {p_ref:8,.0f} MWh",
        f"  equivalent speed, hourly density            {p_hour:8,.0f} MWh "
        f"({100 * (p_hour / p_ref - 1):+.1f} %)",
        f"  equivalent speed, mean density {rho.mean():.3f}       {p_mean:8,.0f}"
        f" MWh ({100 * (p_mean / p_ref - 1):+.1f} %)",
        f"  BEM rotor at {rotor.RHO_SITE} kg/m3, turbulence 10 %   {p_bem:8,.0f}"
        f" MWh ({100 * (p_bem / p_ref - 1):+.1f} %)",
        "  the BEM rotor gives about 2.5 % more, mostly from its higher",
        "  power near cut-in; leaving density out overstates the energy",
        "  by about 9 %: the largest single correction at 1200 m"])


def layouts():
    s4, s5, s8 = 4 * D, 5 * D, 8 * D
    rows = np.array([[x * s4, y * s8] for y in (0, 1) for x in range(6)])
    line = np.array([[x * s4, 0.0] for x in range(12)])
    grid = np.array([[x * s5, y * s5] for y in range(3) for x in range(4)])
    return {"A: 2 rows of 6, 4D x 8D": rows, "B: 1 row of 12, 4D": line,
            "C: 3 x 4 grid, 5D x 5D": grid}


def prevailing(wd) -> float:
    edges = np.arange(0, 361, 30)
    cnt, _ = np.histogram(wd % 360, edges)
    return float(edges[int(np.argmax(cnt))] + 15)


def rotate(xy, deg: float):
    """Rotate a layout so that its rows run across the given direction."""
    a = math.radians(deg)
    r = np.array([[math.cos(a), math.sin(a)], [-math.sin(a), math.cos(a)]])
    return xy @ r.T


def farm_energy(xy):
    """Free-stream and waked energy (MWh) of a layout over the data year,
    with sector totals (30 deg sectors)."""
    v, wd, rho = hourly()
    v_eq = w.density_equivalent_speed(v, rho)
    vg, _, _, ctg = rotor.curve_arrays()
    e_free = e_wake = 0.0
    sec_free, sec_wake = np.zeros(12), np.zeros(12)
    for k in np.flatnonzero(v_eq > 2.5):
        ct = float(np.interp(v_eq[k], vg, ctg))
        vs = w.farm_speeds(xy, float(v_eq[k]), float(wd[k]), ct, D)
        pf = N_T * float(pack_power(v_eq[k]))
        pw = float(pack_power(vs).sum())
        e_free += pf
        e_wake += pw
        s = int((wd[k] % 360) // 30)
        sec_free[s] += pf
        sec_wake[s] += pw
    return e_free / 1e3, e_wake / 1e3, sec_free, sec_wake


def wakes() -> None:
    _, wd, _ = hourly()
    prev = prevailing(wd)
    lines = [f"wake losses with the Jensen model, k 0.05 (A-222); prevailing"
             f" sector {prev:.0f} deg:",
             "  layout                      free GWh   waked GWh   wake loss %"]
    for name, xy0 in layouts().items():
        xy = rotate(xy0, prev)
        e_free, e_wake, sf, sw = farm_energy(xy)
        lines.append(f"  {name:26s}  {e_free / 1e3:8.2f}   {e_wake / 1e3:9.2f}"
                     f"   {100 * (1 - e_wake / e_free):11.2f}")
        if name.startswith("A"):
            csv("ch11-wakerose.csv", "deg,loss",
                [(f"{15 + 30 * k}", f"{100 * (1 - b / a):.2f}" if a else "0")
                 for k, (a, b) in enumerate(zip(sf, sw))])
            csv("ch11-layout.csv", "x,y", [(f"{a:.0f}", f"{b:.0f}") for a, b in xy])
    lines += ["  a single row across the prevailing wind loses least but",
              "  stretches 6.6 km; the compact grid loses most; two rows",
              "  with 8D between them are the middle course; wakes also",
              "  raise turbulence and fatigue loads downstream"]
    emit("d_wakes", lines)


def condition() -> None:
    fs, t_len = 10_000.0, 2.0                      # A-223
    t = np.arange(0, t_len, 1 / fs)
    f_r = 1155 / 60                               # high-speed shaft
    n, d_ratio = 12, 0.2
    bpfo = n / 2 * f_r * (1 - d_ratio)
    rng = np.random.default_rng(59)
    sig = 0.5 * np.sin(2 * np.pi * f_r * t) + 0.8 * np.sin(2 * np.pi * 27 * f_r * t)
    impacts = np.zeros_like(t)
    for t0 in np.arange(0.003, t_len, 1 / bpfo):
        k = int(t0 * fs)
        tau = t[k:] - t[k]
        ring = np.exp(-tau * 800) * np.sin(2 * np.pi * 3000 * tau)
        impacts[k:] += 0.6 * ring
    sig = sig + impacts + rng.normal(0, 0.4, t.size)
    spec = np.abs(np.fft.rfft(sig * np.hanning(t.size))) / t.size
    f = np.fft.rfftfreq(t.size, 1 / fs)
    full = np.fft.rfft(sig)
    full[(f < 2000) | (f > 4000)] = 0.0                    # band-pass
    band = np.fft.irfft(full, n=t.size)
    env = np.abs(hilbert(band))
    env_spec = np.abs(np.fft.rfft((env - env.mean()) * np.hanning(t.size))) / t.size
    sel = (f > 20) & (f < 400)
    k_peak = int(np.argmax(np.where(sel, env_spec, 0)))
    raw_at = spec[int(np.argmin(abs(f - bpfo)))]
    emit("d_condition", [
        "gearbox high-speed bearing, synthetic accelerometer (A-223):",
        f"  shaft {f_r:.2f} Hz, gear mesh 27 x = {27 * f_r:.0f} Hz, outer-race"
        f" defect BPFO {bpfo:.1f} Hz",
        f"  raw spectrum at BPFO: {raw_at:.4f} (lost among the mesh lines"
        " and noise)",
        f"  envelope spectrum peak: {f[k_peak]:.1f} Hz -> the bearing defect"
        " frequency",
        "  impacts excite a structural resonance; demodulating that band",
        "  reveals their repetition rate: the basis of bearing diagnosis",
        "  in condition monitoring systems (chapter 52)"])
    keep = f <= 600
    step = 1
    csv("ch11-spectrum.csv", "f,raw,env",
        [(f"{a:.1f}", f"{1e3 * b:.3f}", f"{1e3 * c:.3f}")
         for a, b, c in zip(f[keep][::step], spec[keep][::step],
                            env_spec[keep][::step])])


if __name__ == "__main__":
    energy()
    density()
    wakes()
    condition()
