"""Chapter 32, lesson N: more on managing people and hazards - how long
audit findings stay open, certificates expiring across a workforce,
shift rosters and fatigue, why touch voltage matters (body current), and
hand-arm vibration over a shift.

Run from the project root:   python -m companion.ch32.examples_n
Writes companion/ch32/expected/n_*.txt and diagrams/data/ch32-expiry.csv.
Teaching values (A-368, A-371); none of this is a procedure: limits and
rules come from local law, the project's system and specialists.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch32 import sources as src
from companion.ch32.common import csv, emit


def audit_ageing(seed: int = 32) -> None:
    rng = np.random.default_rng(seed)
    days = {"high": rng.gamma(2, 6, 12), "medium": rng.gamma(2, 15, 30), "low": rng.gamma(2, 30, 40)}
    target = {"high": 14, "medium": 45, "low": 90}
    lines = ["how long audit findings stay open (construction year, synthetic)",
             "  rating    findings   median days   target days   overdue"]
    for k, d in days.items():
        lines.append(f"  {k:8s} {d.size:9d}   {np.median(d):11.0f}   {target[k]:11d}"
                     f"   {np.mean(d > target[k]) * 100:5.0f} %")
    lines += ["  a finding closed late is a barrier left weak for longer:",
              "  overdue high-rated findings go to the project manager",
              "  every week, and 'closed' means verified on site, not",
              "  a signature on the form"]
    emit("n_audit", lines)


def expiry(seed: int = 32) -> None:
    rng = np.random.default_rng(seed)
    n = src.WORKFORCE["peak"]
    issued = rng.uniform(-24, 0, n)                       # months ago
    validity = rng.choice([24, 36], n)
    expires = issued + validity                           # months from now
    rows = [(m, int(((expires >= m) & (expires < m + 1)).sum())) for m in range(0, 24)]
    csv("ch32-expiry.csv", "month,count", rows)
    peak = max(c for _, c in rows)
    lines = ["certificates (height and rescue) expiring each month, peak workforce",
             f"  {n} people, validity 2 or 3 years, issued over the last two years",
             f"  expiring in the next 12 months: {int((expires < 12).sum())}",
             f"  busiest month: {peak}; course places of 12 -> {math.ceil(peak / 12)} courses",
             "  without a plan, expiries arrive as a wave and crews stop",
             "  for paperwork; the competency matrix (lesson A) flags each",
             "  expiry three months ahead and training is booked in time"]
    emit("n_expiry", lines)


def rosters() -> None:
    rows = [("12 h x 14 days on, 14 off", 12, 14, 14), ("12 h x 21 days on, 7 off", 12, 21, 7),
            ("10 h x 6 days, 1 off", 10, 6, 1)]
    lines = ["shift rosters and the hours worked (teaching)",
             "  roster                       h/week on   longest run h   rest days a cycle"]
    for name, h, on, off in rows:
        week = h * min(7, on)
        lines.append(f"  {name:28s} {week:9d}   {h * on:13d}   {off:17d}")
    lines += ["  long runs of long shifts build fatigue that one rest day",
              "  does not clear; the 21/7 roster puts 252 hours into one",
              "  run - fatigue errors cluster late in runs and after night",
              "  shifts, so critical work (isolation, lifts) is planned",
              "  away from them; legal limits come from the labour law"]
    emit("n_rosters", lines)


def body_current() -> None:
    lines = ["why touch voltage matters: current through the body (teaching)",
             "  I = U / R_body; R_body depends on skin, contact and path",
             "  touch voltage V   R dry ohm   I dry mA   R wet ohm   I wet mA"]
    for u in (25, 50, 230, 400):
        lines.append(f"  {u:15d}   {2000:9d}   {u / 2000 * 1000:8.0f}   {800:9d}"
                     f"   {u / 800 * 1000:8.0f}")
    lines += ["  a few tens of milliamps across the chest can stop a",
              "  heart: even low-voltage circuits are lethal with wet",
              "  skin - which is why isolation, earthing and protective",
              "  devices come first, and why no work here is ever done",
              "  live (ch 6 and 26 for the protection side)"]
    emit("n_body", lines)


def vibration() -> None:
    tasks = [("breaker (hand-held)", 15.0, 1.0), ("angle grinder", 5.0, 1.5),
             ("impact wrench on flanges", 8.0, 2.0)]
    total = math.sqrt(sum(a * a * t for _, a, t in tasks) / 8)
    lines = ["hand-arm vibration over a shift: A(8) = sqrt(sum a^2 t / 8)",
             "  tool                          a m/s2   hours"]
    for name, a, t in tasks:
        lines.append(f"  {name:29s} {a:6.1f}   {t:5.1f}")
    lines += [f"  daily exposure A(8) = {total:.1f} m/s2",
              "  the breaker hour alone gives most of the dose: tools with",
              "  low vibration, tension tools instead of impact wrenches",
              "  on flanges, and rotation between tasks come before",
              "  gloves; action and limit values are set by local law"]
    emit("n_vibration", lines)


if __name__ == "__main__":
    audit_ageing()
    expiry()
    rosters()
    body_current()
    vibration()
