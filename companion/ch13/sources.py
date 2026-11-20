"""Chapter 13 - the wind data of the chapter (all synthetic, seeded).

* a ten-minute year at the Plant P mast, cups at 60, 80 and 100 m, vanes
  at 100 and 60 m, built from the data-pack hourly 100 m speeds with a
  day/night shear and veer, turbulence that falls with speed and at night
  (A-250); the 'true' values and the logged values with four faults (A-251):
  tower shadow on the 80 m cup, bearing wear of the 80 m cup from July,
  icing of the 100 m cup on cold days, a four-day logger outage in May;
* a lidar at 100, 120 and 150 m with its own scatter and outages (A-252);
* a reanalysis-like reference at 100 m: hourly for 2023 and 20 years of
  hourly series made by scaling and reshuffling (A-253).
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from companion.ch13 import common  # noqa: F401  (puts plantp on the path)
from plantp import datapack, physics

N = 8760 * 6
YEARS = 20


def ar1(n: int, tau: float, rng) -> np.ndarray:
    """Unit-variance first-order autoregressive noise, time scale tau steps."""
    phi = np.exp(-1 / tau)
    e = rng.standard_normal(n) * np.sqrt(1 - phi ** 2)
    x = np.empty(n)
    x[0] = rng.standard_normal()
    for k in range(1, n):
        x[k] = phi * x[k - 1] + e[k]
    return x


def hub_density(p_hpa, t_c, dz: float = 98.0) -> np.ndarray:
    """Air density at the hub from station pressure and 2 m temperature:
    pressure reduced over dz, temperature by the standard lapse (D-017)."""
    t_hub = np.asarray(t_c, float) - 0.0065 * dz
    p_hub = np.asarray(p_hpa, float) * np.exp(
        -9.81 * dz / (287.05 * (273.15 + 0.5 * (np.asarray(t_c, float) + t_hub))))
    return np.asarray(physics.air_density(p_hub, t_hub))


@lru_cache(maxsize=1)
def mast_year(seed: int = 141) -> dict:
    rng = np.random.default_rng(seed)
    h = datapack.load_hourly()
    v_h = h["ws_100m_ms"].to_numpy(float)
    wd_h = h["wd_100m_deg"].to_numpy(float)
    t_h = h["t_air_c"].to_numpy(float)
    p_h = h["p_hpa"].to_numpy(float)
    hour = np.repeat(np.arange(8760) % 24, 6)
    day = np.repeat(np.arange(8760) // 24, 6)
    v100 = np.clip(np.repeat(v_h, 6) * (1 + 0.05 * ar1(N, 3.0, rng)), 0.2, None)
    wd = (np.repeat(wd_h, 6) + 6 * rng.standard_normal(N)) % 360
    daytime = (hour >= 9) & (hour < 17)
    night = (hour >= 20) | (hour < 6)
    alpha = np.where(daytime, 0.10, np.where(night, 0.30, 0.20))
    alpha = alpha + 0.04 * np.cos(np.radians(wd - 285)) + 0.03 * rng.standard_normal(N)
    v80 = v100 * (80 / 100) ** alpha
    v60 = v100 * (60 / 100) ** alpha
    ti = (0.06 + 0.9 / np.maximum(v100, 1.0)) * np.where(night, 0.75, 1.0)
    sd100 = ti * v100 * (1 + 0.15 * rng.standard_normal(N)).clip(0.5)
    veer = np.where(night, 10.0, 2.0) + 2 * rng.standard_normal(N)
    wd60 = (wd - veer) % 360
    t = np.repeat(t_h, 6) + 0.3 * rng.standard_normal(N)
    p = np.repeat(p_h, 6)
    true = {"v100": v100, "v80": v80, "v60": v60, "sd100": sd100,
            "wd100": wd, "wd60": wd60, "t": t, "p": p,
            "rho": np.asarray(physics.air_density(p, t)),
            "rho_hub": hub_density(p, t), "hour": hour, "day": day}
    # ---- logged values with faults (A-251)
    m80 = v80.copy()
    shadow = ((wd - 300) % 360 < 40)                     # mast upwind of the boom
    m80[shadow] *= 0.93
    month = day * 12 // 365
    wear = month >= 6                                    # from July
    m80[wear] *= 1 - 0.006 * (month[wear] - 5)           # -0.6 % a month
    m80[wear & (m80 < 4.0)] = np.clip(m80[wear & (m80 < 4.0)] - 0.4, 0, None)
    m100, s100 = v100.copy(), sd100.copy()
    cold = t < -0.5
    iced = np.zeros(N, bool)
    for start in rng.choice(np.flatnonzero(cold[:-60]), 6, replace=False):
        iced[start:start + 48] = True                    # eight-hour events
    m100[iced] = m100[iced] * 0.55
    s100[iced] = 0.02
    outage = (day >= 130) & (day < 134)
    logged = {"v100": m100, "v80": m80, "v60": v60.copy(), "sd100": s100,
              "wd100": wd.copy(), "wd60": wd60.copy(), "t": t.copy(), "p": p.copy()}
    for k in logged:
        logged[k] = np.where(outage, np.nan, logged[k])
    return {"true": true, "logged": logged, "iced": iced, "outage": outage,
            "shadow": shadow, "wear": wear}


@lru_cache(maxsize=1)
def lidar(seed: int = 142) -> dict:
    """Lidar at 100, 120, 150 m: scatter 2 %, bias +0.5 % (A-252), 8 %
    of records lost (low aerosol, rain, fog) in blocks."""
    rng = np.random.default_rng(seed)
    m = mast_year()["true"]
    alpha = np.log(m["v100"] / m["v60"]) / np.log(100 / 60)
    out = {}
    for z in (100, 120, 150):
        v = m["v100"] * (z / 100) ** alpha
        out[z] = v * 1.005 * (1 + 0.02 * rng.standard_normal(N))
    lost = np.zeros(N, bool)
    while lost.mean() < 0.08:
        k = int(rng.integers(0, N - 36))
        lost[k:k + int(rng.integers(6, 36))] = True
    for z in out:
        out[z] = np.where(lost, np.nan, out[z])
    out["lost"] = lost
    return out


@lru_cache(maxsize=1)
def reference(seed: int = 143) -> dict:
    """Reanalysis-like hourly 100 m speed at a grid point near the site:
    0.92 of the site speed with 12 % scatter and a 3 h smoothing; 20 years
    made by scaling 2023 by an annual anomaly (sd 3.5 %) and reshuffling
    days within each month (A-253). 2023 is 2.0 % below the long term."""
    rng = np.random.default_rng(seed)
    h = datapack.load_hourly()
    v = h["ws_100m_ms"].to_numpy(float)
    wd = h["wd_100m_deg"].to_numpy(float)
    smooth = np.convolve(v, np.ones(3) / 3, mode="same")
    ref = 0.92 * smooth * (1 + 0.12 * ar1(8760, 4.0, rng))
    ref = np.clip(ref, 0.2, None)
    anom = 0.035 * rng.standard_normal(YEARS)
    anom[-1] = -0.020                                    # 2023 below average
    anom[:-1] -= anom.sum() / (YEARS - 1)                # long-term mean = 1
    months = h.index.month.to_numpy() - 1
    days = np.arange(8760) // 24
    years = []
    for y in range(YEARS):
        if y == YEARS - 1:
            years.append(ref.copy())
            continue
        order = np.arange(365)
        for m in range(12):
            md = np.unique(days[months == m])
            order[md] = rng.permutation(md)
        idx = (order[days] * 24 + np.arange(8760) % 24)
        years.append(ref[idx] * (1 + anom[y]) / (1 + anom[-1]))
    return {"hourly_2023": ref, "wd_2023": wd, "years": np.arange(2004, 2024),
            "long": np.array(years), "anom": anom}
