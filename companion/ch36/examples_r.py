"""Chapter 36, last round: wireless in the plant, and what happens when a
vendor's contract ends.

Run from the project root:   python -m companion.ch36.examples_r
Writes companion/ch36/expected/r_*.txt.
Teaching values (A-403, A-408); defensive only.
"""
from __future__ import annotations

from companion.ch36.common import emit


def wireless() -> None:
    rows = [("maintenance tablets", "business Wi-Fi", "reports, orders"),
            ("met mast radio (ch 35)", "own encrypted link", "field data"),
            ("nacelle service Wi-Fi", "off unless a permit", "maker's tools"),
            ("control zone", "no wireless at all", "-")]
    lines = ["wireless in the plant (teaching rules)",
             "  user                        network               for"]
    for u, n, f in rows:
        lines.append(f"  {u:27s} {n:21s} {f}")
    lines += ["  a radio reaches past fences and walls: the control zone",
              "  has none, a radio link that carries field data is its own",
              "  encrypted conduit, and a maker's service Wi-Fi is",
              "  switched on for the permit and off again after it"]
    emit("r_wireless", lines)


def contract_end() -> None:
    steps = [("vendor accounts disabled", 0.5), ("jump-host approvals removed", 0.2),
             ("data transfers returned or deleted, confirmed", 2.0),
             ("keys and certificates issued to the vendor revoked", 1.0),
             ("tools and laptops returned, media wiped", 1.0),
             ("conduit table and access matrix updated", 0.5)]
    total = sum(h for _, h in steps)
    lines = ["a vendor's contract ends: closing its access (teaching)",
             "  step                                                 hours"]
    for s, h in steps:
        lines.append(f"  {s:52s} {h:5.1f}")
    lines += [f"  {total:.1f} h of work on one day, from one checklist; a right",
              "  nobody remembers to close outlives the contract by years"]
    emit("r_contract", lines)


if __name__ == "__main__":
    wireless()
    contract_end()
