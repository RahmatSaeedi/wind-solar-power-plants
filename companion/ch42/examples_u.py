"""Chapter 42, a fourth round on hub, pitch, bearings and shafts:
solidification time by Chvorinov's rule (where porosity collects),
nodularity of ductile iron, preload scatter of two tightening methods,
the pitch drive and its emergency feather energy, critical crack size
against what ultrasonic testing finds, and surface finish against
fatigue.

Run from the project root:   python -m companion.ch42.examples_u
Writes companion/ch42/expected/u_*.txt.
Teaching values (A-452, A-453); textbook relations, no process settings.
"""
from __future__ import annotations

import math
import random

from companion.ch42 import sources as src
from companion.ch42.common import emit
from plantp import materials as mt
from plantp import turbinemfg as tm


# ------------------------------------------------ Chvorinov's rule
# [start: chvorinov]
def solid_time(modulus_m: float, b_min_m2: float = 3.0e4) -> float:
    """Solidification time t = B (V/A)^2, minutes (B a mould constant)."""
    return b_min_m2 * modulus_m ** 2
# [end: chvorinov]


def chvorinov() -> dict[str, float]:
    parts = {"flange (200 mm)": 0.100, "body (120 mm)": 0.060,
             "web (60 mm)": 0.030}
    out = {k: solid_time(m) for k, m in parts.items()}
    riser = 1.2 * parts["flange (200 mm)"]
    lines = ["solidification time of hub sections, t = B (V/A)^2 (teaching B)",
             "  section            modulus V/A m   time min"]
    for k, m in parts.items():
        lines.append(f"  {k:18s} {m:13.3f}   {out[k]:8.0f}")
    lines += [f"  the flange freezes last ({out['flange (200 mm)'] / out['web (60 mm)']:.0f}"
              " x the web): the metal that",
              "  shrinks there must be fed;",
              f"  a feeder with modulus {riser:.3f} m freezes after it "
              f"({solid_time(riser):.0f} min); without",
              "  one, shrinkage porosity collects in the flange - exactly",
              "  the zone with the tightest limit (lesson B, casting)"]
    emit("u_chvorinov", lines)
    return out


# ------------------------------------------------ nodularity
def nodularity(seed: int = 4212, need: float = 0.85) -> dict[str, float]:
    rng = random.Random(seed)
    hubs = {f"H-{k:03d}": min(0.99, rng.gauss(0.92, 0.025)) for k in range(18, 26)}
    hubs["H-024"] = 0.78
    low = [k for k, v in hubs.items() if v < need]
    lines = [f"nodularity of the graphite in eight hub castings (teaching need "
             f"{need:.0%})",
             "  " + ", ".join(f"{k} {v:.0%}" for k, v in list(hubs.items())[:4]),
             "  " + ", ".join(f"{k} {v:.0%}" for k, v in list(hubs.items())[4:]),
             f"  below the need: {low}",
             "  round graphite nodules make cast iron ductile; flakes make",
             "  it brittle: a low reading means low elongation and",
             "  toughness in the whole casting, whatever its shape - the",
             "  test bar cast with each heat is the evidence"]
    emit("u_nodularity", lines)
    return dict(low=len(low))


# ------------------------------------------------ preload scatter
def preload(nominal_kn: float = 320.0) -> dict[str, float]:
    t = src.TURBINE
    pull = tm.insert_tension(t["flap_mnm"] * 1e6, 96, 3.2) / 1e3
    phi = 0.15
    out = {}
    lines = [f"blade-root bolts: preload scatter of two tightening methods "
             f"(nominal {nominal_kn:.0f} kN)",
             "  method            scatter   lowest preload   opening margin at "
             "operation"]
    for name, sc in (("torque wrench", 0.25), ("hydraulic tension", 0.10)):
        low = nominal_kn * (1 - sc)
        margin = low / ((1 - phi) * pull)
        out[name] = margin
        lines.append(f"  {name:17s} {sc:7.0%}   {low:14.0f}   {margin:9.2f}")
    lines += ["  friction in the thread and under the nut decides how much",
              "  of a torque becomes preload: a quarter either way with a",
              "  wrench, a tenth with a tensioner - the joint is designed",
              "  on the lowest preload the method can give, and the method",
              "  is named in the work instruction (lesson E, torque)"]
    emit("u_preload", lines)
    return out


# ------------------------------------------------ pitch drive
def pitch(m_blade_knm: float = 250.0, m_fric_knm: float = 200.0,
          rate_deg_s: float = 8.0) -> dict[str, float]:
    m = (m_blade_knm + m_fric_knm) * 1e3
    w = math.radians(rate_deg_s)
    p = m * w
    e = m * math.radians(90)
    lines = ["pitch drive of one blade (teaching moments)",
             f"  blade and bearing friction moment {m / 1e3:.0f} kN m",
             f"  emergency feathering at {rate_deg_s:.0f} deg/s: {p / 1e3:.0f} kW "
             "a blade",
             f"  energy to feather 90 deg: {e / 1e3:.0f} kJ a blade "
             f"({3 * e / 3.6e6:.2f} kWh for three)",
             "  the rotor's safe stop rests on feathering with the grid",
             "  gone: each blade carries its own store (battery or",
             "  accumulator), sized and tested at the factory, and checked",
             "  in service - a weak store is a safety finding (ch 11)"]
    emit("u_pitch", lines)
    return dict(p_kw=p / 1e3, e_kj=e / 1e3)


# ------------------------------------------------ critical crack, shaft
def shaft_crack(k_ic: float = 60e6, sigma: float = 150e6,
                ut_mm: float = 3.0) -> dict[str, float]:
    a_c = mt.critical_crack(k_ic, sigma) * 1000
    lines = ["main shaft: crack size that fails at once (fracture mechanics)",
             f"  K_IC {k_ic / 1e6:.0f} MPa sqrt(m), stress {sigma / 1e6:.0f} MPa, "
             "Y 1.12 (teaching)",
             f"  critical crack depth a_c = (K / (Y sigma))^2 / pi = {a_c:.1f} mm",
             f"  ultrasonic testing of the forging finds about {ut_mm} mm:",
             f"  a margin of {a_c / ut_mm:.0f} x in depth for fatigue growth",
             "  the forging is accepted on what UT finds; the time a crack",
             "  needs to grow from there to a_c is the fatigue design, and",
             "  the inspection interval in service follows from it"]
    emit("u_crack", lines)
    return dict(a_c=a_c)


# ------------------------------------------------ surface and fatigue
def surface(uts: float = 700.0) -> dict[str, float]:
    base = 0.5 * uts
    cases = {"polished": 1.00, "machined": 0.80, "forged skin": 0.50}
    size = 0.75                                    # large diameter, teaching
    out = {}
    lines = [f"endurance limit of a shaft steel (UTS {uts:.0f} MPa; 0.5 UTS "
             "base; size factor 0.75)",
             "  surface           factor   endurance limit MPa"]
    for k, f in cases.items():
        se = base * f * size
        out[k] = se
        lines.append(f"  {k:16s} {f:6.2f}   {se:19.0f}")
    lines += ["  the same steel loses half its fatigue strength with the",
              "  forging skin left on: shoulders and fillets are machined,",
              "  their radius and roughness are on the drawing and in the",
              "  inspection record - finish is a fatigue characteristic"]
    emit("u_surface", lines)
    return out


if __name__ == "__main__":
    chvorinov()
    nodularity()
    preload()
    pitch()
    shaft_crack()
    surface()
