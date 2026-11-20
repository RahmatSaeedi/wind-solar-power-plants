"""Chapter 23 - more lessons: the revenue meter's error budget, the
voltage rise along a wind string, where the battery's auxiliaries are
supplied from, the isolation boundary of a cable section (and the RMU
switches the draft forgot), cable quantities, the LV distribution with
breaker ratings and a selectivity screen, the DC system's voltage window
and the plant's night-time own use.

Run from the project root:   python -m companion.ch23.examples_n
Writes companion/ch23/expected/n_*.txt. Teaching values A-316 to A-320.
"""
from __future__ import annotations

import copy
import math
from collections import deque

from companion.ch23 import sources as src
from companion.ch23.common import emit
from plantp import auxpower as ax
from plantp import oneline as ol

STD_A = (16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 400, 630)


def meter() -> None:
    i = 100e6 / (math.sqrt(3) * 132e3)
    parts = {"current transformer": 0.2, "voltage transformer": 0.2, "meter": 0.2}
    u = math.sqrt(sum(v ** 2 for v in parts.values()))
    e = 295_140.0                                   # MWh a year (D-019)
    lines = ["revenue meter at the 132 kV line bay (teaching classes):",
             f"  full-export current {i:.0f} A -> CT 600/1 A; VT 132/sqrt3 kV : 110/sqrt3 V",
             "  error budget (each a % limit, combined as independent):"]
    lines += [f"    {k:20s} {v:.1f} %" for k, v in parts.items()]
    lines += [f"  combined {u:.2f} % of {e:,.0f} MWh = {u / 100 * e:,.0f} MWh"
              f" = {u / 100 * e * 70 / 1e3:,.0f} k u a year at 70 u/MWh",
              "  a check meter on a second CT core lets the two be compared;",
              "  the classes, the CT burden and the meter's place are set by",
              "  the utility's metering code (U-065), not chosen here"]
    emit("n_meter", lines)


# [start: rise]
def string_profile(n: int = 4, km: float = 1.1, p_mw: float = 5.0,
                   q_mvar: float = 0.0, r: float = 0.160, x: float = 0.116):
    """Voltage rise along a radial string at full output: section k
    (from the substation) carries the units beyond it; dU = (P R + Q X)/U."""
    rise, rows = 0.0, []
    for k in range(1, n + 1):
        carried = n - k + 1
        p, q = carried * p_mw, carried * q_mvar
        du = (p * r * km + q * x * km) / 33.0 ** 2      # per unit
        rise += du
        rows.append((k, carried, du, rise))
    return rows
# [end: rise]


def rise() -> None:
    lines = ["voltage rise along wind string WS1 at full output (pf 1):",
             "  section  units carried  section rise %  rise at its end %"]
    for k, c, du, tot in string_profile():
        lines.append(f"  {k:7d}  {c:13d}  {du * 100:14.2f}  {tot * 100:17.2f}")
    q = string_profile(q_mvar=1.64)                      # pf 0.95 lagging export
    lines += [f"  with pf 0.95 (1.64 Mvar a unit exported): far end"
              f" {q[-1][3] * 100:.2f} %",
              "  the far turbine sits highest; the turbine's own voltage",
              "  range and the plant controller's reactive set-points must",
              "  allow it (ch 20, 27) - another quantity the one-line now",
              "  carries beside the cable"]
    emit("n_rise", lines)


def battery_aux() -> None:
    p, q, s = ax.demand(src.AUX, "normal", src.DIVERSITY)
    bess_kw = 8 * 120.0 / 3.0                           # 8 containers, COP 3
    s2 = math.hypot(p + bess_kw * src.DIVERSITY, q + bess_kw * 0.4 * src.DIVERSITY)
    lines = ["where the battery's auxiliaries are supplied from (a boundary):",
             f"  station service alone: {s:.0f} kVA -> {ax.next_size(s, 0.2)} kVA transformers",
             f"  battery HVAC peak: 8 containers x 120 kW cooling / COP 3 = {bess_kw:.0f} kW",
             f"  if the station service fed it too: {s2:.0f} kVA ->"
             f" {ax.next_size(s2, 0.2)} kVA transformers",
             "  Plant P keeps the battery's auxiliaries in the maker's",
             "  package (IF-006): the maker sizes them against its own",
             "  thermal design, and the station service stays small; the",
             "  boundary is a design decision recorded on the one-line"]
    emit("n_bessaux", lines)


def isolation_boundary(g: ol.OneLine, tag: str) -> list[str]:
    """Isolation points that bound a branch: walk outward from both ends
    and stop at the first isolation point on each path."""
    target = next(b for b in g.branches if b.tag == tag)
    found, seen = [], {target.tag}
    queue = deque([target.a, target.b])
    visited = {target.a, target.b}
    while queue:
        bus = queue.popleft()
        for br, nxt in g.neighbours(bus):
            if br.tag in seen:
                continue
            seen.add(br.tag)
            if br.isolation:
                found.append(br.tag)
            elif nxt not in visited:
                visited.add(nxt)
                queue.append(nxt)
    return sorted(found)


