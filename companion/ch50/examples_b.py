"""Chapter 50, lesson B (progressive tests): PV strings against their
expected values, insulation records, relay injection results against the
settings, the plant-controller step, reactive capability, frequency
response and the performance-ratio test.

Run from the project root:   python -m companion.ch50.examples_b
Writes companion/ch50/expected/b_*.txt and diagrams/data/ch50-*.csv.
"""
from __future__ import annotations

import numpy as np

from companion.ch50 import sources as src
from companion.ch50.common import csv, emit
from plantp import commissioning as cm
from plantp import performance, pq, protection


def strings() -> dict:
    c = src.STRING_COND
    voc_e, isc_e = cm.string_expected(c["n"], c["g"], c["t_cell"])
    out = {s: cm.string_check(v, i, voc_e, isc_e, c["n"]) for s, (v, i) in src.STRINGS.items()}
    csv("ch50-strings.csv", "k,voc", [(k + 1, abs(v)) for k, (v, _) in
                                      enumerate(src.STRINGS.values())])
    bad = {s: v for s, v in out.items() if v != "ok"}
    lines = [f"combiner =PVF1-3-CB07, 20 strings of {c['n']} PVM-550 at {c['g']:.0f} W/m2 and "
             f"{c['t_cell']:.0f} C",
             f"  expected Voc {voc_e:,.0f} V and Isc {isc_e:.2f} A (ch 10 single-diode model)",
             "  (tolerances: Voc 3 %, Isc 5 %, teaching)"]
    lines += [f"  {s}: Voc {src.STRINGS[s][0]:+,d} V, Isc {src.STRINGS[s][1]:.2f} A - {v}"
              for s, v in bad.items()]
    lines += [f"  {len(bad)} of {len(out)} strings fail: a reversed string is found",
              "  before it meets the others at the fuse; a string one or",
              "  two modules short is a connector skipped or a module",
              "  bypassed; low current is shading, soiling or a mixed bin"]
    emit("b_strings", lines)
    return dict(voc=voc_e, isc=isc_e, bad=bad)


def insulation() -> list:
    bad = cm.below(src.IR, src.IR_LIMIT)
    lines = [f"insulation resistance of the 20 strings against the project limit "
             f"({src.IR_LIMIT:.0f} Mohm)"]
    lines += [f"  {s}: {src.IR[s] if src.IR[s] is not None else 'no record'}"
              + (" Mohm" if src.IR[s] is not None else "") for s in bad]
    lines += ["  a low value is a damaged cable, a wet connector or a",
              "  pinched sheath; the string stays isolated until the fault",
              "  is found and the test repeated; the test method and its",
              "  voltage come from the approved procedure, not this book"]
    emit("b_ir", lines)
    return bad


def relays() -> list:
    bad = cm.relay_check(src.RELAYS)
    lines = ["33 kV feeder overcurrent relays: injection results against the settings",
             "  (standard-inverse curve; tolerance 5 % + 40 ms, teaching)",
             "  relay      I/Is  expected s  measured s"]
    for name, i, pu, tms, t in src.RELAYS:
        te = protection.trip_time(i, pu, tms)
        lines.append(f"  {name:10s} {i / pu:4.1f}  {te:10.2f}  "
                     f"{'none' if t is None else format(t, '.2f'):>10s}"
                     + ("  OUT" if any(b[0] == name for b in bad) else ""))
    lines += [f"  {len(bad)} out: WS3's time points to a TMS left at another value",
              "  (the settings file of ch 26 says 0.25; 1.30 s fits about",
              "  0.30) and PVF3 was never tested - the read-back of the",
              "  settings file is the check before injection (lesson A)"]
    emit("b_relays", lines)
    return bad


