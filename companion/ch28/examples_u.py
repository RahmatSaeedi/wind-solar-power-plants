"""Chapter 28 - expansion round 10: sizing the telemetry signal list,
shallow against deep connection charges (commercial concepts, not legal
advice), and the completeness of a draft study report.

Run from the project root:   python -m companion.ch28.examples_u
Writes companion/ch28/expected/u_*.txt. Teaching values.
"""
from __future__ import annotations

from companion.ch28.common import emit


def signals() -> None:
    groups = [   # name, count, points each, period s
        ("wind turbines", 12, 20, 1.0), ("PV inverters", 10, 15, 1.0),
        ("POC and substation", 1, 40, 1.0), ("met stations", 2, 8, 10.0),
        ("battery (S1)", 4, 25, 1.0)]
    lines = ["telemetry inside the plant and to the operator (teaching sizes)",
             "  group                 count   points   period s   values/s"]
    total = 0.0
    for name, n, pts, per in groups:
        rate = n * pts / per
        total += rate
        lines.append(f"  {name:20s}  {n:5d}   {n * pts:6d}   {per:8.0f}   {rate:8.1f}")
    op = 24
    lines += [f"  plant SCADA (with S1): {total:.0f} values a second, ~{total * 86400 * 8 / 1e9:.1f} GB"
              " a day",
              f"  to the operator: a list of about {op} signals (POC P, Q, U, f,",
              "  breaker states, set-points received, limits, availability)",
              "  every 1-2 s within the latency budget of lesson C - the",
              "  list is the operator's (REQ-G17), the rest stays in the",
              "  plant; ch 34-36 build and secure both"]
    emit("u_signals", lines)


def charges() -> None:
    annuity = (1 - 1.075 ** -25) / 0.075
    energy = 295.1e3                               # MWh a year (D-019)
    shallow = 4.38                                 # line and bay (lesson G)
    deep = shallow + 6.0 * 100 / 250               # + share of a substation upgrade
    lines = ["shallow against deep connection charges (teaching; not legal advice)",
             "  charge     capex M u   u/MWh over 25 years at 7.5 %"]
    for name, c in (("shallow", shallow), ("deep", deep)):
        lines.append(f"  {name:8s}   {c:9.2f}   {c * 1e6 / annuity / energy:8.2f}")
    lines += ["  a 'shallow' charge pays for the plant's own connection; a",
              "  'deep' one adds a share of reinforcement further into the",
              "  grid (here 100 of 250 MW of a 6 M u upgrade); which rule",
              "  applies is the operator's and the regulator's (ch 55-57),",
              "  and the finance model (ch 21) carries it as a sensitivity"]
    emit("u_charges", lines)


def report() -> None:
    items = ["scope and stage", "input register with owners", "assumption log",
             "models with versions and validation", "cases (max/min, voltages, outages)",
             "load flow and reactive capability", "losses", "short circuit (max/min)",
             "protection interfaces", "dynamic results (FRT, frequency, control)",
             "sensitivities", "compliance matrix", "operating restrictions",
             "independent check", "signatures and approvals"]
    missing = {"assumption log", "sensitivities", "independent check", "operating restrictions"}
    lines = ["completeness of a draft study report (15 items)"]
    for it in items:
        lines.append(f"  [{'  ' if it in missing else 'ok'}] {it}")
    lines += [f"  {len(items) - len(missing)} of {len(items)} present; the four missing are",
              "  the ones that show what the results depend on and who",
              "  checked them - the report goes back before it goes out"]
    emit("u_report", lines)


if __name__ == "__main__":
    signals()
    charges()
    report()
