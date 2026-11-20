"""Appendix X - answers of the Part VI diagnostic mastery test (chapters
29-33): for each site, structure, logistics, safety and environmental
check, the hazard or impact it controls, the sourced numbers behind it,
who approves it and the evidence that closes it - with the numbers
computed from the chapters' companion code.

Run from the project root:   python -m companion.appx.mastery_part6
Writes companion/appx/expected/mastery_part6.txt.
Data pack 1.1.0 (synthetic), S0 unless stated; decisions D-033 to D-037.
Values marked (test) are used only here.
"""
from __future__ import annotations

import math

import numpy as np

from companion.appx.common import emit
from companion.ch33 import sources as s33
from plantp import civil as cv
from plantp import envsocial as es
from plantp import logistics as lg
from plantp import safety as sf
from plantp import structures as st

OUT: list[str] = []


def p(pid: str, text: str) -> None:
    OUT.append(f"{pid}: {text}")


def civil_water() -> None:
    ls = cv.ls_factor(20, 15)
    bare = cv.usle(300, 0.30, ls, 1.0, 1.0)
    cover = cv.usle(300, 0.30, ls, 0.20, 1.0)
    p("M77", f"road cut 20 m at 15 %: LS {ls:.2f}; bare {bare:.0f} t/ha/yr,"
             f" reinstated {cover:.0f}; proves where sediment control goes;"
             " data: rain R, soil K; evidence: inspections after storms")
    tests = [32.0, 29.0, 35.0, 31.0, 27.0, 33.0]          # friction angles deg (test)
    xk = cv.characteristic(tests)
    p("M78", f"six friction-angle tests (test): mean {np.mean(tests):.1f} deg,"
             f" characteristic {xk:.1f} deg; the design uses the cautious value;"
             " approved by the geotechnical engineer")
    s = cv.cooper_jacob(4e-4, 1.5e-4, 2e-4, 3000.0, 365 * 86400.0)
    p("M79", f"construction water 87,460 m3 against 30,300 m3 from the wells"
             f" (ch 29): 57,130 m3 from outside; one year of W-1 lowers the"
             f" village well {s:.2f} m (ch 33); evidence: pumping test, meters")


def structures_logistics() -> None:
    v = st.vortex_speed(0.215, 3.0)
    p("M80", f"lock-in speed of the erected tower with nacelle, f 0.215 Hz,"
             f" top 3.0 m: {v:.1f} m/s; without nacelle (0.45 Hz) 6.8 m/s -"
             " the bare tower is the risk; evidence: erection sequence, dampers")
    life = st.zinc_life(85.0, 3.0)
    p("M81", f"zinc 85 um in moist silty sand at 3 um/yr: {life:.0f} years,"
             " short of 30; evidence: soil tests and coating thickness records")
    f = lg.wind_on_load(15.0, 133.0, 1.2) / 1000
    p("M82", f"wind on a blade's side (133 m2, Cd 1.2) at 15 m/s: {f:.1f} kN;"
             " the lift plan's wind limit comes from the maker; evidence:"
             " anemometer at hook height, signed lift plan")
    p("M83", "turbine campaign 159-177 days depending on the start month"
             " (ch 31); route capacity sets the pace; evidence: route survey,"
             " permits, convoy log")


def safety() -> None:
    r, lo, hi = sf.incident_rate(11, 1_050_000)
    p("M84", f"11 recordable injuries in 1,050,000 h: {r:.2f} per 200,000 h"
             f" (90 % {lo:.2f} - {hi:.2f}); a small sample ranks, it does not prove")
    h = sf.fall_clearance(1.8, 1.75)
    p("M85", f"clearance below the anchor with a 1.8 m lanyard: {h:.2f} m;"
             " evidence: anchor certificate, rescue plan")
    d = sf.distance_for_flux(250_000.0, 0.30, 12.5)
    p("M86", f"oil fire 250 MW (test), radiant fraction 0.3: 12.5 kW/m2 at"
             f" {d:.0f} m - why spacings are tens of metres; values from the"
             " fire strategy and the authority (U-105, U-110)")
    t = sf.autonomy_minutes(180.0, 3000.0)
    p("M87", f"180 m3 at 3,000 L/min: {t:.0f} min; about 31 % of simulated"
             " arrivals come later (ch 32) - a placeholder the fire strategy decides")


def environment_social() -> None:
    cx, cy = s33.DWELLINGS["herders' camp B (seasonal)"]
    d = np.hypot(s33.TURBINES[:, 0] - cx, s33.TURBINES[:, 1] - cy)
    lvl = es.db_sum([es.noise_at(106.0, r) for r in d])
    p("M88", f"night noise at the camp {lvl:.1f} dB(A) against a placeholder"
             " 40 and a background of 28: under the limit, clearly audible;"
             " evidence: compliance survey with the background subtracted")
    b = s33.BIRDS
    dn = np.hypot(s33.TURBINES[:, 0] - s33.NEST[0], s33.TURBINES[:, 1] - s33.NEST[1])
    n = sum(es.collision_estimate(b["passages_at_nest"] * math.exp(-x / b["decay_m"]),
                                  b["p_collision"], b["avoidance"]) for x in dn)
    p("M89", f"raptor collisions about {n:.1f} a year; the layout waits for"
             " the survey (U-113); evidence: survey, carcass search with"
             " searcher and persistence trials")
    p("M90", "aquifer recharge 72,000 m3: operation takes 31 %, construction"
             " 112 % - construction water comes from outside the aquifer")
    g = es.per_kwh(90_252e3, 295.1e6 * 25)
    p("M91", f"S0 footprint {g:.1f} g/kWh by hand (12.5 median of the"
             " Monte Carlo), S1 13.3: ranges overlap - reported with the"
             " boundary, not ranked")
    p("M92", f"avoided at 0.5 t/MWh: {295_100 * 0.5:,.0f} t a year - a claim"
             " with its counterfactual, never added to the inventory, never"
             " guaranteed")


if __name__ == "__main__":
    civil_water()
    structures_logistics()
    safety()
    environment_social()
    emit("mastery_part6", OUT)
