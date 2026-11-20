"""Chapter 29, lesson F: fire-service site infrastructure in numbers -
access and turning space, firewater volume from placeholder rates and
durations, and containment of contaminated runoff at the main
transformers. No fire-system prescription: rates, durations, spacing
and the need for firewater at all come from the fire strategy, the
authority having jurisdiction and product tests (U-105).

Run from the project root:   python -m companion.ch29.examples_f
Writes companion/ch29/expected/f_*.txt. Placeholder values (A-354).
"""
from __future__ import annotations

from companion.ch29 import sources as src
from companion.ch29.common import emit
from plantp import civil as cv
from plantp import stats as sx


def access() -> None:
    lines = ["fire-service access (placeholders until the fire service states its own)",
             "  item                           placeholder     what decides it"]
    rows = [("road width (clear)", "4.0 m", "fire vehicles"),
            ("turning area at dead ends", "18 m circle", "turning circle"),
            ("hose length to tank or hydrant", "90 m", "local fire code"),
            ("hard standing", "> 150 kN axle", "vehicle mass"),
            ("access to a transformer bay", "two sides", "fire strategy")]
    for item, val, by in rows:
        lines.append(f"  {item:30s} {val:15s} {by}")
    lines += ["  the numbers are agreed with the fire service early: the",
              "  site road (lesson B) and pads are designed to them, and",
              "  a turning area at the substation costs little when drawn",
              "  first and a lot when added later"]
    emit("f_access", lines)


def firewater() -> None:
    lines = ["firewater volume = rate x duration (placeholders, U-105)",
             "  case                                  rate L/min   minutes   volume m3"]
    cases = [("main transformer, external cooling", 3000, 60),
             ("BESS container, exposure protection", 1500, 120),
             ("substation building", 1000, 60)]
    for name, rate, mins in cases:
        lines.append(f"  {name:37s} {rate:10d}   {mins:7d}   {rate * mins / 1000:9.0f}")
    largest = max(r * m / 1000 for _, r, m in cases)
    lines += [f"  the largest single case sets the held reserve: about {largest:.0f} m3",
              "  (if the strategy assumes one event at a time) - kept in",
              "  the tank of D-022 and never used for operations (lesson",
              "  G); whether water is used on a battery at all is the fire",
              "  strategy's and the product tests' call, not this table's"]
    emit("f_water", lines)


def containment() -> None:
    oil = 22.0                                   # m3 per main transformer (ch 25)
    bund_area = 14.0 * 10.0                      # m2 (teaching)
    e = src.extremes()
    mu, beta = sx.gumbel_fit_moments(e["rain_1h"])
    rain = cv.gumbel_return(mu, beta, 10) / 1000 * bund_area
    applied = 3000 * 60 / 1000 * 0.25            # part of the cooling water that lands in the bund
    total = oil + rain + applied
    lines = ["runoff containment at one main transformer (teaching; the rule is local)",
             f"  oil volume                                   {oil:6.1f} m3",
             f"  rain on the bund, 1-hour 10-year storm       {rain:6.1f} m3",
             f"  firewater landing in the bund (1/4 of 180 m3) {applied:5.1f} m3",
             f"  volume to hold or route to an interceptor    {total:6.1f} m3",
             "  the oil alone fits a small bund; firewater and rain make",
             "  it several times larger - or route through an oil",
             "  interceptor to a holding pond; contaminated water is",
             "  tested before release, never let into the wadi"]
    emit("f_contain", lines)


if __name__ == "__main__":
    access()
    firewater()
    containment()
