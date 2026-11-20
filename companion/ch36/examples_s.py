"""Chapter 36, governance in numbers: the firewall rule base over five
years, leavers' accounts, backup storage, log coverage of the zones, patch
priority by exposure, configuration drift between checks, and the work of
rotating secrets.

Run from the project root:   python -m companion.ch36.examples_s
Writes companion/ch36/expected/s_*.txt and diagrams/data/ch36-*.csv.
Synthetic tables and teaching values (A-403, A-404, A-408); defensive only:
no product, address, version or site detail.
"""
from __future__ import annotations

import numpy as np

from companion.ch36 import sources as src
from companion.ch36.common import csv, emit


def rule_backlog(years: int = 5) -> None:
    added, p_unused = 4, 0.03                  # rules a month; share going unused a month
    rows = []
    lines = ["the firewall rule base over five years (teaching rates)",
             f"  {added} rules added a month; a live rule falls out of use"
             f" with chance {p_unused * 100:.0f} %",
             "  a month",
             "  review       rules at month 60   of them unused   unused, 5-yr mean"]
    for name, every in (("never", None), ("yearly", 12), ("quarterly", 3)):
        live, unused = 8.0, 0.0                 # start with the 8 rules of lesson B
        series, unused_t = [], []
        for m in range(1, 12 * years + 1):
            newly = live * p_unused
            live += added - newly
            unused += newly
            series.append(live + unused)
            unused_t.append(unused)
            if every and m % every == 0:
                unused = 0.0                    # the review removes unused rules
        rows.append(series)
        lines.append(f"  {name:12s} {series[-1]:17.0f}   {unused_t[-1]:14.0f}"
                     f"   {np.mean(unused_t):17.0f}")
    csv("ch36-rules.csv", "m,never,yearly,quarterly",
        [(m + 1, round(a, 1), round(b, 1), round(c, 1)) for m, (a, b, c) in enumerate(zip(*rows))])
    lines += ["  without review the rule base grows by every rule that was",
              "  ever needed, and over half of it is rules nobody uses -",
              "  each a door kept open for no purpose. A yearly review",
              "  still leaves dozens open between reviews; a quarterly",
              "  one against the conduit table keeps the base close to",
              "  what the plant needs (lesson B, rules)"]
    emit("s_rules", lines)


def leavers() -> None:
    leavers_a_year = 12                          # staff and contractors (teaching)
    lines = ["accounts of people who left, still enabled (12 leavers a year)",
             "  process                               mean days open   account-days a year"]
    for name, days in (("found by the quarterly access review", 45.0),
                       ("disabled by the HR leaving process", 1.0),
                       ("contractor end date set at creation", 0.0)):
        lines.append(f"  {name:37s} {days:14.0f}   {leavers_a_year * days:19.0f}")
    lines += ["  a review that runs every 90 days leaves each leaver's",
              "  account open for 45 days on average; a leaving process",
              "  that tells the OT administrator closes it the same day,",
              "  and an end date set when the account is made needs no",
              "  one to remember. The review stays, to catch what the",
              "  process missed"]
    emit("s_leavers", lines)


def backup_storage() -> None:
    systems = {"SCADA servers": 0.8, "historian": 6.0, "engineering files": 0.4,
               "configurations": 0.05, "directory and time": 0.1}   # TB full size
    full_weeks, daily_change = 13, 0.02
    lines = ["backup storage: weekly fulls kept 13 weeks, daily changes 2 %",
             "  system                 full TB   kept TB"]
    total = 0.0
    for name, tb in systems.items():
        kept = tb * full_weeks + tb * daily_change * 6 * full_weeks
        total += kept
        lines.append(f"  {name:21s} {tb:8.2f}   {kept:7.1f}")
    copies = 2                                  # one on site, one off site (lesson C)
    lines += [f"  one copy {total:.1f} TB; two independent copies {total * copies:.1f} TB",
              "  the historian sets the size; keeping its fulls for 13",
              "  weeks costs more than every other system together. A",
              "  historian that can be rebuilt from the field devices'",
              "  buffers and the plant's archive needs fewer fulls - a",
              "  decision taken with its recovery objective, not by the",
              "  size of the disk"]
    emit("s_backup", lines)


