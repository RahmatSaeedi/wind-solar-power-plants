"""Raw met-mast logger data: read, normalise time, clean, flag and aggregate.

The logger file of data pack 1.1.0 (A-089) labels each 10-minute interval by
its END, in local standard time UTC+04:00 without the offset written. Every
step below records what it did, so the report can say what was changed.

Flags per value: 0 valid, 1 adjusted, 2 suspect (not used), 9 missing.
"""
from __future__ import annotations

import csv
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

LOCAL = timezone(timedelta(hours=4))
STEP = timedelta(minutes=10)
# [start: limits]
LIMITS = {"ws100_avg": (0, 45), "ws100_sd": (0, 10), "ws80_avg": (0, 45),
          "ws60_avg": (0, 45), "wd100_avg": (0, 360), "t_air": (-40, 55),
          "p_air": (800, 950), "ghi": (0, 1400)}
SENTINELS = {-9999.0, -999.0, 9999.0}
FLAT_RUN = 6                   # identical speeds in a row = stuck (1 hour)
# [end: limits]


def read_logger(path):
    """(header comment lines, rows as dictionaries of text)."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    header = [ln for ln in lines if ln.startswith("#")]
    body = [ln for ln in lines if ln and not ln.startswith("#")]
    return header, list(csv.DictReader(body))


# [start: parse]
def parse(rows):
    """Text rows -> records with a UTC interval START and float values."""
    records = []
    for r in rows:
        end = datetime.strptime(r["timestamp"], "%Y-%m-%d %H:%M")
        start = (end.replace(tzinfo=LOCAL) - STEP).astimezone(timezone.utc)
        rec = {"start": start}
        for col in LIMITS:
            rec[col] = float(r[col])
        records.append(rec)
    return records
# [end: parse]


# [start: clean]
def clean(records):
    """Sort, drop exact duplicates, report gaps; returns (records, log)."""
    log = {"out_of_order": 0, "duplicates": 0, "gaps": []}
    for a, b in zip(records, records[1:]):
        if b["start"] < a["start"]:
            log["out_of_order"] += 1
    ordered = sorted(records, key=lambda r: r["start"])
    unique = []
    for r in ordered:
        if unique and r["start"] == unique[-1]["start"]:
            if r == unique[-1]:
                log["duplicates"] += 1
                continue
            raise ValueError(f"two different records at {r['start']}")
        unique.append(r)
    for a, b in zip(unique, unique[1:]):
        if b["start"] - a["start"] != STEP:
            missing = (b["start"] - a["start"]) // STEP - 1
            log["gaps"].append((a["start"] + STEP, int(missing)))
    return unique, log
# [end: clean]


# [start: flag]
def flag(records):
    """Add a flag for every value; adjust what can be safely corrected."""
    counts = {}
    for r in records:
        r["flags"] = {}
        for col, (low, high) in LIMITS.items():
            v, f = r[col], 0
            if v in SENTINELS:
                v, f, why = math.nan, 9, "sentinel"
            elif col == "p_air" and 80 <= v <= 95:
                v, f, why = v * 10, 1, "kPa -> hPa"
            elif col == "ghi" and -5 <= v < 0:
                v, f, why = 0.0, 1, "night offset -> 0"
            elif not low <= v <= high:
                v, f, why = math.nan, 9, "out of range"
            r[col], r["flags"][col] = v, f
            if f:
                counts[(col, why)] = counts.get((col, why), 0) + 1
    for col in ("ws100_avg", "ws80_avg", "ws60_avg"):
        run = 1
        for k in range(1, len(records) + 1):
            same = (k < len(records) and
                    records[k][col] == records[k - 1][col])
            if same:
                run += 1
                continue
            if run >= FLAT_RUN:
                for r in records[k - run:k]:
                    r[col], r["flags"][col] = math.nan, 9
                counts[(col, "stuck")] = counts.get((col, "stuck"), 0) + run
            run = 1
    return counts
# [end: flag]


# [start: hourly]
def vector_mean(directions):
    s = sum(math.sin(math.radians(d)) for d in directions)
    c = sum(math.cos(math.radians(d)) for d in directions)
    return round(math.degrees(math.atan2(s, c)), 9) % 360.0


def hourly(records, min_count=5):
    """Hour (UTC start) -> {column: mean or NaN, 'n': values used}."""
    groups = {}
    for r in records:
        h = r["start"].replace(minute=0)
        groups.setdefault(h, []).append(r)
    out = {}
    for h, rs in sorted(groups.items()):
        row = {}
        for col in LIMITS:
            vals = [r[col] for r in rs if not math.isnan(r[col])]
            if len(vals) < min_count:
                row[col] = math.nan
            elif col == "wd100_avg":
                row[col] = vector_mean(vals)
            else:
                row[col] = sum(vals) / len(vals)
        row["n"] = len(rs)
        out[h] = row
    return out
# [end: hourly]


def validate(path):
    """Whole chain; returns (hourly table, summary dictionary)."""
    header, rows = read_logger(path)
    records = parse(rows)
    records, log = clean(records)
    counts = flag(records)
    table = hourly(records)
    incomplete = [h for h, r in table.items() if r["n"] < 5]
    summary = {"records_read": len(rows), "records_kept": len(records),
               "out_of_order": log["out_of_order"],
               "duplicates": log["duplicates"],
               "gaps": [(t.astimezone(LOCAL).strftime("%Y-%m-%d %H:%M"), n)
                        for t, n in log["gaps"]],
               "flags": {f"{c}: {w}": n
                         for (c, w), n in sorted(counts.items())},
               "hours": len(table), "incomplete_hours": len(incomplete),
               "header": header}
    return table, summary
