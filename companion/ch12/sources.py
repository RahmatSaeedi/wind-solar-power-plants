"""Chapter 12 - the irradiance data of the chapter.

* the data-pack year (1.1.0, S0), treated as the quality-controlled
  record of the Plant P ground station;
* a synthetic 'provider' hourly series of the same year, built like a
  satellite-derived product: smoother in time, a seasonal bias pattern,
  random scatter, its own decomposition into beam and diffuse (A-240);
* a synthetic 20-year long-term reference (provider monthly sums with
  interannual variability, A-241);
* synthetic one-minute days with known faults for the cleaning lab (A-242).

All synthetic and seeded; teaching values only.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from companion.ch12 import common  # noqa: F401  (puts plantp on the path)
from companion.ch10 import pvyear10
from plantp import datapack, irradiance as ir, solar

LAT = pvyear10.LAT
YEARS = 20


@lru_cache(maxsize=1)
def pack() -> dict:
    """Ground-station year with hour-mean sun geometry (horizontal)."""
    h = datapack.load_hourly()
    _, cz, n = pvyear10.geometry(0.0, 180.0)
    return {"ghi": h["ghi_wm2"].to_numpy(float), "dni": h["dni_wm2"].to_numpy(float),
            "dhi": h["dhi_wm2"].to_numpy(float), "t_air": h["t_air_c"].to_numpy(float),
            "cz": cz, "doy": n, "hour": np.arange(8760) % 24,
            "month": h.index.month.to_numpy() - 1, "g0n": ir.g0n(n)}


# [start: provider]
@lru_cache(maxsize=1)
def provider(seed: int = 121) -> dict:
    """Satellite-style hourly series: clearness index pulled 15 % towards
    a 3-hour running mean (pixel and time smoothing), a seasonal bias
    (+3 % in winter to -1.5 % in summer), random scatter of 7 % of GHI,
    and DNI/DHI from the Erbs model."""
    p = pack()
    rng = np.random.default_rng(seed)
    kt = np.nan_to_num(ir.clearness_index(p["ghi"], p["cz"], p["g0n"]))
    smooth = np.convolve(kt, np.ones(3) / 3, mode="same")
    kt_p = kt + 0.15 * (smooth - kt)
    bias = 0.0075 + 0.0225 * np.cos(2 * np.pi * (p["month"] + 0.5) / 12)
    ghi = kt_p * p["g0n"] * p["cz"] * (1 + bias)
    ghi *= 1 + 0.07 * rng.standard_normal(8760)
    ghi = np.where(p["cz"] > 0.02, np.clip(ghi, 0, None), 0.0)
    dni, dhi = ir.decompose(ghi, p["cz"], p["g0n"])
    return {"ghi": ghi, "dni": dni, "dhi": dhi}
# [end: provider]


@lru_cache(maxsize=1)
def long_term(seed: int = 122) -> dict:
    """Provider monthly GHI sums (kWh/m2) for 20 years ending with the
    station year: annual anomaly sd 2.5 %, monthly sd 4 %; the station
    year is the last one (A-241)."""
    rng = np.random.default_rng(seed)
    pr = provider()["ghi"]
    month = pack()["month"]
    base = np.array([pr[month == m].sum() / 1e3 for m in range(12)])
    annual = 0.025 * rng.standard_normal(YEARS)
    annual -= annual.mean()                              # long-term mean = 1
    annual[-1] = 0.021                                   # 2023 was a sunny year
    monthly = 0.04 * rng.standard_normal((YEARS, 12))
    sums = base[None, :] / (1 + annual[-1]) * (1 + annual[:, None] + monthly)
    sums[-1] = base                                      # concurrent year exact
    return {"years": np.arange(2023 - YEARS + 1, 2024), "monthly": sums,
            "annual": sums.sum(axis=1)}


def clear_sky_minutes(doy: int) -> tuple[np.ndarray, np.ndarray]:
    """One-minute cos(zenith) and Haurwitz clear-sky GHI for one day."""
    t = np.arange(1440) / 60 + 0.5 / 60
    st = solar.solar_time(t, doy)
    el, _ = solar.sun_position(LAT, doy, st)
    cz = np.where(el > 0, np.sin(np.radians(el)), 0.0)
    return cz, ir.clear_sky_haurwitz(cz)


@lru_cache(maxsize=1)
def minute_days(seed: int = 123) -> dict:
    """Three one-minute days (clear, broken cloud, overcast) of a
    thermopile pyranometer, true and with faults injected (A-242)."""
    rng = np.random.default_rng(seed)
    days = {"clear": 172, "broken": 100, "overcast": 340}
    out = {}
    for name, doy in days.items():
        cz, cs = clear_sky_minutes(doy)
        if name == "clear":
            tau = np.full(1440, 0.98)
        elif name == "broken":
            x = np.zeros(1440)
            for k in range(1, 1440):                      # cloud on/off process
                x[k] = x[k - 1] if rng.random() > 0.04 else 1 - x[k - 1]
            tau = np.where(x > 0, 0.35, 1.05)             # cloud edge enhancement
            tau = np.convolve(tau, np.ones(3) / 3, mode="same")
        else:
            tau = 0.25 + 0.05 * rng.standard_normal(1440)
        true = np.clip(cs * tau, 0, None)
        out[name] = {"doy": doy, "cz": cz, "clear_sky": cs, "true": true}
    return out


def faulty_clear_day() -> dict:
    """The clear day with five faults: logger clock 60 min late, thermal
    offset at night, a mast shading the sensor at sunrise, two spikes, and
    a 25-minute gap; plus a 3 % soiling loss after a dust event at noon."""
    d = minute_days()["clear"]
    x = d["true"].copy()
    x = np.roll(x, 60)                                   # clock one hour late
    x = np.where(d["cz"] <= 0, x - 3.0, x)               # night offset -3 W/m2
    t = np.arange(1440)
    x[(t > 330) & (t < 375)] *= 0.25                     # mast shadow
    x[[700, 701]] = 1600.0                               # spikes
    x[(t >= 900) & (t < 925)] = np.nan                   # gap
    x[t >= 780] *= 0.97                                  # dust at 13:00
    return {**d, "measured": x}
