"""Chapter 36, lesson B (defensive architecture): zones and their target
levels, a firewall rule review, the access matrix, remote access by
request, the volume of security logs and the clocks that make them
comparable, the strength of secrets, a hardening checklist, the firewall
pair as a single point of failure, and the interface with physical
security.

Run from the project root:   python -m companion.ch36.examples_b
Writes companion/ch36/expected/b_*.txt.
Synthetic data and teaching values (A-401 to A-403); defensive only.
"""
from __future__ import annotations

from companion.ch36 import sources as src
from companion.ch36.common import emit
from plantp import ot_security as ot


def zones() -> None:
    lines = ["zones of Plant P and their target levels (teaching labels, STD-158 concept)",
             "  zone        devices   target   function"]
    for z, d in src.ZONES.items():
        lines.append(f"  {z:11s} {d['devices']:7d}   {d['target']:6s}   {d['function']}")
    lines += ["  a zone groups devices that share a function and a need for",
              "  protection; a conduit is the one controlled way between",
              "  two zones (lesson A); the target level says how hard",
              "  the zone must be to reach - it is decided by the risk",
              "  assessment of the design (STD-157), not by habit"]
    emit("b_zones", lines)


def rule_review() -> None:
    found = ot.review_rules(src.RULES)
    lines = ["review of the zone firewall rules (synthetic, first match wins)",
             "  rule  src       dst       service          action  hits"]
    for r in src.RULES:
        lines.append(f"  {r['id']:4s}  {r['src']:8s}  {r['dst']:8s}  {r['service']:15s}"
                     f"  {r['action']:6s}  {r['hits']:,}")
    for k, v in found.items():
        lines.append(f"  {k:13s}: {', '.join(v) if v else '-'}")
    lines += ["  R05 allows everything and hides every rule after it,",
              "  including the default deny; R06 is a commissioning rule",
              "  that outlived its purpose; R07 has never matched. The fix",
              "  is the conduit table: one allow rule a conduit, a",
              "  purpose and an owner on each, default deny last, and a",
              "  review of hits and purposes every quarter"]
    emit("b_rules", lines)


def access_matrix() -> None:
    extra = ot.excess_rights(src.USERS, src.ROLES)
    idle = ot.dormant(src.LAST_USE_DAYS, 90)
    shared = [u for u in src.USERS if u.startswith("shared")]
    lines = ["access matrix review (synthetic accounts)",
             "  rights beyond the role:"]
    for u, r in sorted(extra.items()):
        lines.append(f"    {u:10s} {src.USERS[u][0]:16s} extra: {', '.join(sorted(r))}")
    lines += [f"  unused for more than 90 days: {', '.join(idle)}",
              f"  shared accounts: {', '.join(shared)}",
              "  each finding is a door left open by habit: an operator",
              "  who once needed settings, a vendor who loaded software",
              "  in commissioning, a shift login nobody owns. Rights are",
              "  reviewed against roles every quarter, unused accounts",
              "  closed, and shared logins replaced by named ones"]
    emit("b_access", lines)


def remote_access() -> None:
    always = 8760
    on_request = 12 * 4                         # 12 sessions a year of 4 h
    lines = ["vendor remote access: always open or opened on request (teaching)",
             f"  always open: {always:,} h a year that the path exists",
             f"  on request, 12 sessions of 4 h: {on_request} h a year",
             f"  exposure cut by {(1 - on_request / always) * 100:.1f} %",
             "  a session on request: asked for with a reason, approved by",
             "  the plant, through the jump host in the DMZ, with a second",
             "  factor, watched or recorded, closed at the end - the path",
             "  does not exist the rest of the year"]
    emit("b_remote", lines)


def log_volume() -> None:
    sources = [("zone firewalls", 2, 400_000, 300), ("switches", 34, 2_000, 200),
               ("servers and HMIs", 12, 20_000, 400), ("jump host", 1, 5_000, 500),
               ("controllers: changes, logins", 3, 50, 300)]
    lines = ["security logs kept for a year (teaching volumes)",
             "  source                         devices   events/day each   GB/year"]
    total = 0.0
    for name, n, per, size in sources:
        gb = ot.log_volume_gb(n * per, size, 365)
        total += gb
        lines.append(f"  {name:30s} {n:7d}   {per:15,d}   {gb:7.1f}")
    lines += [f"  total about {total:.0f} GB a year",
              "  the controllers write few events, and each one matters:",
              "  a configuration change or a login on a plant controller",
              "  is read by a person the same day; the firewall's many",
              "  events are searched when a question is asked"]
    emit("b_logs", lines)


