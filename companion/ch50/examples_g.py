"""Chapter 50, lessons G and H: grid-service and compliance acceptance
traced from ch 28's requirement register to signed results, and the export
circuit's commissioning records (phasing, cable sheath tests, intertrip
end to end).

Run from the project root:   python -m companion.ch50.examples_g
Writes companion/ch50/expected/g_*.txt and h_*.txt.
"""
from __future__ import annotations

from companion.ch28 import register as r28
from companion.ch50 import sources as src
from companion.ch50.common import emit
from plantp import commissioning as cm


def grid_trace() -> dict:
    reqs = {r.rid: r.topic for r in r28.REQUIREMENTS}
    t = cm.trace(reqs, src.GRID_TESTS)
    lines = [f"ch 28's {len(reqs)} grid requirements traced to commissioning results"]
    lines += [f"  no test planned: {', '.join(t['untested'])}",
              f"  planned, no result yet: {', '.join(t['open'])}",
              f"  failed: {', '.join(t['failed'])}"]
    lines += ["    " + f"{k}: {reqs[k]}" for k in t["untested"] + t["failed"]]
    lines += ["  four requirements have no test in the programme - the",
              "  network operator's acceptance needs an answer for each",
              "  (a test, a type test, a declaration it accepts); the",
              "  capability failure is DEV-11; a model not yet validated",
              "  (G21) holds the final operational notice"]
    emit("g_trace", lines)
    return t


def forecast_vs_service() -> None:
    lines = ["what proves a delivered grid service (REQ-G10, G24 contracted response)",
             "  a forecast score (ch 15, ch 37): how well the plant predicted",
             "    its output - it says nothing about a response delivered",
             "  a test result (lesson B): the controller answers an injected",
             "    signal with the droop asked - proof of capability",
             "  an event record: the plant's measured response to a real",
             "    frequency event, from the service meter at the agreed",
             "    measurement point - proof of delivery",
             "  only the last two go into the service's acceptance file"]
    emit("g_service", lines)


def export() -> dict:
    swapped = [k for k, (a, b) in src.PHASING.items() if a != b]
    sheath_bad = [k for k, v in src.SHEATH.items() if v != "pass"]
    it = src.INTERTRIP
    slow = [(k + 1, m) for k, m in enumerate(it["measured_ms"]) if m > it["limit_ms"]]
    lines = ["export circuit commissioning records",
             f"  phasing: {swapped[0]} designed {src.PHASING[swapped[0]][0]}, "
             f"found {src.PHASING[swapped[0]][1]}",
             f"  cable sheath tests not passed or not done: {', '.join(sheath_bad)}",
             f"  intertrip end to end, limit {it['limit_ms']} ms: trial(s) "
             f"{', '.join(f'{k} ({m} ms)' for k, m in slow)} over",
             "  a transformer phased ACB against ABC would short the bus at",
             "  the first parallel - the phasing check before closing the",
             "  coupler is the one that stops it; the slow intertrip trial",
             "  is the communications path (ch 28 intertrip, ch 35 links)",
             "  and is investigated, not averaged"]
    emit("h_export", lines)
    return dict(swapped=swapped, sheath=sheath_bad, slow=slow)


def energisation() -> None:
    steps = [("1", "export line and bay E1", "network operator, by its switching programme"),
             ("2", "132/33 kV transformers T1 then T2", "owner's authorised person"),
             ("3", "33 kV bus sections and coupler (phasing check)", "authorised person"),
             ("4", "feeders WS1-3, PVF1-3, BESS-A/B one by one", "authorised person"),
             ("5", "unit transformers, then converters (blocks)", "authorised person + makers"),
             ("6", "export in steps to the agreed limit (ch 28 tests)", "network operator")]
    lines = ["energisation order of Plant P (each step needs the one before it",
             "  accepted, and its own permission)"]
    for k, w, b in steps:
        lines += [f"  {k}. {w}", f"     by: {b}"]
    lines += ["  each step's permission is a record (lesson A); the order",
              "  keeps every new energisation backed by a tested upstream",
              "  protection - and the POC acceptance is the network",
              "  operator's signature, not the contractor's"]
    emit("h_order", lines)


if __name__ == "__main__":
    grid_trace()
    forecast_vs_service()
    export()
    energisation()
