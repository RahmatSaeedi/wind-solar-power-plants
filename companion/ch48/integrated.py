"""Chapter 48 - three integrated Plant P examples: three numbers checked by
hand (a pyranometer budget, a 4-20 mA value, a fibre link's expected
loss), the acceptance of the measurement and network hardware
summarised, and the basis D-052.

Run from the project root:   python -m companion.ch48.integrated
Writes companion/ch48/expected/int_*.txt.
"""
from __future__ import annotations

import math

from companion.ch48 import sources as src
from companion.ch48.common import emit


# [start: hand]
def by_hand() -> dict:
    acc = 15.0                                  # 1.5 % of 1000 W/m2
    tc = 0.04 / 100 * 25 * 1000                 # 25 K above 20 C
    dr = 0.5 / 100 * 2 * 1000                   # two years of drift
    nl = 0.2 / 100 * 2000                       # of full scale
    rss = math.sqrt(acc ** 2 + tc ** 2 + dr ** 2 + nl ** 2)
    ma = 4 + 16 * 820 / 1600
    p = src.FIBRE_DB
    fo = 0.71 * p["per_km"] + 2 * p["connector"] + 2 * p["splice"]
    # [end: hand]
    lines = ["three numbers of this chapter checked by hand",
             f"  pyranometer at 45 C, 2 years: sqrt(15^2 + {tc:.0f}^2 + {dr:.0f}^2 + "
             f"{nl:.0f}^2) = {rss:.1f} W/m2",
             f"  820 W/m2 on a 0-1600 W/m2 loop: 4 + 16 x 820/1600 = {ma:.2f} mA",
             f"  T05-T06: 0.71 x 0.35 + 2 x 0.5 + 2 x 0.1 = {fo:.2f} dB expected",
             "  each equals the program's line (a_budgets, s_trace, b_fibre)"]
    emit("int_hand", lines)
    return dict(rss=rss, ma=ma, fo=fo)


def acceptance() -> dict:
    from companion.ch48 import examples_a as ea
    from companion.ch48 import examples_b as eb
    from companion.ch48 import examples_c as ec
    from companion.ch48 import lab_d
    ce = ea.certs()
    mt = ea.metering()
    po = eb.ports()
    fb = eb.fibre()
    cu = eb.copper()
    pw = eb.power()
    fw = ec.firmware()
    bk = ec.backups()
    ck = ec.clocks()
    fo = ec.failover()
    tg = lab_d.tags()
    lines = ["acceptance of the measurement and network hardware, summarised",
             f"  certificates: {len(ce)} of {len(src.CAL_CERTS)} incomplete; meter outside "
             f"its class at {', '.join(map(str, mt['bad']))} % load",
             f"  SW-T05: {len(po['changed'])} field changes on "
             f"{len({k for k, *_ in po['changed']})} ports, {len(po['extra'])} extra port "
             "(a laptop in VLAN 1)",
             "  fibre: " + ", ".join(f"{k} {v[2]}" for k, v in fb.items() if v[2] != "ok")
             + f"; copper: {', '.join(cu['bad'])} fail",
             f"  power: {', '.join(pw['bad'])} on one source; firmware: {len(fw)} "
             f"findings; backups stale: {len(bk)}",
             f"  clocks beyond 2 ms: {', '.join(ck['beyond'])}",
             f"  failover failed: {', '.join(fo['bad'])}; not done: "
             f"{', '.join(fo['missing'])}",
             f"  tag database: {len(tg)} problems",
             "  every item works on the day of the SAT; what fails is the",
             "  proof - and most of it would surface only on the worst day"]
    emit("int_accept", lines)
    return dict(tags=len(tg))


def basis() -> None:
    lines = ["D-052 instrumentation, metering, panel and network hardware basis",
             "  1 each sensor's datasheet turned into a site error budget; the",
             "    recalibration interval set from the drift the plant affords",
             "  2 calibration certificates read for accreditation, traceability,",
             "    uncertainty, conformity and date; metering chain tested at",
             "    low load and witnessed",
             "  3 cabinets rated for their place (IP, temperature, EMC, surge);",
             "    bonding and shield earthing recorded",
             "  4 port, connection and core schedules compared as built against",
             "    design; fibre and copper accepted on their results files",
             "  5 two power feeds from two sources, each supply able to carry",
             "    the cabinet alone",
             "  6 firmware against an approved baseline; backups after every",
             "    change; clocks within 2 ms; every redundancy test done",
             "  7 tag database validated on every revision and read against",
             "    the register map; loop checks to the display for every point",
             "  8 later findings: each anemometer's own transfer function",
             "    (the generic one moved the P50 by 4 %); the main/check meter",
             "    trend watched (16 days ahead of the limit); L-104's new",
             "    isolator needs its own supply; PoE, SCADA licence and WAN",
             "    video sized with room; the PR test names its sensors",
             "  open: makers' calibration and type-test records, the",
             "    integrator's as-built network files (U-129)"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    acceptance()
    basis()
