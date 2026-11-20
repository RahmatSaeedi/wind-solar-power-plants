"""Chapter 25 - fifth round: circulating current between paralleled
transformers on different taps, the PV unit transformer sized for the
inverter's reactive range, cooling a dry-type transformer in a turbine
tower, the uncertainty of measuring losses at low power factor, reading
a heat run by its exponential approach, amorphous cores for the unit
transformers, and the no-load loss of all unit transformers at night.

Run from the project root:   python -m companion.ch25.examples_s
Writes companion/ch25/expected/s_*.txt and diagrams/data/ch25-heatrun.csv.
Teaching values (A-326..A-330 extended).
"""
from __future__ import annotations

import math

from companion.ch25 import sources as src
from companion.ch25.common import csv, emit

M = src.MAIN


def circulating() -> None:
    z1 = z2 = 0.12
    lines = ["two transformers in parallel on different taps (12 % each):",
             "  tap difference   steps   circulating current % of rated   extra loss kW"]
    for steps in (1, 2, 4):
        du = 0.0125 * steps
        ic = du / (z1 + z2)
        loss = 2 * M["pk_kw"] * ic ** 2
        lines.append(f"  {du:14.2%}   {steps:5d}   {ic:31.1%}   {loss:13.1f}")
    lines += ["  a voltage difference across two impedances drives a current",
              "  round the loop with no load at all: it heats both units and",
              "  wastes reactive power - paralleled tap changers run as master",
              "  and follower, or by circulating-current control (Plant P",
              "  runs the sections split, ch 23, but may close the coupler)"]
    emit("s_circulating", lines)


def pv_unit() -> None:
    p, pf_min = 5.0, 0.90
    s_needed = p / pf_min
    lines = ["sizing the PV unit transformer for the inverter's reactive range:",
             f"  inverter 5.0 MW; reactive power down to power factor {pf_min}",
             f"  apparent power needed: {s_needed:.2f} MVA against the unit's 5.5 MVA:",
             f"  {s_needed / 5.5 - 1:.0%} short at the extreme power factor - a finding: rate the",
             "  unit 5.6 MVA, or accept that the transformer, not the",
             "  inverter, limits Q at full power (stated in the specification)",
             "  at night the inverter may still supply reactive power for",
             "  the grid (Q at night, ch 20): the transformer then carries",
             "  current with no active power, and its load loss is paid from",
             "  the grid:"]
    for q in (0.0, 1.0, 2.0):
        k = q / 5.5
        lines.append(f"    Q {q:.1f} Mvar -> load {k:.2f} pu, load loss {45 * k * k:5.1f} kW"
                     f" (+ no-load 4.5 kW)")
    lines += ["  a reactive service at night is a revenue with a loss in it:",
              "  the price must cover both (ch 20, ch 21)"]
    emit("s_pvunit", lines)


def tower() -> None:
    loss_kw = 7.0 + 50.0
    lines = ["cooling the dry-type transformer in the turbine tower (teaching):",
             f"  losses at full output {loss_kw:.0f} kW (no-load 7, load 50)",
             "  air rise K   air flow m3/s   at 2,000 m altitude (air 0.80 x)"]
    for dt in (10, 15, 20):
        q = loss_kw * 1e3 / (1.2 * 1005 * dt)
        lines.append(f"  {dt:10d}   {q:13.2f}   {q / 0.80:21.2f}")
    lines += ["  the heat must leave the tower base through filtered inlets",
              "  and outlets or a duct; thin air at altitude carries less",
              "  heat per cubic metre, so dry types are derated or given",
              "  more air - the maker's rating at the site's altitude and",
              "  temperature is part of the turbine supplier's evidence"]
    emit("s_tower", lines)


def loss_measurement() -> None:
    lines = ["measuring losses at low power factor: a small phase error matters",
             "  dP / P = tan(phi) x angle error (teaching)",
             "  test                  power factor   tan phi   0.1 mrad   0.5 mrad"]
    for name, pf in (("no-load test", 0.15), ("load-loss test", 0.03)):
        tphi = math.tan(math.acos(pf))
        lines.append(f"  {name:21s} {pf:12.2f}   {tphi:7.1f}   {tphi * 1e-4:8.2%}   {tphi * 5e-4:8.2%}")
    lines += ["  the load-loss test runs at a power factor of a few per cent:",
              "  half a milliradian of phase error in the measuring",
              "  transformers is 1.7 % of the loss - as large as some",
              "  tolerances; the test laboratory's calibrated system and",
              "  its stated uncertainty are part of the evidence behind the",
              "  loss penalty of lesson D"]
    emit("s_lossmeas", lines)


