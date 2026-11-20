"""Chapter 48, lesson B: panel and network production - a switch's port
schedule planned against as built, fibre link records against their
budget, copper certification records, and the two power feeds of each
cabinet.

Run from the project root:   python -m companion.ch48.examples_b
Writes companion/ch48/expected/b_*.txt and diagrams/data/ch48-*.csv.
Teaching values (A-501, A-502); defensive administration only.
"""
from __future__ import annotations

from companion.ch48 import sources as src
from companion.ch48.common import csv, emit
from plantp import hwmfg as hw


# ------------------------------------------------ 1. port schedule
def ports() -> dict:
    d = hw.diff_ports(src.PLANNED, src.ACTUAL)
    lines = ["switch SW-T05: port schedule as designed against the as-built file",
             f"  missing: {', '.join(f'{s}:{p}' for s, p in d['missing']) or '-'}",
             f"  extra:   {', '.join(f'{s}:{p}' for s, p in d['extra']) or '-'}"]
    for (s, p), f, a, b in d["changed"]:
        lines.append(f"  changed: {s}:{p} {f} {a} -> {b}")
    lines += ["  ports 5 and 6 swapped: the met station sits in the CCTV",
              "  VLAN and the camera in the control VLAN; the CMS on port 4",
              "  joined the control VLAN; and port 8 carries a laptop in the",
              "  default VLAN - a service connection left in; each one breaks",
              "  a zone of ch 36 without changing a single cable's colour",
              "  - the as-built file is compared with the design, port by port"]
    emit("b_ports", lines)
    return d


# ------------------------------------------------ 2. fibre records
def fibre() -> dict:
    p = src.FIBRE_DB
    lines = ["fibre links: measured loss against the expected loss and the budget",
             f"  (teaching: {p['per_km']} dB/km, {p['connector']} dB a connector, "
             f"{p['splice']} dB a splice;",
             f"  budget {p['budget']} dB: ch 35's 10 dB optics less its 3 dB margin)",
             "  link       km   expected dB   measured dB   verdict"]
    out, rows = {}, []
    for link, km, con, spl, meas in src.FIBRE:
        exp = km * p["per_km"] + con * p["connector"] + spl * p["splice"]
        v = hw.link_check(exp, p["budget"], meas)
        out[link] = (exp, meas, v)
        rows.append((link, round(exp, 2), meas))
        lines.append(f"  {link:9s} {km:4.2f}   {exp:11.2f}   {meas:11.2f}   {v}")
    csv("ch48-fibre.csv", "k,expected,measured",
        [(k + 1, e, m) for k, (_, e, m) in enumerate(rows)])
    lines += ["  T05-T06 passes the budget but is 1.5 dB above its expected",
              "  loss: a dirty or damaged connector, cleaned and re-measured",
              "  before it becomes the ring's weak link; T01-SUB is over",
              "  the budget and 2.4 dB above its own expected loss: its",
              "  connectors and splices are re-made and measured again before",
              "  longer-reach optics are bought - the west ring was already",
              "  tight in ch 35's paper budget"]
    emit("b_fibre", lines)
    return out


# ------------------------------------------------ 3. copper certification
def copper(max_m: float = 90.0) -> dict:
    lines = [f"copper links certified (teaching: permanent link <= {max_m:.0f} m, "
             "NEXT margin >= 0 dB)",
             "  link      length m   NEXT margin dB   report   our verdict"]
    bad = []
    for l, m, nx, res in src.COPPER:
        ok = m <= max_m and nx >= 0
        if not ok:
            bad.append(l)
        lines.append(f"  {l:8s}  {m:8d}   {nx:14.1f}   {res:6s}   "
                     f"{'ok' if ok else 'FAIL'}")
    lines += [f"  the report says 'pass' for all; {', '.join(bad)} fail when the",
              "  numbers are read: one is too long, one has a negative margin",
              "  - a tester set to the wrong limit prints 'pass'; the",
              "  results file, not the summary, is accepted"]
    emit("b_copper", lines)
    return dict(bad=bad)


# ------------------------------------------------ 4. power feeds
def power() -> dict:
    lines = ["the two power feeds of each network and control cabinet"]
    bad = []
    for c, (a, b) in src.POWER.items():
        same = a == b
        if same:
            bad.append(c)
        lines.append(f"  {c:11s} feed A {a:7s} feed B {b:7s} "
                     f"{'ONE SOURCE' if same else 'ok'}")
    lines += [f"  {', '.join(bad)}: two power supplies on one UPS - redundant in",
              "  the cabinet, single at the source; the core switch of the",
              "  substation goes dark with UPS-1, and with it every ring",
              "  (ch 35 single points, ch 36 recovery)"]
    emit("b_power", lines)
    return dict(bad=bad)


if __name__ == "__main__":
    ports()
    fibre()
    copper()
    power()
