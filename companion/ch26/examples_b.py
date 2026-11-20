"""Chapter 26, section B - the protection engineering workflow in numbers:
largest load currents, the pickup window between load and the smallest
fault, time multipliers derived for 0.3 s margins (they must equal the
settings in sources.py), the plant without the grid (converters only),
DC offset and CT saturation, capacitive earth-fault current, a
directional incomer, under-voltage settings against a ride-through
envelope, island detection by ROCOF, and the dependability of main and
backup protection.

Run from the project root:   python -m companion.ch26.examples_b
Writes companion/ch26/expected/b2_*.txt. Teaching values A-331 to A-335;
real settings come from the approved network model and the operator.
"""
from __future__ import annotations

import math

from companion.ch26 import sources as src
from companion.ch26.common import emit
from companion.ch26.examples_a import grading_cases
from plantp import protection as pr
from plantp.cables import peak_ka

N = src.NETWORK
KV = 33.0


def amps(mva: float, v_pu: float = 1.0) -> float:
    return mva * 1e6 / (math.sqrt(3) * KV * 1e3 * v_pu)


def loads() -> None:
    f1, f2 = amps(src.FEEDER_MVA), amps(src.FEEDER_MVA, 0.95)
    s1, s2 = amps(src.SECTION_MVA), amps(src.SECTION_MVA, 0.95)
    lines = ["largest load currents the relays must ride through:",
             f"  feeder =WS1: {src.FEEDER_MVA:.1f} MVA -> {f1:.0f} A at 1.0 pu,"
             f" {f2:.0f} A at 0.95 pu",
             f"  incomer: {src.SECTION_MVA:.1f} MVA -> {s1:.0f} A at 1.0 pu,"
             f" {s2:.0f} A at 0.95 pu",
             "  finding: the incomer breaker of ch 23 (1,250 A, marked",
             f"  provisional) is below {s2:,.0f} A; the protection work raises it",
             "  and its CT to 1,600 A (recorded in D-030; ch 24's panel +H01",
             "  follows) - settings work checks ratings, not only relays"]
    emit("b2_loads", lines)


def windows() -> None:
    far_ll = grading_cases()[2][1]
    bus_ll_min = 0.8 * N["ik_33_one"] * math.sqrt(3) / 2
    rows = [("feeder", amps(src.FEEDER_MVA, 0.95), far_ll),
            ("incomer", amps(src.SECTION_MVA, 0.95), bus_ll_min),
            ("T1 HV side (33 kV amps / 4)", amps(src.SECTION_MVA, 0.95) / 4, bus_ll_min / 4)]
    lines = ["pickup window: above 1.2 x load, below the smallest fault / 1.5",
             "  relay                          load A   min fault A   window A"
             "      set A"]
    for name, i_l, i_f in rows:
        lo, hi, ok = pr.pickup_window(i_l, i_f)
        key = name.split(" (")[0]
        setv = src.RELAYS[key]["pickup"]
        lines.append(f"  {name:30s} {i_l:7.0f}   {i_f:11,.0f}   {lo:5.0f}-{hi:5.0f}"
                     f"   {setv:6.0f}{'' if lo <= setv <= hi else ' (OUT)'}")
    lines += ["  smallest faults: line-to-line at the far end of =WS1 for the",
              "  feeder; line-to-line at the bus with a weak grid (0.8 x) for",
              "  the incomer; the windows are wide - overcurrent works here",
              "  because the grid feeds the faults (next: without the grid)"]
    emit("b2_window", lines)


def tms() -> None:
    cases = grading_cases()
    tf = src.RELAYS["feeder"]["tms"]
    need_i = max((pr.trip_time(i_f, src.RELAYS["feeder"]["pickup"], tf) + 0.3)
                 / pr.trip_time(i_i, src.RELAYS["incomer"]["pickup"], 1.0)
                 for _, i_f, i_i in cases)
    ti = math.ceil(need_i * 100) / 100
    need_h = max((pr.trip_time(i_i, src.RELAYS["incomer"]["pickup"], ti) + 0.3)
                 / pr.trip_time(i_i / 4, src.RELAYS["T1 HV side"]["pickup"], 1.0)
                 for _, _, i_i in cases)
    th = math.ceil(need_h * 100) / 100
    assert (ti, th) == (src.RELAYS["incomer"]["tms"], src.RELAYS["T1 HV side"]["tms"])
    lines = ["time multipliers derived for 0.3 s margins (all three cases):",
             f"  feeder TMS {tf:.2f} (fastest practical - it clears its own faults)",
             f"  incomer: largest need {need_i:.3f} -> TMS {ti:.2f}",
             f"  T1 HV side: largest need {need_h:.3f} -> TMS {th:.2f}",
             "  rounded up to the relay's 0.01 step; the same values are",
             "  in sources.py (the script checks they agree)",
             "  each TMS is set by its worst case: a grading made for one",
             "  switching state only can fail in another"]
    emit("b2_tms", lines)


