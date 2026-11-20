"""Chapter 24, section A - cable fundamentals and sizing for Plant P's
33 kV collector: resistance at temperature, the rating in place with the
installation factors, voltage drop and losses along a wind string,
annual losses from the hourly model, the adiabatic short-circuit limit,
and the preliminary selection of the first section of WS1 (worked
example 1).

Run from the project root:   python -m companion.ch24.examples_a
Writes companion/ch24/expected/a_*.txt. Teaching values A-321 to A-325.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch15 import sources as s15
from companion.ch24 import sources as src
from companion.ch24.common import emit
from plantp import cables as cb

ALPHA_AL = 0.00403


def temps() -> None:
    lines = ["resistance of the 240 mm2 Al conductor with temperature:",
             "  conductor C   ohm/km   vs 20 C"]
    r20 = src.MV_CABLES[240]["r20"]
    for t in (20, 40, 65, 90):
        r = cb.r_at(r20, t, ALPHA_AL)
        lines.append(f"  {t:11d}   {r:6.4f}   {r / r20:6.2f}")
    lines += ["  at its 90 C limit the conductor has 28 % more resistance",
              "  than on the data sheet's 20 C line: losses and drop are",
              "  computed at the temperature the conductor will run at"]
    emit("a_temps", lines)


def ratings() -> None:
    i_need = 5 * 4 * 1e6 / 0.95 / (math.sqrt(3) * 33e3)
    lines = ["rating in place of the 33 kV cables (installation factors):"]
    lines += [f"  {k:30s} {v:.2f}" for k, v in src.FACTORS.items()]
    lines.append("  section  reference A   factor   in place A   first WS1 section")
    for mm2, d in src.MV_CABLES.items():
        i, k = cb.rating(d["i0"], src.FACTORS)
        ok = "ok" if i >= i_need else "too small"
        lines.append(f"  {mm2:4d}     {d['i0']:8.0f}    {k:6.3f}   {i:9.0f}   {ok}")
    lines += [f"  the first section carries {i_need:.0f} A (4 turbines, pf 0.95):",
              "  240 mm2 fits the reference table but not the trench - the",
              "  factors (depth, soil, heat, a second circuit) take a third",
              "  of the rating away"]
    emit("a_ratings", lines)


def string_currents() -> np.ndarray:
    """Hourly current of a 4-turbine string from the ch 15 wind output
    (each string a third of the farm, pf 0.95)."""
    w = s15.plant_year()["w_av"]                      # MW, 12 turbines
    return w / 3 * 1e6 / 0.95 / (math.sqrt(3) * 33e3)


def losses() -> None:
    i = string_currents()
    lines = ["losses of a wind string's cable (4 sections x 1.1 km, teaching):",
             "  section  r at 65 C   loss at full A   kW   loss MWh/yr"]
    for mm2, d in src.MV_CABLES.items():
        r = cb.r_at(d["r20"], 65, ALPHA_AL)
        # section k carries (5 - k)/4 of the string current
        e = sum(cb.annual_loss_mwh(i * (5 - k) / 4, r, 1.1) for k in range(1, 5))
        full = sum(cb.loss_kw(368.3 * (5 - k) / 4, r, 1.1) for k in range(1, 5))
        lines.append(f"  {mm2:4d}     {r:7.4f}    {full:13.0f} kW   {e:10.1f}")
    energy = i.sum() * math.sqrt(3) * 33e3 * 0.95 / 1e6          # MWh
    e240 = sum(cb.annual_loss_mwh(i * (5 - k) / 4,
                                  cb.r_at(src.MV_CABLES[240]["r20"], 65, ALPHA_AL), 1.1)
               for k in range(1, 5))
    lines += [f"  string energy {energy / 1e3:.1f} GWh; the loss is"
              f" {e240 / energy:.2%} with 240 mm2,",
              "  the hourly series is used, not the peak: losses go with",
              "  the square of the current and the wind is mostly below",
              "  rated (ch 15)"]
    emit("a_losses", lines)


def fault() -> None:
    lines = ["short-circuit duty of the 33 kV cables (adiabatic limit):",
             "  conductor: 12.5 kA (ch 23) cleared in 0.5 s by the feeder",
             f"    relay, 1.0 s by the backup: S >= I sqrt(t) / k, k = {src.K_AL:.0f} (Al)"]
    for t in (0.5, 1.0):
        lines.append(f"    t = {t:.1f} s: {cb.adiabatic_mm2(12.5, t, src.K_AL):5.0f} mm2")
    lines += [f"  240 mm2 Al carries {cb.withstand_ka(240, 1.0, src.K_AL):.1f} kA for 1 s",
              "  screen: the earth-fault current is limited to 400 A (ch 23)",
              f"    a 35 mm2 Cu screen carries {cb.withstand_ka(35, 1.0, src.K_CU):.1f} kA for 1 s",
              "  both pass with margin; the backup clearing time sets the",
              "  duty, not the main relay's"]
    emit("a_fault", lines)


def select() -> None:
    i_need = 368.3
    rows = []
    for mm2, d in src.MV_CABLES.items():
        i_in, _ = cb.rating(d["i0"], src.FACTORS)
        r = cb.r_at(d["r20"], 90, ALPHA_AL)
        dv = sum(cb.drop_pct(i_need * (5 - k) / 4, 1.1, r, d["x"], 0.95, 33)
                 for k in range(1, 5))
        sc = cb.withstand_ka(mm2, 1.0, src.K_AL)
        rows.append((mm2, i_in, dv, sc))
    lines = ["worked example 1: preliminary cable for wind string WS1",
             "  checks: current in place >= 368 A; drop along the string",
             "  <= 2 %; withstand >= 12.5 kA for 1 s",
             "  section  in place A  ok   drop %  ok   withstand kA  ok"]
    for mm2, i_in, dv, sc in rows:
        lines.append(f"  {mm2:4d}  {i_in:11.0f}  {'y' if i_in >= i_need else 'n':3s}"
                     f"  {dv:6.2f}  {'y' if dv <= 2 else 'n':3s}  {sc:12.1f}  {'y' if sc >= 12.5 else 'n'}")
    lines.append("  smallest section that carries each section's current:")
    graded = []
    for k in range(1, 5):
        need = i_need * (5 - k) / 4
        mm2 = next(m for m, d in src.MV_CABLES.items()
                   if cb.rating(d["i0"], src.FACTORS)[0] >= need)
        graded.append(mm2)
        units = f"{5 - k} turbine" + ("s" if k < 4 else "")
        lines.append(f"    section {k} ({units}, {need:.0f} A): {mm2} mm2")
    lines += ["  the first section needs 630 mm2 in this trench; the string",
              "  can be graded " + "/".join(str(m) for m in graded) + " mm2 - one size or a",
              "  graded string is an economic choice (section F); the",
              "  reference table alone would have chosen 240 mm2 everywhere"]
    emit("a_select", lines)
    return graded


if __name__ == "__main__":
    temps()
    ratings()
    losses()
    fault()
    select()
