"""Chapter 5, section F - Plant P reference-data laboratory.

    F1 what release 1.1.0 changed (manifests compared, both verified)
    F2 validate the pack: schema, units, time axis, duplicates, provenance,
       scenario selection, ledger
    F3 reproduce the chapter 1 screening numbers and the S0/S1 case
    F4 publish a verification report tied to the release and the input hashes
Run from the project root:   python -m companion.ch05.lab_f
"""
from __future__ import annotations

import csv
import json

import numpy as np
import pandas as pd

from companion.ch05.common import HERE, emit
from plantp import datapack, screening as sc

PUBLISHED = {"pv_gwh": 97.3, "wind_gwh": 192.5, "export_gwh": 289.8,
             "curtailed_mwh": 13.8, "s1_delivered_mwh": 11.8}   # chapter 1 outputs


def f1_release() -> None:
    old = datapack.load_manifest("1.0.0")["files"]
    new = datapack.load_manifest("1.1.0")["files"]
    same = sorted(f for f in old if old[f]["sha256"] == new[f]["sha256"])
    changed = sorted(f for f in old if old[f]["sha256"] != new[f]["sha256"])
    added = sorted(set(new) - set(old))
    emit("f_release", [
        f"verify 1.0.0: {datapack.verify('1.0.0') or 'all checksums match'}; verify 1.1.0: "
        f"{datapack.verify('1.1.0') or 'all checksums match'}",
        f"files identical in both releases: {len(same)} (all time series, equipment, "
        "scenarios, seed ratings)",
        f"changed: {len(changed)} -> {', '.join(changed)}",
        f"added: {len(added)} -> {', '.join(f.split('/')[-1] for f in added)}",
        "rule: additions only and no change of meaning -> minor release 1.1.0;",
        "  every result computed on 1.0.0 is still valid and keeps citing 1.0.0",
    ])


def f2_validate() -> dict:
    h = datapack.load_hourly()
    root = datapack.release_dir()
    dd = list(csv.DictReader((root / "data_dictionary.csv").read_text("utf-8").splitlines()))
    cols = [r["column"] for r in dd if r["file"] == "timeseries/plantp_hourly_8760.csv"]
    checks = {}
    checks["columns = data dictionary"] = ["timestamp"] + list(h.columns) == cols
    bad = []
    for r in dd:
        if r["file"] != "timeseries/plantp_hourly_8760.csv" or r["column"] == "timestamp":
            continue
        lo, hi = (float(x) for x in r["valid_range"].split(" to "))
        if not h[r["column"]].between(lo, hi).all():
            bad.append(r["column"])
    checks["values inside the dictionary ranges"] = not bad
    offsets = {str(t.utcoffset()) for t in h.index}
    checks["one UTC offset (+04:00)"] = offsets == {"4:00:00"}
    steps = h.index.to_series().diff().dropna().unique()
    checks["one-hour steps, 8760 unique stamps"] = (list(steps) == [pd.Timedelta(hours=1)]
                                                    and h.index.is_unique and len(h) == 8760)
    checks["no missing values"] = not h.isna().any().any()
    checks["pressure in hPa (not Pa or kPa)"] = 800 < h["p_hpa"].median() < 1100
    checks["irradiance consistent (DHI <= GHI)"] = bool((h["dhi_wm2"] <= h["ghi_wm2"] + 0.051).all())
    man = datapack.load_manifest()
    checks["provenance: generator and seed recorded"] = bool(man.get("generator") and man.get("seed"))
    s0, s1 = datapack.load_scenario("S0"), datapack.load_scenario("S1")
    checks["scenario cards: S0 no battery, S1 battery"] = s0["bess"] is None and s1["bess"]["power_mw"] == 20
    try:
        datapack.load_scenario("S2")
        checks["unknown scenario refused"] = False
    except ValueError:
        checks["unknown scenario refused"] = True
    led = datapack.load_assumptions()
    checks["ledger A-001..A-099 complete"] = list(led.index) == [f"A-{k:03d}" for k in range(1, 100)]
    lines = [f"data pack {datapack.load_manifest()['release']} validation:"]
    lines += [f"  {'PASS' if ok else 'FAIL'}  {name}" for name, ok in checks.items()]
    emit("f_validate", lines)
    return checks


