"""Chapter 39, lesson J (environmental-data procurement): the data request
in the purchase package, a quality check of three declarations, all
three brought to one boundary with a controlled method for missing data,
a decision rule that respects uncertainty, and the use phase that the
loss guarantee already prices.

Run from the project root:   python -m companion.ch39.examples_j
Writes companion/ch39/expected/j_*.txt and diagrams/data/ch39-envdata.csv.
Synthetic teaching values (A-433): the material, factory and transport
factors are not from a real dataset, and no result is a project claim.
"""
from __future__ import annotations

import math

from companion.ch39 import sources as src
from companion.ch39.common import csv, emit

# ------------------------------------------------------ the request
REQUEST = [  # (field, what the package asks for)
    ("functional unit", "one 5.6 MVA unit transformer as specified,"
     " delivered to site"),
    ("boundary", "materials, manufacture, transport to site;"
     " use-phase losses apart"),
    ("method", "ISO 14067, or ISO 14025 Type III with its"
     " product rules named"),
    ("source and date", "dataset name, version and data year"),
    ("verification", "third-party verified or self-declared - stated"),
    ("allocation", "rule for recycled content and scrap stated"),
    ("limitations", "excluded items and cut-off threshold listed"),
    ("uncertainty", "stated as +/- %"),
    ("update", "re-issued at delivery with the as-built bill of"
     " materials"),
]


def request() -> None:
    lines = ["environmental data request in the transformer package"]
    for field, ask in REQUEST:
        lines += [f"  {field}:", f"      {ask}"]
    lines += ["  the request goes in the supplier data schedule (lesson D)",
              "  with an owner and a due date, like any other data item"]
    emit("j_request", lines)


# ------------------------------------------------ data quality check
FIELDS = [f for f, _ in REQUEST]
GIVEN = {  # fields each offer's declaration answers
    "U-A": set(FIELDS) - {"update"},
    "U-B": {"functional unit", "source and date", "method"},
    "U-C": {"source and date"},
}


def quality() -> dict[str, int]:
    lines = ["declarations against the request (fields answered of 9)"]
    out = {}
    for o, got in GIVEN.items():
        out[o] = len(got)
        missing = [f for f in FIELDS if f not in got]
        lines.append(f"  {o}  {len(got)} of {len(FIELDS)} answered")
        for k in range(0, len(missing), 3):
            lines.append(f"      missing: {', '.join(missing[k:k + 3])}")
    lines += ["  U-A misses only the update promise, which the contract",
              "  adds; U-B and U-C need the controlled method below"]
    emit("j_quality", lines)
    return out


# --------------------------------------- one boundary, controlled method
# [start: factors]
FACTORS = dict(  # t CO2e per t of material (generic, synthetic, A-433)
    core_steel=2.2, copper=3.4, oil=0.9, steel=1.8, other=2.5)
FACTORY_T_PER_MVA = 1.6          # generic factory factor, t CO2e per MVA
SEA, ROAD = 0.012, 0.09          # kg CO2e per t-km (synthetic)
BOM = {  # declared masses per unit, t (supplier data schedules)
    "U-A": dict(core_steel=7.1, copper=2.7, oil=3.6, steel=3.4, other=0.7),
    "U-B": dict(core_steel=7.4, copper=2.9, oil=3.8, steel=3.5, other=0.8),
    "U-C": dict(core_steel=7.0, copper=2.7, oil=3.6, steel=3.3, other=0.7),
}
ROUTE = {"U-A": (5_000, 600), "U-B": (0, 900), "U-C": (8_000, 600)}
# [end: factors]
AS_OFFERED = {"U-A": 41.0, "U-B": 8.0, "U-C": 36.0}   # lesson B, a_envdata

# (part, value t CO2e or None for "estimate", relative uncertainty)
DECLARED = {
    "U-A": [("cradle to gate", 41.0, 0.10)],
    "U-B": [("factory (gate to gate)", 8.0, 0.25),
            ("materials", None, 0.25)],
    "U-C": [("materials", None, 0.25), ("factory", None, 0.40)],
}


def materials(o: str) -> float:
    return sum(m * FACTORS[k] for k, m in BOM[o].items())


def transport(o: str) -> float:
    mass = sum(BOM[o].values())
    sea, road = ROUTE[o]
    return mass * (sea * SEA + road * ROAD) / 1000.0


