"""Command-line interface of resource_tool: three commands, clear exit codes.

Exit codes: 0 success; 1 the data have problems (report written anyway);
2 the request cannot be carried out (bad arguments or configuration).
"""
from __future__ import annotations

import argparse
import json
import math
import sys

from companion.ch05.resource_tool import __version__


# [start: cli]
def build_parser():
    ap = argparse.ArgumentParser(
        prog="resource_tool",
        description="Plant P resource analysis (chapter 5, teaching tool)")
    ap.add_argument("--version", action="version", version=__version__)
    sub = ap.add_subparsers(dest="command", required=True)
    v = sub.add_parser("validate-raw", help="check a 10-min logger file")
    v.add_argument("path", nargs="?", help="default: the data pack sample")
    v.add_argument("--out", default="companion/ch05/output/qc.json")
    r = sub.add_parser("run", help="calculate energies from a run file")
    r.add_argument("config")
    p = sub.add_parser("report", help="write the Markdown report")
    p.add_argument("folder")
    p.add_argument("--qc", default="companion/ch05/output/qc.json")
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.command == "validate-raw":
        return cmd_validate(args)
    if args.command == "run":
        return cmd_run(args)
    return cmd_report(args)
# [end: cli]


def cmd_validate(args):
    from pathlib import Path
    from plantp import datapack
    from companion.ch05.resource_tool import rawdata
    path = args.path or datapack.raw_path("met_mast_10min_raw.csv")
    table, summary = rawdata.validate(path)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(summary, indent=1) + "\n",
                              encoding="utf-8")
    print(f"{summary['records_read']} records, {summary['duplicates']} "
          f"duplicate(s), {summary['out_of_order']} out of order, "
          f"gaps {summary['gaps']}")
    for k, n in summary["flags"].items():
        print(f"  flagged {k}: {n}")
    usable = sum(1 for r in table.values() if not math.isnan(r["ws100_avg"]))
    print(f"{usable} of {summary['hours']} hours usable for ws100")
    has_problems = bool(summary["flags"] or summary["gaps"])
    return 1 if has_problems else 0


def cmd_run(args):
    from companion.ch05.resource_tool import run
    try:
        cfg = run.load_config(args.config)
    except (OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    results, series = run.run(cfg)
    folder = run.write(cfg, results, series)
    for k in ("pv_gwh", "wind_gwh", "export_gwh", "curtailed_mwh"):
        print(f"{k:14s} {results[k]}")
    if "bess" in results:
        print(f"{'bess':14s} {results['bess']}")
    print("written:", folder.relative_to(run.ROOT).as_posix())
    return 0


def cmd_report(args):
    from companion.ch05.resource_tool import report
    try:
        out = report.write_report(args.folder, args.qc)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    print("report:", out.as_posix())
    return 0
