"""Chapter 53, lessons G, H and I: socially responsible closure or
repowering (commitments to close, workforce transition, traffic near the
village, disclosure timeline, land return), asset-information continuity
(retention, migration, access removal), and lifecycle footprint and
carbon claims on one functional unit with uncertainty.

Run from the project root:   python -m companion.ch53.examples_g
Writes companion/ch53/expected/g_*.txt, h_*.txt, i_*.txt and
diagrams/data/ch53-footprint.csv. Teaching values (A-544, A-545).
"""
from __future__ import annotations

import numpy as np

from companion.ch53 import sources as src
from companion.ch53.common import csv, emit
from plantp import lifecycle as lc


# ------------------------------------------------ G1. commitments to close
def commitments() -> dict:
    no_ev = [k for k, (st, ev) in src.COMMITMENTS_CLOSE.items() if not ev]
    lines = ["closure commitments at year 18: status and evidence on file"]
    lines += [f"  {k:36s} {st:14s} {'evidence' if ev else 'NO EVIDENCE'}"
              for k, (st, ev) in src.COMMITMENTS_CLOSE.items()]
    lines += [f"  {len(no_ev)} of {len(src.COMMITMENTS_CLOSE)} without evidence seven years before closure;",
              "  each gets an owner and a date now (ch 33, ch 51 register) -",
              "  land return and local hiring are the two the village will",
              "  measure the closure by"]
    emit("g_commit", lines)
    return dict(no_ev=len(no_ev))


# ------------------------------------------------ G2. workforce transition
def workforce() -> dict:
    w = src.WORKFORCE
    decom_jobs = 70                                      # peak, 10 months (teaching)
    retrain = 20
    lines = [f"O&M staff {w['om_staff']}, of whom local {w['local']}; closure in {w['years_left']} years",
             f"  decommissioning peak {decom_jobs} jobs for 10 months; a repowered plant keeps",
             f"  about {w['om_staff']} O&M jobs, a retired one none",
             f"  transition plan: {retrain} places in a retraining programme (teaching), local",
             "  hiring in decommissioning at the construction share (ch 49)",
             "  and notice to staff at least two years ahead - the plan is",
             "  written with the workforce and their representatives"]
    emit("g_work", lines)
    return dict(peak=decom_jobs)


# ------------------------------------------------ G3. traffic past the village
def traffic(truck_t: float = 25.0, months: int = 10) -> dict:
    w = lc.waste_balance(src.MATERIALS)
    loads = w["total"] / truck_t
    per_day = loads / (months * 22)
    lines = [f"decommissioning traffic: {w['total']:,.0f} t at {truck_t:.0f} t a load = {loads:,.0f} loads",
             f"  over {months} months of 22 working days: {per_day:.1f} loads a day, two",
             "  passes each past the school (ch 33 traffic noise, ch 51",
             "  speed logs) - hours, routes and the school calendar go into",
             "  the traffic plan disclosed to the village"]
    emit("g_traffic", lines)
    return dict(loads=loads, per_day=per_day)


# ------------------------------------------------ G4. disclosure timeline
def disclosure() -> list:
    steps = [(36, "decision to repower or retire disclosed to landholders and village"),
             (30, "consultation on access, schedule and land return"),
             (24, "workforce notice and transition plan"),
             (12, "traffic and works plan; grievance contacts refreshed"),
             (3, "start notice; hazardous-material routes published"),
             (-12, "land return inspected with the landholder; bond release")]
    lines = ["disclosure timeline, months before the end of operation (teaching)"]
    lines += [f"  {m:3d}  {t}" for m, t in steps]
    lines += ["  the dates follow the permit and land agreements verified",
              "  locally (ch 54-58); the record of each step is closure",
              "  evidence (ch 33 commitments)"]
    emit("g_disclose", lines)
    return steps


# ------------------------------------------------ H1. retention schedule
def retention() -> dict:
    keep = {k: v for k, v in src.RECORDS.items() if v[0] > 0}
    not_migrated = [k for k, (y, m, gb) in keep.items() if not m]
    gb = sum(g for _, _, g in keep.values())
    lines = ["records at closure: years to keep, migrated to the successor system?, size"]
    lines += [f"  {k:28s} {y:3d} yr  {'yes' if m else 'NO '}  {g:8,.1f} GB"
              for k, (y, m, g) in src.RECORDS.items()]
    lines += [f"  {len(not_migrated)} record sets to keep are not yet migrated:",
              f"  {', '.join(not_migrated)}",
              f"  ({gb:,.0f} GB in all); the periods are teaching values - the",
              "  real ones come from verified obligations (ch 54-58)"]
    emit("h_retention", lines)
    return dict(not_migrated=not_migrated, gb=gb)