def log_coverage() -> None:
    sending = {"field-ied": 30, "field-wtg": 6, "field-pv": 12, "field-bes": 24,
               "control": 12, "dmz": 3}         # devices that send security logs (synthetic)
    lines = ["devices that send security logs, by zone (synthetic)",
             "  zone          devices   sending   coverage"]
    tot_d = tot_s = 0
    rows = []
    for zone, n_send in sending.items():
        n = src.ZONES[zone]["devices"]
        tot_d += n
        tot_s += n_send
        rows.append((zone, n, n_send))
        lines.append(f"  {zone:12s} {n:8d}   {n_send:7d}   {n_send / n * 100:7.0f} %")
    lines += [f"  all OT zones  {tot_d:7d}   {tot_s:7d}   {tot_s / tot_d * 100:7.0f} %",
              f"  a total of {tot_s / tot_d * 100:.0f} % hides the gaps: a quarter of the turbines",
              "  and under a third of the inverters are silent. Devices",
              "  that cannot log are covered at the next layer - the",
              "  switch port, the firewall in front of the zone - and the",
              "  gap is written in the risk register, not left unseen"]
    csv("ch36-coverage.csv", "i,n,s", [(i, n, s) for i, (_, n, s) in enumerate(rows)])
    emit("s_coverage", lines)


def patch_priority(seed: int = 361) -> None:
    rng = np.random.default_rng(seed)
    n = 40
    severity = rng.integers(1, 6, n)                        # maker's rating 1-5
    exposure = rng.choice([1, 2, 3], n, p=[0.5, 0.3, 0.2])  # 3 = reachable from the DMZ
    days_each = 3                                           # test and install, per notice
    def exposure_days(order):
        t, total = 0, 0.0
        for i in order:
            t += days_each
            total += severity[i] * exposure[i] * t
        return total
    by_sev = np.argsort(-severity, kind="stable")
    by_risk = np.argsort(-(severity * exposure), kind="stable")
    in_order = np.arange(n)
    rows = [("in the order they arrived", exposure_days(in_order)),
            ("by the maker's severity", exposure_days(by_sev)),
            ("by severity x exposure", exposure_days(by_risk))]
    base = rows[0][1]
    lines = ["40 notices (synthetic), 3 days each to test and install",
             "  order                         weighted exposure   share"]
    for name, v in rows:
        lines.append(f"  {name:29s} {v:17,.0f}   {v / base * 100:5.0f} %")
    lines += ["  weighted exposure = severity x exposure x days waiting;",
              "  a severe notice for a device no one can reach waits behind",
              "  a medium one on a device reachable from the DMZ. The",
              "  exposure comes from the zone and conduit tables, which is",
              "  why they are kept current"]
    emit("s_patch", lines)


def drift(seed: int = 362) -> None:
    rng = np.random.default_rng(seed)
    changes = rng.uniform(0, 365, 30)                       # unrecorded changes a year
    lines = ["unrecorded configuration changes found by comparing with the baseline",
             "  check every   mean days undetected   longest"]
    for every in (1, 7, 30, 90):
        wait = (np.ceil(changes / every) * every) - changes
        lines.append(f"  {every:4d} days   {wait.mean():20.1f}   {wait.max():7.1f}")
    lines += ["  a change that bypassed the change process stays unseen",
              "  for half the check interval on average; a weekly",
              "  automated comparison of fingerprints (lesson E) costs",
              "  little and keeps the gap to days"]
    emit("s_drift", lines)


def rotation() -> None:
    secrets = {"service accounts": (40, 365, 0.5), "device local admin": (150, 365, 0.25),
               "vendor break-glass": (12, 90, 0.5), "certificates": (60, 730, 1.0)}
    lines = ["rotating secrets: number, interval and hours each (teaching)",
             "  secret                 count   every d   h each   h a year by hand"]
    total = 0.0
    for name, (n, every, h) in secrets.items():
        year_h = n * 365 / every * h
        total += year_h
        lines.append(f"  {name:21s} {n:6d}   {every:7d}   {h:6.2f}   {year_h:16.0f}")
    lines += [f"  by hand {total:.0f} hours a year - about {total / 1700:.2f} of a person;",
              "  the hours are small, the risk is the rotation forgotten:",
              "  262 secrets on four calendars are rotated late when the",
              "  one person who knows is away. A vault that rotates the",
              "  service and local accounts itself leaves only the",
              "  break-glass and certificate work, and makes each",
              "  rotation a record instead of a memory"]
    emit("s_rotation", lines)


if __name__ == "__main__":
    rule_backlog()
    leavers()
    backup_storage()
    log_coverage()
    patch_priority()
    drift()
    rotation()
