"""Chapter 35, lesson K (manufacturing and configuration): what is built
and tested in the factory for the network and SCADA - switch and server
burn-in, the configuration baseline of every networked device, and the
spares by device type.

Run from the project root:   python -m companion.ch35.examples_k
Writes companion/ch35/expected/k_*.txt.
Teaching values (A-400); the makers' quality plans and ch 48 decide.
"""
from __future__ import annotations

import hashlib
import math

from scipy import stats

from companion.ch35.common import emit


def baseline() -> None:
    devices = [("ring switch", 14), ("substation switch", 6), ("firewall", 2),
               ("RTU", 1), ("SCADA server", 2), ("historian", 1), ("time server", 2)]
    items = sum(n for _, n in devices)
    sample = "switch-T07 fw 4.2.1 vlan 10,20 ring-role member\n"
    fp = hashlib.sha256(sample.encode()).hexdigest()[:12]
    lines = ["configuration baseline of the networked devices (teaching)",
             "  device               count"]
    for d, n in devices:
        lines.append(f"  {d:20s} {n:5d}")
    lines += [f"  {items} devices, each with firmware version, configuration file",
              f"  and fingerprint (e.g. {fp}) recorded at the factory test,",
              "  re-read after installation and compared, and re-read",
              "  after every change - the same rule as the controller's",
              "  configuration in ch 34, applied to the network"]
    emit("k_baseline", lines)


def spares() -> None:
    rows = [("ring switch", 14, 300_000.0), ("SCADA server", 2, 50_000.0),
            ("RTU", 1, 150_000.0), ("fibre transceiver", 40, 500_000.0)]
    lead_h = 6 * 7 * 24                           # six weeks to replace from the maker
    lines = ["spares to cover the maker's lead time with 95 % confidence (teaching)",
             "  item                  installed   MTBF h    failures in lead   spares"]
    for name, n, mtbf in rows:
        lam = n * lead_h / mtbf
        k = int(stats.poisson.ppf(0.95, lam))
        lines.append(f"  {name:20s} {n:9d}   {mtbf:7,.0f}   {lam:16.2f}   {max(k, 1):6d}")
    lines += ["  a minimum of one spare of every type is kept even when the",
              "  expected failures are small: a ring with a dead switch",
              "  waits six weeks otherwise; spares carry the same firmware",
              "  baseline as the installed devices"]
    emit("k_spares", lines)


if __name__ == "__main__":
    baseline()
    spares()
