"""A configured run: check the configuration, verify the data, calculate, and
record everything needed to repeat the run (release, hashes, versions)."""
from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import yaml

from companion.ch05.resource_tool import __version__, model as m

ROOT = Path(__file__).resolve().parents[3]


def load_config(path):
    from plantp import schema
    text = Path(path).read_text(encoding="utf-8")
    cfg = yaml.safe_load(text)
    problems = schema.check(cfg, schema.RUN_SCHEMA)
    if problems:
        raise ValueError("configuration rejected:\n  " + "\n  ".join(problems))
    cfg["_sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return cfg


# [start: calculate]
def calculate(cfg, hourly, curve):
    pv = m.pv_ac_mw(hourly["ghi_wm2"], hourly["t_air_c"], **cfg["pv"])
    rho = (m.air_density(hourly["p_hpa"], hourly["t_air_c"])
           if cfg["wind"]["density_correction"] else m.RHO_REF)
    wind = m.wind_farm_mw(hourly["ws_100m_ms"], rho, curve["wind_speed_ms"],
                          curve["power_kw"], cfg["wind"]["turbines"],
                          cfg["wind"]["loss"])
    exp, cut = m.export_mw(pv, wind, cfg["export_limit_mw"])
    out = {"pv_mw": np.asarray(pv), "wind_mw": np.asarray(wind),
           "export_mw": np.asarray(exp), "curtailed_mw": np.asarray(cut),
           "rho": np.broadcast_to(rho, np.shape(pv))}
    if cfg.get("bess"):
        from plantp import screening
        b = cfg["bess"]
        shift = screening.shift_surplus_with_battery(
            cut, cfg["export_limit_mw"] - exp, b["power_mw"],
            b["usable_mwh"], b["roundtrip"])
        out["bess"] = {"charged_mwh": shift.charged_mwh,
                       "delivered_mwh": shift.delivered_mwh}
    return out
# [end: calculate]


def run(cfg):
    import plantp
    from plantp import datapack
    rel = cfg["data_release"]
    problems = datapack.verify(rel)
    if problems:
        raise RuntimeError(f"data pack {rel}: " + "; ".join(problems))
    hourly = datapack.load_hourly(release=rel)
    curve = datapack.load_power_curve(release=rel)
    s = calculate(cfg, hourly, curve)
    files = datapack.load_manifest(rel)["files"]
    used = ["timeseries/plantp_hourly_8760.csv",
            "equipment/wind_turbine_WT-5.0-150_power_curve.csv"]
    results = {
        "run_id": cfg["run_id"], "scenario": cfg["scenario"],
        "data_release": rel,
        "inputs": {f: files[f]["sha256"] for f in used},
        "config_sha256": cfg["_sha256"],
        "software": {"resource_tool": __version__,
                     "plantp": plantp.__version__,
                     "python": platform.python_version(),
                     "numpy": np.__version__},
        "pv_gwh": round(float(s["pv_mw"].sum()) / 1000, 2),
        "wind_gwh": round(float(s["wind_mw"].sum()) / 1000, 2),
        "export_gwh": round(float(s["export_mw"].sum()) / 1000, 2),
        "curtailed_mwh": round(float(s["curtailed_mw"].sum()), 1),
        "pv_peak_mw": round(float(s["pv_mw"].max()), 2),
        "mean_air_density": round(float(np.mean(s["rho"])), 4),
        "hours": int(len(hourly)),
    }
    if "bess" in s:
        results["bess"] = {k: round(v, 1) for k, v in s["bess"].items()}
    return results, s


def write(cfg, results, series):
    import csv
    folder = ROOT / cfg["outputs"]["folder"]
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "results.json").write_text(json.dumps(results, indent=2) + "\n",
                                         encoding="utf-8")
    with open(folder / "hourly.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["hour", "pv_mw", "wind_mw", "export_mw"])
        for k in range(results["hours"]):
            w.writerow([k] + [f"{series[c][k]:.3f}"
                              for c in ("pv_mw", "wind_mw", "export_mw")])
    return folder
