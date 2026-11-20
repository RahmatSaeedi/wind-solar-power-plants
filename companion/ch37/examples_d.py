"""Chapter 37, lesson D (event taxonomy): the categories an hour can fall
in, the boundaries of a failure and its downtime, two categories at once,
and planned work that overruns.

Run from the project root:   python -m companion.ch37.examples_d
Writes companion/ch37/expected/d_*.txt.
Teaching values (A-411); the contract's definitions decide.
"""
from __future__ import annotations

from companion.ch37.common import emit
from plantp import performance as pf


def taxonomy() -> None:
    rows = [("operating", "producing", "-"),
            ("available, idle", "no wind, no sun", "nobody"),
            ("forced outage", "fault, trip, repair", "plant"),
            ("planned outage", "service in its window", "plant, often excluded"),
            ("external", "grid, operator's limit, ice", "outside the plant"),
            ("unknown", "data missing", "nobody until resolved")]
    lines = ["the categories an hour can fall in (teaching taxonomy)",
             "  category          examples                      charged to"]
    for a, b, c in rows:
        lines.append(f"  {a:17s} {b:29s} {c}")
    lines += ["  every hour of every unit falls in exactly one category,",
              "  chosen by written entry and exit rules; the contract",
              "  decides which categories count against availability",
              "  (STD-165 describes such an information model)"]
    emit("d_taxonomy", lines)


def boundaries() -> None:
    trip, arrive, fixed, restart = 10.0, 14.0, 16.0, 16 + 20 / 60
    lines = ["one turbine trip and its times (teaching, hours of the day)",
             f"  trip {trip:.2f}, technician on site {arrive:.2f}, repaired {fixed:.2f},"
             f" back in service {restart:.2f}",
             f"  downtime (trip to service): {restart - trip:.2f} h",
             f"  repair time (hands on the fault): {fixed - arrive:.2f} h",
             f"  waiting (trip to arrival): {arrive - trip:.2f} h",
             f"  restart checks: {restart - fixed:.2f} h",
             "  'mean time to repair' can mean 2 h or 6.3 h: a report",
             "  names its boundaries, and the waiting - often the largest",
             "  part - is a separate number, because it has a separate",
             "  cure (spares, access, staff on site)"]
    emit("d_boundaries", lines)


def concurrent() -> None:
    fault_h, grid_inside = 10.0, 3.0
    period = 744.0
    up_a = period - fault_h                          # all ten hours charged to the fault
    up_b = period - fault_h                          # grid hours leave the period
    lines = ["a 10 h turbine fault with a 3 h grid outage inside it (March)",
             f"  fault charged for all 10 h: availability"
             f" {pf.time_availability(up_a, period) * 100:.3f} %",
             f"  grid outage takes its 3 h first, as external:"
             f" {pf.time_availability(up_b, period - grid_inside) * 100:.3f} %",
             "  two categories at once need a priority rule, written",
             "  before the dispute: the same log gives two answers"]
    emit("d_concurrent", lines)


def overrun() -> None:
    planned, actual = 24.0, 30.0
    lines = ["a scheduled gearbox oil change that overruns (teaching)",
             f"  planned window {planned:.0f} h, work took {actual:.0f} h",
             f"  planned outage: {planned:.0f} h (excluded if the contract excludes it)",
             f"  overrun: {actual - planned:.0f} h, charged as forced outage",
             "  the plan is recorded before the work starts; whatever",
             "  runs past it is a forced outage, or 'planned' would",
             "  swallow every delay"]
    emit("d_overrun", lines)


if __name__ == "__main__":
    taxonomy()
    boundaries()
    concurrent()
    overrun()
