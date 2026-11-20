#!/usr/bin/env python3
"""Generate the Plant P Reference Data Pack (releases 1.0.0 and 1.1.0).

    python companion/plantp_data/generate_release.py --release 1.1.0          # writes 1.1.0/
    python companion/plantp_data/generate_release.py --release 1.0.0 --check  # compare hashes

Release 1.1.0 (chapter 5) keeps every 1.0.0 time series byte-identical and adds the full
assumptions ledger, raw sample files with documented defects, and a synthetic asset register.

Everything in the pack is SYNTHETIC teaching data for the fictional Plant P.
It describes no real site, no real grid and no real product. The generator is
seeded, so the same release always produces byte-identical files; the manifest
stores a SHA-256 checksum for each of them.

Models used (documented so that readers can reproduce and criticise them):
  sun      Cooper declination, Spencer equation of time, hour angle; the site
           meridian equals the time-zone meridian (no longitude correction)
  clear    Haurwitz clear-sky model  GHI_cs = 1098 mu exp(-0.057/mu)   [W/m2]
  clouds   3-state daily Markov chain (clear / partly / overcast) + hourly noise
  split    Erbs correlation  kt -> diffuse fraction  -> DHI, DNI
  temp     annual + daily sinusoid + AR(1) noise
  wind     AR(1) Gaussian process mapped to a Weibull distribution (k = 2.1),
           scale varying with season and hour; power-law shear to 80 m and 60 m
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
from datetime import datetime, timedelta

import numpy as np

RELEASES = {"1.0.0": "2026-11-14", "1.1.0": "2026-11-15"}
RELEASE = "1.0.0"           # set by main() from --release
CREATED = RELEASES[RELEASE]
SEED = 20260101

# ---- fictional site (teaching assumptions, see assumptions.csv) -------------
LAT_DEG = 34.0          # latitude, degrees north
ELEV_M = 1200.0         # elevation above sea level
YEAR = 2023             # a non-leap calendar year, used only as a label
UTC_OFFSET = "+04:00"   # fixed offset, no daylight saving
HUB_HEIGHT_M = 100.0

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, RELEASE)

HOURLY_COLUMNS = ["timestamp", "ghi_wm2", "dni_wm2", "dhi_wm2", "t_air_c",
                  "ws_100m_ms", "ws_80m_ms", "ws_60m_ms", "wd_100m_deg", "p_hpa", "qc_flag"]


# ---------------------------------------------------------------- solar model
def declination_rad(n: np.ndarray) -> np.ndarray:
    """Cooper (1969): n = day of year, 1..365."""
    return np.radians(23.45) * np.sin(2 * np.pi * (284 + n) / 365)


def equation_of_time_min(n: np.ndarray) -> np.ndarray:
    """Spencer (1971), minutes."""
    b = 2 * np.pi * (n - 1) / 365
    return 229.18 * (0.000075 + 0.001868 * np.cos(b) - 0.032077 * np.sin(b)
                     - 0.014615 * np.cos(2 * b) - 0.04089 * np.sin(2 * b))


def cos_zenith(n: np.ndarray, clock_hour: np.ndarray) -> np.ndarray:
    """Cosine of the solar zenith angle; clock_hour may be fractional."""
    solar_hour = clock_hour + equation_of_time_min(n) / 60.0
    omega = np.radians(15.0 * (solar_hour - 12.0))
    phi, delta = math.radians(LAT_DEG), declination_rad(n)
    return np.sin(phi) * np.sin(delta) + np.cos(phi) * np.cos(delta) * np.cos(omega)


def extraterrestrial_normal(n: np.ndarray) -> np.ndarray:
    return 1361.0 * (1 + 0.033 * np.cos(2 * np.pi * n / 365))


def haurwitz(mu: np.ndarray) -> np.ndarray:
    out = np.zeros_like(mu)
    up = mu > 0
    out[up] = 1098.0 * mu[up] * np.exp(-0.057 / mu[up])
    return out


def erbs_diffuse_fraction(kt: np.ndarray) -> np.ndarray:
    kd = np.where(kt <= 0.22, 1 - 0.09 * kt,
                  0.9511 - 0.1604 * kt + 4.388 * kt**2 - 16.638 * kt**3 + 12.336 * kt**4)
    return np.where(kt > 0.80, 0.165, kd)


# ------------------------------------------------------------- random helpers
def ar1(rng: np.random.Generator, size: int, rho: float) -> np.ndarray:
    """Stationary AR(1) series with unit variance."""
    eps = rng.standard_normal(size)
    z = np.empty(size)
    z[0] = eps[0]
    scale = math.sqrt(1 - rho * rho)
    for i in range(1, size):
        z[i] = rho * z[i - 1] + scale * eps[i]
    return z


def normal_cdf(z: np.ndarray) -> np.ndarray:
    return 0.5 * (1 + np.vectorize(math.erf)(z / math.sqrt(2)))


def daily_states(rng: np.random.Generator, probs_by_day: np.ndarray, stay: float) -> np.ndarray:
    """Markov chain over days: keep yesterday's state with probability `stay`,
    otherwise draw from that day's seasonal distribution."""
    days = probs_by_day.shape[0]
    states = np.empty(days, dtype=int)
    u_stay, u_draw = rng.random(days), rng.random(days)
    for d in range(days):
        if d > 0 and u_stay[d] < stay:
            states[d] = states[d - 1]
        else:
            states[d] = int(np.searchsorted(np.cumsum(probs_by_day[d]), u_draw[d]))
            states[d] = min(states[d], probs_by_day.shape[1] - 1)
    return states


