"""Engineering data handling, chapter 5: validated CSV input, time stamps, aggregation and
raw register decoding.

    Field, validate_rows     a small schema (type, unit, range, required) and its checker
    read_csv_rows            read a CSV with an explicit encoding into dictionaries
    check_timestamps         parse ISO 8601 stamps; report duplicates, gaps, order, offsets
    aggregate_hourly         time-zone-safe averaging of interval data into hours
    qc_range, qc_step, qc_flat   quality tests: limits, jumps, stuck sensors
    vector_mean_deg          mean of directions through unit vectors
    decode_float32           two 16-bit registers -> IEEE 754 single (big-endian words)
    to_int16                 unsigned 16-bit register -> signed value

Every check returns a list of human-readable issues instead of stopping at the first.
"""
from __future__ import annotations

import csv
import struct
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


@dataclass
class Field:
    name: str
    kind: type = float              # float, int or str
    unit: str = ""
    minimum: float | None = None
    maximum: float | None = None
    required: bool = True


def read_csv_rows(path: str | Path, encoding: str = "utf-8") -> list[dict]:
    """All rows as dictionaries. A UTF-8 byte-order mark is refused, not silently kept."""
    raw = Path(path).read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"{path}: file starts with a byte-order mark")
    text = raw.decode(encoding)
    return list(csv.DictReader(text.splitlines()))


def validate_rows(rows: list[dict], schema: list[Field]) -> tuple[list[dict], list[str]]:
    """Convert and check each row. Returns (clean rows, issues). A row with an issue in a
    required field is left out of the clean rows; optional empty fields become None."""
    issues: list[str] = []
    clean: list[dict] = []
    if rows:
        missing_cols = [f.name for f in schema if f.name not in rows[0]]
        if missing_cols:
            return [], [f"missing column(s): {', '.join(missing_cols)}"]
    for n, row in enumerate(rows, start=2):           # line 1 is the header
        out, ok = {}, True
        for f in schema:
            text = (row.get(f.name) or "").strip()
            if text == "":
                if f.required:
                    issues.append(f"line {n}: {f.name} is empty")
                    ok = False
                out[f.name] = None
                continue
            try:
                value = f.kind(text)
            except ValueError:
                issues.append(f"line {n}: {f.name} = {text!r} is not {f.kind.__name__}")
                ok = False
                continue
            if f.minimum is not None and value < f.minimum:
                issues.append(f"line {n}: {f.name} = {value} below {f.minimum} {f.unit}")
                ok = False
            if f.maximum is not None and value > f.maximum:
                issues.append(f"line {n}: {f.name} = {value} above {f.maximum} {f.unit}")
                ok = False
            out[f.name] = value
        if ok:
            clean.append(out)
    return clean, issues


def check_timestamps(stamps: list[str], step: timedelta = timedelta(hours=1)
                     ) -> tuple[list[datetime], list[str]]:
    """Parse ISO 8601 stamps that carry an offset; report problems in UTC terms."""
    issues: list[str] = []
    parsed: list[datetime] = []
    offsets = set()
    for n, s in enumerate(stamps):
        try:
            t = datetime.fromisoformat(s)
        except ValueError:
            issues.append(f"row {n}: {s!r} is not ISO 8601")
            continue
        if t.tzinfo is None:
            issues.append(f"row {n}: {s!r} has no UTC offset")
            continue
        offsets.add(t.utcoffset())
        parsed.append(t.astimezone(timezone.utc))
    if len(offsets) > 1:
        issues.append(f"mixed UTC offsets: {sorted(str(o) for o in offsets)}")
    seen = set()
    for a, b in zip(parsed[:-1], parsed[1:]):
        if b <= a:
            issues.append(f"not increasing at {b.isoformat()}")
        elif b - a != step:
            issues.append(f"gap of {b - a} after {a.isoformat()}")
    for t in parsed:
        if t in seen:
            issues.append(f"duplicate {t.isoformat()}")
        seen.add(t)
    return parsed, issues


def aggregate_hourly(times_utc: list[datetime], values: list[float],
                     min_count: int = 1) -> dict[datetime, tuple[float, int]]:
    """Average interval values into the hour that CONTAINS each interval start (UTC).

    Returns {hour start: (mean, count)}; hours with fewer than min_count values are dropped.
    """
    sums: dict[datetime, list[float]] = {}
    for t, v in zip(times_utc, values):
        if t.tzinfo is None:
            raise ValueError("times must be time-zone aware")
        h = t.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)
        sums.setdefault(h, []).append(v)
    return {h: (sum(v) / len(v), len(v)) for h, v in sorted(sums.items()) if len(v) >= min_count}


def qc_range(values, low: float, high: float):
    """True where a value lies outside [low, high] or is not a number."""
    import numpy as np
    v = np.asarray(values, dtype=float)
    return ~((v >= low) & (v <= high))


def qc_step(values, max_step: float):
    """True where the change from the previous value exceeds max_step."""
    import numpy as np
    v = np.asarray(values, dtype=float)
    out = np.zeros(v.size, dtype=bool)
    out[1:] = np.abs(np.diff(v)) > max_step
    return out


def qc_flat(values, min_run: int, tol: float = 0.0):
    """True inside every run of at least min_run consecutive (nearly) equal values."""
    import numpy as np
    v = np.asarray(values, dtype=float)
    out = np.zeros(v.size, dtype=bool)
    start = 0
    for k in range(1, v.size + 1):
        if k == v.size or abs(v[k] - v[k - 1]) > tol:
            if k - start >= min_run:
                out[start:k] = True
            start = k
    return out


def vector_mean_deg(directions_deg) -> float:
    """Mean wind direction by unit vectors (the arithmetic mean fails across north)."""
    import math
    s = sum(math.sin(math.radians(d)) for d in directions_deg)
    c = sum(math.cos(math.radians(d)) for d in directions_deg)
    return round(math.degrees(math.atan2(s, c)), 9) % 360.0


def to_int16(register: int) -> int:
    if not 0 <= register <= 0xFFFF:
        raise ValueError("a 16-bit register holds 0..65535")
    return register - 0x10000 if register & 0x8000 else register


def decode_float32(high_word: int, low_word: int) -> float:
    """IEEE 754 single precision from two 16-bit registers, high word first."""
    return struct.unpack(">f", struct.pack(">HH", high_word, low_word))[0]
