"""Chapter 34, lesson A (deeper): accuracy as a share of span or of the
reading, a current transformer at low load and its secondary burden, the
self-heating of a resistance thermometer, contact bounce and the time
stamp, leakage and induced current on a digital input, three sensors
with a median, and the lag of a sensor in a pocket.

Run from the project root:   python -m companion.ch34.examples_q
Writes companion/ch34/expected/q_*.txt and diagrams/data/ch34-*.csv.
Teaching values (A-385, extended); makers' data and tests decide.
"""
from __future__ import annotations

import math

import numpy as np
from scipy import stats

from companion.ch34.common import csv, emit
from plantp import instrumentation as ins


def span_vs_reading() -> None:
    span, acc = 200.0, 0.5            # coolant flow 0-200 L/min, 0.5 %
    lines = ["a coolant-flow transmitter 0-200 L/min, 0.5 % (teaching)",
             "  reading L/min   error if % of span   error if % of reading"]
    rows = []
    for q in (20.0, 50.0, 100.0, 200.0):
        e_span = acc * span / q
        lines.append(f"  {q:13.0f}   {e_span:15.2f} %   {acc:19.2f} %")
    for q in range(10, 201, 5):
        rows.append((q, round(acc * span / q, 3), acc))
    csv("ch34-span.csv", "q,span,reading", rows)
    lines += ["  a span figure is a fixed number of L/min: at a tenth of",
              "  the range it is 5 % of what is read; the range is chosen",
              "  so that normal flow (120 L/min) and the low-flow alarm",
              "  (60 L/min) both sit in the upper half, where the",
              "  figure on the data sheet is what the plant gets"]
    emit("q_span", lines)


# class limits of ratio error (teaching shape of the measuring classes;
# the limits themselves are read from the CT standard, STD-038)
CLASS_02 = [(5, 0.75), (20, 0.35), (100, 0.2), (120, 0.2)]
CLASS_02S = [(1, 0.75), (5, 0.35), (20, 0.2), (100, 0.2), (120, 0.2)]


def class_limit(table, pct: float) -> float | None:
    if pct < table[0][0]:
        return None
    for (x0, y0), (x1, y1) in zip(table, table[1:]):
        if pct <= x1:
            return y0 + (y1 - y0) * (pct - x0) / (x1 - x0)
    return None


def ct_low_load() -> None:
    ratio = 600.0                      # metering core of line bay E1 (teaching)
    points = [("night: own use and 2 Mvar", math.hypot(0.3, 2.0)),
              ("low wind, no sun: 5 MW", 5.0),
              ("20 MW", 20.0), ("60 MW", 60.0), ("export limit 100 MW", 100.0)]
    lines = ["132 kV metering core 600/1 A at the plant's operating points",
             "  point                         I A    % rated   class 0.2   0.2S"]
    for name, mva in points:
        i = mva * 1e6 / (math.sqrt(3) * 132e3)
        pct = 100 * i / ratio
        a, b = class_limit(CLASS_02, pct), class_limit(CLASS_02S, pct)
        fa = f"{a:7.2f} %" if a is not None else "   undef."
        fb = f"{b:5.2f} %" if b is not None else " undef."
        lines.append(f"  {name:28s} {i:6.1f}   {pct:6.1f}   {fa:9s}  {fb}")
    rows = [(p, class_limit(CLASS_02, p) or "nan", class_limit(CLASS_02S, p) or "nan")
            for p in (1, 2, 3, 4, 5, 7.5, 10, 15, 20, 40, 60, 80, 100, 120)]
    csv("ch34-ct.csv", "pct,c02,c02s", rows)
    lines += ["  a plant that runs for hours at a few per cent of its",
              "  export - every calm night - spends those hours where an",
              "  ordinary class is not defined; the metering and control",
              "  core is specified as an extended-range class (or with a",
              "  lower ratio), while the protection core keeps the ratio",
              "  the fault currents need (ch 26)"]
    emit("q_ct", lines)


