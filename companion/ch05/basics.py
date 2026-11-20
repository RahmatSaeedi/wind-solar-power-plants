"""Chapter 5, section B - programming from zero. Each demo is quoted in the
book between its [start]/[end] markers; main() runs every demo and saves what
it prints.

Run from the project root:   python -m companion.ch05.basics
"""
from __future__ import annotations

import contextlib
import io
import sys

from companion.ch05.common import emit


# [start: first]
def first_program():
    p_mw = 60.0                  # rated power of the wind farm
    hours = 8760                 # hours in a non-leap year
    cf = 0.366                   # capacity factor (chapter 1)
    energy_mwh = p_mw * hours * cf
    print(f"annual energy: {energy_mwh:,.0f} MWh")
    print(f"             = {energy_mwh / 1000:.1f} GWh")
# [end: first]


# [start: types]
def types_demo():
    n_turbines = 12              # int: a count
    rated_mw = 5.0               # float: a measured or rated quantity
    tag = "PLP-WTG-07"           # str: text
    online = True                # bool: yes / no
    serial = None                # None: "no value yet"
    for x in (n_turbines, rated_mw, tag, online, serial):
        print(f"{x!r:14} is {type(x).__name__}")
    print("7 / 2 =", 7 / 2, "  7 // 2 =", 7 // 2, "  7 % 2 =", 7 % 2)
    print("int('42') + 1 =", int("42") + 1, " '42' + '1' =", "42" + "1")
    print("float('7.10') =", float("7.10"), "  str(3.0) =", str(3.0))
# [end: types]


# [start: conditions]
def region(v_ms):
    """Operating region of the WT-5.0-150 power curve at hub height."""
    if v_ms < 0:
        raise ValueError("wind speed cannot be negative")
    if v_ms < 3.0:
        return "below cut-in"
    elif v_ms < 13.0:
        return "partial load"
    elif v_ms <= 25.0:
        return "rated power"
    else:
        return "stopped (above cut-out)"


def conditions_demo():
    for v in (2.0, 8.0, 13.0, 25.0, 26.5):
        print(f"{v:5.1f} m/s -> {region(v)}")
# [end: conditions]


# [start: loops]
def loops_demo():
    pv_mw = [0, 0, 0, 0, 0, 1.2, 8.5, 20.1, 31.0, 39.2, 44.0, 46.1,
             46.0, 43.5, 38.0, 29.7, 18.6, 6.9, 0.5, 0, 0, 0, 0, 0]
    energy, peak, peak_hour = 0.0, 0.0, None
    for hour, p in enumerate(pv_mw):         # one step = one hour
        energy += p * 1.0                    # MW x 1 h = MWh
        if p > peak:
            peak, peak_hour = p, hour
    print(f"day energy {energy:.1f} MWh, peak {peak} MW at {peak_hour}:00")
    soc, steps = 4.0, 0                      # battery stored energy, MWh
    while soc < 36.0:                        # charge at 10 MWh per step
        soc = min(soc + 10.0, 36.0)
        steps += 1
    print(f"full after {steps} steps, stored {soc} MWh")
# [end: loops]


# [start: functions]
def capacity_factor(energy_mwh, rated_mw, hours=8760):
    """Energy produced / energy at rated power for every hour.

    energy_mwh: energy in the period (MWh); rated_mw: rating (MW);
    hours: length of the period (h). Raises ValueError on bad input.
    """
    if rated_mw <= 0 or hours <= 0:
        raise ValueError("rated power and hours must be positive")
    if energy_mwh < 0:
        raise ValueError("energy cannot be negative")
    return energy_mwh / (rated_mw * hours)


log = []                                     # a global list (avoid this)


def impure_cf(energy_mwh, rated_mw):
    log.append(energy_mwh)                   # side effect: changes the world
    return energy_mwh / (rated_mw * 8760)


def functions_demo():
    print("pure:  ", round(capacity_factor(192_500, 60), 3))
    print("pure:  ", round(capacity_factor(192_500, 60), 3))
    impure_cf(192_500, 60)
    impure_cf(192_500, 60)
    print("impure: the log now holds", len(log), "entries")
    print("week:  ", round(capacity_factor(3_100, 60, hours=168), 3))
# [end: functions]


# [start: collections]
def collections_demo():
    speeds = [7.2, 8.9, 13.4, 2.1, 9.6]          # list: ordered, changeable
    limits = (3.0, 25.0)                          # tuple: fixed pair
    turbine = {"tag": "PLP-WTG-07", "rated_mw": 5.0, "hub_m": 100}   # dict
    tags = ["PLP-INV-01", "PLP-INV-07", "PLP-INV-07", "PLP-INV-09"]
    working = [v for v in speeds if limits[0] <= v <= limits[1]]
    print("working speeds:", working, " count:", len(working))
    print("sorted, fastest first:", sorted(speeds, reverse=True))
    print("hub height:", turbine["hub_m"], "m;  keys:", list(turbine))
    print("unique tags:", sorted(set(tags)), " duplicates:",
          len(tags) - len(set(tags)))
    cubes = {v: round(v ** 3) for v in speeds[:2]}
    print("v^3 by speed:", cubes)
# [end: collections]


# [start: strings]
def strings_demo():
    tag = "  plp-wtg-07-gen \n"
    clean = tag.strip().upper()
    plant, system, number, part = clean.split("-")
    print(repr(tag), "->", repr(clean))
    print(f"system {system}, number {int(number)}, component {part}")
    print("is a turbine part:", clean.startswith("PLP-WTG"))
    print(f"{'value':>8}|{3.14159:8.3f}|{1234567:>12,}|{0.0437:.1%}")
# [end: strings]


# [start: files]
def files_demo(folder):
    import csv
    import json
    from pathlib import Path
    path = Path(folder) / "speeds.csv"
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["hour", "ws_ms"])
        for h, v in enumerate([6.1, 7.4, 8.0]):
            w.writerow([h, v])
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    print("read back:", rows)
    mean = sum(float(r["ws_ms"]) for r in rows) / len(rows)
    out = {"file": path.name, "mean_ws_ms": round(mean, 3), "n": len(rows)}
    summary = Path(folder) / "summary.json"
    summary.write_text(json.dumps(out), encoding="utf-8")
    print("summary.json:", summary.read_text(encoding="utf-8"))
