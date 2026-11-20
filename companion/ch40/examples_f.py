"""Chapter 40, factory environment, health and safety in numbers: the
tension in sling legs when the skid is lifted (a planning number only),
the solvent emitted by painting the frames, the waste streams of ten
skids, and how long stored energy in an inverter's DC link takes to decay
- each as information for the people who plan the work, not as a work
procedure.

Run from the project root:   python -m companion.ch40.examples_f
Writes companion/ch40/expected/f_*.txt.
Teaching values (A-441); lifts, isolation and hot work are planned and
done by competent people under the factory's own permits (ch 32).
"""
from __future__ import annotations

import math

from companion.ch40 import sources as src  # noqa: F401  (plantp on path)
from companion.ch40.common import emit
from plantp import quality as qa

MASS_T = {"transformer": 13.5, "inverter": 6.0, "RMU": 1.5,
          "frame": 4.2, "panel and cables": 1.0}           # A-441


def sling() -> dict[float, float]:
    m = sum(MASS_T.values())
    w = m * 9.81
    lines = [f"lifting the skid: {m:.1f} t, weight {w:.0f} kN",
             "  four-leg sling; a rigid load may hang on two legs only,",
             "  so the plan takes two (a common lifting practice)",
             "  angle from horizontal   tension a leg, kN"]
    out = {}
    for a in (60.0, 45.0, 30.0):
        t = qa.sling_leg(w, 2, a)
        out[a] = t
        lines.append(f"  {a:20.0f}   {t:17.0f}")
    lines += ["  a flatter sling pulls harder: at 30 degrees each leg",
              "  carries the whole weight; the centre of gravity is off",
              "  centre (the transformer is heavy), so the lift plan by a",
              "  competent person sets legs, angles and the spreader"]
    emit("f_sling", lines)
    return out


def voc() -> dict[str, float]:
    area, coats, use = 60.0, 2, 0.25            # m2 a frame, L/m2 a coat
    litres = 10 * area * coats * use
    lines = [f"paint for ten frames: {litres:.0f} L "
             f"({area:.0f} m2 x {coats} coats x {use} L/m2 x 10)"]
    out = {}
    for name, g_l, capture in (("solvent-borne", 420, 0.0),
                               ("high-solids", 250, 0.0),
                               ("solvent-borne, booth with abatement",
                                420, 0.8)):
        kg = litres * g_l / 1000 * (1 - capture)
        out[name] = kg
        lines.append(f"  {name:38s} {kg:5.0f} kg solvent to air")
    lines += ["  a mass balance: what goes in the gun and is not captured",
              "  goes to air; the permit of the shop sets the limit and",
              "  the paint data sheet gives the content (ch 33, data)"]
    emit("f_voc", lines)
    return out


WASTE = [  # stream, kg a skid, class, route (A-441)
    ("steel offcuts", 120.0, "inert", "recycle"),
    ("copper offcuts", 8.0, "inert", "recycle (valuable)"),
    ("packaging timber", 150.0, "non-hazardous", "reuse or recycle"),
    ("cable insulation offcuts", 5.0, "non-hazardous", "licensed waste"),
    ("paint and thinner waste", 6.0, "hazardous", "licensed carrier"),
    ("oily rags, absorbents", 2.0, "hazardous", "licensed carrier"),
]


def waste() -> dict[str, float]:
    tot = {c: 0.0 for _, _, c, _ in WASTE}
    lines = ["waste streams of ten skids"]
    for name, kg, cls, route in WASTE:
        tot[cls] += 10 * kg
        lines.append(f"  {name:26s} {10 * kg:6.0f} kg  {cls:13s} {route}")
    allkg = sum(tot.values())
    lines += [f"  total {allkg:,.0f} kg; hazardous {tot['hazardous']:.0f} kg "
              f"({tot['hazardous'] / allkg:.1%})",
              "  the small hazardous share needs the most care: separate",
              "  bins, a licensed carrier and a record that it arrived"]
    emit("f_waste", lines)
    return tot


def discharge() -> dict[str, float]:
    v0, c_f, r_ohm, safe = 1100.0, 0.010, 10_000.0, 50.0
    tau = r_ohm * c_f
    t = tau * math.log(v0 / safe)
    energy = 0.5 * c_f * v0 ** 2 / 1000
    lines = ["stored energy in an inverter DC link (design information)",
             f"  {c_f * 1000:.0f} mF at {v0:.0f} V holds {energy:.1f} kJ",
             f"  discharge resistor {r_ohm / 1000:.0f} kOhm: time constant "
             f"{tau:.0f} s",
             f"  to fall below {safe:.0f} V takes {t:.0f} s "
             f"(about {t / 60:.0f} minutes)",
             "  the maker's label gives the waiting time and the test bay",
             "  rules give who verifies absence of voltage and how; this",
             "  number only shows why the wait exists (ch 6, ch 32)"]
    emit("f_discharge", lines)
    return dict(tau=tau, t=t, energy=energy)


if __name__ == "__main__":
    sling()
    voc()
    waste()
    discharge()
