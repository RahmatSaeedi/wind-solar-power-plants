"""Chapter 47, round w: flange bolt lots, what plate-to-can marks are worth
in a recall, tracker bearing gaps by installation temperature, sampling
the PV fasteners, specific and non-specific certificates, and damage
found when the sections arrive.

Run from the project root:   python -m companion.ch47.examples_w
Writes companion/ch47/expected/w_*.txt.
Teaching values (A-490 to A-497); no design approval implied.
"""
from __future__ import annotations

import math

from companion.ch30 import sources as s30
from companion.ch47 import sources as src
from companion.ch47.common import emit

# ------------------------------------------------ 1. flange bolt lots
BOLT_LOTS = {   # flange: list of (lot, count)
    "T05-F1": [("BL-71", 120)], "T05-F2": [("BL-71", 96), ("BL-72", 24)],
    "T05-F3": [("BL-73", 88)], "T05-F4": [("BL-73", 60), ("BL-69", 12)],
}
LOT_INFO = {"BL-69": ("10.9", "zinc flake", "older lubricant"),
            "BL-71": ("10.9", "zinc flake", "lubricant A"),
            "BL-72": ("10.9", "zinc flake", "lubricant A"),
            "BL-73": ("10.9", "zinc flake", "lubricant A")}


def bolt_lots() -> dict:
    lines = ["flange bolts of T05 by lot (teaching)", "  flange    lots"]
    mixed, odd = [], []
    for f, lots in BOLT_LOTS.items():
        lines.append(f"  {f}    " + ", ".join(f"{l} x{n}" for l, n in lots))
        if len(lots) > 1:
            mixed.append(f)
        for l, _ in lots:
            if LOT_INFO[l][2] != "lubricant A":
                odd.append((f, l))
    lines += [f"  flanges with mixed lots: {', '.join(mixed)}",
              f"  lot with a different lubricant: "
              + ", ".join(f"{l} in {f}" for f, l in odd),
              "  the tension a torque gives depends on the lubricant: bolts of",
              "  one flange are tensioned as one set, so a flange takes bolts",
              "  of one lot (or lots with the same certified lubricant), and",
              "  the lot of every flange is in the erection record (ch 30)"]
    emit("w_bolts", lines)
    return dict(mixed=mixed, odd=odd)


# ------------------------------------------------ 2. what the marks are worth
def marks_value(cans_per_tower: int = 40, scan_h: float = 3.0,
                rate_ku_h: float = 0.12, mark_min: float = 6.0) -> dict:
    no_marks = cans_per_tower * src.TURBINES
    with_marks = 1 + 8                     # round s: the can, its siblings
    cost_no = no_marks * scan_h * rate_ku_h
    cost_with = with_marks * scan_h * rate_ku_h
    mark_cost = cans_per_tower * src.TURBINES * mark_min / 60 * rate_ku_h
    lines = ["what plate-to-can marks are worth in one heat recall (teaching)",
             f"  without marks every can of the farm is scanned: {no_marks} cans, "
             f"{cost_no:.0f} k u",
             f"  with marks and the heat register: {with_marks} cans, "
             f"{cost_with:.1f} k u",
             f"  marking all {no_marks} cans at {mark_min:.0f} minutes each: "
             f"{mark_cost:.1f} k u",
             "  one recall pays for the marks many times over, before the",
             "  crane days of scanning erected towers are even counted -",
             "  traceability is bought in the factory and used on site"]
    emit("w_marks", lines)
    return dict(no=cost_no, with_=cost_with, mark=mark_cost)


