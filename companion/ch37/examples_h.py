"""Chapter 37, lesson H (service-performance analytics): commands and
response on two clocks, delivered energy against the energy asked for,
recovery before the service is available again, telemetry quality in
settlement, and the limits of attribution.

Run from the project root:   python -m companion.ch37.examples_h
Writes companion/ch37/expected/h_*.txt and diagrams/data/ch37-*.csv.
Synthetic traces; every rule is a placeholder for the grid operator's
verified requirement (U-118).
"""
from __future__ import annotations

import numpy as np

from companion.ch37.common import csv, emit
from plantp import performance as pf


def set_point_series(seed: int = 386):
    """Ten minutes at 1 s: a set point that steps every 2 minutes and a
    first-order plant response with 1 s delay and tau 3 s."""
    rng = np.random.default_rng(seed)
    t = np.arange(600)
    sp = np.repeat([60.0, 45.0, 70.0, 50.0, 65.0], 120)
    r = np.empty(600)
    r[0] = 60.0
    for i in range(1, 600):
        target = sp[max(i - 1, 0)]
        r[i] = r[i - 1] + (target - r[i - 1]) / 3.0
    r += rng.normal(0, 0.15, 600)
    return t, sp, r


def clocks() -> None:
    t, sp, r = set_point_series()
    shift = 4                                           # logger 4 s behind
    r_logged = np.r_[np.full(shift, r[0]), r[:-shift]]   # value at i is r[i - 4]
    w = slice(10, -10)
    rms_raw, _ = pf.tracking_error(sp[w], r_logged[w])
    rms_true, _ = pf.tracking_error(sp[w], r[w])
    best, best_rms = 0, 1e9
    for lag in range(0, 12):
        rr = np.roll(r_logged, -lag)
        rms, _ = pf.tracking_error(sp[w], rr[w])
        if rms < best_rms:
            best, best_rms = lag, rms
    lines = ["set points from the controller, response from a logger 4 s late",
             f"  RMS tracking error as logged:              {rms_raw:5.2f} MW",
             f"  RMS on one clock (known here, synthetic):  {rms_true:5.2f} MW",
             f"  shift that minimises the error: {best} s, RMS {best_rms:5.2f} MW",
             f"  the clocks added {rms_raw - rms_true:.2f} MW of 'error'. The search shifted",
             f"  {best} s, {best - shift} s more than the clock fault: it also removed the",
             "  plant's own delay and flattered the response. Commands and",
             "  response are put on one time base from the clocks' own",
             "  records (ch 35, synchronisation), never from a fit"]
    emit("h_clocks", lines)


def delivered_energy() -> None:
    t = np.arange(0, 900.0, 1.0)                        # 15 min event at 1 s
    asked = np.full(t.size, 10.0)                       # 10 MW of response asked
    tau, delay = 4.0, 1.0
    got = np.where(t < delay, 0.0, 10.0 * (1 - np.exp(-(t - delay) / tau)))
    got[t >= 600] = np.minimum(got[t >= 600], 9.0)      # derates after 10 min (heat)
    e_ask = asked.sum() / 3600
    e_got = got.sum() / 3600
    csv("ch37-energy.csv", "t,p", [(int(a), round(b, 2)) for a, b in zip(t[::10], got[::10])])
    lines = ["a 15-minute response of 10 MW asked of the battery (synthetic)",
             f"  energy asked {e_ask:.3f} MWh, delivered {e_got:.3f} MWh"
             f" ({e_got / e_ask * 100:.1f} %)",
             "  the step was fast and the start looks perfect; a 1 MW",
             "  derating after ten minutes is what costs the energy.",
             "  Power at the step and energy over the event are two",
             "  measures, and the requirement says which one is paid"]
    emit("h_energy", lines)


def recovery() -> None:
    e_cap, soc0, floor = 40.0, 0.60, 0.50               # MWh, start, floor
    used = 10.0 * 0.25                                  # 10 MW for 15 min
    ready = floor + used / e_cap                        # room for one more event
    soc1 = soc0 - used / e_cap
    limit_min = 30.0                                    # recovery time (placeholder)
    lines = ["recovery: available again only with room for one more full event",
             f"  SOC before {soc0 * 100:.0f} %, after the event {soc1 * 100:.2f} %,"
             f" needed {ready * 100:.2f} %",
             f"  recovery allowed (placeholder): {limit_min:.0f} min",
             "  recharge power   energy MWh   time min   within the limit?"]
    for p_ch in (2.0, 5.0):
        need = max(ready - soc1, 0) * e_cap
        m = need / (p_ch * 0.94) * 60
        lines.append(f"  {p_ch:9.0f} MW   {need:10.2f}   {m:8.0f}   "
                     f"{'yes' if m <= limit_min else 'NO'}")
    lines += ["  (94 % one-way efficiency)",
              "  a gentle recharge, kinder to the cells and to the import",
              "  peak, can fail the recovery time; until the battery is",
              "  back above the line it is not available for the",
              "  service, and the record shows SOC with every event",
              "  because the next one is judged on it"]
    emit("h_recovery", lines)


def telemetry_quality() -> None:
    called, failed, bad_tel = 600, 9, 14
    lines = ["600 service hours, 9 failed, 14 with bad-quality telemetry",
             "  settlement rule (placeholder)          hours failed   availability"]
    for name, f in (("bad telemetry counts as failed", failed + bad_tel),
                    ("bad telemetry excluded", failed),
                    ("bad telemetry replaced by the meter", failed + 2)):
        den = called - bad_tel if "excluded" in name else called
        lines.append(f"  {name:37s} {f:12d}   {(den - f) / den * 100:11.2f} %")
    lines += ["  (with the revenue meter as backup, 2 of the 14 hours turn",
              "  out to be real failures)",
              "  the same month gives three results; the rule is in the",
              "  requirement, and the plant's own telemetry quality is",
              "  part of its performance (ch 34, ch 35)"]
    emit("h_telemetry", lines)


def attribution() -> None:
    rows = [("H1", "set point not reached", "inverter limit, 46 C", "plant"),
            ("H2", "response 12 s late", "PPC restart after update", "plant"),
            ("H3", "output cut", "grid voltage dip, FRT active", "unclear"),
            ("H4", "no response", "operator's command lost", "unclear"),
            ("H5", "set point not reached", "export limit order", "excluded")]
    pen = 500                                            # u per failed hour (teaching)
    plant = sum(1 for r in rows if r[3] == "plant")
    unclear = sum(1 for r in rows if r[3] == "unclear")
    lines = ["five failed service hours and who caused them (synthetic)",
             "  hour   what                    evidence                       charged"]
    for a, b, c, d in rows:
        lines.append(f"  {a:5s}  {b:22s}  {c:29s}  {d}")
    lines += [f"  penalty at {pen} u an hour (placeholder): {plant * pen:,} u certain,"
              f" {unclear * pen:,} u disputed",
              "  some hours cannot be pinned on one side with the data the",
              "  plant has: H3 needs the operator's voltage record, H4 its",
              "  command log. The plant states the limit of its own",
              "  evidence and asks for the other party's, instead of",
              "  claiming or accepting the hours on a guess"]
    emit("h_attribution", lines)


if __name__ == "__main__":
    clocks()
    delivered_energy()
    recovery()
    telemetry_quality()
    attribution()
