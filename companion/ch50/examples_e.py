"""Chapter 50, lessons E and F: auxiliary systems tested as functional
chains (transfer, UPS and station battery autonomy, load shedding,
interlocks) and fire-protection acceptance (cause-and-effect coverage,
supervisory signals, readiness of responders).

Run from the project root:   python -m companion.ch50.examples_e
Writes companion/ch50/expected/e_*.txt and f_*.txt.
"""
from __future__ import annotations

from companion.ch50 import sources as src
from companion.ch50.common import emit
from plantp import commissioning as cm


# ------------------------------------------------ E. auxiliary chains
def transfer() -> list:
    t = src.TRANSFER
    bad = [(k + 1, s) for k, s in enumerate(t["measured_s"]) if s > t["limit_s"]]
    lines = [f"normal-to-alternate supply transfer of the 400 V station board, "
             f"limit {t['limit_s']:.0f} s",
             "  trial  time s"]
    lines += [f"  {k + 1:5d}  {s:6.1f}" + ("  OVER" if s > t["limit_s"] else "")
              for k, s in enumerate(t["measured_s"])]
    lines += ["  three trials pass and one takes 9.6 s: the transfer is not",
              "  accepted on its mean - the slow trial is the one the plant",
              "  will meet one night; its cause (a slow breaker spring, a",
              "  timer) is found and the four trials repeated"]
    emit("e_transfer", lines)
    return bad


def autonomy() -> dict:
    u, b = src.UPS_TEST, src.BATT_TEST
    ups_ok = cm.autonomy_ok(u["measured_min"], u["required_min"])
    batt_time = cm.autonomy_ok(b["measured_h"], b["required_h"])
    batt_v = b["end_v"] >= b["min_v"]
    lines = ["autonomy tests on the real load (results from the approved procedure)",
             f"  UPS-1 at {u['load_kw']} kW: {u['measured_min']:.0f} min against "
             f"{u['required_min']:.0f} required - {'pass' if ups_ok else 'FAIL'}",
             f"  110 V station battery at {b['load_a']:.0f} A: {b['measured_h']} h against "
             f"{b['required_h']} h required,",
             f"    but the voltage at the end was {b['end_v']:.0f} V against the "
             f"{b['min_v']:.0f} V the loads need",
             f"    - {'pass' if batt_time and batt_v else 'FAIL'}: the hours were there, the "
             "volts were not",
             "  an autonomy test has two criteria, time and the lowest",
             "  voltage the loads accept (ch 23 battery sizing); the UPS",
             "  becomes DEV-14, the battery a retest after the string is",
             "  checked cell by cell"]
    emit("e_autonomy", lines)
    return dict(ups=ups_ok, batt=batt_time and batt_v)


def shedding() -> list:
    wrong = [(l, p, o) for l, p, o in src.SHED if p != o]
    lines = ["load shedding of the station board: planned step against observed"]
    lines += [f"  {l:24s} planned {p}, observed {o}" + ("  WRONG" if p != o else "")
              for l, p, o in src.SHED]
    lines += ["  HVAC 1 and the workshop shed in the wrong order: the",
              "  control-room cooling went before the workshop - two wires",
              "  swapped at the shedding relay, found by testing the chain,",
              "  not each relay alone"]
    emit("e_shed", lines)
    return wrong


def interlocks() -> dict:
    fail = [k for k, v in src.INTERLOCKS.items() if v == "fail"]
    none = [k for k, v in src.INTERLOCKS.items() if v is None]
    lines = ["auxiliary interlocks tested end to end"]
    lines += [f"  {k:42s} {v or 'not tested'}" for k, v in src.INTERLOCKS.items()]
    lines += ["  the battery-room fan that does not run on charge is a safety",
              "  item (ch 23 ventilation): the room is not used for charging",
              "  until it passes; the diesel start on loss of both feeds is",
              "  the restart chain's first link and is tested before handover"]
    emit("e_interlocks", lines)
    return dict(fail=fail, none=none)


# ------------------------------------------------ F. fire acceptance
# [start: fire]
def fire() -> dict:
    share, missing = cm.cause_effect(src.CANDE, src.TESTED)
    sup_fail = [k for k, v in src.SUPERVISORY.items() if v != "pass"]
    return dict(share=share, missing=missing, sup_fail=sup_fail)
# [end: fire]


def show_fire() -> dict:
    r = fire()
    n = sum(len(v) for v in src.CANDE.values())
    lines = [f"fire cause-and-effect: {n} cause-effect pairs in the approved matrix",
             f"  proven in a test: {r['share']:.0%}; never proven:"]
    lines += [f"    {c} -> {e}" for c, e in r["missing"]]
    lines += [f"  supervisory signals failing: {', '.join(r['sup_fail'])}",
              "  every pair is proven once with the real devices (detectors",
              "  in test mode, extinguishing release simulated - never a",
              "  live discharge); a damper or a call to the fire service",
              "  never proven is a function nobody has seen work"]
    emit("f_cande", lines)
    return r


if __name__ == "__main__":
    transfer()
    autonomy()
    shedding()
    interlocks()
    show_fire()
