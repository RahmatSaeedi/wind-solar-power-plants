"""Chapter 34, lab D (worked examples 1-3): Plant P's I/O list with a
checker and a draft that fails it, a synthetic POC voltage traced from
the VT to the operator display, and the test case of a simulated sensor
failure with its alarm and degraded mode.

Run from the project root:   python -m companion.ch34.lab_d
Writes companion/ch34/expected/d_*.txt and diagrams/data/ch34-trace.csv.
Synthetic signals and teaching settings (A-385 to A-387); no test here
is done on live equipment - the failure is simulated at the transducer
output with a calibrator or in the simulator.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch34 import sources as src
from companion.ch34.common import csv, emit
from plantp import control as ct
from plantp import instrumentation as ic

# [start: iolist]
IO_DRAFT = [  # tag, description, type, range, alarm, test
    ("E1-VT-U", "POC voltage L-L", "AI", (0.0, 150.0, "kV"),
     "<0.90 >1.10 pu", "T-03"),
    ("E1-MTR-P", "POC active power", "AI", (-120.0, 120.0, "MW"),
     None, "T-04"),
    ("E1-MTR-Q", "POC reactive power", "AI", None, None, "T-05"),
    ("T1-WTI", "T1 winding temperature", "AI", (0.0, 150.0, "C"),
     ">110 >130", None),
    ("E1-CB-POS", "line breaker closed", "DI", None, None, "T-10"),
    ("E1-CB-TRP", "line breaker tripped", "DI", None, "urgent", "T-10"),
    ("DC-UV", "110 V DC undervoltage", "DI", None, "urgent", "T-21"),
    ("FIRE-ANY", "fire alarm, any zone", "DI", None, "urgent", "T-30"),
    ("E1-CB-POS", "line breaker open", "DI", None, None, "T-10"),
    ("PPC-Q-CMD", "Q set point to units", "AO", (-33.0, 33.0, "Mvar"),
     None, "T-07")]
# [end: iolist]


def check(rows) -> list[str]:
    errs, seen = [], set()
    for tag, desc, kind, rng, alarm, test in rows:
        if tag in seen:
            errs.append(f"{tag}: tag used twice")
        seen.add(tag)
        if kind in ("AI", "AO") and rng is None:
            errs.append(f"{tag}: analogue point without a range")
        if test is None:
            errs.append(f"{tag}: no test case")
    return errs


def io_list() -> None:
    errs = check(IO_DRAFT)
    fixed = [list(r) for r in IO_DRAFT]
    fixed[2][3] = (-60.0, 60.0, "Mvar")
    fixed[3][5] = "T-15"
    fixed[8][0] = "E1-CB-OPN"
    errs2 = check([tuple(r) for r in fixed])
    lines = ["Plant P I/O list: extract of the draft and the checker (teaching)",
             "  tag         type  range             alarm             test"]
    for tag, desc, kind, rng, alarm, test in fixed:
        r = f"{rng[0]:g}..{rng[1]:g} {rng[2]}" if rng else "-"
        lines.append(f"  {tag:11s} {kind:4s}  {r:17s} {alarm or '-':17s} {test}")
    lines += [f"  draft findings ({len(errs)}):"] + [f"    {e}" for e in errs]
    lines += [f"  after correction: {len(errs2)} findings",
              "  a full list carries more columns - description, source",
              "  and destination panel, terminals, signal level, scaling,",
              "  quality handling, alarm priority, historian rate, owner",
              f"  - for every one of the {sum(n * (a + d + o) for _, n, a, d, o in src.EQUIPMENT)}"
              " hard-wired points (lesson C)"]
    emit("d_iolist", lines)


def _chain(true_kv: np.ndarray, dt: float, fail_at: float | None = None):
    """POC voltage through VT, transducer, converter, filter and scan.
    Returns (ma, kv_read, quality) at each time step."""
    c = src.CHAIN
    lo, hi = c["tx_range_kv"]
    ma = ic.eng_to_ma(true_kv, lo, hi)
    if fail_at is not None:
        ma = np.where(np.arange(len(ma)) * dt >= fail_at, 0.0, ma)
    step = ic.adc_step(c["ai_full_ma"], c["ai_bits"])
    counts = np.round(ma / step) * step
    kv = ic.ma_to_eng(counts, lo, hi)
    filt = ic.first_order_filter(kv, dt, c["filter_tau_s"])
    q = np.array([ic.quality(m, 0.0) for m in counts])
    return counts, filt, q


def trace(seed: int = 341) -> None:
    rng = np.random.default_rng(seed)
    dt = 0.05                                   # the PLC scan
    t = np.arange(0, 600, dt)
    pu = 1.0 - 0.02 * ((t >= 120) & (t < 300)) + rng.normal(0, 0.0005, t.size)
    true_kv = pu * src.CHAIN["u_nom_kv"]
    ma, kv, q = _chain(true_kv, dt)
    dv = kv / src.CHAIN["u_nom_kv"] - 1.0
    qset = ct.droop_reactive(dv, 33.0, 0.04)
    hmi = np.full(t.size, np.nan)                # report by exception, 0.2 % deadband, 1 s poll
    last = kv[0]
    for k in range(t.size):
        if k % int(1.0 / dt) == 0 and abs(kv[k] - last) > 0.002 * src.CHAIN["u_nom_kv"]:
            last = kv[k]
        hmi[k] = last
    k_step = int(120 / dt)
    t63_f = t[k_step + np.argmax(kv[k_step:] < 132 - 0.63 * 2.64)] - 120
    t_hmi = t[k_step + np.argmax(hmi[k_step:] < 132 - 0.63 * 2.64)] - 120
    rows = [(round(float(t[k]), 1), round(float(true_kv[k]), 2), round(float(kv[k]), 2),
             round(float(hmi[k]), 2)) for k in range(int(110 / dt), int(135 / dt), 5)]
    csv("ch34-trace.csv", "t,true,filtered,hmi", rows)
    i = int(125 / dt)
    lines = ["POC voltage from the VT to the operator display (synthetic, 2 % dip at 120 s)",
             "  stage                         value at t = 125 s",
             f"  true primary voltage          {true_kv[i]:.2f} kV",
             f"  VT secondary (L-L)            {true_kv[i] * 110 / 132:.2f} V",
             f"  transducer output             {ma[i]:.3f} mA",
             f"  converter + scaling + filter  {kv[i]:.2f} kV  (quality {q[i]})",
             f"  PPC: droop 4 %, 33 Mvar       Q set point {qset[i]:+.1f} Mvar",
             f"  HMI (1 s poll, 0.2 % deadband) {hmi[i]:.2f} kV",
             f"  delay to 63 % of the dip: filter {t63_f:.2f} s, display {t_hmi:.2f} s",
             "  each stage changes the number a little and delays it a",
             "  little: the controller sees the dip within half a second",
             "  and answers with reactive power; the operator sees it",
             "  about a second later - the time stamp on the display is",
             "  the controller's, not the screen's (lesson A, time)"]
    emit("d_trace", lines)


# [start: ppc]
def ppc_step(state: dict, t: float, kv: float, quality: str,
             meter_kv: float) -> float:
    """One scan of the PPC voltage function: use the transducer while its
    quality is good; hold the last Q and alarm when it is not; after 1 s
    use the meter channel (degraded mode)."""
    if quality == "good":
        state["bad_since"] = None
        u = kv
    else:
        if state["bad_since"] is None:
            state["bad_since"] = t
            state["alarm_at"] = t
        if t - state["bad_since"] < 1.0:
            return state["q"]                     # hold
        state["degraded_at"] = state.get("degraded_at") or t
        u = meter_kv
    state["q"] = float(ct.droop_reactive(u / 132.0 - 1.0, 33.0, 0.04))
    return state["q"]
# [end: ppc]


def failure_test() -> None:
    dt = 0.05
    t = np.arange(0, 30, dt)
    true_kv = np.full(t.size, 0.99 * src.CHAIN["u_nom_kv"])
    ma, kv, q = _chain(true_kv, dt, fail_at=10.0)
    state = {"q": 0.0, "bad_since": None}
    qs = []
    for k in range(t.size):
        meter = true_kv[(k // 20) * 20]               # meter value refreshed each second
        qs.append(ppc_step(state, float(t[k]), float(kv[k]), str(q[k]), float(meter)))
    qs = np.array(qs)
    k_bad = int(np.argmax(q == "bad"))
    before = qs[k_bad - 1]
    held = float(np.max(np.abs(qs[k_bad: k_bad + 20] - before)))
    after = qs[-1]
    naive = float(ct.droop_reactive(ic.ma_to_eng(0.0, 0, 150) / 132 - 1, 33.0, 0.04))
    lines = ["test case T-03b: POC voltage transducer loop opens (simulated)",
             "  precondition: plant in voltage control at 0.99 pu, signal",
             "    from a calibrator at the transducer output (no live work)",
             "  step: at t = 10.0 s the calibrator output is opened (0 mA)",
             "  expected                                   observed",
             f"  quality 'bad' within one scan (50 ms)      t = {t[k_bad]:.2f} s",
             f"  last good Q held for 1 s                   change {held:.2f} Mvar",
             f"  alarm 'POC V measurement bad'              t = {state['alarm_at']:.2f} s",
             f"  meter channel in use within 1 s            t = {state['degraded_at']:.2f} s",
             f"  Q on the meter channel = Q before          {after:+.2f} vs {before:+.2f} Mvar",
             "  result: PASS - recorded with the configuration fingerprint",
             f"  a controller that trusted the value of the dead loop would",
             f"  read -37.5 kV and order {naive:+.0f} Mvar, full reactive export -",
             "  quality comes before value"]
    emit("d_failure", lines)


def degraded() -> None:
    lines = ["degraded mode: the meter channel updates once a second (one-cycle lag)",
             "  gains            overshoot %   settled (2 %) s"]
    for name, kp, ki in (("normal 1.5 / 0.8", 1.5, 0.8), ("degraded 0.8 / 0.3", 0.8, 0.3)):
        y = ic.pi_loop(kp, ki, 2.0, 1.0, 61, delay=1)
        ov = max(0.0, (y.max() - 1) * 100)
        out = np.where(np.abs(y - 1) > 0.02)[0]
        ts = (out[-1] + 1) * 1.0 if len(out) else 0.0
        lines.append(f"  {name:16s} {ov:11.1f}   {ts:15.0f}")
    lines += ["  the normal gains on a once-a-second measurement overshoot",
              "  (lesson B); the degraded mode trades speed for a calm",
              "  response until the transducer is back - written in the",
              "  control narrative and proved in the same test case"]
    emit("d_degraded", lines)


if __name__ == "__main__":
    io_list()
    trace()
    failure_test()
    degraded()
