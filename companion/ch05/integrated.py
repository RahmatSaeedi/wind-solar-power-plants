"""Chapter 5 - three integrated Plant P examples.

    int_1  capacity factors with unit-aware quantities and their checks
    int_2  three days of raw mast data turned into checked wind energy
    int_3  the deliverable: register rev C, exchange package and manifest

Run from the project root:   python -m companion.ch05.integrated
Data pack 1.1.0, scenario S0 (synthetic); assumptions A-089 .. A-099.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math

import numpy as np
import pandas as pd

from companion.ch05 import step3_model as m
from companion.ch05.common import HERE, emit
from companion.ch05.resource_tool import rawdata, run
from plantp import assets, datapack
from plantp.units import DimensionError, Q

OUT = HERE / "output"


def int_1() -> None:
    res, _ = run.run(run.load_config(HERE / "config" / "run_S0.yml"))
    hours = Q(res["hours"], "h")
    rows = [("PV", res["pv_gwh"], 50), ("wind", res["wind_gwh"], 60),
            ("export", res["export_gwh"], 100)]
    lines = [f"data pack {res['data_release']}, S0, chapter 5 models; "
             f"{res['hours']} hours from the data"]
    for name, gwh, rated in rows:
        cf = (Q(gwh, "GWh") / (Q(rated, "MW") * hours)).to("")
        lines.append(f"  {name:6s} {gwh:7.2f} GWh / ({rated:3d} MW x 8760 h) = "
                     f"{cf:.3f}")
        assert 0 <= cf <= 1
    try:
        Q(96.43, "GWh") + Q(50, "MW")
    except DimensionError as e:
        lines.append(f"guard: GWh + MW refused ({type(e).__name__})")
    pv_share = res["pv_gwh"] / (res["pv_gwh"] + res["wind_gwh"])
    lines += [f"checks: every factor in 0..1; PV share of energy {pv_share:.2f};",
              "  export = PV + wind because nothing is curtailed in this model"]
    emit("int_1", lines)


def int_2() -> None:
    table, summary = rawdata.validate(datapack.raw_path("met_mast_10min_raw.csv"))
    curve = datapack.load_power_curve()
    ref = datapack.load_hourly()
    e_raw, e_ref, used, gap_fill = 0.0, 0.0, 0, 0.0
    pairs = []
    for hour, row in table.items():
        local = pd.Timestamp(hour).tz_convert("+04:00")
        r = ref.loc[local]
        p_ref = float(m.wind_farm_mw(r["ws_100m_ms"], m.air_density(r["p_hpa"], r["t_air_c"]),
                                     curve["wind_speed_ms"], curve["power_kw"]))
        e_ref += p_ref
        if math.isnan(row["ws100_avg"]) or math.isnan(row["t_air"]) or math.isnan(row["p_air"]):
            gap_fill += p_ref
            continue
        rho = m.air_density(row["p_air"], row["t_air"])
        p_raw = float(m.wind_farm_mw(row["ws100_avg"], rho, curve["wind_speed_ms"],
                                     curve["power_kw"]))
        e_raw += p_raw
        nxt = local + pd.Timedelta(hours=1)
        p_next = float("nan")
        if nxt in ref.index:
            rn = ref.loc[nxt]
            p_next = float(m.wind_farm_mw(rn["ws_100m_ms"],
                                          m.air_density(rn["p_hpa"], rn["t_air_c"]),
                                          curve["wind_speed_ms"], curve["power_kw"]))
        pairs.append((p_raw, p_ref, p_next))
        used += 1
    arr = np.array(pairs)
    rms_ok = float(np.sqrt(np.mean((arr[:, 0] - arr[:, 1]) ** 2)))
    ok = ~np.isnan(arr[:, 2])
    rms_shift = float(np.sqrt(np.mean((arr[ok, 0] - arr[ok, 2]) ** 2)))
    n_gap = summary["hours"] - used
    emit("int_2", [
        f"raw mast file, 3-5 April: {summary['hours']} hours, {used} with complete "
        "speed, temperature and pressure",
        f"  wind energy from the cleaned raw hours: {e_raw:,.1f} MWh",
        f"  {n_gap} incomplete hour{'s' if n_gap != 1 else ''} taken from the reference "
        f"series (flag 1): {gap_fill:,.1f} MWh",
        f"  total {e_raw + gap_fill:,.1f} MWh; reference series alone {e_ref:,.1f} MWh "
        f"(difference {100 * (e_raw + gap_fill - e_ref) / e_ref:+.3f} %)",
        f"hour-by-hour RMS difference raw vs reference: {rms_ok:.2f} MW;",
        f"  with every raw hour compared one hour late (labels misread): {rms_shift:.1f} MW",
    ])


def fix_register(rev_b: list[dict]) -> list[dict]:
    """Rev C: rev B with each editing error corrected by a recorded decision."""
    seen, out = set(), []
    for r in rev_b:
        r = dict(r)
        if r["tag"] in seen:                                   # duplicate row
            continue
        if r["tag"] == "PLP-WTG-13-GEN":                        # no turbine 13
            continue
        if r["tag"] == "PLP-SWG-01":
            r["criticality"] = "A"
        if r["tag"] == "PLP-WTG-07-GEN":
            r["commissioned"] = "2026-03-15"                    # per CN-001
        if r["tag"] == "PLP-MET-01-HYG":
            r["commissioned"] = ""                              # until serial known
        r["description_fa"] = assets.normalise_persian(r["description_fa"])
        seen.add(r["tag"])
        out.append(r)
    return out


def int_3() -> None:
    rev_a, rev_b = datapack.load_register("A"), datapack.load_register("B")
    rev_c = fix_register(rev_b)
    issues = assets.validate_register(rev_c)
    rec = assets.reconcile(rev_a, rev_c, datapack.load_change_notice())
    OUT.mkdir(exist_ok=True)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rev_c[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(rev_c)
    reg_text = buf.getvalue()
    cmms = assets.to_cmms(rev_c)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(cmms[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(cmms)
    cmms_text = buf.getvalue()
    field_map = "register_field,cmms_field\n" + "".join(
        f"{k},{v}\n" for k, v in assets.CMMS_MAP.items())
    files = {"PLP-GEN-REG-0002_rev-C.csv": reg_text,
             "PLP-GEN-LST-0001_cmms_export.csv": cmms_text,
             "PLP-GEN-LST-0001_field_map.csv": field_map}
    manifest = {name: hashlib.sha256(text.encode("utf-8")).hexdigest()
                for name, text in files.items()}
    for name, text in files.items():
        (OUT / name).write_text(text, encoding="utf-8")
    (OUT / "PLP-GEN-LST-0001_manifest.json").write_text(
        json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    cut = sum(1 for r in rev_c if len(r["description"]) > 40)
    lines = [f"register rev C: {len(rev_c)} records, validation issues: {len(issues)}",
             f"  against the change notice: {len(rec['approved'])} approved, "
             f"{len(rec['unapproved'])} unapproved, {len(rec['not_done'])} not done"]
    lines += [f"    unapproved: {x}" for x in rec["unapproved"]]
    lines += ["exchange package PLP-GEN-LST-0001 (files and SHA-256):"]
    lines += [f"  {name:34s} {digest[:16]}..." for name, digest in manifest.items()]
    lines += [f"  {cut} descriptions longer than 40 characters stay complete in the",
              "  register (owner decision); the CMMS keeps the cut text and the tag link"]
    emit("int_3", lines)


if __name__ == "__main__":
    int_1()
    int_2()
    int_3()