def clocks_for_logs() -> None:
    ppm, days = 20.0, 30
    drift = ppm * 1e-6 * days * 86400
    lines = ["comparing logs from two devices (teaching)",
             f"  an unsynchronised clock at {ppm:.0f} ppm drifts {drift:.0f} s in {days} days",
             "  a login on the jump host and a change on a controller then",
             "  appear in the wrong order, or a minute apart when they were",
             "  seconds apart; every device that logs takes its time from",
             "  the plant's clocks (ch 35), and the log keeps the time base"]
    emit("b_clocks", lines)


def secrets() -> None:
    rows = [("factory default, published", None, None),
            ("8 lower-case letters", 26, 8), ("12 letters and digits", 62, 12),
            ("random 128-bit key", 2, 128)]
    lines = ["strength of a secret chosen at random (bits; defensive sizing)",
             "  secret                        bits"]
    for name, alpha, n in rows:
        b = "0 (known)" if alpha is None else f"{ot.entropy_bits(alpha, n):.0f}"
        lines.append(f"  {name:29s} {b}")
    lines += ["  a default password has no strength at all, however long;",
              "  every device gets its own secret at commissioning, kept in",
              "  a managed vault, and machines use keys or certificates",
              "  rather than passwords where the device supports them"]
    emit("b_secrets", lines)


def hardening() -> None:
    items = [("default accounts removed or renamed", 26, 28),
             ("unused services switched off", 22, 28),
             ("unused ports disabled", 25, 28),
             ("configuration fingerprint recorded", 28, 28),
             ("time from the plant clocks", 27, 28)]
    lines = ["hardening checklist of the 28 networked devices (synthetic FAT result)",
             "  item                                      done   of"]
    gaps = 0
    for name, done, n in items:
        gaps += n - done
        lines.append(f"  {name:41s} {done:4d}   {n}")
    lines += [f"  {gaps} open items go to the punch list of the factory test",
              "  and are closed before shipment; the checklist is part of",
              "  the configuration baseline of ch 35, so a replaced device",
              "  is hardened the same way"]
    emit("b_harden", lines)


def firewall_pair() -> None:
    a_single, a_pair = 0.9995, 1 - (1 - 0.9995) ** 2
    parts = {"core switch pair": 1 - (1 - 0.9998) ** 2, "firewall": a_single,
             "control-zone switch": 0.9998}
    a, _ = ot.series_availability(parts)
    parts2 = dict(parts, firewall=a_pair)
    a2, _ = ot.series_availability(parts2)
    single = [k for k in parts if "pair" not in k]
    lines = ["path from the control zone to the DMZ (teaching availabilities)",
             f"  with one firewall: A = {a:.6f}, {(1 - a) * 8760:.1f} h a year",
             f"  with a firewall pair: A = {a2:.6f}, {(1 - a2) * 8760:.1f} h a year",
             f"  single points of failure with one firewall: {', '.join(single)}",
             "  the DMZ path carries historian copies and supervised support,",
             "  not control: the plant runs if it fails - which is why a",
             "  single firewall may be accepted here, while the paths",
             "  inside the control zone are redundant"]
    emit("b_pair", lines)


def physical_interface() -> None:
    rows = [("control-room door forced", "site security", "OT lead"),
            ("cabinet door open, no work order", "operator", "site security"),
            ("console login at night, no permit", "OT lead", "site security"),
            ("unknown device on a switch port", "OT lead", "control engineer"),
            ("USB device refused at an HMI", "operator", "OT lead")]
    lines = ["where cyber and physical security meet (teaching interface table)",
             "  event                               first owner     informs"]
    for e, o, i in rows:
        lines.append(f"  {e:35s} {o:15s} {i}")
    lines += ["  each event has an owner and a path to the other team;",
              "  this table does not replace the site's physical-security",
              "  assessment (ch 32) - it only joins the two"]
    emit("b_physical", lines)


if __name__ == "__main__":
    zones()
    rule_review()
    access_matrix()
    remote_access()
    log_volume()
    clocks_for_logs()
    secrets()
    hardening()
    firewall_pair()
    physical_interface()