# ------------------------------------------------ H2. access removal
def access() -> dict:
    accounts = {"SCADA operator accounts": 22, "vendor remote access": 5,
                "PPC engineering keys": 3, "cloud data link of the inverters": 1,
                "VPN certificates": 9}
    tot = sum(accounts.values())
    lines = ["at retirement: access to remove, with a record of each removal"]
    lines += [f"  {k:34s} {v:3d}" for k, v in accounts.items()]
    lines += [f"  {tot} credentials and links; the inverters' cloud link (ch 36)",
              "  outlives the plant if nobody closes it - removal is",
              "  verified by a scan of what still answers, not by a list"]
    emit("h_access", lines)
    return dict(tot=tot)


# ------------------------------------------------ I1. footprint on one functional unit
def footprint() -> dict:
    # t CO2e (median, cov) for each option over years 18-25 or 18-30, per kWh delivered
    opts = {
        "A repair gearboxes, run to 25": ({"repairs (parts, transport)": (450.0, 0.4),
                                          "operation 7 yr": (1_100.0, 0.3)}, 7 * 255_000.0),
        "C replace gearboxes, run to 25": ({"new gearboxes (12)": (1_400.0, 0.35),
                                           "operation 7 yr": (1_100.0, 0.3)}, 7 * 256_500.0),
        "repower wind, run to 35": ({"new turbines excl. towers": (21_600.0, 0.3),
                                    "operation 17 yr": (2_700.0, 0.3),
                                    "dismantling and transport": (1_200.0, 0.4)}, 17 * 310_000.0),
    }
    out = {}
    rows = []
    for k, (parts, mwh) in opts.items():
        g = lc.footprint_mc(parts, mwh)
        out[k] = (float(np.median(g)), float(np.percentile(g, 5)), float(np.percentile(g, 95)))
        rows.append((len(rows) + 1, round(out[k][0], 2), round(out[k][1], 2), round(out[k][2], 2)))
    csv("ch53-footprint.csv", "k,median,p5,p95", rows)
    lines = ["footprint per kWh delivered, each option on the same boundary (from the",
             "  decision onwards: new equipment, transport, operation; g CO2e/kWh)",
             "  option                            median    5 %    95 %"]
    lines += [f"  {k:33s} {m:6.2f} {a:6.2f} {b:7.2f}" for k, (m, a, b) in out.items()]
    a, c, r = (out[k] for k in opts)
    overlap = a[2] >= c[1]
    lines += ["  all are a few grams a kWh - far below what they replace;",
              f"  repair and replacement {'overlap' if overlap else 'do not overlap'} "
              f"({a[1]:.2f}-{a[2]:.2f} and {c[1]:.2f}-{c[2]:.2f}), so",
              "  footprint does not pick between them (ch 33 lesson); the",
              f"  repowering is about {r[0] / a[0]:.0f} times higher per kWh - a real but",
              "  small cost to weigh with the energy it adds"]
    emit("i_footprint", lines)
    return out


# ------------------------------------------------ I2. avoided-emissions claims
def avoided(mwh: float = 255_000.0) -> dict:
    factors = {"low (gas margin)": 0.40, "central (grid average)": 0.55,
               "high (oil margin)": 0.75}                     # t CO2e/MWh, teaching
    rows = {k: f * mwh for k, f in factors.items()}
    lines = [f"'avoided emissions' of {mwh:,.0f} MWh a year depend on what is displaced"]
    lines += [f"  {k:24s} {f:.2f} t/MWh -> {v:9,.0f} t a year" for (k, f), v in
              zip(factors.items(), rows.values())]
    lines += [f"  a factor of {max(rows.values()) / min(rows.values()):.1f} between the cases: a claim",
              "  states its displaced source, its method and its uncertainty,",
              "  is kept apart from the plant's own footprint, and is never",
              "  added to it (ch 33 safeguard)"]
    emit("i_avoided", lines)
    return rows


if __name__ == "__main__":
    commitments()
    workforce()
    traffic()
    disclosure()
    retention()
    access()
    footprint()
    avoided()
