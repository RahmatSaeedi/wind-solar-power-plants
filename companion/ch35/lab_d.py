"""Chapter 35, lab D: a benign synthetic telemetry flow - a producer of
records, a validating consumer and logger, alarm rules, a text dashboard
and a diagnosis of the faults planted in the data. Everything runs in
one process on synthetic data: no network, no connection to any plant.

Run from the project root:   python -m companion.ch35.lab_d
Writes companion/ch35/expected/d_*.txt and diagrams/data/ch35-flow.csv.
Synthetic data (A-398, A-399).
"""
from __future__ import annotations

import numpy as np

from companion.ch35.common import csv, emit
from plantp import scada as sc

TAGS = {  # tag: (unit, low, high)
    "PLP-E1-VT.Voltage": ("kV", 0.0, 150.0),
    "PLP-WTG-T01.ActivePower": ("MW", -0.5, 5.5),
    "PLP-TRF-T1.OilTemp": ("C", -20.0, 120.0),
    "PLP-BES-C03.Soc": ("%", 0.0, 100.0),
    "PLP-MET-M1.Ghi": ("W/m2", -10.0, 1500.0)}
QUALITY = {"good", "bad", "uncertain", "substituted"}


# [start: validate]
def validate(rec: dict, last_t: dict) -> list[str]:
    """Reasons a record is refused (empty list = accepted). Checks the
    fields, the tag rule, the unit, the quality and that time moves on."""
    errs = []
    for key in ("tag", "value", "unit", "quality", "t"):
        if key not in rec:
            errs.append(f"missing {key}")
    if errs:
        return errs
    tag = rec["tag"]
    if not sc.tag_ok(tag) or tag not in TAGS:
        errs.append("unknown or malformed tag")
    elif rec["unit"] != TAGS[tag][0]:
        errs.append("wrong unit")
    if not isinstance(rec["value"], (int, float)):
        errs.append("value not a number")
    if rec["quality"] not in QUALITY:
        errs.append("unknown quality")
    if tag in last_t and rec["t"] <= last_t[tag]:
        errs.append("time not increasing")
    return errs
# [end: validate]


def produce(seed: int = 353):
    """Synthetic records, 10 minutes at 1 s, with planted faults."""
    rng = np.random.default_rng(seed)
    recs = []
    for k in range(600):
        t = float(k)
        vals = {"PLP-E1-VT.Voltage": 132.0 + rng.normal(0, 0.2),
                "PLP-WTG-T01.ActivePower": 3.0 + rng.normal(0, 0.1),
                "PLP-TRF-T1.OilTemp": 70.0 + k / 30 + rng.normal(0, 0.3),
                "PLP-BES-C03.Soc": 60.0 - k / 60,
                "PLP-MET-M1.Ghi": 850.0 + rng.normal(0, 5)}
        if k >= 300:
            vals["PLP-WTG-T01.ActivePower"] *= 1000      # planted: sent in kW, labelled MW
        for tag, v in vals.items():
            if tag == "PLP-MET-M1.Ghi" and k > 420:
                continue                                  # planted: station stops sending
            q = "bad" if (tag == "PLP-BES-C03.Soc" and 200 <= k < 230) else "good"
            recs.append({"tag": tag, "value": float(v), "unit": TAGS[tag][0],
                         "quality": q, "t": t})
    recs.insert(1000, {"tag": "plp-e1-vt.voltage", "value": 132.0, "unit": "kV",
                       "quality": "good", "t": 200.0})    # planted: malformed tag
    recs.insert(2000, {"tag": "PLP-E1-VT.Voltage", "value": 132.0, "unit": "kV",
                       "quality": "good", "t": 100.0})    # planted: time goes back
    recs.insert(2500, {"tag": "PLP-TRF-T1.OilTemp", "value": "hot", "unit": "C",
                       "quality": "good", "t": 1000.5})   # planted: text as value
    return recs


