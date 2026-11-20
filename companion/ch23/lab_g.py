"""Chapter 23, lab G - the plant-to-grid boundary: one turbine traced
through its string, the 33 kV bus, the main transformer, the line bay,
the line and the utility's bay; fault levels by the MVA method; the
responsibility matrix of the boundary assets; the two meter locations
and the line losses between them; the unresolved interfaces.

Run from the project root:   python -m companion.ch23.lab_g
Writes companion/ch23/expected/g_*.txt and diagrams/data/ch23-*.csv.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch15 import sources as s15
from companion.ch17 import sources as s17
from companion.ch23 import sources as src
from companion.ch23.common import csv, emit


def trace() -> None:
    g = src.plant()
    lines = ["turbine WS3-4 traced to the grid (interfaces on the way):"]
    lines += [f"  {n}" for n in g.crossings("WS3-4-LV", "GRID")]
    lines += ["  the turbine is the plant's; inside it, the maker's scope ends",
              "  at the transformer's 33 kV terminals (an interface of",
              "  supply, not of ownership)"]
    emit("g_trace", lines)


# [start: mva]
def series(*mva: float) -> float:
    """Short-circuit MVA of elements in series (MVA method)."""
    return 1.0 / sum(1.0 / m for m in mva)


def mva_method() -> dict:
    n = s17.NETWORK
    s_grid = n["s_sc_mva"]                                  # at the POC
    z_line = n["line_km"] * math.hypot(n["r_ohm_km"], n["x_ohm_km"])
    s_line = 132.0 ** 2 / z_line
    s_tr = 63.0 / 0.12                                      # each transformer
    hv = series(s_grid, s_line)
    mv_one = series(hv, s_tr)                               # bus coupler open
    mv_two = series(hv, 2 * s_tr)                           # coupler closed
    lv = series(mv_one, 0.25 / 0.045)
    return {"POC": s_grid, "plant 132 kV": hv, "33 kV (one T)": mv_one,
            "33 kV (both T)": mv_two, "0.4 kV board": lv, "s_line": s_line,
            "s_tr": s_tr}
# [end: mva]


def faults() -> None:
    r = mva_method()
    kv = {"POC": 132, "plant 132 kV": 132, "33 kV (one T)": 33, "33 kV (both T)": 33,
          "0.4 kV board": 0.4}
    rating = {"POC": "-", "plant 132 kV": "31.5", "33 kV (one T)": "25",
              "33 kV (both T)": "25", "0.4 kV board": "-"}
    lines = ["fault levels by the MVA method (grid side only; teaching):",
             f"  line {r['s_line']:,.0f} MVA, each transformer {r['s_tr']:,.0f} MVA",
             "  bus                MVA       kA   switchgear kA"]
    rows = []
    for k in kv:
        ka = r[k] / (math.sqrt(3) * kv[k])
        lines.append(f"  {k:16s} {r[k]:7,.0f}  {ka:7.1f}   {rating[k]:>10s}")
        rows.append((k.split()[0], f"{ka:.1f}"))
    inv = 1.2 * 130 / (math.sqrt(3) * 33)
    both = r["33 kV (both T)"] / (math.sqrt(3) * 33) + inv
    lines += [f"  inverters and converters add about 1.2 x rated current:"
              f" {inv:.1f} kA at 33 kV",
              "  with the coupler closed and every source feeding, the 33 kV",
              f"  duty is about {both:.1f} kA - inside a 25 kA rating; the full",
              "  study with the network's X/R and the makers' data is ch 26"]
    emit("g_faults", lines)
    csv("ch23-faults.csv", "bus,ka", rows)


def responsibility() -> None:
    assets = [("plant line bay (E1)", "plant", "plant", "plant", "plant", "plant"),
              ("revenue meter", "utility*", "plant", "plant", "utility", "utility"),
              ("132 kV line", "open", "open", "open", "open", "open"),
              ("utility line bay (G1)", "utility", "utility", "utility", "utility", "utility"),
              ("line protection, both ends", "both", "both", "both", "both", "both"),
              ("telecom to utility SCADA", "utility", "plant", "plant", "utility", "plant"),
              ("intertrip and PPC signals", "both", "plant", "plant", "both", "plant")]
    lines = ["responsibility matrix of the boundary assets (teaching):",
             "  asset                        design   supply   install  test     own/operate"]
    for a, d, s, i, t, o in assets:
        lines.append(f"  {a:28s} {d:8s} {s[:8]:8s} {i:8s} {t:8s} {o}")
    lines += ["  (* the utility specifies the meter; who supplies it is",
              "  in the connection agreement); 'open' cells wait for the",
              "  grid offer (U-065); 'both' cells need a protocol: one",
              "  owner, one witness"]
    emit("g_responsibility", lines)


def meter_losses() -> None:
    d = s15.plant_year()["delivered"]
    n = s17.NETWORK
    r = n["line_km"] * n["r_ohm_km"]
    loss = d ** 2 * r / 132.0 ** 2                          # MW, pf 1
    e = d.sum()
    lines = ["line losses between meter option A (plant bay) and B (grid bay):",
             f"  line resistance {r:.3f} ohm; at 100 MW: {100 ** 2 * r / 132 ** 2:.3f} MW",
             f"  over the year: {loss.sum():,.0f} MWh of {e:,.0f} MWh delivered"
             f" ({loss.sum() / e:.2%})",
             "  with option A the buyer pays for energy that is lost on the",
             "  line; with option B the plant bears the loss - the meter's",
             "  place is a commercial term with a number (ch 17, 21)"]
    emit("g_meter", lines)


def unresolved() -> None:
    items = ["U-065 owner of the 132 kV line and the point of connection",
             "U-089 utility data: fault level, X/R, protection settings at G1",
             "U-067 grid-code curves: reactive power, ride-through",
             "U-068 connection cost and who builds the line",
             "meter class, CT/VT ratios and the meter's place (A or B)",
             "telecom path and protocol to the utility's control centre",
             "intertrip scheme and its test with the utility",
             "switching and earthing procedures across the boundary"]
    lines = ["unresolved utility and third-party interfaces:"]
    lines += [f"  {k + 1}. {x}" for k, x in enumerate(items)]
    lines += ["  each goes to the connection agreement or the operating",
              "  agreement with the utility; the one-line shows them as",
              "  open, never as assumed"]
    emit("g_unresolved", lines)


if __name__ == "__main__":
    trace()
    faults()
    responsibility()
    meter_losses()
    unresolved()
