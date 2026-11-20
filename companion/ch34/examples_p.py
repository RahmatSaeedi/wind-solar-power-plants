"""Chapter 34, lesson P (design, more): terminals and rail space in the
marshalling cabinets, a 24 V branch fault against a current-limited
supply, how many tests a logic needs, and the punch list left at the
end of the factory test.

Run from the project root:   python -m companion.ch34.examples_p
Writes companion/ch34/expected/p_*.txt.
Teaching values (A-388).
"""
from __future__ import annotations

import math

from companion.ch34.common import emit
from companion.ch34 import examples_c as c34


def marshalling() -> None:
    ai, di, do = c34.io_totals()
    terms = math.ceil((ai * 3 + di * 2 + do * 2) * 1.2)
    width_mm, rail_m, rails = 6.2, 0.6, 10          # per terminal, per rail, per cabinet
    per_rail = int(rail_m * 1000 / width_mm)
    rails_needed = math.ceil(terms / per_rail)
    lines = ["terminals in the marshalling cabinets (teaching sizes)",
             f"  {ai} AI x 3 + {di} DI x 2 + {do} DO x 2, +20 % spare: {terms} terminals",
             f"  {width_mm} mm each on {rail_m} m rails: {per_rail} a rail -> {rails_needed} rails",
             f"  at {rails} rails a cabinet: {math.ceil(rails_needed / rails)} cabinet(s),"
             " before the room left for growth",
             "  space is also for people: room for a hand and a tool",
             "  between rails, labels on both ends of every wire, and",
             "  the field side kept apart from the system side so a",
             "  loop check never needs a terminal opened in a crowd"]
    emit("p_marshal", lines)


def branch_fault() -> None:
    psu_a, limit = 20.0, 1.5                         # 24 V supply rating, current limit x rating
    lines = ["a short circuit on a 24 V branch: does the branch protection clear it?",
             f"  supply {psu_a:.0f} A, current-limited at {limit} x = {psu_a * limit:.0f} A",
             "  branch device              rating A   needs A to clear fast   clears?"]
    for name, rating, mult in (("fuse", 4.0, 5.0), ("fuse", 10.0, 5.0),
                               ("electronic breaker", 4.0, 1.1)):
        need = rating * mult
        ok = "yes" if psu_a * limit >= need else "NO"
        lines.append(f"  {name:26s} {rating:8.0f}   {need:21.0f}   {ok}")
    lines += ["  a current-limited supply may never give a large fuse the",
              "  current it needs: the fault drags the 24 V down for every",
              "  module on the supply until something else gives way;",
              "  small fuses or electronic breakers per branch, sized",
              "  against the supply's limit, keep a fault on its branch"]
    emit("p_branch", lines)


def logic_tests() -> None:
    lines = ["how many test cases a permissive with n conditions needs (teaching)",
             "  conditions   every combination   each condition shown to matter"]
    for n in (3, 5, 6, 10):
        lines.append(f"  {n:10d}   {2 ** n:17d}   {n + 1:30d}")
    lines += ["  testing every combination grows out of reach; a set of",
              "  n + 1 cases in which each condition is shown to change the",
              "  result on its own covers an AND of n conditions - plus the",
              "  bad-quality case of each input (lesson B)"]
    emit("p_logic", lines)


def punch_list() -> None:
    items = {"A (blocks shipment)": 2, "B (close before SAT)": 6, "C (close before handover)": 4}
    rate = 3.0                                     # items closed a week
    lines = ["the punch list at the end of the factory test (synthetic)",
             "  category                      open"]
    for k, v in items.items():
        lines.append(f"  {k:29s} {v:4d}")
    ab = items["A (blocks shipment)"] + items["B (close before SAT)"]
    lines += [f"  A and B items: {ab}; at {rate:.0f} closed a week: {ab / rate:.1f} weeks",
              "  the panel ships when the A items are closed and re-tested;",
              "  B items travel with the panel and are closed and signed",
              "  before the site test; each item names who closes it and",
              "  which test proves it closed (ch 40, ch 50)"]
    emit("p_punch", lines)


if __name__ == "__main__":
    marshalling()
    branch_fault()
    logic_tests()
    punch_list()