# [end: files]


# [start: exceptions]
class DataError(ValueError):
    """A problem with input data (not with the program)."""


def parse_speed(text):
    try:
        v = float(text)
    except ValueError:
        raise DataError(f"not a number: {text!r}") from None
    if not 0 <= v <= 75:
        raise DataError(f"wind speed {v} m/s outside 0..75")
    return v


def exceptions_demo():
    for text in ("8.4", "8,4", "-3", "120", ""):
        try:
            print(f"{text!r:7} -> {parse_speed(text)}")
        except DataError as e:
            print(f"{text!r:7} -> rejected: {e}")
# [end: exceptions]


# [start: modules]
def modules_demo():
    import math
    import statistics
    from plantp import screening
    print("pi =", round(math.pi, 6), "  sqrt(2) =", round(math.sqrt(2), 6))
    data = [6.1, 7.4, 8.0, 9.9, 5.2]
    print("mean", statistics.mean(data), " median", statistics.median(data),
          " stdev", round(statistics.stdev(data), 3))
    p = float(screening.pv_ac_power_mw(800, 60, 50))
    print("PV at 800 W/m2:", round(p, 3), "MW")
    print("this module is called", __name__.rsplit(".", 1)[-1])
# [end: modules]


# [start: algorithm]
def longest_gap(stamps_h):
    """Longest run of missing hours in a sorted list of hour numbers."""
    best, best_start = 0, None
    for a, b in zip(stamps_h, stamps_h[1:]):
        missing = b - a - 1
        if missing > best:
            best, best_start = missing, a + 1
    return best, best_start


def duplicates_slow(items):
    count, found = 0, []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            count += 1
            if items[i] == items[j]:
                found.append(items[i])
    return found, count


def duplicates_fast(items):
    seen, found = set(), []
    for x in items:
        if x in seen:
            found.append(x)
        seen.add(x)
    return found, len(items)


def algorithm_demo():
    print("longest gap:", longest_gap([0, 1, 2, 5, 6, 7, 8, 14, 15]))
    tags = [f"T{k}" for k in range(2000)] + ["T7"]
    print("pairwise: found", duplicates_slow(tags)[0], "after",
          f"{duplicates_slow(tags)[1]:,} comparisons")
    print("with a set: found", duplicates_fast(tags)[0], "after",
          f"{duplicates_fast(tags)[1]:,} look-ups")
# [end: algorithm]


DEMOS = {"first": first_program, "types": types_demo,
         "conditions": conditions_demo,
         "loops": loops_demo, "functions": functions_demo,
         "collections": collections_demo, "strings": strings_demo,
         "exceptions": exceptions_demo, "modules": modules_demo,
         "algorithm": algorithm_demo}


def capture(func, *args) -> list[str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        func(*args)
    return buf.getvalue().rstrip("\n").splitlines()


def main() -> None:
    import tempfile
    for name, func in DEMOS.items():          # one output file per demo
        emit(f"b_{name}", capture(func))
    with tempfile.TemporaryDirectory() as tmp:
        emit("b_files", capture(files_demo, tmp))


if __name__ == "__main__":
    sys.exit(main())