def consume(recs):
    log, refused, last_t = [], {}, {}
    for r in recs:
        errs = validate(r, last_t)
        if errs:
            for e in errs:
                refused[e] = refused.get(e, 0) + 1
            continue
        last_t[r["tag"]] = r["t"]
        log.append(r)
    return log, refused


def flow() -> None:
    recs = produce()
    log, refused = consume(recs)
    lines = ["synthetic telemetry: produced, accepted and refused records",
             f"  produced {len(recs):,}; accepted {len(log):,}; refused"
             f" {len(recs) - len(log)}",
             "  refusals by reason:"]
    for k, v in sorted(refused.items()):
        lines.append(f"    {k:28s} {v}")
    lines += ["  the consumer refuses what it cannot trust and says why;",
              "  it never repairs a record silently, and the refusal",
              "  counts are themselves a health signal of the interface"]
    emit("d_flow", lines)


def diagnose() -> None:
    log, _ = consume(produce())
    now = 599.0
    lines = ["diagnosis of the accepted data at t = 599 s",
             "  tag                          last value   quality   stale   scaling?"]
    rows = []
    for tag, (unit, lo, hi) in TAGS.items():
        recs = [r for r in log if r["tag"] == tag]
        last = recs[-1]
        is_stale = sc.stale([r["t"] for r in recs], now, 10.0)
        suspect = sc.scaling_suspect(last["value"], lo, hi)
        bad = sum(r["quality"] != "good" for r in recs)
        rows.append((tag, last["value"], bad, is_stale, suspect))
        lines.append(f"  {tag:28s} {last['value']:10.1f}   {bad:7d}   {'YES' if is_stale else 'no':5s}"
                     f"   {'YES' if suspect else 'no'}")
    lines += ["  the met station went silent at 420 s and is flagged stale;",
              "  turbine T01's power jumped a thousandfold at 300 s and",
              "  fits its range only divided by 1000 - kW labelled MW;",
              "  the 30 bad-quality battery values are kept, marked, and",
              "  never used for control or reports as if good"]
    emit("d_diagnose", lines)


def alarms() -> None:
    log, _ = consume(produce())
    temps = [r["value"] for r in log if r["tag"] == "PLP-TRF-T1.OilTemp"]
    states = sc.alarm_states(temps, 85.0, 1.0, 5)
    first = states.index(True) if True in states else None
    lines = ["alarm rule on the oil temperature: above 85 C for 5 s, clear below 84",
             f"  alarm raised at sample {first} ({temps[first]:.1f} C); transitions:"
             f" {sc.transitions(states)}",
             "  the rule is data, not code: limit, delay and deadband sit",
             "  in a reviewed table, and a test feeds it a known series and",
             "  checks the expected raise and clear"]
    emit("d_alarms", lines)


def dashboard() -> None:
    log, refused = consume(produce())
    lines = ["dashboard mock-up (text) at t = 599 s",
             "  +" + "-" * 60 + "+",
             f"  | {'Plant P - SCADA overview (SYNTHETIC, NOT A LIVE PLANT)':58s} |",
             "  +" + "-" * 60 + "+"]
    for tag, (unit, lo, hi) in TAGS.items():
        recs = [r for r in log if r["tag"] == tag]
        last = recs[-1]
        flag = "STALE" if sc.stale([r["t"] for r in recs], 599.0, 10.0) else (
            "CHECK SCALE" if sc.scaling_suspect(last["value"], lo, hi) else "ok")
        row = f"{tag:26s} {last['value']:10.1f} {unit:5s} {flag:12s}"
        lines.append(f"  | {row:58s} |")
    lines += ["  +" + "-" * 60 + "+",
              f"  interface refusals in the window: {sum(refused.values())}",
              "  a dashboard shows quality and age next to every value;",
              "  a number without them invites the operator to trust it"]
    emit("d_dashboard", lines)
    csv("ch35-flow.csv", "stage,count", [(1, len(produce())), (2, len(log))])


if __name__ == "__main__":
    flow()
    diagnose()
    alarms()
    dashboard()
