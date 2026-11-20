"""Chapter 31, lesson K: the customs interface and construction spares -
the documents a shipment needs, how clearance time adds to port storage,
and how many spares of a consumable to hold on site through a lead time.

Run from the project root:   python -m companion.ch31.examples_k
Writes companion/ch31/expected/k_*.txt and diagrams/data/ch31-customs.csv.
Teaching values (A-366); customs rules are country-specific and handled
by the freight forwarder and the customs broker (ch 55-57); no rule of
any country is assumed here.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch31 import sources as src  # noqa: F401  (puts plantp on the path)
from companion.ch31.common import csv, emit


def documents() -> None:
    docs = [("commercial invoice", "seller", "value and terms of sale"),
            ("packing list", "seller", "pieces, masses, dimensions"),
            ("bill of lading", "carrier", "title to the goods at sea"),
            ("certificate of origin", "chamber / seller", "where it was made"),
            ("import licence or permit", "importer", "if the item needs one"),
            ("insurance certificate", "insurer", "cover in transit"),
            ("maker's certificates", "maker", "type tests, dangerous goods")]
    lines = ["documents a turbine shipment travels with (typical, not a rule)",
             "  document                   issued by          what it shows"]
    for d, who, what in docs:
        lines.append(f"  {d:26s} {who:18s} {what}")
    lines += ["  one missing or inconsistent document holds the whole",
              "  shipment at the port: the forwarder checks the set before",
              "  the ship sails, and a battery's dangerous-goods papers",
              "  (ch 19) travel with it - the country's rules decide the",
              "  rest (ch 55-57)"]
    emit("k_documents", lines)


def clearance(n: int = 20_000, seed: int = 31) -> None:
    rng = np.random.default_rng(seed)
    days = rng.lognormal(math.log(5), 0.5, n)
    days += np.where(rng.random(n) < 0.08, rng.uniform(5, 20, n), 0.0)   # queries, inspections
    hist, edges = np.histogram(days, bins=30, range=(0, 30))
    csv("ch31-customs.csv", "day,count", [(round(e, 1), int(h)) for e, h in zip(edges[:-1], hist)])
    p50, p90 = np.percentile(days, [50, 90])
    free = 21.0
    lines = ["customs clearance time at the port (Monte Carlo, teaching)",
             "  median 5 days; 8 % of shipments queried (+5-20 days)",
             f"  P50 {p50:.1f} days, P90 {p90:.1f} days",
             f"  clearance alone longer than the 21 free days: {np.mean(days > free) * 100:.1f} %",
             f"  clearance plus a 2-week convoy queue over 21 days: {np.mean(days + 14 > free) * 100:.0f} %",
             "  clearance eats into the free storage before the first",
             "  convoy moves: documents prepared before arrival, a broker",
             "  appointed and the convoy queue planned from the P90, not",
             "  the median, keep the port bill small (lesson A)"]
    emit("k_clearance", lines)


def spares() -> None:
    lines = ["spares on site for a consumable through its lead time (Poisson)",
             "  item                       use a month   lead weeks   stock for 95 %"]
    for name, rate, lead in [("crane wire rope (sets)", 0.1, 10), ("hydraulic hoses", 2.0, 3),
                             ("torque tool pumps", 0.3, 6), ("mats (damaged)", 1.5, 4)]:
        mean = rate * lead / 4.33
        k, cum = 0, math.exp(-mean)
        while cum < 0.95:
            k += 1
            cum += math.exp(-mean) * mean ** k / math.factorial(k)
        lines.append(f"  {name:26s} {rate:11.1f}   {lead:10d}   {k:14d}")
    lines += ["  a rarely used item with a long lead time still needs one",
              "  on site: one broken torque pump can stop the bolting of",
              "  a tower for six weeks - spares are priced against the",
              "  crane days they protect"]
    emit("k_spares", lines)


if __name__ == "__main__":
    documents()
    clearance()
    spares()
