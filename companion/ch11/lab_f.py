"""Chapter 11, section D (second lab): measuring a power curve from
ten-minute records (filtering, density normalisation, the method of bins,
energy and its uncertainty) and the sound of the twelve turbines at three
fictional dwellings, with a reduced-speed night mode.

Run from the project root:   python -m companion.ch11.lab_f
Writes companion/ch11/expected/h_*.txt and diagrams/data/ch11-*.csv.
Teaching values A-233, A-234 (fictional); synthetic records, seed 71;
data pack 1.1.0 (S0) for the hourly year.
"""
from __future__ import annotations

import math
from functools import lru_cache

import numpy as np

from companion.ch11 import lab_d, rotor
from companion.ch11.common import csv, emit
from plantp import wind as w

VG = np.arange(0.0, 30.01, 0.5)
RHO_REF = rotor.RHO_SITE
DENSITIES = (1.00, 1.056, 1.12)


@lru_cache(maxsize=1)
def true_curves():
    """Smoothed model curves at three densities (the 'real' turbine)."""
    return np.array([rotor.curve_arrays(r)[2] for r in DENSITIES])


def true_power(v, rho):
    """Power (kW) of the model turbine at speed v and density rho, linear
    between the three density curves."""
    cur = true_curves()
    p = np.array([np.interp(v, VG, c) for c in cur])          # (3, n)
    return np.array([np.interp(r, DENSITIES, p[:, k])
                     for k, r in enumerate(np.atleast_1d(rho))])


def records(n: int = 8064, seed: int = 71):
    """Eight weeks of synthetic ten-minute records with status flags:
    0 normal, 1 curtailed, 2 iced, 3 unavailable (A-233)."""
    rng = np.random.default_rng(seed)
    v = 8.0 * rng.weibull(2.1, n)
    rho = np.clip(RHO_REF + 0.035 * rng.standard_normal(n), 0.98, 1.12)
    p = true_power(v, rho)
    p = p + rng.standard_normal(n) * (30.0 + 0.02 * p)
    flag = np.zeros(n, int)
    for code, share, length in ((1, 0.04, 18), (2, 0.015, 12), (3, 0.02, 24)):
        hits = 0
        while hits < share * n:
            k = int(rng.integers(0, n - length))
            flag[k:k + length] = np.where(flag[k:k + length] == 0, code,
                                          flag[k:k + length])
            hits += length
    p = np.where(flag == 1, np.minimum(p, 3000.0), p)
    p = np.where(flag == 2, 0.7 * p, p)
    p = np.where(flag == 3, 0.0, p)
    p = np.where(v < 2.5, 0.0, np.maximum(p, 0.0))
    return v, rho, p, flag


def rayleigh_hours(mean: float, centres):
    """Hours a year in 0.5 m/s bins for a Rayleigh distribution."""
    edges = np.concatenate((centres - 0.25, [centres[-1] + 0.25]))
    cdf = 1 - np.exp(-math.pi / 4 * (np.maximum(edges, 0) / mean) ** 2)
    return 8760 * np.diff(cdf)


def aep(bins, mean: float) -> float:
    """Energy (MWh) of a binned curve, Rayleigh hours, linear between bins."""
    vb = np.array([b[0] for b in bins])
    pb = np.array([b[1] for b in bins])
    c = np.arange(0.25, 25.0, 0.5)
    p = np.interp(c, vb, pb, left=0.0, right=float(pb[-1]))
    return float((rayleigh_hours(mean, c) * p).sum() / 1e3)


def measure() -> None:
    v, rho, p, flag = records()
    good = flag == 0
    # [start: normalise]
    v_n = v * (rho / RHO_REF) ** (1 / 3)       # density-normalised speed
    bins = w.bin_power_curve(v_n[good], p[good])
    raw = w.bin_power_curve(v, p)              # no filter, no normalisation
    # [end: normalise]
    model = [(c, float(np.interp(c, VG, rotor.curve_arrays(RHO_REF)[2])), 0.0,
              1) for c in np.arange(0.25, 25.0, 0.5)]
    e_meas, e_raw, e_model = (aep(b, 7.0) for b in (bins, raw, model))
    # type A: scatter of the bin means; type B: anemometer 0.1 m/s + 1 %
    vb = np.array([b[0] for b in bins])
    pb = np.array([b[1] for b in bins])
    hrs = rayleigh_hours(7.0, np.round(vb * 2) / 2 + 0.0)
    ua = math.sqrt(sum((h * b[2] / math.sqrt(b[3])) ** 2
                       for h, b in zip(hrs, bins))) / 1e3
    slope = np.gradient(pb, vb)
    ub = float(np.sum(hrs * slope * (0.1 + 0.01 * vb))) / 1e3
    counts = np.bincount(flag, minlength=4)
    lines = ["power-curve measurement from 8,064 ten-minute records (A-233):",
             f"  status: normal {counts[0]:,}, curtailed {counts[1]}, iced"
             f" {counts[2]}, unavailable {counts[3]}",
             f"  normalised to {RHO_REF} kg/m3, bins 0.5 m/s, at least 10"
             f" records: {len(bins)} bins",
             "  bin m/s   records   measured kW   std kW   model kW"]
    for b in bins:
        if abs(b[0] - round(b[0])) < 0.3 and 4 <= round(b[0]) <= 14:
            mk = float(np.interp(b[0], VG, rotor.curve_arrays(RHO_REF)[2]))
            lines.append(f"  {b[0]:6.2f}    {b[3]:5d}     {b[1]:8.0f}     "
                         f"{b[2]:5.0f}     {mk:6.0f}")
    lines += [f"  energy at a Rayleigh mean of 7.0 m/s: measured"
              f" {e_meas:,.0f} MWh, model {e_model:,.0f} MWh",
              f"    ratio {e_meas / e_model:.3f}; without filtering and"
              f" normalisation {e_raw:,.0f} MWh ({e_raw / e_model:.3f})",
              f"  uncertainty: scatter (type A) {ua:,.0f} MWh"
              f" ({100 * ua / e_meas:.2f} %); anemometer (type B)"
              f" {ub:,.0f} MWh ({100 * ub / e_meas:.1f} %)",
              "  the wind-speed measurement, not the number of records,",
              "  limits the accuracy of a power-curve test"]
    emit("h_measure", lines)
    rng = np.random.default_rng(5)
    pick = rng.choice(np.flatnonzero(good), 1200, replace=False)
    csv("ch11-pcscatter.csv", "v,p",
        [(f"{v_n[k]:.2f}", f"{p[k] / 1e3:.3f}") for k in pick])
    bad = np.flatnonzero(~good & (v > 3.0))
    csv("ch11-pcflag.csv", "v,p",
        [(f"{v_n[k]:.2f}", f"{p[k] / 1e3:.3f}") for k in bad[::2]])
    csv("ch11-pcbins.csv", "v,p,model",
        [(f"{b[0]:.2f}", f"{b[1] / 1e3:.3f}",
          f"{np.interp(b[0], VG, rotor.curve_arrays(RHO_REF)[2]) / 1e3:.3f}")
         for b in bins])