def to_site(o: str) -> tuple[float, float, list[tuple[str, float, str]]]:
    """Cradle-to-site footprint, its +/- (root-sum-square) and parts."""
    parts = []
    for name, val, u in DECLARED[o]:
        if val is None:
            val = materials(o) if name == "materials" else (
                FACTORY_T_PER_MVA * src.PACKAGE["s_mva"])
            kind = "estimate"
        else:
            kind = "declared"
        parts.append((name, val, u, kind))
    parts.append(("transport to site", transport(o), 0.30, "estimate"))
    total = sum(p[1] for p in parts)
    unc = math.sqrt(sum((p[1] * p[2]) ** 2 for p in parts))
    return total, unc, [(p[0], p[1], p[3]) for p in parts]


def boundary() -> dict[str, tuple[float, float]]:
    lines = ["one boundary: cradle to site, t CO2e per unit (synthetic)"]
    out, rows = {}, []
    for o in DECLARED:
        total, unc, parts = to_site(o)
        out[o] = (total, unc)
        lines.append(f"  {o}: {total:5.1f} +/- {unc:4.1f}")
        for name, val, kind in parts:
            lines.append(f"      {name:24s} {val:5.1f}  {kind}")
        rows.append((len(rows) + 1, round(total, 2), round(unc, 2),
                     round(total + unc, 2), AS_OFFERED[o]))
    csv("ch39-envdata.csv", "offer,total,unc,upper,offered", rows)
    lines += ["  U-B was lowest as offered (8 t) and is highest on one",
              "  boundary; U-C's 36 t generic factor becomes a dated",
              "  estimate from its own bill of materials"]
    emit("j_boundary", lines)
    return out


def decide(vals: dict[str, tuple[float, float]]) -> list[str]:
    """Pairs whose difference exceeds the combined uncertainty."""
    names = sorted(vals)
    clear = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            (ta, ua), (tb, ub) = vals[a], vals[b]
            if abs(ta - tb) > math.hypot(ua, ub):
                clear.append(f"{a}-{b}")
    return clear


def decision() -> None:
    vals = {o: to_site(o)[:2] for o in DECLARED}
    clear = decide(vals)
    lines = ["decision rule: a difference counts only beyond the combined",
             "uncertainty (root-sum-square of the two)"]
    names = sorted(vals)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            d = vals[a][0] - vals[b][0]
            c = math.hypot(vals[a][1], vals[b][1])
            lines.append(f"  {a} - {b}: {d:+5.1f} t, combined +/- {c:4.1f}"
                         f" -> {'differs' if abs(d) > c else 'no rank'}")
    lines += [f"  pairs that differ: {len(clear)}",
              "  controlled method for estimates: score the upper bound",
              "  (value + uncertainty) so missing data never wins:"]
    for o in names:
        t, u = vals[o]
        kind = "verified" if o == "U-A" else "estimate"
        lines.append(f"    {o}  {t + u:5.1f}  ({kind})")
    lines += ["  the rule is written in the tender before the offers",
              "  arrive; the estimate is replaced by the supplier's own",
              "  data at delivery, and labelled as an estimate until then"]
    emit("j_decision", lines)


# ------------------------------------------------------- the use phase
def use_phase(grid_t_per_mwh: float = 0.5) -> None:
    f = src.FINANCE
    lines = ["the use phase: average losses over the life of one unit",
             f"  (load-loss factor {f['load_loss_factor']}, "
             f"{f['years']} years; grid factor {grid_t_per_mwh} t/MWh, ch 33)",
             "  offer  avg kW   MWh lost   t CO2e if displaced   x built"]
    for o, d in src.OFFERS.items():
        kw = d["p0_kw"] + d["pk_kw"] * f["load_loss_factor"]
        mwh = kw * 8760 * f["years"] / 1000
        t = mwh * grid_t_per_mwh
        built = to_site(o)[0]
        lines.append(f"  {o:5s}  {kw:6.1f}   {mwh:8,.0f}   {t:19,.0f}"
                     f"   {t / built:6.0f}")
    lines += ["  the losses dwarf the built footprint, and the loss",
              "  guarantee with its capitalisation (lesson D, ch 25)",
              "  already prices them - so the evaluation does not add",
              "  them again as carbon; it reports them beside it"]
    emit("j_use", lines)


if __name__ == "__main__":
    request()
    quality()
    boundary()
    decision()
    use_phase()
