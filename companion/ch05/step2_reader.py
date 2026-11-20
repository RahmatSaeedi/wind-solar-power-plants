"""Step 2: a validated reader for the PV SCADA export of data pack 1.1.0.

The file uses ';' between fields, a decimal comma, UTC time stamps ending in Z
and energy in kWh per hour (A-090). The reader converts to MWh, checks every
row and the time axis, and reports ALL problems instead of stopping at one.

    python -m companion.ch05.step2_reader [path]
"""
from __future__ import annotations

import csv
import sys
from datetime import datetime, timedelta, timezone

# [start: reader]
FIELDS = ["time_utc", "energy_kwh", "availability_pct"]
MAX_KWH = 60_000.0               # 60 MWp for one hour: a physical ceiling


def number(text):
    """'12345,6' -> 12345.6 (decimal comma); raises ValueError."""
    return float(text.strip().replace(",", "."))


def read_scada(path):
    rows, issues = [], []
    with open(path, encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh, delimiter=";")
        header = next(reader, None)
        if header != FIELDS:
            return [], [f"header {header} is not {FIELDS}"]
        for n, rec in enumerate(reader, start=2):
            if len(rec) != len(FIELDS):
                issues.append(f"line {n}: {len(rec)} fields, expected 3")
                continue
            try:
                t = datetime.fromisoformat(rec[0].replace("Z", "+00:00"))
                kwh, avail = number(rec[1]), number(rec[2])
            except ValueError as e:
                issues.append(f"line {n}: {e}")
                continue
            if t.utcoffset() != timedelta(0):
                issues.append(f"line {n}: time {rec[0]} is not UTC")
            if not 0 <= kwh <= MAX_KWH:
                issues.append(f"line {n}: energy {kwh} kWh out of range")
            if not 0 <= avail <= 100:
                issues.append(f"line {n}: availability {avail} % out of range")
            rows.append({"start": t, "energy_mwh": kwh / 1000.0,
                         "availability": avail / 100.0})
    for a, b in zip(rows, rows[1:]):
        step = b["start"] - a["start"]
        if step != timedelta(hours=1):
            issues.append(f"after {a['start']:%Y-%m-%d %H:%M}Z: step {step}")
    return rows, issues
# [end: reader]


# [start: cli]
def main(argv=None):
    from plantp import datapack
    argv = sys.argv[1:] if argv is None else argv
    path = argv[0] if argv else datapack.raw_path("pv_scada_export.csv")
    rows, issues = read_scada(path)
    local = timezone(timedelta(hours=4))
    print(f"{len(rows)} valid rows, {len(issues)} issue(s)")
    for i in issues:
        print("  issue:", i)
    if rows:
        print("first hour (local):", rows[0]["start"].astimezone(local))
        total = sum(r["energy_mwh"] for r in rows)
        print(f"energy in the file: {total:,.1f} MWh")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
# [end: cli]
