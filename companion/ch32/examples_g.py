"""Chapter 32, lesson G: worker welfare and the community interface -
where the workforce lives and what that costs in water, the road risk of
moving people every day, construction traffic past the village, a
grievance log and its closing times, public access to the site, and
which commitments are law, lender conditions or the project's own.

Run from the project root:   python -m companion.ch32.examples_g
Writes companion/ch32/expected/g_*.txt and diagrams/data/ch32-grievance.csv.
Teaching values (A-374); the fictional community of chapters 14 and 22.
Legal obligations come from local law and counsel; lender conditions
from the finance documents (STD-108); none is assumed here.
"""
from __future__ import annotations

import numpy as np

from companion.ch32 import sources as src
from companion.ch32.common import csv, emit


def accommodation() -> None:
    w = src.WORKFORCE
    outside = w["peak"] * (1 - w["local_share"])
    camp_m3_day = outside * w["l_day"] * 1.8 / 1000          # camp use incl. kitchen, laundry
    wells = (0.40 + 0.25) * 86.4                              # m3/day (ch 29)
    lines = ["where the outside workers live (peak, teaching)",
             f"  peak workforce {w['peak']}; local share {w['local_share'] * 100:.0f} %;"
             f" outside workers {outside:.0f}",
             f"  camp water at 1.8 x {w['l_day']:.0f} L a day each: {camp_m3_day:5.1f} m3/day",
             f"  both wells at their safe yield:             {wells:5.1f} m3/day",
             f"  share of the wells a camp on site would use: {camp_m3_day / wells * 100:4.0f} %",
             "  a camp on site would take most of the wells while dust",
             "  suppression already needs trucked water (ch 29): rented",
             "  housing in the town, or a camp with its own supply, is the",
             "  choice - each with its own conduct, health and transport",
             "  plan agreed with the community"]
    emit("g_camp", lines)


def transport() -> None:
    w = src.WORKFORCE
    days = 26 * 18
    avg = w["worker_months"] / 18
    buses = np.ceil(avg * (1 - w["local_share"]) / 40)
    bus_km = buses * 2 * w["km_to_town"] * days
    car_km = avg * (1 - w["local_share"]) / 1.5 * 2 * w["km_to_town"] * days
    rate = 0.5e-6                                     # injury crashes per vehicle-km (teaching)
    lines = ["moving the workforce every day (18 months, 26 days a month)",
             f"  average workforce {avg:.0f}; from town {avg * (1 - w['local_share']):.0f};"
             f" {buses:.0f} buses of 40",
             f"  by bus: {bus_km:,.0f} vehicle-km; by car (1.5 a car): {car_km:,.0f}",
             f"  expected injury crashes at {rate * 1e6:.1f} per million vehicle-km:"
             f" bus {bus_km * rate:.2f}, cars {car_km * rate:.2f}",
             "  the daily drive is one of the largest risks of the whole",
             "  project: buses, rested drivers, no driving after a night",
             "  shift and a road survey cut it more than any site rule"]
    emit("g_transport", lines)


def traffic() -> None:
    hours = np.arange(6, 19)
    trucks = np.array([4, 10, 14, 12, 10, 9, 6, 9, 11, 12, 10, 6, 3])
    school = (hours == 7) | (hours == 13)
    lines = ["construction trucks past the village school (peak month, teaching)",
             "  hour   trucks   school run"]
    for h, t, s in zip(hours, trucks, school):
        lines.append(f"  {h:4d}   {t:6d}   {'yes' if s else ''}")
    moved = int(trucks[school].sum())
    lines += [f"  {trucks.sum()} trucks a day; {moved} pass in the two school hours",
              "  holding them for those two hours moves them into the next,",
              "  with a marshal at the crossing and a lower speed limit",
              "  through the village - agreed with the village, not imposed"]
    emit("g_traffic", lines)


def grievances(seed: int = 32) -> None:
    rng = np.random.default_rng(seed)
    cats = {"dust and noise": 14, "road and traffic": 9, "hiring and pay": 8,
            "land and access": 5, "worker conduct": 3, "water": 3}
    days = {"dust and noise": 6, "road and traffic": 10, "hiring and pay": 25,
            "land and access": 45, "worker conduct": 15, "water": 20}
    rows, all_days = [], []
    for c, n in cats.items():
        d = rng.gamma(2.0, days[c] / 2.0, n)
        all_days += list(d)
        rows.append((c.replace(" ", "_"), n, round(float(np.median(d)), 1)))
    csv("ch32-grievance.csv", "category,n,median_days", rows)
    a = np.array(all_days)
    lines = ["grievance log of the construction year (synthetic)",
             "  category            count   median days to close"]
    for c, n, m in rows:
        lines.append(f"  {c.replace('_', ' '):18s} {n:6d}   {m:8.1f}")
    lines += [f"  {len(a)} grievances; {(a <= 30).mean() * 100:.0f} % closed within 30 days;"
              f" longest {a.max():.0f} days",
              "  land and access cases take longest and go to the",
              "  escalation step with a named senior person; a grievance",
              "  about worker conduct goes to the protection route at once,",
              "  never through the open log"]
    emit("g_grievance", lines)


def public() -> None:
    items = [("substation", "fence, locked gates, signs", "intruder electrocuted"),
             ("BESS yard", "fence, signs, responder plan", "fire, off-gas"),
             ("PV array", "fence, signs at the gates", "DC energised in daylight"),
             ("turbines", "locked doors, ice and blade signs", "falling objects, climbing"),
             ("construction", "barriers, banksmen, night lights", "open trenches, plant")]
    lines = ["public access: what each area protects people from (teaching)",
             "  area          measure                             hazard to a visitor"]
    for a, m, h in items:
        lines.append(f"  {a:12s}  {m:34s}  {h}")
    lines += ["  the fence protects the public as much as the plant: a",
              "  herder's child at the substation fence is the risk the",
              "  signs, the locks and the talks at the village school",
              "  address; grazing and paths across the site are agreed"]
    emit("g_public", lines)


def commitments() -> None:
    rows = [("pay, hours, rest days, safe workplace", "law", "law, counsel"),
            ("worker grievance channel", "lender", "loan (STD-108)"),
            ("accommodation standards", "lender", "loan"),
            ("community grievance mechanism", "lender+own", "ESMP (ch 33)"),
            ("local hiring share 40 %", "project", "community deal"),
            ("school-hour truck hold", "project", "village deal"),
            ("security conduct, use of force", "law, lender", "counsel, loan")]
    lines = ["what kind of commitment each item is (teaching, not legal advice)",
             "  item                                    kind           set by"]
    for i, k, s in rows:
        lines.append(f"  {i:38s}  {k:13s}  {s}")
    lines += ["  keeping the kinds apart matters: a legal duty cannot be",
              "  traded away, a lender condition is a covenant of the loan,",
              "  and a project promise is kept because trust depends on it"]
    emit("g_commit", lines)


if __name__ == "__main__":
    accommodation()
    transport()
    traffic()
    grievances()
    public()
    commitments()
