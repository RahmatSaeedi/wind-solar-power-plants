"""Chapter 2 — short demonstrations of plantp.units and plantp.records quoted in the text.

Run from the project root:   python -m companion.ch02.demo_units
Writes companion/ch02/expected/demo_units.txt.
"""
from __future__ import annotations

import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

OUT = Path(__file__).resolve().parent / "expected" / "demo_units.txt"


def demo() -> None:
    # [start: units]
    from plantp.units import Q, DimensionError, check

    p = Q(60, "MW")                       # a power
    e = p * Q(8760, "h")                  # power x time = energy
    print(e.to("GWh"))                    # 525.6 GWh
    print(Q(7.10, "m/s").to("km/h"))      # 25.56 km/h
    print(Q(2950, "ft lbf").to("N m"))    # bolt torque, imperial drawing
    try:
        Q(60, "MW") + Q(192.5, "GWh")     # power + energy: not allowed
    except DimensionError as err:
        print("refused:", err)
    check(Q(5, "kWh"), "J")               # passes silently: kWh is an energy
    # [end: units]

    # [start: records]
    from plantp import records as rec

    print(rec.doc_number("ELE", "CAL", 12))      # PLP-ELE-CAL-0012
    print(rec.next_revision("B"))                # C
    print(rec.next_revision("B", approve=True))  # 0
    print(rec.digest({"P_dc_MWp": 60, "H_kWh_m2": 1947.2})[:16])
    print(rec.digest({"P_dc_MWp": 60, "H_kWh_m2": 1947.3})[:16])
    # [end: records]


def main() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        demo()
    text = buffer.getvalue()
    lines = []
    for line in text.splitlines():
        while len(line) > 78:
            lines.append(line[:78])
            line = "    " + line[78:]
        lines.append(line)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))
    np.seterr(all="warn")


if __name__ == "__main__":
    main()
