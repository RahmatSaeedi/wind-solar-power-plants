"""Chapter 48, round z: one or two anemometers for the tracker stow, and
how much of a control panel's I/O the factory test can simulate.

Run from the project root:   python -m companion.ch48.examples_z
Writes companion/ch48/expected/z_*.txt.
Teaching values (A-498 to A-505).
"""
from __future__ import annotations

from companion.ch48.common import emit


# ------------------------------------------------ 1. stow anemometers: 1oo1 or 1oo2
def stow_sensors(lam_dangerous: float = 0.10, lam_spurious: float = 0.20,
                 test_y: float = 1.0) -> dict:
    pfd1 = lam_dangerous * test_y / 2                   # 1oo1, simple approximation
    pfd2 = (lam_dangerous * test_y) ** 2 / 3            # 1oo2, independent sensors
    lines = [f"tracker stow on wind: sensor failing low {lam_dangerous}/yr, failing high "
             f"{lam_spurious}/yr,",
             f"  proof-tested every {test_y:.0f} year (teaching values)",
             "  scheme          chance of no stow when needed   spurious stows a year",
             f"  one sensor      {pfd1:30.4f}   {lam_spurious:21.2f}",
             f"  either of two   {pfd2:30.4f}   {2 * lam_spurious:21.2f}",
             f"  the second sensor cuts the chance of missing a stow "
             f"{pfd1 / pfd2:.0f}-fold and",
             "  doubles the stows for nothing - a few hours of lost",
             "  energy against a row that meets a storm flat; common",
             "  causes (one mast, one cable, one icing event) are what",
             "  limits the gain, so the two sensors sit apart"]
    emit("z_stow", lines)
    return dict(pfd1=pfd1, pfd2=pfd2, ratio=pfd1 / pfd2)


# ------------------------------------------------ 2. FAT I/O simulation coverage
IO_FAT = {   # point type: (points, simulated at the FAT)
    "analogue in": (88, 88), "digital in": (151, 140), "digital out": (61, 35),
    "RTD in": (24, 24), "serial points": (420, 260),
}


def fat_coverage(site_min_per_point: float = 6.0) -> dict:
    tot = sum(n for n, _ in IO_FAT.values())
    sim = sum(s for _, s in IO_FAT.values())
    left = tot - sim
    lines = ["RTU cabinet FAT: points simulated at the factory by type"]
    lines += [f"  {k:14s} {n:4d} points, {s:4d} simulated ({s / n:4.0%})"
              for k, (n, s) in IO_FAT.items()]
    lines += [f"  total {sim} of {tot} ({sim / tot:.0%}); {left} points wait for the site",
              f"  at {site_min_per_point:.0f} minutes a point on site: "
              f"{left * site_min_per_point / 60:.0f} h of loop checks,",
              "  two or three days of a test team in the commissioning window",
              "  digital outputs and serial points are the gap: outputs need",
              "  a load to show they switch, serial points a device to answer;",
              "  a simulator of the turbine and inverter protocols at the FAT",
              "  moves those hours out of the critical path (ch 50)"]
    emit("z_fat", lines)
    return dict(tot=tot, sim=sim, left=left, hours=left * site_min_per_point / 60)


if __name__ == "__main__":
    stow_sensors()
    fat_coverage()