# ------------------------------------------------ 3. bearing gaps
def bearing_gaps(span_m: float = 30.0, t_max: float = 70.0,
                 t_min: float = -10.0) -> dict:
    a = s30.STEEL["alpha"]
    lines = [f"tracker bearing gap set at installation, end bearing {span_m:.0f} m "
             f"from the fixed point",
             f"  (tube from {t_min:.0f} to {t_max:.0f} C; steel alpha {a})",
             "  install C   room to grow mm   room to shrink mm"]
    out = {}
    for t in (5.0, 20.0, 35.0, 50.0):
        grow = a * span_m * 1000 * (t_max - t)
        shrink = a * span_m * 1000 * (t - t_min)
        out[t] = (grow, shrink)
        lines.append(f"  {t:9.0f}   {grow:15.1f}   {shrink:17.1f}")
    lines += ["  the same bearing set at noon and at dawn needs different",
              "  room on each side: the installer reads the tube temperature",
              "  and sets the gap from this table - and writes both down, so",
              "  the record explains any bearing found tight later (round s)"]
    emit("w_bearings", lines)
    return out


# ------------------------------------------------ 4. sampling the fasteners
def fasteners(per_table: int = 140, p_bad: float = 0.01, conf: float = 0.95) -> dict:
    n_all = per_table * 2100
    n = math.ceil(math.log(1 - conf) / math.log(1 - p_bad))
    lines = [f"PV fasteners: about {per_table} a table, {n_all:,} in the field",
             f"  to see at least one loose fastener with {conf:.0%} confidence when "
             f"{p_bad:.0%} are loose:",
             f"  n = ln(1 - {conf}) / ln(1 - {p_bad}) = {n} fasteners checked,",
             "  none loose to accept",
             "  the sample does not depend on the field's size; it is spread",
             "  over crews, days and table types, because a loose fastener",
             "  comes from one crew's tool or one day's rush (ch 40 sampling)"]
    emit("w_fasteners", lines)
    return dict(n=n, all=n_all)


# ------------------------------------------------ 5. certificate types
CERT_KIND = {"P101": "specific", "P102": "specific", "P103": "specific",
             "P104": "specific", "P105": "specific", "P106": "non-specific",
             "P107": "specific", "P108": "non-specific"}


def cert_types() -> dict:
    ns = [p for p, k in CERT_KIND.items() if k != "specific"]
    lines = ["kind of certificate behind each plate",
             "  specific: tests on the plates delivered; non-specific: the mill's",
             "  general production record, not these plates",
             f"  non-specific: {', '.join(ns)}",
             "  a tower wall is a fracture-critical member: the order asks for",
             "  certificates from tests on the delivered plates, issued by",
             "  someone independent of production (EN 10204 names the kinds);",
             "  P106 is also the wrong grade, read straight off its",
             "  certificate; P108 is right in every value, but the values are",
             "  not from these plates - the kind of certificate is a check of",
             "  its own"]
    emit("w_certkind", lines)
    return dict(ns=ns)


# ------------------------------------------------ 6. damage on arrival
DAMAGE = {   # section: (coating damage m2, dents, outer area m2)
    "T05-1": (0.8, 0, 340), "T05-2": (2.6, 1, 310), "T05-3": (0.3, 0, 280),
    "T05-4": (0.5, 0, 250),
}


def arrival(rate_m2: float = 0.4) -> dict:
    lines = ["sections inspected on arrival at site (teaching)",
             "  section   coating damage m2   share    dents   action"]
    odd = []
    for s, (d, dent, area) in DAMAGE.items():
        act = "touch-up record" if not dent else "NCR, maker's repair"
        if d / area > 0.005 or dent:
            odd.append(s)
        lines.append(f"  {s:8s}  {d:17.1f}   {d / area:6.2%}   {dent:5d}   {act}")
    lines += ["  T05-2 came with a dent near a flange: dents in a wall that",
              "  carries fatigue are assessed by the maker and the designer,",
              "  not filled; coating damage is touched up to the coating",
              "  maker's repair procedure, with its own DFT readings, before",
              "  the section is lifted"]
    emit("w_arrival", lines)
    return dict(odd=odd)


if __name__ == "__main__":
    bolt_lots()
    marks_value()
    bearing_gaps()
    fasteners()
    cert_types()
    arrival()
