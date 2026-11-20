"""Chapter 52, lesson H: collector and export assets - inspections by
owner against their intervals, spares held for the export path, an
inspection outage by night or by day, the logistics of a line repair, the
boundary of who maintains what, and termination findings over time.

Run from the project root:   python -m companion.ch52.examples_h
Writes companion/ch52/expected/h_*.txt. Teaching values (A-536).
"""
from __future__ import annotations

import numpy as np

from companion.ch15 import sources as s15
from companion.ch52 import sources as src
from companion.ch52.common import emit


# ------------------------------------------------ 1. inspections by owner
def inspections(today: int = 365) -> dict:
    due = {k: (o, m, last, today - last > m * 30.4)
           for k, (o, m, last, _) in src.EXPORT_ASSETS.items()}
    late = [(k, o) for k, (o, m, last, d) in due.items() if d]
    lines = [f"export-path inspections on day {today}: interval and last done"]
    lines += [f"  {k:33s} {o:13s} {m:2d} mo  day {last:3d}" + ("  OVERDUE" if d else "")
              for k, (o, m, last, d) in due.items()]
    mine = [k for k, o in late if o == "plant"]
    lines += [f"  overdue: {len(late)}, of which the plant's own: {len(mine)}",
              "  the plant chases the network owner's overdue insulator",
              "  inspection through the interface agreement (ch 23) and fixes",
              "  its own road; the relays at the plant end were last tested",
              "  at commissioning (day 0) - due in the fourth year, not late"]
    emit("h_inspect", lines)
    return dict(late=len(late), mine=len(mine))


# ------------------------------------------------ 2. spares for the export path
def spares() -> dict:
    short = {k: n - h for k, (n, h) in src.SPARES_EXPORT.items() if h < n}
    lines = ["spares for the export path: needed by the repair plan and held"]
    lines += [f"  {k:26s} needed {n:3d}  held {h:3d}" + (f"  short {n - h}" if h < n else "")
              for k, (n, h) in src.SPARES_EXPORT.items()]
    lines += [f"  {len(short)} lines short; the CT has none - a failed CT holds the",
              "  bay out for its lead time (ch 39: months), with the line",
              "  differential (ch 28) needing a matched replacement"]
    emit("h_spares", lines)
    return short


# ------------------------------------------------ 3. inspection outage by night or day
def outage_timing(hours: int = 8) -> dict:
    poc = s15.plant_year()["poc"]
    hr = np.arange(poc.size) % 24
    day = float(np.mean([poc[d * 24 + 8:d * 24 + 8 + hours].sum() for d in range(365)]))
    night = float(np.mean([poc[d * 24 + 22:d * 24 + 22 + hours].sum() for d in range(364)]))
    lines = [f"an {hours}-hour line outage for insulator inspection: energy not exported",
             f"  08-16 on an average day: {day:,.0f} MWh; 22-06: {night:,.0f} MWh",
             f"  the night saves {day - night:,.0f} MWh an outage, but the network",
             "  owner's crews work days and a night outage needs lighting,",
             "  a night permit and access (ch 32): the window is agreed,",
             "  not chosen by the plant alone"]
    emit("h_timing", lines)
    return dict(day=day, night=night)


# ------------------------------------------------ 4. line repair logistics
def line_repair(seed: int = 536, n: int = 2_000) -> dict:
    rng = np.random.default_rng(seed)
    mob = rng.lognormal(np.log(2.0), 0.4, n)          # mobilise crew, h
    find = rng.lognormal(np.log(1.5), 0.6, n)         # patrol to find the fault
    fix = rng.lognormal(np.log(3.0), 0.5, n)
    wait_part = np.where(rng.random(n) < 0.3, rng.lognormal(np.log(48), 0.5, n), 0.0)
    tot = mob + find + fix + wait_part
    no_wait = mob + find + fix
    lines = ["permanent line fault: time to restore (Monte Carlo of the stages, h)",
             f"  mobilise {np.median(mob):.1f}, find {np.median(find):.1f}, repair "
             f"{np.median(fix):.1f} (medians); 30 % of faults need a part",
             f"  restore: median {np.median(tot):.1f} h, P90 {np.percentile(tot, 90):.1f} h, "
             f"mean {tot.mean():.1f} h",
             f"  with the part always on site: mean {no_wait.mean():.1f} h, P90 "
             f"{np.percentile(no_wait, 90):.1f} h",
             "  the part, not the crew, makes the tail: insulators held on",
             "  site (lesson H spares) cut the worst outages"]
    emit("h_repair", lines)
    return dict(mean=float(tot.mean()), p90=float(np.percentile(tot, 90)),
                mean_np=float(no_wait.mean()))


# ------------------------------------------------ 5. who maintains what
def boundary() -> dict:
    by = {}
    for k, (o, *_) in src.EXPORT_ASSETS.items():
        by.setdefault(o, []).append(k)
    lines = ["the export-path boundary: who maintains what"]
    for o, ks in by.items():
        lines.append(f"  {o} ({len(ks)}):")
        lines += [f"    - {k}" for k in ks]
    lines += ["  'shared' needs both: the teleprotection has an end in each",
              "  substation and one test plan; the boundary drawing (ch 23)",
              "  and the service agreement name the response time for each"]
    emit("h_boundary", lines)
    return {o: len(ks) for o, ks in by.items()}


# ------------------------------------------------ 6. termination findings
def terminations() -> dict:
    years = [1, 2, 3]
    found = [7, 3, 2]                                  # hot terminations found a year
    reterm = [1, 0, 1]                                 # re-made after a finding
    lines = ["33 kV terminations: thermography findings by year (120 inspected)",
             "  year   found   re-made"]
    lines += [f"  {y:4d} {f:7d} {r:9d}" for y, f, r in zip(years, found, reterm)]
    lines += ["  findings fall after the first year (loose bolts from",
              "  installation, ch 49 torque) - a falling count is the sign",
              "  the inspection interval can be stretched, with the record",
              "  as its justification (lesson A)"]
    emit("h_term", lines)
    return dict(found=found)


if __name__ == "__main__":
    inspections()
    spares()
    outage_timing()
    line_repair()
    boundary()
    terminations()
