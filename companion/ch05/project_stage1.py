"""Worked project, stage 1: ONE script from raw files to a report.

It works, and it is written the way first versions usually are: top to
bottom, file names in the code, calculation mixed with printing. Stage 2
(companion/ch05/resource_tool/) refactors it; a test checks that both give
the same numbers.

    python -m companion.ch05.project_stage1
"""
import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

from plantp import datapack

# [start: stage1]
OUT = Path("companion/ch05/output/stage1")
OUT.mkdir(parents=True, exist_ok=True)
LOCAL = timezone(timedelta(hours=4))

# 1. raw logger file: skip comments, end label -> start, UTC
text = datapack.raw_path("met_mast_10min_raw.csv").read_text("utf-8")
rows = list(csv.DictReader(
    [ln for ln in text.splitlines() if not ln.startswith("#")]))
recs = []
for r in rows:
    end = datetime.strptime(r["timestamp"], "%Y-%m-%d %H:%M")
    start = (end.replace(tzinfo=LOCAL) - timedelta(minutes=10))
    recs.append((start.astimezone(timezone.utc), float(r["ws100_avg"])))
recs = sorted(set(recs))                      # order + exact duplicates
gaps = sum(1 for a, b in zip(recs, recs[1:])
           if b[0] - a[0] != timedelta(minutes=10))

# 2. hourly means of the 100 m speed, at least 5 of 6 values
hours = {}
for t, v in recs:
    if 0 <= v <= 45:
        hours.setdefault(t.replace(minute=0), []).append(v)
ws_hourly = {h: sum(v) / len(v) for h, v in hours.items() if len(v) >= 5}

# 3. annual energies with the step-3 models (constants typed here)
h = datapack.load_hourly()
curve = datapack.load_power_curve()
g, ta = h["ghi_wm2"].to_numpy(), h["t_air_c"].to_numpy()
t_cell = ta + (45 - 20) / 800 * g
pv = np.minimum(60 * g / 1000 * (1 - 0.0035 * (t_cell - 25)) * 0.90
                * 0.98, 50)
rho = h["p_hpa"].to_numpy() * 100 / (287.05 * (ta + 273.15))
v_eq = h["ws_100m_ms"].to_numpy() * (rho / 1.225) ** (1 / 3)
wind = np.interp(v_eq, curve["wind_speed_ms"], curve["power_kw"]) \
    * 12 / 1000 * (1 - 0.12)
export = np.minimum(pv + wind, 100)

# 4. report
result = {"pv_gwh": round(pv.sum() / 1000, 2),
          "wind_gwh": round(wind.sum() / 1000, 2),
          "export_gwh": round(export.sum() / 1000, 2),
          "raw_records": len(rows), "kept": len(recs), "gaps": gaps,
          "usable_hours_ws100": len(ws_hourly)}
(OUT / "result.json").write_text(json.dumps(result, indent=1), "utf-8")
print(result)
print("mean of usable hourly ws100 =",
      round(sum(ws_hourly.values()) / len(ws_hourly), 3), "m/s;",
      "mean density", round(float(rho.mean()), 4), "kg/m3")
# [end: stage1]