def f3_reproduce() -> dict:
    h = datapack.load_hourly()
    curve = datapack.load_power_curve()
    pv = np.asarray(sc.pv_ac_power_mw(h["ghi_wm2"], 60, 50))
    wind = np.asarray(sc.wind_power_mw(h["ws_100m_ms"], curve["wind_speed_ms"],
                                       curve["power_kw"], 12))
    exp, cut = sc.export_and_curtailment_mw(pv + wind, 100.0)
    s1 = datapack.load_scenario("S1")["bess"]
    shift = sc.shift_surplus_with_battery(cut, 100.0 - exp, s1["power_mw"],
                                          s1["usable_energy_mwh_bol"],
                                          s1["roundtrip_efficiency_ac_pct"] / 100)
    got = {"pv_gwh": round(pv.sum() / 1000, 1), "wind_gwh": round(wind.sum() / 1000, 1),
           "export_gwh": round(exp.sum() / 1000, 1), "curtailed_mwh": round(cut.sum(), 1),
           "s1_delivered_mwh": round(shift.delivered_mwh, 1)}
    exp_json = json.loads((datapack.release_dir() / "expected_results.json").read_text())
    lines = ["chapter 1 screening model on release 1.1.0 vs the published chapter 1 numbers:"]
    for k, v in got.items():
        lines.append(f"  {k:18s} {v:8.1f}  published {PUBLISHED[k]:8.1f}  "
                     f"{'PASS' if v == PUBLISHED[k] else 'FAIL'}")
    ghi = round(float(h["ghi_wm2"].sum()) / 1000, 1)
    lines.append(f"  annual GHI {ghi} kWh/m2, expected_results.json {exp_json['annual_ghi_kwh_m2']}: "
                 f"{'PASS' if ghi == exp_json['annual_ghi_kwh_m2'] else 'FAIL'}")
    lines.append(f"S1 in this model: charged {shift.charged_mwh:.1f} MWh, delivered "
                 f"{shift.delivered_mwh:.1f} MWh (one role only: store what would be cut)")
    emit("f_reproduce", lines)
    return got


def f4_publish(checks: dict, got: dict) -> None:
    man = datapack.load_manifest()
    used = ["timeseries/plantp_hourly_8760.csv",
            "equipment/wind_turbine_WT-5.0-150_power_curve.csv",
            "scenarios/S0-no-bess.yml", "scenarios/S1-bess.yml"]
    lines = ["# Plant P data-pack verification - release " + man["release"], "",
             "Document PLP-GEN-REP-0003, revision A, status IFR. Synthetic teaching data.", "",
             "## Inputs", ""]
    lines += [f"- `{f}` SHA-256 `{man['files'][f]['sha256']}`" for f in used]
    lines += ["", "## Checks", ""] + [f"- {'PASS' if ok else 'FAIL'}: {n}" for n, ok in checks.items()]
    lines += ["", "## Reproduced results (chapter 1 model)", "", "| quantity | value |",
              "|---|---:|"] + [f"| {k} | {v} |" for k, v in got.items()]
    lines += ["", "Citation: " + datapack.cite("S0") + "; " + datapack.cite("S1"), ""]
    out = HERE / "output" / "PLP-GEN-REP-0003_rev-A.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    emit("f_publish", [f"report written: {out.name} ({len(lines)} lines)",
                       f"  first input hash {man['files'][used[0]]['sha256'][:24]}...",
                       f"  all checks pass: {all(checks.values())}; all results reproduced: "
                       f"{all(got[k] == PUBLISHED[k] for k in got)}"])


if __name__ == "__main__":
    f1_release()
    c = f2_validate()
    g = f3_reproduce()
    f4_publish(c, g)