def step() -> dict:
    s = src.STEP
    t = np.arange(0, 30.01, 0.1)
    p = np.where(t < s["delay"], s["p0"],
                 s["p1"] - (s["p1"] - s["p0"]) * np.exp(-(t - s["delay"]) / s["tau"]))
    p = p + np.where(t > s["delay"], 0.35 * np.exp(-(t - s["delay"]) / 6)
                     * np.sin((t - s["delay"]) * 1.3), 0)
    m = pq.step_metrics(t, p, s["p0"], s["p1"], s["band"])
    csv("ch50-step.csv", "t,p", [(round(a, 1), round(b, 2)) for a, b in zip(t[::3], p[::3])])
    ok = m["rise"] <= s["rise_req"] and m["settle"] <= s["settle_req"]
    lines = [f"plant-controller step test: set point {s['p0']:.0f} -> {s['p1']:.0f} MW at the POC",
             f"  rise (10-90 %) {m['rise']:.1f} s, required <= {s['rise_req']:.0f} s",
             f"  settling (+/-{s['band']:.0%}) {m['settle']:.1f} s, required <= "
             f"{s['settle_req']:.0f} s",
             f"  overshoot {m['overshoot']:.1%} - {'pass' if ok else 'FAIL'}",
             "  the test repeats ch 20's design case on the real plant: the",
             "  delay and the time constant measured here go back into the",
             "  validated model (REQ-G21)"]
    emit("b_step", lines)
    return dict(m=m, ok=ok)


def capability() -> list:
    csv("ch50-capability.csv", "p,qreq,qlag,qlead", src.CAPABILITY)
    bad = [(p, q, a, b) for p, q, a, b in src.CAPABILITY if a < q or -b < q]
    lines = ["reactive capability at the POC (ch 28 REQ-G01: +/-33 Mvar, teaching)",
             "  P MW  required  lagging  leading"]
    lines += [f"  {p:4d}  {q:8.0f}  {a:7.1f}  {b:7.1f}"
              + ("  SHORT" if (p, q, a, b) in bad else "") for p, q, a, b in src.CAPABILITY]
    lines += ["  at 100 MW the plant reaches 30.6 Mvar lagging: the converter",
              "  current limit and the hot day of ch 28 meet; the result is",
              "  a deviation for the network operator to accept or a",
              "  compensator to add - not a test to repeat until it passes"]
    emit("b_capability", lines)
    return bad


def droop() -> dict:
    f = src.FREQ_TEST
    d = pq.droop_fit(np.array(f["df"]), np.array(f["dp"]), f["deadband"])
    ok = abs(d - f["droop_req"]) <= f["tol"]
    csv("ch50-droop.csv", "df,dp", list(zip(f["df"], f["dp"])))
    lines = [f"frequency-response test: injected deviations outside a {f['deadband']} Hz "
             "deadband",
             f"  measured droop {d:.2f} %, required {f['droop_req']} +/- {f['tol']} % - "
             f"{'pass' if ok else 'FAIL'}",
             "  the test injects a signal into the controller, not a real",
             "  frequency event; a real event later is compared with this",
             "  result before the service is paid for (lesson G)"]
    emit("b_droop", lines)
    return dict(droop=d, ok=ok)


def pr_test(min_avail: float = 0.95) -> dict:
    used = [(d, h, e) for d, h, e, a in src.PR_DAYS if a >= min_avail]
    h = sum(x for _, x, _ in used)
    e = sum(x for *_, x in used)
    pr = performance.performance_ratio(e * 1000, src.PR_DC_KWP, h)
    lo = pr - src.PR_U
    lines = [f"PR test, {len(src.PR_DAYS)} days; days with data availability < "
             f"{min_avail:.0%} left out: "
             f"{', '.join(str(d) for d, *_, a in src.PR_DAYS if a < min_avail)}",
             f"  {len(used)} days: AC {e:,.0f} MWh, POA {h:.1f} kWh/m2, DC {src.PR_DC_KWP:,.0f} kWp",
             f"  PR = {e:,.0f} x 1000 / ({src.PR_DC_KWP:,.0f} x {h:.1f}) = {pr:.3f}",
             f"  guarantee {src.PR_GUARANTEE}; test uncertainty +/-{src.PR_U} -> lower bound "
             f"{lo:.3f}",
             "  the measured PR meets the guarantee; its lower bound does",
             "  not - whether the uncertainty counts is the contract's",
             "  rule, written before the test (ch 37, ch 48 sensors)"]
    emit("b_pr", lines)
    return dict(pr=pr, lo=lo, days=len(used))


if __name__ == "__main__":
    strings()
    insulation()
    relays()
    step()
    capability()
    droop()
    pr_test()
