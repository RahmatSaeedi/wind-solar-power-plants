"""Chapter 19, section E - battery fire protection interfaces: a teaching
timeline for the propagation case (when each detection layer could see
the event, and how long the event takes to reach the edge of a module
under three designs). A teaching abstraction only: real times come from
large-scale tests of the product and the hazard mitigation analysis;
no firefighting tactics are given or implied.

Run from the project root:   python -m companion.ch19.examples_e
Writes companion/ch19/expected/e_*.txt.
Teaching values A-294.
"""
from __future__ import annotations

from companion.ch19 import sources as src
from companion.ch19.common import emit

# [start: layers]
LAYERS = {   # detection layer: minutes after the first cell vents (teaching)
    "BMS (voltage, temperature)": -10.0,     # may see a precursor first
    "off-gas detector": 1.0,
    "smoke detector": 5.0,
    "heat detector": 15.0,
}
DESIGNS = {  # design: minutes for the event to pass to the next cell
    "no barriers": 3.0,
    "cell barriers": 20.0,
    "cell barriers, cooled": 45.0,
}
# [end: layers]


def timeline() -> None:
    half = src.BUILD["s_module"] // 2
    lines = ["teaching timeline of a cell event in a module (A-294):",
             "  detection layer               minutes after the first vent"]
    for k, t in LAYERS.items():
        lines.append(f"  {k:30s} {t:6.0f}")
    lines += ["  design                    minutes per cell   to the module edge"]
    for k, tau in DESIGNS.items():
        lines.append(f"  {k:25s} {tau:10.0f}        {tau * half:10.0f}")
    lines += ["  the earlier layers buy time for isolation and for the",
              "  emergency plan; the barrier buys time for everything else;",
              "  the event may also stop by itself between cells; only",
              "  product tests show which (UL 9540A, NFPA 855 as examples of",
              "  what is asked; the authority decides what applies)"]
    emit("e_timeline", lines)


if __name__ == "__main__":
    timeline()
