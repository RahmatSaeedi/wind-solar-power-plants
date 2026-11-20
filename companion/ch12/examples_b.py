"""Chapter 12, section B - measurement systems in numbers: directional
(cosine) error, thermal offset, sampling against averaging, reference cell
against pyranometer, a calibration factor, and the station's data volume.

Run from the project root:   python -m companion.ch12.examples_b
Writes companion/ch12/expected/b_*.txt.
Teaching sensor values A-248 (fictional; real values come from the
calibration certificate and the specification of the instrument).
"""
from __future__ import annotations

import numpy as np

from companion.ch10 import pvyear10
from companion.ch12 import sources
from companion.ch12.common import csv, emit


def cosine_error() -> None:
    """Directional response (A-248): reads 1 % low at 60 deg zenith and
    5 % low at 80 deg, smoothly (teaching curve)."""
    p = sources.pack()
    z = np.degrees(np.arccos(np.clip(p["cz"], 0, 1)))
    err = -0.01 * (z / 60) ** 4
    err = np.where(z > 80, -0.05, np.maximum(err, -0.05))
    meas = p["ghi"] * (1 + err)
    low = (z > 70) & (p["ghi"] > 5)
    lines = ["directional (cosine) error of a pyranometer (A-248, teaching):",
             "  response 1 % low at 60 deg zenith, 5 % low near the horizon",
             f"  annual GHI {p['ghi'].sum() / 1e3:,.1f} -> {meas.sum() / 1e3:,.1f} kWh/m2"
             f" ({100 * (meas.sum() / p['ghi'].sum() - 1):+.2f} %)",
             f"  hours with the sun below 20 deg: {low.sum():,}, their GHI"
             f" {100 * (meas[low].sum() / p['ghi'][low].sum() - 1):+.1f} %",
             "  small in the annual sum, large in winter mornings: the error",
             "  is in the hours a tracker or an east-west array cares about"]
    emit("b_cosine", lines)


def thermal_offset() -> None:
    p = sources.pack()
    day = p["cz"] > 0
    off = -4.0                                            # W/m2, daytime (A-248)
    lines = ["thermal offset of a single-dome pyranometer (A-248, teaching):",
             f"  -4 W/m2 in daylight, {day.sum():,} daylight hours:"
             f" {off * day.sum() / 1e3:+.1f} kWh/m2"
             f" ({100 * off * day.sum() / p['ghi'].sum():+.2f} % of GHI)",
             "  the night readings show it (negative values at night, flag 8);",
             "  a ventilated, double-dome or heated instrument keeps it small"]
    emit("b_offset", lines)


def sampling() -> None:
    days = sources.minute_days()
    csv("ch12-days.csv", "h,clear,broken,overcast",
        [(f"{k / 60:.3f}", f"{days['clear']['true'][k]:.1f}",
          f"{days['broken']['true'][k]:.1f}", f"{days['overcast']['true'][k]:.1f}")
         for k in range(0, 1440, 2)])
    d = days["broken"]
    x = d["true"]
    tenmin = x.reshape(144, 10)
    mean10 = tenmin.mean(axis=1)
    inst10 = tenmin[:, 0]                                 # one sample per 10 min
    day = mean10 > 5
    rms = np.sqrt(np.mean((inst10[day] - mean10[day]) ** 2))
    lines = ["sampling against averaging on a broken-cloud day (one-minute data):",
             f"  daily irradiation {x.sum() / 60 / 1e3:.3f} kWh/m2",
             f"  ten-minute means from all samples: {mean10.sum() / 6 / 1e3:.3f};"
             f" from one sample per 10 min: {inst10.sum() / 6 / 1e3:.3f}",
             f"  RMS difference of the ten-minute values {rms:.0f} W/m2",
             f"  (mean daylight value {mean10[day].mean():.0f} W/m2)",
             "  sample often (every few seconds) and average: sparse samples",
             "  keep the daily sum roughly right but not the ramps that",
             "  clipping, storage and grid studies need"]
    emit("b_sampling", lines)


def reference_cell() -> None:
    p = pvyear10.poa()
    poa, eff = p["poa"].sum() / 1e3, p["eff"].sum() / 1e3
    e_ac = 111_339.0                                      # chapter 10, MWh
    pr_pyr = e_ac / (poa * 60.06)
    pr_ref = e_ac / (eff * 60.06)
    lines = ["plane-of-array pyranometer against a reference cell (PV type):",
             f"  pyranometer (all angles, broad spectrum): {poa:,.0f} kWh/m2",
             "  reference cell (sees the glass reflection like a module):",
             f"    {eff:,.0f} kWh/m2 ({100 * (eff / poa - 1):+.1f} %)",
             f"  PR of the chapter 10 year: {pr_pyr:.3f} with the pyranometer,"
             f" {pr_ref:.3f} with the cell",
             "  neither is wrong: the contract and the model must say which",
             "  sensor the PR uses (IEC 61724-1:2021 names both kinds)"]
    emit("b_refcell", lines)


def calibration() -> None:
    sens, sens_new = 8.50e-6, 8.41e-6                     # V per W/m2 (A-248)
    v = 7.65e-3                                           # logger reading, V
    lines = ["calibration factor of a thermopile pyranometer (A-248):",
             f"  certificate: {sens * 1e6:.2f} uV per W/m2; reading {v * 1e3:.2f} mV"
             f" -> {v / sens:.0f} W/m2",
             f"  after two years the recalibration gives {sens_new * 1e6:.2f}"
             f" uV per W/m2 ({100 * (sens_new / sens - 1):+.1f} %)",
             f"  the same reading is then {v / sens_new:.0f} W/m2: data logged",
             f"    with the old factor read {100 * (1 - sens_new / sens):.1f} % low",
             "  the correction is applied from the date of the change (or",
             "  linearly between the two calibrations) and logged as such",
             "  recalibration interval and method follow the instrument's",
             "  class and the campaign's plan (ISO 9060:2018 classes)"]
    emit("b_calibration", lines)


def data_volume() -> None:
    channels = 14            # GHI, DHI, DNI, 2 POA, 2 rear, 2 soiling, T, RH, p, rain, wind
    per_s = channels * 4     # bytes per sample
    year_raw = per_s * 3600 * 24 * 365 / 1e6
    year_min = channels * 4 * 3 * 60 * 24 * 365 / 1e6    # mean, min, max per min
    lines = ["data volume of the Plant P weather station (teaching):",
             f"  {channels} channels sampled every second: {year_raw:,.0f} MB a"
             " year raw",
             f"  one-minute mean, minimum, maximum: {year_min:,.0f} MB a year",
             "  store the one-minute record with flags, the calibration",
             "  factors in force, the cleaning and maintenance log, and the",
             "  clock synchronisation log: data without metadata is not",
             "  evidence"]
    emit("b_volume", lines)


if __name__ == "__main__":
    cosine_error()
    thermal_offset()
    sampling()
    reference_cell()
    calibration()
    data_volume()
