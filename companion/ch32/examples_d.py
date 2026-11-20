"""Chapter 32, lesson D: firewater and the environment - how long the held
reserve lasts at the strategy's placeholder rates, whether the wells
can refill it, when the fire service arrives (a Monte Carlo of
mobilisation, drive and access), a radiant-heat screen of an oil fire,
contaminated runoff from a battery fire, impairments with their
compensating measures, and the first half hour of incident command.

Run from the project root:   python -m companion.ch32.examples_d
Writes companion/ch32/expected/d_*.txt and diagrams/data/ch32-arrival.csv.
Rates, durations and criteria are PLACEHOLDERS (U-105, A-370): the fire
strategy, the authority having jurisdiction and the product tests set
them. The calculation shows the method and what it is sensitive to.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch32 import sources as src
from companion.ch32.common import csv, emit
from plantp import safety as sf


def autonomy() -> None:
    res = src.TANK["reserve_m3"]
    refill = (0.40 + 0.25) * 60                     # both wells, L/min (ch 29)
    lines = [f"autonomy of the held reserve ({res:.0f} m3, placeholder rates)",
             "  case                                   rate L/min   minutes   +wells"]
    for name, rate in [("main transformer, external cooling", 3000),
                       ("BESS container, exposure protection", 1500),
                       ("both at once (not the design case)", 4500)]:
        t = sf.autonomy_minutes(res, rate)
        t2 = sf.autonomy_minutes(res, rate - refill)
        lines.append(f"  {name:38s} {rate:10d}   {t:7.0f}   {t2:6.0f}")
    lines += [f"  the wells add {refill:.0f} L/min - about 1 % of a fire flow:",
              "  the reserve is what there is, and refilling it takes",
              f"  {res * 1000 / refill / 60:.0f} h. The strategy states whether one event or",
              "  two is the design case, and the authority accepts it"]
    emit("d_autonomy", lines)


def arrival(n: int = 20_000, seed: int = 32) -> np.ndarray:
    r = src.RESPONSE
    rng = np.random.default_rng(seed)
    mob = rng.triangular(5, r["mobilise_min"], 15, n)
    speed = np.clip(rng.normal(r["speed_kmh"], 8, n), 35, 80)
    drive = r["fire_service_km"] / speed * 60
    blocked = np.where(rng.random(n) < 0.05, rng.uniform(10, 40, n), 0.0)
    acc = rng.triangular(5, r["access_min"], 20, n)
    return mob + drive + blocked + acc


def coverage() -> None:
    t = arrival()
    q = np.percentile(t, [10, 50, 90, 99])
    edges = np.arange(30, 125, 5)
    hist = [(int(e), int(((t >= e) & (t < e + 5)).sum())) for e in edges]
    csv("ch32-arrival.csv", "minute,count", hist)
    lines = ["fire-service arrival at the fire (Monte Carlo, 20,000 draws)",
             "  mobilise 5-15 min, 35 km at 60 +/- 8 km/h, road blocked 5 %",
             "  of the time (+10-40 min), access on site 5-20 min",
             f"  P10 {q[0]:.0f}, P50 {q[1]:.0f}, P90 {q[2]:.0f}, P99 {q[3]:.0f} min"]
    for target in (45, 60, 75):
        lines.append(f"  share arriving within {target} min: "
                     f"{sf.coverage_fraction(t, target) * 100:5.1f} %")
    auto = sf.autonomy_minutes(src.TANK["reserve_m3"], 3000)
    late = (1 - sf.coverage_fraction(t, auto)) * 100
    lines += [f"  the reserve lasts {auto:.0f} min at the transformer rate; in about",
              f"  {late:.0f} % of fires the fire service arrives after the site's own",
              "  water is gone - so the strategy, not the tank, sets what",
              "  the water is for (cooling exposures until help arrives),",
              "  and the fire service's own tankers and the meeting point",
              "  are agreed in advance"]
    emit("d_coverage", lines)


def radiant() -> None:
    area = 140.0                                   # bund of one main transformer (ch 29)
    q = 0.039 * 46_000 * area                      # kW: burning rate x heat of combustion
    dia = math.sqrt(4 * area / math.pi)
    lines = ["radiant heat from an oil-pool fire: a point-source screen",
             f"  bund {area:.0f} m2 (equivalent diameter {dia:.1f} m), heat release"
             f" {q / 1000:.0f} MW, radiant 30 %",
             "  distance m   flux kW/m2"]
    for r in (10, 15, 20, 30, 40):
        lines.append(f"  {r:10d}   {sf.heat_flux_point(q, 0.3, r):10.1f}")
    d12 = sf.distance_for_flux(q, 0.3, 12.5)
    lines += [f"  12.5 kW/m2 (a common screening level) is reached at {d12:.0f} m",
              f"  = {d12 / dia:.1f} pool diameters - where a point source is",
              "  least reliable. Separations and fire walls come from the",
              "  standard and the fire engineer's flame model (ch 25,",
              "  STD-123); the screen only shows why they are tens of metres"]
    emit("d_radiant", lines)


def runoff() -> None:
    from companion.ch29 import sources as s29
    from plantp import civil as cv
    from plantp import stats as sx
    mu, beta = sx.gumbel_fit_moments(s29.extremes()["rain_1h"])
    depth = cv.gumbel_return(mu, beta, 10) / 1000          # m, as in ch 29
    applied = 1500 * 120 / 1000                    # m3 of exposure water (placeholder)
    rain = 2400 * depth
    rows = [("water applied (placeholder case)", applied),
            ("share reaching the drains (60 %)", applied * 0.6),
            (f"rain on the BESS yard, 10-year hour ({depth * 1000:.0f} mm)", rain),
            ("volume to hold for testing", applied * 0.6 + rain)]
    lines = ["contaminated runoff from a battery-yard fire (teaching)"]
    for name, v in rows:
        lines.append(f"  {name:48s} {v:6.0f} m3")
    lines += ["  firewater from a battery or an oil fire carries metals,",
              "  fluorides or oil: the drains of the yard lead to a",
              "  closable pond, the outlet stays shut until the water is",
              "  tested, and disposal follows the environmental permit",
              "  (ch 29, 33) - it never runs to the wadi"]
    emit("d_runoff", lines)


def impairment() -> None:
    rows = [("building smoke detection, panel repair", 36, "fire watch, no hot work"),
            ("BESS-3 off-gas detector, replacement", 72, "container stopped, isolated"),
            ("fire-service road, culvert works", 120, "second route marked, notice"),
            ("tank reserve below 180 m3 after a test", 20, "refill first, tanker on call")]
    total = sum(h for _, h, _ in rows)
    lines = ["impairment register for one year (teaching)",
             "  impairment                               hours  compensating measure"]
    for name, h, m in rows:
        lines.append(f"  {name:40s} {h:5d}  {m}")
    lines += [f"  {total} impairment hours, each with a named owner, a",
              "  compensating measure and notice to the insurer and fire",
              "  service where the strategy requires it; an impairment",
              "  without a measure is a hidden gap in the protection"]
    emit("d_impair", lines)


def command() -> None:
    steps = [(0, "alarm reaches the control room; operator confirms location"),
             (1, "site emergency plan started; call the fire service by the plan"),
             (3, "evacuate the area; account for everyone at the muster point"),
             (6, "site team at the scene: cordon, information, no entry"),
             (10, "authorised person isolates by the plan from a safe place"),
             (15, "drains to the pond confirmed closed; neighbours told"),
             (20, "escort meets the fire service at the gate with the plan"),
             (57, "fire service in command (median arrival); site informs"),
             (90, "scene held for investigation; no restart without approval")]
    lines = ["the first ninety minutes of incident command (teaching timeline)",
             "  min  action"]
    for m, a in steps:
        lines.append(f"  {m:3d}  {a}")
    lines += ["  the site's role is alarm, people, isolation, information",
              "  and the environment; firefighting beyond first-aid",
              "  extinguishers by trained staff belongs to the fire",
              "  service, which takes command when it arrives"]
    emit("d_command", lines)


if __name__ == "__main__":
    autonomy()
    coverage()
    radiant()
    runoff()
    impairment()
    command()
