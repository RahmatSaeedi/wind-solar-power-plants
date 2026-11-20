"""Chapter 2 laboratory 1 — what a dimension guard catches, and what it cannot.

Run from the project root:   python -m companion.ch02.lab_guard
Re-runs lines of the faulty draft PLP-GEN-CAL-0002 Rev A with quantities that carry
units (plantp.units), then applies a plausibility guard to the results.
Writes companion/ch02/expected/lab_guard.txt.
"""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plantp.units import Q, DimensionError, UnitError, check, kelvin  # noqa: E402

OUT = Path(__file__).resolve().parent / "expected" / "lab_guard.txt"


def try_step(label: str, step) -> str:
    """Run one calculation step; report the result or the guard's error."""
    try:
        result = step()
        return f"passed  {label}\n        -> {result:.5g}"
    except (DimensionError, UnitError) as err:
        message = textwrap.fill(f"-> {type(err).__name__}: {err}", 78,
                                initial_indent=" " * 8,
                                subsequent_indent=" " * 11)
        return f"CAUGHT  {label}\n{message}"


def plausible_cf(energy: Q, capacity: Q, hours: Q, low=0.15, high=0.55) -> str:
    """Plausibility guard: a wind-solar capacity factor outside low..high is
    suspect. The limits are a JUDGEMENT for screening, not a law of nature."""
    cf = float(energy / (capacity * hours))
    verdict = "ok" if low <= cf <= high else "SUSPECT"
    return f"CF = {cf:.4f} -> {verdict}"


def main() -> None:
    steps = [
        ("L3 as written: 50 MW x 1947.3 kWh/m2 x 0.833, as MWh",
         lambda: check(Q(50, "MW") * Q(1947.3, "kWh/m2") * 0.85 * 0.98, "MWh")),
        ("L3 corrected: 60 MWp x (1947.2 kWh/m2 / 1000 W/m2) x 0.833",
         lambda: check(Q(60, "MWp") * (Q(1947.2, "kWh/m2") / Q(1000, "W/m2"))
                       * 0.85 * 0.98, "MWh").to("MWh")),
        ("L5 as written: 877.67 hPa / (287.05 J/(kg K) x 16.78 degC)",
         lambda: Q(877.67, "hPa") / (Q(287.05, "J/kg/K") * Q(16.78, "degC"))),
        ("L5 corrected: kelvin(16.78) and hPa carried as a unit",
         lambda: check(Q(877.67, "hPa") / (Q(287.05, "J/kg/K") * Q(kelvin(16.78), "K")),
                       "kg/m3").to("kg/m3")),
        ("adding power to energy: 60 MW + 192.5 GWh",
         lambda: Q(60, "MW") + Q(192.5, "GWh")),
        ("L7 as written: 75,427 MWh + 192.5 'MWh' (label wrong, dimension right)",
         lambda: check(Q(75427, "MWh") + Q(192.5, "MWh"), "MWh")),
        ("L9 as written: 120 MW x 8784 h (basis wrong, dimension right)",
         lambda: check(Q(120, "MW") * Q(8784, "h"), "MWh").to("MWh")),
    ]
    lines = ["dimension guard on the Rev A draft"]
    lines += [try_step(label, step) for label, step in steps]
    lines += ["", "plausibility guard on the results",
              "Rev A: " + plausible_cf(Q(75619, "MWh"), Q(120, "MW"), Q(8784, "h")),
              "Rev B: " + plausible_cf(Q(289828, "MWh"), Q(100, "MW"), Q(8760, "h"))]
    text = "\n".join(lines) + "\n"
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(text)


if __name__ == "__main__":
    main()
