"""Appendix Q - the Plant P Reference Data Pack read from its own files:
manifest, scenario cards, data dictionary, expected-results checks
recomputed from the hourly file, and the release history with checksums.

Run from the project root:   python -m companion.appx.appendix_q
Writes companion/appx/expected/appq_*.txt.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import yaml

from companion.appx.common import emit
from plantp import datapack

ROOT = Path(__file__).resolve().parents[1] / "plantp_data"
REL = "1.1.0"


def manifest() -> dict:
    m = json.loads((ROOT / REL / "manifest.json").read_text(encoding="utf-8"))
    s = m["site"]
    lines = [f"manifest of release {m['release']} ({m['created']})",
             f"  status: {m['status']}",
             f"  generator: {m['generator']}, seed {m['seed']}",
             f"  site: {s['latitude_deg_n']} N, {s['elevation_m']:.0f} m, UTC{s['utc_offset']};"
             f" year label {s['calendar_year_label']}",
             f"  time stamps: {s['timestamp_convention']}",
             f"  supersedes {m['supersedes']}: {m['compatibility']}",
             f"  files: {len(m['files'])} (first 10 hex digits of the SHA-256, bytes)"]
    for name, f in sorted(m["files"].items()):
        lines.append(f"    {name:50s} {f['sha256'][:10]}  {f['bytes']:>8,d}")
    emit("appq_manifest", lines)
    return m


def cards() -> None:
    lines = ["scenario cards (every BESS exercise states these or the ones it changes)"]
    for name in ("S0-no-bess.yml", "S1-bess.yml"):
        c = yaml.safe_load((ROOT / REL / "scenarios" / name).read_text(encoding="utf-8"))
        lines.append(f"  {c['id']} {c['name']} ({c['status']}): PV {c['pv']['dc_mwp']} MWp DC /"
                     f" {c['pv']['ac_mw']} MW AC; wind {c['wind']['ac_mw']} MW"
                     f" ({c['wind']['turbines']} x {c['wind']['turbine_id']});"
                     f" export {c['export_limit_mw']} MW")
        b = c["bess"]
        if b is None:
            lines.append("      battery: none")
        else:
            lines += [f"      battery {b['power_mw']} MW / {b['energy_mwh_nominal_bol']} MWh nominal,"
                      f" window {b['soc_window_pct'][0]}-{b['soc_window_pct'][1]} %,"
                      f" usable {b['usable_energy_mwh_bol']} MWh",
                      f"      round trip {b['roundtrip_efficiency_ac_pct']} % AC, fade"
                      f" {b['capacity_fade_pct_per_year']} %/yr, reserve {b['reserve_mwh']} MWh",
                      f"      charging: {b['charging_source']};"
                      f" grid charging {'yes' if b['grid_charging_permitted'] else 'no'}"]
    emit("appq_cards", lines)


def dictionary() -> None:
    rows = list(csv.DictReader(open(ROOT / REL / "data_dictionary.csv", encoding="utf-8")))
    lines = [f"data dictionary: {len(rows)} rows (file, column, unit, status)"]
    last = None
    for r in rows:
        f = r["file"]
        if f != last:
            lines.append(f"  {f}")
            last = f
        lines.append(f"      {r['column'][:30]:30s} {r['unit'][:12]:12s} {r['status']}")
    emit("appq_dictionary", lines)


def expected() -> dict:
    exp = json.loads((ROOT / REL / "expected_results.json").read_text(encoding="utf-8"))
    rows = list(csv.DictReader(open(ROOT / REL / "timeseries" / "plantp_hourly_8760.csv",
                                    encoding="utf-8")))

    def col(k):
        return [float(r[k]) for r in rows]
    got = {"hours": len(rows),
           "annual_ghi_kwh_m2": sum(col("ghi_wm2")) / 1000,
           "annual_dni_kwh_m2": sum(col("dni_wm2")) / 1000,
           "max_ghi_wm2": max(col("ghi_wm2")),
           "mean_t_air_c": sum(col("t_air_c")) / len(rows),
           "min_t_air_c": min(col("t_air_c")),
           "max_t_air_c": max(col("t_air_c")),
           "mean_ws_100m_ms": sum(col("ws_100m_ms")) / len(rows),
           "max_ws_100m_ms": max(col("ws_100m_ms")),
           "mean_p_hpa": sum(col("p_hpa")) / len(rows)}
    lines = ["expected results recomputed from the hourly file (tolerance 0.05 %)",
             f"  {'quantity':22s} {'expected':>10s} {'computed':>10s}  check"]
    ok = 0
    for k, v in got.items():
        e = exp[k]
        good = abs(v - e) <= max(abs(e) * 5e-4, 0.01)
        ok += good
        lines.append(f"  {k:22s} {e:10.2f} {v:10.2f}  {'pass' if good else 'FAIL'}")
    lines.append(f"  {ok} of {len(got)} pass; a failed check means the file or the reader changed")
    emit("appq_expected", lines)
    return dict(ok=ok, n=len(got))


def history() -> None:
    lines = ["releases and their checksum verification"]
    for rel in ("1.0.0", "1.1.0"):
        probs = datapack.verify(rel)
        lines.append(f"  {rel}: {'all checksums match' if not probs else f'{len(probs)} problems'}")
    log = (ROOT / REL / "CHANGELOG.md").read_text(encoding="utf-8").splitlines()
    heads = [x[3:].replace(" — ", " of ") for x in log if x.startswith("## ")]
    lines.append("  change log entries: " + "; ".join(heads))
    lines += ["  rule in the change log: additions only, backwards compatible ->",
              "  minor release; each entry states its reason and the dependent",
              "  artefacts (ch 5)"]
    emit("appq_history", lines)


def main() -> None:
    manifest()
    cards()
    dictionary()
    expected()
    history()


if __name__ == "__main__":
    main()