# ------------------------------------------------------------------ generator
def generate_hourly() -> dict[str, np.ndarray]:
    rng = np.random.default_rng(SEED)
    hours = 8760
    idx = np.arange(hours)
    day = idx // 24                 # 0..364
    n = day + 1                     # day of year
    hour = idx % 24                 # hour-beginning clock hour

    # --- sun: average over six 10-minute sub-steps of each hour
    sub = (np.arange(6) + 0.5) / 6.0
    mu = np.stack([np.clip(cos_zenith(n, hour + s), 0, None) for s in sub])
    mu_mean = mu.mean(axis=0)
    ghi_clear = np.stack([haurwitz(m) for m in mu]).mean(axis=0)
    g0h = extraterrestrial_normal(n) * mu_mean

    # --- clouds: seasonal weights (0 = mid-winter ... 1 = mid-summer)
    summer = 0.5 * (1 + np.cos(2 * np.pi * (np.arange(365) + 1 - 172) / 365))
    p_clear = 0.50 + 0.35 * summer
    p_over = 0.20 - 0.17 * summer
    probs = np.column_stack([p_clear, 1 - p_clear - p_over, p_over])
    sky = daily_states(rng, probs, stay=0.60)                      # 0 clear, 1 partly, 2 overcast
    lo = np.array([0.93, 0.55, 0.15])[sky]
    hi = np.array([1.00, 0.85, 0.40])[sky]
    kc_day = lo + (hi - lo) * rng.random(365)
    sigma = np.array([0.02, 0.18, 0.10])[sky]
    noise = np.exp(sigma[day] * rng.standard_normal(hours) - 0.5 * sigma[day] ** 2)
    ghi = np.clip(ghi_clear * kc_day[day] * noise, 0, 1.05 * ghi_clear)

    kt = np.divide(ghi, g0h, out=np.zeros(hours), where=g0h > 1.0)
    dhi = erbs_diffuse_fraction(np.clip(kt, 0, 1)) * ghi
    low_sun = mu_mean < 0.06
    dhi = np.where(low_sun, ghi, dhi)
    dni = np.where(low_sun, 0.0, np.divide(ghi - dhi, mu_mean, out=np.zeros(hours),
                                           where=mu_mean > 0))
    dni = np.clip(dni, 0, 1050.0)

    # --- air temperature
    t_air = (17.0 + 12.0 * np.cos(2 * np.pi * (n - 200) / 365)
             + 6.5 * np.cos(2 * np.pi * (hour + 0.5 - 15) / 24)
             + 2.2 * ar1(rng, hours, 0.985))

    # --- wind at hub height (100 m)
    scale = (7.7 * (1 + 0.12 * np.cos(2 * np.pi * (n - 30) / 365))
             * (1 + 0.10 * np.cos(2 * np.pi * (hour + 0.5 - 2) / 24)))
    u = np.clip(normal_cdf(ar1(rng, hours, 0.96)), 1e-9, 1 - 1e-9)
    ws100 = scale * (-np.log(1 - u)) ** (1 / 2.1)
    alpha = 0.17 + 0.05 * np.cos(2 * np.pi * (hour + 0.5 - 3) / 24)   # shear exponent
    ws80 = ws100 * (80 / HUB_HEIGHT_M) ** alpha * (1 + 0.015 * rng.standard_normal(hours))
    ws60 = ws100 * (60 / HUB_HEIGHT_M) ** alpha * (1 + 0.015 * rng.standard_normal(hours))

    # --- wind direction: two regimes (290 deg prevailing, 110 deg secondary)
    regime = daily_states(rng, np.tile([0.80, 0.20], (365, 1)), stay=0.70)
    centre = np.array([290.0, 110.0])[regime][day]
    wd = np.mod(centre + 28.0 * ar1(rng, hours, 0.98), 360.0)

    # --- station pressure at 1200 m
    p = 879.0 + 4.0 * ar1(rng, hours, 0.995)

    wd_int = np.mod(np.rint(wd), 360).astype(int)
    return {
        "ghi_wm2": np.round(ghi, 1), "dni_wm2": np.round(dni, 1), "dhi_wm2": np.round(dhi, 1),
        "t_air_c": np.round(t_air, 1),
        "ws_100m_ms": np.round(ws100, 2), "ws_80m_ms": np.round(ws80, 2),
        "ws_60m_ms": np.round(ws60, 2),
        "wd_100m_deg": wd_int, "p_hpa": np.round(p, 1),
        "qc_flag": np.zeros(hours, dtype=int),
    }


