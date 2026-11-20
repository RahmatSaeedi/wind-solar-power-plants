"""Chapter 36, second deeper round: the layers of a network and where each
control acts, local accounts against an OT directory, backup sizes and
windows, the patch backlog over a year, incident classes and who is told,
training by role, and VLAN port settings checked by program.

Run from the project root:   python -m companion.ch36.examples_n
Writes companion/ch36/expected/n_*.txt.
Synthetic data and teaching values (A-401 to A-408); defensive only.
"""
from __future__ import annotations

import numpy as np

from companion.ch36.common import emit


def layers() -> None:
    rows = [("physical", "cables, fibre, ports", "locked cabinets, unused ports off"),
            ("link", "frames inside a subnet", "port settings, VLAN per zone"),
            ("network", "addresses, routing", "zone firewall: conduit rules"),
            ("transport", "sessions, services", "only the conduit's service"),
            ("application", "protocol and its data", "protocol-aware gateway, roles")]
    lines = ["the layers of a network and where each control acts (teaching)",
             "  layer         carries                  control at this layer"]
    for a, b, c in rows:
        lines.append(f"  {a:13s} {b:24s} {c}")
    lines += ["  a control at one layer does not see the others: a",
              "  firewall that allows a service cannot tell a read from a",
              "  write inside it - that is the application's roles; a",
              "  VLAN keeps zones apart only if every port is set right"]
    emit("n_layers", lines)


def identity() -> None:
    devices, people = 28, 6
    local = devices * people
    lines = ["accounts on the networked devices: local or from an OT directory",
             f"  local accounts on each device: {devices} x {people} = {local} accounts",
             f"  one OT directory (not the business one): {people} accounts, {devices} devices"
             " trusting it",
             f"  a person leaves: {devices} devices to change, or 1 account to close",
             "  devices that cannot use the directory keep one local",
             "  account each, its secret in the vault, its use logged;",
             "  the OT directory is separate from the business one so a",
             "  business account problem does not reach the control zone"]
    emit("n_identity", lines)


def backups() -> None:
    rows = [("device configurations", 28, 0.05), ("controller programs", 3, 0.2),
            ("server images", 3, 200.0), ("HMI images", 6, 80.0)]
    rate_gb_h = 1e9 / 8 * 3600 / 1e9 * 0.5        # 1 Gbit/s at half speed
    lines = ["what is backed up and how long it takes (teaching sizes)",
             "  item                     count   GB each   total GB   hours at 0.5 Gbit/s"]
    total = 0.0
    for name, n, gb in rows:
        t = n * gb
        total += t
        lines.append(f"  {name:24s} {n:5d}   {gb:7.2f}   {t:8.1f}   {t / rate_gb_h:8.2f}")
    lines += [f"  {total:,.0f} GB in about {total / rate_gb_h:.1f} h; the historian's"
              " data is not",
              "  imaged but copied continuously to the DMZ (ch 35)",
              "  configurations are small and change often: kept after",
              "  every change; images are large and change rarely: kept",
              "  after each patch window and before each upgrade"]
    emit("n_backups", lines)


def backlog(seed: int = 365) -> None:
    rng = np.random.default_rng(seed)
    days = 365
    arrivals = rng.poisson(2 / 30, days)          # maker notices a day (about 2 a month)
    window_every, test_days = 90, 14
    open_count, queue, history = 0, [], []
    for d in range(days):
        for _ in range(arrivals[d]):
            queue.append(d)
        if d % window_every == window_every - 1:  # install what was tested in time
            queue = [a for a in queue if a > d - test_days]
        history.append(len(queue))
    lines = ["notices from makers waiting for installation over a year (synthetic)",
             f"  notices in the year: {int(arrivals.sum())}",
             f"  waiting on an average day: {np.mean(history):.1f}; at most: {max(history)}",
             "  quarterly windows let the backlog grow to a handful",
             "  before each window; each waiting notice has a risk note",
             "  and, where needed, a compensating control (lesson C)"]
    emit("n_backlog", lines)


def incident_classes() -> None:
    rows = [("1 low", "a refused USB, a failed login", "OT lead, weekly"),
            ("2 medium", "unknown device, unrecorded session", "OT lead, same day"),
            ("3 high", "unexpected change on a controller", "owner and OT lead, 1 h"),
            ("4 critical", "control affected or safety in doubt", "all + grid operator, now")]
    lines = ["incident classes and who is told (teaching)",
             "  class       example                               informed"]
    for a, b, c in rows:
        lines.append(f"  {a:11s} {b:37s} {c}")
    lines += ["  the class decides who is called and how fast, not whether",
              "  the plant stops - stopping is a safety decision of the",
              "  control room under the operating rules; reporting duties",
              "  to authorities come from the country (ch 55-57)"]
    emit("n_classes", lines)


def training() -> None:
    rows = [("operators", 8, 4), ("control engineers", 3, 16),
            ("maintenance staff", 10, 3), ("vendors on site", 12, 1)]
    total = sum(n * h for _, n, h in rows)
    lines = ["security training a year by role (teaching)",
             "  role                 people   hours each"]
    for r, n, h in rows:
        lines.append(f"  {r:20s} {n:6d}   {h:10d}")
    lines += [f"  {total} hours a year in all",
              "  operators learn what to report and to whom; engineers",
              "  learn the change path and restore; vendors learn the",
              "  site's rules before their first session - each course",
              "  ends with the person's name in the record"]
    emit("n_training", lines)


def vlan_ports() -> None:
    ports = [("SW-R01", 1, "wtg", "wtg"), ("SW-R01", 2, "wtg", "wtg"),
             ("SW-R01", 9, "unused", "wtg"),             # planted: unused port left open
             ("SW-C01", 4, "control", "control"), ("SW-C01", 5, "bes", "control"),  # planted
             ("SW-C01", 6, "unused", "disabled")]
    issues = [(s, p, want, got) for s, p, want, got in ports
              if not (want == got or (want == "unused" and got == "disabled"))]
    lines = ["port settings against the design (synthetic extract of 6)",
             "  switch   port   design     found"]
    for s, p, want, got in ports:
        lines.append(f"  {s:8s} {p:4d}   {want:9s}  {got}")
    lines += [f"  {len(issues)} findings: an unused port left in a working VLAN and a",
              "  battery port in the control zone's VLAN - each joins two",
              "  zones without a conduit. Port settings are compared with",
              "  the design by program at the factory test and after",
              "  every change"]
    emit("n_ports", lines)


if __name__ == "__main__":
    layers()
    identity()
    backups()
    backlog()
    incident_classes()
    training()
    vlan_ports()
