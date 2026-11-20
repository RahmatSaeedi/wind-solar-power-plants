"""Chapter 18, section C - interfaces and functional decomposition: the
product breakdown of Plant P with counts by level and make/buy, the
interface register by kind, the mismatch check that finds the planted
problems before procurement (the chapter's third worked example), and
the fixes.

Run from the project root:   python -m companion.ch18.examples_c
Writes companion/ch18/expected/c_*.txt.
Teaching data A-286.
"""
from __future__ import annotations

from collections import Counter, defaultdict

from companion.ch18 import sources as src
from companion.ch18.common import emit


def breakdown() -> None:
    root = src.breakdown()
    by_level = Counter()
    lines = ["product breakdown of Plant P (counts multiply down the tree):"]
    for node, n, depth in root.walk():
        by_level[node.level] += n
        if depth <= 2:
            mb = f" [{node.make_buy}]" if node.make_buy else ""
            lines.append(f"  {'  ' * depth}{node.name} x{n}{mb}")
    items = list(by_level.items())
    lines.append("  items by level: " + ", ".join(f"{k} {v:,}" for k, v in items[:3]))
    lines.append("    " + ", ".join(f"{k} {v:,}" for k, v in items[3:]))
    mb = Counter(node.make_buy or "unmarked" for node, n, _ in root.walk())
    lines += ["  make/buy marks: " + ", ".join(f"{k} {v}" for k, v in mb.items()),
              "  the replaceable units are what O&M stocks and changes; the",
              "  'buy+integrate' nodes are where the project owns the interface",
              "  between bought parts (chapters 39-48)"]
    emit("c_breakdown", lines)


def register() -> None:
    reg = src.interfaces()
    kinds = Counter(i.kind for i in reg)
    owners = defaultdict(list)
    for i in reg:
        owners[i.owner].append(i.iid)
    lines = [f"interface register: {len(reg)} interfaces; by kind:",
             "  " + ", ".join(f"{k} {v}" for k, v in list(kinds.items())[:4]),
             "  " + ", ".join(f"{k} {v}" for k, v in list(kinds.items())[4:]),
             "  owner of each interface:"]
    for o, v in owners.items():
        lines.append(f"    {o:15s} {', '.join(v)}")
    emit("c_register", lines)


def mismatches() -> None:
    reg = src.interfaces()
    bad = [(i, i.mismatch()) for i in reg if i.mismatch()]
    lines = [f"mismatch check before procurement: {len(bad)} of {len(reg)} interfaces"]
    for i, why in bad:
        lines.append(f"  {i.iid} {i.kind:10s} {i.side_a} / {i.side_b}: {i.item}:")
        lines.append(f"      {why}")
    lines += ["  fixes (to agree in the interface-control document):",
              "  IF-001 order the block transformer with a 0.60 kV winding (D-012)",
              "  IF-005 one connector type on both sides, from one maker",
              "  IF-006 HVAC sized on the container's rejected heat plus margin",
              "  IF-007 a protocol gateway, or require IEC 61850 in the BESS order",
              "  each is cheap on paper and costly after delivery"]
    emit("c_mismatch", lines)


if __name__ == "__main__":
    breakdown()
    register()
    mismatches()