def ct_burden() -> None:
    rho, length, area = 0.0175, 150.0, 2.5      # copper, one way, mm2
    r_loop = rho * 2 * length / area
    devices_va = 1.0                            # transducer + meter (teaching)
    lines = ["burden of a CT secondary run of 150 m in 2.5 mm2 copper",
             f"  loop resistance 2 x 150 m: {r_loop:.2f} ohm"]
    for i_sec in (1.0, 5.0):
        va = i_sec ** 2 * r_loop + devices_va
        lines.append(f"  {i_sec:.0f} A secondary: leads {i_sec ** 2 * r_loop:5.1f} VA"
                     f" + devices {devices_va:.1f} VA = {va:5.1f} VA")
    lines += ["  against a rated burden of 5 VA, the 1 A secondary fits",
              "  and the 5 A one needs ten times the copper; the leads are",
              "  part of the burden, and the class holds only over the",
              "  burden range the maker states - too little burden can",
              "  matter too, so the real burden is calculated and written",
              "  on the CT schedule"]
    emit("q_burden", lines)


def self_heating() -> None:
    r95 = ins.pt100_r(95.0)
    lines = ["self-heating of a Pt100 at 95 C (teaching coefficients)",
             f"  resistance at 95 C: {r95:.1f} ohm",
             "  current mA   power mW   error in still air   in an oil pocket"]
    for i_ma in (1.0, 2.0, 5.0):
        p_mw = (i_ma / 1000) ** 2 * r95 * 1000
        lines.append(f"  {i_ma:10.0f}   {p_mw:8.2f}   {0.5 * p_mw:15.2f} K"
                     f"   {0.05 * p_mw:13.3f} K")
    lines += ["  (0.5 K/mW in still air, 0.05 K/mW in oil - teaching)",
              "  the sensor warms itself by I^2 R and reads high; at 1 mA",
              "  the error is small anywhere, at 5 mA in still air it",
              "  exceeds a whole class B tolerance - the input module's",
              "  measuring current belongs on the sensor's data sheet"]
    emit("q_selfheat", lines)


def bounce_signal():
    """Contact state on a 0.1 ms grid (integer ticks avoid float drift)."""
    ticks = np.arange(950, 1250)
    edges = [1000, 1006, 1011, 1019, 1024, 1032, 1036]   # contact closes
    state = np.zeros(ticks.size, dtype=int)
    for k, e in enumerate(edges):
        state[ticks >= e] = 1 - k % 2
    return ticks / 10, state, [e / 10 for e in edges]


def debounce(state, hold_ticks: int):
    """Accept a new state only after it has held for hold_ticks samples."""
    out = np.zeros_like(state)
    accepted, since = state[0], 0
    for k in range(1, state.size):
        if state[k] != state[k - 1]:
            since = k
        if state[k] != accepted and k - since >= hold_ticks:
            accepted = state[k]
        out[k] = accepted
    return out


def contact_bounce() -> None:
    t, raw, edges = bounce_signal()
    deb = debounce(raw, 100)                        # 10 ms
    raw_edges = int(np.abs(np.diff(raw)).sum())
    deb_edges = int(np.abs(np.diff(deb)).sum())
    t_deb = t[np.argmax(deb > 0)]
    csv("ch34-bounce.csv", "t,raw,deb",
        [(round(a, 1), r, d) for a, r, d in zip(t[::5], raw[::5], deb[::5])])
    lines = ["a breaker auxiliary contact closing at 100.0 ms with bounce",
             f"  raw input: {raw_edges} edges in {edges[-1] - edges[0]:.1f} ms",
             f"  10 ms debounce: {deb_edges} edge, accepted at {t_deb:.1f} ms",
             f"  stamp taken at acceptance: {t_deb - edges[0]:.1f} ms late",
             "  stamp taken at the first edge, confirmed after 10 ms:",
             "    0.0 ms late, and still one event",
             "  a sequence-of-events input filters the bounce and keeps",
             "  the time of the first edge; an ordinary input that",
             "  stamps when it accepts adds its filter to every event"]
    emit("q_bounce", lines)


