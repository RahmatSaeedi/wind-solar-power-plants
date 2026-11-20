"""Chapter 17, more lessons - a load model fitted on temperature and the
calendar (trained on eight months, tested on four, then used for a
hotter year), the hosting capacity of the grid node by three bounded
constraints, and indicators of local energy security.

Run from the project root:   python -m companion.ch17.examples_g
Writes companion/ch17/expected/g_*.txt and diagrams/data/ch17-*.csv.
Synthetic data A-284, network teaching values A-285; plant model 15.1.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch15 import sources as s15
from companion.ch17 import sources as src
from companion.ch17.common import csv, emit
from plantp import demand as dm

N = src.NETWORK


# [start: model]
def features(hour, dow, t):
    """Cooling and heating degrees, hour of day (sine/cosine pairs) and a
    working-day flag: all known in advance or forecast."""
    cool = np.clip(t - 24.0, 0, None)
    heat = np.clip(12.0 - t, 0, None)
    work = ((dow < 5) & (hour >= 7) & (hour < 19)).astype(float)
    cols = [np.ones_like(t), cool, heat, work]
    for k in (1, 2, 3):
        w = 2 * np.pi * k * hour / 24
        cols += [np.sin(w), np.cos(w)]
    return np.column_stack(cols)
# [end: model]


def load_model() -> None:
    hour, dow, month, t = src.calendar()
    p = src.regional()["total"]
    X = features(hour, dow, t)
    train = month <= 7
    coef, *_ = np.linalg.lstsq(X[train], p[train], rcond=None)
    pred = X @ coef
    test = ~train
    err = pred - p
    rmse = float(np.sqrt(np.mean(err[test] ** 2)))
    hot = X.copy()
    hot[:, 1] = np.clip(t + 1.5 - 24.0, 0, None)
    hot[:, 2] = np.clip(12.0 - (t + 1.5), 0, None)
    p_hot = hot @ coef
    lines = ["a load model on temperature and calendar (trained Jan-Aug, tested",
             "  Sep-Dec, synthetic load A-284):",
             f"  coefficients: base {coef[0]:.2f} MW, cooling {coef[1]:.2f} MW per degree,"
             f" heating {coef[2]:.2f}, working hours {coef[3]:.2f} MW",
             f"  test RMSE {rmse:.2f} MW ({100 * rmse / p[test].mean():.1f} % of the mean);"
             f" test bias {err[test].mean():+.2f} MW",
             f"  a year 1.5 C hotter: peak {pred.max():.2f} -> {p_hot.max():.2f} MW,"
             f" energy {pred.sum() / 1e3:.1f} -> {p_hot.sum() / 1e3:.1f} GWh",
             "  cooling comes out at 1.35 MW per degree although the data were",
             "  built with 0.9: the summer pumping rises with the heat and the",
             "  model gives it to cooling (confounding); a meter per component",
             "  or a pumping flag separates them",
             "  the model explains the shape, not the future: growth, new",
             "  loads and a changed climate are scenarios on top of it, and a",
             "  real model is fitted on several years of measured data"]
    emit("g_loadmodel", lines)
    idx = np.arange(0, 8760, 7)
    csv("ch17-loadtemp.csv", "t,p", [(f"{t[k]:.1f}", f"{p[k]:.2f}") for k in idx])


def hosting() -> None:
    """Largest plant (same hourly shape as Plant P, scaled) the node takes
    under three teaching constraints: the upstream limit, a 1.1 % voltage
    rise on the 7.06 km line at full output and pf 1, and the line rating."""
    r = s15.plant_year()
    shape = np.clip(r["net"], 0, None) / 100.0          # per MW of export limit
    load = src.regional()["total"]
    R = N["r_ohm_km"] * N["line_km"]
    res = {}
    for scale in np.arange(50, 401, 5):
        flow = dm.net_flow(load, shape * scale)
        if flow.max() <= N["upstream_mw"]:
            res["upstream"] = scale
        if float(dm.voltage_rise(scale, 0, R, 0, N["v_kv"])) <= 1.1:
            res["voltage"] = scale
        if scale <= N["line_rating_mva"]:
            res["thermal"] = scale
    lines = ["hosting capacity of the grid node for a plant shaped like Plant P",
             "  (export limit in MW, teaching constraints A-285):"]
    for k, v in res.items():
        lines.append(f"  {k:9s} up to {v:4.0f} MW")
    lines += [f"  the binding constraint: {min(res, key=res.get)}; Plant P's 100 MW is",
              "  within all three; hosting depends on the local load's minimum,",
              "  which is why the measured load is the first item of the request"]
    emit("g_hosting", lines)


def security() -> None:
    r = s15.plant_year()
    gen = np.clip(r["net"], 0, None)
    load = src.regional()["total"]
    local = np.minimum(gen, load)
    self_h = int((gen >= load).sum())
    lines = ["local energy-security indicators for the regional load:",
             f"  share of the regional energy met by Plant P in the same hour"
             f" {100 * local.sum() / load.sum():.1f} %",
             f"  hours in which the plant alone covers the region {self_h} of 8760",
             f"  longest run of hours not covered {_longest(gen < load)} h",
             "  these say how much the region could lean on the plant; they do",
             "  not make the plant a backup: without the grid it cannot run",
             "  (grid-following units, section A of chapter 18)"]
    emit("g_security", lines)


def _longest(mask) -> int:
    best = cur = 0
    for m in mask:
        cur = cur + 1 if m else 0
        best = max(best, cur)
    return best


def dynamic_limit() -> None:
    """If the network beyond could take only 50 MW (teaching), the export
    the node allows is 50 MW plus the local load of that hour. A static
    limit must assume the lowest load; a dynamic limit follows it."""
    r = s15.plant_year()
    gen = np.clip(r["net"], 0, None)
    load = src.regional()["total"]
    up = 50.0
    static = up + float(load.min())
    dyn = up + load
    cut_s = np.clip(gen - static, 0, None).sum()
    cut_d = np.clip(gen - dyn, 0, None).sum()
    lines = ["static against dynamic export limit (upstream 50 MW, teaching):",
             f"  static limit (50 MW + lowest load {load.min():.1f} MW) = {static:.1f} MW:"
             f" {cut_s / 1e3:.2f} GWh curtailed",
             f"  dynamic limit (50 MW + the hour's load): {cut_d / 1e3:.2f} GWh curtailed",
             "  following the load needs measured flows, a fast plant controller",
             "  and the operator's agreement (chapters 20 and 28); the static",
             "  limit is simpler and costs the difference every year"]
    emit("g_dynamic", lines)


if __name__ == "__main__":
    dynamic_limit()
    load_model()
    hosting()
    security()
