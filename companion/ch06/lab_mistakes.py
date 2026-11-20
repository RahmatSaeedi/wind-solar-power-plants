"""Chapter 6 lab: four classic feeder-calculation mistakes, and how a test
catches each of them.

Run from the project root:   python -m companion.ch06.lab_mistakes
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plantp import dc  # noqa: E402

I, L, A = 314.64, 180.0, 240.0          # A, m (one way), mm2
RHO_AL_50C = dc.resistivity_at("aluminium", 50.0)


# [start: mistakes]
def drop_correct():
    """Two conductors, area in m2, aluminium at 50 C."""
    return I * 2 * RHO_AL_50C * L / (A * 1e-6)


def drop_one_way():
    """Mistake 1: forgets the return conductor."""
    return I * RHO_AL_50C * L / (A * 1e-6)


def drop_area_in_mm2():
    """Mistake 2: puts mm2 where the formula needs m2."""
    return I * 2 * RHO_AL_50C * L / A


def drop_copper_rho():
    """Mistake 3: uses copper resistivity for an aluminium cable."""
    return I * 2 * dc.resistivity_at("copper", 50.0) * L / (A * 1e-6)


def drop_cold():
    """Mistake 4: uses the 20 C resistivity for a 50 C conductor."""
    return I * 2 * dc.RESISTIVITY_20C["aluminium"] * L / (A * 1e-6)
# [end: mistakes]


# [start: check]
reference = dc.feeder(I, L, A, "aluminium", 50.0).drop_v   # tested function
for f in (drop_correct, drop_one_way, drop_area_in_mm2,
          drop_copper_rho, drop_cold):
    value = f()
    ok = abs(value - reference) < 1e-9
    print(f"{f.__name__:18s} {value:14.4f} V  "
          f"{'OK' if ok else 'WRONG: ratio %.4g' % (value / reference)}")
# [end: check]
