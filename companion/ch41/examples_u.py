"""Chapter 41, a fourth round: what a re-flash can prove about a power
warranty (systematic against random uncertainty), the uncertainty of a
field I-V curve, when an infrared survey can fly (hours of strong sun from
the data pack), and sampling the connectors crimped at the site.

Run from the project root:   python -m companion.ch41.examples_u
Writes companion/ch41/expected/u_*.txt and diagrams/data/ch41-*.csv.
Teaching values (A-448, A-449).
"""
from __future__ import annotations

import math

from companion.ch41.common import csv, emit
from plantp import datapack

Z_A, Z_B = 1.645, 1.282           # one-sided 5 % risk, 90 % power


# ------------------------------------------- warranty: what a sample proves
# [start: warranty]
def detectable(n: int, sys_pct: float, rand_pct: float) -> float:
    """Smallest mean power shortfall (%) a sample of n re-flashed modules
    shows with 5 % risk and 90 % power: the systematic part (reference
    chain, shared by every module) does not shrink with n."""
    u = math.sqrt(sys_pct ** 2 + rand_pct ** 2 / n)
    return (Z_A + Z_B) * u
# [end: warranty]


def warranty() -> dict[str, dict[int, float]]:
    sys_lab = math.sqrt(0.4 ** 2 + 0.6 ** 2 + 0.8 ** 2)   # lesson B chain
    rand = math.sqrt(0.9 ** 2 + 0.5 ** 2)                  # tester + module
    cases = {"another lab, new reference": (sys_lab, rand),
             "same lab, kept control modules": (0.3, rand)}
    out, rows = {}, []
    lines = ["re-flashing modules after some years: smallest shortfall shown",
             "  (5 % risk, 90 % power; teaching uncertainties from lesson B)",
             "  measurement                      n = 5   n = 20   n = 100"]
    for name, (s, r) in cases.items():
        out[name] = {n: detectable(n, s, r) for n in (5, 20, 100)}
        lines.append(f"  {name:31s} " + "  ".join(
            f"{out[name][n]:5.2f} %" for n in (5, 20, 100)))
    for n in range(2, 101, 2):
        rows.append((n, round(detectable(n, sys_lab, rand), 3),
                     round(detectable(n, 0.3, rand), 3)))
    csv("ch41-warranty.csv", "n,other,same", rows)
    lines += ["  more modules shrink only the random part; the reference",
              "  chain stays: a breach of about 1 % is never proven by a",
              "  different lab, however many modules - only a relative",
              "  measurement against control modules kept in the dark",
              "  since delivery (same lab, same reference) shows it, with",
              "  about 100 modules; the contract names this method before",
              "  the first claim"]
    emit("u_warranty", lines)
    return out


# ------------------------------------------- field I-V curve uncertainty
def field_iv() -> dict[str, float]:
    parts = [("irradiance sensor (reference cell)", 2.0),
             ("module temperature 2 K x 0.35 %/K", 0.7),
             ("translation to STC (model)", 1.0),
             ("tracer and cabling", 0.5),
             ("non-uniform light and soiling", 1.0)]
    u = math.sqrt(sum(x * x for _, x in parts))
    lines = ["string I-V curve in the field, translated to STC (teaching %)"]
    for name, x in parts:
        lines.append(f"  {name:38s} {x:4.1f}")
    lines += [f"  combined {u:.2f} %, expanded (k = 2) {2 * u:.1f} %",
              f"  a string more than {2 * u:.0f} % low is a finding; 1 % is not -",
              "  field curves compare strings measured together in the same",
              "  hour (shared sensor, shared sun), where most of these",
              "  terms cancel; absolute power is the laboratory's job"]
    emit("u_fieldiv", lines)
    return dict(u=u)


# ------------------------------------------- infrared survey windows
def ir_hours(threshold: float = 600.0) -> dict[int, int]:
    h = datapack.load_hourly()
    month = h.index.month if hasattr(h.index, "month") else None
    if month is None:
        month = [1 + min(11, k // 730) for k in range(len(h))]
    ok = h["ghi_wm2"] >= threshold
    out = {}
    for m in range(1, 13):
        out[m] = int(sum(1 for mm, o in zip(month, ok) if mm == m and o))
    csv("ch41-irhours.csv", "month,hours", list(out.items()))
    need = 60.06 / 2.0                       # MWp a drone hour (teaching)
    best = max(out, key=out.get)
    worst = min(out, key=out.get)
    lines = [f"hours with GHI >= {threshold:.0f} W/m2 (data pack 1.1.0), "
             "for an infrared survey",
             "  month " + " ".join(f"{m:4d}" for m in range(1, 13)),
             "  hours " + " ".join(f"{out[m]:4d}" for m in range(1, 13)),
             f"  a survey of 60 MWp at 2 MWp a drone hour needs {need:.0f} h;",
             f"  month {best} offers {out[best]} such hours, month {worst} "
             f"only {out[worst]}",
             "  a hot cell shows only under strong, steady sun: the survey",
             "  is planned for the season and the time of day the data",
             "  allow, and the threshold is the method's (teaching here)"]
    emit("u_irhours", lines)
    return out


# ------------------------------------------- crimps made at the site
def site_crimps(p_bad: float = 0.05, per_day: int = 5) -> dict[int, float]:
    out = {}
    lines = [f"connectors crimped at the site: {per_day} pull tests a day per "
             "installer",
             f"  an installer making {p_bad:.0%} bad crimps is caught within d "
             "days with chance",
             "  days       1      3      5     10"]
    vals = []
    for d in (1, 3, 5, 10):
        p = 1 - (1 - p_bad) ** (per_day * d)
        out[d] = p
        vals.append(f"{p:5.0%}")
    lines.append("  chance  " + "  ".join(vals))
    lines += ["  sampling per installer, not per string: a bad habit belongs",
              "  to a person and a tool (ch 40, competency) - the samples",
              "  are cut out and the connectors replaced, so the test is",
              "  destructive and the count small; the maker's tool and",
              "  training remove most of the risk before any test"]
    emit("u_crimps", lines)
    return out


if __name__ == "__main__":
    warranty()
    field_iv()
    ir_hours()
    site_crimps()
