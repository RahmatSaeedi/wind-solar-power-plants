"""Chapter 8 - integrated Plant P examples: a motor start on the auxiliary
board fed by the transformer or by the backup generator (introductory),
the value of generator losses for the plant (intermediate), and a
topology-selection matrix for the WT-5.0-150 drivetrain (integrated).

Run from the project root:   python -m companion.ch08.integrated
Writes companion/ch08/expected/i_*.txt.
Data pack 1.1.0 (S0); A-037, A-093, A-110, A-111 .. A-114, A-122 (teaching
values, not vendor data). The decision recorded is D-011.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch08.common import emit
from companion.ch08.examples_a import MOTOR
from companion.ch08.lab_d import generator_year
from plantp import datapack
from plantp import machines as m

S3 = math.sqrt(3)


def motor_start() -> None:
    im = m.InductionMachine(**MOTOR)
    st = im.operate(1.0)
    z_lr = MOTOR["v_ph"] / st["i1"]
    zb = 0.4 ** 2 / 0.25                                     # 250 kVA, ohm
    z_tx = complex(0.012 * zb, math.sqrt(0.06 ** 2 - 0.012 ** 2) * zb)
    z_cab = complex(3.02e-3, 3.20e-3)                        # A-110
    zb_g = 0.4 ** 2 / 0.2                                    # 200 kVA, ohm
    lines = ["direct-on-line start of the 30 kW motor (A-114) at the "
             "auxiliary board:"]
    for name, z_src in (("transformer 250 kVA, 6 % + feeder", z_tx + z_cab),
                        ("backup generator, x_d'' 0.12 pu", complex(0.01 * zb_g,
                                                            0.12 * zb_g)),
                        ("backup generator, x_d' 0.20 pu", complex(0.01 * zb_g,
                                                           0.20 * zb_g))):
        v = abs(MOTOR["v_ph"] * z_lr / (z_lr + z_src))
        lines.append(f"  {name:34s} |Z| {1000 * abs(z_src):5.1f} mohm: "
                     f"dip {100 - 100 * v / 230:4.1f} %")
    k = 3 * 53.8 / abs(st["i1"])
    zg = complex(0.01 * zb_g, 0.20 * zb_g)
    v_soft = abs(MOTOR["v_ph"] * (z_lr / k) / (z_lr / k + zg))
    lines += [f"  backup generator with a soft starter (3 x rated): dip "
              f"{100 - 100 * v_soft / 230:.1f} %",
              "  the generator is a weaker source: the same start dips the "
              "voltage",
              "  two to three times deeper; the AVR recovers it within "
              "a second",
              "  or so, but contactors and electronics see the first dip"]
    emit("i_start", lines)


def value_of_losses() -> None:
    p_gen, loss35 = generator_year(0.35)
    _, loss20 = generator_year(0.20)
    d_mwh = 12 * (loss35.sum() - loss20.sum()) / 1e6
    price, rate, years = 50.0, 0.07, 25                       # A-037, A-093
    af = (1 - (1 + rate) ** -years) / rate
    lines = ["12 generators, gross data-pack year (A-111 loss model):",
             f"  losses with fixed share 35 %: "
             f"{12 * loss35.sum() / 1e6:,.0f} MWh/yr; with 20 %: "
             f"{12 * loss20.sum() / 1e6:,.0f} MWh/yr",
             f"  difference {d_mwh:,.0f} MWh/yr = {d_mwh * price:,.0f} u/yr "
             f"at {price:.0f} u/MWh",
             f"  over {years} years at {100 * rate:.0f} %: annuity factor "
             f"{af:.2f} -> {d_mwh * price * af:,.0f} u today",
             "  a buyer can put this value on the loss figures in a tender",
             "  (capitalised losses, chapter 39): lower losses are worth up",
             "  to that much more in price"]
    emit("i_losses", lines)


def stage_eff(load, eta_r, share):
    return np.array([m.efficiency(x, 1.0, eta_r, share) if x > 0 else 0.0
                     for x in load])


def topology_matrix() -> None:
    hourly = datapack.load_hourly()
    curve = datapack.load_power_curve()
    p_out = np.interp(hourly["ws_100m_ms"].to_numpy(),
                      curve["wind_speed_ms"].to_numpy(),
                      curve["power_kw"].to_numpy()) / 1e3        # MW
    chain_r = 0.97 * 0.975 * 0.975                              # baseline
    p_rotor = p_out / chain_r                                   # same rotor
    topo = {                                                    # A-122
        "DFIG, 3-stage gear": [(0.970, 0.30), (0.970, 0.35), (0.9925, 0.20)],
        "geared HS-PMSG, FC": [(0.970, 0.30), (0.975, 0.40), (0.975, 0.20)],
        "geared MS-PMSG, FC": [(0.980, 0.30), (0.975, 0.40), (0.975, 0.20)],
        "direct-drive PMSG, FC": [(1.000, 0.00), (0.955, 0.30), (0.975, 0.20)],
    }
    lines = ["same rotor power for all; part-load stage efficiencies (A-122):"]
    energy = {}
    for name, stages in topo.items():
        p = p_rotor.copy()
        for eta_r, share in stages:
            if eta_r >= 1.0:
                continue
            load = p / p_rotor.max()
            p = p * stage_eff(load, eta_r, share)
        energy[name] = p.sum()
    base = energy["geared HS-PMSG, FC"]
    for name, e in energy.items():
        lines.append(f"  {name:22s} {e:7.0f} MWh/yr ({100 * (e / base - 1):+.1f} "
                     "% on HS-PMSG)")
    scores = {                       # energy, grid, reliability, mass, supply
        "DFIG, 3-stage gear": [None, 3, 3, 5, 5],
        "geared HS-PMSG, FC": [None, 5, 3, 5, 3],
        "geared MS-PMSG, FC": [None, 5, 4, 4, 3],
        "direct-drive PMSG, FC": [None, 5, 4, 2, 2],
    }
    weights = [30, 20, 20, 15, 15]
    e_min, e_max = min(energy.values()), max(energy.values())
    for label, rule in (("min-max (worst 1, best 5)",
                         lambda e: 1 + 4 * (e - e_min) / (e_max - e_min)),
                        ("3 + 1 point per 1 % of yield",
                         lambda e: 3 + 100 * (e / base - 1))):
        lines.append(f"weighted scores, weights 30/20/20/15/15; energy: "
                     f"{label}")
        for name, sc in scores.items():
            row = [rule(energy[name])] + sc[1:]
            total = sum(w * x for w, x in zip(weights, row)) / 100
            lines.append(f"  {name:22s} " + " ".join(f"{x:3.1f}" for x in row)
                         + f"  total {total:.2f}")
    lines += ["min-max scaling turns a 1.5 % yield spread into 4 points "
              "and moves",
              "  the ranking; the other scores are judgements written down "
              "with",
              "  reasons: the matrix shows the argument, it does not "
              "replace the",
              "  turbine supplier's data"]
    emit("i_topology", lines)


def specification() -> None:
    s_r, v_r = 5.4e6, 690.0                                     # A-111
    i_r = s_r / (S3 * v_r)
    p_r = 5.13e6
    effs = [m.efficiency(x, p_r, 0.970, 0.35) for x in (0.25, 0.5, 1.0)]
    b = m.bearing_freqs(1155, 14, 0.040, 0.220)                  # A-116
    u = m.residual_unbalance(3000, 2.5, 1155)                    # A-115
    v_600 = v_r * 600 / 1155
    lines = ["conceptual data of the Plant P generator (PLP-ELE-SPC-0001, A):",
             f"  type: geared permanent-magnet synchronous, 6 poles, 1155 rpm, "
             f"{m.electrical_freq_hz(1155, 6):.2f} Hz",
             f"  rating {s_r / 1e6:.1f} MVA at {v_r:.0f} V: {i_r:,.0f} A; "
             f"{p_r / 1e6:.2f} MW to the converter",
             f"  efficiency at 25/50/100 % load (loss model): "
             + " / ".join(f"{e:.3f}" for e in effs),
             f"  EMF falls with speed: {v_600:.0f} V at 600 rpm; the "
             "converter",
             "    must work over the whole speed range and at overspeed",
             "  insulation designed for converter impulses (b_insulation); "
             "a",
             "    thermal class with margin over the 94 C hot spot of "
             "c_thermal",
             f"  cooling for about 160 kW: {158.7e3 / (4180 * 8):.1f} kg/s "
             "of water at 8 K (b_cooling)",
             f"  balance grade G 2.5: residual {u['u_gmm'] / 1e3:.0f} kg mm "
             "(c_balance)",
             "  monitoring: winding PT100s, bearing temperatures,",
             f"    accelerometers (outer race {b['bpfo']:.0f} Hz),",
             "    insulated bearing on the non-drive end against shaft "
             "currents",
             "  tests: routine set on every unit, type set on the first "
             "(section C)",
             "the qualified machine designer and the turbine supplier "
             "confirm every line"]
    emit("i_spec", lines)


if __name__ == "__main__":
    motor_start()
    value_of_losses()
    topology_matrix()
    specification()
