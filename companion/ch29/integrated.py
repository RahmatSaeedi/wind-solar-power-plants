"""Chapter 29 - three integrated Plant P examples: two civil checks by
hand, the further investigation plan with its cost against the risk it
removes, and the civil and water basis (D-033).

Run from the project root:   python -m companion.ch29.integrated
Writes companion/ch29/expected/int_*.txt.
"""
from __future__ import annotations

import math

from companion.ch29 import sources as src
from companion.ch29.common import emit
from plantp import civil as cv
from plantp import stats as sx


def by_hand() -> None:
    e = src.extremes()
    mu, beta = sx.gumbel_fit_moments(e["rain_1h"])
    r10 = cv.gumbel_return(mu, beta, 10)
    tc = cv.kirpich_tc(2500, 0.01)
    i = r10 * (60 / tc) ** 0.6
    q_hand = 0.278 * 0.35 * i * 3.2
    nq = math.exp(math.pi * math.tan(math.radians(30))) * math.tan(math.radians(60)) ** 2
    lines = ["two civil results checked by hand",
             f"  wadi crossing, 10-year: Q = 0.278 x 0.35 x {i:.1f} mm/h x 3.2 km2",
             f"    = {q_hand:.1f} m3/s; code {cv.rational_peak(0.35, i, 3.2):.1f}",
             f"  Nq at 30 deg: e^(pi tan 30) tan^2 60 = {nq:.2f}; code"
             f" {cv.bearing_factors(30)[1]:.2f}",
             "  a hand check of a formula's one number protects against",
             "  a wrong unit or a wrong factor in the code - the table of",
             "  results is then trusted, not taken on faith"]
    emit("int_hand", lines)


def investigation() -> None:
    items = [("5 boreholes to 15 m at T02/T04/T06/T08/T10", 5 * 9.0),
             ("deeper borehole or CPT at T05", 6.0), ("2 CPTs and lab tests at T07 (soft clay)", 10.0),
             ("sulphate/chloride tests (all missing)", 4.0), ("pumping test of W-1 (7 days)", 12.0),
             ("drone topographic survey of site and route", 18.0), ("wadi flood study", 15.0)]
    total = sum(c for _, c in items)
    lines = ["further investigation before design (teaching costs, k u)"]
    for name, c in items:
        lines.append(f"  {name:46s} {c:6.0f}")
    lines += [f"  total                                          {total:6.0f}",
              "  against it: one foundation redesigned during construction",
              "  (crane and crew standing, a month late) easily costs more",
              "  than the whole list - the investigation is the cheapest",
              "  risk reduction in the civil works (ch 22 value of",
              "  information)"]
    emit("int_investigation", lines)


def basis() -> None:
    lines = ["civil and water basis of Plant P (D-033):",
             "  ground: model from 10 boreholes and 2 seismic lines,",
             "    interpolated only with stated limits; the further",
             "    investigation of int_investigation before design; no",
             "    foundation chosen here (ch 30 with the engineers)",
             "  roads and pads: grades within the transport limits (U-106),",
             "    curve widening by swept path, aggregate by CBR section,",
             "    crane pads checked where soft ground lies (T07); the",
             "    grade line never dams the wadi (fill capped at the crest)",
             "  drainage: rational method on the 1-hour Gumbel record,",
             "    culvert or ford at the wadi crossing with an overtopping",
             "    path; sediment ponds while ground is bare",
             "  climate: design values with the record's trend, not as if",
             "    stationary; hazards linked to the parts they govern",
             "  fire: access, firewater and runoff containment from the",
             "    fire strategy and the authority (U-105), placeholders here",
             "  water: W-1 for operation with the tank carrying summer;",
             "    construction water from another source (trucked or",
             "    treated) - 54,000 m3 short; cleaning by robots preferred",
             "    on water grounds (D-014 robot vs truck at bid confirmed)",
             "  corridor: the ch 14 route straightened (4 angle points,",
             "    28 towers) with its register of surveys and permits;",
             "    substation 1.8 m above the channel bed: platform level",
             "    and any diversion bund after a flood study (U-107)",
             "  open: water right and abstraction volume (U-104); fire",
             "    strategy values (U-105); transport limits (U-106);",
             "    wadi flood levels and flow paths (U-107)"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    investigation()
    basis()