# [start: heatrun]
def fit_rise(times: list, rises: list) -> tuple:
    """Fit rise(t) = R_final (1 - exp(-t / tau)) to readings by scanning
    tau and solving R_final by least squares for each tau."""
    best = None
    for k in range(30, 600):
        tau = k / 60.0
        e = [1 - math.exp(-t / tau) for t in times]
        r_f = sum(a * b for a, b in zip(e, rises)) / sum(a * a for a in e)
        err = sum((r_f * a - b) ** 2 for a, b in zip(e, rises))
        if best is None or err < best[0]:
            best = (err, r_f, tau)
    return best[1], best[2]
# [end: heatrun]


def heat_run() -> None:
    times = [0.5, 1, 2, 3, 4, 5, 6, 7, 8]
    rises = [9.8, 18.7, 32.6, 42.0, 48.3, 52.5, 55.3, 57.0, 58.2]
    r_f, tau = fit_rise(times, rises)
    csv("ch25-heatrun.csv", "h,meas,fit", [(t, r, f"{r_f * (1 - math.exp(-t / tau)):.1f}")
                                           for t, r in zip(times, rises)])
    lines = ["a heat run stopped too early (teaching data, not lesson D's dossier):",
             "  hours " + " ".join(f"{t:4.1f}" for t in times),
             "  rise K" + " ".join(f"{r:5.1f}" for r in rises),
             f"  fit: final rise {r_f:.1f} K, time constant {tau:.2f} h",
             f"  the last reading ({rises[-1]} K) is {rises[-1] / r_f:.0%} of the way and looks",
             f"  inside the 60 K guarantee; the settled value {r_f:.1f} K is"
             f" {'over' if r_f > 60 else 'inside'} it -",
             "  the test runs until the rise has settled (the standard's",
             "  criterion), and the final value, not the last reading, is",
             "  compared with the guarantee"]
    emit("s_heatrun", lines)


def amorphous() -> None:
    a_factor = 6.84
    units = 10
    lines = ["amorphous cores for the ten PV unit transformers (teaching):",
             "  core                  no-load kW   ten units kW   value k u (A 6.84)"]
    for name, p0 in (("grain-oriented steel", 4.5), ("amorphous alloy", 1.4)):
        lines.append(f"  {name:21s} {p0:10.1f}   {p0 * units:12.1f}   {p0 * units * a_factor:18.0f}")
    lines += [f"  saving {(4.5 - 1.4) * units * a_factor:.0f} k u over the life against a"
              " price premium the",
              "  bidders state; amorphous cores are larger and noisier and are",
              "  offered up to a few MVA - the loss evaluation of lesson A",
              "  decides, unit by unit, as it did for the main transformer"]
    emit("s_amorphous", lines)


def night_units() -> None:
    hours = 4200
    lines = ["the unit transformers at night (no output, still energised):",
             "  group                 units   no-load kW   MWh a year (4,200 h)"]
    tot = 0.0
    for name, n, p0 in (("PV, oil skid", 10, 4.5), ("wind, dry in tower", 12, 7.0),
                        ("BESS", 4, 4.5), ("main transformers", 2, 35.0)):
        mwh = n * p0 * hours / 1e3
        tot += mwh
        lines.append(f"  {name:21s} {n:5d}   {n * p0:10.1f}   {mwh:20.0f}")
    lines += [f"  total {tot:,.0f} MWh a year bought at night - more than the two",
              "  main transformers alone: the 26 small units add up; their",
              "  no-load loss is worth evaluating as carefully (the A factor",
              "  applies to each), and the PV units could be switched off at",
              "  night where the inverters' night service is not needed"]
    emit("s_nightunits", lines)


if __name__ == "__main__":
    circulating()
    pv_unit()
    tower()
    loss_measurement()
    heat_run()
    amorphous()
    night_units()
