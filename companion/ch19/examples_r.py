"""Chapter 19 - formation loss: the first charges build the surface
layer on the negative electrode and use up some lithium for good; the
cell is designed with that loss in mind (teaching values A-298).

Run from the project root:   python -m companion.ch19.examples_r
Writes companion/ch19/expected/r_*.txt.
"""
from __future__ import annotations

from companion.ch19.common import emit


def formation() -> None:
    q_pos = 340.0                         # Ah the positive electrode could give
    lines = ["formation loss of the teaching cell (A-298):",
             "  first-cycle efficiency   lithium left   capacity Ah   loss Ah"]
    for fce in (0.88, 0.92, 0.95):
        q = q_pos * fce
        lines.append(f"  {100 * fce:20.0f} %   {100 * fce:10.0f} %   {q:11.0f}   {q_pos - q:7.0f}")
    lines += ["  the lithium used to build the surface layer in formation is",
              "  gone for good; the maker designs the electrodes so that the",
              "  rated capacity (here 314 Ah) remains after it; a weak",
              "  formation leaves an unstable layer that keeps growing in",
              "  service (calendar fade, section A)"]
    emit("r_formation", lines)


def stacking() -> None:
    """Holding 5 MW of reserve for an hour both ways on top of shifting
    (teaching prices A-273 and a teaching reserve price A-298)."""
    import math
    eta = math.sqrt(0.86)
    head = 2 * 5.0                                   # MWh kept free, up and down
    shift_lost = head * eta * 365                    # MWh a year not shifted
    spread = 75.0 - 35.0 / 0.86
    lost_value = shift_lost * spread / 1000
    reserve_price = 4.0                              # u per MW per hour held
    hours = 8760 - 365 * 9                           # outside shifting hours
    gain = 5.0 * reserve_price * hours / 1000
    lines = ["stacking a 5 MW reserve on the shifting duty (teaching, A-298):",
             f"  headroom kept both ways: {head:.0f} MWh of the usable window",
             f"  shifting given up: {shift_lost:,.0f} MWh a year,"
             f" {lost_value:,.1f} k u at a {spread:.1f} u/MWh spread",
             f"  reserve earned outside the 9 shifting hours: {gain:,.1f} k u"
             f" at {reserve_price:.0f} u/MW/h",
             f"  net {gain - lost_value:+,.1f} k u a year; the reserve also uses",
             "  cycles from the warranty budget when it is called",
             "  stacking pays only if the reserve price and the rules allow;",
             "  the plant controller must keep both duties apart (chapter 20)"]
    emit("r_stacking", lines)


def factory_cover() -> None:
    """The S1 battery serving the chapter 17 factory: store the plant's
    surplus over the factory's load, give it back when the plant falls
    short (window 4-36 MWh, 86 % round trip, 20 MW)."""
    import math

    import numpy as np

    from companion.ch15 import sources as s15
    from companion.ch17 import sources as s17
    f = s17.factory()
    gen = np.clip(s15.plant_year()["net"], 0, None)
    eta = math.sqrt(0.86)
    used0 = np.minimum(gen, f)

    def extra_for(p_mw, e_mwh):
        lo, hi = 0.1 * e_mwh, 0.9 * e_mwh
        e, extra = lo, 0.0
        for k in range(8760):
            surplus = gen[k] - f[k]
            if surplus > 0:
                e += min(surplus, p_mw, (hi - e) / eta) * eta
            else:
                d = min(-surplus, p_mw, (e - lo) * eta)
                e -= d / eta
                extra += d
        return extra
    lines = ["batteries serving the chapter 17 factory (A-284; S1 = 20 MW, 40 MWh):",
             f"  factory {f.sum() / 1e3:.1f} GWh; covered by the plant alone"
             f" {used0.sum() / 1e3:.1f} GWh ({100 * used0.sum() / f.sum():.1f} %)",
             "  battery            added GWh   cover"]
    for p_mw, e_mwh in ((20.0, 40.0), (40.0, 80.0), (40.0, 160.0)):
        x = extra_for(p_mw, e_mwh)
        lines.append(f"  {p_mw:3.0f} MW, {e_mwh:3.0f} MWh    {x / 1e3:9.1f}   "
                     f"{100 * (used0.sum() + x) / f.sum():5.1f} %")
    lines += ["  a battery moves surplus into the next shortfall but cannot",
              "  bridge calm, dark days; doubling it adds less than the first",
              "  one did: storage for a flat load meets falling returns"]
    emit("r_factory", lines)


if __name__ == "__main__":
    formation()
    stacking()
    factory_cover()
