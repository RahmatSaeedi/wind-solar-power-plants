"""Chapter 36, third deeper round: session timeouts, privileged rights only
when needed, a rise in deny-rule hits, the order of recovery by
dependency, makers' notice delays, an audit sample of logins, the
inventory against the devices seen, the risk register after controls,
and the indicators of the security programme.

Run from the project root:   python -m companion.ch36.examples_p
Writes companion/ch36/expected/p_*.txt and diagrams/data/ch36-*.csv.
Synthetic data and teaching values (A-401 to A-408); defensive only.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch36 import sources as src
from companion.ch36.common import csv, emit
from plantp import ot_security as ot


def timeouts() -> None:
    sessions, forgot = 48, 0.1                     # a year; share left open by mistake
    no_timeout_h = sessions * forgot * 45 * 24     # found at the quarterly review
    timeout_h = sessions * forgot * 4
    lines = ["vendor sessions left open by mistake (teaching)",
             f"  {sessions} sessions a year, 1 in 10 not closed by hand",
             f"  without a timeout, found at the next quarterly review: {no_timeout_h:,.0f} h open",
             f"  closed automatically after 4 h: {timeout_h:.0f} h open",
             "  a forgotten session is ordinary human error; the jump host",
             "  closes every session after its approved time, whatever",
             "  the person remembers"]
    emit("p_timeouts", lines)


def just_in_time() -> None:
    engineers, needed_h = 3, 200
    always = engineers * 8760
    jit = engineers * needed_h
    lines = ["administrator rights always held or given when needed (teaching)",
             f"  {engineers} engineers holding rights all year: {always:,} h",
             f"  rights given for each approved task, {needed_h} h each a year: {jit:,} h",
             f"  privileged hours cut by {(1 - jit / always) * 100:.1f} %",
             "  everyday work is done with an everyday account; the",
             "  administrator right is asked for, given for the task and",
             "  taken back, and each grant is in the log"]
    emit("p_jit", lines)


def deny_hits(seed: int = 366) -> None:
    rng = np.random.default_rng(seed)
    days = 60
    hits = rng.poisson(10, days).astype(float)
    hits[47] = 180                                  # a synthetic rise on one day
    base = hits[:30]
    mu, sd = base.mean(), base.std(ddof=1)
    z = (hits - mu) / sd
    flagged = [int(d) for d in np.where(z > 4)[0]]
    csv("ch36-deny.csv", "d,hits", [(d, int(h)) for d, h in enumerate(hits)])
    lines = ["hits on the default-deny rule a day (synthetic two months)",
             f"  first month: mean {mu:.1f}, spread {sd:.1f}",
             f"  days flagged above mean + 4 spreads: {flagged} ({int(hits[47])} hits)",
             "  a deny rule that suddenly blocks many times more than",
             "  usual says that something is trying a path that does not",
             "  exist - a misconfigured new device as often as anything",
             "  else; the flagged day is looked at the same day, and the",
             "  cause is written in the record"]
    emit("p_deny", lines)


DEPS = [  # system, hours to restore, systems it needs first (teaching)
    ("firewall", 2.2, []), ("time server", 1.0, ["firewall"]),
    ("OT directory", 2.0, ["time server"]),
    ("SCADA servers", 6.2, ["OT directory"]), ("HMIs", 2.0, ["SCADA servers"]),
    ("historian", 22.0, ["OT directory"])]


def recovery_order() -> None:
    finish = {}
    for name, h, need in DEPS:                     # listed in a valid order
        start = max((finish[n] for n in need), default=0.0)
        finish[name] = start + h
    serial = sum(h for _, h, _ in DEPS)
    lines = ["order of recovery after losing the control zone (teaching hours)",
             "  system            hours   needs first           ready at h"]
    for name, h, need in DEPS:
        lines.append(f"  {name:16s} {h:6.1f}   {', '.join(need) or '-':20s} {finish[name]:8.1f}")
    rows = [(i, name, finish[name] - h, finish[name]) for i, (name, h, _) in enumerate(DEPS)]
    csv("ch36-gantt.csv", "i,name,start,end", [(i, n.replace(" ", "-"), s, e) for i, n, s, e in rows])
    lines += [f"  operators see the plant again after {finish['HMIs']:.1f} h; the historian",
              f"    is back after {finish['historian']:.1f} h, working in parallel",
              f"  one person doing everything in turn: {serial:.1f} h",
              "  the order comes from what each system needs; the time",
              "  server and the directory are small but everything waits",
              "  for them - so their backups are tested first"]
    emit("p_order", lines)


def notice_delay() -> None:
    makers = {"S-A": 30, "S-B": 90, "S-C": 14}      # days from public report to maker notice
    test, window = 14, 90
    lines = ["from a public report to an installed fix (teaching days)",
             "  maker   notice   test   wait (mean)   total"]
    for m, n in makers.items():
        mean, _ = ot.patch_exposure_days(test, window)
        lines.append(f"  {m:6s} {n:7d}   {test:4d}   {window / 2:11.0f}   {n + mean:5.0f}")
    lines += ["  the maker's delay adds to the plant's own: a fast notice",
              "  is worth asking for in the tender (lesson K), and the",
              "  waiting time is covered by the compensating controls"]
    emit("p_notice", lines)


def audit_sample() -> None:
    logins, bad = 2000, 0.02
    lines = ["checking logins of a quarter against work permits (teaching)",
             f"  {logins:,} logins; suppose 2 % have no permit behind them",
             "  sample size   chance the sample finds at least one"]
    for n in (20, 50, 100, 150):
        lines.append(f"  {n:11d}   {(1 - (1 - bad) ** n) * 100:10.0f} %")
    need = math.ceil(math.log(0.05) / math.log(1 - bad))
    lines += [f"  {need} logins give 95 % confidence of finding the problem",
              "  if 2 % or more are unexplained; the sample is drawn at",
              "  random by program, and every miss is followed up"]
    emit("p_audit", lines)


def inventory_vs_seen() -> None:
    listed = {it["tag"] for it in src.INVENTORY}
    seen = listed - {"GPS-1"} | {"SW-X17", "LAPTOP-TMP"}   # synthetic passive listing
    lines = ["the inventory against the devices seen on the network (synthetic)",
             f"  in the inventory: {len(listed)}; seen talking: {len(seen)}",
             f"  seen but not listed: {', '.join(sorted(seen - listed))}",
             f"  listed but not seen: {', '.join(sorted(listed - seen))}",
             "  a device nobody listed has no owner and no baseline - here",
             "  a spare switch someone connected and a temporary laptop;",
             "  a listed device that is silent may be off, failed or",
             "  gone. The comparison uses the plant's own records of",
             "  traffic, read passively; nothing is probed"]
    emit("p_seen", lines)


def residual() -> None:
    rows = [("vendor remote access left open", (4, 4), (2, 4), "on request, timeouts"),
            ("rule added for a test, never removed", (4, 3), (2, 3), "quarterly review"),
            ("backups never restored", (3, 4), (1, 4), "restore tests"),
            ("shared operator account", (4, 2), (1, 2), "named accounts")]
    lines = ["the risk register before and after its controls (teaching scales)",
             "  scenario                               before  after   control"]
    for s, (l0, c0), (l1, c1), ctl in rows:
        lines.append(f"  {s:38s} {ot.risk_score(l0, c0):6d}  {ot.risk_score(l1, c1):5d}   {ctl}")
    lines += ["  controls lower the likelihood more often than the",
              "  consequence: a backup restored in a test does not make a",
              "  lost server cheaper, it makes a failed restore unlikely.",
              "  What remains is accepted by the asset owner in writing"]
    emit("p_residual", lines)


def indicators() -> None:
    rows = [("accounts reviewed this quarter", 6, 6),
            ("backups restored in a test this quarter", 4, 5),
            ("findings closed by their date", 5, 7),
            ("maker notices assessed within 14 days", 6, 6),
            ("devices matching their baseline", 26, 28)]
    lines = ["indicators of the security programme (synthetic quarter)",
             "  indicator                                   done   of    %"]
    for name, done, n in rows:
        lines.append(f"  {name:43s} {done:4d}   {n:3d}  {done / n * 100:4.0f}")
    lines += ["  indicators count what was done, not what was bought; a",
              "  number below 100 % is a list of names and dates, read by",
              "  the asset owner every quarter"]
    emit("p_kpi", lines)


if __name__ == "__main__":
    timeouts()
    just_in_time()
    deny_hits()
    recovery_order()
    notice_delay()
    audit_sample()
    inventory_vs_seen()
    residual()
    indicators()