def di_leakage() -> None:
    v, r_in = 110.0, 110.0 / 3.0e-3            # input draws 3 mA when on
    on_ma, off_ma = 2.0, 1.5                    # thresholds (teaching)
    lines = ["a 110 V DC digital input with an open contact (teaching)",
             f"  input resistance {r_in / 1e3:.1f} kohm; on above {on_ma} mA,"
             f" off below {off_ma} mA",
             "  leakage across the contact   current mA   reads"]
    for r in (1e6, 100e3, 50e3, 20e3, 10e3):
        i = v / (r + r_in) * 1e3
        st = "off" if i < off_ma else ("ON (false)" if i > on_ma else "undefined")
        lines.append(f"  {r / 1e3:22.0f} kohm   {i:10.2f}   {st}")
    c_per_km, length_km, v_ac = 100e-9, 0.5, 230.0
    i_ac = 2 * math.pi * 50 * c_per_km * length_km * v_ac * 1e3
    lines += ["  230 V AC on another core of the same 500 m cable",
              f"    (100 nF/km between cores): {i_ac:.1f} mA - above the on level",
              "  damp terminals or a mixed AC/DC multicore can make an",
              "  open contact read closed; AC and DC never share a cable,",
              "  terminal boxes are kept dry, and inputs with a threshold",
              "  well above the leakage are chosen for long runs"]
    emit("q_leak", lines)


def median_select(seed: int = 341) -> None:
    rng = np.random.default_rng(seed)
    n, sigma = 3600, 0.2
    true = 60.0 + 2.0 * np.sin(np.linspace(0, 2 * np.pi, n))
    s = true + rng.normal(0, sigma, (3, n))
    s[2, 1800:] += np.minimum(np.arange(n - 1800) / 600, 1.0) * 5.0  # C: +5 K
    avg, med = s.mean(axis=0), np.median(s, axis=0)                 # in 10 min
    e_avg = np.abs(avg - true)[2400:].mean()
    e_med = np.abs(med - true)[2400:].mean()
    k, day = 3.0, 86400
    healthy = rng.normal(0, sigma, (2, day))       # a day of two healthy sensors
    dev = np.abs(healthy[0] - healthy[1]) > k * math.sqrt(2) * sigma
    per_h = dev.sum() / 24
    run = np.convolve(dev.astype(int), np.ones(10, dtype=int), "valid") == 10
    big = (np.abs(s[0] - s[2]) > k * math.sqrt(2) * sigma)[1800:].astype(int)
    held = np.convolve(big, np.ones(10, dtype=int), "valid") == 10
    first = int(np.argmax(held)) + 9
    lines = ["three temperature sensors; C drifts to +5 K over 10 min from",
             "  minute 30 (synthetic, noise 0.2 K each)",
             f"  error of the average once C has drifted: {e_avg:.2f} K",
             f"  error of the median once C has drifted:  {e_med:.2f} K",
             "  deviation alarm |A - B| > 3 x sqrt(2) x sigma, healthy pair:",
             f"    theory {2 * (1 - stats.norm.cdf(k)) * 3600:.1f} a hour at 1 s;"
             f" simulated over a day {per_h:.1f} a hour",
             f"    with 10 s of persistence: {int(run.sum())} in the day",
             f"  sensor C flagged (10 s held) {first} s after it began to drift,",
             f"    at about {5.0 * first / 600:.2f} K off",
             "  the median ignores one wild sensor where the average",
             "  follows it a third of the way; the deviation alarm that",
             "  tells which one drifted needs a threshold from the",
             "  combined uncertainty and a persistence time, or it",
             "  chatters on noise; real noise is correlated from sample",
             "  to sample, so the persistence is tuned on recorded data"]
    emit("q_median", lines)


def pocket_lag() -> None:
    tau, rate = 120.0, 1.0 / 60          # s; K per s (1 K a minute)
    lag_k = tau * rate
    lines = ["a temperature sensor in a pocket, time constant 120 s (teaching)",
             f"  oil warming at 1 K a minute: the reading lags by {lag_k:.1f} K",
             f"  an alarm at 85 C is raised {tau:.0f} s after the oil reaches it",
             "  after a step the reading reaches 63 % in 120 s, 95 % in"
             f" {3 * tau:.0f} s",
             "  the pocket and the paste in it set the lag; a",
             "  protection-grade temperature trip is set with the lag",
             "  in mind, and the pocket is part of the instrument's",
             "  installation drawing"]
    emit("q_lag", lines)


if __name__ == "__main__":
    span_vs_reading()
    ct_low_load()
    ct_burden()
    self_heating()
    contact_bounce()
    di_leakage()
    median_select()
    pocket_lag()