# ----------------------------------------------------------------- sound
LW = 106.0          # dB(A), declared sound power at full speed (A-234)
ALPHA = 0.002       # dB/m, broadband air absorption (teaching)


@lru_cache(maxsize=1)
def quiet_curve():
    """Smoothed power curve with the rotor speed capped at 10.5 rpm; the
    drivetrain torque limit then caps power at 5 MW x 10.5 / 11.5."""
    t = w.Turbine(rotor.blade(), tsr_opt=rotor.tsr_opt(),
                  rated_w=5.0e6 * 10.5 / 11.5,
                  omega_max=10.5 * math.pi / 30)
    ops = [w.operate(t, float(x), RHO_REF) for x in np.arange(3.0, 25.01, 0.5)]
    p = np.zeros_like(VG)
    for o in ops:
        p[int(round(o.v / 0.5))] = o.power_w / 1e3
    sm = w.smooth_power_curve(VG, p)
    sm[(VG > 25.0) | (VG < 2.5)] = 0.0
    return sm


def noise() -> None:
    xy = lab_d.rotate(lab_d.layouts()["A: 2 rows of 6, 4D x 8D"],
                      lab_d.prevailing(lab_d.hourly()[1]))
    centre = xy.mean(axis=0)
    xy = xy - centre
    # three fictional dwellings at set distances from the nearest turbine
    recv = {}
    for name, ang, dist in (("R1", 200.0, 600.0), ("R2", 20.0, 900.0),
                            ("R3", 110.0, 1500.0)):
        u = np.array([math.sin(math.radians(ang)), math.cos(math.radians(ang))])
        s = float(np.max(xy @ u))               # start beyond the farm
        while np.min(np.hypot(*(xy - s * u).T)) < dist:
            s += 5.0
        recv[name] = s * u
    drop = 50 * math.log10(10.5 / 11.5)
    lines = [f"sound at three fictional dwellings, layout A (A-234): L_W"
             f" {LW:.0f} dB(A),",
             f"  hemispherical spreading, absorption {ALPHA * 1e3:.0f} dB/km,"
             " no ground or screening terms",
             "  dwelling  nearest m  nearest dB(A)  12 turbines  night mode"]
    for name, pt in recv.items():
        d = np.hypot(*(xy - pt).T)
        slant = np.hypot(d, rotor.HUB)
        lev = w.sound_pressure_level(LW, slant, ALPHA)
        tot = w.sum_levels(lev)
        lines.append(f"  {name}        {d.min():6.0f}      {lev.max():6.1f}"
                     f"         {tot:6.1f}      {tot + drop:6.1f}")
    v, _, rho = lab_d.hourly()
    hours = lab_d.datapack.load_hourly().index.hour
    night = (hours >= 22) | (hours < 6)
    v_eq = w.density_equivalent_speed(v, rho, RHO_REF)
    _, _, sm, _ = rotor.curve_arrays(RHO_REF)
    full = np.interp(v_eq, VG, sm)
    quiet = np.where(night, np.interp(v_eq, VG, quiet_curve()), full)
    loss = 100 * (1 - quiet.sum() / full.sum())
    lines += ["  night mode: rotor speed 10.5 instead of 11.5 rpm;",
              f"    the tip-speed rule 50 log10(10.5/11.5) gives {drop:.1f} dB",
              f"  the torque limit caps the power at"
              f" {5000 * 10.5 / 11.5:,.0f} kW in this mode",
              f"  energy cost of the mode at night only (22:00 - 06:00):"
              f" {loss:.2f} % of the year",
              "  limits, times and assessment methods are national (chapters",
              "  33 and 55); the declared level comes from a test to the"
              " acoustic",
              "  measurement standard (IEC 61400-11:2012+AMD1:2018)"]
    emit("h_noise", lines)
    dist = np.arange(100.0, 2001.0, 50.0)
    sl = np.hypot(dist, rotor.HUB)
    csv("ch11-noise.csv", "d,full,quiet",
        [(f"{x:.0f}", f"{a:.2f}", f"{a + drop:.2f}") for x, a in
         zip(dist, w.sound_pressure_level(LW, sl, ALPHA))])


if __name__ == "__main__":
    measure()
    noise()
