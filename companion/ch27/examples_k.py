"""Chapter 27 - filter and meter products and their evidence: a failed
capacitor unit detunes the filter, reactor tolerance and damping, the
uncertainty of a harmonic measurement near a limit, and the factory and
site records that link to chapters 46 and 48.

Run from the project root:   python -m companion.ch27.examples_k
Writes companion/ch27/expected/k_*.txt. Teaching values A-340.
"""
from __future__ import annotations

import math

from companion.ch27 import sources as src
from companion.ch27.common import emit
from plantp import pq


def element_failure() -> None:
    f = src.FILTER
    n_units = 12
    lines = [f"filter capacitor bank: {n_units} units in parallel per phase (teaching)",
             "  failed units   capacitance %   tuned to h   distance to the 5th"]
    for k in (0, 1, 2, 3):
        c = (n_units - k) / n_units
        h = f["h_tune"] / math.sqrt(c)
        lines.append(f"  {k:12d}   {100 * c:13.1f}   {h:10.2f}   {5 - h:+19.2f}")
    lines += ["  each failed unit raises the tuning toward the 5th, where the",
              "  filter would sink the whole network's 5th harmonic and",
              "  overload; the bank's unbalance protection (a current between",
              "  two star halves) sees the first failed unit and alarms, the",
              "  second trips - the settings come from the maker's design"]
    emit("k_elements", lines)


def reactor() -> None:
    f = src.FILTER
    lines = ["the reactor: inductance tolerance and quality factor (teaching)",
             "  L tolerance   tuned to h"]
    _, _, xc, xl = pq.tuned_filter(f["q_mvar"], f["h_tune"], 33.0)
    for tol in (-0.03, 0.0, 0.03):
        lines.append(f"  {tol:+11.0%}   {f['h_tune'] / math.sqrt(1 + tol):10.2f}")
    lines.append("  quality factor   filter impedance at its tuning ohm")
    for qual in (20, 40, 80):
        lines.append(f"  {qual:14d}   {xl * f['h_tune'] / qual:34.2f}")
    lines += ["  a lower quality factor damps the resonance below the tuning",
              "  but costs losses at 50 Hz and at the 5th; taps on the reactor",
              "  allow the tuning to be set on site after the capacitors are",
              "  measured - the factory records give both values"]
    emit("k_reactor", lines)


def uncertainty() -> None:
    measured, limit = 1.83, 2.0
    parts = {"instrument (class A, teaching)": 5.0, "inductive VT at the 5th": 3.0,
             "window and grouping": 1.0}
    rel = math.sqrt(sum(v * v for v in parts.values()))
    lines = ["uncertainty of a 5th-harmonic voltage reading near a limit (teaching)",
             "  component                          % of the reading"]
    for k, v in parts.items():
        lines.append(f"  {k:34s} {v:16.1f}")
    lines += [f"  combined (root sum of squares)     {rel:16.1f}",
              f"  95th percentile {measured:.2f} % +/- {measured * rel / 100:.2f}: range"
              f" {measured * (1 - rel / 100):.2f} to {measured * (1 + rel / 100):.2f} % against a teaching",
              f"  limit of {limit:.1f} %",
              "  the range reaches the limit: 'compliant' and 'not compliant'",
              "  both fit the data; the agreed method says how uncertainty",
              "  is treated (guard band or not) before the reading is taken"]
    emit("k_uncertainty", lines)


def records() -> None:
    rows = [("filter capacitors", "capacitance, losses, insulation", "routine tests"),
            ("filter reactor", "inductance, Q, temperature rise", "routine/type tests"),
            ("filter assembly", "tuning measured on site", "commissioning"),
            ("PQ instrument", "class A certificate, calibration", "certificate"),
            ("plant controller", "FAT of the control functions", "FAT (ch 46)"),
            ("service tests", "steps, droop, P-Q points", "site tests (ch 48)")]
    lines = ["product limits and the evidence chain (factory to site):",
             "  item                 checked                           record"]
    for a, b, c in rows:
        lines.append(f"  {a:20s} {b:33s} {c}")
    lines += ["  the factory proves the product, the site proves the plant;",
              "  both records sit in the dossier next to the investigation",
              "  and the monitoring plan"]
    emit("k_records", lines)


if __name__ == "__main__":
    element_failure()
    reactor()
    uncertainty()
    records()