def timestamps() -> list[str]:
    t0 = datetime(YEAR, 1, 1)
    return [(t0 + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%S") + UTC_OFFSET
            for i in range(8760)]


FORMATS = {"ghi_wm2": "{:.1f}", "dni_wm2": "{:.1f}", "dhi_wm2": "{:.1f}", "t_air_c": "{:.1f}",
           "ws_100m_ms": "{:.2f}", "ws_80m_ms": "{:.2f}", "ws_60m_ms": "{:.2f}",
           "wd_100m_deg": "{:d}", "p_hpa": "{:.1f}", "qc_flag": "{:d}"}


def hourly_csv(data: dict[str, np.ndarray], rows: range | list[int]) -> str:
    ts = timestamps()
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(HOURLY_COLUMNS)
    for i in rows:
        w.writerow([ts[i]] + [FORMATS[c].format(data[c][i].item()) for c in HOURLY_COLUMNS[1:]])
    return buf.getvalue()


# ------------------------------------------------------------ equipment data
ROTOR_D_M = 150.0
RATED_KW = 5000.0


def power_curve() -> list[tuple[float, int]]:
    """Fictional 5 MW / 150 m turbine at standard air density 1.225 kg/m3."""
    area = math.pi * (ROTOR_D_M / 2) ** 2
    rows = []
    for k in range(0, 61):                       # 0.0 .. 30.0 m/s in 0.5 m/s bins
        v = 0.5 * k
        if v < 3.0 or v > 25.0:
            p = 0.0
        else:
            cp = 0.46 * (1 - math.exp(-(v - 2.2) / 1.2))
            raw = 0.5 * 1.225 * area * cp * v**3 / 1000.0          # kW
            p = (raw ** -6 + RATED_KW ** -6) ** (-1 / 6)           # smooth knee to rated
            if v >= 13.0:
                p = RATED_KW
        rows.append((v, int(round(p))))
    return rows


def power_curve_csv() -> str:
    lines = ["wind_speed_ms,power_kw"]
    lines += [f"{v:.1f},{p:d}" for v, p in power_curve()]
    return "\n".join(lines) + "\n"


PV_MODULE_YML = """\
# Fictional PV module for Plant P teaching examples. Not a real product.
id: PVM-550
status: synthetic            # vendor-style datasheet values invented for teaching
technology: monocrystalline silicon, 144 half-cut cells, monofacial
stc:                         # standard test conditions: 1000 W/m2, 25 C cell, AM1.5
  p_max_w: 550.0
  v_mp_v: 41.96
  i_mp_a: 13.11
  v_oc_v: 49.90
  i_sc_a: 13.98
  efficiency_pct: 21.29
power_tolerance_w: [0, 5]
temperature_coefficients:    # percent per degree Celsius
  p_max_pct_per_c: -0.35
  v_oc_pct_per_c: -0.27
  i_sc_pct_per_c: 0.048
noct_c: 45.0
max_system_voltage_v: 1500
max_series_fuse_a: 25
dimensions_mm: {length: 2278, width: 1134, thickness: 35}
mass_kg: 28.0
"""

WIND_TURBINE_YML = """\
# Fictional wind turbine for Plant P teaching examples. Not a real product.
id: WT-5.0-150
status: synthetic
rated_power_kw: 5000
rotor_diameter_m: 150.0
hub_height_m: 100.0
cut_in_ms: 3.0
rated_wind_speed_ms: 13.0     # speed from which the curve is flat at rated power
cut_out_ms: 25.0
reference_air_density_kgm3: 1.225
power_curve_file: wind_turbine_WT-5.0-150_power_curve.csv
count_in_plant_p: 12          # 12 x 5 MW = 60 MW
"""

SEED_RATINGS_CSV = """\
id,item,value,unit,status,note
SR-01,PV array capacity (DC),60,MWp,assumed,teaching seed from the book plan
SR-02,PV inverter capacity (AC),50,MW,assumed,teaching seed from the book plan
SR-03,Onshore wind capacity (AC),60,MW,assumed,teaching seed from the book plan
SR-04,Collector nominal voltage,33,kV,assumed,teaching seed from the book plan
SR-05,Point-of-connection nominal voltage,132,kV,assumed,teaching seed from the book plan
SR-06,Point-of-connection export limit,100,MW,assumed,teaching seed from the book plan
SR-07,Optional BESS power (scenario S1),20,MW,assumed,nominal at beginning of life
SR-08,Optional BESS energy (scenario S1),40,MWh,assumed,nominal at beginning of life
"""

ASSUMPTIONS_CSV = """\
id,quantity,value,unit,status,source,introduced_in,note
A-001,Site latitude,34.0,deg N,assumed,data pack 1.0.0,ch01,fictional; no longitude is defined (non-geolocated)
A-002,Site elevation,1200,m,assumed,data pack 1.0.0,ch01,fictional
A-003,Time zone of all timestamps,UTC+04:00,-,assumed,data pack 1.0.0,ch01,fixed offset; no daylight saving; site meridian = zone meridian
A-004,Nominal grid frequency,50,Hz,assumed,data pack 1.0.0,ch01,teaching value
A-005,Wind turbine count and rating,12 x 5,MW,assumed,data pack 1.0.0,ch01,fictional turbine WT-5.0-150
A-006,Wind turbine hub height,100,m,assumed,data pack 1.0.0,ch01,equals the top measurement height
A-007,PV module,PVM-550,-,synthetic,data pack 1.0.0,ch01,fictional 550 Wp module
A-008,PV DC/AC ratio,1.2,-,assumed,derived from SR-01 and SR-02,ch01,60 MWp / 50 MW
A-009,BESS usable state-of-charge window (S1),10 to 90,percent,assumed,scenario S1,ch01,usable 32 MWh at beginning of life
A-010,BESS round-trip efficiency AC to AC (S1),86,percent,assumed,scenario S1,ch01,one-way 92.7 percent
A-011,BESS capacity fade (S1),2.0,percent per year,assumed,scenario S1,ch01,linear teaching model
A-012,BESS charging source (S1),on-site PV and wind only,-,assumed,scenario S1,ch01,grid charging NOT permitted unless a scenario says so
A-013,Hourly resource data,synthetic 8760 h,-,synthetic,generate_release.py seed 20260101,ch01,replaced by measured data in later scenarios
"""

SCENARIO_S0 = """\
# Scenario S0: Plant P without battery storage (the comparison case).
id: S0
name: no-BESS
status: assumed
pv: {dc_mwp: 60, ac_mw: 50}
wind: {ac_mw: 60, turbines: 12, turbine_id: WT-5.0-150}
export_limit_mw: 100
bess: null
"""

SCENARIO_S1 = """\
# Scenario S1: Plant P with battery storage. Every BESS exercise must state
# these values (or the ones it changes) explicitly.
id: S1
name: BESS
status: assumed
pv: {dc_mwp: 60, ac_mw: 50}
wind: {ac_mw: 60, turbines: 12, turbine_id: WT-5.0-150}
export_limit_mw: 100
bess:
  power_mw: 20
  energy_mwh_nominal_bol: 40          # beginning of life
  soc_window_pct: [10, 90]            # usable state-of-charge window
  usable_energy_mwh_bol: 32
  roundtrip_efficiency_ac_pct: 86     # one-way 92.7 percent
  capacity_fade_pct_per_year: 2.0     # linear teaching model
  reserve_mwh: 0                      # no energy held back for services by default
  charging_source: on-site PV and wind only
  grid_charging_permitted: false
"""

DATA_DICTIONARY_CSV = """\
file,column,unit,description,valid_range,status
timeseries/plantp_hourly_8760.csv,timestamp,ISO 8601,start of the hour in local standard time with fixed offset +04:00,2023-01-01T00:00:00+04:00 to 2023-12-31T23:00:00+04:00,synthetic
timeseries/plantp_hourly_8760.csv,ghi_wm2,W/m2,global horizontal irradiance; mean over the hour,0 to 1200,synthetic
timeseries/plantp_hourly_8760.csv,dni_wm2,W/m2,direct normal irradiance; mean over the hour,0 to 1050,synthetic
timeseries/plantp_hourly_8760.csv,dhi_wm2,W/m2,diffuse horizontal irradiance; mean over the hour,0 to 700,synthetic
timeseries/plantp_hourly_8760.csv,t_air_c,degC,air temperature at 2 m; mean over the hour,-25 to 50,synthetic
timeseries/plantp_hourly_8760.csv,ws_100m_ms,m/s,wind speed at 100 m (hub height); mean over the hour,0 to 45,synthetic
timeseries/plantp_hourly_8760.csv,ws_80m_ms,m/s,wind speed at 80 m; mean over the hour,0 to 45,synthetic
timeseries/plantp_hourly_8760.csv,ws_60m_ms,m/s,wind speed at 60 m; mean over the hour,0 to 45,synthetic
timeseries/plantp_hourly_8760.csv,wd_100m_deg,deg,wind direction at 100 m; direction the wind blows FROM; 0 = north; clockwise,0 to 359,synthetic
timeseries/plantp_hourly_8760.csv,p_hpa,hPa,station air pressure,840 to 920,synthetic
timeseries/plantp_hourly_8760.csv,qc_flag,-,quality flag: 0 valid; 1 gap-filled; 2 suspect (all 0 in this clean release),0 to 2,synthetic
equipment/wind_turbine_WT-5.0-150_power_curve.csv,wind_speed_ms,m/s,hub-height wind speed at the centre of a 0.5 m/s bin,0 to 30,synthetic
equipment/wind_turbine_WT-5.0-150_power_curve.csv,power_kw,kW,electrical power at air density 1.225 kg/m3,0 to 5000,synthetic
"""

README_MD = """\
# Plant P Reference Data Pack — release 1.0.0

Synthetic, non-geolocated teaching data for the fictional hybrid wind–solar
plant "Plant P" of the book. Nothing here describes a real site, grid or
product, and nothing here is a recommended design.

| Path | Content |
|---|---|
| `manifest.json` | release id, seed, site assumptions, SHA-256 of every file |
| `seed_ratings.csv` | the plant's seed ratings (60 MWp / 50 MW PV, 60 MW wind, 33/132 kV, 100 MW export, optional 20 MW / 40 MWh BESS) |
| `assumptions.csv` | the assumptions ledger: id, value, unit, status, source, chapter |
| `scenarios/S0-no-bess.yml`, `scenarios/S1-bess.yml` | the two named scenarios |
| `timeseries/plantp_hourly_8760.csv` | one non-leap year of hourly irradiance, temperature, wind and pressure |
| `timeseries/subset_*.csv` | one summer day, one winter day and one spring week for hand calculation |
| `equipment/` | fictional PV module and wind turbine data |
| `data_dictionary.csv` | every column: unit, meaning, valid range, status |
| `expected_results.json` | summary values the test-suite reproduces |
| `CHANGELOG.md` | what changed, why, and which book artefacts depend on it |

Status labels used everywhere: `synthetic`, `assumed`, `measured`, `vendor`, `verified`.
Timestamps mark the START of each hour, local standard time, fixed offset +04:00.

Regenerate or verify: `python companion/plantp_data/generate_release.py [--check]`.

---

**فارسی.** این بسته، دادهٔ **ساختگی** و بدونِ مختصاتِ جغرافیاییِ «نیروگاهِ P» است و فقط برای
آموزش ساخته شده است؛ هیچ ساختگاه، شبکه یا محصولِ واقعی را توصیف نمی‌کند. هر مثالِ کتاب
شمارهٔ انتشارِ این بسته و نامِ سناریو (S0 بدونِ باتری، S1 با باتری) را ذکر می‌کند.
"""

CHANGELOG_MD = """\
# Changelog — Plant P Reference Data Pack

## 1.0.0 — 2026-11-14
- First release: seed ratings, assumptions ledger A-001..A-013, scenarios S0 and S1,
  synthetic hourly resource year (seed 20260101), three hand-calculation subsets,
  fictional PV module PVM-550 and wind turbine WT-5.0-150 with power curve.
- Reason: baseline for the book's worked examples.
- Dependent artefacts: none yet.
"""


# --------------------------------------------------------- release 1.1.0 additions
# id, quantity, value, unit, status, source, introduced_in, note
LEDGER_1_1 = [
    ("A-014", "Strings per combiner box", "24", "-", "assumed", "chapter 6 text", "ch06", ""),
    ("A-015", "Modules per string", "26", "-", "assumed", "chapter 6 text", "ch06", ""),
    ("A-016", "Minimum cell temperature for the voltage check", "-10", "degC", "assumed",
     "chapter 6 text", "ch06", "site climate data replace it (chapter 12)"),
    ("A-017", "Maximum DC system voltage", "1500", "V", "assumed", "chapter 6 text", "ch06", ""),
    ("A-018", "Combiner-box-to-inverter feeder", "180 m aluminium", "-", "assumed",
     "chapter 6 text", "ch06", ""),
    ("A-019", "Conductor temperature for DC loss calculations", "50", "degC", "assumed",
     "chapter 6 text", "ch06", ""),
    ("A-020", "Inverter MPPT voltage range", "850 to 1300", "V", "assumed", "chapter 6 text",
     "ch06", ""),
    ("A-021", "Feeder voltage-drop target at STC", "1", "percent", "assumed", "chapter 6 text",
     "ch06", "a design target, not a rule"),
    ("A-022", "Mean one-way string cable", "70 m copper 4 mm2", "-", "assumed",
     "chapter 6 text", "ch06", ""),
    ("A-023", "Wind direction convention", "from geographic north, clockwise, direction FROM",
     "deg", "assumed", "chapter 2 text", "ch02", "convention"),
    ("A-024", "Active-power sign", "export at the point of connection positive; "
     "battery discharge positive", "-", "assumed", "chapter 2 text", "ch02", "convention"),
    ("A-025", "Interval label", "start of interval; interval-ending data shifted on import",
     "-", "assumed", "chapter 2 text", "ch02", "convention; see raw/ files of 1.1.0"),
    ("A-026", "Data units", "SI; unit in the column header; MWp is a label only", "-",
     "assumed", "chapter 2 text", "ch02", "convention"),
    ("A-027", "Capacity-factor basis", "own AC rating per technology; plant on the "
     "connection limit; hours from the data", "-", "assumed", "chapter 2 text", "ch02",
     "convention"),
    ("A-028", "Air density in the screening model", "power curve at 1.225 kg/m3, uncorrected",
     "-", "assumed", "chapter 2 text", "ch02", "superseded for the dossier by D-008 (ch04)"),
    ("A-029", "Resource uncertainty (teaching)", "speed 3; annual irradiation 4; independent",
     "percent", "assumed", "chapter 2 text", "ch02", ""),
    ("A-030", "Document numbering and revision scheme", "PLP-DIS-TYP-NNNN", "-", "assumed",
     "chapter 2 text", "ch02", "see tbl-ch02-doc-scheme"),
    ("A-031", "PV table geometry", "slope 4.6 m; tilt 25 deg; facing south", "-", "assumed",
     "chapter 3 text", "ch03", ""),
    ("A-032", "33 kV cable impedance", "0.125 + j0.110", "ohm/km", "assumed",
     "chapter 3 text", "ch03", "240 mm2 class; fictional"),
    ("A-033", "Cable thermal model", "time constant 0.5 h (buried 3 h); 40 K at 552.5 A", "-",
     "assumed", "chapter 3 text", "ch03", ""),
    ("A-034", "Transformer two-state thermal model", "C 2e5 and 4e6 J/K; G 4000 and 2500 W/K",
     "-", "assumed", "chapter 3 text", "ch03", "winding and oil"),
    ("A-035", "Hourly price profile", "synthetic", "u/MWh", "synthetic", "chapter 3 text",
     "ch03", "fictional currency unit u"),
    ("A-036", "Annual maxima of 10-min mean wind", "30 values, Gumbel mu 26, beta 2.5", "m/s",
     "synthetic", "chapter 3 text", "ch03", "fixed seed"),
    ("A-037", "Plant costs", "capex 100 million u; opex 2.75 million u/yr; 7 %; 25 years",
     "u", "assumed", "chapter 3 text", "ch03", "fictional money"),
    ("A-038", "Cable cost model and value of losses", "60 000 + 300 A u/km; 40 u/MWh", "u",
     "assumed", "chapter 3 text", "ch03", "fictional money"),
    ("A-039", "Turbine MTBF and MTTR", "2000; 60", "h", "assumed", "chapter 3 text", "ch03",
     ""),
    ("A-040", "Inverter current harmonics", "5th 0.04; 7th 0.03", "pu", "assumed",
     "chapter 3 text", "ch03", ""),
    ("A-041", "Local coordinates of three turbines, mast and substation", "relative to a "
     "reference meridian", "deg", "synthetic", "chapter 3 text", "ch03", "not geolocated"),
    ("A-042", "Gearbox condition-monitoring rates", "prior 2; sensitivity 90; false alarm 5",
     "percent", "assumed", "chapter 3 text", "ch03", ""),
    ("A-043", "Soil thermal diffusivity and cable depth", "0.5e-6 m2/s; 0.8 m", "-",
     "assumed", "chapter 3 text", "ch03", ""),
    ("A-044", "Availability of breaker, transformer, export line", "0.999; 0.995; 0.997",
     "-", "assumed", "chapter 3 text", "ch03", ""),
    ("A-045", "Uncertain factors of the simple energy model", "3; 2; 4; 2", "percent",
     "assumed", "chapter 3 text", "ch03", "one standard deviation each"),
    ("A-046", "Thrust coefficient and rotor-nacelle mass", "C_T 0.8; 350 t", "-", "assumed",
     "chapter 4 text", "ch04", ""),
    ("A-047", "Rotor speed, gearbox ratio, drivetrain efficiencies",
     "10.5 rpm; 1:110; 0.94", "-", "assumed", "chapter 4 text", "ch04", ""),
    ("A-048", "Blade mass and length", "20 t; 73 m; mass tapering to the tip", "-", "assumed",
     "chapter 4 text", "ch04", ""),
    ("A-049", "Gust and force coefficient", "30 m/s; 1.2", "-", "assumed", "chapter 4 text",
     "ch04", ""),
    ("A-050", "Tower geometry and steel", "uniform tube 100 m; E 210 GPa; 7850 kg/m3", "-",
     "assumed", "chapter 4 text", "ch04", ""),
    ("A-051", "Sample busbar and heat-transfer coefficient", "80 x 10 mm; h 10 W/m2K; 40 C",
     "-", "assumed", "chapter 4 text", "ch04", ""),
    ("A-052", "Cable geometry and dielectric constants", "r 10/18 mm; eps_r 2.3; tan d 4e-4",
     "-", "assumed", "chapter 4 text", "ch04", ""),
    ("A-053", "Export transformer core", "0.5 m2; 1.7 T", "-", "assumed", "chapter 4 text",
     "ch04", ""),
    ("A-054", "Short-circuit current, peak factor, busbar spacing", "21.9 kA; 1.8; 0.3 m",
     "-", "assumed", "chapter 4 text", "ch04", ""),
    ("A-055", "Sound power level per turbine", "105", "dB(A)", "assumed", "chapter 4 text",
     "ch04", "as in chapter 3"),
    ("A-056", "Tensile curve and sample bolt", "S355-like; M36 grade 10.9", "-", "synthetic",
     "chapter 4 text", "ch04", ""),
    ("A-057", "Tracker torque tube", "D 140 mm; t 4 mm; span 7 m", "-", "assumed",
     "chapter 4 text", "ch04", ""),
    ("A-058", "Fatigue, fracture, relaxation and corrosion data", "e.g. 71 MPa at 2e6, m 3",
     "-", "assumed", "chapter 4 text", "ch04", ""),
    ("A-059", "Material properties and selection scores", "indicative", "-", "assumed",
     "chapter 4 text", "ch04", "certified supplier data replace them"),
    ("A-060", "Prices, process costs, process-control data", "Cu 9.0 u/kg; Al 2.6 u/kg", "-",
     "assumed", "chapter 4 text", "ch04", "fictional money"),
    ("A-061", "Switchgear room and busbar temperature limit", "air + 15 K; 90 C", "-",
     "assumed", "chapter 4 text", "ch04", ""),
    ("A-062", "Contact-resistance growth model", "1.2 W/K; 0.08 1/yr at 40 C; 70 kJ/mol", "-",
     "assumed", "chapter 4 text", "ch04", ""),
    ("A-063", "Transformer core path and permeability", "6 m; mu_r 30 000; 175 turns", "-",
     "assumed", "chapter 4 text", "ch04", ""),
    ("A-064", "Cell internal resistance; inverter for cooling", "0.25 mOhm; 4.2 MW; 0.985",
     "-", "assumed", "chapter 4 text", "ch04", ""),
    ("A-065", "Insulation ageing", "Ea 100 kJ/mol; reference 90 C", "-", "assumed",
     "chapter 4 text", "ch04", ""),
    ("A-066", "Foundation concrete", "380 kg/m3 cement; 330 kJ/kg", "-", "assumed",
     "chapter 4 text", "ch04", ""),
    ("A-067", "Embodied-energy intensities", "steel 25; composite 100; Cu 60; concrete 1.5",
     "MJ/kg", "assumed", "chapter 4 text", "ch04", "indicative"),
    ("A-068", "PV mounting tolerance chain", "20; 3; 2; 1.5", "mm", "assumed",
     "chapter 4 text", "ch04", "plus-minus, uniform"),
    ("A-069", "Blade section", "r 50 m; chord 2 m; Cl 1.0; Cd 0.01; a 1/3", "-", "assumed",
     "chapter 4 text", "ch04", ""),
    ("A-070", "Power-module thermal resistances", "2 kW; 0.020; 0.010; 0.015 K/W", "-",
     "assumed", "chapter 4 text", "ch04", ""),
    ("A-071", "Cathodic-protection current", "0.5 A for 20 years", "-", "assumed",
     "chapter 4 text", "ch04", ""),
    ("A-072", "Glass strength Weibull parameters", "50 and 150 MPa; m 7", "-", "assumed",
     "chapter 4 text", "ch04", ""),
    ("A-073", "Chvorinov constant", "2.5", "min/cm2", "assumed", "chapter 4 text", "ch04", ""),
    ("A-074", "Transformer winding", "175 turns of 2.5 m; 3 A/mm2", "-", "assumed",
     "chapter 4 text", "ch04", ""),
    ("A-075", "Resistivity of materials", "orders of magnitude", "ohm m", "assumed",
     "chapter 4 text", "ch04", "indicative"),
    ("A-076", "Tower drag", "rho 1.05; v 11 m/s; alpha 0.171; Cd 0.6", "-", "assumed",
     "chapter 4 text", "ch04", ""),
    ("A-077", "Cable-screen earth fault", "35 mm2 Cu; 2 kA for 1 s from 70 C", "-",
     "assumed", "chapter 4 text", "ch04", ""),
    ("A-078", "Flange bolt pattern and moment swing", "140 x M36 on 4.7 m; +-20 MN m", "-",
     "assumed", "chapter 4 text", "ch04", ""),
    ("A-079", "Resin infusion", "mu 0.25 Pa s; phi 0.5; K 2e-10 m2; dP 0.9e5 Pa", "-",
     "assumed", "chapter 4 text", "ch04", ""),
    ("A-080", "Thermography camera setting", "joint 80 C; room 30 C; camera eps 0.95", "-",
     "assumed", "chapter 4 text", "ch04", ""),
    ("A-081", "Cable sheath in sun", "D 50 mm; absorptance 0.6; 1000 W/m2", "-", "assumed",
     "chapter 4 text", "ch04", ""),
    ("A-082", "Ultraviolet share and test-chamber intensity", "5 %; 60 W/m2", "-", "assumed",
     "chapter 4 text", "ch04", ""),
    ("A-083", "Faying-surface friction coefficient", "0.35; 8 x M36", "-", "assumed",
     "chapter 4 text", "ch04", ""),
    ("A-084", "Rain-erosion speed exponent", "7", "-", "assumed", "chapter 4 text", "ch04",
     ""),
    ("A-085", "Chemical composition of two steel heats", "see chapter 4", "-", "assumed",
     "chapter 4 text", "ch04", ""),
    ("A-086", "Process FMEA scores", "1 to 10", "-", "assumed", "chapter 4 text", "ch04", ""),
    ("A-087", "Sample foundation", "600 m3 concrete; 20 m square base; 800 m3 backfill", "-",
     "assumed", "chapter 4 text", "ch04", ""),
    ("A-088", "Flange flatness survey", "16 points on 4.7 m; seed 20260304", "-", "synthetic",
     "chapter 4 text", "ch04", ""),
    ("A-089", "Raw met-mast logger file", "10 min; interval-END labels; UTC+04:00 not written",
     "-", "synthetic", "raw/met_mast_10min_raw.csv", "ch05", "defects listed in the key file"),
    ("A-090", "PV SCADA export", "hourly kWh; UTC with Z; semicolon and decimal comma", "-",
     "synthetic", "raw/pv_scada_export.csv", "ch05", "one hour missing on purpose"),
    ("A-091", "Collector system for the loss calculator", "4 feeders x 6 km; 33 kV; pf 0.95; "
     "R20 0.10 ohm/km; 70 C", "-", "assumed", "chapter 5 text", "ch05", "equal shares"),
    ("A-092", "Export transformer losses", "120 MVA; no-load 60 kW; load 400 kW at rated",
     "-", "assumed", "chapter 5 text", "ch05", "fictional"),
    ("A-093", "Cash-flow inputs", "50 u/MWh; 0.5 %/yr; 70 % debt at 6 % over 15 years; "
     "25 years; no tax", "-", "assumed", "chapter 5 text", "ch05", "fictional money"),
    ("A-094", "Asset register", "teaching tag scheme PLP-SYS-nn[-XXX]", "-", "synthetic",
     "assets/asset_register_rev_A.csv", "ch05", "not a published designation standard"),
    ("A-095", "Mock CMMS", "fixed field names; 40-character text field", "-", "synthetic",
     "chapter 5 text", "ch05", "no vendor implied"),
    ("A-096", "Spreadsheet model sample", "cell formulas of a yield sheet", "-", "synthetic",
     "chapter 5 text", "ch05", ""),
    ("A-097", "PV model of chapter 5", "NOCT cell temperature; -0.35 %/K; k_other 0.90; "
     "inverter 0.98; horizontal irradiance", "-", "assumed", "chapter 5 text", "ch05",
     "refined in chapters 10 and 15"),
    ("A-098", "Measured first tower frequency", "0.221", "Hz", "synthetic",
     "chapter 5 text", "ch05", "invented commissioning value for the CAE example"),
    ("A-099", "Warranty, test and work-order records", "GEN, GBX, INV 5 years; "
     "transformers 2 years", "-", "synthetic", "chapter 5 text", "ch05",
     "asset-information laboratory"),
]


def ledger_csv() -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    for row in LEDGER_1_1:
        w.writerow(row)
    return ASSUMPTIONS_CSV + buf.getvalue()


RAW_START = 92 * 24          # 3 April 2023 00:00 local (hour index)
RAW_HOURS = 72               # three days


def raw_met_mast(data: dict[str, np.ndarray]) -> tuple[str, str]:
    """Ten-minute logger file derived from the hourly series, plus its defect key.

    The six values of each hour average to the published hourly value (zero-mean
    noise), so clean hours can be checked against the reference series."""
    rng = np.random.default_rng(SEED + 11)
    rows = []
    t0 = datetime(YEAR, 4, 3)
    for h in range(RAW_HOURS):
        i = RAW_START + h
        def sub(value, sd, digits):
            e = rng.standard_normal(6) * sd
            e -= e.mean()
            return [round(float(value) + x, digits) for x in e]
        ws100 = sub(data["ws_100m_ms"][i], 0.35, 2)
        ws80 = sub(data["ws_80m_ms"][i], 0.33, 2)
        ws60 = sub(data["ws_60m_ms"][i], 0.31, 2)
        wd = sub(data["wd_100m_deg"][i], 3.0, 0)
        tc = sub(data["t_air_c"][i], 0.15, 1)
        pp = sub(data["p_hpa"][i], 0.08, 1)
        g = data["ghi_wm2"][i]
        gg = sub(g, 0.06 * g, 1) if g > 0 else [0.0] * 6
        gg = [max(x, 0.0) for x in gg]
        for k in range(6):
            end = t0 + timedelta(hours=h, minutes=10 * (k + 1))
            sd = round(0.10 * max(ws100[k], 0.5) + 0.05 * abs(rng.standard_normal()), 2)
            rows.append([end.strftime("%Y-%m-%d %H:%M"), f"{ws100[k]:.2f}", f"{sd:.2f}",
                         f"{ws80[k]:.2f}", f"{ws60[k]:.2f}", f"{int(wd[k]) % 360:d}",
                         f"{tc[k]:.1f}", f"{pp[k]:.1f}", f"{gg[k]:.1f}"])
    pos = {r[0]: n for n, r in enumerate(rows)}
    key = []
    # D1 duplicate record
    n = pos["2023-04-03 06:00"]
    rows.insert(n + 1, list(rows[n]))
    key.append(("D1", "2023-04-03 06:00", "all", "duplicated record", "drop the copy"))
    pos = {r[0]: n for n, r in enumerate(rows)}
    # D2 gap of five records
    for stamp in ("2023-04-03 14:10", "2023-04-03 14:20", "2023-04-03 14:30",
                  "2023-04-03 14:40", "2023-04-03 14:50"):
        rows.pop(pos[stamp])
        pos = {r[0]: n for n, r in enumerate(rows)}
    key.append(("D2", "2023-04-03 14:10..14:50", "all", "five records missing",
                "hour 14:00 incomplete; do not average"))
    # D3 negative speed
    rows[pos["2023-04-04 03:20"]][4] = "-0.40"
    key.append(("D3", "2023-04-04 03:20", "ws60_avg", "negative wind speed", "flag 2"))
    # D4 stuck sensor
    for h, m in [(10, 10), (10, 20), (10, 30), (10, 40), (10, 50), (11, 0), (11, 10),
                 (11, 20), (11, 30), (11, 40), (11, 50), (12, 0)]:
        rows[pos[f"2023-04-04 {h:02d}:{m:02d}"]][3] = "7.32"
    key.append(("D4", "2023-04-04 10:10..12:00", "ws80_avg", "constant value (stuck)",
                "flag 2"))
    # D5 sentinel
    rows[pos["2023-04-04 18:30"]][6] = "-9999"
    key.append(("D5", "2023-04-04 18:30", "t_air", "sentinel -9999", "missing"))
    # D6 unit slip
    for m in ("08:10", "08:20", "08:30", "08:40", "08:50", "09:00"):
        r = rows[pos[f"2023-04-05 {m}"]]
        r[7] = f"{float(r[7]) / 10:.2f}"
    key.append(("D6", "2023-04-05 08:10..09:00", "p_air", "kPa written instead of hPa",
                "convert x10 with flag 1 or reject"))
    # D7 swapped order
    a, b = pos["2023-04-05 20:10"], pos["2023-04-05 20:20"]
    rows[a], rows[b] = rows[b], rows[a]
    key.append(("D7", "2023-04-05 20:10/20:20", "timestamp", "two records out of order",
                "sort, then check"))
    pos = {r[0]: n for n, r in enumerate(rows)}
    # D8 night offset of the pyranometer
    for m in ("02:10", "02:20", "02:30", "02:40", "02:50", "03:00"):
        rows[pos[f"2023-04-05 {m}"]][8] = "-1.6"
    key.append(("D8", "2023-04-05 02:10..03:00", "ghi", "small negative night values",
                "set to 0 with flag 1"))
    # D9 impossible direction
    rows[pos["2023-04-03 21:00"]][5] = "400"
    key.append(("D9", "2023-04-03 21:00", "wd100_avg", "direction outside 0..360", "flag 2"))
    head = ("# logger PLP-MET-01 (synthetic), Plant P Reference Data Pack 1.1.0\n"
            "# interval 10 min; each time stamp marks the END of its interval\n"
            "# clock: local standard time UTC+04:00 (offset not written)\n"
            "# units: ws m/s; wd deg from north; t_air degC; p_air hPa; ghi W/m2\n"
            "timestamp,ws100_avg,ws100_sd,ws80_avg,ws60_avg,wd100_avg,t_air,p_air,ghi\n")
    body = "".join(",".join(r) + "\n" for r in rows)
    kbuf = io.StringIO()
    w = csv.writer(kbuf, lineterminator="\n")
    w.writerow(("id", "where", "column", "defect", "expected_handling"))
    w.writerows(key)
    return head + body, kbuf.getvalue()


def raw_pv_scada(data: dict[str, np.ndarray]) -> str:
    """Hourly PV energy as a foreign-locale SCADA export: UTC, kWh, ';' and ','."""
    lines = ["time_utc;energy_kwh;availability_pct"]
    t0 = datetime(YEAR, 4, 3) - timedelta(hours=4)        # 00:00 local = 20:00 UTC
    for h in range(RAW_HOURS):
        if h == 37:                                       # 2023-04-04 13:00 local missing
            continue
        g = float(data["ghi_wm2"][RAW_START + h])
        p_mw = min(60.0 * g / 1000.0 * 0.85 * 0.98, 50.0)
        kwh = f"{p_mw * 1000.0:.1f}".replace(".", ",")
        stamp = (t0 + timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M:%SZ")
        lines.append(f"{stamp};{kwh};100,0")
    return "\n".join(lines) + "\n"


REG_FIELDS = ["tag", "parent", "description", "description_fa", "vendor", "model", "serial",
              "location", "delivered", "installed", "commissioned", "criticality", "doc_ref"]


def asset_register(rev: str) -> str:
    """Synthetic asset register (teaching tag scheme, fictional vendors)."""
    recs = [["PLP-PLT-01", "", "Plant P", "نیروگاه P", "", "", "", "site", "", "", "", "A",
             "PLP-GEN-SPC-0001"],
            ["PLP-SUB-01", "PLP-PLT-01", "Plant substation 132/33 kV", "پست ۱۳۲/۳۳ کیلوولت",
             "", "", "", "SUB", "", "", "", "A", ""],
            ["PLP-TRF-01", "PLP-SUB-01", "Export transformer 132/33 kV 120 MVA",
             "ترانسفورماتور صادرات", "Vendor-T", "TX-120", "T24-0117", "SUB",
             "2025-02-10", "2025-03-20", "2025-06-15", "A", ""],
            ["PLP-SWG-01", "PLP-SUB-01", "33 kV switchgear line-up", "تابلوی ۳۳ کیلوولت",
             "Vendor-S", "SG-33", "S24-2210", "SUB", "2025-02-01", "2025-03-05",
             "2025-06-10", "A", ""],
            ["PLP-MET-01", "PLP-PLT-01", "Met mast 100 m", "دکل هواشناسی", "Vendor-M",
             "MM-100", "M23-0042", "MET", "2024-09-01", "2024-09-20", "2024-10-01", "B", ""],
            ["PLP-MET-01-ANM", "PLP-MET-01", "Cup anemometer at 100 m", "بادسنج ۱۰۰ متری",
             "Vendor-M", "AN-1", "A23-1001", "MET", "2024-09-01", "2024-09-20",
             "2024-10-01", "B", ""],
            ["PLP-MET-01-VAN", "PLP-MET-01", "Wind vane at 100 m", "بادنما", "Vendor-M",
             "WV-1", "V23-0300", "MET", "2024-09-01", "2024-09-20", "2024-10-01", "B", ""],
            ["PLP-MET-01-PYR", "PLP-MET-01", "Pyranometer, horizontal", "تابش‌سنج",
             "Vendor-P", "PY-2", "P23-0555", "MET", "2024-09-01", "2024-09-20",
             "2024-10-01", "B", ""]]
    for k in range(1, 13):
        wt = f"PLP-WTG-{k:02d}"
        recs.append([wt, "PLP-PLT-01", f"Wind turbine {k} WT-5.0-150", f"توربین بادی {k}",
                     "Vendor-W", "WT-5.0-150", f"W25-{1000 + k}", f"WTG{k:02d}",
                     "2025-03-01", "2025-04-15", "2025-07-01", "A", ""])
        for code, desc, fa in (("GEN", "Generator", "ژنراتور"), ("GBX", "Gearbox", "جعبه‌دنده"),
                               ("TRF", "Turbine transformer 0.69/33 kV", "ترانسفورماتور توربین")):
            recs.append([f"{wt}-{code}", wt, f"{desc}, turbine {k}", f"{fa} توربین {k}",
                         "Vendor-W", f"{code}-5", f"{code[0]}25-{2000 + 10 * k}",
                         f"WTG{k:02d}", "2025-03-01", "2025-04-15", "2025-07-01",
                         "A" if code != "TRF" else "B", ""])
    for k in range(1, 11):
        recs.append([f"PLP-PVB-{k:02d}", "PLP-PLT-01", f"PV block {k}, 6 MWp",
                     f"بلوک خورشیدی {k}", "", "", "", f"PV{k:02d}", "", "2025-05-01",
                     "2025-08-01", "B", ""])
        recs.append([f"PLP-INV-{k:02d}", f"PLP-PVB-{k:02d}", f"Central inverter {k}, 5 MW",
                     f"اینورتر {k}", "Vendor-I", "CI-5000", f"I25-{3000 + k}", f"PV{k:02d}",
                     "2025-04-01", "2025-05-10", "2025-08-01", "A", ""])
    recs.append(["PLP-BES-01", "PLP-PLT-01", "Battery system 20 MW / 40 MWh (scenario S1)",
                 "سامانهٔ باتری (سناریوی S1)", "Vendor-B", "BS-40", "B25-0001", "BES",
                 "2025-05-01", "2025-06-01", "2025-09-01", "A", ""])
    if rev == "B":
        by_tag = {r[0]: r for r in recs}
        g = by_tag["PLP-WTG-07-GEN"]                      # intended: generator exchanged
        g[6], g[8], g[9], g[10] = "G26-0907", "2026-03-02", "2026-03-10", "2026-03-15"
        g[10] = "2025-03-15"                              # DEFECT: year typed wrongly
        by_tag["PLP-MET-01-PYR"][6] = "P26-0610"           # intended: recalibrated spare
        recs.remove(by_tag["PLP-MET-01-VAN"])              # intended: vane replaced by sonic
        recs.insert(6, ["PLP-MET-01-SON", "PLP-MET-01", "Ultrasonic anemometer at 98 m",
                        "بادسنج فراصوتی", "Vendor-M", "US-3", "U26-0077", "MET",
                        "2026-02-01", "2026-02-10", "2026-02-12", "B", ""])
        recs.insert(7, ["PLP-MET-01-HYG", "PLP-MET-01", "Temperature/humidity sensor",
                        "دماسنج و رطوبت‌سنج", "Vendor-M", "TH-1", "", "MET",
                        "2026-02-01", "2026-02-10", "2026-02-12", "C", ""])   # DEFECT: serial
        inv7 = by_tag["PLP-INV-07"]
        recs.insert(recs.index(inv7) + 1, list(inv7))     # DEFECT: duplicated row
        recs.append(["PLP-WTG-13-GEN", "PLP-WTG-13", "Generator, turbine 13",
                     "ژنراتور توربین 13", "Vendor-W", "GEN-5", "G25-2130", "WTG13",
                     "", "", "", "A", ""])                # DEFECT: orphan
        by_tag["PLP-PVB-03"][3] = "بلوك خورشيدي 3"         # DEFECT: Arabic kaf and yeh
        by_tag["PLP-SWG-01"][11] = "a"                     # DEFECT: lowercase class
        by_tag["PLP-TRF-01"][2] = ("Export transformer 132/33 kV 120 MVA, ONAN/ONAF, "
                                   "on-load tap changer")  # intended: longer text
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(REG_FIELDS)
    w.writerows(recs)
    return buf.getvalue()


CHANGE_NOTICE_CSV = """\
notice,tag,field,new_value,reason
CN-001,PLP-WTG-07-GEN,serial,G26-0907,generator exchanged after bearing damage
CN-001,PLP-WTG-07-GEN,delivered,2026-03-02,generator exchanged after bearing damage
CN-001,PLP-WTG-07-GEN,installed,2026-03-10,generator exchanged after bearing damage
CN-001,PLP-WTG-07-GEN,commissioned,2026-03-15,generator exchanged after bearing damage
CN-002,PLP-MET-01-PYR,serial,P26-0610,pyranometer swapped for a recalibrated spare
CN-003,PLP-MET-01-VAN,(removed),,vane replaced by an ultrasonic sensor
CN-003,PLP-MET-01-SON,(added),,ultrasonic sensor at 98 m
CN-004,PLP-MET-01-HYG,(added),,new temperature/humidity sensor
CN-005,PLP-TRF-01,description,"Export transformer 132/33 kV 120 MVA, ONAN/ONAF, on-load tap changer",description completed from the nameplate
"""

DATA_DICTIONARY_ADD = """\
raw/met_mast_10min_raw.csv,timestamp,local time,END of the 10-min interval; UTC+04:00 implied (header comment),2023-04-03 00:10 to 2023-04-06 00:00,synthetic
raw/met_mast_10min_raw.csv,ws100_avg ws80_avg ws60_avg,m/s,10-min mean wind speeds at 100/80/60 m,0 to 45,synthetic
raw/met_mast_10min_raw.csv,ws100_sd,m/s,standard deviation of the 100 m speed within the interval,0 to 10,synthetic
raw/met_mast_10min_raw.csv,wd100_avg,deg,10-min mean direction at 100 m (FROM; 0 = north),0 to 359,synthetic
raw/met_mast_10min_raw.csv,t_air p_air ghi,degC hPa W/m2,10-min means,see hourly file,synthetic
raw/met_mast_defects_key.csv,all,-,the defects placed in the raw file on purpose,-,synthetic
raw/pv_scada_export.csv,time_utc,ISO 8601 UTC (Z),START of the hour; semicolon-delimited; decimal comma,2023-04-02T20:00:00Z to 2023-04-05T19:00:00Z,synthetic
raw/pv_scada_export.csv,energy_kwh,kWh,AC energy of the PV plant in the hour (decimal comma),0 to 50000,synthetic
raw/pv_scada_export.csv,availability_pct,percent,inverter availability in the hour,0 to 100,synthetic
assets/asset_register_rev_A.csv,(13 fields),-,released register at handover (rev A),-,synthetic
assets/asset_register_rev_B.csv,(13 fields),-,register six months later: intended changes AND editing defects,-,synthetic
assets/change_notice.csv,(5 fields),-,changes approved between rev A and rev B,-,synthetic
"""

README_MD_1_1 = README_MD.replace("release 1.0.0", "release 1.1.0").replace(
    "| `CHANGELOG.md` |",
    "| `raw/` | a 10-min met-mast logger file and a PV SCADA export with documented defects "
    "(chapter 5 labs) |\n"
    "| `assets/` | synthetic asset register rev A and rev B and the approved change notice |\n"
    "| `CHANGELOG.md` |")

CHANGELOG_MD_1_1 = """\
# Changelog — Plant P Reference Data Pack

## 1.1.0 — 2026-11-15
- Added: the full assumptions ledger A-014..A-099 (chapters 2 to 6 and 5);
  raw/met_mast_10min_raw.csv with its defect key; raw/pv_scada_export.csv;
  assets/asset_register_rev_A.csv, assets/asset_register_rev_B.csv,
  assets/change_notice.csv; data-dictionary rows for the new files.
- Unchanged: every time series, subset, equipment file, scenario and seed
  rating is byte-identical to 1.0.0 (same SHA-256): no result changes.
- Reason: chapter 5 (data validation and asset-information laboratories).
- Version rule: additions only, backwards compatible -> minor release.
- Dependent artefacts: chapters 1-4 and 6 keep citing 1.0.0 (still valid);
  chapter 5 and later cite 1.1.0.

## 1.0.0 — 2026-11-14
- First release: seed ratings, assumptions ledger A-001..A-013, scenarios S0 and S1,
  synthetic hourly resource year (seed 20260101), three hand-calculation subsets,
  fictional PV module PVM-550 and wind turbine WT-5.0-150 with power curve.
- Reason: baseline for the book's worked examples.
- Dependent artefacts: none yet.
"""


# ------------------------------------------------------------------- assembly
def daily_ghi_kwh(data: dict[str, np.ndarray]) -> np.ndarray:
    return data["ghi_wm2"].reshape(365, 24).sum(axis=1) / 1000.0


def pick_subsets(data: dict[str, np.ndarray]) -> dict[str, tuple[str, range]]:
    daily = daily_ghi_kwh(data)
    june = range(151, 181)                                   # day index 151..180 = 1..30 June
    summer = max(june, key=lambda d: daily[d])
    december = list(range(334, 365))
    median = float(np.median(daily[334:365]))
    winter = min(december, key=lambda d: abs(daily[d] - median))
    week_start = 92                                          # 3 April 2023, a Monday
    return {
        "timeseries/subset_day_summer.csv": ("clearest day of June", range(summer * 24, summer * 24 + 24)),
        "timeseries/subset_day_winter.csv": ("median-irradiance day of December",
                                             range(winter * 24, winter * 24 + 24)),
        "timeseries/subset_week_spring.csv": ("week of 3-9 April", range(week_start * 24, week_start * 24 + 168)),
    }


def expected_results(data: dict[str, np.ndarray]) -> dict:
    curve = power_curve()
    return {
        "release": RELEASE,
        "hours": 8760,
        "annual_ghi_kwh_m2": round(float(data["ghi_wm2"].sum() / 1000.0), 1),
        "annual_dni_kwh_m2": round(float(data["dni_wm2"].sum() / 1000.0), 1),
        "annual_dhi_kwh_m2": round(float(data["dhi_wm2"].sum() / 1000.0), 1),
        "max_ghi_wm2": round(float(data["ghi_wm2"].max()), 1),
        "mean_t_air_c": round(float(data["t_air_c"].mean()), 2),
        "min_t_air_c": round(float(data["t_air_c"].min()), 1),
        "max_t_air_c": round(float(data["t_air_c"].max()), 1),
        "mean_ws_100m_ms": round(float(data["ws_100m_ms"].mean()), 3),
        "mean_ws_80m_ms": round(float(data["ws_80m_ms"].mean()), 3),
        "mean_ws_60m_ms": round(float(data["ws_60m_ms"].mean()), 3),
        "max_ws_100m_ms": round(float(data["ws_100m_ms"].max()), 2),
        "mean_p_hpa": round(float(data["p_hpa"].mean()), 2),
        "power_curve_rows": len(curve),
        "power_curve_kw_at_8_ms": dict(curve)[8.0],
    }


def build_files() -> dict[str, str]:
    data = generate_hourly()
    new = RELEASE != "1.0.0"
    files = {
        "README.md": README_MD_1_1 if new else README_MD,
        "CHANGELOG.md": CHANGELOG_MD_1_1 if new else CHANGELOG_MD,
        "seed_ratings.csv": SEED_RATINGS_CSV,
        "assumptions.csv": ledger_csv() if new else ASSUMPTIONS_CSV,
        "data_dictionary.csv": DATA_DICTIONARY_CSV + (DATA_DICTIONARY_ADD if new else ""),
        "scenarios/S0-no-bess.yml": SCENARIO_S0,
        "scenarios/S1-bess.yml": SCENARIO_S1,
        "equipment/pv_module_PVM-550.yml": PV_MODULE_YML,
        "equipment/wind_turbine_WT-5.0-150.yml": WIND_TURBINE_YML,
        "equipment/wind_turbine_WT-5.0-150_power_curve.csv": power_curve_csv(),
        "timeseries/plantp_hourly_8760.csv": hourly_csv(data, range(8760)),
    }
    subsets = pick_subsets(data)
    for path, (_, rows) in subsets.items():
        files[path] = hourly_csv(data, rows)
    results = expected_results(data)
    if new:
        met, key = raw_met_mast(data)
        files["raw/met_mast_10min_raw.csv"] = met
        files["raw/met_mast_defects_key.csv"] = key
        files["raw/pv_scada_export.csv"] = raw_pv_scada(data)
        files["assets/asset_register_rev_A.csv"] = asset_register("A")
        files["assets/asset_register_rev_B.csv"] = asset_register("B")
        files["assets/change_notice.csv"] = CHANGE_NOTICE_CSV
        results["raw_met_records"] = sum(1 for line in met.splitlines()
                                         if line[:1].isdigit())
        results["raw_met_defects"] = len(key.splitlines()) - 1
        results["register_rev_A_records"] = len(asset_register("A").splitlines()) - 1
    files["expected_results.json"] = json.dumps(results, indent=2) + "\n"

    ts = timestamps()
    manifest = {
        "name": "Plant P Reference Data Pack",
        "release": RELEASE,
        "created": CREATED,
        "status": "synthetic teaching data; no real site, grid or product",
        "generator": "companion/plantp_data/generate_release.py",
        "seed": SEED,
        "site": {"latitude_deg_n": LAT_DEG, "elevation_m": ELEV_M, "longitude": None,
                 "utc_offset": UTC_OFFSET, "calendar_year_label": YEAR,
                 "timestamp_convention": "start of hour, local standard time, no daylight saving"},
        "scenarios": ["S0", "S1"],
        **({"supersedes": "1.0.0", "compatibility": "minor release: additions only; all "
            "1.0.0 time series, subsets, equipment files and scenarios byte-identical"}
           if new else {}),
        "subsets": {path: {"description": desc, "first": ts[rows[0]], "last": ts[rows[-1]]}
                    for path, (desc, rows) in subsets.items()},
        "files": {path: {"sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                         "bytes": len(text.encode("utf-8"))}
                  for path, text in sorted(files.items())},
    }
    files["manifest.json"] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return files


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="write nothing; compare a fresh generation with the files on disk")
    ap.add_argument("--release", choices=sorted(RELEASES), default="1.1.0")
    args = ap.parse_args()
    global RELEASE, CREATED, OUT
    RELEASE, CREATED = args.release, RELEASES[args.release]
    OUT = os.path.join(HERE, RELEASE)
    files = build_files()
    if args.check:
        bad = []
        for rel, text in files.items():
            path = os.path.join(OUT, rel)
            if not os.path.exists(path):
                bad.append(f"missing {rel}")
            elif open(path, encoding="utf-8", newline="").read() != text:
                bad.append(f"differs {rel}")
        print("\n".join(bad) if bad else f"release {RELEASE}: {len(files)} files identical")
        return 1 if bad else 0
    for rel, text in files.items():
        path = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
    print(f"wrote release {RELEASE}: {len(files)} files -> {OUT}")
    print(files["expected_results.json"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