def isolation() -> None:
    g = src.plant()
    before = isolation_boundary(g, "=WS2-W3")
    h = copy.deepcopy(g)
    for b in list(h.branches):                      # add RMU switches
        if b.kind == "transformer" and b.tag.startswith("=WS2-"):
            b.isolation = True                       # T-off switch of the RMU
    for b in h.branches:
        if b.kind == "cable" and b.tag.startswith("=WS2-W"):
            b.isolation = True                       # cable switches of the RMU
    after = isolation_boundary(h, "=WS2-W3")
    lines = ["isolation boundary of the cable section =WS2-W3:",
             f"  draft one-line, isolation points: {len(before)}",
             "    " + ", ".join(before),
             "  only the feeder breaker: the whole string and its four",
             "  turbines go out - the draft has no switches in the RMUs",
             f"  with RMU cable and T-off switches, isolation points: {len(after)}",
             "    " + ", ".join(after),
             "  a section that can be isolated only by stopping the whole",
             "  string costs a string's energy at every repair; the RMU",
             "  switches belong on the one-line (an omission of rev A)"]
    emit("n_isolation", lines)


def quantities() -> None:
    drum = 0.5                                       # km of cable on a drum
    g = src.plant()
    joints = terms = 0
    km = 0.0
    for b in g.branches:
        if b.kind == "cable":
            L = b.rating.get("km", 0.0)
            km += L
            joints += max(0, math.ceil(L / drum) - 1)
            terms += 2
    lines = ["bounded cable quantities for the 33 kV collector:",
             f"  route length {km:.1f} km of three-core cable; drums of {drum * 1000:.0f} m",
             f"  joints {joints}, terminations {terms} (two per section)",
             f"  with the route still +/- 15 %: {km * 0.85:.1f} to {km * 1.15:.1f} km",
             "  quantities are bounded, not exact, until the route survey;",
             "  the joints and terminations are where cable faults start,",
             "  so their count is a reliability number too (ch 24)"]
    emit("n_quantities", lines)


def distribution() -> None:
    rows = []
    for ld in src.AUX:
        i = ld.kw * 1e3 / (math.sqrt(3) * 400 * ld.pf)
        need = 1.25 * i
        rating = next(a for a in STD_A if a >= need)
        rows.append((ld.tag, i, rating))
    incomer = 400
    lines = ["LV distribution: feeder breakers from full-duty currents:",
             "  feeder                             I A   breaker A  ratio to 400 A"]
    for tag, i, r in rows:
        lines.append(f"  {tag[:32]:32s} {i:6.1f}  {r:9d}  {incomer / r:10.1f}")
    lines += [f"  incomer {incomer} A (250 kVA at 0.4 kV is {250e3 / (math.sqrt(3) * 400):.0f} A)",
              "  every ratio is at least 1.6, a first screen for selectivity;",
              "  real selectivity comes from the makers' tables and the",
              "  coordination study (ch 26); motor feeders go to an MCC",
              "  with starters, sub-meters measure each load group"]
    emit("n_distribution", lines)


def dc_window() -> None:
    cells = 55
    lines = ["voltage window of the 110 V station battery (lead-acid, teaching):",
             f"  {cells} cells x 2.0 V nominal = {cells * 2.0:.0f} V",
             f"  float 2.23 V/cell = {cells * 2.23:.1f} V; equalise 2.33 V/cell = {cells * 2.33:.1f} V",
             f"  end of discharge 1.75 V/cell = {cells * 1.75:.1f} V",
             f"  window {cells * 1.75 / 110:.0%} to {cells * 2.33 / 110:.0%} of 110 V",
             "  every device on the DC board must work from the end of",
             "  discharge to the equalising voltage (the makers' ranges);",
             "  if one cannot, equalising is done with it disconnected or",
             "  the window is narrowed - a check, not an assumption"]
    emit("n_dcwindow", lines)


def night() -> None:
    loads = [("12 turbines idle (yaw, heating, control)", 12 * 6.0),
             ("10 PV inverter stations at night", 10 * 1.5),
             ("battery blocks standby (S1)", 8 * 12.0),
             ("station service (normal)", ax.demand(src.AUX, "normal", src.DIVERSITY)[0])]
    tot = sum(v for _, v in loads)
    lines = ["what the plant takes from the grid on a calm night (kW, teaching):"]
    lines += [f"  {k:42s} {v:6.0f}" for k, v in loads]
    lines += [f"  total {tot:.0f} kW; 10 calm night hours a week:"
              f" {tot * 10 * 52 / 1e3:,.0f} MWh a year imported",
              "  the import is metered (the revenue meter runs both ways)",
              "  and priced under the connection agreement; it is part of",
              "  the own use that ch 17 counted (4.5 GWh a year in its",
              "  detailed list), now traced to the equipment"]
    emit("n_night", lines)


if __name__ == "__main__":
    meter()
    rise()
    battery_aux()
    isolation()
    quantities()
    distribution()
    dc_window()
    night()
