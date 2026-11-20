"""Chapter 36, lab D: a defensive design review of Plant P's synthetic
network model - flows seen against the conduit table, single points of
failure of the topology, and one review record that collects every
finding with its owner and due date.

Run from the project root:   python -m companion.ch36.lab_d
Writes companion/ch36/expected/d_*.txt.
Everything runs on synthetic tables in one process: no network, no
scanning, no device. Defensive and non-operational (A-401 to A-407).
"""
from __future__ import annotations

from companion.ch36 import sources as src
from companion.ch36.common import emit
from plantp import ot_security as ot


# [start: unlisted]
def unlisted_flows(flow_log, conduits):
    """Flows seen that no conduit allows: each is a finding."""
    return [(s, d, svc, n) for s, d, svc, n in flow_log
            if not ot.allowed(conduits, s, d, svc)]
# [end: unlisted]


# [start: spof]
def reachable(links, start, removed=None):
    """Nodes reachable from start when one node is removed."""
    adj = {}
    for a, b in links:
        if removed in (a, b):
            continue
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    seen, todo = {start}, [start]
    while todo:
        for nxt in adj.get(todo.pop(), ()):
            if nxt not in seen:
                seen.add(nxt)
                todo.append(nxt)
    return seen


def single_points(links, hub, targets):
    """Nodes whose loss cuts the hub off from at least one target."""
    nodes = {n for link in links for n in link} - {hub} - set(targets)
    out = {}
    for n in sorted(nodes):
        seen = reachable(links, hub, removed=n)
        lost = [t for t in targets if t not in seen]
        if lost:
            out[n] = lost
    return out
# [end: spof]


def flows() -> None:
    bad = unlisted_flows(src.FLOW_LOG, src.CONDUITS)
    lines = ["a week of flows (synthetic) checked against the conduit table",
             f"  flows seen: {len(src.FLOW_LOG)} kinds; allowed by a conduit:"
             f" {len(src.FLOW_LOG) - len(bad)}",
             "  not allowed by any conduit:"]
    for s, d, svc, n in bad:
        lines.append(f"    {s:10s} -> {d:9s} {svc:16s} {n:7,d} in a week")
    lines += ["  a file share from the business zone straight into control,",
              "  and inverters sending data to a maker's cloud past every",
              "  zone: neither has a purpose on the conduit table, so",
              "  each is closed or, if it is needed, given a conduit with",
              "  a purpose, an owner and a rule - through the DMZ"]
    emit("d_flows", lines)


def spof() -> None:
    targets = ["field-ied", "field-wtg", "field-pv", "field-bes", "dmz", "business"]
    sp = single_points(src.LINKS, "control", targets)
    lines = ["single points of failure of the synthetic topology",
             "  node        cuts the control zone off from"]
    for n, lost in sp.items():
        lines.append(f"  {n:11s} {', '.join(lost)}")
    lines += ["  the turbine and substation zones have two core switches;",
              "  PV and battery hang on core A alone - a finding, because",
              "  the battery's control path should not depend on one box;",
              "  the firewall pair is the only way to the DMZ, which is",
              "  accepted (lesson B): the plant runs without the DMZ"]
    emit("d_spof", lines)


FINDINGS = [  # finding, likelihood, consequence, owner, due (days)
    ("rule R05 allows any to any", 4, 5, "OT lead", 7),
    ("inverter data to a maker's cloud", 3, 4, "ctrl eng", 30),
    ("business file share into control", 3, 5, "OT lead", 7),
    ("PV and battery on one core switch", 2, 4, "ctrl eng", 180),
    ("vendor account with software rights", 3, 4, "OT lead", 14),
    ("firewall restore 12 min over target", 2, 2, "ctrl eng", 90),
    ("2 inventory rows without an owner", 3, 2, "OT lead", 30)]


def review_record() -> None:
    lines = ["design review record of the synthetic model (teaching scales)",
             "  finding                               score  band       owner     due d"]
    rows = sorted(((ot.risk_score(l, c), f, o, d) for f, l, c, o, d in FINDINGS),
                  reverse=True)
    for sc, f, o, d in rows:
        lines.append(f"  {f:37s} {sc:5d}  {ot.risk_band(sc):10s} {o:8s} {d:6d}")
    lines += ["  every finding has a score, an owner and a date; the record",
              "  is reviewed until each one is closed or accepted by the",
              "  asset owner in writing - and it names no address, no",
              "  product version and no path a reader outside could use"]
    emit("d_record", lines)


if __name__ == "__main__":
    flows()
    spof()
    review_record()
