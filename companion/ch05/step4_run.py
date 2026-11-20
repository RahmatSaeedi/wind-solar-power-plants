"""Step 4: configuration in, structured outputs out.

    python -m companion.ch05.step4_run companion/ch05/config/run_S0.yml

Reads a YAML run file, checks it against plantp.schema.RUN_SCHEMA, runs the
pure functions of step 3 on the data pack, and writes results.json (numbers
plus the metadata that make them reproducible) and hourly.csv.
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
import yaml

from companion.ch05 import step3_model as m

ROOT = Path(__file__).resolve().parents[2]


# [start: load]
def load_config(path):
    from plantp import schema
    text = Path(path).read_text(encoding="utf-8")
    cfg = yaml.safe_load(text)
    problems = schema.check(cfg, schema.RUN_SCHEMA)
    if problems:
        raise ValueError("configuration rejected:\n  " + "\n  ".join(problems))
    cfg["_sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return cfg
# [end: load]


# [start: run]
def run(cfg):
    import plantp
    from plantp import datapack
    rel = cfg["data_release"]
    if datapack.verify(rel):
        raise RuntimeError(f"data pack {rel} fails its checksums")
    h = datapack.load_hourly(release=rel)
    curve = datapack.load_power_curve(release=rel)
    pv = m.pv_ac_mw(h["ghi_wm2"], h["t_air_c"], **cfg["pv"])
    rho = (m.air_density(h["p_hpa"], h["t_air_c"])
           if cfg["wind"]["density_correction"] else m.RHO_REF)
    wind = m.wind_farm_mw(h["ws_100m_ms"], rho, curve["wind_speed_ms"],
                          curve["power_kw"], cfg["wind"]["turbines"],
                          cfg["wind"]["loss"])
    exp, cut = m.export_mw(pv, wind, cfg["export_limit_mw"])
    manifest = datapack.load_manifest(rel)["files"]
    results = {
        "run_id": cfg["run_id"], "scenario": cfg["scenario"],
        "data_release": rel,
        "input_sha256": manifest["timeseries/plantp_hourly_8760.csv"]
        ["sha256"],
        "config_sha256": cfg["_sha256"],
        "software": {"plantp": plantp.__version__,
                     "python": platform.python_version()},
        "pv_gwh": round(m.energy_mwh(pv) / 1000, 2),
        "wind_gwh": round(m.energy_mwh(wind) / 1000, 2),
        "export_gwh": round(m.energy_mwh(exp) / 1000, 2),
        "curtailed_mwh": round(m.energy_mwh(cut), 1),
        "mean_air_density": round(float(np.mean(rho)), 4),
    }
    return results, {"pv_mw": pv, "wind_mw": wind, "export_mw": exp}
# [end: run]


# [start: write]
def write_outputs(cfg, results, series):
    import csv
    folder = ROOT / cfg["outputs"]["folder"]
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "results.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8")
    with open(folder / "hourly.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["hour", "pv_mw", "wind_mw", "export_mw"])
        for k in range(len(series["pv_mw"])):
            w.writerow([k] + [f"{series[c][k]:.3f}" for c in
                              ("pv_mw", "wind_mw", "export_mw")])
    return folder


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        cfg = load_config(argv[0])
    except (ValueError, IndexError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    results, series = run(cfg)
    folder = write_outputs(cfg, results, series)
    for key in ("pv_gwh", "wind_gwh", "export_gwh", "curtailed_mwh"):
        print(f"{key:14s} {results[key]}")
    print("written to", folder.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    sys.exit(main())
# [end: write]
