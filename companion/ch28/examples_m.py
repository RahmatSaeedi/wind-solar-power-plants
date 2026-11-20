"""Chapter 28 - expansion round 3: connection alternatives compared in
the study, the worst harmonic voltage over the operator's network
impedance locus, and the study programme as a critical path.

Run from the project root:   python -m companion.ch28.examples_m
Writes companion/ch28/expected/m_*.txt and diagrams/data/ch28-locus*.csv.
Teaching values (A-341, A-347).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch28 import sources as src
from companion.ch28.common import csv, emit
from plantp import appraisal as ap
from plantp import gridstudy as gs


def alternatives() -> None:
    from companion.ch15 import sources as s15
    p = np.clip(s15.plant_year()["delivered"], 0, None)
    lf = float(np.sum((p / 100) ** 2))                 # full-load-equivalent hours
    def at_risk(hours: float, limit: float) -> float:
        return hours / 8760 * float(np.sum(np.clip(p - limit, 0, None)))

    host = 40 * 0.006 * 12 + 24                      # host line: faults + its day
    opts = [   # name, kV, km, circuits, r ohm/km, S_sc MVA, capex M u, exposure MWh
        ("A radial 132 kV line, 7.06 km", 132, 7.06, 1, 0.12, 1500, 3.18 + 1.2,
         at_risk(7.06 * 0.006 * 12 + 24, 0.0)),
        ("B 132 kV tee, 2 km", 132, 2.0, 1, 0.12, 1100, 0.9 + 1.6,
         at_risk(2 * 0.006 * 12 + 24 + host, 0.0)),
        ("C 3 x 33 kV circuits, 12 km", 33, 12.0, 3, 0.06, 365, 3 * 12 * 0.165 + 0.9,
         3 * at_risk(12 * 0.01 * 120 + 24, 200 / 3)),
    ]
    lines = ["connection alternatives for the study (teaching data, A-347)",
             "  option                          SCR   loss MW   MWh/yr   exposure   capex",
             "                                        at 100    losses     MWh/yr     M u"]
    for name, kv, km, n, r, ssc, capex, exposure in opts:
        i = 100e6 / (math.sqrt(3) * kv * 1e3)
        loss = 3 * i ** 2 * r * km / n / 1e6
        lines.append(f"  {name:30s} {ssc / 100:5.1f}   {loss:7.2f}   {loss * lf:6.0f}   "
                     f"{exposure:8.0f}   {capex:5.2f}")
    lines += ["  (exposure: faults and one maintenance day a year of every",
              "  circuit the export depends on; one of three 33 kV circuits",
              "  out leaves two-thirds of the capacity)",
              "  the tee is cheapest but doubles the exposure - the plant",
              "  also stops for every fault and maintenance day of a 40 km",
              "  host line - and needs a three-ended protection scheme; the",
              "  33 kV option is weak (SCR below 4) and loses four to five",
              "  times more - the radial 132 kV line stays (D-018), and the",
              "  study records why"]
    emit("m_alternatives", lines)


# [start: locus]
def worst_on_locus(z_plant: complex, z1: complex, h: int, k_max: float = 3.0,
                   ang=(-75.0, 85.0), n: int = 120) -> tuple:
    """Largest |Z_net // Z_plant| over a sector locus of the network
    impedance at order h: |Z| up to k_max h |z1|, angle in ang (deg)."""
    best = (0.0, 0j)
    for m in np.linspace(0.02, 1.0, n) * k_max * h * abs(z1):
        for a in np.radians(np.linspace(ang[0], ang[1], n)):
            z = m * complex(math.cos(a), math.sin(a))
            zp = abs(z * z_plant / (z + z_plant))
            if zp > best[0]:
                best = (zp, z)
    return best
# [end: locus]


def locus() -> None:
    zb = 132.0 ** 2 / src.S_BASE
    z1 = gs.thevenin(1500, 8) * zb                    # ohm at 50 Hz
    zl = complex(src.LINE["r"], src.LINE["x"]) * src.LINE["km"]
    zt = complex(0.0063, 0.1905) / 2 * zb
    b_c = 1.77 / src.S_BASE / zb                      # S, cables seen at 132 kV
    i_h = {5: 6.6, 7: 4.4, 11: 2.6, 13: 2.2}          # A at the POC (teaching)
    v_ph = 132e3 / math.sqrt(3)
    lines = ["harmonic voltage at the POC: nominal network against its locus",
             "  (sector up to 3 h |z1|, -75 to +85 deg; plant: line, transformers,",
             "  cable capacitance; emission currents teaching)",
             "  h    I_h A   U_h nominal %   U_h worst on locus %   worst at R, X ohm"]
    for h, i in i_h.items():
        zp = zl.real + 1j * h * zl.imag + zt.real + 1j * h * zt.imag + 1 / (1j * h * b_c)
        zn = complex(z1.real, h * z1.imag)
        nominal = abs(zn * zp / (zn + zp)) * i / v_ph * 100
        zw, at = worst_on_locus(zp, z1, h)
        lines.append(f"  {h:2d}   {i:5.1f}   {nominal:13.3f}   {zw * i / v_ph * 100:20.3f}"
                     f"   {at.real:7.0f}, {at.imag:6.0f}")
        if h == 11:
            pts = []
            for a in np.linspace(-75, 85, 33):
                r = 3 * h * abs(z1)
                pts.append((f"{r * math.cos(math.radians(a)):.1f}", f"{r * math.sin(math.radians(a)):.1f}"))
            csv("ch28-locus.csv", "r,x", [("0", "0")] + pts + [("0", "0")])
            csv("ch28-locuspts.csv", "name,r,x",
                [("nominal", f"{zn.real:.1f}", f"{zn.imag:.1f}"),
                 ("worst", f"{at.real:.1f}", f"{at.imag:.1f}"),
                 ("plant", f"{zp.real:.1f}", f"{zp.imag:.1f}")])
    lines += ["  with the nominal network the plant adds about half a per",
              "  cent; somewhere on the locus the network resonates with the",
              "  plant's own capacitance and the same currents give far",
              "  more - the operator's locus, not one impedance, is what the",
              "  harmonic study uses (ch 27 allocation, U-100)"]
    emit("m_locus", lines)


def schedule() -> None:
    tasks = {
        "data request": (1.0, []),
        "network model (operator)": (3.0, ["data request"]),
        "RMS models (OEM)": (2.0, ["data request"]),
        "EMT models (OEM)": (4.0, ["data request"]),
        "grid-end settings (operator)": (3.0, ["data request"]),
        "steady-state studies": (1.5, ["network model (operator)"]),
        "dynamic RMS studies": (2.0, ["steady-state studies", "RMS models (OEM)"]),
        "EMT studies": (2.0, ["dynamic RMS studies", "EMT models (OEM)"]),
        "protection study": (1.5, ["steady-state studies", "grid-end settings (operator)"]),
        "report and check": (1.0, ["EMT studies", "protection study"]),
        "operator review": (2.0, ["report and check"]),
    }
    total, crit, slack = ap.critical_path(tasks)
    late = dict(tasks)
    late["EMT models (OEM)"] = (7.0, ["data request"])
    total_late, crit_late, _ = ap.critical_path(late)
    lines = ["the study programme as a network of tasks (months, teaching)",
             f"  total: {total:.1f} months; critical path:"]
    lines += [f"    {t}" for t in crit]
    lines += ["  slack of the tasks not on it (months):"]
    lines += [f"    {t:30s} {slack[t]:4.1f}" for t in tasks if slack[t] > 1e-9]
    lines += [f"  if the EMT models arrive 3 months late: {total_late:.1f} months,",
              "  the critical path then runs through them - the OEM's EMT",
              "  model is ordered with the equipment, not after it"]
    emit("m_schedule", lines)
    _ = crit_late


if __name__ == "__main__":
    alternatives()
    locus()
    schedule()
