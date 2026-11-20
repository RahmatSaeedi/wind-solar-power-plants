"""Turn results.json (and an optional raw-data summary) into a Markdown report
whose every number can be traced to a release, a hash and a configuration."""
from __future__ import annotations

import json
from pathlib import Path

DOC = "PLP-GEN-REP-0002"


# [start: report]
def render(results, qc=None, rev="A", status="IFR"):
    r = results
    lines = [f"# Plant P resource analysis - {r['scenario']}",
             "",
             f"Document {DOC}, revision {rev}, status {status}. Synthetic "
             "teaching data; not a design.",
             "",
             "## Inputs and provenance",
             "",
             f"- Data pack release {r['data_release']}; run {r['run_id']}",
             f"- Configuration SHA-256 `{r['config_sha256'][:16]}...`"]
    for name, digest in r["inputs"].items():
        lines.append(f"- `{name}` SHA-256 `{digest[:16]}...`")
    sw = ", ".join(f"{k} {v}" for k, v in r["software"].items())
    lines += [f"- Software: {sw}", "",
              "## Results", "",
              "| quantity | value | unit |", "|---|---:|---|",
              f"| PV energy | {r['pv_gwh']:.2f} | GWh/yr |",
              f"| wind energy | {r['wind_gwh']:.2f} | GWh/yr |",
              f"| export at the point of connection | {r['export_gwh']:.2f} "
              "| GWh/yr |",
              f"| curtailed | {r['curtailed_mwh']:.1f} | MWh/yr |",
              f"| mean air density | {r['mean_air_density']:.4f} | kg/m3 |"]
    if "bess" in r:
        lines.append(f"| battery: delivered later | "
                     f"{r['bess']['delivered_mwh']:.1f} | MWh/yr |")
    if qc:
        lines += ["", "## Raw-data checks (met mast, 10 min)", "",
                  f"- {qc['records_read']} records read, "
                  f"{qc['records_kept']} kept; "
                  f"{qc['duplicates']} duplicate(s), "
                  f"{qc['out_of_order']} out of order",
                  f"- gaps: {qc['gaps']}; incomplete hours: "
                  f"{qc['incomplete_hours']} of {qc['hours']}"]
        for k, n in qc["flags"].items():
            lines.append(f"- flagged {k}: {n}")
    lines += ["", "## Limitations", "",
              "- Horizontal irradiance on the array; NOCT temperature model;",
              "  lumped losses (A-097; density by D-008).",
              "  Chapters 10, 11 and 15 refine these models.",
              "- Synthetic one-year series; no long-term correction (ch. 13).",
              "", "## Checks and sign-off", "",
              "| role | name | date |", "|---|---|---|",
              "| prepared |  |  |", "| checked |  |  |", "| approved |  |  |"]
    return "\n".join(lines) + "\n"
# [end: report]


def write_report(folder, qc_path=None):
    folder = Path(folder)
    results = json.loads((folder / "results.json").read_text(encoding="utf-8"))
    qc = None
    if qc_path and Path(qc_path).exists():
        qc = json.loads(Path(qc_path).read_text(encoding="utf-8"))
    out = folder / f"{DOC}_rev-A.md"
    out.write_text(render(results, qc), encoding="utf-8")
    return out