def no_grid() -> None:
    i_conv = N["conv_ka"]
    own = 4 * 5.26 / 130 * i_conv              # the faulted feeder's own units
    seen = i_conv - own
    t = pr.trip_time(seen, src.RELAYS["feeder"]["pickup"], src.RELAYS["feeder"]["tms"])
    lines = ["the plant without the grid: only converters feed a fault",
             f"  all converters at about 1.2 x rated current: {i_conv / 1e3:.1f} kA at 33 kV",
             f"  the faulted feeder's relay sees the others: {seen:,.0f} A"
             f" -> trips in {t:.2f} s",
             "  the incomer sees nothing (the grid is gone); a converter's",
             f"  fault current is only {seen / amps(130 - 4 * 5.26):.1f} x the"
             " full-load current of the",
             "  same units - an overcurrent relay can hardly tell a fault",
             "  from a heavy load, and many converters inject little",
             "  negative sequence, which directional elements rely on",
             "  so: the plant must not run as an island (ch 20 keeps only",
             "  critical loads); grid loss is detected by under-voltage,",
             "  frequency and transfer trip, and the converters stop"]
    emit("b2_nogrid", lines)


def dc_offset() -> None:
    lines = ["DC offset of the fault current and CT saturation:",
             "  X/R   peak factor kappa   peak at 12.5 kA   CT size factor 1+X/R"]
    for xr in (5, 10, 20, 40):
        lines.append(f"  {xr:3d}   {peak_ka(1, xr) / math.sqrt(2):17.2f}"
                     f"   {peak_ka(12.5, xr):12.1f} kA   {1 + xr:20d}")
    lines += ["  the peak tests the gear's making rating (63 kA, ch 24); a CT",
              "  that never saturates with full offset would be 1+X/R times",
              "  larger - so relays are designed to cope with some",
              "  saturation, and the knee point is set from the relay",
              "  maker's requirement (the k of lesson A)"]
    emit("b2_offset", lines)


def capacitive() -> None:
    w = 2 * math.pi * 50
    c_f = src.feeder_c_uf() * 1e-6
    i_f = 3 * w * c_f * src.E_PH
    c_sec = (2 * src.feeder_c_uf() + (3 + 2) * 0.6 * 0.21) * 1e-6   # WS1, WS2, PVF3, BESS-A
    i_s = 3 * w * c_sec * src.E_PH
    lines = ["capacitive earth-fault current (charging of the healthy phases):",
             f"  =WS1 cable {src.feeder_c_uf():.2f} uF per phase -> 3 w C E = {i_f:.1f} A",
             f"  whole section A (about {c_sec * 1e6:.1f} uF) -> {i_s:.0f} A",
             "  a healthy feeder sends its own capacitive current through its",
             "  core-balance CT for a fault elsewhere: the feeder pickup",
             f"  ({src.EARTH['feeder']['pickup']:.0f} A) is above 2 x {i_f:.1f} A,"
             " so it does not trip in sympathy",
             f"  the 400 A resistor current is {400 / i_s:.0f} x the section's capacitive",
             "  current: it damps the arcing re-strikes that drive",
             "  overvoltages in an unearthed system",
             "  without its earthing transformer a section is unearthed:",
             f"  an earth fault gives only ~{i_s:.0f} A and the healthy phases rise",
             f"  to {math.sqrt(3):.2f} pu - so no section runs without its earthing source",
             "  (an interlock or an operating rule, decided with ch 23)"]
    emit("b2_capacitive", lines)


def directional() -> None:
    i_t1 = N["ik_33_both"] / 2                       # T1 from the HV side
    i_rev = N["ik_33_both"] / 2 + N["conv_ka"]       # T2 and converters, via the bus
    i_t2 = N["ik_33_both"] / 2                       # through =T2-Q2, forward
    inc = src.RELAYS["incomer"]
    t_rev = pr.trip_time(i_rev, inc["pickup"], inc["tms"])
    t_t2 = pr.trip_time(i_t2, inc["pickup"], inc["tms"])
    lines = ["coupler closed: fault on the cable between T1 and its incomer",
             f"  T1 feeds it from the HV side: about {i_t1 / 1e3:.1f} kA",
             f"  T2 and the converters feed it through the bus and BACKWARDS",
             f"  through =T1-Q2: {i_rev / 1e3:.1f} kA; =T2-Q2 carries"
             f" {i_t2 / 1e3:.1f} kA forward",
             f"  non-directional incomers: =T1-Q2 {t_rev:.2f} s, =T2-Q2 {t_t2:.2f} s"
             f" - margin {t_t2 - t_rev:.2f} s,",
             "  under the 0.3 s needed: the healthy T2 may trip as well,",
             "  and with it the whole plant",
             "  a directional element (67) on each incomer, looking toward",
             "  its transformer, trips only =T1-Q2, fast and selectively;",
             "  the differential of T1 (its zone ends at the incomer's CTs)",
             "  is the main protection and trips =T1-Q1 and =T1-Q2;",
             "  T2 keeps half the plant running"]
    emit("b2_directional", lines)


# [start: frt]
ENVELOPE = [(0.0, 0.0), (0.15, 0.0), (1.5, 0.85), (60.0, 0.85)]   # A-335


def envelope_v(t: float) -> float:
    """Lowest voltage (pu) the plant must ride through at time t (s)."""
    for (t0, v0), (t1, v1) in zip(ENVELOPE, ENVELOPE[1:]):
        if t0 <= t <= t1:
            return v0 + (v1 - v0) * (t - t0) / (t1 - t0) if t1 > t0 else v1
    return ENVELOPE[-1][1]
# [end: frt]


def frt_conflict() -> None:
    stages = [("27-1", 0.80, 0.20), ("27-1", 0.80, 2.00),
              ("27-2", 0.30, 0.10), ("27-2", 0.20, 0.30)]
    lines = ["under-voltage stages against a ride-through envelope (teaching):",
             "  envelope: 0 pu to 0.15 s, rising to 0.85 pu at 1.5 s",
             "  stage   pickup pu   delay s   envelope there   result"]
    for name, v, d in stages:
        e = envelope_v(d)
        bad = v > e
        lines.append(f"  {name:6s} {v:9.2f}   {d:7.2f}   {e:14.2f}   "
                     f"{'TRIPS INSIDE' if bad else 'ok'}")
    lines += ["  a stage trips inside the envelope when it can operate on a",
              "  voltage the plant must ride through: pickup above the",
              "  envelope at its delay; a protection that trips on a grid",
              "  dip breaks the connection requirement (ch 20, ch 28)"]
    emit("b2_frt", lines)


def rocof() -> None:
    lines = ["island detection by rate of change of frequency (teaching):",
             "  df/dt = dP x f0 / (2 H S); setting 1.0 Hz/s",
             "  power mismatch   H s   df/dt Hz/s   detected"]
    for dp, h in ((0.10, 0.5), (0.02, 0.5), (0.01, 2.0), (0.30, 0.5)):
        r = dp * 50 / (2 * h)
        lines.append(f"  {dp:14.0%}   {h:3.1f}   {r:10.2f}   {'yes' if r > 1.0 else 'NO'}")
    lines += ["  a near-balanced island changes frequency slowly and is not",
              "  seen (the non-detection zone); a grid event can raise",
              "  df/dt everywhere and trip healthy plants - the setting is",
              "  the operator's; transfer trip over the telecom link closes",
              "  the gap without depending on the power balance"]
    emit("b2_rocof", lines)


def reliability() -> None:
    p1, p2 = 0.01, 0.02
    lines = ["dependability: probability a fault is not cleared (teaching):",
             f"  main fails {p1:.0%}, backup fails {p2:.0%}, independent:"
             f" {pr.p_fail_to_clear(p1, p2):.1e}"]
    for beta in (0.05, 0.10, 0.20):
        p = (1 - beta) * p1 * p2 + beta * min(p1, p2)
        lines.append(f"  with a common cause (beta {beta:.2f}): {p:.1e}"
                     f"  ({p / (p1 * p2):.0f} x worse)")
    lines += ["  shared DC supply, shared CT core, one trip coil: each makes",
              "  main and backup fail together; separate DC circuits, CT",
              "  cores and trip coils keep them independent",
              "  security is the other side: two relays in parallel trip",
              "  more often by mistake - main and backup are graded, and a",
              "  scheme that must not trip falsely may need two to agree"]
    emit("b2_reliability", lines)


if __name__ == "__main__":
    loads()
    windows()
    tms()
    no_grid()
    dc_offset()
    capacitive()
    directional()
    frt_conflict()
    rocof()
    reliability()
